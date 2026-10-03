"""Konu 5 genel uygulaması: değişkenlik, dağılımın şekli ve iki değişken arasındaki ilişki.

Ders notlarındaki adımlar (§5.1–§5.13) aynı numaralarla, verisi değiştirilebilir biçimde yazılır. Notlarda her adımın
kendi küçük veri seti vardır; genel uygulamada yayılım ölçüleri tek bir sayısal değişken üzerinde hesaplanır. İki grubun
karşılaştırması (Adım 1–2) tam iki kategorili bir grup sütunuyla, değişim katsayılarının karşılaştırması (Adım 5) ile
kovaryans ve korelasyon (Adım 10–11) ikinci bir sayısal sütunla kurulur. Alternatif örnek kurgusal bir kargo verisidir;
"kendi verini yükle" seçeneğinde aynı adımlar öğrencinin dosyasıyla kurulur. Notlardaki uygulama (``core.labs.konu05``)
değişmez.

Çeyrekler Konu 4'teki ders kuralıyla bulunur: L_p = (p/100)(n + 1), tam sayı değilse doğrusal ara değer. Varyans,
standart sapma ve kovaryansın paydası n − 1'dir. Metindeki sayılar ve "=" ile "≈" ayrımı verinin kesin ondalık
değerlerinden kurulur (Konu 4'teki yardımcılar); aykırı değer ve Chebyshev sayımları ise uygulamanın kayan noktalı
hesabıyla aynı kuraldan gelir, böylece metin tabloyla aynı gözlemleri sayar.

Kayan noktalı hesabın iki dil arasında son basamakta ayrılabildiği iki yerde ölçülü bir pay bırakılır: sapmaların
toplamı gibi değeri sıfır olan sonuçlar verinin büyüklüğüne göre güvenilir basamakla yazılır (``_safe_digits``) ve
x̄ ± ks aralığına tam sınırdaki gözlem içeride sayılır (göreli ``CHEBYSHEV_SLACK`` payı).
"""

from __future__ import annotations

import math
from decimal import Context, Decimal, localcontext
from functools import cache

import numpy as np
import pandas as pd

from core.labs import expr as E
from core.labs import kendi_veri as K
from core.labs import tables as T
from core.labs.ornek import (
    Case,
    CustomLab,
    Role,
    TopicVariants,
    free_name,
    kesin,
    kesin_esit,
    kesin_yuvarla,
    liste,
    md,
    ondalik,
    sayilar,
    with_app_values,
    yarim_basamak,
)
from core.labs.ornek_konu03 import data_decimals
from core.labs.ornek_konu04 import (  # Konu 4'ün kesin ondalık yardımcıları (aynı yazım kuralları)
    _EXACT,
    _about,
    _axis,
    _exact_data,
    _exact_digits,
    _math,
    _mean_digits,
    _percentile,
    _spread_plot,
    _term,
)
from core.labs.spec import (
    BoxPlot,
    BoxSummary,
    CellTarget,
    Check,
    CompleteCases,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    NoteRef,
    PairStatistic,
    Percentile,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ScatterPlot,
    ShowFrame,
    Statistic,
    Subset,
    TableTarget,
)

TITLE = "Değişkenlik, dağılım ve ilişki ölçülerini hesaplamak"
SAYISAL, GRUP, IKINCI = "sayisal", "grup", "ikinci"
GROUP_FRAMES = ("grup1", "grup2")
PAIR_FRAME = "veri_xy"
EPS = 2.0 ** -52
"""Kayan noktalı sayının göreli hassasiyeti (IEEE 754 çift duyarlık)."""
CHEBYSHEV_SLACK = 1e-9
"""x̄ ± ks sınırına göreli pay: tam sınırdaki gözlem (|x − x̄| = ks) iki dilde de içeride sayılır."""
SPREAD = 1e-7
"""En küçük ile en büyük değerin farkı, değerlerin büyüklüğünün en az bu katı olmalı: sapmalar en az yedi anlamlı
basamakla hesaplanır ve iki dilin kayan noktalı sonuçları gösterilen basamakta aynı kalır."""
MAX_LISTED = 10
"""Aykırı değer adayları metinde bu sayıya kadar tek tek yazılır."""
_WIDE = Context(prec=200)
"""Kesin karşılaştırmalar için geniş bağlam (60 basamaklı iki sayının çarpımı yuvarlanmaz)."""
EMPIRICAL = ((2, Decimal("0.95")), (3, Decimal("0.997")))
"""Ampirik kuralın yaklaşık oranları (notlardaki %95 ve %99,7)."""

ALT_ROWS = (
    ("Kuzey", 41, 11), ("Güney", 26, 6), ("Kuzey", 36, 9), ("Güney", 58, 15), ("Kuzey", 45, 10),
    ("Güney", 12, 4), ("Kuzey", 33, 11), ("Güney", 37, 7), ("Kuzey", 40, 10), ("Güney", 135, 30),
    ("Kuzey", 38, 9), ("Güney", 22, 6), ("Kuzey", 47, 12), ("Güney", 42, 10), ("Kuzey", 39, 9),
    ("Güney", 18, 8), ("Kuzey", 44, 11), ("Güney", 50, 11), ("Kuzey", 35, 10), ("Güney", 14, 5),
    ("Kuzey", 42, 8), ("Güney", 36, 10), ("Kuzey", 40, 10), ("Güney", 30, 7),
)
"""Kurgusal veri: bir kargo firmasının iki deposundan gönderilen 24 paketin deposu, teslimat mesafesi (km) ve teslim
süresi (saat), gönderi sırasıyla. İki deponun ortalama mesafesi aynıdır (40 km); Güney deposunun mesafeleri çok daha
yayılmıştır ve bir paket 135 km uzağa gider."""
ALT_LABELS = {
    "depo": "Depo",
    "mesafe": "Teslimat mesafesi (km)",
    "sure": "Teslim süresi (saat)",
}
STORY = (
    "Kurgusal veri: bir kargo firmasının iki deposundan (Kuzey, Güney) gönderilen 24 paketin teslimat mesafesi (km) "
    "ve teslim süresi (saat)."
)


# --- Yardımcılar -------------------------------------------------------------------------

def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _missing(step: int, title: str, note: str, roles: str, operations: tuple = ()) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note), operations=operations,
                   explanation=f"Bu adım için yukarıdaki veri panelinden şu rol için sütun seçin: {roles}.")


def _blocked(step: int, title: str, note: str, reason: str) -> LabStep:
    return LabStep(number=step, title=title, note=NoteRef(note), explanation=reason)


def _safe_digits(digits: int, bound: float, value: Decimal | None = None) -> int:
    """Gösterim (ve kontrol) basamağı, iki dilin ve kesin hesabın kayan noktalı sonuçlar arasındaki olası farkın
    (``bound``) içinde kalacak kadar sınırlanır: 10⁻ᵈ ≥ 5·bound, yani iki sonucun farkı (en çok 2·bound) toleransın
    (0,5·10⁻ᵈ) beşte dördünü aşmaz. Olağan verilerde basamak değişmez. Sınırlanan basamakta kesin değer iki gösterimin
    tam ortasındaysa (−19504,875 iki basamakla) bir basamak daha az yazılır: kayan noktalı değer iki yöne de
    yuvarlanabilir, metin ile ekran ayrışırdı."""

    if bound > 0:
        digits = max(0, min(digits, math.floor(-math.log10(5 * bound))))
    if value is not None and digits > 0 and yarim_basamak(value, digits) != digits:
        digits -= 1
    return digits


def _common_digits(values, digits: int, bound: float) -> int:
    """Birlikte gösterilen kesin değerlerin (ör. Q₁ ve Q₃) ortak basamağı: ``_safe_digits`` sınırı ve her değer için
    yarım nokta kuralı (biri için bir basamak azalınca diğeri yeniden denetlenir)."""

    digits = _safe_digits(digits, bound)
    while digits > 0 and any(yarim_basamak(value, digits) != digits for value in values):
        digits -= 1
    return digits


def _checkable(bound: float, value) -> bool:
    """Bu değer iki dilde güvenle karşılaştırılabilir mi: basamak sıfıra inse bile olası fark (2·bound) toleransın
    içinde kalmalı (mutlak 0,5'in beşte dördü ya da göreli 10⁻¹² payı). Çok büyük değerli verilerde bazı kontroller
    (ör. sapmaların toplamı) bu yüzden atlanır; değer yine hesaplanır ve gösterilir."""

    return 5 * bound <= 1 or 2 * bound <= 0.99e-12 * abs(float(value))


def _check(name: str, label: str, digits: int, bound: float, value) -> Check | None:
    return _scalar(name, label, digits) if _checkable(bound, value) else None


def _kept(*checks) -> tuple[Check, ...]:
    return tuple(check for check in checks if check is not None)


def _share_digits(count: int, n: int) -> int:
    """Oranın gösterim basamağı: en çok 3 basamakla tam yazılabiliyorsa tam (23/25 = 0,92), değilse 3."""

    share = Decimal(count) / Decimal(n)
    exact = 0 if share == share.to_integral_value() else -share.normalize().as_tuple().exponent
    return min(3, max(0, exact))


def _percent_about(value: Decimal, digits: int = 1) -> str:
    return _about(value * 100, digits, "%")


# --- Ortak hesaplar ------------------------------------------------------------------------

def _moments(exact: list[Decimal]) -> dict:
    """Kesin ortalama, kareli sapmalar toplamı, varyans ve standart sapma. Kareli sapmalar toplamı n·Σx² − (Σx)²
    özdeşliğiyle bölmesiz hesaplanır: ortalama sonsuz ondalıklı olsa bile (1/3 gibi) sonlu sonuçlar tam kalır."""

    n = len(exact)
    with localcontext(_EXACT):
        total = sum(exact, Decimal(0))
        scaled = n * sum((value * value for value in exact), Decimal(0)) - total * total  # n·Σ(x − x̄)²
        mean = total / n
        squares = scaled / n
        variance = scaled / (n * (n - 1)) if n > 1 else Decimal(0)
        std = variance.sqrt()
    return {"total": total, "scaled": scaled, "mean": mean, "squares": squares, "variance": variance, "std": std}


def _noise(n: int, top: float) -> float:
    """Toplamla bulunan bir ortalamanın (ve bir sapmanın) iki dil arasındaki olası kayan nokta farkı: (log₂ n + 4)·ε·
    en büyük mutlak değer."""

    return (math.log2(max(n, 2)) + 4) * EPS * top


