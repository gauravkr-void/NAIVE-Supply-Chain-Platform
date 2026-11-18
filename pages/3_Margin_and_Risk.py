import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import (
    COLORS,
    style_plotly_fig,
    render_page_header,
    render_kpi_card,
    render_section_heading,
    render_card_header,
    render_spacer,
    render_empty_state,
)
from utils.data_engine import render_global_sidebar

df = render_global_sidebar()

if df is None:
    render_empty_state(
        "Profitability, Cost & Discount Leakage",
        "Isolate discount thresholds causing profit erosion, high-volume loss-making categories, and payment fraud exposure.",
        "Margin & Risk Analytics",
        eyebrow="FINANCIAL & RISK INTELLIGENCE",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Profitability, Cost & Discount Leakage",
    "Isolate discount thresholds causing profit erosion, high-volume loss-making categories, and payment fraud exposure.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="FINANCIAL & RISK INTELLIGENCE",
)

if df.empty:
    st.warning("No records match the active global filters.")
    st.stop()

caps = st.session_state.get("capabilities", {})
if not caps.get("margin", True):
    st.warning("Profitability columns (`Sales`, `Benefit per order`) are not mapped.")
    st.stop()

render_spacer("sm")

# Margin KPIs
total_sales = df["Sales"].sum()
total_profit = df["Benefit per order"].sum()
implied_cost = df["implied_cost"].sum() if "implied_cost" in df.columns else (total_sales - total_profit)
loss_value = df.loc[df["Benefit per order"] < 0, "Benefit per order"].sum()

m1, m2, m3, m4 = st.columns(4)
with m1:
    render_kpi_card("Net Profit", f"${total_profit:,.0f}", f"Margin: {(total_profit / total_sales * 100) if total_sales else 0:.2f}%", "positive" if total_profit > 0 else "negative", COLORS["primary"])
with m2:
    render_kpi_card("Implied Cost", f"${implied_cost:,.0f}", "Sales - Net Profit", "neutral", COLORS["blue"])
with m3:
    render_kpi_card("Total Loss Leakage", f"${abs(loss_value):,.0f}", f"{(df['Benefit per order'] < 0).mean() * 100:.2f}% loss-making orders", "negative", COLORS["red"])
with m4:
    avg_disc = df["Order Item Discount Rate"].mean() * 100 if "Order Item Discount Rate" in df.columns else 0.0
    render_kpi_card("Avg Discount Rate", f"{avg_disc:.2f}%", "Across filtered items", "neutral", COLORS["amber"])

# Discount Threshold & Category Quadrant
render_section_heading(
    "Discount Erosion & Category Profitability",
    "Pinpoint discount tiers turning margins negative and evaluate category-level sales vs. margin.",
)
c_disc, c_quad = st.columns(2)

with c_disc:
    with st.container(border=True, key="card_margin_disc"):
        render_card_header("Discount Tier vs. Avg Profit Ratio", "Zero-line indicates break-even threshold")
        if caps.get("discount", False) and "discount_tier" in df.columns:
            tier_order = ["0%", "1-5%", "6-10%", "11-15%", "16-20%", ">20%"]
            disc_df = (
                df.groupby("discount_tier", as_index=False)
                .agg(
                    Avg_Profit_Ratio=("Order Item Profit Ratio", lambda s: round(s.mean() * 100, 2)),
                    Net_Profit=("Benefit per order", "sum"),
                    Loss_Rate_Pct=("is_loss_making", lambda s: round(s.mean() * 100, 2)),
                    Orders=("Order Id", "count"),
                )
            )
            disc_df["discount_tier"] = pd.Categorical(disc_df["discount_tier"], categories=tier_order, ordered=True)
            disc_df = disc_df.sort_values("discount_tier")
            disc_df["Status"] = disc_df["Avg_Profit_Ratio"].apply(lambda x: "Profitable" if x >= 0 else "Negative Margin")

            fig_disc = px.bar(
                disc_df,
                x="discount_tier",
                y="Avg_Profit_Ratio",
                color="Status",
                color_discrete_map={"Profitable": COLORS["primary"], "Negative Margin": COLORS["red"]},
                text_auto=".2f",
            )
            fig_disc.add_hline(y=0, line_dash="dash", line_color=COLORS["text_muted"])
            style_plotly_fig(fig_disc, height=395, xaxis_title="Discount Tier", yaxis_title="Avg Profit Ratio (%)")
            st.plotly_chart(fig_disc, use_container_width=True)

            neg_tiers = disc_df[disc_df["Avg_Profit_Ratio"] < 0]["discount_tier"].astype(str).tolist()
            if neg_tiers:
                st.caption(f"Negative margin threshold detected at discount tier(s): {', '.join(neg_tiers)}")
        else:
            st.info("Discount rate & profit ratio columns not available.")

