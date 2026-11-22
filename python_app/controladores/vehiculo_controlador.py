import re

import mysql.connector

from modelos import vehiculo


def _limpiar(matricula, marca, modelo, color):
    # La matrícula se guarda en mayúsculas y sin espacios ni guiones
    matricula = re.sub(r"[\s-]", "", matricula).upper()
    return matricula, marca.strip(), modelo.strip(), color.strip()


def validar(matricula, marca, modelo, color):
    """Devuelve una lista con los errores encontrados (vacía si todo está bien)."""
    errores = []
    if not matricula:
        errores.append("La matrícula es obligatoria")
    elif len(matricula) > 7:
        errores.append("La matrícula no puede pasar de 7 caracteres")
    elif not re.fullmatch(r"[A-Z0-9]+", matricula):
        errores.append("La matrícula solo puede tener letras y números")
    if len(marca) > 30:
        errores.append("La marca no puede pasar de 30 caracteres")
    if len(modelo) > 30:
        errores.append("El modelo no puede pasar de 30 caracteres")
    if len(color) > 20:
        errores.append("El color no puede pasar de 20 caracteres")
    return errores


def guardar_vehiculo(matricula, marca, modelo, color, cliente_id):
    """Devuelve (True, mensaje) si se guardó, o (False, mensaje con los errores)."""
    matricula, marca, modelo, color = _limpiar(matricula, marca, modelo, color)
    errores = validar(matricula, marca, modelo, color)
    if errores:
        return False, "\n".join(errores)
    try:
        vehiculo.guardar(matricula, marca, modelo, color, cliente_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "Ya existe un vehículo con esa matrícula"
        raise
    return True, "Vehículo guardado"


def editar_vehiculo(vehiculo_id, matricula, marca, modelo, color, cliente_id):
    matricula, marca, modelo, color = _limpiar(matricula, marca, modelo, color)
    errores = validar(matricula, marca, modelo, color)
    if errores:
        return False, "\n".join(errores)
    try:
        vehiculo.editar(vehiculo_id, matricula, marca, modelo, color, cliente_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "Ya existe un vehículo con esa matrícula"
        raise
    return True, "Vehículo actualizado"


def listar_vehiculos(texto=""):
    return vehiculo.listar(texto.strip())


# ---- Funciones que usan los demás integrantes ----
def buscar_vehiculo_por_matricula(matricula):
    """Devuelve un dict con el vehículo, o None si no existe."""
    matricula = re.sub(r"[\s-]", "", matricula).upper()
    return vehiculo.buscar_por_matricula(matricula)


def obtener_tipo_cliente(vehiculo_id):
    """
    Devuelve {'tipo_cliente_id': ..., 'nombre': ...} del dueño del vehículo.
    Devuelve None si el vehículo no tiene cliente (cliente de paso).
    """
    return vehiculo.obtener_tipo_cliente(vehiculo_id)