def _std_bounds(n: int, noise: float, max_dev: float, std: Decimal, top: float) -> tuple[float, float, float]:
    """Kareli sapmalar toplamının, varyansın ve standart sapmanın kayan noktalı hesaplarındaki olası fark. Ortalamanın
    farkı (``noise``) sapmaların toplamı sıfır olduğu için kareler toplamına yalnız n·fark² kadar yansır; verinin
    ikili gösterimi (her değerde en çok ε·en büyük değer/2) n·en büyük sapma·ε·en büyük değer, toplamanın yuvarlaması
    (log₂ n + 3)·ε·Σ(x − x̄)² kadar."""

    s = float(std)
    squares = n * max_dev * EPS * top + (math.log2(max(n, 2)) + 3) * EPS * (n - 1) * s * s + n * noise * noise
    variance = squares / max(n - 1, 1)
    return squares, variance, (variance / (2 * s) if s > 0 else math.sqrt(variance))


def _check_bounds(n: int, noise: float, std: Decimal) -> tuple[float, float, float]:
    """Kareli sapmalar toplamı, varyans ve standart sapma için iki dilin sonuçları arasındaki olası fark (kontroller
    için). İki dil aynı ikili sayıları okur; ayrılan yalnız ortalamanın farkı (n·fark², sapmaların toplamı sıfır) ve
    toplamanın yuvarlamasıdır (göreli)."""

    s = float(std)
    squares = (math.log2(max(n, 2)) + 3) * EPS * (n - 1) * s * s + n * noise * noise
    variance = squares / max(n - 1, 1)
    return squares, variance, (variance / (2 * s) if s > 0 else math.sqrt(variance))


def _z_bound(noise: float, std_bound: float, std: Decimal, z: Decimal) -> float:
    """z = (x − x̄)/s için olası fark: payın farkı ``noise``, paydanın farkı ``std_bound``."""

    s = float(std)
    return (noise + abs(float(z)) * std_bound) / s + 4 * EPS * abs(float(z))


def _too_close(values: pd.Series) -> bool:
    """Değerler birbirinden farklı ama büyüklüklerine göre çok yakın mı (``SPREAD``): sapmalar güvenilir basamakla
    hesaplanamaz."""

    low, high = float(values.min()), float(values.max())
    return 0 < high - low < SPREAD * max(abs(low), abs(high))


def _context(case: Case) -> dict:
    x = case.roles[SAYISAL]
    values = case.data[x].astype(float)
    n = len(values)
    d = data_decimals(values)
    xs = _exact_data(values, d)
    ordered = sorted(xs)
    moments = _moments(xs)
    mean, std, variance = moments["mean"], moments["std"], moments["variance"]
    with localcontext(_EXACT):
        deviations = [value - mean for value in xs]
    top = float(np.abs(values.to_numpy()).max())
    noise = _noise(n, top)  # bir sapmanın iki dil arasındaki olası kayan nokta farkı
    max_dev = float(max(abs(value) for value in deviations))
    squares_bound, variance_bound, std_bound = _std_bounds(n, noise, max_dev, std, top)
    squares_check, variance_check, std_check = _check_bounds(n, noise, std)
    taken = set(case.data.columns) | set(case.labels)
    names = {}
    for key in ("sapma", "sapma_kare", "z", "aykiri", "icinde_2", "icinde_3", "carpim"):
        names[key] = free_name(key, taken)
        taken.add(names[key])
    return {
        "x": x, "values": values, "n": n, "d": d, "label": case.label(SAYISAL), "xs": xs, "ordered": ordered,
        "total": moments["total"], "mean": mean, "deviations": deviations, "squares": moments["squares"],
        "variance": variance, "std": std, "noise": noise, "top": top, "max_dev": max_dev,
        "squares_bound": squares_bound, "variance_bound": variance_bound, "std_bound": std_bound,
        "squares_check": squares_check, "variance_check": variance_check, "std_check": std_check,
        "scaled": moments["scaled"],
        "mean_digits": _safe_digits(_mean_digits(mean, d), noise, mean),
        "std_digits": _safe_digits(_mean_digits(std, d), std_bound, std),
        "variance_digits": _safe_digits(_mean_digits(variance, d), variance_bound, variance),
        "low": ordered[0], "high": ordered[-1], "low_f": float(values.min()), "high_f": float(values.max()),
        "names": names,
    }


def _groups(case: Case, ctx: dict) -> dict | None:
    """Adım 1, 2, 4, 6 ve 9'un iki grubu: kategori adları, gözlem sayıları, kesin ölçüler ve gösterim basamakları
    (gruptaki değerlerin büyüklüğüne göre güvenilir basamakla sınırlı)."""

    if not case.has(GRUP):
        return None
    x, g, d = ctx["x"], case.roles[GRUP], ctx["d"]
    order = tuple(case.orders[g])
    data = case.data.dropna(subset=[g])
    result = {"column": g, "label": case.label(GRUP), "order": order, "skipped": len(case.data) - len(data),
              "items": []}
    for level, frame in zip(order, GROUP_FRAMES):
        part = data.loc[data[g].astype(str) == level, x].astype(float)
        exact = _exact_data(part, d)
        count = len(exact)
        moments = _moments(exact)
        mean, std = moments["mean"], moments["std"]
        top = float(np.abs(part.to_numpy()).max())
        noise = _noise(count, top)
        with localcontext(_EXACT):
            max_dev = float(max(abs(value - mean) for value in exact))
        _, _, std_bound = _std_bounds(count, noise, max_dev, std, top)
        _, _, std_check = _check_bounds(count, noise, std)
        result["items"].append({
            "level": level, "frame": frame, "n": count, "values": part, "exact": exact, "mean": mean, "std": std,
            "low": min(exact), "high": max(exact), "noise": noise, "std_bound": std_bound, "std_check": std_check,
            "mean_digits": _safe_digits(_mean_digits(mean, d), noise, mean),
            "std_digits": _safe_digits(_mean_digits(std, d), std_bound, std),
        })
    return result


def _pair(case: Case, ctx: dict) -> dict | None:
    """Adım 5, 10 ve 11'in iki sayısal değişkeni: ikinci sütunda değeri olan gözlemler.

    ``problem``: kovaryans ve korelasyon hesaplanmaz (üçten az gözlem; değerler büyüklüklerine göre çok yakın).
    ``constant``: bir sütunun bu gözlemlerdeki bütün değerleri aynı; kovaryans sıfırdır, korelasyon tanımsızdır."""

    if not case.has(IKINCI):
        return None
    x, y = ctx["x"], case.roles[IKINCI]
    data = case.data.dropna(subset=[x, y]).reset_index(drop=True)
    if len(data) == len(case.data):
        frame, load = case.frame, ()
    else:
        frame = PAIR_FRAME
        load = (CompleteCases(PAIR_FRAME, case.frame, (x, y),
                              "İki sayısal sütunda da değeri olan gözlemler"),)
    xv, yv = data[x].astype(float), data[y].astype(float)
    dx, dy = data_decimals(xv), data_decimals(yv)
    exact_x, exact_y = _exact_data(xv, dx), _exact_data(yv, dy)
    n = len(data)
    result = {"y": y, "label": case.label(IKINCI), "frame": frame, "load": load, "n": n, "skipped": len(case.data) - n,
              "xv": xv, "yv": yv, "dx": dx, "dy": dy}
    if n < 3:
        values = f"yalnız {n} gözlemin değeri var" if n else "değeri olan gözlem yok"
        result["reason"] = f"ikinci sütunda {values}"
        result["problem"] = (f"İkinci sayısal sütunda {values}; kovaryans ve korelasyon için en az üç gözlem "
                             "gerekir.")
        return result
    for values, label in ((yv, case.label(IKINCI)), (xv, ctx["label"])):
        if _too_close(values):
            result["reason"] = f"“{md(label)}” sütunundaki değerler bu gözlemlerde büyüklüklerine göre birbirine çok yakın"
            result["problem"] = (f"“{md(label)}” sütunundaki değerler bu gözlemlerde büyüklüklerine göre birbirine "
                                 "çok yakın; kovaryans ve korelasyon güvenilir basamakla hesaplanamaz. Değerlerden "
                                 "ortak bir sayı çıkarın ya da birimi değiştirin.")
            return result
    if xv.nunique() < 2 or yv.nunique() < 2:
        which = case.label(IKINCI) if yv.nunique() < 2 else ctx["label"]
        result["constant"] = (f"“{md(which)}” sütununda bu gözlemlerin bütün değerleri aynı; standart sapması sıfır "
                              "olduğu için korelasyon tanımsızdır.")
    mx, my = _moments(exact_x), _moments(exact_y)
    with localcontext(_EXACT):
        sx, sy = mx["total"], my["total"]
        cross = n * sum((a * b for a, b in zip(exact_x, exact_y)), Decimal(0)) - sx * sy  # n·Σ(x − x̄)(y − ȳ)
        products = cross / n
        cov = cross / (n * (n - 1))
        if mx["scaled"] > 0 and my["scaled"] > 0:
            with localcontext(_WIDE):  # çarpımlar yuvarlanmadan: tam doğrusal ilişkide r tam olarak ±1
                line = cross * cross == mx["scaled"] * my["scaled"]
            corr = Decimal(1 if cross > 0 else -1) if line else cross / (mx["scaled"] * my["scaled"]).sqrt()
        else:
            corr = Decimal(0)
        mean_x, mean_y = mx["mean"], my["mean"]
        max_dx = float(max(abs(value - mean_x) for value in exact_x))
        max_dy = float(max(abs(value - mean_y) for value in exact_y))
    top_x, top_y = float(np.abs(xv.to_numpy()).max()), float(np.abs(yv.to_numpy()).max())
    noise_x, noise_y = _noise(n, top_x), _noise(n, top_y)
    _, _, std_x_bound = _std_bounds(n, noise_x, max_dx, mx["std"], top_x)
    _, _, std_y_bound = _std_bounds(n, noise_y, max_dy, my["std"], top_y)
    _, _, std_x_check = _check_bounds(n, noise_x, mx["std"])
    _, _, std_y_check = _check_bounds(n, noise_y, my["std"])
    # Ortalamaların farkı (sapmaların toplamı sıfır) çarpımlar toplamına ikinci derecede yansır; verinin ikili
    # gösterimi ve toplamanın yuvarlaması birinci derecede.
    cov_bound = (n * (max_dx * EPS * top_y + max_dy * EPS * top_x) / 2
                 + (math.log2(n) + 3) * EPS * n * max_dx * max_dy + n * noise_x * noise_y) / (n - 1)
    cov_check = ((math.log2(n) + 3) * EPS * n * max_dx * max_dy + n * noise_x * noise_y) / (n - 1)
    result.update({
        "mean_x": mean_x, "mean_y": mean_y, "cov": cov, "std_x": mx["std"], "std_y": my["std"], "corr": corr,
        "products": products, "noise_x": noise_x, "noise_y": noise_y, "std_x_bound": std_x_bound,
        "std_y_bound": std_y_bound, "cov_bound": cov_bound, "scaled_y": my["scaled"], "total_y": my["total"],
        "std_x_check": std_x_check, "std_y_check": std_y_check, "cov_check": cov_check,
        "digits_x": _safe_digits(_mean_digits(mean_x, dx), noise_x, mean_x),
        "digits_y": _safe_digits(_mean_digits(mean_y, dy), noise_y, mean_y),
        "cov_digits": _safe_digits(_mean_digits(cov, max(dx, dy)), cov_bound, cov),
        "products_digits": _safe_digits(_mean_digits(products, max(dx, dy)), cov_bound * (n - 1), products),
        "std_x_digits": _safe_digits(_mean_digits(mx["std"], dx), std_x_bound, mx["std"]),
        "std_y_digits": _safe_digits(_mean_digits(my["std"], dy), std_y_bound, my["std"]),
    })
    if "constant" not in result:
        s_x, s_y = float(mx["std"]), float(my["std"])
        corr_bound = (cov_bound / (s_x * s_y) + abs(float(corr)) * (std_x_bound / s_x + std_y_bound / s_y)
                      + 4 * EPS)
        result["corr_digits"] = _safe_digits(max(2, _mean_digits(corr, 1)), corr_bound, corr)
        result["corr_check"] = (cov_check / (s_x * s_y) + abs(float(corr)) * (std_x_check / s_x + std_y_check / s_y)
                                + 4 * EPS)
    return result


