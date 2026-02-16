import streamlit as st
from utils.formatting import format_brl

# ============================================================
# TEMA E ESTILOS
# ============================================================
BG_COLOR = "#0E1117"
CARD_BG = "linear-gradient(135deg, #1A1D24 0%, #252830 100%)"
CARD_BORDER = "#2D3139"
TEXT_COLOR = "#FAFAFA"
SUBTEXT_COLOR = "#8B8D93"
SIDEBAR_BG = "#12151A"
CHART_TEMPLATE = "plotly_dark"
GRID_COLOR = "#2D3139"
TITLE_GRADIENT = "linear-gradient(90deg, #FF6B35, #FF9F1C)"

__all__ = ['BG_COLOR', 'CARD_BG', 'CARD_BORDER', 'TEXT_COLOR', 'SUBTEXT_COLOR', 'SIDEBAR_BG', 'CHART_TEMPLATE', 'GRID_COLOR', 'TITLE_GRADIENT', 'apply_custom_css', 'render_header', 'render_kpi_card', 'get_chart_layout']

def apply_custom_css():
    st.markdown(f"""
    <style>
        /* App Background */
        [data-testid="stAppViewContainer"] {{
            background-color: {BG_COLOR};
            color: {TEXT_COLOR};
        }}
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
        }}
        
        /* KPI Cards */
        .kpi-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 12px;
            padding: 20px 24px;
            text-align: center;
            transition: transform 0.2s, border-color 0.2s;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: #FF6B35;
        }}
        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #FF6B35;
            margin: 4px 0;
            line-height: 1.2;
        }}
        .kpi-label {{
            font-size: 0.85rem;
            color: {SUBTEXT_COLOR};
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .kpi-sublabel {{
            font-size: 0.75rem;
            color: {SUBTEXT_COLOR};
            margin-top: 4px;
        }}

        /* Header */
        .main-header {{
            text-align: center;
            padding: 10px 0 20px;
        }}
        .main-header h1 {{
            font-size: 2.2rem;
            background: {TITLE_GRADIENT};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }}
        .main-header p {{
            color: {SUBTEXT_COLOR};
            font-size: 0.95rem;
        }}

        /* Sidebar headers */
        [data-testid="stSidebar"] h2 {{
            color: #FF6B35;
            font-size: 1.1rem;
        }}

        /* Charts & DataFrame containers */
        .stPlotlyChart, .stDataFrame {{
            border: 1px solid {CARD_BORDER};
            border-radius: 12px;
            overflow: hidden;
            background-color: transparent;
        }}
        
        /* Divider */
        .section-divider {{
            border: 0; height: 1px;
            background: linear-gradient(90deg, transparent, {GRID_COLOR}, transparent);
            margin: 24px 0;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_header(version="3.1"):
    st.markdown(f"""
    <div class="main-header">
        <h1>🏠 QuintoAndar Dashboard v{version}</h1>
        <p>Análise interativa dos imóveis coletados</p>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label, value, sublabel):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sublabel">{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)

def get_chart_layout():
    return dict(
        template=CHART_TEMPLATE,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, family='Inter, sans-serif'),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor=SIDEBAR_BG, font_color=TEXT_COLOR),
    )
