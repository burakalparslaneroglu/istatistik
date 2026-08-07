from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence

import plotly.graph_objects as go
import streamlit as st


def load_css(path: Path) -> None:
    if path.exists():
        st.markdown(f"<style>{path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def topic_header(number: int, title: str, lead: str | None = None) -> None:
    st.markdown(
        f"<span class='topic-badge'>KONU {number:02d}</span>",
        unsafe_allow_html=True,
    )
    st.title(title)
    if lead:
        st.markdown(f"<div class='topic-lead'>{lead}</div>", unsafe_allow_html=True)


def learning_goals(goals: Iterable[str]) -> None:
    with st.container(border=True):
        st.markdown("#### Bu konu sonunda")
        for goal in goals:
            st.markdown(f"- {goal}")


def concept_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="concept-card">
          <div class="concept-title">{title}</div>
          <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feedback_box(correct: bool, correct_text: str, incorrect_text: str) -> None:
    if correct:
        st.success(correct_text)
    else:
        st.warning(incorrect_text)


def render_plotly(
    fig: go.Figure,
    *,
    x_title: str,
    y_title: str,
    legend_title: str | None = None,
    key: str | None = None,
) -> None:
    """Render Plotly figures with mandatory human-readable axis titles."""
    if not x_title.strip() or not y_title.strip():
        raise ValueError("Her grafikte X ve Y eksen adı açıkça belirtilmelidir.")

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend_title_text=legend_title,
        margin=dict(l=30, r=20, t=55, b=35),
        hovermode="closest",
    )
    st.plotly_chart(fig, width="stretch", key=key)


def render_definition_grid(items: Sequence[tuple[str, str]]) -> None:
    cols = st.columns(2)
    for idx, (title, body) in enumerate(items):
        with cols[idx % 2]:
            concept_card(title, body)


def render_mapping_table(rows: Sequence[Mapping[str, str]]) -> None:
    st.table(rows)
