import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Conectar con Firebase
if not firebase_admin._apps:
    datos_firebase = dict(st.secrets["firebase"])
    datos_firebase["private_key"] = datos_firebase["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(datos_firebase)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Documento compartido
encuentro_ref = db.collection("encuentros").document("actual")

st.title("Encuentros")

modo = st.radio(
    "¿Qué querés hacer?",
    ["Proponer un encuentro", "Responder a un encuentro"],
    key="modo"
)

# -----------------------------
# PROPONER
# -----------------------------

if modo == "Proponer un encuentro":

    st.subheader("Proponer un encuentro")

    fecha = st.text_input("Fecha", key="fecha_propuesta")
    hora = st.text_input("Hora", key="hora_propuesta")
    lugar = st.text_input("Lugar", key="lugar_propuesto")

    if st.button("Enviar propuesta", key="enviar_propuesta"):

        encuentro_ref.set({
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar,
            "estado": "Pendiente"
        })

        st.success("Propuesta enviada.")


# -----------------------------
# RESPONDER
# -----------------------------

elif modo == "Responder a un encuentro":

    st.subheader("Propuesta recibida")

    documento = encuentro_ref.get()

    if documento.exists:

        propuesta = documento.to_dict()

        st.write("Fecha:", propuesta["fecha"])
        st.write("Hora:", propuesta["hora"])
        st.write("Lugar:", propuesta["lugar"])
        st.write("Estado:", propuesta["estado"])

        st.divider()

        st.subheader("¿Podés encontrarte en ese momento?")

        if st.button("Sí", key="aceptar_encuentro"):

            encuentro_ref.update({
                "estado": "Confirmada"
            })

            st.success("Encuentro confirmado.")
            st.rerun()

        if st.button("No", key="rechazar_encuentro"):

            encuentro_ref.update({
                "estado": "Rechazada"
            })

            st.warning("Encuentro rechazado.")
            st.rerun()

        if st.button("Otro horario", key="otro_horario"):

            st.session_state["mostrar_otro_horario"] = True

        if st.session_state.get("mostrar_otro_horario", False):

            st.write("Proponer otro horario")

            nueva_fecha = st.text_input(
                "Nueva fecha",
                key="nueva_fecha"
            )

            nueva_hora = st.text_input(
                "Nueva hora",
                key="nueva_hora"
            )

            if st.button(
                "Enviar nuevo horario",
                key="enviar_nuevo_horario"
            ):

                encuentro_ref.update({
                    "fecha": nueva_fecha,
                    "hora": nueva_hora,
                    "estado": "Nueva propuesta"
                })

                st.success("Nuevo horario enviado.")
                st.rerun()

    else:

        st.info("Todavía no hay ningún encuentro propuesto.")
