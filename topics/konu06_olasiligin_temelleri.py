from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic06_logic import (
    SHIPMENT_PROBABILITIES,
    addition_rule,
    combinations,
    complement,
    event_probability,
    factorial,
    permutations,
    product_count,
    relative_frequency,
    shipment_metrics,
)
from core.ui_components import learning_goals, render_plotly, topic_header


QUESTIONS = (
    Question("P(A)=0,80 olması A olayının bir sonraki denemede kesin gerçekleşeceğini gösterir mi?", "Hayır. Olasılık belirsizliğin derecesini ifade eder; tek bir denemeyi garanti etmez."),
    Question("İki zarın toplamlarının 2–12 arasında olması bu 11 toplamın eşit olasılıklı olduğu anlamına gelir mi?", "Hayır. Örneğin toplam 2 tek bir zar çiftiyle, toplam 7 ise altı farklı çiftle oluşur."),
    Question("Sıra önemli değilse kombinasyon mu permütasyon mu kullanılır?", "Kombinasyon. Sıra veya görev önemliyse permütasyon kullanılır."),
    Question("P(A ∪ B) hesabında neden P(A ∩ B) çıkarılır?", "A ve B ayrı ayrı toplandığında ortak bölüm iki kez sayıldığı için bir kez çıkarılır."),
    Question("Ayrık olaylarda kesişim olasılığı kaçtır?", "0'dır; ortak örnek noktaları yoktur."),
    Question("Göreli frekans yöntemi hangi durumda uygundur?", "Aynı sürece ait yeterli sayıda geçmiş tekrar gözlendiğinde olayın gerçekleşme oranı olasılık için doğal bir tahmindir."),
)


def _probability_experiment_tab() -> None:
    st.subheader("1. Olasılık ölçeği ve rassal deney")
    p = st.slider("Bir olay için P(A)", 0.0, 1.0, 0.35, 0.05, key="konu06_probability_slider")
    st.metric("Olasılık", f"{p:.2f} = %{100*p:.0f}")
    if p == 0:
        st.info("P(A)=0: olay imkânsızdır.")
    elif p == 1:
        st.info("P(A)=1: olay kesindir.")
    elif p > 0.5:
        st.info("Olayın gerçekleşmesi gerçekleşmemesine göre daha olasıdır; yine de garanti değildir.")
    elif p < 0.5:
        st.info("Olayın gerçekleşmesi daha az olasıdır; yine de mümkündür.")
    else:
        st.info("Gerçekleşme ve gerçekleşmeme aynı olasılık düzeyindedir.")

    st.markdown("#### Tek deney ile uzun dönem sıklığını ayırın")
    n = st.slider("Tekrar sayısı", 10, 500, 100, 10, key="konu06_trials")
    rng = np.random.default_rng(207)
    outcomes = rng.random(n) < p
    cumulative = np.cumsum(outcomes) / np.arange(1, n + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(1, n + 1), y=100 * cumulative, mode="lines", name="Gerçekleşen göreli frekans"))
    fig.add_hline(y=100 * p, line_dash="dash", annotation_text=f"P(A) = %{100*p:.0f}")
    fig.update_layout(title="Tekrarlı deneylerde göreli frekansın davranışı")
    render_plotly(fig, x_title="Deney tekrar sayısı", y_title="A olayının kümülatif göreli frekansı (%)", legend_title="Gösterim", key="konu06_frequency_sim")
    st.caption("Benzetim sabit seed ile üretilmiştir; amacı olasılığın tek deneme garantisi olmadığını görselleştirmektir.")

    st.markdown("#### Zarın örnek uzayı")
    sample_space = set(range(1, 7))
    event_values = st.multiselect("A olayına dahil zar sonuçlarını seçiniz", options=sorted(sample_space), default=[1, 3, 5], key="konu06_die_event")
    if event_values:
        prob = event_probability(sample_space, set(event_values))
        st.write(f"A = {sorted(event_values)} ve eşit olasılıklı adil zar için **P(A) = {len(event_values)}/6 = {prob:.3f}**.")
    else:
        st.write("A = ∅ ve P(A)=0.")


