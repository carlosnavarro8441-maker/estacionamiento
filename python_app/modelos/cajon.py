from db.conexion import obtener_conexion


def sincronizar(total):
    """
    Deja activos los cajones del 1 al 'total': crea los que faltan,
    reactiva los que estaban apagados y desactiva los que pasan del total.
    """
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("SELECT numero FROM cajones")
        existentes = {fila[0] for fila in cur.fetchall()}
        faltantes = [(n,) for n in range(1, total + 1) if n not in existentes]
        if faltantes:
            cur.executemany("INSERT INTO cajones (numero, activo) VALUES (%s, 1)", faltantes)
        cur.execute("UPDATE cajones SET activo = 1 WHERE numero <= %s", (total,))
        cur.execute("UPDATE cajones SET activo = 0 WHERE numero > %s", (total,))
        con.commit()
    finally:
        con.close()


def numeros_ocupados_mayores_a(total):
    """Números de cajones ocupados que pasan del 'total' (impiden reducir la capacidad)."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT c.numero FROM cajones c "
            "JOIN servicios s ON s.cajon_id = c.cajon_id AND s.fecha_hora_salida IS NULL "
            "WHERE c.numero > %s ORDER BY c.numero",
            (total,),
        )
        return [fila[0] for fila in cur.fetchall()]
    finally:
        con.close()


def listar_con_estado():
    """Cajones activos con su estado. Si está ocupado, trae la matrícula del vehículo."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT c.cajon_id, c.numero, s.servicio_id, v.matricula "
            "FROM cajones c "
            "LEFT JOIN servicios s ON s.cajon_id = c.cajon_id AND s.fecha_hora_salida IS NULL "
            "LEFT JOIN vehiculos v ON v.vehiculo_id = s.vehiculo_id "
            "WHERE c.activo = 1 ORDER BY c.numero"
        )
        filas = cur.fetchall()
    finally:
        con.close()
    for fila in filas:
        fila["ocupado"] = fila["servicio_id"] is not None
    return filas


def listar_libres():
    """Cajones activos que no tienen ningún vehículo dentro."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT c.cajon_id, c.numero FROM cajones c "
            "LEFT JOIN servicios s ON s.cajon_id = c.cajon_id AND s.fecha_hora_salida IS NULL "
            "WHERE c.activo = 1 AND s.servicio_id IS NULL ORDER BY c.numero"
        )
        return cur.fetchall()
    finally:
        con.close()


def obtener(cajon_id):
    """Devuelve el cajón (dict) o None si no existe."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM cajones WHERE cajon_id = %s", (cajon_id,))
        return cur.fetchone()
    finally:
        con.close()


def esta_ocupado(cajon_id):
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM servicios WHERE cajon_id = %s AND fecha_hora_salida IS NULL",
            (cajon_id,),
        )
        return cur.fetchone()[0] > 0
    finally:
        con.close()


def contar_sin_cajon():
    """Vehículos dentro que no tienen un cajón asignado."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM servicios WHERE fecha_hora_salida IS NULL AND cajon_id IS NULL"
        )
        return cur.fetchone()[0]
    finally:
        con.close()
        
def listar_vehiculos_dentro():
    """Servicios sin salida, con la matrícula y el número de cajón (si tiene)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT s.servicio_id, v.matricula, c.numero AS cajon_numero "
            "FROM servicios s "
            "JOIN vehiculos v ON v.vehiculo_id = s.vehiculo_id "
            "LEFT JOIN cajones c ON c.cajon_id = s.cajon_id "
            "WHERE s.fecha_hora_salida IS NULL "
            "ORDER BY s.fecha_hora_entrada"
        )
        return cur.fetchall()
    finally:
        con.close()


def asignar(servicio_id, cajon_id):
    """Pone (o quita, con None) el cajón de un servicio que sigue abierto."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE servicios SET cajon_id = %s "
            "WHERE servicio_id = %s AND fecha_hora_salida IS NULL",
            (cajon_id, servicio_id),
        )
        con.commit()
    finally:
        con.close()