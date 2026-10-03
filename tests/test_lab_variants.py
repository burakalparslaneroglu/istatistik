"""Uygulama sekmesinin ek veri kaynakları: alternatif örnek ve kendi verini yükle (``core.labs.ornekler``).

Kayıttaki her konu kendiliğinden kapsanır: alternatif örneğin adımları notlarla aynı numaralıdır ve aynı bölümlere
bağlıdır;
uygulama, üretilen Python ve R kodu aynı sayıları verir. "Kendi verini yükle" seçeneğinde örnek dosya yüklenince
alternatif örneğin sayıları elde edilir; dosya okuma ve temizleme kuralları iki dilde aynıdır.
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.codegen.base import LANGUAGES, render_script, render_step, script_filename
from core.labs import kendi_veri as K
from core.labs.ornek import CustomChoices, custom_case
from core.labs.ornekler import VARIANTS
from core.labs.registry import get_lab
from core.labs.runner import run_lab

TOPICS = sorted(VARIANTS)
R_ENVIRONMENT = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8")
SAMPLE_ROLES = {
    "konu01": ({"sayisal": "Günlük ciro (bin TL)", "kimlik": "Kafe", "ikili": "Hedef durumu"},
               ("İlçe", "Personel sayısı"), {"ikili": "Tuttu"}),
    "konu02": ({"ana": "Ödeme yöntemi", "satir": "Şube", "secenek": "Şube", "altgrup": "Sipariş türü",
                "sonuc": "Memnuniyet"}, (), {"sonuc": "Memnun"}),
    "konu03": ({"sayisal": "Memnuniyet puanı"}, (), {}),
    "konu04": ({"sayisal": "Aylık kira (bin TL)", "grup": "Oda sayısı", "buyume": "Yıllık kira artışı (%)"}, (), {}),
    "konu05": ({"sayisal": "Teslimat mesafesi (km)", "grup": "Depo", "ikinci": "Teslim süresi (saat)"}, (), {}),
    "konu06": ({"olay_e": "Ödeme yöntemi", "olay_f": "Sipariş türü"}, (), {"olay_e": "Mobil", "olay_f": "Paket"}),
}


def _checks(spec) -> int:
    return sum(len(step.checks) for step in spec.steps)


AGG_SHOW = "ignore:FigureCanvasAgg is non-interactive:UserWarning"
"""Agg arka ucunda ``plt.show()`` Windows'ta (ve DISPLAY tanımlı Linux'ta) bu uyarıyı basar; betiğin kendisinden değil
test ortamından gelir. Diğer bütün uyarılar (ör. pandas) testte yakalanmaya devam eder."""


def _python_environment() -> dict[str, str]:
    warnings = ",".join(item for item in (os.environ.get("PYTHONWARNINGS", ""), AGG_SHOW) if item)
    return dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="cp1254", PYTHONWARNINGS=warnings)


def _run_script(spec, language: str, folder: Path, data: tuple[str, bytes] | None = None):
    path = folder / script_filename(spec, language)
    path.write_text(render_script(spec, language), encoding="utf-8")
    if data:
        (folder / data[0]).write_bytes(data[1])
    command = [sys.executable] if language == "Python" else ["Rscript"]
    environment = _python_environment() if language == "Python" else R_ENVIRONMENT
    result = subprocess.run(command + [path.name], cwd=folder, capture_output=True, encoding="utf-8",
                            errors="replace", timeout=300, env=environment)
    return result, path


def _sample_case(topic: str):
    custom = VARIANTS[topic].custom
    table = K.read_upload(f"ornek_{topic}.xlsx", K.sample_excel(custom.sample()))
    roles, extra, picks = SAMPLE_ROLES[topic]
    return custom_case(custom, table, CustomChoices(roles=roles, extra=extra, order="alfabetik", picks=picks))


# --- Alternatif örnek ------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_alternative_mirrors_the_steps_of_the_notes(topic: str) -> None:
    notes, alternative = get_lab(topic), VARIANTS[topic].alternative()
    assert alternative.source == "alternatif" and notes.source == "notlar"
    assert [step.number for step in alternative.steps] == [step.number for step in notes.steps]
    assert [step.note.section for step in alternative.steps] == [step.note.section for step in notes.steps]
    assert all(step.title and step.explanation for step in alternative.steps)
    assert _checks(alternative) >= 6
    assert VARIANTS[topic].story.startswith("Kurgusal veri")


@pytest.mark.parametrize("topic", TOPICS)
def test_alternative_checks_hold_in_the_app(topic: str) -> None:
    run = run_lab(VARIANTS[topic].alternative())
    assert run.all_passed


@pytest.mark.parametrize("topic", TOPICS)
def test_every_alternative_step_renders(topic: str) -> None:
    spec = VARIANTS[topic].alternative()
    for language in LANGUAGES:
        for step in spec.steps:
            assert bool(render_step(spec, step.number, language)) == bool(step.operations)
        assert script_filename(spec, language).startswith(f"ikt217_{topic}_alternatif.")
    script = render_script(spec, "Python")
    assert "kurgusal alternatif örnek" in script and "ders notlarındaki basılı" not in script
    compile(script, f"{topic}.py", "exec")


@pytest.mark.parametrize("topic", TOPICS)
def test_generated_python_reproduces_the_alternative(topic: str, tmp_path: Path) -> None:
    spec = VARIANTS[topic].alternative()
    result, path = _run_script(spec, "Python", tmp_path)
    assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
    assert result.stdout.count("  OK   ") == _checks(spec)
    assert "Bütün değerler uygulamadaki sonuçlarla uyuşuyor." in result.stdout
    assert sorted(item.name for item in tmp_path.iterdir()) == [path.name]


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="Rscript bulunamadı.")
@pytest.mark.parametrize("topic", TOPICS)
def test_generated_r_reproduces_the_alternative(topic: str, tmp_path: Path) -> None:
    spec = VARIANTS[topic].alternative()
    result, path = _run_script(spec, "R", tmp_path)
    assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
    assert result.stdout.count("  OK   ") == _checks(spec)
    assert "warning" not in (result.stdout + result.stderr).lower()
    assert sorted(item.name for item in tmp_path.iterdir()) == [path.name]


def test_notes_scripts_keep_their_wording_and_names() -> None:
    for topic in TOPICS:
        spec = get_lab(topic)
        script = render_script(spec, "Python")
        assert "ders notlarındaki basılı değerlerle karşılaştırılır" in script
        assert "(notlar: " in script and "(uygulama: " not in script
        assert script_filename(spec, "R") == f"ikt217_{topic}_uygulama.R"


NOTES_MD5 = {
    "konu01": "01a3da3a83c642ce86d77675eec12dd7",
    "konu02": "9fb81e24c8eef836b206c820a29d2b9b",
    "konu03": "a1cf5afe031a40936d07a6830491c37c",
    "konu04": "43636012f083f849f5f1a53927af1608",
    "konu05": "5c11318c38bca5c1e807526e0636f42b",
    "konu06": "fa5762eefee1d8b1ca3fe1916dba2909",
    "konu07": "f956dcc9ce8073ba718c0b465696d3d0",
    "konu08": "c73e1e37a1db8959ea115cabfb96f6e3",
    "konu09": "c71c28b6f9b0d8e12a4d2eaea2f0ed8d",
    "konu10": "10d21d54551fb4335ec49b64517d17c5",
    "konu11": "4f3bcce5cc433122a5b3cd09b511f655",
    "konu12": "2b97e321902ff3ce1226edefb9e3bb90",
}
"""Notlardaki örneklerin ve Sezgi deneylerinin üretilen kodu (bütün betik, her adımın kodu, iki dil): md5 özeti.
Ortak koddaki (ör. kod üreticileri) bir değişiklik notların çıktısını değiştirmemelidir. Notlar bilerek
düzeltildiğinde özet yeniden hesaplanır (``_notes_md5``)."""


def _notes_md5(key: str) -> str:
    import hashlib
    import importlib

    from core.codegen.base import generator

    spec = get_lab(key)
    parts = []
    for language in LANGUAGES:
        parts.append(render_script(spec, language))
        parts += [render_step(spec, step.number, language) for step in spec.steps]
    module = importlib.import_module(f"core.labs.sezgi_{key}")
    for experiment in getattr(module, f"{key.upper()}_EXPERIMENTS"):
        parameters = {item.key: item.default for item in experiment.parameters}
        parts += [generator(experiment.spec(parameters), language).script() for language in LANGUAGES]
    return hashlib.md5("\n\u0000\n".join(parts).encode("utf-8")).hexdigest()


@pytest.mark.parametrize("key", sorted(NOTES_MD5))
def test_notes_outputs_are_unchanged(key: str) -> None:
    assert _notes_md5(key) == NOTES_MD5[key]


# --- Kendi verini yükle: örnek dosya -------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_uploading_the_sample_file_gives_the_alternative_numbers(topic: str) -> None:
    case, notes = _sample_case(topic)
    custom = VARIANTS[topic].custom.build(case)
    assert custom.source == "kendi" and not notes
    alternative = {(step.number, check.label): check.expected
                   for step in VARIANTS[topic].alternative().steps for check in step.checks}
    values = {(step.number, check.label): check.expected for step in custom.steps for check in step.checks}
    shared = set(alternative) & set(values)
    assert len(shared) >= 0.9 * len(alternative)
    for key in shared:
        assert values[key] == pytest.approx(alternative[key], abs=1e-9), key


@pytest.mark.parametrize("topic", TOPICS)
def test_generated_python_reads_the_uploaded_excel(topic: str, tmp_path: Path) -> None:
    case, _ = _sample_case(topic)
    spec = VARIANTS[topic].custom.build(case)
    data = (f"ornek_{topic}.xlsx", K.sample_excel(VARIANTS[topic].custom.sample()))
    result, path = _run_script(spec, "Python", tmp_path, data)
    assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
    assert result.stdout.count("  OK   ") == _checks(spec)
    assert sorted(item.name for item in tmp_path.iterdir()) == sorted([path.name, data[0]])


def _has_readxl() -> bool:
    if shutil.which("Rscript") is None:
        return False
    probe = subprocess.run(["Rscript", "-e", 'quit(status = !requireNamespace("readxl", quietly = TRUE))'],
                           capture_output=True, timeout=60)
    return probe.returncode == 0


@pytest.mark.skipif(not _has_readxl(), reason="R ya da readxl paketi yok (öğrenci makinesinde bir kez çalıştırın).")
@pytest.mark.parametrize("topic", TOPICS)
def test_generated_r_reads_the_uploaded_excel(topic: str, tmp_path: Path) -> None:
    case, _ = _sample_case(topic)
    spec = VARIANTS[topic].custom.build(case)
    data = (f"ornek_{topic}.xlsx", K.sample_excel(VARIANTS[topic].custom.sample()))
    result, path = _run_script(spec, "R", tmp_path, data)
    assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
    assert result.stdout.count("  OK   ") == _checks(spec)
    assert "warning" not in (result.stdout + result.stderr).lower()


# --- Dosya okuma ve temizleme ----------------------------------------------------------

def _messy_frame(mark: str) -> pd.DataFrame:
    """Boş, boşluklu ve metin olarak yazılmış sayılar; ``mark`` metin sayılardaki ondalık işareti."""

    return pd.DataFrame({
        "Ödeme yöntemi": ["Kredi kartı", " Nakit", "Mobil ödeme", None, "Kredi kartı", "Nakit ", "Banka kartı", "T"],
        "Şube kodu": [1, 2, 1, 2, 1, np.nan, 2, 1],
        "Tutar (TL)": [f"12{mark}5", "30", 18, f"22{mark}5", "  ", f"40{mark}25", 15, 9],
    })


def _csv(frame: pd.DataFrame, separator: str, decimal: str, encoding: str) -> bytes:
    text = frame.to_csv(sep=separator, index=False, decimal=decimal)
    return (("﻿" + text).encode("utf-8") if encoding == "utf-8-sig" else text.encode(encoding))


def _messy_spec(table: K.UploadedTable):
    from core.labs.ornek import with_app_values
    from core.labs.spec import Check, CrossTab, FrequencyTable, LabSpec, LabStep, NoteRef, ScalarTarget, \
        Statistic, TableTarget

    names = {"Ödeme yöntemi": "odeme_yontemi", "Şube kodu": "sube_kodu", "Tutar (TL)": "tutar_tl"}
    selections = [K.Selection(names["Ödeme yöntemi"], "Ödeme yöntemi", "kategorik"),
                  K.Selection(names["Şube kodu"], "Şube kodu", "kategorik"),
                  K.Selection(names["Tutar (TL)"], "Tutar (TL)", "sayisal")]
    prepared = K.prepare(table, selections)
    order = K.category_order(prepared.frame["odeme_yontemi"], "alfabetik")
    branches = K.category_order(prepared.frame["sube_kodu"], "alfabetik")
    step = LabStep(1, "Dosya", NoteRef("2.2"), "Deneme", operations=(
        prepared.read,
        FrequencyTable("veri", "odeme_yontemi", "tablo", order, relative=True, totals=True),
        CrossTab("veri", "sube_kodu", "odeme_yontemi", "capraz", branches, order, margins=True),
        Statistic("veri", "tutar_tl", "mean", "ortalama", "Ortalama tutar", decimals=3),
    ), checks=(*(Check(item, TableTarget("tablo", item, "frekans"), 0, 0) for item in order),
               Check("Ortalama", ScalarTarget("ortalama"), 0, 3)))
    return prepared, with_app_values(LabSpec("konu02", "Dosya", "2", (step,), source="kendi"))


def _languages(readxl: bool = False) -> list[str]:
    if readxl:
        return ["Python"] + (["R"] if _has_readxl() else [])
    return ["Python"] + (["R"] if shutil.which("Rscript") else [])


def _reproduce(spec, folder: Path, data: tuple[str, bytes], languages: list[str]) -> None:
    """Üretilen betik dosyayı okuyup uygulamanın bütün sayılarını yeniden üretmeli."""

    for language in languages:
        place = folder / language
        place.mkdir(parents=True)
        result, _ = _run_script(spec, language, place, data)
        assert result.returncode == 0, (language, result.stdout[-1500:] + result.stderr[-1500:])
        assert result.stdout.count("  OK   ") == _checks(spec), language
        assert "warning" not in (result.stdout + result.stderr).lower(), language


@pytest.mark.parametrize("separator, decimal, encoding, mark", [
    (";", ",", "utf-8-sig", ","), (";", ",", "cp1254", ","), (",", ".", "utf-8-sig", "."),
    ("\t", ".", "utf-8-sig", ","),
], ids=["noktali-virgul-utf8", "noktali-virgul-cp1254", "virgul", "sekme-virgullu-sayilar"])
def test_csv_settings_are_detected_and_both_languages_read_the_same_values(separator, decimal, encoding, mark,
                                                                          tmp_path: Path) -> None:
    data = _csv(_messy_frame(mark), separator, decimal, encoding)
    table = K.read_upload("verim.csv", data)
    assert (table.separator, table.decimal, table.encoding) == (separator, decimal, encoding)
    prepared, spec = _messy_spec(table)
    assert [kind for _, _, kind in prepared.read.columns] == ["metin", "kod", "sayi_metin"]
    assert prepared.read.dropped == 3 and len(prepared.frame) == 5
    assert prepared.frame["odeme_yontemi"].tolist() == ["Kredi kartı", "Nakit", "Mobil ödeme", "Banka kartı", "T"]
    assert prepared.frame["sube_kodu"].tolist() == ["1", "2", "1", "2", "1"]
    assert prepared.frame["tutar_tl"].tolist() == [12.5, 30.0, 18.0, 15.0, 9.0]
    _reproduce(spec, tmp_path, ("verim.csv", data), _languages())


def test_excel_cells_are_cleaned_like_the_generated_code(tmp_path: Path) -> None:
    buffer = tmp_path / "verim.xlsx"
    _messy_frame(",").to_excel(buffer, index=False, sheet_name="Satışlar")
    data = buffer.read_bytes()
    buffer.unlink()
    table = K.read_upload("verim.xlsx", data)
    assert table.sheet == "Satışlar" and table.sheets == ("Satışlar",)
    prepared, spec = _messy_spec(table)
    assert [kind for _, _, kind in prepared.read.columns] == ["metin", "kod", "sayi_metin"]
    assert prepared.frame["tutar_tl"].tolist() == [12.5, 30.0, 18.0, 15.0, 9.0]
    _reproduce(spec, tmp_path, ("verim.xlsx", data), _languages(readxl=True))
    r_code = render_script(spec, "R")
    assert 'readxl::read_excel(veri_dosyasi, sheet = "Satışlar", na = c("", "NA")' in r_code
    assert 'install.packages("readxl")' in r_code and "Yalnız temel R" not in r_code


def test_text_cells_follow_one_rule_in_both_languages(tmp_path: Path) -> None:
    """Bölünmez boşluk ve " NA " iki dilde aynı temizlenir (R'nin trimws'i ve readxl bölünmez boşluğu silmez)."""

    rows = [("\xa0Kart", "A"), ("Kart\xa0", "B"), (" NA ", "A"), ("Nakit", "B"), ("Nakit", "A"), ("Kart", "B"),
            ("Mobil", "A"), ("NA", "B")]
    frame = pd.DataFrame(rows, columns=["Ödeme", "Grup"])
    for name, data, readxl in (("metin.csv", _csv(frame, ";", ",", "utf-8-sig"), False),
                               ("metin.xlsx", K.sample_excel(frame), True)):
        table = K.read_upload(name, data)
        prepared = K.prepare(table, [K.Selection("odeme", "Ödeme", "kategorik", required=True),
                                     K.Selection("grup", "Grup", "kategorik")])
        assert prepared.frame["odeme"].tolist() == ["Kart", "Kart", "Nakit", "Nakit", "Kart", "Mobil"]
        assert prepared.read.dropped == 2
        spec = _frequency_spec(prepared)
        _reproduce(spec, tmp_path / name.replace(".", "_"), (name, data), _languages(readxl))


def _frequency_spec(prepared: K.Prepared):
    from core.labs.ornek import with_app_values
    from core.labs.spec import Check, FrequencyTable, LabSpec, LabStep, NoteRef, Shape, ScalarTarget, TableTarget

    name = prepared.read.columns[0][0]
    order = K.category_order(prepared.frame[name], "alfabetik")
    step = LabStep(1, "Dosya", NoteRef("2.2"), "Deneme", operations=(
        prepared.read, Shape("veri", "n", "k"),
        FrequencyTable("veri", name, "tablo", order, relative=False, totals=True),
    ), checks=(Check("n", ScalarTarget("n"), 0, 0), *(Check(item, TableTarget("tablo", item, "frekans"), 0, 0)
                                                      for item in order)))
    return with_app_values(LabSpec("konu02", "Dosya", "2", (step,), source="kendi"))


def test_header_names_are_cleaned_and_unusable_columns_are_left_out(tmp_path: Path) -> None:
    text = (" Ödeme\xa0yöntemi ;Şube ;;NA;\"Not\"\"ı\"\n"
            "Nakit;Merkez;x;1;a\nKart;Sahil;y;2;b\nNakit;Sahil;z;3;c\nKart;Merkez;w;4;d\nMobil;Merkez;v;5;e\n")
    data = text.encode("utf-8")
    table = K.read_upload("baslik.csv", data)
    assert table.columns == ["Ödeme yöntemi", "Şube"] and table.strip_names
    assert any("Başlık hücresi boş" in note for note in table.notes)
    assert any("“NA”" in note for note in table.notes)
    prepared = K.prepare(table, [K.Selection("odeme_yontemi", "Ödeme yöntemi", "kategorik", required=True),
                                 K.Selection("sube", "Şube", "kategorik")])
    assert prepared.read.strip_names
    assert "ham.columns = [str(sutun).replace" in render_script(_frequency_spec(prepared), "Python")
    _reproduce(_frequency_spec(prepared), tmp_path, ("baslik.csv", data), _languages())


def test_excel_header_rules(tmp_path: Path) -> None:
    import openpyxl

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Veri"
    sheet.append(["Ülke", 2020, " Bölge ", None])
    for index in range(6):
        sheet.append([f"Ülke {index % 3}", index, ["Doğu", "Batı"][index % 2], index * 2])
    buffer = io.BytesIO()
    book.save(buffer)
    data = buffer.getvalue()
    table = K.read_upload("baslik.xlsx", data)
    assert table.columns == ["Ülke", "Bölge"] and table.strip_names
    assert any("2020" in note and "metin" in note for note in table.notes)
    assert any("Başlık hücresi boş" in note for note in table.notes)
    prepared = K.prepare(table, [K.Selection("bolge", "Bölge", "kategorik", required=True),
                                 K.Selection("ulke", "Ülke", "kategorik")])
    _reproduce(_frequency_spec(prepared), tmp_path, ("baslik.xlsx", data), _languages(readxl=True))
    empty_first = openpyxl.Workbook()
    empty_first.active["B2"] = "Ödeme"
    empty_first.active["B3"] = "Nakit"
    buffer = io.BytesIO()
    empty_first.save(buffer)
    with pytest.raises(K.UploadError, match="ilk satırı boş"):
        K.read_upload("bos_satir.xlsx", buffer.getvalue())


@pytest.mark.parametrize("text, message", [
    ("Ödeme,Ödeme ,Şube\nA,B,C\nA,B,C\n", "Aynı adı taşıyan"),
    ("Ödeme;Şube\n", "veri bulunamadı"),
    ("\nÖdeme;Şube\nA;B\n", None),
    ("   \nÖdeme;Şube\nA;B\n", "yalnız boşluk"),
    ("Ödeme;Şube\nA;B;C\nD;E;F\n", "daha az alan"),
    (";;\nA;B;C\n", "ilk satırı boş"),
    ('Ödeme;Not\nA;x"y\nB;z\n', "tırnak"),
])
def test_unusable_files_are_rejected(text: str, message: str | None) -> None:
    if message is None:
        assert K.read_upload("dosya.csv", text.encode()).columns == ["Ödeme", "Şube"]
        return
    with pytest.raises(K.UploadError, match=message):
        K.read_upload("dosya.csv", text.encode())


def test_size_rows_and_encoding_limits() -> None:
    with pytest.raises(K.UploadError, match="en çok 10.000 satır"):
        K.read_upload("uzun.csv", ("x\n" + "1\n" * (K.MAX_ROWS + 1)).encode())
    with pytest.raises(K.UploadError, match="MB'tan büyük"):
        K.read_upload("buyuk.csv", b"x" * (K.MAX_BYTES + 1))
    with pytest.raises(K.UploadError, match="UTF-16"):
        K.read_upload("utf16.csv", "Ödeme\nNakit\n".encode("utf-16"))


def test_encoding_is_detected_on_the_whole_file() -> None:
    """UTF-8 dosyada iki baytlı bir harf 64 KB sınırına denk gelse de dosya UTF-8 okunur."""

    prefix = "Şube;Not\nMerkez;"
    text = prefix + "a" * (65535 - len(prefix.encode())) + "ş\n" + "İzmir;b\n" * 3
    data = text.encode("utf-8")
    assert data[65535:65537] == "ş".encode()  # ilk 64 KB iki baytlı harfin ortasında biter
    assert K.detect_csv(data)[0] == "utf-8-sig"
    table = K.read_upload("uzun.csv", data)
    assert table.frame["Şube"].iloc[-1] == "İzmir"


@pytest.mark.parametrize("text, message", [
    ("Tutar;Grup\n1.234;A\n12.000;B\n7;A\n", "noktalı sayılar"),
    ("Tutar;Grup\n1.234,5;A\n2;B\n3;A\n", "binlik ayırıcı"),
    ('Tutar,Grup\n"1,234",A\n"12,500",B\n7,A\n', "üç basamak"),
    ('Tutar,Grup\n"12,5",A\n13.5,B\n7,A\n', "hem noktalı"),
    ("Tutar;Grup\n12,5;A\nyok;B\n7;A\n", "sayı olmayan"),
    ("Tutar;Grup\n12,5;A\nInf;B\n7;A\n", "sonsuz"),
])
def test_numbers_that_could_be_misread_are_rejected(text: str, message: str) -> None:
    table = K.read_upload("sayilar.csv", text.encode())
    with pytest.raises(K.UploadError, match=message):
        K.column_kind(table, "Tutar", "sayisal")


def test_turkish_decimal_texts_are_read_as_numbers() -> None:
    table = K.read_upload("sayilar.csv", 'Tutar,Grup\n"12,5",A\n"7,25",B\n3,A\n'.encode())
    assert K.column_kind(table, "Tutar", "sayisal") == "sayi_metin"
    prepared = K.prepare(table, [K.Selection("tutar", "Tutar", "sayisal", required=True)])
    assert prepared.frame["tutar"].tolist() == [12.5, 7.25, 3.0]


@pytest.mark.parametrize("series, use, message", [
    (pd.Series(pd.to_datetime(["2024-01-01", "2024-02-01"])), "kategorik", "tarih"),
    (pd.Series(["A", pd.Timestamp("2024-01-01")], dtype=object), "serbest", "tarih"),
    (pd.Series([1.5, 2.0]), "kategorik", "ondalıklı sayılar içeriyor"),
    (pd.Series(["A", 12.5], dtype=object), "kategorik", "metinle birlikte ondalıklı"),
    (pd.Series(["A", 2.5], dtype=object), "serbest", "metinle birlikte ondalıklı"),
    (pd.Series(["A", 10 ** 16], dtype=object), "kategorik", "çok büyük"),
    (pd.Series(["12", "abc"], dtype=object), "sayisal", "sayı olmayan"),
    (pd.Series([1.0, np.inf]), "sayisal", "sonsuz"),
    (pd.Series([True, False]), "sayisal", "DOĞRU/YANLIŞ"),
    (pd.Series([True, False, None], dtype=object), "kategorik", "DOĞRU/YANLIŞ"),
    (pd.Series([True, False]), "serbest", "DOĞRU/YANLIŞ"),
])
def test_column_kinds_reject_unsuitable_columns(series, use, message) -> None:
    """Python ile R'nin aynı değeri üretemediği hücreler reddedilir (ör. pandas True, R TRUE yazar)."""

    with pytest.raises(K.UploadError, match=message):
        K.series_kind(series, use, "Sütun")


