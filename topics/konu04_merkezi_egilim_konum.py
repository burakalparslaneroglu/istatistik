from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic04_logic import (
    PERCENTILE_DATA,
    SALES,
    SALES_WITH_OUTLIER,
    arithmetic_mean,
    geometric_mean_growth,
    median,
    modes,
    percentile_course_rule,
    weighted_mean,
)
from core.ui_components import learning_goals, render_plotly, topic_header


QUESTIONS = (
    Question("Örneklem ortalamasının sembolü nedir?", "Örneklem ortalaması x̄ ile, anakütle ortalaması μ ile gösterilir."),
    Question("Aykırı değerlere daha az duyarlı merkez ölçüsü hangisidir?", "Medyan, uç değerin büyüklüğüne aritmetik ortalamadan daha az duyarlıdır."),
    Question("Mod kategorik değişkenlerde kullanılabilir mi?", "Evet. Mod en sık gözlenen kategori veya değeri gösterdiği için kategorik veride de anlamlıdır."),
    Question("Ağırlıkların toplamı 1 değilse ne yapılır?", "Ağırlıklı toplam, ağırlıkların toplamına bölünür."),
    Question("Bu derste yüzdelik konumu hangi kuralla hesaplanır?", "L_p = p(n+1)/100 kuralı kullanılır; tam sayı değilse iki komşu gözlem arasında doğrusal ara değerleme yapılır."),
    Question("Q1, Q2 ve Q3 hangi yüzdeliklere karşılık gelir?", "Q1=P25, Q2=P50=medyan ve Q3=P75'tir."),
    Question("Ardışık büyüme oranlarında neden geometrik ortalama önemlidir?", "Çünkü ardışık büyüme toplamsal değil çarpımsal çalışır; geometrik ortalama bu bileşik yapıyı korur."),
)


def _render_mean_outlier_tab() -> None:
    st.subheader("1. Aritmetik ortalama ve aykırı değerin etkisi")
    st.write("Ders notundaki sekiz günlük satış verisini kullanıyoruz: 16, 18, 20, 22, 22, 22, 24, 26 bin TL.")

    replace_max = st.slider(
        "En yüksek günlük satış değerini değiştiriniz (bin TL)",
        min_value=26,
        max_value=60,
        value=26,
        step=1,
        key="konu04_outlier_value",
    )
    values = SALES.copy()
    values[-1] = replace_max
    mean_value = arithmetic_mean(values)
    median_value = median(values)

    c1, c2 = st.columns(2)
    c1.metric("Aritmetik ortalama", f"{format_number(mean_value, 2)} bin TL")
    c2.metric("Medyan", f"{format_number(median_value, 2)} bin TL")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(values) + 1)),
            y=values,
            mode="markers",
            name="Günlük satış",
            marker={"size": 10},
        )
    )
    fig.add_hline(y=mean_value, line_dash="dash", annotation_text=f"Ortalama = {mean_value:.2f}")
    fig.add_hline(y=median_value, line_dash="dot", annotation_text=f"Medyan = {median_value:.2f}")
    fig.update_layout(title="Tek bir yüksek değerin merkez ölçülerine etkisi")
    render_plotly(
        fig,
        x_title="Gözlem sırası (gün)",
        y_title="Satış geliri (bin TL)",
        legend_title="Gösterge",
        key="konu04_outlier_chart",
    )

    if replace_max == 26:
        st.info("Başlangıç verisinde ortalama 21,25; medyan 22'dir.")
    elif replace_max == 56:
        st.success("Ders notundaki aykırı değer örneği: ortalama 25'e yükselirken medyan 22 olarak kalır.")
    else:
        st.caption("En yüksek değer büyüdükçe ortalamanın bu değerin yönüne çekildiğini, medyanın ise çok daha sınırlı değiştiğini gözleyin.")


