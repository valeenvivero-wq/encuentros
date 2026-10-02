import streamlit as st
import streamlit.components.v1 as components

import firebase_admin
from firebase_admin import credentials, firestore

# ============================================================

# CONFIGURACIÓN DE LA PÁGINA

# ============================================================

st.set_page_config(
page_title="Encuentros",
page_icon="📅",
layout="centered"
)

# ============================================================

# CONECTAR CON FIREBASE

# ============================================================

if not firebase_admin._apps:

```
datos_firebase = dict(st.secrets["firebase"])

datos_firebase["private_key"] = datos_firebase["private_key"].replace(
    "\\n",
    "\n"
)

cred = credentials.Certificate(datos_firebase)

firebase_admin.initialize_app(cred)
```

db = firestore.client()

# Documento compartido

encuentro_ref = db.collection("encuentros").document("actual")

# ============================================================

# TÍTULO

# ============================================================

st.title("Encuentros")

st.write(
"Proponé un encuentro, respondé una propuesta "
"o consultá el estado actual."
)

# ============================================================

# NOTIFICACIONES DEL NAVEGADOR

# ============================================================

st.subheader("Notificaciones")

components.html(
""" <!DOCTYPE html>

```
<html>

<head>

    <style>

        body {
            font-family: sans-serif;
            margin: 0;
        }

        button {
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
        }

        #estado {
            margin-top: 10px;
            font-size: 14px;
        }

    </style>

</head>

<body>

    <button id="activar">
        Activar notificaciones
    </button>

    <div id="estado"></div>


    <script>

        const boton = document.getElementById("activar");
        const estado = document.getElementById("estado");


        function actualizarEstado() {

            if (!("Notification" in window)) {

                estado.innerText =
                    "Este navegador no permite notificaciones.";

                boton.disabled = true;

                return;
            }


            if (Notification.permission === "granted") {

                estado.innerText =
                    "Notificaciones activadas.";

                boton.innerText =
                    "Notificaciones activadas";

            }


            else if (Notification.permission === "denied") {

                estado.innerText =
                    "Las notificaciones están bloqueadas. "
                    + "Tenés que habilitarlas desde la configuración "
                    + "del navegador.";

                boton.innerText =
                    "Notificaciones bloqueadas";

            }

        }


        boton.addEventListener("click", async function() {

            if (!("Notification" in window)) {

                estado.innerText =
                    "Este navegador no permite notificaciones.";

                return;

            }


            try {

                const permiso =
                    await Notification.requestPermission();


                if (permiso === "granted") {

                    estado.innerText =
                        "Notificaciones activadas.";

                    boton.innerText =
                        "Notificaciones activadas";


                    new Notification(
                        "Encuentros",
                        {
                            body:
                                "Las notificaciones están activadas."
                        }
                    );

                }


                else if (permiso === "denied") {

                    estado.innerText =
                        "Las notificaciones están bloqueadas.";

                }


                else {

                    estado.innerText =
                        "No se activaron las notificaciones.";

                }

            }

            catch (error) {

                estado.innerText =
                    "No se pudieron activar las notificaciones.";

                console.error(error);

            }

        });


        actualizarEstado();

    </script>

</body>

</html>
""",
height=120
```

)

st.divider()

# ============================================================

# LEER ENCUENTRO ACTUAL

# ============================================================

documento = encuentro_ref.get()

if documento.exists:

```
propuesta = documento.to_dict()

estado_actual = propuesta.get(
    "estado",
    "Pendiente"
)
```

else:

```
propuesta = None

estado_actual = None
```

# ============================================================

# AVISOS SEGÚN EL ESTADO

# ============================================================

if propuesta:

```
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
```

# ============================================================

# BOTÓN ACTUALIZAR

# ============================================================

if st.button(
"Actualizar",
key="actualizar"
):

```
st.rerun()
```

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

# PROPONER UN ENCUENTRO

# ============================================================

if modo == "Proponer un encuentro":

```
st.subheader(
    "Proponer un encuentro"
)


fecha = st.text_input(
    "Fecha",
    placeholder="Ejemplo: 5 de octubre",
    key="fecha_propuesta"
)


hora = st.text_input(
    "Hora",
    placeholder="Ejemplo: 20:30",
    key="hora_propuesta"
)


lugar = st.text_input(
    "Lugar",
    placeholder="Ejemplo: Costanera",
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


        st.success(
            "Propuesta enviada correctamente."
        )


        st.rerun()
```

# ============================================================

# RESPONDER A UN ENCUENTRO

# ============================================================

elif modo == "Responder a un encuentro":

```
st.subheader(
    "Propuesta recibida"
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


    st.subheader(
        "¿Podés encontrarte en ese momento?"
    )


    # ====================================================
    # SÍ
    # ====================================================

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


    # ====================================================
    # NO
    # ====================================================

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


    # ====================================================
    # OTRO HORARIO
    # ====================================================

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
            placeholder="Ejemplo: 6 de octubre",
            key="nueva_fecha"
        )


        nueva_hora = st.text_input(
            "Nueva hora",
            placeholder="Ejemplo: 21:00",
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
