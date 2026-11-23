from tkinter import messagebox

import ttkbootstrap as ttk

import sesion
from controladores import tarifa_controlador as ctrl
from vistas.base import FUENTE


def _tramo(t):
    if t["unidad"] == "mes":
        return "Mensualidad"
    if t["hora_hasta"] is None:
        return f"Hora {t['hora_desde']} en adelante"
    return f"Horas {t['hora_desde']} a {t['hora_hasta']}"


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)

        # Segunda barrera de seguridad: solo el admin puede ver esta pantalla
        if not sesion.es_admin():
            ttk.Label(self, text="No tienes permiso para ver esta pantalla",
                      bootstyle="danger", font=(FUENTE, 14)).pack(pady=40)
            return

        self.tarifa_id = None
        self.descuento_id = None

        ttk.Label(self, text="Tarifas y descuentos", font=(FUENTE, 20, "bold")).pack(anchor="w")
        self._armar_tarifas()
        self._armar_descuentos()
        self.refrescar()

    # ---------- Construcción de la pantalla ----------
    def _armar_tarifas(self):
        marco = ttk.Labelframe(self, text="Tarifas (MXN)", padding=15)
        marco.pack(fill="both", expand=True, pady=10)

        columnas = ("id", "servicio", "cliente", "tramo", "precio", "unidad")
        encabezados = {"id": "ID", "servicio": "Servicio", "cliente": "Cliente",
                       "tramo": "Tramo", "precio": "Precio", "unidad": "Unidad"}
        anchos = {"id": 50, "servicio": 110, "cliente": 110, "tramo": 200,
                  "precio": 110, "unidad": 90}
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=8,
                                  bootstyle="primary")
        for c in columnas:
            self.tabla.heading(c, text=encabezados[c])
            self.tabla.column(c, width=anchos[c])
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

        edicion = ttk.Frame(marco)
        edicion.pack(fill="x", pady=(10, 0))
        self.etiqueta = ttk.Label(edicion, text="Selecciona una tarifa para cambiar su precio",
                                  bootstyle="secondary")
        self.etiqueta.pack(side="left")
        ttk.Button(edicion, text="Guardar precio", bootstyle="success", width=16,
                   command=self.guardar_precio).pack(side="right")
        self.precio = ttk.Entry(edicion, width=12)
        self.precio.pack(side="right", padx=8)
        ttk.Label(edicion, text="Nuevo precio $").pack(side="right")

    def _armar_descuentos(self):
        marco = ttk.Labelframe(self, text="Descuento de pensión por antigüedad", padding=15)
        marco.pack(fill="x", pady=10)

        self.texto_descuento = ttk.Label(marco, text="")
        self.texto_descuento.pack(side="left")
        ttk.Button(marco, text="Guardar descuento", bootstyle="success", width=18,
                   command=self.guardar_descuento).pack(side="right")
        self.porcentaje = ttk.Entry(marco, width=8)
        self.porcentaje.pack(side="right", padx=8)
        ttk.Label(marco, text="Porcentaje %").pack(side="right")

    # ---------- Datos ----------
    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for t in ctrl.listar_tarifas():
            self.tabla.insert("", "end", iid=str(t["tarifa_id"]), values=(
                t["tarifa_id"], t["servicio"].capitalize(), t["cliente"].capitalize(),
                _tramo(t), f"${t['precio']:.2f}", t["unidad"],
            ))

        descuentos = [d for d in ctrl.listar_descuentos() if d["activo"]]
        if descuentos:
            d = descuentos[0]
            self.descuento_id = d["descuento_id"]
            self.texto_descuento.config(
                text=f"Pensiones con más de {d['anios_minimos']} años: {d['porcentaje']}% de descuento")
            self.porcentaje.delete(0, "end")
            self.porcentaje.insert(0, str(d["porcentaje"]))
        else:
            self.descuento_id = None
            self.texto_descuento.config(text="No hay un descuento configurado en la base de datos")

    # ---------- Acciones ----------
    def seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.tarifa_id = int(seleccion[0])
        valores = self.tabla.item(seleccion[0])["values"]
        self.etiqueta.config(text=f"Tarifa #{self.tarifa_id}: {valores[1]} / {valores[2]} / {valores[3]}")
        self.precio.delete(0, "end")
        self.precio.insert(0, str(valores[4]).replace("$", ""))

    def guardar_precio(self):
        if self.tarifa_id is None:
            messagebox.showinfo("Tarifas", "Selecciona una tarifa de la tabla", parent=self)
            return
        ok, mensaje = ctrl.actualizar_precio(self.tarifa_id, self.precio.get())
        if ok:
            messagebox.showinfo("Tarifas", mensaje, parent=self)
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje, parent=self)

    def guardar_descuento(self):
        if self.descuento_id is None:
            messagebox.showinfo("Descuentos", "No hay un descuento que modificar", parent=self)
            return
        ok, mensaje = ctrl.actualizar_descuento(self.descuento_id, self.porcentaje.get())
        if ok:
            messagebox.showinfo("Descuentos", mensaje, parent=self)
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje, parent=self)
