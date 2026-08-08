from __future__ import annotations

from math import exp, pi, sqrt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.question_engine import Question, render_question_card
from core.topic11_logic import (
    binomial_exact_probability,
    binomial_normal_approx_probability,
    binomial_normal_params,
    continuity_bounds,
    exponential_cdf,
    exponential_interval_probability,
    exponential_survival,
    normal_probability,
    normal_quantile,
    normal_approximation_suitable,
    std_normal_probability,
)
from core.ui_components import learning_goals, render_plotly, reset_widget_state, topic_header

QUESTIONS = (
    Question("Standart normal tablo değeri Φ(z) hangi alanı verir?", "Bu derste Φ(z)=P(Z≤z), yani z'nin solundaki kümülatif alanı verir."),
    Question("P(Z>z) nasıl bulunur?", "1−Φ(z) ile."),
    Question("Binomun normal yaklaşımında süreklilik düzeltmesi neden kullanılır?", "Kesikli tam sayı olayını sürekli normal alanıyla daha doğru temsil etmek için sınırlar 0,5 birim kaydırılır."),
    Question("Üstel dağılım hangi tür değişkenler için uygundur?", "Bir olay gerçekleşene veya bir işlem tamamlanana kadar geçen pozitif bekleme/süre değişkenleri için."),
)


def _normal_pdf(x: np.ndarray, mu: float = 0.0, sigma: float = 1.0) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def _standard_normal_areas() -> None:
    st.subheader("1. Standart normal alanda doğru bölgeyi seç")
    event = st.radio("İstenen alan", ["Sol kuyruk", "Sağ kuyruk", "İki değer arası"], horizontal=True, key="konu11_std_event")
    a = st.slider("Birinci z sınırı", -3.0, 3.0, 1.5, 0.1, key="konu11_std_a")
    b = None
    if event == "İki değer arası":
        b = st.slider("İkinci z sınırı", -3.0, 3.0, -0.5, 0.1, key="konu11_std_b")
    prob = std_normal_probability(event, a, b)
    st.metric("İstenen olasılık", f"{prob:.4f}")

    xs = np.linspace(-3.8, 3.8, 600)
    ys = _normal_pdf(xs)
    if event == "Sol kuyruk":
        mask = xs <= a
        label = f"P(Z≤{a:.1f})"
    elif event == "Sağ kuyruk":
        mask = xs >= a
        label = f"P(Z>{a:.1f})"
    else:
        lo, hi = sorted((a, float(b)))
        mask = (xs >= lo) & (xs <= hi)
        label = f"P({lo:.1f}≤Z≤{hi:.1f})"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Standart normal yoğunluk"))
    fig.add_trace(go.Scatter(x=np.r_[xs[mask], xs[mask][-1], xs[mask][0]], y=np.r_[ys[mask], 0, 0], fill="toself", mode="lines", name=label))
    fig.update_layout(title="Standart normal eğride seçilen alan", xaxis_range=[-3.8, 3.8], yaxis_range=[0, 0.43])
    render_plotly(fig, x_title="Standartlaştırılmış değer, z", y_title="Olasılık yoğunluğu, φ(z)", legend_title="Gösterge", key="konu11_std_chart")
    if event == "Sol kuyruk" and abs(a - 1.5) < 1e-9:
        st.info("Ders notundaki referans: P(Z≤1,50)=0,9332.")


def _original_and_inverse() -> None:
    st.subheader("2. Özgün ölçekten z'ye, olasılıktan eşik değere")
    mu = st.slider("Ortalama μ", 0.0, 120.0, 70.0, 1.0, key="konu11_orig_mu")
    sigma = st.slider("Standart sapma σ", 1.0, 30.0, 10.0, 1.0, key="konu11_orig_sigma")
    event = st.radio("Olay", ["Sol kuyruk", "Sağ kuyruk", "İki değer arası"], horizontal=True, key="konu11_orig_event")
    a = st.slider("Birinci x sınırı", float(mu - 3 * sigma), float(mu + 3 * sigma), float(mu + 1.5 * sigma), 1.0, key="konu11_orig_a")
    b = None
    if event == "İki değer arası":
        b = st.slider("İkinci x sınırı", float(mu - 3 * sigma), float(mu + 3 * sigma), float(mu - sigma), 1.0, key="konu11_orig_b")
    prob = normal_probability(event, a, mu, sigma, b)
    st.metric("Olasılık", f"{prob:.4f}")
    st.caption(f"Birinci sınırın z-skoru: z={(a-mu)/sigma:.2f}.")

    st.markdown("#### Ters normal: alan biliniyor, eşik aranıyor")
    left_area = st.slider("Eşiğin solundaki alan", 0.01, 0.99, 0.90, 0.01, key="konu11_inverse_p")
    cutoff = normal_quantile(left_area, mu, sigma)
    st.metric("Eşik değer", f"{cutoff:.2f}")
    if mu == 70 and sigma == 10 and abs(left_area - 0.90) < 1e-9:
        st.info("Üst %10'luk gruba giriş için sol alan %90'dır; eşik yaklaşık 82,82'dir.")


