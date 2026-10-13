"""URL başlangıcını ortak kabukta, bileşenler kurulmadan önce uygular."""

import streamlit as st

from core.navigation import initialize_navigation


def initialize_from_url() -> None:
    query = {key: st.query_params.get_all(key) for key in st.query_params}
    error = initialize_navigation(query, st.session_state)
    if error:
        st.error(f"Sunum bağlantısı açılamadı: {error} Konuyu kenar çubuğundan seçebilirsiniz.")
