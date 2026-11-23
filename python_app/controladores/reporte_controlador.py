
from datetime import date

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


# ---------------------------------------------------------------------------
# Reportes por año (requisitos 7, 8, 9 y 10 del proyecto)
# ---------------------------------------------------------------------------

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def anios_disponibles():
    """Años con movimientos (entradas, cobros o pagos de pensión), del más nuevo al más viejo."""
    filas = _consultar(
        "SELECT DISTINCT YEAR(fecha) AS anio FROM ("
        "SELECT fecha_hora_entrada AS fecha FROM servicios "
        "UNION ALL SELECT fecha_hora_cobro FROM cobros "
        "UNION ALL SELECT fecha_pago FROM pagos_pension"
        ") t WHERE fecha IS NOT NULL ORDER BY anio DESC"
    )
    anios = [int(f["anio"]) for f in filas]
    hoy = date.today().year
    if hoy not in anios:
        anios.insert(0, hoy)
    return anios


def _por_mes(sql, anio):
    """Ejecuta una consulta (mes, cantidad) y devuelve una lista de 12 valores."""
    por_mes = {int(f["mes"]): f["cantidad"] for f in _consultar(sql, (anio,))}
    return [por_mes.get(m, 0) for m in range(1, 13)]


def _entradas_por_mes(anio):
    return _por_mes(
        "SELECT MONTH(fecha_hora_entrada) AS mes, COUNT(*) AS cantidad "
        "FROM servicios WHERE YEAR(fecha_hora_entrada)=%s "
        "GROUP BY MONTH(fecha_hora_entrada)",
        anio
    )


def reporte_entradas_salidas_mensual(anio):
    """Requisito 7: entradas y salidas de cada mes del año."""
    entradas = _entradas_por_mes(anio)
    salidas = _por_mes(
        "SELECT MONTH(fecha_hora_salida) AS mes, COUNT(*) AS cantidad "
        "FROM servicios "
        "WHERE fecha_hora_salida IS NOT NULL AND YEAR(fecha_hora_salida)=%s "
        "GROUP BY MONTH(fecha_hora_salida)",
        anio
    )
    return [
        {"mes": MESES[i], "entradas": int(entradas[i]), "salidas": int(salidas[i])}
        for i in range(12)
    ]


def reporte_meses_demanda(anio):
    """Requisito 8: meses con mayor demanda (más entradas) del año, de mayor a menor."""
    entradas = _entradas_por_mes(anio)
    meses = [{"mes": MESES[i], "entradas": int(entradas[i])} for i in range(12)]
    ranking = sorted(
        [m for m in meses if m["entradas"] > 0],
        key=lambda m: m["entradas"],
        reverse=True
    )
    return {"meses": meses, "ranking": ranking}


def reporte_horarios_demanda(anio):
    """Requisito 9: horas del día con mayor demanda (entradas) del año."""
    filas = _consultar(
        "SELECT HOUR(fecha_hora_entrada) AS hora, COUNT(*) AS cantidad "
        "FROM servicios WHERE YEAR(fecha_hora_entrada)=%s "
        "GROUP BY HOUR(fecha_hora_entrada)",
        (anio,)
    )
    por_hora = {int(f["hora"]): int(f["cantidad"]) for f in filas}
    horas = [{"hora": h, "entradas": por_hora.get(h, 0)} for h in range(24)]
    ranking = sorted(
        [h for h in horas if h["entradas"] > 0],
        key=lambda h: h["entradas"],
        reverse=True
    )
    return {"horas": horas, "ranking": ranking}


def reporte_ingresos_por_servicio(anio):
    """Requisito 10: ingresos del año por servicio (cajón y pensión), total y por mes.

    Cajón = cobros por hora (solo los vehículos de paso/frecuentes generan cobro).
    Pensión = pagos de pensión (se ubican por su fecha de pago).
    """
    cajon = _por_mes(
        "SELECT MONTH(fecha_hora_cobro) AS mes, SUM(monto_total) AS cantidad "
        "FROM cobros WHERE YEAR(fecha_hora_cobro)=%s "
        "GROUP BY MONTH(fecha_hora_cobro)",
        anio
    )
    pension = _por_mes(
        "SELECT MONTH(fecha_pago) AS mes, SUM(monto_pagado) AS cantidad "
        "FROM pagos_pension WHERE YEAR(fecha_pago)=%s "
        "GROUP BY MONTH(fecha_pago)",
        anio
    )
    cajon = [float(x) for x in cajon]
    pension = [float(x) for x in pension]

    return {
        "totales": [
            {"servicio": "Cajón", "total": sum(cajon)},
            {"servicio": "Pensión", "total": sum(pension)},
        ],
        "mensual": [
            {"mes": MESES[i], "cajon": cajon[i], "pension": pension[i]}
            for i in range(12)
        ],
        "total": sum(cajon) + sum(pension),
    }
