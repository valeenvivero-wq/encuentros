import streamlit as st
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import messaging


st.set_page_config(
    page_title="Encuentros",
    page_icon="📅",
    layout="centered"
)


# ---------------------------------------------------------
# FIREBASE
# ---------------------------------------------------------

if not firebase_admin._apps:

    datos_firebase = dict(st.secrets["firebase"])

    datos_firebase["private_key"] = (
        datos_firebase["private_key"].replace("\\n", "\n")
    )

    cred = credentials.Certificate(datos_firebase)

    firebase_admin.initialize_app(cred)


db = firestore.client()

encuentro_ref = (
    db.collection("encuentros")
    .document("actual")
)


# ---------------------------------------------------------
# FUNCIÓN PARA ENVIAR NOTIFICACIONES
# ---------------------------------------------------------

def enviar_notificacion(titulo, mensaje):

    tokens_ref = db.collection("fcmTokens").stream()

    enviados = 0
    errores = []
    tokens_invalidos = []

    for documento in tokens_ref:

        datos = documento.to_dict()

        token = datos.get("token")

        if not token:
            continue

        try:

            mensaje_firebase = messaging.Message(

                notification=messaging.Notification(
                    title=titulo,
                    body=mensaje
                ),

                token=token
            )

            messaging.send(mensaje_firebase)

            enviados += 1

        except Exception as error:

            texto_error = str(error)

            errores.append(texto_error)

            if (
                "registration-token-not-registered"
                in texto_error
                or "not-found"
                in texto_error
            ):
                tokens_invalidos.append(documento.id)


    # Eliminar tokens que Firebase ya no reconoce
    for token_id in tokens_invalidos:

        db.collection("fcmTokens").document(token_id).delete()


    return enviados, errores


# ---------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------

st.title("Encuentros")

st.write(
    "Proponé un encuentro, respondé una propuesta "
    "y recibí avisos cuando cambie su estado."
)


st.subheader("Notificaciones")

st.info(
    "Las notificaciones del celular se activan desde "
    "la página de notificaciones de Firebase."
)


st.link_button(
    "Activar notificaciones en el celular",
    "https://encuentros-e9cdb.web.app/"
)


# ---------------------------------------------------------
# LEER ENCUENTRO
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# ESTADO ACTUAL
# ---------------------------------------------------------

if propuesta:

    st.divider()

    st.subheader("Estado actual")


    if estado_actual == "Pendiente":

        st.info(
            "Hay una propuesta pendiente de respuesta."
        )


    elif estado_actual == "Confirmada":

        st.success(
            "El encuentro está confirmado."
        )


    elif estado_actual == "Rechazada":

        st.warning(
            "El encuentro fue rechazado."
        )


    elif estado_actual == "Nueva propuesta":

        st.info(
            "Se propuso un nuevo horario."
        )


    st.write(
        "**Fecha:**",
        propuesta.get("fecha", "")
    )

    st.write(
        "**Hora:**",
        propuesta.get("hora", "")
    )

    st.write(
        "**Lugar:**",
        propuesta.get("lugar", "")
    )


else:

    st.info(
        "Todavía no hay ningún encuentro propuesto."
    )


# ---------------------------------------------------------
# ACTUALIZAR
# ---------------------------------------------------------

if st.button(
    "Actualizar",
    key="actualizar"
):

    st.rerun()


# ---------------------------------------------------------
# MODO
# ---------------------------------------------------------

st.divider()


modo = st.radio(
    "¿Qué querés hacer?",
    [
        "Proponer un encuentro",
        "Responder a un encuentro"
    ],
    key="modo"
)


# =========================================================
# PROPONER ENCUENTRO
# =========================================================

if modo == "Proponer un encuentro":

    st.subheader("Nueva propuesta")


    fecha = st.text_input(
        "Fecha",
        placeholder="Ejemplo: 10/10/2026",
        key="fecha_propuesta"
    )


    hora = st.text_input(
        "Hora",
        placeholder="Ejemplo: 18:00",
        key="hora_propuesta"
    )


    lugar = st.text_input(
        "Lugar",
        placeholder="Ejemplo: Plaza 9 de Julio",
        key="lugar_propuesto"
    )


    if st.button(
        "Enviar propuesta",
        key="enviar_propuesta"
    ):

        if not fecha or not hora or not lugar:

            st.warning(
                "Completá la fecha, la hora y el lugar."
            )

        else:

            encuentro_ref.set({

                "fecha": fecha,

                "hora": hora,

                "lugar": lugar,

                "estado": "Pendiente"

            })


            enviados, errores = enviar_notificacion(

                "Encuentros",

                "Hay una nueva propuesta de encuentro."

            )


            if enviados > 0:

                st.success(
                    "La propuesta fue enviada y la notificación fue enviada al celular."
                )

            elif errores:

                st.warning(
                    "La propuesta fue guardada, pero Firebase no pudo enviar la notificación."
                )

                with st.expander("Ver error de Firebase"):

                    for error in errores:

                        st.code(error)

            else:

                st.warning(
                    "La propuesta fue guardada, pero no hay ningún token de celular registrado."
                )


            st.rerun()


