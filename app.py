from __future__ import annotations

from pathlib import Path

import streamlit as st

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
    "Konu 05 · Değişkenlik, Dağılım ve İlişki": render_konu05,
    "Konu 06 · Olasılığın Temelleri": render_konu06,
    "Konu 07 · Koşullu Olasılık, Bağımsızlık ve Bayes": render_konu07,
    "Konu 08 · Rassal Değişkenler ve Kesikli Dağılımlar": render_konu08,
    "Konu 09 · Binom, Poisson ve Hipergeometrik": render_konu09,
    "Konu 10 · Sürekli Rassal Değişkenler ve Normal Dağılım": render_konu10,
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
