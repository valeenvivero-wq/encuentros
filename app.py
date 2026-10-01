import streamlit as st

st.title("Encuentros")

st.subheader("Proponer un encuentro")

fecha = st.text_input("Fecha")
hora = st.text_input("Hora")
lugar = st.text_input("Lugar")

if st.button("Enviar propuesta"):
    st.session_state["fecha"] = fecha
    st.session_state["hora"] = hora
    st.session_state["lugar"] = lugar
    st.session_state["estado"] = "Pendiente"

if "estado" in st.session_state:
    st.divider()

    st.subheader("Propuesta")

    st.write("Fecha:", st.session_state["fecha"])
    st.write("Hora:", st.session_state["hora"])
    st.write("Lugar:", st.session_state["lugar"])
    st.write("Estado:", st.session_state["estado"])

    st.subheader("Responder")

    if st.button("Sí"):
        st.session_state["estado"] = "Confirmada"

    if st.button("No"):
        st.session_state["estado"] = "Rechazada"

    if st.button("Otro horario"):
        st.session_state["estado"] = "Nueva propuesta"
