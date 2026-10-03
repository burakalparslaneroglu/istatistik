"""Konu 6 genel uygulaması: örnek uzay, sayma kuralları, olasılık atama, olaylar ve toplama kuralı.

Ders notlarındaki adımlar (§6.2–§6.10) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Olaylar veriden
kurulur: iki kategorik sütun ve her birinde seçilen bir kategori E ve F olaylarını tanımlar (Adım 2, 4, 6, 8 ve 9).
Sayma kuralları öğrencinin seçtiği değerlerle çalışır: zarın yüz sayısı m (Adım 1, 2, 4–7), ekip büyüklüğü N ve seçilen
kişi sayısı n (Adım 3). Alternatif örnek kurgusal bir kafe veri setidir (200 sipariş), sekiz yüzlü bir zar ve altı
kişilik bir ekip; "kendi verini yükle" seçeneğinde aynı adımlar öğrencinin dosyası ve kaydırıcılarla kurulur. Notlardaki
uygulama (``core.labs.konu06``) değişmez.

Olaylar örnek uzayın alt kümeleridir: her örnek nokta (ya da gözlem) bir satırdır, olayın gösterge sütunu olaydaki
satırlarda 1, diğerlerinde 0'dır. Verideki bir olayın olasılığı göreli frekansıdır: gösterge sütununun ortalaması.
"""

from __future__ import annotations

import math
import string
from decimal import Decimal
from fractions import Fraction
from functools import cache

import numpy as np
import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    Setting,
    TopicVariants,
    free_name,
    liste,
    md,
    ondalik,
    ondalik_tex,
    with_app_values,
)
from core.labs.spec import (
    TOTAL,
    BarChart,
    CellTarget,
    Check,
    CrossTab,
    Derive,
    Event,
    FrequencyTable,
    FromCounts,
    LabSpec,
    LabStep,
    NoteRef,
    Outcomes,
    Scalar,
    ScalarTarget,
    Selections,
    ShowFrame,
    Statistic,
    TableTarget,
)

TITLE = "Örnek uzay, sayma ve temel olasılık kurallarını uygulamak"
OLAY_E, OLAY_F = "olay_e", "olay_f"
ZAR, EKIP, SECIM = "zar", "ekip", "secim"
LIST_LIMIT = 720
"""Kombinasyon ve permütasyonlar bu sayıya kadar tek tek listelenir (P(6, 3) = 120; P(6, 6) = 720)."""
MAX_DIGITS = 4
"""Olasılıkların en çok gösterim basamağı (notlarda 1/6 dört basamakla)."""

ALT_COUNTS = (
    ("Kart", "Masada", 60), ("Kart", "Paket", 30),
    ("Nakit", "Masada", 35), ("Nakit", "Paket", 15),
    ("Mobil", "Masada", 25), ("Mobil", "Paket", 35),
)
"""Kurgusal veri: bir kafenin 200 siparişinin ödeme yöntemi ve sipariş türü (sayım tablosu)."""
ALT_LABELS = {"odeme": "Ödeme yöntemi", "tur": "Sipariş türü"}
ALT_ORDERS = {"odeme": ("Kart", "Nakit", "Mobil"), "tur": ("Masada", "Paket")}
ALT_PICKS = {OLAY_E: "Mobil", OLAY_F: "Paket"}
ALT_SETTINGS = {ZAR: 8, EKIP: 6, SECIM: 3}
ALT_TEAM = {
    "text": ("Kafenin altı çalışanı A, B, C, D, E ve F ile gösterilsin. Hafta sonu vardiyasına üç kişi seçilecekse "
             "sıra önemsizdir; vardiya şefi, kasiyer ve barista görevleri dağıtılacaksa görevler farklıdır."),
    "combination": "Hafta sonu vardiyasına seçilecek üç kişi",
    "permutation": "Vardiya şefi, kasiyer ve barista",
    "roles": (("sef", "Vardiya şefi"), ("kasiyer", "Kasiyer"), ("barista", "Barista")),
}
STORY = (
    "Kurgusal veri: bir kafenin 200 siparişinde ödeme yöntemi (Kart, Nakit, Mobil) ve sipariş türü (Masada, Paket); "
    "ayrıca sekiz yüzlü bir zar ve altı kişilik bir çalışan ekibi."
)


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _digits(value: Fraction) -> int:
    """Olasılığın gösterim basamağı: en çok ``MAX_DIGITS`` basamakla tam yazılabiliyorsa tam (0,175), değilse
    ``MAX_DIGITS`` (1/6 → 0,1667); en az 2 (notlardaki 0,50)."""

    for digits in range(0, MAX_DIGITS + 1):
        if (value * 10 ** digits).denominator == 1:
            return max(2, digits)
    return MAX_DIGITS


def _decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _sign(value: Fraction, digits: int) -> str:
    """Matematik içinde "=" ya da "\\approx": kesir gösterilen basamakla tam yazılabiliyorsa "="."""

    return "=" if (value * 10 ** digits).denominator == 1 else "\\approx"


def _prob(value: Fraction, digits: int | None = None) -> str:
    """Olasılık, matematik ifadesinde (0{,}175)."""

    return ondalik_tex(_decimal(value), _digits(value) if digits is None else digits)


def _text(value: Fraction, digits: int | None = None) -> str:
    """Olasılık, düzyazıda; yuvarlanmışsa başında "yaklaşık"."""

    digits = _digits(value) if digits is None else digits
    shown = ondalik(_decimal(value), digits)
    return shown if _sign(value, digits) == "=" else f"yaklaşık {shown}"


