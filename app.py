import streamlit as st
import joblib
from gad7 import PREGUNTAS_GAD7, OPCIONES, interpretar_puntaje
from respuestas import mensaje_nivel_bajo, mensaje_nivel_alto
from conversacion import responder_charla, es_despedida
from sentence_transformers import SentenceTransformer

# Configuracion de la pagina
st.set_page_config(
    page_title="Asistente de Tamizaje de Ansiedad Académica",
    page_icon="https://api.dicebear.com/9.x/icons/svg?icon=robot&backgroundColor=7C6BF0&iconColor=ffffff",
    layout="centered",
)


# Carga del modelo
@st.cache_resource
def cargar_modelo():
    modelo = joblib.load("modelo_ansiedad.pkl")
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return modelo, embedder

modelo, embedder = cargar_modelo()


# Predicción del modelo: encodea el texto en español y clasifica
def detecta_ansiedad(texto):
    emb = embedder.encode([texto.strip()], normalize_embeddings=True)
    pred = int(modelo.predict(emb)[0])
    return pred


# Inicializacion del estado de la conversacion
def iniciar_estado():
    st.session_state.estado = "conversando"
    st.session_state.mensajes = [
        {"rol": "assistant",
         "contenido": "Hola, soy un asistente de apoyo para estudiantes. "
                      "Puedes contarme con tus palabras cómo te has sentido "
                      "últimamente."}
    ]
    st.session_state.intercambios = 0
    st.session_state.detecto_ansiedad = False
    st.session_state.pregunta_actual = 0
    st.session_state.respuestas_gad7 = []


# Se ejecuta solo la primera vez que se abre la app
if "estado" not in st.session_state:
    iniciar_estado()


# --- Titulo ---
st.title("Asistente de tamizaje de ansiedad académica")

# Avatares
AVATAR_BOT = "https://ui-avatars.com/api/?name=IA&background=7C6BF0&color=fff&bold=true&rounded=true"
AVATAR_USER = "https://api.dicebear.com/9.x/icons/svg?icon=mortarboard&backgroundColor=3BA99C&iconColor=ffffff"

# --- Historial del chat (siempre visible) ---
for msg in st.session_state.mensajes:
    avatar = AVATAR_BOT if msg["rol"] == "assistant" else AVATAR_USER
    with st.chat_message(msg["rol"], avatar=avatar):
        st.write(msg["contenido"])


# --- Zona de accion segun el estado ---

# Estado: conversando -> caja de texto libre
if st.session_state.estado == "conversando":
    entrada = st.chat_input("Escribe aquí cómo te sientes...")
    if entrada:
        # Guardar el mensaje del usuario
        st.session_state.mensajes.append({"rol": "user", "contenido": entrada})
        st.session_state.intercambios += 1

        # Mostrar el mensaje del usuario de inmediato
        with st.chat_message("user", avatar=AVATAR_USER):
            st.write(entrada)

        # Burbuja temporal antes de la respuesta del bot
        marcador = st.empty()
        with marcador.container():
            with st.chat_message("assistant", avatar=AVATAR_BOT):
                st.markdown(
                    "<div class='typing'><span></span><span></span><span></span></div>"
                    "<style>"
                    ".typing{display:flex;gap:5px;padding:4px 2px}"
                    ".typing span{width:8px;height:8px;border-radius:50%;"
                    "background:#7C6BF0;display:inline-block;"
                    "animation:salto 1.2s infinite ease-in-out}"
                    ".typing span:nth-child(2){animation-delay:.2s}"
                    ".typing span:nth-child(3){animation-delay:.4s}"
                    "@keyframes salto{0%,60%,100%{transform:translateY(0);opacity:.3}"
                    "30%{transform:translateY(-5px);opacity:1}}"
                    "</style>",
                    unsafe_allow_html=True,
                )

        # Traducir y analizar con el modelo
        if detecta_ansiedad(entrada) == 1:
            st.session_state.detecto_ansiedad = True

        marcador.empty()

        # Decidir la respuesta del bot
        if es_despedida(entrada):
            # Despedida: cierre, sin ofrecer cuestionario
            respuesta = ("Está bien, gracias por pasar. Recuerda que puedes volver "
                         "cuando quieras conversar. Cuídate.")
            st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})

        elif st.session_state.detecto_ansiedad or st.session_state.intercambios >= 3:
            # Regla: ofrecer el cuestionario
            mensaje = ("Gracias por contármelo. Me gustaría saber un poco más sobre tu estado. ¿Te gustaría "
                       "responder 7 preguntas breves? Te tomará solo un par de minutos.")
            st.session_state.mensajes.append({"rol": "assistant", "contenido": mensaje})
            st.session_state.estado = "ofreciendo"

        else:
            # Charla libre: responder segun el tipo de mensaje
            respuesta = responder_charla(entrada)
            st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})

        st.rerun()