with c_quad:
    with st.container(border=True, key="card_margin_quad"):
        render_card_header("Category Profitability Quadrant", "Bubble size represents order volume")
        if "Category Name" in df.columns:
            cat_df = (
                df.groupby("Category Name", as_index=False)
                .agg(
                    Total_Sales=("Sales", "sum"),
                    Net_Profit=("Benefit per order", "sum"),
                    Orders=("Order Id", "count"),
                )
            )
            cat_df["Profit_Margin_Pct"] = (cat_df["Net_Profit"] / cat_df["Total_Sales"].replace(0, pd.NA) * 100).round(2)
            cat_df["Health"] = cat_df["Profit_Margin_Pct"].apply(lambda x: "Profitable" if x >= 0 else "Loss-Making")

            fig_quad = px.scatter(
                cat_df,
                x="Total_Sales",
                y="Profit_Margin_Pct",
                size="Orders",
                color="Health",
                hover_name="Category Name",
                color_discrete_map={"Profitable": COLORS["primary"], "Loss-Making": COLORS["red"]},
                size_max=42,
            )
            fig_quad.add_hline(y=0, line_dash="dash", line_color=COLORS["text_muted"])
            style_plotly_fig(fig_quad, height=395, xaxis_title="Total Sales ($)", yaxis_title="Profit Margin (%)")
            st.plotly_chart(fig_quad, use_container_width=True)
        else:
            st.info("Category Name column not available.")

# Payment Method & Fraud Exposure
render_section_heading(
    "Payment Method & Fraud Exposure",
    "Suspected fraud and cancellation rates segmented by payment instrument.",
)
with st.container(border=True, key="card_margin_pay"):
    if "Type" in df.columns and "Order Status" in df.columns:
        pay_df = df.copy()
        pay_df["Is_Fraud"] = (pay_df["Order Status"] == "SUSPECTED_FRAUD").astype(int)
        pay_df["Is_Canceled"] = (pay_df["Order Status"] == "CANCELED").astype(int)
        pay_agg = (
            pay_df.groupby("Type", as_index=False)
            .agg(
                Total_Sales=("Sales", "sum"),
                Orders=("Order Id", "count"),
                Fraud_Rate_Pct=("Is_Fraud", lambda s: round(s.mean() * 100, 2)),
                Cancel_Rate_Pct=("Is_Canceled", lambda s: round(s.mean() * 100, 2)),
            )
            .sort_values("Fraud_Rate_Pct", ascending=False)
        )
        p_left, p_right = st.columns([3, 2])
        with p_left:
            render_card_header("Fraud & Cancellation Rates by Payment Type", "Grouped percentage comparison")
            pay_melt = pay_agg.melt(
                id_vars="Type",
                value_vars=["Fraud_Rate_Pct", "Cancel_Rate_Pct"],
                var_name="Risk Metric",
                value_name="Rate (%)",
            )
            fig_pay = px.bar(
                pay_melt,
                x="Type",
                y="Rate (%)",
                color="Risk Metric",
                barmode="group",
                color_discrete_map={"Fraud_Rate_Pct": COLORS["red"], "Cancel_Rate_Pct": COLORS["amber"]},
                text_auto=".2f",
            )
            style_plotly_fig(fig_pay, height=330, xaxis_title="Payment Method", yaxis_title="Rate (%)")
            st.plotly_chart(fig_pay, use_container_width=True)
        with p_right:
            render_card_header("Payment Method Risk Scorecard", "Sales, order count & risk rates")
            st.dataframe(
                pay_agg.style.format({"Total_Sales": "${:,.0f}", "Orders": "{:,}", "Fraud_Rate_Pct": "{:.2f}%", "Cancel_Rate_Pct": "{:.2f}%"}),
                use_container_width=True,
                hide_index=True,
                height=315,
            )
    else:
        st.info("Payment `Type` and `Order Status` columns are required for fraud exposure analysis.")
