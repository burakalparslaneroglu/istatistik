from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.formatting import format_number, format_percent
from core.question_engine import Question, render_question_card
from core.topic01_logic import (
    DATA_SOURCE_EXAMPLES,
    INFERENCE_EXAMPLES,
    SAMPLE_SCENARIOS,
    STUDENT_DATA,
    TIME_STRUCTURE_EXAMPLES,
    VARIABLE_EXAMPLES,
    analytical_variable_count,
    classify_data_source,
    classify_inference,
    classify_time_structure,
    classify_variable,
    mean_exam_score,
    passing_rate,
)
from core.ui_components import (
    concept_card,
    feedback_box,
    learning_goals,
    render_definition_grid,
    render_plotly,
    reset_widget_state,
    topic_header,
)


QUESTIONS = (
    Question(
        "Bir veri tablosunda sütun çoğunlukla neyi temsil eder?",
        "Sütun çoğunlukla bir değişkeni temsil eder. Satır ise bir gözlemi temsil eder.",
    ),
    Question(
        "Bir değişkenin sayılarla kodlanması onu otomatik olarak nicel yapar mı?",
        "Hayır. Öğrenci numarası veya 1=Kadın, 2=Erkek gibi kodlar sayısal görünse de kategorik olabilir.",
    ),
    Question(
        "Zaman serisinde gözlemlerin sırası neden önemlidir?",
        "Çünkü gözlemler zaman içinde ardışık dönemlere aittir; dönemlerin sırasını değiştirmek verinin zaman yapısını bozar.",
    ),
    Question(
        "Örneklem büyüdükçe temsil gücü mutlaka artar mı?",
        "Hayır. Sistematik biçimde yanlı seçilmiş büyük bir örneklem, daha küçük fakat iyi seçilmiş bir örneklemden daha kötü olabilir.",
    ),
    Question(
        "Gözlemsel veride iki değişken birlikte hareket ediyorsa nedensellik kanıtlanmış olur mu?",
        "Hayır. İlişki nedensellik için tek başına yeterli değildir; veri üretim süreci ve araştırma tasarımı hakkında daha fazla bilgi gerekir.",
    ),
)


def _render_data_table_tab() -> None:
    st.subheader("1. Veri tablosunu okuyalım")
    st.write(
        "İstatistiksel analizden önce, her satırın ve sütunun neyi temsil ettiğini doğru tanımlamak gerekir."
    )

    st.dataframe(STUDENT_DATA, hide_index=True, width="stretch")

    c1, c2, c3 = st.columns(3)
    c1.metric("Gözlem sayısı", len(STUDENT_DATA))
    c2.metric("Analitik değişken sayısı", analytical_variable_count())
    c3.metric("Ortalama sınav puanı", format_number(mean_exam_score()))

    selected_student = st.selectbox(
        "Bir öğrenciyi seçerek tek bir gözlemi inceleyiniz",
        STUDENT_DATA["Öğrenci"].tolist(),
        key="konu01_student_selector",
    )
    row = STUDENT_DATA.loc[STUDENT_DATA["Öğrenci"] == selected_student].iloc[0]
    st.info(
        f"{selected_student} öğrencisinin gözlemi: {row['Bölüm']}, "
        f"{row['Haftalık çalışma (saat)']} saat çalışma, {row['Sınav puanı']} puan, {row['Ders durumu']}."
    )

    render_definition_grid(
        [
            ("Gözlem birimi", "Hakkında veri topladığımız kişi, firma, ürün, ülke, dönem veya başka bir birimdir."),
            ("Değişken", "Gözlem birimleri üzerinde ölçtüğümüz özelliktir."),
            ("Gözlem", "Tek bir gözlem birimi için kaydedilen değişken değerlerinin bütünüdür."),
            ("Veri seti", "Belirli bir çalışma için toplanan gözlemlerin tamamıdır."),
        ]
    )

    st.caption(
        f"Bu sekiz öğrencide geçme oranı {format_percent(passing_rate())}. Bu oran yalnızca gözlediğimiz sekiz öğrenciyi betimler."
    )


