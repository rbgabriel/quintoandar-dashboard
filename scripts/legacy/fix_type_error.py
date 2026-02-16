path = "quintoandar_dashboard.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Initialization logic
init_logic = """
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
"""

# Insert after defaults
target = "default_quartos = sorted(df_default['Quartos'].unique().tolist())"
if target in content and "INITIALIZE SESSION STATE" not in content:
    content = content.replace(target, target + "\n" + init_logic)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully initialized session state in dashboard")
