
from modelos import pension, pago_pension


def listar_pensiones(texto="", solo_activas=False):
    pension.actualizar_vencidas()
    return pension.listar(texto, solo_activas)


def obtener_opciones_vehiculos(texto=""):
    return pension.listar_vehiculos_cliente(texto)


def obtener_tarifas():
    return pension.listar_tarifas_mensuales()


def contratar(
    cliente_id,
    vehiculo_id,
    tarifa_id,
    fecha_inicio,
    usuario_id,
    fecha_fin=None
):

    if not all([
        cliente_id,
        vehiculo_id,
        tarifa_id,
        fecha_inicio,
        usuario_id
    ]):
        raise ValueError(
            "Completa cliente, vehículo, tarifa, fecha y usuario."
        )

    return pension.guardar(
        cliente_id,
        vehiculo_id,
        tarifa_id,
        fecha_inicio,
        usuario_id,
        fecha_fin
    )


def cancelar(pension_id):
    return pension.cancelar(pension_id)


def registrar_pago(
    pension_id,
    periodo_inicio,
    periodo_fin,
    metodo_pago_id,
    usuario_id
):

    if not all([
        pension_id,
        periodo_inicio,
        periodo_fin,
        metodo_pago_id,
        usuario_id
    ]):
        raise ValueError(
            "Faltan datos para registrar el pago."
        )

    return pago_pension.registrar_pago(
        pension_id,
        periodo_inicio,
        periodo_fin,
        metodo_pago_id,
        usuario_id
    )


def historial(pension_id):
    return pago_pension.listar_historial(pension_id)


def metodos_pago():
    return pago_pension.listar_metodos_pago()
