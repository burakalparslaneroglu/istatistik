"""Uygulama kabuğu ve yeni mimariye taşınan konuların uçtan uca duman testleri."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _run_app() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=60).run()


def _markdown(app: AppTest) -> str:
    return "\n".join(item.value for item in app.markdown)


def test_app_opens_on_topic_01_with_three_tabs() -> None:
    app = _run_app()
    assert not app.exception
    assert app.radio(key="selected_topic").value == "konu01"
    assert "Veri ve İstatistiğe Giriş" in _markdown(app)
    assert [tab.label for tab in app.tabs][:3] == ["Uygulama", "Sezgi", "Kendini sına"]
    assert app.segmented_control(key="konu01_lab_step").value == 1
    assert {"Gözlem sayısı n": "8", "Değişken sayısı": "4"}.items() <= {m.label: m.value for m in app.metric}.items()


def test_every_lab_step_renders_in_both_languages() -> None:
    app = _run_app()
    for topic, steps in (("konu01", 5), ("konu02", 12), ("konu03", 11), ("konu04", 10), ("konu05", 12),
                         ("konu06", 9), ("konu07", 10), ("konu08", 12), ("konu09", 8), ("konu10", 7), ("konu11", 10),
                         ("konu12", 6)):
        app.radio(key="selected_topic").set_value(topic).run()
        for language in ("Python", "R"):
            app.segmented_control(key="code_language").set_value(language).run()
            for number in range(1, steps + 1):
                app.segmented_control(key=f"{topic}_lab_step").set_value(number).run()
                assert not app.exception, (topic, language, number)
                assert any(item.value.startswith(f"Adım {number}:") for item in app.subheader)


def test_lab_step_shows_the_notes_numbers_in_turkish_format() -> None:
    app = _run_app()
    app.segmented_control(key="konu01_lab_step").set_value(4).run()
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Geçme oranı"] == "0,625"
    assert metrics["Geçme yüzdesi"] == "%62,5"
    assert metrics["Ortalama puan"] == "64,0"


def test_percentile_step_shows_the_location_and_value_as_in_the_notes() -> None:
    app = _run_app()
    app.radio(key="selected_topic").set_value("konu04").run()
    app.segmented_control(key="konu04_lab_step").set_value(7).run()
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Konum L₆₀"] == "7,8"
    assert metrics["60. yüzdelik P₆₀"] == "54,8"


def test_every_experiment_runs_and_reacts_to_its_sliders() -> None:
    app = _run_app()
    app.slider(key="konu01_sezgi1_c").set_value(3.0).run()
    leaders = {metric.label: metric.value for metric in app.metric}
    assert leaders["Önde olan şube, kod 1-2-3"] == leaders["Önde olan şube, kod 1-2-c"] == "A"
    app.slider(key="konu01_sezgi1_c").set_value(10.0).run()
    assert {metric.label: metric.value for metric in app.metric}["Önde olan şube, kod 1-2-c"] == "B"
    for topic in ("konu01", "konu02", "konu03", "konu04", "konu05", "konu06", "konu07", "konu08", "konu09",
                  "konu10", "konu11", "konu12"):
        app.radio(key="selected_topic").set_value(topic).run()
        for number in (1, 2, 3):
            app.segmented_control(key=f"{topic}_sezgi_deney").set_value(number).run()
            assert not app.exception, (topic, number)


def test_quiz_checks_an_answer_and_lists_sections_to_review() -> None:
    app = _run_app()
    app.radio(key="konu01_quiz_k01").set_value(1).run()
    app.button(key="konu01_quiz_check_k01").click().run()
    assert not app.exception
    assert any("Tekrar edilecek bölümler" in item.value and "§1.1" in item.value for item in app.markdown)


def test_topic_switch_keeps_text_scale_and_code_language() -> None:
    app = _run_app()
    app.select_slider(key="text_scale_label").set_value("%120").run()
    app.segmented_control(key="code_language").set_value("R").run()
    app.radio(key="selected_topic").set_value("konu02").run()
    assert not app.exception
    assert app.session_state["text_scale"] == 1.2
    assert app.session_state["code_language"] == "R"
    assert "Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi" in _markdown(app)
