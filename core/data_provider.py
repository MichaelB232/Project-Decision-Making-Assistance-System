import yfinance as yf
import pandas as pd

IDX_STOCKS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "TLKM.JK",
    "ASII.JK",
    "ICBP.JK",
    "INDF.JK",
    "UNVR.JK",
    "CPIN.JK",
    "ADRO.JK",
    "ANTM.JK",
    "PGAS.JK",
]


def fetch_stock_data(tickerList=IDX_STOCKS):
    all_data = []
    try:
        for ticker in tickerList:
            stock = yf.Ticker(ticker)
            info = stock.info

            data = {
                "Ticker": ticker,
                "Name": info.get("shortName", "N/A"),
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
                "Past24H": info.get("Close"),
            }
            all_data.append(data)
    except Exception as e:
        print(f"Failed to fetch data {ticker} : {e}")
    return pd.DataFrame(all_data)


# asda
def get_price_history(ticker, period="24H"):
    return yf.Ticker(ticker).history(period=period)


def fetch_top_gainers(tickerList=IDX_STOCKS, period="1W"):
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

    return df_gainers.sort_values(
        by="ChangePct", ascending=False
    ), df_losers.sort_values(by="ChangePct", ascending=True)


df = fetch_top_gainers()
print(df)
