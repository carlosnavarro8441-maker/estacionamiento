import ttkbootstrap as ttk

TEMA = "flatly"
FUENTE = "Segoe UI"


class App(ttk.Window):
    def __init__(self):
        super().__init__(title="Sistema de Estacionamiento", themename=TEMA, size=(1050, 680))
        self.contenedor = ttk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)
        self.pantalla_actual = None

    def mostrar(self, clase_pantalla):
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()
        self.pantalla_actual = clase_pantalla(self.contenedor, self)
        self.pantalla_actual.pack(fill="both", expand=True)

    def ir_a_login(self):
        from vistas.login import Login
        self.mostrar(Login)

    def ir_a_menu(self):
        from vistas.menu import MenuPrincipal
        self.mostrar(MenuPrincipal)