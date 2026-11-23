
from datetime import date
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import sesion
from controladores import pension_controlador as controlador
from vistas.base import FUENTE


class Pantalla(ttk.Frame):

    def __init__(self, padre):

        super().__init__(padre, padding=15)

        # Segunda barrera de seguridad: solo el admin puede ver esta pantalla
        if not sesion.es_admin():
            ttk.Label(
                self,
                text="No tienes permiso para ver esta pantalla",
                bootstyle="danger",
                font=(FUENTE, 14)
            ).pack(pady=40)
            return

        self.seleccion = None

        ttk.Label(
            self,
            text="Administración de pensiones",
            font=(FUENTE, 18, "bold")
        ).pack(anchor=W)

        barra = ttk.Frame(self)
        barra.pack(fill=X, pady=10)

        self.busqueda = ttk.Entry(barra, width=32)
        self.busqueda.pack(side=LEFT, padx=(0, 6))

        ttk.Button(
            barra,
            text="Buscar",
            command=self.cargar
        ).pack(side=LEFT, padx=3)

        ttk.Button(
            barra,
            text="Actualizar",
            command=self.cargar
        ).pack(side=LEFT, padx=3)

        ttk.Button(
            barra,
            text="Contratar pensión",
            bootstyle="success",
            command=self.contratar
        ).pack(side=RIGHT, padx=3)

        ttk.Button(
            barra,
            text="Registrar pago",
            bootstyle="primary",
            command=self.pagar
        ).pack(side=RIGHT, padx=3)

        ttk.Button(
            barra,
            text="Cancelar pensión",
            bootstyle="danger-outline",
            command=self.cancelar
        ).pack(side=RIGHT, padx=3)

        ttk.Button(
            barra,
            text="Historial de pagos",
            bootstyle="info-outline",
            command=self.ver_historial
        ).pack(side=RIGHT, padx=3)

        columnas = (
            "id",
            "cliente",
            "matricula",
            "inicio",
            "fin",
            "tarifa",
            "estado"
        )

        self.tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=17
        )

        encabezados = {
            "id": "ID",
            "cliente": "Cliente",
            "matricula": "Matrícula",
            "inicio": "Inicio",
            "fin": "Fin",
            "tarifa": "Mensualidad",
            "estado": "Estado"
        }

        anchos = {
            "id": 55,
            "cliente": 190,
            "matricula": 100,
            "inicio": 100,
            "fin": 100,
            "tarifa": 100,
            "estado": 90
        }

        for col in columnas:

            self.tabla.heading(
                col,
                text=encabezados[col]
            )

            self.tabla.column(
                col,
                width=anchos[col],
                anchor=CENTER if col != "cliente" else W
            )

        self.tabla.pack(fill=BOTH, expand=True)

        ttk.Label(
            self,
            text="Selecciona una pensión para registrar su pago.",
            bootstyle=SECONDARY
        ).pack(anchor=W, pady=(8, 0))

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.seleccionar
        )

        self.cargar()

    def cargar(self):

        try:

            texto = self.busqueda.get().strip()

            filas = controlador.listar_pensiones(texto)

            self.tabla.delete(
                *self.tabla.get_children()
            )

            for p in filas:

                self.tabla.insert(
                    "",
                    END,
                    iid=str(p["pension_id"]),
                    values=(
                        p["pension_id"],
                        p["cliente"],
                        p["matricula"],
                        p["fecha_inicio"],
                        p["fecha_fin"] or "—",
                        f"${p['tarifa_mensual']:.2f}",
                        p["estado"]
                    )
                )

        except Exception as error:

            messagebox.showerror(
                "Pensiones",
                f"No se pudieron cargar las pensiones.\n{error}",
                parent=self
            )

    def seleccionar(self, evento=None):

        seleccion = self.tabla.selection()

        self.seleccion = (
            int(seleccion[0])
            if seleccion else None
        )

    
    def ver_historial(self):

        if not self.seleccion:
            messagebox.showwarning(
                "Historial",
                "Selecciona una pensión.",
                parent=self
            )
            return

        try:
            pagos = controlador.historial(self.seleccion)

            ventana = ttk.Toplevel(self)
            ventana.title("Historial de pagos")
            ventana.geometry("700x400")

            columnas = (
                "periodo",
                "fecha",
                "base",
                "descuento",
                "total",
                "metodo"
            )

            tabla = ttk.Treeview(
                ventana,
                columns=columnas,
                show="headings"
            )

            encabezados = {
                "periodo": "Periodo",
                "fecha": "Fecha de pago",
                "base": "Monto base",
                "descuento": "Descuento",
                "total": "Total pagado",
                "metodo": "Método de pago"
            }

            for columna in columnas:
                tabla.heading(
                    columna,
                    text=encabezados[columna]
                )

            tabla.pack(fill=BOTH, expand=True, padx=10, pady=10)

            for pago in pagos:
                tabla.insert(
                    "",
                    END,
                    values=(
                        f"{pago['periodo_inicio']} - {pago['periodo_fin']}",
                        pago["fecha_pago"],
                        f"${pago['monto_base']:.2f}",
                        f"{pago['porcentaje'] or 0}%",
                        f"${pago['monto_pagado']:.2f}",
                        pago["metodo_pago"] or "—"
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "Historial",
                str(error),
                parent=self
            )

    def contratar(self):

        try:

            vehiculos = controlador.obtener_opciones_vehiculos()
            tarifas = controlador.obtener_tarifas()

            if not vehiculos:

                messagebox.showwarning(
                    "Pensiones",
                    "No hay vehículos asociados a clientes activos.",
                    parent=self
                )

                return

            if not tarifas:

                messagebox.showwarning(
                    "Pensiones",
                    "No hay tarifa mensual configurada.",
                    parent=self
                )

                return

            ventana = ttk.Toplevel(self)
            ventana.title("Contratar pensión")
            ventana.geometry("480x330")
            ventana.transient(self.winfo_toplevel())
            ventana.grab_set()

            ttk.Label(
                ventana,
                text="Vehículo y cliente"
            ).pack(anchor=W, padx=15, pady=(15, 4))

            opciones_v = [
                f"{v['vehiculo_id']} | {v['matricula']} | {v['cliente']}"
                for v in vehiculos
            ]

            combo_v = ttk.Combobox(
                ventana,
                values=opciones_v,
                state="readonly",
                width=55
            )

            combo_v.pack(padx=15, fill=X)
            combo_v.current(0)

            ttk.Label(
                ventana,
                text="Tarifa mensual"
            ).pack(anchor=W, padx=15, pady=(12, 4))

            opciones_t = [
                f"{t['tarifa_id']} | ${t['precio']:.2f} por mes"
                for t in tarifas
            ]

            combo_t = ttk.Combobox(
                ventana,
                values=opciones_t,
                state="readonly",
                width=45
            )

            combo_t.pack(padx=15, fill=X)
            combo_t.current(0)

            ttk.Label(
                ventana,
                text="Fecha de inicio (AAAA-MM-DD)"
            ).pack(anchor=W, padx=15, pady=(12, 4))

            entrada_fecha = ttk.Entry(ventana)

            entrada_fecha.insert(
                0,
                date.today().isoformat()
            )

            entrada_fecha.pack(padx=15, fill=X)

            def guardar():

                try:

                    v = vehiculos[combo_v.current()]
                    t = tarifas[combo_t.current()]

                    controlador.contratar(
                        v["cliente_id"],
                        v["vehiculo_id"],
                        t["tarifa_id"],
                        entrada_fecha.get().strip(),
                        sesion.usuario_actual["id"]
                    )

                    messagebox.showinfo(
                        "Pensiones",
                        "Pensión contratada correctamente.",
                        parent=ventana
                    )

                    ventana.destroy()
                    self.cargar()

                except Exception as error:

                    messagebox.showerror(
                        "No se pudo contratar",
                        str(error),
                        parent=ventana
                    )

            ttk.Button(
                ventana,
                text="Guardar contratación",
                bootstyle="success",
                command=guardar
            ).pack(pady=20)

        except Exception as error:

            messagebox.showerror(
                "Pensiones",
                str(error),
                parent=self
            )

    def pagar(self):

        if not self.seleccion:

            messagebox.showwarning(
                "Pensiones",
                "Selecciona una pensión.",
                parent=self
            )

            return

        try:

            metodos = controlador.metodos_pago()

            if not metodos:

                messagebox.showwarning(
                    "Pagos",
                    "No hay métodos de pago registrados.",
                    parent=self
                )

                return

            ventana = ttk.Toplevel(self)
            ventana.title("Registrar pago mensual")
            ventana.geometry("420x330")
            ventana.transient(self.winfo_toplevel())
            ventana.grab_set()

            ttk.Label(
                ventana,
                text="Inicio del periodo (AAAA-MM-DD)"
            ).pack(anchor=W, padx=15, pady=(15, 4))

            inicio = ttk.Entry(ventana)

            inicio.insert(
                0,
                date.today().replace(day=1).isoformat()
            )

            inicio.pack(fill=X, padx=15)

            ttk.Label(
                ventana,
                text="Fin del periodo (AAAA-MM-DD)"
            ).pack(anchor=W, padx=15, pady=(10, 4))

            fin = ttk.Entry(ventana)
            fin.insert(0, date.today().isoformat())
            fin.pack(fill=X, padx=15)

            ttk.Label(
                ventana,
                text="Método de pago"
            ).pack(anchor=W, padx=15, pady=(10, 4))

            combo = ttk.Combobox(
                ventana,
                state="readonly",
                values=[m["nombre"] for m in metodos]
            )

            combo.pack(fill=X, padx=15)
            combo.current(0)

            def guardar_pago():

                try:

                    resultado = controlador.registrar_pago(
                        self.seleccion,
                        inicio.get().strip(),
                        fin.get().strip(),
                        metodos[combo.current()]["metodo_pago_id"],
                        sesion.usuario_actual["id"]
                    )

                    messagebox.showinfo(
                        "Pago registrado",
                        f"Base: ${resultado['monto_base']:.2f}\n"
                        f"Descuento: {resultado['porcentaje']}%\n"
                        f"Total pagado: ${resultado['monto_pagado']:.2f}",
                        parent=ventana
                    )

                    ventana.destroy()

                except Exception as error:

                    messagebox.showerror(
                        "No se pudo registrar el pago",
                        str(error),
                        parent=ventana
                    )

            ttk.Button(
                ventana,
                text="Registrar pago",
                bootstyle="success",
                command=guardar_pago
            ).pack(pady=20)

        except Exception as error:

            messagebox.showerror(
                "Pagos",
                str(error),
                parent=self
            )

    def cancelar(self):

        if not self.seleccion:

            messagebox.showwarning(
                "Pensiones",
                "Selecciona una pensión.",
                parent=self
            )

            return

        if messagebox.askyesno(
            "Confirmar",
            "¿Deseas finalizar esta pensión?",
            parent=self
        ):

            try:

                controlador.cancelar(self.seleccion)
                self.cargar()

            except Exception as error:

                messagebox.showerror(
                    "Pensiones",
                    str(error),
                    parent=self
                )
    
