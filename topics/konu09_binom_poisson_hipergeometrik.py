"""Konu 09: Binom, Poisson ve Hipergeometrik Dağılımlar.

Uygulama sekmesi ders notlarının çözümlü örneklerini (§9.3–§9.12) adım adım yeniden üretir. Sezgi
sekmesi veri üretim süreci bilinen üç kontrollü deney sunar; varsayılan ayarlar notların örnekleridir
(Şekil 9.6, §9.4, Tablo 9.1). Kendini sına sekmesi haftanın kavramlarını dört soru türüyle sınar.
"""

from __future__ import annotations

import streamlit as st

from core.labs.registry import get_lab
from core.labs.sezgi_konu09 import KONU09_EXPERIMENTS
from core.quiz.registry import get_quiz
from topics.lab_ui import render_lab
from topics.quiz_ui import render_quiz
from topics.shared import render_topic_header
from topics.sim_ui import render_experiments

TOPIC_KEY = "konu09"


def render() -> None:
    render_topic_header(TOPIC_KEY)
    application, intuition, self_test = st.tabs(("Uygulama", "Sezgi", "Kendini sına"))
    with application:
        render_lab(get_lab(TOPIC_KEY))
    with intuition:
        render_experiments(KONU09_EXPERIMENTS)
    with self_test:
        render_quiz(get_quiz(TOPIC_KEY))
