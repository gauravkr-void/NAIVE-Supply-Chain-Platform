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
        "Logistics & Delivery SLA Diagnostics",
        "Benchmark shipping modes, pinpoint regional carrier bottlenecks, and analyze delivery variance distributions.",
        "Logistics SLA Diagnostics",
        eyebrow="OPERATIONS & CARRIER SLA",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Logistics & Delivery SLA Diagnostics",
    "Benchmark shipping modes, pinpoint regional carrier bottlenecks, and analyze delivery variance distributions.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="OPERATIONS & CARRIER SLA",
)

if df.empty:
    st.warning("No records match the active global filters.")
    st.stop()

caps = st.session_state.get("capabilities", {})
if not caps.get("logistics", True):
    st.warning("Logistics SLA columns (`Shipping Mode`, `scheduled_days`, `actual_days`, `is_late`) are not mapped.")
    st.stop()

render_spacer("sm")

# Top SLA KPIs
avg_sched = df["scheduled_days"].mean()
avg_actual = df["actual_days"].mean()
avg_var = df["delivery_variance_days"].mean()
severe_delays = (df["delivery_variance_days"] >= 3).mean() * 100

s1, s2, s3, s4 = st.columns(4)
with s1:
    render_kpi_card("Avg Scheduled SLA", f"{avg_sched:.2f} days", "Planned Lead Time", "neutral", COLORS["blue"])
with s2:
    render_kpi_card("Avg Actual Transit", f"{avg_actual:.2f} days", f"Variance: {avg_var:+.2f} days", "negative" if avg_var > 0 else "positive", COLORS["amber"])
with s3:
    late_pct = df["is_late"].mean() * 100
    render_kpi_card("SLA Breach (Late) Rate", f"{late_pct:.2f}%", f"OTD: {100 - late_pct:.2f}%", "negative" if late_pct > 50 else "positive", COLORS["red"])
with s4:
    render_kpi_card("Severe Delays (3+ Days)", f"{severe_delays:.2f}%", "Orders >= 3 days late", "negative" if severe_delays > 15 else "neutral", COLORS["violet"])

# Shipping Mode SLA Benchmarking & Regional Heatmap
render_section_heading(
    "Carrier & Regional SLA Benchmarking",
    "Compare promised vs. actual transit times across shipping tiers and geographic regions.",
)
c1, c2 = st.columns(2)

with c1:
    with st.container(border=True, key="card_sla_ship"):
        render_card_header("Shipping Mode: Scheduled vs. Actual", "Average transit days and breach rate")
        ship_df = (
            df.groupby("Shipping Mode", as_index=False)
            .agg(
                Scheduled_Days=("scheduled_days", "mean"),
                Actual_Days=("actual_days", "mean"),
                Late_Rate_Pct=("is_late", lambda s: round(s.mean() * 100, 2)),
                Orders=("Order Id", "nunique"),
            )
            .sort_values("Late_Rate_Pct", ascending=False)
        )
        ship_melt = ship_df.melt(
            id_vars="Shipping Mode",
            value_vars=["Scheduled_Days", "Actual_Days"],
            var_name="Metric",
            value_name="Days",
        )
        fig_ship = px.bar(
            ship_melt,
            x="Shipping Mode",
            y="Days",
            color="Metric",
            barmode="group",
            color_discrete_map={"Scheduled_Days": COLORS["blue"], "Actual_Days": COLORS["amber"]},
            text_auto=".2f",
        )
        style_plotly_fig(fig_ship, height=310, xaxis_title="Shipping Mode", yaxis_title="Avg Days")
        st.plotly_chart(fig_ship, use_container_width=True)
        st.dataframe(
            ship_df.style.format({"Scheduled_Days": "{:.2f}", "Actual_Days": "{:.2f}", "Late_Rate_Pct": "{:.2f}%", "Orders": "{:,}"}),
            use_container_width=True,
            hide_index=True,
            height=175,
        )