def _render_weighted_mode_tab() -> None:
    st.subheader("2. Ağırlıklı ortalama ve mod")
    st.markdown("#### Ders başarı notu")
    midterm = st.slider("Ara sınav notu", 0, 100, 70, key="konu04_midterm")
    project = st.slider("Proje notu", 0, 100, 80, key="konu04_project")
    final = st.slider("Final notu", 0, 100, 90, key="konu04_final")
    values = [midterm, project, final]
    weights = [0.25, 0.25, 0.50]
    wmean = weighted_mean(values, weights)
    simple = arithmetic_mean(values)

    c1, c2 = st.columns(2)
    c1.metric("Ağırlıklı başarı notu", format_number(wmean, 2))
    c2.metric("Basit aritmetik ortalama", format_number(simple, 2))

    fig = go.Figure(
        go.Bar(
            x=["Ara sınav", "Proje", "Final"],
            y=[25, 25, 50],
            text=["%25", "%25", "%50"],
            textposition="outside",
        )
    )
    fig.update_layout(title="Başarı notu bileşenlerinin ağırlıkları", showlegend=False, yaxis_range=[0, 60])
    render_plotly(
        fig,
        x_title="Değerlendirme bileşeni",
        y_title="Ağırlık (%)",
        key="konu04_weight_chart",
    )

    st.markdown("#### Mod")
    mode_example = st.selectbox(
        "Veri setini seçiniz",
        ["1, 2, 2, 3, 4", "1, 1, 2, 2, 3", "1, 2, 3, 4"],
        key="konu04_mode_example",
    )
    parsed = [float(x.strip()) for x in mode_example.split(",")]
    mode_values = modes(parsed)
    if not mode_values:
        st.info("Bu veri setinde tekrar eden en yüksek frekans yoktur; belirgin bir mod bulunmaz.")
    elif len(mode_values) == 1:
        st.success(f"Mod = {format_number(mode_values[0])}")
    else:
        st.success("Birden fazla mod vardır: " + ", ".join(format_number(x) for x in mode_values))


def _render_percentile_tab() -> None:
    st.subheader("3. Yüzdelikler ve çeyrekler")
    st.write(
        "Bu derste yüzdelik konumu **Lₚ = p(n+1)/100** kuralıyla hesaplanır. Tam sayı olmayan konumlarda doğrusal ara değerleme yapılır."
    )
    p = st.slider("Yüzdelik düzeyi p", 10, 90, 60, 5, key="konu04_percentile_p")
    location, value = percentile_course_rule(PERCENTILE_DATA, p)

    c1, c2 = st.columns(2)
    c1.metric(f"L{p} konumu", format_number(location, 2))
    c2.metric(f"P{p}", format_number(value, 2))

    if p == 60:
        st.success("Ders notundaki örnek: L₆₀ = 7,8 ve P₆₀ = 54,8.")

    sorted_values = list(PERCENTILE_DATA)
    fig = go.Figure(
        go.Scatter(
            x=sorted_values,
            y=list(range(1, len(sorted_values) + 1)),
            mode="markers+lines",
            name="Sıralı gözlemler",
        )
    )
    fig.add_vline(x=value, line_dash="dash", annotation_text=f"P{p} = {value:.2f}")
    fig.update_layout(title=f"P{p} değerinin sıralanmış veri içindeki konumu", showlegend=False)
    render_plotly(
        fig,
        x_title="Gözlem değeri",
        y_title="Sıralamadaki konum",
        key="konu04_percentile_chart",
    )

    q1_loc, q1 = percentile_course_rule(PERCENTILE_DATA, 25)
    _, q2 = percentile_course_rule(PERCENTILE_DATA, 50)
    q3_loc, q3 = percentile_course_rule(PERCENTILE_DATA, 75)
    st.markdown(
        f"**Çeyrekler:** Q₁ = {format_number(q1, 1)}, Q₂ = {format_number(q2, 1)}, Q₃ = {format_number(q3, 1)}. "
        "Çeyrekler sayısal ekseni eşit uzunluklara değil, gözlemleri yaklaşık eşit sayıda dört gruba ayırır."
    )
    st.caption(f"Bu veri setinde L25={format_number(q1_loc, 2)} ve L75={format_number(q3_loc, 2)}.")


