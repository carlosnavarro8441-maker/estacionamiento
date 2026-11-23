
USE estacionamiento_publico;

-- Estados de las pensiones
INSERT IGNORE INTO estados_pension
(estado_pension_id, nombre)
VALUES
(1, 'activa'),
(2, 'vencida');

-- Métodos de pago
INSERT IGNORE INTO metodos_pago
(metodo_pago_id, nombre)
VALUES
(1, 'efectivo'),
(2, 'tarjeta');

-- Tipos de servicio
INSERT IGNORE INTO tipos_servicio
(tipo_servicio_id, nombre)
VALUES
(1, 'cajon'),
(2, 'pension');

-- Tarifa mensual de pensión
-- CAMBIAR 0.00 POR EL PRECIO ACORDADO

INSERT INTO tarifas
(tipo_servicio_id, tipo_cliente_id, hora_desde,
 hora_hasta, precio, unidad, activa)

SELECT 2, NULL, NULL, NULL, 0.00, 'mes', 1
WHERE NOT EXISTS (
    SELECT 1
    FROM tarifas
    WHERE tipo_servicio_id = 2
    AND unidad = 'mes'
    AND activa = 1
);

-- Descuento por antigüedad
-- CAMBIAR 0.00 POR EL PORCENTAJE ACORDADO

INSERT INTO descuentos_pension
(anios_minimos, porcentaje, activo)

SELECT 2, 0.00, 1
WHERE NOT EXISTS (
    SELECT 1
    FROM descuentos_pension
    WHERE anios_minimos = 2
    AND activo = 1
);