def _counting_tab() -> None:
    st.subheader("2. Çok aşamalı sayma, kombinasyon ve permütasyon")
    st.markdown("#### Çarpım yoluyla sayma")
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("1. aşama seçenek sayısı", min_value=1, value=4, step=1, key="konu06_stage1")
    b = c2.number_input("2. aşama seçenek sayısı", min_value=1, value=3, step=1, key="konu06_stage2")
    c = c3.number_input("3. aşama seçenek sayısı", min_value=1, value=2, step=1, key="konu06_stage3")
    st.metric("Toplam farklı sonuç", product_count([int(a), int(b), int(c)]))
    st.caption("Ders notundaki 4 renk × 3 kapasite × 2 garanti paketi örneğinin varsayılan sonucu 24'tür.")

    st.markdown("#### Sıra önemli mi?")
    n = st.slider("n: toplam nesne", 2, 12, 5, key="konu06_count_n")
    r = st.slider("r: seçilecek nesne", 1, n, min(3, n), key="konu06_count_r")
    order_matters = st.radio("Seçilenlerin sırası/görevi önemli mi?", ["Hayır", "Evet"], horizontal=True, key="konu06_order")
    if order_matters == "Hayır":
        st.success(f"Kombinasyon: C({n},{r}) = **{combinations(n, r)}**")
    else:
        st.success(f"Permütasyon: P({n},{r}) = **{permutations(n, r)}**")
    st.caption(f"Kontrol: {n}! = {factorial(n)}")


def _events_tab() -> None:
    st.subheader("3. Olay, tümleyen, birleşim ve kesişim")
    sample_space = set(range(1, 7))
    a_values = set(st.multiselect("A olayının zar sonuçları", options=sorted(sample_space), default=[1, 3, 5], key="konu06_event_a"))
    b_values = set(st.multiselect("B olayının zar sonuçları", options=sorted(sample_space), default=[4, 5, 6], key="konu06_event_b"))

    union = a_values | b_values
    intersection = a_values & b_values
    complement_a = sample_space - a_values
    st.dataframe(pd.DataFrame({
        "İşlem": ["A", "B", "A ∩ B", "A ∪ B", "Aᶜ"],
        "Örnek noktalar": [str(sorted(a_values)), str(sorted(b_values)), str(sorted(intersection)), str(sorted(union)), str(sorted(complement_a))],
        "Olasılık": [len(a_values)/6, len(b_values)/6, len(intersection)/6, len(union)/6, len(complement_a)/6],
    }), hide_index=True, width="stretch")

    if a_values and b_values:
        p_a, p_b, p_int = len(a_values)/6, len(b_values)/6, len(intersection)/6
        st.write(f"Toplama kuralı: P(A∪B) = {p_a:.3f} + {p_b:.3f} − {p_int:.3f} = **{addition_rule(p_a,p_b,p_int):.3f}**")
    st.write(f"Tümleyen kuralı: P(Aᶜ) = 1 − P(A) = **{complement(len(a_values)/6):.3f}**")
    if not intersection and a_values and b_values:
        st.info("A ve B'nin ortak örnek noktası yok: olaylar ayrık. Bu durumda toplama kuralındaki kesişim terimi 0'dır.")

    st.markdown("#### Toplama kuralında çift sayma")
    excel, python, both = 40, 35, 15
    only_excel = excel - both
    only_python = python - both
    neither = 100 - (excel + python - both)
    counts = pd.DataFrame({"Kategori": ["Yalnız Excel", "Her ikisi", "Yalnız Python", "Hiçbiri"], "Çalışan sayısı": [only_excel, both, only_python, neither]})
    fig = go.Figure(go.Bar(x=counts["Kategori"], y=counts["Çalışan sayısı"], text=counts["Çalışan sayısı"], textposition="outside"))
    fig.update_layout(title="100 çalışanda Excel ve Python kullanımı", showlegend=False, yaxis_range=[0, 45])
    render_plotly(fig, x_title="Yazılım kullanım kategorisi", y_title="Çalışan sayısı (kişi)", key="konu06_addition_chart")
    st.info("P(E∪P)=0,40+0,35−0,15=0,60. Ortak %15, ilk iki olasılıkta iki kez sayıldığı için bir kez çıkarılır.")


