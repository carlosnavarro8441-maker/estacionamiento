from db.conexion import obtener_conexion


def listar(texto=""):
    """Lista vehículos con el nombre de su cliente. Busca por matrícula, marca, modelo o cliente."""
    sql = (
        "SELECT v.vehiculo_id, v.matricula, v.marca, v.modelo, v.color, "
        "v.cliente_id, c.nombre AS cliente "
        "FROM vehiculos v "
        "LEFT JOIN clientes c ON c.cliente_id = v.cliente_id "
        "WHERE 1 = 1"
    )
    parametros = []
    if texto:
        sql += (" AND (v.matricula LIKE %s OR v.marca LIKE %s "
                "OR v.modelo LIKE %s OR c.nombre LIKE %s)")
        patron = f"%{texto}%"
        parametros += [patron, patron, patron, patron]
    sql += " ORDER BY v.matricula"

    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, parametros)
        return cur.fetchall()
    finally:
        con.close()


def buscar_por_matricula(matricula):
    """Devuelve el vehículo con esa matrícula (dict) o None si no existe."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM vehiculos WHERE matricula = %s", (matricula,))
        return cur.fetchone()
    finally:
        con.close()


def obtener_tipo_cliente(vehiculo_id):
    """
    Devuelve {'tipo_cliente_id': ..., 'nombre': ...} del dueño del vehículo.
    Si el vehículo no tiene cliente registrado (cliente de paso), devuelve None.
    """
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT t.tipo_cliente_id, t.nombre "
            "FROM vehiculos v "
            "JOIN clientes c ON c.cliente_id = v.cliente_id "
            "JOIN tipos_cliente t ON t.tipo_cliente_id = c.tipo_cliente_id "
            "WHERE v.vehiculo_id = %s",
            (vehiculo_id,),
        )
        return cur.fetchone()
    finally:
        con.close()


def guardar(matricula, marca, modelo, color, cliente_id):
    """Crea un vehículo y devuelve su id. cliente_id puede ser None."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO vehiculos (matricula, marca, modelo, color, cliente_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (matricula, marca, modelo, color, cliente_id),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def editar(vehiculo_id, matricula, marca, modelo, color, cliente_id):
    """Actualiza los datos de un vehículo."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE vehiculos SET matricula = %s, marca = %s, modelo = %s, "
            "color = %s, cliente_id = %s WHERE vehiculo_id = %s",
            (matricula, marca, modelo, color, cliente_id, vehiculo_id),
        )
        con.commit()
    finally:
        con.close()