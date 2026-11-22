from tkinter import messagebox

import ttkbootstrap as ttk

from controladores import cliente_controlador as ctrl
from vistas.base import FUENTE


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.cliente_id = None  # None = cliente nuevo; con número = editando
        self.tipos = {}         # nombre del tipo -> id
        self.filas = {}         # id -> datos del cliente que se ve en la tabla

        ttk.Label(self, text="Clientes", font=(FUENTE, 20, "bold")).pack(anchor="w")
        self._armar_formulario()
        self._armar_tabla()
        self._cargar_tipos()
        self.refrescar()

    # ---------- Construcción de la pantalla ----------
    def _armar_formulario(self):
        marco = ttk.Labelframe(self, text="Datos del cliente", padding=15)
        marco.pack(fill="x", pady=10)

        campos = [
            ("nombre", "Nombre *"),
            ("telefono", "Teléfono (10 dígitos)"),
            ("email", "Correo"),
            ("rfc", "RFC"),
        ]
        self.entradas = {}
        for i, (clave, texto) in enumerate(campos):
            fila, columna = divmod(i, 2)
            ttk.Label(marco, text=texto).grid(row=fila * 2, column=columna, sticky="w", padx=8)
            entrada = ttk.Entry(marco, width=34)
            entrada.grid(row=fila * 2 + 1, column=columna, sticky="w", padx=8, pady=(0, 8))
            self.entradas[clave] = entrada

        ttk.Label(marco, text="Tipo de cliente *").grid(row=4, column=0, sticky="w", padx=8)
        self.tipo = ttk.Combobox(marco, state="readonly", width=32)
        self.tipo.grid(row=5, column=0, sticky="w", padx=8)

        self.estado = ttk.Label(marco, text="Cliente nuevo", bootstyle="secondary")
        self.estado.grid(row=5, column=1, sticky="w", padx=8)

        botones = ttk.Frame(marco)
        botones.grid(row=6, column=0, columnspan=2, sticky="w", pady=(15, 0))
        ttk.Button(botones, text="Guardar", bootstyle="success", width=14,
                   command=self.guardar).pack(side="left", padx=(8, 8))
        ttk.Button(botones, text="Nuevo", bootstyle="secondary-outline", width=14,
                   command=self.limpiar).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Dar de baja", bootstyle="danger-outline", width=14,
                   command=self.dar_de_baja).pack(side="left")

    def _armar_tabla(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busqueda = ttk.Entry(barra, width=30)
        self.busqueda.pack(side="left", padx=8)
        self.busqueda.bind("<KeyRelease>", lambda e: self.refrescar())

        columnas = ("nombre", "telefono", "email", "rfc", "tipo")
        encabezados = {"nombre": "Nombre", "telefono": "Teléfono", "email": "Correo",
                       "rfc": "RFC", "tipo": "Tipo"}
        anchos = {"nombre": 220, "telefono": 110, "email": 200, "rfc": 130, "tipo": 90}

        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=8,
                                  bootstyle="primary")
        for c in columnas:
            self.tabla.heading(c, text=encabezados[c])
            self.tabla.column(c, width=anchos[c])
        self.tabla.pack(fill="both", expand=True, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    # ---------- Datos ----------
    def _cargar_tipos(self):
        self.tipos = {t["nombre"]: t["tipo_cliente_id"] for t in ctrl.listar_tipos()}
        self.tipo["values"] = list(self.tipos)

    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        self.filas = {}
        for c in ctrl.listar_clientes(self.busqueda.get()):
            self.filas[c["cliente_id"]] = c
            self.tabla.insert("", "end", iid=str(c["cliente_id"]), values=(
                c["nombre"], c["telefono"] or "", c["email"] or "", c["rfc"] or "", c["tipo"]
            ))

    # ---------- Acciones ----------
    def seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.cliente_id = int(seleccion[0])
        cliente = self.filas[self.cliente_id]
        for clave, entrada in self.entradas.items():
            entrada.delete(0, "end")
            entrada.insert(0, cliente[clave] or "")
        self.tipo.set(cliente["tipo"])
        self.estado.config(text=f"Editando cliente #{self.cliente_id}")

    def limpiar(self):
        self.cliente_id = None
        for entrada in self.entradas.values():
            entrada.delete(0, "end")
        self.tipo.set("")
        self.tabla.selection_remove(self.tabla.selection())
        self.estado.config(text="Cliente nuevo")

    def guardar(self):
        datos = [self.entradas[k].get() for k in ("nombre", "telefono", "email", "rfc")]
        tipo_id = self.tipos.get(self.tipo.get())
        if self.cliente_id is None:
            ok, mensaje = ctrl.guardar_cliente(*datos, tipo_id)
        else:
            ok, mensaje = ctrl.editar_cliente(self.cliente_id, *datos, tipo_id)
        if ok:
            messagebox.showinfo("Clientes", mensaje)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje)

    def dar_de_baja(self):
        if self.cliente_id is None:
            messagebox.showinfo("Clientes", "Primero elige un cliente de la tabla")
            return
        nombre = self.filas[self.cliente_id]["nombre"]
        if messagebox.askyesno("Dar de baja", f"¿Dar de baja a {nombre}?\nSu historial se conserva."):
            ok, mensaje = ctrl.dar_de_baja_cliente(self.cliente_id)
            messagebox.showinfo("Clientes", mensaje)
            self.limpiar()
            self.refrescar()