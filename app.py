import streamlit as st
import streamlit.components.v1 as components

import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Encuentros", page_icon="📅", layout="centered")

if not firebase_admin._apps:
    datos_firebase = dict(st.secrets["firebase"])
    datos_firebase["private_key"] = datos_firebase["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(datos_firebase)
    firebase_admin.initialize_app(cred)

db = firestore.client()
encuentro_ref = db.collection("encuentros").document("actual")

st.title("Encuentros")
st.write("Proponé un encuentro, respondé una propuesta y recibí avisos cuando cambie su estado.")

st.subheader("Notificaciones")
components.html("""
<div style="font-family: Arial; text-align: center;">
<button onclick="activarNotificaciones()" style="padding:10px 18px;border:none;border-radius:8px;cursor:pointer;font-size:15px;">Activar notificaciones</button>
<p id="estadoNotificacion" style="margin-top:10px;">Notificaciones sin activar</p>
</div>
<script>
function mostrarEstado() {
 const texto=document.getElementById("estadoNotificacion");
 if (!("Notification" in window)) texto.innerText="Este navegador no permite notificaciones.";
 else if (Notification.permission==="granted") texto.innerText="Notificaciones activadas";
 else if (Notification.permission==="denied") texto.innerText="Las notificaciones están bloqueadas en el navegador.";
 else texto.innerText="Notificaciones sin activar";
}
async function activarNotificaciones() {
 if (!("Notification" in window)) { mostrarEstado(); return; }
 const permiso=await Notification.requestPermission();
 if (permiso==="granted") new Notification("Encuentros", {body:"Las notificaciones quedaron activadas."});
 mostrarEstado();
}
mostrarEstado();
</script>
""", height=140)

documento = encuentro_ref.get()
if documento.exists:
    propuesta = documento.to_dict()
    estado_actual = propuesta.get("estado", "Pendiente")
else:
    propuesta = None
    estado_actual = None

# Detecta cambios de estado mientras esta sesión de Streamlit está abierta.
if propuesta:
    estado_anterior = st.session_state.get("estado_anterior")
    if estado_anterior is not None and estado_actual != estado_anterior:
        mensajes = {
            "Pendiente": "Hay una nueva propuesta de encuentro.",
            "Confirmada": "El encuentro fue confirmado.",
            "Rechazada": "El encuentro fue rechazado.",
            "Nueva propuesta": "Se propuso un nuevo horario."
        }
        mensaje = mensajes.get(estado_actual, "El estado del encuentro cambió.")
        components.html(f"""
<script>
if ("Notification" in window && Notification.permission === "granted") {{
    new Notification("Encuentros", {{body: {mensaje!r}}});
}}
</script>
""", height=0)
    st.session_state["estado_anterior"] = estado_actual

if propuesta:
    st.divider()
    st.subheader("Estado actual")
    if estado_actual == "Pendiente": st.info("Hay una propuesta pendiente de respuesta.")
    elif estado_actual == "Confirmada": st.success("El encuentro está confirmado.")
    elif estado_actual == "Rechazada": st.warning("El encuentro fue rechazado.")
    elif estado_actual == "Nueva propuesta": st.info("Se propuso un nuevo horario.")
    st.write("**Fecha:**", propuesta.get("fecha", ""))
    st.write("**Hora:**", propuesta.get("hora", ""))
    st.write("**Lugar:**", propuesta.get("lugar", ""))
else:
    st.info("Todavía no hay ningún encuentro propuesto.")

if st.button("Actualizar", key="actualizar"):
    st.rerun()

st.divider()
modo = st.radio("¿Qué querés hacer?", ["Proponer un encuentro", "Responder a un encuentro"], key="modo")

if modo == "Proponer un encuentro":
    st.subheader("Nueva propuesta")
    fecha = st.text_input("Fecha", placeholder="Ejemplo: 10/10/2026", key="fecha_propuesta")
    hora = st.text_input("Hora", placeholder="Ejemplo: 18:00", key="hora_propuesta")
    lugar = st.text_input("Lugar", placeholder="Ejemplo: Plaza 9 de Julio", key="lugar_propuesto")
    if st.button("Enviar propuesta", key="enviar_propuesta"):
        if not fecha or not hora or not lugar:
            st.warning("Completá la fecha, la hora y el lugar.")
        else:
            encuentro_ref.set({"fecha": fecha, "hora": hora, "lugar": lugar, "estado": "Pendiente"})
            st.success("La propuesta fue enviada.")
            st.rerun()

else:
    st.subheader("Responder a la propuesta")
    if propuesta:
        st.write("**Fecha:**", propuesta.get("fecha", ""))
        st.write("**Hora:**", propuesta.get("hora", ""))
        st.write("**Lugar:**", propuesta.get("lugar", ""))
        st.write("**Estado:**", propuesta.get("estado", ""))
        st.divider()
        if estado_actual == "Pendiente":
            st.write("**¿Podés encontrarte en ese momento?**")
            if st.button("Sí", key="aceptar_encuentro"):
                encuentro_ref.update({"estado": "Confirmada"})
                st.success("El encuentro fue confirmado.")
                st.rerun()
            if st.button("No", key="rechazar_encuentro"):
                encuentro_ref.update({"estado": "Rechazada"})
                st.warning("La propuesta fue rechazada.")
                st.rerun()
            if st.button("Otro horario", key="otro_horario"):
                st.session_state["mostrar_otro_horario"] = True
            if st.session_state.get("mostrar_otro_horario", False):
                st.divider()
                st.write("**Proponer otro horario**")
                nueva_fecha = st.text_input("Nueva fecha", placeholder="Ejemplo: 11/10/2026", key="nueva_fecha")
                nueva_hora = st.text_input("Nueva hora", placeholder="Ejemplo: 19:00", key="nueva_hora")
                if st.button("Enviar nuevo horario", key="enviar_nuevo_horario"):
                    if not nueva_fecha or not nueva_hora:
                        st.warning("Completá la nueva fecha y la nueva hora.")
                    else:
                        encuentro_ref.update({"fecha": nueva_fecha, "hora": nueva_hora, "estado": "Nueva propuesta"})
                        st.success("El nuevo horario fue enviado.")
                        st.session_state["mostrar_otro_horario"] = False
                        st.rerun()
        elif estado_actual == "Confirmada":
            st.success("Este encuentro ya está confirmado.")
        elif estado_actual == "Rechazada":
            st.warning("Este encuentro fue rechazado.")
        elif estado_actual == "Nueva propuesta":
            st.info("Hay un nuevo horario propuesto. Actualizá la página para verlo.")
    else:
        st.info("Todavía no hay ningún encuentro propuesto.")

with st.expander("¿Cómo funcionan las notificaciones?"):
    st.write("La aplicación guarda el estado del encuentro en Firebase.")
    st.write("Cuando el estado cambia durante la sesión abierta, la aplicación intenta mostrar una notificación del navegador si las notificaciones están permitidas.")
    st.write("Los estados utilizados son: Pendiente, Confirmada, Rechazada y Nueva propuesta.")
