"""Doğrudan ders bağlantıları: doğrulama, tek uygulama ve gerçek arayüz durumu."""

import pytest
from streamlit.testing.v1 import AppTest

from core.labs.registry import LABS
from core.navigation import NavigationError, experiments_for, initialize_navigation, parse_destination


def query(**values):
    return {key: [str(value)] for key, value in values.items()}


@pytest.mark.parametrize("topic", list(LABS))
def test_every_registered_target_is_addressable(topic):
    for step in LABS[topic].steps:
        dest = parse_destination(query(konu=topic[-2:], sekme="uygulama", adim=step.number))
        assert dest.initial_state()[f"{topic}_lab_step"] == step.number
        assert dest.initial_state()[f"{topic}_lab_kaynak"] == "notlar"
    for experiment in experiments_for(topic):
        dest = parse_destination(query(konu=topic[-2:], sekme="sezgi", deney=experiment.number))
        assert dict(dest.parameters) == experiment.defaults()


@pytest.mark.parametrize("values", [
    dict(konu="13"), dict(konu="1"), dict(konu="01", sekme="bad"),
    dict(konu="01", sekme="sezgi", deney="99"), dict(konu="01", adim="6"),
    dict(konu="01", adim="1.0"), dict(konu="01", kaynak="bad"), dict(sekme="sezgi"),
    dict(konu="01", sekme="sezgi", adim="1"), dict(konu="01", deney="1"),
    dict(konu="01", sekme="kendini_sina", deney="1"),
    dict(konu="01", sekme="sezgi", p_missing="1"),
    dict(konu="01", sekme="sezgi", p_n="500.5"),
    dict(konu="01", sekme="sezgi", p_c="nan"),
    dict(konu="01", sekme="sezgi", p_c="inf"),
    dict(konu="01", sekme="sezgi", p_c="100000"),
    dict(konu="01", sekme="sezgi", p_c="3.01"),
])
def test_bad_links_do_not_mutate_existing_selections(values):
    state = {"selected_topic": "konu04", "konu04_lab_step": 7}
    assert initialize_navigation(query(**values), state)
    assert state["selected_topic"] == "konu04" and state["konu04_lab_step"] == 7


def test_duplicate_fields_are_rejected():
    with pytest.raises(NavigationError):
        parse_destination({"konu": ["01", "02"]})


def test_valid_parameters_and_normal_interactions_survive_reruns():
    q = query(konu="01", sekme="sezgi", deney="1", p_c="3", p_n="500")
    state = {}
    assert initialize_navigation(q, state) is None
    assert state["konu01_sezgi1_c"] == 3.0
    state.update({"konu01_sezgi1_c": 10.0, "konu01_sezgi_deney": 2, "konu01_tab": "Uygulama"})
    initialize_navigation(q, state)
    assert state["konu01_sezgi1_c"] == 10.0
    assert state["konu01_sezgi_deney"] == 2 and state["konu01_tab"] == "Uygulama"
    initialize_navigation(query(konu="01", sekme="uygulama", adim="4"), state)
    assert state["konu01_lab_step"] == 4 and state["konu01_tab"] == "Uygulama"


@pytest.mark.parametrize("topic", list(LABS))
def test_url_selects_tab_experiment_and_slider_in_real_app(topic):
    app = AppTest.from_file("app.py", default_timeout=60)
    app.query_params.update({"konu": topic[-2:], "sekme": "sezgi", "deney": "3"})
    app.run()
    assert not app.exception
    assert app.radio(key="selected_topic").value == topic
    assert app.session_state[f"{topic}_tab"] == "Sezgi"
    assert app.segmented_control(key=f"{topic}_sezgi_deney").value == 3
    experiment = experiments_for(topic)[2]
    p = experiment.parameters[0]
    key = f"{experiment.key}_{p.key}"
    new = p.minimum if p.default != p.minimum else p.maximum
    app.slider(key=key).set_value(int(new) if p.integer else float(new)).run()
    assert not app.exception and app.slider(key=key).value == new
    app.run()
    assert app.slider(key=key).value == new


def test_lab_link_resets_alternative_source_once_and_allows_changes():
    app = AppTest.from_file("app.py", default_timeout=60).run()
    app.segmented_control(key="konu01_lab_kaynak").set_value("alternatif").run()
    app.query_params.update({"konu": "01", "sekme": "uygulama", "adim": "4"})
    app.run()
    assert not app.exception
    assert app.segmented_control(key="konu01_lab_kaynak").value == "notlar"
    assert app.segmented_control(key="konu01_lab_step").value == 4
    app.segmented_control(key="konu01_lab_kaynak").set_value("alternatif").run()
    assert app.segmented_control(key="konu01_lab_kaynak").value == "alternatif"


def test_upload_target_retains_step_and_displays_upload_panel_without_a_file():
    app = AppTest.from_file("app.py", default_timeout=60)
    app.query_params.update({"konu": "02", "sekme": "uygulama", "adim": "8", "kaynak": "kendi"})
    app.run()
    assert not app.exception and len(app.get("file_uploader")) == 1
    assert app.session_state["konu02_lab_step"] == 8
    app.run()
    assert any("Bağlantı hedefi: Adım 8" in caption.value for caption in app.caption)
    assert app.session_state["_konu02_link_step"] == 8


def test_bad_link_has_visible_error():
    app = AppTest.from_file("app.py", default_timeout=60)
    app.query_params.update({"konu": "01", "sekme": "sezgi", "deney": "99"})
    app.run()
    assert not app.exception and any("Geçersiz deney" in e.value for e in app.error)
