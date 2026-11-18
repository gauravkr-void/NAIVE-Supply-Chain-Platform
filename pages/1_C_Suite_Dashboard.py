import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import (
    COLORS,
    style_plotly_fig,
    render_page_header,
    render_kpi_card,
    render_callout_banner,
    render_section_heading,
    render_card_header,
    render_spacer,
    render_empty_state,
)
from utils.data_engine import render_global_sidebar, compute_dataset_kpis, compute_benchmark_deltas, BENCHMARK_METRICS

df = render_global_sidebar()

if df is None:
    render_empty_state(
        "Executive Overview",
        "Top-line revenue, net profitability, delivery SLA performance, and product extremes.",
        "Executive Overview",
        eyebrow="C-SUITE COMMAND CENTER",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Executive Overview",
    "Top-line revenue, net profitability, delivery SLA performance, and product extremes under active global filters.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="C-SUITE COMMAND CENTER",
)

if df.empty:
    st.warning("No records match the active global filters. Please broaden your sidebar slicers.")
    st.stop()

caps = st.session_state.get("capabilities", {})
if not caps.get("executive", True):
    st.warning("Required executive columns (`Sales`, `Benefit per order`, `order_date`) are not mapped. Visit Data Studio to map them.")
    st.stop()

render_spacer("sm")

# Primary KPI Scorecards
kpis = compute_dataset_kpis(df)
deltas = compute_benchmark_deltas(df)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_kpi_card(
        "Total Revenue (Sales)",
        f"${kpis['total_sales'] / 1e6:,.2f}M" if kpis["total_sales"] >= 1e6 else f"${kpis['total_sales']:,.0f}",
        f"Benchmark: ${BENCHMARK_METRICS['total_sales'] / 1e6:,.2f}M",
        "neutral",
        COLORS["blue"],
    )
with k2:
    render_kpi_card(
        "Net Profit & Margin",
        f"${kpis['total_profit'] / 1e6:,.2f}M" if abs(kpis["total_profit"]) >= 1e6 else f"${kpis['total_profit']:,.0f}",
        f"{kpis['profit_margin_pct']:.2f}% Margin ({deltas['margin_delta_pp']:+.2f} pp)",
        "positive" if deltas["margin_delta_pp"] >= 0 else "negative",
        COLORS["primary"],
    )
with k3:
    render_kpi_card(
        "On-Time Delivery (OTD)",
        f"{kpis['otd_rate_pct']:.2f}%",
        f"{deltas['otd_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['otd_rate_pct']:.2f}%",
        "positive" if deltas["otd_delta_pp"] >= 0 else "negative",
        COLORS["primary"] if kpis["otd_rate_pct"] >= 50 else COLORS["amber"],
    )
with k4:
    render_kpi_card(
        "Unique Order Volume",
        f"{kpis['unique_orders']:,}",
        f"{len(df):,} Order Line Items",
        "neutral",
        COLORS["violet"],
    )
with k5:
    render_kpi_card(
        "Loss-Making Order Rate",
        f"{kpis['loss_rate_pct']:.2f}%",
        f"{deltas['loss_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['loss_rate_pct']:.2f}%",
        "positive" if deltas["loss_delta_pp"] <= 0 else "negative",
        COLORS["red"],
    )

