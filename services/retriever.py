from db_service.embeddings import embed_text, reranker
from settings.config import driver , settings , MIN_EVIDENCE_SCORE, VISUAL_WEIGHT , client

def retrieve(query, top_k=20):
    q_text_vec = embed_text(query)

    # Text-only vector search
    text_results = client.search(
        collection_name=COLLECTION,
        query_vector=("text_vector", q_text_vec),
        limit=top_k
    )

    candidates = []

    # Collect text search results
    for t in text_results:
        candidates.append((t.payload, t.score))

    # Graph augmentation
    with driver.session() as session:
        graph_res = session.run(
            """
            MATCH (c:Concept)-[r:REL]->(d:Concept)
            WHERE toLower(c.name) CONTAINS toLower($q)
            RETURN c.name AS c_name, r.type AS r_type, d.name AS d_name
            LIMIT 5
            """,
            q=query
        )

        for r in graph_res:
            candidates.append((
                {
                    "chunk": f"Graph pathway: {r['c_name']} {r['r_type']} {r['d_name']}",
                    "source": "Graph"
                },
                0.5  # neutral prior score
            ))

    # Rerank using cross-encoder
    texts = [c[0]["chunk"] for c in candidates]
    pairs = [(query, t) for t in texts]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    filtered = [r for r in ranked if r[1] > MIN_EVIDENCE_SCORE]

    return filtered[:5]