def _render_variable_tab() -> None:
    st.subheader("2. Değişken türleri ve ölçme düzeyleri")
    st.write(
        "Bir değişkeni sınıflandırırken önce kategorik–nicel ayrımını, ardından hangi karşılaştırmaların anlamlı olduğunu düşünün."
    )

    example = st.selectbox(
        "Sınıflandırılacak değişken",
        list(VARIABLE_EXAMPLES),
        key="konu01_variable_example",
        on_change=reset_widget_state,
        args=("konu01_variable_type_answer", "konu01_scale_answer"),
    )
    true_type, true_scale = classify_variable(example)

    col1, col2 = st.columns(2)
    with col1:
        chosen_type = st.radio(
            "Değişken türü",
            ["Kategorik", "Nicel – kesikli", "Nicel – sürekli"],
            index=None,
            key="konu01_variable_type_answer",
        )
    with col2:
        chosen_scale = st.radio(
            "Ölçme düzeyi",
            ["Nominal", "Ordinal", "Aralık", "Oran"],
            index=None,
            key="konu01_scale_answer",
        )

    if st.button("Sınıflandırmayı kontrol et", key="konu01_check_variable"):
        if chosen_type is None or chosen_scale is None:
            st.warning("Kontrol etmeden önce hem değişken türünü hem ölçme düzeyini seçin.")
        else:
            type_ok = chosen_type == true_type
            scale_ok = chosen_scale == true_scale
            feedback_box(
                type_ok and scale_ok,
                f"Doğru. Tür: {true_type}; ölçme düzeyi: {true_scale}.",
                f"Tekrar düşünün. Ders notundaki sınıflandırmaya göre tür: {true_type}; ölçme düzeyi: {true_scale}.",
            )

    with st.expander("Ölçme düzeylerini karşılaştır"):
        st.markdown(
            "- **Nominal:** kategori vardır, doğal sıra yoktur.\n"
            "- **Ordinal:** kategori ve anlamlı sıra vardır.\n"
            "- **Aralık:** eşit farklar anlamlıdır; sıfır mutlak yokluk değildir.\n"
            "- **Oran:** eşit farklara ek olarak gerçek sıfır vardır; oranlar anlamlıdır."
        )


def _render_time_source_tab() -> None:
    st.subheader("3. Zaman boyutu ve verinin kaynağı")

    st.markdown("#### Yatay kesit ve zaman serisi")
    scenario = st.selectbox(
        "Veri yapısını sınıflandırınız",
        list(TIME_STRUCTURE_EXAMPLES),
        key="konu01_time_scenario",
        on_change=reset_widget_state,
        args=("konu01_time_answer",),
    )
    answer = st.radio(
        "Bu veri hangi yapıdadır?",
        ["Yatay kesit", "Zaman serisi"],
        index=None,
        horizontal=True,
        key="konu01_time_answer",
    )
    if st.button("Veri yapısını kontrol et", key="konu01_check_time"):
        if answer is None:
            st.warning("Kontrol etmeden önce veri yapısını seçin.")
        else:
            correct = classify_time_structure(scenario)
            feedback_box(
                answer == correct,
                f"Doğru: {correct}.",
                f"Bu örnek {correct} verisidir. Gözlem birimi ile zaman boyutunu yeniden ayırmayı deneyin.",
            )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        cross_fig = go.Figure(
            data=[
                go.Bar(
                    x=STUDENT_DATA["Öğrenci"],
                    y=STUDENT_DATA["Sınav puanı"],
                    name="Sınav puanı",
                )
            ]
        )
        cross_fig.update_layout(title="Yatay kesit: aynı sınav, farklı öğrenciler", showlegend=False)
        render_plotly(
            cross_fig,
            x_title="Öğrenci",
            y_title="Sınav puanı (puan)",
            key="konu01_cross_section_chart",
        )

    with chart_col2:
        months = list(range(1, 9))
        index_values = [100, 102, 101, 106, 111, 116, 121, 128]
        time_fig = go.Figure(
            data=[
                go.Scatter(
                    x=months,
                    y=index_values,
                    mode="lines+markers",
                    name="Fiyat endeksi",
                )
            ]
        )
        time_fig.update_layout(title="Zaman serisi: aynı değişken, farklı aylar", showlegend=False)
        render_plotly(
            time_fig,
            x_title="Ay",
            y_title="Fiyat endeksi (endeks puanı)",
            key="konu01_time_series_chart",
        )

    st.caption(
        "Solda gözlemler farklı öğrencilerdir; sağda X ekseni doğrudan zamanı gösterir ve gözlem sırası veri yapısının bir parçasıdır."
    )

    st.divider()
    st.markdown("#### Veri nasıl elde edildi?")
    source_scenario = st.selectbox(
        "Senaryo",
        list(DATA_SOURCE_EXAMPLES),
        key="konu01_source_scenario",
        on_change=reset_widget_state,
        args=("konu01_source_answer",),
    )
    source_answer = st.radio(
        "Veri elde etme yolu",
        ["Mevcut kaynak", "Gözlemsel çalışma", "Deney"],
        index=None,
        horizontal=True,
        key="konu01_source_answer",
    )
    if st.button("Veri kaynağını kontrol et", key="konu01_check_source"):
        if source_answer is None:
            st.warning("Kontrol etmeden önce veri elde etme yolunu seçin.")
        else:
            correct = classify_data_source(source_scenario)
            feedback_box(
                source_answer == correct,
                f"Doğru: {correct}.",
                f"Bu senaryoda en uygun sınıflandırma: {correct}.",
            )

    st.warning(
        "Gözlemsel veride iki değişkenin birlikte hareket etmesi, birinin diğerini mutlaka nedenlediği anlamına gelmez."
    )


