from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import AutoModel, AutoProcessor
import torch

# Text embedder
text_embed_model = SentenceTransformer("BAAI/bge-m3")

# Image embedder: CONCH (SOTA for histology/diagrams)
processor = AutoProcessor.from_pretrained("mahmoodlab/conch")
image_embed_model = AutoModel.from_pretrained("mahmoodlab/conch")

# Reranker
reranker = CrossEncoder("BAAI/bge-reranker-large")

def embed_text(text):
    return text_embed_model.encode(text).tolist()

def embed_image(image_path):
    if image_path is None:
        return None
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = image_embed_model(**inputs)
        vec = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()  # Pooling
    return vec