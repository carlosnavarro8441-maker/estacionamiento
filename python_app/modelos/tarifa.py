from db.conexion import obtener_conexion


def listar_cajon(tipo_cliente):
    """Tramos de la tarifa por hora del cajón para 'paso' o 'frecuente'."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT t.tarifa_id, t.hora_desde, t.hora_hasta, t.precio "
            "FROM tarifas t "
            "JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id "
            "WHERE t.tipo_servicio_id = 1 AND t.unidad = 'hora' AND t.activa = 1 "
            "AND tc.nombre = %s "
            "ORDER BY t.hora_desde",
            (tipo_cliente,),
        )
        return cur.fetchall()
    finally:
        con.close()


def listar_todas():
    """Todas las tarifas con el nombre del servicio y del tipo de cliente."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT t.tarifa_id, ts.nombre AS servicio, "
            "COALESCE(tc.nombre, 'general') AS cliente, "
            "t.hora_desde, t.hora_hasta, t.precio, t.unidad, t.activa "
            "FROM tarifas t "
            "JOIN tipos_servicio ts ON ts.tipo_servicio_id = t.tipo_servicio_id "
            "LEFT JOIN tipos_cliente tc ON tc.tipo_cliente_id = t.tipo_cliente_id "
            "ORDER BY t.tipo_servicio_id, t.tipo_cliente_id, t.hora_desde"
        )
        return cur.fetchall()
    finally:
        con.close()


def actualizar_precio(tarifa_id, precio):
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("UPDATE tarifas SET precio = %s WHERE tarifa_id = %s", (precio, tarifa_id))
        con.commit()
        return cur.rowcount
    finally:
        con.close()


def listar_descuentos():
    """Descuentos de pensión por antigüedad."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT descuento_id, anios_minimos, porcentaje, activo "
            "FROM descuentos_pension ORDER BY anios_minimos"
        )
        return cur.fetchall()
    finally:
        con.close()


def actualizar_descuento(descuento_id, porcentaje):
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE descuentos_pension SET porcentaje = %s WHERE descuento_id = %s",
            (porcentaje, descuento_id),
        )
        con.commit()
        return cur.rowcount
    finally:
        con.close()
