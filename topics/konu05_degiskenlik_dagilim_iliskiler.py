from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic05_logic import (
    AD_COUNTS,
    OUTLIER_INCOME,
    SALES,
    SUPPLIER_A,
    SUPPLIER_B,
    VARIANCE_EXAMPLE,
    chebyshev_min_percent,
    coefficient_of_variation,
    iqr_summary,
    outlier_candidates,
    sample_correlation,
    sample_covariance,
    sample_range,
    sample_sd,
    sample_variance,
    z_score,
)
from core.ui_components import learning_goals, render_plotly, topic_header


QUESTIONS = (
    Question("İki veri setinin ortalaması aynıysa standart sapmaları da aynı olmak zorunda mıdır?", "Hayır. Merkez aynı olsa bile gözlemlerin merkez çevresindeki yayılımı farklı olabilir."),
    Question("Örneklem varyansında neden n−1 kullanılır?", "Örneklem ortalaması aynı veriden tahmin edildiği için kareli sapmaların sistematik olarak küçük kalma eğilimini düzeltmek amacıyla n−1 kullanılır."),
    Question("z = −2 neyi ifade eder?", "Gözlem, ortalamanın iki standart sapma altındadır."),
    Question("IQR yöntemi bir gözlemi aykırı aday olarak işaretlediğinde gözlem otomatik silinir mi?", "Hayır. Önce veri üretim süreci, ölçüm ve araştırma bağlamı incelenmelidir."),
    Question("Korelasyonun 0'a yakın olması iki değişken arasında hiçbir ilişki olmadığı anlamına gelir mi?", "Hayır. Pearson korelasyonu doğrusal ilişkiyi ölçer; güçlü doğrusal olmayan bir ilişki korelasyonda zayıf görünebilir."),
    Question("Yüksek korelasyon tek başına nedensellik gösterir mi?", "Hayır. Korelasyon birlikte hareketi özetler; nedensellik için araştırma tasarımı ve ek varsayımlar gerekir."),
)


