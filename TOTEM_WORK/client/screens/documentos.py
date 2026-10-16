from pathlib import Path

from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

from screens.estilo_totem import (
    CELESTE, BLANCO, GRIS, VERDE, aplicar_fondo, crear_cabecera
)


class DocumentosScreen(Screen):
    EXTENSIONES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.codigo_tramite = None
        self.tramite_nombre = ""
        self.run = ""
        self.descripcion = ""
        self.archivos_seleccionados = []
        self._popup_archivos = None

        aplicar_fondo(self)
        principal = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(20), dp(28), dp(20)],
            spacing=dp(12)
        )
        principal.add_widget(crear_cabecera("Documentación para su trámite"))

        principal.add_widget(Label(
            text="DOCUMENTACIÓN DE RESPALDO", color=CELESTE,
            bold=True, font_size=dp(26), size_hint_y=None, height=dp(50)
        ))
        self.tramite_label = Label(
            text="Trámite seleccionado", color=BLANCO,
            font_size=dp(19), size_hint_y=None, height=dp(35)
        )
        principal.add_widget(self.tramite_label)
        principal.add_widget(Label(
            text="Formatos permitidos: PDF, JPG, JPEG y PNG",
            color=BLANCO, font_size=dp(17),
            size_hint_y=None, height=dp(35)
        ))

        self.lista_archivos = Label(
            text="Todavía no ha seleccionado documentos.",
            color=BLANCO, font_size=dp(16),
            halign="left", valign="top"
        )
        self.lista_archivos.bind(
            size=lambda obj, val: setattr(obj, "text_size", val)
        )
        principal.add_widget(self.lista_archivos)

        self.mensaje = Label(
            text="", color=CELESTE, font_size=dp(15),
            size_hint_y=None, height=dp(36)
        )
        principal.add_widget(self.mensaje)

        acciones = GridLayout(cols=2, spacing=dp(12),
                              size_hint_y=None, height=dp(62))
        adjuntar = Button(
            text="SELECCIONAR ARCHIVOS", font_size=dp(17),
            background_normal="", background_color=CELESTE,
            color=(0.025, 0.075, 0.13, 1)
        )
        adjuntar.bind(on_release=self.abrir_selector)
        acciones.add_widget(adjuntar)

        continuar = Button(
            text="CONTINUAR", font_size=dp(18),
            background_normal="", background_color=VERDE, color=BLANCO
        )
        continuar.bind(on_release=self.continuar)
        acciones.add_widget(continuar)
        principal.add_widget(acciones)

        volver = Button(
            text="VOLVER AL FORMULARIO", font_size=dp(17),
            size_hint_y=None, height=dp(52),
            background_normal="", background_color=GRIS, color=BLANCO
        )
        volver.bind(on_release=self.volver)
        principal.add_widget(volver)
        self.add_widget(principal)

    def on_pre_enter(self, *args):
        self.tramite_label.text = (
            f"Trámite: {self.tramite_nombre or self.codigo_tramite or 'No seleccionado'}"
        )
        self.actualizar_lista()

    def abrir_selector(self, *_):
        contenido = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        selector = FileChooserListView(
            path=str(Path.home()),
            filters=["*.pdf", "*.PDF", "*.jpg", "*.JPG", "*.jpeg",
                     "*.JPEG", "*.png", "*.PNG"],
            multiselect=True
        )
        contenido.add_widget(selector)

        acciones = GridLayout(cols=2, spacing=dp(8),
                              size_hint_y=None, height=dp(50))
        agregar = Button(text="AGREGAR", background_normal="",
                         background_color=CELESTE,
                         color=(0.025, 0.075, 0.13, 1))
        cancelar = Button(text="CANCELAR", background_normal="",
                          background_color=GRIS, color=BLANCO)
        acciones.add_widget(agregar)
        acciones.add_widget(cancelar)
        contenido.add_widget(acciones)

        popup = Popup(
            title="Seleccionar documentos", content=contenido,
            size_hint=(0.92, 0.9), auto_dismiss=False,
            separator_color=CELESTE
        )
        self._popup_archivos = popup

        def agregar_seleccion(_):
            seleccion = selector.selection or []
            if not seleccion:
                self.mensaje.text = "Seleccione al menos un archivo."
                return
            omitidos = []
            for ruta in seleccion:
                archivo = Path(ruta)
                if not archivo.is_file():
                    continue
                if archivo.suffix.lower() not in self.EXTENSIONES_PERMITIDAS:
                    omitidos.append(archivo.name)
                    continue
                if ruta not in self.archivos_seleccionados:
                    self.archivos_seleccionados.append(ruta)
            popup.dismiss()
            self.actualizar_lista()
            self.mensaje.text = (
                f"{len(self.archivos_seleccionados)} archivo(s) seleccionado(s)."
                if not omitidos else
                "Se omitieron archivos de formato no permitido."
            )

        agregar.bind(on_release=agregar_seleccion)
        cancelar.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def actualizar_lista(self):
        if not self.archivos_seleccionados:
            self.lista_archivos.text = "Todavía no ha seleccionado documentos."
            return
        self.lista_archivos.text = "Documentos seleccionados:\n" + "\n".join(
            f"{i}. {Path(ruta).name}"
            for i, ruta in enumerate(self.archivos_seleccionados, start=1)
        )

    def continuar(self, *_):
        if not self.codigo_tramite:
            self.mensaje.text = "No se identificó el trámite."
            return
        if not self.descripcion.strip():
            self.mensaje.text = "Falta la descripción del formulario."
            return
        if not self.manager or not self.manager.has_screen("confirmacion"):
            self.mensaje.text = "No está disponible la pantalla de confirmación."
            return

        auth = self.manager.get_screen("autenticacion")
        usuario = getattr(auth, "usuario", None) or {}
        run = usuario.get("run", "") if isinstance(usuario, dict) else ""
        run = run or getattr(auth, "run", "") or ""

        confirmacion = self.manager.get_screen("confirmacion")
        confirmacion.configurar(
            codigo_tramite=self.codigo_tramite,
            run=run,
            descripcion=self.descripcion
        )
        confirmacion.archivos_seleccionados = list(self.archivos_seleccionados)
        self.manager.current = "confirmacion"

    def volver(self, *_):
        if self.manager and self.manager.has_screen("formulario"):
            self.manager.current = "formulario"