# --- Adımlar -------------------------------------------------------------------------------

def _read_text(case: Case, ctx: dict) -> str:
    return case.extra.get("read_text") or f"“{md(ctx['label'])}” sütunundaki {ctx['n']} değer okunur."


def _step1(case: Case, ctx: dict, groups: dict | None) -> LabStep:
    title, note = "Aynı merkez, farklı yayılım", "5.1"
    intro = _read_text(case, ctx)
    if groups is None:
        return _missing(1, title, note, "“Grup sütunu (iki kategorili)”, ör. tedarikçi ya da şube",
                        operations=case.load)
    x, d, label = ctx["x"], ctx["d"], ctx["label"]
    first, second = groups["items"]
    axis = _axis(ctx["low_f"], ctx["high_f"])
    operations = list(case.load)
    checks = []
    for item in groups["items"]:
        operations.append(Subset(item["frame"], case.frame, groups["column"], item["level"], f"{item['level']} grubu"))
    for index, item in enumerate(groups["items"], start=1):
        operations.append(Statistic(item["frame"], x, "mean", f"ortalama_{index}", f"Ortalama · {item['level']}",
                                    decimals=item["mean_digits"]))
        checks.append(_check(f"ortalama_{index}", f"{item['level']}: ortalama", item["mean_digits"], item["noise"],
                             item["mean"]))
    for index, item in enumerate(groups["items"], start=1):
        span = f"{ondalik(item['low'], d)}–{ondalik(item['high'], d)} arasında"
        operations.append(_spread_plot(case, item["frame"], x, label, f"{item['level']}: {span}",
                                       ((f"ortalama_{index}", "Ortalama"),), axis, item["n"], ctx["low_f"],
                                       ctx["high_f"]))
    means = [f"{md(item['level'])} grubunda {item['n']} gözlem, ortalama $\\bar{{x}} "
             f"{kesin_esit(item['mean'], item['mean_digits'])} {_math(item['mean'], item['mean_digits'])}$"
             for item in groups["items"]]
    skipped = (f" Grup sütunu boş olan {groups['skipped']} gözlem bu adımda kullanılmaz." if groups["skipped"]
               else "")
    if first["mean"] == second["mean"]:
        shown = _about(first["mean"], max(first["mean_digits"], second["mean_digits"]))
        takeaway = (f"İki grubun ortalaması da {shown}: “ortalama {shown}” bilgisi iki grubu ayırmaz. Fark "
                    "gözlemlerin merkez çevresinde nasıl dağıldığındadır.")
    else:
        takeaway = ("Ortalamalar farklıdır; ama ortalamalar eşit olsaydı bile gözlemler merkez çevresinde çok farklı "
                    "dağılabilirdi. Ortalama yayılım hakkında bilgi vermez.")
    return LabStep(
        number=1,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"{intro} “{md(groups['label'])}” sütununun iki grubu karşılaştırılır: {'; '.join(means)}.{skipped} "
            "Grafiklerde yatay eksen aynıdır; böylece iki grubun yayılımı doğrudan karşılaştırılır."
        ),
        operations=tuple(operations),
        checks=_kept(*checks),
        takeaway=f"{takeaway} Bir veri setini özetlerken merkez ve yayılım birlikte raporlanır (§5.1).",
    )


def _step2(case: Case, ctx: dict, groups: dict | None) -> LabStep:
    title, note = "Değişim aralığı", "5.2"
    if groups is None:
        return _missing(2, title, note, "“Grup sütunu (iki kategorili)”, ör. tedarikçi ya da şube")
    x, d = ctx["x"], ctx["d"]
    operations, checks, parts, ranges = [], [], [], []
    for index, item in enumerate(groups["items"], start=1):
        frame, level = item["frame"], item["level"]
        operations += [
            Statistic(frame, x, "max", f"en_buyuk_{index}", f"En büyük · {level}", decimals=d),
            Statistic(frame, x, "min", f"en_kucuk_{index}", f"En küçük · {level}", decimals=d),
            Scalar(f"aralik_{index}", E.sub(E.ref(f"en_buyuk_{index}"), E.ref(f"en_kucuk_{index}")),
                   f"R · {level}", decimals=d),
        ]
        checks.append(_scalar(f"aralik_{index}", f"{level}: değişim aralığı R", d))
        with localcontext(_EXACT):
            span = item["high"] - item["low"]
        ranges.append(span)
        parts.append(f"{md(level)}: $R = {_math(item['high'], d)} - {_term(item['low'], d)} = {_math(span, d)}$")
    first, second = groups["items"]
    if ranges[0] == ranges[1]:
        compare = "İki grubun değişim aralığı aynıdır."
    else:
        wide = first if ranges[0] > ranges[1] else second
        compare = f"{md(wide['level'])} grubunun gözlemleri daha geniş bir aralığa yayılır."
    return LabStep(
        number=2,
        title=title,
        note=NoteRef(note),
        explanation=(
            "Değişim aralığı en büyük ve en küçük gözlem arasındaki farktır: $R = x_{\\max} - x_{\\min}$. Yalnız iki "
            f"gözlemi kullanır. {'; '.join(parts)}."
        ),
        operations=tuple(operations),
        checks=_kept(*checks),
        takeaway=(
            f"{compare} Ancak değişim aralığı yalnız iki uç gözleme dayanır; tek bir çok büyük değer onu belirgin "
            "biçimde büyütebilir (§5.2). Adım 8'de uç gözlemleri IQR ile belirleyeceğiz."
        ),
    )


def _step3(case: Case, ctx: dict) -> LabStep:
    x, n, d, names = ctx["x"], ctx["n"], ctx["d"], ctx["names"]
    mean, digits = ctx["mean"], ctx["mean_digits"]
    first, deviation = ctx["xs"][0], ctx["deviations"][0]
    noise = ctx["noise"]
    dev_digits = _safe_digits(digits, noise, deviation)
    square = deviation * deviation
    square_bound = 2 * float(abs(deviation)) * noise + noise * noise
    square_digits = _safe_digits(_mean_digits(square, d), square_bound, square)
    max_dev = ctx["max_dev"]
    sum_bound = n * noise + (math.log2(max(n, 2)) + 1) * EPS * n * max_dev
    sum_digits = _safe_digits(dev_digits, sum_bound)
    squares, variance = ctx["squares"], ctx["variance"]
    squares_bound = ctx["squares_bound"]
    squares_digits = _safe_digits(_mean_digits(squares, d), squares_bound, squares)
    # Çok büyük değerlerde bazı sonuçlar iki dilde birkaç birim ayrılabilir: bunlar kontrol edilmez (bkz. _checkable).
    skipped = [text for text, bound, value in (("ilk gözlemin sapması", noise, deviation),
                                                ("ilk gözlemin kareli sapması", square_bound, square),
                                                ("sapmaların toplamı", sum_bound, 0))
               if not _checkable(bound, value)]
    large = ("" if not skipped else
             " Bu verideki değerler çok büyük olduğundan kayan noktalı hesap bu adımda tam kısımda bile ayrılabilir "
             f"(Python ile R arasında da); bu yüzden {liste(skipped)} kontrol edilmez.")
    noisy_sum = "sapmaların toplamı" in skipped
    if noisy_sum:  # ekrandaki toplam kayan nokta gürültüsü olarak okunsun (ör. 1,52; "2" değil)
        sum_digits = max(sum_digits, 2)
    sum_text = (" Bu verideki değerler çok büyük olduğundan kayan noktalı hesapta sapmaların toplamı 0 yerine "
                "birkaç birimlik bir sayı olarak görünebilir; matematiksel değeri yine 0'dır." if noisy_sum else "")
    variance_digits = ctx["variance_digits"]
    # Kareli sapmalar toplamı yuvarlanmışsa bölümün sonucu da "≈" ile yazılır (yazılan sayılarla eşitlik tam değil).
    last = "=" if kesin_esit(squares, squares_digits) == "=" == kesin_esit(variance, variance_digits) else "\\approx"
    sapma, kare = names["sapma"], names["sapma_kare"]
    return LabStep(
        number=3,
        title="Ortalamadan sapmalar ve varyans",
        note=NoteRef("5.3"),
        explanation=(
            f"“{md(ctx['label'])}” sütunundaki {n} gözlemin ortalaması $\\bar{{x}} {kesin_esit(mean, digits)} "
            f"{_math(mean, digits)}$. Her gözlemin sapması $x_i - \\bar{{x}}$, kareli sapması "
            "$(x_i - \\bar{x})^2$'dir; "
            f"ilk gözlem için ${_math(first, d)} - {_term(mean, digits)} {kesin_esit(deviation, dev_digits)} "
            f"{_math(deviation, dev_digits)}$. Örneklem varyansı kareli sapmalar toplamının $n - 1$'e bölümüdür: "
            f"$s^2 = \\sum (x_i - \\bar{{x}})^2 / (n - 1) {kesin_esit(squares, squares_digits)} "
            f"{_math(squares, squares_digits)}/({n} - 1) {last} {_math(variance, variance_digits)}$.{sum_text}"
        ),
        operations=(
            Statistic(case.frame, x, "mean", "ortalama", "Ortalama x̄", decimals=digits),
            Derive(case.frame, sapma, E.sub(E.var(x), E.ref("ortalama")), "Sapma xᵢ − x̄"),
            Derive(case.frame, kare, E.power(E.var(sapma), 2), "Kareli sapma (xᵢ − x̄)²"),
            ShowFrame(case.frame, (x, sapma, kare), "Gözlemler, sapmalar ve kareli sapmalar"),
            Statistic(case.frame, sapma, "sum", "sapma_toplami", "Sapmaların toplamı", decimals=sum_digits),
            Statistic(case.frame, kare, "sum", "kare_toplami", "Kareli sapmalar toplamı", decimals=squares_digits),
            Statistic(case.frame, x, "count", "n", "Gözlem sayısı n", decimals=0),
            Scalar("varyans", E.div(E.ref("kare_toplami"), E.sub(E.ref("n"), 1)), "Varyans s²",
                   decimals=variance_digits),
            Statistic(case.frame, x, "var", "varyans_yazilim", "Yazılımla varyans",
                      decimals=variance_digits),
        ),
        checks=_kept(
            _check("ortalama", "Ortalama x̄", digits, noise, mean),
            Check("İlk gözlemin sapması", CellTarget(case.frame, sapma, 1), 0.0, dev_digits)
            if _checkable(noise, deviation) else None,
            Check("İlk gözlemin kareli sapması", CellTarget(case.frame, kare, 1), 0.0, square_digits)
            if _checkable(square_bound, square) else None,
            _check("sapma_toplami", "Sapmaların toplamı", sum_digits, sum_bound, 0),
            _check("kare_toplami", "Kareli sapmalar toplamı", squares_digits, ctx["squares_check"], squares),
            _check("varyans", "Örneklem varyansı s²", variance_digits, ctx["variance_check"], variance),
            _check("varyans_yazilim", "Yazılımla varyans", variance_digits, ctx["variance_check"], variance),
        ),
        code_note=(
            "pandas'ın var() ve R'nin var() fonksiyonları örneklem varyansını verir (payda n − 1); numpy'nin np.var "
            "fonksiyonu ise varsayılan olarak n'ye böler, örneklem varyansı için ddof=1 yazılmalıdır. Kayan noktalı "
            "hesapta sapmaların toplamı tam 0 yerine çok küçük bir sayı (ör. 1e-15) olarak görünebilir; matematiksel "
            f"değeri 0'dır.{large}"
        ),
        takeaway=(
            "Sapmaların toplamı her veri setinde sıfırdır; pozitif ve negatif sapmalar birbirini götürür. Varyans bu "
            "yüzden kareli sapmaları kullanır. Birimi özgün birimin karesidir (§5.3)."
        ),
    )


