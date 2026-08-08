from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.ui_components import load_css
from core.ui_preferences import render_text_scale_control
from topics.konu01_veri_istatistige_giris import render as render_konu01
from topics.konu02_kategorik_verilerin_ozetlenmesi import render as render_konu02
from topics.konu03_nicel_verilerin_ozetlenmesi import render as render_konu03
from topics.konu04_merkezi_egilim_konum import render as render_konu04


st.set_page_config(
    page_title="İKT 207 İstatistik",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css(Path("assets/styles.css"))
render_text_scale_control()

st.sidebar.markdown("## İKT 207 İstatistik")
st.sidebar.caption("Etkileşimli ders uygulaması")

TOPICS = {
    "Konu 01 · Veri ve İstatistiğe Giriş": render_konu01,
    "Konu 02 · Kategorik Verilerin Özetlenmesi": render_konu02,
    "Konu 03 · Nicel Verilerin Özetlenmesi": render_konu03,
    "Konu 04 · Merkezi Eğilim ve Konum Ölçüleri": render_konu04,
}

selected_topic = st.sidebar.radio(
    "Konu seçiniz",
    options=list(TOPICS),
    key="selected_topic",
)

st.sidebar.divider()
st.sidebar.caption(
    "Ders notları içerik, terminoloji ve konu sırası açısından bağlayıcı kaynaktır."
)

TOPICS[selected_topic]()
