from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.question_engine import Question, render_question_card
from core.topic09_logic import (
    binomial_distribution, binomial_mean_var, binomial_pmf,
    choose_distribution, convert_poisson_rate,
    hypergeometric_distribution, hypergeometric_mean_var, hypergeometric_pmf,
    poisson_distribution, poisson_pmf,
)
from core.ui_components import learning_goals, render_plotly, topic_header

QUESTIONS = (
    Question("Binom dağılımında başarı olasılığı p denemeden denemeye değişebilir mi?", "Hayır. Binom deneyinde p sabittir ve denemeler bağımsızdır."),
    Question("Poisson modelinde temel parametre λ neyi gösterir?", "İncelenen zaman/uzay aralığındaki beklenen olay sayısını."),
    Question("Hipergeometrik dağılımı binomdan ayıran temel örnekleme özelliği nedir?", "Sonlu anakütleden yerine koymadan seçim; bu nedenle başarı olasılığı seçimler boyunca değişebilir."),
    Question("'En az bir başarı' binomda hangi kısa yolla hesaplanabilir?", "Tümleyenle: 1-P(X=0)=1-(1-p)^n."),
)

SCENARIOS = {
    "20 bağımsız müşterinin her biri %15 olasılıkla satın alıyor; satın alan sayısı": "Binom",
    "10 dakikada gelen destek çağrısı sayısı; ortalama 4": "Poisson",
    "30 pakette 6 hasarlı var; yerine koymadan 5 paket seçiliyor": "Hipergeometrik",
    "Sağa çarpık sürekli bekleme süresi": "Bu üç modelden biri olduğu söylenemez",
}


def _model_choice() -> None:
    st.subheader("1. Önce deney yapısı, sonra formül")
    scenario = st.selectbox("Hikâyeyi seçiniz", list(SCENARIOS), key="konu09_story")
    guess = st.radio("Uygun model", ["Binom", "Poisson", "Hipergeometrik", "Bu üç modelden biri olduğu söylenemez"], key="konu09_model_guess")
    if guess == SCENARIOS[scenario]:
        st.success(f"Doğru: **{SCENARIOS[scenario]}**.")
    else:
        st.warning("Modeli değişken adından değil, deneme mekanizmasından seçin: sabit n mi, sabit aralık mı, yoksa sonlu havuzdan yerine koymadan seçim mi?")
    st.markdown("**Karar özeti:** sabit n + iki sonuç + sabit p + bağımsızlık → Binom; sabit aralıkta olay sayısı → Poisson; sonlu anakütleden yerine koymadan seçim → Hipergeometrik.")


def _binomial() -> None:
    st.subheader("2. Binom laboratuvarı")
    n = st.slider("Deneme sayısı, n", 1, 30, 8, 1, key="konu09_bin_n")
    p = st.slider("Başarı olasılığı, p", 0.05, 0.95, 0.25, 0.05, key="konu09_bin_p")
    x = st.slider("Tam başarı sayısı, x", 0, n, min(2, n), 1, key="konu09_bin_x")
    xs, ps = binomial_distribution(n, p)
    mean, var = binomial_mean_var(n, p)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("P(X=x)", f"{binomial_pmf(n,p,x):.4f}")
    c2.metric("P(X≥1)", f"{1-binomial_pmf(n,p,0):.4f}")
    c3.metric("E(X)=np", f"{mean:.2f}")
    c4.metric("Var(X)", f"{var:.2f}")
    fig = go.Figure(go.Bar(x=xs, y=ps, text=[f"{v:.3f}" if v>.02 else "" for v in ps], textposition="outside"))
    fig.update_layout(title=f"Binom dağılımı: n={n}, p={p:.2f}", showlegend=False)
    render_plotly(fig, x_title="Başarı sayısı, x", y_title="Olasılık, P(X=x)", key="konu09_binom_chart")
    if n == 8 and np.isclose(p, .25) and x == 2:
        st.info("Ders notundaki varsayılan: P(X=2)≈0,3115; E(X)=2; Var(X)=1,5.")


def _poisson() -> None:
    st.subheader("3. Poisson laboratuvarı")
    hourly_rate = st.slider("Saatlik ortalama olay sayısı", 1.0, 30.0, 12.0, 1.0, key="konu09_pois_rate")
    minutes = st.slider("İncelenen süre (dakika)", 5, 60, 15, 5, key="konu09_pois_minutes")
    lam = convert_poisson_rate(hourly_rate, 60, minutes)
    x = st.slider("Tam olay sayısı, x", 0, max(10, int(lam+5)), min(2, max(10, int(lam+5))), 1, key="konu09_pois_x")
    xs, ps = poisson_distribution(lam)
    c1, c2, c3 = st.columns(3)
    c1.metric("İlgili aralık için λ", f"{lam:.2f}")
    c2.metric("P(X=x)", f"{poisson_pmf(lam,x):.4f}")
    c3.metric("E(X)=Var(X)", f"{lam:.2f}")
    fig = go.Figure(go.Bar(x=xs, y=ps))
    fig.update_layout(title=f"Poisson dağılımı: λ={lam:.2f}", showlegend=False)
    render_plotly(fig, x_title="Olay sayısı, x", y_title="Olasılık, P(X=x)", key="konu09_poisson_chart")
    if hourly_rate == 12 and minutes == 15 and x == 2:
        st.info("Saatte 12 çağrı → 15 dakikada λ=3. Ders notundaki P(X=2)≈0,2240.")


