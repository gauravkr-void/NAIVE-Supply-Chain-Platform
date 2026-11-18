import streamlit as st
from utils.theme import inject_custom_css
from utils.data_engine import init_session_state

st.set_page_config(
    page_title="NAIVE — Supply Chain Intelligence & Predictive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
init_session_state()

pages = [
    st.Page("pages/0_Data_Studio.py", title="0 — Data Studio", icon="🗄️", default=True),
    st.Page("pages/1_C_Suite_Dashboard.py", title="1 — C-Suite Dashboard", icon="📈"),
    st.Page("pages/2_Logistics_SLA.py", title="2 — Logistics SLA", icon="🚚"),
    st.Page("pages/3_Margin_and_Risk.py", title="3 — Margin & Risk", icon="💰"),
    st.Page("pages/4_Customer_and_Geo.py", title="4 — Customer & Geo", icon="🌍"),
    st.Page("pages/5_Ad_Hoc_Explorer.py", title="5 — Ad-Hoc Explorer", icon="🔎"),
    st.Page("pages/6_Late_Delivery_AI.py", title="6 — Late Delivery AI", icon="🤖"),
]

pg = st.navigation(pages)
pg.run()
