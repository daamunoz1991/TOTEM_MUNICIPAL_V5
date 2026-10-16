from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.graphics import Color, RoundedRectangle

from kivy.metrics import dp

from api.cliente_api import cliente_api


# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = [242/255, 245/255, 248/255, 1]

COLOR_HEADER = [22/255, 50/255, 79/255, 1]

COLOR_PRINCIPAL = [24/255, 166/255, 166/255, 1]

COLOR_SECUNDARIO = [22/255, 50/255, 79/255, 1]

COLOR_TEXTO = [0.10, 0.12, 0.15, 1]

COLOR_SUBTITULO = [0.35, 0.38, 0.42, 1]

COLOR_ERROR = [0.75, 0.15, 0.15, 1]


# ============================================================
# AUTENTICACIÓN
# ============================================================

class AutenticacionScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pantalla_origen = "tramites"
        self.pantalla_destino = "formulario"

        self.tramite_codigo = ""

        self.tramite_nombre = ""

        self.usuario_id = None

        self.usuario = None

        # ----------------------------------------------------
        # FONDO
        # ----------------------------------------------------

        with self.canvas.before:

            Color(
                rgba=COLOR_FONDO
            )

            self.fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ----------------------------------------------------
        # CONTENEDOR
        # ----------------------------------------------------

        principal = FloatLayout()

        # ====================================================
        # ENCABEZADO
        # ====================================================

        encabezado = FloatLayout(
            size_hint=(0.96, None),
            height=dp(90),
            pos_hint={
                "center_x": 0.5,
                "top": 0.98
            }
        )

        with encabezado.canvas.before:

            Color(
                rgba=COLOR_HEADER
            )

            encabezado.rect = RoundedRectangle(
                pos=encabezado.pos,
                size=encabezado.size,
                radius=[dp(18)]
            )

        encabezado.bind(
            pos=lambda obj, value:
                setattr(
                    obj.rect,
                    "pos",
                    value
                ),

            size=lambda obj, value:
                setattr(
                    obj.rect,
                    "size",
                    value
                )
        )

        nombre = Label(
            text="MUNICIPALIDAD DE LA PINTANA",
            font_size=dp(23),
            bold=True,
            color=[1, 1, 1, 1],
            size_hint=(0.90, None),
            height=dp(38),
            pos_hint={
                "x": 0.04,
                "top": 0.78
            }
        )

        encabezado.add_widget(nombre)

        subtitulo = Label(
            text="Atención Digital Municipal",
            font_size=dp(16),
            color=[0.88, 0.92, 0.96, 1],
            size_hint=(0.90, None),
            height=dp(28),
            pos_hint={
                "x": 0.04,
                "top": 0.40
            }
        )

        encabezado.add_widget(subtitulo)

        principal.add_widget(encabezado)

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = Label(
            text="IDENTIFICACIÓN DEL USUARIO",
            font_size=dp(32),
            bold=True,
            color=COLOR_TEXTO,
            size_hint=(0.90, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.78
            }
        )

        principal.add_widget(titulo)

        # ====================================================
        # MENSAJE
        # ====================================================

        self.mensaje = Label(
            text=(
                "Ingrese su RUT y contraseña para continuar"
            ),
            font_size=dp(20),
            color=COLOR_SUBTITULO,
            size_hint=(0.90, None),
            height=dp(45),
            pos_hint={
                "center_x": 0.5,
                "top": 0.68
            }
        )

        principal.add_widget(
            self.mensaje
        )

        # ====================================================
        # RUT
        # ====================================================

        self.input_rut = TextInput(
            hint_text="RUT: 12.345.678-5",
            font_size=dp(20),
            multiline=False,
            size_hint=(0.92, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.57
            },
            padding=[
                dp(15),
                dp(15)
            ]
        )

        principal.add_widget(
            self.input_rut
        )

        # ====================================================
        # CONTRASEÑA
        # ====================================================

        self.input_password = TextInput(
            hint_text="Contraseña",
            font_size=dp(20),
            multiline=False,
            password=True,
            size_hint=(0.92, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.45
            },
            padding=[
                dp(15),
                dp(15)
            ]
        )

        principal.add_widget(
            self.input_password
        )

        # ====================================================
        # INGRESAR
        # ====================================================

        ingresar = Button(
            text="INGRESAR",
            font_size=dp(19),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_PRINCIPAL,
            size_hint=(0.92, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.34
            }
        )

        ingresar.bind(
            on_release=self.ingresar_usuario
        )

        principal.add_widget(
            ingresar
        )

        # ====================================================
        # CREAR CUENTA
        # ====================================================

        crear = Button(
            text="CREAR CUENTA",
            font_size=dp(18),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_SECUNDARIO,
            size_hint=(0.92, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.23
            }
        )

        crear.bind(
            on_release=self.crear_cuenta
        )

        principal.add_widget(
            crear
        )

        # ====================================================
        # VOLVER Y ATRÁS
        # ====================================================

        botones_navegacion = BoxLayout(
            size_hint=(0.92, None),
            height=dp(60),
            pos_hint={
                "center_x": 0.5,
                "top": 0.12
            },
            spacing=dp(10)
        )

        atras = Button(
            text="ATRÁS",
            font_size=dp(18),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_SECUNDARIO,
            size_hint_x=0.5
        )
        atras.bind(on_release=self.atras)

        volver = Button(
            text="VOLVER",
            font_size=dp(18),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_HEADER,
            size_hint_x=0.5
        )
        volver.bind(on_release=self.volver)

        botones_navegacion.add_widget(atras)
        botones_navegacion.add_widget(volver)

        principal.add_widget(botones_navegacion)

        self.add_widget(principal)

    # ========================================================
    # CREAR CUENTA
    # ========================================================

    def crear_cuenta(self, *args):

        print(
            "BOTÓN CREAR CUENTA PRESIONADO"
        )

        try:

            self.manager.current = "registro"

            print(
                "Pantalla actual:",
                self.manager.current
            )

        except Exception as error:

            print(
                "ERROR AL ABRIR REGISTRO:",
                repr(error)
            )

    # ========================================================
    # INGRESAR USUARIO
    # ========================================================

    def ingresar_usuario(self, *args):

        rut = self.input_rut.text.strip()

        password = self.input_password.text

        # ----------------------------------------------------
        # VALIDAR RUT
        # ----------------------------------------------------

        if not rut:

            self.mensaje.text = (
                "Debe ingresar su RUT."
            )

            self.mensaje.color = COLOR_ERROR

            return

        # ----------------------------------------------------
        # VALIDAR PASSWORD
        # ----------------------------------------------------

        if not password:

            self.mensaje.text = (
                "Debe ingresar su contraseña."
            )

            self.mensaje.color = COLOR_ERROR

            return

        # ----------------------------------------------------
        # CONSULTAR
        # ----------------------------------------------------

        try:

            print("========================================")
            print("INTENTANDO AUTENTICAR USUARIO")
            print("RUT:", rut)
            print("========================================")

            # =================================================
            # API
            # =================================================
            # La pantalla NO accede a SQLite.
            # El flujo es:
            # Kivy -> ClienteAPI -> FastAPI -> consultas.py -> BD

         
            respuesta = cliente_api.login(
                rut,
                password
            )

            if isinstance(respuesta, dict) and respuesta.get("ok") is False:

                print(
                    "AUTENTICACIÓN FALLIDA:",
                    respuesta.get("error")
                )

                self.mensaje.text = (
                    respuesta.get(
                        "error",
                        "RUT o contraseña incorrectos."
                    )
                )

                self.mensaje.color = COLOR_ERROR

                return

            # ------------------------------------------------
            # CORRECTO
            # ------------------------------------------------

            usuario = (
                respuesta.get("usuario")
                if isinstance(respuesta, dict)
                else None
            )

            if usuario:

                print(
                    "✓ USUARIO AUTENTICADO CORRECTAMENTE"
                )

                print(
                    "RUT:",
                    usuario.get("run")
                )

                print(
                    "NOMBRE:",
                    usuario.get("nombre")
                )

                self.usuario_id = usuario.get("id")

                self.usuario = usuario

                self.mensaje.text = (
                    f"Bienvenido/a "
                    f"{usuario.get('nombre', '')} "
                    f"{usuario.get('apellido', '')}"
                )

                self.mensaje.color = COLOR_PRINCIPAL

                # -------------------------------------------
                # CONTINUAR
                # -------------------------------------------

                destino = self.pantalla_destino
                self.pantalla_origen = "tramites"
                self.pantalla_destino = "formulario"
                self.input_password.text = ""
                self.manager.current = destino

                # Si el usuario llegó aquí después de completar un trámite,
                # enviar el formulario que quedó guardado antes del login.
                if destino == "tramites" and self.manager.has_screen("tramites"):
                    pantalla_tramites = self.manager.get_screen("tramites")
                    if getattr(pantalla_tramites, "pending_submission", None):
                        pantalla_tramites.procesar_pendiente(usuario)

            else:

                print(
                    "AUTENTICACIÓN FALLIDA: "
                    "respuesta inesperada del servidor"
                )

                self.mensaje.text = (
                    "RUT o contraseña incorrectos."
                )

                self.mensaje.color = COLOR_ERROR

        except Exception as error:

            # IMPORTANTE:
            # Un error de conexión/API no debe cerrar Kivy.
            print("========================================")
            print("ERROR CRÍTICO AL AUTENTICAR")
            print(repr(error))
            print("========================================")

            self.mensaje.text = (
                "No fue posible iniciar sesión. "
                "Revise la conexión con el servidor municipal."
            )

            self.mensaje.color = COLOR_ERROR

    # ========================================================
    # VOLVER Y ATRÁS
    # ========================================================

    def atras(self, *args):
        """Vuelve al formulario del trámite actual."""
        if self.manager:
            self.input_password.text = ""
            # Volver a la pantalla de trámites, que mostrará el formulario
            # del trámite actual porque tramite_actual sigue configurado
            self.manager.current = "tramites"

    def volver(self, *args):
        """Vuelve a la pantalla de origen (categorías)."""
        if self.manager:
            origen = self.pantalla_origen
            self.pantalla_origen = "tramites"
            self.pantalla_destino = "formulario"
            self.input_password.text = ""
            self.manager.current = origen

    # ========================================================
    # FONDO
    # ========================================================

    def actualizar_fondo(self, *args):

        self.fondo.pos = self.pos

        self.fondo.size = self.size