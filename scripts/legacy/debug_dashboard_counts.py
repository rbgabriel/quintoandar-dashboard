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

# Apply normalization
df_raw['Bairro'] = df_raw['Bairro'].apply(normalize_bairro)
df_raw['Zona'] = df_raw['Bairro'].apply(get_zone_for_bairro)

print("=== RAW DATA ===")
print(f"Total in df_raw: {len(df_raw)}")
print(f"Unique IDs in df_raw: {df_raw['ID Imóvel'].nunique()}")

# Default mode (show_all = False)
df_latest = df_raw.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last')

print("\n=== AFTER DEDUP (Default view) ===")
print(f"Total in df_latest: {len(df_latest)}")
print(f"Unique IDs in df_latest: {df_latest['ID Imóvel'].nunique()}")

# Simulate NO filters applied (all defaults selected)
df = df_latest  # Using dedup version

print("\n=== WITH NO FILTERS (simulating dashboard default) ===")
print(f"len(filtered) would show: {len(df)}")
print(f"filtered['ID Imóvel'].nunique() would show: {df['ID Imóvel'].nunique()}")

# Check for duplicates
print("\n=== CHECKING FOR DUPLICATES ===")
duplicates = df[df.duplicated(subset=['ID Imóvel'], keep=False)]
print(f"Rows with duplicate IDs in df_latest: {len(duplicates)}")
if len(duplicates) > 0:
    print("Duplicate IDs found:")
    print(duplicates[['ID Imóvel', 'Endereço', 'Data e Hora da Extração']].sort_values('ID Imóvel'))
