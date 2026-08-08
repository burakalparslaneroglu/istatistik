from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number
from core.question_engine import Question, render_question_card
from core.topic03_logic import TRAVEL_TIMES, approximate_class_width, grouped_frequency, stem_leaf
from core.ui_components import learning_goals, render_plotly, topic_header


QUESTIONS = (
    Question(
        "Nicel veride sınıflar veriyle birlikte hazır mıdır?",
        "Hayır. Sınıf sayısı, sınıf genişliği ve sınıf sınırları analistin özetleme tercihidir.",
    ),
    Question(
        "Sınıflar arasında boşluk veya örtüşme neden sorun yaratır?",
        "Bazı gözlemler hiçbir sınıfa girmeyebilir veya birden fazla sınıfa girebilir. Bu nedenle sınıf sınırları açıkça tanımlanmalıdır.",
    ),
    Question(
        "Histogram ile kategorik sütun grafiğinin temel farkı nedir?",
        "Histogram nicel değişkenin bitişik sayısal aralıklarını gösterir; sütun grafiğinde kategoriler ayrı sınıflardır ve sütunlar arasında boşluk bulunur.",
    ),
    Question(
        "Sınıf genişliği büyüdükçe histogramda ne olur?",
        "Ayrıntı azalır ve dağılım daha kaba bir biçimde özetlenir. Çok küçük sınıf genişliği ise görüntüyü gereğinden fazla parçalayabilir.",
    ),
    Question(
        "Son kümülatif yüzde kaç olmalıdır?",
        "%100 olmalıdır; çünkü son sınıfa gelindiğinde bütün gözlemler kapsanmıştır.",
    ),
    Question(
        "Gövde–yaprak gösteriminin temel avantajı nedir?",
        "Dağılımın biçimini gösterirken tek tek gözlem değerlerini büyük ölçüde korur.",
    ),
)


