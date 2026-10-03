"""Konu 7 genel uygulaması: koşullu olasılık, bağımsızlık, çarpma kuralı, olasılık ağacı ve Bayes teoremi.

Ders notlarındaki adımlar (§7.1–§7.12) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Olaylar veriden
kurulur: koşul değişkeninde seçilen kategori $M$, sonuç değişkeninde seçilen kategori $S$ olayıdır (Adım 1–9).
Olasılık ağacı (Adım 7) ve Bayes hesabı (Adım 8–9) aynı verinin olasılıklarıyla kurulur: önsel olasılık koşul
kategorisinin payı, koşullu olasılık o kategoride $S$'nin payıdır. Adım 10'un temel oranı, yakalama ve yanlış alarm
olasılıkları öğrencinin seçtiği değerlerdir. Alternatif örnek kurgusal bir bankanın 800 kredi kartı başvurusudur;
"kendi verini yükle" seçeneğinde aynı adımlar öğrencinin dosyasıyla kurulur. Notlardaki uygulama (``core.labs.konu07``)
değişmez.
"""

from __future__ import annotations

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
    kesir_ayirt,
    kesir_basamak,
    kesir_esit,
    kesir_gorunur,
    kesir_isaret,
    kesir_metin,
    kesir_ortak_basamak,
    kesir_sayi,
    kesir_tex,
    md,
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
    FromCounts,
    GroupSummary,
    InlineData,
    LabSpec,
    LabStep,
    MosaicChart,
    NoteRef,
    Outcomes,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ShowFrame,
    Statistic,
    TableTarget,
    TreeDiagram,
)

TITLE = "Koşullu olasılık, bağımsızlık ve Bayes teoremini uygulamak"
KOSUL, SONUC = "kosul", "sonuc"
TEMEL, YAKALAMA, YANLIS = "temel", "yakalama", "yanlis"
NATURAL_TOTAL = 10000
"""Adım 10'un doğal frekansları için düşünülen gözlem sayısı (notlardaki gibi 10.000)."""

ALT_COUNTS = (
    ("Şube", "Onaylandı", 150), ("Şube", "Reddedildi", 100),
    ("Mobil", "Onaylandı", 180), ("Mobil", "Reddedildi", 270),
    ("İnternet", "Onaylandı", 30), ("İnternet", "Reddedildi", 70),
)
"""Kurgusal veri: bir bankanın 800 kredi kartı başvurusunun başvuru kanalı ve sonucu (sayım tablosu)."""
ALT_LABELS = {"kanal": "Başvuru kanalı", "karar": "Başvuru sonucu"}
ALT_ORDERS = {"kanal": ("Şube", "Mobil", "İnternet"), "karar": ("Onaylandı", "Reddedildi")}
ALT_PICKS = {KOSUL: "Mobil", SONUC: "Onaylandı"}
ALT_SETTINGS = {TEMEL: 1, YAKALAMA: 92, YANLIS: 3}
ALT_ALARM = {
    "text": ("Bankanın kartlarıyla yapılan işlemlerde sahte işlem ($F$) oranı düşüktür. Bir izleme sistemi sahte "
             "işlemlerde ve gerçek işlemlerin bir kısmında alarm verir ($A$)."),
    "states": ("Sahte", "Sahte değil"),
    "signals": ("Alarm", "Alarm yok"),
    "unit": "işlem",
}
STORY = (
    "Kurgusal veri: bir bankanın 800 kredi kartı başvurusunda başvuru kanalı (Şube, Mobil, İnternet) ve başvuru "
    "sonucu (Onaylandı, Reddedildi); ayrıca kart işlemlerinde bir sahtecilik alarm sistemi."
)
GENERIC_ALARM = {
    "text": ("Bir uyarı sistemi düşünün: ilgilenilen durum $F$ (ör. sahte işlem, kusurlu ürün) gözlemlerin bir "
             "kısmında vardır; sistem durum varken ve yokken farklı olasılıklarla alarm verir ($A$)."),
    "states": ("Durum var", "Durum yok"),
    "signals": ("Alarm", "Alarm yok"),
    "unit": "gözlem",
}


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _other(order: tuple[str, ...], pick: str) -> str:
    """Seçilen kategorinin tümleyeninin ağaçtaki adı: iki kategoride diğer kategori, daha fazlasında "Diğer"."""

    others = [item for item in order if item != pick]
    if len(others) == 1:
        return others[0]
    for label in ("Diğer", "Diğerleri", "Diğer kategoriler"):
        if label not in order:
            return label
    return "Diğer (seçilmeyen kategoriler)"


def _settings(case: Case) -> dict[str, int]:
    chosen = dict(ALT_SETTINGS)
    chosen.update(case.extra.get("settings") or {})
    return chosen


def _context(case: Case) -> dict:
    k_col, s_col = case.roles[KOSUL], case.roles[SONUC]
    m_pick, s_pick = case.levels[KOSUL], case.levels[SONUC]
    data = case.data.astype({k_col: str, s_col: str})
    n = len(data)
    in_m, in_s = data[k_col] == m_pick, data[s_col] == s_pick
    counts = {"m": int(in_m.sum()), "s": int(in_s.sum()), "ms": int((in_m & in_s).sum()),
              "mcs": int((~in_m & in_s).sum())}
    k_order, s_order = tuple(case.orders[k_col]), tuple(case.orders[s_col])
    taken = set(case.data.columns) | set(case.labels)
    names = {}
    for key in ("M", "S", "pay", "M_ve_S", "kosul_dali", "sonuc_dali", "dal_M", "dal_S", "p_ilk", "p_S_dal",
                "p_ikinci", "ortak", "M_ve_S_yolu", "gozlem", "kosullu", "onsel", "sonsal", "durum", "sinyal",
                "F", "A", "F_ve_A", "Fc_ve_A", "islem"):
        names[key] = free_name(key, taken)
        taken.add(names[key])
    by_category = data.groupby(k_col)[s_col].apply(lambda values: int((values == s_pick).sum()))
    sizes = data.groupby(k_col).size()
    sources = tuple((category, int(sizes.get(category, 0)), int(by_category.get(category, 0))) for category in k_order)
    p = {
        "s": Fraction(counts["s"], n), "m": Fraction(counts["m"], n), "ms": Fraction(counts["ms"], n),
        "s_m": Fraction(counts["ms"], counts["m"]), "s_mc": Fraction(counts["mcs"], n - counts["m"]),
        "m_s": Fraction(counts["ms"], counts["s"]),
    }
    return {
        "k_col": k_col, "s_col": s_col, "m_pick": m_pick, "s_pick": s_pick, "n": n, "counts": counts,
        "k_label": case.label(KOSUL), "s_label": case.label(SONUC), "k_order": k_order, "s_order": s_order,
        "m_other": _other(k_order, m_pick), "s_other": _other(s_order, s_pick), "names": names,
        "sources": sources, "p": p, "settings": _settings(case),
    }


def _digits(*values: Fraction) -> int:
    """Birlikte gösterilen olasılıkların ortak basamağı (en çoğu)."""

    return max(kesir_basamak(value) for value in values)


