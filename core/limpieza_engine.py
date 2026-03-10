import re

# Diccionario de corrección fonética
DICCIONARIO_PRONUNCIACION = {
    "InsightdataMind": "In-sait-data-maind",
    "TikTok": "Tik Tok",
    "Youtube": "Yutub",
    "Shorts": "Shorts",
    "Google": "Gúgol",
    "Friends": "Frends",
    "Central Perk": "Céntral Pérk",
    "Perk": "Pérk",
    "sitcom": "sítcom",
    "Rachel Green": "Réichel Grín",
    "Joey Tribbiani": "Yóui Tribiani",
    "Chandler Bing": "Chándler Bing",
    "Phoebe Buffay": "Fibi Bu-féy",
    "Ross Geller": "Ross Guéler",
    "Monica": "Mónica",
    "Chandler": "Chándler",
    "Ross": "Ross",
    "Joey": "Ióui",
    "Phoebe": "Fibi",
    "Jennifer Aniston": "Yénifer Aniston",
    "Courteney Cox": "Córtni Cócs",
    "Matthew Perry": "Máthiu Péri",
    "Matt LeBlanc": "Mat Le-blanc",
    "David Schwimmer": "Déivid Shuímer",
    "Lisa Kudrow": "Lisa Kúdrou",
    "Gunther": "Gánter",
    "Bruce Willis": "Brús Gúilis",
    "Greg Grande": "Greg Gránde",
    "Warner Bros": "Uárner Bros",
    "Warner Brothers": "Uárner Bróders",
    "Burbank": "Bér-bank",
    "Insomnia Cafe": "Insómnia Cafey",
    "Friends Like Us": "Frends Láic Ás",
    "set": "set",
    "velvet": "vélvet",
    "vintage": "víntash",
    "terciopelo": "terciopelo",
    "mirilla": "mi-ri-lla",
    "apartamento": "aparta-mento",
    "Schrodinger": "Schrodin-guer",
    "Schrödinger": "Schrodin-guer",
    "Richard Feynman": "Richard Fain-man",
    "Feynman": "Fain-man",
    "Planck": "Plank",
    "Einstein": "Ainstain",
    "Efecto Casimir": "Efecto Cásimir",
    "Event Boundary": "Ivent Baundari",
    "Uncanny Valley": "An-kani Vali",
    "Salish Sea": "Seilish Si",
    "Malaysia Airlines": "Maleisia Er-lains",
    "Inmarsat": "In-mar-sat",
    "Voynich": "Voinich",
    "Geosmina": "Geos-mina",
    "Photorhabdus": "Fotorab-dus",
    "luminescens": "luminesens",
    "cuánticos": "cuánticos",
    "cuántica": "cuántica",
    "cuántico": "cuántico",
    "Entrelazamiento": "Entre-lazamiento",
    "holográfico": "olo-gráfico",
    "holográfica": "olo-gráfica",
    "residual": "re-sidual",
    "nanotecnología": "nano-tecnología",
    "centímetro cúbico": "centímetro cúbico",
    "vial": "vial",
    "Santo Grial": "Santo Grial",
    "nebulosa": "nebulosa",
    "Harry Potter": "Jarry Poter",
    "Snape": "Sneip",
    "Dumbledore": "Damboldor",
    "Voldemort": "Voldemor",
    "Hallows": "Jalows",
    "Hogwarts": "Jogwarts",
    "Hermione": "Jermayoni",
    "Quidditch": "Quidich",
    "Grindelwald": "Grindeluald",
    "Gryffindor": "Grifindor",
    "Tolkien": "Tolkin",
    "Smaug": "Smog",
    "Gollum": "Golum",
    "Skywalker": "Scaiguolquer",
    "Darth Vader": "Dart Veider",
    "Jedi": "Yedai",
    "Lightsaber": "Laitsaber",
    "Death Star": "Det Estar",
    "Iron Man": "Airon Man",
    "Spider-Man": "Spaider Man",
    "Avengers": "Avényers",
    "Thanos": "Tanos",
    "Thor": "Tor",
    "Joker": "Yóquer",
    "Cumberbatch": "Camberbach",
    "Joaquin Phoenix": "Yoaquín Fínix",
    "Python": "Paiton",
    "OpenAI": "Open-ei-ai",
    "ChatGPT": "Chat-ye-pe-te",
    "Smartphone": "Esmarfon",
    "Bluetooth": "Blutut",
    "Wi-Fi": "Uaifai",
    "Astromia": "Astro-mía",
    "Tauro": "Tauro",
    "Virgo": "Virgo",
    "Géminis": "Géminis",
    "outfit": "áut-fit",
    "look": "luc",
    "grunge": "gronsh",
    "cachemira": "cache-mira",
    "sneakers": "es-ní-quers",
    "blazer": "bléiser",
    "NBC": "ene-be-sé",
    "Warner Bros Studios": "Uárner Bros Estúdios",
    "Jennifer Aniston": "Yénifer Aniston",
    "Matt LeBlanc": "Mat Le-blanc",
    "Ferris Bueller": "Féris Biú-ler",
    "Stephen Hawking": "Estíven Jóquin",
    "Leonard Susskind": "Lénard Sás-kind",
    "Susskind": "Sás-kind",
    "Horizonte de Sucesos": "Ori-zonte de Sucesos",
    "Holográfico": "olo-gráfico",
    "3D": "tres de",
    "2D": "dos de",
    "Entropía": "Entropía",
}


def limpiar_texto_para_tts(texto):
    """Sustitución directa para que la voz sea perfecta."""
    # Quitamos signos que confunden la fonética pero mantenemos la estructura
    texto = texto.replace("..", ".").replace("¿", "").replace("?", "").replace("¡", "").replace("!", "")
    
    # Aplicamos el diccionario de pronunciación
    from .limpieza_engine import DICCIONARIO_PRONUNCIACION # Import local para evitar círculos
    for palabra, fonetica in DICCIONARIO_PRONUNCIACION.items():
        patron = re.compile(r'\b' + re.escape(palabra) + r'\b', re.IGNORECASE)
        texto = patron.sub(fonetica, texto)
    return re.sub(r"\s+", " ", texto).strip()

def corregir_json_subtitulos(word_boundaries):
    """
    Toma la lista de palabras del audio y las devuelve a su ortografía real.
    Maneja inteligentemente la puntuación para no perder datos.
    """
    from .limpieza_engine import DICCIONARIO_PRONUNCIACION
    # Mapa inverso: 'uárner' -> 'Warner'
    mapa_inverso = {v.lower(): k for k, v in DICCIONARIO_PRONUNCIACION.items()}
    
    for item in word_boundaries:
        palabra_audio = item["palabra"]
        
        # 1. Extraemos solo las letras para comparar
        limpia = palabra_audio.lower().strip(",.!?")
        
        # 2. Si la palabra (sin puntos/comas) está en el diccionario, la reemplazamos
        if limpia in mapa_inverso:
            # Detectamos qué puntuación tenía la palabra original
            puntuacion = "".join([c for c in palabra_audio if c in ",.!?"])
            # Reemplazamos manteniendo la puntuación (ej: 'Warner.')
            item["palabra"] = mapa_inverso[limpia] + puntuacion
        
        # Si no está en el diccionario, se queda como venía de la IA (seguro)
            
    return word_boundaries

def insertar_pausas_inteligentes(texto, es_ultima=False):
    """Asegura que cada bloque de texto termine con un punto."""
    texto = texto.strip()
    if not texto.endswith("."):
        texto += "."
    return texto