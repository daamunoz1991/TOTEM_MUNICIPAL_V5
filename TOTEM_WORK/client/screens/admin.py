"""
Panel de Administración.

La pantalla Kivy se comunica con FastAPI.
No accede directamente a SQLite.

NOTA:
La protección de este panel con LDAP/JWT/roles se incorporará
en la siguiente etapa para funcionarios municipales.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from api.cliente_api import ClienteAPI


COLOR_FONDO = [0.95, 0.96, 0.97, 1]
COLOR_HEADER = [0.10, 0.25, 0.40, 1]
COLOR_PRINCIPAL = [0.10, 0.45, 0.65, 1]
COLOR_TEXTO = [0.10, 0.12, 0.15, 1]
COLOR_ERROR = [0.75, 0.15, 0.15, 1]
COLOR_EXITO = [0.10, 0.50, 0.25, 1]


class AdminScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(rgba=COLOR_FONDO)
            self.fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        encabezado = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=[dp(20), dp(10)]
        )

        with encabezado.canvas.before:
            Color(rgba=COLOR_HEADER)
            encabezado.rect = RoundedRectangle(
                pos=encabezado.pos,
                size=encabezado.size,
                radius=[dp(15)]
            )

        encabezado.bind(
            pos=lambda obj, value: setattr(
                encabezado.rect, "pos", value
            ),
            size=lambda obj, value: setattr(
                encabezado.rect, "size", value
            )
        )

        titulo = Label(
            text="PANEL DE ADMINISTRACIÓN",
            font_size=dp(24),
            bold=True,
            color=[1, 1, 1, 1]
        )

        encabezado.add_widget(titulo)
        principal.add_widget(encabezado)

        seccion = Label(
            text="Solicitudes Pendientes",
            font_size=dp(20),
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(40)
        )
        principal.add_widget(seccion)

        self.lista = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10)
        )
        self.lista.bind(
            minimum_height=self.lista.setter("height")
        )

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.lista)
        principal.add_widget(scroll)

        actualizar = Button(
            text="ACTUALIZAR SOLICITUDES",
            size_hint_y=None,
            height=dp(55)
        )
        actualizar.bind(on_release=self.cargar_solicitudes)
        principal.add_widget(actualizar)

        self.mensaje = Label(
            text="",
            size_hint_y=None,
            height=dp(40)
        )
        principal.add_widget(self.mensaje)

        volver = Button(
            text="VOLVER",
            size_hint_y=None,
            height=dp(55)
        )
        volver.bind(
            on_release=lambda *_: setattr(
                self.manager, "current", "inicio"
            )
        )
        principal.add_widget(volver)

        self.add_widget(principal)

    def on_pre_enter(self, *args):
        self.cargar_solicitudes()

    def cargar_solicitudes(self, *args):
        self.lista.clear_widgets()

        try:
            respuesta = ClienteAPI().listar_solicitudes()

            if respuesta.get("ok") is False:
                self.mensaje.text = respuesta.get(
                    "error",
                    "No fue posible obtener las solicitudes."
                )
                self.mensaje.color = COLOR_ERROR
                return

            solicitudes = respuesta.get(
                "solicitudes",
                respuesta if isinstance(respuesta, list) else []
            )

            if not solicitudes:
                self.lista.add_widget(
                    Label(
                        text="No hay solicitudes pendientes.",
                        size_hint_y=None,
                        height=dp(60)
                    )
                )
                self.mensaje.text = ""
                return

            for solicitud in solicitudes:
                codigo = solicitud.get(
                    "codigo_solicitud",
                    ""
                )
                estado = solicitud.get(
                    "estado",
                    ""
                )

                fila = BoxLayout(
                    size_hint_y=None,
                    height=dp(75),
                    spacing=dp(8)
                )

                info = Label(
                    text=(
                        f"{codigo}\n"
                        f"Estado: {estado}"
                    ),
                    color=COLOR_TEXTO
                )

                spinner = Spinner(
                    text=estado or "INGRESADA",
                    values=[
                        "INGRESADA",
                        "EN_REVISION",
                        "EN_PROCESO",
                        "RESUELTA",
                        "RECHAZADA",
                    ],
                    size_hint_x=0.35
                )

                boton = Button(
                    text="ACTUALIZAR",
                    size_hint_x=0.30
                )

                boton.bind(
                    on_release=lambda btn, c=codigo, sp=spinner:
                    self.actualizar_estado(c, sp.text)
                )

                fila.add_widget(info)
                fila.add_widget(spinner)
                fila.add_widget(boton)
                self.lista.add_widget(fila)

            self.mensaje.text = ""

        except Exception as error:
            print("ERROR ADMIN:", repr(error))
            self.mensaje.text = (
                "No fue posible conectar con el servidor municipal."
            )
            self.mensaje.color = COLOR_ERROR

    def actualizar_estado(self, codigo, estado):
        respuesta = ClienteAPI().actualizar_estado(
            codigo,
            estado
        )

        if respuesta.get("ok") is False:
            self.mensaje.text = respuesta.get(
                "error",
                "No fue posible actualizar el estado."
            )
            self.mensaje.color = COLOR_ERROR
            return

        self.mensaje.text = "✓ Estado actualizado correctamente."
        self.mensaje.color = COLOR_EXITO
        self.cargar_solicitudes()

    def actualizar_fondo(self, *args):
        self.fondo.pos = self.pos
        self.fondo.size = self.size
