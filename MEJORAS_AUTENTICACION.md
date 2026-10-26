# Mejoras de autenticación ciudadana — TOTEM_V7

## Cambios incluidos
- Validación del RUT chileno (dígito verificador) en FastAPI y en las pantallas Kivy/web.
- Normalización del RUT a `12345678-5` en la API.
- Respuesta clara cuando el RUT ya tiene una cuenta, incluyendo tratamiento de registros simultáneos.
- La web valida que el RUT de la cuenta coincida con el RUT ingresado en la solicitud **antes** de crear la cuenta, evitando crear cuentas por error.
- Enlace desde el formulario de registro para volver al inicio de sesión y completar el RUT.
- Mostrar/ocultar contraseña en la web.
- Kivy exige contraseña de al menos 10 caracteres y confirmación de contraseña.
- Se retiró el registro en consola del RUT completo durante el inicio de sesión/registro.
- Se conservan los endpoints existentes y la autenticación de funcionarios LDAP.

## Archivos modificados
- `server/main.py`
- `web/index.html`
- `web/app.js`
- `web/styles.css`
- `client/screens/registro.py`
- `client/screens/autenticacion.py`

## Aplicación
1. Respaldar la carpeta del proyecto actual.
2. Extraer el ZIP y comparar los archivos antes de sobrescribir la instalación.
3. No reemplazar el `.env` existente. Este ZIP excluye deliberadamente `.env` por contener configuración/posibles secretos.
4. Instalar los archivos modificados manteniendo las variables de entorno actuales.
5. Reiniciar FastAPI y abrir la web recargando sin caché (Ctrl+F5).
6. Probar un RUT válido, un RUT inválido, contraseña de menos de 10 caracteres, confirmación distinta y RUT ya registrado.
7. Probar en web y Kivy con la misma base de datos de pruebas.

## Nota
La validación de RUT comprueba formato y dígito verificador; no acredita la identidad de la persona. La recuperación de contraseña no se añadió porque requiere definir un canal verificado (correo/SMS) y un flujo de restablecimiento seguro.
