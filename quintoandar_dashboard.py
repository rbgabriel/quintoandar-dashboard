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
    [data-testid="stSidebar"] { background: #12151A; }
    [data-testid="stSidebar"] h2 { color: #FF6B35; font-size: 1.1rem; }
    .stPlotlyChart, .stDataFrame {
        border: 1px solid #2D3139;
        border-radius: 12px;
        overflow: hidden;
    }
    .section-divider {
        border: 0; height: 1px;
        background: linear-gradient(90deg, transparent, #2D3139, transparent);
        margin: 24px 0;
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
df_raw = load_data()

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
    
    # Tipo
    tipos = sorted(df['Tipo'].dropna().unique().tolist())
    sel_tipos = st.multiselect("Tipo de Imóvel", tipos, default=tipos)
    
    # Preço
    st.markdown("---")
    price_min = int(df['Preço'].min())
    price_max = int(df['Preço'].max())
    if price_max > price_min:
        sel_price = st.slider(
            "Faixa de Preço (R$)",
            min_value=price_min, max_value=price_max,
            value=(price_min, price_max), step=10000, format="R$ %d"
        )
    else:
        sel_price = (price_min, price_max)
    
    # Área
    area_min = int(df['Área (m²)'].min())
    area_max = int(df['Área (m²)'].max())
    if area_max > area_min:
        sel_area = st.slider("Área (m²)", min_value=area_min, max_value=area_max, value=(area_min, area_max), step=5)
    else:
        sel_area = (area_min, area_max)
    
    # Quartos
    quartos_opts = sorted(df['Quartos'].unique().tolist())
    sel_quartos = st.multiselect("Quartos", quartos_opts, default=quartos_opts)

    st.markdown("---")
    st.caption(f"Base atualizada: {df_raw['Data e Hora da Extração'].max()}")
    st.caption(f"Imóveis únicos: {df_raw['ID Imóvel'].nunique()} | Registros totais: {len(df_raw)}")
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# APLICAR FILTROS
# ============================================================
filtered = df[
    (df[COL_BAIRRO].isin(sel_bairros)) &
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
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FAFAFA', family='Inter, sans-serif'),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor='#1A1D24', font_color='#FAFAFA'),
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
        fig_hist.update_layout(**chart_layout, showlegend=False,
            xaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            yaxis=dict(gridcolor='#2D3139', title='Quantidade'))
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
        fig_bar.update_layout(**chart_layout, showlegend=False, coloraxis_showscale=False,
            xaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            yaxis=dict(gridcolor='#2D3139'))
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
            size='Preço/m²', size_max=15, opacity=0.7,
            color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0', '#118AB2'],
            labels={'Preço': 'Preço (R$)', 'Área (m²)': 'Área (m²)'},
            hover_data=[COL_BAIRRO, 'Quartos']
        )
        fig_scatter.update_layout(**chart_layout,
            xaxis=dict(gridcolor='#2D3139'),
            yaxis=dict(gridcolor='#2D3139', tickformat=',.0f'),
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5))
        st.plotly_chart(fig_scatter, width="stretch")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# TABELA DE DADOS
# ============================================================
st.markdown("#### 📋 Listagem de Imóveis")

display_cols = [
    'ID Imóvel', COL_BAIRRO, 'Tipo', 'Preço', 'Condomínio',
    'Área (m²)', 'Preço/m²', 'Quartos', 'Endereço', 'Link', 'Data e Hora da Extração'
]
display_df = filtered[[c for c in display_cols if c in filtered.columns]].copy()

# Formatar números com separador de milhares (padrão brasileiro)
def fmt_brl(v):
    return f"R$ {int(v):,}".replace(',', '.') if v > 0 else "N/A"

def fmt_num(v):
    return f"{int(v):,}".replace(',', '.') if v > 0 else "0"

display_df['Preço'] = display_df['Preço'].apply(fmt_brl)
display_df['Condomínio'] = display_df['Condomínio'].apply(fmt_brl)
display_df['Preço/m²'] = display_df['Preço/m²'].apply(fmt_brl)
display_df['Área (m²)'] = display_df['Área (m²)'].apply(lambda x: f"{fmt_num(x)} m²")

st.dataframe(
    display_df,
    width="stretch",
    height=500,
    column_config={
        "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
        "Preço": st.column_config.TextColumn("💰 Preço"),
        "Condomínio": st.column_config.TextColumn("🏢 Condo"),
        "Área (m²)": st.column_config.TextColumn("📐 Área"),
        "Quartos": st.column_config.NumberColumn("🛏️ Quartos"),
        COL_BAIRRO: st.column_config.TextColumn("📍 Bairro"),
        "Tipo": st.column_config.TextColumn("🏠 Tipo"),
        "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
        "Endereço": st.column_config.TextColumn("📍 Endereço"),
        "Preço/m²": st.column_config.TextColumn("💲 R$/m²"),
        "Data e Hora da Extração": st.column_config.TextColumn("📅 Captura"),
    },
    hide_index=True
)

unique_count = filtered['ID Imóvel'].nunique() if not filtered.empty else 0
st.caption(f"Exibindo {len(filtered)} registros ({unique_count} imóveis únicos) | Última atualização: {df_raw['Data e Hora da Extração'].max()}")
