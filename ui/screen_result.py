"""Pantalla final: la solución en notación vectorial. El código LaTeX va oculto."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from calculadora import mathrender
from calculadora.formato import vector_columna_html
from ui.widgets import PantallaBase


class PantallaResultado(PantallaBase):
    def __init__(self, win):
        super().__init__(win)
        self.encabezado("4 · Solución en notación vectorial",
                        "La solución escrita como un vector particular más una "
                        "combinación de vectores, tal como se hace a mano.")

        self.tarjeta = QFrame()
        self.tarjeta.setObjectName("card")
        tv = QVBoxLayout(self.tarjeta)
        tv.setContentsMargins(18, 18, 18, 18)
        self.host = QHBoxLayout()
        tv.addLayout(self.host)
        self.raiz.addWidget(self.tarjeta)

        # --- código LaTeX, oculto por defecto -------------------------- #
        self.toggle_latex = QPushButton("▸  Ver sintaxis LaTeX")
        self.toggle_latex.setObjectName("ghost")
        self.toggle_latex.clicked.connect(self._alternar_latex)
        fila_toggle = QHBoxLayout()
        fila_toggle.addWidget(self.toggle_latex)
        fila_toggle.addStretch()
        self.raiz.addLayout(fila_toggle)

        self.caja_latex = QWidget()
        cl = QVBoxLayout(self.caja_latex)
        cl.setContentsMargins(0, 0, 0, 0)
        self.latex_text = QTextEdit()
        self.latex_text.setReadOnly(True)
        self.latex_text.setMaximumHeight(150)
        cl.addWidget(self.latex_text)
        copiar = QPushButton("Copiar LaTeX")
        copiar.setObjectName("secondary")
        copiar.clicked.connect(self._copiar_latex)
        fila_copiar = QHBoxLayout()
        fila_copiar.addStretch()
        fila_copiar.addWidget(copiar)
        cl.addLayout(fila_copiar)
        self.caja_latex.setVisible(False)
        self.raiz.addWidget(self.caja_latex)

        self.raiz.addStretch(1)
        nota = QLabel("Esc: volver al proceso · Enter: menú principal")
        nota.setObjectName("hint")
        self.raiz.addWidget(nota)

        nav = self.navegacion(texto_continuar="Menú principal")
        nav.continuar.connect(lambda: self.win.ir("menu"))

    # -- ciclo de vida ---------------------------------------------- #

    def al_entrar(self, **kw):
        datos = self.sesion.resultado or self.sesion.resolver()
        self._render(datos)
        self.latex_text.setPlainText(datos.get("latex", "") or
                                     "(sin solución vectorial para este sistema)")
        self.caja_latex.setVisible(False)
        self.toggle_latex.setText("▸  Ver sintaxis LaTeX")

    def al_atras(self):
        self.win.ir("proceso")

    def widget_inicial(self):
        return self.nav.boton_continuar

    # -- render ---------------------------------------------------- #

    def _limpiar_host(self):
        while self.host.count():
            item = self.host.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _pix(self, pixmap):
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        return lbl

    def _render(self, datos):
        self._limpiar_host()
        modo = self.sesion.modo
        tipo = datos["tipo"]

        if tipo == "incompatible":
            self.host.addWidget(QLabel(
                "El sistema es inconsistente: no existe solución, "
                "por lo que no hay forma vectorial."))
            self.host.addStretch()
            return

        if tipo == "determinado":
            componentes = datos["solucion"]
            vectores = []
        else:
            componentes = datos["vectorial"]["particular"]
            vectores = datos["vectorial"]["vectores_nulos"]

        usar_img = mathrender.disponible()
        if usar_img:
            self.host.addWidget(QLabel("<b>x</b>  ="))
            self.host.addWidget(self._pix(mathrender.columna_a_pixmap(componentes, modo, fontsize=18)))
            for k, vec in enumerate(vectores):
                mas = mathrender.latex_a_pixmap(rf"+\;\; t_{{{k + 1}}}", fontsize=18)
                self.host.addWidget(self._pix(mas))
                self.host.addWidget(self._pix(mathrender.columna_a_pixmap(vec, modo, fontsize=18)))
        else:
            partes = ["<b>x</b> = ", vector_columna_html(componentes, modo)]
            for k, vec in enumerate(vectores):
                partes.append(f" &nbsp;+&nbsp; t<sub>{k + 1}</sub> ")
                partes.append(vector_columna_html(vec, modo))
            etiqueta = QLabel("".join(partes))
            etiqueta.setTextFormat(Qt.TextFormat.RichText)
            self.host.addWidget(etiqueta)
        self.host.addStretch()

    # -- latex --------------------------------------------------- #

    def _alternar_latex(self):
        visible = not self.caja_latex.isVisible()
        self.caja_latex.setVisible(visible)
        self.toggle_latex.setText(("▾  Ocultar sintaxis LaTeX" if visible
                                   else "▸  Ver sintaxis LaTeX"))

    def _copiar_latex(self):
        QGuiApplication.clipboard().setText(self.latex_text.toPlainText())
        self.toggle_latex.setText("▾  Ocultar sintaxis LaTeX  ·  copiado ✓")