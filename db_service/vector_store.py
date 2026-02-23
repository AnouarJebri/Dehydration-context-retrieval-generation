from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from app.config import COLLECTION, QDRANT_HOST, QDRANT_PORT
from app.embeddings import embed_text, embed_image

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def store_chunks(chunks):
    text_dim = text_embed_model.get_sentence_embedding_dimension()
    image_dim = 1024  # CONCH output dim (adjust if using DINOv2: 1024)

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config={
            "text_vector": VectorParams(size=text_dim, distance="Cosine"),
            "image_vector": VectorParams(size=image_dim, distance="Cosine")
        }
    )

    points = []

    for idx, c in enumerate(chunks):
        text_vec = embed_text(c["chunk"])
        image_vec = embed_image(c.get("image_path"))

        vectors = {
            "text_vector": text_vec,
            "image_vector": image_vec if image_vec else [0.0] * image_dim  # Null handling
        }

        points.append(
            PointStruct(
                id=idx,
                vector=vectors,
                payload=c
            )
        )

    client.upsert(collection_name=COLLECTION, points=points)