def _hypergeometric() -> None:
    st.subheader("4. Hipergeometrik laboratuvarı")
    N = st.slider("Anakütle büyüklüğü, N", 10, 80, 20, 1, key="konu09_hyp_N")
    r = st.slider("Anakütlede başarı sayısı, r", 1, N-1, min(5, N-1), 1, key="konu09_hyp_r")
    n = st.slider("Yerine koymadan seçilen birim sayısı, n", 1, N, min(4, N), 1, key="konu09_hyp_n")
    xs, ps = hypergeometric_distribution(N, r, n)
    x_default = 1 if 1 in xs else int(xs[0])
    x = st.select_slider("Örneklemdeki başarı sayısı, x", options=xs.tolist(), value=x_default, key="konu09_hyp_x")
    mean, var = hypergeometric_mean_var(N, r, n)
    c1, c2, c3 = st.columns(3)
    c1.metric("P(X=x)", f"{hypergeometric_pmf(N,r,n,int(x)):.4f}")
    c2.metric("E(X)", f"{mean:.2f}")
    c3.metric("Var(X)", f"{var:.4f}")
    fig = go.Figure(go.Bar(x=xs, y=ps))
    fig.update_layout(title=f"Hipergeometrik dağılım: N={N}, r={r}, n={n}", showlegend=False)
    render_plotly(fig, x_title="Seçilen başarı sayısı, x", y_title="Olasılık, P(X=x)", key="konu09_hyper_chart")
    if N == 20 and r == 5 and n == 4 and int(x) == 1:
        st.info("Ders notundaki varsayılan: P(X=1)≈0,4696; E(X)=1; Var(X)≈0,6316.")


def _compare_integrated() -> None:
    st.subheader("5. Aynı işletme, üç farklı belirsizlik mekanizması")
    rows = [
        ("Dönüşüm", "20 bağımsız müşteri, p=0,15", "Binom", 1-(.85**20)),
        ("Çağrı yükü", "10 dakikada ortalama 4 çağrı", "Poisson", poisson_pmf(4,0)),
        ("Kalite denetimi", "30 pakette 6 hasarlı; 5 seçim", "Hipergeometrik", hypergeometric_pmf(30,6,5,1)),
    ]
    df = pd.DataFrame(rows, columns=["Problem", "Hikâye", "Model", "İstenen olasılık"])
    st.dataframe(df, hide_index=True, width="stretch")
    fig = go.Figure(go.Bar(x=df["Problem"], y=100*df["İstenen olasılık"], text=[f"%{100*v:.1f}" for v in df["İstenen olasılık"]], textposition="outside"))
    fig.update_layout(title="Üç farklı mekanizmada örnek olasılıklar", showlegend=False)
    render_plotly(fig, x_title="Belirsizlik problemi", y_title="İstenen olasılık (%)", key="konu09_integrated")
    st.caption("Aynı sektör ve aynı gün içinde farklı veri üretim mekanizmaları farklı dağılımlar gerektirir.")
    render_question_card("konu09", QUESTIONS)


def render() -> None:
    topic_header(9, "Binom, Poisson ve Hipergeometrik Dağılımlar", "Özel bir dağılımı formülden değil, rassal deney yapısından seçmeyi öğreniyoruz.")
    learning_goals([
        "Binom, Poisson ve hipergeometrik deneylerin ayırt edici koşullarını tanımak.",
        "Binomda tam/en az başarı olasılıklarını, beklenen değer ve varyansı hesaplamak.",
        "Poisson'da λ parametresini doğru zaman/uzay aralığına dönüştürmek.",
        "Yerine koymadan sonlu anakütle seçiminde hipergeometrik modeli kullanmak.",
        "Benzer görünen hikâyelerde kritik mekanizma farkına göre doğru modeli seçmek.",
    ])
    tabs = st.tabs(["Modeli seç", "Binom", "Poisson", "Hipergeometrik", "Karşılaştırma"])
    with tabs[0]: _model_choice()
    with tabs[1]: _binomial()
    with tabs[2]: _poisson()
    with tabs[3]: _hypergeometric()
    with tabs[4]: _compare_integrated()
