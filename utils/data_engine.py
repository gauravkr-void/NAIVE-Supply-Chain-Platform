from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
PARQUET_PATH = BASE_DIR / "data" / "supply_chain_data.parquet"

# Verified 180,519-row Historical Benchmark Baseline
BENCHMARK_METRICS = {
    "row_count": 180519,
    "unique_orders": 65752,
    "total_sales": 36784735.01,
    "total_profit": 3966902.97,
    "profit_margin_pct": 10.78,
    "late_rate_pct": 54.83,
    "otd_rate_pct": 45.17,
    "loss_rate_pct": 18.71,
}

STANDARD_COLUMNS = [
    "Type", "Days for shipping (real)", "Days for shipment (scheduled)",
    "Benefit per order", "Sales per customer", "Delivery Status",
    "Late_delivery_risk", "Category Id", "Category Name", "Customer City",
    "Customer Country", "Customer Fname", "Customer Id", "Customer Lname",
    "Customer Segment", "Customer State", "Customer Street", "Customer Zipcode",
    "Department Id", "Department Name", "Latitude", "Longitude", "Market",
    "Order City", "Order Country", "Order Customer Id", "order date (DateOrders)",
    "Order Id", "Order Item Cardprod Id", "Order Item Discount",
    "Order Item Discount Rate", "Order Item Id", "Order Item Product Price",
    "Order Item Profit Ratio", "Order Item Quantity", "Sales", "Order Item Total",
    "Order Profit Per Order", "Order Region", "Order State", "Order Status",
    "Product Card Id", "Product Category Id", "Product Name", "Product Price",
    "Product Status", "shipping date (DateOrders)", "Shipping Mode", "order_date",
    "shipping_date", "scheduled_days", "actual_days", "delivery_variance_days",
    "is_late", "implied_cost", "is_loss_making", "price_tier", "discount_tier",
]

CANONICAL_SYNONYMS: dict[str, list[str]] = {
    "Sales": ["sales", "revenue", "total_amount", "order_total", "gross_sales", "order item total", "total_sales", "amount"],
    "Benefit per order": ["benefit per order", "profit", "net_profit", "order profit per order", "margin", "benefit", "order_profit"],
    "order_date": ["order_date", "order date (dateorders)", "orderdate", "transaction_date", "order date", "date", "created_at", "order_dt"],
    "shipping_date": ["shipping_date", "shipping date (dateorders)", "shipdate", "shipping date", "ship_date", "shipped_at"],
    "Order Id": ["order id", "order_id", "transaction_id", "invoice_id", "id"],
    "Shipping Mode": ["shipping mode", "ship_mode", "shipping_method", "carrier_tier", "service_level"],
    "scheduled_days": ["scheduled_days", "days for shipment (scheduled)", "sla_days", "planned_days"],
    "actual_days": ["actual_days", "days for shipping (real)", "transit_days", "real_days"],
    "is_late": ["is_late", "late_delivery_risk", "late", "is_delayed", "delayed"],
    "Market": ["market", "region_group", "territory", "geo_market"],
    "Order Region": ["order region", "region", "sub_region", "order_region"],
    "Order Country": ["order country", "country", "destination_country"],
    "Customer Id": ["customer id", "customer_id", "client_id", "buyer_id"],
    "Customer Segment": ["customer segment", "segment", "customer_type", "tier"],
    "Product Name": ["product name", "product", "sku", "sku_name", "item_name"],
    "Category Name": ["category name", "category", "product_category"],
    "Product Price": ["product price", "order item product price", "unit_price", "price"],
    "Order Item Quantity": ["order item quantity", "quantity", "qty", "units"],
    "Order Item Discount Rate": ["order item discount rate", "discount_rate", "discount_pct", "discount"],
    "Order Item Profit Ratio": ["order item profit ratio", "profit_ratio", "margin_ratio"],
    "Type": ["type", "payment_type", "payment_method"],
    "Order Status": ["order status", "status", "order_state"],
    "Delivery Status": ["delivery status", "shipment_status"],
    "Latitude": ["latitude", "lat"],
    "Longitude": ["longitude", "lon", "lng", "long"],
}

PII_PATTERNS = ("email", "password", "passwd", "ssn", "phone", "mobile", "credit_card", "card_number")
IMAGE_URL_PATTERNS = ("product image", "image_url", "img_url", "thumbnail")


@st.cache_data(show_spinner=False)
def load_benchmark_data() -> pd.DataFrame:
    """Loads the 180,519-row supply chain dataset from compressed Parquet when requested."""
    df = pd.read_parquet(PARQUET_PATH)
    for col in ("order_date", "shipping_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def get_excel_sheet_names(uploaded_file: Any) -> list[str]:
    """Returns sheet names for an uploaded Excel workbook."""
    uploaded_file.seek(0)
    xl = pd.ExcelFile(uploaded_file, engine="openpyxl")
    return xl.sheet_names


def _sanitize_headers_and_index(df: pd.DataFrame) -> pd.DataFrame:
    """Layer 1: Strips whitespace from headers and removes empty unnamed index columns."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    drop_unnamed = [
        c for c in df.columns
        if c.lower().startswith("unnamed:") or c == ""
    ]
    if drop_unnamed:
        df = df.drop(columns=drop_unnamed)
    return df


def read_uploaded_file(uploaded_file: Any, sheet_name: str | None = None) -> tuple[pd.DataFrame, str]:
    """Layer 1: Resilient multi-format reader with UTF-8 -> Latin-1 -> Windows-1252 fallback."""
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)

    if name.endswith(".csv"):
        raw_bytes = uploaded_file.read()
        encoding_used = "utf-8"
        df = None
        for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                decoded = raw_bytes.decode(enc)
                df = pd.read_csv(io.StringIO(decoded), low_memory=False, on_bad_lines="skip")
                if df.shape[1] == 1:
                    df_sniff = pd.read_csv(io.StringIO(decoded), sep=None, engine="python", on_bad_lines="skip")
                    if df_sniff.shape[1] > 1:
                        df = df_sniff
                encoding_used = enc
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if df is None:
            df = pd.read_csv(io.BytesIO(raw_bytes), encoding="latin-1", low_memory=False, on_bad_lines="skip")
            encoding_used = "latin-1"
        return _sanitize_headers_and_index(df), encoding_used

    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name or 0, engine="openpyxl")
        return _sanitize_headers_and_index(df), "excel"

    if name.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
        return _sanitize_headers_and_index(df), "parquet"

    raise ValueError(f"Unsupported file format: {uploaded_file.name}")


def is_exact_standard_schema(columns: list[str]) -> bool:
    """Checks if uploaded dataset matches the 58-column benchmark schema."""
    return set(STANDARD_COLUMNS).issubset(set(columns))


def fuzzy_suggest_mapping(columns: list[str]) -> dict[str, str | None]:
    """Layer 2 (Tier 1): Auto-detects best matching source column for each canonical field."""
    norm_lookup = {c.strip().lower(): c for c in columns}
    suggestions: dict[str, str | None] = {}
    for canonical, synonyms in CANONICAL_SYNONYMS.items():
        matched = None
        if canonical in columns:
            matched = canonical
        else:
            for syn in synonyms:
                if syn in norm_lookup:
                    matched = norm_lookup[syn]
                    break
            if matched is None:
                for col_lower, orig_col in norm_lookup.items():
                    if any(syn == col_lower or f" {syn}" in col_lower or f"{syn}_" in col_lower for syn in synonyms):
                        matched = orig_col
                        break
        suggestions[canonical] = matched
    return suggestions


def _clean_numeric_series(series: pd.Series) -> tuple[pd.Series, bool]:
    """Layer 4: Strips currency symbols ($, €, ₹, £), commas, and % signs before numeric coercion."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce"), False
    s_str = series.astype(str).str.strip()
    had_pct = s_str.str.contains("%", na=False).any()
    cleaned = s_str.str.replace(r"[$€₹£,\s%]", "", regex=True)
    cleaned = cleaned.replace({"": np.nan, "nan": np.nan, "None": np.nan, "null": np.nan, "N/A": np.nan})
    return pd.to_numeric(cleaned, errors="coerce"), bool(had_pct)


