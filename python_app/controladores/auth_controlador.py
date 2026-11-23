import bcrypt
from db.conexion import obtener_conexion


def _clave_correcta(ingresada, guardada):
    if not guardada:
        return False
    # Si la contraseña está guardada con hash de bcrypt
    if guardada.startswith("$2"):
        try:
            hash_bcrypt = guardada.replace("$2y$", "$2b$", 1)
            return bcrypt.checkpw(ingresada.encode(), hash_bcrypt.encode())
        except ValueError:
            return False
    # Si está en texto plano (como está hoy en la BD)
    return ingresada == guardada


def _cifrar_clave(usuario_id, password):
    """Reemplaza una contraseña en texto plano por su hash bcrypt ($2y$, compatible con PHP)."""
    if len(password.encode()) > 72:
        return
    hash_nuevo = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    hash_nuevo = hash_nuevo.replace("$2b$", "$2y$", 1)
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("UPDATE usuarios SET password_hash = %s WHERE usuario_id = %s",
                    (hash_nuevo, usuario_id))
        con.commit()
    finally:
        con.close()


def iniciar_sesion(username, password):
    """Devuelve un dict con los datos del usuario, o None si falla."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT u.*, p.nombre AS perfil "
            "FROM usuarios u JOIN perfiles p ON p.perfil_id = u.perfil_id "
            "WHERE u.username = %s",
            (username,),
        )
        fila = cur.fetchone()
    finally:
        con.close()

    if fila is None or fila.get("activo", 1) == 0:
        return None
    if not _clave_correcta(password, fila["password_hash"]):
        return None

    # Si la contraseña seguía en texto plano, se guarda ya cifrada (bcrypt)
    if not fila["password_hash"].startswith("$2"):
        _cifrar_clave(fila["usuario_id"], password)

    return {
        "id": fila["usuario_id"],
        "nombre": fila.get("nombre") or fila["username"],
        "username": fila["username"],
        "perfil": fila["perfil"],
    }