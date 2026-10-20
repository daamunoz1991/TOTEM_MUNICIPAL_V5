"""API central FastAPI.
Ejecutar desde la raíz del proyecto:
python -m uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
"""
import os
import json
import secrets
import string
import logging
from pathlib import Path
from datetime import date
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import (
    FastAPI, Depends, HTTPException, UploadFile, File
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from server.database.database import (
    get_db, init_db, Usuario, Tramite, Solicitud, Documento, Reserva
)
from server.auth.security import (
    hash_password, verify_password, issue_token, current_user,
    require_staff, decode_token
)
from server.auth.ldap import autenticar_funcionario

logger = logging.getLogger("totem.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Tótem Municipal API",
    version="3.0.0",
    lifespan=lifespan,
)

origins = [
    x.strip()
    for x in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:5500",
    ).split(",")
    if x.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class Registro(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    run: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=10, max_length=128)
    contacto: str = Field(default="", max_length=50)
    direccion: str = Field(default="", max_length=250)
    correo: str = Field(default="", max_length=150)


class Login(BaseModel):
    run: str
    password: str


class StaffLogin(BaseModel):
    usuario: str
    password: str


class SolicitudNueva(BaseModel):
    usuario_id: int | None = None
    tramite_id: int | None = None
    codigo_tramite: str | None = None
    descripcion: str = Field(default="", max_length=2000)


class ReservaNueva(BaseModel):
    servicio: str = Field(min_length=3, max_length=80)
    fecha: str = Field(min_length=10, max_length=10)
    hora: str = Field(min_length=5, max_length=5)
    nombre: str = Field(min_length=2, max_length=150)
    rut: str = Field(default="", max_length=20)
    contacto: str = Field(default="", max_length=80)


class EstadoUpdate(BaseModel):
    estado: str


class DocumentoNuevo(BaseModel):
    solicitud_id: int
    nombre_archivo: str = Field(min_length=1, max_length=255)
    ruta_archivo: str = Field(min_length=1, max_length=500)
    tipo_documento: str = Field(default="", max_length=100)


ESTADOS = {
    "INGRESADA",
    "EN_REVISION",
    "PENDIENTE_ANTECEDENTES",
    "APROBADA",
    "RECHAZADA",
    "CERRADA",
}


def usuario_publico(u):
    return {
        "id": u.id,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "run": u.run,
        "contacto": u.contacto,
        "direccion": u.direccion,
        "correo": u.correo,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else "",
        "activo": int(u.activo),
    }


def tramite_publico(t):
    return {
        "id": t.id,
        "codigo": t.codigo,
        "nombre": t.nombre,
        "descripcion": t.descripcion,
        "departamento": t.departamento,
        "requiere_autenticacion": int(t.requiere_autenticacion),
        "documentos_requeridos": t.documentos_requeridos,
        "estado": t.estado,
    }


def solicitud_publica(s):
    return {
        "id": s.id,
        "codigo_solicitud": s.codigo_solicitud,
        "usuario_id": s.usuario_id,
        "tramite_id": s.tramite_id,
        "descripcion": s.descripcion,
        "estado": s.estado,
        "fecha_solicitud": s.fecha_solicitud.isoformat() if s.fecha_solicitud else "",
    }


def solicitud_detalle(s):
    d = solicitud_publica(s)
    u = s.usuario
    t = s.tramite
    d.update({
        "usuario_nombre": u.nombre if u else "Denuncia anónima",
        "usuario_apellido": u.apellido if u else "",
        "usuario_run": u.run if u else "",
        "usuario_contacto": u.contacto if u else "",
        "usuario_correo": u.correo if u else "",
        "codigo_tramite": t.codigo,
        "nombre_tramite": t.nombre,
        "departamento": t.departamento,
        "requiere_autenticacion": int(t.requiere_autenticacion),
        "documentos_requeridos": t.documentos_requeridos,
    })
    return d


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Tótem Municipal API funcionando",
        "version": app.version,
    }


