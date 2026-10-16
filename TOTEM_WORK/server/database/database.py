"""Persistencia PostgreSQL mediante SQLAlchemy."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, String, Integer, Text, Boolean,
    DateTime, ForeignKey, func, UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    sessionmaker, relationship
)

# Cargar el .env ubicado en la raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No se encontró DATABASE_URL. Revisa el archivo .env "
        "en la raíz del proyecto."
    )

if not DATABASE_URL.startswith("postgresql+psycopg://"):
    raise RuntimeError(
        "DATABASE_URL debe usar PostgreSQL con psycopg."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    run: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    contacto: Mapped[str] = mapped_column(String(50), default="")
    direccion: Mapped[str] = mapped_column(String(250), default="")
    correo: Mapped[str] = mapped_column(String(150), default="")
    fecha_registro: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    solicitudes: Mapped[list["Solicitud"]] = relationship(
        back_populates="usuario"
    )


class Tramite(Base):
    __tablename__ = "tramites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(180))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    departamento: Mapped[str] = mapped_column(String(120), default="")
    requiere_autenticacion: Mapped[bool] = mapped_column(Boolean, default=True)
    documentos_requeridos: Mapped[str] = mapped_column(Text, default="")
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO")


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo_solicitud: Mapped[str] = mapped_column(
        String(32), unique=True, index=True
    )
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), index=True, nullable=True
    )
    tramite_id: Mapped[int] = mapped_column(ForeignKey("tramites.id"))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    estado: Mapped[str] = mapped_column(String(30), default="INGRESADA", index=True)
    fecha_solicitud: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped[Usuario] = relationship(back_populates="solicitudes")
    tramite: Mapped[Tramite] = relationship()
    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="solicitud"
    )


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(
        ForeignKey("solicitudes.id"), index=True
    )
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    ruta_archivo: Mapped[str] = mapped_column(String(500))
    tipo_documento: Mapped[str] = mapped_column(String(100), default="")
    fecha_carga: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    solicitud: Mapped[Solicitud] = relationship(back_populates="documentos")


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (UniqueConstraint("servicio", "fecha", "hora", "estado", name="uq_reserva_bloque_estado"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo_reserva: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    servicio: Mapped[str] = mapped_column(String(80), index=True)
    fecha: Mapped[str] = mapped_column(String(10), index=True)
    hora: Mapped[str] = mapped_column(String(5), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    rut: Mapped[str] = mapped_column(String(20), default="")
    contacto: Mapped[str] = mapped_column(String(80), default="")
    estado: Mapped[str] = mapped_column(String(20), default="RESERVADA")
    fecha_creacion: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Código, nombre, departamento y documentos informativos de cada trámite.
TRAMITES = [
    ("SAP", "Subsidio Agua Potable", "Departamento Social",
     "Cédula de identidad; RSH; Cuenta de agua al día"),
    ("EDA", "Excepción Derechos de Aseo", "Departamento Social",
     "Cédula de identidad; Rol del domicilio; documentación de respaldo"),
    ("SUF", "Subsidio Único Familiar", "Departamento Social",
     "Cédula de identidad; Certificado de nacimiento"),
    ("POD", "Solicitud de poda", "Operaciones", "Dirección; punto de referencia; descripción; fotografía opcional"),
    ("LUM", "Solicitud de mantención de luminaria", "Operaciones", "Dirección; punto de referencia; área; descripción; fotografía opcional"),
    ("VOL", "Retiro de voluminosos", "Operaciones", "Dirección; punto de referencia; descripción; fotografía opcional"),
    ("DEM", "Solicitud de demarcación", "Operaciones", "Dirección; punto de referencia; descripción; fotografía opcional"),
    ("DEN", "Denuncias y fiscalización", "Fiscalización", "Motivo(s); dirección; punto de referencia; descripción; fotografía opcional"),
    ("RSH", "Registro Social de Hogares", "Departamento Social",
     "Antecedentes del hogar según solicitud"),
    ("AS", "Atención Asistente Social", "Departamento Social",
     "Antecedentes del caso"),
    ("VET", "Atención Clínica Veterinaria", "Veterinaria",
     "Según prestación"),
    ("ESTC", "Esterilización Canina", "Veterinaria",
     "Antecedentes de la mascota"),
    ("ESTF", "Esterilización Felina", "Veterinaria",
     "Antecedentes de la mascota"),
    ("ORG", "Constitución Nueva Organización", "Organizaciones Comunitarias",
     "Antecedentes de la organización"),
    ("LEGAL", "Asesoría Técnica Legal", "UTL", "Antecedentes del caso"),
    ("ESP", "Uso Espacio Público", "Gabinete", "Antecedentes de la solicitud"),
    ("BEC", "Orientación de beneficios", "DIDECO", "Antecedentes según beneficio"),
    ("DIS", "Atención Discapacidad", "Discapacidad", "Antecedentes pertinentes"),
    ("JOV", "Atención Jóvenes y Diversidad", "Jóvenes y Diversidad",
     "Antecedentes pertinentes"),
    ("MAY", "Atención Personas Mayores", "Adulto Mayor",
     "Antecedentes pertinentes"),
    ("OMIL", "Orientación Laboral OMIL", "OMIL",
     "Currículum y antecedentes laborales"),
]


# Descripciones orientativas para la pantalla de detalle del Tótem.
# Validar con cada unidad municipal antes de publicarlas oficialmente.
DESCRIPCIONES_TRAMITES = {
    "SAP": (
        "Permite solicitar orientación y evaluación para acceder "
        "al Subsidio de Agua Potable, de acuerdo con los requisitos "
        "y antecedentes correspondientes."
    ),
    "EDA": (
        "Permite solicitar la evaluación para acceder a la exención "
        "del pago de los Derechos de Aseo Domiciliario, conforme "
        "a los requisitos municipales vigentes."
    ),
    "SUF": (
        "Permite recibir orientación sobre el Subsidio Único Familiar, "
        "sus requisitos y los antecedentes necesarios para solicitarlo."
    ),
    "POD": "Permite ingresar una solicitud de poda de árbol en un espacio que corresponda a la gestión municipal.",
    "LUM": "Permite reportar una luminaria que requiere mantención e indicar si está en vía pública o área verde.",
    "VOL": "Permite solicitar orientación y retiro de residuos voluminosos según cobertura municipal.",
    "DEM": "Permite solicitar evaluación de demarcación vial o peatonal.",
    "DEN": "Permite ingresar una denuncia de fiscalización sin crear una cuenta ciudadana.",
    "RSH": (
        "Permite solicitar orientación sobre el Registro Social de "
        "Hogares y los antecedentes necesarios para realizar trámites "
        "o actualizar información del hogar."
    ),
    "AS": (
        "Permite solicitar atención y orientación de un profesional "
        "del área social para exponer una situación y conocer las "
        "alternativas de apoyo municipal disponibles."
    ),
    "VET": (
        "Permite consultar información y orientación sobre la atención "
        "clínica veterinaria municipal y las condiciones de acceso "
        "a las prestaciones disponibles."
    ),
    "ESTC": (
        "Permite consultar los requisitos y antecedentes necesarios "
        "para solicitar la prestación de esterilización canina."
    ),
    "ESTF": (
        "Permite consultar los requisitos y antecedentes necesarios "
        "para solicitar la prestación de esterilización felina."
    ),
    "ORG": (
        "Permite recibir orientación sobre el proceso de constitución "
        "de una nueva organización comunitaria y los antecedentes "
        "necesarios para iniciar la gestión."
    ),
    "LEGAL": (
        "Permite solicitar orientación sobre asesoría técnica legal "
        "municipal y conocer los antecedentes necesarios para evaluar "
        "la consulta planteada."
    ),
    "ESP": (
        "Permite consultar los requisitos y antecedentes para solicitar "
        "autorización de uso del espacio público, según el tipo "
        "de actividad propuesta."
    ),
    "BEC": (
        "Permite recibir orientación sobre beneficios sociales, "
        "sus requisitos y los antecedentes que podrían ser necesarios "
        "según el beneficio consultado."
    ),
    "DIS": (
        "Permite solicitar orientación sobre atención municipal "
        "relacionada con discapacidad y conocer los canales "
        "de atención disponibles."
    ),
    "JOV": (
        "Permite acceder a orientación sobre los servicios y apoyos "
        "municipales dirigidos a jóvenes y a personas atendidas "
        "por el área de Jóvenes y Diversidad."
    ),
    "MAY": (
        "Permite solicitar orientación sobre los servicios, programas "
        "y apoyos municipales dirigidos a las personas mayores."
    ),
    "OMIL": (
        "Permite acceder a orientación laboral, información sobre "
        "oportunidades de empleo y apoyo para la búsqueda de trabajo."
    ),
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea las tablas y agrega o actualiza las descripciones de trámites."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for codigo, nombre, departamento, docs in TRAMITES:
            tramite = db.query(Tramite).filter_by(codigo=codigo).first()
            descripcion = DESCRIPCIONES_TRAMITES.get(
                codigo,
                "Consulte al departamento responsable para obtener "
                "información sobre este trámite."
            )

            if tramite is None:
                tramite = Tramite(
                    codigo=codigo,
                    nombre=nombre,
                    departamento=departamento,
                    documentos_requeridos=docs,
                    descripcion=descripcion,
                )
                db.add(tramite)
            else:
                # Solo actualiza descripción para no sobrescribir cambios
                # hechos en nombre, departamento o documentos requeridos.
                tramite.descripcion = descripcion

        db.commit()
