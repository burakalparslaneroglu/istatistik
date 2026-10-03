"""Uygulama kabuğu ve yeni mimariye taşınan konuların uçtan uca duman testleri."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _run_app() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=60).run()


def _markdown(app: AppTest) -> str:
    return "\n".join(item.value for item in app.markdown)


def test_app_opens_on_topic_01_with_three_tabs() -> None:
    app = _run_app()
    assert not app.exception
    assert app.radio(key="selected_topic").value == "konu01"
    assert "Veri ve İstatistiğe Giriş" in _markdown(app)
    assert [tab.label for tab in app.tabs][:3] == ["Uygulama", "Sezgi", "Kendini sına"]
    assert app.segmented_control(key="konu01_lab_step").value == 1
    assert {"Gözlem sayısı n": "8", "Değişken sayısı": "4"}.items() <= {m.label: m.value for m in app.metric}.items()


def test_every_lab_step_renders_in_both_languages() -> None:
    app = _run_app()
    for topic, steps in (("konu01", 5), ("konu02", 12), ("konu03", 11), ("konu04", 10), ("konu05", 12),
                         ("konu06", 9), ("konu07", 10), ("konu08", 12), ("konu09", 8), ("konu10", 7), ("konu11", 10),
                         ("konu12", 6)):
        app.radio(key="selected_topic").set_value(topic).run()
        for language in ("Python", "R"):
            app.segmented_control(key="code_language").set_value(language).run()
            for number in range(1, steps + 1):
                app.segmented_control(key=f"{topic}_lab_step").set_value(number).run()
                assert not app.exception, (topic, language, number)
                assert any(item.value.startswith(f"Adım {number}:") for item in app.subheader)


def test_lab_step_shows_the_notes_numbers_in_turkish_format() -> None:
    app = _run_app()
    app.segmented_control(key="konu01_lab_step").set_value(4).run()
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Geçme oranı"] == "0,625"
    assert metrics["Geçme yüzdesi"] == "%62,5"
    assert metrics["Ortalama puan"] == "64,0"


def test_percentile_step_shows_the_location_and_value_as_in_the_notes() -> None:
    app = _run_app()
    app.radio(key="selected_topic").set_value("konu04").run()
    app.segmented_control(key="konu04_lab_step").set_value(7).run()
    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Konum L₆₀"] == "7,8"
    assert metrics["60. yüzdelik P₆₀"] == "54,8"


def test_every_experiment_runs_and_reacts_to_its_sliders() -> None:
    app = _run_app()
    app.slider(key="konu01_sezgi1_c").set_value(3.0).run()
    leaders = {metric.label: metric.value for metric in app.metric}
    assert leaders["Önde olan şube, kod 1-2-3"] == leaders["Önde olan şube, kod 1-2-c"] == "A"
    app.slider(key="konu01_sezgi1_c").set_value(10.0).run()
    assert {metric.label: metric.value for metric in app.metric}["Önde olan şube, kod 1-2-c"] == "B"
    for topic in ("konu01", "konu02", "konu03", "konu04", "konu05", "konu06", "konu07", "konu08", "konu09",
                  "konu10", "konu11", "konu12"):
        app.radio(key="selected_topic").set_value(topic).run()
        for number in (1, 2, 3):
            app.segmented_control(key=f"{topic}_sezgi_deney").set_value(number).run()
            assert not app.exception, (topic, number)


def test_quiz_checks_an_answer_and_lists_sections_to_review() -> None:
    app = _run_app()
    app.radio(key="konu01_quiz_k01").set_value(1).run()
    app.button(key="konu01_quiz_check_k01").click().run()
    assert not app.exception
    assert any("Tekrar edilecek bölümler" in item.value and "§1.1" in item.value for item in app.markdown)


def test_topic_switch_keeps_text_scale_and_code_language() -> None:
    app = _run_app()
    app.select_slider(key="text_scale_label").set_value("%120").run()
    app.segmented_control(key="code_language").set_value("R").run()
    app.radio(key="selected_topic").set_value("konu02").run()
    assert not app.exception
    assert app.session_state["text_scale"] == 1.2
    assert app.session_state["code_language"] == "R"
    assert "Kategorik Verilerin Tablo ve Grafiklerle Özetlenmesi" in _markdown(app)


def test_lab_source_selector_offers_the_alternative_example() -> None:
    app = _run_app()
    assert app.segmented_control(key="konu01_lab_kaynak").value == "notlar"
    for topic, steps in (("konu01", 5), ("konu02", 12), ("konu03", 11), ("konu04", 10)):
        app.radio(key="selected_topic").set_value(topic).run()
        app.segmented_control(key=f"{topic}_lab_kaynak").set_value("alternatif").run()
        assert "Kurgusal veri" in _markdown(app)
        for language in ("Python", "R"):
            app.segmented_control(key="code_language").set_value(language).run()
            for number in range(1, steps + 1):
                app.segmented_control(key=f"{topic}_lab_step").set_value(number).run()
                assert not app.exception, (topic, language, number)
                assert any(item.value.startswith(f"Adım {number}:") for item in app.subheader)
    app.radio(key="selected_topic").set_value("konu05").run()
    assert not any(widget.key == "konu05_lab_kaynak" for widget in app.segmented_control)


def test_own_data_upload_runs_every_step() -> None:
    from core.labs import kendi_veri as K
    from core.labs.ornekler import VARIANTS

    app = _run_app()
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    roles = {
        "konu01": {"sayisal": "Günlük ciro (bin TL)", "kimlik": "Kafe", "ikili": "Hedef durumu"},
        "konu02": {"satir": "Şube", "secenek": "Şube", "altgrup": "Sipariş türü", "sonuc": "Memnuniyet"},
        "konu03": {"sayisal": "Memnuniyet puanı"},
        "konu04": {"grup": "Oda sayısı", "buyume": "Yıllık kira artışı (%)"},
    }
    for topic, steps in (("konu01", 5), ("konu02", 12), ("konu03", 11), ("konu04", 10)):
        app.radio(key="selected_topic").set_value(topic).run()
        app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
        assert any("dosya yükleyin" in item.value for item in app.info)
        data = K.sample_excel(VARIANTS[topic].custom.sample())
        app.file_uploader(key=f"{topic}_kendi_dosya").upload(f"{topic}.xlsx", data, mime).run()
        for role, column in roles[topic].items():
            app.selectbox(key=f"{topic}_kendi_rol_{role}").set_value(column).run()
        assert not app.exception and not app.error, [item.value for item in app.error]
        for number in range(1, steps + 1):
            app.segmented_control(key=f"{topic}_lab_step").set_value(number).run()
            assert not app.exception, (topic, number)
            assert any(item.value.startswith(f"Adım {number}:") for item in app.subheader)
            assert not any("sütun seçin" in item.value for item in app.markdown), (topic, number)


def test_class_count_slider_changes_the_konu03_classes() -> None:
    from core.labs import kendi_veri as K
    from core.labs.ornekler import VARIANTS

    app = _run_app()
    topic, mime = "konu03", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    app.radio(key="selected_topic").set_value(topic).run()
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
    app.file_uploader(key=f"{topic}_kendi_dosya").upload("anket.xlsx", K.sample_excel(VARIANTS[topic].custom.sample()),
                                                         mime).run()
    slider = next(widget for widget in app.slider if str(widget.key).startswith(f"{topic}_kendi_ayar_k_"))
    assert slider.value == 7  # ⌈1 + log₂ 50⌉
    app.segmented_control(key=f"{topic}_lab_step").set_value(2).run()
    assert "/7" in _markdown(app)
    slider.set_value(15).run()
    assert not app.exception and "/15" in _markdown(app)
    app.segmented_control(key=f"{topic}_lab_step").set_value(3).run()
    assert not app.exception


def _class_slider(app: AppTest):
    return next(widget for widget in app.slider if str(widget.key).startswith("konu03_kendi_ayar_k_"))


def test_class_count_error_appears_under_the_slider() -> None:
    """Sınıf sınırları önerilen k ile yazılamıyorsa kaydırıcı yine çizilir ve hata altında görünür; k değişince
    uygulama açılır."""

    app = _run_app()
    app.radio(key="selected_topic").set_value("konu03").run()
    app.segmented_control(key="konu03_lab_kaynak").set_value("kendi").run()
    data = ("x\n" + "\n".join(str(value) for value in (0, 10 ** 9, 2 * 10 ** 9, 3 * 10 ** 9, 4 * 10 ** 9, 5 * 10 ** 9,
                                                        6 * 10 ** 9, 7 * 10 ** 9, 8 * 10 ** 9, 89 * 10 ** 8)) + "\n")
    app.file_uploader(key="konu03_kendi_dosya").upload("buyuk.csv", data.encode("utf-8"), "text/csv").run()
    assert not app.exception and _class_slider(app).value == 5
    assert any("sınıf sayılarından birini seçin: 18, 19 ve 20" in item.value for item in app.error)
    _class_slider(app).set_value(18).run()
    assert not app.exception and not app.error, [item.value for item in app.error]
    assert any(item.value.startswith("Adım 1:") for item in app.subheader)


def test_class_count_follows_the_excel_sheet() -> None:
    import io

    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(2)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"Puan": rng.integers(20, 99, 10)}).to_excel(writer, sheet_name="Az", index=False)
        pd.DataFrame({"Puan": rng.integers(20, 99, 300)}).to_excel(writer, sheet_name="Çok", index=False)
    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    app = _run_app()
    app.radio(key="selected_topic").set_value("konu03").run()
    app.segmented_control(key="konu03_lab_kaynak").set_value("kendi").run()
    app.file_uploader(key="konu03_kendi_dosya").upload("iki_sayfa.xlsx", buffer.getvalue(), mime).run()
    assert _class_slider(app).value == 5  # ⌈1 + log₂ 10⌉
    _class_slider(app).set_value(6).run()
    app.selectbox(key="konu03_kendi_sayfa").set_value("Çok").run()
    assert not app.exception and _class_slider(app).value == 10  # ⌈1 + log₂ 300⌉; önceki sayfanın seçimi taşınmaz
    app.selectbox(key="konu03_kendi_sayfa").set_value("Az").run()
    assert _class_slider(app).value == 6


def test_class_count_follows_the_column_even_when_code_names_coincide() -> None:
    """"Puan (1)" ve "Puan 1" kodda aynı adı alır (puan_1); kaydırıcı yine de dosyadaki sütuna bağlıdır."""

    rows = ["Puan (1),Puan 1"] + [f"{40 + index % 50},{30 + index % 60}" if index < 10 else f",{30 + index % 60}"
                                  for index in range(300)]
    app = _run_app()
    app.radio(key="selected_topic").set_value("konu03").run()
    app.segmented_control(key="konu03_lab_kaynak").set_value("kendi").run()
    app.file_uploader(key="konu03_kendi_dosya").upload("puan.csv", ("\n".join(rows) + "\n").encode("utf-8"),
                                                       "text/csv").run()
    app.selectbox(key="konu03_kendi_rol_sayisal").set_value("Puan (1)").run()
    assert _class_slider(app).value == 5  # n = 10
    _class_slider(app).set_value(6).run()
    app.selectbox(key="konu03_kendi_rol_sayisal").set_value("Puan 1").run()
    assert not app.exception and _class_slider(app).value == 10  # n = 300


def test_own_data_survives_a_source_switch_and_follows_the_file_name() -> None:
    """Kaynak değişince Streamlit widget durumunu siler; dosya ve seçimler yine de korunur. Aynı içerik başka adla
    yüklenince üretilen kod yeni adı kullanır."""

    from core.labs import kendi_veri as K
    from core.labs.ornekler import VARIANTS

    app = _run_app()
    topic, mime = "konu02", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    data = K.sample_excel(VARIANTS[topic].custom.sample())
    app.radio(key="selected_topic").set_value(topic).run()
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
    app.file_uploader(key=f"{topic}_kendi_dosya").upload("ilk.xlsx", data, mime).run()
    app.selectbox(key=f"{topic}_kendi_rol_satir").set_value("Sipariş türü").run()
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("notlar").run()
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
    assert not app.exception and not app.error, [item.value for item in app.error]
    assert app.selectbox(key=f"{topic}_kendi_rol_satir").value == "Sipariş türü"
    assert any("Kullanılan dosya: ilk.xlsx" in item.value for item in app.caption)
    assert "Yüklediğiniz veri dosyası: ilk.xlsx" in _markdown(app)
    app.button(key=f"{topic}_kendi_kaldir").click().run()
    assert any("dosya yükleyin" in item.value for item in app.info)
    app.file_uploader(key=f"{topic}_kendi_dosya").upload("ikinci.xlsx", data, mime).run()
    assert not app.exception and "Yüklediğiniz veri dosyası: ikinci.xlsx" in _markdown(app)


def test_own_data_labels_are_escaped_and_removal_clears_the_session() -> None:
    """Kullanıcının adları başlık ve etiketlerde Markdown/KaTeX olarak yorumlanmaz; dosya kaldırılınca okunan veri
    oturum belleğinde kalmaz."""

    rows = ["Puan;Fiyat"] + [f"{50 + 7 * index % 23};{'$5 ve üstü' if index % 2 else '$5 altı'}" for index in range(8)]
    data = ("\n".join(rows) + "\n").encode()
    app = _run_app()
    topic = "konu01"
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
    app.file_uploader(key=f"{topic}_kendi_dosya").upload("fiyat_listesi.csv", data, "text/csv").run()
    assert app.selectbox(key=f"{topic}_kendi_rol_ikili").value == "Fiyat"
    app.segmented_control(key=f"{topic}_lab_step").set_value(1).run()
    assert "Yüklediğiniz veri dosyası: fiyat\\_listesi.csv" in _markdown(app)
    app.segmented_control(key=f"{topic}_lab_step").set_value(2).run()
    assert not app.exception and not app.error, [item.value for item in app.error]
    headings = [item.value for item in app.markdown if "kodlaması" in item.value]
    assert headings and all("\\$5" in item and "$5" not in item.replace("\\$5", "") for item in headings)
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("notlar").run()
    app.segmented_control(key=f"{topic}_lab_kaynak").set_value("kendi").run()
    app.button(key=f"{topic}_kendi_kaldir").click().run()
    left = [str(key) for key in app.session_state.filtered_state if str(key).startswith(f"{topic}_kendi_")]
    assert not any(key.endswith(("_tablo", "_uygulama", "_yuklenen", "_ozet")) for key in left), left
