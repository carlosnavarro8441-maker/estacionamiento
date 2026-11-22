from db.conexion import obtener_conexion


def listar_perfiles():
    """Devuelve los perfiles (admin, cobrador)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT perfil_id, nombre FROM perfiles ORDER BY perfil_id")
        return cur.fetchall()
    finally:
        con.close()


def listar(texto=""):
    """Lista todos los usuarios (activos e inactivos). Busca por nombre, usuario o correo."""
    sql = (
        "SELECT u.usuario_id, u.nombre, u.email, u.username, u.perfil_id, "
        "p.nombre AS perfil, u.activo "
        "FROM usuarios u "
        "JOIN perfiles p ON p.perfil_id = u.perfil_id "
        "WHERE 1 = 1"
    )
    parametros = []
    if texto:
        sql += " AND (u.nombre LIKE %s OR u.username LIKE %s OR u.email LIKE %s)"
        patron = f"%{texto}%"
        parametros += [patron, patron, patron]
    sql += " ORDER BY u.nombre"

    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, parametros)
        return cur.fetchall()
    finally:
        con.close()


def guardar(nombre, email, username, password_hash, perfil_id):
    """Crea un usuario activo y devuelve su id."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, email, username, password_hash, perfil_id, activo) "
            "VALUES (%s, %s, %s, %s, %s, 1)",
            (nombre, email, username, password_hash, perfil_id),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def editar(usuario_id, nombre, email, perfil_id):
    """Cambia nombre, correo y perfil (el nombre de usuario no se cambia)."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE usuarios SET nombre = %s, email = %s, perfil_id = %s WHERE usuario_id = %s",
            (nombre, email, perfil_id, usuario_id),
        )
        con.commit()
    finally:
        con.close()


def cambiar_password(usuario_id, password_hash):
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE usuarios SET password_hash = %s WHERE usuario_id = %s",
            (password_hash, usuario_id),
        )
        con.commit()
    finally:
        con.close()


def cambiar_activo(usuario_id, activo):
    """Activa (1) o desactiva (0) un usuario. No se borra, para conservar su historial."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("UPDATE usuarios SET activo = %s WHERE usuario_id = %s", (activo, usuario_id))
        con.commit()
    finally:
        con.close()


def contar_admins_activos():
    """Cuántos admins activos hay (para no dejar el sistema sin ninguno)."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM usuarios u "
            "JOIN perfiles p ON p.perfil_id = u.perfil_id "
            "WHERE LOWER(p.nombre) LIKE 'admin%' AND u.activo = 1"
        )
        return cur.fetchone()[0]
    finally:
        con.close()