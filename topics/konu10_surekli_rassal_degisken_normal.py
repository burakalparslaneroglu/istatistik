from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.question_engine import Question, render_question_card
from core.topic10_logic import (
    empirical_rule_bounds, from_z, normal_density, normal_interval_probability,
    uniform_density, uniform_mean_var, uniform_probability, z_score,
)
from core.ui_components import learning_goals, render_plotly, reset_widget_state, topic_header

QUESTIONS = (
    Question("Sürekli bir rassal değişkende P(X=x) neden 0'dır?", "Olasılık tek bir noktanın yüksekliğiyle değil, eğri altındaki alanla ölçülür; tek noktanın genişliği ve dolayısıyla alanı 0'dır."),
    Question("Tek-düze dağılımda doğru ifade 'bütün değerler eşit olasılıklıdır' mıdır?", "Teknik olarak hayır. Her tekil noktanın olasılığı 0'dır; eşit uzunluktaki alt aralıklar eşit olasılıklıdır."),
    Question("Normal dağılımda μ ve σ neyi belirler?", "μ konumu/merkezi, σ yayılımı/genişliği belirler."),
    Question("z=1,5 ne anlama gelir?", "Değer ortalamanın 1,5 standart sapma üzerindedir."),
    Question("Standartlaştırma olasılık alanını değiştirir mi?", "Hayır. Yalnız yatay eksenin ölçeğini standart sapma birimine dönüştürür."),
)


def _continuous_idea() -> None:
    st.subheader("1. Süreklide olasılık: yükseklik değil alan")
    width = st.slider("500 ml çevresindeki aralık genişliği (ml)", 0.0, 20.0, 10.0, 1.0, key="konu10_point_width")
    mu, sigma = 500.0, 10.0
    lo, hi = mu-width/2, mu+width/2
    prob = normal_interval_probability(lo, hi, mu, sigma) if width > 0 else 0.0
    st.metric("Bu aralığın olasılığı", f"{prob:.4f}")
    st.info("Aralık genişliği 0 olduğunda tek bir noktaya, X=500'e, ineriz ve olasılık 0 olur. Sürekli dağılımda olasılık alanla ölçülür.")


def _uniform() -> None:
    st.subheader("2. Tek-düze dağılım: eşit uzunluk, eşit olasılık")
    a = st.number_input("Alt sınır a", value=120.0, step=1.0, key="konu10_u_a")
    b = st.number_input("Üst sınır b", value=140.0, step=1.0, key="konu10_u_b")
    if b <= a:
        st.error("b, a'dan büyük olmalıdır.")
        return
    c = st.slider("Olasılık aralığının alt sınırı c", float(a), float(b), float(max(a, min(b, 128.0))), key="konu10_u_c")
    d = st.slider("Olasılık aralığının üst sınırı d", float(a), float(b), float(max(c, min(b, 136.0))), key="konu10_u_d")
    if d < c:
        c, d = d, c
    dens = uniform_density(a,b)
    prob = uniform_probability(a,b,c,d)
    mean, var = uniform_mean_var(a,b)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Yoğunluk", f"{dens:.4f}")
    c2.metric("P(c≤X≤d)", f"{prob:.3f}")
    c3.metric("Ortalama μ", f"{mean:.2f}")
    c4.metric("Standart sapma σ", f"{np.sqrt(var):.2f}")

    xs = np.linspace(a, b, 200)
    ys = np.full_like(xs, dens)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Yoğunluk"))
    shade_x = np.linspace(c,d,100)
    fig.add_trace(go.Scatter(x=np.r_[shade_x, d, c], y=np.r_[np.full_like(shade_x,dens),0,0], fill="toself", mode="lines", name="Seçilen olasılık alanı"))
    fig.update_layout(title=f"Tek-düze dağılım U({a:g}, {b:g})")
    render_plotly(fig, x_title="Sürekli değişken değeri, x", y_title="Olasılık yoğunluğu, f(x)", legend_title="Gösterge", key="konu10_uniform")
    if a == 120 and b == 140 and c == 128 and d == 136:
        st.info("Ders notundaki varsayılan: yoğunluk 0,05 ve P(128≤X≤136)=0,40.")

    narrow_b = st.slider("Yoğunluk > 1 örneğinde üst sınır", 0.1, 1.0, 0.5, 0.05, key="konu10_density_gt1")
    st.caption(f"U(0,{narrow_b:.2f}) için yoğunluk yüksekliği {1/narrow_b:.2f}'dir. 1'i aşabilir; olasılık olan toplam alan yine 1'dir.")


