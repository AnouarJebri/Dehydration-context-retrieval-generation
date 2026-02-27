from pathlib import Path
import os
from dotenv import load_dotenv

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

settings = Settings()