def _shown_digits(first: Fraction, second: Fraction) -> tuple[int, int]:
    """Karşılaştırılan iki olasılığın gösterim basamakları: her biri kendi basamağıyla (metrik ve tablo gibi); ancak bu
    basamaklarla aynı görünecek kadar yakınsa ikisi de farklı görünecek ortak basamakla (0,497506 ile 0,497512)."""

    apart = kesir_ayirt(first, second)
    if apart > _digits(first, second):
        return apart, apart
    return _digits(first), _digits(second)


def _eq_at(value: Fraction, digits: int) -> str:
    """Matematik içinde, verilen basamakla: "= 0{,}45" ya da "\\approx 0{,}51429"."""

    return f"{kesir_isaret(value, digits)} {kesir_tex(value, digits)}"


def _plain_at(value: Fraction, digits: int) -> str:
    """Düzyazıda, verilen basamakla: "= 0,45" ya da "≈ 0,51429"."""

    return f"{kesir_esit(value, digits)} {kesir_sayi(value, digits)}"


def _percent(value: Fraction, digits: int) -> str:
    """Olasılığın yüzde yazımı, metrikle aynı basamakla (olasılığın basamağı − 2): %40 ya da yaklaşık %33,33."""

    shown = value * 100
    places = max(0, digits - 2)
    text = "%" + kesir_sayi(shown, places)
    return text if kesir_isaret(shown, places) == "=" else f"yaklaşık {text}"


def _m(ctx: dict) -> str:
    return f"“{md(ctx['k_label'])}: {md(ctx['m_pick'])}”"


def _s(ctx: dict) -> str:
    return f"“{md(ctx['s_label'])}: {md(ctx['s_pick'])}”"


def _eq(value: Fraction) -> str:
    """Matematik içinde "= 0{,}45" ya da "\\approx 0{,}5143"."""

    digits = kesir_basamak(value)
    return f"{kesir_isaret(value, digits)} {kesir_tex(value, digits)}"


# --- Adımlar -------------------------------------------------------------------------------

def _step1(case: Case, ctx: dict) -> LabStep:
    names, counts, p = ctx["names"], ctx["counts"], ctx["p"]
    frame, event_m, event_s = case.frame, names["M"], names["S"]
    n, m = ctx["n"], counts["m"]
    lead = case.extra.get("read_text") or f"Dosyanızdaki {n} gözlem okunur."
    d_s, d_sm = _shown_digits(p["s"], p["s_m"])  # yakın iki oran: metrikler de farklı görünecek basamakla
    if p["s"] == p["s_m"]:
        compare = (f"Bu veride iki oran eşittir ({kesir_metin(p['s'])}); yine de farklı paydalarla hesaplanırlar ve "
                   "farklı soruların cevabıdırlar (§7.1).")
    else:
        compare = (f"Bu yüzden {kesir_metin(p['s'], d_s)} ile {kesir_metin(p['s_m'], d_sm)} aynı sorunun cevabı "
                   "değildir: biri bütün gözlemler, diğeri yalnız M'deki gözlemler içindeki paydır (§7.1).")
    return LabStep(
        number=1,
        title="Yeni bilgi paydayı değiştirir",
        note=NoteRef("7.1", objects=("Şekil 7.1",)),
        explanation=(
            f"{lead} $S$ = {_s(ctx)} ve $M$ = {_m(ctx)} olsun. $P(S)$ bütün gözlemler içinde, $P(S \\mid M)$ ise "
            "yalnız $M$'deki gözlemler içinde $S$'nin payıdır: gözlemin $M$'de olduğu öğrenilince ilgili grup "
            f"{m} gözleme daralır."
        ),
        operations=(
            *case.load,
            Event(frame, event_s, ctx["s_col"], (ctx["s_pick"],), f"S: {ctx['s_pick']}"),
            Event(frame, event_m, ctx["k_col"], (ctx["m_pick"],), f"M: {ctx['m_pick']}"),
            Statistic(frame, event_s, "count", "n_veri", "Gözlem sayısı n", decimals=0),
            Statistic(frame, event_s, "sum", "S_sayisi", "S'deki gözlem sayısı", decimals=0),
            Statistic(frame, event_m, "sum", "M_sayisi", "M'deki gözlem sayısı", decimals=0),
            Statistic(frame, event_s, "sum", "M_ve_S_sayisi", "Hem M hem S", where=(event_m, 1), decimals=0),
            Scalar("M_ve_Sc_sayisi", E.sub(E.ref("M_sayisi"), E.ref("M_ve_S_sayisi")), "M'de olup S'de olmayan",
                   decimals=0),
            Statistic(frame, event_s, "mean", "P_S", "P(S): bütün gözlemler içinde", decimals=d_s),
            Statistic(frame, event_s, "mean", "P_S_M", "P(S | M): M'deki gözlemler içinde", where=(event_m, 1),
                      decimals=d_sm),
        ),
        checks=(
            _scalar("S_sayisi", "S'deki gözlem sayısı"),
            _scalar("M_sayisi", "M'deki gözlem sayısı"),
            _scalar("M_ve_S_sayisi", "Hem M hem S"),
            _scalar("M_ve_Sc_sayisi", "M'de olup S'de olmayan"),
            _scalar("P_S", f"P(S) = {counts['s']}/{n}", d_s),
            _scalar("P_S_M", f"P(S | M) = {counts['ms']}/{m}", d_sm),
        ),
        takeaway=(f"P(S) bütün {n} gözlemi, P(S | M) yalnız M'deki {m} gözlemi payda olarak kullanır. {compare}"),
    )


def _joint_digits(case: Case, ctx: dict) -> int:
    """Ortak olasılık tablosunun basamağı: bütün hücreler ve kenar toplamları (sayı / n) bu basamakla gösterilir."""

    data = case.data.astype({ctx["k_col"]: str, ctx["s_col"]: str})
    counts = [*data.groupby([ctx["k_col"], ctx["s_col"]]).size(), *data.groupby(ctx["k_col"]).size(),
              *data.groupby(ctx["s_col"]).size()]
    return kesir_ortak_basamak(*(Fraction(int(count), ctx["n"]) for count in counts))


