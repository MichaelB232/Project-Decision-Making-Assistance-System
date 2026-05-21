import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import core.data_provider as dp
from pages.market_overview import show_market_overview


# LOAD CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("styles/style.css")

st.set_page_config(
    page_title="IDX Portofolio Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ini SIDEBAR
with st.sidebar:
    st.markdown(
        body="""
    <div style='padding: 10px 0 10px;'>
        <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;
                    background:linear-gradient(135deg,#fff,#00d4aa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;'>
            IDX Portfolio<br>Management
        </div>
        <div style='font-size:11px;color:#6b7c99;margin-top:4px;font-family:DM Mono,monospace;
                    letter-spacing:0.1em;'>AHP-BASED DECISION ENGINE</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        label="Navigate",
        options=[
            "📊  Dashboard",
            "📈  Market Overview",
            "💼  Portfolio Management",
            "📐  AHP Explained",
        ],
        label_visibility="collapsed",
    )
    page = page.split("  ")[1]

    st.divider()


if page == "Dashboard":
    pass
elif page == "Market Overview":
    show_market_overview()
elif page == "Portfolio Management":
    pass
else:
    pass
