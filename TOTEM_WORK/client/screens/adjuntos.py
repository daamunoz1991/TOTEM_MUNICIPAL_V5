"""Gestión de adjuntos para Tótem Municipal APT.

Android:
- Selector nativo de archivos con androidstorage4kivy.
- Fotografía mediante la aplicación de cámara de Android (ACTION_IMAGE_CAPTURE),
  sin utilizar kivy.uix.camera.Camera.
- La fotografía pasa temporalmente por MediaStore y se copia de inmediato al
  almacenamiento privado de la app; luego se intenta borrar la entrada pública.
- Captura con MediaStore soportada aquí en Android 10 o superior (API 29+).

Escritorio:
- Selector de archivos Kivy como respaldo.
- La captura fotográfica requiere un Android real.

El callback al_recibir recibe una lista de rutas privadas locales.
IMPORTANTE: Este módulo NO controla los límites de documentos establecidos
por tramites.py/documentos.py ni crea campos de anverso/reverso; eso se ajusta
por separado en esas pantallas y, si procede, en el backend.
"""

from datetime import datetime
from pathlib import Path
from shutil import copy2
from uuid import uuid4

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.utils import platform


class GestorAdjuntos:
    EXTENSIONES = {".pdf", ".jpg", ".jpeg", ".png"}
    MAX_BYTES = 10 * 1024 * 1024  # 10 MiB por archivo
    MAX_ARCHIVOS_LOTE = 8          # Máximo por selección, no por solicitud
    CODIGO_CAMARA = 4827

    def __init__(self, al_recibir, al_error):
        self.al_recibir = al_recibir
        self.al_error = al_error
        self._chooser = None
        self._foto_uri = None
        self._callback_android = None
        self._camara_pendiente = False

    def _carpeta_privada(self):
        app = App.get_running_app()
        if app is None:
            raise RuntimeError("La aplicación aún no está inicializada.")
        carpeta = Path(app.user_data_dir) / "adjuntos_temporales"
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta

    def _validar_y_copiar(self, ruta):
        archivo = Path(str(ruta))
        if not archivo.is_file():
            raise ValueError("No se encontró el archivo seleccionado.")
        if archivo.suffix.lower() not in self.EXTENSIONES:
            raise ValueError("Solo se permiten PDF, JPG, JPEG o PNG.")
        tamano = archivo.stat().st_size
        if not 0 < tamano <= self.MAX_BYTES:
            raise ValueError("El archivo está vacío o supera los 10 MB.")
        destino = self._carpeta_privada() / (
            f"{archivo.stem[:35]}_{uuid4().hex[:8]}{archivo.suffix.lower()}"
        )
        copy2(str(archivo), str(destino))
        return str(destino)

    def seleccionar(self, multiple=False):
        if platform == "android":
            try:
                from androidstorage4kivy import Chooser
                self._chooser = Chooser(self._seleccion_android)
                # El selector permite PDF e imágenes; validamos al recibirlos.
                self._chooser.choose_content("*/*", multiple=multiple)
            except Exception as exc:
                self.al_error(f"No se pudo abrir el selector de Android: {exc}")
        else:
            self._seleccion_escritorio(multiple)

    def _seleccion_android(self, elementos):
        try:
            from androidstorage4kivy import SharedStorage
            almacenamiento = SharedStorage()
            seleccionados = list(elementos or [])
            if len(seleccionados) > self.MAX_ARCHIVOS_LOTE:
                raise ValueError(
                    f"Selecciona como máximo {self.MAX_ARCHIVOS_LOTE} archivos por vez."
                )
            rutas = []
            for uri in seleccionados:
                temporal = almacenamiento.copy_from_shared(uri)
                if temporal:
                    try:
                        rutas.append(self._validar_y_copiar(temporal))
                    finally:
                        # Esta ruta es una copia temporal propia de la aplicación.
                        Path(str(temporal)).unlink(missing_ok=True)
            if rutas:
                Clock.schedule_once(
                    lambda dt, items=rutas: self.al_recibir(items), 0
                )
            else:
                Clock.schedule_once(
                    lambda dt: self.al_error("No se seleccionó un archivo compatible."), 0
                )
        except Exception as exc:
            mensaje = str(exc)
            Clock.schedule_once(
                lambda dt, txt=mensaje: self.al_error(
                    f"No fue posible adjuntar el archivo: {txt}"
                ), 0
            )

    def _seleccion_escritorio(self, multiple):
        contenido = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        selector = FileChooserListView(
            path=str(Path.home()),
            multiselect=multiple,
            filters=["*.pdf", "*.PDF", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG",
                     "*.png", "*.PNG"],
        )
        contenido.add_widget(selector)
        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        aceptar = Button(text="AGREGAR")
        cancelar = Button(text="CANCELAR")
        botones.add_widget(aceptar)
        botones.add_widget(cancelar)
        contenido.add_widget(botones)
        popup = Popup(
            title="Seleccionar archivo", content=contenido,
            size_hint=(0.95, 0.90), auto_dismiss=False
        )

        def confirmar(*_):
            if not selector.selection:
                self.al_error("Selecciona un archivo antes de continuar.")
                return
            try:
                if len(selector.selection) > self.MAX_ARCHIVOS_LOTE:
                    raise ValueError("Se seleccionaron demasiados archivos a la vez.")
                rutas = [self._validar_y_copiar(r) for r in selector.selection]
            except Exception as exc:
                self.al_error(str(exc))
                return
            popup.dismiss()
            self.al_recibir(rutas)

        aceptar.bind(on_release=confirmar)
        cancelar.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def tomar_foto(self):
        if platform != "android":
            self.al_error("Para probar la cámara, abre la APK en un dispositivo Android.")
            return
        if self._camara_pendiente:
            return
        try:
            from android.permissions import Permission, request_permissions
            request_permissions([Permission.CAMERA], self._permiso_camara)
        except Exception as exc:
            self.al_error(f"No se pudo solicitar el permiso de cámara: {exc}")

    def _permiso_camara(self, permisos, resultados):
        if resultados and all(resultados):
            Clock.schedule_once(lambda dt: self._abrir_camara_nativa(), 0)
        else:
            Clock.schedule_once(
                lambda dt: self.al_error("Permite el uso de la cámara en Android."), 0
            )

    def _abrir_camara_nativa(self):
        """Abre la app de cámara del teléfono con destino MediaStore."""
        if self._camara_pendiente:
            return
        try:
            from android import activity as android_activity
            from jnius import autoclass, cast

            BuildVersion = autoclass("android.os.Build$VERSION")
            if int(BuildVersion.SDK_INT) < 29:
                raise RuntimeError(
                    "Este modo de captura necesita Android 10 o superior. "
                    "Puedes adjuntar una foto desde el selector de archivos."
                )

            Intent = autoclass("android.content.Intent")
            ClipData = autoclass("android.content.ClipData")
            ContentValues = autoclass("android.content.ContentValues")
            MediaStore = autoclass("android.provider.MediaStore")
            MediaColumns = autoclass("android.provider.MediaStore$MediaColumns")
            MediaImages = autoclass("android.provider.MediaStore$Images$Media")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            actividad = PythonActivity.mActivity
            valores = ContentValues()
            nombre = f"apt_{datetime.now():%Y%m%d_%H%M%S}_{uuid4().hex[:6]}.jpg"
            valores.put(MediaColumns.DISPLAY_NAME, nombre)
            valores.put(MediaColumns.MIME_TYPE, "image/jpeg")
            valores.put(MediaColumns.RELATIVE_PATH, "Pictures/TotemAPT/")

            resolver = actividad.getContentResolver()
            uri = resolver.insert(MediaImages.EXTERNAL_CONTENT_URI, valores)
            if uri is None:
                raise RuntimeError("Android no pudo preparar el archivo de fotografía.")

            self._foto_uri = uri
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, cast("android.os.Parcelable", uri))
            intent.addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION
                | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )
            intent.setClipData(ClipData.newRawUri("foto_totem", uri))

            self._callback_android = self._resultado_camara
            android_activity.bind(on_activity_result=self._callback_android)
            self._camara_pendiente = True
            actividad.startActivityForResult(intent, self.CODIGO_CAMARA)
        except Exception as exc:
            self._camara_pendiente = False
            self._desvincular_resultado()
            self._borrar_foto_compartida()
            self.al_error(f"No se pudo abrir la cámara de Android: {exc}")

    def _resultado_camara(self, codigo, resultado, intent):
        if codigo != self.CODIGO_CAMARA:
            return
        self._desvincular_resultado()
        self._camara_pendiente = False
        if resultado == -1:  # Activity.RESULT_OK
            Clock.schedule_once(lambda dt: self._procesar_foto(), 0)
        else:
            # Cancelación de la cámara: no conservar una foto vacía en Galería.
            self._borrar_foto_compartida()

    def _procesar_foto(self):
        uri = self._foto_uri
        if uri is None:
            self.al_error("No se recibió ninguna fotografía.")
            return
        try:
            from androidstorage4kivy import SharedStorage
            almacenamiento = SharedStorage()
            temporal = almacenamiento.copy_from_shared(uri)
            if not temporal:
                raise RuntimeError("Android no devolvió una fotografía válida.")
            try:
                privada = self._validar_y_copiar(temporal)
            finally:
                Path(str(temporal)).unlink(missing_ok=True)
            # La pantalla que llamó a este gestor recibe una ruta privada.
            self.al_recibir([privada])
        except Exception as exc:
            self.al_error(f"No fue posible guardar la fotografía: {exc}")
        finally:
            # Una CI no debe permanecer en la Galería pública del dispositivo.
            self._borrar_foto_compartida()

    def _desvincular_resultado(self):
        if self._callback_android is None:
            return
        try:
            from android import activity as android_activity
            android_activity.unbind(on_activity_result=self._callback_android)
        except Exception:
            pass
        self._callback_android = None

    def _borrar_foto_compartida(self):
        uri = self._foto_uri
        self._foto_uri = None
        if uri is None or platform != "android":
            return
        try:
            from jnius import autoclass
            actividad = autoclass("org.kivy.android.PythonActivity").mActivity
            actividad.getContentResolver().delete(uri, None, None)
        except Exception:
            # Si Android impide borrar el registro, la foto puede permanecer
            # en Galería. Hay que revisar esto antes de usar CI reales.
            pass
