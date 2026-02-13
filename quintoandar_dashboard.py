import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from bairros_zonas import BAIRROS_ZONAS_MAPPING, BAIRROS_NORMALIZATION

# ============================================================
# BAIRROS & ZONAS MAPPING
# ============================================================
ZONE_MAPPING = BAIRROS_ZONAS_MAPPING
NORMALIZATION = BAIRROS_NORMALIZATION

def normalize_bairro(bairro):
    """Normaliza nome do bairro (remove variacoes e inconsistencias)"""
    if not bairro or pd.isna(bairro):
        return "N/A"
    
    bairro_normalized = str(bairro).strip().lower()
    
    # Verificar se ha mapeamento especifico
    if bairro_normalized in NORMALIZATION:
        return NORMALIZATION[bairro_normalized]
    
    # Se nao tiver mapeamento, retornar o bairro original com primeira letra maiuscula
    return str(bairro).strip()

def get_zone_for_bairro(bairro):
    """Obtem a zona (Zona Sul, Norte, Leste, Oeste, Centro) para um bairro"""
    normalized = normalize_bairro(bairro)
    
    for zone, bairros_list in ZONE_MAPPING.items():
        if normalized in bairros_list:
            return zone
    
    return "Sem zona"

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

    # Normalizar bairros e adicionar zona
    if 'Bairro' in df.columns:
        df['Bairro'] = df['Bairro'].apply(normalize_bairro)
        df['Zona'] = df['Bairro'].apply(get_zone_for_bairro)
    
    return df

def format_brl(value):
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
# SIDEBAR — FILTROS
# ============================================================
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    
    # Toggle: ver todos os registros ou apenas os mais recentes
    show_all = st.toggle("📜 Mostrar série temporal completa", value=False, 
                          help="Ativado: mostra TODOS os registros (mesmo imóvel repetido ao longo do tempo). Desativado: mostra apenas a captura mais recente de cada imóvel.")
    
    df = df_raw if show_all else df_latest
    
    st.markdown("---")
    
    # Bairro (com busca)
    bairros = sorted(df[COL_BAIRRO].dropna().unique().tolist())
    bairro_search = st.text_input("🔎 Buscar bairro", placeholder="Digite para filtrar...")
    if bairro_search:
        bairros_filtered = [b for b in bairros if bairro_search.lower() in b.lower()]
    else:
        bairros_filtered = bairros
    sel_bairros = st.multiselect("Bairro", bairros_filtered, default=bairros_filtered)
    
    # Zona (new filter)
    st.markdown("---")
    zonas = sorted([z for z in df.get('Zona', pd.Series()).dropna().unique().tolist() if z != "Sem zona"])
    sel_zonas = st.multiselect("📍 Zona", zonas, default=zonas, 
                                help="Zona Sul, Norte, Leste, Oeste, Centro")
    
    # Tipo
    st.markdown("---")
    tipos = sorted(df['Tipo'].dropna().unique().tolist())
    sel_tipos = st.multiselect("Tipo de Imóvel", tipos, default=tipos)
    
    # Preço
    st.markdown("---")
    price_min = int(df['Preço'].min())
    price_max = int(df['Preço'].max())
    if price_max > price_min:
        col_price1, col_price2 = st.columns(2)
        with col_price1:
            price_input_min = st.number_input("Preço Min (R$)", value=price_min, min_value=price_min, max_value=price_max, step=10000)
        with col_price2:
            price_input_max = st.number_input("Preço Max (R$)", value=price_max, min_value=price_min, max_value=price_max, step=10000)
        sel_price = st.slider(
            "Ajuste com slider:",
            min_value=price_min, max_value=price_max,
            value=(price_input_min, price_input_max), step=10000, format="R$ %d"
        )
    else:
        sel_price = (price_min, price_max)
    
    # Área
    st.markdown("---")
    area_min = int(df['Área (m²)'].min())
    area_max = int(df['Área (m²)'].max())
    if area_max > area_min:
        col_area1, col_area2 = st.columns(2)
        with col_area1:
            area_input_min = st.number_input("Área Min (m²)", value=area_min, min_value=area_min, max_value=area_max, step=5)
        with col_area2:
            area_input_max = st.number_input("Área Max (m²)", value=area_max, min_value=area_min, max_value=area_max, step=5)
        sel_area = st.slider("Ajuste com slider:", min_value=area_min, max_value=area_max, value=(area_input_min, area_input_max), step=5)
    else:
        sel_area = (area_min, area_max)
    
    # Quartos
    quartos_opts = sorted(df['Quartos'].unique().tolist())
    sel_quartos = st.multiselect("Quartos", quartos_opts, default=quartos_opts)

    st.markdown("---")
    st.caption(f"Base atualizada: {df_raw['Data e Hora da Extração'].max()}")
    st.caption(f"Imóveis únicos: {df_raw['ID Imóvel'].nunique()} | Registros totais: {len(df_raw)}")
    
    col_refresh, col_reset = st.columns(2)
    with col_refresh:
        if st.button("🔄 Recarregar Dados"):
            st.cache_data.clear()
            st.rerun()
    with col_reset:
        if st.button("🔁 Reset Filtros"):
            st.rerun()

