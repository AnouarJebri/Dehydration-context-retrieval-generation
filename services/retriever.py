from app.vector_store import client
from app.embeddings import embed_text, reranker
from app.config import COLLECTION, MIN_EVIDENCE_SCORE, VISUAL_WEIGHT
from app.graph_store import driver

def is_visual_query(query):
    visual_terms = ["schéma", "diagramme", "microscopie", "histologie", "tubule", "aquaporine", "image"]
    return any(term in query.lower() for term in visual_terms)

def retrieve(query, top_k=20):
    q_text_vec = embed_text(query)

    # Dual search
    text_results = client.search(
        collection_name=COLLECTION,
        query_vector=("text_vector", q_text_vec),
        limit=top_k
    )
    image_results = client.search(
        collection_name=COLLECTION,
        query_vector=("image_vector", q_text_vec),  # Text query projected (approx)
        limit=top_k
    )

    # Fuse with visual weight
    candidates = []
    weight = VISUAL_WEIGHT if is_visual_query(query) else 0.4
    for t, i in zip(text_results, image_results):
        fused_score = (1 - weight) * t.score + weight * i.score
        payload = t.payload if t.score > i.score else i.payload
        candidates.append((payload, fused_score))

    # Graph augmentation
    with driver.session() as session:
        graph_res = session.run(
            """
            MATCH (c:Concept)-[r:REL]->(d:Concept)
            WHERE toLower(c.name) CONTAINS toLower($q)
            RETURN c.name, r.type, d.name LIMIT 5
            """,
            q=query
        )
        for r in graph_res:
            candidates.append((
                {"chunk": f"Graph pathway: {r['c.name']} {r['r.type']} {r['d.name']}",
                 "source": "Graph"},
                0.5
            ))

    # Rerank
    texts = [c[0]["chunk"] for c in candidates]
    pairs = [(query, t) for t in texts]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    filtered = [r for r in ranked if r[1] > MIN_EVIDENCE_SCORE]

    return filtered[:5]