def test_csv_true_false_with_a_blank_cell_is_rejected_with_a_clear_message() -> None:
    data = "Burslu,Bolum\nTRUE,A\nFALSE,B\n,B\nTRUE,A\n".encode()
    table = K.read_upload("burs.csv", data)
    with pytest.raises(K.UploadError, match="DOĞRU/YANLIŞ"):
        K.prepare(table, [K.Selection("burslu", "Burslu", "kategorik")])


def test_reserved_category_names_and_level_limits() -> None:
    table = K.read_upload("kategori.csv", "Kategori\nA\nToplam\nB\n".encode())
    with pytest.raises(K.UploadError, match="Toplam"):
        K.prepare(table, [K.Selection("kategori", "Kategori", "kategorik")])
    with pytest.raises(K.UploadError, match="en az 3"):
        K.check_levels(pd.Series(["a", "b", None]), "Sütun", 3, 5)
    with pytest.raises(K.UploadError, match="en çok 2"):
        K.check_levels(pd.Series(["a", "b", "c"]), "Sütun", 2, 2)


def test_role_rules_are_enforced() -> None:
    custom = VARIANTS["konu02"].custom
    table = K.read_upload("ornek.xlsx", K.sample_excel(custom.sample()))
    with pytest.raises(K.UploadError, match="için bir sütun seçin"):
        custom_case(custom, table, CustomChoices(roles={"ana": None}))
    with pytest.raises(K.UploadError, match="birlikte çalışır"):
        custom_case(custom, table, CustomChoices(roles={"ana": "Ödeme yöntemi", "secenek": "Şube"}))
    with pytest.raises(K.UploadError, match="en çok 2"):
        custom_case(custom, table, CustomChoices(roles={"ana": "Ödeme yöntemi", "secenek": "Ödeme yöntemi",
                                                         "altgrup": "Şube", "sonuc": "Memnuniyet"}))


