"""
Aplicación principal del Tótem Municipal (cliente Kivy).

Este archivo debe estar en:
TOTEM_MUNICIPAL_DEPURADO/client/main.py

El backend FastAPI debe permanecer separado en server/main.py.
"""
from pathlib import Path
import sys

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.text import LabelBase

# Asegura que las importaciones api.* y screens.* funcionen al ejecutar
# el proyecto desde la carpeta raíz o desde client/.
CLIENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CLIENT_DIR.parent

# Registrar Roboto globalmente antes de importar las pantallas.
# Esto aplica la tipografía también a Label, Button y TextInput que no
# indiquen font_name explícitamente.
FONT_DIR = CLIENT_DIR / "assets" / "fonts" / "static"
ROBOTO_REGULAR = FONT_DIR / "Roboto-Regular.ttf"
ROBOTO_ITALIC = FONT_DIR / "Roboto-Italic.ttf"
ROBOTO_BOLD = FONT_DIR / "Roboto-Bold.ttf"
ROBOTO_BOLD_ITALIC = FONT_DIR / "Roboto-BoldItalic.ttf"

if ROBOTO_REGULAR.exists() and ROBOTO_BOLD.exists():
    LabelBase.register(
        name="Roboto",
        fn_regular=str(ROBOTO_REGULAR),
        fn_italic=str(ROBOTO_ITALIC if ROBOTO_ITALIC.exists() else ROBOTO_REGULAR),
        fn_bold=str(ROBOTO_BOLD),
        fn_bolditalic=str(ROBOTO_BOLD_ITALIC if ROBOTO_BOLD_ITALIC.exists() else ROBOTO_BOLD),
    )
    # Fuente predeterminada para los widgets Kivy sin font_name explícito.
    LabelBase.default_font = [
        "Roboto",
        str(ROBOTO_REGULAR),
        str(ROBOTO_ITALIC if ROBOTO_ITALIC.exists() else ROBOTO_REGULAR),
        str(ROBOTO_BOLD),
        str(ROBOTO_BOLD_ITALIC if ROBOTO_BOLD_ITALIC.exists() else ROBOTO_BOLD),
    ]
else:
    print(f"[ADVERTENCIA] No se encontraron las fuentes Roboto en: {FONT_DIR}")

for ruta in (str(CLIENT_DIR), str(PROJECT_DIR)):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from screens.inicio import InicioScreen
from screens.autenticacion import AutenticacionScreen
from screens.registro import RegistroScreen
from screens.tramites import TramitesScreen
from screens.formulario import FormularioScreen
from screens.documentos import DocumentosScreen
from screens.confirmacion import ConfirmacionScreen
from screens.seguimiento import SeguimientoScreen
from screens.admin import AdminScreen


class TotemMunicipalApp(App):
    """Aplicación principal de la interfaz del tótem."""

    title = "Tótem Municipal - La Pintana"

    def build(self):
        administrador = ScreenManager(
            transition=SlideTransition(duration=0.18)
        )

        pantallas = [
            ("inicio", InicioScreen),
            ("autenticacion", AutenticacionScreen),
            ("registro", RegistroScreen),
            ("tramites", TramitesScreen),
            ("formulario", FormularioScreen),
            ("documentos", DocumentosScreen),
            ("confirmacion", ConfirmacionScreen),
            ("seguimiento", SeguimientoScreen),
            ("admin", AdminScreen),
        ]

        for nombre, clase_pantalla in pantallas:
            administrador.add_widget(clase_pantalla(name=nombre))

        administrador.current = "inicio"
        return administrador


if __name__ == "__main__":
    TotemMunicipalApp().run()
