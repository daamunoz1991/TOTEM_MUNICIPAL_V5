from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from screens.estilo_totem import (
    AZUL_MARINO, AZUL_PANEL, CELESTE, BLANCO, GRIS, VERDE,
    aplicar_fondo, crear_cabecera
)


class FormularioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tramite_codigo = None
        self.tramite_nombre = ""
        self.usuario_id = None
        self.descripcion_guardada = ""

        aplicar_fondo(self)

        principal = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(20), dp(28), dp(20)],
            spacing=dp(13)
        )
        principal.add_widget(crear_cabecera())

        principal.add_widget(Label(
            text="FORMULARIO DE SOLICITUD", color=CELESTE,
            bold=True, font_size=dp(27), size_hint_y=None, height=dp(52)
        ))
        self.tramite_label = Label(
            text="Trámite seleccionado", color=BLANCO,
            font_size=dp(20), size_hint_y=None, height=dp(38)
        )
        principal.add_widget(self.tramite_label)
        principal.add_widget(Label(
            text="Describa brevemente el motivo de su solicitud",
            color=BLANCO, font_size=dp(18),
            size_hint_y=None, height=dp(36)
        ))
        self.descripcion = TextInput(
            hint_text="Escriba aquí su solicitud...",
            multiline=True, font_size=dp(19),
            foreground_color=(0.08, 0.12, 0.16, 1),
            background_color=(0.96, 0.98, 1, 1),
            cursor_color=(0.0, 0.45, 0.65, 1),
            padding=dp(14)
        )
        principal.add_widget(self.descripcion)

        self.mensaje = Label(
            text="", color=CELESTE, font_size=dp(16),
            size_hint_y=None, height=dp(38)
        )
        principal.add_widget(self.mensaje)

        acciones = BoxLayout(
            size_hint_y=None, height=dp(62), spacing=dp(12)
        )
        continuar = Button(
            text="CONTINUAR", font_size=dp(19),
            background_normal="", background_color=VERDE,
            color=BLANCO
        )
        continuar.bind(on_release=self.continuar)
        acciones.add_widget(continuar)

        volver = Button(
            text="VOLVER", font_size=dp(18),
            background_normal="", background_color=GRIS,
            color=BLANCO
        )
        volver.bind(on_release=self.volver)
        acciones.add_widget(volver)
        principal.add_widget(acciones)
        self.add_widget(principal)

    def on_pre_enter(self, *args):
        if not self.manager:
            return
        if self.manager.has_screen("autenticacion"):
            auth = self.manager.get_screen("autenticacion")
            self.tramite_codigo = getattr(auth, "tramite_codigo", None)
            self.tramite_nombre = getattr(auth, "tramite_nombre", "") or ""
            self.usuario_id = getattr(auth, "usuario_id", None)
            self.tramite_label.text = (
                f"Trámite: {self.tramite_nombre or self.tramite_codigo or 'No seleccionado'}"
            )
        # Mantener la descripción al volver desde la pantalla de documentos.
        if self.descripcion_guardada and not self.descripcion.text.strip():
            self.descripcion.text = self.descripcion_guardada

    def continuar(self, *_):
        descripcion = self.descripcion.text.strip()
        if not self.tramite_codigo:
            self.mensaje.text = "No se identificó el trámite. Vuelva a seleccionarlo."
            return
        if not self.usuario_id:
            self.mensaje.text = "Debe iniciar sesión para continuar."
            return
        if not descripcion:
            self.mensaje.text = "Debe ingresar una descripción."
            return
        if len(descripcion) > 2000:
            self.mensaje.text = "La descripción no puede superar 2.000 caracteres."
            return
        if not self.manager or not self.manager.has_screen("documentos"):
            self.mensaje.text = "La pantalla de documentos no está disponible."
            return

        self.descripcion_guardada = descripcion
        documentos = self.manager.get_screen("documentos")
        documentos.codigo_tramite = self.tramite_codigo
        documentos.tramite_nombre = self.tramite_nombre
        documentos.descripcion = descripcion
        if not hasattr(documentos, "archivos_seleccionados"):
            documentos.archivos_seleccionados = []

        self.mensaje.text = ""
        self.manager.current = "documentos"

    def volver(self, *_):
        if self.manager and self.manager.has_screen("tramites"):
            self.manager.current = "tramites"
