import yfinance as yf
import pandas as pd

IDX_STOCKS = {
    "BBCA.JK": "Bank Central Asia",
    "BBRI.JK": "Bank Rakyat Indonesia",
    "TLKM.JK": "Telekomunikasi Indonesia",
    "ASII.JK": "Astra International",
    "BMRI.JK": "Bank Mandiri",
    "UNVR.JK": "Unilever Indonesia",
    "BBNI.JK": "Bank Negara Indonesia",
    "GOTO.JK": "GoTo Gojek Tokopedia",
    "BYAN.JK": "Bayan Resources",
    "PGAS.JK": "Perusahaan Gas Negara",
    "ADRO.JK": "Adaro Energy",
    "ICBP.JK": "Indofood CBP",
    "INDF.JK": "Indofood Sukses Makmur",
    "KLBF.JK": "Kalbe Farma",
    "EXCL.JK": "XL Axiata",
    "SMGR.JK": "Semen Indonesia",
    "MNCN.JK": "Media Nusantara Citra",
    "BSDE.JK": "Bumi Serpong Damai",
    "PTBA.JK": "Bukit Asam",
    "GGRM.JK": "Gudang Garam",
    "HMSP.JK": "HM Sampoerna",
    "INTP.JK": "Indocement Tunggal",
    "CPIN.JK": "Charoen Pokphand Indonesia",
    "JPFA.JK": "Japfa Comfeed",
    "JSMR.JK": "Jasa Marga",
    "ANTM.JK": "Aneka Tambang",
    "MEDC.JK": "Medco Energi",
    "MIKA.JK": "Mitra Keluarga Karyasehat",
    "SIDO.JK": "Industri Jamu Sido Muncul",
    "TOWR.JK": "Sarana Menara Nusantara",
}


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


# asda
def get_price_history(ticker, period="1y"):
    return yf.Ticker(ticker).history(period=period)
