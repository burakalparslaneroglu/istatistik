"""Sunum bağlantılarının Streamlit'ten bağımsız doğrulaması ve başlangıç durumu."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from importlib import import_module
from typing import Mapping, MutableMapping, Sequence

from core.labs.registry import get_lab
from core.labs.sezgi import SimExperiment
from core.topic_registry import list_topics

TABS = {"uygulama": "Uygulama", "sezgi": "Sezgi", "kendini_sina": "Kendini sına"}
FIELDS = {"konu", "sekme", "deney", "adim", "kaynak"}


class NavigationError(ValueError):
    """Bağlantı hedefi geçersiz; hiçbir başlangıç seçimi uygulanmaz."""


def experiments_for(topic_key: str) -> tuple[SimExperiment, ...]:
    module = import_module(f"core.labs.sezgi_{topic_key}")
    return getattr(module, f"{topic_key.upper()}_EXPERIMENTS")


@dataclass(frozen=True)
class Destination:
    topic_key: str
    tab: str
    number: int | None = None
    source: str = "notlar"
    parameters: tuple[tuple[str, int | float], ...] = ()

    def initial_state(self) -> dict[str, object]:
        values: dict[str, object] = {
            "selected_topic": self.topic_key,
            f"{self.topic_key}_tab": TABS[self.tab],
        }
        if self.tab == "uygulama":
            values[f"{self.topic_key}_lab_kaynak"] = self.source
            values[f"{self.topic_key}_lab_step"] = self.number
            values[f"_{self.topic_key}_link_step"] = self.number
        elif self.tab == "sezgi":
            values[f"{self.topic_key}_sezgi_deney"] = self.number
            values.update({f"{self.topic_key}_sezgi{self.number}_{name}": value
                           for name, value in self.parameters})
        return values


def _number(text: str, allowed: Sequence[int], label: str) -> int:
    if not text.isascii() or not text.isdigit() or int(text) not in allowed:
        raise NavigationError(f"Geçersiz {label}. Geçerli numaralar: {', '.join(map(str, allowed))}.")
    return int(text)


def parse_destination(query: Mapping[str, Sequence[str]]) -> Destination | None:
    """Tekrarlanan alanları ve kaydırıcı kafesine uymayan değerleri de reddeder."""
    relevant = {key: values for key, values in query.items() if key in FIELDS or key.startswith("p_")}
    if not relevant:
        return None
    if any(len(values) != 1 for values in relevant.values()):
        raise NavigationError("Bağlantıda her seçim yalnız bir kez belirtilmelidir.")
    q = {key: values[0] for key, values in relevant.items()}
    if "konu" not in q:
        raise NavigationError("Bağlantıda konu numarası eksik.")
    topics = {f"{t.number:02d}": t.key for t in list_topics()}
    if q["konu"] not in topics:
        raise NavigationError("Geçersiz konu. Konu numarasını 01–12 biçiminde belirtin.")
    topic_key = topics[q["konu"]]
    tab = q.get("sekme", "uygulama")
    if tab not in TABS:
        raise NavigationError("Geçersiz sekme. uygulama, sezgi veya kendini_sina seçin.")
    supplied = {key[2:]: value for key, value in q.items() if key.startswith("p_")}
    if tab == "uygulama":
        if "deney" in q or supplied:
            raise NavigationError("Deney ve deney parametreleri yalnız Sezgi sekmesinde kullanılabilir.")
        source = q.get("kaynak", "notlar")
        if source not in {"notlar", "alternatif", "kendi"}:
            raise NavigationError("Geçersiz veri kaynağı. notlar, alternatif veya kendi seçin.")
        lab = get_lab(topic_key)
        number = _number(q.get("adim", "1"), [s.number for s in lab.steps], "uygulama adımı")
        return Destination(topic_key, tab, number, source)
    if "adim" in q or "kaynak" in q:
        raise NavigationError("Adım ve veri kaynağı yalnız Uygulama sekmesinde kullanılabilir.")
    if tab == "kendini_sina":
        if "deney" in q or supplied:
            raise NavigationError("Kendini sına bağlantısında deney belirtilemez.")
        return Destination(topic_key, tab)
    experiments = experiments_for(topic_key)
    number = _number(q.get("deney", "1"), [e.number for e in experiments], "deney")
    experiment = next(e for e in experiments if e.number == number)
    if set(supplied) - {p.key for p in experiment.parameters}:
        raise NavigationError("Bağlantıda bu deneye ait olmayan bir parametre var.")
    parameters = []
    for p in experiment.parameters:
        try:
            value = Decimal(supplied.get(p.key, str(p.default)))
        except InvalidOperation as error:
            raise NavigationError(f"{p.label}: sayısal bir değer gerekli.") from error
        if (not value.is_finite() or not Decimal(str(p.minimum)) <= value <= Decimal(str(p.maximum))
                or (p.integer and value != value.to_integral_value())
                or (value - Decimal(str(p.minimum))) % Decimal(str(p.step)) != 0):
            raise NavigationError(f"{p.label}: değer izin verilen aralığa ve kaydırıcı adımına uymalı.")
        parameters.append((p.key, int(value) if p.integer else float(value)))
    return Destination(topic_key, tab, number, parameters=tuple(parameters))


def initialize_navigation(query: Mapping[str, Sequence[str]], state: MutableMapping) -> str | None:
    """Değişen URL'yi bir kez uygular; aynı URL'deki kullanıcı etkileşimlerini korur."""
    signature = tuple(sorted((key, tuple(values)) for key, values in query.items()
                             if key in FIELDS or key.startswith("p_")))
    if state.get("_navigation_signature") != signature:
        try:
            destination = parse_destination(query)
        except NavigationError as error:
            state["_navigation_error"] = str(error)
        else:
            if destination is not None:
                state.update(destination.initial_state())
            state["_navigation_error"] = None
        state["_navigation_signature"] = signature
    return state.get("_navigation_error")