def _normal_shape() -> None:
    st.subheader("3. Normal eğrinin konumu ve yayılımı")
    mu = st.slider("Ortalama μ", -20.0, 20.0, 0.0, 1.0, key="konu10_norm_mu")
    sigma = st.slider("Standart sapma σ", 0.5, 6.0, 1.0, 0.5, key="konu10_norm_sigma")
    xs = np.linspace(-45, 45, 700)
    ys = normal_density(xs, mu, sigma)
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", name="Normal yoğunluk"))
    fig.add_vline(x=mu, line_dash="dash")
    fig.update_layout(title=f"Normal dağılım: μ={mu:g}, σ={sigma:g}", xaxis_range=[-45, 45], yaxis_range=[0, 0.82])
    render_plotly(fig, x_title="Rassal değişken değeri, x", y_title="Olasılık yoğunluğu, f(x)", key="konu10_normal_shape")
    st.caption("Eksenler sabit tutulmuştur: μ değiştikçe eğri aynı X–Y koordinat sisteminde sağa veya sola kayar. σ büyüdükçe eğri genişler ve basıklaşır; toplam alan 1 olarak kalır.")


def _empirical_z() -> None:
    st.subheader("4. 68–95–99,7 kuralı ve z-dönüşümü")
    mu = st.slider("Sınav ortalaması μ", 40.0, 90.0, 70.0, 1.0, key="konu10_z_mu")
    sigma = st.slider("Sınav standart sapması σ", 2.0, 20.0, 10.0, 1.0, key="konu10_z_sigma")
    score = st.slider("Öğrencinin puanı x", 20.0, 120.0, 85.0, 1.0, key="konu10_z_x")
    z = z_score(score, mu, sigma)
    st.metric("z-skoru", f"{z:.2f}")
    st.success(f"x={score:g}, μ={mu:g}, σ={sigma:g} → değer ortalamanın **{abs(z):.2f} standart sapma {'üzerinde' if z>0 else 'altında' if z<0 else 'tam merkezinde'}**.")

    k = st.radio("Ampirik kural aralığı", [1,2,3], horizontal=True, key="konu10_emp_k")
    lo, hi, pct = empirical_rule_bounds(mu,sigma,k)
    st.info(f"Yaklaşık %{pct:.1f} alan: {lo:.1f} ≤ X ≤ {hi:.1f}.")
    xs = np.linspace(mu-4*sigma, mu+4*sigma, 400)
    ys = normal_density(xs,mu,sigma)
    mask=(xs>=lo)&(xs<=hi)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",name="Normal yoğunluk"))
    fig.add_trace(go.Scatter(x=np.r_[xs[mask],hi,lo],y=np.r_[ys[mask],0,0],fill="toself",mode="lines",name=f"μ±{k}σ"))
    fig.add_vline(x=score, line_dash="dot")
    fig.update_layout(title="Normal dağılımda seçilen standart sapma aralığı")
    render_plotly(fig, x_title="Sınav puanı, x", y_title="Olasılık yoğunluğu, f(x)", legend_title="Gösterge", key="konu10_empirical")
    if mu==70 and sigma==10 and score==85:
        st.caption("Ders notundaki varsayılan örnek: 85 puan için z=(85−70)/10=1,5.")