def test_mac_line_endings_and_single_column_files_are_read(tmp_path: Path) -> None:
    """Yalnız CR satır sonu (Excel for Mac) ve ayırıcısı olmayan tek sütunlu dosya; tek sütunda ondalık işareti
    sayıların yazımından belirlenir."""

    mac = "Ödeme;Şube\rNakit;Merkez\rKart;Sahil\rNakit;Sahil\rKart;Merkez\rMobil;Merkez\r".encode()
    table = K.read_upload("mac.csv", mac)
    assert table.columns == ["Ödeme", "Şube"] and len(table.frame) == 5
    prepared = K.prepare(table, [K.Selection("odeme", "Ödeme", "kategorik", required=True),
                                 K.Selection("sube", "Şube", "kategorik")])
    _reproduce(_frequency_spec(prepared), tmp_path / "mac", ("mac.csv", mac), _languages())
    single = "Puan\n12.5\n13\n14.25\n15\n16.5\n".encode()
    table = K.read_upload("tek.csv", single)
    assert table.decimal == "." and K.column_kind(table, "Puan", "sayisal") == "sayi"
    custom = VARIANTS["konu01"].custom
    case, _ = custom_case(custom, table, CustomChoices(roles={"sayisal": "Puan"}))
    assert case.data["puan"].tolist() == [12.5, 13.0, 14.25, 15.0, 16.5]
    _reproduce(custom.build(case), tmp_path / "tek", ("tek.csv", single), _languages())
    assert K.read_upload("tek_virgul.csv", "Puan\n12,5\n13\n".encode()).decimal == ","


