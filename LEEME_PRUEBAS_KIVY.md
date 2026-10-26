# Tótem Municipal V7 — paquete de prueba Kivy + web

## Cambios incluidos
- `client/main.py`: parte del archivo principal Kivy entregado por la usuaria; carga el `.env` del proyecto antes de inicializar pantallas.
- `client/screens/autenticacion.py`: opción para solicitar código de recuperación por correo y definir nueva contraseña; se corrige el color de éxito que faltaba.
- `client/api/cliente_api.py`: usa `TOTEM_API_URL` y por defecto `http://127.0.0.1:8001` para pruebas en el mismo PC; incluye consulta pública de reservas.
- `client/screens/seguimiento.py`: consulta tickets `TM-` y reservas `RES-`.
- `server/main.py`: endpoint público `/publico/reservas/{codigo}` para el seguimiento de reservas, sin devolver datos personales.
- `web/app.js`: versión corregida que separa seguimiento de solicitudes y reservas.

## Prueba local en Windows
1. Descomprime el paquete. Copia `.env.example` a `.env` y revisa `DATABASE_URL`, `TOKEN_SECRET`, `SMTP_*`, `UPLOAD_DIR` y `TOTEM_API_URL`. No compartas ni subas `.env` a GitHub.
2. Activa el mismo entorno virtual que ya utilizas para el proyecto. Si todavía no instalaste las dependencias, instala las dependencias requeridas por tu versión de FastAPI/Kivy antes de iniciar; este paquete no reemplaza ni modifica tu entorno virtual.
3. En una primera ventana PowerShell, inicia FastAPI: `python -m uvicorn server.main:app --host 127.0.0.1 --port 8001`.
4. Abre `http://127.0.0.1:8001/health` y confirma que responde `status: ok`.
5. En otra ventana PowerShell, inicia Kivy con `python client/main.py`. Si habitualmente ejecutas desde `client`, también puedes usar `python main.py` desde esa carpeta.
6. Prueba recuperación: cuenta con correo ya registrado → “¿Olvidó su contraseña?” → solicitar código → introducir código recibido → contraseña nueva de al menos 10 caracteres.
7. Prueba seguimiento con un código `TM-...` y uno `RES-...`.

## Direcciones de API
- Mismo PC: `TOTEM_API_URL=http://127.0.0.1:8001`.
- Kivy en otro PC/tablet de la misma LAN: configurar la IP LAN del equipo donde corre FastAPI (por ejemplo `http://192.168.1.85:8001`) y permitir el puerto solo en la red autorizada.
- En AWS, no uses `127.0.0.1` en la aplicación cliente para referirte al servidor; usa el dominio/HTTPS público previsto.

## Importante
Este paquete no contiene el archivo `.env` real ni contraseñas. El funcionamiento final depende de las variables de entorno, dependencias instaladas, conexión a PostgreSQL/LDAP y acceso al almacenamiento. Antes de producción, prueba en un entorno controlado y no expongas SMB/445 a Internet.


## Correcciones de esta revisión estática
- Unifica los colores de Registro y Administración con azul marino #16324F, turquesa #18A6A6 y fondo #F2F5F8.
- Corrige contraste de textos en formulario, documentos y confirmación para fondos claros.
- Añade confirmación de contraseña y validación básica de correo al registro Kivy.
- Muestra la confirmación de registro en la pantalla de inicio de sesión, donde el usuario puede verla.
- Añade manejo de errores inesperados en los callbacks de recuperación y evita imprimir el RUT completo en consola.
- Completa `.env.example` con variables SMTP y dirección local de API.

## Límite de validación
Se verificó la sintaxis de los archivos Python. No se ejecutó la app conectada a PostgreSQL, LDAP, Gmail ni al recurso compartido de documentos; esas pruebas deben hacerse en el equipo de desarrollo antes de desplegar.

## Seguridad del archivo de configuración
Este paquete no contiene el archivo `.env` real. Mantén ese archivo fuera de ZIP compartidos y de GitHub. Si el ZIP original contenía contraseñas o claves reales, cámbialas antes de producción.