def _application_tab() -> None:
    st.subheader("4. Bütünleştirici tedarik performansı uygulaması")
    df = pd.DataFrame({"Ortak sonuç": list(SHIPMENT_PROBABILITIES), "Olasılık": list(SHIPMENT_PROBABILITIES.values())})
    df["Yüzde"] = 100 * df["Olasılık"]
    st.dataframe(df, hide_index=True, width="stretch")

    fig = go.Figure(go.Bar(x=df["Ortak sonuç"], y=df["Yüzde"], text=[f"%{v:.0f}" for v in df["Yüzde"]], textposition="outside"))
    fig.update_layout(title="Sevkiyat sonuçlarının ortak olasılıkları", showlegend=False, yaxis_range=[0, 80])
    render_plotly(fig, x_title="Sevkiyat sonucu", y_title="Olasılık (%)", key="konu06_shipment_chart")

    metrics = shipment_metrics()
    c1, c2, c3 = st.columns(3)
    c1.metric("Geç", f"%{100*metrics['p_late']:.0f}")
    c2.metric("Hatalı", f"%{100*metrics['p_error']:.0f}")
    c3.metric("Geç veya hatalı", f"%{100*metrics['p_late_or_error']:.0f}")
    st.success("'Geç veya hatalı' olasılığı %30'dur. Tümleyeni olan 'zamanında ve hatasız' olasılığı %70'tir.")

    st.markdown("#### Olasılık atama yöntemini seçin")
    scenario = st.selectbox("Durum", ["Adil bir para atışı", "Geçmiş 200 teslimatın 30'unun gecikmesi", "Daha önce girilmemiş yeni bir pazarda uzman değerlendirmesi"], key="konu06_assignment_scenario")
    mapping = {
        "Adil bir para atışı": "Klasik yöntem — temel sonuçların eşit olasılıklı olduğu kabul edilir.",
        "Geçmiş 200 teslimatın 30'unun gecikmesi": f"Göreli frekans — P(gecikme) ≈ {relative_frequency(30,200):.2f}.",
        "Daha önce girilmemiş yeni bir pazarda uzman değerlendirmesi": "Öznel yöntem — yeterli tekrar verisi olmadığında uzman bilgisi ve mevcut bilgiler kullanılır.",
    }
    st.info(mapping[scenario])
    render_question_card("konu06", QUESTIONS)


def render() -> None:
    topic_header(6, "Olasılığın Temelleri", "Belirsizliği 0 ile 1 arasında sayısallaştırıyor; örnek uzay, sayma ve olay işlemleriyle olasılık problemlerini sistematik kuruyoruz.")
    learning_goals([
        "Olasılığı belirsizliğin derecesi olarak yorumlamak ve tek-deneme garantisiyle karıştırmamak.",
        "Rassal deney, örnek nokta ve örnek uzayı tanımlamak.",
        "Çarpım yoluyla sayma, faktöriyel, kombinasyon ve permütasyonu doğru bağlamda kullanmak.",
        "Klasik, göreli frekans ve öznel olasılık atama yöntemlerini ayırmak.",
        "Olay, tümleyen, birleşim ve kesişim işlemlerini örnek uzay üzerinde göstermek.",
        "Toplama kuralında ortak bölümün neden çıkarıldığını açıklamak ve ayrık olayları tanımak.",
    ])
    tabs = st.tabs(["Olasılık & deney", "Sayma", "Olay işlemleri", "Tedarik uygulaması"])
    with tabs[0]:
        _probability_experiment_tab()
    with tabs[1]:
        _counting_tab()
    with tabs[2]:
        _events_tab()
    with tabs[3]:
        _application_tab()