def _render_inference_sample_tab() -> None:
    st.subheader("4. Betimleme, çıkarım, anakütle ve örneklem")

    inference_scenario = st.selectbox(
        "İfadeyi sınıflandırınız",
        list(INFERENCE_EXAMPLES),
        key="konu01_inference_scenario",
        on_change=reset_widget_state,
        args=("konu01_inference_answer",),
    )
    inference_answer = st.radio(
        "Bu ifade hangi amaca daha yakındır?",
        ["Betimsel istatistik", "İstatistiksel çıkarım"],
        index=None,
        horizontal=True,
        key="konu01_inference_answer",
    )
    if st.button("İfadeyi kontrol et", key="konu01_check_inference"):
        if inference_answer is None:
            st.warning("Kontrol etmeden önce sınıflandırmanızı seçin.")
        else:
            correct = classify_inference(inference_scenario)
            feedback_box(
                inference_answer == correct,
                f"Doğru: {correct}.",
                f"Bu ifade {correct} örneğidir. Gözlenen verinin dışına çıkılıp çıkılmadığına dikkat edin.",
            )

    st.divider()
    st.markdown("#### Büyük örneklem her zaman iyi örneklem midir?")
    sample_size = st.slider(
        "Örneklem büyüklüğü (n)",
        min_value=50,
        max_value=5000,
        value=400,
        step=50,
        key="konu01_sample_size",
    )
    sample_name = st.selectbox(
        "Örneklem seçme biçimi",
        [scenario.name for scenario in SAMPLE_SCENARIOS],
        key="konu01_sample_scenario",
    )
    selected = next(s for s in SAMPLE_SCENARIOS if s.name == sample_name)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Seçilen örneklem", f"n = {sample_size}")
    with c2:
        st.info(f"**Seçim biçimi:** {selected.description}\n\n**Yorum:** {selected.representativeness}")

    st.caption(
        "Kaydırıcı özellikle şu fikri vurgular: örneklem büyüklüğü önemlidir; fakat seçim mekanizmasındaki sistematik yanlılığı otomatik olarak ortadan kaldırmaz."
    )


