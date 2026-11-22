import re

import mysql.connector

import sesion
from modelos import cliente


def validar(nombre, telefono, email, rfc, tipo_cliente_id):
    """Devuelve una lista con los errores encontrados (vacía si todo está bien)."""
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio")
    elif len(nombre) > 50:
        errores.append("El nombre no puede pasar de 50 caracteres")
    if telefono and not re.fullmatch(r"\d{10}", telefono):
        errores.append("El teléfono debe tener 10 dígitos")
    if email and (len(email) > 50 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        errores.append("El correo no es válido")
    if rfc and not re.fullmatch(r"[A-Z&Ñ0-9]{12,13}", rfc):
        errores.append("El RFC debe tener 12 o 13 caracteres")
    if not tipo_cliente_id:
        errores.append("Elige el tipo de cliente")
    return errores


def _limpiar(nombre, telefono, email, rfc):
    return nombre.strip(), telefono.strip(), email.strip(), rfc.strip().upper()


def guardar_cliente(nombre, telefono, email, rfc, tipo_cliente_id):
    """Devuelve (True, mensaje) si se guardó, o (False, mensaje con los errores)."""
    nombre, telefono, email, rfc = _limpiar(nombre, telefono, email, rfc)
    errores = validar(nombre, telefono, email, rfc, tipo_cliente_id)
    if errores:
        return False, "\n".join(errores)
    try:
        cliente.guardar(nombre, telefono, email, rfc, tipo_cliente_id,
                        sesion.usuario_actual["id"])
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "Ya existe un cliente con ese RFC"
        raise
    return True, "Cliente guardado"


def editar_cliente(cliente_id, nombre, telefono, email, rfc, tipo_cliente_id):
    nombre, telefono, email, rfc = _limpiar(nombre, telefono, email, rfc)
    errores = validar(nombre, telefono, email, rfc, tipo_cliente_id)
    if errores:
        return False, "\n".join(errores)
    try:
        cliente.editar(cliente_id, nombre, telefono, email, rfc, tipo_cliente_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "Ya existe un cliente con ese RFC"
        raise
    return True, "Cliente actualizado"


def dar_de_baja_cliente(cliente_id):
    cliente.dar_de_baja(cliente_id)
    return True, "Cliente dado de baja"


def listar_clientes(texto=""):
    return cliente.listar(texto.strip())


def listar_tipos():
    return cliente.listar_tipos()