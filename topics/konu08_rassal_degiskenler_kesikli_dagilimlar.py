from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.question_engine import Question, render_question_card
from core.topic08_logic import (
    ADDON_PROBS, ADDON_VALUES, JOINT_PROBS,
    distribution_sd, distribution_variance, event_probability, expected_value,
    independent_joint, joint_moments, marginals, profit_distribution,
    running_mean_simulation,
)
from core.ui_components import learning_goals, render_plotly, topic_header

QUESTIONS = (
    Question("Rassal değişken ile gözlenen x değeri aynı şey midir?", "Hayır. X deney gerçekleşmeden önce olası sayısal sonuçları tanımlar; x ise X'in belirli bir gerçekleşmesidir."),
    Question("Kesikli bir olasılık dağılımında olasılıkların toplamı kaç olmalıdır?", "1 olmalıdır ve her olasılık 0 ile 1 arasında olmalıdır."),
    Question("E(X)=1,8 olması tek bir işlemde 1,8 ürün gözleneceği anlamına gelir mi?", "Hayır. Beklenen değer uzun dönem olasılık ağırlıklı ortalamadır; X'in alabileceği değerlerden biri olmak zorunda değildir."),
    Question("Aynı beklenen değere sahip iki dağılım aynı riske sahip olmak zorunda mıdır?", "Hayır. Varyans ve standart sapma yayılımı ayrıca ölçer."),
    Question("Bağımsız X ve Y için ortak olasılık nasıl yazılır?", "Her değer çifti için P(X=x,Y=y)=P(X=x)P(Y=y)."),
)


def _rv_types() -> None:
    st.subheader("1. Deney sonucundan sayıya")
    mapping = pd.DataFrame({"Deney sonucu": ["Ek ürün yok", "Bir ek ürün", "İki ek ürün", "Üç ek ürün"], "Rassal değişken değeri": ["X=0", "X=1", "X=2", "X=3"]})
    st.dataframe(mapping, hide_index=True, width="stretch")
    st.info("Rassal değişken yeni bir deney yaratmaz; aynı deney sonuçlarını sayısal biçimde kodlar.")

    scenarios = {
        "15 dakikada gelen müşteri sayısı": "Kesikli",
        "Bir müşterinin bekleme süresi": "Sürekli",
        "100 üründeki kusurlu ürün sayısı": "Kesikli",
        "Bir paketin ağırlığı": "Sürekli",
        "Bir ayda alınan izin günü sayısı": "Kesikli",
    }
    selected = st.selectbox("Bir rassal değişken seçiniz", list(scenarios), key="konu08_rv_scenario")
    answer = st.radio("Sınıflandırmanız", ["Kesikli", "Sürekli"], horizontal=True, key="konu08_rv_type")
    if answer == scenarios[selected]:
        st.success(f"Doğru: **{selected}** → {scenarios[selected].lower()} rassal değişken.")
    else:
        st.warning("Tekrar düşünün: değişken sayılabilir ayrı değerler mi, yoksa bir aralıktaki ara değerleri de alabilir mi?")


def _pmf_lab() -> None:
    st.subheader("2. Kesikli olasılık dağılımını oku")
    df = pd.DataFrame({"Ek ürün sayısı x": ADDON_VALUES.astype(int), "P(X=x)": ADDON_PROBS})
    st.dataframe(df, hide_index=True, width="stretch")
    fig = go.Figure(go.Bar(x=df["Ek ürün sayısı x"], y=df["P(X=x)"], text=[f"{p:.2f}" for p in ADDON_PROBS], textposition="outside"))
    fig.update_layout(title="Bir işlemde satın alınan ek ürün sayısının dağılımı", showlegend=False, yaxis_range=[0, .42])
    render_plotly(fig, x_title="Ek ürün sayısı, x", y_title="Olasılık, P(X=x)", key="konu08_pmf")

    event = st.selectbox("Bir olay seçiniz", ["X = 3", "X ≥ 2", "X < 4", "X ≠ 2"], key="konu08_event")
    probs = {
        "X = 3": event_probability(ADDON_VALUES, ADDON_PROBS, lower=3, upper=3),
        "X ≥ 2": event_probability(ADDON_VALUES, ADDON_PROBS, lower=2),
        "X < 4": event_probability(ADDON_VALUES, ADDON_PROBS, upper=4, inclusive_upper=False),
        "X ≠ 2": 1 - event_probability(ADDON_VALUES, ADDON_PROBS, lower=2, upper=2),
    }
    st.metric("Seçilen olayın olasılığı", f"{probs[event]:.2f}")
    st.caption("Kesikli değişkende ≥ ile > aynı olay değildir; eşitlik çizgisi hangi x değerlerinin toplandığını değiştirir.")


