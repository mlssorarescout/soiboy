import streamlit as st
from src.styles import inject_styles
from src.dashboard import main

st.set_page_config(
    page_title="Soiboy · Sorare Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles()
main()
