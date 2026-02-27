from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from app.generator import generate  # Reuse Mistral

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def extract_entities_relations(chunk: str) -> list[dict]:
    prompt = f"""
    You are an expert medical information extraction system.

    TASK:
    Extract medical entities and relations from the text.

    ENTITY TYPES:
    - Condition (Cognitif , Physical , Contextual)
    - Structure
    - Mechanism
    - Symptom

    RELATIONS:
    - CAUSE
    - AFFECTE
    - IMPLIQUE

    STRICT RULES:
    - Output ONLY valid JSON
    - No explanations
    - No markdown
    - No comments
    - Return a JSON array

    FORMAT:
    [
    {{"entity1": "X", "relation": "Y", "entity2": "Z"}}
    ]

    TEXT:
    {chunk[:1000]}
    """

    response = generate(prompt)

    try:
        cleaned = _clean_llm_json(response)
        data = json.loads(cleaned)

        if isinstance(data, list):
            return [
                triplet
                for triplet in data
                if _is_valid_triplet(triplet)
            ]
        return []

    except Exception as e:
        print(f"?? Extraction parse failed: {e}")
        return []


def _clean_llm_json(text: str) -> str:
    """
    Removes markdown fences and extra text.
    """
    text = text.strip()

    # remove ```json fences if present
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    # try to extract JSON array if model added text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def _is_valid_triplet(obj: dict) -> bool:
    required = {"entity1", "relation", "entity2"}
    return isinstance(obj, dict) and required.issubset(obj.keys())

def add_concept_relation(e1, rel, e2):
    with driver.session() as session:
        session.run(
            """
            MERGE (a:Concept {name: $e1})
            MERGE (b:Concept {name: $e2})
            MERGE (a)-[r:REL {type: $rel}]->(b)
            """,
            e1=e1, rel=rel, e2=e2
        )

def build_graph_from_chunks(chunks):
    for c in chunks:
        extractions = extract_entities_relations(c["chunk"])
        for ext in extractions:
            add_concept_relation(ext["entity1"], ext["relation"], ext["entity2"])