def test_integer_codes_are_the_same_text_in_both_languages(tmp_path: Path) -> None:
    data = "Kod;Grup\n1;A\n-0;B\n2;A\n1;B\n2;A\n20230001001;B\n".encode()
    table = K.read_upload("kod.csv", data)
    prepared = K.prepare(table, [K.Selection("kod", "Kod", "kategorik", required=True),
                                 K.Selection("grup", "Grup", "kategorik")])
    assert sorted(set(prepared.frame["kod"])) == ["0", "1", "2", "20230001001"]
    _reproduce(_frequency_spec(prepared), tmp_path, ("kod.csv", data), _languages())
    huge = K.read_upload("buyuk.csv", "Kod;Grup\n9007199254740993;A\n1;B\n".encode())
    with pytest.raises(K.UploadError, match="çok büyük kodlar"):
        K.column_kind(huge, "Kod", "kategorik")


@pytest.mark.parametrize("text, use, message", [
    ("Tutar;Grup\n４６;A\n13;B\n", "sayisal", "sayı olmayan"),
    ("Tutar;Grup\n4600000000000000000;A\n13;B\n", "sayisal", "çok büyük sayılar"),
    ("Tutar;Grup\n12345678901234567,5;A\n13;B\n", "sayisal", "çok büyük sayılar"),
])
def test_digits_must_be_ascii_and_magnitudes_bounded(text: str, use: str, message: str) -> None:
    table = K.read_upload("sayi.csv", text.encode())
    with pytest.raises(K.UploadError, match=message):
        K.column_kind(table, "Tutar", use)


