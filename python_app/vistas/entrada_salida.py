from datetime import datetime
from tkinter import messagebox

import ttkbootstrap as ttk

from controladores import servicio_controlador as ctrl
from vistas.base import FUENTE


def _duracion(entrada):
    """Texto tipo '2 h 15 min' con el tiempo que lleva dentro el vehículo."""
    minutos = int((datetime.now() - entrada).total_seconds() // 60)
    return f"{minutos // 60} h {minutos % 60:02d} min"


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.filas = {}   # servicio_id -> datos del vehículo que se ve en la tabla

        ttk.Label(self, text="Entradas y salidas", font=(FUENTE, 20, "bold")).pack(anchor="w")
        self._armar_entrada()
        self._armar_tabla()
        self.refrescar()

    # ---------- Construcción de la pantalla ----------
    def _armar_entrada(self):
        marco = ttk.Labelframe(self, text="Registrar entrada", padding=15)
        marco.pack(fill="x", pady=10)

        ttk.Label(marco, text="Matrícula *").pack(side="left", padx=(0, 8))
        self.matricula = ttk.Entry(marco, width=16)
        self.matricula.pack(side="left", padx=(0, 12))
        self.matricula.bind("<Return>", lambda e: self.registrar_entrada())
        self.matricula.focus()

        ttk.Button(marco, text="Registrar entrada", bootstyle="success", width=18,
                   command=self.registrar_entrada).pack(side="left")

    def _armar_tabla(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Label(barra, text="Vehículos dentro del estacionamiento",
                  font=(FUENTE, 12, "bold")).pack(side="left")
        ttk.Button(barra, text="Actualizar", bootstyle="secondary-outline",
                   command=self.refrescar).pack(side="right")
        ttk.Button(barra, text="Dar salida y cobrar", bootstyle="primary", width=20,
                   command=self.dar_salida).pack(side="right", padx=8)

        columnas = ("folio", "matricula", "servicio", "cliente", "entrada", "tiempo")
        encabezados = {"folio": "Folio", "matricula": "Matrícula", "servicio": "Servicio",
                       "cliente": "Tipo de cliente", "entrada": "Hora de entrada",
                       "tiempo": "Tiempo dentro"}
        anchos = {"folio": 70, "matricula": 120, "servicio": 100, "cliente": 120,
                  "entrada": 170, "tiempo": 120}

        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=12,
                                  bootstyle="primary")
        for c in columnas:
            self.tabla.heading(c, text=encabezados[c])
            self.tabla.column(c, width=anchos[c])
        self.tabla.pack(fill="both", expand=True, pady=10)
        self.tabla.bind("<Double-1>", lambda e: self.dar_salida())

    # ---------- Datos ----------
    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        self.filas = {}
        for s in ctrl.listar_dentro():
            self.filas[s["servicio_id"]] = s
            es_pension = s["tipo_servicio_id"] == 2
            self.tabla.insert("", "end", iid=str(s["servicio_id"]), values=(
                f"#{s['servicio_id']}",
                s["matricula"],
                "Pensión" if es_pension else "Cajón",
                s["tipo_cliente"].capitalize(),
                s["fecha_hora_entrada"].strftime("%Y-%m-%d %H:%M"),
                _duracion(s["fecha_hora_entrada"]),
            ))

    # ---------- Acciones ----------
    def registrar_entrada(self):
        ok, mensaje = ctrl.registrar_entrada(self.matricula.get())
        if ok:
            messagebox.showinfo("Entrada", mensaje, parent=self)
            self.matricula.delete(0, "end")
            self.refrescar()
        else:
            messagebox.showwarning("Entrada", mensaje, parent=self)

    def dar_salida(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Salida", "Selecciona un vehículo de la tabla", parent=self)
            return
        servicio_id = int(seleccion[0])
        try:
            calculo = ctrl.calcular_salida(servicio_id)
            metodos = ctrl.listar_metodos_pago()
        except ValueError as error:
            messagebox.showwarning("Salida", str(error), parent=self)
            self.refrescar()
            return
        DialogoCobro(self, calculo, metodos, self.refrescar)


class DialogoCobro(ttk.Toplevel):
    """Ventana con el resumen de salida y el cobro."""

    def __init__(self, pantalla, calculo, metodos, al_terminar):
        super().__init__(title="Salida y cobro")
        self.transient(pantalla.winfo_toplevel())
        self.grab_set()
        self.calculo = calculo
        self.al_terminar = al_terminar
        self.metodos = {m["nombre"].capitalize(): m["metodo_pago_id"] for m in metodos}

        cuerpo = ttk.Frame(self, padding=20)
        cuerpo.pack(fill="both", expand=True)

        ttk.Label(cuerpo, text=f"Matrícula: {calculo['matricula']}",
                  font=(FUENTE, 14, "bold")).pack(anchor="w")
        ttk.Label(cuerpo, text=f"Entrada: {calculo['fecha_hora_entrada']:%Y-%m-%d %H:%M}"
                               f"    Salida: {calculo['salida']:%Y-%m-%d %H:%M}").pack(anchor="w")
        ttk.Label(cuerpo, text=f"Tipo de cliente: {calculo['tipo_cliente'].capitalize()}"
                               f"    Horas a cobrar: {calculo['horas']}").pack(anchor="w", pady=(0, 10))

        if calculo["es_pension"]:
            ttk.Label(cuerpo, text="Vehículo con pensión vigente: no se cobra por hora",
                      bootstyle="info").pack(anchor="w", pady=10)
        else:
            for linea in calculo["desglose"]:
                ttk.Label(cuerpo, text=f"{linea['horas']} h x ${linea['precio']:.2f} = "
                                       f"${linea['subtotal']:.2f}").pack(anchor="w")
            ttk.Label(cuerpo, text=f"TOTAL A PAGAR: ${calculo['total']:.2f} MXN",
                      font=(FUENTE, 18, "bold"), bootstyle="success").pack(pady=15)

            ttk.Label(cuerpo, text="Método de pago").pack(anchor="w")
            self.metodo = ttk.Combobox(cuerpo, state="readonly", values=list(self.metodos), width=20)
            self.metodo.pack(anchor="w", pady=(0, 10))
            if self.metodos:
                self.metodo.current(0)

        botones = ttk.Frame(cuerpo)
        botones.pack(fill="x", pady=(10, 0))
        ttk.Button(botones, text="Cancelar", bootstyle="secondary-outline",
                   command=self.destroy).pack(side="left")
        ttk.Button(botones, text="Confirmar", bootstyle="success", width=16,
                   command=self.confirmar).pack(side="right")

    def confirmar(self):
        metodo_id = None
        if not self.calculo["es_pension"]:
            metodo_id = self.metodos.get(self.metodo.get())
        ok, mensaje = ctrl.registrar_salida(self.calculo["servicio_id"], metodo_id,
                                            self.calculo["salida"])
        if ok:
            messagebox.showinfo("Salida", mensaje, parent=self)
            self.destroy()
            self.al_terminar()
        else:
            messagebox.showwarning("Salida", mensaje, parent=self)
