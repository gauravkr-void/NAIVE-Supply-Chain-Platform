import html
import streamlit as st
import plotly.graph_objects as go

# Refined Executive SaaS Color Tokens
COLORS = {
    "canvas": "#F4F6FA",
    "card": "#FFFFFF",
    "card_subtle": "#F8FAFC",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "grid": "#F1F5F9",
    "primary": "#00B86B",
    "primary_hover": "#009E5B",
    "primary_soft": "#ECFDF5",
    "blue": "#2563EB",
    "blue_soft": "#EFF6FF",
    "amber": "#D97706",
    "amber_soft": "#FFFBEB",
    "red": "#DC2626",
    "red_soft": "#FEF2F2",
    "violet": "#7C3AED",
    "violet_soft": "#F5F3FF",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#64748B",
}

DISCRETE_COLORS = [
    COLORS["primary"],
    COLORS["blue"],
    COLORS["amber"],
    COLORS["red"],
    COLORS["violet"],
]


def inject_custom_css() -> None:
    """Injects refined, executive light-mode SaaS CSS with clear macro/micro spacing."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Pacifico&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: {COLORS["text_primary"]};
            -webkit-font-smoothing: antialiased;
        }}

        h1, h2, h3, .page-title, .section-heading {{
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Main App Canvas */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {COLORS["canvas"]} !important;
        }}

        .block-container {{
            padding: 1.75rem 2.25rem 3rem 2.25rem !important;
            max-width: 1460px !important;
        }}

        /* Balanced Micro & Macro Vertical Rhythm & Equal-Height Columns */
        [data-testid="stVerticalBlock"] {{
            gap: 0.9rem !important;
        }}

        [data-testid="stHorizontalBlock"] {{
            gap: 1.25rem !important;
            align-items: stretch !important;
        }}

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            display: flex !important;
            flex-direction: column !important;
        }}

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div,
        [data-testid="stHorizontalBlock"] > [data-testid="column"] > div,
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"] > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [data-testid="stLayoutWrapper"]:has(div[class*="st-key-card_"]),
        [data-testid="stElementContainer"]:has(div[class*="st-key-card_"]) {{
            flex: 1 1 auto !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }}

        /* Quick Info List inside Data Studio Side Card */
        .quick-info-list {{
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            margin-top: 0.35rem;
            padding-top: 0.75rem;
            border-top: 1px solid {COLORS["grid"]};
        }}

        .quick-info-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.78rem;
            color: {COLORS["text_secondary"]};
        }}

        .quick-info-key {{
            font-weight: 600;
            color: {COLORS["text_muted"]};
        }}

        .quick-info-val {{
            font-weight: 600;
            color: {COLORS["text_primary"]};
        }}

        /* Transparent Glass Header Bar */
        [data-testid="stHeader"] {{
            background-color: rgba(244, 246, 250, 0.82) !important;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.6);
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {COLORS["card"]} !important;
            border-right: 1px solid {COLORS["border"]};
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {{
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, {COLORS["text_primary"]} 0%, {COLORS["primary"]} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.1rem !important;
        }}

        [data-testid="stSidebarNav"] a {{
            border-radius: 8px !important;
            margin: 0.12rem 0.5rem !important;
            padding: 0.45rem 0.75rem !important;
            transition: background-color 0.15s ease, color 0.15s ease;
        }}

        [data-testid="stSidebarNav"] a:hover {{
            background-color: {COLORS["card_subtle"]} !important;
        }}

        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: {COLORS["primary_soft"]} !important;
            color: #065F46 !important;
            font-weight: 600 !important;
            border-left: 3px solid {COLORS["primary"]};
        }}

        /* Portfolio Hero & Brand Logo */
        .portfolio-hero {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F7FBF9 55%, #F1F7FE 100%);
            border: 1px solid {COLORS["border"]};
            border-top: 4px solid {COLORS["primary"]};
            border-radius: 16px;
            padding: 1.6rem 1.85rem 1.45rem 1.85rem;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.045);
            margin-bottom: 0.35rem;
        }}

        .portfolio-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 1rem;
            padding-bottom: 1.05rem;
            border-bottom: 1px solid {COLORS["border"]};
        }}

        .brand-lockup {{
            display: flex;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 0.85rem;
        }}

        .brand-logo {{
            font-family: 'Pacifico', cursive !important;
            font-size: 2.55rem;
            font-weight: 400;
            line-height: 1.05;
            letter-spacing: 0.01em;
            background: linear-gradient(135deg, {COLORS["text_primary"]} 0%, #059669 55%, {COLORS["blue"]} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-right: 0.15rem;
            filter: drop-shadow(0 2px 6px rgba(0, 184, 107, 0.12));
        }}

        .brand-divider {{
            color: {COLORS["border_strong"]};
            font-size: 1.35rem;
            font-weight: 300;
        }}

        .brand-tagline {{
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.02rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            letter-spacing: -0.01em;
        }}

        .portfolio-desc {{
            color: {COLORS["text_secondary"]};
            font-size: 0.9rem;
            line-height: 1.55;
            margin: 0.65rem 0 0 0;
            max-width: 920px;
        }}

        .portfolio-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 0.75rem;
            margin-top: 1.05rem;
        }}

        .portfolio-item {{
            background-color: rgba(255, 255, 255, 0.88);
            border: 1px solid {COLORS["border"]};
            border-radius: 11px;
            padding: 0.75rem 0.9rem;
            transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
        }}

        .portfolio-item:hover {{
            border-color: {COLORS["primary"]};
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
        }}

        .portfolio-item-head {{
            display: flex;
            align-items: center;
            gap: 0.45rem;
            margin-bottom: 0.3rem;
        }}

        .portfolio-num {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 700;
            background-color: {COLORS["primary_soft"]};
            color: #065F46;
            flex-shrink: 0;
        }}

        .portfolio-item-title {{
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 0.84rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
        }}

        .portfolio-item-text {{
            font-size: 0.78rem;
            color: {COLORS["text_secondary"]};
            line-height: 1.42;
            margin: 0;
        }}

        .tech-stack-row {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 1rem;
            padding-top: 0.85rem;
            border-top: 1px solid {COLORS["grid"]};
        }}

        .tech-stack-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {COLORS["text_muted"]};
            margin-right: 0.35rem;
        }}

        .tech-pill {{
            font-size: 0.72rem;
            font-weight: 600;
            color: {COLORS["text_secondary"]};
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 9999px;
            padding: 0.18rem 0.6rem;
        }}

        /* Elevated White Cards for Bordered Containers (All Streamlit Versions) */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[class*="st-key-card_"] {{
            background-color: {COLORS["card"]} !important;
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 14px !important;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 4px 14px rgba(15, 23, 42, 0.03) !important;
            padding: 1.35rem 1.5rem !important;
            flex: 1 1 auto !important;
            height: 100% !important;
            box-sizing: border-box !important;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        div[class*="st-key-card_"]:hover {{
            border-color: {COLORS["border_strong"]} !important;
            box-shadow: 0 4px 18px rgba(15, 23, 42, 0.06) !important;
        }}

        /* Native Metrics */
        [data-testid="stMetric"] {{
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}

        [data-testid="stMetricLabel"] {{
            color: {COLORS["text_muted"]} !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        [data-testid="stMetricValue"] {{
            color: {COLORS["text_primary"]} !important;
            font-weight: 700 !important;
            font-variant-numeric: tabular-nums;
        }}

        /* Section Heading with Accent Bar & Generous Top Breathing Room */
        .section-heading-wrap {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1.15rem 0 0.2rem 0;
            padding-left: 0.75rem;
            border-left: 4px solid {COLORS["primary"]};
        }}

        .section-heading {{
            color: {COLORS["text_primary"]};
            font-size: 1.08rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin: 0;
            line-height: 1.3;
        }}

        .section-subheading {{
            color: {COLORS["text_muted"]};
            font-size: 0.82rem;
            margin: 0.15rem 0 0 0;
            font-weight: 400;
        }}

        /* Card Header Inside Containers */
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding-bottom: 0.75rem;
            margin-bottom: 0.35rem;
            border-bottom: 1px solid {COLORS["grid"]};
        }}

        .card-title {{
            color: {COLORS["text_primary"]};
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 0.98rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.3;
        }}

        .card-subtitle {{
            color: {COLORS["text_muted"]};
            font-size: 0.8rem;
            margin: 0.15rem 0 0 0;
        }}

        .card-badge {{
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            background-color: {COLORS["card_subtle"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            white-space: nowrap;
        }}

        /* Custom SaaS Card & KPI Classes */
        .saas-card {{
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 14px;
            padding: 1.35rem 1.5rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 4px 14px rgba(15, 23, 42, 0.03);
        }}

        .kpi-card {{
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-top: 3px solid {COLORS["primary"]};
            border-radius: 14px;
            padding: 1.15rem 1.3rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 4px 12px rgba(15, 23, 42, 0.025);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
        }}

        .kpi-label {{
            color: {COLORS["text_muted"]};
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.45rem;
        }}

        .kpi-value {{
            color: {COLORS["text_primary"]};
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.72rem;
            font-weight: 800;
            font-variant-numeric: tabular-nums;
            line-height: 1.15;
            letter-spacing: -0.02em;
            margin-bottom: 0.55rem;
        }}

        .kpi-delta {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            width: fit-content;
            font-size: 0.76rem;
            font-weight: 600;
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            font-variant-numeric: tabular-nums;
        }}

        .kpi-delta-pos {{
            color: #065F46;
            background-color: {COLORS["primary_soft"]};
        }}

        .kpi-delta-neg {{
            color: #991B1B;
            background-color: {COLORS["red_soft"]};
        }}

        .kpi-delta-neutral {{
            color: {COLORS["text_secondary"]};
            background-color: {COLORS["card_subtle"]};
        }}

        /* Page Header with Subtle Gradient Accent */
        .page-header {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            border: 1px solid {COLORS["border"]};
            border-left: 5px solid {COLORS["primary"]};
            border-radius: 14px;
            padding: 1.35rem 1.65rem;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.035);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 0.35rem;
        }}

        .page-eyebrow {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {COLORS["primary"]};
            margin-bottom: 0.25rem;
        }}

        .page-title {{
            color: {COLORS["text_primary"]};
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0;
            line-height: 1.2;
        }}

        .page-subtitle {{
            color: {COLORS["text_secondary"]};
            font-size: 0.9rem;
            margin: 0.35rem 0 0 0;
            line-height: 1.45;
        }}

        .mode-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.38rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            background-color: {COLORS["primary_soft"]};
            color: #065F46;
            border: 1px solid #A7F3D0;
            white-space: nowrap;
        }}

        .mode-badge::before {{
            content: "";
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: {COLORS["primary"]};
            display: inline-block;
        }}

        .mode-badge-custom {{
            background-color: {COLORS["blue_soft"]};
            color: #1E40AF;
            border: 1px solid #BFDBFE;
        }}

        .mode-badge-custom::before {{
            background-color: {COLORS["blue"]};
        }}

        .mode-badge-waiting {{
            background-color: {COLORS["amber_soft"]};
            color: #92400E;
            border: 1px solid #FDE68A;
        }}

        .mode-badge-waiting::before {{
            background-color: {COLORS["amber"]};
        }}

        /* Callout Banner */
        .callout-banner {{
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-left: 4px solid {COLORS["primary"]};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
        }}

        .callout-success {{
            background-color: #F6FEF9;
            border-left-color: {COLORS["primary"]};
        }}

        .callout-info {{
            background-color: #F8FAFF;
            border-left-color: {COLORS["blue"]};
        }}

        .callout-warning {{
            background-color: #FFFDF5;
            border-left-color: {COLORS["amber"]};
        }}

        .callout-danger {{
            background-color: #FEF7F7;
            border-left-color: {COLORS["red"]};
        }}

        .callout-title {{
            color: {COLORS["text_primary"]};
            font-weight: 700;
            font-size: 0.92rem;
            margin-bottom: 0.2rem;
        }}

        .callout-body {{
            color: {COLORS["text_secondary"]};
            font-size: 0.87rem;
            line-height: 1.5;
        }}

        /* Stepper Bar for Data Studio */
        .stepper-wrap {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.85rem;
            margin: 0.25rem 0 0.5rem 0;
        }}

        .step-pill {{
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 12px;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.025);
        }}

        .step-pill-active {{
            border-color: {COLORS["primary"]};
            background-color: #F6FEF9;
            box-shadow: 0 2px 8px rgba(0, 184, 107, 0.1);
        }}

        .step-pill-done {{
            border-color: #A7F3D0;
            background-color: {COLORS["primary_soft"]};
        }}

        .step-num {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.78rem;
            font-weight: 700;
            flex-shrink: 0;
            background-color: {COLORS["grid"]};
            color: {COLORS["text_secondary"]};
        }}

        .step-pill-active .step-num {{
            background-color: {COLORS["primary"]};
            color: #FFFFFF;
        }}

        .step-pill-done .step-num {{
            background-color: #059669;
            color: #FFFFFF;
        }}

        .step-text-title {{
            font-size: 0.84rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            line-height: 1.2;
        }}

        .step-text-sub {{
            font-size: 0.75rem;
            color: {COLORS["text_muted"]};
            margin-top: 0.1rem;
        }}

        /* Empty State Card */
        .empty-state-card {{
            background-color: {COLORS["card"]};
            border: 1px dashed {COLORS["border_strong"]};
            border-radius: 16px;
            padding: 2.25rem 2rem;
            text-align: center;
            margin: 1rem auto;
            max-width: 680px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        }}

        .empty-state-title {{
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            margin-bottom: 0.4rem;
        }}

        .empty-state-body {{
            font-size: 0.9rem;
            color: {COLORS["text_secondary"]};
            line-height: 1.55;
            margin-bottom: 0;
        }}

        /* Buttons */
        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 9px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.15s ease !important;
        }}

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {{
            background-color: {COLORS["primary"]} !important;
            border-color: {COLORS["primary"]} !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 6px rgba(0, 184, 107, 0.22) !important;
        }}

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {{
            background-color: {COLORS["primary_hover"]} !important;
            border-color: {COLORS["primary_hover"]} !important;
            box-shadow: 0 4px 12px rgba(0, 184, 107, 0.3) !important;
        }}

        /* Segmented Pill Radio Controls */
        div[role="radiogroup"] {{
            gap: 0.4rem !important;
        }}

        /* File Uploader Dropzone */
        [data-testid="stFileUploaderDropzone"] {{
            background-color: {COLORS["card_subtle"]} !important;
            border: 1.5px dashed {COLORS["border_strong"]} !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            transition: border-color 0.2s ease, background-color 0.2s ease;
        }}

        [data-testid="stFileUploaderDropzone"]:hover {{
            border-color: {COLORS["primary"]} !important;
            background-color: #F6FEF9 !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background-color: {COLORS["card"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 12px;
            padding: 0.35rem 0.5rem;
            margin-bottom: 1rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            color: {COLORS["text_secondary"]};
            font-weight: 600;
            font-size: 0.88rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border-bottom: none !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {COLORS["primary_soft"]} !important;
            color: #065F46 !important;
        }}

        .stTabs [data-baseweb="tab-highlight"] {{
            display: none !important;
        }}

        /* Dataframes */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 10px;
            overflow: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_spacer(size: str = "md") -> None:
    """Renders consistent vertical breathing room between major layout blocks."""
    heights = {"sm": "0.4rem", "md": "0.9rem", "lg": "1.5rem"}
    h = heights.get(size, "0.9rem")
    st.markdown(f'<div style="height: {h};"></div>', unsafe_allow_html=True)


def render_portfolio_overview(badge_text: str | None = None, badge_variant: str = "default") -> None:
    """Renders the cursive Naive brand logo and a clean, compact platform portfolio card."""
    badge_html = ""
    if badge_text:
        cls_map = {
            "default": "mode-badge",
            "custom": "mode-badge mode-badge-custom",
            "waiting": "mode-badge mode-badge-waiting",
        }
        badge_cls = cls_map.get(badge_variant, "mode-badge")
        badge_html = f'<span class="{badge_cls}">{html.escape(badge_text)}</span>'

    tech_stack = [
        "Python", "Streamlit", "Plotly", "Pandas", "NumPy",
        "PyArrow", "Scikit-Learn", "LightGBM", "Joblib",
    ]
    tech_pills = "".join(f'<span class="tech-pill">{html.escape(t)}</span>' for t in tech_stack)

    st.markdown(
        f"""
        <div class="portfolio-hero">
            <div class="portfolio-top" style="border-bottom: none; padding-bottom: 0;">
                <div>
                    <div class="brand-lockup">
                        <span class="brand-logo">Naive</span>
                        <span class="brand-divider">|</span>
                        <span class="brand-tagline">Supply Chain Intelligence &amp; Predictive Analytics</span>
                    </div>
                    <p class="portfolio-desc">
                        A dual-mode BI and Machine Learning platform that transforms raw supply chain exports into
                        executive KPIs, SLA diagnostics, margin leakage insights, and real-time late-delivery risk predictions.
                    </p>
                </div>
                <div>{badge_html}</div>
            </div>
            <div class="tech-stack-row">
                <span class="tech-stack-label">Tech Stack</span>
                {tech_pills}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title: str, subtitle: str | None = None) -> None:
    """Renders a consistently spaced section heading with an executive left accent."""
    sub_html = f'<p class="section-subheading">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-heading-wrap">
            <div>
                <h3 class="section-heading">{html.escape(title)}</h3>
                {sub_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card_header(title: str, subtitle: str | None = None, badge: str | None = None) -> None:
    """Renders a clean header inside an elevated container card."""
    sub_html = f'<p class="card-subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
    badge_html = f'<span class="card-badge">{html.escape(badge)}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="card-header">
            <div>
                <div class="card-title">{html.escape(title)}</div>
                {sub_html}
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    subtitle: str,
    badge_text: str | None = None,
    badge_variant: str = "default",
    eyebrow: str | None = "NAIVE SUPPLY CHAIN PLATFORM",
) -> None:
    """Renders a clean elevated white SaaS header card."""
    badge_html = ""
    if badge_text:
        cls_map = {
            "default": "mode-badge",
            "custom": "mode-badge mode-badge-custom",
            "waiting": "mode-badge mode-badge-waiting",
        }
        badge_cls = cls_map.get(badge_variant, "mode-badge")
        badge_html = f'<span class="{badge_cls}">{html.escape(badge_text)}</span>'

    eyebrow_html = f'<div class="page-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""

    st.markdown(
        f"""
        <div class="page-header">
            <div>
                {eyebrow_html}
                <h1 class="page-title">{html.escape(title)}</h1>
                <p class="page-subtitle">{html.escape(subtitle)}</p>
            </div>
            <div>{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_state: str = "neutral",
    accent_color: str | None = None,
) -> None:
    """Renders an elevated KPI card with semantic accent top border and pill delta."""
    top_color = accent_color or COLORS["primary"]
    delta_cls = {
        "positive": "kpi-delta kpi-delta-pos",
        "negative": "kpi-delta kpi-delta-neg",
        "neutral": "kpi-delta kpi-delta-neutral",
    }.get(delta_state, "kpi-delta kpi-delta-neutral")

    delta_html = f'<div class="{delta_cls}">{html.escape(delta)}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-top-color: {top_color};">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_callout_banner(title: str, body: str, variant: str = "success") -> None:
    """Renders an automated insight banner inside a white card with semantic left accent."""
    cls_map = {
        "success": "callout-banner callout-success",
        "info": "callout-banner callout-info",
        "warning": "callout-banner callout-warning",
        "danger": "callout-banner callout-danger",
    }
    banner_cls = cls_map.get(variant, "callout-banner callout-success")
    st.markdown(
        f"""
        <div class="{banner_cls}">
            <div class="callout-title">{html.escape(title)}</div>
            <div class="callout-body">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(current_step: int) -> None:
    """Renders a 3-step horizontal progress indicator for Data Studio."""
    steps = [
        (1, "Upload & Map Schema", "CSV, Excel, or Parquet"),
        (2, "Clean & Review Audit", "6-layer sanitization"),
        (3, "Activate & Benchmark", "Unlock Pages 1–6"),
    ]
    pills = []
    for num, title, sub in steps:
        if num < current_step:
            cls = "step-pill step-pill-done"
            icon = "✓"
        elif num == current_step:
            cls = "step-pill step-pill-active"
            icon = str(num)
        else:
            cls = "step-pill"
            icon = str(num)
        pills.append(
            f'<div class="{cls}"><div class="step-num">{icon}</div>'
            f'<div><div class="step-text-title">{html.escape(title)}</div>'
            f'<div class="step-text-sub">{html.escape(sub)}</div></div></div>'
        )
    st.markdown(f'<div class="stepper-wrap">{"".join(pills)}</div>', unsafe_allow_html=True)


def render_empty_state(page_title: str, page_subtitle: str, module_name: str, eyebrow: str = "NAIVE SUPPLY CHAIN PLATFORM") -> None:
    """Renders a friendly, actionable empty state with a direct link to Data Studio."""
    render_page_header(
        page_title,
        page_subtitle,
        badge_text="Awaiting Upload",
        badge_variant="waiting",
        eyebrow=eyebrow,
    )
    render_spacer("md")
    st.markdown(
        f"""
        <div class="empty-state-card">
            <div class="empty-state-title">No Active Dataset Loaded</div>
            <p class="empty-state-body">
                Upload and activate your supply chain dataset in <strong>Data Studio</strong> to unlock
                <strong>{html.escape(module_name)}</strong>. Your global sidebar filters and all analytics
                modules will populate automatically once activated.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, col_btn, _ = st.columns([1.4, 1.2, 1.4])
    with col_btn:
        st.page_link("pages/0_Data_Studio.py", label="Open Data Studio to Upload →", icon="🗄️", use_container_width=True)


def style_plotly_fig(
    fig: go.Figure,
    title: str | None = None,
    height: int = 380,
    show_legend: bool = True,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> go.Figure:
    """Applies refined light-mode SaaS Plotly styling: white bg, clean typography, subtle gridlines."""
    layout_kwargs = dict(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        height=height,
        showlegend=show_legend,
        colorway=DISCRETE_COLORS,
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            color=COLORS["text_secondary"],
            size=12,
        ),
        margin=dict(l=16, r=16, t=48 if title else 20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=COLORS["text_secondary"], size=11),
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(
            bgcolor=COLORS["text_primary"],
            bordercolor=COLORS["text_primary"],
            font=dict(color="#FFFFFF", size=12),
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
            title_font=dict(color=COLORS["text_secondary"], size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["grid"],
            gridwidth=1,
            zeroline=False,
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
            title_font=dict(color=COLORS["text_secondary"], size=12),
        ),
    )

    if title:
        layout_kwargs["title"] = dict(
            text=title,
            font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=COLORS["text_primary"], size=14.5),
            x=0.0,
            xanchor="left",
        )
    if xaxis_title is not None:
        layout_kwargs["xaxis"]["title"] = xaxis_title
    if yaxis_title is not None:
        layout_kwargs["yaxis"]["title"] = yaxis_title

    fig.update_layout(**layout_kwargs)
    return fig
