# Cambios de la versión Kivy

- Inicio de navegación con cuatro categorías: Beneficios sociales, Reserva de horas, Solicitudes municipales y Denuncias y fiscalización.
- Beneficios: Subsidio de Agua Potable, Exención de Derechos de Aseo y Subsidio Único Familiar.
- Agenda: Registro Social de Hogares, Clínica Veterinaria, Esterilización Canina y Felina; consulta horarios y confirma una reserva en API.
- Solicitudes: poda, mantención de luminaria (Vía Pública/Área Verde), retiro de voluminosos y demarcación.
- Denuncias: motivos múltiples, dirección, referencia, descripción y fotografía opcional, sin iniciar sesión ni solicitar datos personales.
- Paleta visual azul marino, turquesa, blanco y gris claro.
- API: ingreso público de denuncias, endpoints de disponibilidad/reserva y carga limitada de PDF/JPG/PNG (máximo 8 MB).

## Antes de ejecutar

1. Recrear `.env` copiando `.env.example` y configurar claves privadas. El ZIP no incluye el `.env` que contenía una contraseña de base de datos.
2. Instalar `requirements-server.txt` y `requirements-client.txt`.
3. Si la base PostgreSQL ya existía, respaldarla y ejecutar `docs/MIGRACION_POSTGRESQL.sql` una sola vez; `create_all()` no modifica columnas existentes.
4. Iniciar la API y luego Kivy. La URL del servidor se configura con `TOTEM_API_URL`.

## Validación pendiente antes de producción

Esta entrega fue validada por compilación sintáctica de Python, no mediante una prueba integrada contra una instancia PostgreSQL/LDAP real. Confirmar conexión, autenticación, permisos, archivos y concurrencia en un entorno de prueba. Los documentos se guardan en `UPLOAD_DIR` (por defecto `uploads`); configurar almacenamiento privado, respaldos, antivirus, límites de cuota y retención. El catálogo web queda sin modificar hasta validar Kivy, según el alcance acordado.
