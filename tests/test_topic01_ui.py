from streamlit.testing.v1 import AppTest


def test_app_renders_topic01_without_exception():
    at = AppTest.from_file("app.py", default_timeout=10)
    at.run(timeout=10)
    assert not at.exception
    assert any("Veri ve İstatistiğe Giriş" in title.value for title in at.title)


def test_text_scale_change_does_not_raise_exception():
    at = AppTest.from_file("app.py", default_timeout=10)
    at.run(timeout=10)
    at.select_slider(key="text_scale_label").set_value("%130").run(timeout=10)
    assert not at.exception
