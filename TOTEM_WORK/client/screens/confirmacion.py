from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from screens.estilo_totem import (
    CELESTE, BLANCO, GRIS, VERDE, aplicar_fondo, crear_cabecera
)
from api.cliente_api import cliente_api


class ConfirmacionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.codigo_tramite = None
        self.nombre_tramite = ""
        self.tramite_id = None
        self.usuario_id = None
        self.run = ""
        self.descripcion = ""
        self.archivos_seleccionados = []
        self.solicitud_registrada = False
        self.codigo_solicitud = None
        self.enviando = False
        self._evento_regreso = None

        aplicar_fondo(self)
        principal = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(20), dp(28), dp(20)],
            spacing=dp(12)
        )
        principal.add_widget(crear_cabecera())

        self.titulo = Label(
            text="CONFIRMAR SOLICITUD", color=CELESTE,
            bold=True, font_size=dp(27),
            size_hint_y=None, height=dp(52)
        )
        principal.add_widget(self.titulo)

        self.informacion = Label(
            text="", color=BLANCO, font_size=dp(18),
            halign="left", valign="top"
        )
        self.informacion.bind(
            size=lambda obj, val: setattr(obj, "text_size", val)
        )
        principal.add_widget(self.informacion)

        self.mensaje = Label(
            text="", color=CELESTE, font_size=dp(16),
            size_hint_y=None, height=dp(60)
        )
        principal.add_widget(self.mensaje)

        self.btn_enviar = Button(
            text="CONFIRMAR Y ENVIAR", font_size=dp(19),
            size_hint_y=None, height=dp(62),
            background_normal="", background_color=VERDE, color=BLANCO
        )
        self.btn_enviar.bind(on_release=self.enviar)
        principal.add_widget(self.btn_enviar)

        self.btn_inicio = Button(
            text="VOLVER AL INICIO", font_size=dp(17),
            size_hint_y=None, height=dp(52),
            background_normal="", background_color=GRIS, color=BLANCO,
            disabled=True
        )
        self.btn_inicio.bind(on_release=self.volver_inicio)
        principal.add_widget(self.btn_inicio)
        self.add_widget(principal)

    def configurar(self, codigo_tramite, run, descripcion):
        self.codigo_tramite = codigo_tramite
        self.run = run or ""
        self.descripcion = descripcion or ""
        self.tramite_id = None
        self.codigo_solicitud = None
        self.solicitud_registrada = False
        self.enviando = False

        if self._evento_regreso:
            self._evento_regreso.cancel()
            self._evento_regreso = None

        self.btn_enviar.disabled = False
        self.btn_enviar.text = "CONFIRMAR Y ENVIAR"
        self.btn_inicio.disabled = True
        self.titulo.text = "CONFIRMAR SOLICITUD"
        self.mensaje.text = ""

        auth = self.manager.get_screen("autenticacion")
        self.usuario_id = getattr(auth, "usuario_id", None)
        self.nombre_tramite = (
            getattr(auth, "tramite_nombre", None) or codigo_tramite or "Trámite municipal"
        )

        try:
            respuesta = cliente_api.obtener_tramite(codigo_tramite)
            if isinstance(respuesta, dict) and respuesta.get("ok") is not False:
                self.tramite_id = respuesta.get("id")
                self.nombre_tramite = (
                    respuesta.get("nombre")
                    or respuesta.get("nombre_tramite")
                    or self.nombre_tramite
                )
        except Exception as error:
            print("No se pudo consultar el trámite:", repr(error))

        archivos = self.archivos_seleccionados
        listado = "\n".join(
            f"- {ruta.replace(chr(92), '/').split('/')[-1]}"
            for ruta in archivos
        ) if archivos else "No se adjuntaron documentos."

        self.informacion.text = (
            "Revise los antecedentes antes de enviar.\n\n"
            f"Trámite: {self.nombre_tramite}\n"
            f"RUN: {self.run or 'No disponible'}\n\n"
            f"Descripción:\n{self.descripcion}\n\n"
            f"Documentos seleccionados:\n{listado}\n\n"
            "¿Desea enviar la solicitud?"
        )

    def enviar(self, *_):
        if self.enviando or self.solicitud_registrada:
            return
        if not self.usuario_id:
            self.mensaje.text = "Debe iniciar sesión antes de enviar."
            return
        if not self.codigo_tramite:
            self.mensaje.text = "No se ha seleccionado un trámite."
            return
        if not self.descripcion.strip():
            self.mensaje.text = "Debe ingresar una descripción."
            return

        self.enviando = True
        self.btn_enviar.disabled = True
        self.btn_enviar.text = "ENVIANDO SOLICITUD..."
        self.mensaje.text = "Enviando al servidor municipal..."

        try:
            respuesta = cliente_api.crear_solicitud(
                usuario_id=int(self.usuario_id),
                tramite_id=self.tramite_id,
                codigo_tramite=self.codigo_tramite,
                descripcion=self.descripcion.strip()
            )

            if not isinstance(respuesta, dict) or respuesta.get("ok") is False:
                error = (
                    respuesta.get("error") or respuesta.get("detail")
                    or "No fue posible registrar la solicitud."
                ) if isinstance(respuesta, dict) else "Respuesta no válida del servidor."
                self.mensaje.text = f"No se pudo guardar:\n{error}"
                self.btn_enviar.disabled = False
                self.btn_enviar.text = "REINTENTAR ENVÍO"
                return

            codigo = respuesta.get("codigo_solicitud")
            if not codigo:
                self.mensaje.text = (
                    "El servidor no devolvió el código de solicitud. "
                    "Revise la respuesta del backend."
                )
                self.btn_enviar.disabled = False
                self.btn_enviar.text = "REVISAR RESPUESTA"
                return

            self.solicitud_registrada = True
            self.codigo_solicitud = codigo
            self.titulo.text = "SOLICITUD REGISTRADA"
            self.informacion.text = (
                "La solicitud fue registrada correctamente.\n\n"
                f"Trámite: {self.nombre_tramite}\n"
                f"Código de seguimiento: {codigo}\n\n"
                "Conserve este código para consultar el estado."
            )
            self.mensaje.text = "REGISTRO COMPLETADO"
            self.btn_enviar.text = "SOLICITUD REGISTRADA"
            self.btn_inicio.disabled = False
            self._evento_regreso = Clock.schedule_once(
                self._regreso_programado, 8
            )

        except (TypeError, ValueError) as error:
            print("Error en datos de solicitud:", repr(error))
            self.mensaje.text = "No se pudo identificar correctamente al usuario."
            self.btn_enviar.disabled = False
            self.btn_enviar.text = "REINTENTAR ENVÍO"
        except Exception as error:
            print("Error al crear solicitud:", repr(error))
            self.mensaje.text = "No fue posible conectarse al servidor municipal."
            self.btn_enviar.disabled = False
            self.btn_enviar.text = "REINTENTAR ENVÍO"
        finally:
            self.enviando = False

    def _regreso_programado(self, _dt):
        self._evento_regreso = None
        self.volver_inicio()

    def volver_inicio(self, *_):
        if self._evento_regreso:
            self._evento_regreso.cancel()
            self._evento_regreso = None
        if self.manager and self.manager.has_screen("inicio"):
            self.manager.current = "inicio"
