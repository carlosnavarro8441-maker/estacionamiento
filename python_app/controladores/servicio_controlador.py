from datetime import datetime

import mysql.connector

import sesion
from controladores import vehiculo_controlador
from controladores.calculo_cobro import calcular_importe, horas_a_cobrar
from modelos import cobro, pago_pension, servicio, tarifa
from modelos import vehiculo as vehiculo_modelo

PLACEHOLDER = "Por definir"


def _usuario_id():
    if sesion.usuario_actual is None:
        raise PermissionError("Inicia sesión para continuar")
    return sesion.usuario_actual["id"]


def registrar_entrada(matricula):
    """Registra la entrada de un vehículo. Devuelve (True/False, mensaje)."""
    usuario_id = _usuario_id()
    matricula = vehiculo_controlador._limpiar(matricula, "", "", "")[0]
    errores = vehiculo_controlador.validar(matricula, "", "", "")
    if errores:
        return False, "\n".join(errores)

    veh = vehiculo_modelo.buscar_por_matricula(matricula)
    nuevo = veh is None
    if nuevo:
        # Vehículo que nunca ha venido: se registra y sus datos se completan después
        vehiculo_id = vehiculo_modelo.guardar(matricula, PLACEHOLDER, PLACEHOLDER,
                                              PLACEHOLDER, None)
    else:
        vehiculo_id = veh["vehiculo_id"]

    if servicio.buscar_abierto_por_vehiculo(vehiculo_id):
        return False, f"El vehículo {matricula} ya está dentro del estacionamiento"

    # Si el vehículo tiene una pensión vigente, la entrada es de tipo pensión
    pension = servicio.pension_vigente(vehiculo_id)
    tipo = servicio.TIPO_PENSION if pension else servicio.TIPO_CAJON
    pension_id = pension["pension_id"] if pension else None

    try:
        servicio.registrar_entrada(vehiculo_id, tipo, pension_id, usuario_id)
    except mysql.connector.Error as error:
        return False, str(error.msg)

    mensaje = f"Entrada registrada: {matricula}"
    if pension:
        mensaje += " (pensión, no genera cobro por hora)"
    if nuevo:
        mensaje += "\nVehículo nuevo: completa sus datos en la pantalla Vehículos"
    return True, mensaje


def listar_dentro():
    return servicio.listar_dentro()


def listar_metodos_pago():
    return pago_pension.listar_metodos_pago()


def calcular_salida(servicio_id, salida=None):
    """Calcula el cobro de un servicio abierto con la hora de salida indicada.

    Devuelve un diccionario con los datos del servicio, las horas, el total y el
    desglose. Si el servicio es de pensión, total = 0 y no hay desglose.
    """
    _usuario_id()
    salida = salida or datetime.now()
    datos = servicio.obtener_abierto(servicio_id)
    if datos is None:
        raise ValueError("Este servicio no existe o ya tiene salida registrada")

    horas = horas_a_cobrar(datos["fecha_hora_entrada"], salida)
    es_pension = datos["tipo_servicio_id"] == servicio.TIPO_PENSION
    if es_pension:
        total, desglose = 0, []
    else:
        tramos = tarifa.listar_cajon(datos["tipo_cliente"])
        total, desglose = calcular_importe(horas, tramos)

    return {**datos, "salida": salida, "horas": horas, "total": total,
            "desglose": desglose, "es_pension": es_pension}


def registrar_salida(servicio_id, metodo_pago_id, salida=None):
    """Registra la salida y el cobro. Devuelve (True/False, mensaje).

    Si se pasa `salida` se usa esa hora (la misma con la que se mostró el total
    en pantalla), para que lo cobrado coincida con lo que vio el cobrador.
    """
    usuario_id = _usuario_id()
    try:
        calculo = calcular_salida(servicio_id, salida)
        if calculo["es_pension"]:
            servicio.cerrar_sin_cobro(servicio_id, calculo["salida"], usuario_id)
            return True, f"Salida registrada: {calculo['matricula']} (pensión, sin cobro)"
        if not metodo_pago_id:
            return False, "Elige el método de pago"
        cobro.registrar_salida_con_cobro(
            servicio_id, calculo["salida"], usuario_id, calculo["horas"],
            calculo["total"], metodo_pago_id, calculo["desglose"],
        )
    except ValueError as error:
        return False, str(error)
    except mysql.connector.Error as error:
        return False, str(error.msg)
    return True, (f"Salida registrada: {calculo['matricula']}\n"
                  f"Total cobrado: ${calculo['total']:.2f} MXN")
