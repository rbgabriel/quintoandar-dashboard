import pandas as pd
from bairros_zonas import BAIRROS_ZONAS_MAPPING, BAIRROS_NORMALIZATION

ZONE_MAPPING = BAIRROS_ZONAS_MAPPING
NORMALIZATION = BAIRROS_NORMALIZATION

def normalize_bairro(bairro):
    if not bairro or pd.isna(bairro):
        return "N/A"
    bairro_normalized = str(bairro).strip().lower()
    if bairro_normalized in NORMALIZATION:
        return NORMALIZATION[bairro_normalized]
    return str(bairro).strip()

def get_zone_for_bairro(bairro):
    normalized = normalize_bairro(bairro)
    for zone, bairros_list in ZONE_MAPPING.items():
        if normalized in bairros_list:
            return zone
    return "Sem zona"

# Load exactly like dashboard
df_raw = pd.read_excel('base/quintoandar_database.xlsx', dtype={'ID Imóvel': str})

# Numeric conversion
for col in ['Preço', 'Condomínio', 'Preço/m²']:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace(r'[R$\s\.]', '', regex=True).str.replace(',', ''), errors='coerce').fillna(0).astype(int)
df_raw['Área (m²)'] = pd.to_numeric(df_raw['Área (m²)'], errors='coerce').fillna(0).astype(int)
df_raw['Quartos'] = pd.to_numeric(df_raw['Quartos'], errors='coerce').fillna(0).astype(int)

# Recalculate price per m2
df_raw['Preço/m²'] = df_raw.apply(lambda r: round(r['Preço'] / r['Área (m²)'], 2) if r['Área (m²)'] > 0 else 0, axis=1)

# Normalize neighborhoods and zones
df_raw['Bairro'] = df_raw['Bairro'].apply(normalize_bairro)
df_raw['Zona'] = df_raw['Bairro'].apply(get_zone_for_bairro)

print("=== CHECKING FOR CONSOLACAO ===")
consolacao_count = len(df_raw[df_raw['Bairro'] == 'Consolação'])
print(f"Records with 'Consolação': {consolacao_count}")

# The issue: 251 vs 252
# Let's check if there are exactly 251 records that satisfy some condition
print("\n=== LOOKING FOR GROUP OF 251 RECORDS ===")

# Test: maybe it's filtering to just one zone or neighborhood?
for zona in df_raw['Zona'].unique():
    count = len(df_raw[df_raw['Zona'] == zona])
    uniq = df_raw[df_raw['Zona'] == zona]['ID Imóvel'].nunique()
    if count >= 240:
        print(f"Zona '{zona}': {count} records, {uniq} unique")

print("\n=== LOOKING FOR GROUP OF 252 ===")
for bairro in df_raw['Bairro'].unique():
    count = len(df_raw[df_raw['Bairro'] == bairro])
    uniq = df_raw[df_raw['Bairro'] == bairro]['ID Imóvel'].nunique()
    if count >= 240:
        print(f"Bairro '{bairro}': {count} records, {uniq} unique")

print("\n=== CHECK WITH DEDUP ===")
df_latest = df_raw.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last')
for bairro in df_latest['Bairro'].unique():
    count = len(df_latest[df_latest['Bairro'] == bairro])
    uniq = df_latest[df_latest['Bairro'] == bairro]['ID Imóvel'].nunique()
    if count >= 240:
        print(f"Bairro '{bairro}': {count} records, {uniq} unique")
