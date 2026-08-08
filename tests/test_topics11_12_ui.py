from streamlit.testing.v1 import AppTest

TOPIC_LABELS = [
    "Konu 11 · Normal Uygulamaları ve Diğer Sürekli Dağılımlar",
    "Konu 12 · Örnekleme ve Örnekleme Dağılımları",
]


def _open_topic(label: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=25)
    at.run(timeout=25)
    at.radio(key="selected_topic").set_value(label).run(timeout=25)
    return at


def test_topic11_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[0])
    assert not at.exception
    assert any("Normal Olasılıklar ve Üstel Dağılım" in title.value for title in at.title)


def test_topic12_renders_without_exception():
    at = _open_topic(TOPIC_LABELS[1])
    assert not at.exception
    assert any("Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları" in title.value for title in at.title)
