"""
cliente_api.py
Cliente HTTP utilizado por las pantallas Kivy.

El cliente NO accede a SQLite.
Toda la información pasa por FastAPI.
"""

from typing import Any, Optional
import os

import requests


_TOKEN_COMPARTIDO = {"token": None}

class ClienteAPI:
    def __init__(
        self,
        url_base: Optional[str] = None,
        timeout: int = 10,
    ):
        self.url_base = (url_base or os.getenv("TOTEM_API_URL", "https://aptciudadano.dns.army/api")).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.ultima_error: Optional[str] = None
        self.access_token: Optional[str] = _TOKEN_COMPARTIDO.get("token")

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _request(
        self,
        metodo: str,
        ruta: str,
        **kwargs: Any,
    ):
        self.ultima_error = None

        try:
            headers = dict(kwargs.pop("headers", {}))
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            respuesta = self.session.request(
                metodo,
                f"{self.url_base}{ruta}",
                timeout=self.timeout,
                headers=headers,
                **kwargs,
            )

            try:
                datos = respuesta.json()
            except ValueError:
                datos = {
                    "detail": respuesta.text
                }

            if not respuesta.ok:
                if isinstance(datos, dict):
                    mensaje = datos.get("detail") or datos.get("error")
                else:
                    mensaje = str(datos)

                self.ultima_error = (
                    mensaje or
                    f"Error HTTP {respuesta.status_code}"
                )

                return {
                    "ok": False,
                    "status_code": respuesta.status_code,
                    "error": self.ultima_error,
                }

            return datos

        except requests.Timeout:
            self.ultima_error = (
                "La solicitud tardó demasiado. "
                "Verifique la conexión con el servidor."
            )
            return {
                "ok": False,
                "error": self.ultima_error,
            }

        except requests.ConnectionError:
            self.ultima_error = (
                "No fue posible conectarse al servidor municipal."
            )
            return {
                "ok": False,
                "error": self.ultima_error,
            }

        except requests.RequestException as error:
            self.ultima_error = str(error)
            return {
                "ok": False,
                "error": self.ultima_error,
            }

    @staticmethod
    def _es_error(respuesta) -> bool:
        return isinstance(respuesta, dict) and respuesta.get("ok") is False

    # ========================================================
    # HEALTH
    # ========================================================

    def health(self):
        return self._request("GET", "/health")

    # ========================================================
    # USUARIOS
    # ========================================================

    def registrar_usuario(
        self,
        nombre: str,
        apellido: str,
        run: str,
        password: str,
        contacto: str = "",
        direccion: str = "",
        correo: str = "",
    ):
        datos = {
            "nombre": nombre,
            "apellido": apellido,
            "run": run,
            "password": password,
            "contacto": contacto,
            "direccion": direccion,
            "correo": correo,
        }

        return self._request(
            "POST",
            "/usuarios/registro",
            json=datos,
        )

    def login(self, run: str, password: str):
        respuesta = self._request(
            "POST", "/usuarios/login",
            json={"run": run, "password": password},
        )
        if isinstance(respuesta, dict) and respuesta.get("access_token"):
            self.access_token = respuesta["access_token"]
            _TOKEN_COMPARTIDO["token"] = self.access_token
        return respuesta

    def login_funcionario(self, usuario: str, password: str):
        respuesta = self._request("POST", "/auth/funcionarios/login", json={"usuario": usuario, "password": password})
        if isinstance(respuesta, dict) and respuesta.get("access_token"):
            self.access_token = respuesta["access_token"]
            _TOKEN_COMPARTIDO["token"] = self.access_token
        return respuesta

    # ========================================================
    # TRÁMITES
    # ========================================================

    def obtener_tramites(self):
        return self._request(
            "GET",
            "/tramites",
        )

    def obtener_tramite(self, codigo: str):
        return self._request(
            "GET",
            f"/tramites/{codigo}",
        )

    # ========================================================
    # SOLICITUDES
    # ========================================================

    def crear_solicitud(
        self,
        usuario_id: int,
        tramite_id: Optional[int] = None,
        codigo_tramite: Optional[str] = None,
        descripcion: str = "",
    ):
        datos = {
            "usuario_id": usuario_id,
            "tramite_id": tramite_id,
            "codigo_tramite": codigo_tramite,
            "descripcion": descripcion,
        }

        return self._request(
            "POST",
            "/solicitudes",
            json=datos,
        )

    def enviar_solicitud(self, datos: dict):
        """
        Compatibilidad con el cliente anterior.

        Permite seguir usando:
            cliente.enviar_solicitud(datos)
        """
        return self._request(
            "POST",
            "/solicitudes",
            json=datos,
        )

    def consultar_solicitud(self, codigo: str):
        return self._request(
            "GET",
            f"/publico/solicitudes/{codigo}",
        )

    def listar_solicitudes(self):
        return self._request(
            "GET",
            "/solicitudes",
        )

    def actualizar_estado(
        self,
        codigo: str,
        estado: str,
    ):
        return self._request(
            "PUT",
            f"/solicitudes/{codigo}/estado",
            json={
                "estado": estado,
            },
        )

    # ========================================================
    # DOCUMENTOS
    # ========================================================

    def agregar_documento(
        self,
        solicitud_id: int,
        nombre_archivo: str,
        ruta_archivo: str,
        tipo_documento: str = "",
    ):
        return self._request(
            "POST",
            "/documentos",
            json={
                "solicitud_id": solicitud_id,
                "nombre_archivo": nombre_archivo,
                "ruta_archivo": ruta_archivo,
                "tipo_documento": tipo_documento,
            },
        )

    def obtener_documentos(self, solicitud_id: int):
        return self._request(
            "GET",
            f"/solicitudes/{solicitud_id}/documentos",
        )


# Instancia opcional para uso directo desde las pantallas.
cliente_api = ClienteAPI()