# Estado: ofreciendo -> botones Si / No
elif st.session_state.estado == "ofreciendo":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sí, responder", use_container_width=True):
            # Pasamos al cuestionario
            st.session_state.estado = "en_cuestionario"
            st.session_state.mensajes.append(
                {"rol": "user", "contenido": "Sí, responder"})
            st.rerun()
    with col2:
        if st.button("Ahora no", use_container_width=True):
            # Volver a conversar, sin insistir
            st.session_state.mensajes.append(
                {"rol": "user", "contenido": "Ahora no"})
            st.session_state.mensajes.append(
                {"rol": "assistant",
                 "contenido": "Sin problema, lo dejamos para cuando quieras. "
                              "Si te sirve, podemos seguir conversando."})
            st.session_state.estado = "conversando"
            st.rerun()

# Estado: en_cuestionario -> preguntas del GAD-7 una por una
elif st.session_state.estado == "en_cuestionario":
    idx = st.session_state.pregunta_actual   # en que pregunta vamos (0 a 6)

    # Agregar la pregunta al historial UNA sola vez
    texto_pregunta = (f"**Pregunta {idx + 1} de 7**\n\n"
                      f"{PREGUNTAS_GAD7[idx]}\n\n"
                      f"*(Piensa en las últimas 2 semanas.)*")
    if not st.session_state.mensajes or st.session_state.mensajes[-1]["contenido"] != texto_pregunta:
        st.session_state.mensajes.append(
            {"rol": "assistant", "contenido": texto_pregunta})
        st.rerun()

    # Mostrar las 4 opciones
    opciones = list(OPCIONES.keys())
    fila1 = st.columns(2)
    fila2 = st.columns(2)
    casillas = [fila1[0], fila1[1], fila2[0], fila2[1]]

    for i, opcion in enumerate(opciones):
        with casillas[i]:
            if st.button(opcion, key=f"opt_{idx}_{i}", use_container_width=True):
                # Guardar la respuesta (su valor 0 a 3)
                st.session_state.respuestas_gad7.append(OPCIONES[opcion])
                # Registrar la eleccion en el historial del chat
                st.session_state.mensajes.append(
                    {"rol": "user", "contenido": opcion})

                # Avanzar a la siguiente pregunta o terminar
                if idx + 1 < len(PREGUNTAS_GAD7):
                    st.session_state.pregunta_actual += 1
                else:
                    st.session_state.estado = "finalizado"
                st.rerun()

# Estado: finalizado -> resultado, derivacion y reinicio
elif st.session_state.estado == "finalizado":
    # Calcular el puntaje total y el nivel (una sola vez)
    if "resultado_mostrado" not in st.session_state:
        puntaje = sum(st.session_state.respuestas_gad7)
        nivel, es_alto = interpretar_puntaje(puntaje)

        # Mensaje con el puntaje y el nivel
        resumen = (f"Gracias por responder. Tu puntaje fue de **{puntaje} / 21**, "
                   f"que corresponde a un nivel de ansiedad **{nivel.lower()}**. "
                   f"Esto no es un diagnóstico, sino una orientación.")
        st.session_state.mensajes.append({"rol": "assistant", "contenido": resumen})

        # Regla GAD-7 + modelo: alerta suave si el cuestionario da bajo
        if not es_alto and st.session_state.detecto_ansiedad:
            alerta = ("Tus respuestas indican un nivel bajo, pero por lo que "
                      "escribiste antes podrían existir señales de ansiedad. Si lo "
                      "sientes así, considera conversar con alguien de confianza.")
            st.session_state.mensajes.append({"rol": "assistant", "contenido": alerta})

        # Respuesta segun el nivel
        if es_alto:
            texto, derivacion = mensaje_nivel_alto()
            cuerpo = (f"{texto}\n\n"
                      f"- **Servicio UNMSM:** {derivacion['servicio_unmsm']}\n"
                      f"- **Línea de apoyo:** {derivacion['linea_apoyo']}\n\n"
                      f"Si en algún momento sientes que estás en crisis, comunícate "
                      f"de inmediato con la Línea 113 (opción 5).")
        else:
            texto, estrategias = mensaje_nivel_bajo()
            lista = "\n".join([f"- {e}" for e in estrategias])
            cuerpo = f"{texto}\n\n{lista}"

        st.session_state.mensajes.append({"rol": "assistant", "contenido": cuerpo})
        st.session_state.resultado_mostrado = True
        st.rerun()

    # Boton para reiniciar la conversacion
    if st.button("Empezar de nuevo", use_container_width=True):
        iniciar_estado()
        del st.session_state.resultado_mostrado
        st.rerun()

# Aviso al pie
st.caption("Herramienta de apoyo y orientación. No sustituye atención profesional.")