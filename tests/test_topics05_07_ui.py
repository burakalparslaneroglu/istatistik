from streamlit.testing.v1 import AppTest


TOPIC_LABELS = [
    "Konu 05 · Değişkenlik, Dağılım ve İlişki",
    "Konu 06 · Olasılığın Temelleri",
    "Konu 07 · Koşullu Olasılık, Bağımsızlık ve Bayes",
]


def _open_topic(label: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=20)
    at.run(timeout=20)
    at.radio(key="selected_topic").set_value(label).run(timeout=20)
    return at


def test_topic05_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[0])
    assert not at.exception
    assert any("Değişkenlik" in title.value for title in at.title)


def test_topic06_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[1])
    assert not at.exception
    assert any("Olasılığın Temelleri" in title.value for title in at.title)


def test_topic07_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[2])
    assert not at.exception
    assert any("Koşullu Olasılık" in title.value for title in at.title)
