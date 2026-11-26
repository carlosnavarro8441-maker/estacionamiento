-- =====================================================================
-- CAPACIDAD DEL ESTACIONAMIENTO
-- Ejecutar DESPUÉS de estacionamiento_publico.sql
-- Se puede correr más de una vez sin problema.
-- =====================================================================
USE estacionamiento_publico;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS configuracion (
    clave VARCHAR(50) NOT NULL,
    valor VARCHAR(100) NOT NULL,
    PRIMARY KEY (clave)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Capacidad inicial de ejemplo: el equipo debe acordar el número real
-- (se puede cambiar después desde la pantalla de Capacidad).
INSERT IGNORE INTO configuracion (clave, valor) VALUES ('capacidad_total', '50');