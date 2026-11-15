"""Single-page launcher for both versions: streamlit run app.py
Switching version wipes both games, so each version always starts fresh."""
import streamlit as st

st.set_page_config(page_title="AI Escape Room", page_icon="🔐")

from v1.game import render as render_v1  # noqa: E402
from v2.game import render as render_v2  # noqa: E402

VERSIONS = {
    "Version 1 - Interactive (LLM only)": render_v1,
    "Version 2 - Reliable (state + validation)": render_v2,
}

choice = st.sidebar.radio("Choose game version", list(VERSIONS), key="version_choice")

if st.session_state.get("active_version") != choice:
    for k in [k for k in st.session_state if k.startswith(("v1_", "v2_"))]:
        del st.session_state[k]          # refresh: forget the other version's game
    st.session_state.active_version = choice

VERSIONS[choice]()