def _step2(case: Case, ctx: dict) -> LabStep:
    names, counts, p, n = ctx["names"], ctx["counts"], ctx["p"], ctx["n"]
    frame, k_col, s_col = case.frame, ctx["k_col"], ctx["s_col"]
    m_pick, s_pick = ctx["m_pick"], ctx["s_pick"]
    digits = ctx["joint_digits"]
    p_s_total = Fraction(n - counts["s"], n)
    return LabStep(
        number=2,
        title="Çapraz tablo: ortak ve marjinal olasılıklar",
        note=NoteRef("7.2", objects=("Tablo 7.1", "Tablo 7.2", "Şekil 7.2")),
        explanation=(
            f"“{md(ctx['k_label'])}” ve “{md(ctx['s_label'])}” sütunlarının sayıları çapraz tabloya yazılır. Her hücre "
            f"gözlem sayısına ($n = {n}$) bölününce iç hücreler **ortak olasılıklar** "
            f"($P(M \\cap S) {_eq_at(p['ms'], digits)}$), satır ve sütun toplamları **marjinal olasılıklar** "
            f"($P(M) {_eq_at(p['m'], digits)}$, $P(S) {_eq_at(p['s'], digits)}$) olur. Mozaik grafiğinde sütun "
            "genişliği marjinal olasılık, "
            "sütun içindeki yükseklik o sütundaki paydır; her parçanın alanı ortak olasılığa eşittir."
        ),
        operations=(
            CrossTab(frame, k_col, s_col, "sayilar", ctx["k_order"], ctx["s_order"], margins=True),
            Derive(frame, names["pay"], E.div(1, E.ref("n_veri")), "Her gözlemin payı 1/n"),
            CrossTab(frame, k_col, s_col, "ortak", ctx["k_order"], ctx["s_order"], margins=True, decimals=digits,
                     weights=names["pay"]),
            MosaicChart("ortak", f"{ctx['k_label']} (sütun genişliği: marjinal olasılık)", "Sütun içindeki pay",
                        "Ortak ve marjinal olasılıklar: mozaik", decimals=min(digits, 3)),
        ),
        checks=(
            Check(f"Sayılar: {m_pick} ve {s_pick}", TableTarget("sayilar", m_pick, s_pick), 0.0, 0),
            Check(f"Sayılar: {m_pick} toplamı", TableTarget("sayilar", m_pick, TOTAL), 0.0, 0),
            Check(f"Sayılar: {s_pick} toplamı", TableTarget("sayilar", TOTAL, s_pick), 0.0, 0),
            Check("Sayılar: gözlem sayısı", TableTarget("sayilar", TOTAL, TOTAL), 0.0, 0),
            Check("P(M ∩ S)", TableTarget("ortak", m_pick, s_pick), 0.0, digits),
            Check("P(M)", TableTarget("ortak", m_pick, TOTAL), 0.0, digits),
            Check("P(S)", TableTarget("ortak", TOTAL, s_pick), 0.0, digits),
            Check("Ortak olasılıkların toplamı", TableTarget("ortak", TOTAL, TOTAL), 0.0, 2),
        ),
        takeaway=(
            "İç hücreler iki değişkenin birlikte aldığı değerleri, kenarlar tek bir değişkeni gösterir; bütün ortak "
            f"olasılıkların toplamı 1'dir. Mozaikte “{md(m_pick)}” sütununun genişliği P(M) "
            f"{_plain_at(p['m'], digits)}, bu sütunda “{md(s_pick)}” parçasının yüksekliği P(S | M) "
            f"{_plain_at(p['s_m'], _digits(p['s_m']))}; parçanın alanı ikisinin çarpımıdır: P(M ∩ S) "
            f"{_plain_at(p['ms'], digits)}. S'de olmayan gözlemlerin payı P(Sᶜ) {_plain_at(p_s_total, digits)} (§7.2)."
        ),
    )


def _step3(case: Case, ctx: dict) -> LabStep:
    names, counts, p = ctx["names"], ctx["counts"], ctx["p"]
    frame, event_m, event_s = case.frame, names["M"], names["S"]
    return LabStep(
        number=3,
        title="Koşullu olasılık formülü",
        note=NoteRef("7.3"),
        explanation=(
            "Koşullu olasılık ortak olasılığın koşul olayının olasılığına bölümüdür: "
            "$P(S \\mid M) = P(M \\cap S)/P(M)$, $P(M) > 0$. Pay $M$ ile $S$'nin birlikte gerçekleştiği bölge, payda "
            "artık içinde çalıştığımız koşul olayıdır. Satır yüzdeleri tablosunun her satırı, o satırın kategorisi "
            f"verildiğinde “{md(ctx['s_label'])}” kategorilerinin koşullu olasılıklarını (yüzde olarak) verir."
        ),
        operations=(
            Derive(frame, names["M_ve_S"], E.mul(E.var(event_m), E.var(event_s)), "M ∩ S: hem M hem S"),
            Statistic(frame, names["M_ve_S"], "mean", "P_MS", "P(M ∩ S)", decimals=_digits(p["ms"])),
            Statistic(frame, event_m, "mean", "P_M", "P(M)", decimals=_digits(p["m"])),
            Scalar("P_S_M_formul", E.div(E.ref("P_MS"), E.ref("P_M")), "P(S | M) = P(M ∩ S)/P(M)",
                   decimals=_digits(p["s_m"])),
            Statistic(frame, event_s, "mean", "P_S_Mc", "P(S | Mᶜ): M dışında",
                      where=(event_m, 0), decimals=_digits(p["s_mc"])),
            CrossTab(frame, ctx["k_col"], ctx["s_col"], "kosullu", ctx["k_order"], ctx["s_order"], percent="satir",
                     margins=True, decimals=1),
        ),
        checks=(
            _scalar("P_MS", f"P(M ∩ S) = {counts['ms']}/{ctx['n']}", _digits(p["ms"])),
            _scalar("P_M", f"P(M) = {counts['m']}/{ctx['n']}", _digits(p["m"])),
            _scalar("P_S_M_formul", "P(S | M) = P(M ∩ S)/P(M)", _digits(p["s_m"])),
            _scalar("P_S_Mc", "P(S | Mᶜ)", _digits(p["s_mc"])),
            Check(f"Satır yüzdesi: {ctx['m_pick']} içinde {ctx['s_pick']}",
                  TableTarget("kosullu", ctx["m_pick"], ctx["s_pick"]), 0.0, 1),
        ),
        takeaway=(
            f"Sayılarla ({counts['ms']}/{counts['m']}) ve olasılıklarla (P(M ∩ S)/P(M)) aynı sonuç çıkar: "
            f"{kesir_metin(p['s_m'])}. M dışındaki gözlemlerde S'nin payı {kesir_metin(p['s_mc'])}. En yaygın hata "
            "paydada bütün örnek uzayı kullanmaya devam etmektir; P(S | M) sorulduğunda payda P(M)'dir (§7.3)."
        ),
    )


