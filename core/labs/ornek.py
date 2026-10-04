"""Uygulama sekmesinin ek veri kaynakları: kurgusal alternatif örnek ve öğrencinin kendi verisi.

Ders notlarının çözümlü örnekleri (``core.labs.konuNN``) değişmez. Her konu için ek olarak bir **genel uygulama**
yazılır (``core.labs.ornek_konuNN``): aynı adımlar, aynı numaralar ve aynı işlemler, fakat veri bir ``Case``'ten gelir.
Alternatif örnek, genel uygulamanın kurgusal bir veriyle kurulmuş hâlidir; "kendi verini yükle" seçeneğinde aynı genel
uygulama öğrencinin dosyasıyla kurulur. Böylece iki ek kaynak tek bir tanımı paylaşır.

Notlar dışındaki kaynaklarda kontrollerin beklenen değerleri uygulamanın kendi hesabıdır (``with_app_values``):
indirilen kod bu değerleri yeniden üretmelidir. Alternatif örneklerin değerleri ayrıca testlerde bağımsız bir hesapla
doğrulanır.

Öğrencinin sütun ve kategori adları metinlere ``md`` ile girer: Markdown ve KaTeX işaretleri kaçırılır, böylece bir ad
(ör. "Fiyat ($)", "a|b", "1. sınıf") sayfanın biçimini bozmaz. Ad hiçbir zaman matematik ifadesinin içine yazılmaz.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from decimal import ROUND_HALF_EVEN, Context, Decimal
from fractions import Fraction
from typing import Callable, Iterable, Mapping

import pandas as pd

from core.labs.runner import run_lab
from core.labs.spec import DotPlot, LabSpec, Operation, PairStatistic, Percentile, Scalar, Statistic

SOURCE_LABELS = {
    "notlar": "Notlardaki örnek",
    "alternatif": "Alternatif örnek",
    "kendi": "Kendi verini yükle",
}
POSITIVE_WORDS = ("1", "evet", "var", "geçti", "başarılı", "tuttu", "memnun", "dönüştü", "doğru", "olumlu", "kabul",
                  "yes", "true")
"""İki kategorili bir sonuçta varsayılan "olumlu" kategori (ilk eşleşen; büyük-küçük harf Türkçe kuralıyla)."""


# --- Sayı yazımı (metinler için) --------------------------------------------------------

def sayi(value: float, decimals: int = 0) -> str:
    """Türkçe sayı: ondalık virgül, tipografik eksi (0,625; −1,5)."""

    return f"{value:.{decimals}f}".replace(".", ",").replace("-", "−")


def yuzde(value: float, decimals: int = 1) -> str:
    """Yüzde işareti sayıdan önce (%62,5); ondalığı sıfır olan değer kısaltılır (%40)."""

    text = sayi(value, decimals)
    if decimals and set(text.split(",")[-1]) == {"0"}:
        text = text.split(",")[0]
    return "%" + text


def kisa(value: float, decimals: int = 3) -> str:
    """Gereksiz sıfırları atılmış Türkçe sayı (0,320 → 0,32; 15,0 → 15)."""

    text = f"{value:.{decimals}f}"
    if "." in text:  # yalnız ondalık kısmın sıfırları atılır (20 → 20, 0,320 → 0,32)
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text.replace(".", ",").replace("-", "−")


def tex(value: float, decimals: int = 3) -> str:
    """Matematik ifadesi içindeki Türkçe sayı: virgül KaTeX'te ``{,}`` yazılır (0{,}32)."""

    return kisa(value, decimals).replace(",", "{,}")


def esit(value: float, decimals: int) -> str:
    """Gösterilen (yuvarlanmış) değer tam değere eşitse "=", değilse "\\approx" (notlardaki kural). Karşılaştırma
    göreli 10⁻¹² düzeyindedir: yalnız kayan nokta gürültüsü yutulur; büyük sayılarda da yuvarlama "≈" ile yazılır."""

    shown = float(f"{value:.{decimals}f}")
    return "=" if abs(shown - value) <= 1e-12 * max(1.0, abs(value)) else "\\approx"


# --- Kesin ondalık sayılar (metinler için) ----------------------------------------------------
# Metindeki "=" ile "≈" ayrımı ve "bu değer veride gözlenir mi" gibi yargılar kayan nokta toleransıyla değil, verinin
# kısa ondalık yazımından kurulan kesin değerlerle verilir; böylece çok büyük ya da çok küçük değerlerde de doğru kalır.

_KESIN = Context(prec=60)


def kesin(value: float) -> Decimal:
    """Kayan noktalı sayının kısa ondalık yazımı, kesin bir ondalık sayı olarak (0.30000000000000004 değil, dosyadaki
    gibi 0.3)."""

    return Decimal(repr(float(value)))


def kesin_yuvarla(value: Decimal, decimals: int) -> Decimal:
    """Ondalık sayının ``decimals`` basamağa yuvarlanmışı (yarımlar çift basamağa, Python'un biçimlemesi gibi)."""

    return value.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_EVEN, context=_KESIN)


