from streamlit.testing.v1 import AppTest

TOPIC_LABELS = [
    "Konu 08 · Rassal Değişkenler ve Kesikli Dağılımlar",
    "Konu 09 · Binom, Poisson ve Hipergeometrik",
    "Konu 10 · Sürekli Rassal Değişkenler ve Normal Dağılım",
]


def _open_topic(label: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=20)
    at.run(timeout=20)
    at.radio(key="selected_topic").set_value(label).run(timeout=20)
    return at


def test_topic08_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[0])
    assert not at.exception
    assert any("Rassal Değişkenler" in title.value for title in at.title)


def test_topic09_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[1])
    assert not at.exception
    assert any("Binom" in title.value for title in at.title)


def test_topic10_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[2])
    assert not at.exception
    assert any("Sürekli Rassal Değişkenler" in title.value for title in at.title)