def _ratio_text(big: dict, small: dict) -> str | None:
    """İki grubun standart sapmalarının oranı (büyük / küçük); gösterilen oran 1 ise ``None`` (neredeyse eşit)."""

    with localcontext(_EXACT):
        ratio = big["std"] / small["std"]
    digits = 1 if ratio >= 10 else 2
    if ondalik(ratio, digits) == "1":
        return None
    return (f"{md(big['level'])} grubunun standart sapması {md(small['level'])} grubununkinin "
            f"{_about(ratio, digits)} katıdır")


def _step4(case: Case, ctx: dict, groups: dict | None) -> LabStep:
    x = ctx["x"]
    std, digits = ctx["std"], ctx["std_digits"]
    variance, variance_digits = ctx["variance"], ctx["variance_digits"]
    operations = [Scalar("std_sapma", E.sqrt(E.ref("varyans")), "Standart sapma s", decimals=digits)]
    checks = [_check("std_sapma", "Standart sapma s", digits, ctx["std_check"], std)]
    text = ""
    takeaway = ("Standart sapma özgün ölçü birimindedir; gözlemlerin ortalama çevresinde ne kadar yayıldığını aynı "
                "birimle anlatır (§5.4).")
    if groups is not None:
        shown = []
        for index, item in enumerate(groups["items"], start=1):
            operations.append(Statistic(item["frame"], x, "std", f"std_{index}", f"s · {item['level']}",
                                        decimals=item["std_digits"]))
            checks.append(_check(f"std_{index}", f"{item['level']}: s", item["std_digits"], item["std_check"],
                                 item["std"]))
            shown.append(f"{md(item['level'])}: $s {kesin_esit(item['std'], item['std_digits'])} "
                         f"{_math(item['std'], item['std_digits'])}$")
        first, second = groups["items"]
        text = f" İki grubun standart sapmaları: {'; '.join(shown)}."
        if first["std"] == second["std"]:
            compare = "İki grubun standart sapması aynıdır."
        elif min(first["std"], second["std"]) == 0:
            still = first if first["std"] == 0 else second
            compare = (f"{md(still['level'])} grubunda bütün gözlemler aynı değerdedir (s = 0); diğer grubun "
                       "gözlemleri yayılmıştır.")
        else:
            big, small = (first, second) if first["std"] > second["std"] else (second, first)
            ratio = _ratio_text(big, small)
            compare = (f"{ratio}: bu grubun gözlemleri daha değişkendir." if ratio else
                       "İki grubun standart sapmaları birbirine çok yakındır (oranları yaklaşık 1).")
        takeaway = f"{compare} {takeaway}"
    return LabStep(
        number=4,
        title="Standart sapma",
        note=NoteRef("5.4"),
        explanation=(
            "Standart sapma varyansın pozitif kareköküdür: $s = \\sqrt{s^2}$. Önceki adımda $s^2 "
            f"{kesin_esit(variance, variance_digits)} {_math(variance, variance_digits)}$ olduğundan $s "
            f"{kesin_esit(std, digits)} {_math(std, digits)}$.{text}"
        ),
        operations=tuple(operations),
        checks=_kept(*checks),
        takeaway=takeaway,
    )


def _cv_bound(cv: Decimal, mean: Decimal, std: Decimal, noise: float, std_bound: float) -> float:
    """CV = 100·s/x̄ için olası kayan nokta farkı (paydanın ve payın farklarından)."""

    m, s = abs(float(mean)), float(std)
    return 100 * (std_bound / m + s * noise / (m * m)) + 4 * EPS * abs(float(cv))


def _cv_usable(values: pd.Series, mean: Decimal) -> bool:
    """Değişim katsayısı yalnız negatif olmayan ve ortalaması pozitif değişkende anlamlıdır (notlar §5.5)."""

    return bool(mean > 0 and float(values.min()) >= 0)


def _cv_pair(pair: dict | None) -> bool:
    """Adım 5 ikinci değişkenin CV'sini hesaplar mı (ve iki sütunun tam gözlemlerini o adımda seçer mi)."""

    return pair is not None and "problem" not in pair and _cv_usable(pair["yv"], pair["mean_y"])


def _step5(case: Case, ctx: dict, pair: dict | None) -> LabStep:
    title, note = "Değişim katsayısı", "5.5"
    label = ctx["label"]
    mean, std = ctx["mean"], ctx["std"]
    usable_x = _cv_usable(ctx["values"], mean)
    second = pair is not None and "problem" not in pair
    usable_y = _cv_pair(pair)
    operations, checks, parts, notes = [], [], [], []
    values = {}
    if usable_x:
        with localcontext(_EXACT):
            cv = std / mean * 100
        digits = _safe_digits(_mean_digits(cv, 1), _cv_bound(cv, mean, std, ctx["noise"], ctx["std_bound"]), cv)
        values["x"] = (cv, digits)
        operations.append(Scalar("cv_x", E.mul(E.div(E.ref("std_sapma"), E.ref("ortalama")), 100),
                                 f"CV · {label}", decimals=digits, percent=True))
        checks.append(_check("cv_x", f"{label}: CV (%)", digits,
                             _cv_bound(cv, mean, std, ctx["noise"], ctx["std_check"]), cv))
        parts.append(f"x = “{md(label)}”: $CV = s/\\bar{{x}} \\times 100 {kesin_esit(cv, digits)} "
                     f"\\%{_math(cv, digits)}$")
    else:
        notes.append(f"“{md(label)}” sütununda negatif değer var ya da ortalama pozitif değil; CV bu değişken için "
                     "anlamlı değildir.")
    if usable_y:
        y_label, frame, y = pair["label"], pair["frame"], pair["y"]
        with localcontext(_EXACT):
            cv_y = pair["std_y"] / pair["mean_y"] * 100
        bound = _cv_bound(cv_y, pair["mean_y"], pair["std_y"], pair["noise_y"], pair["std_y_bound"])
        digits_y = _safe_digits(_mean_digits(cv_y, 1), bound, cv_y)
        values["y"] = (cv_y, digits_y)
        operations = list(pair["load"]) + operations + [
            Statistic(frame, y, "mean", "ortalama_y", "Ortalama ȳ", decimals=pair["digits_y"]),
            Statistic(frame, y, "std", "std_y", "Standart sapma s_y", decimals=pair["std_y_digits"]),
            Scalar("cv_y", E.mul(E.div(E.ref("std_y"), E.ref("ortalama_y")), 100), f"CV · {y_label}",
                   decimals=digits_y, percent=True),
        ]
        checks.append(_check("cv_y", f"{y_label}: CV (%)", digits_y,
                             _cv_bound(cv_y, pair["mean_y"], pair["std_y"], pair["noise_y"], pair["std_y_check"]),
                             cv_y))
        used = f" (ikinci sütunda değeri olan {pair['n']} gözlem)" if pair["skipped"] else ""
        parts.append(f"y = “{md(y_label)}”{used}: $CV = s_y/\\bar{{y}} \\times 100 {kesin_esit(cv_y, digits_y)} "
                     f"\\%{_math(cv_y, digits_y)}$")
    elif second:
        notes.append(f"“{md(pair['label'])}” sütununda negatif değer var ya da ortalama pozitif değil; CV bu değişken "
                     "için anlamlı değildir.")
    elif pair is not None:
        notes.append(f"İkinci sütunun CV'si bu adımda hesaplanmaz: {pair['reason']}.")
    if not operations:
        return _blocked(5, title, note, " ".join(notes) + " CV, sıfırın anlamlı olduğu oran ölçekli ve pozitif "
                                                         "değişkenlerde kullanılır (§5.5).")
    lead = ("Ortalamaları ve ölçü birimleri farklı iki değişkenin yayılımı standart sapmayla değil, ortalamaya göre "
            "karşılaştırılır: $CV = (s/\\bar{x}) \\times 100$.")
    if pair is None:
        lead += " İkinci bir sayısal sütun seçerseniz iki değişkenin CV'si karşılaştırılır."
    if len(values) == 2:
        # Kesin karşılaştırma (CV², kareköksüz ve bölmesiz): orantılı iki sütunun CV'si tam olarak aynıdır.
        with localcontext(_WIDE):
            left = ctx["scaled"] * ctx["n"] * (pair["n"] - 1) * pair["total_y"] * pair["total_y"]
            right = pair["scaled_y"] * pair["n"] * (ctx["n"] - 1) * ctx["total"] * ctx["total"]
        if left == right:
            verdict = "İki değişkenin göreli değişkenliği aynıdır."
        else:
            more = label if left > right else pair["label"]
            verdict = f"Kendi ortalamasına göre “{md(more)}” daha değişkendir."
        takeaway = (f"{verdict} Standart sapmalar farklı birimlerde olduğu için doğrudan karşılaştırılamaz; CV "
                    "birimsizdir. CV, sıfırın anlamlı olduğu oran ölçekli değişkenlerde kullanılır; ortalama sıfıra "
                    "yakınsa yanıltır (§5.5).")
    else:
        takeaway = ("CV, standart sapmanın ortalamanın yüzde kaçı olduğunu söyler ve birimsizdir. Sıfırın anlamlı "
                    "olduğu oran ölçekli değişkenlerde kullanılır; ortalama sıfıra yakınsa yanıltır (§5.5).")
    extra = (" " + " ".join(notes)) if notes else ""
    return LabStep(
        number=5,
        title=title,
        note=NoteRef(note),
        explanation=f"{lead} {'; '.join(parts)}.{extra}",
        operations=tuple(operations),
        checks=_kept(*checks),
        takeaway=takeaway,
    )


