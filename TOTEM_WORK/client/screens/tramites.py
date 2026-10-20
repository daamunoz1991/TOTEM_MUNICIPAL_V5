"""Navegación y formularios del Tótem Municipal de La Pintana."""
from datetime import date, timedelta
from pathlib import Path
import json
import unicodedata
import requests
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from api.cliente_api import ClienteAPI
from screens.adjuntos import GestorAdjuntos

NAVY=(22/255,50/255,79/255,1); TEAL=(24/255,166/255,166/255,1); WHITE=(1,1,1,1)
BG=(242/255,245/255,248/255,1); GRAY=(0.30,0.35,0.40,1); GREEN=(24/255,166/255,166/255,1)
# Alias para compatibilidad con los botones del formulario
COLOR_SECUNDARIO = NAVY

CATEGORIES = {
    "Beneficios sociales": [
        ("SAP","Subsidio de Agua Potable","Cédula de identidad, antecedente del Registro Social de Hogares y cuenta de agua."),
        ("EDA","Exención de Derechos de Aseo","Cédula de identidad, rol/dirección del domicilio y antecedentes de respaldo."),
        ("SUF","Subsidio Único Familiar","Cédula de identidad y certificados de nacimiento/antecedentes de causantes, según corresponda."),
    ],
    "Reserva de horas": [
        ("BOOK_RSH","Agenda para el Registro Social de Hogares","Seleccione fecha y hora para solicitar atención."),
        ("BOOK_VET","Atención Clínica Veterinaria","Seleccione fecha y hora para atención veterinaria."),
        ("BOOK_ESTC","Esterilización Canina","Seleccione fecha y hora para consultar disponibilidad."),
        ("BOOK_ESTF","Esterilización Felina","Seleccione fecha y hora para consultar disponibilidad."),
    ],
    "Solicitudes municipales": [
        ("POD","Solicitud de poda","Indique dirección, referencia, descripción y fotografía si está disponible."),
        ("LUM","Solicitud de mantención de luminaria","Indique dirección, referencia, descripción, fotografía y área responsable."),
        ("VOL","Retiro de voluminosos","Indique dirección, referencia, descripción y fotografía si está disponible."),
        ("DEM","Solicitud de demarcación","Indique dirección, referencia, descripción y fotografía si está disponible."),
    ],
    "Denuncias y fiscalización": [
        ("DEN","Denuncias y fiscalización","Puede seleccionar uno o varios motivos. No se solicitan datos personales."),
    ],
}
DENUNCIAS=["Retiro de rucos","Retiro de autos","Insalubridad","Negocio irregular","Otro"]
SERVICES={"BOOK_RSH":"Agenda para el Registro Social de Hogares","BOOK_VET":"Atención Clínica Veterinaria","BOOK_ESTC":"Esterilización Canina","BOOK_ESTF":"Esterilización Felina"}

class TramitesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categoria_actual=""; self.tramite_actual=None; self.archivo=None; self.checks={}; self.horarios=[]; self.pending_submission=None
        # La CI requiere dos fotografías independientes. Los demás respaldos
        # se agregan a una lista sin reemplazar los ya seleccionados.
        self.archivos_eda = {
            "cedula_anverso": None,
            "cedula_reverso": None,
            "avaluo": None,
        }
        self.archivos_extra = []
        self._adjunto_destino = "general"
        self._etiquetas_archivos = {}
        self._lista_adicionales = None
        self.gestor_adjuntos = GestorAdjuntos(self._adjunto_recibido, self._error_adjunto)
        self.api=ClienteAPI()
        with self.canvas.before:
            Color(*BG); self._fondo=RoundedRectangle(pos=self.pos,size=self.size)
        self.bind(pos=self._actualizar_fondo,size=self._actualizar_fondo)
        self.root=BoxLayout(orientation="vertical",padding=dp(20),spacing=dp(12))
        header=BoxLayout(orientation="vertical",size_hint_y=None,height=dp(76),padding=[dp(18),dp(8)])
        with header.canvas.before:
            Color(*NAVY); header.rect=RoundedRectangle(pos=header.pos,size=header.size,radius=[dp(14)])
        header.bind(pos=lambda o,v:setattr(o.rect,'pos',v),size=lambda o,v:setattr(o.rect,'size',v))
        header.add_widget(Label(text="MUNICIPALIDAD DE LA PINTANA",bold=True,font_size=dp(21),color=WHITE,halign="left"))
        header.add_widget(Label(text="Tótem de Atención Digital Municipal",font_size=dp(14),color=(.75,.91,.94,1),halign="left"))
        self.root.add_widget(header)
        self.title=Label(
            text="¿QUÉ NECESITAS REALIZAR?",
            font_size=dp(25),
            bold=True,
            color=NAVY,
            size_hint_y=None,
            height=dp(45),
            halign='center',
            valign='middle'
        )
        self.title.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
        self.root.add_widget(self.title)
        self.body=BoxLayout(orientation="vertical",spacing=dp(10))
        self.root.add_widget(self.body)
        self.message=Label(text="",color=GRAY,font_size=dp(15),size_hint_y=None,height=dp(36))
        self.root.add_widget(self.message)
        back=Button(text="← VOLVER AL INICIO",size_hint_y=None,height=dp(52),background_normal="",background_color=NAVY,color=WHITE,font_size=dp(17))
        back.bind(on_release=lambda *_:setattr(self.manager,'current','inicio'))
        self.root.add_widget(back); self.add_widget(self.root)
        self.mostrar_categorias()

    def _actualizar_fondo(self, *args):
        self._fondo.pos = self.pos
        self._fondo.size = self.size
    def on_pre_enter(self,*_):
        self.api=ClienteAPI()  # recupera el token creado por la pantalla de autenticación
        # Si hay un trámite seleccionado, mostrar su formulario directamente
        # Esto permite que al volver del login (ATRÁS), se muestre el formulario
        if self.tramite_actual and self.categoria_actual:
            self.mostrar_formulario(self.tramite_actual)
        elif not self.categoria_actual and not self.tramite_actual:
            # Solo mostrar categorías si no hay ninguna seleccionada
            self.mostrar_categorias()
        # Si hay categoría pero no trámite, mostrar la lista de trámites de esa categoría
        elif self.categoria_actual and not self.tramite_actual:
            self.mostrar_categoria(self.categoria_actual)
        # Guardar estado para cuando se vuelva de autenticación
        self._volver_a_formulario = bool(self.tramite_actual and self.categoria_actual)

    def _button(self,text,callback,height=68):
        b=Button(text=text,size_hint_y=None,height=dp(height),background_normal="",background_down="",background_color=TEAL,color=WHITE,font_size=dp(18),halign="center")
        b.bind(on_release=callback); return b
    def mostrar_categorias(self):
        self.tramite_actual=None; self.categoria_actual=""
        self._reiniciar_adjuntos()
        self.title.text="¿QUÉ NECESITAS REALIZAR?"
        self.body.clear_widgets()
        self.message.text="Seleccione una sección para continuar."
        for cat in CATEGORIES:
            self.body.add_widget(self._button(cat,lambda _,c=cat:self.mostrar_categoria(c),66))
        # Botón para volver al inicio
        self.body.add_widget(self._button("VOLVER AL INICIO", lambda *_: setattr(self.manager, 'current', 'inicio'), 58))

    @staticmethod
    def _normalizar_categoria(texto):
        """Normaliza mayúsculas, tildes y espacios para evitar errores de navegación."""
        texto = unicodedata.normalize("NFD", str(texto or ""))
        texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
        return " ".join(texto.casefold().split())

    def mostrar_categoria(self, categoria):
        # Los botones de inicio y las claves de CATEGORIES históricamente usaban
        # variantes de mayúsculas y nombres. Resolverlas aquí evita KeyError.
        aliases = {
            "beneficios sociales": "Beneficios sociales",
            "reserva de horas": "Reserva de horas",
            "reservar hora": "Reserva de horas",
            "solicitudes municipales": "Solicitudes municipales",
            "denuncias y fiscalizacion": "Denuncias y fiscalización",
        }
        buscada = self._normalizar_categoria(categoria)
        categoria_real = aliases.get(buscada)
        if categoria_real is None:
            categoria_real = next(
                (nombre for nombre in CATEGORIES
                 if self._normalizar_categoria(nombre) == buscada),
                None,
            )
        if categoria_real is None:
            self.body.clear_widgets()
            self.title.text = "SECCIÓN NO DISPONIBLE"
            self.message.text = f"No se reconoce la sección: {categoria}. Vuelva al inicio e inténtelo nuevamente."
            self.body.add_widget(self._button("VOLVER A SECCIONES", lambda *_: self.mostrar_categorias(), 58))
            return

        self.categoria_actual = categoria_real
        self.title.text = categoria_real.upper()
        self.body.clear_widgets()
        self.message.text = "Seleccione una opción para revisar sus requisitos."
        scroll = ScrollView(do_scroll_x=False)
        items = BoxLayout(orientation="vertical", spacing=dp(10), padding=[0, dp(4)], size_hint_y=None)
        items.bind(minimum_height=items.setter('height'))
        for code, name, desc in CATEGORIES[categoria_real]:
            items.add_widget(self._button(f"{name}\n{desc}", lambda _, x=(code, name, desc): self.seleccionar(x), 84))
        scroll.add_widget(items)
        self.body.add_widget(scroll)

    def seleccionar(self,item):
        self._reiniciar_adjuntos()
        self.tramite_actual={"codigo":item[0],"nombre":item[1],"descripcion":item[2]}
        # Mostrar formulario directamente; el login se solicita al final si es necesario
        self.mostrar_formulario(self.tramite_actual)

    def _field(self, parent, label, hint="", multiline=False, height=48):
        etiqueta = Label(
            text=str(label).upper(),
            color=NAVY,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(27),
            halign='left',
            valign='middle'
        )
        etiqueta.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
        parent.add_widget(etiqueta)
        w=TextInput(hint_text=hint,multiline=multiline,size_hint_y=None,height=dp(height),font_size=dp(16),foreground_color=NAVY,background_color=WHITE,padding=dp(10))
        parent.add_widget(w); return w

    def mostrar_formulario(self,item):
        self.tramite_actual=item; self.body.clear_widgets(); self.title.text=item['nombre'].upper(); self.message.text=item['descripcion']
        scroll=ScrollView(do_scroll_x=False); form=BoxLayout(orientation='vertical',spacing=dp(8),padding=[dp(8),dp(4)],size_hint_y=None); form.bind(minimum_height=form.setter('height'))
        form.add_widget(Label(text=item['descripcion'],color=GRAY,font_size=dp(15),size_hint_y=None,height=dp(50),halign='left'))
        code=item['codigo']; self.fields={}
        if code.startswith('BOOK_'):
            self.fields['nombre']=self._field(form,'Nombre completo','Nombre de quien reserva')
            self.fields['rut']=self._field(form,'RUT','12.345.678-9')
            self.fields['contacto']=self._field(form,'Contacto','Teléfono o correo de contacto')
            # Campo de fecha (visible pero de solo lectura)
            self.fields['fecha']=self._field(form,'Fecha seleccionada','Seleccione en el calendario')
            self.fields['fecha'].readonly=True
            # Calendario mes a mes
            self._calendar_widget(form)
            btn=self._button('CONSULTAR HORARIOS DISPONIBLES',lambda *_:self.cargar_horarios(),48); form.add_widget(btn)
            self.horario_spinner=Spinner(text='Seleccione una hora',values=(),size_hint_y=None,height=dp(48),background_normal='',background_color=TEAL,color=WHITE)
            form.add_widget(self.horario_spinner)
        elif code=='DEN':
            form.add_widget(Label(text='MOTIVOS DE DENUNCIA (PUEDE MARCAR VARIOS)',color=NAVY,size_hint_y=None,height=dp(28),halign='left'))
            self.checks={}
            for motivo in DENUNCIAS:
                row=BoxLayout(size_hint_y=None,height=dp(38),spacing=dp(8))
                cb=CheckBox(size_hint_x=None,width=dp(44),color=TEAL); self.checks[motivo]=cb
                etiqueta_motivo = Label(
                    text=motivo.upper(),
                    color=NAVY,
                    halign='left',
                    valign='middle'
                )
                etiqueta_motivo.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
                row.add_widget(cb)
                row.add_widget(etiqueta_motivo)
                form.add_widget(row)
            self.fields['direccion']=self._field(form,'Dirección','Calle y número')
            self.fields['referencia']=self._field(form,'Punto de referencia','Entre calles, local o referencia')
            self.fields['descripcion']=self._field(form,'Descripción de los hechos','Describa los hechos observados',True,100)
            self._file_button(form,optional=True)
        else:
            if code=='SUF':
                self.fields['nombre_causal']=self._field(form,'Nombre de causal','Nombre del causante')
                self.fields['rut_causal']=self._field(form,'RUT de causal','12.345.678-9')
                self.fields['fecha_nacimiento']=self._field(form,'Fecha de nacimiento','AAAA-MM-DD')
                self.fields['descripcion']=self._field(form,'Descripción de solicitud','Describa la solicitud',True,100)
            elif code=='EDA':
                self.fields['direccion']=self._field(form,'Dirección','Calle y número')
                self.fields['rol_propiedad']=self._field(form,'ROL de la Propiedad','xxxxx-xx')
                self.fields['causal']=Spinner(text='Seleccione causal',values=('Adulto Mayor','Discapacidad','Enfermedad Catastrófica','Ingresos'),size_hint_y=None,height=dp(48),background_normal='',background_color=WHITE,color=NAVY)
                etiqueta_causal = Label(
                    text='CAUSAL DE POSTULACIÓN',
                    color=NAVY,
                    size_hint_y=None,
                    height=dp(26),
                    halign='left',
                    valign='middle'
                )
                etiqueta_causal.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
                form.add_widget(etiqueta_causal)
                form.add_widget(self.fields['causal'])
                # EDA: la CI se solicita separada en anverso y reverso.
                self._campos_cedula(form)
                self._file_button_labeled(form, "CERTIFICADO DE AVALÚO", "avaluo", "Adjunte certificado de avalúo")
            elif code=='SAP':
                self.fields['nombre_propietario']=self._field(form,'Nombre de propietario','Nombre completo del propietario')
                self.fields['direccion']=self._field(form,'Dirección','Calle y número')
                self.fields['porcentaje_rsh']=Spinner(text='Seleccione porcentaje',values=('40%','50%','60%','70%','80%','90%','100%'),size_hint_y=None,height=dp(48),background_normal='',background_color=WHITE,color=NAVY)
                etiqueta_rsh = Label(
                    text='PORCENTAJE DE REGISTRO SOCIAL DE HOGAR',
                    color=NAVY,
                    size_hint_y=None,
                    height=dp(26),
                    halign='left',
                    valign='middle'
                )
                etiqueta_rsh.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
                form.add_widget(etiqueta_rsh)
                form.add_widget(self.fields['porcentaje_rsh'])
                self._campos_cedula(form)
            else:
                self.fields['direccion']=self._field(form,'Dirección','Calle y número')
                self.fields['referencia']=self._field(form,'Punto de referencia','Entre calles o referencia cercana')
                if code=='LUM':
                    self.fields['area']=Spinner(text='Seleccione área',values=('Vía Pública','Área Verde'),size_hint_y=None,height=dp(48),background_normal='',background_color=WHITE,color=NAVY)
                    etiqueta_area = Label(
                        text='ÁREA RESPONSABLE',
                        color=NAVY,
                        size_hint_y=None,
                        height=dp(26),
                        halign='left',
                        valign='middle'
                    )
                    etiqueta_area.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
                    form.add_widget(etiqueta_area)
                    form.add_widget(self.fields['area'])
                self.fields['descripcion']=self._field(form,'Descripción','Describa la solicitud',True,100)
            if code == 'SUF':
                self._campos_cedula(form)
            # Todas las solicitudes pueden llevar varios documentos de respaldo.
            self._file_button(form, optional=True)
        # Botones de acción
        botones_box = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(10))
        btn_atras = Button(text='ATRÁS', background_normal='', background_color=COLOR_SECUNDARIO, color=WHITE, font_size=dp(16))
        btn_atras.bind(on_release=lambda *_: self.mostrar_categoria(self.categoria_actual))
        botones_box.add_widget(btn_atras)
        btn_enviar = self._button('ENVIAR SOLICITUD' if not code.startswith('BOOK') else 'CONFIRMAR RESERVA', lambda *_: self.enviar(), 54)
        botones_box.add_widget(btn_enviar)
        form.add_widget(botones_box)
        scroll.add_widget(form); self.body.add_widget(scroll)

    def _calendar_widget(self, parent):
        """Crea un calendario interactivo con navegación mes a mes."""
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        from datetime import date
        import calendar

        # Inicializar estado del calendario
        today = date.today()
        self._cal_anio = today.year
        self._cal_mes = today.month

        # Contenedor del calendario
        cal_container = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, height=dp(320))
        cal_container.bind(minimum_height=cal_container.setter('height'))

        # Título del calendario
        cal_title = Label(text='SELECCIONE UNA FECHA', color=NAVY, font_size=dp(14), size_hint_y=None, height=dp(24), halign='left', valign='middle')
        cal_title.bind(size=lambda obj, value: setattr(obj, 'text_size', value))
        cal_container.add_widget(cal_title)

        # Navegación de mes
        nav_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        btn_anterior = Button(text='◀️', size_hint_x=None, width=dp(50), background_normal='', background_color=TEAL, color=WHITE, font_size=dp(18))
        self._cal_label = Label(text='', color=NAVY, font_size=dp(16), bold=True)
        btn_siguiente = Button(text='▶️', size_hint_x=None, width=dp(50), background_normal='', background_color=TEAL, color=WHITE, font_size=dp(18))
        nav_box.add_widget(btn_anterior)
        nav_box.add_widget(self._cal_label)
        nav_box.add_widget(btn_siguiente)
        cal_container.add_widget(nav_box)

        # Grid del calendario
        self._cal_grid = GridLayout(cols=7, spacing=dp(4), size_hint_y=None, height=dp(220))
        cal_container.add_widget(self._cal_grid)

        parent.add_widget(cal_container)

        # Bindings de navegación
        btn_anterior.bind(on_release=lambda *_: self._cal_mes_anterior())
        btn_siguiente.bind(on_release=lambda *_: self._cal_mes_siguiente())

        # Dibujar calendario inicial
        self._dibujar_calendario()

    def _cal_mes_anterior(self):
        """Navega al mes anterior."""
        if self._cal_mes == 1:
            self._cal_mes = 12
            self._cal_anio -= 1
        else:
            self._cal_mes -= 1
        self._dibujar_calendario()

    def _cal_mes_siguiente(self):
        """Navega al mes siguiente."""
        if self._cal_mes == 12:
            self._cal_mes = 1
            self._cal_anio += 1
        else:
            self._cal_mes += 1
        self._dibujar_calendario()

    def _dibujar_calendario(self):
        """Dibuja el calendario del mes actual."""
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.metrics import dp
        from datetime import date
        import calendar

        # Actualizar etiqueta de mes
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        self._cal_label.text = f"{meses[self._cal_mes - 1]} {self._cal_anio}"

        # Limpiar grid
        self._cal_grid.clear_widgets()
        self.calendario_botones = {}

        # Encabezados de días
        dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
        for dia in dias_semana:
            lbl = Label(text=dia, color=NAVY, font_size=dp(12), bold=True)
            self._cal_grid.add_widget(lbl)

        # Obtener información del mes
        primer_dia = date(self._cal_anio, self._cal_mes, 1)
        inicio_semana = primer_dia.weekday()  # 0=Lunes
        dias_en_mes = calendar.monthrange(self._cal_anio, self._cal_mes)[1]

        # Celdas vacías antes del primer día
        for _ in range(inicio_semana):
            self._cal_grid.add_widget(Label(text='', size_hint_y=None, height=dp(30)))

        # Días del mes
        today = date.today()
        for dia in range(1, dias_en_mes + 1):
            fecha = date(self._cal_anio, self._cal_mes, dia)
            if fecha >= today:
                btn = Button(
                    text=str(dia),
                    size_hint_y=None,
                    height=dp(30),
                    background_normal='',
                    background_color=WHITE,
                    color=NAVY,
                    font_size=dp(12)
                )
                btn.bind(on_release=lambda x, f=fecha: self._seleccionar_fecha(f))
                self.calendario_botones[fecha] = btn
                self._cal_grid.add_widget(btn)
            else:
                self._cal_grid.add_widget(Label(text=str(dia), color=GRAY, font_size=dp(12), size_hint_y=None, height=dp(30)))

    def _seleccionar_fecha(self, fecha):
        """Maneja la selección de fecha en el calendario."""
        self.fields['fecha'].text = fecha.isoformat()
        # Resaltar el botón seleccionado
        for f, btn in self.calendario_botones.items():
            if f == fecha:
                btn.background_color = TEAL
                btn.color = WHITE
            else:
                btn.background_color = WHITE
                btn.color = NAVY

    # ==============================================================
    # ADJUNTOS: anverso, reverso, avalúo y varios respaldos
    # ==============================================================
    MAX_ADICIONALES = 6

    def _reiniciar_adjuntos(self):
        """Limpia los adjuntos al iniciar otro trámite (no durante el login)."""
        self.archivo = None  # compatibilidad con la navegación existente
        self.archivos_eda = {
            'cedula_anverso': None,
            'cedula_reverso': None,
            'avaluo': None,
        }
        self.archivos_extra = []
        self._adjunto_destino = 'general'
        self._etiquetas_archivos = {}
        self._lista_adicionales = None

    def _campos_cedula(self, parent):
        self._file_button_labeled(
            parent, 'CÉDULA DE IDENTIDAD - ANVERSO',
            'cedula_anverso', 'Fotografía del frente del carnet'
        )
        self._file_button_labeled(
            parent, 'CÉDULA DE IDENTIDAD - REVERSO',
            'cedula_reverso', 'Fotografía de la parte posterior del carnet'
        )

    def _file_button_labeled(self, parent, etiqueta, key, hint):
        titulo = Label(
            text=etiqueta, color=NAVY, font_size=dp(14),
            size_hint_y=None, height=dp(30), halign='left', valign='middle'
        )
        titulo.bind(size=lambda o, v: setattr(o, 'text_size', v))
        parent.add_widget(titulo)

        estado = Label(
            text='Pendiente: ' + hint, color=GRAY, font_size=dp(12),
            size_hint_y=None, height=dp(30), halign='left', valign='middle'
        )
        estado.bind(size=lambda o, v: setattr(o, 'text_size', v))
        parent.add_widget(estado)
        self._etiquetas_archivos[key] = estado
        if self.archivos_eda.get(key):
            estado.text = 'Adjuntado: ' + Path(self.archivos_eda[key]).name[:36]

        acciones = GridLayout(cols=3, size_hint_y=None, height=dp(49), spacing=dp(5))
        b_archivo = self._button('ELEGIR', lambda *_: self.abrir_archivo_eda(key), 45)
        b_foto = self._button('FOTO', lambda *_: self.tomar_foto_adjunto(key), 45)
        b_quitar = self._button('QUITAR', lambda *_: self._quitar_documento(key), 45)
        for boton in (b_archivo, b_foto, b_quitar):
            boton.font_size = dp(13)
            acciones.add_widget(boton)
        parent.add_widget(acciones)

    def _file_button(self, parent, optional=True):
        titulo = Label(
            text=f'DOCUMENTOS ADICIONALES (máximo {self.MAX_ADICIONALES})',
            color=NAVY, font_size=dp(14), bold=True,
            size_hint_y=None, height=dp(34), halign='left', valign='middle'
        )
        titulo.bind(size=lambda o, v: setattr(o, 'text_size', v))
        parent.add_widget(titulo)
        acciones = GridLayout(cols=2, size_hint_y=None, height=dp(52), spacing=dp(8))
        b_archivo = self._button('ELEGIR ARCHIVOS', lambda *_: self.abrir_archivo(), 48)
        b_foto = self._button('TOMAR FOTO', lambda *_: self.tomar_foto_adjunto(), 48)
        b_archivo.font_size = dp(14)
        b_foto.font_size = dp(14)
        acciones.add_widget(b_archivo)
        acciones.add_widget(b_foto)
        parent.add_widget(acciones)

        self._lista_adicionales = BoxLayout(
            orientation='vertical', spacing=dp(5), size_hint_y=None
        )
        self._lista_adicionales.bind(
            minimum_height=self._lista_adicionales.setter('height')
        )
        parent.add_widget(self._lista_adicionales)
        self._actualizar_lista_adicionales()

    def abrir_archivo_eda(self, key):
        self._adjunto_destino = key
        self.gestor_adjuntos.seleccionar(multiple=False)

    def abrir_archivo(self):
        self._adjunto_destino = 'general'
        self.gestor_adjuntos.seleccionar(multiple=True)

    def tomar_foto_adjunto(self, key='general'):
        self._adjunto_destino = key
        self.gestor_adjuntos.tomar_foto()

    def _adjunto_recibido(self, rutas):
        if not rutas:
            return
        destino = self._adjunto_destino
        if destino in self.archivos_eda:
            ruta = str(rutas[0])
            self.archivos_eda[destino] = ruta
            etiqueta = self._etiquetas_archivos.get(destino)
            if etiqueta is not None:
                etiqueta.text = 'Adjuntado: ' + Path(ruta).name[:36]
            self.message.text = 'Documento preparado correctamente.'
            return

        nuevos = [str(r) for r in rutas if str(r) not in self.archivos_extra]
        if len(self.archivos_extra) + len(nuevos) > self.MAX_ADICIONALES:
            self.message.text = (
                f'Solo se permiten {self.MAX_ADICIONALES} archivos adicionales por solicitud. '
                'Quite uno antes de agregar más.'
            )
            return
        self.archivos_extra.extend(nuevos)
        self.archivo = self.archivos_extra[0] if self.archivos_extra else None
        self._actualizar_lista_adicionales()
        self.message.text = f'{len(self.archivos_extra)} archivo(s) adicional(es) preparados.'

    def _quitar_documento(self, key):
        self.archivos_eda[key] = None
        etiqueta = self._etiquetas_archivos.get(key)
        if etiqueta is not None:
            etiqueta.text = 'Pendiente: seleccione un archivo o tome una foto.'
        self.message.text = 'Documento retirado de la solicitud.'

    def _quitar_adicional(self, ruta):
        if ruta in self.archivos_extra:
            self.archivos_extra.remove(ruta)
        self.archivo = self.archivos_extra[0] if self.archivos_extra else None
        self._actualizar_lista_adicionales()
        self.message.text = 'Archivo retirado de la solicitud.'

    def _actualizar_lista_adicionales(self):
        panel = self._lista_adicionales
        if panel is None:
            return
        panel.clear_widgets()
        if not self.archivos_extra:
            panel.add_widget(Label(
                text='Sin archivos adicionales.', color=GRAY,
                size_hint_y=None, height=dp(28), font_size=dp(13)
            ))
            return
        for indice, ruta in enumerate(self.archivos_extra, start=1):
            fila = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
            etiqueta = Label(
                text=f'{indice}. {Path(ruta).name[:32]}',
                color=GRAY, font_size=dp(12), halign='left', valign='middle'
            )
            etiqueta.bind(size=lambda o, v: setattr(o, 'text_size', v))
            quitar = self._button(
                'QUITAR', lambda *_, r=ruta: self._quitar_adicional(r), 38
            )
            quitar.size_hint_x = None
            quitar.width = dp(92)
            quitar.font_size = dp(12)
            fila.add_widget(etiqueta)
            fila.add_widget(quitar)
            panel.add_widget(fila)

    def _error_adjunto(self, mensaje):
        self.message.text = str(mensaje)

    def _validar_adjuntos(self, codigo_tramite):
        # La CI es obligatoria cuando el beneficio exige identificación.
        if codigo_tramite in {'SAP', 'EDA', 'SUF'}:
            if not self.archivos_eda.get('cedula_anverso'):
                raise ValueError('Adjunte el ANVERSO (frente) de la cédula de identidad.')
            if not self.archivos_eda.get('cedula_reverso'):
                raise ValueError('Adjunte el REVERSO (parte trasera) de la cédula de identidad.')
        if codigo_tramite == 'EDA' and not self.archivos_eda.get('avaluo'):
            raise ValueError('Adjunte el Certificado de Avalúo.')

    def _adjuntos_para_subir(self):
        archivos = []
        for tipo, ruta in self.archivos_eda.items():
            if ruta:
                archivos.append((tipo, ruta))
        for indice, ruta in enumerate(self.archivos_extra, start=1):
            archivos.append((f'adicional_{indice}', ruta))
        return archivos

    def _subir_adjuntos(self, codigo_solicitud):
        """POST de cada archivo al endpoint ya utilizado por FastAPI.

        Devuelve advertencias concretas; registrar el ticket no garantiza
        que sus documentos hayan sido recibidos por el servidor.
        """
        problemas = []
        token = self.api.access_token
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        for tipo, ruta in self._adjuntos_para_subir():
            try:
                # Los prefijos distinguen anverso y reverso en el backend.
                nombre = f'{tipo}_{Path(ruta).name}'
                with open(ruta, 'rb') as archivo:
                    respuesta = requests.post(
                        f'{self.api.url_base}/solicitudes/{codigo_solicitud}/archivos',
                        files={'archivo': (nombre, archivo)},
                        headers=headers, timeout=30
                    )
                if not respuesta.ok:
                    problemas.append(f'{tipo}: HTTP {respuesta.status_code}')
            except Exception as exc:
                problemas.append(f'{tipo}: {str(exc)[:80]}')
        return problemas

    def cargar_horarios(self):
        try:
            fecha_str=self.fields['fecha'].text.strip()
            if not fecha_str:
                self.message.text="Seleccione una fecha en el calendario."
                return
            fecha=date.fromisoformat(fecha_str)
            dia_semana=fecha.weekday()  # 0=Lunes, 6=Domingo
            servicio=SERVICES[self.tramite_actual['codigo']]
            codigo=self.tramite_actual['codigo']

            # Verificar si el servicio atiende ese día
            dias_atencion={
                'BOOK_ESTC':[1,3],  # Martes y Jueves
                'BOOK_ESTF':[0,2,4],  # Lunes, Miércoles y Viernes
            }
            if codigo in dias_atencion and dia_semana not in dias_atencion[codigo]:
                dias_nombres={0:'Lunes',1:'Martes',2:'Miércoles',3:'Jueves',4:'Viernes',5:'Sábado',6:'Domingo'}
                dias_texto=', '.join([dias_nombres[d] for d in dias_atencion[codigo]])
                self.message.text=f"Este servicio atiende solo los días: {dias_texto}."
                self.horario_spinner.values=()
                self.horario_spinner.text='No disponible este día'
                return

            # Consultar disponibilidad al servidor
            r=requests.get(f'{self.api.url_base}/reservas/disponibilidad',params={'servicio':servicio,'fecha':fecha_str},timeout=10)
            data=self._leer_respuesta(r)
            values=[x['hora'] for x in data['horarios'] if x['disponible']]
            self.horario_spinner.values=values
            self.horario_spinner.text=values[0] if values else 'Sin horas disponibles'
            self.message.text=f"{len(values)} horario(s) disponible(s) para {fecha_str}."
        except Exception as e:
            self.message.text=f"No fue posible consultar horarios: {e}"

    @staticmethod
    def _leer_respuesta(r):
        """Lee respuestas JSON o texto sin provocar errores por cuerpos vacíos."""
        try:
            contenido = (r.text or "").strip()
        except Exception:
            contenido = ""

        if not contenido:
            raise ValueError(
                f"El servidor respondió sin contenido (HTTP {getattr(r, 'status_code', '?')}). "
                "Revise el endpoint y los registros del servidor."
            )

        try:
            data = r.json()
        except (ValueError, json.JSONDecodeError):
            detalle = contenido[:400]
            raise ValueError(
                f"El servidor no devolvió JSON válido (HTTP {getattr(r, 'status_code', '?')}): "
                f"{detalle}"
            )

        if not getattr(r, "ok", False):
            if isinstance(data, dict):
                detalle = data.get("detail") or data.get("error") or data.get("message")
            else:
                detalle = str(data)
            raise ValueError(detalle or f"Error del servidor (HTTP {getattr(r, 'status_code', '?')}).")

        if not isinstance(data, dict):
            raise ValueError("El servidor respondió en un formato inesperado.")
        return data

    def enviar(self):
        code=self.tramite_actual['codigo']
        try:
            if code.startswith('BOOK_'):
                nombre=self.fields['nombre'].text.strip()
                rut=self.fields['rut'].text.strip()
                contacto=self.fields['contacto'].text.strip()
                fecha=self.fields['fecha'].text.strip()
                hora=self.horario_spinner.text
                if not nombre: raise ValueError('Ingrese el nombre completo.')
                if not rut: raise ValueError('Ingrese el RUT.')
                if not contacto: raise ValueError('Ingrese el contacto.')
                if not fecha: raise ValueError('Seleccione una fecha en el calendario.')
                if hora in ('Seleccione una hora','Sin horas disponibles',''): raise ValueError('Consulte disponibilidad y seleccione una hora.')
                data={'servicio':SERVICES[code],'fecha':fecha,'hora':hora,'nombre':nombre,'rut':rut,'contacto':contacto}
                r=requests.post(self.api.url_base+'/reservas',json=data,timeout=15); result=self._leer_respuesta(r)
                self.mostrar_exito('Reserva confirmada',f"Código: {result['codigo_reserva']}\nServicio: {result['servicio']}\nFecha: {result['fecha']} · Hora: {result['hora']}\nNombre: {nombre}\nRUT: {rut}"); return
            data={'codigo_tramite':code,'nombre_tramite':self.tramite_actual['nombre']}
            for key,widget in self.fields.items():
                value=widget.text.strip()
                if key in {'direccion','descripcion'} and not value: raise ValueError(f'Complete el campo: {key}.')
                if key=='area' and value=='Seleccione área': raise ValueError('Seleccione Vía Pública o Área Verde.')
                data[key]=value
            if code=='DEN':
                motivos=[m for m,cb in self.checks.items() if cb.active]
                if not motivos: raise ValueError('Seleccione al menos un motivo de denuncia.')
                data['motivos']=motivos
            self._validar_adjuntos(code)
            # Verificar autenticación para trámites que la requieren
            if code not in {'DEN'} and not self.api.access_token:
                # Guardar el formulario completo antes de autenticar.
                self.pending_submission = data.copy()
                auth = self.manager.get_screen('autenticacion')
                auth.tramite_codigo = code
                auth.tramite_nombre = self.tramite_actual['nombre']
                auth.pantalla_origen = 'tramites'
                auth.pantalla_destino = 'tramites'
                auth.usuario_id = None
                auth.usuario = None
                self.message.text = "Complete la autenticación para registrar su solicitud."
                self.manager.current = 'autenticacion'
                return
            data['descripcion']=json.dumps(data,ensure_ascii=False)
            if code=='DEN':
                r=requests.post(self.api.url_base+'/solicitudes/publica',json=data,timeout=15)
            else:
                if not self.api.access_token: raise ValueError('Su sesión no está activa. Vuelva e inicie sesión.')
                r=self.api._request('POST','/solicitudes',json={'codigo_tramite':code,'descripcion':data['descripcion']})
                if isinstance(r,dict) and r.get('ok') is False: raise ValueError(r.get('error','No fue posible registrar la solicitud.'))
                result=r
                r=None
            if r is not None:
                result=self._leer_respuesta(r)
            codigo_solicitud = result.get('codigo_solicitud') if isinstance(result, dict) else None
            if not codigo_solicitud:
                raise ValueError('La API no devolvió el código de la solicitud.')
            errores = self._subir_adjuntos(codigo_solicitud)
            detalle = (
                'Su solicitud fue registrada.\n'
                f'Código de ticket: {codigo_solicitud}\n'
                'Guarde este código para consultar el estado.'
            )
            if errores:
                detalle += ('\nAVISO: algunos documentos no llegaron al servidor: '
                            + '; '.join(errores[:3]))
            self.mostrar_exito('Solicitud ingresada', detalle)
        except Exception as e: self.message.text=str(e)

    def procesar_pendiente(self, usuario):
        """Registra el formulario conservado después de una autenticación exitosa."""
        data = self.pending_submission
        if not data:
            self.message.text = "No hay una solicitud pendiente para enviar."
            self.manager.current = "tramites"
            return

        code = data.get("codigo_tramite", "")
        try:
            self.api = ClienteAPI()
            descripcion = json.dumps(data, ensure_ascii=False)
            respuesta = self.api._request(
                "POST", "/solicitudes",
                json={"codigo_tramite": code, "descripcion": descripcion}
            )
            if not isinstance(respuesta, dict) or respuesta.get("ok") is False:
                error = respuesta.get("error", "No fue posible registrar la solicitud.") if isinstance(respuesta, dict) else "Respuesta no válida del servidor."
                self.message.text = f"No se pudo registrar la solicitud: {error}"
                self.manager.current = "tramites"
                return

            codigo_ticket = respuesta.get("codigo_solicitud")
            if not codigo_ticket:
                self.message.text = "El servidor no devolvió un número de ticket. No se puede confirmar el registro."
                self.manager.current = "tramites"
                return

            nombre = data.get("nombre_tramite", self.tramite_actual.get("nombre", "Trámite municipal") if self.tramite_actual else "Trámite municipal")
            self.pending_submission = None
            errores = self._subir_adjuntos(codigo_ticket)
            advertencia = ('No se pudieron subir algunos documentos: '
                           + '; '.join(errores[:3])) if errores else ''
            self.mostrar_ticket(nombre, codigo_ticket, advertencia)
        except Exception as error:
            self.message.text = f"No fue posible registrar la solicitud: {error}"
            self.manager.current = "tramites"

    def mostrar_ticket(self, nombre, codigo_ticket, advertencia=''):
        """Pantalla de salida con opciones de nuevo trámite o cerrar sesión."""
        self.body.clear_widgets()
        self.title.text = "TRÁMITE REGISTRADO"
        panel = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(18))
        panel.add_widget(Label(
            text="¡Su solicitud fue ingresada correctamente!",
            color=GREEN, bold=True, font_size=dp(22),
            size_hint_y=None, height=dp(55)
        ))
        panel.add_widget(Label(
            text=(f"Trámite: {nombre}\n\nTICKET DE SALIDA\n{codigo_ticket}"
                  "\n\nConserve este número para consultar el estado."
                  + (f"\n\nAVISO: {advertencia}" if advertencia else "")),
            color=NAVY, font_size=dp(22), halign="center", valign="middle"
        ))
        panel.add_widget(self._button("REALIZAR OTRO TRÁMITE", lambda *_: self.nuevo_tramite(), 60))
        panel.add_widget(self._button("SALIR / CERRAR SESIÓN", lambda *_: self.cerrar_sesion(), 60))
        self.body.add_widget(panel)
        self.message.text = ""

    def nuevo_tramite(self):
        # Mantiene el token de la sesión para evitar una segunda autenticación.
        self.tramite_actual = None
        self._reiniciar_adjuntos()
        self.pending_submission = None
        self.categoria_actual = ""
        self.mostrar_categorias()
        self.manager.current = "tramites"

    def cerrar_sesion(self):
        """Limpia el token compartido y vuelve al inicio."""
        from api.cliente_api import _TOKEN_COMPARTIDO
        _TOKEN_COMPARTIDO["token"] = None
        self.api.access_token = None
        self.api.session.cookies.clear()
        auth = self.manager.get_screen("autenticacion") if self.manager.has_screen("autenticacion") else None
        if auth:
            auth.usuario_id = None
            auth.usuario = None
            auth.input_rut.text = ""
            auth.input_password.text = ""
            auth.mensaje.text = ""
        self.tramite_actual = None
        self.pending_submission = None
        self.categoria_actual = ""
        self._reiniciar_adjuntos()
        self.manager.current = "inicio"

    def mostrar_exito(self,titulo,detalle):
        self.body.clear_widgets()
        self.title.text = titulo.upper()
        self.message.text = ""
        self.body.add_widget(Label(
            text=detalle, color=NAVY, font_size=dp(20),
            halign="center", valign="middle"
        ))
        self.body.add_widget(self._button(
            "REALIZAR OTRO TRÁMITE",
            lambda *_: self.nuevo_tramite(), 60
        ))
        self.body.add_widget(self._button(
            "SALIR / CERRAR SESIÓN",
            lambda *_: self.cerrar_sesion(), 60
        ))
    def mostrar_error(self,mensaje): self.message.text=mensaje
    def volver_inicio(self,*_): self.manager.current='inicio'