import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.theme import (
    COLORS,
    style_plotly_fig,
    render_page_header,
    render_section_heading,
    render_card_header,
    render_spacer,
    render_empty_state,
)
from utils.data_engine import render_global_sidebar

df = render_global_sidebar()

if df is None:
    render_empty_state(
        "Customer Segmentation & Geospatial Intelligence",
        "Explore global supply chain hotspots, RFM customer cohorts, and Pareto 80/20 ABC product classification.",
        "Customer & Geospatial Intelligence",
        eyebrow="CUSTOMER & INVENTORY ANALYTICS",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Customer Segmentation & Geospatial Intelligence",
    "Explore global supply chain hotspots, RFM customer cohorts, and Pareto 80/20 ABC product classification.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="CUSTOMER & INVENTORY ANALYTICS",
)

if df.empty:
    st.warning("No records match the active global filters.")
    st.stop()

caps = st.session_state.get("capabilities", {})

# 1. Interactive Global Supply Chain Map
render_section_heading(
    "Global Supply Chain Hotspots",
    "Country-level volume, profitability, and late-delivery exposure.",
)
with st.container(border=True, key="card_geo_map"):
    render_card_header("Interactive Global Distribution Map", "Bubble size indicates unique order volume")
    if caps.get("geo", False):
        metric_choice = st.radio(
            "Map Metric Toggle",
            ["Total Sales ($)", "Net Profit ($)", "Late Delivery Rate (%)"],
            horizontal=True,
            key="geo_metric_toggle",
        )
        geo_df = (
            df.dropna(subset=["Latitude", "Longitude", "Order Country"])
            .groupby("Order Country", as_index=False)
            .agg(
                Latitude=("Latitude", "mean"),
                Longitude=("Longitude", "mean"),
                Total_Sales=("Sales", "sum"),
                Net_Profit=("Benefit per order", "sum"),
                Late_Rate_Pct=("is_late", lambda s: round(s.mean() * 100, 2)),
                Orders=("Order Id", "nunique"),
            )
        )
        metric_col_map = {
            "Total Sales ($)": ("Total_Sales", [COLORS["blue"], COLORS["primary"]]),
            "Net Profit ($)": ("Net_Profit", [COLORS["red"], COLORS["amber"], COLORS["primary"]]),
            "Late Delivery Rate (%)": ("Late_Rate_Pct", [COLORS["primary"], COLORS["amber"], COLORS["red"]]),
        }
        col_key, scale_colors = metric_col_map[metric_choice]

        fig_map = px.scatter_geo(
            geo_df,
            lat="Latitude",
            lon="Longitude",
            size="Orders",
            color=col_key,
            hover_name="Order Country",
            hover_data={"Total_Sales": ":,.0f", "Net_Profit": ":,.0f", "Late_Rate_Pct": ":.2f", "Orders": ":,"},
            color_continuous_scale=scale_colors,
            size_max=34,
            projection="natural earth",
        )
        fig_map.update_geos(
            showcoastlines=True,
            coastlinecolor=COLORS["border"],
            showland=True,
            landcolor="#F8FAFC",
            showocean=True,
            oceancolor="#FFFFFF",
            showcountries=True,
            countrycolor=COLORS["border"],
        )
        style_plotly_fig(fig_map, title=f"Global Distribution by {metric_choice}", height=410, show_legend=False)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Geospatial columns (`Order Country`, `Latitude`, `Longitude`) are not mapped in the active dataset.")

# 2. RFM Customer Segmentation & 3. ABC Product Classification
render_section_heading(
    "RFM Customer Cohorts & ABC Inventory Classification",
    "Segment customers by Recency-Frequency-Monetary value and classify SKUs via Pareto 80/20.",
)
c_rfm, c_abc = st.columns(2)

