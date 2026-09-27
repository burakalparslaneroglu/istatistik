"""Konu 9 uygulaması: Bernoulli denemesi, binom, Poisson ve hipergeometrik dağılımlar.

Ders notlarının çözümlü örnekleri: §9.3 (8 müşteri, p = 0,25: Bernoulli dizileri, Denklem 9.1–9.5; Şekil 9.6),
§9.4 (15 dakikada ortalama 3 kritik çağrı; Şekil 9.7–9.8), §9.5 (20 faturadan 4; Denklem 9.11–9.13) ve §9.12
(e-ticaret işletmesinde üç model; sonuçlar cevap anahtarında, Egzersiz 9.12). Buradaki her ``Check`` notlarda basılı
bir sayıdır; değer notlardan kopyalanmıştır, hesaplanmamıştır. §9.1–9.2 ve §9.6–9.11 model seçimidir, hesap içermez;
§9.6'daki binom–hipergeometrik karşılaştırması Sezgi sekmesindeki Deney 3'tür.

Olasılıklar iki yoldan hesaplanır: notlardaki formülle (kombinasyon, üs, e) ve yazılımın dağılım fonksiyonlarıyla
(Python ``scipy.stats``, R ``dbinom``/``dpois``/``dhyper``). İki yol aynı sayıyı verir.
"""

from __future__ import annotations

from core.labs import expr as E
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    Derive,
    Event,
    GroupSummary,
    LabSpec,
    LabStep,
    NoteRef,
    Outcomes,
    RowSum,
    Scalar,
    ScalarTarget,
    ShowFrame,
    Statistic,
    Support,
    TableTarget,
)

N_CUSTOMERS, P_BUY = 8, 0.25
"""§9.3: 8 müşteri, her birinin satın alma olasılığı p = 0,25; kararlar bağımsız."""
SHAPE_N, SHAPE_P = 10, (0.20, 0.50, 0.80)
"""§9.3 (Şekil 9.6): n = 10 sabitken p = 0,20, 0,50 ve 0,80."""
HOURLY_CALLS, MINUTES = 12, 15
"""§9.4: saatte ortalama 12 kritik çağrı; 15 dakikalık aralık."""
POISSON_SHAPES = (1, 3, 6)
"""§9.4 (Şekil 9.8): λ = 1, 3 ve 6."""
INVOICES, ERRORS, AUDITED = 20, 5, 4
"""§9.5: 20 faturanın 5'i hatalı; denetçi 4 faturayı yerine koymadan seçer."""


def _scalar(name: str, expected: float, label: str, decimals: int) -> Check:
    return Check(label, ScalarTarget(name), expected, decimals)


def _cell(frame: str, column: str, x: int, expected: float, label: str, decimals: int = 4) -> Check:
    """Olasılık tablosunda x değerinin satırı (satırlar 0'dan başlayan olası değerlerdir)."""

    return Check(label, CellTarget(frame, column, x + 1), expected, decimals)


def _moments(frame: str, suffix: str, label: str) -> tuple:
    """Konu 8'in tanımları olasılık fonksiyonu tablosuna: E(X) = Σ x f(x), Var(X) = Σ (x − μ)² f(x)."""

    mean, variance = f"E_{suffix}", f"Var_{suffix}"
    return (
        Derive(frame, "xf", E.mul(E.var("x"), E.var("f")), "x f(x)"),
        Statistic(frame, "xf", "sum", mean, f"E(X) = Σ x f(x): {label}", decimals=4),
        Derive(frame, "kare", E.mul(E.power(E.sub(E.var("x"), E.ref(mean)), 2), E.var("f")), "(x − μ)² f(x)"),
        Statistic(frame, "kare", "sum", variance, f"Var(X) = Σ (x − μ)² f(x): {label}", decimals=4),
    )


