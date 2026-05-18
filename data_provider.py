import yfinance as yf
import pandas as pd


def get_stock_data(tickerList):
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
                "Price": info.get("currentPrice"),
                "MarketCap": info.get("marketCap"),
                "ROE": info.get("returnOnEquity"),
                "DER": info.get("debtToEquity"),
                "DivYield": info.get("dividendYield"),
                "PE_Ratio": info.get("trailingPE"),
                "PBV": info.get("priceToBook"),
                "Beta": info.get("beta"),
            }
            all_data.append(data)
    except Exception as e:
        print(f"Failed to fetch data {ticker} : {e}")
    return pd.DataFrame(all_data)


def get_price_history(ticker, period="1y"):
    return yf.Ticker(ticker).history(period=period)
