from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from utils.theme import render_page_header, render_card_header, render_spacer
from utils.data_engine import render_global_sidebar

render_global_sidebar()

BASE_DIR = Path(__file__).resolve().parent.parent
PBI_DIR = BASE_DIR / "power_BI"
PBIX_PATH = PBI_DIR / "SupplyChainAnalysis.pbix"

# Optional: Paste your Power BI Service "Publish to web" URL here if you have one
PBI_EMBED_URL = ""

render_page_header(
    "Power BI Companion Dashboard",
    "Executive Power BI report views (Supply Chain Overview, Price Dynamics, and Delivery & SLA Performance).",
    badge_text="3 Report Pages",
    badge_variant="default",
    eyebrow="ENTERPRISE BI INTEGRATION",
)

render_spacer("sm")

col_info, col_dl = st.columns([3, 1])
with col_info:
    with st.container(border=True, key="card_pbi_info"):
        render_card_header(
            "About This Report",
            "Built in Microsoft Power BI Desktop with DAX measures, Year/Market/Segment slicers, and cross-filtering.",
        )
        st.caption("Use the tabs below to inspect each Power BI page, or download the .pbix workbook to explore locally.")

with col_dl:
    with st.container(border=True, key="card_pbi_dl"):
        render_card_header("Workbook", "Power BI Desktop (.pbix)")
        if PBIX_PATH.exists():
            st.download_button(
                label="Download .pbix File",
                data=PBIX_PATH.read_bytes(),
                file_name="SupplyChainAnalysis.pbix",
                mime="application/octet-stream",
                type="primary",
                use_container_width=True,
            )
        else:
            st.info("Place `SupplyChainAnalysis.pbix` inside `powerbi/`.")

render_spacer("md")

if PBI_EMBED_URL.strip():
    with st.container(border=True, key="card_pbi_live"):
        render_card_header("Live Interactive Power BI Report", "Embedded via Power BI Service")
        components.iframe(PBI_EMBED_URL.strip(), height=720, scrolling=True)
else:
    tab1, tab2, tab3 = st.tabs([
        "1. Supply Chain Overview",
        "2. Price Dynamics",
        "3. Delivery & SLA Performance",
    ])

    pages_info = [
        (tab1, "01_supply_chain_overview.png", "Supply Chain Overview", "Net Revenue ($33.05M), OTD (45.17%), Margin (12.00%), and Regional KPIs"),
        (tab2, "02_price_dynamics.png", "Price Dynamics", "Gross Sales ($36.78M), Discounts ($3.73M), Loss-Making Rate (18.71%), and Category Quadrant"),
        (tab3, "03_delivery_sla.png", "Delivery & SLA Performance", "Actual vs. Scheduled Lead Time (3.50 vs. 2.93 days) and Late Delivery Rate (54.83%)"),
    ]

    for tab, img_name, title, subtitle in pages_info:
        with tab:
            with st.container(border=True, key=f"card_pbi_{img_name}"):
                render_card_header(title, subtitle)
                img_path = PBI_DIR / img_name
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.warning(f"Screenshot not found: `powerbi/{img_name}`")