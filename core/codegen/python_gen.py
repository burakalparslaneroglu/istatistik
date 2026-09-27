"""Uygulama tanımından Python (pandas + matplotlib) kodu üretir.

Üretilen kod, uygulamanın hesabıyla aynı işlem sırasını izler; sayılar bit düzeyinde aynıdır.
"""

from __future__ import annotations

import re

from core.codegen.base import (
    PALETTE,
    REFERENCE_COLORS,
    Generator,
    flatten,
    functions_used,
    text,
    uses_charts,
    wrapped,
)
from core.labs import expr as E
from core.labs.spec import (
    TOTAL,
    BarChart,
    BoxPlot,
    BoxSummary,
    CellTarget,
    Check,
    ClassHistogram,
    ClassTable,
    CompareBarChart,
    Count,
    CrossTab,
    Derive,
    DotPlot,
    Draw,
    DrawCategory,
    Event,
    FrequencyTable,
    FromCounts,
    GroupedBarChart,
    Groups,
    GroupSummary,
    Histogram,
    InlineData,
    JoinColumns,
    LineChart,
    MapCodes,
    MonteCarlo,
    NewSample,
    Operation,
    Outcomes,
    PairStatistic,
    Percentile,
    PieChart,
    Scalar,
    ScalarTable,
    ScalarTarget,
    ScatterPlot,
    Selections,
    Shape,
    ShowFrame,
    Statistic,
    StatTarget,
    StemLeaf,
    TableTarget,
    VariableTypes,
)
from core.labs.tables import class_edges

_STAT = {
    "count": "count()", "sum": "sum()", "mean": "mean()", "median": "median()", "mode": "mode().item()",
    "mode_freq": "value_counts().max()", "prod": "prod()", "min": "min()", "max": "max()", "var": "var()",
    "std": "std()", "nunique": "nunique()", "value": "item()",
}
"""İstatistiğin pandas karşılığı; ``mode().item()`` birden fazla mod varsa hata verir (tek mod beklenir).
``var()`` ve ``std()`` pandas'ta örneklem ölçüleridir (payda n − 1)."""
_SCIPY_FUNCTIONS = {"normcdf", "normpdf", "norminv"}
_MATH_FUNCTIONS = set(E.COUNTING_FUNCTIONS)
_FUNCTIONS = {
    "log": "np.log", "exp": "np.exp", "sqrt": "np.sqrt", "abs": "np.abs", "maximum": "np.maximum",
    "minimum": "np.minimum", "round": "np.rint", "floor": "np.floor", "cumprod": "np.cumprod",
    "cummean": "np.cumsum({0}) / np.arange(1, len({0}) + 1)", "seq": "np.arange(1, len({0}) + 1)",
    "factorial": "math.factorial(int({0}))", "comb": "math.comb(int({0}), int({1}))",
    "perm": "math.perm(int({0}), int({1}))",
    "normcdf": "stats.norm.cdf", "normpdf": "stats.norm.pdf", "norminv": "stats.norm.ppf",
    **{name: f"np.where({{0}} {symbol} {{1}}, 1.0, 0.0)" for name, symbol in E.COMPARISONS.items()},
}

_NUMBER_TEXT = [
    "def sayi_metni(deger, basamak=0, yuzde=False):",
    '    """Grafik etiketleri için Türkçe sayı: ondalık virgül, yüzde işareti sayıdan önce."""',
    '    metin = f"{deger:.{basamak}f}".replace(".", ",")',
    '    return "%" + metin if yuzde else metin',
]
_BOUNDARY_TEXT = [
    "def sinir_metni(deger):",
    '    """Sınıf sınırının yazımı: ondalık virgül (ör. 12,5)."""',
    '    return f"{deger:.10g}".replace(".", ",")',
]
_PERCENTILE = [
    "def yuzdelik(degerler, p):",
    '    """Ders kuralı: L_p = (p/100)(n + 1). L_p tam sayı değilse komşu iki gözlem arasında doğrusal ara',
    "    değer; L_p ≤ 1 ise en küçük, L_p ≥ n ise en büyük gözlem. np.percentile(degerler, p,",
    '    method="weibull") aynı sonucu verir; np.percentile varsayılanı farklı bir kural kullanır."""',
    "    x = np.sort(np.asarray(degerler, dtype=float))",
    "    n = len(x)",
    "    konum = p / 100 * (n + 1)",
    "    if konum <= 1:",
    "        return x[0]",
    "    if konum >= n:",
    "        return x[-1]",
    "    k = int(np.floor(konum))",
    "    return x[k - 1] + (konum - k) * (x[k] - x[k - 1])",
]


_BOX_SUMMARY = [
    "def kutu_ozeti(degerler):",
    '    """Kutu grafiği özeti: çeyrekler ders kuralıyla (yuzdelik); bıyıklar Q1 − 1,5·IQR ile Q3 + 1,5·IQR',
    '    sınırlarının içindeki en uç gözlemlere uzanır; sınırların dışındakiler aykırı değer adayıdır."""',
    "    x = np.sort(np.asarray(degerler, dtype=float))",
    "    q1, medyan, q3 = yuzdelik(x, 25), yuzdelik(x, 50), yuzdelik(x, 75)",
    "    iqr = q3 - q1",
    "    alt, ust = q1 - 1.5 * iqr, q3 + 1.5 * iqr",
    "    icerde = x[(x >= alt) & (x <= ust)]",
    "    return pd.Series({",
    '        "en_kucuk": x[0], "q1": q1, "medyan": medyan, "q3": q3, "en_buyuk": x[-1], "iqr": iqr,',
    '        "alt_sinir": alt, "ust_sinir": ust, "alt_biyik": icerde.min(), "ust_biyik": icerde.max(),',
    '        "aykiri_sayisi": float(((x < alt) | (x > ust)).sum()),',
    "    })",
]


