from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=500, chunk_overlap=100)

def chunk_docs(docs):
    chunks = []

    for d in docs:
        parts = splitter.split_text(d["content"]) if d["modality"] == "text" else [d["content"]]

        for i, p in enumerate(parts):
            chunks.append({
                "chunk": p,
                "modality": d["modality"],
                "source": d["source"],
                "page": d["page"],
                "section": d["section"],
                "image_path": d.get("image_path"),
                "chunk_id": f"{d['source']}_p{d['page']}_{i}"
            })

    return chunks