def _binomial_normal() -> None:
    st.subheader("3. Binom dağılımının normal yaklaştırması")
    n = st.slider("Deneme sayısı n", 10, 300, 100, 5, key="konu11_bin_n")
    p = st.slider("Başarı olasılığı p", 0.05, 0.95, 0.10, 0.05, key="konu11_bin_p")
    event = st.selectbox("Binom olayı", ["X = x", "X ≤ x", "X ≥ x", "a ≤ X ≤ b"], key="konu11_bin_event")
    x = st.slider("x", 0, n, min(12, n), 1, key="konu11_bin_x")
    upper = None
    if event == "a ≤ X ≤ b":
        upper = st.slider("b", 0, n, min(max(x, 20), n), 1, key="konu11_bin_b")

    mu, sigma = binomial_normal_params(n, p)
    suitable = normal_approximation_suitable(n, p)
    c1, c2, c3 = st.columns(3)
    c1.metric("μ=np", f"{mu:.2f}")
    c2.metric("σ=√np(1−p)", f"{sigma:.2f}")
    c3.metric("Yaklaşım koşulu", "Uygun" if suitable else "Zayıf")
    if not suitable:
        st.warning("np≥5 ve n(1−p)≥5 koşullarından en az biri sağlanmıyor; normal yaklaşım güvenilir olmayabilir.")

    exact = binomial_exact_probability(n, p, event, x, upper)
    approx = binomial_normal_approx_probability(n, p, event, x, upper)
    approx_table = binomial_normal_approx_probability(n, p, event, x, upper, z_decimals=2)
    lo, hi = continuity_bounds(event, x, upper)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tam binom olasılığı", f"{exact:.4f}")
    c2.metric("Normal yaklaşım (yuvarlanmamış z)", f"{approx:.4f}")
    c3.metric("z'ler 2 ondalığa yuvarlanırsa", f"{approx_table:.4f}")
    bounds_text = f"{lo:.1f}" if hi is None else f"{hi:.1f}" if lo is None else f"{lo:.1f} – {hi:.1f}"
    st.caption(f"Süreklilik düzeltmesi sonrası normal sınır(lar): {bounds_text}.")

    xs_disc = np.arange(0, n + 1)
    pmf = np.array([binomial_exact_probability(n, p, "X = x", int(k)) for k in xs_disc])
    xmin = max(0, int(mu - 4.5 * sigma))
    xmax = min(n, int(mu + 4.5 * sigma) + 1)
    x_cont = np.linspace(xmin - 0.5, xmax + 0.5, 500)
    y_cont = _normal_pdf(x_cont, mu, sigma)
    fig = go.Figure()
    maskd = (xs_disc >= xmin) & (xs_disc <= xmax)
    fig.add_trace(go.Bar(x=xs_disc[maskd], y=pmf[maskd], name="Binom olasılığı"))
    fig.add_trace(go.Scatter(x=x_cont, y=y_cont, mode="lines", name="Normal yaklaşım"))
    fig.update_layout(title="Kesikli binom ve sürekli normal yaklaşımının karşılaştırılması")
    render_plotly(fig, x_title="Başarı sayısı, x", y_title="Olasılık / yoğunluk", legend_title="Dağılım", key="konu11_bin_chart")
    if n == 100 and abs(p - 0.10) < 1e-9 and event == "X = x" and x == 12:
        st.info("Ders notundaki tablo hesabında z₁=0,50 ve z₂≈0,83 kullanıldığı için sonuç 0,1052'dir. Yuvarlanmamış z₂=0,8333… ile doğrudan CDF hesabı yaklaşık 0,1062 verir.")


