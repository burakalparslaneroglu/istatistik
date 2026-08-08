from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic02_logic import (
    MATERIAL_CROSSTAB,
    SIMPSON_DATA,
    STUDY_RESOURCE_FREQUENCIES,
    TRANSPORT_FREQUENCIES,
    column_percentages,
    frequency_summary,
    row_percentages,
    simpson_rates,
)
from core.ui_components import (
    concept_card,
    learning_goals,
    render_plotly,
    topic_header,
)


QUESTIONS = (
    Question(
        "Bir kategorinin frekansı neyi gösterir?",
        "O kategoriye düşen gözlem sayısını gösterir. Bütün kategori frekanslarının toplamı gözlem sayısı n'ye eşit olmalıdır.",
    ),
    Question(
        "Göreli frekans ile yüzde frekans arasındaki ilişki nedir?",
        "Göreli frekans f/n'dir. Yüzde frekans, göreli frekansın 100 ile çarpılmış biçimidir.",
    ),
    Question(
        "Ordinal kategorileri frekanslarına göre yeniden sıralamak her zaman uygun mudur?",
        "Hayır. Ordinal veride kategorilerin doğal sırası korunmalıdır; frekansa göre sıralama bu anlamlı sırayı bozabilir.",
    ),
    Question(
        "'İktisat öğrencilerinin yüzde kaçı dijital materyal tercih ediyor?' sorusunda payda nedir?",
        "İktisat satır toplamıdır. Ders notundaki örnekte payda 40'tır ve oran 18/40 = %45'tir.",
    ),
    Question(
        "Yüzde 72'den yüzde 78'e çıkış kaç yüzde puandır?",
        "6 yüzde puandır. Bu ifade göreli yüzde artışıyla aynı değildir.",
    ),
    Question(
        "Simpson paradoksu örneğinin temel mesajı nedir?",
        "Genel oranlar alt grupların büyüklüğü ve bileşiminden etkilenebilir. Bu nedenle yalnız toplulaştırılmış oranlara bakmak önemli örüntüleri gizleyebilir.",
    ),
)


def _render_frequency_tab() -> None:
    st.subheader("1. Frekans, göreli frekans ve yüzde frekans")
    st.write(
        "Ders notundaki 40 öğrencilik kampüse ulaşım örneğini kullanarak aynı dağılımı üç farklı ölçekte inceleyelim."
    )

    summary = frequency_summary(TRANSPORT_FREQUENCIES, "Ulaşım biçimi")
    display = summary.copy()
    display["Göreli frekans"] = display["Göreli frekans"].map(lambda x: f"{x:.3f}".replace(".", ","))
    display["Yüzde frekans"] = display["Yüzde frekans"].map(lambda x: f"%{x:.1f}".replace(".", ","))
    st.dataframe(display, hide_index=True, width="stretch")

    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam gözlem", int(summary["Frekans"].sum()))
    c2.metric("En sık kategori", summary.loc[summary["Frekans"].idxmax(), "Ulaşım biçimi"])
    c3.metric("Otobüs yüzdesi", "%40,0")

    scale = st.radio(
        "Grafikte hangi ölçek gösterilsin?",
        ["Frekans", "Yüzde frekans"],
        horizontal=True,
        key="konu02_frequency_scale",
    )
    if scale == "Frekans":
        fig = go.Figure(
            go.Bar(
                x=summary["Ulaşım biçimi"],
                y=summary["Frekans"],
                name="Frekans",
                text=summary["Frekans"],
                textposition="outside",
            )
        )
        fig.update_layout(title="Kampüse ulaşım biçimi: frekans", showlegend=False, yaxis_range=[0, 18])
        render_plotly(
            fig,
            x_title="Ulaşım biçimi",
            y_title="Öğrenci sayısı (frekans)",
            key="konu02_frequency_chart",
        )
    else:
        fig = go.Figure(
            go.Bar(
                x=summary["Ulaşım biçimi"],
                y=summary["Yüzde frekans"],
                name="Yüzde frekans",
                text=[f"%{x:.1f}".replace(".", ",") for x in summary["Yüzde frekans"]],
                textposition="outside",
            )
        )
        fig.update_layout(title="Kampüse ulaşım biçimi: yüzde frekans", showlegend=False, yaxis_range=[0, 45])
        render_plotly(
            fig,
            x_title="Ulaşım biçimi",
            y_title="Öğrencilerin payı (%)",
            key="konu02_percentage_chart",
        )

    st.info(
        "Frekanslar **40**'a, göreli frekanslar **1**'e, yüzde frekanslar **%100**'e toplamlanır. "
        "Bu üç sütun aynı dağılımı farklı ölçeklerde ifade eder."
    )

    st.markdown("#### Kategori sırası neden önemlidir?")
    variable = st.selectbox(
        "Değişkeni seçiniz",
        [
            "Müşteri memnuniyeti: Çok kötü → Kötü → Orta → İyi → Çok iyi",
            "Sosyal medya platformu: A, B, C, D",
            "Kredi notu sınıfı: Düşük → Orta → Yüksek",
        ],
        key="konu02_order_example",
    )
    if "Sosyal medya" in variable:
        st.success("Bu değişken nominaldir. Araştırma amacına göre alfabetik veya frekansa göre sıralama kullanılabilir.")
    else:
        st.success("Bu değişken ordinaldir. Grafikte doğal sıra korunmalıdır.")

    st.caption(
        "Dilim grafiği bütünün parçalarını gösterebilir; ancak küçük farkların karşılaştırılmasında sütun grafiği genellikle daha etkilidir. "
        "Bu uygulamada karşılaştırma amacı nedeniyle eksenli sütun grafiklerini tercih ediyoruz."
    )


