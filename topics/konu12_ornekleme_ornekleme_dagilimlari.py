from __future__ import annotations

from statistics import NormalDist
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.question_engine import Question, render_question_card
from core.topic12_logic import (
    clt_exponential_sample_means,
    finite_population_correction,
    repeated_sample_means,
    sample_mean_se,
    sample_proportion_se,
    standardized_sample_mean,
    standardized_sample_proportion,
)
from core.ui_components import learning_goals, render_plotly, reset_widget_state, topic_header

QUESTIONS = (
    Question("Örnekleme dağılımının gözlemleri tek tek bireyler midir?", "Hayır. Gözlemler, tekrarlı örneklemlerden hesaplanan örneklem istatistikleridir."),
    Question("E(X̄)=μ neyi anlatır?", "Örneklem ortalamasının tekrarlı örneklemede anakütle ortalamasının çevresinde merkezlendiğini; yani yansız olduğunu."),
    Question("Ortalamanın standart hatası nedir?", "σ/√n. Örneklem ortalamasının örneklemden örnekleme değişkenliğini ölçer."),
    Question("Büyük n örnekleme dışı hataları otomatik olarak yok eder mi?", "Hayır. Ölçüm, kapsama, yanıtlamama veya tasarım kaynaklı sistematik hatalar büyük örneklemle ortadan kalkmaz."),
)


def _sampling_foundations() -> None:
    st.subheader("1. Anakütleden örnekleme: parametre ve istatistik")
    st.markdown("Örnekleme, anakütlenin tamamını gözlemek yerine seçilmiş bir alt kümeden bilgi üretir. Basit rassal örneklemde seçim mekanizması önceden tanımlıdır; örnekleme çerçevesi ise seçimin yapılabildiği birim listesidir.")
    cases = {
        "Türkiye'deki tüm üniversite öğrencilerinin ortalama aylık harcaması": "Parametre",
        "Seçilen 400 öğrencinin ortalama aylık harcaması": "İstatistik",
        "Tüm müşterilerin memnuniyet oranı": "Parametre",
        "Örneklemdeki memnun müşteri oranı": "İstatistik",
    }
    case = st.selectbox(
        "İfadeyi seçiniz",
        list(cases),
        key="konu12_param_case",
        on_change=reset_widget_state,
        args=("konu12_param_guess",),
    )
    guess = st.radio("Bu ifade", ["Parametre", "İstatistik"], index=None, horizontal=True, key="konu12_param_guess")
    if guess is None:
        st.caption("Önce kararınızı verin; açıklama daha sonra görünecektir.")
    elif guess == cases[case]:
        st.success(f"Doğru: {cases[case]}. Parametre anakütleyi, istatistik örneklemi özetler.")
    else:
        st.warning("Anakütlenin tamamına ait sabit özet parametredir; seçilmiş örneklemden hesaplanan özet istatistiktir.")


def _sampling_distribution_mean() -> None:
    st.subheader("2. Örneklem ortalamasının örnekleme dağılımı")
    mu = 50.0
    sigma = 15.0
    n = st.slider("Örneklem büyüklüğü n", 4, 100, 25, 1, key="konu12_xbar_n")
    reps = st.slider("Tekrarlı örneklem sayısı", 200, 3000, 1000, 200, key="konu12_xbar_reps")
    rng = np.random.default_rng(207)
    population = rng.normal(mu, sigma, 200_000)
    means = repeated_sample_means(population, n, reps, seed=207)
    theoretical_se = sample_mean_se(sigma, n)
    c1, c2, c3 = st.columns(3)
    c1.metric("Teorik merkez E(X̄)", f"{mu:.1f}")
    c2.metric("Standart hata σ/√n", f"{theoretical_se:.2f}")
    c3.metric("Simülasyon ortalaması", f"{means.mean():.2f}")

    fig = go.Figure(go.Histogram(x=means, nbinsx=35, histnorm="probability density", name="Örneklem ortalamaları"))
    xs = np.linspace(20, 80, 500)
    ys = np.exp(-0.5 * ((xs - mu) / theoretical_se) ** 2) / (theoretical_se * np.sqrt(2 * np.pi))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Teorik örnekleme dağılımı"))
    fig.update_layout(title="Tekrarlı örneklemlerde X̄ dağılımı", xaxis_range=[20, 80])
    render_plotly(fig, x_title="Örneklem ortalaması, X̄", y_title="Yoğunluk", legend_title="Gösterge", key="konu12_xbar_hist")
    st.caption("n büyüdükçe merkez değişmez; σ/√n küçüldüğü için örneklem ortalamaları μ çevresinde daha sık toplanır.")


