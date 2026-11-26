import mysql.connector

import sesion
from modelos import cajon, capacidad


def obtener_estado():
    """Resumen del estacionamiento: capacidad, ocupados, disponibles y si está lleno."""
    total = capacidad.obtener_capacidad()
    ocupados = capacidad.contar_ocupados()
    if total is None:
        # Sin límite configurado: no se bloquea nada
        return {"configurado": False, "capacidad": None, "ocupados": ocupados,
                "disponibles": None, "lleno": False}
    return {
        "configurado": True,
        "capacidad": total,
        "ocupados": ocupados,
        "disponibles": max(0, total - ocupados),
        "lleno": ocupados >= total,
    }


def espacios_disponibles():
    """Número de espacios libres, o None si no hay límite configurado."""
    return obtener_estado()["disponibles"]


def hay_espacio():
    """Devuelve (True, mensaje) si se puede registrar otra entrada, o (False, mensaje)."""
    estado = obtener_estado()
    if estado["lleno"]:
        return False, (f"Estacionamiento lleno: {estado['ocupados']} de "
                       f"{estado['capacidad']} espacios ocupados")
    return True, "Hay espacio"


def cambiar_capacidad(texto):
    """Solo el admin. Devuelve (True/False, mensaje)."""
    if not sesion.es_admin():
        return False, "Solo el administrador puede cambiar la capacidad"
    texto = texto.strip()
    if not texto.isdigit() or int(texto) < 1:
        return False, "La capacidad debe ser un número entero mayor a 0"
    total = int(texto)
    if total > 9999:
        return False, "La capacidad no puede pasar de 9999"
    ocupados = capacidad.contar_ocupados()
    if total < ocupados:
        return False, (f"Hay {ocupados} vehículos dentro; la capacidad no puede ser "
                       f"menor a esa cantidad")
    try:
        bloqueados = cajon.numeros_ocupados_mayores_a(total)
    except mysql.connector.ProgrammingError:
        bloqueados = []  # la tabla cajones todavía no existe en esta base
    if bloqueados:
        lista = ", ".join(str(n) for n in bloqueados)
        return False, f"No se puede reducir a {total}: están ocupados los cajones {lista}"
    capacidad.guardar_capacidad(total)
    return True, f"Capacidad actualizada a {total} espacios"