def test_unusual_category_characters_sort_without_errors() -> None:
    values = pd.Series(["1²", "2²", "١٣", "10", "2"])
    order = K.category_order(values, "alfabetik")
    assert set(order) == set(values) and order.index("2") < order.index("10")


# --- Kendi verini yükle: boş hücreler --------------------------------------------------

def _orders_with_blanks() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    n = 60
    frame = pd.DataFrame({
        "Ödeme": rng.choice(["Nakit", "Kart", "Mobil"], n),
        "Şube": rng.choice(["Merkez", "Sahil"], n).astype(object),
        "Tür": rng.choice(["Masada", "Paket"], n).astype(object),
        "Memnuniyet": rng.choice(["Evet", "Hayır"], n).astype(object),
        "Not": [None] * 40 + ["iyi"] * 20,
    })
    frame.loc[[3, 17, 41], "Şube"] = None
    frame.loc[[5, 17], "Tür"] = None
    frame.loc[[29], "Memnuniyet"] = None
    return frame


def test_blank_cells_in_optional_columns_do_not_change_the_main_variable(tmp_path: Path) -> None:
    """Satırlar yalnız zorunlu rolün boş hücreleri yüzünden çıkarılır; isteğe bağlı rolleri kullanan adımlar kendi
    tam gözlemleriyle çalışır ve bunu söyler."""

    from core.labs.spec import CompleteCases

    frame = _orders_with_blanks()
    data = _csv(frame, ";", ",", "utf-8-sig")
    table = K.read_upload("bos.csv", data)
    custom = VARIANTS["konu02"].custom
    roles = {"ana": "Ödeme", "satir": "Şube", "secenek": "Şube", "altgrup": "Tür", "sonuc": "Memnuniyet"}
    full, notes = custom_case(custom, table, CustomChoices(roles=roles))
    alone, _ = custom_case(custom, table, CustomChoices(roles={"ana": "Ödeme"}))
    assert len(full.data) == len(alone.data) == len(frame)
    assert any("“Şube” sütununda 3 boş hücre" in note for note in notes)
    spec, single = custom.build(full), custom.build(alone)
    assert spec.step(1).checks[0].expected == single.step(1).checks[0].expected == len(frame)  # n
    for number in (2, 3, 6, 10, 12):
        assert [check.expected for check in spec.step(number).checks] == \
               [check.expected for check in single.step(number).checks], number
    first = spec.step(7).operations[0]
    assert isinstance(first, CompleteCases) and first.columns == ("odeme", "sube")
    assert "boş olan 3 gözlem" in spec.step(7).explanation
    total = next(check for check in spec.step(7).checks if check.label == "Genel toplam")
    assert total.expected == len(frame) - 3
    simpson = spec.step(11).operations[0]
    assert isinstance(simpson, CompleteCases) and simpson.frame == "veri_simpson"
    assert "boş hücre olan 5 gözlem" in spec.step(11).explanation
    _reproduce(spec, tmp_path, ("bos.csv", data), _languages())