def _step4(case: Case, ctx: dict) -> LabStep:
    names, counts, p = ctx["names"], ctx["counts"], ctx["p"]
    frame, event_m, event_s = case.frame, names["M"], names["S"]
    digits = _digits(p["m_s"])
    denominators = (f"M'deki {counts['m']} gözlem yerine S'deki {counts['s']} gözlem" if counts["m"] != counts["s"] else
                    f"M yerine S; bu veride iki grubun büyüklüğü aynıdır ({counts['m']} gözlem)")
    if counts["ms"] == 0:
        compare = ("Bu veride M ile S'nin ortak gözlemi yoktur: iki koşullu olasılık da sıfırdır, ama yine farklı "
                   "paydalarla hesaplanır.")
    elif p["s_m"] == p["m_s"]:
        compare = (f"Bu veride iki olasılık eşittir ({kesir_metin(p['s_m'])}), çünkü P(M) = P(S): M ve S'deki gözlem "
                   "sayıları aynıdır.")
    else:
        compare = (f"M'deki gözlemlerin {_percent(p['s_m'], _digits(p['s_m']))} kadarı S'dedir; S'deki gözlemlerin ise "
                   f"{_percent(p['m_s'], digits)} kadarı M'dedir.")
    return LabStep(
        number=4,
        title="Koşulun yönü: P(S | M) ile P(M | S)",
        note=NoteRef("7.4", objects=("Şekil 7.4",)),
        explanation=(
            "Aynı iki olayda $P(S \\mid M)$ ile $P(M \\mid S)$ genellikle farklıdır. $P(S \\mid M)$, $M$'deki "
            "gözlemler içinde $S$'nin; $P(M \\mid S)$ ise $S$'deki gözlemler içinde $M$'nin payıdır. Sütun yüzdeleri "
            f"tablosu “{md(ctx['s_label'])}” verildiğinde “{md(ctx['k_label'])}” kategorilerinin koşullu "
            "olasılıklarını verir."
        ),
        operations=(
            Statistic(frame, event_m, "mean", "P_M_S", "P(M | S): S'deki gözlemler içinde", where=(event_s, 1),
                      decimals=digits),
            Scalar("yuzde_M_S", E.mul(100, E.ref("P_M_S")), "S'deki gözlemlerin M yüzdesi", decimals=max(0, digits - 2),
                   percent=True),
            CrossTab(frame, ctx["k_col"], ctx["s_col"], "sutun_yuzde", ctx["k_order"], ctx["s_order"],
                     percent="sutun", margins=True, decimals=1),
        ),
        checks=(
            _scalar("P_M_S", f"P(M | S) = {counts['ms']}/{counts['s']}", digits),
            _scalar("yuzde_M_S", "S'deki gözlemlerin yüzde kaçı M'de", max(0, digits - 2)),
            Check(f"Sütun yüzdesi: {ctx['s_pick']} içinde {ctx['m_pick']}",
                  TableTarget("sutun_yuzde", ctx["m_pick"], ctx["s_pick"]), 0.0, 1),
        ),
        takeaway=(
            f"Pay aynı ortak hücredir ({counts['ms']} gözlem), ama koşul değişince payda değişir: {denominators}. "
            f"{compare} Dikey çizginin sağındaki olay karşılaştırma grubunu belirler (§7.4)."
        ),
    )


def _step5(case: Case, ctx: dict) -> LabStep:
    p = ctx["p"]
    difference = p["s_m"] - p["s"]
    digits = kesir_ayirt(p["s"], p["s_m"], p["s_mc"])
    difference_digits = kesir_gorunur(difference)
    if difference == 0:
        verdict = ("P(S | M) = P(S): M bilgisi S'nin olasılığını değiştirmez, bu veride M ile S bağımsızdır. "
                   "Bağımsızlıkta M dışındaki gözlemlerde de oran aynıdır.")
    else:
        direction = "büyüktür" if difference > 0 else "küçüktür"
        verdict = (f"P(S | M) ({kesir_metin(p['s_m'], digits)}) P(S)'den ({kesir_metin(p['s'], digits)}) "
                   f"{direction}: M bilgisi S'nin olasılığını değiştirdiği için bu veride M ile S bağımlıdır. Veriden "
                   "hesaplanan iki oran arasındaki küçük bir fark rastlantıdan da doğabilir; farkın anlamlı olup "
                   "olmadığı istatistiksel çıkarımın konusudur.")
    return LabStep(
        number=5,
        title="Bağımsızlık kontrolü",
        note=NoteRef("7.5", objects=("Şekil 7.5",)),
        explanation=(
            "$M$ ile $S$ bağımsızsa $M$'nin gerçekleştiğini öğrenmek $S$'nin olasılığını değiştirmez: "
            "$P(S \\mid M) = P(S)$. Verideki kontrol $P(S \\mid M)$ ile $P(S)$ karşılaştırılarak yapılır; tabloya "
            "$M$ dışındaki gözlemlerdeki oran $P(S \\mid M^c)$ da eklenir."
        ),
        operations=(
            Scalar("fark_S_M", E.sub(E.ref("P_S_M"), E.ref("P_S")), "P(S | M) − P(S)", decimals=difference_digits),
            ScalarTable(
                (
                    ("P(S): bütün gözlemler", E.ref("P_S")),
                    ("P(S | M): M'deki gözlemler", E.ref("P_S_M")),
                    ("P(S | Mᶜ): M dışındaki gözlemler", E.ref("P_S_Mc")),
                ),
                "bagimsizlik",
                decimals=digits,
            ),
        ),
        checks=(
            _scalar("fark_S_M", "P(S | M) − P(S)", difference_digits),
        ),
        takeaway=(f"{verdict} Bağımsız olaylar birlikte gerçekleşebilir; bağımsızlık ayrıklık demek değildir "
                  "(§7.5, §7.6)."),
    )


def _step6(case: Case, ctx: dict) -> LabStep:
    p = ctx["p"]
    product = p["m"] * p["s"]
    digits_ms = digits_product = kesir_ayirt(p["ms"], product)
    chain = (f"${kesir_tex(p['m'])} \\times {kesir_tex(p['s_m'])} {_eq_at(p['ms'], digits_ms)}$"
             if all(kesir_isaret(value, kesir_basamak(value)) == "=" for value in (p["m"], p["s_m"])) else
             f"$P(M)P(S \\mid M) {_eq_at(p['ms'], digits_ms)}$")
    if p["ms"] == product:
        verdict = "P(M)P(S) ile P(M ∩ S) eşittir: çarpım eşitliği sağlandığı için bu veride M ile S bağımsızdır"
    else:
        relation = "büyüktür" if p["ms"] > product else "küçüktür"
        tendency = ("M ile S birlikte, bağımsızlıkta beklenenden daha sık görülür" if p["ms"] > product else
                    "M ile S birlikte, bağımsızlıkta beklenenden daha seyrek görülür")
        verdict = (f"P(M ∩ S) ({kesir_metin(p['ms'], digits_ms)}) bağımsızlık altındaki çarpımdan "
                   f"({kesir_metin(product, digits_ms)}) {relation}: {tendency}; çarpım eşitliği sağlanmadığı için M "
                   "ile S bağımsız değildir")
    return LabStep(
        number=6,
        title="Çarpma kuralı",
        note=NoteRef("7.7", objects=("Şekil 7.7",)),
        explanation=(
            "Koşullu olasılık formülü yeniden düzenlenince $P(M \\cap S) = P(M)P(S \\mid M)$ elde edilir: "
            f"{chain}. Bağımsız olaylarda kural $P(M \\cap S) = P(M)P(S)$ biçimine sadeleşir; bu eşitlik "
            "bağımsızlığı denetlemek için de kullanılabilir."
        ),
        operations=(
            Scalar("P_MS_carpim", E.mul(E.ref("P_M"), E.ref("P_S_M")), "P(M ∩ S) = P(M)P(S | M)",
                   decimals=digits_ms),
            Scalar("carpim_MS", E.mul(E.ref("P_M"), E.ref("P_S")), "Bağımsızlık altında: P(M)P(S)",
                   decimals=digits_product),
        ),
        checks=(
            _scalar("P_MS_carpim", "P(M ∩ S) = P(M)P(S | M)", digits_ms),
            _scalar("carpim_MS", "P(M)P(S)", digits_product),
        ),
        takeaway=f"{verdict} (§7.7).",
    )