def _model_and_integrated() -> None:
    st.subheader("5. Model seçimi ve dolum uygulaması")
    scenarios={
        "Servis süresi 20–30 dakika arasında eşit uzunluktaki aralıklarda eşit olasılıklı": "Tek-düze",
        "Dolum miktarları merkez çevresinde simetrik ve çan biçimli": "Normal",
        "Bekleme süresi güçlü biçimde sağa çarpık": "Bu iki modelden biri olduğu söylenemez",
    }
    s=st.selectbox(
        "Hikâye",
        list(scenarios),
        key="konu10_model_story",
        on_change=reset_widget_state,
        args=("konu10_model_guess",),
    )
    g=st.radio(
        "Model",
        ["Tek-düze", "Normal", "Bu iki modelden biri olduğu söylenemez"],
        index=None,
        key="konu10_model_guess",
    )
    if g is None:
        st.caption("Önce modelinizi seçin; geri bildirim seçimden sonra görünecektir.")
    elif g == scenarios[s]:
        st.success("Doğru model seçimi.")
    else:
        st.warning("Sürekli olmak tek başına normal dağılım demek değildir; hikâyedeki biçim/alan yapısını kullanın.")

    st.markdown("#### Dolum miktarı: X ~ N(500, 10²)")
    x=st.slider("İncelenen dolum miktarı (ml)",460,540,510,1,key="konu10_fill_x")
    z=z_score(x,500,10)
    c1,c2=st.columns(2)
    c1.metric("Seçilen değerin z-skoru",f"{z:.2f}")
    c2.metric("μ±2σ aralığı", "480–520 ml")
    xs=np.linspace(460,540,400); ys=normal_density(xs,500,10); mask=(xs>=480)&(xs<=520)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",name="Normal yoğunluk"))
    fig.add_trace(go.Scatter(x=np.r_[xs[mask],520,480],y=np.r_[ys[mask],0,0],fill="toself",mode="lines",name="Yaklaşık %95,4 alan"))
    fig.add_vline(x=x,line_dash="dot")
    fig.update_layout(title="Dolum miktarı örneğinde merkez, yayılım ve seçilen değer")
    render_plotly(fig,x_title="Dolum miktarı (ml)",y_title="Olasılık yoğunluğu, f(x)",legend_title="Gösterge",key="konu10_filling")
    st.caption("Konu 11'de herhangi bir z aralığının olasılığını sistematik biçimde hesaplayacağız; burada normal alanın temel yapısı ve standartlaştırma mantığıyla sınırlıyız.")
    render_question_card("konu10",QUESTIONS)


def render() -> None:
    topic_header(10, "Sürekli Rassal Değişkenler, Tek-Düze ve Normal Dağılım", "Kesikli olasılık kütlesinden sürekli yoğunluk ve alan mantığına geçiyor; tek-düze ve normal modelleri inceliyoruz.")
    learning_goals([
        "Sürekli rassal değişkende tek nokta olasılığının sıfır, aralık olasılığının alan olduğunu açıklamak.",
        "Tek-düze dağılımda yoğunluk, aralık olasılığı, ortalama ve yayılımı yorumlamak.",
        "Normal dağılımda μ'nün konumu, σ'nın yayılımı nasıl değiştirdiğini görselleştirmek.",
        "68–95–99,7 kuralını normal dağılıma uygulamak.",
        "z=(x−μ)/σ ile farklı ölçekleri standart sapma biriminde yorumlamak.",
        "Tek-düze ve normal modeli hikâyenin yapısına göre ayırmak.",
    ])
    tabs=st.tabs(["Sürekli olasılık","Tek-düze","Normal eğri","68–95–99,7 & z","Uygulama"])
    with tabs[0]: _continuous_idea()
    with tabs[1]: _uniform()
    with tabs[2]: _normal_shape()
    with tabs[3]: _empirical_z()
    with tabs[4]: _model_and_integrated()
