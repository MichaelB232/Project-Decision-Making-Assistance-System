import numpy as np
import pandas as pd

from core.ahp_engine import AHPEngine

CRITERIA = {
    "ROE": {
        "label": "Return on Equity",
        "benefit": True,
        "desc": "Semakin tinggi semakin baik",
    },
    "DivYield": {
        "label": "Dividend Yield",
        "benefit": True,
        "desc": "Semakin tinggi semakin baik",
    },
    "PE_Ratio": {
        "label": "P/E Ratio",
        "benefit": False,
        "desc": "Semakin rendah semakin baik",
    },
    "PBV": {
        "label": "Price to Book Value",
        "benefit": False,
        "desc": "Semakin rendah semakin baik",
    },
    "Beta": {
        "label": "Beta (Risiko)",
        "benefit": False,
        "desc": "Semakin rendah semakin stabil",
    },
}


def safe_val(v, fallback=0.0):

    try:

        f = float(v)

        return f if (f == f and f is not None) else fallback

    except Exception:

        return fallback


def build_criteria_matrix(user_inputs: dict):

    n = len(CRITERIA)

    keys = list(CRITERIA.keys())

    idx = {k: i for i, k in enumerate(keys)}

    matrix = np.ones((n, n))

    for (c1, c2), val in user_inputs.items():

        i, j = idx[c1], idx[c2]

        v = max(1 / 9, min(9, val))

        matrix[i][j] = v
        matrix[j][i] = 1 / v

    return matrix


def ahp_weights(matrix):

    engine = AHPEngine()

    ok, weights, cr = engine.validity_check(matrix)

    n = matrix.shape[0]

    norm = matrix / matrix.sum(axis=0)

    w = norm.mean(axis=1)

    lam = np.mean(np.dot(matrix, w) / w)

    ci = (lam - n) / (n - 1)

    return weights, lam, ci, cr, ok


def score_alternatives(df, crit_weights):

    engine = AHPEngine()

    crit_keys = list(CRITERIA.keys())

    n = len(df)

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

    for ci, crit in enumerate(crit_keys):

        df[f"w_{crit}"] = W_alt[:, ci]

    df = df.sort_values("AHP_Score", ascending=False).reset_index(drop=True)

    df["Rank"] = df.index + 1

    return df


def gauge_cr(cr: float):

    color = "#00d4aa" if cr <= 0.1 else "#ff4d6d"

    label = "✅ Konsisten" if cr <= 0.1 else "⚠️ Tidak Konsisten"

    return color, label
