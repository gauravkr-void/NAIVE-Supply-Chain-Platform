import io
import streamlit as st
import pandas as pd
from utils.theme import (
    COLORS,
    render_portfolio_overview,
    render_kpi_card,
    render_callout_banner,
    render_section_heading,
    render_card_header,
    render_spacer,
    render_stepper,
)
from utils.data_engine import (
    BENCHMARK_METRICS,
    CANONICAL_SYNONYMS,
    load_benchmark_data,
    get_excel_sheet_names,
    read_uploaded_file,
    is_exact_standard_schema,
    fuzzy_suggest_mapping,
    run_universal_ingestion_pipeline,
    evaluate_capabilities,
    compute_dataset_kpis,
    compute_benchmark_deltas,
    render_global_sidebar,
)

render_global_sidebar()

df_active = st.session_state.get("df_active")
staged_clean = st.session_state.get("staged_clean_df")
staged_audit = st.session_state.get("staged_audit")
active_audit = st.session_state.get("ingestion_audit")

if df_active is not None:
    badge_text = (active_audit or {}).get("schema_status", "Active")
    badge_variant = "default" if badge_text == "Exact Auto-Matched" else "custom"
    current_step = 3
elif staged_clean is not None:
    badge_text, badge_variant = "Cleaned — Ready to Activate", "waiting"
    current_step = 2
else:
    badge_text, badge_variant = "Awaiting Upload", "waiting"
    current_step = 1

render_portfolio_overview(badge_text=badge_text, badge_variant=badge_variant)

render_section_heading(
    "Data Studio & Ingestion Engine",
    "Upload and sanitize raw CSV, Excel, or Parquet files, inspect the audit scorecard, and activate for analysis.",
)
render_stepper(current_step)
render_spacer("sm")

# 1. Upload & Quick Actions Row
col_upload, col_side = st.columns([2.1, 1])

with col_upload:
    with st.container(border=True, key="card_ds_upload"):
        render_card_header(
            "Step 1: Upload & Clean Dataset",
            "Supports CSV, Excel (.xlsx/.xls), and Parquet with automatic schema detection.",
            badge="6-Layer Pipeline",
        )
        uploaded = st.file_uploader(
            "Drag and drop a .csv, .xlsx, .xls, or .parquet file",
            type=["csv", "xlsx", "xls", "parquet"],
            key="data_studio_uploader",
        )

        if uploaded is not None:
            sheet_name = None
            if uploaded.name.lower().endswith((".xlsx", ".xls")):
                sheets = get_excel_sheet_names(uploaded)
                sheet_name = st.selectbox("Select Excel Sheet", options=sheets)

            file_sig = (uploaded.name, uploaded.size, sheet_name)
            if st.session_state.get("staged_raw_meta") != file_sig:
                try:
                    with st.spinner("Reading uploaded file..."):
                        df_raw, encoding_used = read_uploaded_file(uploaded, sheet_name=sheet_name)
                    st.session_state["staged_raw_df"] = df_raw
                    st.session_state["staged_raw_meta"] = file_sig
                    st.session_state["staged_encoding"] = encoding_used
                    st.session_state["staged_clean_df"] = None
                    st.session_state["staged_audit"] = None
                except Exception as exc:
                    st.error(f"Failed to parse uploaded file: {exc}")
                    st.stop()

            df_raw = st.session_state["staged_raw_df"]
            encoding_used = st.session_state.get("staged_encoding", "utf-8")
            st.success(
                f"Loaded **{uploaded.name}** ({len(df_raw):,} raw rows × {df_raw.shape[1]} columns, encoding: `{encoding_used}`)"
            )

            exact_match = is_exact_standard_schema(list(df_raw.columns))
            mapping_result: dict[str, str | None] = {}

            if exact_match:
                render_callout_banner(
                    "Tier 1: Zero-Config Exact Schema Recognized",
                    "All 58 standard columns were detected. Run the 6-layer cleaning & sanitization pipeline below.",
                    variant="success",
                )
            else:
                suggestions = fuzzy_suggest_mapping(list(df_raw.columns))
                matched_cnt = sum(1 for v in suggestions.values() if v is not None)
                canonical_keys = list(CANONICAL_SYNONYMS.keys())
                with st.expander(
                    f"Tier 2: Interactive Fuzzy Schema Mapper ({matched_cnt}/{len(canonical_keys)} auto-matched)",
                    expanded=True,
                ):
                    st.caption("Auto-detected column mappings are pre-selected. Override any dropdown or leave optional dimensions unmapped.")
                    col_options = ["— Not Mapped —"] + list(df_raw.columns)
                    grid_cols = st.columns(3)
                    for idx, canon in enumerate(canonical_keys):
                        suggested = suggestions.get(canon)
                        default_idx = col_options.index(suggested) if suggested in col_options else 0
                        with grid_cols[idx % 3]:
                            choice = st.selectbox(
                                f"Target: {canon}",
                                options=col_options,
                                index=default_idx,
                                key=f"map_{canon}",
                            )
                            mapping_result[canon] = None if choice == "— Not Mapped —" else choice

            render_spacer("sm")
            if st.button("Step 1: Clean & Enrich Dataset", type="primary", use_container_width=True):
                with st.spinner("Running 6-layer cleaning, PII pruning, imputation & feature engineering..."):
                    status_label = "Exact Auto-Matched" if exact_match else "Custom-Mapped"
                    df_clean, audit_rep = run_universal_ingestion_pipeline(
                        df_raw, mapping_result, schema_status=status_label
                    )
                    st.session_state["staged_clean_df"] = df_clean
                    st.session_state["staged_audit"] = audit_rep
                    st.session_state["staged_name"] = uploaded.name
                st.rerun()

