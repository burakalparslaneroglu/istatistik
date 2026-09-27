"""Yeni mimariye taşınan konu sayfalarının ortak başlığı."""

from __future__ import annotations

from html import escape

import streamlit as st

from core.topic_registry import get_topic


def render_topic_header(topic_key: str) -> None:
    topic = get_topic(topic_key)
    st.markdown(
        "<section class='topic-band'>"
        f"<div class='topic-number'>Konu {topic.number:02d}</div>"
        f"<h2>{escape(topic.title)}</h2>"
        "</section>",
        unsafe_allow_html=True,
    )
    if topic.guiding_question:
        st.markdown(
            "<div class='guiding-question'>"
            "<div class='label'>Yönlendirici soru</div>"
            f"<p>{escape(topic.guiding_question)}</p>"
            "</div>",
            unsafe_allow_html=True,
        )
