import pandas as pd
import numpy as np
import streamlit as st
from core.idx_tickers import IDX_STOCKS
from core.data_provider import fetch_stock_data
from core.data_provider import fetch_price_history
import plotly.graph_objects as go


def show_stock_explorer():
    st.markdown(
        '<div class="hero-title">Stock<br>Explorer</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-sub">Deep-dive into any IDX stock — Fundamentals, Technicals & Price History</div>',
        unsafe_allow_html=True,
    )

    ticker_labels = {f"{t.replace('.JK','')} — {n}": t for t, n in IDX_STOCKS.items()}
    chosen_label = st.selectbox("Select a stock", list(ticker_labels.keys()))
    chosen_ticker = ticker_labels[chosen_label]

    period = st.select_slider(
        "Price history period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y"
    )

    with st.spinner(f"Loading {chosen_ticker}…"):
        info_df = fetch_stock_data((chosen_ticker,))
        hist = fetch_price_history(chosen_ticker, period)

    if info_df.empty:
        st.warning("No data available for this ticker.")
        st.stop()

    row = info_df.iloc[0]

    # Header card
    st.markdown(
        f"""
    <div class="metric-card" style="margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-family:Syne,sans-serif;font-size:30px;font-weight:800;
                            color:#0097ff;">{row.get('Ticker','—')}</div>
                <div style="font-size:16px;color:#e8edf5;margin-top:2px;">{row.get('Name','—')}</div>
                <div style="font-size:12px;color:#6b7c99;margin-top:4px;">{row.get('Sector','—')} · {row.get('Industry','—')}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:#e8edf5;">
                    Rp {row.get('Price',0):,.0f}
                </div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Fundamental Metriks
    st.markdown(
        '<div class="section-header">FUNDAMENTALS</div>', unsafe_allow_html=True
    )
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    metrics = [
        (
            f1,
            "P/E Ratio",
            (
                f"{row.get('PE_Ratio',np.nan):.1f}x"
                if pd.notna(row.get("PE_Ratio"))
                else "—"
            ),
            "",
        ),
        (
            f2,
            "P/BV",
            f"{row.get('PBV',np.nan):.2f}x" if pd.notna(row.get("PBV")) else "—",
            "",
        ),
        (
            f3,
            "ROE",
            f"{row.get('ROE',np.nan)*100:.1f}%" if pd.notna(row.get("ROE")) else "—",
            "",
        ),
        (
            f4,
            "DER",
            f"{row.get('DER',np.nan):.2f}" if pd.notna(row.get("DER")) else "—",
            "",
        ),
        (
            f5,
            "Div Yield",
            (
                f"{row.get('DivYield',np.nan)*100:.2f}%"
                if pd.notna(row.get("DivYield"))
                else "—"
            ),
            "",
        ),
        (
            f6,
            "Beta",
            f"{row.get('Beta',np.nan):.2f}" if pd.notna(row.get("Beta")) else "—",
            "",
        ),
    ]
    for col, label, val, sub in metrics:
        with col:
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:20px;">{val}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    # Price chart
    if not hist.empty and "Close" in hist.columns:

        st.markdown(
            '<div class="section-header">PRICE HISTORY</div>', unsafe_allow_html=True
        )

        close = hist["Close"].squeeze().dropna()

        latest_price = close.iloc[-1]
        max_price = close.max()
        min_price = close.min()

        fig = go.Figure()

        # Price Line
        fig.add_trace(
            go.Scatter(
                x=close.index,
                y=close.values,
                mode="lines",
                name="Close Price",
                line=dict(color="#00d4aa", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,212,170,0.08)",
                hovertemplate="<b>%{x}</b><br>"
                + "Price: Rp %{y:,.0f}"
                + "<extra></extra>",
            )
        )
        # Latest Price Marker
        fig.add_trace(
            go.Scatter(
                x=[close.index[-1]],
                y=[latest_price],
                mode="markers+text",
                text=[f"Latest Rp {latest_price:,.0f}"],
                textposition="top right",
                marker=dict(
                    size=10, color="#ffffff", line=dict(color="#00d4aa", width=2)
                ),
                hovertemplate="<b>Latest</b><br>"
                + "%{x}<br>"
                + "Rp %{y:,.0f}"
                + "<extra></extra>",
            )
        )

        # Highest Price Marker
        fig.add_trace(
            go.Scatter(
                x=[close.idxmax()],
                y=[max_price],
                mode="markers+text",
                text=[f"High Rp {max_price:,.0f}"],
                textposition="top center",
                marker=dict(size=9, color="#00d4aa"),
                hovertemplate="<b>Highest Price</b><br>"
                + "%{x}<br>"
                + "Rp %{y:,.0f}"
                + "<extra></extra>",
            )
        )

        # Lowest Price Marker
        fig.add_trace(
            go.Scatter(
                x=[close.idxmin()],
                y=[min_price],
                mode="markers+text",
                text=[f"Low Rp {min_price:,.0f}"],
                textposition="bottom center",
                marker=dict(size=9, color="#ff4d6d"),
                hovertemplate="<b>Lowest Price</b><br>"
                + "%{x}<br>"
                + "Rp %{y:,.0f}"
                + "<extra></extra>",
            )
        )

        fig.update_layout(
            height=450,
            template="plotly_dark",
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220",
            margin=dict(l=20, r=20, t=20, b=20),
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor="#1e2d45", title=""),
            yaxis=dict(title="Price (IDR)", showgrid=True, gridcolor="#1e2d45"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Volume Chart
        if "Volume" in hist.columns:

            st.markdown(
                '<div class="section-header">VOLUME</div>', unsafe_allow_html=True
            )

            vol = hist["Volume"].squeeze().dropna()

            fig2 = go.Figure()

            fig2.add_trace(
                go.Bar(
                    x=vol.index,
                    y=vol.values,
                    marker_color="#0097ff",
                    opacity=0.7,
                    hovertemplate="<b>%{x}</b><br>"
                    + "Volume: %{y:,.0f}"
                    + "<extra></extra>",
                )
            )

            fig2.update_layout(
                height=250,
                template="plotly_dark",
                paper_bgcolor="#0b1220",
                plot_bgcolor="#0b1220",
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(title="Volume", showgrid=True, gridcolor="#1e2d45"),
            )

            st.plotly_chart(fig2, use_container_width=True)