with c2:
    with st.container(border=True, key="card_sla_heat"):
        render_card_header("Regional Bottleneck Heatmap", "Late delivery percentage by region and carrier")
        if "Order Region" in df.columns:
            heat_df = df.groupby(["Order Region", "Shipping Mode"], as_index=False)["is_late"].mean()
            heat_df["Late_Pct"] = (heat_df["is_late"] * 100).round(1)
            pivot_heat = heat_df.pivot(index="Order Region", columns="Shipping Mode", values="Late_Pct").fillna(0)
            fig_heat = px.imshow(
                pivot_heat,
                text_auto=".1f",
                aspect="auto",
                color_continuous_scale=[[0.0, COLORS["primary"]], [0.5, COLORS["amber"]], [1.0, COLORS["red"]]],
                labels=dict(color="Late %"),
            )
            style_plotly_fig(fig_heat, height=500, show_legend=False)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Order Region column not available for heatmap.")

# Delivery Variance Distribution & Order/Delivery Status Funnel (Clean 2x2 Card Grid)
render_section_heading(
    "Delivery Variance & Order Status Funnel",
    "Distribution of schedule deviations and fulfillment outcomes across all orders.",
)
r1_left, r1_right = st.columns(2)

with r1_left:
    with st.container(border=True, key="card_sla_hist"):
        render_card_header("Delivery Variance Distribution", "Actual minus scheduled days")
        fig_hist = px.histogram(
            df,
            x="delivery_variance_days",
            color="Shipping Mode",
            barmode="overlay",
            nbins=20,
            color_discrete_sequence=[COLORS["primary"], COLORS["blue"], COLORS["amber"], COLORS["red"]],
            opacity=0.75,
        )
        style_plotly_fig(fig_hist, height=330, xaxis_title="Variance (Days)", yaxis_title="Line Items")
        st.plotly_chart(fig_hist, use_container_width=True)

with r1_right:
    with st.container(border=True, key="card_sla_status"):
        render_card_header("Order Status Funnel Breakdown", "Volume across fulfillment stages")
        if "Order Status" in df.columns:
            status_df = (
                df.groupby("Order Status", as_index=False)
                .agg(Count=("Order Id", "count"))
                .sort_values("Count", ascending=True)
            )
            fig_order_status = px.bar(
                status_df,
                x="Count",
                y="Order Status",
                orientation="h",
                color_discrete_sequence=[COLORS["blue"]],
                text_auto=",",
            )
            style_plotly_fig(fig_order_status, height=330, show_legend=False, xaxis_title="Line Items", yaxis_title="")
            st.plotly_chart(fig_order_status, use_container_width=True)
        else:
            st.info("Order Status column not available.")

render_spacer("sm")
r2_left, r2_right = st.columns(2)

with r2_left:
    with st.container(border=True, key="card_sla_box"):
        render_card_header("Transit Variance Spread by Mode", "Quartile distribution per shipping class")
        fig_box = px.box(
            df,
            x="Shipping Mode",
            y="delivery_variance_days",
            color="Shipping Mode",
            color_discrete_sequence=[COLORS["primary"], COLORS["blue"], COLORS["amber"], COLORS["red"]],
        )
        style_plotly_fig(fig_box, height=330, show_legend=False, xaxis_title="Shipping Mode", yaxis_title="Variance (Days)")
        st.plotly_chart(fig_box, use_container_width=True)

with r2_right:
    with st.container(border=True, key="card_sla_mix"):
        render_card_header("Delivery Status Mix", "Share of on-time, advance, late, and canceled shipments")
        if "Delivery Status" in df.columns:
            del_df = df.groupby("Delivery Status", as_index=False).agg(Count=("Order Id", "count"))
            fig_del = px.pie(
                del_df,
                names="Delivery Status",
                values="Count",
                hole=0.58,
                color="Delivery Status",
                color_discrete_map={
                    "Advance shipping": COLORS["primary"],
                    "Shipping on time": COLORS["blue"],
                    "Late delivery": COLORS["red"],
                    "Shipping canceled": COLORS["amber"],
                },
            )
            style_plotly_fig(fig_del, height=330)
            st.plotly_chart(fig_del, use_container_width=True)
        else:
            st.info("Delivery Status column not available.")
