"""Script para reorganizar dashboard com tabs"""
import os

# Ler arquivo original
with open('quintoandar_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Localizar ponto de inserção (antes de "# ============================================================\n# KPIs")
kpi_marker = "# ============================================================\n# KPIs\n# ============================================================\n"
kpi_index = content.find(kpi_marker)

if kpi_index == -1:
    print("❌ Não encontrou marker de KPIs")
    exit(1)

# Conteúdo até os KPIs (não muda)
before_kpis = content[:kpi_index]

# Conteúdo a partir dos KPIs (precisa indentar + adicionar abas antes)
from_kpis = content[kpi_index:]

# Inserir st.tabs() antes dos KPIs
tabs_code = """# ============================================================
# CRIAR ABAS
# ============================================================
tab1, tab2 = st.tabs(['📊 Dashboard', '🗺️ Mapa de Calor'])

# ============ ABA 1: DASHBOARD ============
with tab1:

    """

# Indentar everything from KPIs até o fim (adicionar 4 espaços no início de cada linha não-vazia)
indented_content = ""
for line in from_kpis.split('\n'):
    if line.strip():  # Se a linha não é vazia
        indented_content += "    " + line + "\n"
    else:
        indented_content += "\n"

# Adicionar aba de mapa
mapa_code = """

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
                # Formatar para exibição
                tabela_display = tabela_bairros.copy()
                tabela_display['Preço Min'] = tabela_display['Preço Min'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço Max'] = tabela_display['Preço Max'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço Médio'] = tabela_display['Preço Médio'].apply(lambda x: f"R$ {int(x):,}".replace(",", "."))
                tabela_display['Preço/m² Médio'] = tabela_display['Preço/m² Médio'].apply(lambda x: f"R$ {int(x):,.0f}".replace(",", "."))
                tabela_display['Área Média'] = tabela_display['Área Média'].apply(lambda x: f"{int(x):,} m²".replace(",", "."))
                tabela_display = tabela_display.rename(columns={'Imóveis': '🏠 Imóveis'})
                
                st.dataframe(
                    tabela_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Bairro": st.column_config.TextColumn("📍 Bairro", width="medium"),
                        "🏠 Imóveis": st.column_config.NumberColumn("🏠 Imóveis", format="%d"),
                        "Preço Min": st.column_config.TextColumn("Min"),
                        "Preço Max": st.column_config.TextColumn("Max"),
                        "Preço Médio": st.column_config.TextColumn("Médio"),
                        "Preço/m² Médio": st.column_config.TextColumn("R$/m²"),
                        "Área Média": st.column_config.TextColumn("Área Média"),
                        "Última Atualização": st.column_config.TextColumn("Última Atualização", width="small"),
                    }
                )
    else:
        st.warning("❌ Nenhum dado disponível com os filtros selecionados")
"""

# Juntar tudo
new_content = before_kpis + tabs_code + indented_content + mapa_code

# Salvar
with open('quintoandar_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Dashboard reorganizado com sucesso!")
print(f"Total de linhas: {len(new_content.split(chr(10)))}")
