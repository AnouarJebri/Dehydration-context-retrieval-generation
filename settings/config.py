from pathlib import Path
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from neo4j import GraphDatabase

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    QDRANT_PORT: int = os.getenv("QDRANT_PORT")
    NEO4J_PORT_HOST_DB: int = os.getenv("NEO4J_PORT_HOST_DB")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")
    NEO4J_USER: str = os.getenv("NEO4J_USER")
    VERSION: str = os.getenv("VERSION")
    PORT: int = int(os.getenv("PORT"))
    NEO4J_PORT_RN_DB: int = int(os.getenv("NEO4J_PORT_RN_DB"))
    COLLECTION: str = os.getenv("COLLECTION")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")

settings = Settings()
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
MIN_EVIDENCE_SCORE = 0.45
VISUAL_WEIGHT = 0.6