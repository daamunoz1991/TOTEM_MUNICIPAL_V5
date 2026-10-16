from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from api.cliente_api import ClienteAPI


class SeguimientoScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(40),
            spacing=dp(20)
        )

        titulo = Label(
            text="CONSULTA DE SOLICITUD",
            font_size=dp(30)
        )

        self.codigo_input = TextInput(
            hint_text="Ejemplo: ABC-123456",
            multiline=False,
            font_size=dp(22)
        )

        btn_consultar = Button(
            text="CONSULTAR",
            font_size=dp(22)
        )

        self.resultado = Label(
            text="",
            font_size=dp(19)
        )

        btn_volver = Button(
            text="VOLVER",
            font_size=dp(20)
        )

        btn_consultar.bind(on_release=self.consultar)
        btn_volver.bind(on_release=self.volver)

        layout.add_widget(titulo)
        layout.add_widget(self.codigo_input)
        layout.add_widget(btn_consultar)
        layout.add_widget(self.resultado)
        layout.add_widget(btn_volver)

        self.add_widget(layout)

    def consultar(self, instance):
        codigo = self.codigo_input.text.strip()

        if not codigo:
            self.resultado.text = "Ingrese el código de solicitud."
            return

        try:
            respuesta = ClienteAPI().consultar_solicitud(codigo)

            if respuesta.get("ok") is False:
                self.resultado.text = respuesta.get(
                    "error",
                    "No se encontró la solicitud."
                )
                return

            solicitud = respuesta

            self.resultado.text = (
                "SOLICITUD ENCONTRADA\n\n"
                f"Código: {solicitud.get('codigo_solicitud', codigo)}\n"
                f"Trámite: {solicitud.get('nombre_tramite', '')}\n"
                f"Fecha: {solicitud.get('fecha_solicitud', '')}\n"
                f"Estado: {solicitud.get('estado', '')}\n"
                f"Departamento: {solicitud.get('departamento', '')}"
            )

        except Exception as error:
            print("ERROR AL CONSULTAR:", repr(error))
            self.resultado.text = (
                "No fue posible consultar la solicitud.\n"
                "Revise la conexión con el servidor municipal."
            )

    def volver(self, instance):
        self.manager.current = "inicio"
