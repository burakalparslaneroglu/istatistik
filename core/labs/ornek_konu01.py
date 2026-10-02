"""Konu 1 genel uygulaması: bir veri setini okumak ve betimlemek.

Ders notlarındaki adımlar (§1.2, §1.3–1.4, §1.5, §1.7, §1.11) aynı numaralarla, verisi değiştirilebilir biçimde yazılır.
Alternatif örnek kurgusal bir kafe zinciri veri setidir; "kendi verin" seçeneğinde aynı adımlar öğrencinin dosyasıyla
kurulur. Notlardaki uygulama (``core.labs.konu01``) değişmez.
"""

from __future__ import annotations

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
    free_name,
    kisa,
    liste,
    md,
    sayi,
    tex,
    with_app_values,
    yuzde,
)
from core.labs.spec import (
    BarChart,
    CellTarget,
    Check,
    Count,
    Derive,
    InlineData,
    LabSpec,
    LabStep,
    LineChart,
    MapCodes,
    NoteRef,
    Scalar,
    ScalarTarget,
    Shape,
    Statistic,
    VariableTypes,
)

TITLE = "Bir veri setini okumak ve betimlemek"
KIMLIK, SAYISAL, IKILI, ZAMAN = "kimlik", "sayisal", "ikili", "zaman"
MAX_BARS = 40
"""Yatay kesit grafiğinde her gözlem bir sütundur; daha çok gözlemde grafik okunmaz."""
MAX_SHOWN = 40
"""Metinde gösterilen hücre değerinin en çok karakter sayısı."""

ALT_COLUMNS = ("kafe", "ilce", "personel", "ciro", "hedef")
ALT_ROWS = (
    ("A", "Bornova", 4, 18.5, "Tutmadı"),
    ("B", "Karşıyaka", 6, 26.0, "Tuttu"),
    ("C", "Bornova", 3, 15.2, "Tutmadı"),
    ("D", "Buca", 8, 34.8, "Tuttu"),
    ("E", "Karşıyaka", 5, 22.4, "Tutmadı"),
    ("F", "Bornova", 7, 29.6, "Tuttu"),
    ("G", "Buca", 4, 19.9, "Tutmadı"),
    ("H", "Karşıyaka", 6, 24.1, "Tutmadı"),
)
"""Kurgusal veri: sekiz kafenin ilçesi, personel sayısı, günlük cirosu (bin TL) ve 25 bin TL hedefini tutup
tutmadığı."""
ALT_SERIES = ((1, 182), (2, 185), (3, 190), (4, 188), (5, 196), (6, 203), (7, 209), (8, 217))
"""Kurgusal zaman serisi: zincirin aylık ortalama sepet tutarı (TL)."""
ALT_LABELS = {
    "kafe": "Kafe",
    "ilce": "İlçe",
    "personel": "Personel sayısı",
    "ciro": "Günlük ciro (bin TL)",
    "hedef": "Hedef durumu",
    "hedef_kod": "Hedef durumu kodu",
    "ay": "Ay",
    "sepet": "Ortalama sepet tutarı (TL)",
    "gozlem_no": "Gözlem numarası",
}
STORY = (
    "Kurgusal veri: bir kafe zincirinin sekiz şubesinin bir günlük kaydı (ilçe, personel sayısı, günlük ciro ve "
    "25 bin TL'lik ciro hedefinin tutup tutmadığı) ve zincirin sekiz aylık ortalama sepet tutarı."
)
IDENTITY_TYPE = "Kimlik etiketi"
TYPE_CHOICES = {
    IDENTITY_TYPE: (IDENTITY_TYPE, "Analitik değişken sayılmaz"),
    "Kategorik: nominal": ("Kategorik", "Nominal: kategoriler arasında sıra yok"),
    "Kategorik: sıralı": ("Kategorik", "Sıralı (ordinal): kategoriler arasında doğal bir sıra var"),
    "Nicel: kesikli": ("Nicel", "Kesikli: sayma ile elde edilir"),
    "Nicel: sürekli": ("Nicel", "Sürekli: ölçme ile elde edilir"),
}
"""Kendi verinde öğrencinin her sütun için seçtiği istatistiksel tür: (tür, ayrıntı)."""
CODE_TYPE = ("Kategorik", "0 ve 1 yalnızca etiket; miktar değildir")
CONCEPTS_ALT = (
    "| Kavram | Kafe araştırmasındaki karşılığı |\n"
    "|---|---|\n"
    "| Gözlem birimi | Her kafe (şube) |\n"
    "| Değişken | İlçe, personel sayısı, günlük ciro, hedef durumu |\n"
    "| Kategorik değişken | İlçe (nominal); hedef durumu (iki kategori) |\n"
    "| Ordinal değişken | Bu veride yok |\n"
    "| Nicel değişken | Personel sayısı (kesikli), günlük ciro (sürekli) |\n"
    "| Zaman serisi | Zincirin aylık ortalama sepet tutarı |\n"
    "| Örneklem | Kaydı incelenen sekiz kafe |\n"
    "| Olası anakütle | Araştırma sorusuna bağlı olarak zincirin bütün kafeleri |\n"
    "| Betimsel soru | Sekiz kafenin ortalama günlük cirosu kaç bin TL? |\n"
    "| Çıkarımsal soru | Zincirin bütün kafelerinde ortalama günlük ciro yaklaşık kaç bin TL? |"
)