def _set(values: list[int]) -> str:
    """Küme yazımı: altıya kadar öğe tek tek; daha fazlasında düzenli artan baş kısım üç noktayla, düzeni bozan son
    öğeler açıkça ({2, 4, …, 20}; {2, 4, …, 18, 19, 20}; {2, 4, …, 12, 13})."""

    items = [str(value) for value in values]
    if len(values) > 6:
        step, end = values[1] - values[0], 1
        while end + 1 < len(values) and values[end + 1] - values[end] == step:
            end += 1
        if end >= 3:  # düzenli baş kısım en az dört öğe: ilk iki öğe, üç nokta, son öğesi
            items = [items[0], items[1], "\\ldots", *items[end:]]
    return "\\{" + ", ".join(items) + "\\}"


def _settings(case: Case) -> dict[str, int]:
    chosen = dict(ALT_SETTINGS)
    chosen.update(case.extra.get("settings") or {})
    return chosen


def _context(case: Case) -> dict:
    e_col, f_col = case.roles[OLAY_E], case.roles[OLAY_F]
    e_pick, f_pick = case.levels[OLAY_E], case.levels[OLAY_F]
    data = case.data.astype({e_col: str, f_col: str})
    n = len(data)
    in_e = data[e_col] == e_pick
    in_f = data[f_col] == f_pick
    counts = {"e": int(in_e.sum()), "f": int(in_f.sum()), "ef": int((in_e & in_f).sum()),
              "union": int((in_e | in_f).sum())}
    settings = _settings(case)
    taken = set(case.data.columns) | set(case.labels)
    names = {}
    for key in ("sonuc", "birinci", "ikinci", "toplam", "olasilik", "agirlik", "E", "F", "E_degil", "E_ve_F",
                "E_veya_F", "hicbiri"):
        names[key] = free_name(key, taken)
        taken.add(names[key])
    people = []
    for index in range(1, settings[SECIM] + 1):
        people.append(free_name(f"kisi_{index}", taken))
        taken.add(people[-1])
    tasks = []
    for index in range(1, settings[SECIM] + 1):
        tasks.append(free_name(f"gorev_{index}", taken))
        taken.add(tasks[-1])
    observed = data.groupby([e_col, f_col]).size()
    return {
        "e_col": e_col, "f_col": f_col, "e_pick": e_pick, "f_pick": f_pick, "n": n, "counts": counts,
        "e_label": case.label(OLAY_E), "f_label": case.label(OLAY_F),
        "e_order": tuple(case.orders[e_col]), "f_order": tuple(case.orders[f_col]),
        "m": settings[ZAR], "team": settings[EKIP], "pick": settings[SECIM], "names": names,
        "people": tuple(people), "tasks": tuple(tasks),
        "unobserved": len(case.orders[e_col]) * len(case.orders[f_col]) - len(observed),
    }


# --- Adımlar -------------------------------------------------------------------------------

def _faces(m: int) -> tuple[int, ...]:
    return tuple(range(1, m + 1))


def _step1(case: Case, ctx: dict) -> LabStep:
    m, names = ctx["m"], ctx["names"]
    sonuc, birinci, ikinci, toplam = (names[key] for key in ("sonuc", "birinci", "ikinci", "toplam"))
    faces = _faces(m)
    sums = tuple(range(2, 2 * m + 1))
    return LabStep(
        number=1,
        title="Örnek uzay: bir zar ve iki zar",
        note=NoteRef("6.2"),
        explanation=(
            f"{m} yüzlü adil bir zar atıldığında örnek uzay $S = {_set(list(faces))}$ kümesidir. İki zar atıldığında "
            f"temel örnek noktalar $(1, 1), (1, 2), \\ldots, ({m}, {m})$ biçimindeki zar çiftleridir. Toplam 2 ile "
            f"{2 * m} arasında bir değer alır; ama her toplam aynı sayıda temel sonuçla oluşmaz."
        ),
        operations=(
            Outcomes("zar", ((sonuc, faces),), f"{m} yüzlü zar atılır: örnek uzay S"),
            Statistic("zar", sonuc, "count", "m", "Örnek nokta sayısı m", decimals=0),
            Outcomes("iki_zar", ((birinci, faces), (ikinci, faces)), "İki zar atılır: temel örnek noktalar"),
            Derive("iki_zar", toplam, E.add(E.var(birinci), E.var(ikinci)), "İki zarın toplamı"),
            Statistic("iki_zar", toplam, "nunique", "farkli_toplam", "Farklı toplam sayısı", decimals=0),
            FrequencyTable("iki_zar", toplam, "toplamlar", sums, relative=False),
            BarChart("toplamlar", "frekans", "İki zarın toplamı", "Temel örnek nokta sayısı",
                     "Her toplam kaç temel sonuçla oluşur?"),
        ),
        checks=(
            _scalar("m", "Bir zarda örnek nokta sayısı"),
            _scalar("farkli_toplam", f"Farklı toplam sayısı (2, …, {2 * m})"),
            Check("Toplam 2: yalnız (1, 1)", TableTarget("toplamlar", 2, "frekans"), 0.0, 0),
            Check(f"Toplam {m + 1}: en sık toplam", TableTarget("toplamlar", m + 1, "frekans"), 0.0, 0),
        ),
        takeaway=(
            f"{2 * m - 1} toplamın her biri mümkündür ama eşit olasılıklı değildir: toplam 2 yalnız bir, toplam "
            f"{m + 1} ise {m} temel sonuçla oluşur. Olasılıkları kurmak için örnek noktalar zar çiftleri olarak "
            "yazılır (§6.2)."
        ),
    )


def _categories(order: tuple[str, ...]) -> str:
    return liste([md(item) for item in order])