def _expectation_variance() -> None:
    st.subheader("3. Beklenen değer, uzun dönem ortalaması ve yayılım")
    mu = expected_value(ADDON_VALUES, ADDON_PROBS)
    var = distribution_variance(ADDON_VALUES, ADDON_PROBS)
    sd = distribution_sd(ADDON_VALUES, ADDON_PROBS)
    c1, c2, c3 = st.columns(3)
    c1.metric("E(X)", f"{mu:.2f} ürün")
    c2.metric("Var(X)", f"{var:.3f} ürün²")
    c3.metric("σX", f"{sd:.2f} ürün")

    repetitions = st.slider("Tekrarlanan işlem sayısı", 20, 1000, 200, 20, key="konu08_reps")
    running = running_mean_simulation(ADDON_VALUES, ADDON_PROBS, repetitions, seed=207)
    x = np.arange(1, repetitions + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=running, mode="lines", name="Gerçekleşen kümülatif ortalama"))
    fig.add_trace(go.Scatter(x=[1, repetitions], y=[mu, mu], mode="lines", name="E(X)=1,80", line=dict(dash="dash")))
    fig.update_layout(title="Tekrarlı deneylerde gerçekleşen ortalamanın beklenen değere yaklaşması")
    render_plotly(fig, x_title="Tekrarlanan işlem sayısı", y_title="Gerçekleşen ortalama ek ürün sayısı", legend_title="Gösterge", key="konu08_running_mean")

    st.markdown("#### Aynı merkez, farklı risk")
    a_values, a_probs = np.array([0, 2, 4]), np.array([.25, .50, .25])
    b_values, b_probs = np.array([1, 2, 3]), np.array([.25, .50, .25])
    comp = pd.DataFrame({"Dağılım": ["A", "B"], "E(X)": [expected_value(a_values, a_probs), expected_value(b_values, b_probs)], "Var(X)": [distribution_variance(a_values, a_probs), distribution_variance(b_values, b_probs)]})
    st.dataframe(comp, hide_index=True, width="stretch")
    st.info("İki dağılımın beklenen değeri 2'dir; ancak A'nın varyansı 2, B'nin varyansı 0,5'tir. Merkez aynı olsa da belirsizlik aynı değildir.")


def _joint_distribution() -> None:
    st.subheader("4. İki rassal değişken: ortak ve marjinal dağılım")
    px, py = marginals(JOINT_PROBS)
    moments = joint_moments(JOINT_PROBS)
    table = pd.DataFrame(JOINT_PROBS, index=["Y=0", "Y=1", "Y=2"], columns=["X=0", "X=1", "X=2"])
    st.dataframe(table, width="stretch")
    fig = go.Figure(go.Heatmap(z=JOINT_PROBS, x=[0,1,2], y=[0,1,2], text=np.round(JOINT_PROBS,2), texttemplate="%{text:.2f}", colorbar_title="Olasılık"))
    fig.update_layout(title="Teklif sayısı ile satış sayısının ortak olasılık dağılımı")
    render_plotly(fig, x_title="Teklif talebi sayısı, X", y_title="Satışa dönüşen teklif sayısı, Y", key="konu08_joint_heatmap")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("E(X)", f"{moments['E_X']:.2f}")
    c2.metric("E(Y)", f"{moments['E_Y']:.2f}")
    c3.metric("Cov(X,Y)", f"{moments['Cov']:.4f}")
    c4.metric("Corr(X,Y)", f"{moments['Corr']:.3f}")
    st.caption(f"X marjinali: {px.round(2).tolist()} · Y marjinali: {py.round(2).tolist()}")
    st.warning("Bu ortak dağılım bağımsız değildir. Örneğin P(X=1,Y=1)=0,25 iken P(X=1)P(Y=1)=0,1225'tir.")
    assert not independent_joint(JOINT_PROBS)


def _integrated() -> None:
    st.subheader("5. Bütünleştirici uygulama: talep ve günlük kâr")
    profits, probs = profit_distribution()
    df = pd.DataFrame({"Talep X": ADDON_VALUES.astype(int), "Olasılık": probs, "Kâr Π (TL)": profits.astype(int)})
    st.dataframe(df, hide_index=True, width="stretch")
    e_profit = expected_value(profits, probs)
    sd_profit = distribution_sd(profits, probs)
    c1, c2 = st.columns(2)
    c1.metric("Beklenen günlük kâr E(Π)", f"{e_profit:,.0f} TL")
    c2.metric("Kârın standart sapması", f"{sd_profit:,.0f} TL")
    fig = go.Figure(go.Bar(x=df["Kâr Π (TL)"], y=df["Olasılık"], text=[f"{p:.2f}" for p in probs], textposition="outside"))
    fig.update_layout(title="Talep dağılımından türetilen günlük kâr dağılımı", showlegend=False)
    render_plotly(fig, x_title="Günlük kâr (TL)", y_title="Olasılık", key="konu08_profit")
    render_question_card("konu08", QUESTIONS)


def render() -> None:
    topic_header(8, "Rassal Değişkenler ve Kesikli Olasılık Dağılımları", "Olaylardan sayısal rassal değişkenlere geçiyor; bir dağılımın merkezini, yayılımını ve iki değişkenli yapısını inceliyoruz.")
    learning_goals([
        "Bir rassal deney sonucunu sayısal rassal değişkenle ifade etmek ve X ile x'i ayırmak.",
        "Kesikli ve sürekli rassal değişkenleri sınıflandırmak.",
        "Kesikli olasılık dağılımını okumak ve geçerlilik koşullarını kullanmak.",
        "Beklenen değer, varyans ve standart sapmayı hesaplayıp uzun dönem/risk açısından yorumlamak.",
        "Ortak ve marjinal dağılımları okuyup kovaryans, korelasyon ve bağımsızlık bağlantısını görmek.",
    ])
    tabs = st.tabs(["Rassal değişken", "Olasılık dağılımı", "Beklenen değer & risk", "Ortak dağılım", "Uygulama"])
    with tabs[0]: _rv_types()
    with tabs[1]: _pmf_lab()
    with tabs[2]: _expectation_variance()
    with tabs[3]: _joint_distribution()
    with tabs[4]: _integrated()
