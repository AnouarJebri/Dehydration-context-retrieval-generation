from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from services.justification import justify
from services.audit_logger import log_case
from ingest import ingest_folder
from chunking import chunk_docs
from vectore_store import store_chunks
import shutil
import os
from typing import List

app = FastAPI(title="Clinical Justification API", version="1.0")

# ---------------------------
# Health check
# ---------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ---------------------------
# Justification endpoint
# ---------------------------
@app.post("/justify")
async def justify_patient(agent_output: dict):
    """
    Input: agent_output dict containing:
    - patient_id
    - primary_prediction
    - components: { agents: { agent_breakdown } }
    """
    try:
        result = justify(agent_output)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        
        # Log the case asynchronously (can be done in background later)
        log_case(agent_output.get("patient_id"), result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# Ingestion endpoint
# ---------------------------
@app.post("/ingest")
async def ingest_pdfs(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload multiple PDF files. Ingest them, chunk, and store embeddings in vector DB.
    """
    try:
        tmp_folder = "tmp_uploads"
        os.makedirs(tmp_folder, exist_ok=True)
        uploaded_paths = []

        for file in files:
            path = os.path.join(tmp_folder, file.filename)
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_paths.append(path)

        # Run ingestion and storage in the background
        if background_tasks:
            background_tasks.add_task(process_and_store_docs, tmp_folder)

        return {"message": f"{len(files)} files received. Processing in background."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))