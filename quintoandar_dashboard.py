import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from mapa_calor import criar_mapa_calor, criar_tabela_bairros

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except Exception:
    HAS_STATSMODELS = False

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
# TEMA E CSS
# ============================================================
# DARK MODE (Default)
bg_color = "#0E1117"
card_bg = "linear-gradient(135deg, #1A1D24 0%, #252830 100%)"
card_border = "#2D3139"
text_color = "#FAFAFA"
subtext_color = "#8B8D93"
sidebar_bg = "#12151A"
chart_template = "plotly_dark"
chart_bg = "rgba(0,0,0,0)"
grid_color = "#2D3139"
title_gradient = "linear-gradient(90deg, #FF6B35, #FF9F1C)"

st.markdown(f"""
<style>
    /* App Background */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}
    
    /* KPI Cards */
    .kpi-card {{
        background: {card_bg};
        border: 1px solid {card_border};
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
        color: {subtext_color};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .kpi-sublabel {{
        font-size: 0.75rem;
        color: {subtext_color};
        margin-top: 4px;
    }}

    /* Header */
    .main-header {{
        text-align: center;
        padding: 10px 0 20px;
    }}
    .main-header h1 {{
        font-size: 2.2rem;
        background: {title_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }}
    .main-header p {{
        color: {subtext_color};
        font-size: 0.95rem;
    }}

    /* Sidebar headers */
    [data-testid="stSidebar"] h2 {{
        color: #FF6B35;
        font-size: 1.1rem;
    }}

    /* Charts & DataFrame containers */
    .stPlotlyChart, .stDataFrame {{
        border: 1px solid {card_border};
        border-radius: 12px;
        overflow: hidden;
        background-color: {card_bg if 'gradient' not in card_bg else 'transparent'};
    }}
    
    /* Divider */
    .section-divider {{
        border: 0; height: 1px;
        background: linear-gradient(90deg, transparent, {grid_color}, transparent);
        margin: 24px 0;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================
DATA_PATH = os.path.join("base", "quintoandar_database.xlsx")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(file_path, _file_mtime):
    """Load data with cache invalidation based on file modification time"""
    if not os.path.exists(file_path):
        return None
    df = pd.read_excel(file_path, dtype={'ID Imóvel': str})

    # Garantir tipos numéricos
    for col in ['Preço', 'Condomínio', 'Preço/m²']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[R$\s\.]', '', regex=True).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    df['Área (m²)'] = pd.to_numeric(df['Área (m²)'], errors='coerce').fillna(0).astype(int)
    df['Quartos'] = pd.to_numeric(df['Quartos'], errors='coerce').fillna(0).astype(int)
    
    # Recalcular Preço/m² para consistência
    df['Preço/m²'] = df.apply(lambda r: round(r['Preço'] / r['Área (m²)'], 2) if r['Área (m²)'] > 0 else 0, axis=1)
    
    return df

def format_brl(value):
    """Formata valor em BRL com separador de milhares e R$ prefix"""
    if pd.isna(value) or value == 0:
        return "R$ 0"
    # Formata número completo com separador de milhares (ponto)
    formatted = f"{int(value):,}".replace(",", ".")
    return f"R$ {formatted}"

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🏠 QuintoAndar Dashboard v3.1</h1>
    <p>Análise interativa dos imóveis coletados</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
# Cache-busting: use file modification time to invalidate cache when data updates
file_mtime = os.path.getmtime(DATA_PATH) if os.path.exists(DATA_PATH) else 0
df_raw = load_data(DATA_PATH, file_mtime)

if df_raw is None or df_raw.empty:
    st.error("❌ Nenhum dado encontrado. Execute o scraper primeiro: `python quintoandar_scraper.py`")
    st.stop()

# Detectar nomes de coluna (compatível com dados antigos e novos)
COL_BAIRRO = 'Bairro' if 'Bairro' in df_raw.columns else 'Bairro de Busca'
COL_CIDADE = 'Cidade' if 'Cidade' in df_raw.columns else 'Cidade de Busca'

# ============================================================
# VISÃO: ÚLTIMA CAPTURA vs TODOS OS REGISTROS
# ============================================================
# Por padrão, exibir apenas o registro mais recente de cada imóvel
df_latest = df_raw.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last')

# ============================================================
# DEFAULTS — RESET DE FILTROS
# ============================================================
df_default = df_latest if not df_latest.empty else df_raw
default_cidades = sorted(df_default[COL_CIDADE].dropna().unique().tolist()) if COL_CIDADE in df_default.columns else []
default_bairros = sorted(df_default[COL_BAIRRO].dropna().unique().tolist())
default_tipos = sorted(df_default['Tipo'].dropna().unique().tolist())
default_price_min = int(df_default['Preço'].min())
default_price_max = int(df_default['Preço'].max())
default_area_min = int(df_default['Área (m²)'].min())
default_area_max = int(df_default['Área (m²)'].max())
default_quartos = sorted(df_default['Quartos'].unique().tolist())

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if 'sel_price' not in st.session_state:
    st.session_state.sel_price = (default_price_min, default_price_max)
if 'price_input_min' not in st.session_state:
    st.session_state.price_input_min = default_price_min
if 'price_input_max' not in st.session_state:
    st.session_state.price_input_max = default_price_max
if 'sel_area' not in st.session_state:
    st.session_state.sel_area = (default_area_min, default_area_max)
if 'area_input_min' not in st.session_state:
    st.session_state.area_input_min = default_area_min
if 'area_input_max' not in st.session_state:
    st.session_state.area_input_max = default_area_max


# ============================================================

# Price Sync functions
def update_price_slider():
    st.session_state.sel_price = (st.session_state.price_input_min, st.session_state.price_input_max)

def update_price_inputs():
    st.session_state.price_input_min = st.session_state.sel_price[0]
    st.session_state.price_input_max = st.session_state.sel_price[1]

# Area Sync functions
def update_area_slider():
    st.session_state.sel_area = (st.session_state.area_input_min, st.session_state.area_input_max)

def update_area_inputs():
    st.session_state.area_input_min = st.session_state.sel_area[0]
    st.session_state.area_input_max = st.session_state.sel_area[1]

# SIDEBAR — FILTROS
# ============================================================
with st.sidebar:
    st.markdown("## 🔍 Filtros")

    # Toggle: ver todos os registros ou apenas os mais recentes
    show_all = st.toggle("📜 Mostrar série temporal completa", value=False, key="show_all",
                          help="Ativado: mostra TODOS os registros (mesmo imóvel repetido ao longo do tempo). Desativado: mostra apenas a captura mais recente de cada imóvel.")
    
    df = df_raw if show_all else df_latest
    
    st.markdown("---")
    
    # Cidade
    cidades = sorted(df[COL_CIDADE].dropna().unique().tolist()) if COL_CIDADE in df.columns else []
    if cidades:
        sel_cidades = st.multiselect("Cidade", cidades, default=cidades, key="sel_cidades")
        st.markdown("---")
    else:
        sel_cidades = []
    
    # Reset button at top - always visible
    col_reset_top = st.columns(1)[0]
    with col_reset_top:
        if st.button("🔁 Reset Filtros", use_container_width=True, key="reset_top"):
            # Reset all filter-related session state keys to defaults
            st.session_state.update({
                "show_all": False,
                "cidade_search": "",
                "sel_cidades": default_cidades,
                "bairro_search": "",
                "sel_bairros": default_bairros,
                "sel_tipos": default_tipos,
                "price_input_min": default_price_min,
                "price_input_max": default_price_max,
                "sel_price": (default_price_min, default_price_max),
                "area_input_min": default_area_min,
                "area_input_max": default_area_max,
                "sel_area": (default_area_min, default_area_max),
                "sel_quartos": default_quartos,
            })
            st.rerun()
    
    st.markdown("---")
    

    # Bairro (com busca)
    bairros = sorted(df[COL_BAIRRO].dropna().unique().tolist())
    bairro_search = st.text_input("🔎 Buscar bairro", placeholder="Digite para filtrar...", key="bairro_search")
    if bairro_search:
        bairros_filtered = [b for b in bairros if bairro_search.lower() in b.lower()]
    else:
        bairros_filtered = bairros
    sel_bairros = st.multiselect("Bairro", bairros_filtered, default=bairros_filtered, key="sel_bairros")
    
    # Tipo
    st.markdown("---")
    tipos = sorted(df['Tipo'].dropna().unique().tolist())
    sel_tipos = st.multiselect("Tipo de Imóvel", tipos, default=tipos, key="sel_tipos")
    
    # Preço
    st.markdown("---")
    price_min = int(df['Preço'].min())
    price_max = int(df['Preço'].max())
    if price_max > price_min:
        col_price1, col_price2 = st.columns(2)
        with col_price1:
            st.number_input("Preço Min (R$)", value=price_min, min_value=price_min, max_value=price_max, step=10000, key="price_input_min", on_change=update_price_slider)
        with col_price2:
            st.number_input("Preço Max (R$)", value=price_max, min_value=price_min, max_value=price_max, step=10000, key="price_input_max", on_change=update_price_slider)
        st.slider(
            "Ajuste com slider:",
            min_value=price_min, max_value=price_max,
            key="sel_price", step=10000, format="R$ %d", on_change=update_price_inputs
        )
        sel_price = st.session_state.sel_price
    else:
        sel_price = (price_min, price_max)
    
    # Área
    st.markdown("---")
    area_min = int(df['Área (m²)'].min())
    area_max = int(df['Área (m²)'].max())
    if area_max > area_min:
        col_area1, col_area2 = st.columns(2)
        with col_area1:
            st.number_input("Área Min (m²)", value=area_min, min_value=area_min, max_value=area_max, step=5, key="area_input_min", on_change=update_area_slider)
        with col_area2:
            st.number_input("Área Max (m²)", value=area_max, min_value=area_min, max_value=area_max, step=5, key="area_input_max", on_change=update_area_slider)
        st.slider("Ajuste com slider:", min_value=area_min, max_value=area_max, key="sel_area", step=5, on_change=update_area_inputs)
        sel_area = st.session_state.sel_area
    else:
        sel_area = (area_min, area_max)
    
    # Quartos
    quartos_opts = sorted(df['Quartos'].unique().tolist())
    sel_quartos = st.multiselect("Quartos", quartos_opts, default=quartos_opts, key="sel_quartos")

    st.markdown("---")
    st.caption(f"Base atualizada: {df_raw['Data e Hora da Extração'].max()}")
    st.caption(f"Imóveis únicos: {df_raw['ID Imóvel'].nunique()} | Registros totais: {len(df_raw)}")
    
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# APLICAR FILTROS
# ============================================================
# Base filter for cities
df_filtered_city = df[df[COL_CIDADE].isin(sel_cidades)] if (COL_CIDADE in df.columns and sel_cidades) else df

filtered = df_filtered_city[
    (df_filtered_city[COL_BAIRRO].isin(sel_bairros)) &
    (df_filtered_city['Tipo'].isin(sel_tipos)) &
    (df['Preço'].between(sel_price[0], sel_price[1])) &
    (df['Área (m²)'].between(sel_area[0], sel_area[1])) &
    (df['Quartos'].isin(sel_quartos))
].copy()

# ============================================================
# CRIAR ABAS
# ============================================================
tab1, tab2 = st.tabs(['📊 Dashboard', '🗺️ Mapa de Calor'])

# ============ ABA 1: DASHBOARD ============
with tab1:
    # ============================================================
    # KPIs
    # ============================================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Imóveis</div>
            <div class="kpi-value">{len(filtered):,}</div>
            <div class="kpi-sublabel">{'registros totais' if show_all else 'únicos'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_price = filtered['Preço'].mean() if not filtered.empty else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Preço Médio</div>
            <div class="kpi-value">{format_brl(avg_price)}</div>
            <div class="kpi-sublabel">mediana: {format_brl(filtered['Preço'].median()) if not filtered.empty else 'N/A'}</div>
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
        avg_condo = filtered['Condomínio'].mean() if not filtered.empty else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Condomínio Médio</div>
            <div class="kpi-value">{format_brl(avg_condo)}</div>
            <div class="kpi-sublabel">encargos mensais</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # ============================================================
    # GRÁFICOS
    # ============================================================
    chart_layout = dict(
        template=chart_template,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, family='Inter, sans-serif'),
        margin=dict(l=40, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor=sidebar_bg, font_color=text_color),
    )
    
    if not filtered.empty:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### 📊 Distribuição de Preços")
            fig_hist = px.histogram(
                filtered, x='Preço', nbins=30,
                color_discrete_sequence=['#FF6B35'],
                labels={'Preço': 'Preço (R$)', 'count': 'Quantidade'}
            )
            fig_hist.update_layout(**chart_layout, showlegend=False)
            fig_hist.update_xaxes(gridcolor=grid_color, tickformat=',.0f')
            fig_hist.update_yaxes(gridcolor=grid_color, title='Quantidade')
            st.plotly_chart(fig_hist, width="stretch")
        
        with chart_col2:
            st.markdown(f"#### 🏘️ Preço/m² por Bairro")
            avg_by_bairro = filtered.groupby(COL_BAIRRO)['Preço/m²'].mean().reset_index()
            avg_by_bairro = avg_by_bairro.sort_values('Preço/m²', ascending=True)
            fig_bar = px.bar(
                avg_by_bairro, x='Preço/m²', y=COL_BAIRRO, orientation='h',
                color='Preço/m²', color_continuous_scale=['#FF6B35', '#FF9F1C', '#FFD166'],
                labels={'Preço/m²': 'R$/m²', COL_BAIRRO: ''}
            )
            fig_bar.update_layout(**chart_layout, showlegend=False, coloraxis_showscale=False)
            fig_bar.update_xaxes(gridcolor=grid_color, tickformat=',.0f')
            fig_bar.update_yaxes(gridcolor=grid_color)
            st.plotly_chart(fig_bar, width="stretch")
    
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
        chart_col3, chart_col4 = st.columns(2)
        
        with chart_col3:
            st.markdown("#### 🏠 Tipos de Imóvel")
            type_counts = filtered['Tipo'].value_counts().reset_index()
            type_counts.columns = ['Tipo', 'Quantidade']
            fig_donut = px.pie(
                type_counts, values='Quantidade', names='Tipo', hole=0.55,
                color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0', '#118AB2']
            )
            fig_donut.update_layout(**chart_layout,
                legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5))
            fig_donut.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig_donut, width="stretch")
        
        with chart_col4:
            st.markdown("#### 💎 Preço vs Área")
            scatter_df = filtered[(filtered['Preço'] > 0) & (filtered['Área (m²)'] > 0)]
            trendline_mode = "ols" if HAS_STATSMODELS else None
            fig_scatter = px.scatter(
                scatter_df, x='Área (m²)', y='Preço', color='Tipo',
                size='Preço/m²', size_max=15, opacity=0.7, trendline=trendline_mode,
                color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0', '#118AB2'],
                labels={'Preço': 'Preço (R$)', 'Área (m²)': 'Área (m²)'},
                hover_data=[COL_BAIRRO, 'Quartos']
            )
            fig_scatter.update_layout(**chart_layout,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5))
            fig_scatter.update_xaxes(gridcolor=grid_color)
            fig_scatter.update_yaxes(gridcolor=grid_color, tickformat=',.0f')
            st.plotly_chart(fig_scatter, width="stretch")
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # ============================================================
    # TABELA DE DADOS
    # ============================================================
    st.markdown("#### 📋 Listagem de Imóveis")
    
    # 🔍 Search inputs for each column - organized in columns
    search_col1, search_col2, search_col3, search_col4 = st.columns(4)
    
    with search_col1:
        search_id = st.text_input("🆔 ID", placeholder="Buscar ID...", key="search_id", help="Digite parte do ID do imóvel")
    
    with search_col2:
        search_bairro = st.text_input("📍 Bairro", placeholder="Ex: Vila...", key="search_bairro", help="Busca parcial em Bairro")
    
    with search_col3:
        search_tipo = st.text_input("🏠 Tipo", placeholder="Ex: Apart...", key="search_tipo", help="Busca parcial em Tipo")
    
    with search_col4:
        search_endereco = st.text_input("📮 Endereço", placeholder="Ex: Rua...", key="search_endereco", help="Busca parcial em Endereço")
    
    # Apply filters based on search inputs
    if search_id:
        filtered = filtered[filtered['ID Imóvel'].astype(str).str.contains(search_id, case=False, na=False)]
    
    if search_bairro:
        filtered = filtered[filtered[COL_BAIRRO].astype(str).str.contains(search_bairro, case=False, na=False)]
    
    if search_tipo:
        filtered = filtered[filtered['Tipo'].astype(str).str.contains(search_tipo, case=False, na=False)]
    
    if search_endereco:
        filtered = filtered[filtered['Endereço'].astype(str).str.contains(search_endereco, case=False, na=False)]
    
    # Calcular IBairro (Índice de Preço do Bairro)
    bairro_avg_pm2 = df_raw.groupby(COL_BAIRRO)['Preço/m²'].mean()
    filtered['IBairro'] = filtered[COL_BAIRRO].apply(
        lambda b: filtered[filtered[COL_BAIRRO] == b]['Preço/m²'].values[0] / bairro_avg_pm2.get(b, 1) 
        if b in bairro_avg_pm2.index and len(filtered[filtered[COL_BAIRRO] == b]) > 0 else 0
    )
    filtered['IBairro'] = filtered.apply(
        lambda row: row['Preço/m²'] / bairro_avg_pm2.get(row[COL_BAIRRO], 1) if bairro_avg_pm2.get(row[COL_BAIRRO], 0) > 0 else 0,
        axis=1
    )
    
    display_cols = [
        'ID Imóvel', COL_BAIRRO, 'Tipo', 'Título/Descrição', 'Preço', 'Condomínio',
        'Área (m²)', 'Preço/m²', 'IBairro', 'Quartos', 'Endereço', 'Link', 'Data e Hora da Extração'
    ]
    display_df = filtered[[c for c in display_cols if c in filtered.columns]].copy()
    
    # Renomear colunas para exibição final (garante cabeçalho correto)
    display_df = display_df.rename(columns={
        'Preço': 'Preço (R$)',
        'Condomínio': 'Condomínio (R$)',
        'Área (m²)': 'Área (m²)',
        'Preço/m²': 'Preço/m² (R$)',
        'IBairro': 'IBairro',
        'Quartos': 'Quartos',
        'Data e Hora da Extração': 'Captura'
    })
    
    # Formatação estilo brasileiro (Pontos para milhar)
    def brl_fmt(x):
        try:
            return f"R$ {int(x):,}".replace(",", ".")
        except:
            return str(x)
    
    # Para grandes datasets (>1000 linhas), usar formatação simples
    # Para pequenos datasets, usar Styler com formatação avançada
    # Configuração de colunas para garantir ordenação numérica
    column_config = {
        "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
        "Captura": st.column_config.TextColumn("📅 Captura"),
        "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
        COL_BAIRRO: st.column_config.TextColumn("📍 Bairro"),
        "Preço (R$)": st.column_config.NumberColumn("Preço", format="R$ %,.0f"),
        "Condomínio (R$)": st.column_config.NumberColumn("Condo", format="R$ %,.0f"),
        "Preço/m² (R$)": st.column_config.NumberColumn("R$/m²", format="R$ %,.2f"),
        "Área (m²)": st.column_config.NumberColumn("Área", format="%,.0f m²"),
        "IBairro": st.column_config.NumberColumn("IBairro", format="%.2f"),
    }

    # Usar Styler apenas para cores se o dataset for pequeno, mas mantendo tipos numéricos
    if len(display_df) <= 1000:
        def highlight_ibairro(val):
            if pd.isna(val) or val == 0: return ''
            return 'background-color: rgba(6, 214, 160, 0.3); color: #06D6A0' if val < 1 else 'background-color: rgba(255, 107, 53, 0.3); color: #FF6B35'
        
        styler = display_df.style.map(highlight_ibairro, subset=['IBairro'])
        st.dataframe(styler, width="stretch", height=500, column_config=column_config, hide_index=True)
    else:
        st.dataframe(display_df, width="stretch", height=500, column_config=column_config, hide_index=True)
    
    unique_count = filtered['ID Imóvel'].nunique() if not filtered.empty else 0
    st.caption(f"Exibindo {len(filtered)} registros ({unique_count} imóveis únicos) | Última atualização: {df_raw['Data e Hora da Extração'].max()}")


# ============ ABA 2: MAPA DE CALOR ============
with tab2:
    st.markdown("#### 🗺️ Mapa de Calor - Preços Médios por Bairro")
    
    # Criar mapa com todos os dados (sem filtros de preço/área, apenas bairro e tipo)
    mapa_filtered = df[
        (df[COL_BAIRRO].isin(sel_bairros)) &
        (df['Tipo'].isin(sel_tipos)) &
        (df['Quartos'].isin(sel_quartos))
    ].copy()
    
    if not mapa_filtered.empty:
        fig_mapa = criar_mapa_calor(mapa_filtered)
        if fig_mapa:
            st.plotly_chart(fig_mapa, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 📊 Estatísticas por Bairro")
            tabela_bairros = criar_tabela_bairros(mapa_filtered)
            if tabela_bairros is not None:
                tabela_display = tabela_bairros.copy()
                tabela_display['Preço Min'] = tabela_display['Preço Min'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço Max'] = tabela_display['Preço Max'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço Médio'] = tabela_display['Preço Médio'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço/m² Médio'] = tabela_display['Preço/m² Médio'].apply(lambda x: f"R$ {int(x):,.0f}".replace(",", "."))
                tabela_display['Área Média'] = tabela_display['Área Média'].apply(lambda x: f"{int(x):,} m²".replace(",", "."))
                tabela_display = tabela_display.rename(columns={'Imóveis': '🏠 Imóveis'})
                
                st.dataframe(tabela_display, use_container_width=True, hide_index=True)
    else:
        st.warning("❌ Nenhum dado disponível com os filtros selecionados")

