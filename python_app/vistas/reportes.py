
from datetime import date, timedelta
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from controladores import reporte_controlador as controlador
from vistas.base import FUENTE


class Pantalla(ttk.Frame):

    def __init__(self, padre):

        super().__init__(padre, padding=15)

        ttk.Label(
            self,
            text="Reportes del estacionamiento",
            font=(FUENTE, 18, "bold")
        ).pack(anchor=W)

        ttk.Button(
            self,
            text="Actualizar reportes",
            command=self.actualizar_todos
        ).pack(anchor=E, pady=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, pady=10)

        self.frames = {}

        reportes = [
            ("ingresos", "Ingresos"),
            ("movimiento", "Entradas y salidas"),
            ("clientes", "Clientes"),
            ("pensiones", "Pensiones")
        ]

        for clave, titulo in reportes:

            frame = ttk.Frame(
                self.notebook,
                padding=10
            )

            self.notebook.add(
                frame,
                text=titulo
            )

            self.frames[clave] = frame

        self.actualizar_todos()

    def dibujar(
        self,
        frame,
        titulo,
        etiquetas,
        valores,
        tipo="bar"
    ):

        for widget in frame.winfo_children():
            widget.destroy()

        if not etiquetas:

            ttk.Label(
                frame,
                text="No hay datos suficientes para mostrar este reporte.",
                bootstyle=SECONDARY
            ).pack(pady=30)

            return

        fig = Figure(
            figsize=(7.5, 4.2),
            dpi=100
        )

        ax = fig.add_subplot(111)

        if tipo == "pie":

            ax.pie(
                valores,
                labels=etiquetas,
                autopct="%1.1f%%"
            )

        elif tipo == "line":

            ax.plot(
                etiquetas,
                valores,
                marker="o"
            )

            ax.tick_params(
                axis="x",
                rotation=35
            )

        else:

            ax.bar(
                etiquetas,
                valores
            )

            ax.tick_params(
                axis="x",
                rotation=25
            )

        ax.set_title(titulo)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(
            fig,
            master=frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill=BOTH,
            expand=True
        )

    def actualizar_todos(self):

        try:

            hoy = date.today()
            inicio = hoy - timedelta(days=29)

            # REPORTE 1: INGRESOS

            ingresos = controlador.reporte_ingresos(
                inicio,
                hoy
            )

            resumen = ingresos["resumen"]

            self.dibujar(
                self.frames["ingresos"],
                "Ingresos por día",
                [
                    str(x["periodo"])
                    for x in ingresos["serie"]
                ],
                [
                    float(x["total"])
                    for x in ingresos["serie"]
                ],
                "line"
            )

            ttk.Label(
                self.frames["ingresos"],
                text=(
                    f"Ingresos del periodo: "
                    f"${resumen['total']:.2f} "
                    f"| Cobros: {resumen['cantidad']}"
                ),
                font=(FUENTE, 12, "bold")
            ).pack(
                anchor=W,
                before=self.frames["ingresos"].winfo_children()[0]
            )

            # REPORTE 2: MOVIMIENTO

            movimiento = controlador.reporte_movimiento(
                inicio,
                hoy
            )

            datos = movimiento["resumen"]

            self.dibujar(
                self.frames["movimiento"],
                "Entradas por hora",
                [
                    str(x["hora"])
                    for x in movimiento["serie"]
                ],
                [
                    int(x["cantidad"])
                    for x in movimiento["serie"]
                ]
            )

            ttk.Label(
                self.frames["movimiento"],
                text=(
                    f"Entradas: {datos['entradas'] or 0} "
                    f"| Salidas: {datos['salidas'] or 0} "
                    f"| Dentro: {datos['dentro'] or 0}"
                ),
                font=(FUENTE, 12, "bold")
            ).pack(
                anchor=W,
                before=self.frames["movimiento"].winfo_children()[0]
            )

            # REPORTE 3: CLIENTES

            clientes = controlador.reporte_clientes()

            self.dibujar(
                self.frames["clientes"],
                "Clientes activos por tipo",
                [
                    x["categoria"]
                    for x in clientes
                ],
                [
                    int(x["clientes"])
                    for x in clientes
                ],
                "pie"
            )

            # REPORTE 4: PENSIONES

            pensiones = controlador.reporte_pensiones()

            estados = pensiones["estados"]

            self.dibujar(
                self.frames["pensiones"],
                "Pensiones por estado",
                [
                    x["estado"]
                    for x in estados
                ],
                [
                    int(x["cantidad"])
                    for x in estados
                ]
            )

            # Ingresos de pensiones
            total_pensiones = sum(
                float(x["total"] or 0)
                for x in pensiones["pagos"]
            )

            ttk.Label(
                self.frames["pensiones"],
                text=(
                    f"Total de ingresos por pensiones: "
                    f"${total_pensiones:.2f}"
                ),
                font=(FUENTE, 12, "bold")
            ).pack(
                anchor=W,
                before=self.frames["pensiones"].winfo_children()[0]
            )

        except Exception as error:

            messagebox.showerror(
                "Reportes",
                f"No se pudieron generar los reportes.\n{error}",
                parent=self
            )
