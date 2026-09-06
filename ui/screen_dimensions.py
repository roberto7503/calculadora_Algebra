"""Primera pantalla: dimensiones del sistema y notación."""

from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QSpinBox,
)

from calculadora.formato import MODO_DECIMAL, MODO_FRACCION
from ui.widgets import PantallaBase


class PantallaDimensiones(PantallaBase):
    def __init__(self, win):
        super().__init__(win)
        self.encabezado("1 · Dimensiones y notación",
                        "Elige cuántas ecuaciones e incógnitas tiene el sistema.")

        ficha = QFrame()
        ficha.setObjectName("card")
        rejilla = QGridLayout(ficha)
        rejilla.setContentsMargins(22, 20, 22, 20)
        rejilla.setHorizontalSpacing(18)
        rejilla.setVerticalSpacing(14)

        self.ecuaciones = QSpinBox()
        self.ecuaciones.setRange(1, 12)
        self.incognitas = QSpinBox()
        self.incognitas.setRange(1, 12)
        self.notacion = QComboBox()
        self.notacion.addItems(["Fracción", "Decimal"])
        self.notacion.setToolTip(
            "Fracción: recíprocos exactos como 1/2, 1/4, -8/3 (como se hace a mano).\n"
            "Decimal: aproximación con 4 cifras.")

        rejilla.addWidget(QLabel("Ecuaciones (filas)"), 0, 0)
        rejilla.addWidget(self.ecuaciones, 0, 1)
        rejilla.addWidget(QLabel("Incógnitas (columnas de A)"), 1, 0)
        rejilla.addWidget(self.incognitas, 1, 1)
        rejilla.addWidget(QLabel("Notación de los números"), 2, 0)
        rejilla.addWidget(self.notacion, 2, 1)
        rejilla.setColumnStretch(2, 1)

        self.raiz.addWidget(ficha)
        self.raiz.addStretch(1)

        nota = QLabel("Enter para continuar · Esc para volver al menú")
        nota.setObjectName("hint")
        self.raiz.addWidget(nota)

        nav = self.navegacion(texto_continuar="Ingresar términos  →")
        nav.continuar.connect(self._continuar)

        self.notacion = QComboBox()
        self.notacion.addItems(["Fracción", "Decimal"])

        # --- NUEVO: Selector de método ---
        self.metodo = QComboBox()
        self.metodo.addItems(["Gauss (Escalonada + Sustitución)", "Gauss-Jordan (Escalonada Reducida)"])
        self.metodo.setToolTip("Gauss: Llega a REF y despeja.\nGauss-Jordan: Llega a RREF entregando la solución directa.")

        rejilla.addWidget(QLabel("Ecuaciones (filas)"), 0, 0)
        rejilla.addWidget(self.ecuaciones, 0, 1)
        rejilla.addWidget(QLabel("Incógnitas (columnas de A)"), 1, 0)
        rejilla.addWidget(self.incognitas, 1, 1)
        rejilla.addWidget(QLabel("Notación de los números"), 2, 0)
        rejilla.addWidget(self.notacion, 2, 1)
        # --- NUEVO: Añadir a la rejilla ---
        rejilla.addWidget(QLabel("Método de resolución"), 3, 0)
        rejilla.addWidget(self.metodo, 3, 1)
        rejilla.setColumnStretch(2, 1)

    def al_entrar(self, **kw):
        self.ecuaciones.setValue(self.sesion.n_eq)
        self.incognitas.setValue(self.sesion.n_var)
        self.notacion.setCurrentText(
            "Decimal" if self.sesion.modo == MODO_DECIMAL else "Fracción")
        # --- NUEVO ---
        idx = 0 if getattr(self.sesion, 'metodo', 'gauss') == 'gauss' else 1
        self.metodo.setCurrentIndex(idx)

    def al_atras(self):
        self.win.ir("menu")

    def widget_inicial(self):
        return self.ecuaciones

    def _continuar(self):
        self.sesion.modo = (MODO_DECIMAL if self.notacion.currentText() == "Decimal"
                            else MODO_FRACCION)
        # --- NUEVO ---
        self.sesion.metodo = "gauss" if self.metodo.currentIndex() == 0 else "gauss_jordan"

        n_eq, n_var = self.ecuaciones.value(), self.incognitas.value()
        if (n_eq, n_var) != (self.sesion.n_eq, self.sesion.n_var):
            self.sesion.redimensionar(n_eq, n_var)
        else:
            self.sesion.resultado = None
        self.win.ir("entrada")
