import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import (
    COLORS,
    style_plotly_fig,
    render_page_header,
    render_kpi_card,
    render_callout_banner,
    render_card_header,
    render_spacer,
    render_empty_state,
)
from utils.data_engine import render_global_sidebar, read_uploaded_file
from utils.ml_engine import (
    MODEL_FEATURES,
    get_benchmark_model,
    train_and_evaluate_model,
    predict_single_with_what_if,
    batch_predict_df,
)

df = render_global_sidebar()

if df is None:
    render_empty_state(
        "Late Delivery AI & What-If Simulator",
        "Real-time late-delivery risk scoring, prescriptive shipping class simulation, feature explainability, and batch CSV scoring.",
        "Late Delivery AI",
        eyebrow="PREDICTIVE & PRESCRIPTIVE ML",
    )
    st.stop()

is_custom = st.session_state.get("data_mode") != "Benchmark (180k)"
render_page_header(
    "Late Delivery AI & What-If Simulator",
    "Real-time late-delivery risk scoring, prescriptive shipping class simulation, feature explainability, and batch CSV scoring.",
    badge_text=st.session_state.get("data_mode", "Custom Upload"),
    badge_variant="custom" if is_custom else "default",
    eyebrow="PREDICTIVE & PRESCRIPTIVE ML",
)

caps = st.session_state.get("capabilities", {})
if not caps.get("ml", True):
    st.warning(
        "ML prediction requires `Shipping Mode`, `Market`, `Order Region`, `Category Name`, "
        "`Order Item Quantity`, `discount_tier`, `scheduled_days`, and `Late_delivery_risk`."
    )
    st.stop()

render_spacer("sm")

if "custom_ml_bundle" in st.session_state and st.session_state.get("use_custom_model", False):
    bundle = st.session_state["custom_ml_bundle"]
else:
    bundle = get_benchmark_model(st.session_state["df_active"])

pipeline = bundle["pipeline"]
metrics = bundle["metrics"]
imp_df = bundle["feature_importance"]

# Model Performance KPIs
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_kpi_card("Active Model", metrics["model_name"].split()[0], metrics["model_name"], "neutral", COLORS["blue"])
with m2:
    render_kpi_card("Validation Accuracy", f"{metrics['accuracy']:.2f}%", f"Val Rows: {metrics['val_rows']:,}", "positive", COLORS["primary"])
with m3:
    render_kpi_card("ROC-AUC Score", f"{metrics['roc_auc']:.4f}", f"F1: {metrics['f1']:.4f}", "positive", COLORS["violet"])
with m4:
    render_kpi_card("Precision / Recall", f"{metrics['precision']:.2f} / {metrics['recall']:.2f}", f"Train Rows: {metrics['train_rows']:,}", "neutral", COLORS["amber"])

render_spacer("md")

tab_sim, tab_explain, tab_batch = st.tabs([
    "Live Risk Predictor & What-If Simulator",
    "Explainability & On-the-Fly Retraining",
    "Batch CSV Scoring",
])

df_full = st.session_state["df_active"]
ship_modes = sorted(df_full["Shipping Mode"].dropna().astype(str).unique().tolist())
markets = sorted(df_full["Market"].dropna().astype(str).unique().tolist())
regions = sorted(df_full["Order Region"].dropna().astype(str).unique().tolist())
categories = sorted(df_full["Category Name"].dropna().astype(str).unique().tolist())
discount_tiers = ["0%", "1-5%", "6-10%", "11-15%", "16-20%", ">20%"]

