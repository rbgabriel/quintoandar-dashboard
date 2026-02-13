import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="QuintoAndar Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS CUSTOMIZADO
# ============================================================
st.markdown("""
<style>
    /* --- KPI Cards --- */
    .kpi-card {
        background: linear-gradient(135deg, #1A1D24 0%, #252830 100%);
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #FF6B35;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #FF6B35;
        margin: 4px 0;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #8B8D93;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-sublabel {
        font-size: 0.75rem;
        color: #555;
        margin-top: 4px;
    }

    /* --- Header --- */
    .main-header {
        text-align: center;
        padding: 10px 0 20px;
    }
    .main-header h1 {
        font-size: 2.2rem;
        background: linear-gradient(90deg, #FF6B35, #FF9F1C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .main-header p {
        color: #8B8D93;
        font-size: 0.95rem;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background: #12151A;
    }
    [data-testid="stSidebar"] h2 {
        color: #FF6B35;
        font-size: 1.1rem;
    }

    /* --- Plotly Charts --- */
    .stPlotlyChart {
        border: 1px solid #2D3139;
        border-radius: 12px;
        overflow: hidden;
    }

    /* --- Dataframe --- */
    .stDataFrame {
        border: 1px solid #2D3139;
        border-radius: 12px;
        overflow: hidden;
    }

    /* --- Divider --- */
    .section-divider {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #2D3139, transparent);
        margin: 24px 0;
    }

    /* --- Expander --- */
    .streamlit-expanderHeader {
        background: #1A1D24;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================
DATA_PATH = os.path.join("base", "quintoandar_database.xlsx")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_excel(DATA_PATH, dtype={'ID Imóvel': str})

    # Normalizar preço para numérico
    df['Preço_num'] = df['Preço'].apply(parse_price)
    df['Condo_num'] = df['Condomínio'].apply(parse_price)
    
    # Garantir tipos
    df['Área (m²)'] = pd.to_numeric(df['Área (m²)'], errors='coerce').fillna(0).astype(int)
    df['Preço/m²'] = pd.to_numeric(df['Preço/m²'], errors='coerce').fillna(0)
    df['Quartos'] = df['Quartos'].apply(lambda x: int(x) if str(x).isdigit() else 0)
    
    return df

def parse_price(val):
    if pd.isna(val) or val == "N/A":
        return 0
    text = str(val).replace("R$", "").replace(".", "").replace(",", "").strip()
    nums = ''.join(c for c in text if c.isdigit())
    return int(nums) if nums else 0

def format_brl(value):
    """Formata número como moeda brasileira."""
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"R$ {value/1_000:.0f}k"
    return f"R$ {value:.0f}"

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🏠 QuintoAndar Dashboard</h1>
    <p>Análise interativa dos imóveis coletados</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
df = load_data()

if df is None or df.empty:
    st.error("❌ Nenhum dado encontrado. Execute o scraper primeiro: `python quintoandar_scraper.py`")
    st.stop()

# ============================================================
# SIDEBAR — FILTROS
# ============================================================
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    
    # Bairro
    bairros = sorted(df['Bairro de Busca'].dropna().unique().tolist())
    sel_bairros = st.multiselect("Bairro", bairros, default=bairros)
    
    # Tipo
    tipos = sorted(df['Tipo'].dropna().unique().tolist())
    sel_tipos = st.multiselect("Tipo de Imóvel", tipos, default=tipos)
    
    # Preço
    st.markdown("---")
    price_min = int(df['Preço_num'].min())
    price_max = int(df['Preço_num'].max())
    if price_max > price_min:
        sel_price = st.slider(
            "Faixa de Preço (R$)",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, price_max),
            step=10000,
            format="R$ %d"
        )
    else:
        sel_price = (price_min, price_max)
    
    # Área
    area_min = int(df['Área (m²)'].min())
    area_max = int(df['Área (m²)'].max())
    if area_max > area_min:
        sel_area = st.slider(
            "Área (m²)",
            min_value=area_min,
            max_value=area_max,
            value=(area_min, area_max),
            step=5
        )
    else:
        sel_area = (area_min, area_max)
    
    # Quartos
    quartos_opts = sorted(df['Quartos'].unique().tolist())
    sel_quartos = st.multiselect("Quartos", quartos_opts, default=quartos_opts)

    st.markdown("---")
    st.caption(f"Base atualizada: {df['Data e Hora da Extração'].max()}")
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# APLICAR FILTROS
# ============================================================
filtered = df[
    (df['Bairro de Busca'].isin(sel_bairros)) &
    (df['Tipo'].isin(sel_tipos)) &
    (df['Preço_num'].between(sel_price[0], sel_price[1])) &
    (df['Área (m²)'].between(sel_area[0], sel_area[1])) &
    (df['Quartos'].isin(sel_quartos))
].copy()

# ============================================================
# KPIs
# ============================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total de Imóveis</div>
        <div class="kpi-value">{len(filtered):,}</div>
        <div class="kpi-sublabel">de {len(df):,} na base</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_price = filtered['Preço_num'].mean() if not filtered.empty else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Preço Médio</div>
        <div class="kpi-value">{format_brl(avg_price)}</div>
        <div class="kpi-sublabel">mediana: {format_brl(filtered['Preço_num'].median()) if not filtered.empty else 'N/A'}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_pm2 = filtered['Preço/m²'].mean() if not filtered.empty else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Preço/m² Médio</div>
        <div class="kpi-value">{format_brl(avg_pm2)}</div>
        <div class="kpi-sublabel">por metro quadrado</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_area = filtered['Área (m²)'].mean() if not filtered.empty else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Área Média</div>
        <div class="kpi-value">{avg_area:.0f} m²</div>
        <div class="kpi-sublabel">média dos filtrados</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    avg_condo = filtered['Condo_num'].mean() if not filtered.empty else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Condomínio Médio</div>
        <div class="kpi-value">{format_brl(avg_condo)}</div>
        <div class="kpi-sublabel">encargos mensais</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# GRÁFICOS — LINHA 1
# ============================================================
if not filtered.empty:
    chart_col1, chart_col2 = st.columns(2)
    
    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA', family='Inter, sans-serif'),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor='#1A1D24', font_color='#FAFAFA'),
    )
    
    # Distribuição de Preços
    with chart_col1:
        st.markdown("#### 📊 Distribuição de Preços")
        fig_hist = px.histogram(
            filtered,
            x='Preço_num',
            nbins=30,
            color_discrete_sequence=['#FF6B35'],
            labels={'Preço_num': 'Preço (R$)', 'count': 'Quantidade'}
        )
        fig_hist.update_layout(
            **chart_layout,
            showlegend=False,
            xaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            yaxis=dict(gridcolor='#2D3139', title='Quantidade')
        )
        st.plotly_chart(fig_hist, width="stretch")
    
    # Preço/m² por Bairro
    with chart_col2:
        st.markdown("#### 🏘️ Preço/m² por Bairro")
        avg_by_bairro = filtered.groupby('Bairro de Busca')['Preço/m²'].mean().reset_index()
        avg_by_bairro = avg_by_bairro.sort_values('Preço/m²', ascending=True)
        
        fig_bar = px.bar(
            avg_by_bairro,
            x='Preço/m²',
            y='Bairro de Busca',
            orientation='h',
            color='Preço/m²',
            color_continuous_scale=['#FF6B35', '#FF9F1C', '#FFD166'],
            labels={'Preço/m²': 'R$/m²', 'Bairro de Busca': ''}
        )
        fig_bar.update_layout(
            **chart_layout,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            yaxis=dict(gridcolor='#2D3139')
        )
        st.plotly_chart(fig_bar, width="stretch")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ============================================================
    # GRÁFICOS — LINHA 2
    # ============================================================
    chart_col3, chart_col4 = st.columns(2)
    
    # Tipos de Imóvel (Donut)
    with chart_col3:
        st.markdown("#### 🏠 Tipos de Imóvel")
        type_counts = filtered['Tipo'].value_counts().reset_index()
        type_counts.columns = ['Tipo', 'Quantidade']
        
        fig_donut = px.pie(
            type_counts,
            values='Quantidade',
            names='Tipo',
            hole=0.55,
            color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0', '#118AB2']
        )
        fig_donut.update_layout(
            **chart_layout,
            legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5)
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )
        st.plotly_chart(fig_donut, width="stretch")
    
    # Scatter: Preço vs Área
    with chart_col4:
        st.markdown("#### 💎 Preço vs Área")
        scatter_df = filtered[(filtered['Preço_num'] > 0) & (filtered['Área (m²)'] > 0)]
        
        fig_scatter = px.scatter(
            scatter_df,
            x='Área (m²)',
            y='Preço_num',
            color='Tipo',
            size='Preço/m²',
            size_max=15,
            opacity=0.7,
            color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0', '#118AB2'],
            labels={'Preço_num': 'Preço (R$)', 'Área (m²)': 'Área (m²)'},
            hover_data=['Bairro de Busca', 'Quartos']
        )
        fig_scatter.update_layout(
            **chart_layout,
            xaxis=dict(gridcolor='#2D3139'),
            yaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
        )
        st.plotly_chart(fig_scatter, width="stretch")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# TABELA DE DADOS
# ============================================================
st.markdown("#### 📋 Listagem de Imóveis")

# Preparar tabela para exibição
display_cols = [
    'ID Imóvel', 'Bairro de Busca', 'Tipo', 'Preço', 'Condomínio',
    'Área (m²)', 'Preço/m²', 'Quartos', 'Endereço', 'Link'
]
display_df = filtered[display_cols].copy()
display_df['Preço/m²'] = display_df['Preço/m²'].apply(lambda x: f"R$ {x:,.0f}" if x > 0 else "N/A")

st.dataframe(
    display_df,
    width="stretch",
    height=500,
    column_config={
        "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
        "Preço": st.column_config.TextColumn("💰 Preço"),
        "Condomínio": st.column_config.TextColumn("🏢 Condo"),
        "Área (m²)": st.column_config.NumberColumn("📐 Área", format="%d m²"),
        "Quartos": st.column_config.NumberColumn("🛏️ Quartos"),
        "Bairro de Busca": st.column_config.TextColumn("📍 Bairro"),
        "Tipo": st.column_config.TextColumn("🏠 Tipo"),
        "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
        "Endereço": st.column_config.TextColumn("📍 Endereço"),
        "Preço/m²": st.column_config.TextColumn("💲 R$/m²"),
    },
    hide_index=True
)

st.caption(f"Exibindo {len(filtered)} de {len(df)} imóveis | Última atualização: {df['Data e Hora da Extração'].max()}")
