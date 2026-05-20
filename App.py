import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import core.data_provider as dp


# LOAD CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("styles/style.css")
# ini SIDEBAR
st.set_page_config(page_title="IDX Portofolio Intelligence", page_icon="📊")
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
#     st.markdown(body="""
# <div style =
# """)

# ini page Dashboard
if page == "Dashboard":
    pass
elif page == "Market Overview":
    st.markdown(
        '<div class="hero-title">IDX Market<br>Overview</div>', unsafe_allow_html=True
    )
    with st.spinner("TUNGGU GUYS"):
        df = dp.fetch_stock_data()

    if df.empty:
        st.error("Can't Fetch data, check your connection")
        st.stop()
    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    # st.write(c1)
    with c1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="metric-label">Stocks Tracked</div>
            <div class="metric-value">{len(df)}</div>
            <div class="metric-sub">IDX Listed Equities</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        average_PE = (df["PE_Ratio"].dropna()).mean()
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average PE/Ratio</div>
                    <div class="metric-value"> {average_PE:.1f}x </div>
                    <div class="metric-sub"> Average PE Accross Industries </div> 
                    </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        average_ROE = df["ROE"].dropna().mean()
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average ROE</div>
                    <div class="metric-value"> {average_ROE:.1f}% </div>
                    <div class="metric-sub"> Average ROE Accross Industries </div> 
                    </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        average_BETA = df["Beta"].dropna().mean()
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average BETA </div>
                    <div class="metric-value"> {average_BETA:.1f} </div>
                    <div class="metric-sub">Market Sensitivity </div> 
                    </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header">ALL STOCKS</div>', unsafe_allow_html=True)

    sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
    selected_sector = st.selectbox("Filter by Sector", sectors)
    view_df = df if selected_sector == "All" else df[df["Sector"] == selected_sector]

    # Display table
    display_cols = [
        "Ticker",
        "Name",
        "Industry",
        "Price",
        "PE_Ratio",
        "ROE",
        "Beta",
        "DivYield",
        "PBV",
    ]
    # import pandas as pd
    fmt_df = view_df[display_cols].copy()
    fmt_df["ROE"] = fmt_df["ROE"].apply(
        lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
    )
    fmt_df["DivYield"] = fmt_df["DivYield"].apply(
        lambda x: f"{x*100:.2f}%" if pd.notna(x) else "—"
    )
    fmt_df["Price"] = fmt_df["Price"].apply(
        lambda x: f"Rp {x:,.0f}" if pd.notna(x) and x else "—"
    )
    fmt_df["PE_Ratio"] = fmt_df["PE_Ratio"].apply(
        lambda x: f"{x:.1f}x" if pd.notna(x) else "—"
    )
    fmt_df["Beta"] = fmt_df["Beta"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    fmt_df["PBV"] = fmt_df["PBV"].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "—")

    st.dataframe(fmt_df.reset_index(drop=True), use_container_width=True, height=480)


elif page == "Portfolio Management":
    pass
else:
    pass