def _render(expression: E.Expr, dialect: E.Dialect) -> str:
    """İfadenin Python yazımı; tam sayı değişmezinin etrafındaki gereksiz ``int()`` atılır (``math.comb(5, 2)``)."""

    return re.sub(r"\bint\((\d+)\)", r"\1", E.render(expression, dialect))


def _list(values) -> str:
    return "[" + ", ".join(text(value) for value in values) + "]"


def _quote(value: str) -> str:
    """Çift tırnaklı dizge içinde düz metin."""

    return value.replace("\\", "\\\\").replace('"', '\\"')


def _fstring(value: str) -> str:
    """f-dizgesi içinde düz metin: tırnak, ters bölü ve süslü parantez kaçırılır."""

    return _quote(value).replace("{", "{{").replace("}", "}}")


def _needs_numpy(operations) -> bool:
    """numpy yalnız rastgele çekiliş, grup etiketi, histogram, yüzdelik, veriden sınıf sınırı veya ifade
    fonksiyonu varsa gerekir."""

    numpy_ops = (Groups, NewSample, Draw, DrawCategory, Histogram, MonteCarlo, Percentile, BoxSummary, BoxPlot)
    for op in flatten(operations):
        if isinstance(op, numpy_ops) or (isinstance(op, ClassTable) and op.lower is None):
            return True
    return bool(functions_used(operations) - _SCIPY_FUNCTIONS - _MATH_FUNCTIONS)


def _needs_percentile(operations) -> bool:
    """Ders kuralıyla yüzdelik fonksiyonu: yüzdelik işlemi ya da kutu grafiği özeti varsa."""

    for op in flatten(operations):
        if (isinstance(op, Percentile) and op.method == "ders") or isinstance(op, (BoxSummary, BoxPlot)):
            return True
    return False


def _stat_call(source: str, stat: str) -> str:
    return f"{source}.{_STAT[stat]}"


def _labelled_charts(operations) -> bool:
    """Değer etiketi yazan grafikler (Türkçe sayı yardımcısı gerekir)."""

    for op in flatten(operations):
        if isinstance(op, (BarChart, CompareBarChart)) or (isinstance(op, GroupedBarChart) and op.labels):
            return True
        if isinstance(op, ClassHistogram) and op.labels:
            return True
    return False


def _where(frame: str, where) -> str:
    column, value = where
    return f'{frame}["{column}"] == {text(value)}'