# Automated Executive Callouts
callout_parts = []
if "Market" in df.columns:
    mkt_agg = df.groupby("Market", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Benefit per order", "sum"))
    top_mkt = mkt_agg.sort_values("Sales", ascending=False).iloc[0]
    callout_parts.append(
        f"Top Market: {top_mkt['Market']} generated ${top_mkt['Sales']:,.0f} in sales (${top_mkt['Profit']:,.0f} profit)."
    )
if "Category Name" in df.columns:
    cat_agg = df.groupby("Category Name", as_index=False).agg(
        Profit=("Benefit per order", "sum"),
        Loss_Orders=("is_loss_making", "sum"),
    )
    worst_cat = cat_agg.sort_values("Loss_Orders", ascending=False).iloc[0]
    callout_parts.append(
        f"Highest Profit-Draining Category: {worst_cat['Category Name']} recorded {int(worst_cat['Loss_Orders']):,} loss-making line items."
    )

if callout_parts:
    render_spacer("sm")
    render_callout_banner("Automated Executive Callout", " | ".join(callout_parts), variant="info")

# Revenue vs Profit Dual-Axis Time Series + Market Performance
render_section_heading(
    "Revenue Trends & Market Performance",
    "Track dual-axis revenue vs. net profit over time alongside regional market contribution.",
)
col_ts, col_mkt = st.columns([3, 2])

with col_ts:
    with st.container(border=True, key="card_exec_ts"):
        render_card_header("Revenue vs. Net Profit Trend", "Dual-axis time series")
        granularity = st.radio("Time Granularity", ["Monthly", "Quarterly"], horizontal=True, key="exec_gran")
        freq = "ME" if granularity == "Monthly" else "QE"
        ts_df = (
            df.dropna(subset=["order_date"])
            .set_index("order_date")
            .resample(freq)
            .agg(Sales=("Sales", "sum"), Profit=("Benefit per order", "sum"))
            .reset_index()
        )
        fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ts.add_trace(
            go.Scatter(
                x=ts_df["order_date"],
                y=ts_df["Sales"],
                name="Total Sales ($)",
                mode="lines+markers",
                line=dict(color=COLORS["blue"], width=2.5),
                fill="tozeroy",
                fillcolor="rgba(37, 99, 235, 0.08)",
            ),
            secondary_y=False,
        )
        fig_ts.add_trace(
            go.Scatter(
                x=ts_df["order_date"],
                y=ts_df["Profit"],
                name="Net Profit ($)",
                mode="lines+markers",
                line=dict(color=COLORS["primary"], width=2.5),
            ),
            secondary_y=True,
        )
        style_plotly_fig(fig_ts, title=f"{granularity} Revenue vs. Net Profit", height=350)
        fig_ts.update_yaxes(title_text="Total Sales ($)", secondary_y=False, showgrid=True, gridcolor=COLORS["grid"])
        fig_ts.update_yaxes(title_text="Net Profit ($)", secondary_y=True, showgrid=False)
        st.plotly_chart(fig_ts, use_container_width=True)

with col_mkt:
    with st.container(border=True, key="card_exec_mkt"):
        render_card_header("Market Sales vs. Net Profit", "Grouped regional breakdown")
        if "Market" in df.columns:
            mkt_df = (
                df.groupby("Market", as_index=False)
                .agg(Sales=("Sales", "sum"), Profit=("Benefit per order", "sum"))
                .sort_values("Sales", ascending=False)
            )
            mkt_melt = mkt_df.melt(id_vars="Market", value_vars=["Sales", "Profit"], var_name="Metric", value_name="USD")
            fig_mkt = px.bar(
                mkt_melt,
                x="Market",
                y="USD",
                color="Metric",
                barmode="group",
                color_discrete_map={"Sales": COLORS["blue"], "Profit": COLORS["primary"]},
            )
            style_plotly_fig(fig_mkt, height=445, xaxis_title="Market", yaxis_title="USD ($)")
            st.plotly_chart(fig_mkt, use_container_width=True)
        else:
            st.info("Market dimension not available in active dataset.")

# Top 10 Revenue Products vs Bottom 10 Loss-Making Products
if "Product Name" in df.columns:
    render_section_heading(
        "Product Performance Extremes",
        "Highest-grossing SKUs compared against the largest net-loss drivers.",
    )
    p1, p2 = st.columns(2)
    prod_agg = df.groupby("Product Name", as_index=False).agg(
        Total_Sales=("Sales", "sum"),
        Net_Profit=("Benefit per order", "sum"),
        Orders=("Order Id", "nunique"),
        Late_Rate_Pct=("is_late", lambda s: round(s.mean() * 100, 2)),
    )
    prod_agg["Margin %"] = (prod_agg["Net_Profit"] / prod_agg["Total_Sales"].replace(0, pd.NA) * 100).round(2)

    with p1:
        with st.container(border=True, key="card_exec_top10"):
            render_card_header("Top 10 Revenue-Generating Products", "Sorted by total sales", badge="Top Performers")
            top10 = prod_agg.sort_values("Total_Sales", ascending=False).head(10)
            st.dataframe(
                top10.style.format({"Total_Sales": "${:,.0f}", "Net_Profit": "${:,.0f}", "Margin %": "{:.2f}%", "Late_Rate_Pct": "{:.1f}%"}),
                use_container_width=True,
                hide_index=True,
                height=380,
            )

    with p2:
        with st.container(border=True, key="card_exec_bot10"):
            render_card_header("Bottom 10 Loss-Making Products", "Sorted by lowest net profit", badge="Margin Risk")
            bot10 = prod_agg.sort_values("Net_Profit", ascending=True).head(10)
            st.dataframe(
                bot10.style.format({"Total_Sales": "${:,.0f}", "Net_Profit": "${:,.0f}", "Margin %": "{:.2f}%", "Late_Rate_Pct": "{:.1f}%"}),
                use_container_width=True,
                hide_index=True,
                height=380,
            )
