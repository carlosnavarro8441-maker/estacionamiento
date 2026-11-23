
USE estacionamiento_publico;

-- REPORTE 1: INGRESOS DEL ESTACIONAMIENTO

SELECT
    DATE(fecha_hora_cobro) AS fecha,
    COUNT(*) AS cantidad_cobros,
    SUM(monto_total) AS total_ingresos
FROM cobros
WHERE DATE(fecha_hora_cobro)
BETWEEN '2026-01-01' AND '2026-12-31'
GROUP BY DATE(fecha_hora_cobro)
ORDER BY fecha;


-- REPORTE 2: ENTRADAS Y SALIDAS

SELECT
    COUNT(*) AS entradas,
    SUM(fecha_hora_salida IS NOT NULL) AS salidas,
    SUM(fecha_hora_salida IS NULL) AS vehiculos_dentro
FROM servicios;


-- REPORTE 3: CLIENTES POR TIPO

SELECT
    tc.nombre AS tipo_cliente,
    COUNT(DISTINCT c.cliente_id) AS cantidad
FROM tipos_cliente tc
LEFT JOIN clientes c
    ON c.tipo_cliente_id = tc.tipo_cliente_id
    AND c.activo = 1
GROUP BY tc.tipo_cliente_id, tc.nombre;


-- REPORTE 4: PENSIONES POR ESTADO

SELECT
    ep.nombre AS estado,
    COUNT(p.pension_id) AS cantidad
FROM estados_pension ep
LEFT JOIN pensiones p
    ON p.estado_pension_id = ep.estado_pension_id
GROUP BY ep.estado_pension_id, ep.nombre;


-- INGRESOS POR PAGOS DE PENSION

SELECT
    DATE_FORMAT(periodo_inicio, '%Y-%m') AS periodo,
    COUNT(*) AS cantidad_pagos,
    SUM(monto_pagado) AS total_pagado
FROM pagos_pension
GROUP BY DATE_FORMAT(periodo_inicio, '%Y-%m')
ORDER BY periodo;
