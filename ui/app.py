"""Ventana principal: un QStackedWidget que va mostrando cada pantalla."""

import os
import sys

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget

from calculadora import mathrender
from ui.theme import APP_INFO, aplicar_tema

_ORDEN = ("menu", "dimensiones", "entrada", "proceso", "resultado")


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        from ui.state import Sesion  # import perezoso: evita ciclos al arrancar

        self.sesion = Sesion()
        self.setWindowTitle(f"{APP_INFO['nombre']} · Eliminación de Gauss")
        self.resize(1040, 760)
        self.setMinimumSize(820, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        from ui.screen_dimensions import PantallaDimensiones
        from ui.screen_input import PantallaEntrada
        from ui.screen_menu import PantallaMenu
        from ui.screen_process import PantallaProceso
        from ui.screen_result import PantallaResultado

        clases = {
            "menu": PantallaMenu,
            "dimensiones": PantallaDimensiones,
            "entrada": PantallaEntrada,
            "proceso": PantallaProceso,
            "resultado": PantallaResultado,
        }
        self.pantallas = {}
        for nombre in _ORDEN:
            pantalla = clases[nombre](self)
            self.pantallas[nombre] = pantalla
            self.stack.addWidget(pantalla)

        QShortcut(QKeySequence("Escape"), self, activated=self._atras_global)
        QShortcut(QKeySequence("F1"), self, activated=lambda: self.ir("menu"))

        self.ir("menu")

    def ir(self, nombre, **kw):
        pantalla = self.pantallas[nombre]
        pantalla.al_entrar(**kw)
        self.stack.setCurrentWidget(pantalla)
        inicial = pantalla.widget_inicial()
        if inicial is not None:
            inicial.setFocus()

    def _atras_global(self):
        self.stack.currentWidget().al_atras()


def main():
    app = QApplication(sys.argv)
    aplicar_tema(app)

    ventana = VentanaPrincipal()
    ventana.show()

    if not mathrender.disponible() and os.environ.get("AQUA_GAUSS_SILENCIAR") != "1":
        QMessageBox.information(
            ventana, "Notación matemática como texto",
            "No se encontró <b>matplotlib</b>, así que la notación se mostrará como "
            "texto en vez de renderizada.<br><br>"
            "Para verla bonita, cierra la app y ejecútala dentro del entorno de uv:"
            "<br><code>uv sync</code><br><code>uv run python gui.py</code>")

    sys.exit(app.exec())