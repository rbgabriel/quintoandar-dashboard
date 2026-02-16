import sys
import re

def patch_dashboard():
    path = "quintoandar_dashboard.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure Cidade filter is at the top of the sidebar
    # (It was already there in my last patch, but I will make sure it is consolidated)
    
    # 2. Synchronize Price Sliders and Inputs
    # We need to change how the price_input and sel_price interact.
    # We will use on_change callbacks or just direct session state mapping.
    
    sync_logic = """
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
"""

    if "def update_price_slider():" not in content:
        # Insert before the sidebar section
        content = content.replace("# SIDEBAR — FILTROS", sync_logic + "\n# SIDEBAR — FILTROS")

    # Update the sidebar UI for sync
    old_price_ui = """        with col_price1:
            price_input_min = st.number_input("Preço Min (R$)", value=price_min, min_value=price_min, max_value=price_max, step=10000, key="price_input_min")
        with col_price2:
            price_input_max = st.number_input("Preço Max (R$)", value=price_max, min_value=price_min, max_value=price_max, step=10000, key="price_input_max")
        sel_price = st.slider(
            "Ajuste com slider:",
            min_value=price_min, max_value=price_max,
            value=(price_input_min, price_input_max), step=10000, format="R$ %d", key="sel_price"
        )"""

    new_price_ui = """        with col_price1:
            st.number_input("Preço Min (R$)", value=price_min, min_value=price_min, max_value=price_max, step=10000, key="price_input_min", on_change=update_price_slider)
        with col_price2:
            st.number_input("Preço Max (R$)", value=price_max, min_value=price_min, max_value=price_max, step=10000, key="price_input_max", on_change=update_price_slider)
        st.slider(
            "Ajuste com slider:",
            min_value=price_min, max_value=price_max,
            key="sel_price", step=10000, format="R$ %d", on_change=update_price_inputs
        )
        sel_price = st.session_state.sel_price"""

    old_area_ui = """        with col_area1:
            area_input_min = st.number_input("Área Min (m²)", value=area_min, min_value=area_min, max_value=area_max, step=5, key="area_input_min")
        with col_area2:
            area_input_max = st.number_input("Área Max (m²)", value=area_max, min_value=area_min, max_value=area_max, step=5, key="area_input_max")
        sel_area = st.slider("Ajuste com slider:", min_value=area_min, max_value=area_max, value=(area_input_min, area_input_max), step=5, key="sel_area")"""

    new_area_ui = """        with col_area1:
            st.number_input("Área Min (m²)", value=area_min, min_value=area_min, max_value=area_max, step=5, key="area_input_min", on_change=update_area_slider)
        with col_area2:
            st.number_input("Área Max (m²)", value=area_max, min_value=area_min, max_value=area_max, step=5, key="area_input_max", on_change=update_area_slider)
        st.slider("Ajuste com slider:", min_value=area_min, max_value=area_max, key="sel_area", step=5, on_change=update_area_inputs)
        sel_area = st.session_state.sel_area"""

    content = content.replace(old_price_ui, new_price_ui)
    content = content.replace(old_area_ui, new_area_ui)

    # 3. Fix Numerical Sorting
    # Remove the manual string formatting in display_df and use NumberColumn config
    
    old_table_formatting = """    if len(display_df) > 1000:
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
            \"\"\"Colorir IBairro: verde se < 1, vermelho se >= 1\"\"\"
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
        }).map(lambda val: highlight_ibairro(val) if True else '', subset=['IBairro'])
        
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
        )"""

    new_table_formatting = """    # Configuração de colunas para garantir ordenação numérica
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
        st.dataframe(display_df, width="stretch", height=500, column_config=column_config, hide_index=True)"""

    content = content.replace(old_table_formatting, new_table_formatting)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched dashboard with improvements")

if __name__ == "__main__":
    patch_dashboard()