class PythonGenerator(Generator):
    language = "Python"
    comment = "#"

    def dialect(self, frame: str) -> E.Dialect:
        return E.Dialect(variable=lambda name: f'{frame}["{name}"]', functions=_FUNCTIONS, power="**")

    # --- Başlık ve yardımcılar ------------------------------------------
    def imports(self, operations: tuple[Operation, ...], *, script: bool = False) -> list[str]:
        flat = flatten(operations)
        standard = ["import sys"] if script else []
        if functions_used(operations) & _MATH_FUNCTIONS:
            standard.append("import math")
        tools = {"product" for op in flat if isinstance(op, Outcomes) and len(op.stages) > 1}
        tools |= {"permutations" if op.ordered else "combinations" for op in flat if isinstance(op, Selections)}
        tools = sorted(tools)
        if tools:
            standard.append(f"from itertools import {', '.join(tools)}")
        lines = standard + [""] if standard else []
        if uses_charts(operations):
            lines.append("import matplotlib.pyplot as plt")
        if _needs_numpy(operations):
            lines.append("import numpy as np")
        lines.append("import pandas as pd")
        if functions_used(operations) & _SCIPY_FUNCTIONS:
            lines.append("from scipy import stats")
        lines.append("")
        return lines

    def output_setup(self) -> list[str]:
        return [
            "# Windows'ta çıktı bir dosyaya ya da başka bir programa yönlendirildiğinde Python yerel kod",
            "# sayfasını (ör. cp1254) kullanır ve bazı karakterleri yazamaz; çıktı UTF-8 olsun.",
            'if hasattr(sys.stdout, "reconfigure"):',
            '    sys.stdout.reconfigure(encoding="utf-8")',
            "",
        ]

    def helpers(self, operations: tuple[Operation, ...], *, with_checks: bool) -> list[str]:
        lines: list[str] = [""]  # üst düzey fonksiyonlardan önce iki boş satır (PEP 8)
        flat = flatten(operations)
        if _labelled_charts(operations):
            lines += _NUMBER_TEXT + ["", ""]
        if any(isinstance(op, ClassTable) for op in flat):
            lines += _BOUNDARY_TEXT + ["", ""]
        if _needs_percentile(operations):
            lines += _PERCENTILE + ["", ""]
        if any(isinstance(op, (BoxSummary, BoxPlot)) for op in flat):
            lines += _BOX_SUMMARY + ["", ""]
        if with_checks:
            lines += [
                "def kontrol_et(etiket, deger, beklenen, ondalik=4):",
                '    """Hesaplanan değeri ders notlarındaki basılı değerle karşılaştırır."""',
                "    tolerans = 0.5 * 10 ** (-ondalik) + 1e-12",
                '    durum = "OK  " if abs(deger - beklenen) <= tolerans else "HATA"',
                '    print(f"  {durum} {etiket}: {deger:.{ondalik}f}  (notlar: {beklenen:.{ondalik}f})")',
                '    assert abs(deger - beklenen) <= tolerans, f"{etiket} notlarla uyuşmuyor."',
                "",
                "",
            ]
        return lines if len(lines) > 1 else []

    # --- İşlemler --------------------------------------------------------
    def operation(self, op: Operation) -> list[str]:
        lines = self._operation(op)
        if self.quiet:
            lines = [line for line in lines if not line.lstrip().startswith("print(")]
        return lines

    def _operation(self, op: Operation) -> list[str]:  # noqa: C901 - tek dağıtıcı, işlem türü başına bir blok
        if isinstance(op, InlineData):
            return self._inline(op)
        if isinstance(op, FromCounts):
            return self._from_counts(op)
        if isinstance(op, Outcomes):
            return self._outcomes(op)
        if isinstance(op, Selections):
            return self._selections(op)
        if isinstance(op, VariableTypes):
            rows = [f'    ({text(v)}, {text(k)}, {text(d)}),' for v, k, d in op.rows]
            return [
                "# Yazılımın saklama türü: sayı (int64/float64) ya da metin (object)",
                f"print({op.frame}.dtypes)",
                "# İstatistiksel tür yazılımdan değil, değişkenin anlamından gelir",
                f"{op.result} = pd.DataFrame(",
                "    [",
                *[f"    {row}" for row in rows],
                "    ],",
                '    columns=["degisken", "tur", "ayrinti"],',
                ').set_index("degisken")',
                f"print({op.result})",
            ]
        if isinstance(op, Event):
            members = ", ".join(str(value) for value in op.values)
            return [
                f"# {op.comment}: {op.column} ∈ {{{members}}} olan satırlar 1, diğerleri 0",
                f'{op.frame}["{op.name}"] = {op.frame}["{op.column}"].isin({_list(op.values)}).astype(int)',
            ]
        if isinstance(op, ShowFrame):
            return [f"# {op.comment}", f"print({op.frame}[{_list(op.columns)}])"]
        if isinstance(op, MapCodes):
            pairs = ", ".join(f"{text(label)}: {text(code)}" for label, code in op.mapping)
            return [
                f"# {op.comment}",
                f'{op.frame}["{op.name}"] = {op.frame}["{op.source}"].map({{{pairs}}})',
                f'print({op.frame}[["{op.source}", "{op.name}"]].head(8))',
            ]
        if isinstance(op, Groups):
            return [
                f"# {op.comment}",
                f'{op.frame}["{op.name}"] = np.repeat({_list(op.labels)}, {_list(op.sizes)})',
            ]
        if isinstance(op, Derive):
            rhs = _render(op.expr, self.dialect(op.frame))
            return [f"# {op.comment}", f'{op.frame}["{op.name}"] = {rhs}']
        if isinstance(op, NewSample):
            frame = f'{op.frame} = pd.DataFrame({{"id": np.arange(1, {op.nobs} + 1)}})'
            if op.seed is None:
                return [frame]
            return [
                "# Sabit tohum: betik her çalıştırmada aynı veriyi üretir",
                f"rng = np.random.default_rng({op.seed})",
                frame,
            ]
        if isinstance(op, Draw):
            a, b = E.format_number(op.first), E.format_number(op.second)
            method = {"normal": "normal", "uniform": "uniform", "beta": "beta", "gamma": "gamma"}[op.distribution]
            call = f"rng.{method}({a}, {b}, size=len({op.frame}))"
            return [f"# {op.comment}", f'{op.frame}["{op.name}"] = {call}']
        if isinstance(op, DrawCategory):
            return self._draw_category(op)
        if isinstance(op, Shape):
            columns = f".drop(columns={_list(op.exclude)})" if op.exclude else ""
            note = "  # kimlik sütunu değişken sayılmaz" if op.exclude else ""
            return [
                f"{op.observations} = len({op.frame})  # gözlem sayısı",
                f"{op.variables} = {op.frame}{columns}.shape[1]{note}",
                f'print("Gözlem sayısı:", {op.observations}, "| Değişken sayısı:", {op.variables})',
            ]
        if isinstance(op, Count):
            return [
                f"# {op.comment}",
                f'{op.name} = int(({op.frame}["{op.column}"] == {text(op.value)}).sum())',
                f'print("{_quote(op.comment)}:", {op.name})',
            ]
        if isinstance(op, Statistic):
            source = (f'{op.frame}["{op.variable}"]' if op.where is None
                      else f'{op.frame}.loc[{_where(op.frame, op.where)}, "{op.variable}"]')
            return [
                f"# {op.comment}",
                f"{op.name} = {_stat_call(source, op.stat)}",
                f'print(f"{_fstring(op.comment)}: {{{op.name}:.{op.decimals}f}}")',
            ]
        if isinstance(op, PairStatistic):
            method = {"cov": "cov", "corr": "corr"}[op.stat]
            note = "  # payda n − 1" if op.stat == "cov" else "  # Pearson korelasyonu"
            return [
                f"# {op.comment}",
                f'{op.name} = {op.frame}["{op.x}"].{method}({op.frame}["{op.y}"]){note}',
                f'print(f"{_fstring(op.comment)}: {{{op.name}:.{op.decimals}f}}")',
            ]
        if isinstance(op, Scalar):
            rhs = _render(op.expr, self.dialect(""))
            shown = f"%{{{op.name}:.{op.decimals}f}}" if op.percent else f"{{{op.name}:.{op.decimals}f}}"
            return [f"# {op.comment}", f"{op.name} = {rhs}", f'print(f"{_fstring(op.comment)}: {shown}")']
        if isinstance(op, ScalarTable):
            dialect = self.dialect("")
            rows = [f"    {text(label)}: {_render(expression, dialect)}," for label, expression in op.rows]
            return [
                f"{op.result} = pd.DataFrame({{\"deger\": {{", *rows, "}})",
                f"print({op.result}.round({op.decimals}))",
            ]
        if isinstance(op, GroupSummary):
            lines = [f'{op.result} = {op.frame}.groupby("{op.by}").agg(']
            for name, variable, stat in op.columns:
                lines.append(f'    {name}=("{variable}", "{stat}"),')
            lines += [f").reindex({_list(op.order)})", f"print({op.result}.round(4))"]
            return lines
        if isinstance(op, FrequencyTable):
            return self._frequency(op)
        if isinstance(op, CrossTab):
            return self._crosstab(op)
        if isinstance(op, JoinColumns):
            items = [f'    {text(name)}: {table}["{column}"].to_numpy(),' for name, table, column in op.columns]
            return [
                f"{op.result} = pd.DataFrame({{",
                *items,
                f"}}, index={op.columns[0][1]}.index)",
                f"print({op.result}.round({op.decimals}))",
            ]
        if isinstance(op, BoxSummary):
            items = [f'    {text(label)}: kutu_ozeti({frame}["{variable}"]),' for frame, variable, label in op.series]
            return [
                "# Beş sayı özeti, IQR, aykırı değer sınırları ve bıyık uçları",
                f"{op.result} = pd.DataFrame({{",
                *items,
                "})",
                f"print({op.result}.round(3))",
            ]
        if isinstance(op, ClassTable):
            return self._class_table(op)
        if isinstance(op, StemLeaf):
            return self._stem_leaf(op)
        if isinstance(op, Percentile):
            return self._percentile(op)
        if isinstance(op, ClassHistogram):
            return self._class_histogram(op)
        if isinstance(op, DotPlot):
            return self._dot_plot(op)
        if isinstance(op, BarChart):
            return self._bar(op)
        if isinstance(op, GroupedBarChart):
            return self._grouped(op)
        if isinstance(op, CompareBarChart):
            return self._compare(op)
        if isinstance(op, PieChart):
            return self._pie(op)
        if isinstance(op, LineChart):
            return self._line(op)
        if isinstance(op, ScatterPlot):
            return [
                "fig, ax = plt.subplots(figsize=(7, 5))",
                f'ax.scatter({op.frame}["{op.x}"], {op.frame}["{op.y}"], color="{PALETTE[0]}", s=45, zorder=3)',
                "ax.grid(alpha=0.3)",
                *self._axes(op.x_label, op.y_label, op.title),
            ]
        if isinstance(op, BoxPlot):
            return self._box_plot(op)
        if isinstance(op, Histogram):
            return self._histogram(op)
        if isinstance(op, MonteCarlo):
            return self._monte_carlo(op)
        raise TypeError(f"Python üreticisi bu işlemi tanımıyor: {type(op).__name__}")

    @staticmethod
    def _axes(x_label: str, y_label: str, title: str, legend: bool | str = False) -> list[str]:
        lines = [
            f'ax.set_xlabel("{_quote(x_label)}")',
            f'ax.set_ylabel("{_quote(y_label)}")',
            f'ax.set_title("{_quote(title)}")',
        ]
        if legend == "disarida":
            lines.append('ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))  # açıklama sütunların dışında')
        elif legend:
            lines.append("ax.legend()")
        return lines + ["plt.tight_layout()", "plt.show()"]

    def _inline(self, op: InlineData) -> list[str]:
        lines = [f"# {op.comment}"]
        if op.layout and len(op.columns) == 1:
            name = f"{op.frame}_ham"
            items = [text(row[0]) for row in op.rows]
            lines += wrapped(f"{name} = [", items, "]", per_line=op.layout)
            lines += [f'{op.frame} = pd.DataFrame({{"{op.columns[0]}": {name}}})']
        else:
            lines.append(f"{op.frame} = pd.DataFrame({{")
            for position, column in enumerate(op.columns):
                values = [text(row[position]) for row in op.rows]
                lines += wrapped(f'    "{column}": [', values, "],")
            lines.append("})")
        lines.append(f"print({op.frame})" if len(op.rows) <= 12 else f"print({op.frame}.head())  # ilk beş gözlem")
        return lines

    def _from_counts(self, op: FromCounts) -> list[str]:
        name = f"{op.frame}_sayim"
        rows = ["        (" + ", ".join(text(value) for value in row) + ")," for row in op.rows]
        columns = _list((*op.columns, "sayi"))
        return [
            f"# {op.comment}",
            f"{name} = pd.DataFrame(",
            "    [",
            *rows,
            "    ],",
            f"    columns={columns},",
            ")",
            '# Her satır "sayi" kez tekrarlanır: bir satır = bir gözlem',
            f'satirlar = {name}.index.repeat({name}["sayi"])',
            f"{op.frame} = {name}.loc[satirlar, {_list(op.columns)}].reset_index(drop=True)",
            f"print(len({op.frame}))  # gözlem sayısı",
        ]

    def _outcomes(self, op: Outcomes) -> list[str]:
        shown = f"print({op.frame})" if self._row_count(op) <= 12 else f"print({op.frame}.head())  # ilk beş sonuç"
        if len(op.stages) == 1:
            name, values = op.stages[0]
            return [
                f"# {op.comment}",
                f"{op.frame} = pd.DataFrame({{{text(name)}: {_list(values)}}})",
                shown,
                f'print("Sonuç sayısı:", len({op.frame}))',
            ]
        stages = [f"    {text(name)}: {_list(values)}," for name, values in op.stages]
        return [
            f"# {op.comment}",
            f"{op.frame}_asamalar = {{",
            *stages,
            "}",
            "# Bütün bileşimler (çarpım kuralı): ilk aşama en yavaş, son aşama en hızlı değişir",
            f"{op.frame} = pd.DataFrame(list(product(*{op.frame}_asamalar.values())),",
            f"{' ' * len(op.frame)}                columns=list({op.frame}_asamalar))",
            shown,
            f'print("Sonuç sayısı:", len({op.frame}))',
        ]

    @staticmethod
    def _row_count(op: Outcomes) -> int:
        count = 1
        for _, values in op.stages:
            count *= len(values)
        return count

    def _selections(self, op: Selections) -> list[str]:
        method = "permutations" if op.ordered else "combinations"
        note = "sıra önemli: permütasyonlar" if op.ordered else "sıra önemsiz: kombinasyonlar"
        return [
            f"# {op.comment} ({note})",
            f"{op.frame}_ogeler = {_list(op.items)}",
            f"{op.frame} = pd.DataFrame(list({method}({op.frame}_ogeler, {op.k})), columns={_list(op.columns)})",
            f"print({op.frame}.head(10))",
            f'print("Seçim sayısı:", len({op.frame}))',
        ]

    def _draw_category(self, op: DrawCategory) -> list[str]:
        categories = f"{op.name}_kategoriler"
        lines = [
            f"# {op.comment}",
            "# u ~ Tekdüze(0, 1); kategori, birikimli olasılığı u'yu ilk aşan kategoridir",
            f"u = rng.random(len({op.frame}))",
            f"{categories} = np.array({_list(op.categories)})",
        ]
        if not op.by:
            probs = op.probabilities[0][1]
            return lines + [
                f"esik = np.cumsum({_list(probs)})",
                "esik[-1] = 1.0  # yuvarlama hatasına karşı son eşik tam 1",
                f'{op.frame}["{op.name}"] = {categories}[np.searchsorted(esik, u, side="right")]',
            ]
        if len(op.by) == 1:
            entries = [f"    {text(condition[0])}: {_list(probs)}," for condition, probs in op.probabilities]
            selection = f'({op.frame}["{op.by[0]}"] == kosul).to_numpy()'
        else:
            entries = [
                f"    ({', '.join(text(value) for value in condition)}): {_list(probs)},"
                for condition, probs in op.probabilities
            ]
            selection = " & ".join(
                f'({op.frame}["{column}"] == kosul[{index}]).to_numpy()' for index, column in enumerate(op.by)
            )
        return lines + [
            f"{op.name}_olasilik = {{",
            *entries,
            "}",
            f'{op.frame}["{op.name}"] = ""',
            f"for kosul, olasilik in {op.name}_olasilik.items():",
            f"    secili = {selection}",
            "    esik = np.cumsum(olasilik)",
            "    esik[-1] = 1.0",
            f'    {op.frame}.loc[secili, "{op.name}"] = {categories}[np.searchsorted(esik, u[secili], side="right")]',
        ]

    def _frequency(self, op: FrequencyTable) -> list[str]:
        order = f"{op.result}_sira"
        lines = [
            f"{order} = {_list(op.order)}",
            f'sayilar = {op.frame}["{op.variable}"].value_counts()  # her kategorideki gözlem sayısı',
            f'{op.result} = sayilar.reindex({order}, fill_value=0).to_frame("frekans")',
        ]
        if op.relative:
            lines += [
                f'{op.result}["goreli"] = {op.result}["frekans"] / {op.result}["frekans"].sum()  # r = f / n',
                f'{op.result}["yuzde"] = 100 * {op.result}["goreli"]  # p = 100 r',
            ]
        if op.totals:
            lines.append(f'{op.result}.loc["{TOTAL}"] = {op.result}.sum()')
        lines.append(f"print({op.result}.round(3))")
        return lines

    def _crosstab(self, op: CrossTab) -> list[str]:
        lines: list[str] = []
        data = op.frame
        if op.where is not None:
            data = f"{op.result}_veri"
            lines += [
                f"# Yalnız {op.where[0]} = {op.where[1]} olan gözlemler",
                f"{data} = {op.frame}[{_where(op.frame, op.where)}]",
            ]
        counts = op.result if op.percent is None else f"{op.result}_sayi"
        if op.weights is None:
            lines.append(f'{counts} = pd.crosstab({data}["{op.row}"], {data}["{op.column}"]).reindex(')
        else:
            lines += [
                f'# Hücreler gözlem sayısı değil, "{op.weights}" sütununun toplamıdır',
                f'{counts} = pd.crosstab({data}["{op.row}"], {data}["{op.column}"], values={data}["{op.weights}"],',
                f'{" " * (len(counts) + 15)}aggfunc="sum").fillna(0).reindex(',
            ]
        lines += [
            f"    index={_list(op.row_order)},",
            f"    columns={_list(op.column_order)},",
            "    fill_value=0,",
            ")",
        ]
        if op.percent is None:
            if op.margins:
                lines += [
                    f'{op.result}.loc["{TOTAL}"] = {op.result}.sum()  # sütun toplamları',
                    f'{op.result}["{TOTAL}"] = {op.result}.sum(axis=1)  # satır toplamları',
                ]
            return lines + [f"print({op.result})"]
        if op.percent == "satir":
            lines += [
                "# Satır yüzdesi: payda satır toplamıdır",
                f"{op.result} = {counts}.div({counts}.sum(axis=1), axis=0) * 100",
            ]
            if op.margins:
                lines.append(f'{op.result}["{TOTAL}"] = {op.result}.sum(axis=1)')
        else:
            lines += [
                "# Sütun yüzdesi: payda sütun toplamıdır",
                f"{op.result} = {counts}.div({counts}.sum(axis=0), axis=1) * 100",
            ]
            if op.margins:
                lines.append(f'{op.result}.loc["{TOTAL}"] = {op.result}.sum()')
        return lines + [f"print({op.result}.round({op.decimals}))"]

    def _class_table(self, op: ClassTable) -> list[str]:
        source = f'{op.frame}["{op.variable}"]'
        r = op.result
        if op.lower is None:
            lines = [
                f"h = {E.format_number(op.width)}  # sınıf genişliği",
                f"alt_sinir = np.floor({source}.min() / h) * h  # en küçük değeri içeren h katı",
                f"k = int(np.floor(({source}.max() - alt_sinir) / h)) + 1  # en büyük değeri de kapsayan sınıf sayısı",
                "kenarlar = alt_sinir + h * np.arange(k + 1)",
            ]
        else:
            edges = class_edges(None, op.width, op.lower, op.classes)
            lines = wrapped("kenarlar = [", [E.format_number(value) for value in edges], "]  # sınıf sınırları")
        if op.row_labels == "ust":
            labels = 'etiketler = [f"x < {sinir_metni(b)}" for b in kenarlar[1:]]'
        else:
            labels = ('etiketler = [f"{sinir_metni(a)} ≤ x < {sinir_metni(b)}" '
                      'for a, b in zip(kenarlar[:-1], kenarlar[1:])]')
        lines += [
            "# Sınıflar [alt, üst): alt sınır dahil, üst sınır hariç",
            f"siniflar = pd.cut({source}, bins=kenarlar, right=False)",
            "frekans = siniflar.value_counts(sort=False).to_numpy()  # her sınıftaki gözlem sayısı",
            "n_sinif = frekans.sum()",
            labels,
            f'{r} = pd.DataFrame({{"alt": kenarlar[:-1], "ust": kenarlar[1:]}}, index=etiketler)',
        ]
        steps = {
            "orta_nokta": f'{r}["orta_nokta"] = ({r}["alt"] + {r}["ust"]) / 2  # m = (alt + üst) / 2',
            "frekans": f'{r}["frekans"] = frekans',
            "goreli": f'{r}["goreli"] = frekans / n_sinif  # r = f / n',
            "yuzde": f'{r}["yuzde"] = 100 * (frekans / n_sinif)  # p = 100 r',
            "kumulatif_frekans": f'{r}["kumulatif_frekans"] = frekans.cumsum()  # F = f₁ + ... + fⱼ',
            "kumulatif_goreli": f'{r}["kumulatif_goreli"] = frekans.cumsum() / n_sinif',
            "kumulatif_yuzde": f'{r}["kumulatif_yuzde"] = 100 * (frekans.cumsum() / n_sinif)',
        }
        lines += [line for column, line in steps.items() if column in op.columns]
        if op.totals:
            summed = [column for column in ("frekans", "goreli", "yuzde") if column in op.columns]
            lines.append(f'{r}.loc["{TOTAL}"] = {r}[{_list(summed)}].sum()  # alt ve üst sınır toplanmaz')
        return lines + [f"print({r}.round(3))"]

    def _stem_leaf(self, op: StemLeaf) -> list[str]:
        r = op.result
        return [
            f'sirali = {op.frame}["{op.variable}"].sort_values().astype(int)',
            "govde, yaprak = sirali // 10, sirali % 10  # gövde: onlar basamağı, yaprak: birler basamağı",
            "govdeler = range(govde.min(), govde.max() + 1)",
            f"{r} = pd.DataFrame({{",
            '    "yapraklar": [" ".join(str(v) for v in yaprak[govde == g]) for g in govdeler],',
            '    "yaprak_sayisi": [int((govde == g).sum()) for g in govdeler],',
            "}, index=[str(g) for g in govdeler])",
            f"for g, satir in {r}.iterrows():",
            '    print(f"{g} | {satir[\'yapraklar\']}")',
        ]

    def _percentile(self, op: Percentile) -> list[str]:
        p = E.format_number(op.p)
        source = f'{op.frame}["{op.variable}"]'
        if op.method == "ders":
            lines = [f"# {op.comment}: ders kuralı L_p = (p/100)(n + 1)"]
            location = f"{p} / 100 * (len({source}) + 1)"
            value = f"yuzdelik({source}, {p})"
        else:
            lines = [f"# {op.comment}: numpy varsayılanı, konum 1 + (p/100)(n − 1)"]
            location = f"1 + {p} / 100 * (len({source}) - 1)"
            value = f"np.percentile({source}, {p})"
        if op.location is not None:
            lines.append(f"{op.location} = {location}")
        lines.append(f"{op.name} = {value}")
        shown = f"{_fstring(op.comment)}: {{{op.name}:.{op.decimals}f}}"
        if op.location is not None:
            shown += f" (konum {{{op.location}:.2f}})"
        return lines + [f'print(f"{shown}")']

    def _class_histogram(self, op: ClassHistogram) -> list[str]:
        lines = [
            f"cizim = {self._chart_table(op.table)}",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            "# Bitişik dikdörtgenler: genişlik sınıf genişliği, yükseklik sınıfın değeri",
            f'cubuklar = ax.bar(cizim["alt"], cizim["{op.y}"], width=cizim["ust"] - cizim["alt"], align="edge",',
            f'                  color="{PALETTE[0]}", edgecolor="white")',
            'ax.set_xticks(list(cizim["alt"]) + [cizim["ust"].iloc[-1]])  # sınıf sınırları',
        ]
        if op.labels:
            percent = ", yuzde=True" if op.percent else ""
            lines.append(
                f'ax.bar_label(cubuklar, labels=[sayi_metni(v, {op.decimals}{percent}) for v in cizim["{op.y}"]], '
                "padding=2)"
            )
        return lines + self._axes(op.x_label, op.y_label, op.title)

    def _dot_plot(self, op: DotPlot) -> list[str]:
        source = f'{op.frame}["{op.variable}"]'
        lines = [
            f'yigin = {op.frame}.groupby("{op.variable}").cumcount() + 1  # aynı değerdeki gözlemler üst üste',
            "fig, ax = plt.subplots(figsize=(8, 3.5))",
            f'ax.scatter({source}, yigin, color="{PALETTE[0]}", s=45, zorder=3)',
        ]
        for index, (name, label) in enumerate(op.references):
            color = REFERENCE_COLORS[index % len(REFERENCE_COLORS)]
            style = ("--", ":", "-.")[index % 3]
            lines.append(f'ax.axvline({name}, color="{color}", linestyle="{style}", linewidth=2, label={text(label)})')
        lines += [
            "ax.set_yticks(range(1, int(yigin.max()) + 1))",
            "ax.set_ylim(0.3, yigin.max() + 0.7)",
        ]
        if op.x_range is not None:
            low, high = (E.format_number(value) for value in op.x_range)
            lines.append(f"ax.set_xlim({low}, {high})  # karşılaştırılan grafiklerde aynı yatay eksen")
        return lines + self._axes(op.x_label, op.y_label, op.title, legend=bool(op.references))

    def _line(self, op: LineChart) -> list[str]:
        marker = ', marker="o"' if op.markers else ""
        plot = f'ax.plot({op.frame}["{op.x}"], {op.frame}["{op.y}"]{marker}, color="{PALETTE[0]}"'
        lines = ["fig, ax = plt.subplots(figsize=(8, 5))"]
        # Başvuru çizgisi varsa açıklama (legend) gerekir; seri de adıyla açıklamada yer alır.
        lines += [plot + ",", f"        label={text(op.y_label)})"] if op.references else [plot + ")"]
        for index, (name, label) in enumerate(op.references):
            color = REFERENCE_COLORS[index % len(REFERENCE_COLORS)]
            style = ("--", ":", "-.")[index % 3]
            lines.append(f'ax.axhline({name}, color="{color}", linestyle="{style}", linewidth=2, label={text(label)})')
        return lines + self._axes(op.x_label, op.y_label, op.title, legend=bool(op.references))

    def _box_plot(self, op: BoxPlot) -> list[str]:
        series = [f'    ({text(label)}, {frame}["{variable}"]),' for frame, variable, label in op.series]
        return [
            "# Kutu: Q1'den Q3'e; çizgi: medyan; bıyıklar: sınırların içindeki en uç gözlemler; noktalar: aykırı",
            "seriler = [",
            *series,
            "]",
            "fig, ax = plt.subplots(figsize=(8, 1.6 + 1.1 * len(seriler)))",
            "for y, (etiket, degerler) in enumerate(seriler, start=1):",
            "    k = kutu_ozeti(degerler)",
            f'    ax.add_patch(plt.Rectangle((k["q1"], y - 0.25), k["iqr"], 0.5, facecolor="{PALETTE[0]}33",',
            f'                               edgecolor="{PALETTE[0]}", linewidth=2))',
            f'    ax.plot([k["medyan"], k["medyan"]], [y - 0.25, y + 0.25], color="{PALETTE[1]}", linewidth=3)',
            '    ax.plot([k["alt_biyik"], k["q1"]], [y, y], color="black")  # sol bıyık',
            '    ax.plot([k["q3"], k["ust_biyik"]], [y, y], color="black")  # sağ bıyık',
            '    for uc in (k["alt_biyik"], k["ust_biyik"]):',
            '        ax.plot([uc, uc], [y - 0.12, y + 0.12], color="black")',
            "    x = np.asarray(degerler, dtype=float)",
            '    aykiri = x[(x < k["alt_sinir"]) | (x > k["ust_sinir"])]',
            f'    ax.scatter(aykiri, [y] * len(aykiri), color="{PALETTE[1]}", s=45, zorder=3)',
            "ax.set_yticks(range(1, len(seriler) + 1), [etiket for etiket, _ in seriler])",
            "ax.set_ylim(0.4, len(seriler) + 0.6)",
            "ax.autoscale(axis=\"x\")",
            *self._axes(op.x_label, op.y_label, op.title),
        ]

    def _chart_table(self, table: str) -> str:
        rows, columns = self.totals.get(table, (False, False))
        drops = []
        if rows:
            drops.append(f'index="{TOTAL}"')
        if columns:
            drops.append(f'columns="{TOTAL}"')
        return f"{table}.drop({', '.join(drops)})" if drops else table

    def _bar(self, op: BarChart) -> list[str]:
        if op.x is None:
            lines = [f'cizim = {self._chart_table(op.source)}["{op.y}"]']
        else:
            lines = [f'cizim = pd.Series({op.source}["{op.y}"].to_numpy(), index={op.source}["{op.x}"])']
        if op.sort == "azalan":
            lines.append('cizim = cizim.sort_values(ascending=False, kind="stable")  # yüksekten düşüğe')
        labels = f"[sayi_metni(v, {op.decimals}{', yuzde=True' if op.percent else ''}) for v in cizim]"
        lines.append("fig, ax = plt.subplots(figsize=(8, 5))")
        if op.horizontal:
            lines += [
                f'cubuklar = ax.barh(cizim.index, cizim.values, color="{PALETTE[0]}")',
                "ax.invert_yaxis()  # ilk kategori en üstte",
                f"ax.bar_label(cubuklar, labels={labels}, padding=3)",
            ]
            if op.y_range is not None:
                lines.append(f"ax.set_xlim({E.format_number(op.y_range[0])}, {E.format_number(op.y_range[1])})")
            return lines + self._axes(op.y_label, op.x_label, op.title)
        lines += [
            f'cubuklar = ax.bar(cizim.index, cizim.values, color="{PALETTE[0]}")',
            f"ax.bar_label(cubuklar, labels={labels}, padding=3)",
        ]
        if op.y_range is not None:
            lines.append(f"ax.set_ylim({E.format_number(op.y_range[0])}, {E.format_number(op.y_range[1])})")
        return lines + self._axes(op.x_label, op.y_label, op.title)

    def _grouped(self, op: GroupedBarChart) -> list[str]:
        table = self._chart_table(op.table)
        frame = f"{table}.T" if op.series == "satir" else table
        stacked = ", stacked=True" if op.stacked else ""
        position = ', label_type="center", color="white"' if op.stacked else ", padding=2"
        labels = [
            "for kap in ax.containers:",
            f"    ax.bar_label(kap, labels=[sayi_metni(v, {op.decimals}) for v in kap.datavalues]{position})",
        ] if op.labels else []
        return [
            f"cizim = {frame}  # satırlar yatay eksende, sütunlar seriler",
            f"renkler = {_list(PALETTE)}[: cizim.shape[1]]",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            f"cizim.plot.bar(ax=ax, rot=0{stacked}, color=renkler)",
            *labels,
            *self._axes(op.x_label, op.y_label, op.title, legend="disarida" if op.stacked else True),
        ]

    def _compare(self, op: CompareBarChart) -> list[str]:
        items = [f'    {text(label)}: {name}["{op.column}"],' for label, name in op.tables]
        return [
            "# Her tablonun aynı sütunu yan yana; satırlar yatay eksende, sütunlar seriler",
            "cizim = pd.DataFrame({",
            *items,
            "}).T",
            f"renkler = {_list(PALETTE)}[: cizim.shape[1]]",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            "cizim.plot.bar(ax=ax, rot=0, color=renkler)",
            "for kap in ax.containers:",
            f"    ax.bar_label(kap, labels=[sayi_metni(v, {op.decimals}) for v in kap.datavalues], padding=2)",
            *self._axes(op.x_label, op.y_label, op.title, legend=True),
        ]

    def _pie(self, op: PieChart) -> list[str]:
        order = f"{op.result}_sira"
        return [
            f"{order} = {_list(op.order)}  # dilimlerin sırası",
            f'{op.result} = {op.table}.loc[{order}, ["{op.column}"]]',
            f'{op.result}["aci"] = 360 * {op.result}["{op.column}"]  # θ = 360° × r',
            f"print({op.result}.round(3))",
            "fig, ax = plt.subplots(figsize=(6, 6))",
            f'ax.pie({op.result}["{op.column}"], labels={op.result}.index, startangle=0, counterclock=True,',
            f"       colors={_list(PALETTE[:len(op.order)])},",
            '       autopct=lambda p: "%" + f"{p:.1f}".replace(".", ","))',
            f'ax.set_title("{_quote(op.title)}")',
            "plt.show()",
        ]

    def _histogram(self, op: Histogram) -> list[str]:
        lower, upper = E.format_number(op.lower), E.format_number(op.upper)
        lines = [
            f"# [{lower}, {upper}] aralığında {op.bins} eşit genişlikte kutu",
            f"kutular = np.linspace({lower}, {upper}, {op.bins} + 1)",
            "fig, ax = plt.subplots(figsize=(8, 5))",
        ]
        for index, (column, label) in enumerate(op.columns):
            color = PALETTE[index % len(PALETTE)]
            lines.append(
                f'ax.hist({op.table}["{column}"], bins=kutular, alpha=0.55, color="{color}", label={text(label)})'
            )
        for index, (value, label) in enumerate(op.references):
            color = REFERENCE_COLORS[index % len(REFERENCE_COLORS)]
            position = value if isinstance(value, str) else E.format_number(value)
            lines.append(
                f'ax.axvline({position}, color="{color}", linestyle="--", linewidth=2, label={text(label)})'
            )
        return lines + self._axes(op.x_label, op.y_label, op.title, legend=True)

    def _monte_carlo(self, op: MonteCarlo) -> list[str]:
        lines = [
            f"# {op.comment}",
            f"# {op.reps} tekrar; rastgele sayı üreteci döngüden önce bir kez tohumlanır",
            f"rng = np.random.default_rng({op.seed})",
            "sonuclar = []",
            f"for tekrar in range({op.reps}):",
        ]
        self.quiet = True
        try:
            for inner in op.body:
                lines += [f"    {line}" if line else "" for line in self.operation(inner)]
        finally:
            self.quiet = False
        dialect = self.dialect("")
        lines.append("    sonuclar.append({")
        for name, expression in op.collect:
            lines.append(f'        "{name}": {_render(expression, dialect)},')
        return lines + ["    })", f"{op.result} = pd.DataFrame(sonuclar)", f"print({op.result}.describe().round(3))"]

    # --- Notlarla karşılaştırma -----------------------------------------
    def target(self, target) -> str:
        if isinstance(target, StatTarget):
            source = (f'{target.frame}["{target.variable}"]' if target.where is None
                      else f'{target.frame}.loc[{_where(target.frame, target.where)}, "{target.variable}"]')
            return _stat_call(source, target.stat)
        if isinstance(target, ScalarTarget):
            return target.name
        if isinstance(target, TableTarget):
            return f"{target.table}.loc[{text(target.row)}, {text(target.column)}]"
        if isinstance(target, CellTarget):
            return f'{target.frame}["{target.column}"].iloc[{target.row - 1}]'
        raise TypeError(f"Tanınmayan hedef: {type(target).__name__}")

    def check_lines(self, checks: tuple[Check, ...]) -> list[str]:
        lines = ['print("Notlarla karşılaştırma:")']
        for check in checks:
            expected = f"{check.expected:.{check.decimals}f}"
            lines.append(
                f'kontrol_et("{_quote(check.label)}", {self.target(check.target)}, {expected}, {check.decimals})'
            )
        return lines

    def closing(self) -> list[str]:
        return ['print("\\nBütün değerler ders notlarıyla uyuşuyor.")']