def _z(value: Decimal, mean: Decimal, std: Decimal) -> Decimal:
    with localcontext(_EXACT):
        return (value - mean) / std


def _step6(case: Case, ctx: dict, groups: dict | None) -> LabStep:
    x, d, names = ctx["x"], ctx["d"], ctx["names"]
    mean, std = ctx["mean"], ctx["std"]
    digits, std_digits = ctx["mean_digits"], ctx["std_digits"]
    high, low = ctx["high"], ctx["low"]
    z_high, z_low = _z(high, mean, std), _z(low, mean, std)
    noise, std_bound = ctx["noise"], ctx["std_bound"]
    high_bound, low_bound = _z_bound(noise, std_bound, std, z_high), _z_bound(noise, std_bound, std, z_low)
    # İki z-skoru aynı cümlede aynı basamakla yazılır (|z| < 1 için üç anlamlı basamak kuralı ikisine de uyar).
    common = max(_mean_digits(z_high, 1), _mean_digits(z_low, 1))
    high_digits = _safe_digits(common, high_bound, z_high)
    low_digits = _safe_digits(common, low_bound, z_low)
    # Yerine konan x̄ ya da s yuvarlanmışsa eşitlikler "≈" ile yazılır.
    exact = kesin_esit(mean, digits) == "=" == kesin_esit(std, std_digits)
    put = "=" if exact else "\\approx"
    result = "=" if exact and kesin_esit(z_high, high_digits) == "=" else "\\approx"
    z = names["z"]
    operations = [
        Derive(case.frame, z, E.div(E.sub(E.var(x), E.ref("ortalama")), E.ref("std_sapma")), "z-skoru (xᵢ − x̄)/s"),
        Statistic(case.frame, z, "max", "z_en_buyuk", "En büyük gözlemin z-skoru", decimals=high_digits),
        Statistic(case.frame, z, "min", "z_en_kucuk", "En küçük gözlemin z-skoru", decimals=low_digits),
    ]
    std_check = ctx["std_check"]
    checks = [_check("z_en_buyuk", "En büyük gözlemin z-skoru", high_digits,
                     _z_bound(noise, std_check, std, z_high), z_high),
              _check("z_en_kucuk", "En küçük gözlemin z-skoru", low_digits,
                     _z_bound(noise, std_check, std, z_low), z_low)]
    shown = [ctx["x"], z]
    groups_text = ""
    usable = groups is not None and all(item["std"] > 0 for item in groups["items"])
    if usable:
        parts = []
        for index, item in enumerate(groups["items"], start=1):
            value = _z(item["high"], item["mean"], item["std"])
            bound = _z_bound(item["noise"], item["std_bound"], item["std"], value)
            item_digits = _safe_digits(_mean_digits(value, 1), bound, value)
            operations.append(Scalar(
                f"z_grup_{index}",
                E.div(E.sub(E.ref(f"en_buyuk_{index}"), E.ref(f"ortalama_{index}")), E.ref(f"std_{index}")),
                f"En büyük z · {item['level']}", decimals=item_digits))
            checks.append(_check(f"z_grup_{index}", f"{item['level']}: en büyük gözlemin z-skoru", item_digits,
                                 _z_bound(item["noise"], item["std_check"], item["std"], value), value))
            parts.append(f"{md(item['level'])} grubunun en büyük gözlemi ({ondalik(item['high'], d)}) kendi grubunda "
                         f"$z {kesin_esit(value, item_digits)} {_math(value, item_digits)}$")
        groups_text = (" Farklı dağılımlardaki gözlemlerin göreli konumu da z ile karşılaştırılır: "
                       + "; ".join(parts) + ".")
    far = sum(1 for value in ctx["xs"] if abs(_z(value, mean, std)) > 3)
    far_text = ("Bu veride |z| > 3 olan gözlem yok." if far == 0 else
                f"Bu veride |z| > 3 olan gözlem sayısı: {far}; çan biçimli veride böyle gözlemler dikkatle incelenir "
                "(Adım 8).")
    return LabStep(
        number=6,
        title="z-skoru ve göreli konum",
        note=NoteRef("5.7"),
        explanation=(
            "$z = (x - \\bar{x})/s$, bir gözlemin ortalamadan kaç standart sapma uzakta olduğunu gösterir. "
            f"$\\bar{{x}} {kesin_esit(mean, digits)} {_math(mean, digits)}$ ve $s {kesin_esit(std, std_digits)} "
            f"{_math(std, std_digits)}$ ile en büyük gözlem için $z {put} ({_math(high, d)} - {_term(mean, digits)})/"
            f"{_math(std, std_digits)} {result} {_math(z_high, high_digits)}$, en küçük "
            f"gözlem için $z {kesin_esit(z_low, low_digits)} {_math(z_low, low_digits)}$.{groups_text}"
        ),
        operations=(*operations, ShowFrame(case.frame, tuple(shown), "Gözlemler ve z-skorları")),
        checks=_kept(*checks),
        takeaway=(
            "z > 0 ise gözlem ortalamanın üstünde, z < 0 ise altındadır; |z| büyüdükçe gözlem ortalamadan standart "
            f"sapma cinsinden daha uzaktadır. {far_text} Ham değerleri farklı ölçeklerde olan gözlemlerin göreli "
            "konumu z ile karşılaştırılır (§5.7)."
        ),
    )


def _slack(ctx: dict) -> float:
    """x̄ ± ks sınırının göreli payı: en az ``CHEBYSHEV_SLACK``. |x − x̄| ve ks'nin iki dil arasındaki olası farkı
    (``noise`` ve k·``std_bound``) bunun sekizde birini aşıyorsa (çok büyük değerler, dar yayılım) farkın sekiz katını
    aşan en küçük on kuvveti: tam sınırdaki gözlem iki dilde de içeride sayılır."""

    s = float(ctx["std"])
    need = 8 * max((ctx["noise"] + k * ctx["std_bound"]) / (k * s) for k, _ in EMPIRICAL)
    if need <= CHEBYSHEV_SLACK:
        return CHEBYSHEV_SLACK
    return 10.0 ** math.ceil(math.log10(need))


def _power_text(value: float) -> str:
    """On kuvvetinin yazımı: 1e-09 → 10⁻⁹."""

    exponent = round(math.log10(value))
    return "10" + str(exponent).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))


def _inside(ctx: dict, k: int, slack: float) -> int:
    """x̄ ± ks aralığındaki gözlem sayısı; uygulamanın kayan noktalı hesabıyla aynı kural (göreli pay ``slack``)."""

    values = ctx["values"].to_numpy(dtype=float)
    mean = float(pd.Series(values).mean())
    deviations = values - mean
    variance = float(pd.Series(deviations ** 2).sum()) / (len(values) - 1)
    std = math.sqrt(variance)
    return int(np.sum(np.abs(values - mean) <= k * std * (1 + slack)))


def _step7(case: Case, ctx: dict) -> LabStep:
    x, n, names = ctx["x"], ctx["n"], ctx["names"]
    indicators = []
    operations = [
        Scalar("chebyshev_2", E.sub(1, E.div(1, E.power(2, 2))), "k = 2: en az 1 − 1/2²", decimals=2),
        Scalar("chebyshev_3", E.sub(1, E.div(1, E.power(3, 2))), "k = 3: en az 1 − 1/3²", decimals=3),
    ]
    checks = [_scalar("chebyshev_2", "k = 2 için en az", 2), _scalar("chebyshev_3", "k = 3 için en az 8/9", 3)]
    rows, sentences, comparison = [], [], []
    slack = _slack(ctx)
    for k, empirical in EMPIRICAL:
        column = names[f"icinde_{k}"]
        count = _inside(ctx, k, slack)
        share = Decimal(count) / Decimal(n)
        share_digits = _share_digits(count, n)
        indicators.append(Derive(case.frame, column,
                                 E.compare("le", E.absolute(E.sub(E.var(x), E.ref("ortalama"))),
                                           E.mul(E.mul(k, E.ref("std_sapma")), 1 + slack)),
                                 f"x̄ ± {k}s aralığında mı? (1: evet, 0: hayır)"))
        operations.append(Statistic(case.frame, column, "mean", f"pay_{k}", f"k = {k}: bu verideki pay",
                                    decimals=max(2, share_digits)))
        checks.append(_scalar(f"pay_{k}", f"k = {k}: x̄ ± {k}s içindeki gözlemlerin payı", max(2, share_digits)))
        chebyshev = E.ref(f"chebyshev_{k}")
        rows += [(f"k = {k}: Chebyshev (en az)", chebyshev),
                 (f"k = {k}: ampirik kural (yaklaşık)", E.const(float(empirical))),
                 (f"k = {k}: bu veride", E.ref(f"pay_{k}"))]
        sentences.append(f"$\\bar{{x}} \\pm {k}s$ aralığında {n} gözlemin {count} tanesi ({_percent_about(share)})")
        comparison.append(f"k = {k} için bu veride {_percent_about(share)}, ampirik kuralda yaklaşık "
                          f"%{ondalik(empirical * 100)}")
    operations.append(ScalarTable(tuple(rows), "kurallar", decimals=3))
    shape = ("Ampirik kural yalnız yaklaşık çan biçimli dağılımlar için yaklaşık oranlar verir; verideki paylar bu "
             f"oranlardan ayrılabilir ({'; '.join(comparison)}).")
    return LabStep(
        number=7,
        title="Chebyshev eşitsizliği",
        note=NoteRef("5.8"),
        explanation=(
            "Dağılımın biçimi ne olursa olsun, $k > 1$ için gözlemlerin en az $1 - 1/k^2$ kadarı $\\bar{x} \\pm ks$ "
            "aralığındadır. Yaklaşık çan biçimli dağılımlarda ampirik kural daha güçlü bir yaklaşık bilgi verir: %68, "
            f"%95 ve %99,7. Verideki paylar: {'; '.join(sentences)}."
        ),
        operations=(*indicators, *operations),
        checks=_kept(*checks),
        code_note=(
            "Sınırdaki bir gözlem (|x − x̄| = ks) içeride sayılır; kayan noktalı hesap bu eşitliği son basamakta "
            f"bozmasın diye sınır {_power_text(slack)} göreli payla (ks × {ondalik(kesin(1 + slack))}) karşılaştırılır."
        ),
        takeaway=(
            "Chebyshev her veri seti için geçerli bir alt sınırdır (“en az”): bu veride de paylar %75 ve %88,9'dan "
            f"küçük değildir. {shape} İki kuralın kapsamı aynı değildir (§5.8)."
        ),
    )


