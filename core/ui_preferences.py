from __future__ import annotations

import streamlit as st


TEXT_SCALE_OPTIONS = {
    "%100": 1.00,
    "%110": 1.10,
    "%120": 1.20,
    "%130": 1.30,
}


def render_text_scale_control() -> None:
    """Render a single-source text scaling preference in the sidebar."""
    label = st.sidebar.select_slider(
        "Metin ölçeği",
        options=list(TEXT_SCALE_OPTIONS),
        value="%100",
        key="text_scale_label",
    )
    scale = TEXT_SCALE_OPTIONS[label]
    st.session_state["text_scale"] = scale

    # Scale is applied once through a CSS custom property. Child components
    # derive rem values from it and do not apply an additional em multiplier.
    st.markdown(
        f"""
        <style>
        :root {{ --course-text-scale: {scale}; }}
        .stApp p, .stApp li, .stApp label {{
            font-size: calc(1rem * var(--course-text-scale));
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