# =========================================================
# RESPONDER
# =========================================================

else:

    st.subheader(
        "Responder a la propuesta"
    )


    if propuesta:

        st.write(
            "**Fecha:**",
            propuesta.get("fecha", "")
        )

        st.write(
            "**Hora:**",
            propuesta.get("hora", "")
        )

        st.write(
            "**Lugar:**",
            propuesta.get("lugar", "")
        )

        st.write(
            "**Estado:**",
            propuesta.get("estado", "")
        )


        st.divider()


        if estado_actual == "Pendiente":

            st.write(
                "**¿Podés encontrarte en ese momento?**"
            )


            if st.button(
                "Sí",
                key="aceptar_encuentro"
            ):

                encuentro_ref.update({
                    "estado": "Confirmada"
                })


                enviados, errores = enviar_notificacion(

                    "Encuentros",

                    "El encuentro fue confirmado."

                )


                if enviados > 0:

                    st.success(
                        "El encuentro fue confirmado y se envió la notificación."
                    )

                elif errores:

                    st.warning(
                        "El encuentro fue confirmado, pero Firebase no pudo enviar la notificación."
                    )

                    with st.expander("Ver error de Firebase"):

                        for error in errores:

                            st.code(error)

                else:

                    st.warning(
                        "El encuentro fue confirmado, pero no hay ningún token registrado."
                    )


                st.rerun()


            if st.button(
                "No",
                key="rechazar_encuentro"
            ):

                encuentro_ref.update({
                    "estado": "Rechazada"
                })


                enviados, errores = enviar_notificacion(

                    "Encuentros",

                    "La propuesta fue rechazada."

                )


                if enviados > 0:

                    st.success(
                        "La propuesta fue rechazada y se envió la notificación."
                    )

                elif errores:

                    st.warning(
                        "La propuesta fue rechazada, pero Firebase no pudo enviar la notificación."
                    )

                    with st.expander("Ver error de Firebase"):

                        for error in errores:

                            st.code(error)

                else:

                    st.warning(
                        "La propuesta fue rechazada, pero no hay ningún token registrado."
                    )


                st.rerun()


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

                st.divider()

                st.write(
                    "**Proponer otro horario**"
                )


                nueva_fecha = st.text_input(
                    "Nueva fecha",
                    placeholder="Ejemplo: 11/10/2026",
                    key="nueva_fecha"
                )


                nueva_hora = st.text_input(
                    "Nueva hora",
                    placeholder="Ejemplo: 19:00",
                    key="nueva_hora"
                )


                if st.button(
                    "Enviar nuevo horario",
                    key="enviar_nuevo_horario"
                ):

                    if not nueva_fecha or not nueva_hora:

                        st.warning(
                            "Completá la nueva fecha y la nueva hora."
                        )

                    else:

                        encuentro_ref.update({

                            "fecha": nueva_fecha,

                            "hora": nueva_hora,

                            "estado": "Nueva propuesta"

                        })


                        enviados, errores = enviar_notificacion(

                            "Encuentros",

                            "Se propuso un nuevo horario."

                        )


                        if enviados > 0:

                            st.success(
                                "El nuevo horario fue enviado y se envió la notificación."
                            )

                        elif errores:

                            st.warning(
                                "El nuevo horario fue guardado, pero Firebase no pudo enviar la notificación."
                            )

                            with st.expander("Ver error de Firebase"):

                                for error in errores:

                                    st.code(error)

                        else:

                            st.warning(
                                "El nuevo horario fue guardado, pero no hay ningún token registrado."
                            )


                        st.session_state[
                            "mostrar_otro_horario"
                        ] = False


                        st.rerun()


        elif estado_actual == "Confirmada":

            st.success(
                "Este encuentro ya está confirmado."
            )


        elif estado_actual == "Rechazada":

            st.warning(
                "Este encuentro fue rechazado."
            )


        elif estado_actual == "Nueva propuesta":

            st.info(
                "Hay un nuevo horario propuesto."
            )


    else:

        st.info(
            "Todavía no hay ningún encuentro propuesto."
        )


# ---------------------------------------------------------
# EXPLICACIÓN
# ---------------------------------------------------------

with st.expander(
    "¿Cómo funcionan las notificaciones?"
):

    st.write(
        "El celular obtiene un token de Firebase Cloud Messaging."
    )

    st.write(
        "Ese token se guarda de forma segura en Firestore."
    )

    st.write(
        "Cuando cambia el estado del encuentro, "
        "la aplicación envía una notificación mediante Firebase."
    )

    st.write(
        "Los estados utilizados son: Pendiente, "
        "Confirmada, Rechazada y Nueva propuesta."
    )
