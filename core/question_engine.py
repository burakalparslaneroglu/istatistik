from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence



@dataclass(frozen=True)
class Question:
    prompt: str
    answer: str


def current_question_index(topic_key: str, question_count: int) -> int:
    import streamlit as st
    if question_count <= 0:
        raise ValueError("Soru havuzu boş olamaz.")
    key = f"{topic_key}_question_index"
    if key not in st.session_state:
        st.session_state[key] = 0
    return int(st.session_state[key]) % question_count


def render_question_card(topic_key: str, questions: Sequence[Question]) -> None:
    import streamlit as st
    if not questions:
        raise ValueError("Soru havuzu boş olamaz.")

    index_key = f"{topic_key}_question_index"
    visible_key = f"{topic_key}_answer_visible"
    if index_key not in st.session_state:
        st.session_state[index_key] = 0
    if visible_key not in st.session_state:
        st.session_state[visible_key] = False

    idx = int(st.session_state[index_key]) % len(questions)
    question = questions[idx]

    with st.container(border=True):
        st.markdown("#### Kısa kontrol")
        st.write(question.prompt)

        col_answer, col_next = st.columns(2)
        with col_answer:
            label = "Cevabı gizle" if st.session_state[visible_key] else "Cevabı göster"
            if st.button(label, type="primary", key=f"{topic_key}_toggle_answer"):
                st.session_state[visible_key] = not st.session_state[visible_key]
                st.rerun()
        with col_next:
            if st.button("Yeni soru", key=f"{topic_key}_next_question"):
                st.session_state[index_key] = (idx + 1) % len(questions)
                st.session_state[visible_key] = False
                st.rerun()

        if st.session_state[visible_key]:
            st.info(question.answer)
