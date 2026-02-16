import pandas as pd
import os

DATA_PATH = os.path.join("base", "quintoandar_database.xlsx")

def migrate():
    if not os.path.exists(DATA_PATH):
        print(f"File not found: {DATA_PATH}")
        return

    print(f"Loading {DATA_PATH}...")
    df = pd.read_excel(DATA_PATH, dtype={'ID Imóvel': str})
    
    # Normalize 'Cidade' column
    if 'Cidade' not in df.columns and 'Cidade de Busca' in df.columns:
        df = df.rename(columns={'Cidade de Busca': 'Cidade'})
        print("Renamed 'Cidade de Busca' to 'Cidade'")
    elif 'Cidade' not in df.columns:
        df['Cidade'] = "São Paulo"
        print("Created 'Cidade' column")
    
    # Fill all records with 'São Paulo' as requested
    original_cities = df['Cidade'].unique()
    print(f"Original cities found: {original_cities}")
    
    df['Cidade'] = "São Paulo"
    print("Set all records 'Cidade' to 'São Paulo'")

    # Save
    try:
        df.to_excel(DATA_PATH, index=False)
        print(f"Successfully migrated {len(df)} records.")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    migrate()
