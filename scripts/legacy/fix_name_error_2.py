path = "quintoandar_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Snippet to search and move
toggle_snippet = """    # Toggle: ver todos os registros ou apenas os mais recentes
    show_all = st.toggle("📜 Mostrar série temporal completa", value=False, key="show_all",
                          help="Ativado: mostra TODOS os registros (mesmo imóvel repetido ao longo do tempo). Desativado: mostra apenas a captura mais recente de cada imóvel.")
    
    df = df_raw if show_all else df_latest
    
    st.markdown("---")"""

sidebar_header = """with st.sidebar:
    st.markdown("## 🔍 Filtros")"""

if toggle_snippet in content:
    content = content.replace(toggle_snippet, "")
    # Cleanup any extra whitespace left behind
    content = content.replace('\n    \n    # Bairro (com busca)', '\n    # Bairro (com busca)')
    
    # Insert at top of sidebar
    new_sidebar_start = sidebar_header + "\n\n" + toggle_snippet
    content = content.replace(sidebar_header, new_sidebar_start)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully moved df definition to top of sidebar")
