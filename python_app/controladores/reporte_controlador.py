
from db.conexion import obtener_conexion


def _consultar(sql, parametros=()):

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, parametros)
        return cur.fetchall()

    finally:
        con.close()


def reporte_ingresos(fecha_inicio=None, fecha_fin=None):

    where = (
        " WHERE DATE(c.fecha_hora_cobro) BETWEEN %s AND %s"
        if fecha_inicio and fecha_fin else ""
    )

    params = (
        (fecha_inicio, fecha_fin)
        if where else ()
    )

    resumen = _consultar(
        "SELECT COALESCE(SUM(monto_total),0) AS total, "
        "COUNT(*) AS cantidad "
        "FROM cobros c" + where,
        params
    )[0]

    por_dia = _consultar(
        "SELECT DATE(c.fecha_hora_cobro) AS periodo, "
        "SUM(c.monto_total) AS total "
        "FROM cobros c" + where +
        " GROUP BY DATE(c.fecha_hora_cobro) "
        "ORDER BY periodo",
        params
    )

    por_metodo = _consultar(
        "SELECT mp.nombre AS categoria, "
        "SUM(c.monto_total) AS total "
        "FROM cobros c "
        "JOIN metodos_pago mp "
        "ON mp.metodo_pago_id=c.metodo_pago_id" +
        (
            " WHERE DATE(c.fecha_hora_cobro) BETWEEN %s AND %s"
            if where else ""
        ) +
        " GROUP BY mp.metodo_pago_id, mp.nombre "
        "ORDER BY total DESC",
        params
    )

    return {
        "resumen": resumen,
        "serie": por_dia,
        "categorias": por_metodo
    }


def reporte_movimiento(fecha_inicio=None, fecha_fin=None):

    where = (
        " WHERE DATE(s.fecha_hora_entrada) BETWEEN %s AND %s"
        if fecha_inicio and fecha_fin else ""
    )

    params = (
        (fecha_inicio, fecha_fin)
        if where else ()
    )

    resumen = _consultar(
        "SELECT COUNT(*) AS entradas, "
        "SUM(CASE WHEN s.fecha_hora_salida IS NOT NULL "
        "THEN 1 ELSE 0 END) AS salidas, "
        "SUM(CASE WHEN s.fecha_hora_salida IS NULL "
        "THEN 1 ELSE 0 END) AS dentro "
        "FROM servicios s" + where,
        params
    )[0]

    horas = _consultar(
        "SELECT HOUR(s.fecha_hora_entrada) AS hora, "
        "COUNT(*) AS cantidad "
        "FROM servicios s" + where +
        " GROUP BY HOUR(s.fecha_hora_entrada) "
        "ORDER BY hora",
        params
    )

    return {
        "resumen": resumen,
        "serie": horas
    }


def reporte_clientes():

    return _consultar(
        "SELECT tc.nombre AS categoria, "
        "COUNT(DISTINCT c.cliente_id) AS clientes "
        "FROM tipos_cliente tc "
        "LEFT JOIN clientes c "
        "ON c.tipo_cliente_id=tc.tipo_cliente_id "
        "AND c.activo=1 "
        "GROUP BY tc.tipo_cliente_id, tc.nombre "
        "ORDER BY tc.nombre"
    )


def reporte_pensiones():

    resumen = _consultar(
        "SELECT ep.nombre AS estado, "
        "COUNT(p.pension_id) AS cantidad "
        "FROM estados_pension ep "
        "LEFT JOIN pensiones p "
        "ON p.estado_pension_id=ep.estado_pension_id "
        "GROUP BY ep.estado_pension_id, ep.nombre "
        "ORDER BY ep.nombre"
    )

    pagos = _consultar(
        "SELECT DATE_FORMAT(pp.periodo_inicio,'%Y-%m') AS periodo, "
        "SUM(pp.monto_pagado) AS total, "
        "COUNT(*) AS pagos "
        "FROM pagos_pension pp "
        "GROUP BY DATE_FORMAT(pp.periodo_inicio,'%Y-%m') "
        "ORDER BY periodo"
    )

    return {
        "estados": resumen,
        "pagos": pagos
    }
