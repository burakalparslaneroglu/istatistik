"""Konu 10: Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım.

Uygulama sekmesi ders notlarının çözümlü örneklerini (§10.3–§10.14) adım adım yeniden üretir; eğri altındaki
alanlar tablo kullanılmadan dikdörtgenlerle bulunur. Sezgi sekmesi veri üretim süreci bilinen üç kontrollü
deney sunar; varsayılan ayarlar notların örnekleridir (N(70, 10²), U(120, 140)). Kendini sına sekmesi haftanın
kavramlarını dört soru türüyle sınar.
"""

from __future__ import annotations

import streamlit as st

from core.labs.registry import get_lab
from core.labs.sezgi_konu10 import KONU10_EXPERIMENTS
from core.quiz.registry import get_quiz
from topics.lab_ui import render_lab
from topics.quiz_ui import render_quiz
from topics.shared import render_topic_header
from topics.sim_ui import render_experiments

TOPIC_KEY = "konu10"


def render() -> None:
    render_topic_header(TOPIC_KEY)
    application, intuition, self_test = st.tabs(("Uygulama", "Sezgi", "Kendini sına"))
    with application:
        render_lab(get_lab(TOPIC_KEY))
    with intuition:
        render_experiments(KONU10_EXPERIMENTS)
    with self_test:
        render_quiz(get_quiz(TOPIC_KEY))