def _render_crosstab_tab() -> None:
    st.subheader("2. Çapraz tablo ve doğru paydayı seçmek")
    st.write(
        "60 öğrencilik örnekte bölüm ile ders materyali tercihini birlikte inceleyelim. Bir hücreyi yorumlarken iki kategori birlikte söylenmelidir."
    )

    table = MATERIAL_CROSSTAB.copy()
    table["Toplam"] = table.sum(axis=1)
    total_row = table.sum(axis=0)
    table_with_total = table.copy()
    table_with_total.loc["Toplam"] = total_row
    st.dataframe(table_with_total, width="stretch")

    highlighted = st.selectbox(
        "Bir hücre seçiniz",
        ["İktisat × Dijital", "İşletme × Basılı", "İktisat × Her ikisi"],
        key="konu02_cell_selector",
    )
    interpretations = {
        "İktisat × Dijital": "18 İktisat öğrencisi dijital materyali tercih etmektedir.",
        "İşletme × Basılı": "10 İşletme öğrencisi basılı materyali tercih etmektedir.",
        "İktisat × Her ikisi": "10 İktisat öğrencisi hem basılı hem dijital materyali tercih etmektedir.",
    }
    st.info(interpretations[highlighted])

    st.markdown("#### Aynı hücre, farklı soru, farklı payda")
    question = st.radio(
        "18 sayısını hangi soruya göre yüzdeye çevirelim?",
        [
            "İktisat öğrencilerinin yüzde kaçı dijital tercih ediyor?",
            "Dijital tercih edenlerin yüzde kaçı İktisat öğrencisi?",
        ],
        key="konu02_denominator_question",
    )
    if question.startswith("İktisat"):
        st.metric("Doğru yüzde", "%45,0")
        st.caption("Payda İktisat satır toplamıdır: 18 / 40 × 100 = %45.")
    else:
        st.metric("Doğru yüzde", "%69,2")
        st.caption("Payda Dijital sütun toplamıdır: 18 / 26 × 100 ≈ %69,2.")

    view = st.radio(
        "Grupları hangi biçimde karşılaştıralım?",
        ["Ham frekans", "Satır yüzdesi"],
        horizontal=True,
        key="konu02_crosstab_chart_view",
    )
    if view == "Ham frekans":
        fig = go.Figure()
        for material in MATERIAL_CROSSTAB.columns:
            fig.add_trace(
                go.Bar(
                    x=MATERIAL_CROSSTAB.index,
                    y=MATERIAL_CROSSTAB[material],
                    name=material,
                )
            )
        fig.update_layout(title="Bölüm ve materyal tercihi: ham frekans", barmode="group")
        render_plotly(
            fig,
            x_title="Bölüm",
            y_title="Öğrenci sayısı (frekans)",
            legend_title="Materyal tercihi",
            key="konu02_crosstab_count_chart",
        )
    else:
        percentages = row_percentages(MATERIAL_CROSSTAB)
        fig = go.Figure()
        for material in percentages.columns:
            fig.add_trace(
                go.Bar(
                    x=percentages.index,
                    y=percentages[material],
                    name=material,
                )
            )
        fig.update_layout(title="Her bölümün kendi içindeki materyal dağılımı", barmode="stack", yaxis_range=[0, 100])
        render_plotly(
            fig,
            x_title="Bölüm",
            y_title="Bölüm içindeki pay (%)",
            legend_title="Materyal tercihi",
            key="konu02_crosstab_percent_chart",
        )

    with st.expander("Satır ve sütun yüzdelerini tablo halinde karşılaştır"):
        row_pct = row_percentages(MATERIAL_CROSSTAB).round(1)
        col_pct = column_percentages(MATERIAL_CROSSTAB).round(1)
        st.markdown("**Satır yüzdeleri — her satır %100'e toplamlanır**")
        st.dataframe(row_pct, width="stretch")
        st.markdown("**Sütun yüzdeleri — her sütun %100'e toplamlanır**")
        st.dataframe(col_pct, width="stretch")


