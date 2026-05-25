import yfinance as yf
import pandas as pd
from core.idx_tickers import IDX_STOCKS
import streamlit as st
import os


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock_data(tickerList=list(IDX_STOCKS.keys())):
    # Kalau CSV sudah ada, langsung baca — skip fetch
    if os.path.exists("data.csv"):
        return pd.read_csv("data.csv")

    # Kalau belum ada, baru fetch dari yfinance
    all_data = []
    for ticker in tickerList:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Past24H: ambil dari history, bukan info
            hist = stock.history(period="2d")
            past_24h = (
                round(
                    (
                        (hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                        / hist["Close"].iloc[-2]
                    )
                    * 100,
                    2,
                )
                if len(hist) >= 2
                else 0
            )

            data = {
                "Ticker": ticker,
                "Name": IDX_STOCKS.get(ticker, info.get("shortName", "N/A")),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Price": info.get("currentPrice", 0),
                "MarketCap": info.get("marketCap", 0),
                "ROE": info.get("returnOnEquity", 0),
                "DER": info.get("debtToEquity", 0),
                "DivYield": info.get("dividendYield", 0),
                "PE_Ratio": info.get("trailingPE", 0),
                "PBV": info.get("priceToBook", 0),
                "Beta": info.get("beta", 0),
                "Past24H": past_24h,
            }
            all_data.append(data)

        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv("data.csv", index=False)  # Simpan ke CSV
    return df


# asda
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_price_history(ticker: str, period: str = "1y"):
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_top_gainers(tickerList=IDX_STOCKS, period="1D"):
    top_gainers = []
    lose_gainers = []

    period_map = {
        "1D": ("5d", -2),
        "1W": ("1mo", -6),
        "1M": ("3mo", 0),
        "3M": ("6mo", 0),
        "1Y": ("1y", 0),
    }

    yf_period, compare_idx = period_map[period]

    for ticker in tickerList:
        try:
            stock = yf.Ticker(ticker)

            hist = stock.history(period=yf_period)

            if len(hist) < 2:
                continue

            latest_close = hist["Close"].iloc[-1]

            # ambil harga pembanding
            if compare_idx == 0:
                old_price = hist["Close"].iloc[0]
            else:
                if abs(compare_idx) > len(hist):
                    continue

                old_price = hist["Close"].iloc[compare_idx]

            change_pct = ((latest_close - old_price) / old_price) * 100

            if change_pct >= 0.0:

                top_gainers.append(
                    {
                        "Ticker": ticker,
                        "Name": stock.info.get("shortName", "N/A"),
                        "Price": round(latest_close, 2),
                        "ChangePct": round(change_pct, 2),
                    }
                )
            else:
                lose_gainers.append(
                    {
                        "Ticker": ticker,
                        "Name": stock.info.get("shortName", "N/A"),
                        "Price": round(latest_close, 2),
                        "ChangePct": round(change_pct, 2),
                    }
                )
        except Exception as e:
            print(f"{ticker}: {e}")

    df_gainers = pd.DataFrame(top_gainers)
    df_losers = pd.DataFrame(lose_gainers)

    return (
        df_gainers.head(20).sort_values(by="ChangePct", ascending=False),
        df_losers.head(20).sort_values(by="ChangePct", ascending=True),
    )
