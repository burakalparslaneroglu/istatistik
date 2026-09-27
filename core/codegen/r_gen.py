"""Uygulama tanımından temel R kodu üretir (ek paket gerekmez).

Deterministik adımlarda sayılar Python ve uygulamayla ondalık düzeyinde aynıdır. Simülasyonlarda R'nin
rastgele sayı üreteci numpy'ninkinden farklıdır: aynı tohum aynı çekilişi vermez (yalnız dağılım aynıdır).
"""

from __future__ import annotations

from core.codegen.base import (
    PALETTE,
    REFERENCE_COLORS,
    Generator,
    flatten,
    text,
    uses_charts,
    wrapped,
)
from core.labs import expr as E
from core.labs.spec import (
    TOTAL,
    BarChart,
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
    FrequencyTable,
    FromCounts,
    GroupedBarChart,
    Groups,
    GroupSummary,
    Histogram,
    InlineData,
    LineChart,
    MapCodes,
    MonteCarlo,
    NewSample,
    Operation,
    Percentile,
    PieChart,
    Scalar,
    ScalarTable,
    ScalarTarget,
    Shape,
    Statistic,
    StatTarget,
    StemLeaf,
    TableTarget,
    VariableTypes,
)
from core.labs.tables import class_edges

_STAT = {"sum": "sum", "mean": "mean", "median": "median", "prod": "prod", "min": "min", "max": "max",
         "count": "length"}
_FUNCTIONS = {
    "log": "log", "exp": "exp", "sqrt": "sqrt", "abs": "abs", "maximum": "pmax", "minimum": "pmin",
    "round": "round", "floor": "floor", "normcdf": "pnorm", "normpdf": "dnorm", "norminv": "qnorm",
    "cumprod": "cumprod",
    **{name: f"as.numeric({{0}} {symbol} {{1}})" for name, symbol in E.COMPARISONS.items()},
}
_REFERENCE_STYLES = tuple(zip(REFERENCE_COLORS, ("2", "3", "4")))

_NUMBER_TEXT = [
    "# Grafik etiketleri için Türkçe sayı: ondalık virgül, yüzde işareti sayıdan önce",
    "sayi_metni <- function(deger, basamak = 0, yuzde = FALSE) {",
    '  metin <- formatC(deger, format = "f", digits = basamak, decimal.mark = ",")',
    '  if (yuzde) paste0("%", metin) else metin',
    "}",
]
_BOUNDARY_TEXT = [
    "# Sınıf sınırının yazımı: ondalık virgül (ör. 12,5)",
    'sinir_metni <- function(deger) trimws(formatC(deger, format = "fg", digits = 10, decimal.mark = ","))',
]
_PERCENTILE = [
    "# Ders kuralı: L_p = (p/100)(n + 1). L_p tam sayı değilse komşu iki gözlem arasında doğrusal ara değer;",
    "# L_p <= 1 ise en küçük, L_p >= n ise en büyük gözlem. quantile(x, p / 100, type = 6) aynı sonucu verir;",
    "# R'nin varsayılanı (type = 7) farklı bir kural kullanır.",
    "yuzdelik <- function(x, p) {",
    "  x <- sort(x)",
    "  n <- length(x)",
    "  konum <- p / 100 * (n + 1)",
    "  if (konum <= 1) return(x[1])",
    "  if (konum >= n) return(x[n])",
    "  k <- floor(konum)",
    "  x[k] + (konum - k) * (x[k + 1] - x[k])",
    "}",
]


def _vector(values) -> str:
    return "c(" + ", ".join(text(value) for value in values) + ")"


def _colors(count: int) -> str:
    return _vector(PALETTE[:count])


def _sprintf(value: str) -> str:
    """``sprintf`` biçim dizgesi içinde düz metin: tırnak, ters bölü ve yüzde işareti kaçırılır."""

    return value.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%")


def _quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _subset(frame: str, variable: str, where) -> str:
    """``frame$variable``; ``where`` verilirse yalnız koşulu sağlayan gözlemler."""

    values = f"{frame}${variable}"
    if where is None:
        return values
    column, value = where
    return f"{values}[{frame}${column} == {text(value)}]"


def _statistic(values: str, stat: str) -> str:
    if stat == "value":
        return values
    if stat == "count":
        return f"sum(!is.na({values}))"
    if stat == "mode":
        # En yüksek frekanslı değer(ler); tek mod beklenir
        return f"as.numeric(names(which(table({values}) == max(table({values})))))"
    if stat == "mode_freq":
        return f"max(table({values}))"
    return f"{_STAT[stat]}({values})"


