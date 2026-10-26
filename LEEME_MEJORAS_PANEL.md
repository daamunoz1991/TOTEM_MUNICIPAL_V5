# Tótem Municipal V6 — paquete de mejoras de interfaz y panel

Este paquete contiene el código fuente del proyecto sin `.env`, sin `.venv`, sin `.git` y sin archivos de adjuntos. No contiene credenciales ni copias de la base de datos.

## Mejoras incluidas

- Panel de funcionarios con paleta institucional alineada al tótem Kivy: azul marino, turquesa, blanco y gris claro.
- Inicio de sesión LDAP con rol administrador explícito mediante `TOTEM_ADMIN_USERS`.
- La cuenta `Dmunoz` puede quedar habilitada como administrador al agregarla a `TOTEM_ADMIN_USERS`.
- Administrador: listado transversal, historial, acceso a adjuntos, derivación por área y vista de indicadores.
- Funcionarios: acceso a solicitudes de su área, asignación a sí mismos, historial y adjuntos autorizados por área.
- Endpoint seguro para consultar metadatos y abrir/descargar documentos adjuntos.
- Vista separada para solicitudes con estado `COMPLETADA` o `CERRADA`.
- Indicadores agregados por área y estado desde PostgreSQL.
- No se elimina ni reemplaza ninguna tabla existente. Las tablas de asignación e historial existentes se conservan.

## Antes de probar

1. Haz copia de seguridad del proyecto actual.
2. No sobrescribas tu `.env`; mantenlo fuera de este paquete.
3. Abre tu `.env` local y agrega la siguiente variable:

   `TOTEM_ADMIN_USERS=Dmunoz`

   Si hay más de un administrador, separa los UID por coma, por ejemplo `TOTEM_ADMIN_USERS=Dmunoz,admin.secundario`.
4. Verifica que `Dmunoz` sea exactamente el UID de la cuenta LDAP autorizada.
5. Mantén `LDAP_STAFF_AREAS` para los funcionarios normales. El administrador no necesita tener un área individual en esa variable.
6. Reinicia FastAPI después de guardar `.env`.

## Prueba local en Windows

Desde la raíz del proyecto:

```powershell
python -m uvicorn server.main:app --host 0.0.0.0 --port 8001
```

En otra ventana, sirve la web:

```powershell
cd web
python -m http.server 5500
```

Abre:
- Portal ciudadano: `http://127.0.0.1:5500/index.html`
- Panel funcionario: `http://127.0.0.1:5500/panel_funcionario_totem.html`
- Documentación API: `http://127.0.0.1:8001/docs`

En el panel, la dirección de API debe ser `http://192.168.1.85:8001` si se está probando desde la red municipal. Para abrir el panel desde el mismo equipo también se puede usar `http://127.0.0.1:8001` como API.

## Pruebas funcionales recomendadas

1. Iniciar sesión como `Dmunoz`: debe aparecer la insignia de administrador y solicitudes de varias áreas.
2. Iniciar sesión como `prueba.social`: debe ver solo Departamento Social.
3. En el panel, abrir documentos adjuntos de una solicitud de su área.
4. Como administrador, derivar una solicitud a un área habilitada. Para asignar a un funcionario específico, su UID debe existir en `LDAP_STAFF_AREAS` con esa misma área.
5. Cambiar una solicitud de prueba a `COMPLETADA`; debe desaparecer de “En gestión” y aparecer en “Archivo de completadas”.
6. Abrir “Indicadores de atención” con el administrador.

## Consideraciones técnicas importantes

- La autorización se valida en FastAPI, no solo en los botones del HTML.
- El administrador se autoriza mediante una lista explícita de UID en `TOTEM_ADMIN_USERS`. El archivo `server/auth/ldap.py` de esta versión valida credenciales LDAP, pero no consulta membresía de grupos LDAP; por eso esta lista es el control de privilegios para esta etapa.
- El estado `COMPLETADA` es nuevo a nivel de lógica de aplicación; no requiere columna nueva. El esquema de estados se valida en el backend.
- El acceso a archivos está restringido al directorio configurado en `UPLOAD_DIR`. Asegúrate de que esa variable apunte al mismo directorio donde se guardan los adjuntos.
- Para AWS/producción: no publiques el panel por HTTP abierto. Configura HTTPS, CORS restringido a los dominios reales, `TOKEN_SECRET` aleatorio de al menos 32 caracteres y acceso a PostgreSQL únicamente por la red privada/WireGuard.
- El ZIP original que se compartió incluía un `.env` y una carpeta `.venv`. Si los valores del `.env` eran reales, considera rotar la contraseña de PostgreSQL y `TOKEN_SECRET`; no subas `.env`, contraseñas, claves privadas ni adjuntos de usuarios a repositorios.
