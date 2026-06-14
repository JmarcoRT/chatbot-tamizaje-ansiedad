# respuestas.py — Contenido de apoyo segun el nivel de ansiedad

# Estrategias para nivel bajo (minima / leve)
ESTRATEGIAS = [
    "Practica respiración profunda: inhala 4 segundos, mantén 4, exhala 4.",
    "Organiza tus tareas académicas en bloques pequeños y con pausas.",
    "Mantén horarios regulares de sueño y evita estudiar de madrugada.",
    "Dedica momentos a actividad física o caminatas cortas.",
    "Habla con personas de confianza sobre cómo te sientes.",
]

# Datos de derivacion para nivel alto (moderada / severa)
# IMPORTANTE: verificar y completar con los datos reales de la UNMSM.
DERIVACION = {
    "servicio_unmsm": "Oficina de Bienestar Universitario - UNMSM "
                      "(área de atención psicológica).",
    "linea_apoyo": "Línea 113 del MINSA, opción 5 (salud mental), "
                   "gratuita y a nivel nacional.",
}


def mensaje_nivel_bajo():
    texto = ("Tus resultados sugieren un nivel bajo de ansiedad. "
             "Aún así, aquí tienes algunas estrategias que pueden ayudarte:")
    return texto, ESTRATEGIAS


def mensaje_nivel_alto():
    texto = ("Tus resultados sugieren un nivel de ansiedad que conviene "
             "atender con apoyo profesional. No estás solo/a y buscar ayuda "
             "es una decisión valiosa. Puedes acudir a:")
    return texto, DERIVACION