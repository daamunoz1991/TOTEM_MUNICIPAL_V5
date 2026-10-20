"""Consulta de solicitudes del prototipo Tótem Municipal APT.

Diseño adaptable a celular y tablet, conservando la consulta existente
mediante ClienteAPI().consultar_solicitud(codigo).
"""

from datetime import datetime

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from api.cliente_api import ClienteAPI


AZUL = (22 / 255, 50 / 255, 79 / 255, 1)
TURQUESA = (24 / 255, 166 / 255, 166 / 255, 1)
FONDO = (242 / 255, 245 / 255, 248 / 255, 1)
BLANCO = (1, 1, 1, 1)
GRIS = (0.36, 0.41, 0.46, 1)
VERDE = (0.12, 0.48, 0.34, 1)
AMBAR = (0.55, 0.35, 0.08, 1)
ROJO = (0.69, 0.19, 0.23, 1)


class SeguimientoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*FONDO)
            self._fondo = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

        self._scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self._centrador = AnchorLayout(
            anchor_x="center", anchor_y="top", size_hint=(1, None)
        )
        self._contenido = BoxLayout(
            orientation="vertical", spacing=dp(14),
            padding=(0, dp(18), 0, dp(24)), size_hint=(None, None)
        )
        self._contenido.bind(minimum_height=self._contenido.setter("height"))
        self._contenido.bind(height=self._ajustar_alto_centrador)
        self._centrador.add_widget(self._contenido)
        self._scroll.add_widget(self._centrador)
        self.add_widget(self._scroll)
        self.bind(width=self._ajustar_ancho)

        # Encabezado consistente con la identidad visual del resto de la APK.
        encabezado = BoxLayout(
            orientation="vertical", padding=[dp(12), dp(10)],
            spacing=dp(1), size_hint_y=None, height=dp(80)
        )
        self._redondear(encabezado, AZUL, dp(13))
        encabezado.add_widget(self._etiqueta(
            "MUNICIPALIDAD DE LA PINTANA", sp(18), BLANCO,
            negrita=True, altura=dp(34), centrar=True
        ))
        encabezado.add_widget(self._etiqueta(
            "Tótem de Atención Digital Municipal", sp(12),
            (0.78, 0.91, 0.94, 1), altura=dp(23), centrar=True
        ))
        self._contenido.add_widget(encabezado)

        self._contenido.add_widget(self._etiqueta(
            "CONSULTA DE SOLICITUD", sp(22), AZUL,
            negrita=True, altura=dp(40), centrar=True
        ))

        # Tarjeta de búsqueda.
        formulario = BoxLayout(
            orientation="vertical", padding=dp(16),
            spacing=dp(10), size_hint_y=None, height=dp(176)
        )
        self._redondear(formulario, BLANCO, dp(12))
        formulario.add_widget(self._etiqueta(
            "CÓDIGO DE SEGUIMIENTO", sp(14), AZUL,
            negrita=True, altura=dp(25)
        ))
        self.codigo_input = TextInput(
            hint_text="Ejemplo: TM-XXXXXXXXXX", multiline=False,
            font_size=sp(17), size_hint_y=None, height=dp(48),
            foreground_color=AZUL, hint_text_color=(0.5, 0.53, 0.56, 1),
            background_normal="", background_active="", background_color=FONDO,
            padding=[dp(12), dp(12), dp(12), dp(8)],
            write_tab=False
        )
        self.codigo_input.bind(on_text_validate=self.consultar)
        formulario.add_widget(self.codigo_input)
        formulario.add_widget(self._boton(
            "CONSULTAR SOLICITUD", self.consultar, TURQUESA, dp(47)
        ))
        self._contenido.add_widget(formulario)

        self._mensaje = self._etiqueta("", sp(14), ROJO, altura=0, centrar=True)
        self._mensaje.bind(texture_size=self._actualizar_altura_mensaje)
        self._contenido.add_widget(self._mensaje)

        # Esta zona solo ocupa espacio cuando hay un resultado.
        self._zona_resultado = BoxLayout(
            orientation="vertical", spacing=dp(10),
            size_hint_y=None, height=0
        )
        self._zona_resultado.bind(
            minimum_height=self._zona_resultado.setter("height")
        )
        self._contenido.add_widget(self._zona_resultado)
        self._contenido.add_widget(self._boton(
            "VOLVER AL INICIO", self.volver, AZUL, dp(51)
        ))

        Clock.schedule_once(self._ajustar_ancho, 0)

    @staticmethod
    def _redondear(widget, color, radio):
        with widget.canvas.before:
            Color(*color)
            rect = RoundedRectangle(
                pos=widget.pos, size=widget.size, radius=[radio]
            )
        widget.bind(
            pos=lambda obj, valor: setattr(rect, "pos", valor),
            size=lambda obj, valor: setattr(rect, "size", valor)
        )

    @staticmethod
    def _etiqueta(texto, tamano, color, negrita=False, altura=dp(28), centrar=False):
        etiqueta = Label(
            text=str(texto), font_size=tamano, color=color, bold=negrita,
            size_hint_y=None, height=altura,
            halign="center" if centrar else "left", valign="middle"
        )
        etiqueta.bind(
            size=lambda obj, valor: setattr(obj, "text_size", (valor[0], None))
        )
        return etiqueta

    @staticmethod
    def _boton(texto, callback, color, altura):
        boton = Button(
            text=texto, font_size=sp(16), bold=True,
            size_hint_y=None, height=altura,
            background_normal="", background_down="",
            background_color=color, color=BLANCO
        )
        boton.bind(on_release=callback)
        return boton

    def _actualizar_fondo(self, *_):
        self._fondo.pos = self.pos
        self._fondo.size = self.size

    def _ajustar_ancho(self, *_):
        # Se centra y nunca ocupa más de 640 dp en la tablet.
        ancho = self.width if self.width > 1 else dp(360)
        self._contenido.width = min(dp(640), max(dp(200), ancho - dp(28)))
        self._ajustar_alto_centrador()

    def _ajustar_alto_centrador(self, *_):
        self._centrador.height = self._contenido.height

    def _actualizar_altura_mensaje(self, *_):
        if not self._mensaje.text:
            self._mensaje.height = 0
        else:
            self._mensaje.height = max(dp(36), self._mensaje.texture_size[1] + dp(12))

    def _mostrar_mensaje(self, texto, error=True):
        self._mensaje.color = ROJO if error else VERDE
        self._mensaje.text = texto
        self._actualizar_altura_mensaje()

    @staticmethod
    def _fecha_legible(valor):
        if not valor:
            return "No informada"
        texto = str(valor)
        try:
            fecha = datetime.fromisoformat(texto.replace("Z", "+00:00"))
            if fecha.tzinfo is not None:
                fecha = fecha.astimezone()  # Hora local del celular/tablet.
            return fecha.strftime("%d/%m/%Y  %H:%M")
        except ValueError:
            return texto

    @staticmethod
    def _estado_color(estado):
        nombre = str(estado or "").casefold()
        if any(termino in nombre for termino in ("rechaz", "cancel")):
            return ROJO
        if any(termino in nombre for termino in ("progreso", "pendiente", "revisi")):
            return AMBAR
        return VERDE

    def _dato(self, titulo, valor):
        grupo = BoxLayout(
            orientation="vertical", spacing=dp(2),
            size_hint_y=None, height=dp(63)
        )
        grupo.add_widget(self._etiqueta(
            titulo.upper(), sp(12), GRIS, altura=dp(20)
        ))
        texto = self._etiqueta(
            str(valor).strip() if valor not in (None, "") else "No informado",
            sp(16), AZUL, negrita=True, altura=dp(39)
        )

        def ajustar_texto(*_):
            texto.height = max(dp(36), texto.texture_size[1] + dp(6))
            grupo.height = dp(22) + texto.height

        texto.bind(width=ajustar_texto, texture_size=ajustar_texto)
        grupo.add_widget(texto)
        Clock.schedule_once(ajustar_texto, 0)
        return grupo

    def _mostrar_solicitud(self, solicitud, codigo_buscado):
        self._zona_resultado.clear_widgets()
        tarjeta = BoxLayout(
            orientation="vertical", padding=dp(16),
            spacing=dp(10), size_hint_y=None
        )
        tarjeta.bind(minimum_height=tarjeta.setter("height"))
        self._redondear(tarjeta, BLANCO, dp(12))

        tarjeta.add_widget(self._etiqueta(
            "SOLICITUD ENCONTRADA", sp(18), TURQUESA,
            negrita=True, altura=dp(35)
        ))

        estado = str(solicitud.get("estado") or "Sin estado")
        indicador = AnchorLayout(
            anchor_x="left", anchor_y="center",
            size_hint_y=None, height=dp(40)
        )
        estado_widget = Label(
            text="ESTADO: " + estado.upper(),
            font_size=sp(14), bold=True, color=BLANCO,
            size_hint=(None, None), width=dp(190), height=dp(34),
            halign="center", valign="middle"
        )
        estado_widget.bind(
            size=lambda obj, valor: setattr(obj, "text_size", valor)
        )
        self._redondear(estado_widget, self._estado_color(estado), dp(9))
        indicador.add_widget(estado_widget)
        tarjeta.add_widget(indicador)

        tarjeta.add_widget(self._dato(
            "Código de ticket", solicitud.get("codigo_solicitud") or codigo_buscado
        ))
        tarjeta.add_widget(self._dato(
            "Trámite", solicitud.get("nombre_tramite")
        ))
        tarjeta.add_widget(self._dato(
            "Fecha de ingreso", self._fecha_legible(solicitud.get("fecha_solicitud"))
        ))
        tarjeta.add_widget(self._dato(
            "Departamento", solicitud.get("departamento")
        ))
        self._zona_resultado.add_widget(tarjeta)

    def consultar(self, *_):
        codigo = self.codigo_input.text.strip().upper()
        self._zona_resultado.clear_widgets()
        self._mostrar_mensaje("")

        if not codigo:
            self._mostrar_mensaje("Ingrese el código de su solicitud.")
            return

        try:
            # Misma llamada a la API que tenía la pantalla original.
            respuesta = ClienteAPI().consultar_solicitud(codigo)
            if not isinstance(respuesta, dict):
                self._mostrar_mensaje("El servidor devolvió una respuesta inesperada.")
                return
            if respuesta.get("ok") is False:
                self._mostrar_mensaje(
                    str(respuesta.get("error") or "No se encontró la solicitud.")
                )
                return
            self._mostrar_solicitud(respuesta, codigo)
            self._mostrar_mensaje("")
        except Exception as error:
            print("ERROR AL CONSULTAR:", repr(error))
            self._mostrar_mensaje(
                "No fue posible consultar la solicitud. "
                "Verifique la conexión con el servidor e inténtelo nuevamente."
            )

    def volver(self, *_):
        self.manager.current = "inicio"
