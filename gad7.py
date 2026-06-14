# gad7.py — Cuestionario GAD-7 (tamizaje de ansiedad)

# Las 7 preguntas oficiales del GAD-7.
# Encabezado: "Durante las ultimas 2 semanas, con que frecuencia te has
# sentido afectado/a por los siguientes problemas?"
PREGUNTAS_GAD7 = [
    "Sentirse nervioso/a, ansioso/a o muy alterado/a",
    "No poder dejar de preocuparse o controlar la preocupación",
    "Preocuparse demasiado por diferentes cosas",
    "Dificultad para relajarse",
    "Estar tan inquieto/a que es difícil permanecer sentado/a tranquilo/a",
    "Irritarse o enojarse con facilidad",
    "Sentir miedo como si algo terrible fuera a pasar",
]

# Cada pregunta se responde de 0 a 3:
OPCIONES = {
    "Nunca": 0,
    "Varios días": 1,
    "Más de la mitad de los días": 2,
    "Casi todos los días": 3,
}


def interpretar_puntaje(puntaje):
    """Devuelve (nivel, es_alto) segun el puntaje total del GAD-7 (0 a 21)."""
    if puntaje <= 4:
        return "Mínima", False
    elif puntaje <= 9:
        return "Leve", False
    elif puntaje <= 14:
        return "Moderada", True
    else:
        return "Severa", True