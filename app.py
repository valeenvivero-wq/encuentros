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

# Referencia al encuentro
encuentro_ref = db.collection("encuentros").document("actual")

st.title("Encuentros")

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
