from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import streamlit as st

MODEL_FEATURES = [
    "Shipping Mode",
    "Market",
    "Order Region",
    "Category Name",
    "Order Item Quantity",
    "discount_tier",
    "scheduled_days",
]
CAT_FEATURES = ["Shipping Mode", "Market", "Order Region", "Category Name", "discount_tier"]
NUM_FEATURES = ["Order Item Quantity", "scheduled_days"]
TARGET_COL = "Late_delivery_risk"

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "late_delivery_model.joblib"


def _build_classifier_pipeline(use_lgbm: bool = True):
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.impute import SimpleImputer

    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", cat_pipe, CAT_FEATURES),
            ("num", num_pipe, NUM_FEATURES),
        ]
    )

    clf = None
    model_name = "RandomForestClassifier"
    if use_lgbm:
        try:
            from lightgbm import LGBMClassifier
            clf = LGBMClassifier(
                n_estimators=180,
                learning_rate=0.08,
                num_leaves=31,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            )
            model_name = "LightGBM Classifier"
        except ImportError:
            clf = None

    if clf is None:
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            random_state=42,
            n_jobs=-1,
        )
        model_name = "RandomForest Classifier"

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", clf),
    ])
    return pipeline, model_name


def train_and_evaluate_model(
    df: pd.DataFrame,
    save_path: Path | None = DEFAULT_MODEL_PATH,
    max_rows: int = 60000,
) -> dict[str, Any]:
    """Trains the Late Delivery Risk pipeline and computes validation metrics + feature importance."""
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score

    work_df = df[MODEL_FEATURES + [TARGET_COL]].dropna(subset=[TARGET_COL]).copy()
    if len(work_df) > max_rows:
        work_df = work_df.sample(n=max_rows, random_state=42)

    X = work_df[MODEL_FEATURES]
    y = work_df[TARGET_COL].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    pipeline, model_name = _build_classifier_pipeline(use_lgbm=True)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_val)
    y_prob = pipeline.predict_proba(X_val)[:, 1] if len(pipeline.classes_) > 1 else y_pred.astype(float)

    metrics = {
        "model_name": model_name,
        "train_rows": int(len(X_train)),
        "val_rows": int(len(X_val)),
        "accuracy": round(float(accuracy_score(y_val, y_pred)) * 100, 2),
        "roc_auc": round(float(roc_auc_score(y_val, y_prob)), 4) if y_val.nunique() > 1 else 0.0,
        "f1": round(float(f1_score(y_val, y_pred, zero_division=0)), 4),
        "precision": round(float(precision_score(y_val, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_val, y_pred, zero_division=0)), 4),
    }

    # Extract aggregated feature importances back to raw feature names
    pre = pipeline.named_steps["preprocessor"]
    clf = pipeline.named_steps["classifier"]
    feature_names = pre.get_feature_names_out()
    raw_importances = clf.feature_importances_

    grouped_imp: dict[str, float] = {f: 0.0 for f in MODEL_FEATURES}
    for fname, imp in zip(feature_names, raw_importances):
        clean_name = fname.replace("cat__", "").replace("num__", "")
        matched_base = next((f for f in MODEL_FEATURES if clean_name.startswith(f)), clean_name)
        grouped_imp[matched_base] = grouped_imp.get(matched_base, 0.0) + float(imp)

    imp_df = (
        pd.DataFrame({"Feature": list(grouped_imp.keys()), "Importance": list(grouped_imp.values())})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )
    total_imp = imp_df["Importance"].sum()
    if total_imp > 0:
        imp_df["Importance %"] = (imp_df["Importance"] / total_imp * 100).round(2)
    else:
        imp_df["Importance %"] = 0.0

    bundle = {
        "pipeline": pipeline,
        "metrics": metrics,
        "feature_importance": imp_df,
    }

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, save_path)

    return bundle


@st.cache_resource(show_spinner="Training / loading Late Delivery Risk ML pipeline...")
def get_benchmark_model(df: pd.DataFrame) -> dict[str, Any]:
    """Loads persisted joblib model if present, otherwise trains and caches it."""
    import joblib
    if DEFAULT_MODEL_PATH.exists():
        try:
            return joblib.load(DEFAULT_MODEL_PATH)
        except Exception:
            pass
    return train_and_evaluate_model(df, save_path=DEFAULT_MODEL_PATH)


def classify_risk_tier(prob_pct: float) -> tuple[str, str]:
    """Maps probability % to semantic risk tier and color key."""
    if prob_pct >= 65.0:
        return "High Risk", "red"
    if prob_pct >= 35.0:
        return "Medium Risk", "amber"
    return "Low Risk", "primary"


def predict_single_with_what_if(
    pipeline: Any,
    input_dict: dict[str, Any],
    shipping_modes: list[str],
) -> dict[str, Any]:
    """Predicts late delivery probability and simulates alternative Shipping Modes."""
    row_df = pd.DataFrame([input_dict])[MODEL_FEATURES]
    base_prob = float(pipeline.predict_proba(row_df)[0, 1]) * 100.0
    tier, color_key = classify_risk_tier(base_prob)

    what_if_rows = []
    for mode in shipping_modes:
        sim_input = dict(input_dict)
        sim_input["Shipping Mode"] = mode
        sim_df = pd.DataFrame([sim_input])[MODEL_FEATURES]
        sim_prob = float(pipeline.predict_proba(sim_df)[0, 1]) * 100.0
        what_if_rows.append({
            "Shipping Mode": mode,
            "Predicted Late Risk (%)": round(sim_prob, 2),
            "Risk Delta (pp)": round(sim_prob - base_prob, 2),
        })

    what_if_df = pd.DataFrame(what_if_rows).sort_values("Predicted Late Risk (%)").reset_index(drop=True)
    best_row = what_if_df.iloc[0]

    return {
        "base_prob": round(base_prob, 2),
        "tier": tier,
        "color_key": color_key,
        "what_if_df": what_if_df,
        "best_mode": best_row["Shipping Mode"],
        "best_prob": float(best_row["Predicted Late Risk (%)"]),
        "risk_reduction_pp": round(base_prob - float(best_row["Predicted Late Risk (%)"]), 2),
    }


def batch_predict_df(pipeline: Any, batch_df: pd.DataFrame) -> pd.DataFrame:
    """Scores an unlabelled batch DataFrame and appends Predicted_Late_Risk & Risk_Probability."""
    scored = batch_df.copy()
    for col in MODEL_FEATURES:
        if col not in scored.columns:
            scored[col] = np.nan
    X_batch = scored[MODEL_FEATURES]
    probs = pipeline.predict_proba(X_batch)[:, 1]
    preds = (probs >= 0.5).astype(int)
    scored["Predicted_Late_Risk"] = preds
    scored["Risk_Probability"] = (probs * 100.0).round(2)
    return scored
