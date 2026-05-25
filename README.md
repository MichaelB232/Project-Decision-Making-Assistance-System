# 📊 IDX Portfolio Management

IDX Portfolio Management is a Streamlit-based financial analytics and portfolio management dashboard designed for Indonesian stock market investors.  
The application integrates market analytics, stock screening, and AHP (Analytical Hierarchy Process) based portfolio decision-making into a modern interactive dashboard.

---

# ✨ Features

## 📈 Market Overview

- Real-time IDX stock data using Yahoo Finance
- Top gainers & losers analysis
- Sector filtering
- Key market metrics:
  - Average PE Ratio
  - Average ROE
  - Average Beta
  - Dividend Yield
- Styled interactive data tables

---

## 💼 Portfolio Management

- AHP-based portfolio recommendation engine
- Multi-criteria stock evaluation
- Pairwise comparison matrix
- Weight calculation & ranking system

---

## 📐 AHP Engine

Implements Analytical Hierarchy Process including:

- Criteria comparison matrix
- Alternative comparison matrix
- Matrix normalization
- Consistency Ratio (CR) validation
- Final weighted score calculation

---

# 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Yahoo Finance API (`yfinance`)
- Plotly

---

# 📂 Project Structure

```bash
project/
│
├── App.py
├── core/
│   ├── ahp_engine.py
│   ├── chart_utils.py
│   ├── data_provider.py
│   ├── formatters.py
│   └── idx_tickers.py
│
├── pages/
│   ├── market_overview.py
│   └── portofolio_management.py
│   ├── stock_explorer.py
├── styles/
│   └── style.css
│
└── README.md
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/MichaelB232/IDX-portfolio-management
cd idx-portfolio-management
```

---

## 2. Install Dependencies

```bash
pip install -r requirement.txt
```

---

## 3. Run Application

```bash
streamlit run app.py
```

---

# 📦 Requirements

```txt
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
yfinance>=0.2.40
plotly>=6.7.0
```

---

# 🎨 UI Features

- Modern dark-mode dashboard
- Gradient-based design system
- Responsive layout
- Custom styled Streamlit components
- Dynamic market tables
- Financial data visualization

---

# 📊 Data Source

Market data is fetched from:

- Yahoo Finance API
- IDX-listed stock tickers

---

# 🧠 Analytical Hierarchy Process (AHP)

The application uses AHP methodology to:

- Rank investment alternatives
- Assign criteria importance
- Validate consistency ratio
- Generate weighted portfolio recommendations

---

# 📌 Future Improvements

- Portfolio backtesting
- Risk-adjusted optimization
- Monte Carlo simulation
- Candlestick chart visualization
- Export portfolio report to PDF
- Live IDX API integration

---

# 👨‍💻 Author

Michael Bintang
Constantine Rylianno

---

# 📄 License

This project is licensed for educational and research purposes.
