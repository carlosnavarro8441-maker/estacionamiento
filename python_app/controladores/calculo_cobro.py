"""Cálculo del cobro por cajón.

Todo lo de este archivo es lógica pura (no toca la base de datos), así que se
puede probar fácil. Los precios NO están escritos aquí: vienen de la tabla
`tarifas`, por eso el administrador puede cambiarlos desde la pantalla Tarifas.

Reglas del proyecto (se cargan como tarifas en la base de datos):
  - Cliente de paso:  $30.00 por hora; de la hora 6 en adelante, $25.00 por hora.
  - Cliente frecuente: $26.00 por hora; de la hora 6 en adelante, $22.00 por hora.
"""
import math
from decimal import Decimal


def horas_a_cobrar(entrada, salida):
    """Horas que se cobran: una fracción de hora cuenta como hora completa.

    Siempre se cobra mínimo 1 hora.
    """
    segundos = (salida - entrada).total_seconds()
    return max(1, math.ceil(segundos / 3600))


def calcular_importe(horas, tramos):
    """Calcula el total y el desglose por tramo de tarifa.

    `tramos` es una lista de diccionarios con las claves:
      tarifa_id, hora_desde, hora_hasta (None = "en adelante") y precio.

    Devuelve (total, desglose). Cada elemento del desglose es un diccionario con
    tarifa_id, horas, precio y subtotal (lo que se guarda en cobros_detalle).
    """
    if horas < 1:
        raise ValueError("Las horas a cobrar deben ser al menos 1")

    desglose = []
    total = Decimal("0")
    horas_cubiertas = 0

    for tramo in sorted(tramos, key=lambda t: t["hora_desde"]):
        desde = tramo["hora_desde"]
        hasta = horas if tramo["hora_hasta"] is None else min(tramo["hora_hasta"], horas)
        cantidad = hasta - desde + 1
        if cantidad <= 0:
            continue
        precio = Decimal(str(tramo["precio"]))
        subtotal = precio * cantidad
        desglose.append({
            "tarifa_id": tramo["tarifa_id"],
            "horas": cantidad,
            "precio": precio,
            "subtotal": subtotal,
        })
        total += subtotal
        horas_cubiertas += cantidad

    if horas_cubiertas != horas:
        raise ValueError("Las tarifas configuradas no cubren todas las horas. "
                         "Pide al administrador que las revise.")
    return total, desglose
