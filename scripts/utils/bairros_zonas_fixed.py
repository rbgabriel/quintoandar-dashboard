# Mapping de bairros para zonas de Sao Paulo
# Baseado no zoneamento oficial da cidade

BAIRROS_ZONAS_MAPPING = {
    "Zona Centro": [
        "Centro", "Consolacao", "Republica", "Bom Retiro", "Bras",
        "Cambuci", "Pari", "Santa Cecilia", "Se", "Tatuape",
        "Belenzinho", "Campos Eliseos", "Higienopolis"
    ],
    "Zona Sul": [
        "Aclimaçao", "Bela Vista", "Cambuci", "Consolacao", "Imirim",
        "Ipiranga", "Jabaquara", "Jardim Paulista", "Parque Jabaquara",
        "Vila Andrade", "Vila Guarani", "Vila Monte Alegre", "Vila Pita",
        "Vila Sonia", "Vila Santa Catarina", "Macedo", "Santo Amaro",
        "Saude", "Cursino", "Congonhas", "Morumbi", "Fazenda Morumbi",
        "Moinho Velho", "Cupece", "Sacomã", "Quarta Parada", "Vila Mariana",
        "Cidade Vargas", "Vila Re", "Cidade Antonio Estevao", "Vila Firmiano Pinto",
        "Vila Parque Jabaquara"
    ],
    "Zona Norte": [
        "Barra Funda", "Brasilandia", "Cachoeirinha", "Casa Verde",
        "Freguesia do O", "Horto Florestal", "Jacana", "Jaragua", "Perus",
        "Pirituba", "Sao Domingos", "Tremembe", "Tucuruvi", "Vila Curuça",
        "Vila Gilda", "Vila Guilherme", "Vila Mariana", "Vila Medeiros",
        "Vila Nova Cachoeirinha", "Vila Pirituba"
    ],
    "Zona Leste": [
        "Agua Rasa", "Analia Franco", "Artur Alvim", "Belem", "Bras",
        "Carrao", "Cidade Patriarca", "Ciguera", "Ermelino Matarazzo",
        "Guaianazes", "Itaquera", "Jardim Iguatemi", "Jardim Oriental",
        "Jardim Vila Formosa", "Lajeado", "Maia", "Mooca", "Parque Doria",
        "Penha", "Ponte Rasa", "Sapopemba", "Sao Lucas", "Sao Mateus",
        "Tatuape", "Terra da Esperança", "Parque Marajoara", "Vila Carbone",
        "Vila Curuça", "Vila Futura", "Vila Matilde", "Vila Re", "Vila Mazzei",
        "Maranhao", "Jardim Marajoara", "Agua Fria", "Vila Santa Clara",
        "Vila Campanela", "Jardim Iris", "Vila Formosa", "Jardim Vergueiro",
        "Jardim Santa Emilia", "Alto da Mooca"
    ],
    "Zona Oeste": [
        "Alto da Lapa", "Alto de Pinheiros", "Anhanguera", "Bairro da Esperança",
        "Bom Retiro", "Butanta", "Cotia", "Jaguare", "Jardim Paulista", "Lapa",
        "Perdizes", "Pinheiros", "Pompeia", "Raposo Tavares", "Santo Amaro",
        "Sao Conrado", "Vila Leopoldina", "Vila Mariana", "Vila Madalena",
        "Vila Sonia", "Rio Pequeno", "Previdencia", "Vila Mineira",
        "Conjunto Residencial Butanta", "Jardim Sao Saverio", "Jardim Umarizal"
    ]
}

# Normalizacao de nomes de bairros (variacoes e acentos)
BAIRROS_NORMALIZATION = {
    # Vila Guarani variations
    "vila guarani (z sul)": "Vila Guarani",
    "vila guarani (zona sul)": "Vila Guarani",
    "vila guarani": "Vila Guarani",
    
    # Consolidation with and without accents
    "consolacao": "Consolacao",
    "consolação": "Consolacao",
    "bela vista": "Bela Vista",
    "jardim oriental": "Jardim Oriental",
    "jabaquara": "Jabaquara",
    "vila monte alegre": "Vila Monte Alegre",
    "tatuape": "Tatuape",
    "tatuapé": "Tatuape",
    "parque jabaquara": "Parque Jabaquara",
    "vila pita": "Vila Pita",
    "vila sonia": "Vila Sonia",
    "vila sônia": "Vila Sonia",
    "vila santa catarina": "Vila Santa Catarina",
    "vila andrade": "Vila Andrade",
    "jardim vila formosa": "Jardim Vila Formosa",
    "maranhao": "Maranhao",
    "maranhão": "Maranhao",
    "cidade antonio estevao": "Cidade Antonio Estevao",
    "cidade antônio estêvão": "Cidade Antonio Estevao",
    "cidade antônio estêvão de carvalho": "Cidade Antonio Estevao",
    "conjunto residencial i": "Conjunto Residencial I",
    "conjunto residencial butanta": "Conjunto Residencial Butanta",
    
    # Additional single entries
    "santa cecilia": "Santa Cecilia",
    "santa cecília": "Santa Cecilia",
    "tremembé": "Tremembe",
    "república": "Republica",
    "centro": "Centro",
    "higienópolis": "Higienopolis",
    "campos elíseos": "Campos Eliseos",
    "belenzinho": "Belenzinho",
    "agua fria": "Agua Fria",
    "água fria": "Agua Fria",
    "vila mazzei": "Vila Mazzei",
    "jardim marajoara": "Jardim Marajoara",
    "vila parque jabaquara": "Vila Parque Jabaquara",
    "vila campanela": "Vila Campanela",
    "cupecê": "Cupece",
    "sacomã": "Sacomã",
    "quarta parada": "Quarta Parada",
    "jardim vergueiro": "Jardim Vergueiro",
    "jardim vergueiro (sacomã)": "Jardim Vergueiro",
    "jardim santa emilia": "Jardim Santa Emilia",
    "alto da mooca": "Alto da Mooca",
    "vila ré": "Vila Re",
    "moinho velho": "Moinho Velho",
    "fazenda morumbi": "Fazenda Morumbi",
    "jardim são savério": "Jardim Sao Saverio",
    "jardim iris": "Jardim Iris",
    "vila polopoli": "Vila Polopoli",
    "colônia (zona leste)": "Colonia Zona Leste",
    "terra da esperança": "Terra da Esperança",
}
