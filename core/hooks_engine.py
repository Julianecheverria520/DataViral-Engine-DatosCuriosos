import random

HOOKS_POR_CANAL = {

    "misterio": [
        lambda t: f"Nadie quiere que sepas esto sobre {t}.",
        lambda t: f"Hay algo oscuro detrás de {t}.",
        lambda t: f"La verdad sobre {t} fue ocultada.",
        lambda t: f"Esto cambia todo lo que creías sobre {t}.",
        lambda t: f"El secreto oculto de {t} finalmente salió.",
        lambda t: f"Lo que descubrieron en {t} es perturbador.",
    ],

    "dinero": [
        lambda t: f"Si ignoras {t}, perderás dinero.",
        lambda t: f"Te están engañando con {t}.",
        lambda t: f"El sistema gana cuando no entiendes {t}.",
        lambda t: f"Esto afecta tu bolsillo más de lo que crees.",
    ],

    "guerra": [
        lambda t: f"La verdad brutal sobre {t} no se cuenta.",
        lambda t: f"Esto fue peor de lo que imaginas en {t}.",
        lambda t: f"Hay detalles prohibidos sobre {t}.",
        lambda t: f"Lo que pasó en {t} fue manipulado.",
    ],

    "fantasia": [
        lambda t: f"El secreto oculto detrás de {t}.",
        lambda t: f"Esto cambia la historia de {t}.",
        lambda t: f"Nadie vio esto en {t}.",
        lambda t: f"La parte oscura de {t} que ignoraste.",
    ],

    "datos": [
        lambda t: f"Este dato sobre {t} te sorprenderá.",
        lambda t: f"Nunca te explicaron esto sobre {t}.",
        lambda t: f"Este detalle cambia cómo ves {t}.",
        lambda t: f"Lo que no sabías sobre {t}.",
    ]
}

def generar_hook_controlado(tema, canal):

    canal = canal.lower()

    if canal not in HOOKS_POR_CANAL:
        canal = "datos"

    hook = random.choice(HOOKS_POR_CANAL[canal])(tema)

    palabras = hook.split()
    if len(palabras) > 12:
        hook = " ".join(palabras[:12])

    return hook