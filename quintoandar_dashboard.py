import streamlit as st # Reloaded to fix import cache
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from mapa_calor import criar_mapa_calor, criar_tabela_bairros, criar_tabela_ruas

# New modules
from utils.formatting import format_brl, fmt_br_currency, fmt_br_pm2, fmt_br_area
from dashboard.ui_components import *
from dashboard.filters import init_filter_session_state, update_price_slider, update_price_inputs, update_area_slider, update_area_inputs, reset_filters

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except Exception:
    HAS_STATSMODELS = False

# Apply custom styles from ui_components
apply_custom_css()

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

# ============================================================
# PAGE CONFIG & HEADER
# ============================================================
st.set_page_config(
    page_title="QuintoAndar Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)
render_header(version="3.1")

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
if 'Data e Hora da Extração' in df_raw.columns:
    df_latest = df_raw.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last').copy()
else:
    df_latest = df_raw.drop_duplicates(subset=['ID Imóvel'], keep='last').copy()

# Calculate defaults for filters
df_default = df_latest
default_cidades = sorted(df_default[COL_CIDADE].dropna().unique().tolist()) if COL_CIDADE in df_default.columns else []
default_bairros = sorted(df_default[COL_BAIRRO].dropna().unique().tolist()) if COL_BAIRRO in df_default.columns else []
default_tipos = sorted(df_default['Tipo'].dropna().unique().tolist()) if 'Tipo' in df_default.columns else []
default_price_min = int(df_default['Preço'].min()) if not df_default.empty else 0
default_price_max = int(df_default['Preço'].max()) if not df_default.empty else 1000000
default_area_min = int(df_default['Área (m²)'].min()) if not df_default.empty else 0
default_area_max = int(df_default['Área (m²)'].max()) if not df_default.empty else 1000
default_quartos = sorted(df_default['Quartos'].dropna().unique().tolist()) if 'Quartos' in df_default.columns else []

# Initialize session state for filters
init_filter_session_state(df_default, default_cidades, default_bairros, default_tipos, default_price_min, default_price_max, default_area_min, default_area_max, default_quartos)

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
    
    col_reset_top = st.columns(1)[0]
    with col_reset_top:
        if st.button("🔁 Reset Filtros", use_container_width=True, key="reset_top"):
            reset_filters(default_cidades, default_bairros, default_tipos, default_price_min, default_price_max, default_area_min, default_area_max, default_quartos)
    
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
    quartos_opts = sorted(df['Quartos'].dropna().unique().tolist())
    sel_quartos = st.multiselect("Quartos", quartos_opts, default=quartos_opts, key="sel_quartos")

    st.markdown("---")
    st.caption(f"Base atualizada: {df_raw['Data e Hora da Extração'].max()}")
    st.caption(f"Imóveis únicos: {df_raw['ID Imóvel'].nunique()} | Registros totais: {len(df_raw)}")
    
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.button("🗑️ Limpar Filtros", use_container_width=True):
        reset_filters(default_cidades, default_bairros, default_tipos, default_price_min, default_price_max, default_area_min, default_area_max, default_quartos)

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
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_kpi_card("Imóveis", f"{len(filtered):,}", 'registros totais' if show_all else 'únicos')
    
    with col2:
        avg_price = filtered['Preço'].mean() if not filtered.empty else 0
        render_kpi_card("Preço Médio", format_brl(avg_price), f"mediana: {format_brl(filtered['Preço'].median()) if not filtered.empty else 'N/A'}")
    
    with col3:
        avg_pm2 = filtered['Preço/m²'].mean() if not filtered.empty else 0
        render_kpi_card("Preço/m² Médio", format_brl(avg_pm2), "por metro quadrado")
    
    with col4:
        avg_area = filtered['Área (m²)'].mean() if not filtered.empty else 0
        render_kpi_card("Área Média", f"{avg_area:.0f} m²", "média dos filtrados")
    
    with col5:
        avg_condo = filtered['Condomínio'].mean() if not filtered.empty else 0
        render_kpi_card("Condomínio Médio", format_brl(avg_condo), "encargos mensais")
    
    # 🕒 Freshness Indicator
    last_update = df_raw['Data e Hora da Extração'].max()
    st.markdown(f"""
    <div style="text-align: right; margin-top: -15px; margin-bottom: 5px;">
        <span style="color: {SUBTEXT_COLOR}; font-size: 0.8rem; background: {CARD_BG}; padding: 4px 12px; border-radius: 20px; border: 1px solid {CARD_BORDER};">
            ⏱️ Última coleta: {last_update}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    if not filtered.empty:
        chart_layout = get_chart_layout()
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### 📊 Distribuição de Preços")
            fig_hist = px.histogram(
                filtered, x='Preço', nbins=30,
                color_discrete_sequence=['#FF6B35'],
                labels={'Preço': 'Preço (R$)', 'count': 'Quantidade'}
            )
            fig_hist.update_layout(**chart_layout, showlegend=False)
            fig_hist.update_xaxes(gridcolor="#2D3139", tickformat=',.0f')
            fig_hist.update_yaxes(gridcolor="#2D3139", title='Quantidade')
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
            fig_bar.update_xaxes(gridcolor=GRID_COLOR, tickformat=',.0f')
            fig_bar.update_yaxes(gridcolor=GRID_COLOR)
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
            fig_scatter.update_xaxes(gridcolor=GRID_COLOR)
            fig_scatter.update_yaxes(gridcolor=GRID_COLOR, tickformat=',.0f')
            st.plotly_chart(fig_scatter, width="stretch")
    
    # ============================================================
    # EVOLUÇÃO TEMPORAL E COMPARAÇÃO
    # ============================================================
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    col_hist, col_comp = st.columns([1.2, 0.8])
    
    with col_hist:
        st.markdown("#### 🕒 Evolução de Preço Médio (Total)")
        # Process temporal data
        df_temporal = df_raw.copy()
        df_temporal['Data'] = pd.to_datetime(df_temporal['Data e Hora da Extração']).dt.date
        hist_data = df_temporal.groupby('Data')['Preço'].mean().reset_index()
        
        if len(hist_data) > 1:
            fig_line = px.line(
                hist_data, x='Data', y='Preço',
                color_discrete_sequence=['#FF6B35'],
                markers=True,
                labels={'Preço': 'Preço Médio (R$)', 'Data': ''}
            )
            fig_line.update_layout(**get_chart_layout(), showlegend=False)
            fig_line.update_xaxes(gridcolor=GRID_COLOR)
            fig_line.update_yaxes(gridcolor=GRID_COLOR, tickformat=',.0f')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("ℹ️ Dados históricos insuficientes para gerar o gráfico de evolução.")

    with col_comp:
        st.markdown("#### ⚖️ Comparar Bairros")
        target_bairros = st.multiselect(
            "Selecione para comparar:",
            options=sorted(df[COL_BAIRRO].dropna().unique()),
            default=sorted(filtered[COL_BAIRRO].dropna().unique())[:2] if not filtered.empty else [],
            max_selections=4,
            key="comp_bairros"
        )
        
        if target_bairros:
            comp_df = df_latest[df_latest[COL_BAIRRO].isin(target_bairros)]
            comp_stats = comp_df.groupby(COL_BAIRRO).agg({
                'Preço': 'mean',
                'Preço/m²': 'mean',
                'Área (m²)': 'mean'
            }).reset_index()
            
            # Show a small comparison table or bar chart
            fig_comp = px.bar(
                comp_stats, x=COL_BAIRRO, y='Preço/m²',
                color=COL_BAIRRO,
                color_discrete_sequence=['#FF6B35', '#FF9F1C', '#FFD166', '#06D6A0'],
                labels={'Preço/m²': 'R$/m²', COL_BAIRRO: ''}
            )
            fig_comp.update_layout(**get_chart_layout(), showlegend=False)
            fig_comp.update_yaxes(gridcolor=GRID_COLOR)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.write("Selecione bairros para visualizar a comparação de R$/m².")
    
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
    
    # Configuração de colunas para garantir ordenação numérica
    column_config = {
        "Link": st.column_config.LinkColumn("🔗 Link", display_text="Abrir"),
        "Captura": st.column_config.TextColumn("📅 Captura"),
        "ID Imóvel": st.column_config.TextColumn("🆔 ID"),
        COL_BAIRRO: st.column_config.TextColumn("📍 Bairro"),
        "Preço (R$)": st.column_config.NumberColumn("Preço"),
        "Condomínio (R$)": st.column_config.NumberColumn("Condo"),
        "Preço/m² (R$)": st.column_config.NumberColumn("R$/m²"),
        "Área (m²)": st.column_config.NumberColumn("Área"),
        "IBairro": st.column_config.NumberColumn("IBairro"),
    }

    def highlight_ibairro(val):
        if pd.isna(val) or val == 0: return ''
        return 'background-color: rgba(6, 214, 160, 0.3); color: #06D6A0' if val < 1 else 'background-color: rgba(255, 107, 53, 0.3); color: #FF6B35'

    # FORMATAÇÃO: Streamlit dataframe preserva ordenação numérica se o DF original for numérico
    styler = display_df.style.format({
        "Preço (R$)": fmt_br_currency,
        "Condomínio (R$)": fmt_br_currency,
        "Preço/m² (R$)": fmt_br_pm2,
        "Área (m²)": fmt_br_area,
        "IBairro": "{:.2f}"
    }).map(highlight_ibairro, subset=['IBairro'])
    
    st.dataframe(styler, width="stretch", height=500, column_config=column_config, hide_index=True)
    
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
            
            # --- Tabela de Bairros (Ordenação Numérica) ---
            st.markdown("---")
            st.markdown("#### 📊 Estatísticas por Bairro")
            tabela_bairros = criar_tabela_bairros(mapa_filtered)
            if tabela_bairros is not None:
                st.dataframe(
                    tabela_bairros.style.format({
                        "Preço Min": fmt_br_currency,
                        "Preço Max": fmt_br_currency,
                        "Preço Médio": fmt_br_currency,
                        "Preço/m² Médio": fmt_br_pm2,
                        "Área Média": fmt_br_area,
                    }),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Imóveis": st.column_config.NumberColumn("🏠 Imóveis"),
                        "Preço Médio": st.column_config.NumberColumn("Preço Médio"),
                    }
                )
            
            # --- Tabela de Ruas (NOVO) ---
            st.markdown("---")
            st.markdown("#### 🛣️ Top Ruas com mais imóveis (nesta seleção)")
            tabela_ruas = criar_tabela_ruas(mapa_filtered)
            if tabela_ruas is not None:
                st.dataframe(
                    tabela_ruas.style.format({
                        "Preço Médio": fmt_br_currency,
                        "Preço/m² Médio": fmt_br_pm2,
                        "Área Média": fmt_br_area,
                    }),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Imóveis": st.column_config.NumberColumn("🏠 Imóveis"),
                    }
                )
            else:
                st.info("ℹ️ Dados de endereço insuficientes para análise por rua.")
    else:
        st.warning("❌ Nenhum dado disponível com os filtros selecionados")

