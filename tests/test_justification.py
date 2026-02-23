import pytest
import json
from app.justification import justify
from app.retriever import retrieve  # for mocking/isolation if needed

# Sample valid agent output (minimal realistic shape)
VALID_AGENT_OUTPUT = {
    "patient_id": "P12345",
    "primary_prediction": "déshydratation hypernatrémique modérée",
    "components": {
        "agents": {
            "agent_breakdown": ["confusion", "hypotension orthostatique", "oligurie"]
        }
    }
}

EMPTY_AGENT_OUTPUT = {
    "patient_id": "P999",
    "primary_prediction": "inconnu",
    "components": {"agents": {"agent_breakdown": []}}
}

MALFORMED_AGENT_OUTPUT = {
    "patient_id": "P000",
    # missing primary_prediction and components
}

@pytest.mark.integration  # or @pytest.mark.slow if retrieval is real
def test_justification_has_required_sections():
    """
    Verify the generated justification follows the strict structured format.
    """
    result = justify(VALID_AGENT_OUTPUT)

    assert "error" not in result, "Should not return error on valid input"
    assert "clinical_justification" in result

    justification = result["clinical_justification"]

    # Check for the 6 mandatory numbered sections
    expected_sections = [
        "1. Résumé du risque",
        "2. Physiologique",
        "3. Cognitif",
        "4. Contextuel",
        "5. Citations",
        "6. Actions recommandées"
    ]

    for section in expected_sections:
        assert section in justification, f"Missing section: {section}"

    assert "patient_id" in result
    assert result["patient_id"] == VALID_AGENT_OUTPUT["patient_id"]


@pytest.mark.integration
def test_refusal_when_no_evidence():
    """
    When retrieval returns nothing (or very low score), should refuse politely.
    """
    result = justify(EMPTY_AGENT_OUTPUT)

    assert "error" in result
    assert "Aucune preuve" in result["error"] or "insuffisante" in result["error"]


@pytest.mark.integration
def test_handles_visual_evidence_in_citations():
    """
    If visual chunks (diagrams, histology) are retrieved, they should appear
    in citations with figure/page reference.
    """
    # Force a visual-heavy query to increase chance of hitting image chunks
    # (assumes you already ingested some PDFs with figures)
    visual_query_result = retrieve("schéma aquaporine-2 tubule collecteur déshydratation âgé")

    if not visual_query_result:
        pytest.skip("No visual chunks found in KB ? run ingestion first")

    # At least one should be a diagram or microscopy
    has_visual = any(
        payload.get("modality") in ["diagram", "microscopy"] or
        payload.get("image_path") is not None
        for (payload, _), _ in visual_query_result
    )

    assert has_visual, "Visual query should retrieve at least one diagram/image"

    # Now run full justification
    result = justify(VALID_AGENT_OUTPUT)

    justification = result["clinical_justification"]

    # Look for typical figure citation patterns we put