def test_konu01_blank_cells_in_extra_columns_are_kept(tmp_path: Path) -> None:
    frame = pd.DataFrame({"Puan": [55, 61, None, 72, 80, 47, 66], "Not": ["a", None, "b", None, "c", "d", "e"],
                          "Durum": ["Geçti", "Geçti", "Kaldı", "Geçti", "Geçti", "Kaldı", "Geçti"]})
    data = _csv(frame, ",", ".", "utf-8-sig")
    table = K.read_upload("puan.csv", data)
    custom = VARIANTS["konu01"].custom
    case, notes = custom_case(custom, table, CustomChoices(roles={"sayisal": "Puan", "ikili": "Durum"},
                                                           extra=("Not",)))
    assert len(case.data) == 6 and case.levels["ikili"] == "Geçti"
    assert any("1 satır çıkarıldı" in note for note in notes)
    _reproduce(custom.build(case), tmp_path, ("puan.csv", data), _languages())


# --- Adlar ve sıralar -------------------------------------------------------------------

def test_code_names_are_ascii_unique_and_not_reserved() -> None:
    assert K.code_name("Ödeme yöntemi") == "odeme_yontemi"
    assert K.code_name("İl / İlçe (2024)") == "il_ilce_2024"
    assert K.code_name("2024 satış") == "degisken_2024_satis"
    assert K.code_name("if") == "if_" and K.code_name("TRUE") == "true"
    assert K.code_name("Şube", taken={"sube"}) == "sube_2"
    assert K.code_name("???") == "degisken"


