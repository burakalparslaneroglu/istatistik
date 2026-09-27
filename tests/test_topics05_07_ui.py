from streamlit.testing.v1 import AppTest


def _open_topic(key: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=20)
    at.run(timeout=20)
    at.radio(key="selected_topic").set_value(key).run(timeout=20)
    return at


def test_topic07_renders_without_exception():
    at = _open_topic("konu07")
    assert not at.exception
    assert any("Koşullu Olasılık" in title.value for title in at.title)
