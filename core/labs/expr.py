"""Laboratuvar tanımlarında kullanılan küçük ifade dili.

Türetilmiş değişkenler ve skalerler bir kez burada tanımlanır; aynı ifade hem
uygulamada (numpy/pandas) değerlendirilir hem de Python ve R koduna çevrilir.
Böylece iki dildeki kod ile uygulamanın hesabı tek kaynaktan gelir.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class Var:
    """Veri çerçevesindeki bir değişken (sütun)."""

    name: str


@dataclass(frozen=True)
class Const:
    value: float


@dataclass(frozen=True)
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Call:
    fn: str
    args: tuple["Expr", ...]


@dataclass(frozen=True)
class Ref:
    """Daha önce hesaplanmış bir skaler; üretilen kodda aynı adlı değişken."""

    name: str


Expr = Union[Var, Const, BinOp, Call, Ref]

BINARY_OPS = ("+", "-", "*", "/", "^")
COMPARISONS = {"le": "<=", "lt": "<", "ge": ">=", "gt": ">", "eq": "==", "ne": "!="}
"""Karşılaştırma fonksiyonları: koşul sağlanırsa 1, değilse 0 (gösterge değişkeni)."""
FUNCTIONS = (
    "log", "exp", "sqrt", "abs", "maximum", "minimum", "round", "floor", "normcdf", "normpdf", *COMPARISONS,
)
_BINARY_FUNCTIONS = ("maximum", "minimum", *COMPARISONS)
_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
_ATOM = 4


# --- Kurucular: tanım dosyalarının okunaklı kalması için -------------------

def var(name: str) -> Var:
    return Var(name)


def const(value: float) -> Const:
    return Const(float(value))


def _wrap(value: "Expr | float | int") -> "Expr":
    if isinstance(value, (int, float)):
        return Const(float(value))
    return value


def add(a, b) -> BinOp:
    return BinOp("+", _wrap(a), _wrap(b))


def sub(a, b) -> BinOp:
    return BinOp("-", _wrap(a), _wrap(b))


def mul(a, b) -> BinOp:
    return BinOp("*", _wrap(a), _wrap(b))


def div(a, b) -> BinOp:
    return BinOp("/", _wrap(a), _wrap(b))


def power(a, b) -> BinOp:
    return BinOp("^", _wrap(a), _wrap(b))


def log(a) -> Call:
    return Call("log", (_wrap(a),))


def exp(a) -> Call:
    return Call("exp", (_wrap(a),))


def sqrt(a) -> Call:
    return Call("sqrt", (_wrap(a),))


def absolute(a) -> Call:
    return Call("abs", (_wrap(a),))


def maximum(a, b) -> Call:
    return Call("maximum", (_wrap(a), _wrap(b)))


def minimum(a, b) -> Call:
    return Call("minimum", (_wrap(a), _wrap(b)))


def floor(a) -> Call:
    return Call("floor", (_wrap(a),))


def rounded(a) -> Call:
    """En yakın tam sayıya yuvarlama (sürekli çekilişlerde yarım değer olasılığı sıfırdır)."""

    return Call("round", (_wrap(a),))


def normcdf(a) -> Call:
    """Standart normal dağılım fonksiyonu Φ(a)."""

    return Call("normcdf", (_wrap(a),))


def normpdf(a) -> Call:
    """Standart normal yoğunluk φ(a)."""

    return Call("normpdf", (_wrap(a),))


def compare(name: str, a, b) -> Call:
    """Gösterge: ``a`` ile ``b`` karşılaştırması doğruysa 1, değilse 0 (``name``: le, lt, ge, gt, eq, ne)."""

    if name not in COMPARISONS:
        raise ValueError(f"Desteklenmeyen karşılaştırma: {name}")
    return Call(name, (_wrap(a), _wrap(b)))


def ref(name: str) -> Ref:
    return Ref(name)


# --- Doğrulama ---------------------------------------------------------------

def validate(expr: Expr) -> None:
    if isinstance(expr, (Var, Const, Ref)):
        return
    if isinstance(expr, BinOp):
        if expr.op not in BINARY_OPS:
            raise ValueError(f"Desteklenmeyen işlem: {expr.op}")
        validate(expr.left)
        validate(expr.right)
        return
    if isinstance(expr, Call):
        if expr.fn not in FUNCTIONS:
            raise ValueError(f"Desteklenmeyen fonksiyon: {expr.fn}")
        expected = 2 if expr.fn in _BINARY_FUNCTIONS else 1
        if len(expr.args) != expected:
            raise ValueError(f"{expr.fn} {expected} argüman alır.")
        for argument in expr.args:
            validate(argument)
        return
    raise TypeError(f"Tanınmayan ifade düğümü: {type(expr).__name__}")


def variables(expr: Expr) -> set[str]:
    """İfadenin başvurduğu veri değişkenleri."""

    if isinstance(expr, Var):
        return {expr.name}
    if isinstance(expr, BinOp):
        return variables(expr.left) | variables(expr.right)
    if isinstance(expr, Call):
        found: set[str] = set()
        for argument in expr.args:
            found |= variables(argument)
        return found
    return set()


def references(expr: Expr) -> set[str]:
    """İfadenin başvurduğu skaler adları (``ref``)."""

    if isinstance(expr, Ref):
        return {expr.name}
    if isinstance(expr, BinOp):
        return references(expr.left) | references(expr.right)
    if isinstance(expr, Call):
        found: set[str] = set()
        for argument in expr.args:
            found |= references(argument)
        return found
    return set()


def functions_in(expr: Expr) -> set[str]:
    """İfadede geçen fonksiyon adları."""

    if isinstance(expr, Call):
        found = {expr.fn}
        for argument in expr.args:
            found |= functions_in(argument)
        return found
    if isinstance(expr, BinOp):
        return functions_in(expr.left) | functions_in(expr.right)
    return set()


# --- Değerlendirme -----------------------------------------------------------

def evaluate(
    expr: Expr,
    frame: pd.DataFrame | dict | None = None,
    scalar: Callable[[str], float] | None = None,
):
    """İfadeyi bir veri çerçevesi (vektör) veya skalerler üzerinde hesaplar."""

    def again(node: Expr):
        return evaluate(node, frame, scalar)

    if isinstance(expr, Const):
        return expr.value
    if isinstance(expr, Var):
        if frame is None:
            raise ValueError(f"'{expr.name}' için veri çerçevesi gerekir.")
        return np.asarray(frame[expr.name], dtype=float)
    if isinstance(expr, Ref):
        if scalar is None:
            raise ValueError(f"'{expr.name}' skaleri için hesaplanmış skalerler gerekir.")
        return scalar(expr.name)
    if isinstance(expr, BinOp):
        left = again(expr.left)
        right = again(expr.right)
        if expr.op == "+":
            return left + right
        if expr.op == "-":
            return left - right
        if expr.op == "*":
            return left * right
        if expr.op == "/":
            return left / right
        return left**right
    if isinstance(expr, Call):
        values = [again(argument) for argument in expr.args]
        if expr.fn == "log":
            return np.log(values[0])
        if expr.fn == "exp":
            return np.exp(values[0])
        if expr.fn == "sqrt":
            return np.sqrt(values[0])
        if expr.fn == "abs":
            return np.abs(values[0])
        if expr.fn == "round":
            return np.rint(values[0])
        if expr.fn == "floor":
            return np.floor(values[0])
        if expr.fn == "normcdf":
            return stats.norm.cdf(values[0])
        if expr.fn == "normpdf":
            return stats.norm.pdf(values[0])
        if expr.fn in COMPARISONS:
            left, right = np.asarray(values[0]), np.asarray(values[1])
            outcome = {
                "le": left <= right, "lt": left < right, "ge": left >= right,
                "gt": left > right, "eq": left == right, "ne": left != right,
            }[expr.fn]
            return np.where(outcome, 1.0, 0.0)
        if expr.fn == "minimum":
            return np.minimum(values[0], values[1])
        return np.maximum(values[0], values[1])
    raise TypeError(f"Tanınmayan ifade düğümü: {type(expr).__name__}")


# --- Dile çevirme ------------------------------------------------------------

@dataclass(frozen=True)
class Dialect:
    """Bir hedef dilin ifade sözdizimi.

    ``functions`` değerleri ya bir ad (``np.exp`` → ``np.exp(x)``) ya da ``{0}``
    yer tutuculu bir kalıptır (``as.numeric({0} > {1})``).
    """

    variable: Callable[[str], str]
    functions: dict[str, str]
    power: str
    scalar: Callable[[str], str] | None = None


def format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return repr(float(value))


def _precedence(expr: Expr) -> int:
    return _PRECEDENCE[expr.op] if isinstance(expr, BinOp) else _ATOM


def render(expr: Expr, dialect: Dialect) -> str:
    """İfadeyi gereksiz parantez olmadan hedef dile yazar."""

    if isinstance(expr, Const):
        return format_number(expr.value)
    if isinstance(expr, Var):
        return dialect.variable(expr.name)
    if isinstance(expr, Ref):
        return dialect.scalar(expr.name) if dialect.scalar is not None else expr.name
    if isinstance(expr, Call):
        arguments = [render(argument, dialect) for argument in expr.args]
        spec = dialect.functions[expr.fn]
        if "{0}" in spec:
            return spec.format(*arguments)
        return f"{spec}({', '.join(arguments)})"
    parent = _PRECEDENCE[expr.op]
    left = render(expr.left, dialect)
    right = render(expr.right, dialect)
    if _precedence(expr.left) < parent or (
        expr.op == "^" and _precedence(expr.left) == parent
    ):
        left = f"({left})"
    if _precedence(expr.right) < parent or (
        expr.op in ("-", "/") and _precedence(expr.right) == parent
    ):
        right = f"({right})"
    symbol = dialect.power if expr.op == "^" else expr.op
    return f"{left} {symbol} {right}"