def _fences(ctx: dict) -> dict:
    """Ders kuralıyla çeyrekler ve 1,5·IQR sınırları: kesin değerler (metin) ve kayan noktalı değerler (sayımlar;
    uygulamanın ve üretilen kodun işlem sırasıyla aynı).

    Çeyrekler komşu iki gözlemin 0,25'lik adımlarla ara değeridir; sınırlar en çok d + 3 ondalık basamaklıdır (d:
    verinin basamağı). Kayan noktalı hesabın farkı bu basamağın yarısından çok küçükse sınırlar sınıflamadan önce bu
    basamağa yuvarlanır (``decimals``): tam sınırdaki gözlem (ör. Q₃ + 1,5·IQR = 1,91 ve x = 1,91) aykırı sayılmaz.
    """

    ordered = ctx["ordered"]
    (q1, l25), (q3, l75) = _percentile(ordered, 25), _percentile(ordered, 75)
    with localcontext(_EXACT):
        iqr = q3 - q1
        lower = q1 - Decimal("1.5") * iqr
        upper = q3 + Decimal("1.5") * iqr
    bound = 8 * EPS * ctx["top"]  # ara değer ve sınır işlemlerinin olası farkı
    decimals = ctx["d"] + 3 if _safe_digits(ctx["d"] + 3, bound) == ctx["d"] + 3 else None
    values = ctx["values"].to_numpy(dtype=float)
    summary = T.box_summary(values, decimals)  # uygulamadaki ve koddaki kutu özetiyle aynı hesap
    lower_f, upper_f = float(summary["alt_sinir"]), float(summary["ust_sinir"])
    outliers = sorted(float(value) for value in values if value < lower_f or value > upper_f)
    return {"q1": q1, "q3": q3, "l25": l25, "l75": l75, "iqr": iqr, "lower": lower, "upper": upper,
            "lower_f": lower_f, "upper_f": upper_f, "outliers": outliers, "decimals": decimals, "bound": bound}


def _step8(case: Case, ctx: dict, fences: dict) -> LabStep:
    x, n, d, label, names = ctx["x"], ctx["n"], ctx["d"], ctx["label"], ctx["names"]
    q1, q3, iqr, lower, upper = (fences[key] for key in ("q1", "q3", "iqr", "lower", "upper"))
    bound, rounded = fences["bound"], fences["decimals"]
    q_digits = _common_digits((q1, q3), max(_exact_digits(q1), _exact_digits(q3)), bound)
    iqr_digits = _common_digits((iqr,), _exact_digits(iqr), bound)
    fence_digits = _common_digits((lower, upper), max(_exact_digits(lower), _exact_digits(upper)), bound)
    outliers = fences["outliers"]
    shown = [ondalik(kesin(value), d) for value in outliers[:MAX_LISTED]]
    if not outliers:
        verdict = "Sınırların dışında gözlem yok: bu veride aykırı değer adayı bulunmaz"
    elif len(outliers) == 1:
        verdict = (f"Sınırların dışındaki gözlem ({shown[0]}) aykırı değer adayıdır. Bu bir silme emri değildir: "
                   "gözlem doğruysa ve incelenen anakütleye aitse analizde kalır; önce nedeni araştırılır")
    elif len(outliers) <= MAX_LISTED:
        verdict = (f"Sınırların dışındaki {len(outliers)} gözlem aykırı değer adayıdır: {sayilar(shown)}. Bu bir silme "
                   "emri değildir: gözlemler doğruysa ve incelenen anakütleye aitse analizde kalır; önce nedenleri "
                   "araştırılır")
    else:
        verdict = (f"Sınırların dışında {len(outliers)} gözlem var (ilk {MAX_LISTED} tanesi: {sayilar(shown)}). Bu "
                   "bir silme emri değildir; önce nedenleri araştırılır")
    verdict += _fence_note(ctx, fences)
    aykiri = names["aykiri"]
    axis = _axis(min(ctx["low_f"], fences["lower_f"]), max(ctx["high_f"], fences["upper_f"]))
    return LabStep(
        number=8,
        title="IQR ile aykırı değer",
        note=NoteRef("5.9"),
        explanation=(
            f"Çeyrekler Konu 4'teki kuralla bulunur: $n = {n}$ için $L_{{25}} = 0{{,}}25 \\times {n + 1} = "
            f"{_math(fences['l25'], _exact_digits(fences['l25']))}$ ve $L_{{75}} = "
            f"{_math(fences['l75'], _exact_digits(fences['l75']))}$; $Q_1 {kesin_esit(q1, q_digits)} "
            f"{_math(q1, q_digits)}$; $Q_3 {kesin_esit(q3, q_digits)} {_math(q3, q_digits)}$ ve $IQR "
            f"{kesin_esit(iqr, iqr_digits)} {_math(iqr, iqr_digits)}$. Sınırlar $Q_1 - 1{{,}}5\\,IQR "
            f"{kesin_esit(lower, fence_digits)} {_math(lower, fence_digits)}$ ve $Q_3 + 1{{,}}5\\,IQR "
            f"{kesin_esit(upper, fence_digits)} {_math(upper, fence_digits)}$; bunların dışındaki gözlemler aykırı "
            "değer adayıdır."
        ),
        operations=(
            Percentile(case.frame, x, 25, "Q1", "Birinci çeyrek Q₁", location="L25", decimals=q_digits),
            Percentile(case.frame, x, 75, "Q3", "Üçüncü çeyrek Q₃", location="L75", decimals=q_digits),
            Scalar("iqr", E.sub(E.ref("Q3"), E.ref("Q1")), "IQR = Q₃ − Q₁", decimals=iqr_digits),
            Scalar("alt_sinir", _fence(E.sub(E.ref("Q1"), E.mul(1.5, E.ref("iqr"))), rounded),
                   "Alt sınır Q₁ − 1,5·IQR", decimals=fence_digits),
            Scalar("ust_sinir", _fence(E.add(E.ref("Q3"), E.mul(1.5, E.ref("iqr"))), rounded),
                   "Üst sınır Q₃ + 1,5·IQR", decimals=fence_digits),
            Derive(case.frame, aykiri,
                   E.add(E.compare("lt", E.var(x), E.ref("alt_sinir")), E.compare("gt", E.var(x), E.ref("ust_sinir"))),
                   "Sınırların dışında mı? (1: evet, 0: hayır)"),
            Statistic(case.frame, aykiri, "sum", "aykiri_sayisi", "Aykırı değer adayı sayısı", decimals=0),
            _spread_plot(case, case.frame, x, label, "Aykırı değer sınırları",
                         (("alt_sinir", "Alt sınır"), ("ust_sinir", "Üst sınır")), axis, n, ctx["low_f"],
                         ctx["high_f"], range_note="sınır çizgileri de görünsün"),
        ),
        checks=(
            _scalar("Q1", "Q₁", q_digits),
            _scalar("Q3", "Q₃", q_digits),
            _scalar("iqr", "IQR = Q₃ − Q₁", iqr_digits),
            _scalar("alt_sinir", "Alt sınır Q₁ − 1,5·IQR", fence_digits),
            _scalar("ust_sinir", "Üst sınır Q₃ + 1,5·IQR", fence_digits),
            _scalar("aykiri_sayisi", "Aykırı değer adayı sayısı"),
        ),
        code_note=(
            "" if rounded is None else
            f"Sınırlar en çok {rounded} ondalık basamaklıdır (çeyrekler komşu iki gözlemin 0,25'lik adımlarla ara "
            f"değeridir). Kod sınırları {rounded} basamağa yuvarlar: kayan noktalı hesabın son basamaktaki farkı atılır "
            "ve tam sınırdaki bir gözlem aykırı değer sayılmaz (aykırı değer sınırın dışında kalan gözlemdir)."
        ),
        takeaway=f"{verdict} (§5.9).",
    )


def _fence_note(ctx: dict, fences: dict) -> str:
    """Sınırlar yuvarlanamıyorsa (çok büyük değerler) kayan noktalı sınıflama tam sınırdaki bir gözlemde kesin hesaptan
    ayrılabilir: metin bunu açıkça söyler (uygulama ve kod aynı sınıflamayı yapar)."""

    if fences["decimals"] is not None:
        return ""
    d, lower, upper = ctx["d"], fences["lower"], fences["upper"]
    exact = sorted(value for value in ctx["xs"] if value < lower or value > upper)
    computed = sorted(kesin_yuvarla(kesin(value), d) for value in fences["outliers"])
    outside = [value for value in computed if value not in exact]
    inside = [value for value in exact if value not in computed]
    parts = []
    if outside:
        parts.append(f"{sayilar([ondalik(value, d) for value in outside])} kesin hesapta sınırların içindedir ama "
                     "kayan noktalı hesapta dışında kalır")
    if inside:
        parts.append(f"{sayilar([ondalik(value, d) for value in inside])} kesin hesapta sınırların dışındadır ama "
                     "kayan noktalı hesapta içinde kalır")
    if not parts:
        return ""
    return (f". Not: {'; '.join(parts)}. Bu büyüklükteki değerlerde kayan noktalı sınır son basamakta kesin değerden "
            "ayrılır; uygulama ve kod aynı sonucu verir")


def _fence(expression, decimals: int | None):
    """Sınır ifadesi; ``decimals`` verilmişse o basamağa yuvarlanmış (bkz. ``_fences``)."""

    return expression if decimals is None else E.roundto(expression, decimals)


def _overall_label(groups: dict | None, label: str) -> str:
    """Kutu grafiğinde bütün gözlemlerin serisi: grup varsa "Tümü" (bir grubun adıyla çakışmayan)."""

    if groups is None:
        return label
    names = set(groups["order"])
    for candidate in ("Tümü", "Tüm gözlemler", "Bütün veri"):
        if candidate not in names:
            return candidate
    return free_name("Tümü", names)