def _tree_operations(case: Case, ctx: dict) -> tuple:
    names = ctx["names"]
    first, second = names["kosul_dali"], names["sonuc_dali"]
    branch_m, branch_s = names["dal_M"], names["dal_S"]
    p_first, p_s_branch, p_second = names["p_ilk"], names["p_S_dal"], names["p_ikinci"]
    one = E.const(1)
    return (
        Outcomes("agac", ((first, (ctx["m_pick"], ctx["m_other"])), (second, (ctx["s_pick"], ctx["s_other"]))),
                 "Ağacın yolları: önce koşul (M ya da Mᶜ), sonra sonuç (S ya da Sᶜ)"),
        Event("agac", branch_m, first, (ctx["m_pick"],), "İlk aşamada M dalı"),
        Event("agac", branch_s, second, (ctx["s_pick"],), "İkinci aşamada S dalı"),
        Derive("agac", p_first, E.add(E.mul(E.var(branch_m), E.ref("P_M")),
                                      E.mul(E.sub(one, E.var(branch_m)), E.sub(one, E.ref("P_M")))),
               "İlk dalın olasılığı: P(M) ya da P(Mᶜ) = 1 − P(M)"),
        Derive("agac", p_s_branch, E.add(E.mul(E.var(branch_m), E.ref("P_S_M")),
                                         E.mul(E.sub(one, E.var(branch_m)), E.ref("P_S_Mc"))),
               "Dalda S'nin koşullu olasılığı: P(S | M) ya da P(S | Mᶜ)"),
        Derive("agac", p_second, E.add(E.mul(E.var(branch_s), E.var(p_s_branch)),
                                       E.mul(E.sub(one, E.var(branch_s)), E.sub(one, E.var(p_s_branch)))),
               "İkinci dalın koşullu olasılığı: S dalında P(S | ·), Sᶜ dalında 1 − P(S | ·)"),
        Derive("agac", names["ortak"], E.mul(E.var(p_first), E.var(p_second)),
               "Yolun ortak olasılığı: dal olasılıkları çarpılır"),
    )


def _tree_digits(ctx: dict) -> dict[str, int]:
    """Ağacın, yol tablosunun (Adım 7–8) ve Bayes tablosunun (Adım 9) ortak basamakları; aynı olasılık iki tabloda
    aynı basamakla görünür. İlk dal: P(M), P(Mᶜ) ve önseller; ikinci dal: dört koşullu olasılık ve kaynaklardaki
    P(S | ·); yollar: dört ortak olasılık ve kaynakların ortak olasılıkları. Tam yarımda bir basamak daha."""

    p, n = ctx["p"], ctx["n"]
    priors = [Fraction(size, n) for _, size, _ in ctx["sources"]]
    likelihoods = [Fraction(hits, size) for _, size, hits in ctx["sources"]]
    joints = [Fraction(hits, n) for _, _, hits in ctx["sources"]]
    paths = (p["ms"], p["m"] - p["ms"], p["s"] - p["ms"], 1 - p["m"] - p["s"] + p["ms"])
    second = (p["s_m"], 1 - p["s_m"], p["s_mc"], 1 - p["s_mc"])
    return {"first": kesir_ortak_basamak(p["m"], 1 - p["m"], *priors),
            "second": kesir_ortak_basamak(*second, *likelihoods),
            "branch": kesir_ortak_basamak(p["m"], 1 - p["m"], *second),
            "paths": kesir_ortak_basamak(*paths, *joints)}


def _step7(case: Case, ctx: dict) -> LabStep:
    names, p = ctx["names"], ctx["p"]
    first, second = names["kosul_dali"], names["sonuc_dali"]
    paths = (p["ms"], p["m"] - p["ms"], p["s"] - p["ms"], 1 - p["m"] - p["s"] + p["ms"])
    digits = _tree_digits(ctx)
    branch_digits, tree_digits = digits["branch"], digits["paths"]
    path_digits = [_digits(value) for value in paths]
    root = case.extra.get("root", "Gözlem")
    sum_text = (f"P(S) = P(M ∩ S) + P(Mᶜ ∩ S) {kesir_esit(p['s'], kesir_basamak(p['s']))} {kesir_sayi(p['s'])}")
    return LabStep(
        number=7,
        title="Olasılık ağacı",
        note=NoteRef("7.8", objects=("Şekil 7.8",)),
        explanation=(
            f"İlk aşamada gözlem ya $M$ ({_m(ctx)}) ya $M^c$ (“{md(ctx['m_other'])}”) dalındadır: $P(M) "
            f"{_eq(p['m'])}$. İkinci aşamada $S$ (“{md(ctx['s_pick'])}”) ya da $S^c$ (“{md(ctx['s_other'])}”) gelir; "
            f"dal olasılıkları ilk dala göre koşulludur: $P(S \\mid M) {_eq(p['s_m'])}$, $P(S \\mid M^c) "
            f"{_eq(p['s_mc'])}$. Ağaçta her tam yol bir ortak sonuçtur: aynı yol üzerindeki olasılıklar çarpılır, aynı "
            "sonuca ulaşan farklı yolların ortak olasılıkları toplanır."
        ),
        operations=(
            *_tree_operations(case, ctx),
            TreeDiagram("agac", first, second, names["p_ilk"], names["p_ikinci"], root,
                        "Koşul ve sonuç: iki aşamalı olasılık ağacı", decimals=tree_digits,
                        branch_decimals=branch_digits),
            ShowFrame("agac", (first, second, names["ortak"]), "Dört yolun ortak olasılıkları",
                      decimals=((names["ortak"], tree_digits),)),
            Statistic("agac", names["ortak"], "sum", "yol_toplami", "Dört ortak olasılığın toplamı", decimals=0),
            Statistic("agac", names["ortak"], "sum", "P_S_agac", "P(S): S ile biten yolların toplamı",
                      where=(names["dal_S"], 1), decimals=_digits(p["s"])),
        ),
        checks=(
            Check("P(M ∩ S): birinci yol", CellTarget("agac", names["ortak"], 1), 0.0, path_digits[0]),
            Check("P(M ∩ Sᶜ): ikinci yol", CellTarget("agac", names["ortak"], 2), 0.0, path_digits[1]),
            Check("P(Mᶜ ∩ S): üçüncü yol", CellTarget("agac", names["ortak"], 3), 0.0, path_digits[2]),
            Check("P(Mᶜ ∩ Sᶜ): dördüncü yol", CellTarget("agac", names["ortak"], 4), 0.0, path_digits[3]),
            _scalar("yol_toplami", "Dört ortak olasılığın toplamı"),
            _scalar("P_S_agac", "P(S) = P(M ∩ S) + P(Mᶜ ∩ S)", _digits(p["s"])),
        ),
        takeaway=(
            "S iki yoldan gelir: M ve S ile Mᶜ ve S. Yollar birbirini dışladığı için olasılıklar toplanır: "
            f"{sum_text}; bu, Adım 1'de doğrudan sayılan orandır. Bu iki işlem, çarpma ve toplama, Bayes teoreminde "
            "yeniden kullanılır (§7.8)."
        ),
    )


