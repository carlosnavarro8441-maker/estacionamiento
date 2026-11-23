from decimal import Decimal, InvalidOperation

import sesion
from modelos import tarifa

PRECIO_MAXIMO = Decimal("99999.99")


def _solo_admin():
    return sesion.es_admin()


def listar_tarifas():
    if not _solo_admin():
        raise PermissionError("Solo el administrador puede ver las tarifas")
    return tarifa.listar_todas()


def listar_descuentos():
    if not _solo_admin():
        raise PermissionError("Solo el administrador puede ver los descuentos")
    return tarifa.listar_descuentos()


def _a_decimal(texto):
    try:
        valor = Decimal(str(texto).strip().replace("$", "").replace(",", ""))
    except InvalidOperation:
        return None
    return valor if valor.is_finite() else None


def actualizar_precio(tarifa_id, precio):
    if not _solo_admin():
        return False, "Solo el administrador puede cambiar tarifas"
    valor = _a_decimal(precio)
    if valor is None or valor <= 0 or valor > PRECIO_MAXIMO:
        return False, "Escribe un precio mayor a cero"
    tarifa.actualizar_precio(tarifa_id, valor.quantize(Decimal("0.01")))
    return True, "Tarifa actualizada"


def actualizar_descuento(descuento_id, porcentaje):
    if not _solo_admin():
        return False, "Solo el administrador puede cambiar descuentos"
    valor = _a_decimal(porcentaje)
    if valor is None or valor < 0 or valor > 100:
        return False, "El descuento debe estar entre 0 y 100"
    tarifa.actualizar_descuento(descuento_id, valor.quantize(Decimal("0.01")))
    return True, "Descuento actualizado"
