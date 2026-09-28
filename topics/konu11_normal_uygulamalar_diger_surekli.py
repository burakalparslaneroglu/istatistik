"""Konu 11: Normal Olasılıklar ve Üstel Dağılım.

Uygulama sekmesi ders notlarının çözümlü örneklerini (§11.1–§11.13) adım adım yeniden üretir; Φ değerleri notlardaki
tablo kuralıyla (z iki, Φ dört ondalık basamak) ve yuvarlamasız olarak gösterilir. Sezgi sekmesi veri üretim süreci
bilinen üç kontrollü deney sunar; varsayılan ayarlar notların örnekleridir (N(70, 10²), Bin(100, 0,10), saatte 12
müşteri). Kendini sına sekmesi haftanın kavramlarını dört soru türüyle sınar.
"""

from __future__ import annotations

import streamlit as st

from core.labs.registry import get_lab
from core.labs.sezgi_konu11 import KONU11_EXPERIMENTS
from core.quiz.registry import get_quiz
from topics.lab_ui import render_lab
from topics.quiz_ui import render_quiz
from topics.shared import render_topic_header
from topics.sim_ui import render_experiments

TOPIC_KEY = "konu11"


def render() -> None:
    render_topic_header(TOPIC_KEY)
    application, intuition, self_test = st.tabs(("Uygulama", "Sezgi", "Kendini sına"))
    with application:
        render_lab(get_lab(TOPIC_KEY))
    with intuition:
        render_experiments(KONU11_EXPERIMENTS)
    with self_test:
        render_quiz(get_quiz(TOPIC_KEY))
