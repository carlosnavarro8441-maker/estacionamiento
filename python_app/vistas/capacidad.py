from tkinter import messagebox

import ttkbootstrap as ttk

import sesion
from controladores import capacidad_controlador as ctrl
from vistas.base import FUENTE


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)

        # Segunda barrera de seguridad: solo el admin ve esta pantalla
        if not sesion.es_admin():
            ttk.Label(self, text="No tienes permiso para ver esta pantalla",
                      bootstyle="danger", font=(FUENTE, 14)).pack(pady=40)
            return

        ttk.Label(self, text="Capacidad del estacionamiento",
                  font=(FUENTE, 20, "bold")).pack(anchor="w")

        tarjetas = ttk.Frame(self)
        tarjetas.pack(fill="x", pady=15)
        self.lbl_capacidad = self._tarjeta(tarjetas, "Capacidad")
        self.lbl_ocupados = self._tarjeta(tarjetas, "Ocupados")
        self.lbl_disponibles = self._tarjeta(tarjetas, "Disponibles")

        self.barra = ttk.Progressbar(self, maximum=100, value=0, length=500,
                                     bootstyle="success")
        self.barra.pack(fill="x", pady=(5, 8))
        self.lbl_estado = ttk.Label(self, text="", font=(FUENTE, 14, "bold"))
        self.lbl_estado.pack(anchor="w")

        marco = ttk.Labelframe(self, text="Cambiar capacidad total", padding=15)
        marco.pack(fill="x", pady=25)
        ttk.Label(marco, text="Nueva capacidad (número de espacios):").pack(side="left")
        self.nueva = ttk.Entry(marco, width=10)
        self.nueva.pack(side="left", padx=10)
        self.nueva.bind("<Return>", lambda e: self.guardar())
        ttk.Button(marco, text="Guardar", bootstyle="success", width=12,
                   command=self.guardar).pack(side="left")
        ttk.Button(marco, text="Actualizar", bootstyle="secondary-outline", width=12,
                   command=self.refrescar).pack(side="right")

        self.refrescar()

    def _tarjeta(self, padre, titulo):
        marco = ttk.Labelframe(padre, text=titulo, padding=(25, 10))
        marco.pack(side="left", padx=(0, 15))
        etiqueta = ttk.Label(marco, text="-", font=(FUENTE, 32, "bold"))
        etiqueta.pack()
        return etiqueta

    def refrescar(self):
        estado = ctrl.obtener_estado()
        self.lbl_ocupados.configure(text=str(estado["ocupados"]))

        if not estado["configurado"]:
            self.lbl_capacidad.configure(text="-")
            self.lbl_disponibles.configure(text="-")
            self.barra.configure(value=0, bootstyle="secondary")
            self.lbl_estado.configure(
                text="Sin límite configurado: no se bloquea ninguna entrada",
                bootstyle="secondary")
            return

        total = estado["capacidad"]
        porcentaje = min(100, estado["ocupados"] * 100 / total)
        self.lbl_capacidad.configure(text=str(total))
        self.lbl_disponibles.configure(text=str(estado["disponibles"]))

        if estado["lleno"]:
            estilo, texto = "danger", "ESTACIONAMIENTO LLENO"
        elif porcentaje >= 80:
            estilo, texto = "warning", "Casi lleno"
        else:
            estilo, texto = "success", "Hay espacio disponible"
        self.barra.configure(value=porcentaje, bootstyle=estilo)
        self.lbl_estado.configure(text=f"{texto} ({porcentaje:.0f}% ocupado)",
                                  bootstyle=estilo)

    def guardar(self):
        ok, mensaje = ctrl.cambiar_capacidad(self.nueva.get())
        if ok:
            messagebox.showinfo("Capacidad", mensaje)
            self.nueva.delete(0, "end")
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje)