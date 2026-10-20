"""Pantalla de inicio adaptable del Tótem Municipal (Kivy 2.x).

Diseño para teléfonos y tablets. Conserva los nombres de pantalla y los
métodos de navegación originales del proyecto.
"""
from datetime import datetime
from pathlib import Path

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def asset(nombre):
    return str(ASSETS_DIR / nombre)


AZUL_HEADER = (22 / 255, 50 / 255, 79 / 255, 1)
TURQUESA = (24 / 255, 166 / 255, 166 / 255, 1)
BLANCO = (1, 1, 1, 1)
GRIS = (0.25, 0.30, 0.37, 1)
FONDO = (242 / 255, 245 / 255, 248 / 255, 1)


def ajustar_texto(widget, *args):
    """Permite ajuste de línea dentro del espacio asignado al Label/Button."""
    widget.text_size = (max(0, widget.width - dp(4)), max(0, widget.height - dp(2)))


def fondo_redondeado(widget, color, radio=16):
    """Dibuja un fondo que acompaña el tamaño del widget."""
    with widget.canvas.before:
        Color(rgba=color)
        rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radio)])
    widget.bind(pos=lambda obj, value: setattr(rect, "pos", value))
    widget.bind(size=lambda obj, value: setattr(rect, "size", value))
    return rect


class TarjetaMunicipal(ButtonBehavior, BoxLayout):
    """Tarjeta táctil de contenido vertical, legible en anchos reducidos."""

    def __init__(self, titulo, subtitulo, icono, color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(8), dp(9), dp(8), dp(9)]
        self.spacing = dp(3)
        fondo_redondeado(self, color, radio=18)

        icono_path = ASSETS_DIR / icono
        if icono_path.is_file():
            imagen = Image(source=str(icono_path), size_hint=(1, 1))
        else:
            imagen = Label(text="●", color=BLANCO, font_size=sp(38), size_hint=(1, 1))
        self.add_widget(imagen)

        self.titulo_label = Label(
            text=titulo,
            font_size=sp(14),
            bold=True,
            color=BLANCO,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(47),
        )
        self.titulo_label.bind(size=ajustar_texto)
        self.add_widget(self.titulo_label)

        self.subtitulo_label = Label(
            text=subtitulo,
            font_size=sp(11),
            color=BLANCO,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(36),
        )
        self.subtitulo_label.bind(size=ajustar_texto)
        self.add_widget(self.subtitulo_label)
        self.bind(size=self._adaptar_tarjeta)
        Clock.schedule_once(self._adaptar_tarjeta, 0)

    def _adaptar_tarjeta(self, *args):
        estrecha = self.width < dp(175)
        baja = self.height < dp(160)
        self.titulo_label.font_size = sp(12.5 if estrecha else 17)
        self.titulo_label.height = dp(39 if estrecha else 52)
        self.subtitulo_label.font_size = sp(10 if estrecha else 13)
        self.subtitulo_label.height = dp(0 if baja else (33 if estrecha else 38))
        self.subtitulo_label.opacity = 0 if baja else 1


class InicioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=FONDO)
            self.fondo = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.actualizar_fondo, size=self.actualizar_fondo)

        self.principal = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(9),
        )
        self.add_widget(self.principal)

        # Encabezado: sin espacios manuales que desplacen el título.
        self.header = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(84),
            padding=[dp(12), dp(8), dp(12), dp(8)], spacing=dp(10),
        )
        fondo_redondeado(self.header, AZUL_HEADER, radio=18)

        logo_path = ASSETS_DIR / "logo_municipal.png"
        if logo_path.is_file():
            self.logo = Image(source=str(logo_path), size_hint_x=None, width=dp(60))
        else:
            self.logo = Label(text="M", font_size=sp(35), color=BLANCO,
                              bold=True, size_hint_x=None, width=dp(60))
        self.header.add_widget(self.logo)

        # El nombre del municipio se compone con dos renglones independientes
        # para que "MUNICIPALIDAD" no se corte en celulares estrechos.
        datos = BoxLayout(orientation="vertical", spacing=0)
        self.nombre_muni_1 = Label(
            text="MUNICIPALIDAD", font_size=sp(15), bold=True,
            color=BLANCO, halign="left", valign="middle",
        )
        self.nombre_muni_2 = Label(
            text="DE LA PINTANA", font_size=sp(15), bold=True,
            color=BLANCO, halign="left", valign="middle",
        )
        self.subtitulo_header = Label(
            text="Tótem de Atención Digital", font_size=sp(11),
            color=(0.88, 0.94, 1, 1), halign="left", valign="middle",
        )
        for etiqueta in (self.nombre_muni_1, self.nombre_muni_2, self.subtitulo_header):
            etiqueta.bind(size=ajustar_texto)
            datos.add_widget(etiqueta)
        self.header.add_widget(datos)

        self.frase_header = Label(
            text="La Pintana\nCon Todos", italic=True, font_size=sp(16),
            color=BLANCO, halign="right", valign="middle",
            size_hint_x=None, width=0,
        )
        self.frase_header.bind(size=ajustar_texto)
        self.header.add_widget(self.frase_header)
        self.principal.add_widget(self.header)

        self.titulo = Label(
            text="BIENVENIDO", color=AZUL_HEADER, bold=True,
            font_size=sp(29), size_hint_y=None, height=dp(46),
            halign="center", valign="middle",
        )
        self.principal.add_widget(self.titulo)
        self.mensaje = Label(
            text="Seleccione una opción para comenzar", color=GRIS,
            font_size=sp(15), size_hint_y=None, height=dp(30),
            halign="center", valign="middle",
        )
        self.mensaje.bind(size=ajustar_texto)
        self.principal.add_widget(self.mensaje)

        # La cuadrícula utiliza todo el espacio vertical disponible.
        from kivy.uix.gridlayout import GridLayout
        self.tarjetas = GridLayout(
            cols=2, spacing=dp(10), padding=[dp(2), dp(2), dp(2), dp(2)],
            size_hint_y=1,
        )
        opciones = [
            ("BENEFICIOS SOCIALES", "Solicitud de beneficios sociales",
             "icon_beneficios.png", TURQUESA, self.abrir_beneficios),
            ("RESERVAR HORA", "Agendar atención",
             "icon_reserva.png", TURQUESA, self.abrir_reserva),
            ("SOLICITUDES MUNICIPALES", "Solicitudes y requerimientos",
             "icon_solicitudes.png", TURQUESA, self.abrir_solicitudes),
            ("DENUNCIAS Y FISCALIZACIÓN", "Solicitudes de denuncias y fiscalización",
             "icon_denuncias.png", AZUL_HEADER, self.abrir_denuncias),
        ]
        for titulo, subtitulo, icono, color, accion in opciones:
            tarjeta = TarjetaMunicipal(
                titulo=titulo, subtitulo=subtitulo, icono=icono, color=color,
            )
            tarjeta.bind(on_release=accion)
            self.tarjetas.add_widget(tarjeta)
        self.principal.add_widget(self.tarjetas)

        # El pie se divide en información y acciones: nunca compiten por ancho.
        self.pie = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(88),
            padding=[dp(10), dp(6), dp(10), dp(6)], spacing=dp(4),
        )
        fondo_redondeado(self.pie, AZUL_HEADER, radio=16)
        informacion = BoxLayout(orientation="horizontal", size_hint_y=None,
                                height=dp(25), spacing=dp(8))
        self.label_hora = Label(
            text="00:00", color=BLANCO, bold=True, font_size=sp(14),
            size_hint_x=None, width=dp(55), halign="left", valign="middle",
        )
        self.label_hora.bind(size=ajustar_texto)
        informacion.add_widget(self.label_hora)
        self.label_fecha = Label(
            text="", color=BLANCO, font_size=sp(11),
            halign="right", valign="middle",
        )
        self.label_fecha.bind(size=ajustar_texto)
        informacion.add_widget(self.label_fecha)
        self.pie.add_widget(informacion)

        acciones = BoxLayout(orientation="horizontal", spacing=dp(8),
                             size_hint_y=1)
        self.boton_estado = Button(
            text="ESTADO DE MI SOLICITUD", color=BLANCO,
            font_size=sp(12), bold=True,
            background_normal="", background_down="",
            background_color=(0.12, 0.38, 0.53, 1),
            size_hint_x=0.73, halign="center", valign="middle",
        )
        self.boton_estado.bind(size=ajustar_texto, on_release=self.abrir_estado)
        acciones.add_widget(self.boton_estado)
        self.boton_ayuda = Button(
            text="AYUDA", color=BLANCO, font_size=sp(12), bold=True,
            background_normal="", background_down="",
            background_color=(0.12, 0.38, 0.53, 1),
            size_hint_x=0.27,
        )
        self.boton_ayuda.bind(on_release=self.mostrar_ayuda)
        acciones.add_widget(self.boton_ayuda)
        self.pie.add_widget(acciones)
        self.principal.add_widget(self.pie)

        # Aviso de derechos discreto, debajo de la barra de acciones.
        self.copyright_label = Label(
            text="© 2026 Sistema de Atención Ciudadana APT - Todos los derechos reservados",
            color=(0.38, 0.43, 0.49, 1),
            font_size=sp(9),
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        self.copyright_label.bind(size=ajustar_texto)
        self.principal.add_widget(self.copyright_label)

        self.bind(size=self.adaptar_pantalla)
        Clock.schedule_once(self.adaptar_pantalla, 0)
        Clock.schedule_interval(self.actualizar_fecha_hora, 1)
        self.actualizar_fecha_hora()

    def actualizar_fondo(self, *args):
        self.fondo.pos = self.pos
        self.fondo.size = self.size

    def adaptar_pantalla(self, *args):
        # dp() convierte tamaños lógicos a píxeles físicos de Android.
        ancho, alto = self.width, self.height
        telefono = ancho < dp(600)
        poca_altura = alto < dp(560)
        self.principal.padding = [dp(10), dp(8), dp(10), dp(8)] if telefono else [dp(24), dp(18), dp(24), dp(18)]
        self.principal.spacing = dp(7 if telefono else 13)
        self.header.height = dp(84 if telefono else 116)
        self.logo.width = dp(54 if telefono else 86)
        self.nombre_muni_1.font_size = sp(15 if telefono else 23)
        self.nombre_muni_2.font_size = sp(15 if telefono else 23)
        self.subtitulo_header.font_size = sp(11 if telefono else 15)
        self.frase_header.width = dp(0 if telefono else 145)
        self.frase_header.opacity = 0 if telefono else 1
        self.titulo.font_size = sp(26 if telefono else 36)
        self.titulo.height = dp(44 if telefono else 56)
        self.mensaje.font_size = sp(14 if telefono else 18)
        self.mensaje.height = dp(30 if telefono else 36)
        self.tarjetas.cols = 4 if ancho >= dp(850) and poca_altura else 2
        self.tarjetas.spacing = dp(10 if telefono else 18)
        self.pie.height = dp(85 if telefono else 92)
        self.copyright_label.font_size = sp(9 if telefono else 11)
        self.copyright_label.height = dp(28 if telefono else 22)
        self.boton_estado.font_size = sp(11 if telefono else 14)
        self.boton_ayuda.font_size = sp(11 if telefono else 14)
        self.actualizar_fecha_hora()

    def actualizar_fecha_hora(self, *args):
        ahora = datetime.now()
        self.label_hora.text = ahora.strftime("%H:%M")
        if self.width < dp(600):
            self.label_fecha.text = ahora.strftime("%d/%m/%Y")
        else:
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            self.label_fecha.text = (
                f"{dias[ahora.weekday()]}, {ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"
            )

    # Navegación del código original: mantiene los mismos destinos y categorías.
    def abrir_categoria(self, categoria):
        """Abre categoría; autenticación al registrar un trámite, si corresponde."""
        tramites = self.manager.get_screen("tramites")
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

    def mostrar_ayuda(self, *args):
        mensaje = Label(
            text="Seleccione un servicio para comenzar.\n"
                 "Use 'Estado de mi solicitud' para consultar su seguimiento.",
            halign="center", valign="middle", font_size=sp(15),
        )
        mensaje.bind(size=ajustar_texto)
        popup = Popup(
            title="Ayuda del Tótem Municipal", content=mensaje,
            size_hint=(0.85, None), height=dp(240), auto_dismiss=True,
        )
        popup.open()