def _scalar(name: str, label: str, decimals: int = 0) -> Check:
    return Check(label, ScalarTarget(name), 0.0, decimals)


def _shown(value: object) -> str:
    """Tablodaki bir değerin metindeki yazımı: sayılar Türkçe biçimde, boş hücre "boş", uzun metin kısaltılmış."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "boş"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return kisa(float(value), 4)
    text = str(value)
    return md(text if len(text) <= MAX_SHOWN else text[:MAX_SHOWN] + "…")


def _types(case: Case) -> dict[str, tuple[str, str]]:
    return dict(case.extra.get("types", {}))


def _identity(case: Case) -> list[str]:
    """Kimlik etiketi olan sütunlar: kimlik rolündeki sütun ve türü kimlik etiketi seçilen diğer sütunlar."""

    types = _types(case)
    columns = [column for column in case.data.columns if types.get(column, ("",))[0] == IDENTITY_TYPE]
    if case.has(KIMLIK) and case.roles[KIMLIK] not in columns:
        columns.insert(0, case.roles[KIMLIK])
    return columns


def _derived(case: Case) -> tuple[str | None, str]:
    """Türetilen sütunların adları (kod sütunu, gözlem numarası); dosyadaki sütunlarla çakışmaz."""

    taken = set(case.data.columns)
    code = free_name(f"{case.roles[IKILI]}_kod", taken) if case.has(IKILI) else None
    if code:
        taken.add(code)
    return code, free_name("gozlem_no", taken)


def _quoted(case: Case, columns: list[str]) -> str:
    return liste([f"“{md(case.labels.get(column, column))}”" for column in columns])


def _step1(case: Case) -> LabStep:
    data, frame, unit = case.data, case.frame, case.unit
    x = case.roles[SAYISAL]
    n, x_label = len(data), case.md(SAYISAL)
    identity = _identity(case)
    k = data.shape[1] - len(identity)
    last = n
    picked = [float(data[x].iloc[index]) for index in (0, 1, last - 1)]
    values = [f"{esit(value, 4)} {tex(value, 4)}" for value in picked]
    intro = case.extra.get("read_text") or "Seçtiğiniz sütunlar bir veri tablosu oluşturur."
    identity_text = ""
    if identity:
        noun = "sütunu" if len(identity) == 1 else "sütunları"
        identity_text = (f" {_quoted(case, identity)} {noun} yalnızca kimlik etiketidir; analitik değişken "
                         "sayılmaz.")
    row = ", ".join(f"{md(case.labels.get(column, column))} = {_shown(data[column].iloc[0])}"
                    for column in data.columns)
    checks = [
        _scalar("n", "Gözlem sayısı n"),
        _scalar("k", "Analitik değişken sayısı"),
        Check("x₁: 1. gözlemin değeri", CellTarget(frame, x, 1), 0.0, 4),
        Check("x₂: 2. gözlemin değeri", CellTarget(frame, x, 2), 0.0, 4),
        Check(f"x{_subscript(last)}: son gözlemin değeri", CellTarget(frame, x, last), 0.0, 4),
    ]
    return LabStep(
        number=1,
        title="Veri tablosu: gözlem, değişken, hücre",
        note=NoteRef("1.2"),
        explanation=(
            f"{intro} Her **satır** bir gözlemdir, her **sütun** bir değişkendir, her **hücre** bir değişken "
            f"değeridir.{identity_text}\n\n“{x_label}” değişkenini $x$ ile gösterirsek $x_i$, $i$ numaralı gözlemin "
            f"değeridir: $x_1 {values[0]}$, $x_2 {values[1]}$, $\\ldots$, $x_{{{last}}} {values[2]}$. Alt indis "
            "hangi gözlemden söz ettiğimizi belirtir."
        ),
        operations=(*case.load, Shape(frame, "n", "k", exclude=tuple(identity))),
        checks=tuple(checks),
        takeaway=(
            f"Tablonun ilk satırındaki gözlem: {row}. Bir gözlem, tek bir birim için kaydedilen bütün değişken "
            f"değerlerinin bütünüdür. Bu tabloda {n} {unit} ve {k} analitik değişken var."
        ),
    )


def _subscript(number: int) -> str:
    return str(number).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))


def _step2(case: Case) -> LabStep:
    frame, data = case.frame, case.data
    types = _types(case)
    operations = []
    checks = []
    code_text = ""
    code, _ = _derived(case)
    if case.has(IKILI) and code:
        b = case.roles[IKILI]
        chosen = case.levels[IKILI]
        other = next(item for item in case.orders[b] if item != chosen)
        operations.append(MapCodes(frame, b, code, ((other, 0), (chosen, 1)), f"{other} = 0, {chosen} = 1 kodlaması"))
        types[code] = CODE_TYPE
        for label in (other, chosen):
            position = int((data[b].astype(str) == label).to_numpy().argmax()) + 1
            checks.append(Check(f"{position}. gözlemin kodu ({label})", CellTarget(frame, code, position), 0.0, 0))
        code_text = (
            f" “{case.md(IKILI)}” değişkeni {md(other)} = 0, {md(chosen)} = 1 biçiminde kodlanır; bu kodlar yalnızca "
            "iki kategoriyi temsil eden etiketlerdir."
        )
    columns = [*data.columns, *([code] if case.has(IKILI) and code else [])]
    rows = tuple((column, *types.get(column, ("Belirtilmedi", ""))) for column in columns)
    operations.append(VariableTypes(frame, rows, "turler"))
    return LabStep(
        number=2,
        title="Değişken türü ve ölçme düzeyi",
        note=NoteRef("1.3–1.4"),
        explanation=(
            "Her değişkene aynı işlemi uygulayamayız: nicel bir değişkenin ortalaması anlamlıdır, kategori "
            f"etiketlerinin ortalaması anlamsızdır.{code_text}\n\nYazılım bir sütunu sayı ya da metin olarak saklar. "
            "İstatistiksel tür ise yazılımdan değil, değişkenin anlamından gelir: aşağıdaki tabloda iki bilgi yan "
            "yana durur."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            "Sayıyla yazılan her değişken nicel değildir. Kategori kodları sayı olarak saklanabilir; fakat 1'in 0'dan "
            "“bir birim fazla” olduğu biçiminde nicel yorum yapılmaz."
        ),
    )


def _label_decimals(values: pd.Series) -> int:
    """Grafikteki değer etiketlerinin basamağı: verideki en çok ondalık basamak (en çok 2)."""

    numbers = values.astype(float)
    for decimals in (0, 1):
        if ((numbers * 10 ** decimals).round(9) % 1 == 0).all():
            return decimals
    return 2


def _step3(case: Case) -> LabStep:
    frame, data = case.frame, case.data
    x, x_label = case.roles[SAYISAL], case.label(SAYISAL)
    n = len(data)
    title, note = "Yatay kesit ve zaman serisi", NoteRef("1.5")
    explanation = (
        "Yatay kesitte aynı değişken aynı anda farklı birimlerde gözlenir; zaman serisinde aynı değişken farklı "
        "dönemlerde gözlenir."
    )
    takeaway = (
        "Zaman serisinde gözlemlerin sırası bilgidir: bir dönem öncekinden sonra gelir. Yatay kesitte gözlemlerin "
        "tablodaki sırasını değiştirmek çoğu zaman verinin anlamını değiştirmez."
    )
    if case.has(ZAMAN):
        time = case.roles[ZAMAN]
        return LabStep(
            number=3,
            title=title,
            note=note,
            explanation=(
                f"{explanation} “{case.md(ZAMAN)}” sütunu seçildiği için bu veri bir zaman serisidir: "
                f"“{md(x_label)}” değişkeni {n} dönemde gözlenir ve dönemlerin sırasıyla çizilir."
            ),
            operations=(LineChart(frame, time, x, case.label(ZAMAN), x_label,
                                  "Zaman serisi: aynı değişken, farklı dönemler"),),
            takeaway=takeaway,
        )
    operations = []
    decimals = _label_decimals(data[x])
    if n <= MAX_BARS:
        if case.has(KIMLIK):
            operations.append(BarChart(frame, x, case.label(KIMLIK), x_label,
                                       "Yatay kesit: aynı değişken, farklı gözlemler", x=case.roles[KIMLIK],
                                       decimals=decimals))
        else:
            _, number = _derived(case)
            operations.append(Derive(frame, number, E.seq(E.var(x)), "Gözlem numarası 1, 2, …, n"))
            operations.append(BarChart(frame, x, "Gözlem numarası", x_label,
                                       "Yatay kesit: aynı değişken, farklı gözlemler", x=number, decimals=decimals))
    series = case.extra.get("series")
    if series is not None:
        load, series_frame, time, value, time_label, value_label = series
        operations += [load, LineChart(series_frame, time, value, time_label, value_label,
                                       "Zaman serisi: aynı değişken, farklı dönemler")]
        explanation += " " + str(case.extra.get("series_text", ""))
    elif n <= MAX_BARS:
        explanation += (" Seçtiğiniz veri bir yatay kesittir: aşağıdaki grafikte her gözlem bir sütundur. Zaman "
                        "serisi için dosyada artan sırada bir zaman sütunu (ör. yıl) seçin.")
    else:
        explanation += (f" Seçtiğiniz veri bir yatay kesittir. Gözlem sayısı ({n}) {MAX_BARS} değerinden büyük olduğu "
                        "için her gözlem için ayrı sütun çizilmez. Zaman serisi için dosyada artan sırada bir zaman "
                        "sütunu (ör. yıl) seçin.")
    return LabStep(number=3, title=title, note=note, explanation=explanation.strip(), operations=tuple(operations),
                   takeaway=takeaway)


def _step4(case: Case) -> LabStep:
    frame, data, unit = case.frame, case.data, case.unit
    x, x_label = case.roles[SAYISAL], case.label(SAYISAL)
    n = len(data)
    total = float(data[x].sum())
    operations = []
    checks = []
    parts = []
    summary = []
    if case.has(IKILI):
        b, chosen = case.roles[IKILI], case.levels[IKILI]
        count = int((data[b].astype(str) == chosen).sum())
        operations += [
            Count(frame, "secilen", b, chosen, f"{chosen} sayısı"),
            Scalar("oran", E.div(E.ref("secilen"), E.ref("n")), f"{chosen} oranı", decimals=3),
            Scalar("yuzde", E.mul(100, E.div(E.ref("secilen"), E.ref("n"))), f"{chosen} yüzdesi", decimals=1,
                   percent=True),
        ]
        checks += [_scalar("secilen", f"{chosen} sayısı"), _scalar("oran", f"{chosen} oranı", 3),
                   _scalar("yuzde", f"{chosen} yüzdesi", 1)]
        parts.append(
            f"“{case.md(IKILI)}” değişkeninde {md(chosen)} kategorisindeki gözlemler sayılır: oran ${count}/{n}$, "
            f"yüzde $100 \\times {count}/{n}$ ile bulunur."
        )
        summary.append(f"{md(chosen)} yüzdesi {yuzde(100 * count / n)}")
    operations += [
        Statistic(frame, x, "sum", "toplam", f"{x_label} toplamı", decimals=4),
        Scalar("ortalama", E.div(E.ref("toplam"), E.ref("n")), f"{x_label} ortalaması", decimals=2),
    ]
    checks += [_scalar("toplam", f"{x_label} toplamı", 4), _scalar("ortalama", f"{x_label} ortalaması", 2)]
    parts.append(
        f"“{md(x_label)}” değerlerinin toplamı $\\sum x_i {esit(total, 4)} {tex(total, 4)}$ ve ortalaması "
        f"$\\bar{{x}} = \\sum x_i / n$ ile bulunur (ortalama Konu 4'te ayrıntılı işlenir)."
    )
    summary.append(f"“{md(x_label)}” ortalaması {sayi(total / n, 2)}")
    return LabStep(
        number=4,
        title="Betimsel istatistik: oran ve ortalama",
        note=NoteRef("1.7"),
        explanation=(
            " ".join(parts) + " Amaç, betimsel istatistiğin veriyi daha okunabilir bir sayıya dönüştürdüğünü görmektir."
        ),
        operations=tuple(operations),
        checks=tuple(checks),
        takeaway=(
            f"Bu sonuçlar ({liste(summary)}) yalnızca bu {n} {unit} için geçerlidir. Daha geniş bir topluluk hakkında "
            "konuşmak çıkarımdır ve örneklemin nasıl seçildiğine bağlıdır (§1.8)."
        ),
    )


def _concepts_custom(case: Case) -> str:
    types = _types(case)
    identity = set(_identity(case))
    names = [column for column in case.data.columns if column not in identity]

    def shown(columns: list[str]) -> str:
        return liste([md(case.labels.get(column, column)) for column in columns]) or "—"

    def kind(column: str) -> tuple[str, str]:
        return types.get(column, ("", ""))

    categorical = [column for column in names if kind(column)[0] == "Kategorik"]
    ordinal = [column for column in categorical if kind(column)[1].startswith("Sıralı")]
    nominal = [column for column in categorical if column not in ordinal]
    numeric = [column for column in names if kind(column)[0] == "Nicel"]
    n, x = len(case.data), case.md(SAYISAL)
    rows = [
        ("Gözlem birimi", "Her satırın temsil ettiği birim (ör. öğrenci, firma, dönem)"),
        ("Değişken", shown(names)),
        ("Kategorik değişken", shown(nominal)),
        ("Ordinal değişken", shown(ordinal)),
        ("Nicel değişken", shown(numeric)),
    ]
    if case.has(ZAMAN):
        rows.append(("Zaman serisi", f"“{x}” değişkeninin “{case.md(ZAMAN)}” sırasıyla gözlenmesi"))
    rows += [
        ("Örneklem", f"Dosyadaki {n} gözlem"),
        ("Olası anakütle", "Araştırma sorusuna bağlı olarak bu gözlemlerin seçildiği bütün birimler"),
        ("Betimsel soru", f"Bu {n} gözlemde “{x}” ortalaması nedir?"),
        ("Çıkarımsal soru", f"Anakütlede “{x}” ortalaması yaklaşık nedir?"),
    ]
    return "| Kavram | Sizin verinizdeki karşılığı |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in rows)


def _step5(case: Case) -> LabStep:
    table = case.extra.get("concepts") or _concepts_custom(case)
    return LabStep(
        number=5,
        title="Bütünleştirici uygulama: kavramları eşleştirmek",
        note=NoteRef("1.11"),
        explanation=f"Bu konunun kavramları verideki karşılıklarıyla eşleştirilir:\n\n{table}",
        takeaway=(
            "Aynı veriyle farklı sorular sorulur: en yaygın kategori kategorik veriyi, ortalama nicel veriyi özetler; "
            "iki değişkeni birlikte incelemek ilişkiler hakkında düşünmenin ilk adımıdır."
        ),
    )


def build(case: Case) -> LabSpec:
    """Konu 1 uygulamasını verilen veriyle kurar; kontrollerin beklenen değerleri uygulamanın hesabıdır."""

    labels = dict(case.labels)
    code, number = _derived(case)
    if code:
        labels.setdefault(code, f"{case.label(IKILI)} kodu")
    labels.setdefault(number, "Gözlem numarası")
    spec = LabSpec(
        topic_key="konu01",
        title=TITLE,
        note_section="1",
        steps=(_step1(case), _step2(case), _step3(case), _step4(case), _step5(case)),
        labels=tuple(labels.items()),
        source=case.source,
    )
    return with_app_values(spec)


def alternative_case() -> Case:
    data = pd.DataFrame(list(ALT_ROWS), columns=list(ALT_COLUMNS))
    return Case(
        source="alternatif",
        load=(InlineData("kafeler", ALT_COLUMNS, ALT_ROWS,
                         "Kurgusal veri: sekiz kafenin ilçesi, personel sayısı, günlük cirosu ve hedef durumu"),),
        frame="kafeler",
        data=data,
        roles={KIMLIK: "kafe", SAYISAL: "ciro", IKILI: "hedef"},
        labels=ALT_LABELS,
        levels={IKILI: "Tuttu"},
        orders={"hedef": ("Tutmadı", "Tuttu")},
        unit="kafe",
        extra={
            "read_text": "Sekiz kafenin kaydı satır satır yazılır.",
            "types": {
                "kafe": TYPE_CHOICES[IDENTITY_TYPE],
                "ilce": ("Kategorik", "Nominal: ilçeler arasında sıra yok"),
                "personel": ("Nicel", "Kesikli (sayma); oran ölçeği"),
                "ciro": ("Nicel", "Sürekli; oran ölçeği (gerçek sıfır: 0 TL)"),
                "hedef": ("Kategorik", "İki kategori: Tutmadı, Tuttu"),
            },
            "series": (
                InlineData("aylik", ("ay", "sepet"), ALT_SERIES,
                           "Kurgusal veri: zincirin sekiz aylık ortalama sepet tutarı (TL)"),
                "aylik", "ay", "sepet", "Ay", "Ortalama sepet tutarı (TL)",
            ),
            "series_text": "Aşağıda önce sekiz kafenin günlük cirosu (yatay kesit), sonra zincirin sekiz aylık "
                           "ortalama sepet tutarı (zaman serisi) çizilir.",
            "concepts": CONCEPTS_ALT,
        },
    )


@cache
def alternative() -> LabSpec:
    return build(alternative_case())


def guess_type(series: pd.Series, role: str | None) -> str:
    """Önerilen tür: kimlik rolü kimlik etiketi; metin ve kategorik roller nominal; tam sayılar kesikli; diğer sayılar
    sürekli. Öğrenci öneriyi değiştirebilir."""

    numeric = pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)
    if role == KIMLIK:
        return IDENTITY_TYPE
    if role in (SAYISAL, ZAMAN) and not numeric:
        return "Nicel: sürekli"  # metin olarak saklanmış sayılar
    if role == IKILI or not numeric:
        return "Kategorik: nominal"
    values = series.dropna().astype(float)
    return "Nicel: kesikli" if (values == values.round()).all() else "Nicel: sürekli"


def validate(case: Case) -> None:
    """Zaman sütunu dosyada artan sırada ve tekrarsız olmalı (zaman serisi dönemlerin sırasıyla çizilir)."""

    if case.has(ZAMAN):
        values = case.data[case.roles[ZAMAN]].astype(float)
        if not (values.is_monotonic_increasing and values.is_unique):
            raise K.UploadError(f"“{case.label(ZAMAN)}” zaman sütunu dosyada artan sırada ve tekrarsız olmalı. "
                                "Dosyayı zamana göre sıralayın ya da zaman sütununu kaldırın.")


def sample() -> pd.DataFrame:
    return pd.DataFrame(list(ALT_ROWS), columns=[ALT_LABELS[name] for name in ALT_COLUMNS])


ROLES = (
    Role(SAYISAL, "Sayısal değişken", "sayisal", True, (1, 3, 4),
         "Gözlem değerleri, grafik, toplam ve ortalama için (ör. sınav puanı, ciro). Türü nicel olmalı.",
         allowed_types=("Nicel: kesikli", "Nicel: sürekli")),
    Role(KIMLIK, "Kimlik sütunu", "serbest", False, (1, 3),
         "Gözlemlerin adı ya da numarası; her gözlemde dolu ve farklı olmalı. Analitik değişken sayılmaz.",
         suggest=True, complete=True, unique=True, fixed_type=IDENTITY_TYPE),
    Role(IKILI, "İki kategorili değişken", "kategorik", False, (2, 4),
         "Tam iki kategorili sütun (ör. geçti, kaldı); oranı hesaplanır. Her gözlemde dolu olmalı.", levels=(2, 2),
         pick="Oranı hesaplanacak kategori (kod 1)", suggest=True, complete=True,
         allowed_types=("Kategorik: nominal", "Kategorik: sıralı")),
    Role(ZAMAN, "Zaman sütunu", "sayisal", False, (3,),
         "Yıl ya da dönem numarası; dosyada artan sırada ve tekrarsız olmalı. Seçilirse veri zaman serisi olarak "
         "çizilir.", complete=True),
)

CUSTOM = CustomLab(
    roles=ROLES,
    build=build,
    sample=sample,
    intro=(
        "Bir Excel (.xlsx) ya da CSV dosyası yükleyin. Sayısal değişken zorunludur; diğer roller ve veri tablosuna "
        "eklenecek sütunlar isteğe bağlıdır. Sayısal değişkeni boş olan satırlar analizden çıkarılır. Adım 2'de her "
        "sütunun istatistiksel türünü siz belirlersiniz."
    ),
    order_roles=(IKILI,),
    min_rows=3,
    extra_columns=True,
    type_choices=TYPE_CHOICES,
    guess_type=guess_type,
    validate=validate,
)

VARIANTS = TopicVariants(alternative=alternative, story=STORY, custom=CUSTOM)
