
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from db.conexion import obtener_conexion
from modelos.pension import calcular_antiguedad


def calcular_monto(monto_base, porcentaje=0):

    base = Decimal(str(monto_base))
    descuento = Decimal(str(porcentaje))

    if base <= 0 or descuento < 0 or descuento > 100:
        raise ValueError(
            "La tarifa debe ser positiva y el descuento "
            "debe estar entre 0 y 100."
        )

    return (
        base * (
            Decimal("1") -
            descuento / Decimal("100")
        )
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def registrar_pago(
    pension_id,
    periodo_inicio,
    periodo_fin,
    metodo_pago_id,
    usuario_id
):

    if isinstance(periodo_inicio, str):
        periodo_inicio = date.fromisoformat(periodo_inicio)

    if isinstance(periodo_fin, str):
        periodo_fin = date.fromisoformat(periodo_fin)

    if periodo_fin < periodo_inicio:
        raise ValueError(
            "El periodo final no puede ser anterior al inicial."
        )

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        con.start_transaction()

        # Consultar pensión
        cur.execute(
            "SELECT p.pension_id, p.fecha_inicio, "
            "p.fecha_fin, p.estado_pension_id, "
            "t.precio AS monto_base "
            "FROM pensiones p "
            "JOIN tarifas t ON t.tarifa_id=p.tarifa_id "
            "WHERE p.pension_id=%s FOR UPDATE",
            (pension_id,)
        )

        pension = cur.fetchone()

        if not pension:
            raise ValueError(
                "La pensión indicada no existe."
            )

        if pension["estado_pension_id"] != 1:
            raise ValueError(
                "No se pueden registrar pagos "
                "para una pensión que no está activa."
            )

        if periodo_inicio < pension["fecha_inicio"]:
            raise ValueError(
                "El periodo no puede comenzar antes de la pensión."
            )

        if (
            pension["fecha_fin"]
            and periodo_fin > pension["fecha_fin"]
        ):
            raise ValueError(
                "El periodo no puede terminar después "
                "de la fecha final de la pensión."
            )

        # Evitar pagos duplicados o periodos traslapados
        cur.execute(
            "SELECT pago_pension_id FROM pagos_pension "
            "WHERE pension_id=%s "
            "AND NOT (periodo_fin < %s OR periodo_inicio > %s)",
            (pension_id, periodo_inicio, periodo_fin)
        )

        if cur.fetchone():
            raise ValueError(
                "Ya existe un pago que se cruza con ese periodo."
            )

        # Calcular antigüedad
        anios = calcular_antiguedad(
            pension["fecha_inicio"]
        )

        # Buscar descuento
        cur.execute(
            "SELECT descuento_id, porcentaje "
            "FROM descuentos_pension "
            "WHERE activo=1 AND anios_minimos < %s "
            "ORDER BY anios_minimos DESC LIMIT 1",
            (anios,)
        )

        descuento = cur.fetchone()

        porcentaje = (
            descuento["porcentaje"]
            if descuento else 0
        )

        monto = calcular_monto(
            pension["monto_base"],
            porcentaje
        )

        # Registrar pago
        cur.execute(
            "INSERT INTO pagos_pension "
            "(pension_id, periodo_inicio, periodo_fin, "
            "monto_base, descuento_id, monto_pagado, "
            "fecha_pago, metodo_pago_id, usuario_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                pension_id,
                periodo_inicio,
                periodo_fin,
                pension["monto_base"],
                descuento["descuento_id"] if descuento else None,
                monto,
                datetime.now(),
                metodo_pago_id,
                usuario_id
            )
        )

        pago_id = cur.lastrowid

        con.commit()

        return {
            "pago_pension_id": pago_id,
            "monto_base": pension["monto_base"],
            "porcentaje": porcentaje,
            "monto_pagado": monto
        }

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def listar_historial(pension_id):

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT pp.*, mp.nombre AS metodo_pago, "
            "dp.porcentaje "
            "FROM pagos_pension pp "
            "LEFT JOIN metodos_pago mp "
            "ON mp.metodo_pago_id=pp.metodo_pago_id "
            "LEFT JOIN descuentos_pension dp "
            "ON dp.descuento_id=pp.descuento_id "
            "WHERE pp.pension_id=%s "
            "ORDER BY pp.periodo_inicio DESC",
            (pension_id,)
        )

        return cur.fetchall()

    finally:
        con.close()


def listar_metodos_pago():

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT metodo_pago_id, nombre "
            "FROM metodos_pago ORDER BY nombre"
        )

        return cur.fetchall()

    finally:
        con.close()
