from app.retriever import retrieve

def test_visual_boost():
    evidence = retrieve("schéma tubule rénal déshydratation")
    assert any("diagram" in e[0][0]["modality"] for e in evidence)  # Should hit visuals