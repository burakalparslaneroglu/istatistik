from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic07_logic import (
    DEVICE_PURCHASE_COUNTS,
    bayes_posteriors,
    conditional_probability,
    fraud_alarm_posterior,
    independent_from_conditional,
    joint_probability_table,
    multiplication_rule,
    natural_frequencies,
    shipping_tree_paths,
)
from core.ui_components import learning_goals, render_plotly, topic_header


QUESTIONS = (
    Question("P(A|B) ifadesinde yeni karşılaştırma grubunu hangi olay belirler?", "Dikey çizginin sağındaki B olayı. Koşullu olasılıkta payda B olayına göre daralır."),
    Question("P(A|B) ile P(B|A) genellikle aynı mıdır?", "Hayır. Koşul değiştiğinde payda ve sorulan karşılaştırma grubu değişir."),
    Question("Bağımsızlıkta P(A|B) neye eşittir?", "P(A)'ya. B bilgisinin gelmesi A'nın olasılığını değiştirmez."),
    Question("Sıfırdan büyük olasılıklı iki ayrık olay bağımsız olabilir mi?", "Hayır. Birinin gerçekleşmesi diğerinin olasılığını sıfıra düşürür; dolayısıyla yeni bilgi olasılığı değiştirir."),
    Question("Olasılık ağacında aynı yol üzerindeki dal olasılıkları ne yapılır?", "Çarpılır. Aynı sonuca ulaşan farklı yolların ortak olasılıkları ise toplanır."),
    Question("Bayes hesabında neden yalnız koşullu doğruluk oranına bakmak yeterli değildir?", "Çünkü önsel/temel oran da hesaba katılır. Nadir bir olayda küçük yanlış alarm oranı bile çok sayıda yanlış pozitif üretebilir."),
)


def _conditional_tab() -> None:
    st.subheader("1. Yeni bilgi paydada neyi değiştirir?")
    counts = DEVICE_PURCHASE_COUNTS.copy()
    counts["Toplam"] = counts.sum(axis=1)
    total_row = counts.sum(axis=0)
    display = pd.concat([counts, pd.DataFrame([total_row], index=["Toplam"])])
    st.dataframe(display, width="stretch")

    p_table = joint_probability_table(DEVICE_PURCHASE_COUNTS)
    p_s = float(DEVICE_PURCHASE_COUNTS["Satın aldı"].sum() / DEVICE_PURCHASE_COUNTS.to_numpy().sum())
    p_m = float(DEVICE_PURCHASE_COUNTS.loc["Mobil"].sum() / DEVICE_PURCHASE_COUNTS.to_numpy().sum())
    p_ms = float(p_table.loc["Mobil", "Satın aldı"])
    p_s_given_m = conditional_probability(p_ms, p_m)
    p_m_given_s = conditional_probability(p_ms, p_s)

    compare = pd.DataFrame({"Olasılık": ["P(S)", "P(S | M)", "P(M | S)"], "Yüzde": [100*p_s, 100*p_s_given_m, 100*p_m_given_s]})
    fig = go.Figure(go.Bar(x=compare["Olasılık"], y=compare["Yüzde"], text=[f"%{v:.1f}" for v in compare["Yüzde"]], textposition="outside"))
    fig.update_layout(title="Koşul değiştiğinde paydanın ve sonucun değişmesi", showlegend=False, yaxis_range=[0, 80])
    render_plotly(fig, x_title="Olasılık ifadesi", y_title="Olasılık (%)", key="konu07_conditional_compare")
    st.info("P(S)=%26 bütün 1000 ziyaretçiyi; P(S|M)=%30 yalnız 600 mobil kullanıcıyı; P(M|S)≈%69,2 ise yalnız 260 satın alanı payda olarak kullanır.")

    condition = st.radio("Hangi koşullu olasılığı görmek istiyorsunuz?", ["Mobil olanlar içinde satın alma", "Satın alanlar içinde mobil kullanım"], key="konu07_direction")
    if condition == "Mobil olanlar içinde satın alma":
        st.success("180 / 600 = %30. Dikey çizginin sağındaki M, yeni paydayı belirler.")
    else:
        st.success("180 / 260 ≈ %69,2. Aynı 180 ortak hücresi bu kez farklı bir paydaya bölünür.")


