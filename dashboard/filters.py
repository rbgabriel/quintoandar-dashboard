import streamlit as st

def init_filter_session_state(df_default, default_cidades, default_bairros, default_tipos, default_price_min, default_price_max, default_area_min, default_area_max, default_quartos):
    """Inicializa chaves do session_state necessárias para os filtros sincronizados."""
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

def update_price_slider():
    st.session_state.sel_price = (st.session_state.price_input_min, st.session_state.price_input_max)

def update_price_inputs():
    st.session_state.price_input_min = st.session_state.sel_price[0]
    st.session_state.price_input_max = st.session_state.sel_price[1]

def update_area_slider():
    st.session_state.sel_area = (st.session_state.area_input_min, st.session_state.area_input_max)

def update_area_inputs():
    st.session_state.area_input_min = st.session_state.sel_area[0]
    st.session_state.area_input_max = st.session_state.sel_area[1]

def reset_filters(default_cidades, default_bairros, default_tipos, default_price_min, default_price_max, default_area_min, default_area_max, default_quartos):
    """Reseta todos os filtros para os valores originais."""
    st.session_state["show_all"] = False
    st.session_state["sel_cidades"] = default_cidades
    st.session_state["bairro_search"] = ""
    st.session_state["sel_bairros"] = default_bairros
    st.session_state["sel_tipos"] = default_tipos
    st.session_state["price_input_min"] = default_price_min
    st.session_state["price_input_max"] = default_price_max
    st.session_state["sel_price"] = (default_price_min, default_price_max)
    st.session_state["area_input_min"] = default_area_min
    st.session_state["area_input_max"] = default_area_max
    st.session_state["sel_area"] = (default_area_min, default_area_max)
    st.session_state["sel_quartos"] = default_quartos
    st.session_state["search_id"] = ""
    st.session_state["search_bairro"] = ""
    st.session_state["search_tipo"] = ""
    st.session_state["search_endereco"] = ""
