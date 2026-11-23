
USE estacionamiento_publico;

DROP TRIGGER IF EXISTS trg_entrada_abierta_insert;
DROP TRIGGER IF EXISTS trg_entrada_abierta_update;
DROP TRIGGER IF EXISTS trg_salida_valida_insert;
DROP TRIGGER IF EXISTS trg_salida_valida_update;
DROP TRIGGER IF EXISTS trg_pension_activa_insert;
DROP TRIGGER IF EXISTS trg_pension_activa_update;

DELIMITER $$

-- UNA ENTRADA ABIERTA POR VEHICULO

CREATE TRIGGER trg_entrada_abierta_insert
BEFORE INSERT ON servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_hora_salida IS NULL
    AND EXISTS (
        SELECT 1
        FROM servicios
        WHERE vehiculo_id = NEW.vehiculo_id
        AND fecha_hora_salida IS NULL
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El vehiculo ya tiene una entrada abierta';
    END IF;
END$$

CREATE TRIGGER trg_entrada_abierta_update
BEFORE UPDATE ON servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_hora_salida IS NULL
    AND EXISTS (
        SELECT 1
        FROM servicios
        WHERE vehiculo_id = NEW.vehiculo_id
        AND fecha_hora_salida IS NULL
        AND servicio_id <> OLD.servicio_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El vehiculo ya tiene otra entrada abierta';
    END IF;
END$$

-- VALIDAR FECHA DE SALIDA

CREATE TRIGGER trg_salida_valida_insert
BEFORE INSERT ON servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_hora_salida IS NOT NULL
    AND NEW.fecha_hora_salida <= NEW.fecha_hora_entrada THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'La salida debe ser posterior a la entrada';
    END IF;
END$$

CREATE TRIGGER trg_salida_valida_update
BEFORE UPDATE ON servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_hora_salida IS NOT NULL
    AND NEW.fecha_hora_salida <= NEW.fecha_hora_entrada THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'La salida debe ser posterior a la entrada';
    END IF;
END$$

-- UNA PENSION ACTIVA POR VEHICULO

CREATE TRIGGER trg_pension_activa_insert
BEFORE INSERT ON pensiones
FOR EACH ROW
BEGIN
    IF NEW.estado_pension_id = 1
    AND EXISTS (
        SELECT 1
        FROM pensiones
        WHERE vehiculo_id = NEW.vehiculo_id
        AND estado_pension_id = 1
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El vehiculo ya tiene una pension activa';
    END IF;
END$$

CREATE TRIGGER trg_pension_activa_update
BEFORE UPDATE ON pensiones
FOR EACH ROW
BEGIN
    IF NEW.estado_pension_id = 1
    AND EXISTS (
        SELECT 1
        FROM pensiones
        WHERE vehiculo_id = NEW.vehiculo_id
        AND estado_pension_id = 1
        AND pension_id <> OLD.pension_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'El vehiculo ya tiene otra pension activa';
    END IF;
END$$

DELIMITER ;