@app.post("/usuarios/registro", status_code=201)
def registrar(data: Registro, db: Session = Depends(get_db)):
    run = "".join(
        c for c in data.run.upper() if c.isalnum() or c == "-"
    )
    if db.scalar(select(Usuario).where(Usuario.run == run)):
        raise HTTPException(409, "Ya existe una cuenta para ese RUT.")

    u = Usuario(
        nombre=data.nombre.strip(),
        apellido=data.apellido.strip(),
        run=run,
        password_hash=hash_password(data.password),
        contacto=data.contacto,
        direccion=data.direccion,
        correo=data.correo,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return usuario_publico(u)


@app.post("/usuarios/login")
def login(data: Login, db: Session = Depends(get_db)):
    run = "".join(
        c for c in data.run.upper() if c.isalnum() or c == "-"
    )
    u = db.scalar(
        select(Usuario).where(
            Usuario.run == run,
            Usuario.activo.is_(True),
        )
    )
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(401, "RUT o contraseña incorrectos.")

    return {
        "mensaje": "Login exitoso",
        "usuario": usuario_publico(u),
        "access_token": issue_token(u.run, "ciudadano", u.id),
        "token_type": "bearer",
    }


@app.post("/auth/funcionarios/login")
def login_funcionario(data: StaffLogin):
    if not autenticar_funcionario(data.usuario, data.password):
        raise HTTPException(
            401,
            "No fue posible validar las credenciales institucionales.",
        )
    return {
        "mensaje": "Login institucional exitoso",
        "access_token": issue_token(data.usuario, "funcionario"),
        "token_type": "bearer",
    }


@app.get("/tramites")
def listar_tramites(db: Session = Depends(get_db)):
    return [
        tramite_publico(t)
        for t in db.scalars(
            select(Tramite)
            .where(Tramite.estado == "ACTIVO")
            .order_by(Tramite.nombre)
        ).all()
    ]


@app.get("/tramites/{codigo}")
def obtener_tramite(codigo: str, db: Session = Depends(get_db)):
    t = db.scalar(
        select(Tramite).where(
            Tramite.codigo.ilike(codigo),
            Tramite.estado == "ACTIVO",
        )
    )
    if not t:
        raise HTTPException(404, "Trámite no encontrado o inactivo.")
    return tramite_publico(t)


@app.post("/solicitudes", status_code=201)
def crear_solicitud(
    data: SolicitudNueva,
    user: dict = Depends(current_user),
    db: Session = Depends(get_db),
):
    if user.get("role") != "ciudadano":
        raise HTTPException(
            403,
            "Solo una cuenta ciudadana puede ingresar solicitudes.",
        )
    u = db.get(Usuario, user.get("uid"))
    if not u or not u.activo:
        raise HTTPException(401, "La cuenta no está activa.")
    if data.usuario_id is not None and data.usuario_id != u.id:
        raise HTTPException(
            403,
            "No puede crear solicitudes a nombre de otra persona.",
        )

    t = (
        db.get(Tramite, data.tramite_id)
        if data.tramite_id
        else db.scalar(
            select(Tramite).where(Tramite.codigo == data.codigo_tramite)
        )
    )
    if not t or t.estado != "ACTIVO":
        raise HTTPException(404, "Trámite no encontrado o inactivo.")

    codigo = "TM-" + "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(10)
    )
    s = Solicitud(
        codigo_solicitud=codigo,
        usuario_id=u.id,
        tramite_id=t.id,
        descripcion=data.descripcion,
        estado="INGRESADA",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return solicitud_publica(s)


@app.post("/solicitudes/publica", status_code=201)
def crear_solicitud_publica(
    data: dict,
    db: Session = Depends(get_db),
):
    """
    Ingreso público para denuncias y requerimientos autorizados.
    No exige cuenta ciudadana. Los errores se registran en la consola.
    """
    codigo_tramite = str(data.get("codigo_tramite", "")).strip().upper()
    permitidos = {"DEN", "POD", "LUM", "VOL", "DEM", "SAP", "EDA", "SUF"}

    if codigo_tramite not in permitidos:
        raise HTTPException(400, "Tipo de solicitud no permitido.")

    descripcion = str(data.get("descripcion", "")).strip()
    if not descripcion:
        raise HTTPException(422, "La descripción es obligatoria.")
    if len(descripcion) > 6000:
        raise HTTPException(422, "La descripción excede el máximo permitido.")

    nombres = {
        "DEN": ("Denuncias y Fiscalización", "Fiscalización"),
        "POD": ("Solicitud de poda", "Operaciones"),
        "LUM": ("Mantención de luminaria", "Operaciones"),
        "VOL": ("Retiro de voluminosos", "Operaciones"),
        "DEM": ("Solicitud de demarcación", "Operaciones"),
        "SAP": ("Subsidio de Agua Potable", "Departamento Social"),
        "EDA": ("Exención de Derechos de Aseo", "Departamento Social"),
        "SUF": ("Subsidio Único Familiar", "Departamento Social"),
    }

    try:
        tramite = db.scalar(
            select(Tramite).where(Tramite.codigo == codigo_tramite)
        )

        if tramite is None:
            nombre, departamento = nombres[codigo_tramite]
            tramite = Tramite(
                codigo=codigo_tramite,
                nombre=nombre,
                departamento=departamento,
                descripcion="Solicitud ingresada mediante Tótem Municipal",
                documentos_requeridos="",
                requiere_autenticacion=False,
                estado="ACTIVO",
            )
            db.add(tramite)
            db.flush()
        elif tramite.estado != "ACTIVO":
            raise HTTPException(
                409,
                "El trámite existe, pero está inactivo. Contacte al administrador.",
            )

        codigo = "TM-" + "".join(
            secrets.choice(string.ascii_uppercase + string.digits)
            for _ in range(10)
        )
        solicitud = Solicitud(
            codigo_solicitud=codigo,
            usuario_id=None,
            tramite_id=tramite.id,
            descripcion=json.dumps(data, ensure_ascii=False),
            estado="INGRESADA",
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud_publica(solicitud)

    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "Error de base de datos al registrar solicitud pública (%s)",
            codigo_tramite,
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo guardar la solicitud en la base de datos. "
                "Revise la consola de FastAPI para conocer el detalle."
            ),
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Error inesperado al registrar solicitud pública (%s)",
            codigo_tramite,
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Ocurrió un error interno al registrar la solicitud. "
                "Revise la consola de FastAPI para conocer el detalle."
            ),
        ) from exc


