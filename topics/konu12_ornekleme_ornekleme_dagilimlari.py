"""Konu 12: Örnekleme, Nokta Tahmini ve Örnekleme Dağılımları.

Uygulama sekmesi ders notlarının çözümlü örneklerini (§12.6–§12.15) adım adım yeniden üretir. Sezgi sekmesi veri
üretim süreci bilinen üç kontrollü deney sunar: tutarlılık (Şekil 12.13'ün yolu, tohum 217), Merkezi Limit Teoremi
(Şekil 12.8'in üstel anakütlesi) ve örneklem oranının dağılımı (Şekil 12.10). Kendini sına sekmesi haftanın
kavramlarını dört soru türüyle sınar.
"""

from __future__ import annotations

import streamlit as st

from core.labs.registry import get_lab
from core.labs.sezgi_konu12 import KONU12_EXPERIMENTS
from core.quiz.registry import get_quiz
from topics.lab_ui import render_lab
from topics.quiz_ui import render_quiz
from topics.shared import render_topic_header
from topics.sim_ui import render_experiments

TOPIC_KEY = "konu12"


def render() -> None:
    render_topic_header(TOPIC_KEY)
    application, intuition, self_test = st.tabs(("Uygulama", "Sezgi", "Kendini sına"))
    with application:
        render_lab(get_lab(TOPIC_KEY))
    with intuition:
        render_experiments(KONU12_EXPERIMENTS)
    with self_test:
        render_quiz(get_quiz(TOPIC_KEY))