def _se_and_clt() -> None:
    st.subheader("3. Örneklem büyüklüğü, standart hata ve Merkezi Limit Teoremi")
    sigma = st.slider("Anakütle standart sapması σ", 5.0, 40.0, 20.0, 1.0, key="konu12_se_sigma")
    max_n = 400
    ns = np.arange(1, max_n + 1)
    ses = sigma / np.sqrt(ns)
    fig = go.Figure(go.Scatter(x=ns, y=ses, mode="lines", name="Standart hata"))
    fig.update_layout(title="Örneklem büyüklüğü arttıkça standart hatanın azalması")
    render_plotly(fig, x_title="Örneklem büyüklüğü, n", y_title="Ortalamanın standart hatası, σ/√n", key="konu12_se_curve")

    st.markdown("#### Sağ çarpık anakütleden örneklem ortalamaları")
    n_clt = st.slider("CLT için örneklem büyüklüğü n", 1, 60, 5, 1, key="konu12_clt_n")
    means = clt_exponential_sample_means(n_clt, 4000, mean=1.0, seed=207)
    fig2 = go.Figure(go.Histogram(x=means, nbinsx=45, histnorm="probability density", name=f"Simülasyon: X̄, n={n_clt}"))
    clt_xs = np.linspace(0.0, 4.0, 500)
    clt_se = 1.0 / np.sqrt(n_clt)
    normal_ys = np.exp(-0.5 * ((clt_xs - 1.0) / clt_se) ** 2) / (clt_se * np.sqrt(2 * np.pi))
    fig2.add_trace(
        go.Scatter(
            x=clt_xs,
            y=normal_ys,
            mode="lines",
            name="Normal yaklaşım: N(1, 1/n)",
            line=dict(dash="dash"),
        )
    )
    fig2.update_layout(
        title="Sağa çarpık anakütlede örneklem ortalamasının biçimi",
        xaxis_range=[0, 4],
        yaxis_range=[0, 3.5],
    )
    render_plotly(
        fig2,
        x_title="Örneklem ortalaması, X̄",
        y_title="Yoğunluk",
        legend_title="Dağılım",
        key="konu12_clt_chart",
    )
    st.caption("Kesikli çizgi, aynı teorik merkez ve standart hataya sahip normal yaklaşımı gösterir. n arttıkça simülasyon histogramının bu eğriye yaklaşması beklenir.")
    st.info("Merkezi Limit Teoremi 'n=30 ise her şey kesin normaldir' kuralı değildir. Yaklaşımın ne kadar hızlı olduğu anakütle biçimine bağlıdır.")


def _probability_and_proportion() -> None:
    st.subheader("4. Örneklem ortalaması ve oranıyla olasılık")
    mu, sigma, n = 500.0, 60.0, 36
    xbar = st.slider("Örneklem ortalaması X̄ (ml)", 470.0, 530.0, 510.0, 1.0, key="konu12_mean_prob_xbar")
    z = standardized_sample_mean(xbar, mu, sigma, n)
    prob_left = NormalDist().cdf(z)
    c1, c2 = st.columns(2)
    c1.metric("Standart hata", f"{sample_mean_se(sigma, n):.1f} ml")
    c2.metric("P(X̄≤seçilen değer)", f"{prob_left:.4f}")
    st.caption(f"z=(X̄−μ)/(σ/√n)={z:.2f}; burada payda σ değil, σ/√n'dir.")

    st.markdown("#### Örneklem oranı")
    p = st.slider("Anakütle başarı oranı p", 0.05, 0.95, 0.40, 0.05, key="konu12_prop_p")
    n_prop = st.slider("Örneklem büyüklüğü n", 20, 500, 100, 10, key="konu12_prop_n")
    phat = st.slider("Gözlenen örneklem oranı p̂", 0.0, 1.0, 0.45, 0.01, key="konu12_prop_phat")
    se = sample_proportion_se(p, n_prop)
    z_prop = standardized_sample_proportion(phat, p, n_prop)
    c1, c2, c3 = st.columns(3)
    c1.metric("E(p̂)", f"{p:.2f}")
    c2.metric("SE(p̂)", f"{se:.4f}")
    c3.metric("p̂'nin z uzaklığı", f"{z_prop:.2f}")


