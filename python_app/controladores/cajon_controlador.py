from modelos import cajon, capacidad


def sincronizar_con_capacidad():
    """Crea los cajones 1..N según la capacidad. Devuelve False si no hay capacidad."""
    total = capacidad.obtener_capacidad()
    if total is None:
        return False
    cajon.sincronizar(total)
    return True


def obtener_mapa():
    """Datos para el mapa de cajones, o None si no hay capacidad configurada."""
    if not sincronizar_con_capacidad():
        return None
    cajones = cajon.listar_con_estado()
    ocupados = sum(1 for c in cajones if c["ocupado"])
    return {
        "cajones": cajones,
        "libres": len(cajones) - ocupados,
        "ocupados": ocupados,
        "sin_cajon": cajon.contar_sin_cajon(),
    }


# ---- Funciones que usa el integrante 3 en la pantalla de entradas ----
def listar_cajones_libres():
    """Cajones libres para llenar una lista desplegable: [{'cajon_id', 'numero'}, ...]."""
    sincronizar_con_capacidad()
    return cajon.listar_libres()


def validar_cajon(cajon_id):
    """
    Devuelve (True, mensaje) si el cajón se puede asignar, o (False, mensaje).
    cajon_id = None significa que no se eligió cajón, y eso se permite.
    """
    if cajon_id is None:
        return True, "Sin cajón asignado"
    c = cajon.obtener(cajon_id)
    if c is None or not c["activo"]:
        return False, "El cajón no existe o está desactivado"
    if cajon.esta_ocupado(cajon_id):
        return False, f"El cajón {c['numero']} ya está ocupado"
    return True, f"Cajón {c['numero']} disponible"

def listar_vehiculos_dentro():
    return cajon.listar_vehiculos_dentro()


def asignar_cajon(servicio_id, cajon_id):
    """
    Asigna un cajón libre a un vehículo que está dentro,
    o le quita el cajón si cajon_id es None. Devuelve (True/False, mensaje).
    """
    dentro = {v["servicio_id"]: v for v in cajon.listar_vehiculos_dentro()}
    vehiculo = dentro.get(servicio_id)
    if vehiculo is None:
        return False, "Ese vehículo ya salió del estacionamiento"
    if cajon_id is None:
        if vehiculo["cajon_numero"] is None:
            return False, "Ese vehículo no tiene cajón asignado"
        cajon.asignar(servicio_id, None)
        return True, f"Se quitó el cajón a {vehiculo['matricula']}"
    ok, mensaje = validar_cajon(cajon_id)
    if not ok:
        return False, mensaje
    cajon.asignar(servicio_id, cajon_id)
    numero = cajon.obtener(cajon_id)["numero"]
    return True, f"{vehiculo['matricula']} quedó en el cajón {numero}"