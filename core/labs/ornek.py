"""Uygulama sekmesinin ek veri kaynakları: kurgusal alternatif örnek ve öğrencinin kendi verisi.

Ders notlarının çözümlü örnekleri (``core.labs.konuNN``) değişmez. Her konu için ek olarak bir **genel uygulama**
yazılır (``core.labs.ornek_konuNN``): aynı adımlar, aynı numaralar ve aynı işlemler, fakat veri bir ``Case``'ten gelir.
Alternatif örnek, genel uygulamanın kurgusal bir veriyle kurulmuş hâlidir; "kendi verin" seçeneğinde aynı genel
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
from typing import Callable, Iterable, Mapping

import pandas as pd

from core.labs.runner import run_lab
from core.labs.spec import LabSpec, Operation

SOURCE_LABELS = {
    "notlar": "Notlardaki örnek",
    "alternatif": "Alternatif örnek",
    "kendi": "Kendi verin",
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

    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text.replace(".", ",").replace("-", "−")


def tex(value: float, decimals: int = 3) -> str:
    """Matematik ifadesi içindeki Türkçe sayı: virgül KaTeX'te ``{,}`` yazılır (0{,}32)."""

    return kisa(value, decimals).replace(",", "{,}")


def esit(value: float, decimals: int) -> str:
    """Gösterilen (yuvarlanmış) değer tam değere eşitse "=", değilse "\\approx" (notlardaki kural)."""

    shown = float(f"{value:.{decimals}f}")
    return "=" if abs(shown - value) <= 1e-9 * max(1.0, abs(value)) else "\\approx"


def liste(items: list[str]) -> str:
    """Türkçe sıralama: "A", "A ve B", "A, B ve C"."""

    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " ve " + items[-1]


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


def with_app_values(spec: LabSpec) -> LabSpec:
    """Kontrollerin beklenen değerlerini uygulamanın kendi hesabıyla doldurur (notlar dışındaki kaynaklar)."""

    run = run_lab(spec)
    steps = []
    for step in spec.steps:
        results = run.step_checks(step.number)
        checks = []
        for result in results:
            if not math.isfinite(result.value):
                raise ValueError(f"{result.check.label}: değer hesaplanamadı.")
            checks.append(replace(result.check, expected=result.value))
        steps.append(replace(step, checks=tuple(checks)))
    return replace(spec, steps=tuple(steps))


# --- Kendi verin: roller ----------------------------------------------------------------

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


@dataclass(frozen=True)
class CustomLab:
    """Bir konunun "kendi verin" tanımı: roller, genel uygulamayı kuran fonksiyon ve örnek dosya."""

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


@dataclass(frozen=True)
class TopicVariants:
    """Bir konunun ek veri kaynakları."""

    alternative: Callable[[], LabSpec]
    story: str
    """Alternatif örneğin tek cümlelik tanımı (sekmenin üstünde gösterilir)."""
    custom: CustomLab | None = None


# --- Kendi verin: seçimlerden örneğe -----------------------------------------------------

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
    dosyadaki sütun adı → tür seçeneği (``CustomLab.type_choices``).
    """

    roles: Mapping[str, str | None]
    extra: tuple[str, ...] = ()
    order: str = "alfabetik"
    picks: Mapping[str, str] = field(default_factory=dict)
    types: Mapping[str, str] = field(default_factory=dict)


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
        if not original:
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
    roles = {role.key: names[choices.roles[role.key]] for role in custom.roles if choices.roles.get(role.key)}
    labels = {item.name: item.original for item in selections}
    for role in custom.roles:
        if role.key not in roles:
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
        if role.key not in roles or role.use != "kategorik":
            continue
        column = roles[role.key]
        K.check_levels(data[column], labels[column], *role.levels)
        orders[column] = K.category_order(data[column], choices.order)
        if role.pick:
            pick = choices.picks.get(role.key)
            levels[role.key] = pick if pick in orders[column] else default_pick(orders[column])
    extra: dict[str, object] = {"order_text": ORDER_TEXT[choices.order]}
    if custom.type_choices is not None:
        extra["types"] = _types(custom, table, choices, selections, roles)
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