def _step2(case: Case, ctx: dict) -> LabStep:
    e_col, f_col, m = ctx["e_col"], ctx["f_col"], ctx["m"]
    k_e, k_f = len(ctx["e_order"]), len(ctx["f_order"])
    unobserved = ctx["unobserved"]
    lead = case.extra.get("read_text") or f"Dosyanızdaki {ctx['n']} gözlem okunur."
    missing = (f" Bu bileşimlerden {unobserved} tanesi veride hiç gözlenmemiştir; örnek uzay deney yapılmadan önce "
               "mümkün olan bütün sonuçları içerdiği için onlar da listededir." if unobserved else "")
    return LabStep(
        number=2,
        title="Çok aşamalı deney ve çarpım kuralı",
        note=NoteRef("6.3"),
        explanation=(
            f"{lead} Bir gözlem önce “{md(ctx['e_label'])}” sütununa ({k_e} seçenek: {_categories(ctx['e_order'])}), "
            f"sonra “{md(ctx['f_label'])}” sütununa ({k_f} seçenek: {_categories(ctx['f_order'])}) göre sınıflanır. "
            "Ağaç diyagramındaki her tam dal bir örnek noktadır. $k$ aşamada $n_1, n_2, \\ldots, n_k$ seçenek varsa "
            f"sonuç sayısı $n_1 n_2 \\cdots n_k$'dır: ${k_e} \\times {k_f} = {k_e * k_f}$.{missing} İki zar atmak da "
            f"iki aşamalı bir deneydir: ${m} \\times {m} = {m * m}$ temel sonuç (Adım 1)."
        ),
        operations=(
            *case.load,
            Outcomes("siniflama", ((e_col, ctx["e_order"]), (f_col, ctx["f_order"])),
                     "İki aşamalı sınıflama: bütün sonuçlar"),
            Statistic("siniflama", e_col, "count", "sonuc_sayisi", "Listelenen sonuç sayısı", decimals=0),
            Scalar("iki_asama", E.mul(k_e, k_f), f"Çarpım kuralı: {k_e} × {k_f}", decimals=0),
            Scalar("zar_ciftleri", E.mul(m, m), f"İki zar: {m} × {m}", decimals=0),
        ),
        checks=(
            _scalar("sonuc_sayisi", "Listelenen sonuç sayısı"),
            _scalar("iki_asama", f"{k_e} × {k_f}"),
            _scalar("zar_ciftleri", f"{m} × {m}"),
        ),
        takeaway=(
            "Sonuçlar ağaçtaki sırayla listelenir: ilk aşama en yavaş, son aşama en hızlı değişir. Çarpım kuralı "
            "listeyi yazmadan sonuç sayısını verir; aşama sayısı arttıkça listelemek pratik olmaktan çıkar (§6.3)."
        ),
    )


def _team(case: Case, ctx: dict) -> dict:
    """Adım 3'ün ekibi: üyelerin harfleri, seçim ve görev sütunları (alternatif örnekte görev adlarıyla)."""

    size, pick = ctx["team"], ctx["pick"]
    members = tuple(string.ascii_uppercase[:size])
    own = case.extra.get("team")
    if own and len(own["roles"]) == pick:
        roles = own["roles"]
        text, combination, permutation = own["text"], own["combination"], own["permutation"]
    else:
        roles = tuple((name, f"{index}. görev") for index, name in enumerate(ctx["tasks"], start=1))
        shown = ", ".join(members[:3]) + (", …" if size > 3 else "")
        text = (f"{size} kişilik bir ekibi {shown} harfleriyle gösterelim. {pick} kişi seçilecekse ve sıra önemsizse "
                "kombinasyon; aynı kişiler farklı görevlere dağıtılacaksa permütasyon sayılır.")
        combination = f"{size} kişiden seçilen {pick} kişi"
        permutation = f"{size} kişiye dağıtılan {pick} farklı görev"
    people = tuple((name, f"{index}. kişi") for index, name in enumerate(ctx["people"], start=1))
    return {"members": members, "roles": roles, "people": people, "text": text, "combination": combination,
            "permutation": permutation}


