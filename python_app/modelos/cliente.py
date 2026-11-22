from db.conexion import obtener_conexion


def listar_tipos():
    """Devuelve los tipos de cliente (paso, frecuente)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT tipo_cliente_id, nombre FROM tipos_cliente ORDER BY tipo_cliente_id")
        return cur.fetchall()
    finally:
        con.close()


def listar(texto="", solo_activos=True):
    """Lista clientes. Si hay texto, busca por nombre, teléfono o RFC."""
    sql = (
        "SELECT c.cliente_id, c.nombre, c.telefono, c.email, c.rfc, "
        "c.tipo_cliente_id, t.nombre AS tipo, c.activo "
        "FROM clientes c "
        "JOIN tipos_cliente t ON t.tipo_cliente_id = c.tipo_cliente_id "
        "WHERE 1 = 1"
    )
    parametros = []
    if solo_activos:
        sql += " AND c.activo = 1"
    if texto:
        sql += " AND (c.nombre LIKE %s OR c.telefono LIKE %s OR c.rfc LIKE %s)"
        patron = f"%{texto}%"
        parametros += [patron, patron, patron]
    sql += " ORDER BY c.nombre"

    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, parametros)
        return cur.fetchall()
    finally:
        con.close()


def obtener(cliente_id):
    """Devuelve un cliente por su id, o None si no existe."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM clientes WHERE cliente_id = %s", (cliente_id,))
        return cur.fetchone()
    finally:
        con.close()


def guardar(nombre, telefono, email, rfc, tipo_cliente_id, registrado_por):
    """Crea un cliente nuevo y devuelve su id."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO clientes "
            "(nombre, telefono, email, rfc, tipo_cliente_id, registrado_por, fecha_registro, activo) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW(), 1)",
            (nombre, telefono, email, rfc or None, tipo_cliente_id, registrado_por),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def editar(cliente_id, nombre, telefono, email, rfc, tipo_cliente_id):
    """Actualiza los datos de un cliente."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE clientes SET nombre = %s, telefono = %s, email = %s, "
            "rfc = %s, tipo_cliente_id = %s WHERE cliente_id = %s",
            (nombre, telefono, email, rfc or None, tipo_cliente_id, cliente_id),
        )
        con.commit()
    finally:
        con.close()


def dar_de_baja(cliente_id):
    """Baja lógica: se desactiva, no se borra, para conservar su historial."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("UPDATE clientes SET activo = 0 WHERE cliente_id = %s", (cliente_id,))
        con.commit()
    finally:
        con.close()