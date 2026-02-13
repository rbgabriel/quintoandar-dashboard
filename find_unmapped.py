import pandas as pd
from bairros_zonas import BAIRROS_ZONAS_MAPPING, BAIRROS_NORMALIZATION

ZONE_MAPPING = BAIRROS_ZONAS_MAPPING
NORMALIZATION = BAIRROS_NORMALIZATION

def normalize_bairro(b):
    bn = str(b).strip().lower()
    return NORMALIZATION.get(bn, str(b).strip())

def get_zone(b):
    n = normalize_bairro(b)
    return next((z for z, bl in ZONE_MAPPING.items() if n in bl), 'Sem zona')

df = pd.read_excel('base/quintoandar_database.xlsx')
df['Bairro_norm'] = df['Bairro'].apply(normalize_bairro)
df['Zona'] = df['Bairro'].apply(get_zone)

sem_zona = df[df['Zona'] == 'Sem zona']
print('Bairros SEM zona mapeada:')
print(sem_zona['Bairro_norm'].value_counts())
