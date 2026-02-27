import json

def build_prompt(agent_output, evidence):
    evidence_text = ""

    for (payload, _), score in evidence:
        img_desc = f" (Figure from {payload.get('image_path')} )" if payload.get("image_path") else ""
        evidence_text += f"""
        - {payload['chunk'][:250]}{img_desc}
        Source: {payload.get('source')} p.{payload.get('page')}
        Score: {score:.2f}
        """

        return f"""
        Vous êtes un assistant clinique hospitalier spécialisé en gériatrie.

        RÈGLES STRICTES:
        - Justifiez uniquement avec les preuves fournies, incluant diagrammes et images.
        - Chaque affirmation doit être liée à une source ou figure.
        - Ne posez aucun diagnostic.
        - Si les preuves sont insuffisantes, dites-le clairement.

        SORTIE AGENT:
        {json.dumps(agent_output, indent=2)}

        CONTEXTE CLINIQUE:
        {evidence_text}

        TÂCHE:
        Rédiger une justification médicale structurée.

        FORMAT:
        1. Résumé du risque
        2. Physiologique
        3. Cognitif
        4. Contextuel
        5. Citations
        6. Actions recommandées
        """