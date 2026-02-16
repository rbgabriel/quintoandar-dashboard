path = "quintoandar_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Snippet that defines df
old_df_def = """    # Toggle: ver todos os registros ou apenas os mais recentes
    show_all = st.toggle("📜 Mostrar série temporal completa", value=False, key="show_all",
                          help="Ativado: mostra TODOS os registros (mesmo imóvel repetido ao longo do tempo). Desativado: mostra apenas a captura mais recente de cada imóvel.")
    
    df = df_raw if show_all else df_latest"""

# Snippet for the sidebar header
sidebar_header = """with st.sidebar:
    st.markdown("## 🔍 Filtros")"""

# Remove old df def and insert it after sidebar header
if old_df_def in content:
    content = content.replace(old_df_def, "")
    # Cleanup trailing/leading whitespace and dividers around the old location
    content = re.sub(r'\n\s*st\.markdown\("---"\)\s*\n\s*\n\s*st\.markdown\("---"\)', '\n    st.markdown("---")', content)
    
    # Insert at top of sidebar
    new_sidebar_start = sidebar_header + "\n    " + old_df_def + "\n\n    st.markdown(\"---\")"
    content = content.replace(sidebar_header, new_sidebar_start)

# Final fix for any double dividers that might have been created
content = content.replace('st.markdown("---")\n\n    st.markdown("---")', 'st.markdown("---")')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully moved df definition to top of sidebar")
