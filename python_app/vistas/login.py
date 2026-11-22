import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import sesion
from controladores.auth_controlador import iniciar_sesion
from vistas.base import FUENTE


class Login(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app

        caja = ttk.Frame(self, padding=40)
        caja.place(relx=0.5, rely=0.5, anchor=CENTER)

        ttk.Label(caja, text="Estacionamiento Público", font=(FUENTE, 22, "bold")).pack()
        ttk.Label(caja, text="Inicia sesión para continuar", bootstyle=SECONDARY).pack(pady=(0, 25))

        ttk.Label(caja, text="Usuario").pack(anchor=W)
        self.usuario = ttk.Entry(caja, width=32)
        self.usuario.pack(pady=(0, 12))

        ttk.Label(caja, text="Contraseña").pack(anchor=W)
        self.clave = ttk.Entry(caja, width=32, show="•")
        self.clave.pack(pady=(0, 8))

        self.mensaje = ttk.Label(caja, text="", bootstyle=DANGER)
        self.mensaje.pack(pady=(0, 8))

        ttk.Button(caja, text="Entrar", bootstyle=PRIMARY, width=30, command=self.entrar).pack()

        self.clave.bind("<Return>", lambda e: self.entrar())
        self.usuario.bind("<Return>", lambda e: self.clave.focus())
        self.usuario.focus()

    def entrar(self):
        username = self.usuario.get().strip()
        password = self.clave.get()
        if not username or not password:
            self.mensaje.config(text="Escribe tu usuario y contraseña")
            return
        try:
            datos = iniciar_sesion(username, password)
        except Exception as error:
            print("Error de conexión:", error)
            self.mensaje.config(text="No se pudo conectar a la base de datos")
            return
        if datos is None:
            self.mensaje.config(text="Usuario o contraseña incorrectos")
            return
        sesion.iniciar(datos)
        self.app.ir_a_menu()