@app.get("/reservas/disponibilidad")
def disponibilidad(
    servicio: str,
    fecha: str,
    db: Session = Depends(get_db),
):
    try:
        fecha_obj = date.fromisoformat(fecha)
    except ValueError:
        raise HTTPException(422, "La fecha debe tener formato AAAA-MM-DD.")

    if fecha_obj < date.today():
        raise HTTPException(422, "No se puede reservar una fecha pasada.")

    servicios_validos = {
        "Agenda para el Registro Social de Hogares",
        "Registro Social de Hogares",
        "Atención Clínica Veterinaria",
        "Esterilización Canina",
        "Esterilización Felina",
    }
    if servicio not in servicios_validos:
        raise HTTPException(400, "Servicio no válido.")

    dia_semana = fecha_obj.weekday()  # 0=Lunes, 6=Domingo

    # Reglas de horarios por servicio
    if servicio == "Esterilización Canina":
        # Martes (1) y Jueves (3), solo hasta 09:18 cada 2 minutos
        if dia_semana not in [1, 3]:
            horarios = []
        else:
            horarios = [
                f"{h:02d}:{m:02d}"
                for h in range(9, 10)  # Solo hora 9
                for m in range(0, 20, 2)  # 09:00 a 09:18
            ]
    elif servicio == "Esterilización Felina":
        # Lunes (0), Miércoles (2) y Viernes (4), solo hasta 09:18 cada 2 minutos
        if dia_semana not in [0, 2, 4]:
            horarios = []
        else:
            horarios = [
                f"{h:02d}:{m:02d}"
                for h in range(9, 10)  # Solo hora 9
                for m in range(0, 20, 2)  # 09:00 a 09:18
            ]
    else:
        # Otros servicios: Lunes a Jueves 09:00-17:00, Viernes hasta 16:00, cada 20 minutos
        if dia_semana in [0, 1, 2, 3]:  # Lunes a Jueves
            horarios = [
                f"{h:02d}:{m:02d}"
                for h in range(9, 17)  # 09:00 a 16:59
                for m in (0, 20, 40)  # Cada 20 minutos
            ]
        elif dia_semana == 4:  # Viernes - última hora 16:00
            horarios = [
                f"{h:02d}:{m:02d}"
                for h in range(9, 16)  # 09:00 a 15:59
                for m in (0, 20, 40)  # Cada 20 minutos
            ]
            horarios.append("16:00")  # Agregar última hora 16:00
        else:  # Sábado y Domingo
            horarios = []

    try:
        ocupados = set(
            db.scalars(
                select(Reserva.hora).where(
                    Reserva.servicio == servicio,
                    Reserva.fecha == fecha,
                    Reserva.estado == "RESERVADA",
                )
            ).all()
        )
    except SQLAlchemyError as e:
        logger.exception("Error consultando reservas ocupadas")
        raise HTTPException(500, "Error al consultar disponibilidad")

    return {
        "servicio": servicio,
        "fecha": fecha,
        "horarios": [
            {"hora": h, "disponible": h not in ocupados}
            for h in horarios
        ],
    }


