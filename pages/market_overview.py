import streamlit as st
import core.data_provider as dp
import pandas as pd
from core.formatters import format_change, color_change
import plotly.graph_objects as go


def show_market_overview():
    st.markdown(
        '<div class="hero-title">IDX Market<br>Overview</div>', unsafe_allow_html=True
    )
    with st.spinner():
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
        average_PE = df["PE_Ratio"].dropna()
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average PE/Ratio</div>
                    <div class="metric-value"> {average_PE.mean():.1f}x </div>
                    <div class="metric-sub"> Average PE Accross Industries </div> 
                    </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        average_ROE = df["ROE"].dropna() * 100
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average ROE</div>
                    <div class="metric-value"> {average_ROE.mean():.1f}% </div>
                    <div class="metric-sub"> Average ROE Accross Industries </div> 
                    </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        average_BETA = df["Beta"].dropna()
        st.markdown(
            f"""
            <div class="metric-card">
                    <div class="metric-label"> Average BETA </div>
                    <div class="metric-value"> {average_BETA.mean():.1f} </div>
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
        lambda x: f"Rp {x:,.1f}" if pd.notna(x) and x else "—"
    )
    fmt_df["PE_Ratio"] = fmt_df["PE_Ratio"].apply(
        lambda x: f"{x:.1f}x" if pd.notna(x) else "—"
    )
    fmt_df["Beta"] = fmt_df["Beta"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    fmt_df["PBV"] = fmt_df["PBV"].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "—")

    st.dataframe(fmt_df.reset_index(drop=True), use_container_width=True, height=480)

    # <--- Gainers and Losers Section ---->
    col1, col2 = st.columns([10, 1.4])

    with col1:
        st.markdown(
            "<div class='section-header-2'>Top 20 Stock Gainers</div>",
            unsafe_allow_html=True,
        )

    with col2:
        period = st.selectbox(
            "", ["1D", "1W", "1M", "1Y"], label_visibility="collapsed", index=0
        )

    with st.spinner():
        top_gainers, top_losers = dp.fetch_top_gainers(period=period)

    top_gainers[period] = top_gainers["ChangePct"]
    top_gainers.drop(columns=["ChangePct"], inplace=True)
    top_losers[period] = top_losers["ChangePct"]
    top_losers.drop(columns=["ChangePct"], inplace=True)

    # Change the format of the price
    top_gainers["Price"] = top_gainers["Price"].apply(
        lambda x: f"Rp {x:,.1f}" if pd.notna(x) and x else "—"
    )
    top_losers["Price"] = top_losers["Price"].apply(
        lambda x: f"Rp {x:,.1f}" if pd.notna(x) and x else "—"
    )

    gainers_display = top_gainers.copy()
    gainers_display = top_gainers.style.map(color_change, subset=[period]).format(
        {period: format_change}
    )

    losers_display = top_losers.copy()
    losers_display = top_losers.style.map(color_change, subset=[period]).format(
        {period: format_change}
    )
    st.dataframe(gainers_display, use_container_width=True, height=480)

    st.markdown(
        "<div class='section-header-2'>Top 20 Loser Stock</div>", unsafe_allow_html=True
    )
    st.dataframe(losers_display, use_container_width=True, height=480)
    # Sector distribution chart
    st.markdown(
        '<div class="section-header">SECTOR DISTRIBUTION</div>', unsafe_allow_html=True
    )

    sector_counts = df["Sector"].value_counts()

    colors = [
        "#00d4aa",
        "#0097ff",
        "#ff6b35",
        "#a855f7",
        "#f59e0b",
        "#ec4899",
        "#14b8a6",
        "#f97316",
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=sector_counts.values,
            y=sector_counts.index,
            orientation="h",
            marker=dict(
                color=[colors[i % len(colors)] for i in range(len(sector_counts))]
            ),
            text=sector_counts.values,
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>" + "Stocks: %{x}" + "<extra></extra>",
        )
    )

    fig.update_layout(
        height=450,
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Number of Stocks", showgrid=True, gridcolor="#1e2d45"),
        yaxis=dict(title="", autorange="reversed"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
