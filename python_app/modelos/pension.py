
from datetime import date
from db.conexion import obtener_conexion


ESTADO_ACTIVA = 1
ESTADO_VENCIDA = 2


def listar(texto="", solo_activas=False):
    sql = (
        "SELECT p.pension_id, p.cliente_id, c.nombre AS cliente, "
        "p.vehiculo_id, v.matricula, p.tarifa_id, "
        "t.precio AS tarifa_mensual, p.fecha_inicio, p.fecha_fin, "
        "p.estado_pension_id, ep.nombre AS estado "
        "FROM pensiones p "
        "JOIN clientes c ON c.cliente_id = p.cliente_id "
        "JOIN vehiculos v ON v.vehiculo_id = p.vehiculo_id "
        "JOIN tarifas t ON t.tarifa_id = p.tarifa_id "
        "JOIN estados_pension ep ON "
        "ep.estado_pension_id = p.estado_pension_id "
        "WHERE 1=1"
    )

    params = []

    if solo_activas:
        sql += " AND p.estado_pension_id = %s"
        params.append(ESTADO_ACTIVA)

    if texto:
        patron = f"%{texto}%"
        sql += " AND (c.nombre LIKE %s OR v.matricula LIKE %s)"
        params.extend([patron, patron])

    sql += " ORDER BY p.fecha_inicio DESC, p.pension_id DESC"

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        con.close()


def obtener(pension_id):
    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT p.*, c.nombre AS cliente, "
            "v.matricula, t.precio AS tarifa_mensual, "
            "ep.nombre AS estado "
            "FROM pensiones p "
            "JOIN clientes c ON c.cliente_id=p.cliente_id "
            "JOIN vehiculos v ON v.vehiculo_id=p.vehiculo_id "
            "JOIN tarifas t ON t.tarifa_id=p.tarifa_id "
            "JOIN estados_pension ep ON "
            "ep.estado_pension_id=p.estado_pension_id "
            "WHERE p.pension_id=%s",
            (pension_id,)
        )

        return cur.fetchone()

    finally:
        con.close()


def listar_vehiculos_cliente(texto=""):
    sql = (
        "SELECT v.vehiculo_id, v.matricula, v.marca, "
        "v.modelo, c.cliente_id, c.nombre AS cliente "
        "FROM vehiculos v "
        "JOIN clientes c ON c.cliente_id=v.cliente_id "
        "WHERE c.activo=1"
    )

    params = []

    if texto:
        patron = f"%{texto}%"
        sql += " AND (v.matricula LIKE %s OR c.nombre LIKE %s)"
        params.extend([patron, patron])

    sql += " ORDER BY c.nombre, v.matricula"

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        con.close()


def listar_tarifas_mensuales():
    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        cur.execute(
            "SELECT tarifa_id, precio, unidad FROM tarifas "
            "WHERE tipo_servicio_id=2 "
            "AND activa=1 AND unidad='mes' AND precio>0 "
            "ORDER BY precio"
        )

        return cur.fetchall()

    finally:
        con.close()


def calcular_antiguedad(fecha_inicio, fecha_referencia=None):

    if isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)

    fecha_referencia = fecha_referencia or date.today()

    anios = fecha_referencia.year - fecha_inicio.year

    if (
        fecha_referencia.month,
        fecha_referencia.day
    ) < (
        fecha_inicio.month,
        fecha_inicio.day
    ):
        anios -= 1

    return max(anios, 0)


def sumar_anios(fecha, anios):
    """Misma fecha dentro de `anios` años (el 29 de febrero pasa al 28 si hace falta)."""
    try:
        return fecha.replace(year=fecha.year + anios)
    except ValueError:
        return fecha.replace(year=fecha.year + anios, day=28)


def tiene_mas_de(fecha_inicio, anios, fecha_referencia=None):
    """True si la pensión lleva MÁS de `anios` años (estrictamente más).

    Con 2 años exactos todavía no; al día siguiente del aniversario sí.
    """
    if isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)
    fecha_referencia = fecha_referencia or date.today()
    return fecha_referencia > sumar_anios(fecha_inicio, anios)


