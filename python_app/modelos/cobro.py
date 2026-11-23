from db.conexion import obtener_conexion


def registrar_salida_con_cobro(servicio_id, salida, usuario_id, horas, total,
                               metodo_pago_id, desglose):
    """Cierra el servicio y guarda el cobro con su detalle en una sola transacción.

    Si algo falla no se guarda nada: nunca queda una salida sin cobro.
    """
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE servicios SET fecha_hora_salida = %s, usuario_salida_id = %s "
            "WHERE servicio_id = %s AND fecha_hora_salida IS NULL",
            (salida, usuario_id, servicio_id),
        )
        if cur.rowcount != 1:
            raise ValueError("Este servicio ya tiene salida registrada")

        cur.execute(
            "INSERT INTO cobros (servicio_id, horas_cobradas, monto_total, "
            "fecha_hora_cobro, metodo_pago_id, usuario_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (servicio_id, horas, total, salida, metodo_pago_id, usuario_id),
        )
        cobro_id = cur.lastrowid

        for linea in desglose:
            cur.execute(
                "INSERT INTO cobros_detalle (cobro_id, tarifa_id, horas, "
                "precio_hora_aplicado, subtotal) VALUES (%s, %s, %s, %s, %s)",
                (cobro_id, linea["tarifa_id"], linea["horas"],
                 linea["precio"], linea["subtotal"]),
            )
        con.commit()
        return cobro_id
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
