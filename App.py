import streamlit as st
from pages.market_overview import show_market_overview
from pages.portofolio_management import show_portofolio_management
from pages.stock_explorer import show_stock_explorer


# LOAD CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("styles/style.css")
st.set_page_config(
    page_title="IDX Portofolio Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ini SIDEBAR
with st.sidebar:
    st.markdown(
        body="""
    <div style='padding: 10px 0 10px;'>
        <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;
                    background:linear-gradient(135deg,#fff,#00d4aa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;'>
            IDX Portfolio<br>Management
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        label="Navigate",
        options=[
            "📈  Market Overview",
            "🔍  Stock Explorer",
            "💼  Portfolio Management",
        ],
        label_visibility="collapsed",
    )
    page = page.split("  ")[1]

    st.divider()


if page == "Portfolio Management":
    show_portofolio_management()

elif page == "Market Overview":
    show_market_overview()
elif page == "Stock Explorer":
    show_stock_explorer()
else:
    st.stop()