@app.post("/reservas", status_code=201)
def crear_reserva(data: ReservaNueva, db: Session = Depends(get_db)):
    try:
        fecha_obj = date.fromisoformat(data.fecha)
    except ValueError:
        raise HTTPException(422, "Fecha inválida.")

    if fecha_obj < date.today():
        raise HTTPException(422, "No se puede reservar una fecha pasada.")

    servicios_validos = {
        "Agenda para el Registro Social de Hogares",
        "Registro Social de Hogares",
        "Atención Clínica Veterinaria",
        "Esterilización Canina",
        "Esterilización Felina",
    }
    if data.servicio not in servicios_validos:
        raise HTTPException(400, "Servicio no válido.")

    existente = db.scalar(
        select(Reserva).where(
            Reserva.servicio == data.servicio,
            Reserva.fecha == data.fecha,
            Reserva.hora == data.hora,
            Reserva.estado == "RESERVADA",
        )
    )
    if existente:
        raise HTTPException(
            409,
            "Ese horario acaba de ser reservado. Seleccione otro.",
        )

    codigo = "RES-" + "".join(
        secrets.choice(string.ascii_uppercase + string.digits)
        for _ in range(10)
    )
    reserva = Reserva(
        codigo_reserva=codigo,
        servicio=data.servicio,
        fecha=data.fecha,
        hora=data.hora,
        nombre=data.nombre.strip(),
        rut=data.rut.strip(),
        contacto=data.contacto.strip(),
    )
    db.add(reserva)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Error al guardar la reserva")
        raise HTTPException(
            409,
            "No fue posible reservar el horario; actualice la disponibilidad.",
        ) from exc

    db.refresh(reserva)
    return {
        "id": reserva.id,
        "codigo_reserva": reserva.codigo_reserva,
        "servicio": reserva.servicio,
        "fecha": reserva.fecha,
        "hora": reserva.hora,
        "estado": reserva.estado,
    }


@app.post("/solicitudes/{codigo}/archivos", status_code=201)
def cargar_archivo(
    codigo: str,
    archivo: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
):
    """Carga documentos e imágenes con límite de tamaño y extensión."""
    s = db.scalar(
        select(Solicitud).where(
            Solicitud.codigo_solicitud == codigo.upper()
        )
    )
    if not s:
        raise HTTPException(404, "Solicitud no encontrada.")

    if s.tramite.codigo != "DEN":
        if not credentials:
            raise HTTPException(
                401,
                "Debe iniciar sesión para adjuntar archivos a esta solicitud.",
            )
        user = decode_token(credentials.credentials)
        if (
            user.get("role") != "funcionario"
            and s.usuario_id != user.get("uid")
        ):
            raise HTTPException(
                403,
                "No tiene permiso para adjuntar archivos a esta solicitud.",
            )

    ext = Path(archivo.filename or "").suffix.lower()
    if ext not in {".pdf", ".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            415,
            "Formato no permitido. Use PDF, JPG o PNG.",
        )

    contenido = archivo.file.read(8 * 1024 * 1024 + 1)
    if len(contenido) > 8 * 1024 * 1024:
        raise HTTPException(413, "El archivo supera 8 MB.")

    carpeta = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = secrets.token_hex(16) + ext
    destino = carpeta / nombre
    destino.write_bytes(contenido)

    doc = Documento(
        solicitud_id=s.id,
        nombre_archivo=Path(archivo.filename or nombre).name,
        ruta_archivo=str(destino),
        tipo_documento=archivo.content_type or "",
    )
    db.add(doc)
    try:
        db.commit()
        db.refresh(doc)
    except Exception as exc:
        db.rollback()
        logger.exception("Error al registrar el archivo adjunto")
        try:
            destino.unlink(missing_ok=True)
        except OSError:
            logger.warning("No fue posible eliminar archivo huérfano: %s", destino)
        raise HTTPException(
            500,
            "No fue posible registrar el archivo adjunto.",
        ) from exc

    return {
        "id": doc.id,
        "nombre_archivo": doc.nombre_archivo,
        "mensaje": "Archivo recibido.",
    }


