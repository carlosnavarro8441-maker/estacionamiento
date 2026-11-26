-- =====================================================================
-- CAJONES DEL ESTACIONAMIENTO
-- Ejecutar DESPUÉS de estacionamiento_publico.sql y capacidad.sql.
-- Se puede correr más de una vez (XAMPP usa MariaDB).
-- =====================================================================
USE estacionamiento_publico;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS cajones (
    cajon_id INT NOT NULL AUTO_INCREMENT,
    numero INT NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (cajon_id),
    UNIQUE KEY uk_cajones_numero (numero)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Cada servicio puede decir en qué cajón está (opcional)
ALTER TABLE servicios ADD COLUMN IF NOT EXISTS cajon_id INT(11) NULL;
ALTER TABLE servicios DROP FOREIGN KEY IF EXISTS fk_servicios_cajon;
ALTER TABLE servicios
    ADD CONSTRAINT fk_servicios_cajon
    FOREIGN KEY (cajon_id) REFERENCES cajones (cajon_id);