def _independence_tab() -> None:
    st.subheader("2. Bağımsızlık, ayrıklık ve çarpma kuralı")
    p_a = st.slider("P(A)", 0.05, 0.95, 0.30, 0.05, key="konu07_p_a")
    p_a_given_b = st.slider("P(A | B)", 0.0, 1.0, 0.30, 0.05, key="konu07_p_a_given_b")
    independent = independent_from_conditional(p_a, p_a_given_b, tol=1e-9)
    if independent:
        st.success("P(A|B)=P(A): verilen sayılar bağımsızlıkla uyumludur.")
    else:
        st.warning("P(A|B) ≠ P(A): B bilgisi A olasılığını değiştiriyor; olaylar bağımsız değildir.")

    compare = go.Figure(go.Bar(x=["P(A)", "P(A | B)"], y=[100*p_a, 100*p_a_given_b], text=[f"%{100*p_a:.0f}", f"%{100*p_a_given_b:.0f}"], textposition="outside"))
    compare.update_layout(title="Bağımsızlıkta koşul öncesi ve sonrası oran", showlegend=False, yaxis_range=[0, 105])
    render_plotly(compare, x_title="Olasılık", y_title="Olasılık (%)", key="konu07_independence_chart")

    st.markdown("#### Çarpma kuralı")
    p_first = st.slider("P(O): ödeme aynı gün tamamlandı", 0.0, 1.0, 0.80, 0.05, key="konu07_mult_first")
    p_second = st.slider("P(K | O): bu grup içinde aynı gün kargolandı", 0.0, 1.0, 0.90, 0.05, key="konu07_mult_second")
    joint = multiplication_rule(p_first, p_second)
    st.metric("P(O ∩ K)", f"%{100*joint:.1f}")
    st.caption("Genel çarpma kuralı P(A∩B)=P(A)P(B|A)'dır. Bağımsız olaylarda koşullu olasılık P(B)'ye eşit olduğu için formül sadeleşir.")

    st.warning("Ayrıklık bağımsızlık değildir. Sıfırdan büyük olasılıklı iki ayrık olaydan biri gerçekleştiğinde diğerinin koşullu olasılığı 0'a düşer.")


def _tree_bayes_tab() -> None:
    st.subheader("3. Olasılık ağacı ve Bayes güncellemesi")
    st.markdown("#### İki aşamalı sipariş ağacı")
    paths = shipping_tree_paths()
    tree_df = pd.DataFrame({"Yol": list(paths), "Ortak olasılık": list(paths.values())})
    tree_df["Yüzde"] = 100 * tree_df["Ortak olasılık"]
    st.dataframe(tree_df, hide_index=True, width="stretch")
    p_same_day = paths["Standart × aynı gün"] + paths["Öncelikli × aynı gün"]
    st.success(f"Aynı gün kargolanma olasılığı = 0,56 + 0,285 = **{p_same_day:.3f} = %{100*p_same_day:.1f}**.")

    tree_fig = go.Figure(go.Bar(x=tree_df["Yol"], y=tree_df["Yüzde"], text=[f"%{v:.1f}" for v in tree_df["Yüzde"]], textposition="outside"))
    tree_fig.update_layout(title="Olasılık ağacındaki tam yolların ortak olasılıkları", showlegend=False, yaxis_range=[0, 65])
    render_plotly(tree_fig, x_title="Tam yol", y_title="Ortak olasılık (%)", key="konu07_tree_paths")

    st.markdown("#### İki tedarikçili Bayes örneği")
    share_t1 = st.slider("Tedarikçi 1'in parça payı (%)", 10, 90, 70, 5, key="konu07_bayes_share") / 100
    defect_t1 = st.slider("Tedarikçi 1 kusurlu oranı (%)", 1, 20, 2, 1, key="konu07_bayes_defect1") / 100
    defect_t2 = st.slider("Tedarikçi 2 kusurlu oranı (%)", 1, 20, 6, 1, key="konu07_bayes_defect2") / 100
    post = bayes_posteriors([share_t1, 1-share_t1], [defect_t1, defect_t2])
    evidence = share_t1 * defect_t1 + (1-share_t1) * defect_t2
    c1, c2 = st.columns(2)
    c1.metric("Toplam kusurlu olasılığı", f"%{100*evidence:.2f}")
    c2.metric("P(T₂ | kusurlu)", f"%{100*post[1]:.2f}")

    bayes_df = pd.DataFrame({"Aşama": ["Önsel P(T₂)", "Sonsal P(T₂ | kusurlu)"], "Yüzde": [100*(1-share_t1), 100*post[1]]})
    bayes_fig = go.Figure(go.Bar(x=bayes_df["Aşama"], y=bayes_df["Yüzde"], text=[f"%{v:.2f}" for v in bayes_df["Yüzde"]], textposition="outside"))
    bayes_fig.update_layout(title="Kusurlu parça bilgisiyle Tedarikçi 2 olasılığının güncellenmesi", showlegend=False, yaxis_range=[0, 100])
    render_plotly(bayes_fig, x_title="Bilgi aşaması", y_title="Tedarikçi 2 olasılığı (%)", key="konu07_bayes_update")
    if share_t1 == 0.70 and defect_t1 == 0.02 and defect_t2 == 0.06:
        st.info("Ders notundaki varsayılan örnek: ortak olasılıklar 0,014 ve 0,018; P(kusurlu)=0,032; P(T₂|kusurlu)=0,5625.")