@app.get("/publico/solicitudes/{codigo}")
def consultar_solicitud_publica(codigo: str, db: Session = Depends(get_db)):
    """Consulta pública mínima por código de ticket, sin exponer datos personales."""
    s = db.scalar(
        select(Solicitud).where(Solicitud.codigo_solicitud == codigo.upper())
    )
    if not s:
        raise HTTPException(404, "No encontramos una solicitud con ese código.")
    return {
        "codigo_solicitud": s.codigo_solicitud,
        "nombre_tramite": s.tramite.nombre if s.tramite else "Trámite municipal",
	"departamento": s.tramite.departamento if s.tramite and s.tramite.departamento else "Por asignar",
        "estado": s.estado,
        "fecha_solicitud": s.fecha_solicitud.isoformat() if s.fecha_solicitud else "",
    }


@app.get("/solicitudes/{codigo}")
def consultar_solicitud(
    codigo: str,
    user: dict = Depends(current_user),
    db: Session = Depends(get_db),
):
    s = db.scalar(
        select(Solicitud).where(
            Solicitud.codigo_solicitud == codigo.upper()
        )
    )
    if not s:
        raise HTTPException(404, "Solicitud no encontrada.")
    if (
        user.get("role") != "funcionario"
        and s.usuario_id != user.get("uid")
    ):
        raise HTTPException(
            403,
            "No tiene permiso para consultar esta solicitud.",
        )
    return solicitud_detalle(s)


@app.get("/solicitudes")
def listar_solicitudes(
    user: dict = Depends(require_staff),
    db: Session = Depends(get_db),
):
    return [
        solicitud_detalle(s)
        for s in db.scalars(
            select(Solicitud).order_by(Solicitud.fecha_solicitud.desc())
        ).all()
    ]


@app.put("/solicitudes/{codigo}/estado")
def actualizar_estado(
    codigo: str,
    data: EstadoUpdate,
    user: dict = Depends(require_staff),
    db: Session = Depends(get_db),
):
    estado = data.estado.strip().upper()
    if estado not in ESTADOS:
        raise HTTPException(
            400,
            detail={
                "mensaje": "Estado no válido",
                "estados_permitidos": sorted(ESTADOS),
            },
        )

    s = db.scalar(
        select(Solicitud).where(
            Solicitud.codigo_solicitud == codigo.upper()
        )
    )
    if not s:
        raise HTTPException(404, "Solicitud no encontrada.")

    s.estado = estado
    db.commit()
    return {
        "mensaje": "Estado actualizado",
        "codigo": s.codigo_solicitud,
        "nuevo_estado": estado,
    }


@app.post("/documentos", status_code=201)
def agregar_documento(
    data: DocumentoNuevo,
    user: dict = Depends(current_user),
    db: Session = Depends(get_db),
):
    s = db.get(Solicitud, data.solicitud_id)
    if not s:
        raise HTTPException(404, "Solicitud no encontrada.")
    if (
        user.get("role") != "funcionario"
        and s.usuario_id != user.get("uid")
    ):
        raise HTTPException(
            403,
            "No tiene permiso para adjuntar documentos a esta solicitud.",
        )

    doc = Documento(
        solicitud_id=data.solicitud_id,
        nombre_archivo=data.nombre_archivo,
        ruta_archivo=data.ruta_archivo,
        tipo_documento=data.tipo_documento,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": doc.id,
        "solicitud_id": doc.solicitud_id,
        "nombre_archivo": doc.nombre_archivo,
        "ruta_archivo": doc.ruta_archivo,
        "tipo_documento": doc.tipo_documento,
        "fecha_carga": doc.fecha_carga.isoformat() if doc.fecha_carga else "",
    }


@app.get("/solicitudes/{solicitud_id}/documentos")
def obtener_documentos(
    solicitud_id: int,
    user: dict = Depends(current_user),
    db: Session = Depends(get_db),
):
    s = db.get(Solicitud, solicitud_id)
    if not s:
        raise HTTPException(404, "Solicitud no encontrada.")
    if (
        user.get("role") != "funcionario"
        and s.usuario_id != user.get("uid")
    ):
        raise HTTPException(
            403,
            "No tiene permiso para consultar estos documentos.",
        )
    return [
        {
            "id": d.id,
            "solicitud_id": d.solicitud_id,
            "nombre_archivo": d.nombre_archivo,
            "ruta_archivo": d.ruta_archivo,
            "tipo_documento": d.tipo_documento,
            "fecha_carga": d.fecha_carga.isoformat() if d.fecha_carga else "",
        }
        for d in s.documentos
    ]
