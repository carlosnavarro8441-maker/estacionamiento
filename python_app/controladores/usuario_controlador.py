import re

import bcrypt
import mysql.connector

import sesion
from modelos import usuario

MIN_PASSWORD = 6


# ---------- Ayudas internas ----------
def _es_perfil_admin(perfil_id):
    for p in usuario.listar_perfiles():
        if p["perfil_id"] == perfil_id:
            return p["nombre"].lower().startswith("admin")
    return False


def _buscar(usuario_id):
    return next((u for u in usuario.listar() if u["usuario_id"] == usuario_id), None)


def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _errores_password(password, confirmar):
    errores = []
    if len(password) < MIN_PASSWORD:
        errores.append(f"La contraseña debe tener al menos {MIN_PASSWORD} caracteres")
    elif len(password.encode()) > 72:
        errores.append("La contraseña es demasiado larga (máximo 72 caracteres)")
    if password != confirmar:
        errores.append("Las contraseñas no coinciden")
    return errores


def _errores_datos(nombre, email, perfil_id):
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio")
    elif len(nombre) > 50:
        errores.append("El nombre no puede pasar de 50 caracteres")
    if not email:
        errores.append("El correo es obligatorio")
    elif len(email) > 50 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errores.append("El correo no es válido")
    if not perfil_id:
        errores.append("Elige el perfil")
    return errores


def _errores_username(username):
    if not username:
        return ["El nombre de usuario es obligatorio"]
    if not re.fullmatch(r"[A-Za-z0-9_.]{3,30}", username):
        return ["El usuario debe tener de 3 a 30 caracteres (letras, números, _ o .)"]
    return []


# ---------- Funciones que usa la pantalla ----------
def listar_usuarios(texto=""):
    return usuario.listar(texto.strip())


def listar_perfiles():
    return usuario.listar_perfiles()


def guardar_usuario(nombre, email, username, password, confirmar, perfil_id):
    """Devuelve (True, mensaje) si se guardó, o (False, mensaje con los errores)."""
    nombre, email, username = nombre.strip(), email.strip(), username.strip()
    errores = (_errores_datos(nombre, email, perfil_id)
               + _errores_username(username)
               + _errores_password(password, confirmar))
    if errores:
        return False, "\n".join(errores)
    try:
        usuario.guardar(nombre, email, username, _hash(password), perfil_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            if "username" in str(error.msg).lower():
                return False, "Ya existe un usuario con ese nombre de usuario"
            return False, "Ya existe un usuario con ese correo"
        raise
    return True, "Usuario creado"


def editar_usuario(usuario_id, nombre, email, perfil_id):
    nombre, email = nombre.strip(), email.strip()
    existente = _buscar(usuario_id)
    if existente is None:
        return False, "El usuario no existe"
    errores = _errores_datos(nombre, email, perfil_id)
    if errores:
        return False, "\n".join(errores)

    if perfil_id != existente["perfil_id"]:
        if usuario_id == sesion.usuario_actual["id"]:
            return False, "No puedes cambiar tu propio perfil"
        if (existente["activo"] and _es_perfil_admin(existente["perfil_id"])
                and not _es_perfil_admin(perfil_id)
                and usuario.contar_admins_activos() <= 1):
            return False, "Debe quedar al menos un administrador activo"

    try:
        usuario.editar(usuario_id, nombre, email, perfil_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "Ya existe un usuario con ese correo"
        raise
    return True, "Usuario actualizado"


def cambiar_password_usuario(usuario_id, password, confirmar):
    errores = _errores_password(password, confirmar)
    if errores:
        return False, "\n".join(errores)
    usuario.cambiar_password(usuario_id, _hash(password))
    return True, "Contraseña actualizada"


def cambiar_estado_usuario(usuario_id, activar):
    """Activa o desactiva un usuario. Nunca se borra."""
    existente = _buscar(usuario_id)
    if existente is None:
        return False, "El usuario no existe"
    if activar:
        usuario.cambiar_activo(usuario_id, 1)
        return True, "Usuario activado"

    if usuario_id == sesion.usuario_actual["id"]:
        return False, "No puedes desactivarte a ti mismo"
    if (existente["activo"] and _es_perfil_admin(existente["perfil_id"])
            and usuario.contar_admins_activos() <= 1):
        return False, "Debe quedar al menos un administrador activo"
    usuario.cambiar_activo(usuario_id, 0)
    return True, "Usuario desactivado"