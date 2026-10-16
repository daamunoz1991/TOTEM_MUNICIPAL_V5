-- Migración: agregar columna rut a la tabla reservas
-- Ejecutar en PostgreSQL

ALTER TABLE reservas ADD COLUMN IF NOT EXISTS rut VARCHAR(20) DEFAULT '';

-- Verificar que la columna se agregó correctamente
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'reservas' AND column_name = 'rut';
