"""Run Version 1 alone: streamlit run v1/app.py"""
import os, sys
import streamlit as st
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from v1.game import render

st.set_page_config(page_title="AI Escape Room v1", page_icon="🔐")
render()
