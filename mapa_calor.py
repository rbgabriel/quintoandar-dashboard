"""Módulo para criar o mapa de calor dos bairros de São Paulo"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from bairro_coordinates import BAIRRO_COORDINATES


def criar_mapa_calor(df):
    """
    Cria um mapa de calor (scatter geográfico) dos bairros com preços médios.
    
    Args:
        df: DataFrame com dados dos imóveis (deve ter 'Bairro' e 'Preço')
    
    Returns:
        figura Plotly
    """
    if df.empty:
        st.warning("❌ Nenhum dado disponível para o mapa")
        return None
    
    # Calcular preço médio por bairro
    preco_por_bairro = df.groupby('Bairro').agg({
        'Preço': ['mean', 'count'],
        'Área (m²)': 'mean',
        'Preço/m²': 'mean'
    }).round(2)
    
    preco_por_bairro.columns = ['Preço Médio', 'Quantidade', 'Área Média', 'Preço/m² Médio']
    preco_por_bairro = preco_por_bairro.reset_index()
    
    # Adicionar coordenadas
    preco_por_bairro['lat'] = preco_por_bairro['Bairro'].map(lambda x: BAIRRO_COORDINATES.get(x, (0, 0))[0])
    preco_por_bairro['lon'] = preco_por_bairro['Bairro'].map(lambda x: BAIRRO_COORDINATES.get(x, (0, 0))[1])
    
    # Filtrar bairros com coordenadas válidas
    preco_por_bairro = preco_por_bairro[(preco_por_bairro['lat'] != 0) | (preco_por_bairro['lon'] != 0)]
    
    if preco_por_bairro.empty:
        st.warning("❌ Nenhum bairro com coordenadas encontrado")
        return None
    
    # Normalizar Preço Médio para escala de cor (0-100)
    preco_min = preco_por_bairro['Preço Médio'].min()
    preco_max = preco_por_bairro['Preço Médio'].max()
    preco_por_bairro['Color'] = ((preco_por_bairro['Preço Médio'] - preco_min) / (preco_max - preco_min)) * 100
    
    # Criar figura Plotly
    fig = go.Figure()
    
    # Adicionar scatter plot
    fig.add_trace(go.Scattergeo(
        mode='markers',
        lon=preco_por_bairro['lon'],
        lat=preco_por_bairro['lat'],
        marker=dict(
            size=preco_por_bairro['Quantidade'].apply(lambda x: max(8, min(25, x / 5))),  # Tamanho baseado em quantidade
            color=preco_por_bairro['Color'],
            colorscale='RdYlGn_r',  # Vermelho (caro) a Verde (barato)
            showscale=True,
            colorbar=dict(
                title="Preço Médio<br>(%)  ",
                thickness=15,
                len=0.7,
                x=1.02
            ),
            line=dict(width=1, color='rgba(255, 255, 255, 0.5)'),
            opacity=0.8
        ),
        text=[
            f"<b>{bairro}</b><br>" +
            f"Preço Médio: R$ {preco:,.0f}<br>" +
            f"Preço/m²: R$ {pm2:,.0f}<br>" +
            f"Área Média: {area:.0f} m²<br>" +
            f"Imóveis: {qty:.0f}"
            for bairro, preco, pm2, area, qty in zip(
                preco_por_bairro['Bairro'],
                preco_por_bairro['Preço Médio'],
                preco_por_bairro['Preço/m² Médio'],
                preco_por_bairro['Área Média'],
                preco_por_bairro['Quantidade']
            )
        ],
        hovertemplate='%{text}<extra></extra>',
        name=''
    ))
    
    # Atualizar layout
    fig.update_layout(
        title={
            'text': '🗺️ Mapa de Calor - Preços Médios por Bairro',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#FAFAFA'}
        },
        geo=dict(
            scope='south america',
            projection_type='mercator',
            center=dict(lat=-23.55, lon=-46.65),
            fitbounds='locations',
            showland=True,
            landcolor='rgba(50, 50, 50, 0.2)',
            showocean=True,
            oceancolor='rgba(20, 20, 50, 0.1)',
            showlakes=True,
            lakecolor='rgba(20, 20, 50, 0.1)',
            coastcolor='rgba(100, 100, 100, 0.3)',
            countrycolor='rgba(100, 100, 100, 0.3)',
            showframe=False,
            bgcolor='rgba(14, 17, 23, 0)'
        ),
        hovermode='closest',
        width=None,
        height=700,
        paper_bgcolor='rgba(14, 17, 23, 0)',
        plot_bgcolor='rgba(14, 17, 23, 0)',
        font=dict(color='#FAFAFA', family='Inter, sans-serif'),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig


def criar_tabela_bairros(df):
    """
    Cria uma tabela com estatísticas dos bairros.
    
    Args:
        df: DataFrame com dados dos imóveis
    
    Returns:
        DataFrame formatado para visualização
    """
    if df.empty:
        return None
    
    stats_bairros = df.groupby('Bairro').agg({
        'ID Imóvel': 'nunique',
        'Preço': ['min', 'max', 'mean'],
        'Preço/m²': 'mean',
        'Área (m²)': 'mean',
        'Data e Hora da Extração': 'max'
    }).round(2)
    
    stats_bairros.columns = ['Imóveis', 'Preço Min', 'Preço Max', 'Preço Médio', 'Preço/m² Médio', 'Área Média', 'Última Atualização']
    stats_bairros = stats_bairros.reset_index().sort_values('Preço Médio', ascending=False)
    
    return stats_bairros
