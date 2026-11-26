from tkinter import messagebox

import ttkbootstrap as ttk

from controladores import cliente_controlador
from controladores import vehiculo_controlador as ctrl
from vistas.base import FUENTE

SIN_CLIENTE = "Sin cliente (de paso)"
FILTROS = {
    "Todos": "todos",
    "Dentro ahora": "dentro",
    "Con visitas": "con_visitas",
    "Sin historial (se pueden eliminar)": "sin_historial",
}


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.vehiculo_id = None   # None = vehículo nuevo; con número = editando
        self.clientes = {}        # texto de la lista -> cliente_id (o None)
        self.filas = {}           # id -> datos del vehículo que se ve en la tabla

        ttk.Label(self, text="Vehículos", font=(FUENTE, 20, "bold")).pack(anchor="w")
        self._armar_formulario()
        self._armar_tabla()
        self._cargar_clientes()
        self.refrescar()

    # ---------- Construcción de la pantalla ----------
    def _armar_formulario(self):
        marco = ttk.Labelframe(self, text="Datos del vehículo", padding=15)
        marco.pack(fill="x", pady=10)

        campos = [
            ("matricula", "Matrícula *"),
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("color", "Color"),
        ]
        self.entradas = {}
        for i, (clave, texto) in enumerate(campos):
            fila, columna = divmod(i, 2)
            ttk.Label(marco, text=texto).grid(row=fila * 2, column=columna, sticky="w", padx=8)
            entrada = ttk.Entry(marco, width=34)
            entrada.grid(row=fila * 2 + 1, column=columna, sticky="w", padx=8, pady=(0, 8))
            self.entradas[clave] = entrada

        ttk.Label(marco, text="Cliente").grid(row=4, column=0, sticky="w", padx=8)
        self.cliente = ttk.Combobox(marco, state="readonly", width=32)
        self.cliente.grid(row=5, column=0, sticky="w", padx=8)

        self.estado = ttk.Label(marco, text="Vehículo nuevo", bootstyle="secondary")
        self.estado.grid(row=5, column=1, sticky="w", padx=8)

        botones = ttk.Frame(marco)
        botones.grid(row=6, column=0, columnspan=2, sticky="w", pady=(15, 0))
        ttk.Button(botones, text="Guardar", bootstyle="success", width=14,
                   command=self.guardar).pack(side="left", padx=(8, 8))
        ttk.Button(botones, text="Nuevo", bootstyle="secondary-outline", width=14,
                   command=self.limpiar).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Eliminar", bootstyle="danger-outline", width=14,
                   command=self.eliminar).pack(side="left")

    def _armar_tabla(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busqueda = ttk.Entry(barra, width=26)
        self.busqueda.pack(side="left", padx=8)
        self.busqueda.bind("<KeyRelease>", lambda e: self.refrescar())

        ttk.Label(barra, text="Mostrar:").pack(side="left", padx=(15, 0))
        self.filtro = ttk.Combobox(barra, state="readonly", width=32, values=list(FILTROS))
        self.filtro.set("Todos")
        self.filtro.pack(side="left", padx=8)
        self.filtro.bind("<<ComboboxSelected>>", lambda e: self.refrescar())

        columnas = ("matricula", "marca", "modelo", "color", "cliente", "visitas", "estado")
        encabezados = {"matricula": "Matrícula", "marca": "Marca", "modelo": "Modelo",
                       "color": "Color", "cliente": "Cliente", "visitas": "Visitas",
                       "estado": "Estado"}
        anchos = {"matricula": 90, "marca": 100, "modelo": 100, "color": 80,
                  "cliente": 190, "visitas": 60, "estado": 90}

        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8,
                                  bootstyle="primary")
        for c in columnas:
            self.tabla.heading(c, text=encabezados[c])
            self.tabla.column(c, width=anchos[c])
        self.tabla.pack(fill="both", expand=True, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    # ---------- Datos ----------
    def _cargar_clientes(self):
        self.clientes = {SIN_CLIENTE: None}
        for c in cliente_controlador.listar_clientes():
            self.clientes[f"{c['nombre']} (#{c['cliente_id']})"] = c["cliente_id"]
        self.cliente["values"] = list(self.clientes)
        self.cliente.set(SIN_CLIENTE)

    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        self.filas = {}
        filtro = FILTROS[self.filtro.get()]
        for v in ctrl.listar_vehiculos(self.busqueda.get(), filtro):
            self.filas[v["vehiculo_id"]] = v
            if v["dentro"] > 0:
                estado = "Dentro"
            elif v["visitas"] > 0:
                estado = "Fuera"
            else:
                estado = "Sin visitas"
            self.tabla.insert("", "end", iid=str(v["vehiculo_id"]), values=(
                v["matricula"], v["marca"] or "", v["modelo"] or "", v["color"] or "",
                v["cliente"] or "Sin cliente", v["visitas"], estado,
            ))

    # ---------- Acciones ----------
    def seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.vehiculo_id = int(seleccion[0])
        vehiculo = self.filas[self.vehiculo_id]
        for clave, entrada in self.entradas.items():
            entrada.delete(0, "end")
            entrada.insert(0, vehiculo[clave] or "")

        texto = SIN_CLIENTE
        if vehiculo["cliente_id"] is not None:
            texto = next((t for t, i in self.clientes.items() if i == vehiculo["cliente_id"]), None)
            if texto is None:  # el cliente está dado de baja y no sale en la lista
                texto = f"{vehiculo['cliente']} (#{vehiculo['cliente_id']}) - de baja"
                self.clientes[texto] = vehiculo["cliente_id"]
                self.cliente["values"] = list(self.clientes)
        self.cliente.set(texto)
        self.estado.config(text=f"Editando vehículo #{self.vehiculo_id} "
                                f"({vehiculo['visitas']} visita(s))")

    def limpiar(self):
        self.vehiculo_id = None
        for entrada in self.entradas.values():
            entrada.delete(0, "end")
        self.cliente.set(SIN_CLIENTE)
        self.tabla.selection_remove(self.tabla.selection())
        self.estado.config(text="Vehículo nuevo")

    def guardar(self):
        datos = [self.entradas[k].get() for k in ("matricula", "marca", "modelo", "color")]
        cliente_id = self.clientes.get(self.cliente.get())
        if self.vehiculo_id is None:
            ok, mensaje = ctrl.guardar_vehiculo(*datos, cliente_id)
        else:
            ok, mensaje = ctrl.editar_vehiculo(self.vehiculo_id, *datos, cliente_id)
        if ok:
            messagebox.showinfo("Vehículos", mensaje)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje)

    def eliminar(self):
        if self.vehiculo_id is None:
            messagebox.showinfo("Vehículos", "Primero elige un vehículo de la tabla")
            return
        matricula = self.filas[self.vehiculo_id]["matricula"]
        if not messagebox.askyesno(
                "Eliminar", f"¿Eliminar el vehículo {matricula}?\n"
                            f"Solo se puede si nunca ha tenido visitas ni pensiones."):
            return
        ok, mensaje = ctrl.eliminar_vehiculo(self.vehiculo_id)
        if ok:
            messagebox.showinfo("Vehículos", mensaje)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("No se pudo eliminar", mensaje)