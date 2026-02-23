import os
from unstructured.partition.pdf import partition_pdf
from PIL import Image
import io
import base64
import easyocr  # For OCR on diagrams

reader = easyocr.Reader(['fr', 'en'])  # French/English

def ingest_folder(folder="knowledge_base/"):
    docs = []
    os.makedirs("extracted_images", exist_ok=True)

    for file in os.listdir(folder):
        if not file.endswith(".pdf"):
            continue

        path = os.path.join(folder, file)

        elements = partition_pdf(
            filename=path,
            strategy="hi_res",
            infer_table_structure=True,
            extract_images_in_pdf=True,
            languages=["fra", "eng"]
        )

        for el in elements:
            modality = "text"
            image_path = None
            ocr_text = ""

            if el.category in ["Image", "Figure"]:
                modality = "diagram" if "schematic" in str(el.metadata) else "microscopy"  # Simple heuristic; improve if needed
                if hasattr(el.metadata, "image_base64"):
                    img_data = base64.b64decode(el.metadata.image_base64)
                    img = Image.open(io.BytesIO(img_data))
                    image_path = f"extracted_images/{file}_{el.id}.png"
                    img.save(image_path)

                    # OCR for text in diagrams/flowcharts
                    ocr_result = reader.readtext(image_path)
                    ocr_text = " ".join([text for _, text, _ in ocr_result])

            text_content = el.text.strip() if el.text else ocr_text

            if text_content:
                docs.append({
                    "content": text_content,
                    "modality": modality,
                    "source": file,
                    "page": getattr(el.metadata, "page_number", None),
                    "section": getattr(el.metadata, "section_title", "Unknown"),
                    "image_path": image_path
                })

    return docs