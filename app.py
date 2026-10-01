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

# Referencia al encuentro compartido
encuentro_ref = db.collection("encuentros").document("actual")


st.title("Encuentros")

st.write("Elegí una opción:")

modo = st.radio(
    "¿Qué querés hacer?",
    ["Proponer un encuentro", "Responder a un encuentro"]
)


# --------------------------------------------------
# MODO 1: PROPONER
# --------------------------------------------------

if modo == "Proponer un encuentro":

    st.subheader("Proponer un encuentro")

    fecha = st.text_input("Fecha")
    hora = st.text_input("Hora")
    lugar = st.text_input("Lugar")

    if st.button("Enviar propuesta"):

        encuentro_ref.set({
            "fecha": fecha,
            "hora": hora,
            "lugar": lugar,
            "estado": "Pendiente"
        })

        st.success("Propuesta enviada.")


# --------------------------------------------------
# MODO 2: RESPONDER
# --------------------------------------------------

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

        if st.button("Sí"):
            encuentro_ref.update({
                "estado": "Confirmada"
            })

            st.success("Encuentro confirmado.")
            st.rerun()

        if st.button("No"):
            encuentro_ref.update({
                "estado": "Rechazada"
            })

            st.warning("Encuentro rechazado.")
            st.rerun()

        if st.button("Otro horario"):

            st.session_state["otro_horario"] = True

        if st.session_state.get("otro_horario", False):

            st.write("Proponer otro horario")

            nueva_fecha = st.text_input("Nueva fecha")
            nueva_hora = st.text_input("Nueva hora")

            if st.button("Enviar nuevo horario"):

                encuentro_ref.update({
                    "fecha": nueva_fecha,
                    "hora": nueva_hora,
                    "estado": "Nueva propuesta"
                })

                st.success("Nuevo horario enviado.")
                st.rerun()

    else:

        st.info("Todavía no hay ningún encuentro propuesto.")

# Leer la propuesta desde Firestore
documento = encuentro_ref.get()

if documento.exists:
    propuesta = documento.to_dict()

    st.divider()

    st.subheader("Propuesta")

    st.write("Fecha:", propuesta["fecha"])
    st.write("Hora:", propuesta["hora"])
    st.write("Lugar:", propuesta["lugar"])
    st.write("Estado:", propuesta["estado"])

    st.subheader("Responder")

    if st.button("Sí"):
        encuentro_ref.update({
            "estado": "Confirmada"
        })
        st.rerun()

    if st.button("No"):
        encuentro_ref.update({
            "estado": "Rechazada"
        })
        st.rerun()

    if st.button("Otro horario"):
        encuentro_ref.update({
            "estado": "Nueva propuesta"
        })
        st.rerun()
