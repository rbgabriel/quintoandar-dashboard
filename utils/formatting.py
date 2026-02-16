import pandas as pd

def format_brl(value):
    """Formata valor em BRL com separador de milhares e R$ prefix.
    Ex: 1234567 -> R$ 1.234.567
    """
    if pd.isna(value) or value == 0:
        return "R$ 0"
    # Formata número completo com separador de milhares (ponto)
    formatted = f"{int(value):,}".replace(",", ".")
    return f"R$ {formatted}"

def fmt_br_currency(x):
    """Alias for format_brl, used in dataframes."""
    return format_brl(x)

def fmt_br_pm2(x):
    """Formata preço por m2 com 2 casas decimais e padrão BR.
    Ex: 1234.56 -> R$ 1.234,56
    """
    try:
        if pd.isna(x) or x == 0:
            return "R$ 0,00"
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(x)

def fmt_br_area(x):
    """Formata área com separador de milhares e sufixo m2.
    Ex: 1234 -> 1.234 m2
    """
    try:
        if pd.isna(x) or x == 0:
            return "0 m²"
        return f"{int(x):,}".replace(",", ".") + " m²"
    except:
        return str(x)
