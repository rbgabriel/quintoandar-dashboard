import pandas as pd

df = pd.read_excel('base/quintoandar_database.xlsx', dtype={'ID Imóvel': str})
df_latest = df.sort_values('Data e Hora da Extração').drop_duplicates(subset=['ID Imóvel'], keep='last')

print('=== Dashboard Data Summary ===')
print(f'Total records in file: {len(df)}')
print(f'Unique properties: {df["ID Imóvel"].nunique()}')
print(f'After dedup (default view): {len(df_latest)}')
print(f'\nTop 5 Cities:')
print(df_latest['Cidade'].value_counts().head())
print(f'\nTop 10 Neighborhoods:')
print(df_latest['Bairro'].value_counts().head(10))
