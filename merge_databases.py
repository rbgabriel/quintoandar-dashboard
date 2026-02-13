import pandas as pd
import subprocess
import tempfile
import os

# Extract Brooklin data from commit 8ad0431
print("Extraindo dados do Brooklin do commit 8ad0431...")
with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
    tmp_path = tmp.name

try:
    # Get file from git and save to temp
    result = subprocess.run(
        ['git', 'show', '8ad0431:base/quintoandar_database.xlsx'],
        capture_output=True,
        check=True
    )
    with open(tmp_path, 'wb') as f:
        f.write(result.stdout)
    
    # Load both datasets
    print("Carregando dados antigos (2.206 registros)...")
    df_old = pd.read_excel('base/quintoandar_database.xlsx', dtype={'ID Imóvel': str})
    
    print("Carregando dados do Brooklin (924 registros)...")
    df_brooklin = pd.read_excel(tmp_path, dtype={'ID Imóvel': str})
    
    print(f"\nDados antigos: {len(df_old)} registros")
    print(f"Dados Brooklin: {len(df_brooklin)} registros")
    
    # Combine - manter mais recentes
    df_combined = pd.concat([df_old, df_brooklin], ignore_index=True)
    print(f"Combinados: {len(df_combined)} registros (antes dedup)")
    
    # Deduplicate - keep last (most recent)
    df_final = df_combined.sort_values('Data e Hora da Extração').drop_duplicates(
        subset=['ID Imóvel'], 
        keep='last'
    )
    
    print(f"\nApós deduplicação: {len(df_final)} registros únicos")
    print(f"Bairros: {df_final['Bairro'].nunique()}")
    
    # Save
    df_final.to_excel('base/quintoandar_database.xlsx', index=False)
    print("\n✅ Base mesclada e salva!")
    
    # Show Brooklin count
    brooklin_count = len(df_final[df_final['Bairro'].str.contains('Brooklin', case=False, na=False)])
    print(f"Brooklin: {brooklin_count} registros")
    
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