def test_turkish_order_and_frequency_order() -> None:
    values = pd.Series(["Çay", "Su", "Ayran", "Şalgam", "Çay", "ılık", "İçecek", "10. sınıf", "2. sınıf", "Su", "Çay"])
    assert K.category_order(values, "alfabetik") == (
        "2. sınıf", "10. sınıf", "Ayran", "Çay", "ılık", "İçecek", "Su", "Şalgam")
    assert K.category_order(values, "frekans")[:2] == ("Çay", "Su")
    assert K.category_order(values, "dosya")[:3] == ("Çay", "Su", "Ayran")


# --- Konu 3–4: zor veri setleri iki dilde -------------------------------------------------------

def _plain_csv(frame: pd.DataFrame, separator: str, decimal: str) -> bytes:
    """Sayılar üstel gösterim olmadan, seçilen ondalık işaretiyle (0.000012; 999000000000001); boş hücre boş."""

    def cell(value) -> str:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return ""
        if isinstance(value, (int, float, np.integer, np.floating)):
            text = format(Decimal(repr(float(value))).normalize(), "f")
            return text.replace(".", decimal)
        return str(value)

    lines = [separator.join(frame.columns)]
    lines += [separator.join(cell(value) for value in row) for row in frame.itertuples(index=False)]
    return ("\n".join(lines) + "\n").encode("utf-8")


HARD_DATA = {
    "konu03-not-ortalamasi": ("konu03", pd.DataFrame({"Not": [2.37, 2.15, 3.98, 1.85, 3.02, 2.66, 3.41, 2.95, 3.5,
                                                               2.2, 1.9, 3.75, 2.05, 3.33]}),
                              {"sayisal": "Not"}, {"k": 6}, ";", ","),
    "konu03-satis-yaprak-10": ("konu03", pd.DataFrame({"Satış": [1565, 1852, 1644, 1766, 1888, 1912, 2044, 1812,
                                                                 1790, 1679, 2008, 1852, 1967, 1954, 1733]}),
                               {"sayisal": "Satış"}, {}, ",", "."),
    "konu03-negatif": ("konu03", pd.DataFrame({"Büyüme": [-3.5, -1.2, 0.4, 2.8, 1.1, -0.6, 3.9, 2.2, -2.7, 0.9]}),
                       {"sayisal": "Büyüme"}, {}, "\t", ","),
    "konu03-dar-genislik": ("konu03", pd.DataFrame({"Oran": [round(0.0001 * index, 4) for index in range(1, 13)]}),
                            {"sayisal": "Oran"}, {}, ",", "."),
    "konu04-bos-grup-buyume": ("konu04", pd.DataFrame({
        "Kira": [20.5, -3, 22, 30, None, 28, 26.25, None, 19, 24],
        "Bölge": ["Merkez", "Sahil", None, "Merkez", "Sahil", "Sahil", "Merkez", "Sahil", None, "Merkez"],
        "Artış (%)": [45, 30.5, 18, -12, 9, None, None, None, None, None],
    }), {"sayisal": "Kira", "grup": "Bölge", "buyume": "Artış (%)"}, {}, ";", ","),
    "konu04-cok-buyuk": ("konu04", pd.DataFrame({"x": [999000000000000 + step * 1000003 for step in (0, 4, 1, 9, 6)]}),
                         {"sayisal": "x"}, {}, ",", "."),
    "konu04-cok-kucuk": ("konu04", pd.DataFrame({"x": [0.000012, 0.000034, 0.000021, 0.000045, 0.000018]}),
                         {"sayisal": "x"}, {}, ",", "."),
    "konu04-buyuk-cift-n": ("konu04", pd.DataFrame({"Süre": np.round(np.random.default_rng(8).gamma(2, 9, 320), 1)}),
                            {"sayisal": "Süre"}, {}, ",", "."),
    "konu05-bos-grup-ikinci": ("konu05", pd.DataFrame({
        "Gelir": [12.5, 14.0, 13.25, 18.0, 11.75, 15.5, 40.0, 13.0, None, 16.25],
        "Şube": ["A", "B", None, "A", "B", "A", "B", "A", "B", "B"],
        "Harcama": [3.1, None, 2.8, 4.0, 2.5, 3.6, 6.9, 3.0, 3.3, None],
    }), {"sayisal": "Gelir", "grup": "Şube", "ikinci": "Harcama"}, {}, ";", ","),
    "konu05-chebyshev-siniri": ("konu05", pd.DataFrame({"x": [1.0, 0.6, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]}),
                                {"sayisal": "x"}, {}, ",", "."),
    "konu05-sinirdaki-gozlem": ("konu05", pd.DataFrame({"x": [1.2, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.0, 3.6],
                                                        "y": [5, -2, 3, 1, 0, -4, 2, 6, -1, 3, 4]}),
                                {"sayisal": "x", "ikinci": "y"}, {}, "\t", ","),
    "konu05-negatif-buyuk-n": ("konu05", pd.DataFrame({
        "Getiri": np.round(np.random.default_rng(9).normal(0.4, 2.5, 360), 2),
        "Grup": np.random.default_rng(10).choice(["Fon A", "Fon B"], 360),
    }), {"sayisal": "Getiri", "grup": "Grup"}, {}, ",", "."),
    "konu05-buyuk-degerler": ("konu05", pd.DataFrame({"x": [123456789012.5 + step * 1000.25 for step in range(40)]}),
                              {"sayisal": "x"}, {}, ",", "."),
    "konu05-chebyshev-buyuk-deger": ("konu05", pd.DataFrame({"Tutar": [86349475.7, 86349463.98] + [86349469.84] * 17}),
                                     {"sayisal": "Tutar"}, {}, ";", ","),
    "konu05-sinirdaki-gozlem-aykiri-degil": ("konu05", pd.DataFrame({"Süre": [0.05, 0.33, 0.4, 0.58, 0.59, 1.91]}),
                                             {"sayisal": "Süre"}, {}, ";", ","),
    "konu05-tam-dogrusal-ve-sabit": ("konu05", pd.DataFrame({
        "x": [15, 41, 5, 30, 36, 9, 3, 14, 33, 28, 8, 22, 33],
        "y": [-16, -42, -6, -31, -37, -10, -4, -15, -34, -29, -9, -23, -34],
        "Sabit": [2.5] * 13,
    }), {"sayisal": "x", "ikinci": "y"}, {}, ",", "."),
    "konu05-sabit-y": ("konu05", pd.DataFrame({"x": [1, 2, 3, 4, 5.5, 7], "y": [2.5] * 6}),
                       {"sayisal": "x", "ikinci": "y"}, {}, "\t", ","),
    # Kareli sapma yarım noktaya çok yakın (…970,5004): beklenen değer iki basamak fazlasıyla yazılmasa R düşerdi.
    "konu05-ciro-yarim-nokta": ("konu05", pd.DataFrame({"Ciro": [1200144548.63, 1200145870.07, 1200076418.91,
                                                                 1200022653.63, 1200132337.88, 1200109793.08]}),
                                {"sayisal": "Ciro"}, {}, ";", ","),
    # Kareli sapmanın tam kısmı bile iki dilde ayrılabilir: o kontrol atlanır, değer gösterilir.
    "konu05-cok-buyuk-dar": ("konu05", pd.DataFrame({"x": [150000153920.88, 150000094822.75, 150000184223.36,
                                                           150000097995.95, 150000051684.85, 150000028393.93]}),
                             {"sayisal": "x"}, {}, ",", "."),
    # IQR = 299999,875 iki basamakla tam yarım: bir basamak daha az yazılır.
    "konu05-iqr-yarim": ("konu05", pd.DataFrame({"x": [999999999000, 1000000000000, 1000000000000.5, 1000000001000,
                                                       1000000002000, 1000000300000, 1000000300000,
                                                       1000000300001]}), {"sayisal": "x"}, {}, ",", "."),
    # R altı ondalıklı 0,718528'i son ikili basamakta farklı okuyabilir; tam sınırdaki gözlem iki dilde de içeride.
    "konu05-alti-ondalik-sinir": ("konu05", pd.DataFrame({"x": [0.1, 0.3, 0.35, 0.4, 0.45, 0.4674112, 0.718528]}),
                                  {"sayisal": "x"}, {}, ",", "."),
    "konu06-kodlar-bos": ("konu06", pd.DataFrame({
        "Kod": [1, 2, 3, 1, 2, 2, 1, 3, 3, 1, None, 2],
        "Durum": ["Evet", "Hayır", "Evet", "Hayır", "Evet", "Hayır", "Evet", "Hayır", "Evet", None, "Evet", "Hayır"],
    }), {"olay_e": "Kod", "olay_f": "Durum"}, {"zar": 20, "ekip": 10, "secim": 4}, ";", ","),
    "konu06-ayrik": ("konu06", pd.DataFrame({
        "Teslim": ["Geç", "Geç", "Zamanında", "Zamanında", "Zamanında", "Geç", "Zamanında"],
        "Hasar": ["Yok", "Yok", "Var", "Var", "Yok", "Yok", "Yok"],
    }), {"olay_e": "Teslim", "olay_f": "Hasar"}, {"zar": 5, "ekip": 7, "secim": 7}, ",", "."),
}


