"""Identidad visual oficial del Tótem Municipal de La Pintana.
Paleta Institucional Moderna + tipografía Roboto.
"""
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

# Colores hexadecimales convertidos a RGBA para Kivy
AZUL_MARINO = (22/255, 50/255, 79/255, 1)       # #16324F
AZUL_PANEL = AZUL_MARINO
CELESTE = (24/255, 166/255, 166/255, 1)        # #18A6A6
TURQUESA = CELESTE
BLANCO = (1, 1, 1, 1)                           # #FFFFFF
GRIS = (0.30, 0.35, 0.40, 1)
FONDO = (242/255, 245/255, 248/255, 1)          # #F2F5F8
VERDE = CELESTE                                 # CTA uniforme turquesa
TEXTO = AZUL_MARINO
FUENTE = "Roboto"  # Registrada globalmente en client/main.py

def aplicar_fondo(pantalla, color=FONDO):
    with pantalla.canvas.before:
        Color(*color)
        pantalla._fondo_totem = RoundedRectangle(pos=pantalla.pos, size=pantalla.size, radius=[dp(12)])
    pantalla.bind(pos=lambda obj, val: setattr(pantalla._fondo_totem, "pos", val),
                  size=lambda obj, val: setattr(pantalla._fondo_totem, "size", val))

def crear_cabecera(subtitulo="Tótem de Atención Ciudadana"):
    cabecera = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(88),
                         padding=[dp(14), dp(8)], spacing=dp(4))
    with cabecera.canvas.before:
        Color(*AZUL_MARINO)
        cabecera._fondo = RoundedRectangle(pos=cabecera.pos, size=cabecera.size, radius=[dp(10)])
    cabecera.bind(pos=lambda obj, val: setattr(cabecera._fondo, "pos", val),
                  size=lambda obj, val: setattr(cabecera._fondo, "size", val))
    cabecera.add_widget(Label(text="[b]MUNICIPALIDAD DE LA PINTANA[/b]", markup=True,
                              color=BLANCO, font_name=FUENTE, font_size=dp(23)))
    cabecera.add_widget(Label(text=subtitulo, color=(0.88, 0.93, 0.97, 1),
                              font_name=FUENTE, font_size=dp(16)))
    return cabecera
