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


def test_every_render_plotly_call_has_nonempty_xy_titles():
    failures = []
    for path in TOPICS_DIR.glob("*.py"):
        for call in _calls_in(path):
            if _call_name(call) != "render_plotly":
                continue
            kwargs = {kw.arg: kw.value for kw in call.keywords if kw.arg}
            for required in ("x_title", "y_title"):
                value = kwargs.get(required)
                if not isinstance(value, ast.Constant) or not isinstance(value.value, str) or not value.value.strip():
                    failures.append(f"{path}:{call.lineno} -> {required}")
    assert not failures, "Eksik/boş grafik eksen başlığı: " + ", ".join(failures)
