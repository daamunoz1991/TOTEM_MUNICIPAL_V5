# Tótem Municipal — versión depurada (base de trabajo)

Esta carpeta conserva las pantallas Kivy y recursos del ZIP recibido, elimina cachés/base SQLite del repositorio y centraliza la API FastAPI con PostgreSQL. Incluye una página web de prueba que consume la misma API.

> **Importante:** es una base de integración para desarrollo y pruebas, no un despliegue municipal listo para producción. Antes de publicar datos reales, revisar roles, tratamiento de documentos, validación de RUT, políticas de contraseñas, certificados TLS, auditoría y pruebas de seguridad.

## Estructura

- `main.py`: entrada Kivy existente.
- `client/screens/`: pantallas Kivy originales conservadas.
- `client/api/cliente_api.py`: cliente HTTP; URL configurable mediante `TOTEM_API_URL`.
- `server/main.py`: API central FastAPI.
- `server/database/database.py`: modelos SQLAlchemy y PostgreSQL.
- `server/auth/`: hash/token y autenticación LDAP de funcionarios en el backend.
- `web/index.html`: página web de demostración que consulta salud y catálogo de trámites.
- `docker-compose.yml`: PostgreSQL local para desarrollo.

## 1. Requisitos

Python 3.12 recomendado. Instalar Docker Desktop para levantar PostgreSQL local, o preparar una instancia PostgreSQL administrada. No copiar la base SQLite original al repositorio.

## 2. Configurar PostgreSQL

Copia `.env.example` a `.env` y define valores privados. En particular, establece `POSTGRES_PASSWORD` y un `TOKEN_SECRET` aleatorio de al menos 32 caracteres. `.env` está excluido de Git.

Con Docker Compose:

```powershell
Copy-Item .env.example .env
# Edita .env y añade POSTGRES_PASSWORD=una_clave_larga
# Cambia TOKEN_SECRET por un secreto aleatorio largo
docker compose up -d postgres
```

Configura `DATABASE_URL` con la misma contraseña, por ejemplo:

`postgresql+psycopg://totem_app:CLAVE@127.0.0.1:5432/totem_municipal`

No uses esa clave de ejemplo literalmente.

## 3. Instalar dependencias y ejecutar API

Desde la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-server.txt
uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
```

Prueba `http://127.0.0.1:8001/health` y la documentación `http://127.0.0.1:8001/docs`.

Para que otros dispositivos de la red accedan, cambia `127.0.0.1` por `0.0.0.0`, limita el firewall a redes autorizadas y publica detrás de un proxy HTTPS. No expongas directamente el puerto de desarrollo a Internet.

## 4. Ejecutar el tótem

En otra terminal, activa el entorno e instala dependencias del cliente:

```powershell
pip install -r requirements-client.txt
$env:TOTEM_API_URL="http://127.0.0.1:8001"
python main.py
```

En otro equipo, reemplaza la URL por la URL/IP privada del servidor. Para producción, usar HTTPS y certificado confiable.

## 5. Página web de prueba

Abre `web/index.html` en un navegador o sirve la carpeta con un servidor estático. Ajusta la URL de API en la página. El origen del sitio debe estar incluido en `CORS_ORIGINS` del servidor.

Esta página solo demuestra conexión y catálogo; todavía no implementa formularios ciudadanos completos ni autenticación de funcionarios desde una interfaz web.

## 6. LDAP / Active Directory

El backend dispone de `/auth/funcionarios/login`. Define `LDAP_HOST`, `LDAP_DOMAIN` y `LDAP_BASE_DN` con los valores de la organización. El código exige LDAPS en el puerto 636 y validación de certificado. Instala la CA del dominio en el sistema donde se ejecuta la API si corresponde.

El formato de usuario y las reglas de acceso/grupos deben ajustarse con el administrador de Active Directory. La API valida credenciales, pero antes de producción se debe agregar autorización basada en grupos/roles municipales. No expongas LDAP a Internet.

## 7. Seguridad y limitaciones conocidas

- La API usa token firmado con HMAC y expiración, pero la gestión de revocación, renovación y auditoría debe completarse antes de producción.
- El flujo de creación de solicitudes requiere token de ciudadano; los endpoints administrativos requieren token de funcionario.
- Las pantallas Kivy originales se conservaron para no perder trabajo. Algunas pantallas pueden requerir ajustes de integración, especialmente el panel administrativo, porque ahora debe iniciar sesión como funcionario para obtener un token de rol.
- La ruta de documentos guarda metadatos, no implementa carga segura de archivos binarios. No guardar rutas arbitrarias del sistema ni servir documentos sin autorización.
- No se migraron usuarios ni solicitudes desde la base SQLite original. La base original se excluyó deliberadamente por seguridad. Diseñar una migración auditada después de verificar y anonimizar los datos.
- El `create_all` crea tablas nuevas; no reemplaza una herramienta de migraciones para futuras modificaciones de esquema.

## 8. GitHub

```powershell
git init
git status
git add .
git status
git commit -m "Base depurada Tótem Municipal con PostgreSQL"
```

Revisa `git status` antes del commit: `.env`, archivos `.db`, datos personales y credenciales no deben aparecer. Luego crea un repositorio privado en GitHub, añade el remoto que te entrega GitHub y ejecuta `git push -u origin main`.