# ============================================================
# APLICAR FILTROS
# ============================================================
filtered = df[
    (df[COL_BAIRRO].isin(sel_bairros)) &
    (df['Zona'].isin(sel_zonas)) &
    (df['Tipo'].isin(sel_tipos)) &
    (df['Preço'].between(sel_price[0], sel_price[1])) &
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
        fig_scatter = px.scatter(
            scatter_df, x='Área (m²)', y='Preço', color='Tipo',
            size='Preço/m²', size_max=15, opacity=0.7, trendline="ols",
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
search_col1, search_col2, search_col3, search_col4, search_col5 = st.columns(5)

with search_col1:
    search_id = st.text_input("🆔 ID", placeholder="Buscar ID...", key="search_id", help="Digite parte do ID do imóvel")

with search_col2:
    search_bairro = st.text_input("📍 Bairro", placeholder="Ex: Vila...", key="search_bairro", help="Busca parcial em Bairro")

with search_col3:
    search_zona = st.text_input("🗺️ Zona", placeholder="Ex: Sul...", key="search_zona", help="Busca parcial em Zona")

with search_col4:
    search_tipo = st.text_input("🏠 Tipo", placeholder="Ex: Apart...", key="search_tipo", help="Busca parcial em Tipo")

with search_col5:
    search_endereco = st.text_input("📮 Endereço", placeholder="Ex: Rua...", key="search_endereco", help="Busca parcial em Endereço")

# Apply filters based on search inputs
if search_id:
    filtered = filtered[filtered['ID Imóvel'].astype(str).str.contains(search_id, case=False, na=False)]

if search_bairro:
    filtered = filtered[filtered[COL_BAIRRO].astype(str).str.contains(search_bairro, case=False, na=False)]

if search_zona:
    filtered = filtered[filtered['Zona'].astype(str).str.contains(search_zona, case=False, na=False)]

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
    'ID Imóvel', COL_BAIRRO, 'Zona', 'Tipo', 'Título/Descrição', 'Preço', 'Condomínio',
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
if len(display_df) > 1000:
    # Formatação simples para grandes datasets
    display_df_fmt = display_df.copy()
    for col in ['Preço (R$)', 'Condomínio (R$)', 'Preço/m² (R$)']:
        if col in display_df_fmt.columns:
            display_df_fmt[col] = display_df_fmt[col].apply(lambda x: brl_fmt(x) if pd.notna(x) else "N/A")
    if 'Área (m²)' in display_df_fmt.columns:
        display_df_fmt['Área (m²)'] = display_df_fmt['Área (m²)'].apply(lambda x: f"{int(x):,} m²".replace(",", ".") if pd.notna(x) else "N/A")
    
    st.dataframe(
        display_df_fmt,
        width="stretch",
        height=500,
        column_config={
            "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
            "Captura": st.column_config.TextColumn("📅 Captura"),
            "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
            COL_BAIRRO: st.column_config.TextColumn("📍 Bairro"),
        },
        hide_index=True
    )
else:
    # Usar Styler para pequenos datasets
    def highlight_ibairro(val):
        """Colorir IBairro: verde se < 1, vermelho se >= 1"""
        if pd.isna(val) or val == 0:
            return ''
        elif val < 1:
            return 'background-color: rgba(6, 214, 160, 0.3); color: #06D6A0'  # Verde
        else:
            return 'background-color: rgba(255, 107, 53, 0.3); color: #FF6B35'  # Vermelho
    
    styler = display_df.style.format({
        'Preço (R$)': brl_fmt,
        'Condomínio (R$)': brl_fmt,
        'Área (m²)': lambda x: f"{int(x):,} m²".replace(",", "."),
        'Preço/m² (R$)': brl_fmt,
        'IBairro': lambda x: f"{x:.2f}" if x > 0 else "N/A"
    }).applymap(lambda val: highlight_ibairro(val) if True else '', subset=['IBairro'])
    
    st.dataframe(
        styler,
        width="stretch",
        height=500,
        column_config={
            "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
            "Captura": st.column_config.TextColumn("📅 Captura"),
            "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
            COL_BAIRRO: st.column_config.TextColumn("📍 Bairro"),
        },
        hide_index=True
    )

unique_count = filtered['ID Imóvel'].nunique() if not filtered.empty else 0
st.caption(f"Exibindo {len(filtered)} registros ({unique_count} imóveis únicos) | Última atualização: {df_raw['Data e Hora da Extração'].max()}")
