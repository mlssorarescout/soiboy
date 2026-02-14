import streamlit as st

def inject_styles():
    st.markdown("""<style>
    ...PASTE YOUR FULL STYLE BLOCK HERE EXACTLY...
    </style>""", unsafe_allow_html=True)
