import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk

from controladores import cajon_controlador as ctrl
from vistas.base import FUENTE

COLUMNAS = 10


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.vehiculos = {}   # texto de la lista -> servicio_id
        self.libres = {}      # texto de la lista -> cajon_id

        ttk.Label(self, text="Cajones", font=(FUENTE, 20, "bold")).pack(anchor="w")

        encabezado = ttk.Frame(self)
        encabezado.pack(fill="x", pady=(5, 10))
        self.lbl_resumen = ttk.Label(encabezado, text="", font=(FUENTE, 12))
        self.lbl_resumen.pack(side="left")
        ttk.Button(encabezado, text="Actualizar", bootstyle="secondary-outline",
                   command=self.refrescar).pack(side="right")

        self._armar_asignacion()

        leyenda = ttk.Frame(self)
        leyenda.pack(fill="x", pady=(0, 10))
        ttk.Label(leyenda, text=" Libre ", bootstyle="inverse-success").pack(side="left", padx=(0, 8))
        ttk.Label(leyenda, text=" Ocupado ", bootstyle="inverse-danger").pack(side="left")

        zona = ttk.Frame(self)
        zona.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(zona, highlightthickness=0, bg=ttk.Style().colors.bg)
        barra = ttk.Scrollbar(zona, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)

        self.mapa = ttk.Frame(self.lienzo)
        self.lienzo.create_window((0, 0), window=self.mapa, anchor="nw")
        self.mapa.bind("<Configure>",
                       lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))

        self.refrescar()

    # ---------- Panel de asignación ----------
    def _armar_asignacion(self):
        marco = ttk.Labelframe(self, text="Asignar cajón a un vehículo que está dentro", padding=12)
        marco.pack(fill="x", pady=(0, 10))

        ttk.Label(marco, text="Vehículo:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.cmb_vehiculo = ttk.Combobox(marco, state="readonly", width=28)
        self.cmb_vehiculo.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(marco, text="Cajón libre:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.cmb_cajon = ttk.Combobox(marco, state="readonly", width=14)
        self.cmb_cajon.grid(row=0, column=3, padx=(0, 20))

        ttk.Button(marco, text="Asignar", bootstyle="success", width=12,
                   command=self.asignar).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(marco, text="Quitar cajón", bootstyle="danger-outline", width=14,
                   command=self.quitar).grid(row=0, column=5)

    def _cargar_listas(self):
        self.vehiculos = {}
        for v in ctrl.listar_vehiculos_dentro():
            estado = f"cajón {v['cajon_numero']}" if v["cajon_numero"] else "sin cajón"
            self.vehiculos[f"{v['matricula']} ({estado})"] = v["servicio_id"]
        self.cmb_vehiculo["values"] = list(self.vehiculos)
        self.cmb_vehiculo.set("")

        self.libres = {f"Cajón {c['numero']}": c["cajon_id"] for c in ctrl.listar_cajones_libres()}
        self.cmb_cajon["values"] = list(self.libres)
        self.cmb_cajon.set("")

    def asignar(self):
        servicio_id = self.vehiculos.get(self.cmb_vehiculo.get())
        cajon_id = self.libres.get(self.cmb_cajon.get())
        if servicio_id is None or cajon_id is None:
            messagebox.showinfo("Cajones", "Elige un vehículo y un cajón libre")
            return
        ok, mensaje = ctrl.asignar_cajon(servicio_id, cajon_id)
        self._resultado(ok, mensaje)

    def quitar(self):
        servicio_id = self.vehiculos.get(self.cmb_vehiculo.get())
        if servicio_id is None:
            messagebox.showinfo("Cajones", "Elige un vehículo")
            return
        ok, mensaje = ctrl.asignar_cajon(servicio_id, None)
        self._resultado(ok, mensaje)

    def _resultado(self, ok, mensaje):
        if ok:
            messagebox.showinfo("Cajones", mensaje)
        else:
            messagebox.showwarning("Cajones", mensaje)
        self.refrescar()

    # ---------- Mapa ----------
    def refrescar(self):
        for widget in self.mapa.winfo_children():
            widget.destroy()
        try:
            datos = ctrl.obtener_mapa()
        except Exception as error:
            print("Error al cargar cajones:", error)
            self.lbl_resumen.configure(
                text="No se pudieron cargar los cajones. ¿Importaste database/cajones.sql?")
            return
        if datos is None:
            self.lbl_resumen.configure(
                text="Todavía no hay capacidad configurada (pantalla Capacidad)")
            return

        self.lbl_resumen.configure(
            text=f"Libres: {datos['libres']}   ·   Ocupados: {datos['ocupados']}   ·   "
                 f"Dentro sin cajón asignado: {datos['sin_cajon']}")

        for i, c in enumerate(datos["cajones"]):
            fila, columna = divmod(i, COLUMNAS)
            ocupado = c["ocupado"]
            texto = f"{c['numero']}\n{c['matricula'] or ''}" if ocupado else f"{c['numero']}\nLibre"
            ttk.Label(
                self.mapa, text=texto, width=11, anchor="center", justify="center", padding=8,
                bootstyle="inverse-danger" if ocupado else "inverse-success",
            ).grid(row=fila, column=columna, padx=4, pady=4)

        self._cargar_listas()