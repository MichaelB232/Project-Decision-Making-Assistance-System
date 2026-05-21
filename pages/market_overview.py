import streamlit as st
from core.ahp_engine import AHPEngine
import core.data_provider as dp
import pandas as pd


def show_market_overview():
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

    st.markdown('<div class="section-header"> Sector Distribution </div>', True)

    def color_change(val):
        if val > 0:
            return "color: #00f5c4; font-weight: 600;"
        elif val < 0:
            return "color: #ff4b6e; font-weight: 600;"
        return ""

    def format_change(val):
        if val > 0:
            return f"▲ {val:.2f}%"
        elif val < 0:
            return f"▼ {abs(val):.2f}%"
        return f"{val:.2f}%"

    with st.spinner():
        top_gainers, top_losers = dp.fetch_top_gainers(period="1W")

    gainers_display = top_gainers.copy()

    gainers_display = top_gainers.style.map(color_change, subset=["ChangePct"]).format(
        {"ChangePct": format_change}
    )

    losers_display = top_losers.copy()
    losers_display = top_losers.style.map(color_change, subset=["ChangePct"]).format(
        {"ChangePct": format_change}
    )

    col1, col2 = st.columns([10, 1.4])

    with col1:
        st.markdown(
            "<div class='section-header-2'>Top 20 Stock Gainers</div>",
            unsafe_allow_html=True,
        )

    with col2:
        period = st.selectbox(
            "", ["24H", "1W", "1M", "1Y"], label_visibility="collapsed"
        )
    st.dataframe(gainers_display, use_container_width=True, height=480)

    st.markdown(
        "<div class='section-header-2'>Top 20 Loser Stock</div>", unsafe_allow_html=True
    )
    st.dataframe(losers_display, use_container_width=True, height=480)
