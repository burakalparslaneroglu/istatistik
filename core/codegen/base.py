"""Uygulama tanımından Python ve R kodu üretmenin ortak çatısı."""

from __future__ import annotations

from dataclasses import dataclass

from core.labs import expr as E
from core.labs.spec import (
    CHARTS,
    BoxPlot,
    BoxSummary,
    Check,
    ClassTable,
    CrossTab,
    Derive,
    Draw,
    DrawDiscrete,
    Event,
    FrequencyTable,
    FromCounts,
    InlineData,
    JoinColumns,
    LabSpec,
    LabStep,
    MapCodes,
    MonteCarlo,
    NewSample,
    Operation,
    Outcomes,
    Scalar,
    ScalarTable,
    ScalarTarget,
    Selections,
)

LANGUAGES = ("Python", "R")

COURSE = "IKT 217 İstatistik I"
PALETTE = ("#107C89", "#B3392F", "#2F9E6B", "#C98A1B", "#6B4C9A", "#07373D")
"""Grafik serilerinin renkleri; uygulamada ve iki dilde aynı sırayla kullanılır."""
REFERENCE_COLORS = ("#07373D", "#6B4C9A", "#C98A1B")
"""Dikey başvuru çizgilerinin renkleri (ör. ortalama, medyan, çeyrekler)."""
HEAT_LOW = "#E7F2F3"
"""Isı haritasında sıfırın rengi: ana rengin açık tonu. Sıfır hücreler de beyaz zeminden ayrılır (notlardaki gibi)."""


@dataclass(frozen=True)
class LanguageInfo:
    name: str
    extension: str
    highlight: str
    mime: str


LANGUAGE_INFO = {
    "Python": LanguageInfo("Python", "py", "python", "text/x-python"),
    "R": LanguageInfo("R", "R", "r", "text/plain"),
}


def flatten(operations) -> list[Operation]:
    """İşlemler ve Monte Carlo döngülerinin içindeki işlemler, sırasıyla."""

    found: list[Operation] = []
    for op in operations:
        found.append(op)
        if isinstance(op, MonteCarlo):
            found.extend(flatten(op.body))
    return found


def expressions(operations) -> list[E.Expr]:
    """İşlemlerdeki bütün ifadeler (türetilmiş değişkenler, skalerler, döngü çıktıları)."""

    found: list[E.Expr] = []
    for op in flatten(operations):
        if isinstance(op, (Derive, Scalar)):
            found.append(op.expr)
        elif isinstance(op, ScalarTable):
            found.extend(expression for _, expression in op.rows)
        elif isinstance(op, MonteCarlo):
            found.extend(expression for _, expression in op.collect)
    return found


def functions_used(operations) -> set[str]:
    names: set[str] = set()
    for expression in expressions(operations):
        names |= E.functions_in(expression)
    return names


def uses_charts(operations) -> bool:
    return any(isinstance(op, CHARTS) for op in flatten(operations))


def _numbers(values) -> bool:
    return all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values)


def numeric_columns(spec: LabSpec) -> set[tuple[str, str]]:
    """Sayısal değerli veri çerçevesi sütunları (veri çerçevesi, sütun).

    Satır içi veride bütün değerleri sayı olan sütunlar (ör. kesikli rassal değişkenin değerleri x = 0, 1, 2, …) ile
    türetilen, olay göstergesi ve sayısal çekiliş sütunları. Sütun grafiğinde bu değerler kategori etiketi olarak
    yazılır: matplotlib sayısal konumlara çizip ara değerlere (0,5, 1,5, …) eksen işareti koyardı.
    """

    found: set[tuple[str, str]] = set()
    for step in spec.steps:
        for op in flatten(step.operations):
            if isinstance(op, (InlineData, FromCounts)):
                for position, column in enumerate(op.columns):
                    if _numbers(row[position] for row in op.rows):
                        found.add((op.frame, column))
            elif isinstance(op, Outcomes):
                found |= {(op.frame, column) for column, values in op.stages if _numbers(values)}
            elif isinstance(op, (Derive, Event, Draw, DrawDiscrete, MapCodes)):
                found.add((op.frame, op.name))
    return found


