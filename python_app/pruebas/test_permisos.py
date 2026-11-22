import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sesion
from vistas.modulos import MODULOS

ADMIN = {"id": 1, "nombre": "Admin", "username": "admin", "perfil": "admin"}
COBRADOR = {"id": 2, "nombre": "Cobrador", "username": "cobrador1", "perfil": "cobrador"}


def modulos_visibles():
    """Mismos botones que dibuja el menú según la sesión actual."""
    return [texto for texto, _archivo, solo_admin in MODULOS
            if not solo_admin or sesion.es_admin()]


def probar_sin_sesion():
    sesion.cerrar()
    assert not sesion.es_admin(), "Sin sesión nadie debe ser admin"


def probar_admin():
    sesion.iniciar(ADMIN)
    assert sesion.es_admin()
    assert len(modulos_visibles()) == len(MODULOS), "El admin debe ver todos los módulos"
    sesion.iniciar({**ADMIN, "perfil": "Administrador"})
    assert sesion.es_admin(), "El perfil 'Administrador' también cuenta como admin"


def probar_cobrador():
    sesion.iniciar(COBRADOR)
    assert not sesion.es_admin()
    visibles = modulos_visibles()
    assert visibles == ["Entradas y salidas", "Clientes", "Vehículos"], visibles
    for prohibido in ("Pensiones", "Reportes", "Tarifas", "Usuarios"):
        assert prohibido not in visibles, f"El cobrador no debe ver {prohibido}"


def probar_cierre_de_sesion():
    sesion.iniciar(ADMIN)
    sesion.cerrar()
    assert sesion.usuario_actual is None
    assert not sesion.es_admin()


if __name__ == "__main__":
    probar_sin_sesion()
    probar_admin()
    probar_cobrador()
    probar_cierre_de_sesion()
    print("Todas las pruebas de permisos pasaron")