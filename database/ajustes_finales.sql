-- =====================================================================
-- AJUSTES FINALES (requisitos del PDF del Módulo 3)
-- Ejecutar DESPUÉS de importar estacionamiento_publico.sql
-- (y de restricciones.sql). Se puede correr más de una vez sin problema.
-- =====================================================================
USE estacionamiento_publico;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. Tarifas por hora del cajón (requisito 5)
--    Cliente de paso:     $30.00 las horas 1 a 5  | $25.00 de la hora 6 en adelante
--    Cliente frecuente:   $26.00 las horas 1 a 5  | $22.00 de la hora 6 en adelante
--    (la tarifa del cliente de paso estaba en $40.00)
-- ---------------------------------------------------------------------
UPDATE tarifas t
JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id
SET t.precio = 30.00
WHERE t.tipo_servicio_id = 1 AND t.unidad = 'hora'
  AND tc.nombre = 'paso' AND t.hora_desde = 1;

UPDATE tarifas t
JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id
SET t.precio = 25.00
WHERE t.tipo_servicio_id = 1 AND t.unidad = 'hora'
  AND tc.nombre = 'paso' AND t.hora_desde = 6;

UPDATE tarifas t
JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id
SET t.precio = 26.00
WHERE t.tipo_servicio_id = 1 AND t.unidad = 'hora'
  AND tc.nombre = 'frecuente' AND t.hora_desde = 1;

UPDATE tarifas t
JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id
SET t.precio = 22.00
WHERE t.tipo_servicio_id = 1 AND t.unidad = 'hora'
  AND tc.nombre = 'frecuente' AND t.hora_desde = 6;

-- ---------------------------------------------------------------------
-- 2. Nombres de los tipos de servicio
--    En el dump los acentos se perdieron ('caj?n', 'pensi?n').
--    Los reportes por servicio (requisito 10) usan estos nombres.
-- ---------------------------------------------------------------------
UPDATE tipos_servicio SET nombre = 'cajón'   WHERE tipo_servicio_id = 1;
UPDATE tipos_servicio SET nombre = 'pensión' WHERE tipo_servicio_id = 2;

-- ---------------------------------------------------------------------
-- 3. Pensión (requisito 6)
--    OJO: el PDF NO dice cuánto cuesta la pensión ni qué porcentaje de
--    descuento se da. Los valores de abajo son EJEMPLOS: cámbialos desde
--    la pantalla "Tarifas" de la aplicación (o aquí) con los valores
--    que acuerde tu equipo.
--    El descuento aplica a pensiones con MÁS de 2 años de antigüedad.
-- ---------------------------------------------------------------------
UPDATE tarifas SET precio = 1500.00
WHERE tipo_servicio_id = 2 AND unidad = 'mes' AND precio = 0;

INSERT INTO tarifas
(tipo_servicio_id, tipo_cliente_id, hora_desde, hora_hasta, precio, unidad, activa)
SELECT 2, NULL, NULL, NULL, 1500.00, 'mes', 1
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM tarifas WHERE tipo_servicio_id = 2 AND unidad = 'mes'
);

UPDATE descuentos_pension SET porcentaje = 10.00
WHERE anios_minimos = 2 AND porcentaje = 0;

INSERT INTO descuentos_pension (anios_minimos, porcentaje, activo)
SELECT 2, 10.00, 1
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM descuentos_pension WHERE anios_minimos = 2
);

-- ---------------------------------------------------------------------
-- Revisión rápida
-- ---------------------------------------------------------------------
SELECT t.tarifa_id, ts.nombre AS servicio, COALESCE(tc.nombre, '-') AS cliente,
       t.hora_desde, t.hora_hasta, t.precio, t.unidad
FROM tarifas t
JOIN tipos_servicio ts ON ts.tipo_servicio_id = t.tipo_servicio_id
LEFT JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id
ORDER BY t.tarifa_id;

SELECT * FROM descuentos_pension;