with tab_sim:
    c_form, c_out = st.columns([1, 1.15])
    with c_form:
        with st.container(border=True, key="card_ml_form"):
            render_card_header("Order Parameters", "Configure scenario inputs for real-time scoring")
            sel_ship = st.selectbox("Shipping Mode", ship_modes, index=0)
            sel_market = st.selectbox("Market", markets, index=0)
            sel_region = st.selectbox("Order Region", regions, index=0)
            sel_cat = st.selectbox("Category Name", categories, index=0)
            sel_qty = st.slider("Order Item Quantity", min_value=1, max_value=10, value=1)
            sel_disc = st.selectbox("Discount Tier", discount_tiers, index=0)
            sel_sched = st.slider("Scheduled Shipping Days", min_value=0, max_value=6, value=4)

            input_payload = {
                "Shipping Mode": sel_ship,
                "Market": sel_market,
                "Order Region": sel_region,
                "Category Name": sel_cat,
                "Order Item Quantity": sel_qty,
                "discount_tier": sel_disc,
                "scheduled_days": sel_sched,
            }

    sim_result = predict_single_with_what_if(pipeline, input_payload, ship_modes)
    prob = sim_result["base_prob"]
    tier = sim_result["tier"]
    accent = COLORS[sim_result["color_key"]]

    with c_out:
        render_kpi_card(
            "Predicted Late Delivery Probability",
            f"{prob:.2f}%",
            f"Risk Tier: {tier}",
            "negative" if prob >= 50 else "positive",
            accent,
        )
        render_spacer("sm")
        if sim_result["best_mode"] != sel_ship and sim_result["risk_reduction_pp"] > 0:
            render_callout_banner(
                "Prescriptive What-If Recommendation",
                f"Switching Shipping Mode from {sel_ship} to {sim_result['best_mode']} reduces late-delivery risk by {sim_result['risk_reduction_pp']:.2f} percentage points (to {sim_result['best_prob']:.2f}%).",
                variant="success",
            )
        else:
            render_callout_banner(
                "Optimal Shipping Mode Selected",
                f"{sel_ship} currently yields the lowest predicted late-delivery probability ({prob:.2f}%) among available modes.",
                variant="info",
            )

        render_spacer("sm")
        with st.container(border=True, key="card_ml_whatif"):
            render_card_header("What-If Shipping Mode Risk Comparison", "Predicted delay probability across all carrier tiers")
            fig_wif = px.bar(
                sim_result["what_if_df"],
                x="Shipping Mode",
                y="Predicted Late Risk (%)",
                color="Shipping Mode",
                color_discrete_sequence=[COLORS["primary"], COLORS["blue"], COLORS["amber"], COLORS["red"]],
                text_auto=".2f",
            )
            style_plotly_fig(fig_wif, height=300, show_legend=False, yaxis_title="Late Risk (%)")
            st.plotly_chart(fig_wif, use_container_width=True)

with tab_explain:
    e1, e2 = st.columns([3, 2])
    with e1:
        with st.container(border=True, key="card_ml_imp"):
            render_card_header("Global Feature Importance", "Primary drivers of late delivery predictions")
            fig_imp = px.bar(
                imp_df.sort_values("Importance %", ascending=True),
                x="Importance %",
                y="Feature",
                orientation="h",
                color_discrete_sequence=[COLORS["blue"]],
                text_auto=".2f",
            )
            style_plotly_fig(fig_imp, height=360, show_legend=False, xaxis_title="Relative Importance (%)", yaxis_title="")
            st.plotly_chart(fig_imp, use_container_width=True)

    with e2:
        with st.container(border=True, key="card_ml_retrain"):
            render_card_header("On-the-Fly Model Retraining", "Fit a fresh classifier on your active dataset")
            st.caption("Train a fresh Late Delivery classifier directly on the currently active dataset without leaving the browser.")
            render_spacer("sm")
            if st.button("Retrain Classifier on Active Dataset", type="primary", use_container_width=True):
                with st.spinner("Training classifier..."):
                    new_bundle = train_and_evaluate_model(df_full, save_path=None)
                    st.session_state["custom_ml_bundle"] = new_bundle
                    st.session_state["use_custom_model"] = True
                    st.success(f"Retrained {new_bundle['metrics']['model_name']} — Accuracy: {new_bundle['metrics']['accuracy']}%")
                    st.rerun()

with tab_batch:
    with st.container(border=True, key="card_ml_batch"):
        render_card_header("Batch CSV Scoring", f"Required columns: {', '.join(MODEL_FEATURES)}")
        template_csv = df_full[MODEL_FEATURES].head(100).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Sample Unlabelled Batch CSV",
            data=template_csv,
            file_name="naive_sample_unlabelled_orders.csv",
            mime="text/csv",
        )

        render_spacer("sm")
        batch_file = st.file_uploader("Upload Order Batch (.csv)", type=["csv"], key="batch_ml_upload")
        if batch_file is not None:
            batch_raw, _ = read_uploaded_file(batch_file)
            scored_df = batch_predict_df(pipeline, batch_raw)
            high_risk_cnt = int((scored_df["Risk_Probability"] >= 65.0).sum())
            high_risk_pct = (high_risk_cnt / len(scored_df) * 100) if len(scored_df) else 0.0
            avg_prob = float(scored_df["Risk_Probability"].mean()) if len(scored_df) else 0.0

            b1, b2, b3 = st.columns(3)
            with b1:
                render_kpi_card("Orders Scored", f"{len(scored_df):,}", "Batch CSV rows processed", "neutral", COLORS["blue"])
            with b2:
                render_kpi_card("High-Risk Orders (>=65%)", f"{high_risk_cnt:,}", f"{high_risk_pct:.1f}% of batch", "negative" if high_risk_pct > 40 else "neutral", COLORS["red"])
            with b3:
                render_kpi_card("Avg Predicted Late Risk", f"{avg_prob:.1f}%", "Mean batch probability", "negative" if avg_prob >= 50 else "positive", COLORS["amber"])
            render_spacer("sm")
            st.dataframe(scored_df.head(50), use_container_width=True)

            render_spacer("sm")
            scored_csv = scored_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Scored Predictions CSV",
                data=scored_csv,
                file_name="naive_scored_late_delivery_predictions.csv",
                mime="text/csv",
                type="primary",
            )
