import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import (
    DISCRETE_COLORS,
    style_plotly_fig,
    render_page_header,
    render_card_header,
    render_spacer,
    render_empty_state,
)
from utils.data_engine import render_global_sidebar

df = render_global_sidebar()

if df is None:
    render_empty_state(
        "Ad-Hoc Explorer (Self-Service BI)",
        "Dynamically build custom Bar, Line, Scatter, Box, or Treemap visualizations across any dimension and metric.",
        "Ad-Hoc Explorer",
        eyebrow="SELF-SERVICE BI",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Ad-Hoc Explorer (Self-Service BI)",
    "Dynamically build custom Bar, Line, Scatter, Box, or Treemap visualizations across any dimension and metric.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="SELF-SERVICE BI",
)

if df.empty:
    st.warning("No records match the active global filters.")
    st.stop()

render_spacer("sm")

num_cols = df.select_dtypes(include=["number"]).columns.tolist()
all_cols = df.columns.tolist()

with st.container(border=True, key="card_adhoc_cfg"):
    render_card_header(
        "Visual Builder Configuration",
        "Select chart geometry, axes, grouping, and aggregation function.",
        badge=f"{len(df):,} rows · {len(all_cols)} cols",
    )
    b1, b2, b3, b4, b5 = st.columns(5)

    default_x = all_cols.index("Market") if "Market" in all_cols else 0
    default_y = num_cols.index("Sales") if "Sales" in num_cols else 0

    with b1:
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Box", "Treemap"], index=0)
    with b2:
        x_col = st.selectbox("X-Axis / Hierarchy", all_cols, index=default_x)
    with b3:
        y_col = st.selectbox("Y-Axis (Numeric)", num_cols, index=default_y)
    with b4:
        color_options = ["None"] + all_cols
        default_color = color_options.index("Shipping Mode") if "Shipping Mode" in color_options else 0
        color_col = st.selectbox("Color / Group-By", color_options, index=default_color)
    with b5:
        agg_func = st.selectbox("Aggregation", ["Sum", "Mean", "Median", "Count"], index=0)

color_arg = None if color_col == "None" or color_col == x_col else color_col
agg_map = {"Sum": "sum", "Mean": "mean", "Median": "median", "Count": "count"}
selected_agg = agg_map[agg_func]

render_spacer("sm")

with st.container(border=True, key="card_adhoc_viz"):
    render_card_header(
        f"{chart_type} Visualization",
        f"{agg_func} of {y_col} by {x_col}" + (f" · Grouped by {color_arg}" if color_arg else ""),
        badge=chart_type,
    )
    if chart_type in ("Bar", "Line", "Treemap"):
        group_cols = [x_col] + ([color_arg] if color_arg else [])
        agg_df = df.groupby(group_cols, dropna=False)[y_col].agg(selected_agg).reset_index()

        if agg_df[x_col].nunique() > 40 and chart_type == "Bar":
            top_keys = agg_df.groupby(x_col)[y_col].sum().nlargest(40).index
            agg_df = agg_df[agg_df[x_col].isin(top_keys)]

        if chart_type == "Bar":
            fig = px.bar(
                agg_df,
                x=x_col,
                y=y_col,
                color=color_arg,
                barmode="group",
                color_discrete_sequence=DISCRETE_COLORS,
            )
        elif chart_type == "Line":
            agg_df = agg_df.sort_values(x_col)
            fig = px.line(
                agg_df,
                x=x_col,
                y=y_col,
                color=color_arg,
                markers=True,
                color_discrete_sequence=DISCRETE_COLORS,
            )
        else:
            path_cols = [x_col] + ([color_arg] if color_arg else [])
            agg_df = agg_df[agg_df[y_col] > 0]
            fig = px.treemap(
                agg_df,
                path=path_cols,
                values=y_col,
                color=y_col,
                color_continuous_scale=[DISCRETE_COLORS[1], DISCRETE_COLORS[0]],
            )
        style_plotly_fig(fig, height=480)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter":
        sample_df = df.sample(min(5000, len(df)), random_state=42)
        fig = px.scatter(
            sample_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_sequence=DISCRETE_COLORS,
            opacity=0.7,
        )
        style_plotly_fig(fig, title=f"Scatter: {y_col} vs. {x_col} (up to 5,000 sampled points)", height=480)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box":
        sample_df = df.sample(min(10000, len(df)), random_state=42)
        fig = px.box(
            sample_df,
            x=x_col,
            y=y_col,
            color=color_arg,
            color_discrete_sequence=DISCRETE_COLORS,
        )
        style_plotly_fig(fig, title=f"Distribution of {y_col} across {x_col}", height=480)
        st.plotly_chart(fig, use_container_width=True)
