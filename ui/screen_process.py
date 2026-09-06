"""Tercera pantalla: el proceso paso a paso y, al final, solución y comprobación."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from calculadora.formato import MENOS, POR, formatear_display, texto_verificacion, var
from ui.widgets import FilaAnalisis, PantallaBase, matriz_widget

_EXPL = {
    "rango": ("Filas linealmente independientes (nº de pivotes).",
              "Rango(A): cuántas ecuaciones aportan información nueva. Es el número "
              "de pivotes que quedan en la forma escalonada."),
    "nulidad": ("Número de variables libres (parámetros).",
                "Nulidad(A): dimensión del conjunto de soluciones de Ax = 0. "
                "Coincide con cuántas incógnitas quedan sin pivote."),
    "suma": ("Debe dar el número de incógnitas n.",
             "Teorema del rango–nulidad: rango(A) + nulidad(A) = n. Sirve de control."),
    "forma": ("Cómo quedó la matriz tras eliminar.",
              "REF: cada pivote más a la derecha que el de arriba y ceros debajo. "
              "RREF: además cada pivote vale 1 y es el único no nulo de su columna."),
}
_FORMA_TXT = {"RREF": "RREF (escalonada reducida)", "REF": "REF (escalonada)",
              "ninguna": "no escalonada"}


class PantallaProceso(PantallaBase):
    def __init__(self, win):
        super().__init__(win)
        self.encabezado("3 · Proceso y resultado",
                        "Recorre la eliminación paso a paso. Debajo, la solución y su "
                        "comprobación.")

        self.estado = QLabel("—")
        self.estado.setObjectName("status")
        self.estado.setWordWrap(True)
        self.raiz.addWidget(self.estado)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = QWidget()
        self.cuerpo = QVBoxLayout(contenido)
        self.cuerpo.setContentsMargins(2, 2, 2, 2)
        self.cuerpo.setSpacing(16)
        scroll.setWidget(contenido)
        self.raiz.addWidget(scroll, 1)

        # --- bloque de PASOS (protagonista) --------------------------- #
        pasos_card = QFrame()
        pasos_card.setObjectName("card")
        pv = QVBoxLayout(pasos_card)
        pv.setContentsMargins(16, 14, 16, 14)
        cabecera = QLabel("Paso a paso")
        cabecera.setObjectName("h1")
        pv.addWidget(cabecera)
        self.paso_desc = QLabel("—")
        self.paso_desc.setObjectName("prompt")
        self.paso_desc.setWordWrap(True)
        pv.addWidget(self.paso_desc)
        self.paso_matriz_host = QVBoxLayout()
        pv.addLayout(self.paso_matriz_host)
        fila_nav = QHBoxLayout()
        self.btn_prev = QPushButton("←  Anterior")
        self.btn_prev.setObjectName("secondary")
        self.btn_prev.clicked.connect(lambda: self._mostrar_paso(self.paso - 1))
        self.btn_next = QPushButton("Siguiente  →")
        self.btn_next.setObjectName("secondary")
        self.btn_next.clicked.connect(lambda: self._mostrar_paso(self.paso + 1))
        self.contador = QLabel("—")
        self.contador.setObjectName("hint")
        fila_nav.addWidget(self.btn_prev)
        fila_nav.addWidget(self.contador, 1)
        fila_nav.addWidget(self.btn_next)
        pv.addLayout(fila_nav)
        self.cuerpo.addWidget(pasos_card)

        # --- solución + comprobación (al final) ---------------------- #
        self.sol_card = QFrame()
        self.sol_card.setObjectName("card")
        self.sol_layout = QVBoxLayout(self.sol_card)
        self.sol_layout.setContentsMargins(16, 14, 16, 14)
        self.sol_layout.setSpacing(6)
        self.cuerpo.addWidget(self.sol_card)

        # --- análisis ---------------------------------------------- #
        self.ana_card = QFrame()
        self.ana_card.setObjectName("card")
        self.ana_layout = QVBoxLayout(self.ana_card)
        self.ana_layout.setContentsMargins(16, 14, 16, 14)
        titulo_ana = QLabel("Análisis: rango, nulidad y forma escalonada")
        titulo_ana.setObjectName("h1")
        self.ana_layout.addWidget(titulo_ana)
        self.cuerpo.addWidget(self.ana_card)

        nota = QLabel("← → recorren los pasos · Enter: ver solución vectorial · Esc: volver")
        nota.setObjectName("hint")
        self.raiz.addWidget(nota)

        nav = self.navegacion(texto_continuar="Ver solución vectorial  →")
        nav.continuar.connect(lambda: self.win.ir("resultado"))

        QShortcut(QKeySequence("Left"), self,
                  activated=lambda: self._mostrar_paso(self.paso - 1))
        QShortcut(QKeySequence("Right"), self,
                  activated=lambda: self._mostrar_paso(self.paso + 1))

        self.paso = 0
        self.pasos = []

    # -- ciclo de vida ------------------------------------------------- #

    def al_entrar(self, **kw):
        datos = self.sesion.resultado or self.sesion.resolver()
        self.pasos = datos["pasos"]
        self._pintar_estado(datos["tipo"])
        self._pintar_solucion(datos)
        self._pintar_analisis(datos)
        self.paso = 0
        self._mostrar_paso(0)

    def al_atras(self):
        # Si venimos de un ejemplo, no hay pantallas de entrada que revisar.
        self.win.ir("entrada" if self.sesion.origen == "manual" else "menu")

    def widget_inicial(self):
        # El foco va al botón de continuar (Enter avanza de pantalla); los pasos
        # se recorren con ← → gracias a los atajos de ventana.
        return self.nav.boton_continuar

    # -- pasos ------------------------------------------------------- #

    def _mostrar_paso(self, indice):
        if not self.pasos:
            return
        self.paso = max(0, min(indice, len(self.pasos) - 1))
        descripcion, matriz = self.pasos[self.paso]
        self.paso_desc.setText(f"Paso {self.paso + 1} de {len(self.pasos)} · {descripcion}")
        self.contador.setText(f"{self.paso + 1} / {len(self.pasos)}")
        while self.paso_matriz_host.count():
            w = self.paso_matriz_host.takeAt(0).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self.paso_matriz_host.addWidget(matriz_widget(matriz, self.sesion))
        self.btn_prev.setEnabled(self.paso > 0)
        self.btn_next.setEnabled(self.paso < len(self.pasos) - 1)

    # -- estado / solución / análisis ------------------------------ #

    def _pintar_estado(self, tipo):
        estilos = {
            "determinado": ("Sistema consistente determinado · solución única",
                            "background:#dff7e7; color:#176b46;"),
            "indeterminado": ("Sistema consistente indeterminado · infinitas soluciones",
                              "background:#fff3cf; color:#805900;"),
            "incompatible": ("Sistema inconsistente · no tiene solución",
                             "background:#ffe6e5; color:#9f2520;"),
        }
        texto, css = estilos[tipo]
        self.estado.setText(texto)
        self.estado.setStyleSheet(f"#status {{ {css} }}")

    @staticmethod
    def _limpiar(layout, desde=0):
        while layout.count() > desde:
            item = layout.takeAt(desde)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            elif item.layout():
                PantallaProceso._limpiar(item.layout())

    def _fmt(self, valor):
        return formatear_display(valor, self.sesion.modo)

    def _pintar_solucion(self, datos):
        self._limpiar(self.sol_layout)
        titulo = QLabel("Solución y comprobación")
        titulo.setObjectName("h1")
        self.sol_layout.addWidget(titulo)

        tipo = datos["tipo"]
        if tipo == "incompatible":
            self.sol_layout.addWidget(QLabel(
                "Una ecuación se redujo a 0 = c con c ≠ 0: el sistema no tiene solución."))
            return

        if tipo == "determinado":
            for i, valor in enumerate(datos["solucion"]):
                self.sol_layout.addWidget(QLabel(f"{var(i)} = <b>{self._fmt(valor)}</b>"))
        else:
            libres, expresiones = datos["parametrica"]
            n = datos["n"]
            for v in range(n):
                if v in libres:
                    self.sol_layout.addWidget(QLabel(
                        f"{var(v)} = t{libres.index(v) + 1}  (variable libre)"))
                    continue
                cte, partes = expresiones[v]
                txt = self._fmt(cte)
                for coef, libre in partes:
                    signo = "+" if coef >= 0 else MENOS
                    txt += f" {signo} {self._fmt(abs(coef))} {POR} t{libres.index(libre) + 1}"
                self.sol_layout.addWidget(QLabel(f"{var(v)} = {txt}"))

        encabezado, filas = datos["verificacion"]
        comp = QLabel(f"<b>{encabezado}</b>")
        comp.setStyleSheet("margin-top:8px;")
        self.sol_layout.addWidget(comp)
        todo_ok = True
        for i, fila in enumerate(filas):
            if not fila["coincide"]:
                todo_ok = False
            linea = QLabel(texto_verificacion(i, fila, self.sesion.modo))
            linea.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.sol_layout.addWidget(linea)
        cierre = QLabel("✓ La solución satisface todas las ecuaciones." if todo_ok
                        else "✗ La solución NO satisface todas las ecuaciones.")
        cierre.setStyleSheet("font-weight:700; color:%s;" % ("#176b46" if todo_ok else "#9f2520"))
        self.sol_layout.addWidget(cierre)

    def _pintar_analisis(self, datos):
        self._limpiar(self.ana_layout, desde=1)  # conserva el título
        rango, nul, suma, n = datos["rango"], datos["nulidad"], datos["suma"], datos["n"]
        casa = "✓ coincide con n" if suma == n else "✗ no coincide"
        filas = (
            (f"Rango(A) = {rango}", *_EXPL["rango"]),
            (f"Nulidad(A) = {nul}", *_EXPL["nulidad"]),
            (f"Rango + Nulidad = {rango} + {nul} = {suma}",
             f"n = {n} · {casa}.", _EXPL["suma"][1]),
            (f"Forma: {_FORMA_TXT.get(datos['forma'], datos['forma'])}", *_EXPL["forma"]),
        )
        for titulo, breve, detalle in filas:
            self.ana_layout.addWidget(FilaAnalisis(titulo, breve, detalle))