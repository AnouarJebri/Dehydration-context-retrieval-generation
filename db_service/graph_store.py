from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from app.generator import generate  # Reuse Mistral

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def extract_entities_relations(chunk):
    prompt = f"""
    Extract medical entities (Conditions, Structures, Mechanisms, Symptoms) and relations (CAUSE, AFFECTE, IMPLIQUE) from:
    {chunk[:1000]}

    Output JSON: [{{"entity1": "X", "relation": "Y", "entity2": "Z"}}]
    """
    response = generate(prompt)
    try:
        return eval(response)  # Parse list of dicts
    except:
        return []

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