from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from kivy.graphics import Color, RoundedRectangle

from kivy.metrics import dp

from api.cliente_api import ClienteAPI


# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = [0.95, 0.96, 0.97, 1]

COLOR_HEADER = [0.10, 0.25, 0.40, 1]

COLOR_PRINCIPAL = [0.10, 0.45, 0.65, 1]

COLOR_SECUNDARIO = [0.20, 0.35, 0.50, 1]

COLOR_TEXTO = [0.10, 0.12, 0.15, 1]

COLOR_SUBTITULO = [0.35, 0.38, 0.42, 1]

COLOR_ERROR = [0.75, 0.15, 0.15, 1]

COLOR_EXITO = [0.10, 0.50, 0.25, 1]


# ============================================================
# REGISTRO
# ============================================================

class RegistroScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

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

        principal = BoxLayout(
            orientation="vertical",
            padding=[
                dp(15),
                dp(12),
                dp(15),
                dp(10)
            ],
            spacing=dp(7)
        )

        # ====================================================
        # ENCABEZADO
        # ====================================================

        encabezado = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(90),
            padding=[
                dp(15),
                dp(7)
            ]
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
            size_hint_y=None,
            height=dp(38)
        )

        subtitulo = Label(
            text="Atención Digital Municipal",
            font_size=dp(16),
            color=[0.88, 0.92, 0.96, 1],
            size_hint_y=None,
            height=dp(27)
        )

        encabezado.add_widget(nombre)
        encabezado.add_widget(subtitulo)

        principal.add_widget(encabezado)

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = Label(
            text="CREAR CUENTA",
            font_size=dp(32),
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(50)
        )

        principal.add_widget(titulo)

        # ====================================================
        # SUBTÍTULO
        # ====================================================

        mensaje = Label(
            text=(
                "Complete sus datos para registrarse "
                "en Atención Digital Municipal"
            ),
            font_size=dp(18),
            color=COLOR_SUBTITULO,
            size_hint_y=None,
            height=dp(40)
        )

        principal.add_widget(mensaje)

        # ====================================================
        # SCROLL
        # ====================================================

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8)
        )

        formulario = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[
                dp(5),
                dp(5),
                dp(5),
                dp(20)
            ],
            size_hint_y=None
        )

        formulario.bind(
            minimum_height=formulario.setter(
                "height"
            )
        )

        # ====================================================
        # NOMBRE
        # ====================================================

        self.input_nombre = self.crear_campo(
            formulario,
            "Nombre",
            "Ingrese su nombre"
        )

        # ====================================================
        # APELLIDO
        # ====================================================

        self.input_apellido = self.crear_campo(
            formulario,
            "Apellido",
            "Ingrese su apellido"
        )

        # ====================================================
        # RUT
        # ====================================================

        self.input_rut = self.crear_campo(
            formulario,
            "RUT",
            "Ejemplo: 12.345.678-5"
        )

        # Formato automático del RUT: 12.345.678-5
        self.input_rut.bind(
            text=self.formatear_rut
        )

        # ====================================================
        # CONTRASEÑA
        # ====================================================

        self.input_password = self.crear_campo(
            formulario,
            "Contraseña",
            "Mínimo 6 caracteres",
            password=True
        )

        # ====================================================
        # CONTACTO
        # ====================================================

        self.input_contacto = self.crear_campo(
            formulario,
            "Contacto",
            "Ejemplo: +56912345678"
        )

        # ====================================================
        # DIRECCIÓN
        # ====================================================

        self.input_direccion = self.crear_campo(
            formulario,
            "Dirección",
            "Ingrese su dirección"
        )

        # ====================================================
        # CORREO
        # ====================================================

        self.input_correo = self.crear_campo(
            formulario,
            "Correo electrónico",
            "ejemplo@correo.cl"
        )

        scroll.add_widget(formulario)

        principal.add_widget(scroll)

        # ====================================================
        # MENSAJE RESULTADO
        # ====================================================

        self.mensaje_resultado = Label(
            text="",
            font_size=dp(15),
            bold=True,
            color=COLOR_ERROR,
            size_hint_y=None,
            height=dp(30)
        )

        principal.add_widget(
            self.mensaje_resultado
        )

        # ====================================================
        # REGISTRAR
        # ====================================================

        registrar = Button(
            text="REGISTRAR CUENTA",
            font_size=dp(19),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_PRINCIPAL,
            size_hint_y=None,
            height=dp(55)
        )

        registrar.bind(
            on_release=self.registrar
        )

        principal.add_widget(registrar)

        # ====================================================
        # VOLVER
        # ====================================================

        volver = Button(
            text="VOLVER",
            font_size=dp(18),
            bold=True,
            color=[1, 1, 1, 1],
            background_normal="",
            background_down="",
            background_color=COLOR_HEADER,
            size_hint_y=None,
            height=dp(50)
        )

        volver.bind(
            on_release=self.volver
        )

        principal.add_widget(volver)

        self.add_widget(principal)

    # ========================================================
    # FORMATEAR RUT AUTOMÁTICAMENTE
    # ========================================================

    def formatear_rut(self, instance, valor):

        # Eliminar puntos, guiones y espacios
        rut = valor.replace(".", "").replace("-", "").replace(" ", "")

        # Convertir a mayúscula para aceptar K
        rut = rut.upper()

        # Permitir solamente números y K
        rut = "".join(
            caracter
            for caracter in rut
            if caracter.isdigit() or caracter == "K"
        )

        # Máximo 9 caracteres: 8 dígitos + dígito verificador
        rut = rut[:9]

        if len(rut) <= 1:
            formato = rut

        else:
            cuerpo = rut[:-1]
            verificador = rut[-1]

            partes = []

            while len(cuerpo) > 3:
                partes.insert(0, cuerpo[-3:])
                cuerpo = cuerpo[:-3]

            if cuerpo:
                partes.insert(0, cuerpo)

            cuerpo_formateado = ".".join(partes)
            formato = cuerpo_formateado + "-" + verificador

        # Evitar ciclo infinito al modificar el texto
        if instance.text != formato:
            instance.text = formato
            instance.cursor = (len(formato), 0)

    # ========================================================
    # CREAR CAMPO
    # ========================================================

    def crear_campo(
        self,
        contenedor,
        etiqueta,
        texto_ayuda,
        password=False
    ):

        label = Label(
            text=etiqueta,
            font_size=dp(16),
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(27),
            halign="left"
        )

        contenedor.add_widget(label)

        campo = TextInput(
            hint_text=texto_ayuda,
            font_size=dp(18),
            multiline=False,
            password=password,
            size_hint_y=None,
            height=dp(52),
            padding=[
                dp(15),
                dp(12)
            ]
        )

        contenedor.add_widget(campo)

        return campo

    # ========================================================
    # REGISTRAR USUARIO
    # ========================================================

    def registrar(self, *args):

        nombre = self.input_nombre.text.strip()

        apellido = self.input_apellido.text.strip()

        rut = self.input_rut.text.strip()

        password = self.input_password.text

        contacto = self.input_contacto.text.strip()

        direccion = self.input_direccion.text.strip()

        correo = self.input_correo.text.strip()

        # ----------------------------------------------------
        # VALIDACIONES
        # ----------------------------------------------------

        if not nombre:

            self.mostrar_error(
                "Debe ingresar su nombre."
            )

            return

        if not apellido:

            self.mostrar_error(
                "Debe ingresar su apellido."
            )

            return

        if not rut:

            self.mostrar_error(
                "Debe ingresar su RUT."
            )

            return

        if not password:

            self.mostrar_error(
                "Debe ingresar una contraseña."
            )

            return

        if len(password) < 6:

            self.mostrar_error(
                "La contraseña debe tener al menos 6 caracteres."
            )

            return

        if not contacto:

            self.mostrar_error(
                "Debe ingresar un contacto."
            )

            return

        if not direccion:

            self.mostrar_error(
                "Debe ingresar su dirección."
            )

            return

        if not correo:

            self.mostrar_error(
                "Debe ingresar su correo electrónico."
            )

            return

        # ----------------------------------------------------
        # REGISTRAR
        # ----------------------------------------------------

        try:

            print("========================================")
            print("INTENTANDO REGISTRAR USUARIO")
            print("RUT:", rut)
            print("========================================")

            # =================================================
            # API
            # =================================================
            # La pantalla NO accede a SQLite.
            # El flujo es:
            # Kivy -> ClienteAPI -> FastAPI -> consultas.py -> BD

            cliente = ClienteAPI()

            respuesta = cliente.registrar_usuario(
                nombre=nombre,
                apellido=apellido,
                run=rut,
                password=password,
                contacto=contacto,
                direccion=direccion,
                correo=correo
            )

            if isinstance(respuesta, dict) and respuesta.get("ok") is False:

                informacion = respuesta.get(
                    "error",
                    "No fue posible registrar la cuenta."
                )

                print(
                    "ERROR AL REGISTRAR:",
                    informacion
                )

                self.mostrar_error(
                    str(informacion)
                )

                return

            # ------------------------------------------------
            # CORRECTO
            # ------------------------------------------------

            if isinstance(respuesta, dict) and respuesta.get("id"):

                print("✓ USUARIO REGISTRADO CORRECTAMENTE")

                self.mensaje_resultado.text = (
                    "✓ CUENTA CREADA CORRECTAMENTE"
                )

                self.mensaje_resultado.color = COLOR_EXITO

                self.limpiar_formulario()

                # Después de registrar, volver a autenticación
                # para que el usuario pueda iniciar sesión.
                self.manager.current = "autenticacion"

            else:

                print(
                    "ERROR AL REGISTRAR: "
                    "respuesta inesperada del servidor"
                )

                self.mostrar_error(
                    "El servidor no confirmó el registro."
                )

        except Exception as error:

            # IMPORTANTE:
            # No permitir que un error de conexión/API/Kivy
            # cierre completamente la aplicación.
            print("========================================")
            print("ERROR CRÍTICO AL REGISTRAR USUARIO")
            print(repr(error))
            print("========================================")

            self.mostrar_error(
                "No fue posible registrar la cuenta. "
                "Revise los datos o intente nuevamente."
            )

    # ========================================================
    # ERROR
    # ========================================================

    def mostrar_error(self, mensaje):

        self.mensaje_resultado.text = (
            "⚠ " + mensaje
        )

        self.mensaje_resultado.color = COLOR_ERROR

    # ========================================================
    # LIMPIAR
    # ========================================================

    def limpiar_formulario(self):

        self.input_nombre.text = ""

        self.input_apellido.text = ""

        self.input_rut.text = ""

        self.input_password.text = ""

        self.input_contacto.text = ""

        self.input_direccion.text = ""

        self.input_correo.text = ""

    # ========================================================
    # VOLVER
    # ========================================================

    def volver(self, *args):

        self.manager.current = "autenticacion"

    # ========================================================
    # FONDO
    # ========================================================

    def actualizar_fondo(self, *args):

        self.fondo.pos = self.pos

        self.fondo.size = self.size