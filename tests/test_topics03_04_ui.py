from streamlit.testing.v1 import AppTest


TOPIC_KEYS = [
    "konu03",
    "konu04",
]


def _open_topic(key: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run(timeout=15)
    at.radio(key="selected_topic").set_value(key).run(timeout=15)
    return at


def test_topic03_renders_without_exception():
    at = _open_topic(TOPIC_KEYS[0])
    assert not at.exception
    assert any("Nicel Verilerin Tablo ve Grafiklerle Özetlenmesi" in title.value for title in at.title)


def test_topic04_renders_without_exception():
    at = _open_topic(TOPIC_KEYS[1])
    assert not at.exception
    assert any("Merkezi Eğilim ve Konum Ölçüleri" in title.value for title in at.title)
