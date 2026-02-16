import sys

def patch_separators():
    path = "quintoandar_dashboard.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Function to replace the table formatting logic
    # We want to change the column_config and the Styler formatting
    
    old_logic = """    # Configuração de colunas para garantir ordenação numérica
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

    new_logic = """    # Configuração de colunas para garantir ordenação numérica (sem format string que força vírgula)
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

    # Formatadores BR (ponto para milhar)
    def fmt_br_val(x): 
        try: return f"R$ {int(x):,}".replace(",", ".")
        except: return str(x)
    
    def fmt_br_pm2(x):
        try: return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except: return str(x)
        
    def fmt_br_area(x):
        try: return f"{int(x):,}".replace(",", ".") + " m²"
        except: return str(x)

    def highlight_ibairro(val):
        if pd.isna(val) or val == 0: return ''
        return 'background-color: rgba(6, 214, 160, 0.3); color: #06D6A0' if val < 1 else 'background-color: rgba(255, 107, 53, 0.3); color: #FF6B35'

    # SEMPRE usar Styler para garantir a formatação visual (milhar com ponto)
    # Streamlit dataframe preserva ordenação numérica se o DF original for numérico, mesmo com Styler
    styler = display_df.style.format({
        "Preço (R$)": fmt_br_val,
        "Condomínio (R$)": fmt_br_val,
        "Preço/m² (R$)": fmt_br_pm2,
        "Área (m²)": fmt_br_area,
        "IBairro": "{:.2f}"
    }).map(highlight_ibairro, subset=['IBairro'])
    
    st.dataframe(styler, width="stretch", height=500, column_config=column_config, hide_index=True)"""

    if old_logic in content:
        content = content.replace(old_logic, new_logic)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Successfully applied thousands separator improvements")
    else:
        print("Table formatting logic not found")

if __name__ == "__main__":
    patch_separators()