def elegir_descuento(descuentos, fecha_inicio, fecha_referencia=None):
    """Del listado de descuentos activos, devuelve el mayor que le corresponde.

    Regla del proyecto: descuento para clientes con MÁS de 2 años de pensión
    (los años mínimos y el porcentaje salen de la tabla descuentos_pension).
    """
    aplicables = [
        d for d in descuentos
        if tiene_mas_de(fecha_inicio, d["anios_minimos"], fecha_referencia)
    ]
    if not aplicables:
        return None
    return max(aplicables, key=lambda d: d["anios_minimos"])


def listar_descuentos_activos(cur=None):
    """Descuentos activos. Si se pasa un cursor se usa ese (por ejemplo, dentro de una transacción)."""
    if cur is not None:
        cur.execute(
            "SELECT descuento_id, anios_minimos, porcentaje "
            "FROM descuentos_pension WHERE activo=1"
        )
        return cur.fetchall()

    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT descuento_id, anios_minimos, porcentaje "
            "FROM descuentos_pension WHERE activo=1"
        )
        return cur.fetchall()
    finally:
        con.close()


def obtener_descuento(fecha_inicio, fecha_referencia=None):
    return elegir_descuento(
        listar_descuentos_activos(),
        fecha_inicio,
        fecha_referencia
    )


def guardar(
    cliente_id,
    vehiculo_id,
    tarifa_id,
    fecha_inicio,
    usuario_id,
    fecha_fin=None
):

    if isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)

    con = obtener_conexion()

    try:
        cur = con.cursor(dictionary=True)

        # Verificar pensiones activas
        cur.execute(
            "SELECT pension_id FROM pensiones "
            "WHERE vehiculo_id=%s AND estado_pension_id=%s",
            (vehiculo_id, ESTADO_ACTIVA)
        )

        if cur.fetchone():
            raise ValueError(
                "El vehículo ya tiene una pensión activa."
            )

        # Verificar tarifa mensual
        cur.execute(
            "SELECT tarifa_id FROM tarifas "
            "WHERE tarifa_id=%s AND tipo_servicio_id=2 "
            "AND unidad='mes' AND activa=1 AND precio>0",
            (tarifa_id,)
        )

        if not cur.fetchone():
            raise ValueError(
                "Selecciona una tarifa mensual activa."
            )

        # Verificar que el vehículo pertenezca al cliente
        cur.execute(
            "SELECT vehiculo_id FROM vehiculos "
            "WHERE vehiculo_id=%s AND cliente_id=%s",
            (vehiculo_id, cliente_id)
        )

        if not cur.fetchone():
            raise ValueError(
                "El vehículo no pertenece al cliente seleccionado."
            )

        # Registrar pensión
        cur.execute(
            "INSERT INTO pensiones "
            "(cliente_id, vehiculo_id, tarifa_id, "
            "fecha_inicio, fecha_fin, estado_pension_id, usuario_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                cliente_id,
                vehiculo_id,
                tarifa_id,
                fecha_inicio,
                fecha_fin,
                ESTADO_ACTIVA,
                usuario_id
            )
        )

        con.commit()

        return cur.lastrowid

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def cancelar(pension_id, fecha_fin=None):

    fecha_fin = fecha_fin or date.today()

    con = obtener_conexion()

    try:
        cur = con.cursor()

        cur.execute(
            "UPDATE pensiones "
            "SET estado_pension_id=%s, fecha_fin=%s "
            "WHERE pension_id=%s AND estado_pension_id=%s",
            (
                ESTADO_VENCIDA,
                fecha_fin,
                pension_id,
                ESTADO_ACTIVA
            )
        )

        if cur.rowcount == 0:
            raise ValueError(
                "No se encontró una pensión activa para cancelar."
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def actualizar_vencidas():

    con = obtener_conexion()

    try:
        cur = con.cursor()

        cur.execute(
            "UPDATE pensiones "
            "SET estado_pension_id=%s "
            "WHERE estado_pension_id=%s "
            "AND fecha_fin IS NOT NULL "
            "AND fecha_fin < CURDATE()",
            (ESTADO_VENCIDA, ESTADO_ACTIVA)
        )

        con.commit()

        return cur.rowcount

    finally:
        con.close()
