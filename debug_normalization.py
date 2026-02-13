import pandas as pd
from bairros_zonas import BAIRROS_ZONAS_MAPPING, BAIRROS_NORMALIZATION

ZONE_MAPPING = BAIRROS_ZONAS_MAPPING
NORMALIZATION = BAIRROS_NORMALIZATION

def normalize_bairro(bairro):
    """Normaliza nome do bairro (remove variacoes e inconsistencias)"""
    if not bairro or pd.isna(bairro):
        return "N/A"
    
    bairro_normalized = str(bairro).strip().lower()
    
    # Verificar se ha mapeamento especifico
    if bairro_normalized in NORMALIZATION:
        return NORMALIZATION[bairro_normalized]
    
    # Se nao tiver mapeamento, retornar o bairro original com primeira letra maiuscula
    return str(bairro).strip()

def get_zone_for_bairro(bairro):
    """Obtem a zona (Zona Sul, Norte, Leste, Oeste, Centro) para um bairro"""
    normalized = normalize_bairro(bairro)
    
    for zone, bairros_list in ZONE_MAPPING.items():
        if normalized in bairros_list:
            return zone
    
    return "Sem zona"

# Load data
df = pd.read_excel('base/quintoandar_database.xlsx', dtype={'ID Imóvel': str})

print("=== BEFORE NORMALIZATION ===")
print(f"Unique Bairros: {df['Bairro'].nunique()}")
print(f"Bairro values with 'Guarani':")
print(df[df['Bairro'].str.contains('Guarani', case=False, na=False)]['Bairro'].value_counts())

# Apply normalization
df['Bairro'] = df['Bairro'].apply(normalize_bairro)
df['Zona'] = df['Bairro'].apply(get_zone_for_bairro)

print("\n=== AFTER NORMALIZATION ===")
print(f"Unique Bairros: {df['Bairro'].nunique()}")
print(f"Bairro values with 'Guarani':")
print(df[df['Bairro'].str.contains('Guarani', case=False, na=False)]['Bairro'].value_counts())

# Show final stats
print("\n=== FINAL DATA STATS ===")
print(f"Total records: {len(df)}")
print(f"Unique properties (ID): {df['ID Imóvel'].nunique()}")

# After dedup (like the dashboard does)
df_latest = df.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last')
print(f"After dedup (latest per property): {len(df_latest)}")
print(f"Unique IDs in dedup: {df_latest['ID Imóvel'].nunique()}")