def signed_columns(spec: LabSpec) -> set[tuple[str, str]]:
    """Satır içi veride negatif değer içeren sütunlar (ör. geçersiz bir olasılık tablosu): sütun grafiğinde bu
    değerlerin etiketi sütunun altına yazılır."""

    found: set[tuple[str, str]] = set()
    for step in spec.steps:
        for op in flatten(step.operations):
            if isinstance(op, InlineData):
                for position, column in enumerate(op.columns):
                    values = [row[position] for row in op.rows]
                    if _numbers(values) and min(values) < 0:
                        found.add((op.frame, column))
    return found


def totals_of(spec: LabSpec) -> dict[str, tuple[bool, bool]]:
    """Her sonuç tablosunda ``Toplam`` satırı ve sütunu olup olmadığı (grafiklerde çıkarılır)."""

    found: dict[str, tuple[bool, bool]] = {}
    for step in spec.steps:
        for op in flatten(step.operations):
            if isinstance(op, (FrequencyTable, ClassTable)):
                found[op.result] = (op.totals, False)
            elif isinstance(op, CrossTab):
                if not op.margins:
                    found[op.result] = (False, False)
                elif op.percent is None:
                    found[op.result] = (True, True)
                elif op.percent == "satir":
                    found[op.result] = (False, True)
                else:
                    found[op.result] = (True, False)
    return found


def text(value: object) -> str:
    """Dizge veya sayı değişmezinin iki dilde de geçerli yazımı."""

    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return E.format_number(float(value))


def wrapped(opening: str, items: list[str], closing: str, width: int = 88, per_line: int | None = None,
            indent: str = "    ") -> list[str]:
    """Uzun listeleri okunur satırlara böler; ``per_line`` verilirse her satırda o kadar öğe."""

    if per_line:
        lines = [opening]
        for start in range(0, len(items), per_line):
            chunk = items[start:start + per_line]
            ending = "," if start + per_line < len(items) else ""
            lines.append(indent + ", ".join(chunk) + ending)
        lines.append(closing.lstrip())
        return lines
    lines: list[str] = []
    current = opening
    indent = " " * len(opening)
    for index, item in enumerate(items):
        piece = item + (", " if index < len(items) - 1 else "")
        if len(current) + len(piece.rstrip()) > width and current.strip() not in (opening.strip(), ""):
            lines.append(current.rstrip())
            current = indent
        current += piece
    lines.append(current.rstrip() + closing)
    return lines


