# conversacion.py — Respuestas del bot durante la charla libre (estado conversando)
import random


# Respuestas por defecto
RESPUESTAS_NEUTRAS = [
    "Gracias por contarme. ¿Cómo describirías tu estado de ánimo en estos días?",
    "Entiendo. ¿Hay algo que te haya estado preocupando últimamente?",
    "Te escucho. ¿Cómo te has sentido en general esta última semana?",
]

# Palabras clave para detectar cada tipo de mensaje
SALUDOS = ("hola", "buenas", "que tal", "qué tal", "buenos dias", "buenas tardes")
DESPEDIDAS = ("chau", "adios", "adiós", "vete", "me voy", "nos vemos", "bye")
PREGUNTA_INICIO = ("que", "qué", "como", "cómo", "quien", "quién", "por que",
                   "por qué", "cuando", "cuándo", "donde", "dónde")
GRACIAS = ("gracias", "grax", "thank")


def responder_charla(texto):
    """Devuelve una respuesta del bot segun el tipo de mensaje del usuario."""
    t = texto.lower().strip()

    # Escenario 5: mensaje muy corto o sin contenido util
    if len(t) < 3:
        return ("Te leo. Cuando quieras, cuéntame con tus palabras cómo te has "
                "sentido últimamente.")

    # Escenario 1: saludo
    if any(t.startswith(s) for s in SALUDOS):
        return "¡Hola! Me alegra que estés aquí. ¿Cómo te has sentido en estos últimos días?"

    # Escenario 2: despedida
    if any(p in t for p in DESPEDIDAS):
        return ("Está bien, gracias por pasar. Recuerda que puedes volver cuando "
                "quieras conversar. Cuídate.")

    # Escenario 4: agradecimiento
    if any(p in t for p in GRACIAS):
        return "Con gusto. Si quieres, cuéntame un poco más sobre cómo te has sentido."

    # Escenario 3: pregunta
    if t.endswith("?") or t.startswith(PREGUNTA_INICIO):
        return ("Buena pregunta. Soy un asistente de apoyo enfocado en cómo te "
                "sientes, así que no tengo todas las respuestas, pero con gusto te "
                "escucho. ¿Cómo has estado anímicamente?")

    # Escenario 6: por defecto, una respuesta neutral al azar
    return random.choice(RESPUESTAS_NEUTRAS)

def es_despedida(texto):
    """Devuelve True si el mensaje parece una despedida."""
    t = texto.lower().strip()
    return any(p in t for p in DESPEDIDAS)