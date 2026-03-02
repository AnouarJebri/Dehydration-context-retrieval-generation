from qdrant_client.models import PointStruct, VectorParams
from settings.config import client , settings
from db_service.embeddings import embed_text , text_embed_model

text_dim = text_embed_model.get_sentence_embedding_dimension()

def store_chunks(chunks):
    # Only text vector
    client.recreate_collection(
        collection_name=settings.COLLECTION,
        vectors_config=VectorParams(size=text_dim, distance="Cosine")
    )

    points = []

    for idx, c in enumerate(chunks):
        text_vec = embed_text(c["chunk"])

        points.append(
            PointStruct(
                id=c["chunk_id"],
                vector=text_vec,
                payload=c
            )
        )

    client.upsert(collection_name=settings.COLLECTION, points=points)