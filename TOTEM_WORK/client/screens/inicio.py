from pathlib import Path
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def asset(nombre):
    return str(ASSETS_DIR / nombre)


# ============================================================
# COLORES
# ============================================================

AZUL_HEADER = [22/255, 50/255, 79/255, 1]

AZUL_BENEFICIOS = [24/255, 166/255, 166/255, 1]
VERDE_RESERVA = [24/255, 166/255, 166/255, 1]
MORADO_SOLICITUDES = [24/255, 166/255, 166/255, 1]
NARANJO_DENUNCIAS = [22/255, 50/255, 79/255, 1]

AZUL_PIE = [22/255, 50/255, 79/255, 1]
AZUL_PIE_OSCURO = [22/255, 50/255, 79/255, 1]

BLANCO = [1, 1, 1, 1]
GRIS = [0.25, 0.30, 0.37, 1]

FONDO = [242/255, 245/255, 248/255, 1]


# ============================================================
# TARJETA MUNICIPAL
# ============================================================

class TarjetaMunicipal(ButtonBehavior, FloatLayout):

    def __init__(
        self,
        titulo,
        subtitulo,
        icono,
        color,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.color_tarjeta = color

        # ----------------------------------------------------
        # FONDO
        # ----------------------------------------------------

        with self.canvas.before:

            Color(
                rgba=color
            )

            self.fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ----------------------------------------------------
        # ICONO
        # ----------------------------------------------------

        icono_path = ASSETS_DIR / icono

        if icono_path.exists():

            imagen = Image(
                source=str(icono_path),
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                pos_hint={
                    "x": 0.04,
                    "center_y": 0.50
                },
                allow_stretch=True,
                keep_ratio=True
            )

            self.add_widget(imagen)

        else:

            # Si falta el archivo mostramos un símbolo
            imagen = Label(
                text="●",
                font_size=dp(55),
                bold=True,
                color=BLANCO,
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                pos_hint={
                    "x": 0.04,
                    "center_y": 0.50
                }
            )

            self.add_widget(imagen)

        # ----------------------------------------------------
        # SEPARADOR
        # ----------------------------------------------------

        separador = FloatLayout(
            size_hint=(None, None),
            size=(dp(2), dp(105)),
            pos_hint={
                "x": 0.20,
                "center_y": 0.50
            }
        )

        with separador.canvas:

            Color(
                rgba=[
                    1,
                    1,
                    1,
                    0.45
                ]
            )

            Rectangle(
                pos=separador.pos,
                size=separador.size
            )

        self.add_widget(separador)

        # ----------------------------------------------------
        # TITULO
        # ----------------------------------------------------

        titulo_label = Label(
            text=titulo,
            font_size=dp(21),
            bold=True,
            color=BLANCO,
            halign="left",
            valign="middle",
            size_hint=(0.60, 0.35),
            pos_hint={
                "x": 0.24,
                "y": 0.48
            }
        )

        titulo_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        self.add_widget(
            titulo_label
        )

        # ----------------------------------------------------
        # SUBTITULO
        # ----------------------------------------------------

        subtitulo_label = Label(
            text=subtitulo,
            font_size=dp(15),
            color=[
                0.95,
                0.98,
                1,
                1
            ],
            halign="left",
            valign="top",
            size_hint=(0.60, 0.30),
            pos_hint={
                "x": 0.24,
                "y": 0.18
            }
        )

        subtitulo_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        self.add_widget(
            subtitulo_label
        )

        # ----------------------------------------------------
        # FLECHA
        # ----------------------------------------------------

        flecha = Label(
            text="›",
            font_size=dp(50),
            bold=True,
            color=BLANCO,
            halign="center",
            valign="middle",
            size_hint=(0.10, 0.45),
            pos_hint={
                "x": 0.86,
                "center_y": 0.50
            }
        )

        flecha.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        self.add_widget(
            flecha
        )

    # ========================================================
    # ACTUALIZAR FONDO
    # ========================================================

    def actualizar_fondo(
        self,
        *args
    ):

        self.fondo.pos = self.pos
        self.fondo.size = self.size


# ============================================================
# PANTALLA INICIO
# ============================================================

class InicioScreen(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        # ====================================================
        # FONDO
        # ====================================================

        with self.canvas.before:

            Color(
                rgba=FONDO
            )

            self.fondo = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ====================================================
        # CONTENEDOR PRINCIPAL
        # ====================================================

        principal = BoxLayout(
            orientation="vertical",
            padding=[
                dp(25),
                dp(18)
            ],
            spacing=dp(10)
        )

        # ====================================================
        # ENCABEZADO
        # ====================================================

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(120),
            padding=[
                dp(25),
                dp(10)
            ]
        )

        with header.canvas.before:

            Color(
                rgba=AZUL_HEADER
            )

            header.fondo = RoundedRectangle(
                pos=header.pos,
                size=header.size,
                radius=[dp(18)]
            )

        header.bind(
            pos=lambda obj, value:
            setattr(
                obj.fondo,
                "pos",
                value
            ),
            size=lambda obj, value:
            setattr(
                obj.fondo,
                "size",
                value
            )
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo_path = ASSETS_DIR / "logo_municipal.png"

        if logo_path.exists():

            logo = Image(
                source=str(logo_path),
                size_hint_x=0.27,
                allow_stretch=True,
                keep_ratio=True
            )

            header.add_widget(
                logo
            )

        else:

            nombre_municipio = Label(
                text="BIENVENIDOS",
                font_size=dp(26),
                bold=True,
                color=BLANCO,
                halign="left",
                valign="middle",
                size_hint_x=0.35
            )

            nombre_municipio.bind(
                size=lambda obj, value:
                setattr(
                    obj,
                    "text_size",
                    value
                )
            )

            header.add_widget(
                nombre_municipio
            )

        # ----------------------------------------------------
        # TEXTO CENTRAL
        # ----------------------------------------------------

        datos = BoxLayout(
            orientation="vertical",
            size_hint_x=0.48
        )

        titulo_header = Label(
            text="                       MUNICIPALIDAD DE LA PINTANA",
            font_size=dp(25),
            bold=True,
            color=BLANCO,
            halign="left",
            valign="middle"
        )

        titulo_header.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        subtitulo_header = Label(
            text="                                   Totem de Atención Digital",
            font_size=dp(17),
            color=[
                0.88,
                0.94,
                1,
                1
            ],
            halign="left",
            valign="top"
        )

        subtitulo_header.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        datos.add_widget(
            titulo_header
        )

        datos.add_widget(
            subtitulo_header
        )

        header.add_widget(
            datos
        )

        # ----------------------------------------------------
        # LOGO MUNICIPAL Y FRASE
        # ----------------------------------------------------

        marca_municipal = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.25,
            spacing=dp(10)
        )

        logo_municipal_path = ASSETS_DIR / "logo_municipLLal.png"
        if logo_municipal_path.exists():
            logo_municipal = Image(
                source=str(logo_municipal_path),
                size_hint=(None, None),
                size=(dp(90), dp(90)),
                pos_hint={"center_y": 0.5},
                allow_stretch=True,
                keep_ratio=True
            )
            marca_municipal.add_widget(logo_municipal)

        frase = Label(
            text="La Pintana\n Con Todos",
            font_size=dp(18),
            italic=True,
            color=BLANCO,
            halign="right",
            valign="middle"
        )
        frase.bind(
            size=lambda obj, value: setattr(obj, "text_size", value)
        )
        marca_municipal.add_widget(frase)
        header.add_widget(marca_municipal)

        principal.add_widget(
            header
        )

        # ====================================================
        # TITULO
        # ====================================================

        titulo = Label(
            text="BIENVENIDO",
            font_size=dp(38),
            bold=True,
            color=AZUL_HEADER,
            size_hint_y=None,
            height=dp(60)
        )

        principal.add_widget(
            titulo
        )

        # ====================================================
        # SUBTITULO
        # ====================================================

        mensaje = Label(
            text="Seleccione una opción para comenzar",
            font_size=dp(19),
            color=GRIS,
            size_hint_y=None,
            height=dp(35)
        )

        principal.add_widget(
            mensaje
        )

        # ====================================================
        # TARJETAS
        # ====================================================

        tarjetas = GridLayout(
            cols=2,
            spacing=dp(18),
            padding=[
                dp(8),
                dp(5)
            ],
            size_hint_y=1
        )

        # ----------------------------------------------------
        # BENEFICIOS
        # ----------------------------------------------------

        beneficios = TarjetaMunicipal(
            titulo="BENEFICIOS SOCIALES",
            subtitulo="Solicitud de beneficios sociales",
            icono="icon_beneficios.png",
            color=AZUL_BENEFICIOS
        )

        beneficios.bind(
            on_release=self.abrir_beneficios
        )

        tarjetas.add_widget(
            beneficios
        )

        # ----------------------------------------------------
        # RESERVAR
        # ----------------------------------------------------

        reservar = TarjetaMunicipal(
            titulo="RESERVAR HORA",
            subtitulo="Agendar atención",
            icono="icon_reserva.png",
            color=VERDE_RESERVA
        )

        reservar.bind(
            on_release=self.abrir_reserva
        )

        tarjetas.add_widget(
            reservar
        )

        # ----------------------------------------------------
        # SOLICITUDES
        # ----------------------------------------------------

        solicitudes = TarjetaMunicipal(
            titulo="SOLICITUDES MUNICIPALES",
            subtitulo="Solicitudes y requerimientos",
            icono="icon_solicitudes.png",
            color=MORADO_SOLICITUDES
        )

        solicitudes.bind(
            on_release=self.abrir_solicitudes
        )

        tarjetas.add_widget(
            solicitudes
        )

        # ----------------------------------------------------
        # DENUNCIAS
        # ----------------------------------------------------

        denuncias = TarjetaMunicipal(
            titulo="DENUNCIAS Y FISCALIZACIÓN",
            subtitulo="Solicitudes de denuncias y fiscalización",
            icono="icon_denuncias.png",
            color=NARANJO_DENUNCIAS
        )

        denuncias.bind(
            on_release=self.abrir_denuncias
        )

        tarjetas.add_widget(
            denuncias
        )

        principal.add_widget(
            tarjetas
        )

        # ====================================================
        # PIE DE PÁGINA
        # ====================================================

        pie = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(68),
            spacing=dp(8),
            padding=[
                dp(8),
                dp(5)
            ]
        )

        with pie.canvas.before:

            Color(
                rgba=AZUL_PIE
            )

            pie.fondo = RoundedRectangle(
                pos=pie.pos,
                size=pie.size,
                radius=[dp(16)]
            )

        pie.bind(
            pos=lambda obj, value:
            setattr(
                obj.fondo,
                "pos",
                value
            ),
            size=lambda obj, value:
            setattr(
                obj.fondo,
                "size",
                value
            )
        )

        # ====================================================
        # HORA
        # ====================================================

        reloj = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.13,
            spacing=dp(5)
        )

        self.label_hora = Label(
            text="00:00",
            font_size=dp(17),
            bold=True,
            color=BLANCO
        )

        reloj.add_widget(
            self.label_hora
        )

        pie.add_widget(
            reloj
        )

        # ====================================================
        # FECHA
        # ====================================================

        calendario = BoxLayout(
            orientation="horizontal",
            size_hint_x=0.37,
            spacing=dp(5)
        )

        self.label_fecha = Label(
            text="",
            font_size=dp(12),
            color=BLANCO,
            halign="left",
            valign="middle"
        )

        self.label_fecha.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        calendario.add_widget(
            self.label_fecha
        )

        pie.add_widget(
            calendario
        )

        # ====================================================
        # ESTADO
        # ====================================================

        estado = Button(
            text="ESTADO DE MI SOLICITUD",
            font_size=dp(14),
            bold=True,
            color=BLANCO,
            background_normal="",
            background_down="",
            background_color=AZUL_PIE_OSCURO,
            size_hint_x=0.32
        )

        estado.bind(
            on_release=self.abrir_estado
        )

        pie.add_widget(
            estado
        )

        # ====================================================
        # AYUDA
        # ====================================================

        ayuda = Button(
            text="?   AYUDA",
            font_size=dp(13),
            bold=True,
            color=BLANCO,
            background_normal="",
            background_down="",
            background_color=AZUL_PIE_OSCURO,
            size_hint_x=0.18
        )

        ayuda.bind(
            on_release=self.mostrar_ayuda
        )

        pie.add_widget(
            ayuda
        )

        principal.add_widget(
            pie
        )

        # ====================================================
        # AGREGAR A LA PANTALLA
        # ====================================================

        self.add_widget(
            principal
        )

        # ====================================================
        # RELOJ
        # ====================================================

        Clock.schedule_interval(
            self.actualizar_fecha_hora,
            1
        )

        self.actualizar_fecha_hora()

    # ========================================================
    # FECHA Y HORA
    # ========================================================

    def actualizar_fecha_hora(
        self,
        *args
    ):

        ahora = datetime.now()

        self.label_hora.text = ahora.strftime(
            "%H:%M"
        )

        dias = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo"
        }

        meses = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre"
        }

        self.label_fecha.text = (
            f"{dias[ahora.weekday()]}, "
            f"{ahora.day} de "
            f"{meses[ahora.month]} de "
            f"{ahora.year}"
        )

    # ========================================================
    # NAVEGACIÓN
    # ========================================================

    def abrir_categoria(self, categoria):
        """Abre directamente la categoría elegida, sin exigir inicio de sesión.

        La autenticación se solicita al final del trámite, justo antes de
        registrar/enviar la solicitud cuando el trámite lo requiere.
        """
        tramites = self.manager.get_screen("tramites")

        # Limpiar los datos de una navegación anterior para no recuperar
        # accidentalmente un trámite o formulario previo.
        tramites.tramite_actual = None
        tramites.categoria_actual = ""
        tramites.archivo = None
        tramites.checks = {}
        tramites.horarios = []
        if hasattr(tramites, "archivos_eda"):
            tramites.archivos_eda = {"cedula": None, "avaluo": None, "otro": None}

        tramites.mostrar_categoria(categoria)
        self.manager.current = "tramites"

    def abrir_beneficios(self, *args):
        print("ABRIENDO BENEFICIOS SOCIALES")
        self.abrir_categoria("Beneficios Sociales")

    def abrir_reserva(self, *args):
        print("ABRIENDO RESERVA DE HORA")
        self.abrir_categoria("Reservar Hora")

    def abrir_solicitudes(self, *args):
        print("ABRIENDO SOLICITUDES MUNICIPALES")
        self.abrir_categoria("Solicitudes Municipales")

    def abrir_denuncias(self, *args):
        print("ABRIENDO DENUNCIAS Y FISCALIZACIÓN")
        autenticacion = self.manager.get_screen("autenticacion")
        autenticacion.usuario = None
        autenticacion.usuario_id = None
        autenticacion.tramite_codigo = ""
        autenticacion.tramite_nombre = ""
        self.abrir_categoria("Denuncias y Fiscalización")

    def abrir_estado(self, *args):
        print("ABRIENDO ESTADO DE SOLICITUD")
        self.manager.current = "seguimiento"

    # ========================================================
    # AYUDA
    # ========================================================

    def mostrar_ayuda(
        self,
        *args
    ):

        print(
            "AYUDA SELECCIONADA"
        )

    # ========================================================
    # FONDO
    # ========================================================

    def actualizar_fondo(
        self,
        *args
    ):

        self.fondo.pos = self.pos
        self.fondo.size = self.size