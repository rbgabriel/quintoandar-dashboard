# Mapping de bairros para zonas de Sao Paulo
# Baseado no zoneamento oficial da cidade

BAIRROS_ZONAS_MAPPING = {
    "Zona Centro": [
        "Centro", "Consolacao", "Republica", "Bom Retiro", "Bras",
        "Cambuci", "Pari", "Santa Cecilia", "Se", "Tatuape"
    ],
    "Zona Sul": [
        "Aclimaçao", "Bela Vista", "Cambuci", "Consolacao", "Imirim",
        "Ipiranga", "Jabaquara", "Jardim Paulista", "Parque Jabaquara",
        "Vila Andrade", "Vila Guarani", "Vila Monte Alegre", "Vila Pita",
        "Vila Sonia", "Vila Santa Catarina", "Macedo", "Santo Amaro",
        "Saude", "Cursino", "Congonhas"
    ],
    "Zona Norte": [
        "Barra Funda", "Brasilandia", "Cachoeirinha", "Casa Verde",
        "Freguesia do O", "Horto Florestal", "Jacana", "Jaragua", "Perus",
        "Pirituba", "Sao Domingos", "Tremembe", "Tucuruvi", "Vila Curuçá",
        "Vila Gilda", "Vila Guilherme", "Vila Mariana", "Vila Medeiros",
        "Vila Nova Cachoeirinha"
    ],
    "Zona Leste": [
        "Agua Rasa", "Analia Franco", "Artur Alvim", "Belem", "Bras",
        "Carrao", "Cidade Patriarca", "Ciguera", "Ermelino Matarazzo",
        "Guaianazes", "Itaquera", "Jardim Iguatemi", "Jardim Oriental",
        "Jardim Vila Formosa", "Lajeado", "Maia", "Mooca", "Parque Doria",
        "Penha", "Ponte Rasa", "Sapopemba", "Sao Lucas", "Sao Mateus",
        "Tatuape", "Terra da Esperança", "Parque Marajoara", "Vila Carbone",
        "Vila Curuçá", "Vila Futura", "Vila Matilde", "Vila Re"
    ],
    "Zona Oeste": [
        "Alto da Lapa", "Alto de Pinheiros", "Anhanguera", "Bairro da Esperança",
        "Bom Retiro", "Butanta", "Cotia", "Jaguare", "Jardim Paulista", "Lapa",
        "Perdizes", "Pinheiros", "Pompeia", "Raposo Tavares", "Santo Amaro",
        "Sao Conrado", "Vila Leopoldina", "Vila Mariana", "Vila Madalena",
        "Vila Sonia", "Morumbi", "Rio Pequeno", "Previdencia", "Vila Mineira"
    ]
}

# Normalizacao de nomes de bairros (variacoes)
BAIRROS_NORMALIZATION = {
    "vila guarani (z sul)": "Vila Guarani",
    "vila guarani (zona sul)": "Vila Guarani",
    "vila guarani (zona sul)": "Vila Guarani",
    "vila guarani": "Vila Guarani",
    "consolacao": "Consolacao",
    "bela vista": "Bela Vista",
    "jardim oriental": "Jardim Oriental",
    "jabaquara": "Jabaquara",
    "vila monte alegre": "Vila Monte Alegre",
    "tatuape": "Tatuape",
    "parque jabaquara": "Parque Jabaquara",
    "vila pita": "Vila Pita",
    "vila sonia": "Vila Sonia",
    "vila santa catarina": "Vila Santa Catarina",
    "vila andrade": "Vila Andrade",
    "jardim vila formosa": "Jardim Vila Formosa",
    "maranhao": "Maranhao",
    "cidade antonio estevao": "Cidade Antonio Estevao",
    "conjunto residencial i": "Conjunto Residencial I"
}