def _render_graph_audit_tab() -> None:
    st.subheader("3. Etkili ve yanıltıcı kategorik veri görselleri")
    st.write(
        "Ders notundaki mağaza örneğinde memnuniyet oranları A için %72, B için %78'dir. Eksen başlangıcı görsel algıyı güçlü biçimde etkileyebilir."
    )

    truncated = st.toggle(
        "Dikey ekseni %70'ten başlat (yanıltıcı görünümü dene)",
        value=False,
        key="konu02_truncated_axis",
    )
    fig = go.Figure(
        go.Bar(
            x=["Mağaza A", "Mağaza B"],
            y=[72, 78],
            text=["%72", "%78"],
            textposition="outside",
            name="Memnuniyet",
        )
    )
    if truncated:
        fig.update_layout(title="Aynı sayılar, daraltılmış dikey eksen", yaxis_range=[70, 80], showlegend=False)
    else:
        fig.update_layout(title="Aynı sayılar, sıfırdan başlayan dikey eksen", yaxis_range=[0, 85], showlegend=False)
    render_plotly(
        fig,
        x_title="Mağaza",
        y_title="Müşteri memnuniyeti (%)",
        key="konu02_axis_audit_chart",
    )

    if truncated:
        st.warning(
            "%72 ile %78 arasındaki fark yalnızca **6 yüzde puandır**; %70'ten başlayan eksen bu farkı görsel olarak olduğundan çok büyük gösterebilir."
        )
    else:
        st.success("Sıfırdan başlayan eksen sütun uzunluklarını oranlarla daha tutarlı biçimde gösterir.")

    concept_card(
        "Grafik denetim listesi",
        "Eksen başlangıcını ve ölçeğini kontrol edin; kategori ve ölçü adlarını açık yazın; gereksiz üç boyutlu efektlerden kaçının; görsel seçimini araştırma sorusuna göre yapın.",
    )


