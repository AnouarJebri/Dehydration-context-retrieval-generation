from services.retriever import retrieve
from services.prompt_builder import build_prompt
from services.generator import generate

def justify(agent_output):
    query = f"""
    Déshydratation sujet âgé.
    Phase: {agent_output['primary_prediction']}
    Agents: {agent_output['components']['agents']['agent_breakdown']}
    """

    evidence = retrieve(query)

    if not evidence:
        return {"error": "Aucune preuve clinique suffisante."}

    prompt = build_prompt(agent_output, evidence)
    justification = generate(prompt)

    return {
        "patient_id": agent_output["patient_id"],
        "clinical_justification": justification,
        #"evidence": [e[0][0] for e in evidence]  # Payloads
        "evidence": [
            {
                "chunk": payload["chunk"],
                "source": payload.get("source"),
                "page": payload.get("page"),
                "score": score
            }
            for payload, score in evidence
        ]
    }