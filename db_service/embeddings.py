from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import AutoModel, AutoProcessor
import torch

# Text embedder
text_embed_model = SentenceTransformer("BAAI/bge-m3")

# Reranker
reranker = CrossEncoder("BAAI/bge-reranker-large")

def embed_text(text):
    return text_embed_model.encode(text).tolist()