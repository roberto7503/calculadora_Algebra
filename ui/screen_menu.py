"""Pantalla de menú: punto de entrada al flujo. Info de la app abajo, pequeña."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QListWidgetItem, QVBoxLayout

from ui.state import EJEMPLOS
from ui.theme import APP_INFO
from ui.widgets import ListaOpciones, PantallaBase

_PRINCIPAL = "principal"
_EJEMPLOS = "ejemplos"


class PantallaMenu(PantallaBase):
    def __init__(self, win):
        super().__init__(win)
        self.encabezado(f"{APP_INFO['nombre']}", APP_INFO["resumen"])

        self.raiz.addStretch(2)

        self.titulo_lista = QLabel("¿Qué quieres hacer?")
        self.titulo_lista.setObjectName("h1")
        self.titulo_lista.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.raiz.addWidget(self.titulo_lista)

        self.lista = ListaOpciones()
        self.lista.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lista.elegido.connect(self._activar)
        self.raiz.addWidget(self.lista)

        ayuda = QLabel("↑ ↓ para moverte · Enter para elegir · Esc para volver")
        ayuda.setObjectName("hint")
        ayuda.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.raiz.addWidget(ayuda)

        self.raiz.addStretch(3)

        # Pie: autores, licencia, etc. — pequeño y discreto.
        pie = QLabel(
            f"v{APP_INFO['version']}  ·  {APP_INFO['autores']}  ·  "
            f"Licencia {APP_INFO['licencia']}  ·  {APP_INFO['repo']}  ·  "
            "Método: eliminación de Gauss (sin NumPy/SymPy)")
        pie.setObjectName("pie")
        pie.setWordWrap(True)
        pie.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        pie.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.raiz.addWidget(pie)

        self._modo = _PRINCIPAL
        self._poblar_principal()

    # -- poblado de la lista ------------------------------------------------ #

    def _poblar_principal(self):
        self._modo = _PRINCIPAL
        self.titulo_lista.setText("¿Qué quieres hacer?")
        self.lista.clear()
        for texto in ("Iniciar — crear un sistema nuevo",
                      "Ejemplo rápido — cargar un caso de muestra",
                      "Salir"):
            self.lista.addItem(QListWidgetItem(texto))
        self.lista.setCurrentRow(0)
        self.lista.setFixedHeight(self.lista.sizeHintForRow(0) * 3 + 22)

    def _poblar_ejemplos(self):
        self._modo = _EJEMPLOS
        self.titulo_lista.setText("¿Qué tipo de ejemplo? (se resuelve directamente)")
        self.lista.clear()
        for nombre in EJEMPLOS:
            self.lista.addItem(QListWidgetItem(nombre))
        self.lista.addItem(QListWidgetItem("←  Volver"))
        self.lista.setCurrentRow(0)
        self.lista.setFixedHeight(self.lista.sizeHintForRow(0) * 4 + 28)

    # -- eventos ---------------------------------------------------------- #

    def _activar(self, item):
        # Un gesto que repuebla la lista (p. ej. doble clic en "Ejemplo rápido")
        # puede reinvocar este handler con un item ya borrado: Qt lo entrega como
        # None o como un wrapper de C++ inválido. En ambos casos, no hacer nada.
        try:
            texto = item.text() if item is not None else None
        except RuntimeError:
            texto = None
        if texto is None:
            return
        if self._modo == _PRINCIPAL:
            if texto.startswith("Iniciar"):
                self.sesion.iniciar_manual()
                self.win.ir("dimensiones")
            elif texto.startswith("Ejemplo"):
                self._poblar_ejemplos()
            else:
                QApplication.instance().quit()
        else:
            if texto.startswith("←"):
                self._poblar_principal()
            else:
                # Un ejemplo trae dimensiones y valores dados: se acepta tal cual
                # y se salta directo al proceso (pantalla 3).
                self.sesion.cargar_ejemplo(texto)
                self.win.ir("proceso")

        if self._modo == _PRINCIPAL:
            if texto.startswith("Iniciar"):
                self.sesion.iniciar_manual()
                self.win.ir("dimensiones")
            elif texto.startswith("Combinaciones"):
                self.win.ir("vectores_menu") # NUEVA PANTALLA A CREAR
            elif texto.startswith("Ejemplo"):
                self._poblar_ejemplos()
            else:
                QApplication.instance().quit()

    def al_entrar(self, **kw):
        self._poblar_principal()

    def al_atras(self):
        if self._modo == _EJEMPLOS:
            self._poblar_principal()

    def widget_inicial(self):
        return self.lista

    def _poblar_principal(self):
        self._modo = _PRINCIPAL
        self.titulo_lista.setText("¿Qué quieres hacer?")
        self.lista.clear()
        for texto in ("Iniciar — resolver sistema Ax = b",
                      "Combinaciones lineales — propiedades en R^n", # NUEVO
                      "Ejemplo rápido — cargar un caso de muestra",
                      "Salir"):
            self.lista.addItem(QListWidgetItem(texto))
        self.lista.setCurrentRow(0)
        self.lista.setFixedHeight(self.lista.sizeHintForRow(0) * 4 + 28)