def _render_growth_choice_tab() -> None:
    st.subheader("4. Geometrik ortalama, ölçü seçimi ve merkezin sınırı")
    st.markdown("#### Bileşik büyüme")
    first = st.slider("1. yıl değişimi (%)", -30, 30, 10, key="konu04_growth1")
    second = st.slider("2. yıl değişimi (%)", -30, 30, -10, key="konu04_growth2")
    start = 100.0
    final_value = start * (1 + first / 100) * (1 + second / 100)
    arithmetic_rate = (first + second) / 2
    geometric_rate = geometric_mean_growth([first, second])

    c1, c2, c3 = st.columns(3)
    c1.metric("İki yıl sonundaki endeks", format_number(final_value, 2))
    c2.metric("Oranların aritmetik ortalaması", f"%{format_number(arithmetic_rate, 2)}")
    c3.metric("Ortalama bileşik büyüme", f"%{format_number(geometric_rate, 2)}")
    st.caption("Ardışık yüzde değişimleri bir önceki dönemin düzeyi üzerine çarpılarak işler.")

    st.markdown("#### Hangi konum ölçüsü?")
    scenario = st.selectbox(
        "Araştırma durumunu seçiniz",
        [
            "Üst yönetimde az sayıda çok yüksek ücret bulunan çalışan ücretleri",
            "Bir markette en sık satılan paket boyu",
            "Finalin %60 ağırlığa sahip olduğu ders başarı notu",
            "Bir öğrencinin sınıftaki göreli sınav konumu",
            "Beş yıllık ortalama bileşik büyüme oranı",
        ],
        key="konu04_measure_scenario",
    )
    choice_map = {
        "Üst yönetimde az sayıda çok yüksek ücret bulunan çalışan ücretleri": "Medyan",
        "Bir markette en sık satılan paket boyu": "Mod",
        "Finalin %60 ağırlığa sahip olduğu ders başarı notu": "Ağırlıklı ortalama",
        "Bir öğrencinin sınıftaki göreli sınav konumu": "Yüzdelik / çeyrek",
        "Beş yıllık ortalama bileşik büyüme oranı": "Geometrik ortalama",
    }
    st.info(f"Öncelikli ölçü: **{choice_map[scenario]}**")

    st.markdown("#### Aynı merkez, farklı dağılım")
    group_a = [28, 29, 30, 31, 32]
    group_b = [10, 20, 30, 40, 50]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=group_a, y=["Veri A"] * 5, mode="markers", name="Veri A", marker={"size": 11}))
    fig.add_trace(go.Scatter(x=group_b, y=["Veri B"] * 5, mode="markers", name="Veri B", marker={"size": 11}))
    fig.add_vline(x=30, line_dash="dash", annotation_text="Ortak merkez = 30")
    fig.update_layout(title="Aynı ortalama ve medyan, farklı dağılım")
    render_plotly(
        fig,
        x_title="Değer",
        y_title="Veri seti",
        legend_title="Grup",
        key="konu04_same_center_chart",
    )
    st.warning(
        "Her iki veri setinin ortalaması ve medyanı 30'dur; buna rağmen gözlemlerin merkez çevresindeki yayılımı belirgin biçimde farklıdır. "
        "Bu fark Konu 05'te değişkenlik ve yayılım ölçüleriyle sayısallaştırılacaktır."
    )

    render_question_card("konu04", QUESTIONS)


def render() -> None:
    topic_header(
        4,
        "Merkezi Eğilim ve Konum Ölçüleri",
        "Bir veri setinin merkezini tek bir sayı ile özetlemek mümkündür; ancak ortalama, medyan ve mod farklı sorulara cevap verir.",
    )
    learning_goals(
        [
            "Örneklem ve anakütle ortalaması notasyonunu ayırt etmek.",
            "Aritmetik ortalamayı hesaplamak ve uç değerlere duyarlılığını görmek.",
            "Ağırlıklı ortalamayı uygun ağırlıklarla hesaplamak.",
            "Medyan ve modu belirlemek; ortalama ile medyanı karşılaştırmak.",
            "Dersin Lₚ=p(n+1)/100 kuralıyla yüzdelik ve çeyrek hesaplamak.",
            "Ardışık bileşik büyümede geometrik ortalamanın neden ayrı bir rolü olduğunu kavramak.",
            "Aynı merkez ölçülerine sahip veri setlerinin yine de farklı dağılımlara sahip olabileceğini görmek.",
        ]
    )

    tabs = st.tabs(["Ortalama & aykırı değer", "Ağırlıklı ortalama & mod", "Yüzdelikler", "Ölçü seçimi & kontrol"])
    with tabs[0]:
        _render_mean_outlier_tab()
    with tabs[1]:
        _render_weighted_mode_tab()
    with tabs[2]:
        _render_percentile_tab()
    with tabs[3]:
        _render_growth_choice_tab()