def _step9(case: Case, ctx: dict, groups: dict | None, fences: dict) -> LabStep:
    x, d, label = ctx["x"], ctx["d"], ctx["label"]
    overall = _overall_label(groups, label)
    series = [(case.frame, x, overall)]
    if groups is not None:
        series += [(item["frame"], x, item["level"]) for item in groups["items"]]
    ordered = ctx["ordered"]
    median, _ = _percentile(ordered, 50)
    digits = _common_digits((fences["q1"], median, fences["q3"]),
                            max(_exact_digits(fences["q1"]), _exact_digits(median), _exact_digits(fences["q3"])),
                            fences["bound"])
    values = ctx["values"].to_numpy(dtype=float)
    inside = values[(values >= fences["lower_f"]) & (values <= fences["upper_f"])]
    whisker_low, whisker_high = kesin(float(inside.min())), kesin(float(inside.max()))
    rows = (("en_kucuk", "En küçük değer", d), ("q1", "Q₁", digits), ("medyan", "Medyan", digits),
            ("q3", "Q₃", digits), ("en_buyuk", "En büyük değer", d), ("alt_biyik", "Sol bıyık ucu", d),
            ("ust_biyik", "Sağ bıyık ucu", d))
    checks = [Check(text, TableTarget("kutu", row, overall), 0.0, places) for row, text, places in rows]
    five = [ondalik(ctx["low"], d), ondalik(fences["q1"], digits), ondalik(median, digits),
            ondalik(fences["q3"], digits), ondalik(ctx["high"], d)]
    count = len(fences["outliers"])
    if count:
        outside = "sınırların dışındaki gözlem" if count == 1 else f"sınırların dışındaki {count} gözlem"
        whiskers = (f"Bıyıklar sınırların içindeki en uç gözlemlere uzanır: sol bıyık {ondalik(whisker_low, d)}, sağ "
                    f"bıyık {ondalik(whisker_high, d)}; {outside} ayrı nokta olarak gösterilir")
    else:
        whiskers = "Aykırı değer adayı olmadığı için bıyıklar en küçük ve en büyük gözleme uzanır"
    group_text = ""
    if groups is not None:
        for item in groups["items"]:
            group_median, _ = _percentile(sorted(item["exact"]), 50)
            median_digits = _common_digits((group_median,), _exact_digits(group_median), fences["bound"])
            checks.append(Check(f"{item['level']}: medyan", TableTarget("kutu", "medyan", item["level"]), 0.0,
                                median_digits))
        group_text = (" Grupların kutuları aynı eksende çizilir: kutu grafikleri iki grubun merkezini, yayılımını ve "
                      "aykırı değerlerini aynı ölçekte karşılaştırır.")
    return LabStep(
        number=9,
        title="Beş sayı özeti ve kutu grafiği",
        note=NoteRef("5.10"),
        explanation=(
            "Beş sayı özeti: en küçük değer, $Q_1$, medyan, $Q_3$ ve en büyük değer. Kutu $Q_1$'den $Q_3$'e çizilir, "
            "içindeki çizgi medyandır. Bıyıklar sınırların içindeki en uç gözlemlere uzanır; sınırların dışındaki "
            f"gözlemler ayrı noktalardır.{group_text}"
        ),
        operations=(
            BoxSummary(tuple(series), "kutu", fence_decimals=fences["decimals"]),
            BoxPlot(tuple(series), label, "Veri seti", f"{label}: kutu grafiği", fence_decimals=fences["decimals"]),
        ),
        checks=_kept(*checks),
        code_note=(
            "matplotlib'in boxplot ve R'nin boxplot fonksiyonları çeyrekleri kendi kurallarıyla hesaplar ve bu kural "
            "ders kuralından farklı olabilir. Kod, kutuyu ders kuralıyla bulunan özetten çizer."
        ),
        takeaway=f"Beş sayı özeti {sayilar(five)}. {whiskers} (§5.10).",
    )


def _corr_words(corr: Decimal) -> str:
    """Korelasyonun yönü; güç için mekanik bir eşik kullanılmaz (notlar §5.12)."""

    if corr == 1 or corr == -1:
        return "noktaların hepsi bir doğrunun üzerindedir (tam doğrusal ilişki)"
    if corr == 0:
        return "örneklemde doğrusal ilişki yoktur"
    direction = "pozitif" if corr > 0 else "negatif"
    return f"örneklemdeki doğrusal ilişkinin yönü {direction}"


def _step10(case: Case, ctx: dict, pair: dict | None, loaded: bool) -> LabStep:
    title, note = "Kovaryans", "5.11"
    if pair is None:
        return _missing(10, title, note, "“İkinci sayısal değişken (y)”, ör. satış ya da süre")
    if "problem" in pair:
        return _blocked(10, title, note, pair["problem"])
    x, y, frame, n = ctx["x"], pair["y"], pair["frame"], pair["n"]
    carpim = ctx["names"]["carpim"]
    label, y_label = ctx["label"], pair["label"]
    mean_x, mean_y, cov = pair["mean_x"], pair["mean_y"], pair["cov"]
    dx, dy, cov_digits = pair["digits_x"], pair["digits_y"], pair["cov_digits"]
    skipped = (f" İkinci sütunu boş olan {pair['skipped']} gözlem bu adımda kullanılmaz; {n} gözlem kalır."
               if pair["skipped"] else "")
    positive = sum(1 for a, b in zip(pair["xv"], pair["yv"]) if (kesin(a) - mean_x) * (kesin(b) - mean_y) > 0)
    negative = sum(1 for a, b in zip(pair["xv"], pair["yv"]) if (kesin(a) - mean_x) * (kesin(b) - mean_y) < 0)
    sign = "pozitif" if cov > 0 else ("negatif" if cov < 0 else "sıfır")
    zero = n - positive - negative  # gözlemlerden biri tam ortalamada (x = x̄ ya da y = ȳ)
    if positive == negative == 0:
        products = f"Sapmaların çarpımı {n} gözlemin hepsinde sıfır"
    else:
        kinds = [f"{count} tanesinde {word}" for count, word in ((positive, "pozitif"), (negative, "negatif"),
                                                                 (zero, "sıfır")) if count]
        products = f"Sapmaların çarpımı {n} gözlemin {liste(kinds)}"
        if negative == 0:
            products += "; negatif çarpım yok"
        elif positive == 0:
            products += "; pozitif çarpım yok"
    return LabStep(
        number=10,
        title=title,
        note=NoteRef(note),
        explanation=(
            f"x = “{md(label)}”, y = “{md(y_label)}”.{skipped} Her gözlem için sapmaların çarpımı "
            "$(x_i - \\bar{x})(y_i - \\bar{y})$ hesaplanır; örneklem kovaryansı bu çarpımların toplamının $n - 1$'e "
            "bölümüdür: $s_{xy} = \\sum (x_i - \\bar{x})(y_i - \\bar{y}) / (n - 1)$. Burada $\\bar{x} "
            f"{kesin_esit(mean_x, dx)} {_math(mean_x, dx)}$; $\\bar{{y}} {kesin_esit(mean_y, dy)} {_math(mean_y, dy)}$ "
            f"ve $s_{{xy}} {kesin_esit(cov, cov_digits)} {_math(cov, cov_digits)}$."
        ),
        operations=(
            *(() if loaded else pair["load"]),
            Statistic(frame, x, "mean", "ortalama_x", "x̄", decimals=dx),
            Statistic(frame, y, "mean", "ortalama_y_xy", "ȳ", decimals=dy),
            Derive(frame, carpim, E.mul(E.sub(E.var(x), E.ref("ortalama_x")), E.sub(E.var(y), E.ref("ortalama_y_xy"))),
                   "Sapmaların çarpımı (xᵢ − x̄)(yᵢ − ȳ)"),
            ShowFrame(frame, (x, y, carpim), "Gözlemler ve sapmaların çarpımı"),
            Statistic(frame, carpim, "sum", "carpim_toplami", "Çarpımların toplamı", decimals=pair["products_digits"]),
            Statistic(frame, x, "count", "n_xy", "Gözlem sayısı n", decimals=0),
            Scalar("kovaryans", E.div(E.ref("carpim_toplami"), E.sub(E.ref("n_xy"), 1)),
                   "Kovaryans s_xy", decimals=cov_digits),
            PairStatistic(frame, x, y, "cov", "kovaryans_yazilim", "Yazılımla kovaryans",
                          decimals=cov_digits),
            ScatterPlot(frame, x, y, label, y_label, f"{label} ve {y_label}: serpilme diyagramı"),
        ),
        checks=_kept(
            _check("ortalama_x", "x̄", dx, pair["noise_x"], mean_x),
            _check("ortalama_y_xy", "ȳ", dy, pair["noise_y"], mean_y),
            _check("kovaryans", "Kovaryans s_xy", cov_digits, pair["cov_check"], cov),
            _check("kovaryans_yazilim", "Yazılımla kovaryans", cov_digits, pair["cov_check"], cov),
        ),
        takeaway=(
            f"{products}; kovaryans {sign}. "
            "Kovaryansın işareti yönü gösterir; büyüklüğü ise ölçü birimine bağlıdır (§5.11)."
        ),
    )


def _step11(case: Case, ctx: dict, pair: dict | None) -> LabStep:
    title, note = "Korelasyon katsayısı", "5.12"
    if pair is None:
        return _missing(11, title, note, "“İkinci sayısal değişken (y)”, ör. satış ya da süre")
    if "problem" in pair:
        return _blocked(11, title, note, pair["problem"])
    if "constant" in pair:
        return _blocked(11, title, note, pair["constant"])
    x, y, frame = ctx["x"], pair["y"], pair["frame"]
    corr, digits = pair["corr"], pair["corr_digits"]
    std_x, std_y = pair["std_x"], pair["std_y"]
    sx_digits, sy_digits = pair["std_x_digits"], pair["std_y_digits"]
    return LabStep(
        number=11,
        title=title,
        note=NoteRef(note),
        explanation=(
            "Kovaryans iki standart sapmaya bölünerek ölçekten bağımsız hâle gelir: $r_{xy} = s_{xy}/(s_x s_y)$. "
            f"Değer her zaman $-1$ ile $1$ arasındadır. Burada $s_x {kesin_esit(std_x, sx_digits)} "
            f"{_math(std_x, sx_digits)}$; $s_y {kesin_esit(std_y, sy_digits)} {_math(std_y, sy_digits)}$ ve $r "
            f"{kesin_esit(corr, digits)} {_math(corr, digits)}$."
        ),
        operations=(
            Statistic(frame, x, "std", "std_x", "s_x", decimals=sx_digits),
            Statistic(frame, y, "std", "std_y_xy", "s_y", decimals=sy_digits),
            Scalar("korelasyon", E.div(E.ref("kovaryans"), E.mul(E.ref("std_x"), E.ref("std_y_xy"))),
                   "Korelasyon r", decimals=digits),
            PairStatistic(frame, x, y, "corr", "korelasyon_yazilim", "Yazılımla korelasyon",
                          decimals=digits),
        ),
        checks=_kept(
            _check("std_x", "s_x", sx_digits, pair["std_x_check"], std_x),
            _check("std_y_xy", "s_y", sy_digits, pair["std_y_check"], std_y),
            _check("korelasyon", "Korelasyon r", digits, pair["corr_check"], corr),
            _check("korelasyon_yazilim", "Yazılımla korelasyon", digits, pair["corr_check"], corr),
        ),
        takeaway=(
            f"r {'=' if kesin_esit(corr, digits) == '=' else '≈'} {ondalik(corr, digits)}: {_corr_words(corr)}. "
            "|r| 1'e yaklaştıkça noktalar bir doğru çevresinde daha sıkı toplanır; “güçlü” ya da “zayıf” için her "
            "alanda geçerli tek bir eşik yoktur. Korelasyon betimsel bir doğrusal ilişki ölçüsüdür: neden–sonuç "
            "ilişkisini tek başına göstermez ve eğrisel bir ilişkide sıfıra yakın olabilir (§5.12)."
        ),
    )


