from db_service.embeddings import embed_text, reranker
from settings.config import driver , settings , MIN_EVIDENCE_SCORE, VISUAL_WEIGHT , client
from services.graph_store import extract_entities_relations

def retrieve(query, top_k=20):
    q_text_vec = embed_text(query)

    # Text-only vector search
    text_results = client.search(
        collection_name=settings.COLLECTION,
        query_vector=q_text_vec,
        limit=top_k
    )

    candidates = []

    # Collect candidates with their vector score
    candidates = [(t.payload, t.score) for t in text_results]

    # -----------------------------
    # Step 2: Graph augmentation
    # -----------------------------
    entities = extract_entities_relations(query)
    entity_names = list(
        {e["entity1"] for e in entities} |
        {e["entity2"] for e in entities}
    )
    
    with driver.session() as session:
        for name in entity_names:
            graph_res = session.run(
                """
                MATCH (c:Concept {name: $name})-[r:REL]->(d:Concept)
                RETURN c.name AS c_name, r.type AS r_type, d.name AS d_name
                LIMIT 5
                """,
                name=name
            )

            for r in graph_res:
                candidates.append((
                    {
                        "chunk": f"Graph pathway: {r['c_name']} {r['r_type']} {r['d_name']}",
                        "source": "Graph",
                        "page": None,
                        "image_path": None,
                        "origin": "graph"
                    },
                    0.5  # neutral prior score for graph hits
                ))

    # -----------------------------
    # Step 3: Rerank with CrossEncoder + fusion
    # -----------------------------
    texts = [c[0]["chunk"] for c in candidates]
    pairs = [(query, t) for t in texts]
    cross_scores = reranker.predict(pairs)

    final_candidates = []
    for ((payload, vec_score), cross_score) in zip(candidates, cross_scores):
        # Weighted combination
        combined_score = 0.4 * vec_score + 0.6 * cross_score

        # Optional boost for OCR / diagram content
        if payload.get("origin") == "ocr_text":
            combined_score *= VISUAL_WEIGHT

        final_candidates.append((payload, combined_score))

    # Sort by combined score
    ranked = sorted(final_candidates, key=lambda x: x[1], reverse=True)

    # Filter by minimum evidence threshold
    filtered = [r for r in ranked if r[1] > MIN_EVIDENCE_SCORE]

    return filtered[:top_k]