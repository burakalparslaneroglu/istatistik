"""Konu 01: Veri ve İstatistiğe Giriş.

Uygulama sekmesi ders notlarının çözümlü örneklerini (Tablo 1.1, Şekil 1.4, §1.7) adım adım yeniden
üretir. Sezgi sekmesi veri üretim süreci bilinen üç kontrollü deney sunar. Kendini sına sekmesi
haftanın kavramlarını dört soru türüyle sınar.
"""

from __future__ import annotations

import streamlit as st

from core.labs.registry import get_lab
from core.labs.sezgi_konu01 import KONU01_EXPERIMENTS
from core.quiz.registry import get_quiz
from topics.lab_ui import render_lab
from topics.quiz_ui import render_quiz
from topics.shared import render_topic_header
from topics.sim_ui import render_experiments

TOPIC_KEY = "konu01"


def render() -> None:
    render_topic_header(TOPIC_KEY)
    application, intuition, self_test = st.tabs(("Uygulama", "Sezgi", "Kendini sına"))
    with application:
        render_lab(get_lab(TOPIC_KEY))
    with intuition:
        render_experiments(KONU01_EXPERIMENTS)
    with self_test:
        render_quiz(get_quiz(TOPIC_KEY))