def _step8(case: Case, ctx: dict) -> LabStep:
    names, p = ctx["names"], ctx["p"]
    first, second = names["kosul_dali"], names["sonuc_dali"]
    p_mcs = p["s"] - p["ms"]
    d_prior, digits = _shown_digits(p["m"], p["m_s"])  # önsel ve sonsal; metrik sonsalın basamağıyla
    tree = _tree_digits(ctx)
    d_sm, d_smc = _shown_digits(p["s_m"], p["s_mc"])
    likelihoods = (f"P(S | M) {_plain_at(p['s_m'], d_sm)}", f"P(S | Mᶜ) {_plain_at(p['s_mc'], d_smc)}")
    if p["m_s"] > p["m"]:
        change = ("Sonsal önselden büyüktür: S, M'de M dışındakilere göre daha sık görülür "
                  f"({likelihoods[0]} > {likelihoods[1]}).")
    elif p["m_s"] < p["m"]:
        change = ("Sonsal önselden küçüktür: S, M'de M dışındakilere göre daha seyrek görülür "
                  f"({likelihoods[0]} < {likelihoods[1]}).")
    else:
        change = "Sonsal önsele eşittir: S, M'de ve M dışında aynı oranda görülür; S bilgisi M hakkında bilgi vermez."
    return LabStep(
        number=8,
        title="Bayes teoremi: S gözlendiğinde M'nin olasılığı",
        note=NoteRef("7.10", objects=("Şekil 7.10",)),
        explanation=(
            f"Önsel olasılık $P(M) {_eq_at(p['m'], d_prior)}$: gözlem hakkında başka bilgi yokken $M$'de olma "
            "olasılığıdır. Gözlemin $S$'de olduğu öğrenilince $P(M \\mid S)$ aranır. Önce $S$ ile biten iki yolun "
            f"ortak olasılıkları bulunur ($P(M \\cap S) {_eq_at(p['ms'], tree['paths'])}$ ve $P(M^c \\cap S) "
            f"{_eq_at(p_mcs, tree['paths'])}$), sonra $M$ yolu bu iki yolun toplamı içinde yeniden "
            "oranlanır: $P(M \\mid S) = P(M \\cap S)/P(S)$."
        ),
        operations=(
            Derive("agac", names["M_ve_S_yolu"], E.mul(E.var(names["dal_M"]), E.var(names["dal_S"])),
                   "M ∩ S yolu: M dalı ve S dalı"),
            ShowFrame("agac", (first, second, names["p_ilk"], names["p_ikinci"], names["ortak"]),
                      "Ağacın yolları: önsel, koşullu ve ortak olasılıklar",
                      decimals=((names["p_ilk"], tree["first"]), (names["p_ikinci"], tree["second"]),
                                (names["ortak"], tree["paths"]))),
            Statistic("agac", names["ortak"], "sum", "P_MS_agac", "P(M ∩ S): M ve S yolu",
                      where=(names["M_ve_S_yolu"], 1), decimals=tree["paths"]),
            Scalar("P_M_bilinen_S", E.div(E.ref("P_MS_agac"), E.ref("P_S_agac")), "P(M | S) = P(M ∩ S)/P(S)",
                   decimals=digits),
        ),
        checks=(
            _scalar("P_MS_agac", "P(M ∩ S): M ve S yolu", tree["paths"]),
            _scalar("P_M_bilinen_S", "P(M | S) = P(M ∩ S)/P(S)", digits),
        ),
        takeaway=(
            f"Önsel P(M) {_plain_at(p['m'], d_prior)} iken S bilgisiyle sonsal P(M | S) {_plain_at(p['m_s'], digits)} "
            f"olur; bu, Adım 4'te doğrudan sayılan orandır. {change} Bayes hesabı S ile biten iki dalı toplamları "
            "içinde yeniden oranlar (§7.10)."
        ),
    )


def _step9(case: Case, ctx: dict) -> LabStep:
    names, p, n = ctx["names"], ctx["p"], ctx["n"]
    frame, k_col, event_s = case.frame, ctx["k_col"], names["S"]
    sources = ctx["sources"]
    priors = [Fraction(size, n) for _, size, _ in sources]
    likelihoods = [Fraction(hits, size) for _, size, hits in sources]
    joints = [Fraction(hits, n) for _, _, hits in sources]
    posteriors = [Fraction(hits, ctx["counts"]["s"]) for _, _, hits in sources]
    digits = min(4, _digits(*priors, *likelihoods, *joints, *posteriors))
    tree = _tree_digits(ctx)  # Adım 8'deki yol tablosuyla aynı basamaklar
    gozlem, kosullu, onsel, ortak, sonsal = (names[key] for key in ("gozlem", "kosullu", "onsel", "ortak", "sonsal"))
    checks = [
        Check(f"Sonsal P({category} | S)", CellTarget("bayes", sonsal, index), 0.0, _digits(posterior))
        for index, ((category, _, _), posterior) in enumerate(zip(sources, posteriors), start=1)
    ]
    top = max(posteriors)
    leaders = [f"“{md(category)}”" for (category, _, _), posterior in zip(sources, posteriors) if posterior == top]
    leader_text = (f"S bilindiğinde sonsal olasılığı en büyük kaynak: {leaders[0]}" if len(leaders) == 1 else
                   "S bilindiğinde sonsal olasılığı en büyük kaynaklar: " + ", ".join(leaders[:-1]) + " ve "
                   + leaders[-1])
    return LabStep(
        number=9,
        title="Bayes hesabı tabloyla",
        note=NoteRef("7.11", objects=("Tablo 7.4",)),
        explanation=(
            f"Kategori sayısı arttıkça tablo daha düzenlidir. “{md(ctx['k_label'])}” sütununun her kategorisi bir "
            "kaynaktır: (1) kaynakları ve önsel olasılıkları (kategorinin payı) yazın, (2) her kaynak için "
            "$S$'nin koşullu olasılığını yazın, (3) ikisini çarparak ortak olasılıkları bulun, (4) ortak olasılıkları "
            "kendi toplamlarına bölerek sonsal olasılıkları elde edin."
        ),
        operations=(
            GroupSummary(frame, k_col, ((gozlem, event_s, "count"), (kosullu, event_s, "mean")), "bayes",
                         ctx["k_order"], decimals=digits, as_frame=True),
            Derive("bayes", onsel, E.div(E.var(gozlem), E.ref("n_veri")), "Önsel = kategorideki gözlem / n"),
            Derive("bayes", ortak, E.mul(E.var(onsel), E.var(kosullu)), "Ortak = önsel × koşullu"),
            Statistic("bayes", ortak, "sum", "P_S_tablo", "P(S): ortak olasılıkların toplamı",
                      decimals=_digits(p["s"])),
            Derive("bayes", sonsal, E.div(E.var(ortak), E.ref("P_S_tablo")), "Sonsal = ortak / P(S)"),
            ShowFrame("bayes", (k_col, onsel, kosullu, ortak, sonsal), "Bayes tablosu",
                      decimals=((onsel, tree["first"]), (kosullu, tree["second"]), (ortak, tree["paths"]),
                                (sonsal, kesir_ortak_basamak(*posteriors)))),
            Statistic("bayes", onsel, "sum", "onsel_toplami", "Önsel olasılıkların toplamı", decimals=2),
            Statistic("bayes", sonsal, "sum", "sonsal_toplami", "Sonsal olasılıkların toplamı", decimals=2),
        ),
        checks=(
            *checks,
            _scalar("P_S_tablo", "P(S)", _digits(p["s"])),
            _scalar("onsel_toplami", "Önsel toplamı", 2),
            _scalar("sonsal_toplami", "Sonsal toplamı", 2),
        ),
        takeaway=(
            "Tablo, ağaçtaki iki işlemi sütunlara çevirir: ortak sütunu yol çarpımlarıdır ve toplamı P(S)'dir; sonsal "
            "sütunu ortak olasılıkların P(S) içindeki payıdır ve toplamı 1'dir. Sonsal sütunu, Adım 4'teki sütun "
            f"yüzdelerinin olasılık hâlidir. {leader_text} (§7.11)."
        ),
    )


