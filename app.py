import streamlit as st
import joblib
from gad7 import PREGUNTAS_GAD7, OPCIONES, interpretar_puntaje
from respuestas import mensaje_nivel_bajo, mensaje_nivel_alto

# Configuracion de la pagina
st.set_page_config(page_title="Asistente de tamizaje de ansiedad", page_icon="🧠")


# Carga del modelo y el vectorizador (una sola vez)
@st.cache_resource
def cargar_modelo():
    modelo = joblib.load("modelo_ansiedad.pkl")
    vectorizador = joblib.load("vectorizador_tfidf.pkl")
    return modelo, vectorizador


# Analisis del texto del usuario con el modelo
def analizar_texto(texto):
    X = vectorizador.transform([texto.lower().strip()])
    pred = modelo.predict(X)[0]   # 1 = Anxiety, 0 = Normal

    if pred == 1:
        respuesta = ("Gracias por compartirlo. Por lo que escribes, percibo "
                     "señales que podrían estar relacionadas con la ansiedad. "
                     "Para entenderlo mejor, te propongo responder un breve "
                     "cuestionario (GAD-7) más abajo.")
    else:
        respuesta = ("Gracias por contarme cómo te sientes. No percibo señales "
                     "claras de ansiedad en tu mensaje, pero igual te invito a "
                     "responder el cuestionario (GAD-7) para tener una mejor "
                     "referencia.")
    return pred, respuesta


modelo, vectorizador = cargar_modelo()

st.title("Asistente de tamizaje de ansiedad académica")


# Seccion 1: conversacion inicial con el modelo
st.subheader("Cuéntame, ¿cómo te has sentido últimamente?")

# Inicializacion de la memoria de la conversacion
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "deteccion_texto" not in st.session_state:
    st.session_state.deteccion_texto = None

# Mostrar el historial del chat
for msg in st.session_state.mensajes:
    with st.chat_message(msg["rol"]):
        st.write(msg["contenido"])

# Entrada del usuario
entrada = st.chat_input("Escribe aquí cómo te sientes...")
if entrada:
    # Guardar y mostrar el mensaje del usuario
    st.session_state.mensajes.append({"rol": "user", "contenido": entrada})
    with st.chat_message("user"):
        st.write(entrada)

    # El modelo analiza y responde
    pred, respuesta = analizar_texto(entrada)
    st.session_state.deteccion_texto = pred   # se usara junto al GAD-7 (Paso 4)
    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})
    with st.chat_message("assistant"):
        st.write(respuesta)

st.divider()


# Seccion 2: cuestionario GAD-7
st.subheader("Cuestionario GAD-7")
st.write("Responde según cómo te has sentido durante las últimas 2 semanas.")

# Mostrar las 7 preguntas
respuestas = []
for i, pregunta in enumerate(PREGUNTAS_GAD7):
    st.markdown(f"**{i + 1}. {pregunta}**")
    eleccion = st.radio(
        label=f"pregunta_{i}",
        options=list(OPCIONES.keys()),
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    respuestas.append(OPCIONES[eleccion])

# Calcular el puntaje y combinarlo con la deteccion del modelo
if st.button("Calcular resultado"):
    puntaje = sum(respuestas)
    nivel, es_alto = interpretar_puntaje(puntaje)
    deteccion = st.session_state.deteccion_texto   # None, 0 (Normal) o 1 (Anxiety)

    st.divider()
    st.subheader(f"Puntaje GAD-7: {puntaje} / 21")
    st.subheader(f"Nivel de ansiedad: {nivel}")

    # Regla de decision: el GAD-7 define el nivel; el modelo solo agrega
    # una alerta cuando el cuestionario da bajo pero el texto indica ansiedad.
    if not es_alto and deteccion == 1:
        st.warning(
            "Tus respuestas indican un nivel bajo, pero por lo que escribiste "
            "antes podrían existir señales de ansiedad. Si lo sientes así, "
            "considera conversar con alguien de confianza o un profesional."
        )

    # Guardamos el resultado para usarlo en el Paso 5 (respuestas y derivacion)
    st.session_state.resultado = {
        "puntaje": puntaje,
        "nivel": nivel,
        "es_alto": es_alto,
        "deteccion": deteccion,
    }

    # Respuesta final segun el nivel
    st.divider()
    if es_alto:
        # Nivel moderado o severo: mensaje de apoyo + derivacion
        texto, derivacion = mensaje_nivel_alto()
        st.error(texto)
        st.markdown(f"- **Servicio UNMSM:** {derivacion['servicio_unmsm']}")
        st.markdown(f"- **Línea de apoyo:** {derivacion['linea_apoyo']}")
        st.info("Si en algún momento sientes que estás en crisis, comunícate "
                "de inmediato con la Línea 113 (opción 5).")
    else:
        # Nivel minimo o leve: estrategias de afrontamiento
        texto, estrategias = mensaje_nivel_bajo()
        st.success(texto)
        for e in estrategias:
            st.markdown(f"- {e}")

# Aviso al pie
st.caption("Herramienta de apoyo y orientación. No sustituye atención profesional.")