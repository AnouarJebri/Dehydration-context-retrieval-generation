from qdrant_client.models import PointStruct, VectorParams
from settings.config import client , settings
from db_service.embeddings import embed_text , text_embed_model
from db_service.ingest import ingest_folder

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

def process_and_store_docs(folder_path):
    """
    1. Ingest PDFs
    2. Chunk documents
    3. Store embeddings in vector DB
    4. Cleanup temp folder
    """
    from db_service.chunking import chunk_docs
    try:
        docs = ingest_folder(folder_path)
        chunks = chunk_docs(docs)
        store_chunks(chunks)

    finally:
        # Always cleanup temporary folder
        shutil.rmtree(folder_path, ignore_errors=True)