def _alarm(case: Case) -> dict:
    return case.extra.get("alarm") or GENERIC_ALARM


def _step10(case: Case, ctx: dict) -> LabStep:
    names = ctx["names"]
    settings = ctx["settings"]
    alarm = _alarm(case)
    state_yes, state_no = alarm["states"]
    signal_yes, signal_no = alarm["signals"]
    unit = alarm["unit"]
    base, hit, false = (Fraction(settings[key], 100) for key in (TEMEL, YAKALAMA, YANLIS))
    p_fa, p_fca = base * hit, (1 - base) * false
    p_a = p_fa + p_fca
    posterior = p_fa / p_a
    true_alarms, false_alarms = int(p_fa * NATURAL_TOTAL), int(p_fca * NATURAL_TOTAL)
    total_alarms = true_alarms + false_alarms
    durum, sinyal, onsel, kosullu, ortak = (names[key] for key in ("durum", "sinyal", "onsel", "kosullu", "ortak"))
    event_f, event_a, both, false_both, count = (names[key] for key in ("F", "A", "F_ve_A", "Fc_ve_A", "islem"))
    paths = (
        (state_yes, signal_yes, float(base), float(hit)),
        (state_yes, signal_no, float(base), float(1 - hit)),
        (state_no, signal_yes, float(1 - base), float(false)),
        (state_no, signal_no, float(1 - base), float(1 - false)),
    )
    post_digits = kesir_basamak(posterior, 3, 3)
    group_no = int((1 - base) * NATURAL_TOTAL)
    if false_alarms > true_alarms and false < hit:  # bu durumda “durum yok” grubu zorunlu olarak daha kalabalıktır
        crowd = (f"“{md(state_no)}” grubu daha kalabalık olduğu için ({group_no} {unit}) yanlış alarmlar "
                 f"({false_alarms}) gerçek alarmları ({true_alarms}) sayıca geçer: durum yokken alarm olasılığı durum "
                 "varkenkinden küçük olsa da kalabalık bir grupta çok sayıda alarm üretir.")
    elif false_alarms > true_alarms:
        crowd = (f"Yanlış alarmlar ({false_alarms}) gerçek alarmları ({true_alarms}) sayıca geçer: durum yokken alarm "
                 "olasılığı durum varkenkinden küçük değildir, yani alarm durumu ayırt etmez.")
    elif false_alarms == true_alarms:
        crowd = f"Yanlış alarm sayısı ({false_alarms}) gerçek alarm sayısına eşittir: alarmların yarısı yanlıştır."
    elif false_alarms == 0:
        crowd = "Durum yokken hiç alarm verilmediği için (P(A | Fᶜ) = 0) her alarm gerçektir."
    else:
        crowd = (f"Bu değerlerle gerçek alarmlar ({true_alarms}) yanlış alarmlardan ({false_alarms}) çoktur; temel "
                 "oran küçüldükçe ya da yanlış alarm olasılığı büyüdükçe yanlış alarmların payı artar ve bu sıra "
                 "tersine dönebilir.")
    return LabStep(
        number=10,
        title="Bütünleştirici uygulama: alarm ve temel oran",
        note=NoteRef("7.12", objects=("Tablo 7.5", "Şekil 7.12")),
        explanation=(
            f"{alarm['text']} Temel oran $P(F) {_eq(base)}$; alarm, durum varken $P(A \\mid F) {_eq(hit)}$, durum "
            f"yokken $P(A \\mid F^c) {_eq(false)}$ olasılıkla verilir. Alarm verildiğinde durumun gerçekten var olma "
            "olasılığı $P(F \\mid A) = P(F \\cap A)/P(A)$'dır. Doğal frekans tablosu aynı hesabı 10.000 "
            f"{unit} üzerinden sayılarla gösterir."
        ),
        operations=(
            InlineData("alarm", (durum, sinyal, onsel, kosullu), paths, "Yollar: gerçek durum ve alarm"),
            Derive("alarm", ortak, E.mul(E.var(onsel), E.var(kosullu)), "Yolun ortak olasılığı"),
            Event("alarm", event_f, durum, (state_yes,), f"F: {state_yes}"),
            Event("alarm", event_a, sinyal, (signal_yes,), f"A: {signal_yes}"),
            Derive("alarm", both, E.mul(E.var(event_f), E.var(event_a)), "F ∩ A: durum var ve alarm"),
            Derive("alarm", false_both, E.mul(E.sub(1, E.var(event_f)), E.var(event_a)),
                   "Fᶜ ∩ A: durum yok ve alarm"),
            Statistic("alarm", ortak, "sum", "P_FA", "P(F ∩ A)", where=(both, 1), decimals=_digits(p_fa)),
            Statistic("alarm", ortak, "sum", "P_FcA", "P(Fᶜ ∩ A)", where=(false_both, 1), decimals=_digits(p_fca)),
            Statistic("alarm", ortak, "sum", "P_A_alarm", "P(A): toplam alarm olasılığı", where=(event_a, 1),
                      decimals=_digits(p_a)),
            Scalar("P_F_bilinen_A", E.div(E.ref("P_FA"), E.ref("P_A_alarm")), "P(F | A) = P(F ∩ A)/P(A)",
                   decimals=post_digits),
            Derive("alarm", count, E.mul(NATURAL_TOTAL, E.var(ortak)), "10.000 gözlemde beklenen sayı"),
            CrossTab("alarm", durum, sinyal, "dogal", (state_yes, state_no), (signal_yes, signal_no), margins=True,
                     decimals=0, weights=count),
            BarChart("dogal", signal_yes, "Gerçek durum", "Alarm sayısı",
                     f"Alarm alan {total_alarms} {unit}: gerçek alarm ve yanlış alarm"),
            Statistic("alarm", count, "sum", "dogru_alarm", "Durum var ve alarm", where=(both, 1), decimals=0),
            Statistic("alarm", count, "sum", "toplam_alarm", "Alarm alan", where=(event_a, 1), decimals=0),
            Scalar("dogal_oran", E.div(E.ref("dogru_alarm"), E.ref("toplam_alarm")),
                   f"{true_alarms}/{total_alarms}", decimals=post_digits),
        ),
        checks=(
            _scalar("P_FA", "P(F ∩ A) = P(F)P(A | F)", _digits(p_fa)),
            _scalar("P_FcA", "P(Fᶜ ∩ A) = P(Fᶜ)P(A | Fᶜ)", _digits(p_fca)),
            _scalar("P_A_alarm", "P(A) = P(F ∩ A) + P(Fᶜ ∩ A)", _digits(p_a)),
            _scalar("P_F_bilinen_A", "P(F | A) = P(F ∩ A)/P(A)", post_digits),
            Check("Doğal frekans: durum var ve alarm", TableTarget("dogal", state_yes, signal_yes), 0.0, 0),
            Check("Doğal frekans: durum yok ve alarm", TableTarget("dogal", state_no, signal_yes), 0.0, 0),
            Check("Doğal frekans: alarm alan", TableTarget("dogal", TOTAL, signal_yes), 0.0, 0),
            Check("Doğal frekans: toplam", TableTarget("dogal", TOTAL, TOTAL), 0.0, 0),
            _scalar("dogal_oran", f"{true_alarms}/{total_alarms}", post_digits),
        ),
        takeaway=(
            f"Alarm verildiğinde durumun gerçekten var olma olasılığı: P(F | A) "
            f"{kesir_esit(posterior, post_digits)} {kesir_sayi(posterior, post_digits)}. {crowd} Bayes teoremi hem "
            "alarmın doğruluğunu hem temel oranı birlikte hesaba katar (§7.12)."
        ),
    )


