import os

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

COLLECTION = "clinical_dehydration_kb"

MIN_EVIDENCE_SCORE = 0.45
VISUAL_WEIGHT = 0.6  # Boost for image_vector if query visual

#All of it to be repeated
#Create a setting class and load all of the .env in it