def _base_rate_tab() -> None:
    st.subheader("4. Alarm ve temel oran")
    prevalence = st.slider("Gerçek sahtecilik temel oranı (%)", 1, 20, 2, 1, key="konu07_fraud_prevalence") / 100
    sensitivity = st.slider("Sahte işlemde alarm oranı (%)", 50, 100, 90, 5, key="konu07_fraud_sensitivity") / 100
    fpr = st.slider("Sahte olmayan işlemde yanlış alarm oranı (%)", 1, 30, 5, 1, key="konu07_fraud_fpr") / 100
    posterior = fraud_alarm_posterior(prevalence, sensitivity, fpr)
    st.metric("Alarm verildiğinde işlemin gerçekten sahte olma olasılığı", f"%{100*posterior:.1f}")

    freq = natural_frequencies(10_000, prevalence, sensitivity, fpr)
    table = pd.DataFrame(
        {
            "Gerçek durum": ["Gerçekten sahte", "Sahte değil"],
            "Alarm": [freq["Gerçek sahte + alarm"], freq["Sahte değil + alarm"]],
            "Alarm yok": [freq["Gerçek sahte + alarm yok"], freq["Sahte değil + alarm yok"]],
        }
    )
    table["Toplam"] = table["Alarm"] + table["Alarm yok"]
    st.dataframe(table, hide_index=True, width="stretch")

    alarm_total = int(table["Alarm"].sum())
    alarm_df = pd.DataFrame({"Alarm grubunun içeriği": ["Gerçek sahte", "Yanlış alarm"], "İşlem sayısı": [freq["Gerçek sahte + alarm"], freq["Sahte değil + alarm"]]})
    fig = go.Figure(go.Bar(x=alarm_df["Alarm grubunun içeriği"], y=alarm_df["İşlem sayısı"], text=alarm_df["İşlem sayısı"], textposition="outside"))
    fig.update_layout(title=f"10.000 işlemde alarm alan {alarm_total} işlemin bileşimi", showlegend=False)
    render_plotly(fig, x_title="Alarm sonucunun gerçek durumu", y_title="İşlem sayısı (adet)", key="konu07_base_rate_chart")

    if prevalence == 0.02 and sensitivity == 0.90 and fpr == 0.05:
        st.success("Ders notundaki varsayılan durumda 10.000 işlemde 180 gerçek sahte alarmı ve 490 yanlış alarm vardır; P(sahte | alarm)≈%26,9'dur.")
    st.caption("Yüksek duyarlılık, düşük temel oranı ortadan kaldırmaz. Bayes hesabı önsel oran ile alarm performansını birlikte değerlendirir.")
    render_question_card("konu07", QUESTIONS)


def render() -> None:
    topic_header(7, "Koşullu Olasılık, Bağımsızlık ve Bayes Teoremi", "Yeni bilgi geldiğinde ilgili örnek uzayın nasıl daraldığını ve olasılıkların nasıl güncellendiğini inceliyoruz.")
    learning_goals([
        "Koşullu olasılıkta paydanın verilen bilgiye göre değiştiğini açıklamak.",
        "Ortak ve marjinal olasılıkları çapraz tablodan okumak.",
        "P(A|B) ile P(B|A) ifadelerinin farklı sorular olduğunu göstermek.",
        "Bağımsızlık ile ayrıklığı ayırmak ve çarpma kuralını uygulamak.",
        "Olasılık ağacında aynı yol üzerindeki olasılıkları çarpıp aynı sonuca ulaşan yolları toplamak.",
        "Önsel olasılıkları yeni bilgiyle sonsal olasılıklara dönüştürmek ve Bayes teoremini uygulamak.",
        "Temel oran ihmalinin neden yanıltıcı olabileceğini doğal frekanslarla görmek.",
    ])
    tabs = st.tabs(["Koşullu olasılık", "Bağımsızlık & çarpma", "Ağaç & Bayes", "Temel oran"])
    with tabs[0]:
        _conditional_tab()
    with tabs[1]:
        _independence_tab()
    with tabs[2]:
        _tree_bayes_tab()
    with tabs[3]:
        _base_rate_tab()