def _render_simpson_summary_tab() -> None:
    st.subheader("4. Toplulaştırma, Simpson paradoksu ve bütünleştirici uygulama")
    rates = simpson_rates()
    display = rates.copy()
    display["Dönüşüm oranı"] = display["Dönüşüm oranı"].map(lambda x: f"%{x:.1f}".replace(".", ","))
    st.dataframe(display, hide_index=True, width="stretch")

    level = st.radio(
        "Hangi karşılaştırmayı gösterelim?",
        ["Alt gruplar", "Tüm gruplar"],
        horizontal=True,
        key="konu02_simpson_level",
    )
    if level == "Alt gruplar":
        subgroup = rates[rates["Müşteri grubu"] != "Tüm gruplar"]
        fig = go.Figure()
        for design in ["A", "B"]:
            part = subgroup[subgroup["Tasarım"] == design]
            fig.add_trace(
                go.Bar(
                    x=part["Müşteri grubu"],
                    y=part["Dönüşüm oranı"],
                    name=f"Tasarım {design}",
                )
            )
        fig.update_layout(title="Alt gruplara göre dönüşüm oranları", barmode="group", yaxis_range=[0, 100])
        render_plotly(
            fig,
            x_title="Müşteri grubu",
            y_title="Dönüşüm oranı (%)",
            legend_title="Reklam tasarımı",
            key="konu02_simpson_subgroup_chart",
        )
        st.success("Kolay grupta B: %95 > A: %90; zor grupta B: %20 > A: %10.")
    else:
        overall = rates[rates["Müşteri grubu"] == "Tüm gruplar"]
        fig = go.Figure(
            go.Bar(
                x=[f"Tasarım {x}" for x in overall["Tasarım"]],
                y=overall["Dönüşüm oranı"],
                text=[f"%{x:.1f}".replace(".", ",") for x in overall["Dönüşüm oranı"]],
                textposition="outside",
            )
        )
        fig.update_layout(title="Gruplar birleştirildiğinde dönüşüm oranları", showlegend=False, yaxis_range=[0, 90])
        render_plotly(
            fig,
            x_title="Reklam tasarımı",
            y_title="Genel dönüşüm oranı (%)",
            key="konu02_simpson_overall_chart",
        )
        st.warning("Genelde A ≈ %82,7 > B = %45 görünür. Alt grup büyüklüklerinin bileşimi sonucu tersine çevirmiştir.")

    st.caption(
        "Bu örneğin amacı genel oranların 'yanlış' olduğunu söylemek değil; toplam bir oranın alt grupların bileşiminden etkilenebileceğini göstermektir."
    )

    st.divider()
    st.markdown("#### Bütünleştirici öğrenci anketi")
    resources = frequency_summary(STUDY_RESOURCE_FREQUENCIES, "Kaynak")
    fig = go.Figure(
        go.Bar(
            x=resources["Kaynak"],
            y=resources["Yüzde frekans"],
            text=[f"%{x:.0f}" for x in resources["Yüzde frekans"]],
            textposition="outside",
        )
    )
    fig.update_layout(title="120 öğrencinin ana çalışma kaynağı", showlegend=False, yaxis_range=[0, 40])
    render_plotly(
        fig,
        x_title="Ana çalışma kaynağı",
        y_title="Öğrencilerin payı (%)",
        key="konu02_resource_chart",
    )
    c1, c2 = st.columns(2)
    c1.metric("Ders notu + video", "%60")
    c2.metric("Soru çözümü − ders kitabı", "6 öğrenci / 5 yüzde puan")

    render_question_card("konu02", QUESTIONS)


def render() -> None:
    topic_header(
        2,
        "Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi",
        "Kategorik veride temel amaç, kategori sayılarını doğru paydayla oranlara dönüştürmek ve karşılaştırmayı açık bir tablo veya grafikle sunmaktır.",
    )
    learning_goals(
        [
            "Frekans, göreli frekans ve yüzde frekans dağılımlarını oluşturmak ve yorumlamak.",
            "Nominal ve ordinal kategorilerde uygun kategori sırasını seçmek.",
            "İki kategorik değişken için çapraz tabloyu ve marjinal toplamları okumak.",
            "Satır ve sütun yüzdelerinde doğru paydayı seçmek.",
            "Yan yana ve yüzde 100 yığılmış sütun grafiklerinin hangi sorulara cevap verdiğini ayırt etmek.",
            "Yanıltıcı eksen kullanımını ve toplulaştırmanın oluşturabileceği yanılsamayı fark etmek.",
        ]
    )

    tabs = st.tabs(["Frekans & grafik", "Çapraz tablo", "Grafik denetimi", "Toplulaştırma & kontrol"])
    with tabs[0]:
        _render_frequency_tab()
    with tabs[1]:
        _render_crosstab_tab()
    with tabs[2]:
        _render_graph_audit_tab()
    with tabs[3]:
        _render_simpson_summary_tab()