def _render_raw_grouping_tab() -> None:
    st.subheader("1. Ham nicel veriden sınıflara")
    st.write(
        "Ders notundaki örnekte 40 öğrencinin kampüse tek yönlü ulaşım süresi dakika cinsinden ölçülmüştür."
    )
    values = [int(x) for x in TRAVEL_TIMES]
    st.dataframe(
        {"Sıralı gözlem": list(range(1, len(values) + 1)), "Ulaşım süresi (dakika)": values},
        hide_index=True,
        width="stretch",
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Gözlem sayısı", len(values))
    c2.metric("En kısa süre", f"{int(TRAVEL_TIMES.min())} dk")
    c3.metric("En uzun süre", f"{int(TRAVEL_TIMES.max())} dk")

    raw_fig = go.Figure(
        go.Scatter(
            x=list(range(1, len(values) + 1)),
            y=TRAVEL_TIMES,
            mode="markers+lines",
            name="Ulaşım süresi",
        )
    )
    raw_fig.update_layout(title="Sıralanmış ham ulaşım süreleri", showlegend=False)
    render_plotly(
        raw_fig,
        x_title="Sıralı gözlem numarası",
        y_title="Ulaşım süresi (dakika)",
        key="konu03_raw_chart",
    )

    class_count = st.slider(
        "Ön değerlendirme için sınıf sayısı",
        min_value=4,
        max_value=10,
        value=7,
        step=1,
        key="konu03_class_count",
    )
    approx = approximate_class_width(TRAVEL_TIMES, class_count)
    st.info(
        f"Yaklaşık sınıf genişliği = (76 − 12) / {class_count} = **{format_number(approx, 2)} dakika**. "
        "Uygulamada daha kolay yorumlanan bir genişliğe yuvarlama yapılabilir. Ders notunda 7 sınıf için 10 dakika seçilmiştir."
    )


def _render_histogram_tab() -> None:
    st.subheader("2. Frekans dağılımı ve histogram")
    width = st.select_slider(
        "Sınıf genişliği (dakika)",
        options=[5, 10, 20],
        value=10,
        key="konu03_class_width",
    )
    grouped = grouped_frequency(TRAVEL_TIMES, width)

    display = grouped[["Sınıf", "Orta nokta", "Frekans", "Göreli frekans", "Yüzde frekans"]].copy()
    display["Göreli frekans"] = display["Göreli frekans"].map(lambda x: f"{x:.3f}".replace(".", ","))
    display["Yüzde frekans"] = display["Yüzde frekans"].map(lambda x: f"%{x:.1f}".replace(".", ","))
    st.dataframe(display, hide_index=True, width="stretch")

    measure = st.radio(
        "Histogramın dikey ekseni",
        ["Frekans", "Yüzde frekans"],
        horizontal=True,
        key="konu03_hist_measure",
    )
    if measure == "Frekans":
        fig = go.Figure(
            go.Bar(
                x=grouped["Orta nokta"],
                y=grouped["Frekans"],
                width=[width] * len(grouped),
                name="Frekans",
            )
        )
        fig.update_layout(title=f"Ulaşım süresi histogramı — sınıf genişliği {width} dakika", bargap=0, showlegend=False)
        render_plotly(
            fig,
            x_title="Ulaşım süresi (dakika)",
            y_title="Öğrenci sayısı (frekans)",
            key="konu03_hist_frequency",
        )
    else:
        fig = go.Figure(
            go.Bar(
                x=grouped["Orta nokta"],
                y=grouped["Yüzde frekans"],
                width=[width] * len(grouped),
                name="Yüzde frekans",
            )
        )
        fig.update_layout(title=f"Ulaşım süresi yüzde histogramı — sınıf genişliği {width} dakika", bargap=0, showlegend=False)
        render_plotly(
            fig,
            x_title="Ulaşım süresi (dakika)",
            y_title="Öğrencilerin payı (%)",
            key="konu03_hist_percent",
        )

    if width == 10:
        st.success("Ders notundaki 10 dakikalık sınıflarda en yoğun aralık 30–<40 dakikadır ve 11 gözlem içerir.")
    elif width == 20:
        st.warning("Daha geniş sınıflar daha sade bir görünüm sağlar; ancak 10 dakikalık sınıflarda görülen bazı ayrıntılar birleşir.")
    else:
        st.info("Daha dar sınıflar daha fazla ayrıntı gösterir; fakat dağılım daha parçalı görünebilir.")

    st.caption(
        "Histogramda sınıflar sayısal eksende bitişiktir. Bu nedenle sütunlar arasında kategorik sütun grafiğindeki gibi anlamlı boşluk yoktur."
    )


def _render_cumulative_stem_tab() -> None:
    st.subheader("3. Kümülatif dağılım ve gövde–yaprak")
    grouped = grouped_frequency(TRAVEL_TIMES, 10)

    cumulative_fig = go.Figure(
        go.Scatter(
            x=grouped["Üst sınır"],
            y=grouped["Kümülatif yüzde"],
            mode="lines+markers",
            name="Kümülatif yüzde",
        )
    )
    cumulative_fig.update_layout(title="Ulaşım süresinin kümülatif yüzde dağılımı", yaxis_range=[0, 105], showlegend=False)
    render_plotly(
        cumulative_fig,
        x_title="Sınıfın üst sınırı (dakika)",
        y_title="Kümülatif yüzde (%)",
        key="konu03_cumulative_chart",
    )

    threshold = st.select_slider(
        "'Bu süreden kısa' eşiğini seçiniz",
        options=[20, 30, 40, 50, 60, 70, 80],
        value=50,
        key="konu03_cumulative_threshold",
    )
    row = grouped[grouped["Üst sınır"] == threshold].iloc[0]
    st.metric(
        f"{threshold} dakikadan kısa",
        f"{int(row['Kümülatif frekans'])} öğrenci / %{row['Kümülatif yüzde']:.1f}".replace(".", ","),
    )

    st.markdown("#### Gövde–yaprak gösterimi")
    stem_rows = stem_leaf(TRAVEL_TIMES)
    st.dataframe(
        {"Gövde": [s for s, _ in stem_rows], "Yapraklar": [leaves for _, leaves in stem_rows]},
        hide_index=True,
        width="stretch",
    )
    st.caption("Anahtar: **3 | 5 = 35 dakika**. Yapraklar her gövde içinde küçükten büyüğe sıralanır.")


def _render_summary_tab() -> None:
    st.subheader("4. Dağılımı raporlamak")
    grouped = grouped_frequency(TRAVEL_TIMES, 10)
    st.markdown(
        "Ders notundaki bütünleştirici raporlamada tablo, histogram ve kümülatif dağılım birlikte okunur. "
        "Aşağıdaki sonuçları aynı örnekten doğrudan elde ediyoruz."
    )
    between_20_40 = int(((TRAVEL_TIMES >= 20) & (TRAVEL_TIMES < 40)).sum())
    ge_60 = int((TRAVEL_TIMES >= 60).sum())
    c1, c2 = st.columns(2)
    c1.metric("20–<40 dakika", f"{between_20_40} öğrenci / %{100 * between_20_40 / len(TRAVEL_TIMES):.1f}".replace(".", ","))
    c2.metric("60 dakika ve üzeri", f"{ge_60} öğrenci / %{100 * ge_60 / len(TRAVEL_TIMES):.1f}".replace(".", ","))

    st.info(
        "10 dakikalık sınıflamada dağılım 30–<40 dakika çevresinde en yüksek frekansa ulaşır; 60 dakika ve üzerindeki gözlemler daha seyrektir."
    )
    st.warning(
        "Sınıf genişliği grafik görünümünü etkiler. Bu nedenle histogram yorumlanırken yalnız şekle değil, kullanılan sınıf sınırlarına ve genişliğine de bakılmalıdır."
    )
    render_question_card("konu03", QUESTIONS)


def render() -> None:
    topic_header(
        3,
        "Nicel Verilerin Özetlenmesi",
        "Nicel veriyi özetlerken sayısal ekseni sınıflara ayırır; frekans, histogram ve kümülatif gösterimlerle dağılımın nerede yoğunlaştığını inceleriz.",
    )
    learning_goals(
        [
            "Sınıf sayısı, sınıf genişliği ve sınıf sınırlarını açık biçimde tanımlamak.",
            "Nicel frekans, göreli frekans ve yüzde frekans dağılımlarını oluşturmak.",
            "Sınıf orta noktasını hesaplamak ve histogramı doğru okumak.",
            "Histogramın sınıf genişliğine duyarlılığını görmek.",
            "Kümülatif frekans ve kümülatif yüzdeyi yorumlamak.",
            "Gövde–yaprak gösteriminin tek tek değerleri nasıl koruduğunu görmek.",
        ]
    )

    tabs = st.tabs(["Ham veri & sınıflar", "Histogram", "Kümülatif & gövde–yaprak", "Raporlama & kontrol"])
    with tabs[0]:
        _render_raw_grouping_tab()
    with tabs[1]:
        _render_histogram_tab()
    with tabs[2]:
        _render_cumulative_stem_tab()
    with tabs[3]:
        _render_summary_tab()
