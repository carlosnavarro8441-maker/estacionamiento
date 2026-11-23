from datetime import datetime

from db.conexion import obtener_conexion

TIPO_CAJON = 1
TIPO_PENSION = 2


def buscar_abierto_por_vehiculo(vehiculo_id):
    """Servicio sin salida del vehículo (None si no está dentro)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT servicio_id FROM servicios "
            "WHERE vehiculo_id = %s AND fecha_hora_salida IS NULL",
            (vehiculo_id,),
        )
        return cur.fetchone()
    finally:
        con.close()


def pension_vigente(vehiculo_id):
    """Pensión activa y no vencida del vehículo (None si no tiene)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT pension_id FROM pensiones "
            "WHERE vehiculo_id = %s AND estado_pension_id = 1 "
            "AND fecha_inicio <= CURDATE() "
            "AND (fecha_fin IS NULL OR fecha_fin >= CURDATE()) "
            "LIMIT 1",
            (vehiculo_id,),
        )
        return cur.fetchone()
    finally:
        con.close()


def registrar_entrada(vehiculo_id, tipo_servicio_id, pension_id, usuario_id):
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO servicios (vehiculo_id, tipo_servicio_id, pension_id, "
            "fecha_hora_entrada, usuario_entrada_id) VALUES (%s, %s, %s, %s, %s)",
            (vehiculo_id, tipo_servicio_id, pension_id, datetime.now(), usuario_id),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def listar_dentro():
    """Vehículos que están dentro del estacionamiento ahora."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT s.servicio_id, v.matricula, s.fecha_hora_entrada, "
            "s.tipo_servicio_id, COALESCE(tc.nombre, 'paso') AS tipo_cliente "
            "FROM servicios s "
            "JOIN vehiculos v ON v.vehiculo_id = s.vehiculo_id "
            "LEFT JOIN clientes c ON c.cliente_id = v.cliente_id "
            "LEFT JOIN tipos_cliente tc ON tc.tipo_cliente_id = c.tipo_cliente_id "
            "WHERE s.fecha_hora_salida IS NULL "
            "ORDER BY s.fecha_hora_entrada DESC"
        )
        return cur.fetchall()
    finally:
        con.close()


def obtener_abierto(servicio_id):
    """Datos de un servicio que todavía no tiene salida (None si no existe o ya salió)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT s.servicio_id, s.vehiculo_id, s.tipo_servicio_id, s.pension_id, "
            "s.fecha_hora_entrada, v.matricula, "
            "COALESCE(tc.nombre, 'paso') AS tipo_cliente "
            "FROM servicios s "
            "JOIN vehiculos v ON v.vehiculo_id = s.vehiculo_id "
            "LEFT JOIN clientes c ON c.cliente_id = v.cliente_id "
            "LEFT JOIN tipos_cliente tc ON tc.tipo_cliente_id = c.tipo_cliente_id "
            "WHERE s.servicio_id = %s AND s.fecha_hora_salida IS NULL",
            (servicio_id,),
        )
        return cur.fetchone()
    finally:
        con.close()


def cerrar_sin_cobro(servicio_id, salida, usuario_id):
    """Registra la salida de un vehículo con pensión (no genera cobro por hora)."""
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
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
