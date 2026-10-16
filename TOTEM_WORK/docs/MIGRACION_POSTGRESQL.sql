-- Ejecutar una sola vez sobre la base existente antes de iniciar la nueva API.
-- Realizar respaldo y probar primero en una copia de la base.
ALTER TABLE solicitudes ALTER COLUMN usuario_id DROP NOT NULL;
CREATE TABLE IF NOT EXISTS reservas (
  id SERIAL PRIMARY KEY,
  codigo_reserva VARCHAR(32) NOT NULL UNIQUE,
  servicio VARCHAR(80) NOT NULL,
  fecha VARCHAR(10) NOT NULL,
  hora VARCHAR(5) NOT NULL,
  nombre VARCHAR(150) NOT NULL,
  contacto VARCHAR(80) NOT NULL DEFAULT '',
  estado VARCHAR(20) NOT NULL DEFAULT 'RESERVADA',
  fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uq_reserva_bloque_estado UNIQUE (servicio, fecha, hora, estado)
);