with c_rfm:
    with st.container(border=True, key="card_geo_rfm"):
        render_card_header("RFM Customer Segmentation", "Champions, Loyal, At-Risk & Churned cohorts")
        if caps.get("rfm", False):
            ref_date = df["order_date"].max() + pd.Timedelta(days=1)
            rfm = (
                df.dropna(subset=["Customer Id", "order_date"])
                .groupby("Customer Id", as_index=False)
                .agg(
                    Recency=("order_date", lambda s: (ref_date - s.max()).days),
                    Frequency=("Order Id", "nunique"),
                    Monetary=("Sales", "sum"),
                )
            )
            rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
            rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
            rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
            rfm["RFM_Sum"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

            def _assign_cohort(row):
                if row["RFM_Sum"] >= 10:
                    return "Champions"
                if row["RFM_Sum"] >= 7:
                    return "Loyal"
                if row["R_Score"] >= 2 and row["RFM_Sum"] >= 5:
                    return "At-Risk"
                return "Churned"

            rfm["Cohort"] = rfm.apply(_assign_cohort, axis=1)
            cohort_agg = (
                rfm.groupby("Cohort", as_index=False)
                .agg(
                    Customers=("Customer Id", "count"),
                    Avg_Monetary=("Monetary", "mean"),
                    Total_Revenue=("Monetary", "sum"),
                )
                .sort_values("Total_Revenue", ascending=False)
            )

            fig_rfm = px.bar(
                cohort_agg,
                x="Cohort",
                y="Customers",
                color="Cohort",
                color_discrete_map={
                    "Champions": COLORS["primary"],
                    "Loyal": COLORS["blue"],
                    "At-Risk": COLORS["amber"],
                    "Churned": COLORS["red"],
                },
                text_auto=",",
            )
            style_plotly_fig(fig_rfm, height=320, show_legend=False, xaxis_title="RFM Cohort", yaxis_title="Customers")
            st.plotly_chart(fig_rfm, use_container_width=True)
            st.dataframe(
                cohort_agg.style.format({"Customers": "{:,}", "Avg_Monetary": "${:,.0f}", "Total_Revenue": "${:,.0f}"}),
                use_container_width=True,
                hide_index=True,
                height=175,
                
            )
            at_risk_df = rfm[rfm["Cohort"].isin(["At-Risk", "Churned"])].sort_values("Monetary", ascending=False)
            st.download_button(
                label=f"Export At-Risk & Churned Customers ({len(at_risk_df):,})",
                data=at_risk_df[["Customer Id", "Cohort", "Recency", "Frequency", "Monetary"]].to_csv(index=False).encode("utf-8"),
                file_name="naive_at_risk_customers.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("RFM requires `Customer Id`, `order_date`, and `Sales`.")

with c_abc:
    with st.container(border=True, key="card_geo_abc"):
        render_card_header("ABC Product Classification (Pareto 80/20)", "Revenue concentration by SKU tier")
        if caps.get("abc", False):
            abc = (
                df.groupby("Product Name", as_index=False)
                .agg(
                    Sales=("Sales", "sum"),
                    Profit=("Benefit per order", "sum") if "Benefit per order" in df.columns else ("Sales", "count"),
                    Orders=("Order Id", "nunique"),
                )
                .sort_values("Sales", ascending=False)
                .reset_index(drop=True)
            )
            total_rev = abc["Sales"].sum()
            abc["Cum_Pct"] = (abc["Sales"].cumsum() / total_rev * 100) if total_rev else 0.0

            def _abc_class(pct: float) -> str:
                if pct <= 80.0:
                    return "Class A (Top 80%)"
                if pct <= 95.0:
                    return "Class B (Next 15%)"
                return "Class C (Bottom 5%)"

            abc["ABC_Class"] = abc["Cum_Pct"].apply(_abc_class)
            abc_summary = (
                abc.groupby("ABC_Class", as_index=False)
                .agg(
                    SKUs=("Product Name", "count"),
                    Total_Sales=("Sales", "sum"),
                    Revenue_Share_Pct=("Sales", lambda s: round(s.sum() / total_rev * 100, 2) if total_rev else 0.0),
                )
            )
            fig_abc = px.pie(
                abc_summary,
                names="ABC_Class",
                values="Total_Sales",
                hole=0.58,
                color="ABC_Class",
                color_discrete_map={
                    "Class A (Top 80%)": COLORS["primary"],
                    "Class B (Next 15%)": COLORS["blue"],
                    "Class C (Bottom 5%)": COLORS["amber"],
                },
            )
            style_plotly_fig(fig_abc, height=320)
            st.plotly_chart(fig_abc, use_container_width=True)
            st.dataframe(
                abc_summary.style.format({"SKUs": "{:,}", "Total_Sales": "${:,.0f}", "Revenue_Share_Pct": "{:.2f}%"}),
                use_container_width=True,
                hide_index=True,
                height=175,
            )
            class_a_df = abc[abc["ABC_Class"] == "Class A (Top 80%)"]
            st.download_button(
                label=f"Export Class A Core SKUs ({len(class_a_df):,})",
                data=class_a_df[["Product Name", "Sales", "Profit", "Orders", "Cum_Pct"]].to_csv(index=False).encode("utf-8"),
                file_name="naive_class_a_skus.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("ABC Classification requires `Product Name` and `Sales`.")
