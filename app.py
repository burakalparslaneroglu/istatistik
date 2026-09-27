"""IKT 217 İstatistik I etkileşimli ders uygulamasının kabuğu ve konu yönlendirmesi."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.codegen.base import LANGUAGES
from core.topic_registry import get_topic, list_topics
from core.ui_components import load_css
from core.ui_preferences import render_text_scale_control
from topics.konu01_veri_istatistige_giris import render as render_konu01
from topics.konu02_kategorik_verilerin_ozetlenmesi import render as render_konu02
from topics.konu03_nicel_verilerin_ozetlenmesi import render as render_konu03
from topics.konu04_merkezi_egilim_konum import render as render_konu04
from topics.konu05_degiskenlik_dagilim_iliskiler import render as render_konu05
from topics.konu06_olasiligin_temelleri import render as render_konu06
from topics.konu07_kosullu_olasilik_bayes import render as render_konu07
from topics.konu08_rassal_degiskenler_kesikli_dagilimlar import render as render_konu08
from topics.konu09_binom_poisson_hipergeometrik import render as render_konu09
from topics.konu10_surekli_rassal_degisken_normal import render as render_konu10
from topics.konu11_normal_uygulamalar_diger_surekli import render as render_konu11
from topics.konu12_ornekleme_ornekleme_dagilimlari import render as render_konu12

COURSE = "IKT 217 İstatistik I"

TOPIC_RENDERERS = {
    "konu01": render_konu01,
    "konu02": render_konu02,
    "konu03": render_konu03,
    "konu04": render_konu04,
    "konu05": render_konu05,
    "konu06": render_konu06,
    "konu07": render_konu07,
    "konu08": render_konu08,
    "konu09": render_konu09,
    "konu10": render_konu10,
    "konu11": render_konu11,
    "konu12": render_konu12,
}

st.set_page_config(page_title=COURSE, page_icon="📊", layout="wide", initial_sidebar_state="expanded")

load_css(Path(__file__).parent / "assets" / "styles.css")
render_text_scale_control()

with st.sidebar:
    st.markdown(f"## {COURSE}")
    st.caption("Etkileşimli ders uygulaması")
    selected_topic = st.radio(
        "Konu seçiniz",
        options=[topic.key for topic in list_topics()],
        format_func=lambda key: get_topic(key).label,
        key="selected_topic",
    )
    st.divider()
    st.markdown("#### Kod dili")
    st.segmented_control(
        "Kod dili", options=LANGUAGES, default=LANGUAGES[0], key="code_language",
        label_visibility="collapsed", width="stretch",
    )
    st.caption("Uygulama ve Sezgi sekmelerindeki kodlar bu dilde gösterilir.")
    st.divider()
    st.caption("Ders notları içerik, terminoloji ve konu sırası açısından bağlayıcı kaynaktır.")

TOPIC_RENDERERS[selected_topic]()
