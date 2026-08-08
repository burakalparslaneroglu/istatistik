from streamlit.testing.v1 import AppTest


TOPIC_LABELS = [
    "Konu 02 · Kategorik Verilerin Özetlenmesi",
    "Konu 03 · Nicel Verilerin Özetlenmesi",
    "Konu 04 · Merkezi Eğilim ve Konum Ölçüleri",
]


def _open_topic(label: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=15)
    at.run(timeout=15)
    at.radio(key="selected_topic").set_value(label).run(timeout=15)
    return at


def test_topic02_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[0])
    assert not at.exception
    assert any("Kategorik Verilerin Özetlenmesi" in title.value for title in at.title)


def test_topic03_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[1])
    assert not at.exception
    assert any("Nicel Verilerin Özetlenmesi" in title.value for title in at.title)


def test_topic04_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[2])
    assert not at.exception
    assert any("Merkezi Eğilim ve Konum Ölçüleri" in title.value for title in at.title)
