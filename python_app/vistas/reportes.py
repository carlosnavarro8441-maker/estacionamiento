from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import sesion
from controladores import reporte_controlador as controlador
from vistas.base import FUENTE


class Pantalla(ttk.Frame):

    def __init__(self, padre):

        super().__init__(padre, padding=15)

        # Segunda barrera de seguridad: solo el admin puede ver los reportes
        if not sesion.es_admin():
            ttk.Label(
                self,
                text="No tienes permiso para ver esta pantalla",
                bootstyle="danger",
                font=(FUENTE, 14)
            ).pack(pady=40)
            return

        ttk.Label(
            self,
            text="Reportes del estacionamiento",
            font=(FUENTE, 18, "bold")
        ).pack(anchor=W)

        barra = ttk.Frame(self)
        barra.pack(fill=X, pady=5)

        ttk.Label(barra, text="Año:").pack(side=LEFT)

        self.anio = ttk.Combobox(barra, state="readonly", width=8)
        self.anio.pack(side=LEFT, padx=8)
        self.anio.bind("<<ComboboxSelected>>", lambda e: self.actualizar_todos())

        ttk.Button(
            barra,
            text="Actualizar reportes",
            command=self.actualizar_todos
        ).pack(side=RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, pady=10)

        self.frames = {}

        reportes = [
            ("mensual", "Entradas y salidas por mes"),
            ("meses", "Meses de mayor demanda"),
            ("horarios", "Horarios de mayor demanda"),
            ("ingresos", "Ingresos por servicio"),
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

        try:
            anios = controlador.anios_disponibles()
        except Exception as error:
            messagebox.showerror(
                "Reportes",
                f"No se pudo conectar a la base de datos.\n{error}",
                parent=self
            )
            return

        self.anio["values"] = anios
        self.anio.set(anios[0])

        self.actualizar_todos()

    # ---------- Ayudas para dibujar ----------

    def _limpiar(self, frame):

        for widget in frame.winfo_children():
            widget.destroy()

    def _resumen(self, frame, texto):

        ttk.Label(
            frame,
            text=texto,
            font=(FUENTE, 12, "bold")
        ).pack(anchor=W, pady=(0, 6))

    def _sin_datos(self, frame, texto="No hay datos suficientes para mostrar este reporte."):

        ttk.Label(
            frame,
            text=texto,
            bootstyle=SECONDARY
        ).pack(pady=30)

    def dibujar(
        self,
        frame,
        titulo,
        etiquetas,
        series,
        tipo="bar",
        rotacion=30
    ):
        """Dibuja una gráfica. `series` es una lista de (nombre, valores)."""

        fig = Figure(
            figsize=(8.5, 4.2),
            dpi=100
        )

        ax = fig.add_subplot(111)

        if tipo == "pie":

            ax.pie(
                series[0][1],
                labels=etiquetas,
                autopct="%1.1f%%"
            )

        elif tipo == "line":

            for nombre, valores in series:
                ax.plot(
                    etiquetas,
                    valores,
                    marker="o",
                    label=nombre
                )

        else:

            n = len(series)
            ancho = 0.8 / n
            posiciones = range(len(etiquetas))

            for k, (nombre, valores) in enumerate(series):
                ax.bar(
                    [p + k * ancho - 0.4 + ancho / 2 for p in posiciones],
                    valores,
                    width=ancho,
                    label=nombre
                )

            ax.set_xticks(list(posiciones))
            ax.set_xticklabels(etiquetas)

        if tipo != "pie":

            ax.tick_params(
                axis="x",
                rotation=rotacion
            )

            if len(series) > 1:
                ax.legend()

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

    # ---------- Reportes ----------

    def actualizar_todos(self):

        if not self.anio.get():
            return

        anio = int(self.anio.get())

        try:

            self._mensual(anio)
            self._meses(anio)
            self._horarios(anio)
            self._ingresos(anio)
            self._clientes()
            self._pensiones()

        except Exception as error:

            messagebox.showerror(
                "Reportes",
                f"No se pudieron generar los reportes.\n{error}",
                parent=self
            )

    def _mensual(self, anio):
        """Requisito 7: entradas y salidas por mes."""

        frame = self.frames["mensual"]
        self._limpiar(frame)

        datos = controlador.reporte_entradas_salidas_mensual(anio)

        entradas = sum(d["entradas"] for d in datos)
        salidas = sum(d["salidas"] for d in datos)

        self._resumen(
            frame,
            f"{anio}: {entradas} entradas | {salidas} salidas"
        )

        if entradas == 0 and salidas == 0:
            self._sin_datos(frame, f"No hay entradas ni salidas en {anio}.")
            return

        self.dibujar(
            frame,
            f"Entradas y salidas por mes - {anio}",
            [d["mes"][:3] for d in datos],
            [
                ("Entradas", [d["entradas"] for d in datos]),
                ("Salidas", [d["salidas"] for d in datos])
            ],
            rotacion=0
        )

    def _meses(self, anio):
        """Requisito 8: meses con mayor demanda del año."""

        frame = self.frames["meses"]
        self._limpiar(frame)

        datos = controlador.reporte_meses_demanda(anio)
        ranking = datos["ranking"]

        if not ranking:
            self._sin_datos(frame, f"No hay entradas en {anio}.")
            return

        top = ", ".join(
            f"{m['mes']} ({m['entradas']})"
            for m in ranking[:3]
        )

        self._resumen(
            frame,
            f"Mayor demanda en {anio}: {top}"
        )

        self.dibujar(
            frame,
            f"Entradas por mes - {anio}",
            [m["mes"][:3] for m in datos["meses"]],
            [("Entradas", [m["entradas"] for m in datos["meses"]])],
            rotacion=0
        )

    def _horarios(self, anio):
        """Requisito 9: horarios con mayor demanda del año."""

        frame = self.frames["horarios"]
        self._limpiar(frame)

        datos = controlador.reporte_horarios_demanda(anio)
        ranking = datos["ranking"]

        if not ranking:
            self._sin_datos(frame, f"No hay entradas en {anio}.")
            return

        top = ", ".join(
            f"{h['hora']:02d}:00 ({h['entradas']})"
            for h in ranking[:3]
        )

        self._resumen(
            frame,
            f"Horas con mayor demanda en {anio}: {top}"
        )

        self.dibujar(
            frame,
            f"Entradas por hora del día - {anio}",
            [f"{h['hora']:02d}" for h in datos["horas"]],
            [("Entradas", [h["entradas"] for h in datos["horas"]])],
            rotacion=0
        )

    def _ingresos(self, anio):
        """Requisito 10: ingresos por servicio según el año."""

        frame = self.frames["ingresos"]
        self._limpiar(frame)

        datos = controlador.reporte_ingresos_por_servicio(anio)

        detalle = " | ".join(
            f"{t['servicio']}: ${t['total']:,.2f}"
            for t in datos["totales"]
        )

        self._resumen(
            frame,
            f"{anio}: {detalle} | Total: ${datos['total']:,.2f}"
        )

        if datos["total"] == 0:
            self._sin_datos(frame, f"No hay ingresos en {anio}.")
            return

        self.dibujar(
            frame,
            f"Ingresos por mes y servicio - {anio} (MXN)",
            [d["mes"][:3] for d in datos["mensual"]],
            [
                ("Cajón", [d["cajon"] for d in datos["mensual"]]),
                ("Pensión", [d["pension"] for d in datos["mensual"]])
            ],
            rotacion=0
        )

    def _clientes(self):

        frame = self.frames["clientes"]
        self._limpiar(frame)

        clientes = controlador.reporte_clientes()

        if not clientes or sum(int(x["clientes"]) for x in clientes) == 0:
            self._sin_datos(frame)
            return

        self.dibujar(
            frame,
            "Clientes activos por tipo",
            [x["categoria"] for x in clientes],
            [("Clientes", [int(x["clientes"]) for x in clientes])],
            "pie"
        )

    def _pensiones(self):

        frame = self.frames["pensiones"]
        self._limpiar(frame)

        pensiones = controlador.reporte_pensiones()
        estados = pensiones["estados"]

        total_pensiones = sum(
            float(x["total"] or 0)
            for x in pensiones["pagos"]
        )

        self._resumen(
            frame,
            f"Total de ingresos por pensiones: ${total_pensiones:,.2f}"
        )

        if not estados or sum(int(x["cantidad"]) for x in estados) == 0:
            self._sin_datos(frame, "Todavía no hay pensiones registradas.")
            return

        self.dibujar(
            frame,
            "Pensiones por estado",
            [x["estado"] for x in estados],
            [("Pensiones", [int(x["cantidad"]) for x in estados])],
            rotacion=0
        )