class Generator:
    """Tek bir hedef dil için kod üreticisi. Alt sınıflar dili tanımlar."""

    language = ""
    comment = "#"

    def __init__(self, spec: LabSpec) -> None:
        self.spec = spec
        self.has_checks = any(step.checks for step in spec.steps)
        self.totals = totals_of(spec)
        self.numeric_columns = numeric_columns(spec)
        self.signed_columns = signed_columns(spec)
        self.quiet = False
        """Monte Carlo döngüsü içinde ekrana yazdırma satırları üretilmez."""
        self.scalar_refs = {
            check.target.name for step in spec.steps for check in step.checks if isinstance(check.target, ScalarTarget)
        }

    # --- Alt sınıfların doldurduğu parçalar -------------------------------
    def imports(self, operations: tuple[Operation, ...], *, script: bool = False) -> list[str]:
        return []

    def output_setup(self) -> list[str]:
        return []

    def helpers(self, operations: tuple[Operation, ...], *, with_checks: bool) -> list[str]:
        return []

    def operation(self, op: Operation) -> list[str]:
        raise NotImplementedError

    def check_lines(self, checks: tuple[Check, ...]) -> list[str]:
        raise NotImplementedError

    def closing(self) -> list[str]:
        return []

    # --- Ortak yapı -------------------------------------------------------
    def banner(self, title: str) -> list[str]:
        rule = self.comment + " " + "=" * 74
        return [rule, f"{self.comment} {title}", rule]

    def header(self) -> list[str]:
        c = self.comment
        topic = self.spec.topic_key[-2:]
        if self.spec.kind == "sezgi":
            return [
                f"{c} {COURSE}",
                f"{c} Konu {topic} sezgi deneyi: {self.spec.title}",
                f"{c} Ders notları §{self.spec.note_section} ile ilişkili kontrollü simülasyon.",
                f"{c}",
                f"{c} Veri bu betikte üretilir; veri üretim süreci (DGP) aşağıda açıkça yazılıdır.",
                f"{c} Rastgele sayı üreteçleri diller arasında farklıdır: Python sürümü uygulamadaki",
                f"{c} sayıların aynısını verir, R aynı dağılımdan farklı çekiliş yapar.",
                "",
            ]
        return [
            f"{c} {COURSE}",
            f"{c} Konu {topic} uygulaması: {self.spec.title}",
            f"{c} Ders notlarındaki çözümlü örneklerle aynı adımlar (§{self.spec.note_section}).",
            f"{c}",
            f"{c} Veri: ders notlarındaki örnek veri setleri; bu betiğin içinde yazılıdır.",
            f"{c} Betik sonunda sonuçlar ders notlarındaki basılı değerlerle karşılaştırılır.",
            "",
        ]

    def step_title(self, step: LabStep) -> str:
        word = "Deney" if self.spec.kind == "sezgi" else "Adım"
        return f"{word} {step.number}: {step.title}   ({step.note.label()})"

    def render_operations(self, operations: tuple[Operation, ...]) -> list[str]:
        lines: list[str] = []
        for op in operations:
            block = self.operation(op)
            if block:
                lines.extend(block)
                lines.append("")
        return lines

    def step_snippet(self, number: int) -> str:
        """Uygulama ekranında gösterilen, tek adımlık kod parçası."""

        step = self.spec.step(number)
        if not step.operations:
            return ""
        lines: list[str] = []
        lines.extend(self.imports(step.operations))
        lines.extend(self.helpers(step.operations, with_checks=False))
        if number > 1 and self.spec.kind != "sezgi" and self.depends_on_earlier(step):
            lines.append(f"{self.comment} Önceki adımlar çalıştırılmış olmalıdır (veri ve tablolar hazır).")
            lines.append("")
        lines.extend(self.render_operations(step.operations))
        return "\n".join(lines).rstrip() + "\n"

    def depends_on_earlier(self, step: LabStep) -> bool:
        """Adım kendi verisini kurmuyorsa önceki adımların çıktısına dayanır."""

        sources = (InlineData, FromCounts, NewSample, Outcomes, Selections)
        created = {op.frame for op in step.operations if isinstance(op, sources)}
        used: set[str] = set()
        for op in flatten(step.operations):
            for name in ("frame", "source", "table"):
                value = getattr(op, name, None)
                if isinstance(value, str):
                    used.add(value)
            if isinstance(op, (BoxSummary, BoxPlot)):
                used |= {frame for frame, _, _ in op.series}  # kutu grafiği serileri
            if isinstance(op, JoinColumns):
                used |= {table for _, table, _ in op.columns}  # yan yana toplanan tablolar
        produced = {getattr(op, "result", None) for op in step.operations}
        return bool(used - created - produced)

    def script(self) -> str:
        """Bütün uygulamayı tek başına çalışan bir dosya olarak üretir."""

        operations: tuple[Operation, ...] = tuple(op for step in self.spec.steps for op in step.operations)
        lines = self.header()
        lines.extend(self.imports(operations, script=True))
        lines.extend(self.output_setup())
        lines.extend(self.helpers(operations, with_checks=self.has_checks))
        for step in self.spec.steps:
            if not step.operations and not step.checks:
                continue
            lines.extend(self.banner(self.step_title(step)))
            lines.append("")
            lines.extend(self.render_operations(step.operations))
            if step.checks:
                lines.extend(self.check_lines(step.checks))
                lines.append("")
        if self.has_checks:
            lines.extend(self.closing())
        return "\n".join(lines).rstrip() + "\n"


def generator(spec: LabSpec, language: str) -> Generator:
    from core.codegen.python_gen import PythonGenerator
    from core.codegen.r_gen import RGenerator

    classes = {"Python": PythonGenerator, "R": RGenerator}
    if language not in classes:
        raise ValueError(f"Desteklenmeyen dil: {language}")
    return classes[language](spec)


def render_script(spec: LabSpec, language: str) -> str:
    return generator(spec, language).script()


def render_step(spec: LabSpec, number: int, language: str) -> str:
    return generator(spec, language).step_snippet(number)


def script_filename(spec: LabSpec, language: str) -> str:
    return f"ikt217_{spec.topic_key}_uygulama.{LANGUAGE_INFO[language].extension}"
