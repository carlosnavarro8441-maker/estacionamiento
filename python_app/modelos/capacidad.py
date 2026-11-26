import mysql.connector

from db.conexion import obtener_conexion

CLAVE_CAPACIDAD = "capacidad_total"


def obtener_capacidad():
    """
    Devuelve la capacidad total (int).
    Devuelve None si no está configurada o si la tabla todavía no existe.
    """
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave = %s", (CLAVE_CAPACIDAD,))
        fila = cur.fetchone()
        return int(fila[0]) if fila else None
    except mysql.connector.ProgrammingError:
        return None  # la tabla configuracion no existe en esta base
    finally:
        con.close()


def guardar_capacidad(total):
    """Crea o actualiza la capacidad total."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO configuracion (clave, valor) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE valor = VALUES(valor)",
            (CLAVE_CAPACIDAD, str(total)),
        )
        con.commit()
    finally:
        con.close()


def contar_ocupados():
    """Vehículos que están dentro: tienen entrada y todavía no tienen salida."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM servicios WHERE fecha_hora_salida IS NULL")
        return cur.fetchone()[0]
    finally:
        con.close()