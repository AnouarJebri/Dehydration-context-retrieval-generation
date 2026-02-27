from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from app.config import COLLECTION, QDRANT_HOST, QDRANT_PORT
from app.embeddings import embed_text , text_embed_model

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
text_dim = text_embed_model.get_sentence_embedding_dimension()

def store_chunks(chunks):
    # Only text vector
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=text_dim, distance="Cosine")
    )

    points = []

    for idx, c in enumerate(chunks):
        text_vec = embed_text(c["chunk"])

        points.append(
            PointStruct(
                id=idx,
                vector=text_vec,
                payload=c
            )
        )

    client.upsert(collection_name=COLLECTION, points=points)