def _render_ethics_summary_tab() -> None:
    st.subheader("5. Etik, yazılımın rolü ve bütünleştirici uygulama")

    ethics_scenario = st.selectbox(
        "Etik değerlendirme senaryosu",
        [
            "Restoran anketi yalnızca sadakat kartı olan müşterilere gönderiliyor.",
            "Araştırmacı üç düşük gözlemi gerekçe göstermeden veri setinden çıkarıyor.",
            "Bir rapor iki değişken arasında ilişki bulup doğrudan nedensellik iddia ediyor.",
        ],
        key="konu01_ethics_scenario",
    )
    ethics_map = {
        "Restoran anketi yalnızca sadakat kartı olan müşterilere gönderiliyor.": "Örneklem seçimi bütün müşterileri temsil etmeyebilir.",
        "Araştırmacı üç düşük gözlemi gerekçe göstermeden veri setinden çıkarıyor.": "Gözlem dışlama ölçütü açık ve savunulabilir değildir.",
        "Bir rapor iki değişken arasında ilişki bulup doğrudan nedensellik iddia ediyor.": "Sonuç, verinin izin verdiğinden daha güçlü bir dille yorumlanmaktadır.",
    }
    if st.button("Etik sorunu göster", key="konu01_show_ethics"):
        st.warning(ethics_map[ethics_scenario])

    concept_card(
        "Yazılımın rolü",
        "Yazılım hesaplamayı hızlandırır ve grafikleri üretir; fakat araştırma sorusunun, veri kalitesinin ve yorumun doğruluğuna tek başına karar vermez.",
    )

    st.markdown("#### Ulaşım araştırması: kavramları birleştirelim")
    st.write(
        "Bir üniversite 200 ikinci sınıf öğrencisine ana ulaşım aracını, tek yön ulaşım süresini ve ulaşım kolaylığını soruyor."
    )
    st.table(
        {
            "Kavram": [
                "Gözlem birimi",
                "Kategorik değişken",
                "Ordinal değişken",
                "Nicel değişken",
                "Örneklem",
                "Betimsel soru",
                "Çıkarımsal soru",
            ],
            "Ulaşım araştırmasındaki karşılığı": [
                "Ankete katılan her öğrenci",
                "Ulaşım aracı",
                "Zor / orta / kolay değerlendirmesi",
                "Dakika cinsinden ulaşım süresi",
                "Ankete katılan 200 öğrenci",
                "200 öğrencinin ortalama ulaşım süresi kaç dakikadır?",
                "Bütün ikinci sınıf öğrencilerinin ortalama ulaşım süresi yaklaşık kaç dakikadır?",
            ],
        }
    )

    render_question_card("konu01", QUESTIONS)


def render() -> None:
    topic_header(
        1,
        "Veri ve İstatistiğe Giriş",
        "Bu bölümün amacı hesaplamadan önce verinin neyi temsil ettiğini doğru tanımaktır.",
    )

    learning_goals(
        [
            "Gözlem birimi, değişken, gözlem ve veri setini ayırt etmek.",
            "Değişkenleri kategorik veya nicel olarak sınıflandırmak.",
            "Nominal, ordinal, aralık ve oran ölçme düzeylerini tanımak.",
            "Yatay kesit ve zaman serisi verisini ayırt etmek.",
            "Mevcut kaynak, gözlemsel çalışma ve deney arasındaki farkı görmek.",
            "Betimsel istatistik ile istatistiksel çıkarımı; anakütle ile örneklemi ilişkilendirmek.",
            "Temsil gücü, veri kalitesi ve etik yorumlama sorunlarını fark etmek.",
        ]
    )

    st.info(
        "İstatistiksel düşünme akışı: **soru → veri → düzenleme → özetleme → çıkarım → yorum**. "
        "Bu akış katı bir reçete değildir; veri yeni sorular doğurabilir."
    )

    tabs = st.tabs(
        [
            "Veri tablosu",
            "Değişkenler",
            "Zaman & veri kaynağı",
            "Örneklem & çıkarım",
            "Etik & genel kontrol",
        ]
    )
    with tabs[0]:
        _render_data_table_tab()
    with tabs[1]:
        _render_variable_tab()
    with tabs[2]:
        _render_time_source_tab()
    with tabs[3]:
        _render_inference_sample_tab()
    with tabs[4]:
        _render_ethics_summary_tab()
