import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from core.data_provider import fetch_stock_data
from core.idx_tickers import IDX_STOCKS

from core.ahp_service import (
    CRITERIA,
    build_criteria_matrix,
    ahp_weights,
    score_alternatives,
    gauge_cr,
    safe_val
)

# ─────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────
def show_portofolio_management():

    st.markdown(
        '<div class="hero-title">Portfolio<br>Management</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-sub">Rangking saham IDX menggunakan metode '
        '<b>AHP (Analytic Hierarchy Process)</b></div>',
        unsafe_allow_html=True,
    )

    # STEP 1
    st.markdown("## 🏦 Step 1 — Pilih Saham")

    ticker_labels = {
        f"{t.replace('.JK','')} — {n}": t
        for t, n in IDX_STOCKS.items()
    }

    chosen_labels = st.multiselect(
        "Pilih saham IDX",
        options=list(ticker_labels.keys()),
        default=list(ticker_labels.keys())[:5],
        max_selections=10,
    )

    chosen_tickers = [
        ticker_labels[lbl]
        for lbl in chosen_labels
    ]

    if len(chosen_tickers) < 2:
        st.info("Pilih minimal 2 saham")
        st.stop()

    # FETCH DATA
    with st.spinner("Mengambil data saham..."):

        df_raw = fetch_stock_data(
            tuple(chosen_tickers)
        )

    if df_raw.empty:
        st.error("Gagal mengambil data")
        st.stop()

    # STEP 2
    st.markdown("## ⚖️ Step 2 — Pairwise Comparison")

    crit_keys = list(CRITERIA.keys())

    crit_labels = {
        k: CRITERIA[k]["label"]
        for k in crit_keys
    }

    if "pw_inputs" not in st.session_state:
        st.session_state.pw_inputs = {}

    pairs = [
        (crit_keys[i], crit_keys[j])
        for i in range(len(crit_keys))
        for j in range(i + 1, len(crit_keys))
    ]

    pair_values = {}

    for c1, c2 in pairs:

        val = st.select_slider(
            f"{c1} vs {c2}",
            options=list(range(-9, 0)) + [1] + list(range(2, 10)),
            value=1
        )

        pair_values[(c1, c2)] = val

    # NORMALISASI INPUT
    user_inputs_normalized = {}

    for (c1, c2), raw in pair_values.items():

        if raw < 0:
            user_inputs_normalized[(c1, c2)] = 1 / abs(raw)

        elif raw == 1:
            user_inputs_normalized[(c1, c2)] = 1.0

        else:
            user_inputs_normalized[(c1, c2)] = float(raw)

    # HITUNG AHP
    crit_matrix = build_criteria_matrix(
        user_inputs_normalized
    )

    weights, lam_max, ci, cr, is_consistent = ahp_weights(
        crit_matrix
    )

    # HASIL BOBOT
    st.markdown("## 📊 Bobot Kriteria")

    fig_weights = go.Figure(
        go.Bar(
            x=[crit_labels[k] for k in crit_keys],
            y=weights
        )
    )

    st.plotly_chart(
        fig_weights,
        use_container_width=True
    )

    # HITUNG RANKING
    df_scored = score_alternatives(
        df_raw,
        weights
    )

    # TABEL RANKING
    st.markdown("## 🏆 Ranking Saham")

    st.dataframe(
        df_scored,
        use_container_width=True
    )

    # BAR CHART
    fig_bar = go.Figure(
        go.Bar(
            x=df_scored["AHP_Score"],
            y=df_scored["Ticker"],
            orientation="h"
        )
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )