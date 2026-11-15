"""Run Version 2 alone: streamlit run v2/app.py"""
import os, sys
import streamlit as st
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from v2.game import render

st.set_page_config(page_title="AI Escape Room v2", page_icon="🔐")
render()