def _step3(case: Case, ctx: dict) -> LabStep:
    size, pick = ctx["team"], ctx["pick"]
    team = _team(case, ctx)
    combinations, permutations = math.comb(size, pick), math.perm(size, pick)
    operations = [
        Scalar("faktoriyel", E.factorial(size), f"{size}!", decimals=0),
        Scalar("kombinasyon", E.comb(size, pick), f"Kombinasyon C({size}, {pick})", decimals=0),
        Scalar("permutasyon", E.perm(size, pick), f"Permütasyon P({size}, {pick})", decimals=0),
    ]
    checks = [
        _scalar("faktoriyel", f"{size}!"),
        _scalar("kombinasyon", f"C({size}, {pick}) = {size}!/({pick}! {size - pick}!)"),
        _scalar("permutasyon", f"P({size}, {pick}) = {size}!/{size - pick}!"),
    ]
    listed = []
    if combinations <= LIST_LIMIT:
        operations += [
            Selections("secim", team["members"], pick, False, tuple(name for name, _ in team["people"]),
                       team["combination"]),
            Statistic("secim", team["people"][0][0], "count", "grup_sayisi", "Listelenen grup sayısı", decimals=0),
        ]
        checks.append(_scalar("grup_sayisi", "Listelenen grup sayısı"))
        listed.append("combination")
    if permutations <= LIST_LIMIT:
        operations += [
            Selections("gorev", team["members"], pick, True, tuple(name for name, _ in team["roles"]),
                       team["permutation"]),
            Statistic("gorev", team["roles"][0][0], "count", "gorev_sayisi", "Listelenen görev dağılımı sayısı",
                      decimals=0),
        ]
        checks.append(_scalar("gorev_sayisi", "Listelenen görev dağılımı sayısı"))
        listed.append("permutation")
    if pick == 1:
        takeaway = ("Tek kişi seçilirken sıra ya da görev fark yaratmaz: kombinasyon ve permütasyon sayısı aynıdır. "
                    "Formülden önce “sıra veya görev önemli mi?” sorusu cevaplanır (§6.4).")
    elif len(listed) == 2:
        takeaway = (f"Permütasyon listesinde her grup {math.factorial(pick)} kez görünür ({pick}! farklı sırayla). Bu "
                    f"yüzden P({size}, {pick}) = {pick}! × C({size}, {pick}). Formülden önce “sıra veya görev önemli "
                    "mi?” sorusu cevaplanır (§6.4).")
    else:
        unlisted = ("Permütasyon listesi" if listed else "Kombinasyon ve permütasyon listeleri")
        takeaway = (f"P({size}, {pick}) = {pick}! × C({size}, {pick}): her grup {pick}! farklı sırayla dizilir. "
                    f"{unlisted} {LIST_LIMIT} satırı aşacağı için sayı yalnız formülle bulunur; formülden önce “sıra "
                    "veya görev önemli mi?” sorusu cevaplanır (§6.4).")
    return LabStep(
        number=3,
        title="Faktöriyel, kombinasyon ve permütasyon",
        note=NoteRef("6.4"),
        explanation=(
            f"{team['text']} Sıra önemsizse $\\binom{{{size}}}{{{pick}}} = {size}!/({pick}!\\,{size - pick}!)$; "
            f"görevler farklıysa $P({size}, {pick}) = {size}!/{size - pick}!$."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=takeaway,
    )


def _step4(case: Case, ctx: dict) -> LabStep:
    m, n, names = ctx["m"], ctx["n"], ctx["names"]
    sonuc, olasilik = names["sonuc"], names["olasilik"]
    e_col, e_pick = ctx["e_col"], ctx["e_pick"]
    count = ctx["counts"]["e"]
    share = Fraction(count, n)
    digits = min(_digits(share), 3)  # frekans tablosu göreli frekansı üç basamakla gösterir
    one = Fraction(1, m)
    return LabStep(
        number=4,
        title="Olasılık atama: klasik ve göreli frekans",
        note=NoteRef("6.5"),
        explanation=(
            f"Klasik yöntem: $m$ eşit olasılıklı sonuç varsa her örnek noktaya $1/m$ atanır; {m} yüzlü adil zarda "
            f"$P(1) = \\cdots = P({m}) = 1/{m} {_sign(one, MAX_DIGITS)} {_prob(one)}$. Göreli frekans yöntemi: "
            f"“{md(ctx['e_label'])}” sütununda {n} gözlemin {count} tanesi “{md(e_pick)}” ise bu kategorinin "
            f"olasılığı $\\approx {count}/{n} {_sign(share, digits)} {_prob(share, digits)}$ olarak tahmin edilir. İki "
            "durumda da $0 \\le P(E_i) \\le 1$ ve $\\sum P(E_i) = 1$'dir."
        ),
        operations=(
            Derive("zar", olasilik, E.div(1, E.ref("m")), "Klasik yöntem: her örnek noktaya 1/m"),
            ShowFrame("zar", (sonuc, olasilik), "Adil zarın örnek noktaları ve olasılıkları"),
            Statistic("zar", olasilik, "sum", "olasilik_toplami", "Olasılıkların toplamı", decimals=0),
            FrequencyTable(case.frame, e_col, "e_tablo", ctx["e_order"], totals=True),
        ),
        checks=(
            Check(f"Klasik yöntem: P(1) = 1/{m}", CellTarget("zar", olasilik, 1), 0.0, _digits(one)),
            _scalar("olasilik_toplami", "Olasılıkların toplamı"),
            Check("Gözlem sayısı", TableTarget("e_tablo", TOTAL, "frekans"), 0.0, 0),
            Check(f"Göreli frekans: {e_pick}", TableTarget("e_tablo", e_pick, "goreli"), 0.0, digits),
        ),
        takeaway=(
            "Göreli frekans, aynı sürecin çok sayıda tekrarından gelen bir tahmindir. Az gözlemde oran belirgin "
            "biçimde oynar; gözlem arttıkça daha istikrarlı bir düzeye yaklaşır. Sezgi sekmesindeki Deney 1 bunu "
            "gösterir (§6.5)."
        ),
    )


def _evens(m: int) -> list[int]:
    return list(range(2, m + 1, 2))


def _step5(case: Case, ctx: dict) -> LabStep:
    m, names = ctx["m"], ctx["names"]
    sonuc, olasilik = names["sonuc"], names["olasilik"]
    evens, top = _evens(m), [m - 1, m]
    p_a = Fraction(len(evens), m)
    digits = _digits(p_a)
    terms = " + ".join([f"1/{m}"] * len(evens)) if len(evens) <= 4 else f"{len(evens)} \\times 1/{m}"
    sum_label = " + ".join([f"1/{m}"] * len(evens)) if len(evens) <= 4 else "olasılıklar toplamı"
    return LabStep(
        number=5,
        title="Olay ve olayın olasılığı",
        note=NoteRef("6.6"),
        explanation=(
            f"Olay örnek uzayın bir alt kümesidir: $A$ = “çift sayı” $= {_set(evens)}$, $B$ = “en az {m - 1}” "
            f"$= {_set(top)}$. Olayın olasılığı olaydaki örnek noktaların olasılıklarının toplamıdır: "
            "$P(A) = \\sum_{E_i \\in A} P(E_i)$. Sonuçlar eşit olasılıklıysa bu, olaydaki nokta sayısının $m$'ye "
            "bölümüne eşittir."
        ),
        operations=(
            Event("zar", "A", sonuc, tuple(evens), "A: çift sayı gelmesi"),
            Event("zar", "B", sonuc, tuple(top), f"B: en az {m - 1} gelmesi"),
            ShowFrame("zar", (sonuc, olasilik, "A", "B"), "Örnek noktalar ve olaylar (1: olayda, 0: değil)"),
            Statistic("zar", olasilik, "sum", "P_A", "P(A): olasılıklar toplamı", where=("A", 1),
                      decimals=digits),
            Statistic("zar", "A", "sum", "A_sayisi", "A'daki örnek nokta sayısı", decimals=0),
            Scalar("P_A_klasik", E.div(E.ref("A_sayisi"), E.ref("m")), "P(A) = A'daki nokta sayısı / m",
                   decimals=digits),
        ),
        checks=(
            _scalar("A_sayisi", "A'daki örnek nokta sayısı"),
            _scalar("P_A", f"P(A) = {sum_label}", digits),
            _scalar("P_A_klasik", f"P(A) = {len(evens)}/{m}", digits),
        ),
        takeaway=(
            f"İki yol aynı sonucu verir: ${terms} = {len(evens)}/{m} {_sign(p_a, digits)} {_prob(p_a, digits)}$. Sayma "
            "oranı yalnız örnek noktalar eşit olasılıklıysa kullanılır; genel kural olasılıkları toplamaktır (§6.6)."
        ),
    )


def _step6(case: Case, ctx: dict) -> LabStep:
    n, names = ctx["n"], ctx["names"]
    e_col, e_pick = ctx["e_col"], ctx["e_pick"]
    event, outside = names["E"], names["E_degil"]
    count = ctx["counts"]["e"]
    p_e = Fraction(count, n)
    p_not = 1 - p_e
    digits = _digits(p_e)
    not_digits = _digits(p_not)
    others = [item for item in ctx["e_order"] if item != e_pick]
    return LabStep(
        number=6,
        title="Tümleyen olay",
        note=NoteRef("6.7"),
        explanation=(
            "$A^c$, örnek uzayda olup $A$'da olmayan noktalardır. Bir deneyde ya $A$ ya $A^c$ gerçekleşir: "
            "$P(A) + P(A^c) = 1$, dolayısıyla $P(A) = 1 - P(A^c)$. Verideki olay: $E$ = “"
            f"{md(ctx['e_label'])}: {md(e_pick)}”, $P(E) {_sign(p_e, digits)} {_prob(p_e, digits)}$. Tümleyeni "
            f"$E^c$ diğer kategorilerdir ({_categories(tuple(others))}) ve tümleyen kuralıyla bulunur."
        ),
        operations=(
            Derive("zar", "A_degil", E.sub(1, E.var("A")), "Aᶜ: çift olmayan sayı (A'da 0 olan noktalar)"),
            Event(case.frame, event, e_col, (e_pick,), f"E: {e_pick}"),
            Derive(case.frame, outside, E.sub(1, E.var(event)), "Eᶜ: E'de olmayan gözlemler"),
            Statistic("zar", names["olasilik"], "sum", "P_A_degil", "P(Aᶜ)", where=("A_degil", 1), decimals=_digits(
                Fraction(ctx["m"] - len(_evens(ctx["m"])), ctx["m"]))),
            Scalar("toplam_A", E.add(E.ref("P_A"), E.ref("P_A_degil")), "P(A) + P(Aᶜ)", decimals=0),
            Statistic(case.frame, event, "mean", "P_E", "P(E): göreli frekans", decimals=digits),
            Scalar("P_E_degil", E.sub(1, E.ref("P_E")), "P(Eᶜ) = 1 − P(E)", decimals=not_digits),
            Statistic(case.frame, outside, "mean", "P_E_degil_sayim", "P(Eᶜ): doğrudan sayım", decimals=not_digits),
        ),
        checks=(
            _scalar("toplam_A", "P(A) + P(Aᶜ)"),
            _scalar("P_E_degil", "P(Eᶜ) = 1 − P(E)", not_digits),
            _scalar("P_E_degil_sayim", "P(Eᶜ): E'de olmayan gözlemlerin oranı", not_digits),
        ),
        takeaway=(
            f"P(Eᶜ) = 1 − P(E) {'=' if _sign(p_e, digits) == '=' else '≈'} 1 − {ondalik(_decimal(p_e), digits)} "
            f"{'=' if _sign(p_not, not_digits) == '=' else '≈'} {ondalik(_decimal(p_not), not_digits)}: bu, E'de olmayan gözlemlerin doğrudan sayılan oranıyla aynıdır. "
            "E ile Eᶜ aynı anda gerçekleşemez ve birlikte bütün örnek uzayı kapsar. “En az bir”, “hiçbiri” gibi "
            "ifadelerde tümleyen çoğu zaman en kısa yoldur (§6.7)."
        ),
    )


def _step7(case: Case, ctx: dict) -> LabStep:
    m, names = ctx["m"], ctx["names"]
    evens, top = _evens(m), [m - 1, m]
    union = sorted(set(evens) | set(top))
    both = sorted(set(evens) & set(top))
    p_union, p_both = Fraction(len(union), m), Fraction(len(both), m)
    return LabStep(
        number=7,
        title="Birleşim ve kesişim",
        note=NoteRef("6.8"),
        explanation=(
            "$A \\cup B$: $A$ veya $B$ veya ikisi (göstergelerden en az biri 1). $A \\cap B$: hem $A$ hem $B$ (iki "
            f"gösterge de 1). $A = {_set(evens)}$ ve $B = {_set(top)}$ için $A \\cup B = {_set(union)}$ ve "
            f"$A \\cap B = {_set(both)}$."
        ),
        operations=(
            Derive("zar", "A_veya_B", E.maximum(E.var("A"), E.var("B")), "A ∪ B: iki göstergenin büyüğü"),
            Derive("zar", "A_ve_B", E.mul(E.var("A"), E.var("B")), "A ∩ B: iki göstergenin çarpımı"),
            ShowFrame("zar", (names["sonuc"], "A", "B", "A_veya_B", "A_ve_B"), "Birleşim ve kesişim"),
            Statistic("zar", names["olasilik"], "sum", "P_A_veya_B", "P(A ∪ B)", where=("A_veya_B", 1),
                      decimals=_digits(p_union)),
            Statistic("zar", names["olasilik"], "sum", "P_A_ve_B", "P(A ∩ B)", where=("A_ve_B", 1),
                      decimals=_digits(p_both)),
        ),
        checks=(
            _scalar("P_A_veya_B", f"P(A ∪ B) = {len(union)}/{m}", _digits(p_union)),
            _scalar("P_A_ve_B", f"P(A ∩ B) = {len(both)}/{m}", _digits(p_both)),
        ),
        takeaway=(
            f"Olasılıkta “veya” kapsayıcıdır: {both[0]} hem A'da hem B'dedir ve A ∪ B'de bir kez yer alır. “Yalnız "
            "biri” ayrı bir olay olarak açıkça belirtilmelidir (§6.8)."
        ),
    )


def _step8(case: Case, ctx: dict) -> LabStep:
    n, names, counts = ctx["n"], ctx["names"], ctx["counts"]
    e_col, f_col, e_pick, f_pick = ctx["e_col"], ctx["f_col"], ctx["e_pick"], ctx["f_pick"]
    event_e, event_f, both, either = names["E"], names["F"], names["E_ve_F"], names["E_veya_F"]
    p_e, p_f = Fraction(counts["e"], n), Fraction(counts["f"], n)
    p_ef, p_union = Fraction(counts["ef"], n), Fraction(counts["union"], n)
    digits = {key: _digits(value) for key, value in (("e", p_e), ("f", p_f), ("ef", p_ef), ("union", p_union))}
    sums = p_e + p_f
    # Terimlerden biri yuvarlanmışsa (1/3 → 0,3333) eşitlik yazılan sayılarla tam tutmaz: "≈".
    exact = all(_sign(value, _digits(value)) == "=" for value in (p_e, p_f, p_ef, p_union))
    rule_sign = "=" if exact else "\\approx"
    if counts["ef"] == 0:
        overlap = ("Bu veride E ile F ayrıktır (ortak gözlem yok): P(E ∩ F) = 0 olduğu için kural P(E) + P(F)'ye "
                   "sadeleşir.")
    else:
        sum_sign = "=" if _sign(sums, _digits(sums)) == "=" else "≈"
        overlap = (f"P(E) + P(F) {sum_sign} {ondalik(_decimal(sums), _digits(sums))} ortak kısmı iki kez sayar; "
                   f"çıkarınca {_text(p_union)} bulunur ve bu, en az birinin gerçekleştiği gözlemlerin doğrudan "
                   "sayılan oranıyla aynıdır. Ayrık olaylarda P(E ∩ F) = 0 olduğu için kural P(E) + P(F)'ye "
                   "sadeleşir.")
    both_text = (f"{counts['ef']} tanesi ikisinde birden" if counts["ef"] else "ikisinde birden olan gözlem yok")
    return LabStep(
        number=8,
        title="Toplama kuralı",
        note=NoteRef("6.9"),
        explanation=(
            f"$E$ = “{md(ctx['e_label'])}: {md(e_pick)}” ve $F$ = “{md(ctx['f_label'])}: {md(f_pick)}”. {n} gözlemin "
            f"{counts['e']} tanesi $E$'de, {counts['f']} tanesi $F$'de; {both_text}. "
            "Rastgele seçilen bir gözlem için olasılıklar oranlardır. Toplama kuralı: $P(E \\cup F) = P(E) + P(F) - "
            "P(E \\cap F)$; ortak kısım $P(E)$ ve $P(F)$'de iki kez sayıldığı için bir kez çıkarılır: "
            f"${_prob(p_e)} + {_prob(p_f)} - {_prob(p_ef)} {rule_sign} {_prob(p_union)}$."
        ),
        operations=(
            CrossTab(case.frame, e_col, f_col, "capraz", ctx["e_order"], ctx["f_order"], margins=True),
            Event(case.frame, event_f, f_col, (f_pick,), f"F: {f_pick}"),
            Derive(case.frame, both, E.mul(E.var(event_e), E.var(event_f)), "E ∩ F: ikisi birden"),
            Derive(case.frame, either, E.maximum(E.var(event_e), E.var(event_f)), "E ∪ F: en az biri"),
            Statistic(case.frame, event_f, "mean", "P_F", "P(F)", decimals=digits["f"]),
            Statistic(case.frame, both, "mean", "P_E_ve_F", "P(E ∩ F)", decimals=digits["ef"]),
            Scalar("P_E_veya_F", E.sub(E.add(E.ref("P_E"), E.ref("P_F")), E.ref("P_E_ve_F")),
                   "P(E ∪ F): toplama kuralı", decimals=digits["union"]),
            Statistic(case.frame, either, "mean", "P_E_veya_F_sayim", "P(E ∪ F): doğrudan sayım",
                      decimals=digits["union"]),
        ),
        checks=(
            _scalar("P_E", "P(E)", digits["e"]),
            _scalar("P_F", "P(F)", digits["f"]),
            _scalar("P_E_ve_F", "P(E ∩ F)", digits["ef"]),
            _scalar("P_E_veya_F", "P(E ∪ F) = P(E) + P(F) − P(E ∩ F)", digits["union"]),
            _scalar("P_E_veya_F_sayim", "P(E ∪ F): en az birinin gerçekleştiği gözlemlerin oranı", digits["union"]),
        ),
        takeaway=f"{overlap} Ayrıklık bağımsızlıkla aynı kavram değildir (§6.9).",
    )


def _step9(case: Case, ctx: dict) -> LabStep:
    n, names, counts = ctx["n"], ctx["names"], ctx["counts"]
    e_col, f_col, e_pick, f_pick = ctx["e_col"], ctx["f_col"], ctx["e_pick"], ctx["f_pick"]
    weight, neither = names["agirlik"], names["hicbiri"]
    event_e, event_f = names["E"], names["F"]
    cells = case.data.astype({e_col: str, f_col: str}).groupby([e_col, f_col]).size()
    digits = max([_digits(Fraction(int(count), n)) for count in cells] +
                 [_digits(Fraction(counts[key], n)) for key in ("e", "f", "ef", "union")])
    p_union = Fraction(counts["union"], n)
    p_neither = 1 - p_union
    union_digits, neither_digits = _digits(p_union), _digits(p_neither)
    covered = ("Bütün gözlemlerde E ya da F (ya da ikisi) gerçekleşir." if p_union == 1 else
               f"Gözlemlerin {_percent(p_union)} kadarında E ya da F (ya da ikisi) gerçekleşir.")
    return LabStep(
        number=9,
        title="Bütünleştirici uygulama: ortak olasılık tablosu",
        note=NoteRef("6.10"),
        explanation=(
            f"Gözlemlerden biri rastgele seçilsin; her gözleme $1/{n}$ olasılık düşer. “{md(ctx['e_label'])}” ve "
            f"“{md(ctx['f_label'])}” sütunlarının ortak olasılık tablosunda her hücre bir örnek noktanın olasılığıdır "
            "(göreli frekans); satır ve sütun toplamları olayların olasılıklarını verir. $P(E)$ satır toplamında, "
            "$P(F)$ sütun toplamında, $P(E \\cap F)$ ise iki olayın kesiştiği hücrededir. “Ne E ne F” olayı "
            "$E \\cup F$'nin tümleyenidir: "
            f"$1 - P(E \\cup F) {_sign(p_union, union_digits)} 1 - {_prob(p_union, union_digits)} "
            f"{_sign(p_neither, neither_digits)} {_prob(p_neither, neither_digits)}$."
        ),
        operations=(
            Statistic(case.frame, e_col, "count", "n_veri", "Gözlem sayısı n", decimals=0),
            Derive(case.frame, weight, E.div(1, E.ref("n_veri")), "Her gözlemin olasılığı 1/n"),
            Derive(case.frame, neither, E.mul(E.sub(1, E.var(event_e)), E.sub(1, E.var(event_f))),
                   "Ne E ne F: iki göstergenin de 0 olduğu gözlemler"),
            CrossTab(case.frame, e_col, f_col, "ortak", ctx["e_order"], ctx["f_order"], margins=True, decimals=digits,
                     weights=weight),
            Statistic(case.frame, weight, "sum", "toplam_olasilik", "Olasılıkların toplamı", decimals=2),
            Scalar("P_hicbiri", E.sub(1, E.ref("P_E_veya_F")), "Ne E ne F: 1 − P(E ∪ F)", decimals=neither_digits),
            Statistic(case.frame, neither, "mean", "P_hicbiri_sayim", "Ne E ne F: doğrudan sayım",
                      decimals=neither_digits),
        ),
        checks=(
            _scalar("toplam_olasilik", "Örnek nokta olasılıklarının toplamı", 2),
            Check(f"P(E): {e_pick} satırının toplamı", TableTarget("ortak", e_pick, TOTAL), 0.0, _digits(
                Fraction(counts["e"], n))),
            Check(f"P(F): {f_pick} sütununun toplamı", TableTarget("ortak", TOTAL, f_pick), 0.0, _digits(
                Fraction(counts["f"], n))),
            Check("P(E ∩ F): ortak hücre", TableTarget("ortak", e_pick, f_pick), 0.0, _digits(
                Fraction(counts["ef"], n))),
            _scalar("P_hicbiri", "Ne E ne F: 1 − P(E ∪ F)", neither_digits),
            _scalar("P_hicbiri_sayim", "Ne E ne F: iki olayın da dışındaki gözlemlerin oranı", neither_digits),
        ),
        takeaway=(
            f"{covered} Tümleyeni “ne E ne F” "
            f"sonucudur: tabloda “{md(e_pick)}” satırı ile “{md(f_pick)}” sütunu dışında kalan hücrelerin (Toplam "
            f"satırı ve sütunu hariç) toplamı da aynı değeri verir ({_text(p_neither, neither_digits)}). Aynı soruya "
            "iki yoldan gelmek hesabı denetlemenin iyi bir yoludur (§6.10)."
        ),
    )


def _percent(value: Fraction) -> str:
    """Düzyazıda yüzde: %52,5 ya da yaklaşık %33,3."""

    shown = value * 100
    digits = next((d for d in range(0, 2) if (shown * 10 ** d).denominator == 1), 1)
    text = "%" + ondalik(_decimal(shown), digits)
    return text if (shown * 10 ** digits).denominator == 1 else f"yaklaşık {text}"


def check_settings(case: Case) -> None:
    """Seçilen kişi sayısı ekip büyüklüğünü aşamaz (hata kaydırıcıların altında görünür)."""

    settings = _settings(case)
    if settings[SECIM] > settings[EKIP]:
        raise K.UploadError(f"Seçilen kişi sayısı n ({settings[SECIM]}) ekip büyüklüğü N'den ({settings[EKIP]}) büyük "
                            "olamaz; n'yi küçültün ya da N'yi büyütün.")


def build(case: Case) -> LabSpec:
    """Konu 6 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    check_settings(case)
    ctx = _context(case)
    steps = (_step1(case, ctx), _step2(case, ctx), _step3(case, ctx), _step4(case, ctx), _step5(case, ctx),
             _step6(case, ctx), _step7(case, ctx), _step8(case, ctx), _step9(case, ctx))
    names = ctx["names"]
    team = _team(case, ctx)
    labels = dict(case.labels)
    labels.update({names["sonuc"]: "Sonuç", names["birinci"]: "Birinci zar", names["ikinci"]: "İkinci zar",
                   names["toplam"]: "İki zarın toplamı", names["olasilik"]: "Olasılık P(Eᵢ)", "A_degil": "Aᶜ",
                   "A_veya_B": "A ∪ B", "A_ve_B": "A ∩ B"})
    for name, text in (*team["people"], *team["roles"]):
        labels.setdefault(name, text)
    for key, text in (("E", "E"), ("F", "F"), ("E_degil", "Eᶜ"), ("E_ve_F", "E ∩ F"), ("E_veya_F", "E ∪ F"),
                      ("hicbiri", "Ne E ne F"), ("agirlik", "Gözlemin olasılığı 1/n")):
        labels.setdefault(names[key], text)
    spec = LabSpec(
        topic_key="konu06",
        title=TITLE,
        note_section="6",
        steps=steps,
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def _alternative_frame() -> pd.DataFrame:
    rows = [(odeme, tur) for odeme, tur, count in ALT_COUNTS for _ in range(count)]
    return pd.DataFrame(rows, columns=["odeme", "tur"])


def alternative_case() -> Case:
    return Case(
        source="alternatif",
        load=(FromCounts("siparisler", ("odeme", "tur"), ALT_COUNTS,
                         "Kurgusal veri: 200 siparişin ödeme yöntemi ve sipariş türü"),),
        frame="siparisler",
        data=_alternative_frame(),
        roles={OLAY_E: "odeme", OLAY_F: "tur"},
        labels=ALT_LABELS,
        levels=dict(ALT_PICKS),
        orders=ALT_ORDERS,
        unit="sipariş",
        extra={
            "settings": dict(ALT_SETTINGS),
            "team": ALT_TEAM,
            "read_text": "Kafenin 200 siparişi ödeme yöntemi ve sipariş türüyle kaydedilmiştir.",
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin 200 siparişi, sabit bir karışık sırayla (sayılar sıradan bağımsızdır)."""

    frame = _alternative_frame()
    order = np.random.default_rng(217).permutation(len(frame))
    frame = frame.iloc[order].reset_index(drop=True)
    return frame.rename(columns=ALT_LABELS)


def validate(case: Case) -> None:
    """İki olay farklı sütunlardan kurulur (aynı sütunun iki kategorisi ayrık olaylar olurdu; Adım 2 ve 9 anlamını
    yitirirdi)."""

    if case.roles[OLAY_E] == case.roles[OLAY_F]:
        raise K.UploadError("E ve F olayları için iki farklı sütun seçin: aynı sütunun kategorileri iki aşamalı bir "
                            "sınıflama ya da ortak olasılık tablosu kurmaz.")


ROLES = (
    Role(OLAY_E, "Birinci kategorik değişken (E olayı)", "kategorik", True, (2, 4, 6, 8, 9),
         "Gözlemleri sınıflayan kategorik sütun (ör. ödeme yöntemi, teslim durumu); seçtiğiniz kategori E olayıdır.",
         levels=(2, 10), pick="E olayının kategorisi"),
    Role(OLAY_F, "İkinci kategorik değişken (F olayı)", "kategorik", True, (2, 8, 9),
         "İkinci kategorik sütun (ör. sipariş türü, hasar durumu); seçtiğiniz kategori F olayıdır.", levels=(2, 10),
         pick="F olayının kategorisi"),
)

SETTINGS = (
    Setting(ZAR, "Zar yüzü sayısı m", 4, 20, lambda data, roles: ALT_SETTINGS[ZAR],
            "Adil zarın yüz sayısı (ör. 6, 8, 12, 20); örnek uzay {1, …, m}.", steps=(1, 2, 4, 5, 6, 7)),
    Setting(EKIP, "Ekip büyüklüğü N", 2, 10, lambda data, roles: ALT_SETTINGS[EKIP],
            "Seçimin yapılacağı ekipteki kişi sayısı.", steps=(3,)),
    Setting(SECIM, "Seçilen kişi sayısı n", 1, 10, lambda data, roles: ALT_SETTINGS[SECIM],
            "Ekipten seçilen kişi sayısı; N'den büyük olamaz.", steps=(3,)),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "İki kategorik sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin ve her sütunda bir kategori seçin: "
        "seçilen kategoriler E ve F olaylarını kurar (Adım 2, 4, 6, 8, 9). Zar ve ekip adımlarının sayılarını "
        "kaydırıcılarla değiştirebilirsiniz. İki sütundan birinde değeri boş olan satırlar analizden çıkarılır."
    ),
    order_roles=(OLAY_E, OLAY_F),
    min_rows=5,
    validate=validate,
    settings=SETTINGS,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
