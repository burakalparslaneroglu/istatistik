from pathlib import Path


def test_css_contains_shared_topic_badge():
    css = Path("assets/styles.css").read_text(encoding="utf-8")
    assert ".topic-badge" in css
    assert "--course-text-scale" in css
