import sys

def patch_dashboard():
    path = "quintoandar_dashboard.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Cidade to session state reset
    old_reset = """            st.session_state.update({
                "show_all": False,
                "bairro_search": "",
                "sel_bairros": default_bairros,
                "sel_tipos": default_tipos,"""
    new_reset = """            st.session_state.update({
                "show_all": False,
                "cidade_search": "",
                "sel_cidades": default_cidades,
                "bairro_search": "",
                "sel_bairros": default_bairros,
                "sel_tipos": default_tipos,"""

    # 2. Update defaults for reset
    old_defaults = """df_default = df_latest if not df_latest.empty else df_raw
default_bairros = sorted(df_default[COL_BAIRRO].dropna().unique().tolist())"""
    new_defaults = """df_default = df_latest if not df_latest.empty else df_raw
default_cidades = sorted(df_default[COL_CIDADE].dropna().unique().tolist()) if COL_CIDADE in df_default.columns else []
default_bairros = sorted(df_default[COL_BAIRRO].dropna().unique().tolist())"""

    # 3. Add City Filter in Sidebar
    old_sidebar_start = """with st.sidebar:
    st.markdown("## 🔍 Filtros")"""
    
    # We want to insert the city filter after the "Filtros" header
    new_sidebar_city = """with st.sidebar:
    st.markdown("## 🔍 Filtros")
    
    # Cidade
    cidades = sorted(df[COL_CIDADE].dropna().unique().tolist()) if COL_CIDADE in df.columns else []
    if cidades:
        sel_cidades = st.multiselect("Cidade", cidades, default=cidades, key="sel_cidades")
        st.markdown("---")
    else:
        sel_cidades = []"""

    # 4. Apply Filters logic
    old_apply_filters = """# ============================================================
# APLICAR FILTROS
# ============================================================
filtered = df[
    (df[COL_BAIRRO].isin(sel_bairros)) &
    (df['Tipo'].isin(sel_tipos)) &"""
    
    new_apply_filters = """# ============================================================
# APLICAR FILTROS
# ============================================================
# Base filter for cities
df_filtered_city = df[df[COL_CIDADE].isin(sel_cidades)] if (COL_CIDADE in df.columns and sel_cidades) else df

filtered = df_filtered_city[
    (df_filtered_city[COL_BAIRRO].isin(sel_bairros)) &
    (df_filtered_city['Tipo'].isin(sel_tipos)) &"""

    # Perform replacements
    content = content.replace(old_reset, new_reset)
    content = content.replace(old_defaults, new_defaults)
    content = content.replace(old_sidebar_start, new_sidebar_city)
    content = content.replace(old_apply_filters, new_apply_filters)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched quintoandar_dashboard.py")

if __name__ == "__main__":
    patch_dashboard()
