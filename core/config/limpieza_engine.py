import re

# Diccionario de corrección fonética (con espacios, luego se normalizarán a guiones)
DICCIONARIO_PRONUNCIACION_ORIGINAL = {
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
    "CERN": "Sern",
    "LHC": "ele-ache-sé",
    "Mandela": "Mandéla",
    "Colisionador": "Colisionador",
    "Hadrones": "Adrones",
    "serotonina": "serotonina",
    "neuronas": "neuronas",
    "bioluminiscente": "bioluminiscente",
    "vago": "vago",
    "epigenética": "epigenética",
    "glinfático": "glinfático",
    "hormesis": "ormésis",
    "Glinfático": "Glin-fá-ti-co",
    "Cefalorraquídeo": "Se-fa-lo-rra-kí-de-o",
    "Rochester": "Ró-ches-ter",
    "Alzheimer": "Als-jái-mer",
    "Beta-amiloide": "Be-ta a-mi-lói-de",
    "serotonina": "se-ro-to-ní-na",
    "microbiota": "mi-cro-bió-ta",
    "vago": "vá-go",
    "Gershon": "Gér-shon",
    "intestinal": "in-tes-ti-nál",
    "Laniakea": "la-nia-ké-a",
    "Atractor": "a-trac-tór",
    "Anomalía": "a-no-ma-lí-a",
    "Vía Láctea": "vía láctea",
    "infrarrojas": "in-fra-rró-jas",
     "BLC1": "be-ele-se-uno",
    "Próxima Centauri": "prók-si-ma sen-táu-ri",
    "Megahertzios": "me-ga-ért-sios",
    "Espectrograma": "es-pec-tro-grá-ma",
    "982 MHz": "novecientos ochenta y dos mega-ért-sios",
    "Reencarnación": "Re-en-car-na-sión",
    "Kármica": "Kár-mi-ca",
    "Ian Stevenson": "Í-an Stí-ven-son",
    "Akáshicos": "A-ká-shi-cos",
    "Ethereal": "E-té-re-o",
    "Déjà vu": "De-ya-vú","Annie Kagan": "Áni Kágan",
    "Brian Weiss": "Bráian Uáis",
    "Samsara": "Sam-sá-ra",
    "Dharma": "Dár-ma",
    "Karma": "Kár-ma",
    "Pre-natal": "Pre-natál",
    "Carl Jung": "Carl Yung",
    "Sincronicidad": "Sin-cro-ni-si-dád",
    "Déjà vu": "De-ya-vú",
    "Inconsciente": "In-cons-sién-te",
    "Folclore": "Fol-cló-re",
    "Ian Stevenson": "Í-an Stí-ven-son",
    "Virginia": "Vir-yí-nia",
    "Psiquiatría": "Si-kia-trí-a",
    "autenticidad": "au-ten-ti-si-dád",
    "pre-natal": "pre-na-tál","Reencarnación": "re-en-car-na-sión",
    "dualidad": "dua-li-dád",
    "traumas": "tráu-mas",
    "esencia": "e-sén-sia",
    "omnipresente": "om-ni-pre-sén-te",
    "Akáshicos": "a-ká-shi-cos",
    "Fermi": "Fér-mi",
    "Enrico": "En-rí-ko",
    "Shor": "Shor",
    "James Webb": "Yeims Güéb",
    
    # Conceptos Cuánticos y Espaciales
    "qubits": "kiú-bits",
    "nebula": "né-bu-la",
    "supernova": "su-per-nó-va",
    "exoplanetas": "ek-so-pla-né-tas",
    
    # Siglas y Otros
    "RSA": "erre-ese-a",
    "UHD": "u-ache-de",
    "NASA": "ná-sa",
    "AI": "i-a",
     # Matemáticas y Algoritmos
    "Fibonacci": "Fi-bo-ná-chi",
    "áurea": "áurea",
    "algoritmo": "al-go-rítmo",
    "ecuación": "e-cua-sión",
    "cálculo": "cálculo",
    "hardware": "járgüer",
    "CPU": "se-pe-ú",
    "clímax": "clí-maks",
    "binario": "bi-ná-rio",
    "redes": "ré-des",
    "PulsoCurioso": "Púl-so Cu-rió-so", # O 'i-a' si prefieres Inteligencia Artificial
}


# Normalizar fonéticas: reemplazar espacios por guiones para que edge_tts las trate como una sola palabra
DICCIONARIO_PRONUNCIACION = {k: v.replace(' ', '-') for k, v in DICCIONARIO_PRONUNCIACION_ORIGINAL.items()}

def limpiar_texto_para_tts(texto):
    """Sustitución directa para que la voz sea perfecta."""
    # Quitamos signos que confunden la fonética pero mantenemos la estructura
    texto = texto.replace("..", ".").replace("¿", "").replace("?", "").replace("¡", "").replace("!", "")
    
    # Aplicamos el diccionario de pronunciación (ya con guiones)
    for palabra, fonetica in DICCIONARIO_PRONUNCIACION.items():
        patron = re.compile(r'\b' + re.escape(palabra) + r'\b', re.IGNORECASE)
        texto = patron.sub(fonetica, texto)
    return re.sub(r"\s+", " ", texto).strip()

def corregir_json_subtitulos(word_boundaries):
    """
    Toma la lista de palabras del audio y las devuelve a su ortografía real.
    Maneja inteligentemente la puntuación para no perder datos.
    """
    # Mapa inverso: 'uárner-bros' -> 'Warner Bros' (con espacios originales)
    mapa_inverso = {v.lower(): k for k, v in DICCIONARIO_PRONUNCIACION.items()}
    
    for item in word_boundaries:
        palabra_audio = item["palabra"]
        
        # Extraemos solo las letras y guiones (para mantener la estructura de la palabra fonética)
        # pero quitamos puntuación al final
        limpia = palabra_audio.lower().strip(",.!?")
        
        # Si la palabra (con guiones) está en el mapa inverso, la reemplazamos
        if limpia in mapa_inverso:
            # Detectamos qué puntuación tenía la palabra original
            puntuacion = "".join([c for c in palabra_audio if c in ",.!?"])
            # Reemplazamos manteniendo la puntuación
            item["palabra"] = mapa_inverso[limpia] + puntuacion
        # Si no está, se queda como venía de la IA (seguro)
            
    return word_boundaries

def insertar_pausas_inteligentes(texto, es_ultima=False):
    """Asegura que cada bloque de texto termine con un punto."""
    texto = texto.strip()
    if not texto.endswith("."):
        texto += "."
    return texto