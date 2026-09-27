from streamlit.testing.v1 import AppTest


TOPIC_KEYS = [
    "konu05",
    "konu06",
    "konu07",
]


def _open_topic(key: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=20)
    at.run(timeout=20)
    at.radio(key="selected_topic").set_value(key).run(timeout=20)
    return at


def test_topic05_renders_without_exception():
    at = _open_topic(TOPIC_KEYS[0])
    assert not at.exception
    assert any("Değişkenlik" in title.value for title in at.title)


def test_topic06_renders_without_exception():
    at = _open_topic(TOPIC_KEYS[1])
    assert not at.exception
    assert any("Olasılığın Temelleri" in title.value for title in at.title)


def test_topic07_renders_without_exception():
    at = _open_topic(TOPIC_KEYS[2])
    assert not at.exception
    assert any("Koşullu Olasılık" in title.value for title in at.title)