def _step12(case: Case, ctx: dict, fences: dict) -> LabStep:
    x, d = ctx["x"], ctx["d"]
    mean, digits = ctx["mean"], ctx["mean_digits"]
    median, _ = _percentile(ctx["ordered"], 50)
    median_digits = _common_digits((median,), _exact_digits(median), fences["bound"])
    iqr_digits = _common_digits((fences["iqr"],), _exact_digits(fences["iqr"]), fences["bound"])
    decimals = max(2, digits, median_digits, ctx["std_digits"], iqr_digits)
    outliers = len(fences["outliers"])
    if outliers:
        verdict = (f"Bu veride aykırı değer adayı sayısı: {outliers}. Uç gözlemler ortalamayı, standart sapmayı ve "
                   "değişim aralığını etkiler; IQR ve medyan ise orta %50'ye ve sıraya dayandığı için etkilenmez. Bu "
                   "yüzden medyan ve IQR, kutu grafiği ve aykırı değer notuyla birlikte raporlanır")
    else:
        verdict = ("Bu veride aykırı değer adayı yok. Ortalama ve standart sapma, medyan ve IQR ile birlikte bir "
                   "grafikle raporlanır; dağılımın biçimi hangi ölçünün öne çıkacağını belirler")
    if mean > median:
        position = "ortalamanın medyandan büyük olması sağa çarpıklığa işaret edebilir"
    elif mean < median:
        position = "ortalamanın medyandan küçük olması sola çarpıklığa işaret edebilir"
    else:
        position = "ortalama ile medyan eşittir"
    return LabStep(
        number=12,
        title="Tek sayı yerine istatistiksel profil",
        note=NoteRef("5.13"),
        explanation=(
            "Raporlama ilkesi: ortalamanın yanında standart sapma veya IQR, dağılımın biçimini gösteren bir grafik ve "
            f"aykırı değer bilgisi verilir. “{md(ctx['label'])}” değişkeninin profilini bu bölümün ölçüleriyle "
            f"birlikte çıkaralım: ortalama {_about(mean, digits)} ve medyan {_about(median, median_digits)}; "
            f"{position}."
        ),
        operations=(
            Statistic(case.frame, x, "mean", "profil_ortalama", "Ortalama", decimals=digits),
            Statistic(case.frame, x, "median", "profil_medyan", "Medyan", decimals=median_digits),
            Statistic(case.frame, x, "std", "profil_std", "Standart sapma s", decimals=ctx["std_digits"]),
            Statistic(case.frame, x, "max", "profil_max", "En büyük değer", decimals=d),
            Statistic(case.frame, x, "min", "profil_min", "En küçük değer", decimals=d),
            ScalarTable(
                (
                    ("Ortalama", E.ref("profil_ortalama")),
                    ("Medyan", E.ref("profil_medyan")),
                    ("Standart sapma s", E.ref("profil_std")),
                    ("IQR", E.ref("iqr")),
                    ("Değişim aralığı", E.sub(E.ref("profil_max"), E.ref("profil_min"))),
                ),
                "profil",
                decimals=decimals,
            ),
        ),
        takeaway=f"{verdict} (§5.13).",
    )


def build(case: Case) -> LabSpec:
    """Konu 5 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    ctx = _context(case)
    groups = _groups(case, ctx)
    pair = _pair(case, ctx)
    fences = _fences(ctx)
    steps = (
        _step1(case, ctx, groups), _step2(case, ctx, groups), _step3(case, ctx), _step4(case, ctx, groups),
        _step5(case, ctx, pair), _step6(case, ctx, groups), _step7(case, ctx), _step8(case, ctx, fences),
        _step9(case, ctx, groups, fences), _step10(case, ctx, pair, _cv_pair(pair)), _step11(case, ctx, pair),
        _step12(case, ctx, fences),
    )
    names = ctx["names"]
    labels = dict(case.labels)
    for key, text in (("sapma", "Sapma xᵢ − x̄"), ("sapma_kare", "Kareli sapma (xᵢ − x̄)²"), ("z", "z-skoru"),
                      ("aykiri", "Aykırı değer adayı (1: evet)"), ("icinde_2", "x̄ ± 2s içinde (1: evet)"),
                      ("icinde_3", "x̄ ± 3s içinde (1: evet)"), ("carpim", "(xᵢ − x̄)(yᵢ − ȳ)")):
        labels.setdefault(names[key], text)
    spec = LabSpec(
        topic_key="konu05",
        title=TITLE,
        note_section="5",
        steps=steps,
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


# --- Alternatif örnek ve kendi verin ---------------------------------------------------------

def alternative_case() -> Case:
    data = pd.DataFrame(list(ALT_ROWS), columns=["depo", "mesafe", "sure"])
    return Case(
        source="alternatif",
        load=(InlineData("teslimatlar", ("depo", "mesafe", "sure"), ALT_ROWS,
                         "Kurgusal veri: 24 paketin deposu, teslimat mesafesi (km) ve teslim süresi (saat)"),),
        frame="teslimatlar",
        data=data,
        roles={SAYISAL: "mesafe", GRUP: "depo", IKINCI: "sure"},
        labels=ALT_LABELS,
        orders={"depo": ("Kuzey", "Güney")},
        unit="paket",
        extra={
            "read_text": ("Kargo firmasının iki deposundan gönderilen 24 paketin deposu, teslimat mesafesi (km) ve "
                          "teslim süresi (saat) gönderi sırasıyla okunur."),
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def sample() -> pd.DataFrame:
    """Örnek dosya: alternatif örneğin verisi, Türkçe sütun adlarıyla."""

    return pd.DataFrame({
        ALT_LABELS["depo"]: [row[0] for row in ALT_ROWS],
        ALT_LABELS["mesafe"]: [row[1] for row in ALT_ROWS],
        ALT_LABELS["sure"]: [row[2] for row in ALT_ROWS],
    })


def validate(case: Case) -> None:
    """Yayılım ölçüleri için en az iki farklı değer gerekir; değerler büyüklüklerine göre birbirinden ayırt
    edilebilmeli (``SPREAD``). x ve y farklı sütunlar olmalı. Grup sütunu seçilmişse her grupta standart sapma için en
    az iki gözlem olmalı ve gruptaki değerler de büyüklüklerine göre ayırt edilebilmeli."""

    label = case.label(SAYISAL)
    if case.has(IKINCI) and case.roles[IKINCI] == case.roles[SAYISAL]:
        raise K.UploadError(f"“{label}” sütunu hem x hem y için seçildi. Kovaryans ve korelasyon iki farklı değişken "
                            "arasındaki ilişkiyi ölçer; “İkinci sayısal değişken (y)” için başka bir sütun seçin ya da "
                            "seçimi kaldırın.")
    values = case.data[case.roles[SAYISAL]].astype(float)
    if values.nunique() < 2:
        raise K.UploadError(f"“{label}” sütununda bütün değerler aynı; yayılım ölçüleri için en az iki farklı değer "
                            "gerekir.")
    low, high = float(values.min()), float(values.max())
    if high - low < SPREAD * max(abs(low), abs(high)):
        raise K.UploadError(f"“{label}” sütunundaki değerler büyüklüklerine göre birbirine çok yakın (en küçük "
                            f"{ondalik(kesin(low))}, en büyük {ondalik(kesin(high))}); sapmalar güvenilir basamakla "
                            "hesaplanamaz. Değerlerden ortak bir sayı çıkarın (ör. her değerden en küçük değeri) ya da "
                            "birimi değiştirin.")
    if case.has(GRUP):
        column = case.roles[GRUP]
        counts = case.data.dropna(subset=[column])[column].astype(str).value_counts()
        small = [level for level in case.orders[column] if counts.get(level, 0) < 2]
        if small:
            raise K.UploadError(f"“{case.label(GRUP)}” sütununun her grubunda en az iki gözlem olmalı (standart sapma "
                                f"için); “{small[0]}” grubunda daha az var.")
        grouped = case.data.dropna(subset=[column])
        for level in case.orders[column]:
            part = grouped.loc[grouped[column].astype(str) == level, case.roles[SAYISAL]].astype(float)
            if _too_close(part):
                raise K.UploadError(f"“{level}” grubundaki “{label}” değerleri büyüklüklerine göre birbirine çok yakın; "
                                    "grubun standart sapması güvenilir basamakla hesaplanamaz. Değerlerden ortak bir "
                                    "sayı çıkarın, birimi değiştirin ya da grup sütununun seçimini kaldırın.")


ROLES = (
    Role(SAYISAL, "Sayısal değişken (x)", "sayisal", True, tuple(range(1, 13)),
         "Yayılım ölçülerinin değişkeni (ör. mesafe, süre, gelir); kovaryans ve korelasyonda yatay eksen."),
    Role(GRUP, "Grup sütunu (iki kategorili)", "kategorik", False, (1, 2, 4, 6, 9),
         "Tam iki kategorili sütun (ör. tedarikçi A ve B, iki şube); iki grubun yayılımı karşılaştırılır.",
         levels=(2, 2), suggest=True),
    Role(IKINCI, "İkinci sayısal değişken (y)", "sayisal", False, (5, 10, 11),
         "Kovaryans ve korelasyonun ikinci değişkeni (dikey eksen) ve değişim katsayısının karşılaştırması (ör. süre, "
         "satış).", suggest=True),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Sayısal bir sütun içeren bir Excel (.xlsx) ya da CSV dosyası yükleyin. Sayısal değişken zorunludur. İki "
        "grubun yayılımını karşılaştırmak için tam iki kategorili bir grup sütunu (Adım 1, 2, 4, 6 ve 9); değişim "
        "katsayılarının karşılaştırması, kovaryans ve korelasyon için ikinci bir sayısal sütun (Adım 5, 10 ve 11) "
        "seçebilirsiniz. Sayısal değişkeni boş olan satırlar analizden çıkarılır; isteğe bağlı sütunlardaki boş "
        "hücreler yalnız o sütunu kullanan adımları etkiler."
    ),
    order_roles=(GRUP,),
    min_rows=5,
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
