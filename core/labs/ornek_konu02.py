"""Konu 2 genel uygulaması: kategorik verileri tablo ve grafiklerle özetlemek.

Ders notlarındaki adımlar (§2.1–§2.12) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Alternatif örnek
kurgusal bir kafe veri setidir; "kendi verin" seçeneğinde aynı adımlar öğrencinin dosyasıyla kurulur. Notlardaki
uygulama (``core.labs.konu02``) değişmez.
"""

from __future__ import annotations

import math
from functools import cache

import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    TopicVariants,
    esit,
    kisa,
    liste,
    md,
    tex,
    with_app_values,
    yuzde,
)
from core.labs.spec import (
    TOTAL,
    BarChart,
    Check,
    CompareBarChart,
    CompleteCases,
    Count,
    CrossTab,
    FrequencyTable,
    GroupedBarChart,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PieChart,
    Scalar,
    ScalarTarget,
    Shape,
    TableTarget,
)

TITLE = "Kategorik verileri tablo ve grafiklerle özetlemek"
ANA, SATIR, SECENEK, ALTGRUP, SONUC = "ana", "satir", "secenek", "altgrup", "sonuc"
SIMPSON = (SECENEK, ALTGRUP, SONUC)

ALT_ROWS = (
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Yemek kartı", "Sahil", "Paket", "Memnun"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun değil"),
    ("Yemek kartı", "Merkez", "Masada", "Memnun değil"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Yemek kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Paket", "Memnun değil"),
    ("Banka kartı", "Merkez", "Paket", "Memnun"),
    ("Banka kartı", "Merkez", "Paket", "Memnun"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun değil"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Yemek kartı", "Sahil", "Paket", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Paket", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Sahil", "Paket", "Memnun değil"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun değil"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun"),
    ("Yemek kartı", "Sahil", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Paket", "Memnun değil"),
    ("Nakit", "Merkez", "Paket", "Memnun değil"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Yemek kartı", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Sahil", "Paket", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun değil"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Paket", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Sahil", "Paket", "Memnun"),
    ("Kredi kartı", "Sahil", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Paket", "Memnun"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Paket", "Memnun"),
    ("Mobil ödeme", "Merkez", "Paket", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Sahil", "Paket", "Memnun değil"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun değil"),
    ("Yemek kartı", "Merkez", "Paket", "Memnun değil"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Paket", "Memnun değil"),
    ("Kredi kartı", "Merkez", "Paket", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Nakit", "Sahil", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Paket", "Memnun değil"),
    ("Banka kartı", "Merkez", "Paket", "Memnun değil"),
    ("Kredi kartı", "Sahil", "Masada", "Memnun değil"),
    ("Nakit", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Sahil", "Paket", "Memnun değil"),
    ("Nakit", "Sahil", "Masada", "Memnun"),
    ("Kredi kartı", "Sahil", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Yemek kartı", "Sahil", "Paket", "Memnun değil"),
    ("Yemek kartı", "Merkez", "Masada", "Memnun değil"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun değil"),
    ("Kredi kartı", "Merkez", "Paket", "Memnun"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun"),
    ("Yemek kartı", "Merkez", "Masada", "Memnun"),
    ("Kredi kartı", "Merkez", "Masada", "Memnun"),
    ("Mobil ödeme", "Merkez", "Masada", "Memnun"),
    ("Banka kartı", "Sahil", "Masada", "Memnun"),
)
"""Kurgusal veri: bir kafenin iki şubesindeki 100 sipariş (ödeme yöntemi, şube, sipariş türü, memnuniyet)."""

ALT_COLUMNS = ("odeme", "sube", "siparis_turu", "memnuniyet")
ALT_LABELS = {"odeme": "Ödeme yöntemi", "sube": "Şube", "siparis_turu": "Sipariş türü", "memnuniyet": "Memnuniyet"}
ALT_ORDERS = {
    "odeme": ("Nakit", "Kredi kartı", "Banka kartı", "Mobil ödeme", "Yemek kartı"),
    "sube": ("Merkez", "Sahil"),
    "siparis_turu": ("Masada", "Paket"),
    "memnuniyet": ("Memnun", "Memnun değil"),
}
STORY = (
    "Kurgusal veri: bir kafenin iki şubesinde (Merkez ve Sahil) kaydedilen 100 sipariş. Her siparişte ödeme yöntemi, "
    "şube, sipariş türü (masada ya da paket) ve müşterinin memnuniyeti var."
)


# --- Yardımcılar ------------------------------------------------------------------------

def _counts(case: Case, column: str, data: pd.DataFrame | None = None, order: tuple | None = None) -> pd.Series:
    data = case.data if data is None else data
    order = case.orders[column] if order is None else order
    return data[column].dropna().astype(str).value_counts().reindex(order, fill_value=0).astype(int)


def _ranked(counts: pd.Series) -> list[str]:
    """Kategoriler frekansa göre (çoktan aza); eşitlikte Türkçe alfabe sırası."""

    return sorted(counts.index, key=lambda item: (-int(counts[item]), K.turkish_key(item)))


def _cell(table: str, row: str, column: str, label: str, decimals: int = 0) -> Check:
    return Check(label, TableTarget(table, row, column), 0.0, decimals)


def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _missing(step: int, title: str, note: str, roles: str) -> LabStep:
    """Kendi verinde gereken sütun seçilmediyse adım yalnız ne gerektiğini söyler."""

    return LabStep(
        number=step,
        title=title,
        note=NoteRef(note),
        explanation=f"Bu adım için yukarıdaki veri panelinden şu rol(ler) için sütun seçin: {roles}.",
    )


def _blocked(step: int, title: str, note: str, reason: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note), explanation=reason)


def _extremes(counts: pd.Series) -> tuple[list[str], int, list[str], int]:
    high, low = int(counts.max()), int(counts.min())
    return ([str(item) for item in counts.index if counts[item] == high], high,
            [str(item) for item in counts.index if counts[item] == low], low)


def _closest(shares: pd.Series) -> tuple[str, str] | None:
    """Payları birbirine en yakın (eşit olmayan) iki kategori."""

    items = sorted(shares.items(), key=lambda pair: pair[1])
    best = None
    for (first, a), (second, b) in zip(items, items[1:]):
        gap = b - a
        if gap > 1e-9 and (best is None or gap < best[0]):
            best = (gap, second, first)
    return None if best is None else (best[1], best[2])


def _names(items) -> str:
    return liste([md(item) for item in items])


def _decimals(*values: float, start: int = 1, limit: int = 4) -> int:
    """Gösterilen değerler birbirinden ve (sıfır olmayanlar) sıfırdan ayrılacak kadar ondalık basamak: %36,02 ile
    %36 aynı yazılmaz, %0,01 sıfır görünmez."""

    for decimals in range(start, limit + 1):
        shown = [round(value, decimals) for value in values]
        if len(set(shown)) == len(shown) and all(item != 0 for item, value in zip(shown, values) if value != 0):
            return decimals
    return limit


def _complete(case: Case, columns: tuple[str, ...], name: str, comment: str):
    """Seçilen sütunların hepsinde değeri olan gözlemler. Boş hücre yoksa ana veri kullanılır; varsa ``CompleteCases``
    işlemiyle yeni bir çerçeve kurulur ve adım kaç gözlemle çalıştığını söyler."""

    subset = case.data.dropna(subset=list(columns)).reset_index(drop=True)
    if len(subset) == len(case.data):
        return case.frame, case.data, ()
    return name, subset, (CompleteCases(name, case.frame, columns, comment),)


def _present(case: Case, column: str, data: pd.DataFrame) -> tuple[str, ...]:
    found = set(data[column].dropna().astype(str))
    return tuple(item for item in case.orders[column] if item in found)


# --- Adımlar ------------------------------------------------------------------------------

def _step1(case: Case) -> LabStep:
    label = case.md(ANA)
    n, k = len(case.data), case.data.shape[1]
    intro = case.extra.get("read_text") or (
        f"Dosyanızdan seçilen {k} sütun okunur: her satır bir gözlem, her sütun bir değişkendir."
    )
    return LabStep(
        number=1,
        title="Ham kategorik veri",
        note=NoteRef("2.1"),
        explanation=(
            f"{intro}\n\n“{label}” sütunundaki {n} etiketi tek tek saymak yavaş ve hataya açıktır. Betimsel "
            "istatistiğin ilk görevi bu ham veriyi okunabilir bir özete dönüştürmektir."
        ),
        operations=(*case.load, Shape(case.frame, "n", "k")),
        checks=(_scalar("n", "Gözlem sayısı n"), _scalar("k", "Değişken sayısı")),
        takeaway=(
            "Özette bilgi kaybolmaz, yoğunlaşır: hangi gözlemin hangi kategoride olduğunu artık görmeyiz; buna "
            "karşılık hangi kategorinin ne kadar yaygın olduğunu hemen görürüz."
        ),
    )


def _step2(case: Case) -> LabStep:
    a, order = case.roles[ANA], case.orders[case.roles[ANA]]
    counts, n = _counts(case, a), len(case.data)
    most, high, least, low = _extremes(counts)
    head = "En sık gözlenen kategori" if len(most) == 1 else "En sık gözlenen kategoriler"
    tail = "en az gözlenen" if len(least) == 1 else "en az gözlenenler"
    each = "" if len(most) == 1 else "her biri "
    each_low = "" if len(least) == 1 else "her biri "
    takeaway = (
        f"{head}: {_names(most)} ({n} {case.unit} içinde {each}{high}); {tail}: {_names(least)} ({each_low}{low}). "
        f"Bu ifadeler yalnız gözlenen {n} {case.unit} için geçerlidir."
    )
    if high == low:
        takeaway = (f"Bütün kategoriler aynı frekansa sahip ({high}). Bu ifade yalnız gözlenen {n} {case.unit} için "
                    "geçerlidir.")
    return LabStep(
        number=2,
        title="Frekans dağılımı",
        note=NoteRef("2.2"),
        explanation=(
            "Her kategorideki gözlem sayısı o kategorinin frekansıdır ($f_j$). Kategoriler "
            f"{case.extra.get('order_text', 'seçilen sırayla')} dizilir ve sona toplam satırı eklenir. Frekansların "
            f"toplamı gözlem sayısına eşit olmalıdır: $\\sum_{{j=1}}^{{k}} f_j = n = {n}$. Bu eşitlik yeni bir hesap "
            "değil, tablonun kontrol kuralıdır."
        ),
        operations=(FrequencyTable(case.frame, a, "frekans_tablosu", order, relative=False, totals=True),),
        checks=(
            *(_cell("frekans_tablosu", item, "frekans", f"{item} frekansı") for item in order),
            _cell("frekans_tablosu", TOTAL, "frekans", "Frekansların toplamı = n"),
        ),
        takeaway=takeaway,
    )


def _step3(case: Case) -> LabStep:
    a, order = case.roles[ANA], case.orders[case.roles[ANA]]
    counts, n = _counts(case, a), len(case.data)
    top = _ranked(counts)[0]
    f, share = int(counts[top]), counts[top] / n
    return LabStep(
        number=3,
        title="Göreli frekans ve yüzde frekans",
        note=NoteRef("2.3"),
        explanation=(
            "Göreli frekans $r_j = f_j / n$, yüzde frekans $p_j = 100 \\times r_j$ ile bulunur. Örneğin "
            f"{md(top)} için $r = {f}/{n} {esit(share, 3)} {tex(share, 3)}$ ve "
            f"$p = 100 \\times {f}/{n} {esit(100 * share, 1)} \\%{tex(100 * share, 1)}$. "
            "Üç sütun aynı dağılımı üç ölçekte anlatır: $\\sum f_j = n$, $\\sum r_j = 1$, $\\sum p_j = 100$."
        ),
        operations=(FrequencyTable(case.frame, a, "tam_tablo", order, relative=True, totals=True),),
        checks=(
            *(_cell("tam_tablo", item, "goreli", f"{item} göreli frekansı", 3) for item in order),
            _cell("tam_tablo", TOTAL, "goreli", "Göreli frekansların toplamı", 3),
            *(_cell("tam_tablo", item, "yuzde", f"{item} yüzde frekansı", 1) for item in order),
            _cell("tam_tablo", TOTAL, "yuzde", "Yüzde frekansların toplamı", 1),
        ),
        takeaway=(
            "Frekans “kaç gözlem?”, göreli ve yüzde frekans “toplamın ne kadarı?” sorusunu cevaplar. Farklı "
            "büyüklükteki veri setleri yüzdelerle karşılaştırılır."
        ),
    )


def _step4(case: Case) -> LabStep:
    label = case.label(ANA)
    return LabStep(
        number=4,
        title="Sütun grafiği",
        note=NoteRef("2.4"),
        explanation=(
            "Kategoriler yatay eksende, frekanslar dikey eksende gösterilir; her kategori ayrı bir sütundur. Sütunun "
            "uzunluğu büyüklüğü temsil ettiği için dikey eksen sıfırdan başlar."
        ),
        operations=(
            BarChart("frekans_tablosu", "frekans", label, f"{case.unit.capitalize()} sayısı",
                     f"{label} için sütun grafiği"),
        ),
        takeaway=(
            "Sütunlar arasındaki boşluk, kategorilerin birbirinden ayrı olduğunu gösterir. Bu özellik sütun grafiğini "
            "Konu 3'teki histogramdan ayırır."
        ),
    )


def _step5(case: Case) -> LabStep:
    label = case.label(ANA)
    nature = case.extra.get("nominal_text") or (
        f"“{case.md(ANA)}” sıralı (ordinal) bir değişkense bu grafik yerine kategorilerin doğal sırası korunmalıdır."
    )
    return LabStep(
        number=5,
        title="Kategori sırası: sıralanmış sütun grafiği",
        note=NoteRef("2.5"),
        explanation=(
            "Kategorilerin doğal bir sırası yoksa (nominal değişken) sütunları yüksekten düşüğe sıralamak "
            f"karşılaştırmayı kolaylaştırır. {nature}"
        ),
        operations=(
            BarChart("frekans_tablosu", "frekans", label, f"{case.unit.capitalize()} sayısı",
                     "Frekansa göre sıralanmış sütun grafiği", sort="azalan"),
        ),
        takeaway=(
            "Nominal veride frekansa göre sıralama yapılabilir. Ordinal veride ise öncelik kategorilerin doğal "
            "sırasını korumaktır (ör. Çok düşük < Düşük < Orta < Yüksek < Çok yüksek)."
        ),
    )


def _step6(case: Case) -> LabStep:
    a, label = case.roles[ANA], case.label(ANA)
    counts, n = _counts(case, a), len(case.data)
    ranked = _ranked(counts)
    top = ranked[0]
    f, share = int(counts[top]), counts[top] / n
    shares = 100 * counts / n
    pair = _closest(shares)
    if pair:
        first, second = pair
        digits = _decimals(shares[first], shares[second])
        takeaway = (
            f"{yuzde(shares[first], digits)} ({md(first)}) ile {yuzde(shares[second], digits)} ({md(second)}) "
            "arasındaki fark, sütunlar ortak bir tabandan başladığı için sütun grafiğinde daha kolay görülür."
        )
    else:
        takeaway = "Sütun grafiğinde bütün sütunlar ortak bir tabandan başlar; paylar doğrudan karşılaştırılır."
    takeaway += " Grafik seçimi veriyi değiştirmez; hangi özelliğin kolay görüleceğini değiştirir."
    if len(counts) > 6:
        takeaway += (f" Kategori sayısı arttıkça dilim grafiği okunmaz olur; {len(counts)} kategoride sütun grafiği "
                     "daha uygundur.")
    angle = 360 * share
    return LabStep(
        number=6,
        title="Dilim grafiği ve dilim açısı",
        note=NoteRef("2.6"),
        explanation=(
            "Daire bütün veri setini, her dilim bir kategorinin payını temsil eder. Bir daire $360^\\circ$ olduğundan "
            "dilim açısı $\\theta_j = 360^\\circ \\times r_j$ ile bulunur; "
            f"{md(top)} için $\\theta = 360^\\circ \\times {f}/{n} {esit(angle, 1)} {tex(angle, 1)}^\\circ$. "
            "Dilimler $0^\\circ$ çizgisinden başlar ve saat yönünün tersine, büyükten küçüğe dizilir. Aynı yüzdeler "
            "karşılaştırma için bir de sütun grafiğiyle çizilir."
        ),
        operations=(
            PieChart("tam_tablo", "goreli", "dilim_acilari", f"{label} için dilim grafiği", tuple(ranked)),
            BarChart("tam_tablo", "yuzde", label, "Yüzde", "Aynı yüzdelerin sütun grafiği", sort="azalan",
                     percent=True, decimals=1),
        ),
        checks=(_cell("dilim_acilari", top, "aci", f"{top} dilim açısı (derece)", 1),),
        takeaway=takeaway,
    )


def _crosstab_data(case: Case):
    """Adım 7–9'un verisi: iki değişkende de değeri olan gözlemler ve tablonun satır/sütun sırası."""

    a, b = case.roles[ANA], case.roles[SATIR]
    frame, data, load = _complete(case, (a, b), "veri_capraz",
                                  "Çapraz tablo için iki sütunda da değeri olan gözlemler")
    return frame, data, load, _present(case, b, data), _present(case, a, data)


def _largest_cell(data: pd.DataFrame, a: str, b: str, rows: tuple, columns: tuple) -> tuple[str, str, int]:
    table = pd.crosstab(data[b].astype(str), data[a].astype(str)).reindex(index=rows, columns=columns, fill_value=0)
    stacked = table.stack()
    best = max(stacked.items(), key=lambda pair: int(pair[1]))  # eşitlikte tablo sırasındaki ilk hücre
    (row, column), value = best
    return str(row), str(column), int(value)


def _step7(case: Case) -> LabStep:
    title, note = "İki kategorik değişken: çapraz tablo", "2.7"
    if not case.has(SATIR):
        return _missing(7, title, note, "İkinci kategorik değişken (satırlar)")
    a, b = case.roles[ANA], case.roles[SATIR]
    if a == b:
        return _blocked(7, title, note, "Çapraz tablo için iki farklı sütun gerekir.")
    a_label, b_label = case.md(ANA), case.md(SATIR)
    frame, data, load, rows, columns = _crosstab_data(case)
    n = len(data)
    row, column, value = _largest_cell(data, a, b, rows, columns)
    skipped = len(case.data) - n
    note_text = (f" “{b_label}” sütunu boş olan {skipped} gözlem bu adımda ve sonraki iki adımda kullanılmaz."
                 if skipped else "")
    return LabStep(
        number=7,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"{n} {case.unit} için iki değişken birlikte özetlenir: satırlar “{b_label}”, sütunlar “{a_label}” "
            "kategorileridir. Her hücre iki koşulu birlikte sağlayan gözlem sayısıdır; son satır ve son sütun "
            f"marjinal toplamlardır.{note_text}"
        ),
        operations=(*load, CrossTab(frame, b, a, "capraz", rows, columns, margins=True)),
        checks=(
            _cell("capraz", row, column, f"{row} ∩ {column}"),
            *(_cell("capraz", item, TOTAL, f"{item} satır toplamı") for item in rows),
            *(_cell("capraz", TOTAL, item, f"{item} sütun toplamı") for item in columns),
            _cell("capraz", TOTAL, TOTAL, "Genel toplam"),
        ),
        takeaway=(
            f"Bir hücre iki koşulu birlikte söyler. En büyük hücre {value}: {b_label} = {md(row)} ve {a_label} = "
            f"{md(column)}. Yalnız “{md(column)} için {value}” demek eksiktir; bu sayı yalnız {md(row)} grubuna aittir."
        ),
    )


def _step8(case: Case) -> LabStep:
    title, note = "Satır ve sütun yüzdeleri: doğru payda", "2.8"
    if not case.has(SATIR):
        return _missing(8, title, note, "İkinci kategorik değişken (satırlar)")
    a, b = case.roles[ANA], case.roles[SATIR]
    if a == b:
        return _blocked(8, title, note, "Çapraz tablo için iki farklı sütun gerekir.")
    a_label, b_label = case.md(ANA), case.md(SATIR)
    frame, data, _, rows, columns = _crosstab_data(case)
    row, column, value = _largest_cell(data, a, b, rows, columns)
    row_total = int((data[b].astype(str) == row).sum())
    column_total = int((data[a].astype(str) == column).sum())
    by_row, by_column = 100 * value / row_total, 100 * value / column_total
    return LabStep(
        number=8,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"“Her {b_label} grubunda {a_label} nasıl dağılıyor?” sorusunun paydası **satır toplamıdır**: {md(row)} "
            f"grubunda {md(column)} payı ${value}/{row_total} \\times 100 {esit(by_row, 1)} \\%{tex(by_row, 1)}$. "
            f"“{md(column)} kategorisindeki gözlemler {b_label} gruplarına nasıl dağılıyor?” sorusunun paydası ise "
            f"**sütun toplamıdır**: ${value}/{column_total} \\times 100 {esit(by_column, 1)} \\%{tex(by_column, 1)}$."
        ),
        operations=(
            CrossTab(frame, b, a, "satir_yuzde", rows, columns, percent="satir", margins=True),
            CrossTab(frame, b, a, "sutun_yuzde", rows, columns, percent="sutun", margins=True),
        ),
        checks=(
            *(_cell("satir_yuzde", row, item, f"{row}: {item} (satır %)", 1) for item in columns),
            _cell("satir_yuzde", row, TOTAL, f"{row} satır toplamı (%)", 1),
            *(_cell("sutun_yuzde", item, column, f"{column} içinde {item} (sütun %)", 1) for item in rows),
        ),
        takeaway=(
            f"Aynı {value} hücresi farklı sorularda farklı paydaya bölünür. Yüzde hesabında en önemli adım çoğu zaman "
            "bölme değil, doğru paydayı seçmektir."
        ),
    )


def _step9(case: Case) -> LabStep:
    title, note = "Yan yana ve yüzde 100 yığılmış sütun grafikleri", "2.9"
    if not case.has(SATIR):
        return _missing(9, title, note, "İkinci kategorik değişken (satırlar)")
    a, b = case.roles[ANA], case.roles[SATIR]
    if a == b:
        return _blocked(9, title, note, "Çapraz tablo için iki farklı sütun gerekir.")
    a_label, b_label = case.label(ANA), case.label(SATIR)
    _, _, _, rows, columns = _crosstab_data(case)
    labels = len(rows) * len(columns) <= 12
    return LabStep(
        number=9,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"Satır yüzdeleri iki biçimde çizilir. Yan yana grafikte her “{md(a_label)}” kategorisinde "
            f"“{md(b_label)}” grupları doğrudan karşılaştırılır. Yüzde 100 yığılmış grafikte her grup tek bir sütundur "
            "ve sütun %100'e tamamlanır; böylece grup büyüklükleri farklı olsa da iç bileşim karşılaştırılır."
        ),
        operations=(
            GroupedBarChart("satir_yuzde", a_label, "Grup içindeki yüzde",
                            f"{b_label} gruplarına göre {a_label}: yan yana sütun grafiği", series="satir",
                            labels=labels),
            GroupedBarChart("satir_yuzde", b_label, "Grup içindeki yüzde",
                            "Grup içindeki dağılım: yüzde 100 yığılmış sütun grafiği", series="sutun", stacked=True,
                            labels=labels),
        ),
        takeaway=(
            "Yan yana grafik tek bir kategoride grupları karşılaştırmayı kolaylaştırır; yığılmış grafik her grubun iç "
            "bileşimini özetler. Yığılmış grafikte orta parçaların ortak tabanı olmadığı için küçük farkları "
            "karşılaştırmak zorlaşır."
        ),
    )


def _nice_step(width: float) -> float:
    return 10.0 ** math.floor(math.log10(width)) if width > 0 else 1.0


def _truncated_axis(larger: float, smaller: float) -> tuple[float, float]:
    """Kesilmiş eksen (notlardaki %70–%80 gibi): alt sınır küçük değerin hemen altında, üst sınır büyük değerin hemen
    üstünde. Küçük sütunun eksende kalan yüksekliği farkın yarısı kadardır; bu yüzden fark olduğundan büyük görünür."""

    drop = min(larger - smaller, smaller) / 2
    step = _nice_step(drop)
    low = step * math.floor((smaller - drop) / step + 1e-9)
    if low <= 0:
        low = smaller - drop
    high = step * math.ceil((larger + 0.12 * (larger - low)) / step - 1e-9)
    if high > 100 >= larger + step / 2:
        high = 100.0
    return round(low, 10), round(high, 10)


def _zero_axis(larger: float) -> float:
    """Sıfır tabanlı eksenin üst sınırı: büyük değerin biraz üstündeki onluk (en çok 100)."""

    return float(min(100, 10 * math.ceil(larger * 1.15 / 10)))


def _step10(case: Case) -> LabStep:
    title, note = "Kesilmiş eksen: yüzde ve yüzde puan", "2.10"
    a, label = case.roles[ANA], case.label(ANA)
    counts, n = _counts(case, a), len(case.data)
    ranked = _ranked(counts)
    first = ranked[0]
    lower = [item for item in ranked if counts[item] < counts[first]]
    if not lower:
        return _blocked(10, title, note, (
            f"Bütün kategorilerin frekansı eşit ({int(counts[first])}); kesilmiş eksenin etkisini göstermek için "
            "payları farklı iki kategori gerekir."
        ))
    second = lower[0]
    f1, f2 = int(counts[first]), int(counts[second])
    p1, p2 = 100 * f1 / n, 100 * f2 / n
    low, high = _truncated_axis(p1, p2)
    full = _zero_axis(p1)
    gap, relative = p1 - p2, 100 * (p1 - p2) / p2
    digits = _decimals(p1, p2)
    exact = esit(p1, digits) == "=" and esit(p2, digits) == "="
    sign = esit(relative, 1) if exact else "\\approx"
    roughly = "" if esit(gap, digits) == "=" else "yaklaşık "
    pair = (first, second)
    ties = sum(int(counts[item]) == f1 for item in ranked)
    lead = "En yaygın kategorilerden" if ties > 1 else "En yaygın kategori"
    return LabStep(
        number=10,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"{lead} {md(first)} ({yuzde(p1, digits)}) ile payı ondan küçük olan ilk kategori {md(second)} "
            f"({yuzde(p2, digits)}) karşılaştırılır. Aynı iki yüzde önce {kisa(low, 4)}–{kisa(high, 4)} aralığına "
            f"kesilmiş, sonra sıfırdan başlayan bir eksenle çizilir. Fark {roughly}{kisa(gap, digits)} **yüzde "
            f"puandır**; göreli fark ise $({tex(p1, digits)} - {tex(p2, digits)})/{tex(p2, digits)} \\times 100 "
            f"{sign} \\%{tex(relative, _decimals(relative))}$ olur."
        ),
        operations=(
            BarChart("tam_tablo", "yuzde", label, "Yüzde", "Kesilmiş eksen", y_range=(low, high), percent=True,
                     decimals=1, rows=pair),
            BarChart("tam_tablo", "yuzde", label, "Yüzde", "Sıfır tabanlı eksen", y_range=(0, full), percent=True,
                     decimals=1, rows=pair),
            Count(case.frame, "f_1", a, first, f"{first} frekansı"),
            Count(case.frame, "f_2", a, second, f"{second} frekansı"),
            Scalar("yuzde_1", E.mul(100, E.div(E.ref("f_1"), E.ref("n"))), f"{first} yüzdesi", decimals=1,
                   percent=True),
            Scalar("yuzde_2", E.mul(100, E.div(E.ref("f_2"), E.ref("n"))), f"{second} yüzdesi", decimals=1,
                   percent=True),
            Scalar("fark_puan", E.sub(E.ref("yuzde_1"), E.ref("yuzde_2")), "Fark (yüzde puan)", decimals=1),
            Scalar("goreli_fark", E.mul(100, E.div(E.sub(E.ref("yuzde_1"), E.ref("yuzde_2")), E.ref("yuzde_2"))),
                   "Göreli fark", decimals=1, percent=True),
        ),
        checks=(
            _scalar("fark_puan", "Fark (yüzde puan)", 1),
            _scalar("goreli_fark", "Göreli fark (%)", 1),
        ),
        takeaway=(
            f"Kesilmiş eksende {md(first)} sütunu {md(second)} sütununun yaklaşık {kisa((p1 - low) / (p2 - low), 1)} "
            f"katı uzunluğunda görünür; iki yüzdenin gerçek oranı ise {kisa(p1 / p2, 2)}. Sütun grafiğinde değer "
            "ekseni genel olarak sıfırdan başlamalıdır; “yüzde” ile “yüzde puan” aynı kavram değildir."
        ),
    )


def _rate(data: pd.DataFrame, option_col: str, option: str, outcome_col: str, positive: str) -> float:
    chosen = data[data[option_col].astype(str) == option]
    return 100 * float((chosen[outcome_col].astype(str) == positive).mean())


def _sign(value: float) -> int:
    return (value > 1e-9) - (value < -1e-9)


def _simpson_text(first: str, second: str, within: list[float], overall: float) -> str:
    """Alt gruplardaki ve toplamdaki yön; bütün durumlar (eşitlikler dahil) ayrı ayrı yazılır."""

    signs = [_sign(diff) for diff in within]
    nonzero = {sign for sign in signs if sign}
    total = _sign(overall)

    def winner(sign: int) -> str:
        return md(first if sign > 0 else second)

    direction = next(iter(nonzero)) if len(nonzero) == 1 else 0
    if not nonzero:
        within_text = "Her alt grupta iki seçeneğin oranı eşit."
    elif len(nonzero) == 2:
        within_text = (f"Alt gruplarda yön aynı değil: bazı gruplarda {md(first)}, bazılarında {md(second)} daha "
                       "yüksek orana sahip.")
    elif 0 in signs:
        within_text = (f"Alt grupların bir kısmında {winner(direction)} daha yüksek orana sahip; diğerlerinde oranlar "
                       "eşit.")
    else:
        within_text = f"Her alt grupta daha yüksek oran: {winner(direction)}."
    overall_text = ("Gruplar birleştirilince oranlar eşit." if total == 0
                    else f"Gruplar birleştirilince daha yüksek oran: {winner(total)}.")
    if direction and total == direction:
        conclusion = "Bu veride yön değişmiyor; yine de farkın büyüklüğü alt grupların bileşiminden etkilenir."
    elif direction and total == -direction and 0 not in signs:
        conclusion = "Bu, Simpson paradoksudur."
    elif direction and total == -direction:
        conclusion = ("Gruplar birleştirilince yön tersine dönüyor; toplam oran alt grupların bileşiminden "
                      "etkilenir.")
    elif direction:
        conclusion = ("Toplamdaki karşılaştırma alt gruplardaki yönü göstermiyor; toplam oran alt grupların "
                      "bileşiminden etkilenir.")
    elif not nonzero:
        conclusion = ("Toplamdaki fark alt gruplardan değil, iki seçeneğin alt gruplara farklı dağılmasından doğar."
                      if total else "")
    elif total == 0:
        conclusion = "Toplamda iki yön birbirini dengeliyor."
    else:
        conclusion = "Toplamdaki fark, alt grupların büyüklüğüne bağlı olarak bu yönlerden birine benzer."
    return " ".join(part for part in (within_text, overall_text, conclusion) if part)


def _composition_text(data: pd.DataFrame, s: str, g: str, o: str, options: tuple, groups: tuple,
                      positive: str) -> str:
    first, second = options
    shares = {group: {option: 100 * float((data.loc[data[s] == option, g] == group).mean()) for option in options}
              for group in groups}
    differences = {group: shares[group][first] - shares[group][second] for group in groups}
    if all(abs(value) < 1e-9 for value in differences.values()):
        return ("İki seçeneğin alt gruplara dağılımı aynı; bu durumda toplamdaki fark alt gruplardaki farkların "
                "ağırlıklı ortalamasıdır: alt gruplarda yön aynıysa toplamda da aynı kalır. Karşılaştırmayı alt "
                "gruplarda yapmak yine de bileşimi görünür kılar.")
    rates = {group: float((data.loc[data[g] == group, o] == positive).mean()) for group in groups}
    easiest = max(groups, key=lambda group: rates[group])
    target = easiest if abs(differences[easiest]) > 1e-9 else max(groups, key=lambda group: abs(differences[group]))
    remark = f" ({md(positive)} oranı en yüksek grup)" if target == easiest else ""
    return (
        f"Seçenekler alt gruplara eşit dağılmamıştır: “{md(target)}” alt grubunun{remark} payı {md(first)} "
        f"gözlemlerinde {yuzde(shares[target][first])}, {md(second)} gözlemlerinde {yuzde(shares[target][second])}. "
        "Toplam oran alt grupların bileşiminden etkilenir; karşılaştırma alt gruplarda da yapılmalıdır."
    )


def _step11(case: Case) -> LabStep:
    title, note = "Toplulaştırma yanılsaması: Simpson paradoksu", "2.11"
    if not all(case.has(role) for role in SIMPSON):
        return _missing(11, title, note, "Karşılaştırılan iki seçenek, Alt grup ve Sonuç")
    s, g, o = (case.roles[role] for role in SIMPSON)
    if len({s, g, o}) < 3:
        return _blocked(11, title, note, "Seçenek, alt grup ve sonuç için üç farklı sütun gerekir.")
    s_label, g_label = case.label(SECENEK), case.label(ALTGRUP)
    positive = case.levels[SONUC]
    frame, data, load = _complete(case, (s, g, o), "veri_simpson",
                                  "Simpson adımı için üç sütunda da değeri olan gözlemler")
    data = data.astype({s: str, g: str, o: str})
    options, groups = _present(case, s, data), _present(case, g, data)
    outcome_values = _present(case, o, data)
    skipped = len(case.data) - len(data)
    if len(options) != 2 or len(groups) < 2 or positive not in outcome_values:
        return _blocked(11, title, note, (
            f"Üç sütunda da değeri olan {len(data)} gözlemde iki seçenek, en az iki alt grup ve seçilen sonuç "
            f"(“{md(positive)}”) bulunmalı."
        ))
    outcomes = (positive, *[item for item in outcome_values if item != positive])
    missing = [group for group in groups for option in options
               if not ((data[g] == group) & (data[s] == option)).any()]
    if missing:
        return _blocked(11, title, note, (
            "Her alt grupta iki seçeneğin de gözlemi olmalıdır; şu alt grup(lar)da bir seçenek hiç yok: "
            f"{_names(sorted(set(missing), key=K.turkish_key))}."
        ))
    first, second = options
    within = [(_rate(data[data[g] == group], s, first, o, positive)
               - _rate(data[data[g] == group], s, second, o, positive)) for group in groups]
    overall = _rate(data, s, first, o, positive) - _rate(data, s, second, o, positive)
    result = _simpson_text(first, second, within, overall)
    operations = [
        *load,
        *(CrossTab(frame, s, o, f"oran_{index}", options, outcomes, percent="satir", where=(g, group))
          for index, group in enumerate(groups, start=1)),
        CrossTab(frame, s, o, "genel_sayi", options, outcomes, margins=True),
        CrossTab(frame, s, o, "genel_oran", options, outcomes, percent="satir"),
        CompareBarChart(
            (*((group, f"oran_{index}") for index, group in enumerate(groups, start=1)), ("Tüm gruplar", "genel_oran")),
            positive,
            g_label,
            f"{positive} oranı (%)",
            f"{s_label} seçeneklerine göre {positive} oranı: alt gruplar ve toplam",
        ),
    ]
    checks = [
        _cell(f"oran_{index}", option, positive, f"{group}: {option} (%)", 1)
        for index, group in enumerate(groups, start=1) for option in options
    ]
    checks += [_cell("genel_sayi", option, positive, f"Tüm gruplarda {option}: {positive}") for option in options]
    checks += [_cell("genel_sayi", option, TOTAL, f"Tüm gruplarda {option}: toplam") for option in options]
    checks += [_cell("genel_oran", option, positive, f"Tüm gruplarda {option} (%)", 1) for option in options]
    skipped_text = f" Bu üç sütundan birinde boş hücre olan {skipped} gözlem bu adımda kullanılmaz." if skipped else ""
    return LabStep(
        number=11,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"“{md(s_label)}” sütunundaki iki seçeneğin ({md(first)}, {md(second)}) “{md(positive)}” oranı önce her "
            f"“{md(g_label)}” grubunda ayrı ayrı, sonra bütün gözlemlerde birlikte hesaplanır.{skipped_text} {result}"
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=_composition_text(data, s, g, o, options, groups, positive),
    )


def _step12(case: Case) -> LabStep:
    a, label, order = case.roles[ANA], case.label(ANA), case.orders[case.roles[ANA]]
    counts, n = _counts(case, a), len(case.data)
    most, high, _, _ = _extremes(counts)
    share = yuzde(100 * high / n)
    common = f"{_names(most)}, {share}" if len(most) == 1 else f"{_names(most)}, her biri {share}"
    return LabStep(
        number=12,
        title="Bütünleştirici uygulama: bir değişkeni raporlamak",
        note=NoteRef("2.12"),
        explanation=(
            f"“{md(label)}” rapor biçiminde özetlenir: frekanslardan yüzdeler hesaplanır, toplamlar kontrol edilir ve "
            "yüzdeler büyükten küçüğe yatay sütun grafiğiyle çizilir. Grafikte frekans yerine yüzde kullanılır: soru "
            f"“kaç {case.unit}?” değil, “toplamın ne kadarı?” sorusudur."
        ),
        operations=(
            FrequencyTable(case.frame, a, "rapor_tablosu", order, relative=True, totals=True),
            BarChart("rapor_tablosu", "yuzde", label, "Yüzde", f"{label} için yatay sütun grafiği", sort="azalan",
                     horizontal=True, percent=True, decimals=1),
        ),
        checks=(
            _cell("rapor_tablosu", TOTAL, "frekans", "Frekansların toplamı"),
            *(_cell("rapor_tablosu", item, "yuzde", f"{item} (%)", 1) for item in order),
            _cell("rapor_tablosu", TOTAL, "yuzde", "Yüzdelerin toplamı", 1),
        ),
        takeaway=(
            f"Rapor sırası: değişkeni tanımla, özeti kontrol et ({n} gözlem ve %100), örüntüyü belirt (en yaygın: "
            f"{common}), uygun grafiği seç ve sınırı yaz: sonuçlar yalnız bu {n} {case.unit} için geçerlidir."
        ),
    )


def build(case: Case) -> LabSpec:
    """Konu 2 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    steps = (_step1(case), _step2(case), _step3(case), _step4(case), _step5(case), _step6(case), _step7(case),
             _step8(case), _step9(case), _step10(case), _step11(case), _step12(case))
    spec = LabSpec(
        topic_key="konu02",
        title=TITLE,
        note_section="2",
        steps=steps,
        labels=tuple(case.labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def alternative_case() -> Case:
    data = pd.DataFrame(list(ALT_ROWS), columns=list(ALT_COLUMNS))
    return Case(
        source="alternatif",
        load=(InlineData("siparisler", ALT_COLUMNS, ALT_ROWS, "Kurgusal veri: bir kafenin 100 siparişi"),),
        frame="siparisler",
        data=data,
        roles={ANA: "odeme", SATIR: "sube", SECENEK: "sube", ALTGRUP: "siparis_turu", SONUC: "memnuniyet"},
        labels=ALT_LABELS,
        levels={SONUC: "Memnun"},
        orders=ALT_ORDERS,
        unit="sipariş",
        extra={
            "read_text": "Sipariş kayıtları satır satır okunur: her satır bir sipariş (gözlem), her sütun bir "
                         "değişkendir.",
            "order_text": "kayıt formundaki sırayla",
            "nominal_text": "Ödeme yöntemi nominal bir değişkendir; kategorilerin doğal bir sırası yoktur.",
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin verisi, Türkçe sütun adlarıyla."""

    return pd.DataFrame(list(ALT_ROWS), columns=[ALT_LABELS[name] for name in ALT_COLUMNS])


ROLES = (
    Role(ANA, "Ana kategorik değişken", "kategorik", True, (1, 2, 3, 4, 5, 6, 10, 12),
         "Frekans tablosu ve grafiklerin değişkeni (ör. ulaşım biçimi, ödeme yöntemi).", levels=(2, 15)),
    Role(SATIR, "İkinci kategorik değişken (satırlar)", "kategorik", False, (7, 8, 9),
         "Çapraz tablonun satırları (ör. bölüm, şube).", levels=(2, 10), suggest=True),
    Role(SECENEK, "Karşılaştırılan iki seçenek", "kategorik", False, (11,),
         "Tam iki kategorili sütun (ör. tasarım A ve B).", levels=(2, 2), group="simpson"),
    Role(ALTGRUP, "Alt grup", "kategorik", False, (11,),
         "Gözlemleri gruplara ayıran sütun (ör. müşteri grubu).", levels=(2, 6), group="simpson"),
    Role(SONUC, "Sonuç", "kategorik", False, (11,),
         "Tam iki kategorili sonuç (ör. dönüştü, dönüşmedi).", levels=(2, 2), pick="Oranı hesaplanacak sonuç",
         group="simpson"),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Kategorik sütunlar içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin. Ana kategorik değişken zorunludur; "
        "çapraz tablo (Adım 7–9) ve Simpson paradoksu (Adım 11) için ek sütunlar seçebilirsiniz. Ana değişkeni boş "
        "olan satırlar analizden çıkarılır; diğer sütunlardaki boş hücreler yalnız o sütunu kullanan adımları etkiler."
    ),
    order_roles=(ANA, SATIR, SECENEK, ALTGRUP, SONUC),
    min_rows=5,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
