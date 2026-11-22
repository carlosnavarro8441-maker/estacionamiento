usuario_actual = None


def iniciar(datos):
    global usuario_actual
    usuario_actual = datos


def cerrar():
    global usuario_actual
    usuario_actual = None


def es_admin():
    return usuario_actual is not None and usuario_actual["perfil"].lower().startswith("admin")