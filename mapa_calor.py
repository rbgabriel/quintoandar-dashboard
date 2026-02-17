"""Módulo para criar o mapa de calor dos bairros de São Paulo.

Usa plotly.express.scatter_mapbox com OpenStreetMap (sem token).
"""

import pandas as pd
import plotly.express as px
from bairro_coordinates import BAIRRO_COORDINATES

# Centro de São Paulo para o mapa
SP_CENTER = {"lat": -23.5605, "lon": -46.6533}
SP_ZOOM = 11


def criar_mapa_calor(df: pd.DataFrame):
    """Cria mapa interativo com bolhas coloridas por preço médio do bairro.

    Args:
        df: DataFrame com colunas 'Bairro', 'Preço', 'Área (m²)', 'Preço/m²'.

    Returns:
        plotly.graph_objects.Figure ou None se não houver dados.
    """
    if df.empty:
        return None

    # --- agregar por bairro ---
    agg = (
        df.groupby("Bairro")
        .agg(
            preco_medio=("Preço", "mean"),
            pm2_medio=("Preço/m²", "mean"),
            area_media=("Área (m²)", "mean"),
            qtd=("Preço", "count"),
        )
        .reset_index()
    )

    # --- coordenadas ---
    agg["lat"] = agg["Bairro"].map(lambda b: BAIRRO_COORDINATES.get(b, (None, None))[0])
    agg["lon"] = agg["Bairro"].map(lambda b: BAIRRO_COORDINATES.get(b, (None, None))[1])
    agg = agg.dropna(subset=["lat", "lon"])

    if agg.empty:
        return None

    # --- tamanho proporcional à quantidade de imóveis ---
    agg["size"] = agg["qtd"].clip(lower=3, upper=300)

    # --- tooltip formatado ---
    agg["hover"] = agg.apply(
        lambda r: (
            f"<b>{r['Bairro']}</b><br>"
            f"Preço Médio: R$ {r['preco_medio']:,.0f}<br>"
            f"Preço/m²: R$ {r['pm2_medio']:,.0f}<br>"
            f"Área Média: {r['area_media']:.0f} m²<br>"
            f"Imóveis: {int(r['qtd'])}"
        ),
        axis=1,
    )

    # --- mapa ---
    fig = px.scatter_mapbox(
        agg,
        lat="lat",
        lon="lon",
        color="preco_medio",
        size="size",
        hover_name="Bairro",
        hover_data={
            "lat": False,
            "lon": False,
            "size": False,
            "hover": False,
            "preco_medio": ":,.0f",
            "pm2_medio": ":,.0f",
            "area_media": ":.0f",
            "qtd": True,
        },
        color_continuous_scale="RdYlGn_r",
        size_max=30,
        zoom=SP_ZOOM,
        center=SP_CENTER,
        mapbox_style="carto-darkmatter",
        labels={
            "preco_medio": "Preço Médio (R$)",
            "pm2_medio": "Preço/m²",
            "area_media": "Área Média",
            "qtd": "Imóveis",
        },
    )

    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(14,17,23,0)",
        font=dict(color="#FAFAFA", family="Inter, sans-serif"),
        coloraxis_colorbar=dict(
            title="Preço Médio",
            thickness=15,
            len=0.65,
        ),
    )

    return fig


def criar_tabela_bairros(df: pd.DataFrame):
    """Retorna DataFrame com estatísticas agregadas por bairro (valores numéricos)."""
    if df.empty:
        return None

    stats = (
        df.groupby("Bairro")
        .agg(
            Imóveis=("ID Imóvel", "nunique"),
            **{
                "Preço Min": ("Preço", "min"),
                "Preço Max": ("Preço", "max"),
                "Preço Médio": ("Preço", "mean"),
                "Preço/m² Médio": ("Preço/m²", "mean"),
                "Área Média": ("Área (m²)", "mean"),
            },
        )
        .round(2)
        .reset_index()
        .sort_values("Preço Médio", ascending=False)
    )

    return stats


def criar_tabela_ruas(df: pd.DataFrame):
    """Retorna DataFrame com estatísticas agregadas por rua."""
    if df.empty:
        return None

    # Tenta extrair o nome da rua (tudo antes da primeira vírgula ou hífen no endereço)
    def extrair_rua(addr):
        if not isinstance(addr, str): return "N/A"
        # Remove números e complementos comuns da rua para agrupar melhor
        rua = addr.split(',')[0].split(' - ')[0].strip()
        return rua

    df_ruas = df.copy()
    df_ruas['Rua'] = df_ruas['Endereço'].apply(extrair_rua)

    stats = (
        df_ruas.groupby("Rua")
        .agg(
            Imóveis=("ID Imóvel", "nunique"),
            **{
                "Preço Médio": ("Preço", "mean"),
                "Preço/m² Médio": ("Preço/m²", "mean"),
                "Área Média": ("Área (m²)", "mean"),
            },
        )
        .round(2)
        .reset_index()
        .sort_values("Imóveis", ascending=False)
    )

    return stats.head(20) # Retorna as top 20 ruas
