from __future__ import annotations

import ast
from pathlib import Path


TOPICS_DIR = Path("topics")


def _calls_in(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield node


def _call_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts = []
        cur = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return ".".join(reversed(parts))
    return None


def test_topic_files_do_not_bypass_shared_plotly_renderer():
    offenders = []
    for path in TOPICS_DIR.glob("*.py"):
        for call in _calls_in(path):
            if _call_name(call) == "st.plotly_chart":
                offenders.append(str(path))
    assert not offenders, f"Doğrudan st.plotly_chart kullanımı bulundu: {offenders}"


def test_plotly_chart_is_called_only_by_the_shared_renderers():
    allowed = {Path("core/charts.py")}
    offenders = []
    for path in [*Path("core").rglob("*.py"), *TOPICS_DIR.glob("*.py"), Path("app.py")]:
        if path in allowed:
            continue
        for call in _calls_in(path):
            if _call_name(call) == "st.plotly_chart":
                offenders.append(str(path))
    assert not offenders, f"Ortak grafik katmanı dışında st.plotly_chart: {offenders}"


def test_shared_figure_renderer_rejects_missing_axis_titles():
    import plotly.graph_objects as go
    import pytest

    from core.charts import show_figure, style_figure

    figure = style_figure(go.Figure(go.Bar(x=["a"], y=[1])), title="Başlık", x_title="Kategori", y_title="")
    with pytest.raises(ValueError, match="eksen adı"):
        show_figure(figure)


def test_every_lab_and_experiment_chart_has_axis_titles():
    import importlib

    from core.labs.registry import LABS
    from core.labs.spec import AXISLESS_CHARTS, CHARTS, Histogram

    experiments = []
    for key in LABS:
        module = importlib.import_module(f"core.labs.sezgi_{key}")
        experiments.extend(getattr(module, f"{key.upper()}_EXPERIMENTS"))
    operations = [op for spec in LABS.values() for step in spec.steps for op in step.operations]
    operations += [op for experiment in experiments for op in experiment.build(experiment.defaults())]
    for op in operations:
        if not isinstance(op, CHARTS):
            continue
        assert op.title.strip(), op
        if isinstance(op, AXISLESS_CHARTS):  # pasta dilimleri ve olasılık ağacında eksen yoktur
            continue
        assert op.x_label.strip(), op
        assert isinstance(op, Histogram) or op.y_label.strip(), op