with col_side:
    if st.button("Load 180k Benchmark Dataset", type="primary", use_container_width=True):
        with st.spinner("Loading 180,519-row historical benchmark..."):
            bench_df = load_benchmark_data()
        st.session_state["df_active"] = bench_df
        st.session_state["data_mode"] = "Benchmark (180k)"
        st.session_state["dataset_name"] = "supply_chain_data.parquet"
        st.session_state["capabilities"] = evaluate_capabilities(bench_df)
        st.session_state["ingestion_audit"] = {"schema_status": "Exact Auto-Matched"}
        st.rerun()

    bench_sample = load_benchmark_data().head(500).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Sample CSV Template",
        data=bench_sample,
        file_name="naive_sample_supply_chain.csv",
        mime="text/csv",
        use_container_width=True,
    )

    export_df = staged_clean if staged_clean is not None else df_active
    if export_df is None:
        st.markdown(
            """
            <div class="quick-info-list">
                <div class="quick-info-row"><span class="quick-info-key">Supported Formats</span><span class="quick-info-val">CSV, Excel, Parquet</span></div>
                <div class="quick-info-row"><span class="quick-info-key">Sample Template</span><span class="quick-info-val">500 pre-formatted rows</span></div>
                <div class="quick-info-row"><span class="quick-info-key">Auto Sanitization</span><span class="quick-info-val">PII pruning &amp; KPI fill</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if export_df is not None:
        clean_csv = export_df.head(100000).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Cleaned CSV",
            data=clean_csv,
            file_name="naive_cleaned_supply_chain.csv",
            mime="text/csv",
            use_container_width=True,
        )
        pq_buf = io.BytesIO()
        export_df.to_parquet(pq_buf, index=False, compression="snappy")
        st.download_button(
            label="Export Cleaned Parquet",
            data=pq_buf.getvalue(),
            file_name="naive_cleaned_supply_chain.parquet",
            mime="application/octet-stream",
            use_container_width=True,
        )

    if df_active is not None or staged_clean is not None:
        if st.button("Clear & Reset Session", use_container_width=True):
            for k in (
                "df_active", "data_mode", "ingestion_audit",
                "staged_raw_df", "staged_raw_meta", "staged_clean_df", "staged_audit",
            ):
                st.session_state[k] = None
            st.session_state["dataset_name"] = "No dataset loaded"
            st.session_state["capabilities"] = {}
            st.rerun()

# Step 2: Review Cleaned Audit & Activate Dataset
if staged_clean is not None and staged_audit is not None:
    render_section_heading(
        "Step 2: Review Cleaning Audit & Activate Dataset",
        "Inspect pipeline transformations before activating the dataset across all analytics modules.",
    )
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1:
        render_kpi_card(
            "Raw → Clean Rows",
            f"{staged_audit['clean_rows']:,}",
            f"From {staged_audit['raw_rows']:,} raw rows",
            "positive",
            COLORS["primary"],
        )
    with t2:
        render_kpi_card(
            "Duplicates Removed",
            f"{staged_audit['duplicates_removed']:,}",
            f"Invalid anchors dropped: {staged_audit['invalid_anchor_dropped']:,}",
            "neutral",
            COLORS["blue"],
        )
    with t3:
        render_kpi_card(
            "Missing Values Imputed",
            f"{staged_audit['missing_values_imputed']:,}",
            "Domain-aware fill",
            "positive",
            COLORS["violet"],
        )
    with t4:
        render_kpi_card(
            "Outliers Capped",
            f"{staged_audit['outliers_capped']:,}",
            "Clipped to [0, 60] days",
            "neutral",
            COLORS["amber"],
        )
    with t5:
        render_kpi_card(
            "PII / Sparse Dropped",
            f"{len(staged_audit['dropped_columns'])}",
            f"Engineered cols: {len(staged_audit['engineered_columns'])}",
            "neutral",
            COLORS["red"] if staged_audit["dropped_columns"] else COLORS["primary"],
        )

    render_spacer("sm")
    dropped_str = ", ".join(staged_audit["dropped_columns"]) if staged_audit["dropped_columns"] else "None"
    eng_str = ", ".join(staged_audit["engineered_columns"]) if staged_audit["engineered_columns"] else "All standard KPIs already present"
    render_callout_banner(
        f"Transformation Summary ({staged_audit['schema_status']})",
        f"Dropped PII/Sparse Columns: {dropped_str} | Auto-Engineered Columns: {eng_str}",
        variant="info",
    )

    is_already_active = (
        df_active is not None
        and st.session_state.get("dataset_name") == st.session_state.get("staged_name")
        and len(df_active) == len(staged_clean)
    )
    if not is_already_active:
        render_spacer("sm")
        if st.button("Step 2: Activate Cleaned Dataset for Analysis", type="primary", use_container_width=True):
            st.session_state["df_active"] = staged_clean
            st.session_state["data_mode"] = "Custom Upload"
            st.session_state["dataset_name"] = st.session_state.get("staged_name", "Uploaded Dataset")
            st.session_state["capabilities"] = evaluate_capabilities(staged_clean)
            st.session_state["ingestion_audit"] = staged_audit
            st.rerun()
    else:
        st.success("Dataset is **Active**! Use the sidebar navigation to explore Pages 1–6.")

elif df_active is None:
    render_spacer("sm")
    render_callout_banner(
        "Ready for Your Data",
        "Upload a file in Step 1 and click Clean & Enrich Dataset, then review the audit and activate it for analysis.",
        variant="info",
    )
    st.stop()

# Show Benchmark Comparison & Module Readiness once Active
if df_active is not None:
    render_section_heading(
        "Historical Benchmark Comparison",
        "How your active dataset compares against the 180k-row historical baseline.",
    )
    curr_kpis = compute_dataset_kpis(df_active)
    deltas = compute_benchmark_deltas(df_active)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        render_kpi_card(
            "Profit Margin %",
            f"{curr_kpis['profit_margin_pct']:.2f}%",
            f"{deltas['margin_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['profit_margin_pct']:.2f}% Baseline",
            "positive" if deltas["margin_delta_pp"] >= 0 else "negative",
            COLORS["primary"],
        )
    with b2:
        render_kpi_card(
            "Late Delivery Rate",
            f"{curr_kpis['late_rate_pct']:.2f}%",
            f"{deltas['late_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['late_rate_pct']:.2f}% Baseline",
            "positive" if deltas["late_delta_pp"] <= 0 else "negative",
            COLORS["red"] if curr_kpis["late_rate_pct"] > 50 else COLORS["primary"],
        )
    with b3:
        render_kpi_card(
            "On-Time Delivery %",
            f"{curr_kpis['otd_rate_pct']:.2f}%",
            f"{deltas['otd_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['otd_rate_pct']:.2f}% Baseline",
            "positive" if deltas["otd_delta_pp"] >= 0 else "negative",
            COLORS["blue"],
        )
    with b4:
        render_kpi_card(
            "Loss-Making Order Rate",
            f"{curr_kpis['loss_rate_pct']:.2f}%",
            f"{deltas['loss_delta_pp']:+.2f} pp vs. {BENCHMARK_METRICS['loss_rate_pct']:.2f}% Baseline",
            "positive" if deltas["loss_delta_pp"] <= 0 else "negative",
            COLORS["amber"],
        )

    caps = st.session_state.get("capabilities", evaluate_capabilities(df_active))
    render_section_heading(
        "Module Readiness & Cleaned Data Preview",
        "Unlocked analytics modules and a 25-row sample of the sanitized dataset.",
    )
    c_left, c_right = st.columns([1, 2])
    with c_left:
        with st.container(border=True, key="card_ds_readiness"):
            render_card_header("Module Readiness Status", "Schema capability check")
            cap_rows = [
                {"Module": k.upper(), "Status": "Unlocked" if v else "Locked (Missing Columns)"}
                for k, v in caps.items()
            ]
            st.dataframe(pd.DataFrame(cap_rows), use_container_width=True, hide_index=True, height=320)

    with c_right:
        with st.container(border=True, key="card_ds_preview"):
            render_card_header("Active Dataset Preview", "Top 25 sanitized rows", badge=f"{len(df_active):,} rows")
            st.dataframe(df_active.head(25), use_container_width=True, height=320)