def _spread_tab() -> None:
    st.subheader("1. Aynı merkez, farklı yayılım")
    st.write("Ders notundaki iki tedarikçinin ortalama teslim süresi aynıdır; yayılımları ise farklıdır.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=SUPPLIER_A, y=["Tedarikçi A"] * len(SUPPLIER_A), mode="markers", name="Tedarikçi A", marker={"size": 12}))
    fig.add_trace(go.Scatter(x=SUPPLIER_B, y=["Tedarikçi B"] * len(SUPPLIER_B), mode="markers", name="Tedarikçi B", marker={"size": 12}))
    fig.add_vline(x=10, line_dash="dash", annotation_text="Ortak ortalama = 10")
    fig.update_layout(title="Aynı ortalamaya sahip iki teslimat serisi")
    render_plotly(fig, x_title="Teslim süresi (gün)", y_title="Tedarikçi", legend_title="Seri", key="konu05_supplier_spread")

    rows = []
    for name, values in [("Tedarikçi A", SUPPLIER_A), ("Tedarikçi B", SUPPLIER_B)]:
        rows.append(
            {
                "Seri": name,
                "Ortalama": np.mean(values),
                "Değişim aralığı": sample_range(values),
                "Örneklem varyansı": sample_variance(values),
                "Standart sapma": sample_sd(values),
            }
        )
    summary = pd.DataFrame(rows)
    st.dataframe(summary.style.format({"Ortalama": "{:.2f}", "Değişim aralığı": "{:.2f}", "Örneklem varyansı": "{:.2f}", "Standart sapma": "{:.2f}"}), hide_index=True, width="stretch")
    st.info("Her iki ortalama 10 gündür. Buna karşılık B'nin standart sapması yaklaşık 2,55; A'nınki yaklaşık 0,71 gündür.")

    st.markdown("#### Varyansın adımları")
    mean = float(np.mean(VARIANCE_EXAMPLE))
    variance_table = pd.DataFrame({
        "xᵢ": VARIANCE_EXAMPLE,
        "xᵢ − x̄": VARIANCE_EXAMPLE - mean,
        "(xᵢ − x̄)²": (VARIANCE_EXAMPLE - mean) ** 2,
    })
    st.dataframe(variance_table, hide_index=True, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ortalama", format_number(mean, 2))
    c2.metric("Kareli sapmalar toplamı", format_number(float(((VARIANCE_EXAMPLE - mean) ** 2).sum()), 2))
    c3.metric("Örneklem varyansı", format_number(sample_variance(VARIANCE_EXAMPLE), 2))

    st.markdown("#### Mutlak ve göreli değişkenlik")
    c1, c2 = st.columns(2)
    with c1:
        mean_a = st.number_input("Değişken A ortalaması", min_value=1.0, value=80.0, step=1.0, key="konu05_cv_mean_a")
        sd_a = st.number_input("Değişken A standart sapması", min_value=0.0, value=8.0, step=1.0, key="konu05_cv_sd_a")
    with c2:
        mean_b = st.number_input("Değişken B ortalaması", min_value=1.0, value=10.0, step=1.0, key="konu05_cv_mean_b")
        sd_b = st.number_input("Değişken B standart sapması", min_value=0.0, value=2.0, step=1.0, key="konu05_cv_sd_b")
    cv_a = coefficient_of_variation(mean_a, sd_a)
    cv_b = coefficient_of_variation(mean_b, sd_b)
    st.write(f"A için CV = **%{format_number(cv_a, 1)}**, B için CV = **%{format_number(cv_b, 1)}**.")
    st.caption("CV yalnız ortalamanın pozitif ve anlamlı olduğu oran ölçekli değişkenlerde uygun bir göreli değişkenlik ölçüsüdür.")


def _standardization_tab() -> None:
    st.subheader("2. z-skoru, Chebyshev ve aykırı değer")
    st.markdown("#### Göreli konumu standartlaştırma")
    mean = st.slider("Sınav ortalaması", 40, 90, 70, key="konu05_z_mean")
    sd = st.slider("Standart sapma", 2, 20, 10, key="konu05_z_sd")
    value = st.slider("Öğrencinin notu", 0, 100, 85, key="konu05_z_value")
    z = z_score(value, mean, sd)
    st.metric("z-skoru", format_number(z, 2))

    z_fig = go.Figure(go.Scatter(x=[-3, -2, -1, 0, 1, 2, 3], y=[0] * 7, mode="markers", name="Standart konum"))
    z_fig.add_trace(go.Scatter(x=[z], y=[0], mode="markers+text", text=[f"z={z:.2f}"], textposition="top center", name="Seçilen gözlem", marker={"size": 14}))
    z_fig.add_vline(x=0, line_dash="dash", annotation_text="Ortalama")
    z_fig.update_layout(title="Gözlemin ortalamaya göre standartlaştırılmış konumu", yaxis_range=[-0.5, 0.5])
    render_plotly(z_fig, x_title="z-skoru (standart sapma birimi)", y_title="Göreli konum ekseni", legend_title="Gösterim", key="konu05_z_chart")

    st.markdown("#### Chebyshev ile ampirik kuralı ayırın")
    k = st.select_slider("Ortalamanın kaç standart sapma çevresi?", options=[2, 3], value=2, key="konu05_k_rule")
    empirical = {2: 95.0, 3: 99.7}[k]
    cheb = chebyshev_min_percent(k)
    rule_df = pd.DataFrame({"Kural": ["Chebyshev — en az", "Ampirik kural — yaklaşık"], "Yüzde": [cheb, empirical]})
    rule_fig = go.Figure(go.Bar(x=rule_df["Kural"], y=rule_df["Yüzde"], text=[f"%{x:.1f}" for x in rule_df["Yüzde"]], textposition="outside"))
    rule_fig.update_layout(title=f"Ortalamanın ±{k} standart sapması içindeki gözlemler", yaxis_range=[0, 105], showlegend=False)
    render_plotly(rule_fig, x_title="Kural", y_title="Gözlemlerin payı (%)", key="konu05_rules_chart")
    st.caption("Chebyshev dağılım biçiminden bağımsız bir alt sınır verir; ampirik kural yaklaşık çan biçimli dağılımlar içindir.")

    st.markdown("#### IQR ile aykırı değer adayı")
    max_income = st.slider("Son gözlemin değeri", 30, 90, 65, key="konu05_outlier_value")
    income = OUTLIER_INCOME.copy()
    income[-1] = max_income
    summary = iqr_summary(income)
    candidates = outlier_candidates(income)
    c1, c2, c3 = st.columns(3)
    c1.metric("Q₁", format_number(summary["q1"], 1))
    c2.metric("Q₃", format_number(summary["q3"], 1))
    c3.metric("IQR", format_number(summary["iqr"], 1))
    st.write(f"Alt sınır = **{format_number(summary['lower_fence'], 1)}**, üst sınır = **{format_number(summary['upper_fence'], 1)}**.")
    if candidates:
        st.warning("Aykırı değer adayı: " + ", ".join(format_number(x, 1) for x in candidates) + ". Bu etiket otomatik silme kararı değildir.")
    else:
        st.success("IQR sınırlarının dışında gözlem yok.")

    out_fig = go.Figure(go.Scatter(x=income, y=["Gelir gözlemleri"] * len(income), mode="markers", name="Gözlem", marker={"size": 11}))
    out_fig.add_vline(x=summary["lower_fence"], line_dash="dash", annotation_text="Alt IQR sınırı")
    out_fig.add_vline(x=summary["upper_fence"], line_dash="dash", annotation_text="Üst IQR sınırı")
    out_fig.update_layout(title="IQR sınırları ve aykırı değer adayları")
    render_plotly(out_fig, x_title="Gelir değeri", y_title="Gözlem grubu", key="konu05_outlier_chart")


def _boxplot_tab() -> None:
    st.subheader("3. Beş sayı özeti ve kutu grafiği")
    summary = iqr_summary(OUTLIER_INCOME)
    st.dataframe(
        pd.DataFrame(
            {
                "Özet": ["En küçük", "Q₁", "Medyan", "Q₃", "En büyük"],
                "Değer": [summary["min"], summary["q1"], summary["median"], summary["q3"], summary["max"]],
            }
        ),
        hide_index=True,
        width="stretch",
    )
    st.caption("65, IQR kuralına göre aykırı olduğundan standart kutu grafiğinde ayrı nokta olarak gösterilir; üst bıyık aykırı olmayan en büyük değere kadar uzanır.")

    fig = go.Figure(go.Box(x=OUTLIER_INCOME, name="Gelir", boxpoints="outliers", orientation="h"))
    fig.update_layout(title="Gelir verisinin kutu grafiği", showlegend=False)
    render_plotly(fig, x_title="Gelir değeri", y_title="Veri seti", key="konu05_boxplot")

    st.markdown("#### Aynı medyan, farklı yayılım")
    class_a = [60, 68, 70, 72, 80]
    class_b = [40, 60, 70, 80, 100]
    compare = go.Figure()
    compare.add_trace(go.Box(x=class_a, name="Sınıf A", orientation="h", boxpoints="all"))
    compare.add_trace(go.Box(x=class_b, name="Sınıf B", orientation="h", boxpoints="all"))
    compare.update_layout(title="Aynı medyana sahip iki grubun yayılım karşılaştırması")
    render_plotly(compare, x_title="Sınav notu (puan)", y_title="Sınıf", legend_title="Sınıf", key="konu05_box_compare")


def _relationship_tab() -> None:
    st.subheader("4. Kovaryans ve korelasyon")
    cov = sample_covariance(AD_COUNTS, SALES)
    corr = sample_correlation(AD_COUNTS, SALES)
    c1, c2 = st.columns(2)
    c1.metric("Örneklem kovaryansı", format_number(cov, 2))
    c2.metric("Pearson korelasyonu", format_number(corr, 3))

    fig = go.Figure(go.Scatter(x=AD_COUNTS, y=SALES, mode="markers+lines", name="Haftalar", marker={"size": 11}))
    fig.update_layout(title="Reklam sayısı ile satış arasındaki ilişki", showlegend=False)
    render_plotly(fig, x_title="Reklam sayısı (haftalık)", y_title="Satış (bin TL)", key="konu05_corr_scatter")
    st.info("Pozitif kovaryans ve pozitif korelasyon, iki değişkenin örneklemde aynı yönde hareket ettiğini gösterir. Kovaryansın büyüklüğü birimlere bağlıdır; korelasyon −1 ile +1 arasındadır.")

    relation = st.selectbox("Korelasyonun sınırını görmek için ilişki türünü seçiniz", ["Pozitif doğrusal", "Negatif doğrusal", "Doğrusal olmayan U biçimi"], key="konu05_relation_type")
    x = np.arange(-5, 6, dtype=float)
    if relation == "Pozitif doğrusal":
        y = 2 * x + 3
    elif relation == "Negatif doğrusal":
        y = -2 * x + 3
    else:
        y = x**2
    r = sample_correlation(x, y)
    demo = go.Figure(go.Scatter(x=x, y=y, mode="markers", name=relation, marker={"size": 10}))
    demo.update_layout(title=f"{relation}: r = {r:.3f}", showlegend=False)
    render_plotly(demo, x_title="X değişkeni", y_title="Y değişkeni", key="konu05_relation_demo")
    if relation == "Doğrusal olmayan U biçimi":
        st.warning("Burada belirgin bir ilişki vardır; fakat Pearson korelasyonu yaklaşık 0'dır. Korelasyon doğrusal ilişkiyi ölçer.")
    st.warning("Korelasyon tek başına nedensellik göstermez.")
    render_question_card("konu05", QUESTIONS)


def render() -> None:
    topic_header(5, "Değişkenlik, Dağılımın Şekli ve İki Değişken Arasındaki İlişki", "Merkez ölçülerine yayılımı ekliyor; ardından iki nicel değişkenin birlikte hareketini inceliyoruz.")
    learning_goals([
        "Değişim aralığı, IQR, örneklem varyansı ve standart sapmayı hesaplamak ve ayırmak.",
        "Değişim katsayısını yalnız uygun ölçeklerde göreli değişkenlik için kullanmak.",
        "z-skoruyla bir gözlemin ortalamaya göre göreli konumunu ifade etmek.",
        "Chebyshev eşitsizliği ile ampirik kuralın kapsamını ayırmak.",
        "IQR sınırları ve kutu grafiğiyle aykırı değer adaylarını incelemek.",
        "Kovaryans ve korelasyonu yön, güç ve ölçü birimi açısından yorumlamak.",
        "Korelasyonun yalnız doğrusal ilişkiyi özetlediğini ve nedensellik göstermediğini hatırlamak.",
    ])
    tabs = st.tabs(["Yayılım", "z & aykırı değer", "Kutu grafiği", "Kovaryans & korelasyon"])
    with tabs[0]:
        _spread_tab()
    with tabs[1]:
        _standardization_tab()
    with tabs[2]:
        _boxplot_tab()
    with tabs[3]:
        _relationship_tab()