class RGenerator(Generator):
    language = "R"
    comment = "#"

    def dialect(self, frame: str) -> E.Dialect:
        return E.Dialect(variable=lambda name: f"{frame}${name}", functions=_FUNCTIONS, power="^")

    # --- Başlık ve yardımcılar ------------------------------------------
    def imports(self, operations: tuple[Operation, ...], *, script: bool = False) -> list[str]:
        if not script:
            return []
        lines = ["# Yalnız temel R kullanılır; ek paket gerekmez.", ""]
        if uses_charts(operations):
            lines += [
                "# Rscript ile (etkileşimsiz) çalıştırıldığında R grafikleri çalışma klasöründe Rplots.pdf",
                "# dosyasına yazar. Klasörde dosya oluşmasın diye grafikler R'nin geçici klasörüne yazılır;",
                "# R kapanınca bu klasör silinir. RStudio'da grafikler her zamanki gibi Plots panelinde görünür.",
                'if (!interactive()) png(file.path(tempdir(), "grafik%02d.png"))',
                "",
            ]
        return lines

    def helpers(self, operations: tuple[Operation, ...], *, with_checks: bool) -> list[str]:
        lines: list[str] = []
        flat = flatten(operations)
        labelled = (BarChart, GroupedBarChart, CompareBarChart, PieChart)
        if any(isinstance(op, labelled) or (isinstance(op, ClassHistogram) and op.labels) for op in flat):
            lines += _NUMBER_TEXT + [""]
        if any(isinstance(op, (ClassTable, ClassHistogram)) for op in flat):
            lines += _BOUNDARY_TEXT + [""]
        if any(isinstance(op, Percentile) and op.method == "ders" for op in flat):
            lines += _PERCENTILE + [""]
        if with_checks:
            lines += [
                "# Hesaplanan değeri ders notlarındaki basılı değerle karşılaştırır",
                "kontrol_et <- function(etiket, deger, beklenen, ondalik = 4) {",
                "  tolerans <- 0.5 * 10^(-ondalik) + 1e-12",
                '  durum <- if (abs(deger - beklenen) <= tolerans) "OK  " else "HATA"',
                '  cat(sprintf("  %s %s: %.*f  (notlar: %s)\\n", durum, etiket, ondalik, deger,',
                '              sprintf("%.*f", ondalik, beklenen)))',
                '  if (abs(deger - beklenen) > tolerans) stop(etiket, " notlarla uyuşmuyor.")',
                "}",
                "",
            ]
        return lines

    # --- İşlemler --------------------------------------------------------
    def operation(self, op: Operation) -> list[str]:
        lines = self._operation(op)
        if self.quiet:
            lines = [line for line in lines if not line.lstrip().startswith(("print(", "cat(", "str("))]
        return lines

    def _operation(self, op: Operation) -> list[str]:  # noqa: C901 - tek dağıtıcı, işlem türü başına bir blok
        if isinstance(op, InlineData):
            return self._inline(op)
        if isinstance(op, FromCounts):
            return self._from_counts(op)
        if isinstance(op, VariableTypes):
            return self._variable_types(op)
        if isinstance(op, MapCodes):
            pairs = ", ".join(f"{text(label)} = {text(code)}" for label, code in op.mapping)
            return [
                f"# {op.comment}",
                f"{op.frame}${op.name} <- unname(c({pairs})[{op.frame}${op.source}])",
                f'print(head({op.frame}[, c("{op.source}", "{op.name}")], 8))',
            ]
        if isinstance(op, Groups):
            return [
                f"# {op.comment}",
                f"{op.frame}${op.name} <- rep({_vector(op.labels)}, times = {_vector(op.sizes)})",
            ]
        if isinstance(op, Derive):
            return [f"# {op.comment}", f"{op.frame}${op.name} <- {E.render(op.expr, self.dialect(op.frame))}"]
        if isinstance(op, NewSample):
            frame = f"{op.frame} <- data.frame(id = seq_len({op.nobs}))"
            if op.seed is None:
                return [frame]
            return [
                "# Sabit tohum: betik her çalıştırmada aynı veriyi üretir",
                f"set.seed({op.seed})",
                frame,
            ]
        if isinstance(op, Draw):
            a, b = E.format_number(op.first), E.format_number(op.second)
            call = {
                "normal": f"rnorm(nrow({op.frame}), mean = {a}, sd = {b})",
                "uniform": f"runif(nrow({op.frame}), min = {a}, max = {b})",
                "beta": f"rbeta(nrow({op.frame}), shape1 = {a}, shape2 = {b})",
            }[op.distribution]
            return [f"# {op.comment}", f"{op.frame}${op.name} <- {call}"]
        if isinstance(op, DrawCategory):
            return self._draw_category(op)
        if isinstance(op, Shape):
            columns = (f"length(setdiff(names({op.frame}), {_vector(op.exclude)}))  # kimlik sütunu değişken sayılmaz"
                       if op.exclude else f"ncol({op.frame})")
            return [
                f"{op.observations} <- nrow({op.frame})  # gözlem sayısı",
                f"{op.variables} <- {columns}",
                f'cat("Gözlem sayısı:", {op.observations}, "| Değişken sayısı:", {op.variables}, "\\n")',
            ]
        if isinstance(op, Count):
            return [
                f"# {op.comment}",
                f"{op.name} <- sum({op.frame}${op.column} == {text(op.value)})",
                f'cat("{_quote(op.comment)}:", {op.name}, "\\n")',
            ]
        if isinstance(op, Statistic):
            values = _subset(op.frame, op.variable, op.where)
            return [
                f"# {op.comment}",
                f"{op.name} <- {_statistic(values, op.stat)}",
                f'cat(sprintf("{_sprintf(op.comment)}: %.{op.decimals}f\\n", {op.name}))',
            ]
        if isinstance(op, Scalar):
            rhs = E.render(op.expr, self.dialect(""))
            shown = f"%%%.{op.decimals}f" if op.percent else f"%.{op.decimals}f"
            return [
                f"# {op.comment}",
                f"{op.name} <- {rhs}",
                f'cat(sprintf("{_sprintf(op.comment)}: {shown}\\n", {op.name}))',
            ]
        if isinstance(op, ScalarTable):
            dialect = self.dialect("")
            rows = [f"  {text(label)} = {E.render(expression, dialect)}" for label, expression in op.rows]
            rows = [row + ("," if index < len(rows) - 1 else "") for index, row in enumerate(rows)]
            return [f"{op.result} <- data.frame(deger = c(", *rows, "))", f"print(round({op.result}, {op.decimals}))"]
        if isinstance(op, GroupSummary):
            return self._group_summary(op)
        if isinstance(op, FrequencyTable):
            return self._frequency(op)
        if isinstance(op, CrossTab):
            return self._crosstab(op)
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
            return [
                f'plot({op.frame}${op.x}, {op.frame}${op.y}, type = "b", pch = 19, lwd = 2, col = "{PALETTE[0]}",',
                f'     xlab = "{_quote(op.x_label)}", ylab = "{_quote(op.y_label)}", main = "{_quote(op.title)}")',
            ]
        if isinstance(op, Histogram):
            return self._histogram(op)
        if isinstance(op, MonteCarlo):
            return self._monte_carlo(op)
        raise TypeError(f"R üreticisi bu işlemi tanımıyor: {type(op).__name__}")

    def _inline(self, op: InlineData) -> list[str]:
        lines = [f"# {op.comment}"]
        if op.layout and len(op.columns) == 1:
            name = f"{op.frame}_ham"
            items = [text(row[0]) for row in op.rows]
            lines += wrapped(f"{name} <- c(", items, ")", per_line=op.layout, indent="  ")
            lines.append(f"{op.frame} <- data.frame({op.columns[0]} = {name})")
        else:
            lines.append(f"{op.frame} <- data.frame(")
            for position, column in enumerate(op.columns):
                values = [text(row[position]) for row in op.rows]
                ending = "," if position < len(op.columns) - 1 else ""
                lines += wrapped(f"  {column} = c(", values, f"){ending}")
            lines.append(")")
        lines.append(f"print({op.frame})" if len(op.rows) <= 12 else f"print(head({op.frame}, 5))  # ilk beş gözlem")
        return lines

    def _from_counts(self, op: FromCounts) -> list[str]:
        name = f"{op.frame}_sayim"
        lines = [f"# {op.comment}", f"{name} <- data.frame("]
        names = (*op.columns, "sayi")
        for position, column in enumerate(names):
            values = [text(row[position]) for row in op.rows]
            ending = "," if position < len(names) - 1 else ""
            lines += wrapped(f"  {column} = c(", values, f"){ending}")
        lines += [
            ")",
            '# Her satır "sayi" kez tekrarlanır: bir satır = bir gözlem',
            f"satirlar <- rep(seq_len(nrow({name})), {name}$sayi)",
            f"{op.frame} <- {name}[satirlar, {_vector(op.columns)}, drop = FALSE]",
            f"rownames({op.frame}) <- NULL",
            f"print(nrow({op.frame}))  # gözlem sayısı",
        ]
        return lines

    def _variable_types(self, op: VariableTypes) -> list[str]:
        lines = [
            "# Yazılımın saklama türü: sayı (num) ya da metin (chr)",
            f"str({op.frame})",
            "# İstatistiksel tür yazılımdan değil, değişkenin anlamından gelir",
            f"{op.result} <- data.frame(",
        ]
        fields = (("degisken", 0), ("tur", 1), ("ayrinti", 2))
        for index, (field, position) in enumerate(fields):
            values = [text(row[position]) for row in op.rows]
            ending = "," if index < len(fields) - 1 else ""
            lines += wrapped(f"  {field} = c(", values, f"){ending}")
        return lines + [")", f"print({op.result})"]

    def _draw_category(self, op: DrawCategory) -> list[str]:
        categories = f"{op.name}_kategoriler"
        lines = [
            f"# {op.comment}",
            "# u ~ Tekdüze(0, 1); kategori, birikimli olasılığı u'yu ilk aşan kategoridir",
            f"u <- runif(nrow({op.frame}))",
            f"{categories} <- {_vector(op.categories)}",
        ]
        if not op.by:
            probs = op.probabilities[0][1]
            return lines + [
                f"esik <- cumsum({_vector(probs)})",
                "esik[length(esik)] <- 1  # yuvarlama hatasına karşı son eşik tam 1",
                f"{op.frame}${op.name} <- {categories}[findInterval(u, esik) + 1]",
            ]
        table = f"{op.name}_olasilik"
        if len(op.by) == 1:
            entries = [f"  {text(condition[0])} = {_vector(probs)}" for condition, probs in op.probabilities]
            entries = [entry + ("," if index < len(entries) - 1 else "") for index, entry in enumerate(entries)]
            return lines + [
                f"{table} <- list(",
                *entries,
                ")",
                f"{op.frame}${op.name} <- NA_character_",
                f"for (kosul in names({table})) {{",
                f"  secili <- {op.frame}${op.by[0]} == kosul",
                f"  esik <- cumsum({table}[[kosul]])",
                "  esik[length(esik)] <- 1",
                f"  {op.frame}${op.name}[secili] <- {categories}[findInterval(u[secili], esik) + 1]",
                "}",
            ]
        entries = [
            f"  list(kosul = {_vector(condition)}, olasilik = {_vector(probs)})"
            for condition, probs in op.probabilities
        ]
        entries = [entry + ("," if index < len(entries) - 1 else "") for index, entry in enumerate(entries)]
        selection = " & ".join(
            f"{op.frame}${column} == satir$kosul[{index + 1}]" for index, column in enumerate(op.by)
        )
        return lines + [
            f"{table} <- list(",
            *entries,
            ")",
            f"{op.frame}${op.name} <- NA_character_",
            f"for (satir in {table}) {{",
            f"  secili <- {selection}",
            "  esik <- cumsum(satir$olasilik)",
            "  esik[length(esik)] <- 1",
            f"  {op.frame}${op.name}[secili] <- {categories}[findInterval(u[secili], esik) + 1]",
            "}",
        ]

    def _group_summary(self, op: GroupSummary) -> list[str]:
        order = _vector(op.order)
        lines = [f"{op.result} <- data.frame("]
        for index, (name, variable, stat) in enumerate(op.columns):
            ending = "," if index < len(op.columns) - 1 else ""
            lines.append(
                f"  {name} = tapply({op.frame}${variable}, {op.frame}${op.by}, {_STAT[stat]})[{order}]{ending}"
            )
        return lines + [")", f"print(round({op.result}, 4))"]

    def _frequency(self, op: FrequencyTable) -> list[str]:
        order = f"{op.result}_sira"
        lines = [
            f"{order} <- {_vector(op.order)}",
            f"{op.result} <- data.frame(",
            f"  frekans = as.vector(table(factor({op.frame}${op.variable}, levels = {order}))),",
            f"  row.names = {order}",
            ")",
        ]
        if op.relative:
            lines += [
                f"{op.result}$goreli <- {op.result}$frekans / sum({op.result}$frekans)  # r = f / n",
                f"{op.result}$yuzde <- 100 * {op.result}$goreli  # p = 100 r",
            ]
        if op.totals:
            lines.append(f'{op.result}["{TOTAL}", ] <- colSums({op.result})')
        lines.append(f"print(round({op.result}, 3))")
        return lines

    def _crosstab(self, op: CrossTab) -> list[str]:
        lines: list[str] = []
        data = op.frame
        if op.where is not None:
            data = f"{op.result}_veri"
            column, value = op.where
            lines += [
                f"# Yalnız {column} = {value} olan gözlemler",
                f"{data} <- {op.frame}[{op.frame}${column} == {text(value)}, ]",
            ]
        factors = [
            f"  factor({data}${op.row}, levels = {_vector(op.row_order)}),",
            f"  factor({data}${op.column}, levels = {_vector(op.column_order)})",
        ]
        if op.percent is None:
            lines += [f"{op.result} <- as.data.frame.matrix(table(", *factors, "))"]
            if op.margins:
                lines += [
                    f'{op.result}["{TOTAL}", ] <- colSums({op.result})  # sütun toplamları',
                    f"{op.result}${TOTAL} <- rowSums({op.result})  # satır toplamları",
                ]
            return lines + [f"print({op.result})"]
        counts = f"{op.result}_sayi"
        lines += [f"{counts} <- table(", *factors, ")"]
        if op.percent == "satir":
            lines += [
                "# Satır yüzdesi: payda satır toplamıdır",
                f"{op.result} <- as.data.frame.matrix(100 * prop.table({counts}, 1))",
            ]
            if op.margins:
                lines.append(f"{op.result}${TOTAL} <- rowSums({op.result})")
        else:
            lines += [
                "# Sütun yüzdesi: payda sütun toplamıdır",
                f"{op.result} <- as.data.frame.matrix(100 * prop.table({counts}, 2))",
            ]
            if op.margins:
                lines.append(f'{op.result}["{TOTAL}", ] <- colSums({op.result})')
        return lines + [f"print(round({op.result}, {op.decimals}))"]

    def _class_table(self, op: ClassTable) -> list[str]:
        source = f"{op.frame}${op.variable}"
        r = op.result
        if op.lower is None:
            lines = [
                f"h <- {E.format_number(op.width)}  # sınıf genişliği",
                f"alt_sinir <- floor(min({source}) / h) * h  # en küçük değeri içeren h katı",
                f"k <- floor((max({source}) - alt_sinir) / h) + 1  # en büyük değeri de kapsayan sınıf sayısı",
                "kenarlar <- alt_sinir + h * (0:k)",
            ]
        else:
            edges = class_edges(None, op.width, op.lower, op.classes)
            lines = wrapped("kenarlar <- c(", [E.format_number(value) for value in edges], ")  # sınıf sınırları")
        if op.row_labels == "ust":
            labels = 'paste("x <", sinir_metni(kenarlar[-1]))'
        else:
            labels = 'paste(sinir_metni(head(kenarlar, -1)), "≤ x <", sinir_metni(kenarlar[-1]))'
        lines += [
            "# Sınıflar [alt, üst): alt sınır dahil, üst sınır hariç",
            f"siniflar <- cut({source}, breaks = kenarlar, right = FALSE)",
            "frekans <- as.vector(table(siniflar))  # her sınıftaki gözlem sayısı",
            "n_sinif <- sum(frekans)",
            f"{r} <- data.frame(alt = head(kenarlar, -1), ust = kenarlar[-1],",
            f"{' ' * len(r)}              row.names = {labels})",
        ]
        steps = {
            "orta_nokta": f"{r}$orta_nokta <- ({r}$alt + {r}$ust) / 2  # m = (alt + üst) / 2",
            "frekans": f"{r}$frekans <- frekans",
            "goreli": f"{r}$goreli <- frekans / n_sinif  # r = f / n",
            "yuzde": f"{r}$yuzde <- 100 * (frekans / n_sinif)  # p = 100 r",
            "kumulatif_frekans": f"{r}$kumulatif_frekans <- cumsum(frekans)  # F = f1 + ... + fj",
            "kumulatif_goreli": f"{r}$kumulatif_goreli <- cumsum(frekans) / n_sinif",
            "kumulatif_yuzde": f"{r}$kumulatif_yuzde <- 100 * (cumsum(frekans) / n_sinif)",
        }
        lines += [line for column, line in steps.items() if column in op.columns]
        if op.totals:
            summed = [column for column in ("frekans", "goreli", "yuzde") if column in op.columns]
            lines += [
                f"toplamlar <- colSums({r}[, {_vector(summed)}, drop = FALSE])",
                f'{r}["{TOTAL}", ] <- NA  # alt ve üst sınır toplanmaz',
                f'{r}["{TOTAL}", names(toplamlar)] <- toplamlar',
            ]
        return lines + [f"print(round({r}, 3))"]

    def _stem_leaf(self, op: StemLeaf) -> list[str]:
        r = op.result
        return [
            "# R'nin stem() fonksiyonu gövde ölçeğini kendisi seçer; notlardaki gösterimle aynı olsun diye",
            "# gövde (onlar basamağı) ve yaprak (birler basamağı) açıkça ayrılır.",
            f"sirali <- sort({op.frame}${op.variable})",
            "govde <- sirali %/% 10",
            "yaprak <- sirali %% 10",
            "govdeler <- seq(min(govde), max(govde))",
            f"{r} <- data.frame(",
            '  yapraklar = sapply(govdeler, function(g) paste(yaprak[govde == g], collapse = " ")),',
            "  yaprak_sayisi = sapply(govdeler, function(g) sum(govde == g)),",
            "  row.names = govdeler",
            ")",
            f'cat(paste(govdeler, "|", {r}$yapraklar), sep = "\\n")',
        ]

    def _percentile(self, op: Percentile) -> list[str]:
        p = E.format_number(op.p)
        source = f"{op.frame}${op.variable}"
        if op.method == "ders":
            lines = [f"# {op.comment}: ders kuralı L_p = (p/100)(n + 1)"]
            location = f"{p} / 100 * (length({source}) + 1)"
            value = f"yuzdelik({source}, {p})"
        else:
            lines = [f"# {op.comment}: R'nin varsayılanı (type = 7), konum 1 + (p/100)(n - 1)"]
            location = f"1 + {p} / 100 * (length({source}) - 1)"
            value = f"quantile({source}, {p} / 100, names = FALSE)"
        if op.location is not None:
            lines.append(f"{op.location} <- {location}")
        lines.append(f"{op.name} <- {value}")
        if op.location is not None:
            lines.append(
                f'cat(sprintf("{_sprintf(op.comment)}: %.{op.decimals}f (konum %.2f)\\n", {op.name}, {op.location}))'
            )
        else:
            lines.append(f'cat(sprintf("{_sprintf(op.comment)}: %.{op.decimals}f\\n", {op.name}))')
        return lines

    def _class_histogram(self, op: ClassHistogram) -> list[str]:
        rows, _ = self.totals.get(op.table, (False, False))
        source = f'{op.table}[rownames({op.table}) != "{TOTAL}", ]' if rows else op.table
        values = f"cizim${op.y}"
        lines = [
            f"cizim <- {source}",
            "genislik <- cizim$ust - cizim$alt",
            "# Bitişik dikdörtgenler (space = 0): genişlik sınıf genişliği, yükseklik sınıfın değeri",
            f'konum <- barplot({values}, width = genislik, space = 0, col = "{PALETTE[0]}", border = "white",',
            f"                 ylim = c(0, max({values}) * 1.15),",
            f'                 xlab = "{_quote(op.x_label)}", ylab = "{_quote(op.y_label)}",',
            f'                 main = "{_quote(op.title)}")',
            "axis(1, at = c(0, cumsum(genislik)), labels = sinir_metni(c(cizim$alt, cizim$ust[nrow(cizim)])))",
        ]
        if op.labels:
            percent = ", yuzde = TRUE" if op.percent else ""
            lines.append(
                f"text(konum, {values}, labels = sayi_metni({values}, {op.decimals}{percent}), pos = 3, xpd = TRUE)"
            )
        return lines

    def _dot_plot(self, op: DotPlot) -> list[str]:
        source = f"{op.frame}${op.variable}"
        limits = ""
        if op.x_range is not None:
            low, high = (E.format_number(value) for value in op.x_range)
            limits = f"xlim = c({low}, {high}), "  # karşılaştırılan grafiklerde aynı yatay eksen
        lines = [
            f"yigin <- ave({source}, {source}, FUN = seq_along)  # aynı değerdeki gözlemler üst üste",
            f'plot({source}, yigin, pch = 19, col = "{PALETTE[0]}", yaxt = "n", ylim = c(0.5, max(yigin) + 0.5),',
            f'     {limits}xlab = "{_quote(op.x_label)}", ylab = "{_quote(op.y_label)}", main = "{_quote(op.title)}")',
            "axis(2, at = seq_len(max(yigin)), las = 1)",
        ]
        if op.references:
            colors, ltys, labels = [], [], []
            for index, (name, label) in enumerate(op.references):
                color, lty = _REFERENCE_STYLES[index % len(_REFERENCE_STYLES)]
                lines.append(f'abline(v = {name}, col = "{color}", lty = {lty}, lwd = 2)')
                colors.append(f'"{color}"')
                ltys.append(lty)
                labels.append(text(label))
            lines.append(
                f'legend("topright", legend = c({", ".join(labels)}), col = c({", ".join(colors)}), '
                f'lty = c({", ".join(ltys)}), lwd = 2, bty = "n")'
            )
        return lines

    def _chart_matrix(self, table: str) -> str:
        """Grafikte çizilecek sayılar: ``Toplam`` satırı ve sütunu çıkarılmış matris."""

        rows, columns = self.totals.get(table, (False, False))
        row_part = f'rownames({table}) != "{TOTAL}"' if rows else ""
        column_part = f'names({table}) != "{TOTAL}"' if columns else ""
        if rows or columns:
            return f"as.matrix({table}[{row_part}, {column_part}, drop = FALSE])"
        return f"as.matrix({table})"

    def _bar(self, op: BarChart) -> list[str]:
        if op.x is None:
            lines = [f"cizim <- setNames({op.source}${op.y}, rownames({op.source}))"]
            if self.totals.get(op.source, (False, False))[0]:
                lines.append(f'cizim <- cizim[names(cizim) != "{TOTAL}"]  # toplam çizilmez')
        else:
            lines = [f"cizim <- setNames({op.source}${op.y}, {op.source}${op.x})"]
        if op.sort == "azalan":
            lines.append("cizim <- cizim[order(-cizim)]  # yüksekten düşüğe")
        labels = f"sayi_metni(cizim, {op.decimals}{', yuzde = TRUE' if op.percent else ''})"
        x_label, y_label, title = _quote(op.x_label), _quote(op.y_label), _quote(op.title)
        if op.horizontal:
            limit = (f"c({E.format_number(op.y_range[0])}, {E.format_number(op.y_range[1])})"
                     if op.y_range is not None else "range(0, cizim) * 1.2")
            return lines + [
                "cizim <- rev(cizim)  # barplot yatayda ilk değeri en alta çizer; ilk kategori en üstte olsun",
                "eski_par <- par(mar = c(5, 10, 4, 2))  # uzun kategori adları için geniş sol kenar",
                f'konum <- barplot(cizim, horiz = TRUE, las = 1, col = "{PALETTE[0]}", border = NA,',
                f'                 xlim = {limit}, xlab = "{y_label}",',
                f'                 main = "{title}")',
                f'title(ylab = "{x_label}", line = 8.5)',
                f"text(cizim, konum, labels = {labels}, pos = 4, xpd = TRUE)",
                "par(eski_par)",
            ]
        if op.y_range is not None:
            limit = f"c({E.format_number(op.y_range[0])}, {E.format_number(op.y_range[1])})"
            return lines + [
                "# Değer ekseni verilen aralıkla sınırlanır; sütunlar alt sınırdan başlıyormuş gibi görünür",
                f'konum <- barplot(cizim, col = "{PALETTE[0]}", border = NA, ylim = {limit}, xpd = FALSE,',
                f'                 xlab = "{x_label}", ylab = "{y_label}",',
                f'                 main = "{title}")',
                "box(bty = \"l\")",
                f"text(konum, cizim, labels = {labels}, pos = 3, xpd = TRUE)",
            ]
        return lines + [
            f'konum <- barplot(cizim, col = "{PALETTE[0]}", border = NA, ylim = range(0, cizim) * 1.15,',
            f'                 xlab = "{x_label}", ylab = "{y_label}",',
            f'                 main = "{title}")',
            f"text(konum, cizim, labels = {labels}, pos = 3, xpd = TRUE)",
        ]

    def _bars_with_legend(self, x_label: str, y_label: str, title: str, stacked: bool, decimals: int) -> list[str]:
        """``cizim`` matrisinin çok serili sütun grafiği: satırlar seriler, sütunlar yatay eksen."""

        x_label, y_label, title = _quote(x_label), _quote(y_label), _quote(title)
        colors = f"{_colors(len(PALETTE))}[seq_len(nrow(cizim))]"
        if stacked:
            return [
                f"renkler <- {colors}",
                "konum <- barplot(cizim, col = renkler, border = NA, ylim = c(0, max(colSums(cizim)) * 1.3),",
                f'                 xlab = "{x_label}", ylab = "{y_label}",',
                f'                 main = "{title}")',
                "orta <- apply(cizim, 2, function(s) cumsum(s) - s / 2)  # her parçanın ortası",
                f'text(rep(konum, each = nrow(cizim)), orta, labels = sayi_metni(cizim, {decimals}), col = "white")',
                'legend("top", legend = rownames(cizim), fill = renkler, border = NA, horiz = TRUE, bty = "n")',
            ]
        return [
            f"renkler <- {colors}",
            "konum <- barplot(cizim, beside = TRUE, col = renkler, border = NA, ylim = range(0, cizim) * 1.3,",
            f'                 xlab = "{x_label}", ylab = "{y_label}",',
            f'                 main = "{title}")',
            f"text(konum, cizim, labels = sayi_metni(cizim, {decimals}), pos = 3, xpd = TRUE)",
            'legend("top", legend = rownames(cizim), fill = renkler, border = NA, horiz = TRUE, bty = "n")',
        ]

    def _grouped(self, op: GroupedBarChart) -> list[str]:
        matrix = self._chart_matrix(op.table)
        if op.series == "satir":
            lines = ["# Tablonun satırları seriler, sütunları yatay eksende", f"cizim <- {matrix}"]
        else:
            lines = ["# Tablonun sütunları seriler, satırları yatay eksende (matris devriği)", f"cizim <- t({matrix})"]
        return lines + self._bars_with_legend(op.x_label, op.y_label, op.title, op.stacked, op.decimals)

    def _compare(self, op: CompareBarChart) -> list[str]:
        items = [f'  {text(label)} = {name}[, "{op.column}"]' for label, name in op.tables]
        items = [item + ("," if index < len(items) - 1 else "") for index, item in enumerate(items)]
        first = op.tables[0][1]
        return [
            "# Her tablonun aynı sütunu yan yana; sütunlar yatay eksende, satırlar seriler",
            "cizim <- cbind(",
            *items,
            ")",
            f"rownames(cizim) <- rownames({first})",
            *self._bars_with_legend(op.x_label, op.y_label, op.title, False, op.decimals),
        ]

    def _pie(self, op: PieChart) -> list[str]:
        order = f"{op.result}_sira"
        return [
            f"{order} <- {_vector(op.order)}  # dilimlerin sırası",
            f'{op.result} <- {op.table}[{order}, "{op.column}", drop = FALSE]',
            f"{op.result}$aci <- 360 * {op.result}${op.column}  # θ = 360° × r",
            f"print(round({op.result}, 3))",
            f"pie({op.result}${op.column},",
            f"    labels = paste(rownames({op.result}), sayi_metni(100 * {op.result}${op.column}, 1, yuzde = TRUE)),",
            f"    col = {_colors(len(op.order))}, clockwise = FALSE, init.angle = 0,",
            f'    main = "{_quote(op.title)}")',
        ]

    def _histogram(self, op: Histogram) -> list[str]:
        lower, upper = E.format_number(op.lower), E.format_number(op.upper)
        series = [f"{op.table}${column}" for column, _ in op.columns]
        lines = [
            f"# [{lower}, {upper}] aralığında {op.bins} eşit genişlikte kutu; aralık dışındaki değerler çizilmez",
            f"kutular <- seq({lower}, {upper}, length.out = {op.bins + 1})",
            f"aralikta <- function(x) x[x >= {lower} & x <= {upper}]",
            f"sayimlar <- sapply(list({', '.join(series)}),",
            "                   function(x) hist(aralikta(x), breaks = kutular, plot = FALSE)$counts)",
        ]
        fills, labels, ltys, colors = [], [], [], []
        for index, (item, (_, label)) in enumerate(zip(series, op.columns)):
            color = f'adjustcolor("{PALETTE[index % len(PALETTE)]}", 0.55)'
            if index == 0:
                lines += [
                    f'hist(aralikta({item}), breaks = kutular, col = {color}, border = "white",',
                    f'     ylim = c(0, max(sayimlar)), xlab = "{_quote(op.x_label)}", ylab = "Tekrar sayısı",',
                    f'     main = "{_quote(op.title)}")',
                ]
            else:
                lines.append(f'hist(aralikta({item}), breaks = kutular, col = {color}, border = "white", add = TRUE)')
            fills.append(color)
            labels.append(text(label))
            ltys.append("NA")
            colors.append("NA")
        for index, (value, label) in enumerate(op.references):
            color, lty = _REFERENCE_STYLES[index % len(_REFERENCE_STYLES)]
            lines.append(f'abline(v = {E.format_number(value)}, col = "{color}", lty = {lty}, lwd = 2)')
            fills.append("NA")
            labels.append(text(label))
            ltys.append(lty)
            colors.append(f'"{color}"')
        return lines + [
            f"legend(\"topright\", legend = c({', '.join(labels)}),",
            f"       fill = c({', '.join(fills)}), border = NA,",
            f"       lty = c({', '.join(ltys)}), col = c({', '.join(colors)}), lwd = 2, bty = \"n\")",
        ]

    def _monte_carlo(self, op: MonteCarlo) -> list[str]:
        lines = [
            f"# {op.comment}",
            f"# {op.reps} tekrar; tohum döngüden önce bir kez ayarlanır",
            f"set.seed({op.seed})",
            f'sonuclar <- vector("list", {op.reps})',
            f"for (tekrar in seq_len({op.reps})) {{",
        ]
        self.quiet = True
        try:
            for inner in op.body:
                lines += [f"  {line}" if line else "" for line in self.operation(inner)]
        finally:
            self.quiet = False
        dialect = self.dialect("")
        lines.append("  sonuclar[[tekrar]] <- c(")
        for index, (name, expression) in enumerate(op.collect):
            ending = "," if index < len(op.collect) - 1 else ""
            lines.append(f"    {name} = {E.render(expression, dialect)}{ending}")
        return lines + [
            "  )",
            "}",
            f"{op.result} <- as.data.frame(do.call(rbind, sonuclar))",
            f"print(summary({op.result}))",
        ]

    # --- Notlarla karşılaştırma -----------------------------------------
    def target(self, target) -> str:
        if isinstance(target, StatTarget):
            return _statistic(_subset(target.frame, target.variable, target.where), target.stat)
        if isinstance(target, ScalarTarget):
            return target.name
        if isinstance(target, TableTarget):
            return f"{target.table}[{text(target.row)}, {text(target.column)}]"
        if isinstance(target, CellTarget):
            return f"{target.frame}${target.column}[{target.row}]"
        raise TypeError(f"Tanınmayan hedef: {type(target).__name__}")

    def check_lines(self, checks: tuple[Check, ...]) -> list[str]:
        lines = ['cat("Notlarla karşılaştırma:\\n")']
        for check in checks:
            expected = f"{check.expected:.{check.decimals}f}"
            target = self.target(check.target)
            lines.append(f'kontrol_et("{_quote(check.label)}", {target}, {expected}, {check.decimals})')
        return lines

    def closing(self) -> list[str]:
        return ['cat("\\nBütün değerler ders notlarıyla uyuşuyor.\\n")']