def _exponential() -> None:
    st.subheader("4. Üstel dağılım: sayı değil bekleme süresi")
    mean = st.slider("Ortalama bekleme süresi μ (dakika)", 1.0, 60.0, 15.0, 1.0, key="konu11_exp_mean")
    event = st.radio("Olay", ["X ≤ x", "X > x", "a < X ≤ b"], horizontal=True, key="konu11_exp_event")
    x = st.slider("x (dakika)", 0.0, 90.0, 18.0, 1.0, key="konu11_exp_x")
    b = None
    if event == "X ≤ x":
        prob = exponential_cdf(x, mean)
        lo, hi = 0.0, x
    elif event == "X > x":
        prob = exponential_survival(x, mean)
        lo, hi = x, 5 * mean
    else:
        b = st.slider("b (dakika)", 0.0, 90.0, 30.0, 1.0, key="konu11_exp_b")
        prob = exponential_interval_probability(x, b, mean)
        lo, hi = sorted((x, b))
    st.metric("İstenen olasılık", f"{prob:.4f}")
    st.caption(f"Üstel dağılımda E(X)=σ={mean:.1f} dakika; Var(X)={mean**2:.1f} dakika².")

    xmax = max(60.0, 5 * mean, hi)
    xs = np.linspace(0, xmax, 500)
    ys = np.exp(-xs / mean) / mean
    shade = (xs >= lo) & (xs <= hi)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Üstel yoğunluk"))
    fig.add_trace(go.Scatter(x=np.r_[xs[shade], xs[shade][-1], xs[shade][0]], y=np.r_[ys[shade], 0, 0], fill="toself", mode="lines", name="Seçilen olasılık alanı"))
    fig.update_layout(title="Üstel bekleme süresi dağılımı")
    render_plotly(fig, x_title="Bekleme / tamamlanma süresi (dakika)", y_title="Olasılık yoğunluğu, f(x)", legend_title="Gösterge", key="konu11_exp_chart")
    st.info("Poisson belirli bir aralıktaki olay sayısını; üstel dağılım olaylar arasındaki süreyi modellemek için kullanılır.")


def _model_choice_and_integrated() -> None:
    st.subheader("5. Hikâyeden doğru modele")
    scenarios = {
        "100 müşteriden satın alanların sayısı": "Binom",
        "Bir saatte gelen müşteri sayısı": "Poisson",
        "20 üründen yerine koymadan seçilen 4 üründeki kusurlu sayısı": "Hipergeometrik",
        "Dolum miktarının çan biçimli sürekli dağılımı": "Normal",
        "10–20 dakika arasında eşit yoğunluklu servis süresi": "Tek-düze",
        "Bir sonraki müşteri gelene kadar geçen süre": "Üstel",
    }
    scenario = st.selectbox(
        "Hikâye",
        list(scenarios),
        key="konu11_model_story",
        on_change=reset_widget_state,
        args=("konu11_model_guess",),
    )
    guess = st.radio("Modelinizi seçiniz", ["Binom", "Poisson", "Hipergeometrik", "Normal", "Tek-düze", "Üstel"], index=None, key="konu11_model_guess")
    if guess is None:
        st.caption("Önce modelinizi seçin; geri bildirim seçimden sonra görünecektir.")
    elif guess == scenarios[scenario]:
        st.success(f"Doğru: {scenarios[scenario]}.")
    else:
        st.warning(f"Bu hikâyede belirleyici mekanizma {scenarios[scenario]} dağılımına karşılık geliyor. Değişkenin sayı mı süre mi olduğuna ve örnekleme mekanizmasına bakın.")

    st.markdown("#### Bütünleştirici örnek")
    st.markdown("Bir çağrı merkezinde saatte ortalama 4 müşteri çağrısı geliyor. Olay sayısı için Poisson; iki çağrı arasındaki bekleme süresi için ortalaması 15 dakika olan üstel model aynı sürecin iki farklı yüzünü anlatır.")
    render_question_card("konu11", QUESTIONS)


def render() -> None:
    topic_header(11, "Normal Dağılım Uygulamaları ve Diğer Sürekli Dağılımlar", "Standart normal alanlardan özgün ölçeğe, ters normal eşiklere, binomun normal yaklaştırmasına ve üstel bekleme sürelerine geçiyoruz.")
    learning_goals([
        "Φ(z)=P(Z≤z) sol kümülatif alanını kullanarak sol, sağ ve aralık olasılıklarını hesaplamak.",
        "X~N(μ,σ²) değişkenini z-skoruna dönüştürmek ve ters normal sorularında eşik değer bulmak.",
        "Binom dağılımının normal yaklaşım koşullarını ve 0,5 süreklilik düzeltmesini uygulamak.",
        "Üstel dağılımla bekleme/tamamlanma sürelerini modellemek ve Poisson ile bağlantısını kurmak.",
        "Hikâyenin veri üretim mekanizmasına göre uygun dağılımı seçmek.",
    ])
    tabs = st.tabs(["Standart normal", "Özgün ölçek & ters normal", "Binom → normal", "Üstel", "Model seçimi"])
    with tabs[0]: _standard_normal_areas()
    with tabs[1]: _original_and_inverse()
    with tabs[2]: _binomial_normal()
    with tabs[3]: _exponential()
    with tabs[4]: _model_choice_and_integrated()