STEPS = (
    LabStep(
        number=1,
        title="Bernoulli denemelerinden binoma: bütün diziler",
        note=NoteRef("9.3", objects=("Şekil 9.3", "Şekil 9.4")),
        explanation=(
            "Tek bir müşterinin satın alıp almaması bir Bernoulli denemesidir: satın alırsa $Y = 1$ (olasılık "
            "$p = 0{,}25$), almazsa $Y = 0$. Sekiz müşterinin kararları bağımsızsa $2^8 = 256$ olası sonuç dizisi "
            "vardır. İçinde $x$ başarı bulunan bir dizinin olasılığı $p^x(1-p)^{8-x}$'tir; başarı sayısı "
            "$X = Y_1 + \\cdots + Y_8$'dir (Denklem 9.1). Aynı $x$'i veren dizilerin olasılıkları toplanınca binom "
            "olasılık fonksiyonu elde edilir."
        ),
        operations=(
            Outcomes("diziler", tuple((f"Y{i}", (0, 1)) for i in range(1, N_CUSTOMERS + 1)),
                     "Sekiz müşterinin bütün sonuç dizileri: 1 = satın alma, 0 = satın almama"),
            RowSum("diziler", "x", tuple(f"Y{i}" for i in range(1, N_CUSTOMERS + 1)),
                   "X = Y1 + ... + Y8: dizideki başarı sayısı (satır toplamı)"),
            Derive("diziler", "olasilik",
                   E.mul(E.power(P_BUY, E.var("x")), E.power(1 - P_BUY, E.sub(N_CUSTOMERS, E.var("x")))),
                   "Dizinin olasılığı: p^x (1 − p)^(8 − x)"),
            GroupSummary("diziler", "x", (("dizi_sayisi", "olasilik", "count"), ("olasilik", "olasilik", "sum")),
                         "binom_dizi", tuple(range(N_CUSTOMERS + 1)), decimals=4),
            BarChart("binom_dizi", "olasilik", "Satın alan müşteri sayısı, x", "P(X = x)",
                     "Aynı x'i veren dizilerin olasılıkları toplamı", decimals=4),
            Event("diziler", "en_az_bir", "x", tuple(range(1, N_CUSTOMERS + 1)), "X ≥ 1: en az bir satın alma"),
            Statistic("diziler", "olasilik", "sum", "P_en_az_bir_dizi", "P(X ≥ 1): en az bir başarı içeren diziler",
                      where=("en_az_bir", 1), decimals=4),
        ),
        checks=(
            Check("P(X = 2): iki başarılı 28 dizinin toplamı", TableTarget("binom_dizi", 2, "olasilik"), 0.3115, 4),
            _scalar("P_en_az_bir_dizi", 0.8999, "P(X ≥ 1)", 4),
        ),
        takeaway=(
            "Tam iki satın alma içeren 28 dizi vardır ve her birinin olasılığı (0,25)²(0,75)⁶'dır; toplam 0,3115. "
            "Dizi sayısı sütunu binom katsayısıdır: iki başarının 8 konuma C(8, 2) = 28 farklı yerleşimi (Şekil 9.5). "
            "Binom rassal değişkeni, bağımsız Bernoulli denemelerindeki başarıların toplamıdır (§9.3)."
        ),
    ),
    LabStep(
        number=2,
        title="Binom olasılık fonksiyonu ve tümleyen",
        note=NoteRef("9.3", objects=("(9.2)", "(9.3)")),
        explanation=(
            "$n$ denemede tam $x$ başarının olasılığı $P(X = x) = \\binom{n}{x}p^x(1-p)^{n-x}$'tir (Denklem 9.2). "
            "\"En az bir\" olayı için tümleyen kısa yoldur: $P(X \\geq 1) = 1 - P(X = 0) = 1 - (1 - p)^n$ "
            "(Denklem 9.3). Yazılımda binom olasılık fonksiyonu Python'da `stats.binom.pmf`, R'de `dbinom`; "
            "birikimli olasılık $P(X \\leq x)$ ise `stats.binom.cdf` ve `pbinom` ile hesaplanır."
        ),
        operations=(
            Scalar("yerlesim", E.comb(N_CUSTOMERS, 2), "C(8, 2): iki başarının 8 konuma yerleşim sayısı", decimals=0),
            Scalar("P2_binom_formul", E.mul(E.comb(N_CUSTOMERS, 2),
                                            E.mul(E.power(P_BUY, 2), E.power(1 - P_BUY, N_CUSTOMERS - 2))),
                   "P(X = 2) = C(8, 2)(0,25)²(0,75)⁶", decimals=4),
            Scalar("P2_binom", E.dbinom(2, N_CUSTOMERS, P_BUY), "P(X = 2): binom olasılık fonksiyonu", decimals=4),
            Scalar("P_en_az_bir", E.sub(1, E.power(1 - P_BUY, N_CUSTOMERS)), "P(X ≥ 1) = 1 − (0,75)⁸", decimals=4),
            Scalar("P_en_az_bir_birikimli", E.sub(1, E.pbinom(0, N_CUSTOMERS, P_BUY)),
                   "P(X ≥ 1) = 1 − P(X ≤ 0): birikimli olasılıkla", decimals=4),
        ),
        checks=(
            _scalar("P2_binom_formul", 0.3115, "P(X = 2) formülle", 4),
            _scalar("P2_binom", 0.3115, "P(X = 2) yazılımla", 4),
            _scalar("P_en_az_bir", 0.8999, "P(X ≥ 1) = 1 − (0,75)⁸", 4),
            _scalar("P_en_az_bir_birikimli", 0.8999, "P(X ≥ 1) birikimli olasılıkla", 4),
        ),
        takeaway=(
            "Formül ve yazılım aynı sayıyı verir: 8 müşteriden tam 2'sinin satın alma olasılığı yaklaşık %31,15'tir. "
            "En az bir satın alma için tek tek x = 1, …, 8 olasılıklarını toplamak yerine tümleyen yeterlidir. "
            "P(X = 2), P(X ≥ 2) ve P(X ≤ 2) farklı olaylardır; \"en az\" ifadesindeki eşitlik çizgisi 2'yi olaya "
            "katar (§9.3)."
        ),
    ),
    LabStep(
        number=3,
        title="Binomda beklenen değer ve varyans",
        note=NoteRef("9.3", objects=("(9.4)–(9.5)",)),
        explanation=(
            "Binom dağılımı Konu 8'deki kesikli dağılımın özel bir hâlidir: $E(X) = \\sum_x x f(x)$ ve "
            "$\\operatorname{Var}(X) = \\sum_x (x - \\mu)^2 f(x)$ tanımları olasılık fonksiyonu tablosuna aynen "
            "uygulanır. Binomda bu toplamlar $E(X) = np$ ve $\\operatorname{Var}(X) = np(1 - p)$ formüllerine "
            "indirgenir (Denklem 9.4–9.5)."
        ),
        operations=(
            Support("bin8", "x", 0, N_CUSTOMERS, "Bin(8, 0,25): X'in olası değerleri 0, 1, ..., 8"),
            Derive("bin8", "f", E.dbinom(E.var("x"), N_CUSTOMERS, P_BUY), "f(x) = P(X = x)"),
            *_moments("bin8", "binom", "tablodan"),
            ShowFrame("bin8", ("x", "f", "xf", "kare"), "Olasılık fonksiyonu tablosu ve momentlerin hesabı"),
            Scalar("E_np", E.mul(N_CUSTOMERS, P_BUY), "E(X) = np", decimals=0),
            Scalar("Var_npq", E.mul(E.mul(N_CUSTOMERS, P_BUY), 1 - P_BUY), "Var(X) = np(1 − p)", decimals=1),
        ),
        checks=(
            _scalar("E_binom", 2, "E(X) = Σ x f(x)", 0),
            _scalar("Var_binom", 1.5, "Var(X) = Σ (x − μ)² f(x)", 1),
            _scalar("E_np", 2, "E(X) = 8(0,25)", 0),
            _scalar("Var_npq", 1.5, "Var(X) = 8(0,25)(0,75)", 1),
        ),
        takeaway=(
            "Tablodan hesaplanan momentler formüllerle aynıdır: E(X) = 2, Var(X) = 1,5. Beklenen değer, 8 müşteriden "
            "mutlaka 2'sinin satın alacağı anlamına gelmez; çok sayıda benzer 8 müşterilik grupta başarı sayısının "
            "uzun dönem ortalamasıdır (§9.3)."
        ),
    ),
    LabStep(
        number=4,
        title="p değiştiğinde binom dağılımının biçimi",
        note=NoteRef("9.3", objects=("Şekil 9.6",)),
        explanation=(
            "$n = 10$ sabitken başarı olasılığı $p = 0{,}20$, $0{,}50$ ve $0{,}80$ alınır (Şekil 9.6). Her $p$ için "
            "olasılık fonksiyonu aynı olası değerler (0, 1, …, 10) üzerinde yazılır."
        ),
        operations=(
            Support("bin10", "x", 0, SHAPE_N, "n = 10: olası değerler 0, 1, ..., 10"),
            *(Derive("bin10", f"f_{round(100 * p):03d}", E.dbinom(E.var("x"), SHAPE_N, p),
                     f"f(x), p = {p:.2f}".replace(".", ","))
              for p in SHAPE_P),
            ShowFrame("bin10", ("x", "f_020", "f_050", "f_080"), "Üç binom dağılımı aynı değer ekseninde"),
            BarChart("bin10", "f_020", "Başarı sayısı, x", "P(X = x)", "Bin(10, 0,20): sağa çarpık", x="x",
                     decimals=3),
            BarChart("bin10", "f_050", "Başarı sayısı, x", "P(X = x)", "Bin(10, 0,50): simetrik", x="x", decimals=3),
            BarChart("bin10", "f_080", "Başarı sayısı, x", "P(X = x)", "Bin(10, 0,80): sola çarpık", x="x",
                     decimals=3),
        ),
        checks=(
            _cell("bin10", "f_020", 1, 0.2684, "p = 0,20: P(X = 1)"),
            _cell("bin10", "f_020", 2, 0.3020, "p = 0,20: P(X = 2)"),
            _cell("bin10", "f_050", 5, 0.2461, "p = 0,50: P(X = 5)"),
            _cell("bin10", "f_050", 4, 0.2051, "p = 0,50: P(X = 4)"),
            _cell("bin10", "f_080", 8, 0.3020, "p = 0,80: P(X = 8)"),
            _cell("bin10", "f_080", 9, 0.2684, "p = 0,80: P(X = 9)"),
        ),
        takeaway=(
            "p arttıkça dağılım daha büyük başarı sayılarına kayar; en yüksek sütun E(X) = np = 2, 5 ve 8 "
            "çevresindedir. p = 0,50'de dağılım simetriktir; p = 0,20 ile p = 0,80 birbirinin aynadaki görüntüsüdür: "
            "P(X = x | p) = P(X = 10 − x | 1 − p). Sezgi sekmesindeki Deney 1'de n ve p kaydırıcılarla değişir (§9.3)."
        ),
    ),
    LabStep(
        number=5,
        title="Poisson: λ'yı aralığa taşımak ve olasılık fonksiyonu",
        note=NoteRef("9.4", objects=("Şekil 9.7",)),
        explanation=(
            "Bir destek merkezine saatte ortalama 12 kritik çağrı geliyor. 15 dakikalık aralığın ortalaması "
            "$\\lambda_{15\\text{ dk}} = 12(15/60) = 3$'tür (Şekil 9.7). Tam iki çağrı olasılığı "
            "$P(X = 2) = \\lambda^2 e^{-\\lambda}/2!$ ile bulunur (Denklem 9.7). Yazılımda Poisson olasılık "
            "fonksiyonu Python'da `stats.poisson.pmf`, R'de `dpois`'tir."
        ),
        operations=(
            Scalar("lambda_15", E.mul(HOURLY_CALLS, E.div(MINUTES, 60)), "λ = 12 × 15/60: 15 dakikadaki ortalama",
                   decimals=0),
            Scalar("P2_pois_formul",
                   E.div(E.mul(E.power(E.ref("lambda_15"), 2), E.exp(E.neg(E.ref("lambda_15")))), E.factorial(2)),
                   "P(X = 2) = λ² e^(−λ) / 2!", decimals=4),
            Scalar("P2_pois", E.dpois(2, E.ref("lambda_15")), "P(X = 2): Poisson olasılık fonksiyonu", decimals=4),
        ),
        checks=(
            _scalar("lambda_15", 3, "λ₁₅ = 12(15/60)", 0),
            _scalar("P2_pois_formul", 0.2240, "P(X = 2) formülle", 4),
            _scalar("P2_pois", 0.2240, "P(X = 2) yazılımla", 4),
        ),
        takeaway=(
            "15 dakikalık olasılık hesabında λ = 12 değil λ = 3 kullanılır: olay hızı önce sorudaki aralığa taşınır. "
            "Tam iki çağrı olasılığı yaklaşık 0,2240'tır (§9.4)."
        ),
    ),
    LabStep(
        number=6,
        title="Poisson'da E(X) = Var(X) = λ ve λ'nın biçime etkisi",
        note=NoteRef("9.4", objects=("Şekil 9.8",)),
        explanation=(
            "Poisson rassal değişkeninin teorik üst sınırı yoktur, ama $x$ büyüdükçe olasılıklar hızla küçülür: "
            "$\\lambda = 3$ için 40'tan büyük değerlerin toplam olasılığı $10^{-20}$'den küçüktür. Bu yüzden "
            "0–40 değerleriyle $\\sum x f(x)$ ve $\\sum (x - \\mu)^2 f(x)$ hesaplanabilir. Şekil 9.8'deki üç dağılım "
            "$\\lambda = 1$, 3 ve 6 içindir."
        ),
        operations=(
            Support("pois3", "x", 0, 40, "Pois(3): olası değerler 0, 1, ..., 40 (sonraki değerlerin olasılığı ihmal "
                                        "edilebilir)"),
            Derive("pois3", "f", E.dpois(E.var("x"), E.ref("lambda_15")), "f(x) = P(X = x)"),
            Statistic("pois3", "f", "sum", "toplam_pois", "Σ f(x), x = 0, ..., 40", decimals=4),
            *_moments("pois3", "pois", "λ = 3"),
            Support("pois12", "x", 0, 12, "Şekil 9.8: x = 0, 1, ..., 12"),
            *(Derive("pois12", f"f_{lam}", E.dpois(E.var("x"), lam), f"f(x), λ = {lam}") for lam in POISSON_SHAPES),
            ShowFrame("pois12", ("x", "f_1", "f_3", "f_6"), "Üç Poisson dağılımı aynı değer ekseninde"),
            *(BarChart("pois12", f"f_{lam}", "Olay sayısı, x", "P(X = x)", f"Pois({lam})", x="x", decimals=3)
              for lam in POISSON_SHAPES),
        ),
        checks=(
            _scalar("E_pois", 3, "E(X) = λ", 0),
            _scalar("Var_pois", 3, "Var(X) = λ", 0),
            _cell("pois12", "f_1", 0, 0.3679, "λ = 1: P(X = 0)"),
            _cell("pois12", "f_1", 1, 0.3679, "λ = 1: P(X = 1)"),
            _cell("pois12", "f_3", 2, 0.2240, "λ = 3: P(X = 2)"),
            _cell("pois12", "f_3", 3, 0.2240, "λ = 3: P(X = 3)"),
            _cell("pois12", "f_6", 5, 0.1606, "λ = 6: P(X = 5)"),
            _cell("pois12", "f_6", 6, 0.1606, "λ = 6: P(X = 6)"),
        ),
        takeaway=(
            "Teorik Poisson modelinde ortalama ile varyans eşittir: ikisi de λ = 3. λ tam sayıyken en olası iki değer "
            "λ − 1 ve λ'dır (λ = 3'te 2 ve 3). λ küçükken dağılım belirgin biçimde sağa çarpıktır; λ büyüdükçe sağa "
            "kayar ve daha dengeli bir biçim alır (§9.4)."
        ),
    ),
    LabStep(
        number=7,
        title="Hipergeometrik: 20 faturadan yerine koymadan 4",
        note=NoteRef("9.5", objects=("(9.11)–(9.13)",)),
        explanation=(
            "20 faturanın 5'inde hata vardır; denetçi 4 faturayı yerine koymadan seçer: $N = 20$, $r = 5$, $n = 4$. "
            "Tam bir hatalı fatura olasılığı $P(X = 1) = \\binom{5}{1}\\binom{15}{3}/\\binom{20}{4}$'tür "
            "(Denklem 9.11). Yazılımda hipergeometrik olasılık fonksiyonu Python'da `stats.hypergeom.pmf(x, N, r, n)`, "
            "R'de `dhyper(x, r, N - r, n)`'dir: R başarı ve başarısızlık sayılarını ayrı ister."
        ),
        operations=(
            Scalar("P1_hiper_formul",
                   E.div(E.mul(E.comb(ERRORS, 1), E.comb(INVOICES - ERRORS, AUDITED - 1)), E.comb(INVOICES, AUDITED)),
                   "P(X = 1) = C(5, 1) C(15, 3) / C(20, 4)", decimals=4),
            Scalar("P1_hiper", E.dhyper(1, INVOICES, ERRORS, AUDITED), "P(X = 1): hipergeometrik olasılık fonksiyonu",
                   decimals=4),
            Support("hiper", "x", 0, AUDITED, "Hiper(20, 5, 4): olası değerler 0, 1, ..., 4"),
            Derive("hiper", "f", E.dhyper(E.var("x"), INVOICES, ERRORS, AUDITED), "f(x) = P(X = x)"),
            *_moments("hiper", "hiper", "tablodan"),
            ShowFrame("hiper", ("x", "f", "xf", "kare"), "Olasılık fonksiyonu tablosu ve momentlerin hesabı"),
            Scalar("E_hiper_formul", E.mul(AUDITED, E.div(ERRORS, INVOICES)), "E(X) = n r/N", decimals=0),
            Scalar("Var_hiper_formul",
                   E.mul(E.mul(E.mul(AUDITED, E.div(ERRORS, INVOICES)), E.sub(1, E.div(ERRORS, INVOICES))),
                         E.div(INVOICES - AUDITED, INVOICES - 1)),
                   "Var(X) = n (r/N)(1 − r/N)(N − n)/(N − 1)", decimals=4),
        ),
        checks=(
            _scalar("P1_hiper_formul", 0.4696, "P(X = 1) formülle", 4),
            _scalar("P1_hiper", 0.4696, "P(X = 1) yazılımla", 4),
            _scalar("E_hiper", 1, "E(X) = Σ x f(x)", 0),
            _scalar("Var_hiper", 0.6316, "Var(X) = Σ (x − μ)² f(x)", 4),
            _scalar("E_hiper_formul", 1, "E(X) = 4(5/20)", 0),
            _scalar("Var_hiper_formul", 0.6316, "Var(X) formülle", 4),
        ),
        takeaway=(
            "Seçilen 4 faturada tam 1 hatalı fatura bulunma olasılığı yaklaşık %46,96'dır. Varyans formülündeki "
            "(N − n)/(N − 1) = 16/19 çarpanı sonlu anakütleden yerine koymadan seçimin varyansı azaltan etkisidir: "
            "aynı p = 5/20 ile binom varyansı 4(0,25)(0,75) = 0,75 olurdu. Sezgi sekmesindeki Deney 3 iki modeli "
            "karşılaştırır (§9.5–9.6)."
        ),
    ),
    LabStep(
        number=8,
        title="Bütünleştirici uygulama: aynı işletmede üç model",
        note=NoteRef("9.12", objects=("Tablo 9.6",)),
        explanation=(
            "Bir e-ticaret işletmesi aynı gün üç soruyla karşılaşır (Tablo 9.6): reklamı gören 20 bağımsız müşterinin "
            "her biri 0,15 olasılıkla satın alır, $X \\sim \\operatorname{Bin}(20, 0{,}15)$; destek merkezine 10 "
            "dakikada ortalama 4 çağrı gelir, $Y \\sim \\operatorname{Pois}(4)$; 30 paketlik sevkiyatta 6 hasarlı "
            "paket vardır ve 5 paket yerine koymadan incelenir, $Z \\sim \\text{Hiper}(30, 6, 5)$. İstenen olasılıklar "
            "$P(X \\geq 1)$, $P(Y = 0)$ ve $P(Z = 1)$'dir; sonuçlar cevap anahtarındadır (Egzersiz 9.12)."
        ),
        operations=(
            Scalar("P_donusum", E.sub(1, E.power(0.85, 20)), "P(X ≥ 1) = 1 − (0,85)^20", decimals=4),
            Scalar("P_donusum_birikimli", E.sub(1, E.pbinom(0, 20, 0.15)), "P(X ≥ 1) = 1 − P(X ≤ 0)", decimals=4),
            Scalar("P_cagri", E.exp(-4), "P(Y = 0) = e^(−4)", decimals=4),
            Scalar("P_cagri_pois", E.dpois(0, 4), "P(Y = 0): Poisson olasılık fonksiyonu", decimals=4),
            Scalar("P_kalite", E.div(E.mul(E.comb(6, 1), E.comb(24, 4)), E.comb(30, 5)),
                   "P(Z = 1) = C(6, 1) C(24, 4) / C(30, 5)", decimals=4),
            Scalar("P_kalite_hiper", E.dhyper(1, 30, 6, 5), "P(Z = 1): hipergeometrik olasılık fonksiyonu",
                   decimals=4),
        ),
        checks=(
            _scalar("P_donusum", 0.9612, "P(X ≥ 1)", 4),
            _scalar("P_donusum_birikimli", 0.9612, "P(X ≥ 1) birikimli olasılıkla", 4),
            _scalar("P_cagri", 0.0183, "P(Y = 0)", 4),
            _scalar("P_cagri_pois", 0.0183, "P(Y = 0) yazılımla", 4),
            _scalar("P_kalite", 0.4474, "P(Z = 1)", 4),
            _scalar("P_kalite_hiper", 0.4474, "P(Z = 1) yazılımla", 4),
        ),
        takeaway=(
            "20 müşteriden en az birinin satın alma olasılığı yaklaşık %96,1; 10 dakikada hiç çağrı gelmeme olasılığı "
            "yaklaşık %1,83; seçilen 5 paketin tam birinin hasarlı olma olasılığı yaklaşık %44,7'dir. Aynı işletmede "
            "üç farklı dağılım gerekir: model sektörün adından değil, veri üretim mekanizmasından seçilir (§9.12)."
        ),
    ),
)

KONU09_LAB = LabSpec(
    topic_key="konu09",
    title="Binom, Poisson ve hipergeometrik olasılıkları hesaplamak",
    note_section="9",
    steps=STEPS,
    labels=(
        ("x", "x"),
        ("f", "f(x)"),
        ("xf", "x f(x)"),
        ("kare", "(x − μ)² f(x)"),
        ("olasilik", "Olasılık"),
        ("dizi_sayisi", "Dizi sayısı"),
        ("en_az_bir", "X ≥ 1"),
        ("f_020", "p = 0,20"),
        ("f_050", "p = 0,50"),
        ("f_080", "p = 0,80"),
        ("f_1", "λ = 1"),
        ("f_3", "λ = 3"),
        ("f_6", "λ = 6"),
    ),
)