def ondalik(value: Decimal, decimals: int | None = None) -> str:
    """Ondalık sayının Türkçe yazımı (2,5; 10; −0,25); ``decimals`` verilirse o basamağa yuvarlanır. Gereksiz sıfır ve
    −0 yazılmaz."""

    if decimals is not None:
        value = kesin_yuvarla(value, decimals)
    if value.is_zero():
        return "0"
    text = format(value.normalize(_KESIN), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


def ondalik_tex(value: Decimal, decimals: int | None = None) -> str:
    """Matematik ifadesi içindeki ondalık sayı (0{,}25)."""

    return ondalik(value, decimals).replace(",", "{,}")


def kesin_esit(value: Decimal, decimals: int) -> str:
    """Kesin değer, ``decimals`` basamakla gösterilen değere eşitse "=", değilse "\\approx"."""

    return "=" if kesin_yuvarla(value, decimals) == value else "\\approx"


def yarim_basamak(value: Decimal, decimals: int) -> int:
    """Gösterim basamağı: kesin değer tam iki gösterimin ortasındaysa (49,475 iki basamakla) bir basamak daha.
    Böylece metin ile tablo aynı sayıyı gösterir; kayan noktalı hesap böyle bir yarımı iki yöne de yuvarlayabilir."""

    scaled = _KESIN.scaleb(_KESIN.abs(value), decimals + 1)
    if scaled == _KESIN.to_integral_value(scaled) and int(scaled) % 10 == 5:
        return decimals + 1
    return decimals


# --- Kesirler (olasılıklar için) ------------------------------------------------------------
# Veriden gelen olasılıklar sayımların oranıdır (k/n); metindeki "=" / "≈" ve gösterim basamağı bu kesirden kurulur.

def kesir_basamak(value: Fraction, maximum: int = 4, minimum: int = 2) -> int:
    """Olasılığın gösterim basamağı: en çok ``maximum`` basamakla tam yazılabiliyorsa tam (0,175), değilse
    ``maximum`` (1/6 → 0,1667); en az ``minimum`` (0,50). Kesin değer ``maximum`` basamakta iki gösterimin tam
    ortasındaysa (1/800 = 0,00125) bir basamak daha: kayan noktalı değer yarımı iki yöne de yuvarlayabilir, metin ile
    tablo ayrışırdı."""

    for digits in range(0, maximum + 1):
        if (value * 10 ** digits).denominator == 1:
            return max(minimum, digits)
    scaled = abs(value) * 10 ** (maximum + 1)
    if scaled.denominator == 1 and scaled.numerator % 10 == 5:
        return maximum + 1
    return maximum


def kesir_ondalik(value: Fraction) -> Decimal:
    return _KESIN.divide(Decimal(value.numerator), Decimal(value.denominator))


def kesir_isaret(value: Fraction, digits: int) -> str:
    """Matematik içinde "=" ya da "\\approx": kesir gösterilen basamakla tam yazılabiliyorsa "="."""

    return "=" if (value * 10 ** digits).denominator == 1 else "\\approx"


def kesir_esit(value: Fraction, digits: int) -> str:
    """Düzyazıda "=" ya da "≈" (``kesir_isaret`` ile aynı kural)."""

    return "=" if kesir_isaret(value, digits) == "=" else "≈"


def kesir_tex(value: Fraction, digits: int | None = None) -> str:
    """Olasılık, matematik ifadesinde (0{,}175)."""

    return ondalik_tex(kesir_ondalik(value), kesir_basamak(value) if digits is None else digits)


def kesir_sayi(value: Fraction, digits: int | None = None) -> str:
    """Olasılık, düzyazıda, "yaklaşık" eklenmeden (0,175; 0,1667)."""

    return ondalik(kesir_ondalik(value), kesir_basamak(value) if digits is None else digits)


def kesir_metin(value: Fraction, digits: int | None = None) -> str:
    """Olasılık, düzyazıda; yuvarlanmışsa başında "yaklaşık"."""

    digits = kesir_basamak(value) if digits is None else digits
    shown = kesir_sayi(value, digits)
    return shown if kesir_isaret(value, digits) == "=" else f"yaklaşık {shown}"


def kesir_tablo_tex(value: Fraction, digits: int) -> str:
    """Sabit basamaklı bir tabloda da görünen olasılık, matematik ifadesinde: tablonun kayan noktalı değeri nasıl
    yuvarlıyorsa öyle (3/80 = 0,0375 üç basamakla tabloda 0,037; kesin yarım çift basamağa giderdi: 0,038)."""

    return ondalik_tex(Decimal(f"{float(value):.{digits}f}"))


def kesir_yarimda(value: Fraction, digits: int) -> bool:
    """Kesin değer ``digits`` basamakta iki gösterimin tam ortasında mı (0,000625 beş basamakla)? Kayan noktalı biçim
    böyle bir değeri iki yöne de yuvarlayabilir; metin (kesin, yarımlar çifte) ile tablo ayrışabilir."""

    scaled = abs(value) * 10 ** (digits + 1)
    return (value * 10 ** digits).denominator != 1 and scaled.denominator == 1 and scaled.numerator % 10 == 5


def kesir_ayirt(*values: Fraction, maximum: int = 12, start: int | None = None) -> int:
    """Birlikte karşılaştırılan kesirlerin ortak basamağı: farklı olanlar gösterimde de farklı görünecek kadar (en çok
    ``maximum``; ör. 0,49751 ile 0,4975). Tam yarımdaki bir değerde bir basamak daha (``kesir_basamak`` gibi). Arama
    ``start`` basamaktan (verilmezse değerlerin ``kesir_basamak``larının en büyüğünden) başlar."""

    distinct = set(values)

    def readable(digits: int) -> bool:
        if len({format(float(value), f".{digits}f") for value in distinct}) < len(distinct):
            return False
        return not any(kesir_yarimda(value, digits) for value in distinct)

    digits = max(kesir_basamak(value) for value in values) if start is None else start
    while digits < maximum and not readable(digits):
        digits += 1
    return digits


def kesir_ortak_basamak(*values: Fraction, maximum: int = 12) -> int:
    """Bir tabloda birlikte gösterilen kesirlerin ortak basamağı: ``kesir_basamak``ların en büyüğü; bu basamakta tam
    yarımda kalan bir değer varsa (1/1600 = 0,000625 beş basamakla) bir basamak daha. Tablo kayan noktalı değeri
    biçimler, metin kesin değeri yuvarlar; yarımda ikisi farklı sayı gösterebilirdi."""

    digits = max(kesir_basamak(value) for value in values)
    while digits < maximum and any(kesir_yarimda(value, digits) for value in values):
        digits += 1
    return digits


def kesir_gorunur(value: Fraction, maximum: int = 12) -> int:
    """Sıfırdan farklı bir kesrin (ör. iki oranın farkı) sıfır görünmediği basamak (en çok ``maximum``)."""

    digits = kesir_basamak(value)
    while value != 0 and digits < maximum and float(f"{float(value):.{digits}f}") == 0:
        digits += 1
    return digits


def kesir_yuzde(value: Fraction) -> str:
    """Düzyazıda yüzde: %52,5 ya da yaklaşık %33,3 (en çok bir ondalık)."""

    shown = value * 100
    digits = next((d for d in range(0, 2) if (shown * 10 ** d).denominator == 1), 1)
    if digits == 1 and kesir_basamak(shown, 1, 0) == 2:  # %12,25 gibi yarım: iki ondalık
        digits = 2
    text = "%" + ondalik(kesir_ondalik(shown), digits)
    return text if (shown * 10 ** digits).denominator == 1 else f"yaklaşık {text}"


# --- Sürekli dağılımlar ve tablo kuralı (Konu 10–12) ------------------------------------------------
# Girilen ondalık sayılar kesin kesirlere çevrilir; z = (x − μ)/σ, μ ± kσ, (d − c)/(b − a) gibi değerler kesin
# hesaplanır ve metindeki "=" / "≈" ayrımı bu kesirden kurulur. Karekök, e ve Φ içeren değerler (irrasyonel) "≈" ile
# yazılır.
# Tablo kuralı (z iki, Φ dört ondalık) ders kuralıyla yuvarlar: tam yarım sıfırdan uzağa (``E.yuvarla``).

def kesir_degeri(value: float) -> Fraction:
    """Girilen ondalık sayının kesin değeri (0,3 → 3/10; kayan noktalı yazımın kısa biçiminden)."""

    return Fraction(kesin(value))


def kesir_kok(value: Fraction) -> Fraction | None:
    """Kesrin kesin karekökü; pay ya da payda tam kare değilse ``None`` (karekök irrasyoneldir)."""

    if value < 0:
        return None
    top, bottom = math.isqrt(value.numerator), math.isqrt(value.denominator)
    if top * top == value.numerator and bottom * bottom == value.denominator:
        return Fraction(top, bottom)
    return None


def kisa_kesir(value: Fraction) -> str:
    """Kısa ondalık bir kesrin (girilen değer, μ ± kσ, μ + zσ) Türkçe yazımı: 0,4; −1,25; 250. Sonsuz ondalıklı
    kesirler için kullanılmaz (bkz. ``kesir_sayi``)."""

    return ondalik(kesir_ondalik(value))


def kisa_kesir_tex(value: Fraction) -> str:
    """Aynı sayı matematik ifadesinde (0{,}4; -1{,}25)."""

    return kisa_kesir(value).replace(",", "{,}").replace("−", "-")


def parantezli(text: str) -> str:
    """Negatif sayı bir işlemin sağında parantez içinde yazılır: 10 − (−5)."""

    return f"({text})" if text.startswith(("−", "-")) else text


def sabit(value: Fraction):
    """Koddaki sabit; negatif sayı tek terimli eksiyle yazılır (işlemin sağında parantezli: 90 - (-30))."""

    from core.labs import expr as E

    return E.neg(float(-value)) if value < 0 else E.const(float(value))


def ders_yuvarla(value: Fraction, digits: int) -> Fraction:
    """Ders kuralıyla yuvarlama (``E.yuvarla``): tam yarım sıfırdan uzağa (0,835 → 0,84; −0,835 → −0,84)."""

    scale = 10 ** digits
    magnitude = math.floor(abs(value) * scale + Fraction(1, 2))
    return Fraction(magnitude if value >= 0 else -magnitude, scale)


def ders_yuvarla_kok(factor: Fraction, radicand: Fraction, digits: int) -> Fraction:
    """z = factor · √radicand için ders kuralıyla yuvarlama, kesin aritmetikle (radicand ≥ 0). Karşılaştırmalar
    karelerle yapılır; irrasyonel bir z de (ör. z = (x̄ − μ)√n/σ) yarıma ne kadar yakın olursa olsun doğru tarafa
    yuvarlanır. ``radicand = 1`` iken ``ders_yuvarla`` ile aynıdır."""

    scale = 10 ** digits
    target = factor * factor * radicand * scale * scale  # (|z| · 10^d)²
    count = math.isqrt(math.floor(target))
    while count > 0 and (count - Fraction(1, 2)) ** 2 > target:
        count -= 1
    while (count + Fraction(1, 2)) ** 2 <= target:
        count += 1
    return Fraction(count if factor >= 0 else -count, scale)


def onemli_basamak(value: float, exact: Fraction | None = None, minimum: int = 0) -> int:
    """Konu 10–12'de bir büyüklüğün gösterim basamağı: kesin değer en çok dört basamakla tam yazılabiliyorsa o kadar
    (en az ``minimum``; tam yarımda bir basamak daha), değilse dört. Mutlak değeri 10⁻³'ten küçük bir değer üç anlamlı
    basamak görünecek kadar basamakla yazılır (en çok 12; kesin değer daha az basamakla tam yazılabiliyorsa o kadar):
    1/(b − a) = 0,000025 "≈ 0" görünmez ve kontrolün toleransı değerin kendisinden büyük olmaz."""

    if exact is not None:
        digits = kesir_basamak(exact, 4, minimum)
        if (exact * 10 ** digits).denominator == 1:
            return digits
    magnitude = abs(float(exact if exact is not None else value))
    if magnitude == 0 or magnitude >= 1e-3:
        return 4 if exact is None else kesir_basamak(exact, 4, minimum)
    digits = min(12, math.floor(-math.log10(magnitude)) + 3)
    if exact is not None:
        shorter = next((places for places in range(5, digits) if (exact * 10 ** places).denominator == 1), None)
        if shorter is not None:
            return shorter
        if digits < 12 and kesir_yarimda(exact, digits):
            digits += 1
    return digits


def olasilik_basamak(value: float, exact: Fraction | None = None) -> int:
    """Olasılığın gösterim basamağı (Konu 9'daki kural): kesir en çok dört basamakla tam yazılabiliyorsa o kadar;
    değilse dört; 10⁻³'ten küçük olasılıklarda üç anlamlı basamak görünecek kadar (en çok 12). Kesin değer tam
    yarımdaysa bir basamak daha."""

    if exact is not None and kesir_isaret(exact, kesir_basamak(exact)) == "=" and kesir_basamak(exact) <= 4:
        return kesir_basamak(exact)
    magnitude = abs(float(value))
    if magnitude == 0 or magnitude >= 1e-3:
        return 4 if exact is None else max(4, kesir_basamak(exact))
    digits = min(12, math.floor(-math.log10(magnitude)) + 3)
    if exact is not None and kesir_yarimda(exact, digits):
        digits += 1
    return digits


def deger_metni(value: float, exact: Fraction | None, digits: int) -> tuple[str, str]:
    """Düzyazıda gösterilen değer: (işaret, sayı). Kesin değer ``digits`` basamakla tam yazılabiliyorsa "=", değilse
    "≈"; kesin değeri bilinmeyen (irrasyonel) sayılar "≈" ile ve ekrandaki gibi yuvarlanır. Sondaki sıfırlar
    yazılmaz (genel uygulamaların ortak kuralı)."""

    if exact is not None:
        return kesir_esit(exact, digits), kesir_sayi(exact, digits)
    return "≈", ondalik(Decimal(f"{float(value):.{digits}f}"))


def olasilik_metni(value: float, exact: Fraction | None = None, digits: int | None = None) -> str:
    """Olasılık düzyazıda işaretiyle: "= 0,25", "≈ 0,2668"; çok küçükse "≈ 0 (10⁻¹²'den küçük)"."""

    digits = olasilik_basamak(value, exact) if digits is None else digits
    if 0 < abs(float(value)) < 5e-13 or (exact is None and float(value) == 0):  # kayan noktada sıfıra inen değer
        return "≈ 0 (10⁻¹²'den küçük)"
    return " ".join(deger_metni(value, exact, digits))


def deger_tex(value: float, exact: Fraction | None, digits: int) -> str:
    """Matematik ifadesinde gösterilen değer işaretiyle: "= 0{,}25" ya da "\\approx 0{,}0167"."""

    if exact is not None:
        return f"{kesir_isaret(exact, digits)} {kesir_tex(exact, digits)}".replace("−", "-")
    return f"\\approx {ondalik_tex(Decimal(f'{float(value):.{digits}f}'))}".replace("−", "-")


def liste(items: list[str]) -> str:
    """Türkçe sıralama: "A", "A ve B", "A, B ve C"."""

    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " ve " + items[-1]


def sayilar(items: list[str]) -> str:
    """Sayıların sıralaması: ondalık virgüllü bir sayı varsa ayırıcı noktalı virgüldür ("2,15; 2,2 ve 2,37")."""

    if len(items) <= 1 or not any("," in item for item in items):
        return liste(items)
    return "; ".join(items[:-1]) + " ve " + items[-1]


_MARKDOWN = re.compile(r"([\\`*_\[\]<>#|$~&])")


def md(text: object) -> str:
    """Markdown metnine girecek kullanıcı metni (sütun ya da kategori adı): biçim işaretleri kaçırılır, satır sonları
    boşluk olur, baştaki "1." numaralı liste sanılmaz."""

    value = re.sub(r"\s*[\r\n]+\s*", " ", str(text))
    value = _MARKDOWN.sub(r"\\\1", value)
    return re.sub(r"^(\d+)([.)])", r"\1\\\2", value)


def free_name(base: str, taken: Iterable[str]) -> str:
    """Türetilen sütun için kullanılmayan ad (``base``, ``base_2``, …)."""

    used = set(taken)
    candidate, index = base, 2
    while candidate in used:
        candidate, index = f"{base}_{index}", index + 1
    return candidate


def default_pick(categories: Iterable[str]) -> str:
    """İki kategorili sonucun varsayılanı: {0, 1} kodunda 1, aksi hâlde Evet, Var, Geçti, Tuttu, Memnun gibi olumlu
    bir kategori; yoksa sıradaki ilk kategori."""

    from core.labs.kendi_veri import fold

    items = list(categories)
    folded = {fold(item): item for item in items}
    for word in POSITIVE_WORDS:
        if word in folded:
            return folded[word]
    return items[0]


# --- Örnek (vaka) ---------------------------------------------------------------------

@dataclass(frozen=True, eq=False)
class Case:
    """Genel uygulamanın verisi ve değişkenlerin rolleri.

    ``load``: veriyi kuran işlemler (alternatif örnekte satır içi veri, kendi verinde ``ReadFile``). ``data``: aynı
    verinin temizlenmiş hâli (sıraları, metinleri ve kontrolleri kurmak için). ``roles``: rol → sütun (koddaki ad);
    ``labels``: sütun → ekranda görünen ad; ``levels``: rol → seçilen kategori (ör. olumlu sonuç); ``orders``: sütun →
    kategori sırası; ``unit``: gözlem biriminin adı (ör. "sipariş"); ``extra``: konuya özgü ayarlar ve metinler.
    """

    source: str
    load: tuple[Operation, ...]
    frame: str
    data: pd.DataFrame
    roles: Mapping[str, str]
    labels: Mapping[str, str]
    levels: Mapping[str, str] = field(default_factory=dict)
    orders: Mapping[str, tuple] = field(default_factory=dict)
    unit: str = "gözlem"
    extra: Mapping[str, object] = field(default_factory=dict)

    def label(self, role: str) -> str:
        return self.labels.get(self.roles[role], self.roles[role])

    def md(self, role: str) -> str:
        """Rolün sütun adı, Markdown metnine girecek biçimde."""

        return md(self.label(role))

    def has(self, role: str) -> bool:
        return role in self.roles


def _reference_decimals(spec: LabSpec) -> LabSpec:
    """Nokta grafiğindeki başvuru çizgilerinin açıklamada gösterdiği değer, o skaleri hesaplayan işlemin basamağıyla
    yazılır (ör. alt sınır 11,625; iki basamakla 11,62 olurdu ve metrikle uyuşmazdı)."""

    decimals: dict[str, int] = {}
    steps = []
    for step in spec.steps:
        operations = []
        for op in step.operations:
            if isinstance(op, (Statistic, PairStatistic, Scalar, Percentile)):
                decimals[op.name] = op.decimals
            if isinstance(op, DotPlot) and op.references:
                op = replace(op, reference_decimals=tuple(decimals.get(name, 2) for name, _ in op.references))
            operations.append(op)
        steps.append(replace(step, operations=tuple(operations)))
    return replace(spec, steps=tuple(steps))


def with_app_values(spec: LabSpec) -> LabSpec:
    """Kontrollerin beklenen değerlerini uygulamanın kendi hesabıyla doldurur (notlar dışındaki kaynaklar); nokta
    grafiklerinin başvuru değerleri metriklerle aynı basamakla gösterilir (``_reference_decimals``)."""

    run = run_lab(spec)
    steps = []
    for step in _reference_decimals(spec).steps:
        results = run.step_checks(step.number)
        checks = []
        for result in results:
            if not math.isfinite(result.value):
                raise ValueError(f"{result.check.label}: değer hesaplanamadı.")
            checks.append(replace(result.check, expected=result.value))
        steps.append(replace(step, checks=tuple(checks)))
    return replace(spec, steps=tuple(steps))


# --- Kendi verini yükle: roller --------------------------------------------------------

@dataclass(frozen=True)
class Role:
    """Kendi verinde öğrencinin bir sütun seçtiği rol.

    ``use``: ``kategorik``, ``sayisal`` ya da ``serbest`` (olduğu gibi; ör. kimlik sütunu). ``required``: rol zorunludur
    ve bu sütunda değeri olmayan satırlar analizden çıkarılır. ``levels``: kategorik rolün kategori sayısı aralığı.
    ``pick``: verilirse öğrenci bu rolün kategorilerinden birini de seçer (ör. "olumlu sonuç"). ``group``: aynı adımda
    birlikte gereken rollerin adı (ör. Simpson üçlüsü); grubun bir rolü seçilirse hepsi seçilmelidir.
    """

    key: str
    label: str
    use: str
    required: bool
    steps: tuple[int, ...]
    help: str
    levels: tuple[int, int] = (2, 15)
    pick: str | None = None
    group: str | None = None
    suggest: bool = False
    """İsteğe bağlı rol için de dosyadan bir sütun önerilir (öğrenci kaldırabilir)."""
    complete: bool = False
    """Seçilirse sütunda boş hücre olamaz (ör. kimlik ya da zaman sütunu)."""
    unique: bool = False
    """Seçilirse sütundaki değerler birbirinden farklı olmalı (kimlik sütunu)."""
    fixed_type: str | None = None
    """Tür seçimi olan konularda bu rolün sabit türü (ör. "Kimlik etiketi")."""
    allowed_types: tuple[str, ...] = ()
    """Tür seçimi olan konularda bu rol için seçilebilecek türler (boşsa hepsi)."""
    separate: bool = False
    """Seçilirse sütun ana veriden ayrı okunur: yalnız kendi dolu hücreleri, dosyadaki sırayla (ör. dönemlik yüzde
    değişimler; sütun diğerlerinden kısa olabilir). Ana verinin satır çıkarma kuralı bu sütuna uygulanmaz; değerleri
    ``Case.extra["separate"]`` içindedir."""


@dataclass(frozen=True, eq=False)
class SeparateColumn:
    """Ayrı okunan bir sütun (``Role.separate``): yükleme işlemleri, çerçeve, koddaki sütun adı ve değerler."""

    load: tuple[Operation, ...]
    frame: str
    column: str
    values: pd.Series


@dataclass(frozen=True)
class Setting:
    """Kendi verinde öğrencinin seçtiği bir tam sayı ayarı (ör. sınıf sayısı); veri panelinde kaydırıcıdır.

    ``default``: temizlenmiş veri ve rol → sütun eşlemesinden önerilen değer (ör. gözlem sayısına göre); öğrenci
    değiştirmezse bu değer kullanılır. Değer her zaman [``minimum``, ``maximum``] aralığına çekilir.
    """

    key: str
    label: str
    minimum: int
    maximum: int
    default: Callable[[pd.DataFrame, Mapping[str, str]], int]
    help: str
    steps: tuple[int, ...] = ()


@dataclass(frozen=True)
class CustomLab:
    """Bir konunun "kendi verini yükle" tanımı: roller, genel uygulamayı kuran fonksiyon ve örnek dosya."""

    roles: tuple[Role, ...]
    build: Callable[[Case], LabSpec]
    sample: Callable[[], pd.DataFrame]
    intro: str
    order_roles: tuple[str, ...] = ()
    """Kategori sırası seçeneğinin uygulandığı roller."""
    min_rows: int = 5
    extra_columns: bool = False
    """Öğrenci veri tablosuna rolü olmayan sütunlar da ekleyebilir (Konu 1)."""
    type_choices: Mapping[str, tuple[str, str]] | None = None
    """Verilirse öğrenci her sütunun istatistiksel türünü bu seçeneklerden seçer (Konu 1, Adım 2):
    seçenek adı → (tür, ayrıntı)."""
    guess_type: Callable[[pd.Series, str | None], str] | None = None
    """Bir sütun için önerilen tür seçeneği (sütun, rolü)."""
    validate: Callable[[Case], None] | None = None
    """Konuya özgü ek denetim (ör. zaman sütunu artan sırada mı); kullanılamıyorsa ``UploadError``."""
    settings: tuple[Setting, ...] = ()
    """Öğrencinin seçtiği tam sayı ayarları (ör. Konu 3'te sınıf sayısı); değerleri ``Case.extra["settings"]``."""


@dataclass(frozen=True)
class Parameter:
    """Dosyasız konularda (Konu 9–12) öğrencinin girdiği bir sayı; veri panelinde sayı girişidir.

    ``decimals`` 0 ise değer tam sayıdır; değilse bu kadar ondalıkla kesin yuvarlanır (0,25). Değer her zaman
    [``minimum``, ``maximum``] aralığına çekilir. ``group``: paneldeki sütun başlığı (ör. "Binom")."""

    key: str
    label: str
    minimum: float
    maximum: float
    default: float
    step: float = 1
    decimals: int = 0
    help: str = ""
    group: str = ""
    steps: tuple[int, ...] = ()


@dataclass(frozen=True)
class ParamLab:
    """Dosya yüklenmeyen konuların "Kendi değerlerini gir" tanımı: parametreler ve genel uygulamayı kuran fonksiyon.
    ``validate`` parametreler arasındaki koşulları denetler (ör. x ≤ n); kullanılamıyorsa ``UploadError``."""

    parameters: tuple[Parameter, ...]
    build: Callable[[Mapping[str, float]], LabSpec]
    intro: str
    groups: tuple[str, ...] = ()
    validate: Callable[[Mapping[str, float]], None] | None = None


def parameter_value(parameter: Parameter, chosen: object = None) -> int | float:
    """Parametrenin değeri: öğrencinin girdiği ya da varsayılan değer, aralığa çekilmiş ve kesin yuvarlanmış."""

    value = parameter.default if chosen is None else chosen
    value = min(max(float(value), parameter.minimum), parameter.maximum)
    if parameter.decimals == 0:
        return int(kesin_yuvarla(kesin(value), 0))
    return float(kesin_yuvarla(kesin(value), parameter.decimals))


def parameter_values(params: ParamLab, chosen: Mapping[str, object] | None = None) -> dict[str, int | float]:
    chosen = chosen or {}
    return {parameter.key: parameter_value(parameter, chosen.get(parameter.key)) for parameter in params.parameters}


@dataclass(frozen=True)
class TopicVariants:
    """Bir konunun ek veri kaynakları: kurgusal alternatif örnek ve öğrencinin kendisi (dosyayla ``custom`` ya da
    dosyasız konularda sayı girişleriyle ``params``)."""

    alternative: Callable[[], LabSpec]
    story: str
    """Alternatif örneğin tek cümlelik tanımı (sekmenin üstünde gösterilir)."""
    custom: CustomLab | None = None
    params: ParamLab | None = None


# --- Kendi verini yükle: seçimlerden örneğe ---------------------------------------------

ORDER_TEXT = {
    "alfabetik": "alfabetik sırayla",
    "dosya": "dosyadaki ilk görülme sırasıyla",
    "frekans": "frekansa göre (çoktan aza)",
}


@dataclass(frozen=True)
class CustomChoices:
    """Öğrencinin veri panelindeki seçimleri.

    ``roles``: rol → dosyadaki sütun adı (seçilmediyse ``None``); ``extra``: veri tablosuna eklenecek diğer sütunlar;
    ``order``: kategori sırası kuralı (``kendi_veri.ORDER_RULES``); ``picks``: rol → seçilen kategori; ``types``:
    dosyadaki sütun adı → tür seçeneği (``CustomLab.type_choices``); ``settings``: ayar → seçilen değer
    (``CustomLab.settings``; verilmeyen ayar önerilen değeri alır).
    """

    roles: Mapping[str, str | None]
    extra: tuple[str, ...] = ()
    order: str = "alfabetik"
    picks: Mapping[str, str] = field(default_factory=dict)
    types: Mapping[str, str] = field(default_factory=dict)
    settings: Mapping[str, int] = field(default_factory=dict)


def _selections(custom: CustomLab, table, choices: CustomChoices):
    from core.labs import kendi_veri as K

    for role in custom.roles:
        if role.required and not choices.roles.get(role.key):
            raise K.UploadError(f"“{role.label}” için bir sütun seçin.")
    groups: dict[str, list[Role]] = {}
    for role in custom.roles:
        if role.group:
            groups.setdefault(role.group, []).append(role)
    for members in groups.values():
        chosen = [role for role in members if choices.roles.get(role.key)]
        if chosen and len(chosen) < len(members):
            missing = [f"“{role.label}”" for role in members if not choices.roles.get(role.key)]
            raise K.UploadError("Bu rol grubu birlikte çalışır; şunlar için de sütun seçin: " + liste(missing) + ".")
    uses: dict[str, str] = {}
    required: dict[str, bool] = {}
    for role in custom.roles:
        original = choices.roles.get(role.key)
        if not original or role.separate:  # ayrı okunan sütun ana veriye girmez (bkz. ``_separate``)
            continue
        if original not in table.columns:
            raise K.UploadError(f"“{original}” sütunu dosyada yok.")
        previous = uses.get(original)
        if previous and previous != role.use:
            raise K.UploadError(f"“{original}” sütunu farklı türde iki rol için seçildi; her rol için uygun bir sütun "
                                "seçin.")
        uses[original] = role.use
        required[original] = required.get(original, False) or role.required
    for original in choices.extra:
        if original in table.columns:
            uses.setdefault(original, "serbest")
    taken: set[str] = set()
    selections = []
    for original, use in uses.items():
        name = K.code_name(original, taken)
        taken.add(name)
        selections.append(K.Selection(name, original, use, required=required.get(original, False)))
    return selections


def _types(custom: CustomLab, table, choices: CustomChoices, selections, roles: Mapping[str, str]):
    """Konu 1: her sütunun istatistiksel türü. Kimlik gibi rollerin türü sabittir; sayısal rol nicel olmalıdır."""

    from core.labs import kendi_veri as K

    role_of = {column: key for key, column in roles.items()}
    by_key = {role.key: role for role in custom.roles}
    types = {}
    for item in selections:
        role = by_key.get(role_of.get(item.name, ""))
        choice = choices.types.get(item.original)
        if role is not None and role.fixed_type:
            choice = role.fixed_type
        elif choice not in custom.type_choices:
            choice = custom.guess_type(table.frame[item.original], role.key if role else None) \
                if custom.guess_type else next(iter(custom.type_choices))
        if role is not None and role.allowed_types and choice not in role.allowed_types:
            raise K.UploadError(f"“{item.original}” sütunu “{role.label}” rolünde; türü "
                                f"{liste([f'“{name}”' for name in role.allowed_types])} seçeneklerinden biri olmalı. "
                                "Türü ya da rolün sütununu değiştirin.")
        types[item.name] = custom.type_choices[choice]
    return types


def _separate(custom: CustomLab, table, choices: CustomChoices, taken: set[str]) -> dict[str, SeparateColumn]:
    """Ayrı okunan rollerin sütunları: her biri kendi ``ReadFile`` işlemiyle, yalnız dolu hücreleriyle okunur."""

    from core.labs import kendi_veri as K

    columns: dict[str, SeparateColumn] = {}
    for role in custom.roles:
        original = choices.roles.get(role.key)
        if not role.separate or not original:
            continue
        if original not in table.columns:
            raise K.UploadError(f"“{original}” sütunu dosyada yok.")
        if all(K.clean_text(value) is None for value in table.frame[original]):
            raise K.UploadError(f"“{original}” sütununda dolu hücre yok; “{role.label}” için başka bir sütun seçin ya "
                                "da seçimi kaldırın.")
        name = K.code_name(original, taken)
        taken.add(name)
        frame = f"veri_{role.key}"
        part = K.prepare(table, [K.Selection(name, original, role.use, required=True)], frame=frame,
                         comment=f"{role.label}: sütunun dolu hücreleri, dosyadaki sırayla")
        # Boş hücreler bu sütunun doğal parçasıdır (ör. dört yıllık artış, on beş satırlık veri): not yazılmaz.
        columns[role.key] = SeparateColumn((replace(part.read, dropped=0),), frame, name, part.frame[name])
    return columns


def setting_value(setting: Setting, data: pd.DataFrame, roles: Mapping[str, str], chosen: object = None) -> int:
    """Ayarın değeri: öğrencinin seçimi ya da önerilen değer, [en küçük, en büyük] aralığına çekilmiş."""

    value = setting.default(data, roles) if chosen is None else int(chosen)
    return min(max(int(value), setting.minimum), setting.maximum)


def custom_case(custom: CustomLab, table, choices: CustomChoices) -> tuple[Case, tuple[str, ...]]:
    """Öğrencinin dosyası ve seçimlerinden genel uygulamanın örneğini kurar; kullanılamıyorsa ``UploadError``."""

    from core.labs import kendi_veri as K

    selections = _selections(custom, table, choices)
    prepared = K.prepare(table, selections, frame="veri", comment=f"Yüklediğiniz veri dosyası: {table.file_name}")
    data = prepared.frame
    if len(data) < custom.min_rows:
        raise K.UploadError(f"Analiz için en az {custom.min_rows} gözlem gerekir; seçilen sütunlarda {len(data)} "
                            "gözlem var.")
    names = {item.original: item.name for item in selections}
    roles = {role.key: names[choices.roles[role.key]] for role in custom.roles
             if choices.roles.get(role.key) and not role.separate}
    labels = {item.name: item.original for item in selections}
    separate = _separate(custom, table, choices, set(labels))
    for key, part in separate.items():
        roles[key] = part.column
        labels[part.column] = choices.roles[key]
    for role in custom.roles:
        if role.key not in roles or role.separate:
            continue
        column = roles[role.key]
        values = data[column]
        blanks = int(values.isna().sum())
        if role.complete and blanks:
            raise K.UploadError(f"“{labels[column]}” sütununda {blanks} boş hücre var. “{role.label}” rolündeki "
                                "sütunda her gözlemin değeri olmalı; boş hücreleri doldurun ya da başka bir sütun "
                                "seçin.")
        if role.unique and values.duplicated().any():
            repeated = values[values.duplicated()].iloc[0]
            raise K.UploadError(f"“{labels[column]}” sütununda tekrar eden değerler var (ör. “{repeated}”). "
                                f"“{role.label}” rolündeki sütunda her gözlemin değeri farklı olmalı.")
    orders: dict[str, tuple] = {}
    levels: dict[str, str] = {}
    for role in custom.roles:
        if role.key not in roles or role.use != "kategorik" or role.separate:
            continue
        column = roles[role.key]
        K.check_levels(data[column], labels[column], *role.levels)
        orders[column] = K.category_order(data[column], choices.order)
        if role.pick:
            pick = choices.picks.get(role.key)
            levels[role.key] = pick if pick in orders[column] else default_pick(orders[column])
    extra: dict[str, object] = {"order_text": ORDER_TEXT[choices.order]}
    if separate:
        extra["separate"] = separate
    if custom.type_choices is not None:
        extra["types"] = _types(custom, table, choices, selections, roles)
    if custom.settings:
        extra["settings"] = {setting.key: setting_value(setting, data, roles, choices.settings.get(setting.key))
                             for setting in custom.settings}
    case = Case(
        source="kendi",
        load=(prepared.read,),
        frame="veri",
        data=data,
        roles=roles,
        labels=labels,
        levels=levels,
        orders=orders,
        unit="gözlem",
        extra=extra,
    )
    if custom.validate is not None:
        custom.validate(case)
    return case, prepared.notes
