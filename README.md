# 🏠 QuintoAndar Dashboard

Dashboard interativo para análise de imóveis à venda no QuintoAndar.

## 📊 Features

- **KPIs**: Total de imóveis, Preço médio, Preço/m², Área média, Condomínio médio
- **Filtros**: Bairro, Tipo, Faixa de preço, Área, Quartos
- **Gráficos**: Distribuição de preços, Preço/m² por bairro, Tipos de imóvel, Preço vs Área
- **Tabela**: Listagem completa com links diretos para o QuintoAndar

## 🚀 Como Usar

### Local
```
pip install -r requirements.txt
streamlit run quintoandar_dashboard.py
```

### Streamlit Cloud
1. Faça fork/clone deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório GitHub
4. Deploy automático!

## 📁 Estrutura

```
├── quintoandar_dashboard.py   # Dashboard principal
├── quintoandar_scraper.py     # Scraper de dados
├── requirements.txt           # Dependências Python
├── .streamlit/
│   └── config.toml            # Tema escuro customizado
└── base/
    └── quintoandar_database.xlsx  # Dados extraídos
```

## 🛠️ Stack

- **Streamlit** — Interface interativa
- **Plotly** — Gráficos dinâmicos
- **Pandas** — Processamento de dados
- **undetected-chromedriver** — Scraping (apenas local)
