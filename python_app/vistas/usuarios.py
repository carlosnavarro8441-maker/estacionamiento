from tkinter import messagebox

import ttkbootstrap as ttk

import sesion
from controladores import usuario_controlador as ctrl
from vistas.base import FUENTE


class Pantalla(ttk.Frame):
    def __init__(self, padre):
        super().__init__(padre)

        # Segunda barrera de seguridad: solo el admin puede ver esta pantalla
        if not sesion.es_admin():
            ttk.Label(self, text="No tienes permiso para ver esta pantalla",
                      bootstyle="danger", font=(FUENTE, 14)).pack(pady=40)
            return

        self.usuario_id = None   # None = usuario nuevo; con número = editando
        self.perfiles = {}       # nombre del perfil -> id
        self.filas = {}          # id -> datos del usuario que se ve en la tabla

        ttk.Label(self, text="Usuarios", font=(FUENTE, 20, "bold")).pack(anchor="w")
        self._armar_formulario()
        self._armar_tabla()
        self._cargar_perfiles()
        self.refrescar()

    # ---------- Construcción de la pantalla ----------
    def _armar_formulario(self):
        marco = ttk.Labelframe(self, text="Datos del usuario", padding=15)
        marco.pack(fill="x", pady=10)

        campos = [
            ("nombre", "Nombre *", ""),
            ("email", "Correo *", ""),
            ("username", "Usuario *", ""),
        ]
        self.entradas = {}
        for i, (clave, texto, mostrar) in enumerate(campos):
            fila, columna = divmod(i, 2)
            ttk.Label(marco, text=texto).grid(row=fila * 2, column=columna, sticky="w", padx=8)
            entrada = ttk.Entry(marco, width=34)
            entrada.grid(row=fila * 2 + 1, column=columna, sticky="w", padx=8, pady=(0, 8))
            self.entradas[clave] = entrada

        ttk.Label(marco, text="Perfil *").grid(row=2, column=1, sticky="w", padx=8)
        self.perfil = ttk.Combobox(marco, state="readonly", width=32)
        self.perfil.grid(row=3, column=1, sticky="w", padx=8, pady=(0, 8))

        ttk.Label(marco, text="Contraseña").grid(row=4, column=0, sticky="w", padx=8)
        self.entradas["password"] = ttk.Entry(marco, width=34, show="•")
        self.entradas["password"].grid(row=5, column=0, sticky="w", padx=8, pady=(0, 8))

        ttk.Label(marco, text="Confirmar contraseña").grid(row=4, column=1, sticky="w", padx=8)
        self.entradas["confirmar"] = ttk.Entry(marco, width=34, show="•")
        self.entradas["confirmar"].grid(row=5, column=1, sticky="w", padx=8, pady=(0, 8))

        self.estado = ttk.Label(marco, text="Usuario nuevo", bootstyle="secondary")
        self.estado.grid(row=6, column=0, columnspan=2, sticky="w", padx=8)

        botones = ttk.Frame(marco)
        botones.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(botones, text="Guardar", bootstyle="success", width=18,
                   command=self.guardar).pack(side="left", padx=(8, 8))
        ttk.Button(botones, text="Nuevo", bootstyle="secondary-outline", width=14,
                   command=self.limpiar).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Cambiar contraseña", bootstyle="warning-outline", width=20,
                   command=self.cambiar_password).pack(side="left", padx=(0, 8))
        self.btn_estado = ttk.Button(botones, text="Desactivar", bootstyle="danger-outline",
                                     width=14, command=self.alternar_estado)
        self.btn_estado.pack(side="left")

    def _armar_tabla(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busqueda = ttk.Entry(barra, width=30)
        self.busqueda.pack(side="left", padx=8)
        self.busqueda.bind("<KeyRelease>", lambda e: self.refrescar())

        columnas = ("nombre", "username", "email", "perfil", "estado")
        encabezados = {"nombre": "Nombre", "username": "Usuario", "email": "Correo",
                       "perfil": "Perfil", "estado": "Estado"}
        anchos = {"nombre": 220, "username": 130, "email": 220, "perfil": 100, "estado": 90}

        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=7,
                                  bootstyle="primary")
        for c in columnas:
            self.tabla.heading(c, text=encabezados[c])
            self.tabla.column(c, width=anchos[c])
        self.tabla.tag_configure("inactivo", foreground="gray")
        self.tabla.pack(fill="both", expand=True, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    # ---------- Datos ----------
    def _cargar_perfiles(self):
        self.perfiles = {p["nombre"]: p["perfil_id"] for p in ctrl.listar_perfiles()}
        self.perfil["values"] = list(self.perfiles)

    def refrescar(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        self.filas = {}
        for u in ctrl.listar_usuarios(self.busqueda.get()):
            self.filas[u["usuario_id"]] = u
            activo = bool(u["activo"])
            self.tabla.insert("", "end", iid=str(u["usuario_id"]), tags=() if activo else ("inactivo",),
                              values=(u["nombre"], u["username"], u["email"], u["perfil"],
                                      "Activo" if activo else "Inactivo"))

    def _limpiar_claves(self):
        self.entradas["password"].delete(0, "end")
        self.entradas["confirmar"].delete(0, "end")

    # ---------- Acciones ----------
    def seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.usuario_id = int(seleccion[0])
        u = self.filas[self.usuario_id]

        for clave in ("nombre", "email"):
            self.entradas[clave].delete(0, "end")
            self.entradas[clave].insert(0, u[clave] or "")

        # El nombre de usuario no se cambia al editar (se bloquea el campo)
        self.entradas["username"].config(state="normal")
        self.entradas["username"].delete(0, "end")
        self.entradas["username"].insert(0, u["username"])
        self.entradas["username"].config(state="disabled")

        self.perfil.set(u["perfil"])
        self._limpiar_claves()
        self.estado.config(text=f"Editando usuario #{self.usuario_id}. "
                                f"Para cambiar su contraseña, escríbela dos veces y usa el botón.")
        self.btn_estado.config(text="Desactivar" if u["activo"] else "Reactivar")

    def limpiar(self):
        self.usuario_id = None
        self.entradas["username"].config(state="normal")
        for entrada in self.entradas.values():
            entrada.delete(0, "end")
        self.perfil.set("")
        self.tabla.selection_remove(self.tabla.selection())
        self.estado.config(text="Usuario nuevo")
        self.btn_estado.config(text="Desactivar")

    def guardar(self):
        perfil_id = self.perfiles.get(self.perfil.get())
        e = self.entradas
        if self.usuario_id is None:
            ok, mensaje = ctrl.guardar_usuario(
                e["nombre"].get(), e["email"].get(), e["username"].get(),
                e["password"].get(), e["confirmar"].get(), perfil_id)
        else:
            ok, mensaje = ctrl.editar_usuario(
                self.usuario_id, e["nombre"].get(), e["email"].get(), perfil_id)
        if ok:
            messagebox.showinfo("Usuarios", mensaje)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Revisa los datos", mensaje)

    def cambiar_password(self):
        if self.usuario_id is None:
            messagebox.showinfo("Usuarios", "Primero elige un usuario de la tabla")
            return
        ok, mensaje = ctrl.cambiar_password_usuario(
            self.usuario_id, self.entradas["password"].get(), self.entradas["confirmar"].get())
        if ok:
            messagebox.showinfo("Usuarios", mensaje)
            self._limpiar_claves()
        else:
            messagebox.showwarning("Revisa los datos", mensaje)

    def alternar_estado(self):
        if self.usuario_id is None:
            messagebox.showinfo("Usuarios", "Primero elige un usuario de la tabla")
            return
        u = self.filas[self.usuario_id]
        activar = not u["activo"]
        if not activar and not messagebox.askyesno(
                "Desactivar", f"¿Desactivar a {u['nombre']}?\nYa no podrá iniciar sesión, "
                              f"pero su historial se conserva."):
            return
        ok, mensaje = ctrl.cambiar_estado_usuario(self.usuario_id, activar)
        if ok:
            messagebox.showinfo("Usuarios", mensaje)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("No se pudo", mensaje)