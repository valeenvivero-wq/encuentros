```python
import streamlit as st
import streamlit.components.v2 as components

import firebase_admin
from firebase_admin import credentials, firestore


# ============================================================
# CONECTAR CON FIREBASE
# ============================================================

if not firebase_admin._apps:
    datos_firebase = dict(st.secrets["firebase"])

    datos_firebase["private_key"] = datos_firebase["private_key"].replace(
        "\\n", "\n"
    )

    cred = credentials.Certificate(datos_firebase)

    firebase_admin.initialize_app(cred)


db = firestore.client()


# Documento compartido
encuentro_ref = db.collection("encuentros").document("actual")


# ============================================================
# PÁGINA
# ============================================================

st.title("Encuentros")


# ============================================================
# NOTIFICACIONES
# ============================================================

notificaciones = components.component(
    name="notificaciones",

    html="""
    <button id="activar">
        Activar notificaciones
    </button>
    """,

    js="""
    export default function(component) {

        const { parentElement, setStateValue } = component;

        const boton = parentElement.querySelector("#activar");

        boton.onclick = async () => {

            const permiso = await Notification.requestPermission();

            setStateValue("permiso", permiso);
        };
    }
    """
)


resultado = notificaciones(
    key="notificaciones",
    default={"permiso": None},
    on_permiso_change=lambda: None
)


if resultado.permiso == "granted":

    st.success("Notificaciones activadas.")

elif resultado.permiso == "denied":

    st.warning("Las notificaciones están bloqueadas.")


# ============================================================
# LEER ENCUENTRO ACTUAL
# ============================================================

documento = encuentro_ref.get()


if documento.exists:

    propuesta = documento.to_dict()

    estado_actual = propuesta.get(
        "estado",
        "Pendiente"
    )

else:

    propuesta = None

    estado_actual = None


# ============================================================
# AVISOS
# ============================================================

if propuesta:

    if estado_actual == "Pendiente":

        st.info(
            "Hay una propuesta pendiente de respuesta."
        )

    elif estado_actual == "Confirmada":

        st.success(
            "El encuentro fue confirmado."
        )

    elif estado_actual == "Rechazada":

        st.warning(
            "La propuesta fue rechazada."
        )

    elif estado_actual == "Nueva propuesta":

        st.info(
            "Te propusieron un nuevo horario."
        )


# ============================================================
# ACTUALIZAR
# ============================================================

if st.button(
    "Actualizar",
    key="actualizar"
):

    st.rerun()


st.divider()


# ============================================================
# ELEGIR MODO
# ============================================================

modo = st.radio(
    "¿Qué querés hacer?",
    [
        "Proponer un encuentro",
        "Responder a un encuentro"
    ],
    key="modo"
)


# ============================================================
# PROPONER
# ============================================================

if modo == "Proponer un encuentro":

    st.subheader(
        "Proponer un encuentro"
    )

    fecha = st.text_input(
        "Fecha",
        key="fecha_propuesta"
    )

    hora = st.text_input(
        "Hora",
        key="hora_propuesta"
    )

    lugar = st.text_input(
        "Lugar",
        key="lugar_propuesto"
    )


    if st.button(
        "Enviar propuesta",
        key="enviar_propuesta"
    ):

        encuentro_ref.set({

            "fecha": fecha,

            "hora": hora,

            "lugar": lugar,

            "estado": "Pendiente"

        })

        st.success(
            "Propuesta enviada."
        )

        st.rerun()


# ============================================================
# RESPONDER
# ============================================================

elif modo == "Responder a un encuentro":

    st.subheader(
        "Propuesta recibida"
    )


    if propuesta:

        st.write(
            "Fecha:",
            propuesta.get("fecha", "")
        )

        st.write(
            "Hora:",
            propuesta.get("hora", "")
        )

        st.write(
            "Lugar:",
            propuesta.get("lugar", "")
        )

        st.write(
            "Estado:",
            propuesta.get("estado", "")
        )


        st.divider()


        st.subheader(
            "¿Podés encontrarte en ese momento?"
        )


        # ----------------------------------------------------
        # SÍ
        # ----------------------------------------------------

        if st.button(
            "Sí",
            key="aceptar_encuentro"
        ):

            encuentro_ref.update({

                "estado": "Confirmada"

            })

            st.success(
                "Encuentro confirmado."
            )

            st.rerun()


        # ----------------------------------------------------
        # NO
        # ----------------------------------------------------

        if st.button(
            "No",
            key="rechazar_encuentro"
        ):

            encuentro_ref.update({

                "estado": "Rechazada"

            })

            st.warning(
                "Encuentro rechazado."
            )

            st.rerun()


        # ----------------------------------------------------
        # OTRO HORARIO
        # ----------------------------------------------------

        if st.button(
            "Otro horario",
            key="otro_horario"
        ):

            st.session_state[
                "mostrar_otro_horario"
            ] = True


        if st.session_state.get(
            "mostrar_otro_horario",
            False
        ):

            st.write(
                "Proponer otro horario"
            )


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


                st.success(
                    "Nuevo horario enviado."
                )


                st.session_state[
                    "mostrar_otro_horario"
                ] = False


                st.rerun()


    else:

        st.info(
            "Todavía no hay ningún encuentro propuesto."
        )
```

