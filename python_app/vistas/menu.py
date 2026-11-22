import importlib

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import sesion
from vistas.base import FUENTE
from vistas.modulos import MODULOS


class MenuPrincipal(ttk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        self.app = app
        usuario = sesion.usuario_actual

        barra = ttk.Frame(self, bootstyle="dark", padding=(20, 12))
        barra.pack(fill=X)
        ttk.Label(barra, text="Estacionamiento", font=(FUENTE, 16, "bold"),
                  bootstyle="inverse-dark").pack(side=LEFT)
        ttk.Button(barra, text="Salir", bootstyle="danger-outline",
                   command=self.cerrar_sesion).pack(side=RIGHT)
        ttk.Label(barra, text=f"{usuario['nombre']} ({usuario['perfil']})",
                  bootstyle="inverse-dark").pack(side=RIGHT, padx=15)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill=BOTH, expand=True)

        lateral = ttk.Frame(cuerpo, padding=15)
        lateral.pack(side=LEFT, fill=Y)
        self.contenido = ttk.Frame(cuerpo, padding=20)
        self.contenido.pack(side=LEFT, fill=BOTH, expand=True)

        for texto, archivo, solo_admin in MODULOS:
            if solo_admin and not sesion.es_admin():
                continue
            ttk.Button(
                lateral, text=texto, width=20, bootstyle="primary-outline",
                command=lambda a=archivo, t=texto: self.abrir(a, t),
            ).pack(pady=4)

        self.inicio()

    def limpiar(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def inicio(self):
        self.limpiar()
        ttk.Label(self.contenido, text=f"Bienvenido, {sesion.usuario_actual['nombre']}",
                  font=(FUENTE, 20, "bold")).pack(anchor=W)
        ttk.Label(self.contenido, text="Elige una opción del menú de la izquierda.",
                  bootstyle=SECONDARY).pack(anchor=W, pady=5)

    def abrir(self, archivo, titulo, solo_admin=False):
        if solo_admin and not sesion.es_admin():
            return
        self.limpiar()
        try:
            modulo = importlib.import_module(f"vistas.{archivo}")
        except ModuleNotFoundError as error:
            if error.name != f"vistas.{archivo}":
                raise
            ttk.Label(self.contenido, text=f"{titulo}: en construcción",
                      font=(FUENTE, 14)).pack(pady=40)
            return
        modulo.Pantalla(self.contenido).pack(fill=BOTH, expand=True)

    def cerrar_sesion(self):
        sesion.cerrar()
        self.app.ir_a_login()