def run_universal_ingestion_pipeline(
    df_raw: pd.DataFrame,
    mapping: dict[str, str | None],
    schema_status: str = "Custom-Mapped",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Executes Layers 2–6:
    - Column mapping
    - Structural hygiene & PII / >80% sparse column pruning + deduplication
    - Data type sanitization (currency/%, mixed dates, outlier capping)
    - Critical anchor validation & domain-aware imputation
    - On-the-fly feature engineering
    Returns (cleaned_df, transformation_audit).
    """
    raw_rows, raw_cols = df_raw.shape
    df = df_raw.copy()

    # Layer 2: Apply mapping
    rename_map = {
        src_col: canonical
        for canonical, src_col in mapping.items()
        if src_col and src_col in df.columns and src_col != canonical
    }
    df = df.rename(columns=rename_map)

    # Layer 3: PII, image URL, and >80% sparse column pruning
    dropped_cols: list[str] = []
    for col in list(df.columns):
        col_l = col.lower()
        is_pii = any(p in col_l for p in PII_PATTERNS)
        is_img = any(p in col_l for p in IMAGE_URL_PATTERNS)
        null_frac = float(df[col].isna().mean()) if len(df) else 0.0
        if is_pii or is_img or null_frac > 0.80:
            dropped_cols.append(col)
    if dropped_cols:
        df = df.drop(columns=dropped_cols)

    # Exact deduplication
    before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = before_dedup - len(df)

    # Layer 4: Universal Date Parsing
    if "order_date" not in df.columns and "order date (DateOrders)" in df.columns:
        df["order_date"] = df["order date (DateOrders)"]
    if "shipping_date" not in df.columns and "shipping date (DateOrders)" in df.columns:
        df["shipping_date"] = df["shipping date (DateOrders)"]

    for d_col in ("order_date", "shipping_date"):
        if d_col in df.columns:
            df[d_col] = pd.to_datetime(df[d_col], errors="coerce", format="mixed")

    # Currency & Percentage Stripping
    numeric_targets = [
        "Sales", "Benefit per order", "Order Item Total", "Order Profit Per Order",
        "scheduled_days", "actual_days", "Days for shipment (scheduled)", "Days for shipping (real)",
        "Order Item Quantity", "Order Item Discount Rate", "Order Item Discount",
        "Order Item Profit Ratio", "Product Price", "Order Item Product Price",
        "Latitude", "Longitude",
    ]
    for num_col in numeric_targets:
        if num_col in df.columns:
            coerced, had_pct = _clean_numeric_series(df[num_col])
            if had_pct and num_col in ("Order Item Discount Rate", "Order Item Profit Ratio"):
                coerced = coerced / 100.0
            df[num_col] = coerced

    # Layer 5: Critical Key Validation (drop rows if core anchor order_date or Sales is null)
    before_anchor = len(df)
    anchor_cols = [c for c in ("order_date", "Sales") if c in df.columns]
    if anchor_cols:
        df = df.dropna(subset=anchor_cols).reset_index(drop=True)
    invalid_anchor_dropped = before_anchor - len(df)

    # Layer 4b: Outlier & Anomaly Capping on transit/scheduled days
    outliers_capped = 0
    for day_col in ("scheduled_days", "actual_days", "Days for shipment (scheduled)", "Days for shipping (real)"):
        if day_col in df.columns:
            neg_mask = df[day_col] < 0
            ext_mask = df[day_col] > 60
            outliers_capped += int((neg_mask | ext_mask).sum())
            df[day_col] = df[day_col].clip(lower=0, upper=60)

    # Layer 5b: Domain-Aware Missing Value Imputation
    missing_values_imputed = 0
    cat_fill_cols = [
        "Customer Lname", "Customer Fname", "Order Region", "Category Name",
        "Shipping Mode", "Market", "Order Country", "Customer Segment",
        "Product Name", "Type", "Order Status", "Delivery Status",
    ]
    for c_col in cat_fill_cols:
        if c_col in df.columns:
            null_cnt = int(df[c_col].isna().sum())
            if null_cnt > 0:
                df[c_col] = df[c_col].fillna("Unknown").astype(str)
                missing_values_imputed += null_cnt

    num_zero_cols = ["Order Item Discount", "Order Item Discount Rate", "Customer Zipcode"]
    for z_col in num_zero_cols:
        if z_col in df.columns:
            null_cnt = int(df[z_col].isna().sum())
            if null_cnt > 0:
                df[z_col] = df[z_col].fillna(0)
                missing_values_imputed += null_cnt

    num_median_cols = ["Order Item Quantity", "Product Price", "Order Item Product Price", "Latitude", "Longitude"]
    for m_col in num_median_cols:
        if m_col in df.columns:
            null_cnt = int(df[m_col].isna().sum())
            if null_cnt > 0:
                med = df[m_col].median()
                df[m_col] = df[m_col].fillna(0 if pd.isna(med) else med)
                missing_values_imputed += null_cnt

    # Layer 6: On-the-Fly Feature Engineering (Auto-Enrichment Engine)
    engineered_cols: list[str] = []

    if "scheduled_days" not in df.columns:
        if "Days for shipment (scheduled)" in df.columns:
            df["scheduled_days"] = df["Days for shipment (scheduled)"]
        else:
            df["scheduled_days"] = 4.0
        engineered_cols.append("scheduled_days")
    elif df["scheduled_days"].isna().any():
        med_s = df["scheduled_days"].median()
        missing_values_imputed += int(df["scheduled_days"].isna().sum())
        df["scheduled_days"] = df["scheduled_days"].fillna(4.0 if pd.isna(med_s) else med_s)

    if "actual_days" not in df.columns:
        if "Days for shipping (real)" in df.columns:
            df["actual_days"] = df["Days for shipping (real)"]
        elif "shipping_date" in df.columns and "order_date" in df.columns:
            df["actual_days"] = (df["shipping_date"] - df["order_date"]).dt.days.clip(lower=0, upper=60)
        else:
            df["actual_days"] = df["scheduled_days"]
        engineered_cols.append("actual_days")
    elif df["actual_days"].isna().any():
        med_a = df["actual_days"].median()
        missing_values_imputed += int(df["actual_days"].isna().sum())
        df["actual_days"] = df["actual_days"].fillna(df["scheduled_days"] if pd.isna(med_a) else med_a)

    if "delivery_variance_days" not in df.columns:
        df["delivery_variance_days"] = df["actual_days"] - df["scheduled_days"]
        engineered_cols.append("delivery_variance_days")

    if "is_late" not in df.columns:
        if "Late_delivery_risk" in df.columns:
            df["is_late"] = pd.to_numeric(df["Late_delivery_risk"], errors="coerce").fillna(0).astype(int)
        else:
            df["is_late"] = (df["delivery_variance_days"] > 0).astype(int)
        engineered_cols.append("is_late")
    else:
        df["is_late"] = pd.to_numeric(df["is_late"], errors="coerce").fillna(0).astype(int)

    if "Late_delivery_risk" not in df.columns:
        df["Late_delivery_risk"] = df["is_late"]
        engineered_cols.append("Late_delivery_risk")
    else:
        df["Late_delivery_risk"] = pd.to_numeric(df["Late_delivery_risk"], errors="coerce").fillna(df["is_late"]).astype(int)

    if "Benefit per order" in df.columns:
        if "is_loss_making" not in df.columns:
            df["is_loss_making"] = (df["Benefit per order"] < 0).astype(int)
            engineered_cols.append("is_loss_making")
        else:
            df["is_loss_making"] = pd.to_numeric(df["is_loss_making"], errors="coerce").fillna(0).astype(int)

        if "implied_cost" not in df.columns:
            base_rev = df["Order Item Total"] if "Order Item Total" in df.columns else df.get("Sales", 0)
            df["implied_cost"] = base_rev - df["Benefit per order"]
            engineered_cols.append("implied_cost")

        if "Order Item Profit Ratio" not in df.columns and "Sales" in df.columns:
            df["Order Item Profit Ratio"] = np.where(df["Sales"] != 0, df["Benefit per order"] / df["Sales"], 0.0)
            engineered_cols.append("Order Item Profit Ratio")

    if "price_tier" not in df.columns:
        unit_price = None
        if "Product Price" in df.columns:
            unit_price = df["Product Price"]
        elif "Order Item Product Price" in df.columns:
            unit_price = df["Order Item Product Price"]
        elif "Sales" in df.columns:
            qty = df["Order Item Quantity"].replace(0, 1) if "Order Item Quantity" in df.columns else 1
            unit_price = df["Sales"] / qty
        if unit_price is not None:
            p_bins = [-0.01, 50.0, 100.0, 200.0, 500.0, 1e9]
            p_labels = ["Under $50", "$50-$100", "$100-$200", "$200-$500", "Over $500"]
            df["price_tier"] = pd.cut(unit_price.fillna(0), bins=p_bins, labels=p_labels).astype(str)
            engineered_cols.append("price_tier")

    if "discount_tier" not in df.columns and "Order Item Discount Rate" in df.columns:
        rate_vals = df["Order Item Discount Rate"].fillna(0)
        rate_pct = np.where(rate_vals <= 1.0, rate_vals * 100.0, rate_vals)
        d_bins = [-0.01, 0.001, 5.0, 10.0, 15.0, 20.0, 1000.0]
        d_labels = ["0%", "1-5%", "6-10%", "11-15%", "16-20%", ">20%"]
        df["discount_tier"] = pd.Series(pd.cut(rate_pct, bins=d_bins, labels=d_labels), index=df.index).astype(str).replace("nan", "0%")
        engineered_cols.append("discount_tier")

    if "Order Id" not in df.columns:
        df["Order Id"] = np.arange(1, len(df) + 1)
        engineered_cols.append("Order Id")

    if schema_status == "Exact Auto-Matched" and engineered_cols:
        schema_status = "Auto-Enriched"

    audit_report = {
        "schema_status": schema_status,
        "raw_rows": int(raw_rows),
        "raw_cols": int(raw_cols),
        "clean_rows": int(len(df)),
        "clean_cols": int(df.shape[1]),
        "duplicates_removed": int(duplicates_removed),
        "invalid_anchor_dropped": int(invalid_anchor_dropped),
        "outliers_capped": int(outliers_capped),
        "missing_values_imputed": int(missing_values_imputed),
        "dropped_columns": dropped_cols,
        "engineered_columns": engineered_cols,
    }
    return df, audit_report


def evaluate_capabilities(df: pd.DataFrame) -> dict[str, bool]:
    """Determines which analytical modules can run based on present columns."""
    cols = set(df.columns)
    return {
        "executive": {"Sales", "Benefit per order", "order_date"}.issubset(cols),
        "logistics": {"Shipping Mode", "scheduled_days", "actual_days", "is_late"}.issubset(cols),
        "margin": {"Sales", "Benefit per order"}.issubset(cols),
        "discount": {"Order Item Discount Rate", "Order Item Profit Ratio"}.issubset(cols),
        "geo": {"Order Country", "Latitude", "Longitude"}.issubset(cols),
        "rfm": {"Customer Id", "order_date", "Sales"}.issubset(cols),
        "abc": {"Product Name", "Sales"}.issubset(cols),
        "ml": {
            "Shipping Mode", "Market", "Order Region", "Category Name",
            "Order Item Quantity", "discount_tier", "scheduled_days", "Late_delivery_risk",
        }.issubset(cols),
    }


def compute_data_health_audit(df: pd.DataFrame) -> dict[str, Any]:
    """Computes live data quality scorecard."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    missing_pct = round((missing_cells / total_cells) * 100, 2) if total_cells else 0.0
    dup_rows = int(df.duplicated().sum())
    dup_orders = int(df["Order Id"].duplicated().sum()) if "Order Id" in df.columns else 0

    date_min, date_max = None, None
    if "order_date" in df.columns and df["order_date"].notna().any():
        date_min = df["order_date"].min()
        date_max = df["order_date"].max()

    null_by_col = df.isna().sum()
    null_by_col = null_by_col[null_by_col > 0].sort_values(ascending=False)

    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": dup_rows,
        "duplicate_order_ids": dup_orders,
        "date_min": date_min,
        "date_max": date_max,
        "null_columns": null_by_col,
    }


