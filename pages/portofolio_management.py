import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core.ahp_engine import AHPEngine
from core.data_provider import fetch_stock_data
from core.idx_tickers import IDX_STOCKS

# ─────────────────────────────────────────────
#  KRITERIA AHP (5 kriteria fundamental)
# ─────────────────────────────────────────────
CRITERIA = {
    "ROE":      {"label": "Return on Equity",    "benefit": True,  "desc": "Semakin tinggi semakin baik"},
    "DivYield": {"label": "Dividend Yield",       "benefit": True,  "desc": "Semakin tinggi semakin baik"},
    "PE_Ratio": {"label": "P/E Ratio",            "benefit": False, "desc": "Semakin rendah semakin baik"},
    "PBV":      {"label": "Price to Book Value",  "benefit": False, "desc": "Semakin rendah semakin baik"},
    "Beta":     {"label": "Beta (Risiko)",         "benefit": False, "desc": "Semakin rendah semakin stabil"},
}

SAATY_SCALE = {
    1: "Sama pentingnya",
    2: "Di antara sama & sedikit lebih penting",
    3: "Sedikit lebih penting",
    4: "Di antara sedikit & cukup lebih penting",
    5: "Cukup lebih penting",
    6: "Di antara cukup & sangat lebih penting",
    7: "Sangat lebih penting",
    8: "Di antara sangat & mutlak lebih penting",
    9: "Mutlak lebih penting",
}

# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def safe_val(v, fallback=0.0):
    try:
        f = float(v)
        return f if (f == f and f is not None) else fallback
    except Exception:
        return fallback


def build_criteria_matrix(user_inputs: dict) -> np.ndarray:
    """Build NxN pairwise criteria matrix dari user inputs {(c1,c2): value}."""
    n = len(CRITERIA)
    keys = list(CRITERIA.keys())
    idx = {k: i for i, k in enumerate(keys)}
    matrix = np.ones((n, n))
    for (c1, c2), val in user_inputs.items():
        i, j = idx[c1], idx[c2]
        v = max(1/9, min(9, val))
        matrix[i][j] = v
        matrix[j][i] = 1 / v
    return matrix


def ahp_weights(matrix: np.ndarray):
    """Return (weights, lambda_max, CI, CR, is_consistent)."""
    engine = AHPEngine()
    ok, weights, cr = engine.validity_check(matrix)
    n = matrix.shape[0]
    norm = matrix / matrix.sum(axis=0)
    w = norm.mean(axis=1)
    lam = np.mean(np.dot(matrix, w) / w)
    ci = (lam - n) / (n - 1)
    return weights, lam, ci, cr, ok


