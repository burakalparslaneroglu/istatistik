from pathlib import Path


def test_topic08_classification_waits_for_selection():
    text = Path("topics/konu08_rassal_degiskenler_kesikli_dagilimlar.py").read_text(encoding="utf-8")
    assert 'key="konu08_rv_type"' in text
    assert "index=None" in text
    assert "if answer is None" in text


def test_topic09_model_choice_waits_for_selection():
    text = Path("topics/konu09_binom_poisson_hipergeometrik.py").read_text(encoding="utf-8")
    assert 'key="konu09_model_guess"' in text
    assert "index=None" in text
    assert "if guess is None" in text


def test_topic10_normal_shape_uses_fixed_coordinate_system():
    text = Path("topics/konu10_surekli_rassal_degisken_normal.py").read_text(encoding="utf-8")
    assert "xaxis_range=[-45, 45]" in text
    assert "yaxis_range=[0, 0.82]" in text