def compute_dataset_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Computes core KPIs for any standardized DataFrame."""
    total_sales = float(df["Sales"].sum()) if "Sales" in df.columns else 0.0
    total_profit = float(df["Benefit per order"].sum()) if "Benefit per order" in df.columns else 0.0
    margin_pct = (total_profit / total_sales * 100.0) if total_sales else 0.0
    late_rate = float(df["is_late"].mean() * 100.0) if "is_late" in df.columns and len(df) else 0.0
    otd_rate = 100.0 - late_rate
    loss_rate = float(df["is_loss_making"].mean() * 100.0) if "is_loss_making" in df.columns and len(df) else 0.0
    unique_orders = int(df["Order Id"].nunique()) if "Order Id" in df.columns else len(df)

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "profit_margin_pct": margin_pct,
        "late_rate_pct": late_rate,
        "otd_rate_pct": otd_rate,
        "loss_rate_pct": loss_rate,
        "unique_orders": unique_orders,
    }


def compute_benchmark_deltas(df: pd.DataFrame) -> dict[str, float]:
    """Calculates percentage/point deltas vs. the 180k-row historical baseline."""
    curr = compute_dataset_kpis(df)
    return {
        "margin_delta_pp": curr["profit_margin_pct"] - BENCHMARK_METRICS["profit_margin_pct"],
        "late_delta_pp": curr["late_rate_pct"] - BENCHMARK_METRICS["late_rate_pct"],
        "otd_delta_pp": curr["otd_rate_pct"] - BENCHMARK_METRICS["otd_rate_pct"],
        "loss_delta_pp": curr["loss_rate_pct"] - BENCHMARK_METRICS["loss_rate_pct"],
    }


def init_session_state() -> None:
    """Initializes session state with no pre-loaded data so the user uploads manually."""
    defaults = {
        "df_active": None,
        "data_mode": None,
        "dataset_name": "No dataset loaded",
        "capabilities": {},
        "ingestion_audit": None,
        "staged_raw_df": None,
        "staged_raw_meta": None,
        "staged_clean_df": None,
        "staged_audit": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_global_sidebar() -> pd.DataFrame | None:
    """Renders NAIVE sidebar and persistent global slicers when data is loaded."""
    init_session_state()
    df = st.session_state["df_active"]
    mode = st.session_state.get("data_mode")

    with st.sidebar:
        st.markdown("## NAIVE")
        st.caption("Supply Chain Intelligence & Predictive Analytics")

        if df is None:
            st.warning("No dataset loaded yet. Upload a file in **0 — Data Studio** to unlock analytics.")
            return None

        st.caption(f"Active Source: **{st.session_state.get('dataset_name', 'Uploaded Data')}**")
        if mode == "Benchmark (180k)":
            st.success(f"Benchmark Mode ({len(df):,} rows)")
        else:
            st.info(f"Custom Upload ({len(df):,} rows)")

        st.divider()
        st.markdown("#### Global Slicers")

        mask = pd.Series(True, index=df.index)

        if "order_date" in df.columns and df["order_date"].notna().any():
            min_dt = df["order_date"].min().date()
            max_dt = df["order_date"].max().date()
            date_range = st.date_input(
                "Order Date Range",
                value=(min_dt, max_dt),
                min_value=min_dt,
                max_value=max_dt,
                key="global_date_range",
            )
            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_dt = pd.to_datetime(date_range[0])
                end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                mask &= (df["order_date"] >= start_dt) & (df["order_date"] <= end_dt)

        slicer_specs = [
            ("Market", "Market", "global_market"),
            ("Order Region", "Order Region", "global_region"),
            ("Shipping Mode", "Shipping Mode", "global_ship_mode"),
            ("Customer Segment", "Customer Segment", "global_segment"),
        ]
        for col, label, key in slicer_specs:
            if col in df.columns:
                options = sorted(df[col].dropna().astype(str).unique().tolist())
                selected = st.multiselect(label, options=options, default=[], placeholder=f"All {label}s", key=key)
                if selected:
                    mask &= df[col].astype(str).isin(selected)

        df_filtered = df.loc[mask].copy()

        st.divider()
        st.caption(f"Filtered Records: **{len(df_filtered):,}** / {len(df):,}")

        csv_bytes = df_filtered.head(50000).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Filtered CSV",
            data=csv_bytes,
            file_name="naive_filtered_supply_chain.csv",
            mime="text/csv",
            use_container_width=True,
            help="Downloads up to 50,000 filtered rows as CSV.",
        )

    return df_filtered