def score_alternatives(df: pd.DataFrame, crit_weights: np.ndarray) -> pd.DataFrame:
    """Hitung skor AHP tiap saham berdasarkan bobot kriteria."""
    engine = AHPEngine()
    crit_keys = list(CRITERIA.keys())
    n = len(df)

    # Bangun matriks alternatif per kriteria
    W_alt = np.zeros((n, len(crit_keys)))
    for ci, crit in enumerate(crit_keys):
        vals = [safe_val(df.iloc[i][crit]) for i in range(n)]
        benefit = CRITERIA[crit]["benefit"]
        mat = engine.build_matrix_alternative(vals, benefit=benefit)
        norm = mat / mat.sum(axis=0)
        W_alt[:, ci] = norm.mean(axis=1)

    final_scores = W_alt @ crit_weights
    df = df.copy()
    df["AHP_Score"] = final_scores

    # Tambah bobot per kriteria
    for ci, crit in enumerate(crit_keys):
        df[f"w_{crit}"] = W_alt[:, ci]

    df = df.sort_values("AHP_Score", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df


def gauge_cr(cr: float):
    color = "#00d4aa" if cr <= 0.1 else "#ff4d6d"
    label = "✅ Konsisten" if cr <= 0.1 else "⚠️ Tidak Konsisten — ubah perbandingan"
    return color, label


# ─────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────
def show_portofolio_management():
    st.markdown('<div class="hero-title">Portfolio<br>Management</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Rangking saham IDX menggunakan metode <b>AHP (Analytic Hierarchy Process)</b> '
        '— tentukan bobot kriteria lalu sistem menghitung prioritas terbaik untuk portofolio Anda.</div>',
        unsafe_allow_html=True,
    )

    # ── STEP 1 : Pilih Saham ──────────────────────────────────────────────────
    st.markdown("## 🏦 Step 1 — Pilih Saham")
    st.markdown("Pilih minimal **2** saham yang ingin dibandingkan (maksimal 10).")

    ticker_labels = {f"{t.replace('.JK','')} — {n}": t for t, n in IDX_STOCKS.items()}
    chosen_labels = st.multiselect(
        "Pilih saham IDX",
        options=list(ticker_labels.keys()),
        default=list(ticker_labels.keys())[:5],
        max_selections=10,
        label_visibility="collapsed",
    )
    chosen_tickers = [ticker_labels[lbl] for lbl in chosen_labels]

    if len(chosen_tickers) < 2:
        st.info("ℹ️ Pilih minimal 2 saham untuk melanjutkan.")
        st.stop()

    # Fetch data
    with st.spinner("Mengambil data saham dari Yahoo Finance…"):
        df_raw = fetch_stock_data(tuple(chosen_tickers))

    if df_raw.empty:
        st.error("Gagal mengambil data saham. Coba lagi.")
        st.stop()

    # Tampilkan preview data saham
    with st.expander("📋 Preview data saham yang dipilih", expanded=False):
        preview_cols = ["Ticker", "Name", "Sector", "Price", "ROE", "DivYield", "PE_Ratio", "PBV", "Beta"]
        avail_cols = [c for c in preview_cols if c in df_raw.columns]
        fmt = {}
        for c in ["ROE", "DivYield"]:
            if c in avail_cols:
                fmt[c] = "{:.2%}"
        for c in ["Price", "PE_Ratio", "PBV", "Beta"]:
            if c in avail_cols:
                fmt[c] = "{:.2f}"
        st.dataframe(
            df_raw[avail_cols].style.format(fmt, na_rep="—"),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── STEP 2 : Bobot Kriteria (Pairwise Comparison) ────────────────────────
    st.markdown("## ⚖️ Step 2 — Perbandingan Berpasangan Kriteria")
    st.markdown(
        "Tentukan **seberapa penting** satu kriteria dibandingkan kriteria lainnya "
        "menggunakan Skala Saaty (1–9). Nilai **positif** → kriteria kiri lebih penting; "
        "nilai **1** → sama penting."
    )

    crit_keys = list(CRITERIA.keys())
    crit_labels = {k: CRITERIA[k]["label"] for k in crit_keys}

    # State untuk menyimpan input pairwise
    if "pw_inputs" not in st.session_state:
        st.session_state.pw_inputs = {}

    pairs = [(crit_keys[i], crit_keys[j]) for i in range(len(crit_keys)) for j in range(i + 1, len(crit_keys))]

    # Tampilkan slider per pasang
    cols_per_row = 1
    pair_values = {}

    for c1, c2 in pairs:
        col_l, col_s, col_r = st.columns([3, 4, 3])
        with col_l:
            st.markdown(
                f"<div style='text-align:right;padding-top:8px;font-size:13px;"
                f"color:#00d4aa;font-weight:600'>{crit_labels[c1]}</div>",
                unsafe_allow_html=True,
            )
        with col_s:
            key = f"pw_{c1}_{c2}"
            val = st.select_slider(
                label=f"{c1} vs {c2}",
                options=list(range(-9, 0)) + [1] + list(range(2, 10)),
                value=st.session_state.pw_inputs.get((c1, c2), 1),
                format_func=lambda x: (
                    f"← {abs(x)}×  {crit_labels[c2][:20]}" if x < 0
                    else ("= Sama" if x == 1 else f"{x}×  {crit_labels[c1][:20]}  →")
                ),
                key=key,
                label_visibility="collapsed",
            )
            pair_values[(c1, c2)] = val
            st.session_state.pw_inputs[(c1, c2)] = val
        with col_r:
            st.markdown(
                f"<div style='padding-top:8px;font-size:13px;color:#0097ff;font-weight:600'>"
                f"{crit_labels[c2]}</div>",
                unsafe_allow_html=True,
            )

    # Build matrix & hitung bobot
    user_inputs_normalized = {}
    for (c1, c2), raw in pair_values.items():
        if raw < 0:
            user_inputs_normalized[(c1, c2)] = 1 / abs(raw)
        elif raw == 1:
            user_inputs_normalized[(c1, c2)] = 1.0
        else:
            user_inputs_normalized[(c1, c2)] = float(raw)

    crit_matrix = build_criteria_matrix(user_inputs_normalized)
    weights, lam_max, ci, cr, is_consistent = ahp_weights(crit_matrix)

    # Tampilkan hasil bobot kriteria
    st.markdown("### 📊 Hasil Bobot Kriteria")
    cr_color, cr_label = gauge_cr(cr)

    col_cr, col_lam, col_ci = st.columns(3)
    with col_cr:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-label">Consistency Ratio (CR)</div>
                <div class="metric-value" style="color:{cr_color}">{cr:.4f}</div>
                <div class="metric-sub">{cr_label}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_lam:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-label">λ Max (Eigenvalue)</div>
                <div class="metric-value">{lam_max:.4f}</div>
                <div class="metric-sub">Ideal = {len(crit_keys):.0f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_ci:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-label">Consistency Index (CI)</div>
                <div class="metric-value">{ci:.4f}</div>
                <div class="metric-sub">CR ≤ 0.10 = konsisten</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Bar chart bobot kriteria
    fig_weights = go.Figure(
        go.Bar(
            x=[crit_labels[k] for k in crit_keys],
            y=weights,
            marker_color=["#00d4aa", "#0097ff", "#ff6b35", "#a78bfa", "#fbbf24"],
            text=[f"{w:.1%}" for w in weights],
            textposition="outside",
        )
    )
    fig_weights.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5", family="DM Sans"),
        yaxis=dict(tickformat=".0%", gridcolor="#1e2d45", showgrid=True),
        xaxis=dict(showgrid=False),
        margin=dict(t=20, b=10, l=10, r=10),
        height=280,
        showlegend=False,
    )
    st.plotly_chart(fig_weights, use_container_width=True)

    # Tabel bobot kriteria
    df_weights = pd.DataFrame({
        "Kriteria": [crit_labels[k] for k in crit_keys],
        "Bobot": weights,
        "Jenis": [("✅ Benefit" if CRITERIA[k]["benefit"] else "🔻 Cost") for k in crit_keys],
        "Keterangan": [CRITERIA[k]["desc"] for k in crit_keys],
    }).sort_values("Bobot", ascending=False)
    st.dataframe(
        df_weights.style.format({"Bobot": "{:.4f}"}).bar(subset=["Bobot"], color="#00d4aa40"),
        use_container_width=True,
        hide_index=True,
    )

    if not is_consistent:
        st.warning(
            "⚠️ **CR > 0.10** — matriks perbandingan tidak konsisten. "
            "Silakan revisi perbandingan agar hasil lebih valid."
        )

    st.divider()

    # ── STEP 3 : Hitung & Tampilkan Ranking ──────────────────────────────────
    st.markdown("## 🏆 Step 3 — Hasil Ranking Portofolio AHP")

    with st.spinner("Menghitung skor AHP untuk tiap saham…"):
        df_scored = score_alternatives(df_raw, weights)

    # ── Pairwise matrix visual ────────────────────────────────────────────────
    with st.expander("🔢 Matriks Perbandingan Kriteria", expanded=False):
        df_matrix = pd.DataFrame(
            crit_matrix,
            index=[crit_labels[k] for k in crit_keys],
            columns=[crit_labels[k] for k in crit_keys],
        )
        st.dataframe(df_matrix.style.format("{:.3f}").background_gradient(cmap="Blues"), use_container_width=True)

    # ── Ranking cards ─────────────────────────────────────────────────────────
    top3 = df_scored.head(3)
    medals = ["🥇", "🥈", "🥉"]
    badge_colors = ["#00d4aa", "#0097ff", "#ff6b35"]

    card_html = "<div style='display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap;'>"
    for i, row in top3.iterrows():
        medal = medals[i] if i < 3 else f"#{i+1}"
        color = badge_colors[i] if i < 3 else "#6b7c99"
        ticker_clean = str(row.get("Ticker", "")).replace(".JK", "")
        name = str(row.get("Name", "—"))[:22]
        score = row.get("AHP_Score", 0)
        roe = safe_val(row.get("ROE", 0))
        div = safe_val(row.get("DivYield", 0))
        pe = safe_val(row.get("PE_Ratio", 0))
        card_html += f"""
        <div style='flex:1;min-width:180px;background:#151d2e;border:1px solid {color}40;
                    border-radius:14px;padding:20px 18px;position:relative;overflow:hidden;'>
          <div style='position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,{color},{color}55);'></div>
          <div style='font-size:28px;margin-bottom:4px;'>{medal}</div>
          <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:{color};'>{ticker_clean}</div>
          <div style='font-size:12px;color:#6b7c99;margin-bottom:12px;'>{name}</div>
          <div style='font-family:DM Mono,monospace;font-size:24px;font-weight:700;color:#e8edf5;'>
            {score:.4f}
          </div>
          <div style='font-size:11px;color:#6b7c99;margin-top:4px;letter-spacing:.08em;text-transform:uppercase;'>
            AHP Score
          </div>
          <div style='margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;'>
            <div style='background:#0a0e17;border-radius:6px;padding:6px 8px;'>
              <div style='color:#6b7c99;'>ROE</div>
              <div style='color:#e8edf5;font-weight:600;'>{roe:.1%}</div>
            </div>
            <div style='background:#0a0e17;border-radius:6px;padding:6px 8px;'>
              <div style='color:#6b7c99;'>Div Yield</div>
              <div style='color:#e8edf5;font-weight:600;'>{div:.2%}</div>
            </div>
            <div style='background:#0a0e17;border-radius:6px;padding:6px 8px;'>
              <div style='color:#6b7c99;'>P/E</div>
              <div style='color:#e8edf5;font-weight:600;'>{pe:.1f}×</div>
            </div>
          </div>
        </div>"""
    card_html += "</div>"
    st.markdown(card_html, unsafe_allow_html=True)

    # ── Full Ranking Table ────────────────────────────────────────────────────
    st.markdown("### 📋 Tabel Ranking Lengkap")
    display_cols = ["Rank", "Ticker", "Name", "Sector", "AHP_Score", "ROE", "DivYield", "PE_Ratio", "PBV", "Beta"]
    avail = [c for c in display_cols if c in df_scored.columns]

    styled = df_scored[avail].style.format({
        "AHP_Score": "{:.4f}",
        "ROE": "{:.2%}",
        "DivYield": "{:.2%}",
        "PE_Ratio": "{:.2f}",
        "PBV": "{:.2f}",
        "Beta": "{:.2f}",
    }).bar(subset=["AHP_Score"], color="#00d4aa40")

    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Radar / Spider chart per saham ────────────────────────────────────────
    st.markdown("### 🕸️ Radar Chart — Bobot Alternatif per Kriteria")
    crit_weight_cols = [f"w_{k}" for k in crit_keys]
    avail_radar = [c for c in crit_weight_cols if c in df_scored.columns]

    if avail_radar:
        fig_radar = go.Figure()
        colors_radar = px.colors.qualitative.Plotly
        theta_labels = [crit_labels[k] for k in crit_keys if f"w_{k}" in avail_radar]

        for i, row in df_scored.iterrows():
            vals = [row[f"w_{k}"] for k in crit_keys if f"w_{k}" in avail_radar]
            vals += [vals[0]]  # close polygon
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=theta_labels + [theta_labels[0]],
                mode="lines+markers",
                name=str(row["Ticker"]).replace(".JK", ""),
                line=dict(color=colors_radar[i % len(colors_radar)], width=2),
                fill="toself",
                fillcolor=colors_radar[i % len(colors_radar)].replace("rgb", "rgba").replace(")", ",0.07)"),
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, gridcolor="#1e2d45", color="#6b7c99"),
                angularaxis=dict(gridcolor="#1e2d45", color="#6b7c99"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf5", family="DM Sans"),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.25,
                font=dict(size=11), bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(t=20, b=60, l=40, r=40),
            height=400,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Horizontal bar chart final score ─────────────────────────────────────
    st.markdown("### 📊 Visualisasi Skor Akhir AHP")
    df_bar = df_scored.copy()
    df_bar["TickerClean"] = df_bar["Ticker"].str.replace(".JK", "", regex=False)
    df_bar = df_bar.sort_values("AHP_Score")

    bar_colors = ["#00d4aa" if i == len(df_bar) - 1 else "#0097ff" if i == len(df_bar) - 2
                  else "#ff6b35" if i == len(df_bar) - 3 else "#1e2d45"
                  for i in range(len(df_bar))]

    fig_bar = go.Figure(go.Bar(
        x=df_bar["AHP_Score"],
        y=df_bar["TickerClean"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{s:.4f}" for s in df_bar["AHP_Score"]],
        textposition="outside",
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8edf5", family="DM Sans"),
        xaxis=dict(gridcolor="#1e2d45", showgrid=True),
        yaxis=dict(showgrid=False),
        margin=dict(t=10, b=10, l=10, r=60),
        height=max(250, len(df_bar) * 42),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Alokasi Portofolio Rekomendasi ────────────────────────────────────────
    st.divider()
    st.markdown("## 💰 Rekomendasi Alokasi Portofolio")
    st.markdown("Alokasi dana proporsional berdasarkan skor AHP, hanya untuk saham dengan CR konsisten.")

    total_invest = st.number_input(
        "Total investasi (Rp)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=10_000_000,
        step=1_000_000,
        format="%d",
    )

    top_n = st.slider("Jumlah saham terpilih untuk alokasi", 2, min(len(df_scored), 10), min(5, len(df_scored)))
    df_alloc = df_scored.head(top_n).copy()
    score_sum = df_alloc["AHP_Score"].sum()
    df_alloc["Alokasi_%"] = df_alloc["AHP_Score"] / score_sum
    df_alloc["Alokasi_Rp"] = (df_alloc["Alokasi_%"] * total_invest).round(-3)

    # Pie chart alokasi
    col_pie, col_tbl = st.columns([1, 1])
    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=df_alloc["Ticker"].str.replace(".JK", "", regex=False),
            values=df_alloc["Alokasi_%"],
            hole=0.5,
            marker=dict(colors=px.colors.qualitative.Plotly[:top_n]),
            textinfo="label+percent",
            textfont=dict(size=12),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8edf5", family="DM Sans"),
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_tbl:
        df_alloc_display = df_alloc[["Rank", "Ticker", "Name", "AHP_Score", "Alokasi_%", "Alokasi_Rp"]].copy()
        st.dataframe(
            df_alloc_display.style.format({
                "AHP_Score": "{:.4f}",
                "Alokasi_%": "{:.1%}",
                "Alokasi_Rp": "Rp {:,.0f}",
            }).bar(subset=["Alokasi_%"], color="#00d4aa40"),
            use_container_width=True,
            hide_index=True,
            height=320,
        )

    # ── Catatan Metodologi ────────────────────────────────────────────────────
    with st.expander("📚 Metodologi AHP SCPK", expanded=False):
        st.markdown("""
**Analytic Hierarchy Process (AHP)** adalah metode pengambilan keputusan multi-kriteria yang dikembangkan oleh Thomas L. Saaty.

### Langkah Perhitungan:
1. **Pairwise Comparison Matrix** — setiap kriteria dibandingkan berpasangan menggunakan Skala Saaty (1–9)
2. **Normalisasi Matrix** — tiap elemen dibagi dengan jumlah kolom
3. **Priority Vector (Bobot)** — rata-rata baris dari matrix ternormalisasi
4. **Consistency Check** — λ_max → CI → CR
   - `CI = (λ_max − n) / (n − 1)`
   - `CR = CI / RI` (RI = Random Index Saaty)
   - **CR ≤ 0.10** → konsisten ✅
5. **Matriks Alternatif** — tiap saham dibandingkan per kriteria; *benefit* = nilai tinggi lebih baik; *cost* = nilai rendah lebih baik
6. **Skor Akhir** — perkalian matriks bobot alternatif × bobot kriteria

### Kriteria yang Digunakan:
| Kriteria | Jenis | Keterangan |
|---|---|---|
| ROE | Benefit | Semakin tinggi semakin baik |
| Dividend Yield | Benefit | Semakin tinggi semakin baik |
| P/E Ratio | Cost | Semakin rendah = lebih murah |
| PBV | Cost | Semakin rendah = lebih murah |
| Beta | Cost | Semakin rendah = lebih stabil |
        """)