def _fpc_estimators_methods() -> None:
    st.subheader("5. Sonlu anakütle düzeltmesi, tahmin edici özellikleri ve örnekleme hataları")
    N = st.slider("Sonlu anakütle büyüklüğü N", 100, 5000, 400, 100, key="konu12_fpc_N")
    n_max = min(N, max(20, int(N * 0.8)))
    n = st.slider("Örneklem büyüklüğü n", 10, n_max, min(100, n_max), 10, key="konu12_fpc_n")
    sigma = st.slider("Anakütle standart sapması σ", 5.0, 50.0, 20.0, 1.0, key="konu12_fpc_sigma")
    plain = sample_mean_se(sigma, n)
    fpc = finite_population_correction(N, n)
    adjusted = sample_mean_se(sigma, n, population_size=N)
    df = pd.DataFrame({"Hesap": ["Düzeltmesiz", "Sonlu anakütle düzeltmeli"], "Standart hata": [plain, adjusted]})
    fig = go.Figure(go.Bar(x=df["Hesap"], y=df["Standart hata"], text=[f"{v:.2f}" for v in df["Standart hata"]], textposition="outside"))
    fig.update_layout(title="Sonlu anakütle düzeltmesinin standart hataya etkisi", showlegend=False)
    render_plotly(fig, x_title="Standart hata hesabı", y_title="Standart hata", key="konu12_fpc_chart")
    st.caption(f"Örnekleme oranı n/N=%{100*n/N:.1f}; düzeltme çarpanı={fpc:.3f}.")

    st.markdown("#### Tahmin edici özelliğini tanı")
    props = {
        "Tekrarlı örneklemede dağılımın merkezi gerçek parametreye eşit": "Yansızlık",
        "n arttıkça gerçek parametreden büyük sapmaların olasılığı azalıyor": "Tutarlılık",
        "Aynı hedefi tahmin eden yansız tahmin edicilerden daha dar dağılıma sahip": "Etkinlik",
    }
    case = st.selectbox(
        "Durum",
        list(props),
        key="konu12_est_case",
        on_change=reset_widget_state,
        args=("konu12_est_guess",),
    )
    guess = st.radio("Özellik", ["Yansızlık", "Tutarlılık", "Etkinlik"], index=None, horizontal=True, key="konu12_est_guess")
    if guess is None:
        st.caption("Önce özelliği seçin.")
    elif guess == props[case]:
        st.success(f"Doğru: {props[case]}.")
    else:
        st.warning(f"Bu durum {props[case]} kavramını tanımlar.")

    st.markdown("#### Hikâyeden örnekleme yöntemine")
    methods = {
        "Öğrenci listesinden rassal sayı üreterek 100 kişi seçiliyor": "Basit rassal",
        "Öğrenciler sınıf düzeyine ayrılıyor ve her düzeyden rassal seçim yapılıyor": "Tabakalı",
        "Rassal bir başlangıçtan sonra listedeki her 20. kişi seçiliyor": "Sistematik",
        "Şubelerden bazıları rassal seçiliyor ve seçilen şubelerdeki öğrenciler inceleniyor": "Küme",
        "Kampüste kolay ulaşılan ilk 100 öğrenciye anket uygulanıyor": "Kolayda",
        "Araştırmacı özellikle bilgi sahibi olduğunu düşündüğü kişileri seçiyor": "Yargısal",
    }
    method_case = st.selectbox(
        "Örnekleme hikâyesi",
        list(methods),
        key="konu12_method_case",
        on_change=reset_widget_state,
        args=("konu12_method_guess",),
    )
    method_guess = st.radio(
        "Yöntem",
        ["Basit rassal", "Tabakalı", "Sistematik", "Küme", "Kolayda", "Yargısal"],
        index=None,
        horizontal=True,
        key="konu12_method_guess",
    )
    if method_guess is None:
        st.caption("Önce örnekleme yöntemini seçin.")
    elif method_guess == methods[method_case]:
        family = "olasılıklı" if method_guess in {"Basit rassal", "Tabakalı", "Sistematik", "Küme"} else "olasılıklı olmayan"
        st.success(f"Doğru: {method_guess}; bu örnek {family} örnekleme ailesindedir.")
    else:
        st.warning(f"Bu hikâye {methods[method_case]} örneklemesini tanımlar.")

    st.markdown("#### Örnekleme hatası mı, örnekleme dışı hata mı?")
    errors = {
        "Aynı tasarımla başka bir rassal örnek seçilince ortalamanın biraz değişmesi": "Örnekleme hatası",
        "Ankette gelirin sistematik olarak eksik beyan edilmesi": "Örnekleme dışı hata",
        "Örnekleme çerçevesinin bazı grupları kapsamaması": "Örnekleme dışı hata",
    }
    err_case = st.selectbox(
        "Durum",
        list(errors),
        key="konu12_error_case",
        on_change=reset_widget_state,
        args=("konu12_error_guess",),
    )
    err_guess = st.radio("Hata türü", ["Örnekleme hatası", "Örnekleme dışı hata"], index=None, horizontal=True, key="konu12_error_guess")
    if err_guess is None:
        st.caption("Sınıflandırmanızı yaptıktan sonra geri bildirim görünecek.")
    elif err_guess == errors[err_case]:
        st.success(f"Doğru: {errors[err_case]}.")
    else:
        st.warning(f"Bu örnek {errors[err_case]} kapsamındadır.")


def _integrated() -> None:
    st.subheader("6. Bütünleştirici uygulama: müşteri harcaması ve memnuniyet")
    mu, sigma, p, n = 600.0, 120.0, 0.64, 100
    se_mean = sample_mean_se(sigma, n)
    se_prop = sample_proportion_se(p, n)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("E(X̄)", "600 TL")
    c2.metric("SE(X̄)", f"{se_mean:.0f} TL")
    c3.metric("E(p̂)", f"{p:.2f}")
    c4.metric("SE(p̂)", f"{se_prop:.3f}")
    prob = NormalDist().cdf(1) - NormalDist().cdf(-1)
    st.info(f"588≤X̄≤612 aralığı μ±1 standart hatadır; normal yaklaşım altında olasılık yaklaşık %{100*prob:.1f}.")
    z70 = standardized_sample_proportion(0.70, p, n)
    st.caption(f"p̂=0,70 gözlenirse anakütle oranından yaklaşık {z70:.2f} standart hata yukarıdadır.")
    st.warning("Örneklem yalnız sadakat kartı üyelerinden seçilirse sorun büyük n ile çözülmeyebilir; kapsama/seçim mekanizması örnekleme dışı hata doğurabilir.")
    render_question_card("konu12", QUESTIONS)


def render() -> None:
    topic_header(12, "Örnekleme ve Örnekleme Dağılımları", "Tek bir örneklem sonucundan, tekrarlı örneklemede istatistiklerin nasıl dağıldığını anlamaya geçiyoruz.")
    learning_goals([
        "Anakütle, örneklem, parametre, istatistik, nokta tahmini ve örnekleme çerçevesini ayırmak.",
        "Örneklem ortalamasının örnekleme dağılımında E(X̄)=μ ve SE(X̄)=σ/√n ilişkilerini yorumlamak.",
        "Örneklem büyüklüğünün standart hatayı nasıl azalttığını ve Merkezi Limit Teoreminin biçime etkisini görselleştirmek.",
        "Örneklem oranının merkezi ve standart hatasını hesaplamak.",
        "Sonlu anakütle düzeltmesini, yansızlık–tutarlılık–etkinlik ayrımını ve örnekleme/örnekleme dışı hata farkını yorumlamak.",
    ])
    tabs = st.tabs(["Örnekleme temeli", "X̄ dağılımı", "n, SE & CLT", "X̄ ve p̂", "FPC & tahmin ediciler", "Uygulama"])
    with tabs[0]: _sampling_foundations()
    with tabs[1]: _sampling_distribution_mean()
    with tabs[2]: _se_and_clt()
    with tabs[3]: _probability_and_proportion()
    with tabs[4]: _fpc_estimators_methods()
    with tabs[5]: _integrated()