@pytest.mark.parametrize("name", sorted(HARD_DATA))
def test_hard_own_data_is_reproduced_in_both_languages(name: str, tmp_path: Path) -> None:
    """Kendi verisi (CSV): ondalıklı sınıf sınırları, yaprak birimi 10, negatif değerler, çok dar sınıflar, boş grup
    hücreleri, ayrı okunan yüzde değişim sütunu, çok büyük ve çok küçük değerler; Python ve R aynı sayıları verir."""

    topic, frame, roles, settings, separator, decimal = HARD_DATA[name]
    data = _plain_csv(frame, separator, decimal)
    table = K.read_upload("zor.csv", data)
    custom = VARIANTS[topic].custom
    case, _ = custom_case(custom, table, CustomChoices(roles=roles, settings=settings))
    spec = custom.build(case)
    assert run_lab(spec).all_passed
    _reproduce(spec, tmp_path, ("zor.csv", data), _languages())


def test_numbers_with_more_than_fifteen_significant_digits_are_rejected() -> None:
    """pandas ve R 16–17 basamaklı sayıları (ör. 0,1 + 0,2 = 0,30000000000000004) son basamakta farklı okuyabilir;
    eşitliğe dayanan sayımlar (mod, sınıf frekansı) iki dilde ayrışırdı. Sayısal rolde açık bir iletiyle reddedilir."""

    data = "x;y\n0,30000000000000004;1\n0,5;2\n0,7;3\n0,9;4\n1,1;5\n".encode("utf-8")
    table = K.read_upload("uzun.csv", data)
    assert table.long_numbers == {"x": ("0,30000000000000004",)}
    custom = VARIANTS["konu04"].custom
    with pytest.raises(K.UploadError, match="15'ten fazla anlamlı basamaklı"):
        custom_case(custom, table, CustomChoices(roles={"sayisal": "x"}))
    case, _ = custom_case(custom, table, CustomChoices(roles={"sayisal": "y"}))
    assert len(case.data) == 5
    with pytest.raises(K.UploadError, match="15'ten fazla anlamlı basamaklı"):
        K.series_kind(pd.Series(["0,30000000000000004", "0,5"]), "sayisal", "x", ",")
    assert K.significant_digits("1234567.0025") == 11 and K.significant_digits("0,000012") == 2