def build(case: Case) -> LabSpec:
    """Konu 7 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    ctx = _context(case)
    ctx["joint_digits"] = _joint_digits(case, ctx)
    steps = (_step1(case, ctx), _step2(case, ctx), _step3(case, ctx), _step4(case, ctx), _step5(case, ctx),
             _step6(case, ctx), _step7(case, ctx), _step8(case, ctx), _step9(case, ctx), _step10(case, ctx))
    names = ctx["names"]
    labels = dict(case.labels)
    for key, text in (("M", "M"), ("S", "S"), ("pay", "Gözlemin payı (1/n)"), ("M_ve_S", "M ∩ S"),
                      ("kosul_dali", "Koşul dalı"), ("sonuc_dali", "Sonuç dalı"), ("dal_M", "M dalı"),
                      ("dal_S", "S dalı"), ("p_ilk", "İlk dalın olasılığı"), ("p_S_dal", "Dalda P(S | ·)"),
                      ("p_ikinci", "İkinci dalın olasılığı"), ("ortak", "Ortak olasılık"),
                      ("M_ve_S_yolu", "M ∩ S yolu"),
                      ("gozlem", "Gözlem sayısı"), ("kosullu", "Koşullu olasılık"), ("onsel", "Önsel olasılık"),
                      ("sonsal", "Sonsal olasılık"), ("durum", "Gerçek durum"), ("sinyal", "Alarm durumu"),
                      ("F", "F"), ("A", "A"), ("F_ve_A", "F ∩ A"), ("Fc_ve_A", "Fᶜ ∩ A"),
                      ("islem", "10.000 gözlemde sayı")):
        labels.setdefault(names[key], text)
    spec = LabSpec(
        topic_key="konu07",
        title=TITLE,
        note_section="7",
        steps=steps,
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def _alternative_frame() -> pd.DataFrame:
    rows = [(kanal, karar) for kanal, karar, count in ALT_COUNTS for _ in range(count)]
    return pd.DataFrame(rows, columns=["kanal", "karar"])


def alternative_case() -> Case:
    return Case(
        source="alternatif",
        load=(FromCounts("basvurular", ("kanal", "karar"), ALT_COUNTS,
                         "Kurgusal veri: 800 kredi kartı başvurusunun kanalı ve sonucu"),),
        frame="basvurular",
        data=_alternative_frame(),
        roles={KOSUL: "kanal", SONUC: "karar"},
        labels=ALT_LABELS,
        levels=dict(ALT_PICKS),
        orders=ALT_ORDERS,
        unit="başvuru",
        extra={
            "settings": dict(ALT_SETTINGS),
            "alarm": ALT_ALARM,
            "root": "Başvuru",
            "read_text": "Bankanın 800 kredi kartı başvurusu başvuru kanalı ve sonucuyla kaydedilmiştir.",
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin 800 başvurusu, sabit bir karışık sırayla (sayılar sıradan bağımsızdır)."""

    frame = _alternative_frame()
    order = np.random.default_rng(217).permutation(len(frame))
    frame = frame.iloc[order].reset_index(drop=True)
    return frame.rename(columns=ALT_LABELS)


def validate(case: Case) -> None:
    """Koşul ve sonuç farklı sütunlardan seçilir (aynı sütunun iki kategorisi ayrık olaylar olurdu)."""

    if case.roles[KOSUL] == case.roles[SONUC]:
        raise K.UploadError("Koşul ve sonuç için iki farklı sütun seçin: aynı sütunun kategorileri bir çapraz tablo ya "
                            "da koşullu olasılık kurmaz.")


ROLES = (
    Role(KOSUL, "Koşul değişkeni (M olayı)", "kategorik", True, (1, 2, 3, 4, 5, 6, 7, 8, 9),
         "Gözlemleri gruplara ayıran kategorik sütun (ör. cihaz türü, başvuru kanalı); seçtiğiniz kategori M "
         "olayıdır.", levels=(2, 10), pick="M olayının kategorisi"),
    Role(SONUC, "Sonuç değişkeni (S olayı)", "kategorik", True, (1, 2, 3, 4, 5, 6, 7, 8, 9),
         "Sonucu gösteren kategorik sütun (ör. satın alma, başvuru sonucu); seçtiğiniz kategori S olayıdır.",
         levels=(2, 10), pick="S olayının kategorisi"),
)

SETTINGS = (
    Setting(TEMEL, "Temel oran P(F), %", 1, 50, lambda data, roles: ALT_SETTINGS[TEMEL],
            "Durumun (ör. sahte işlem) bütün gözlemler içindeki yüzdesi.", steps=(10,)),
    Setting(YAKALAMA, "Yakalama P(A | F), %", 50, 100, lambda data, roles: ALT_SETTINGS[YAKALAMA],
            "Durum varken alarm verilme yüzdesi.", steps=(10,)),
    Setting(YANLIS, "Yanlış alarm P(A | Fᶜ), %", 0, 50, lambda data, roles: ALT_SETTINGS[YANLIS],
            "Durum yokken alarm verilme yüzdesi.", steps=(10,)),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "İki kategorik sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin ve her sütunda bir kategori seçin: "
        "koşul değişkenindeki kategori M, sonuç değişkenindeki kategori S olayını kurar (Adım 1–9). Adım 10'un temel "
        "oranını, yakalama ve yanlış alarm yüzdelerini kaydırıcılarla değiştirebilirsiniz. İki sütundan birinde değeri "
        "boş olan satırlar analizden çıkarılır."
    ),
    order_roles=(KOSUL, SONUC),
    min_rows=5,
    validate=validate,
    settings=SETTINGS,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
