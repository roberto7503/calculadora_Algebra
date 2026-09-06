"""Widgets reutilizables por varias pantallas."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from calculadora import mathrender


class ListaOpciones(QListWidget):
    """QListWidget que emite ``elegido`` una sola vez por gesto, con Enter/Return
    o con doble clic.

    En macOS ``itemActivated`` no se dispara con Enter (de ahí ``keyPressEvent``).
    NO se conecta ``itemDoubleClicked`` además de ``itemActivated``: haría que un
    doble clic emitiera dos veces, y si el primer handler repuebla la lista el
    segundo recibe un item ya borrado (``None``) -> AttributeError."""

    elegido = pyqtSignal(object)  # el QListWidgetItem seleccionado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._emitiendo = False
        self.itemActivated.connect(self._emitir)

    def _emitir(self, item):
        if item is None or self._emitiendo:
            return
        self._emitiendo = True
        try:
            self.elegido.emit(item)
        finally:
            self._emitiendo = False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._emitir(self.currentItem())
            return
        super().keyPressEvent(event)


class PantallaBase(QWidget):
    """Andamiaje común: una columna centrada (no ocupa todo el ancho) con
    encabezado 'hero', cuerpo y barra de navegación."""

    ANCHO_MAX = 820

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.sesion = win.sesion
        self.setObjectName("pantalla")

        exterior = QHBoxLayout(self)
        exterior.setContentsMargins(24, 20, 24, 18)
        exterior.addStretch(1)
        columna = QWidget()
        columna.setMaximumWidth(self.ANCHO_MAX)
        columna.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        exterior.addWidget(columna, 8)   # 8:1:1 -> ocupa el centro pero topado en ANCHO_MAX
        exterior.addStretch(1)

        self.raiz = QVBoxLayout(columna)
        self.raiz.setContentsMargins(0, 0, 0, 0)
        self.raiz.setSpacing(14)
        self.nav = None

    def encabezado(self, titulo, subtitulo=""):
        hero = QFrame()
        hero.setObjectName("hero")
        v = QVBoxLayout(hero)
        v.setContentsMargins(22, 15, 22, 15)
        t = QLabel(titulo)
        t.setObjectName("title")
        t.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        v.addWidget(t)
        if subtitulo:
            s = QLabel(subtitulo)
            s.setObjectName("subtitle")
            s.setWordWrap(True)
            s.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            v.addWidget(s)
        self.raiz.addWidget(hero)

    def navegacion(self, **kw):
        self.nav = BarraNavegacion(**kw)
        self.nav.atras.connect(self.al_atras)
        self.raiz.addWidget(self.nav)
        return self.nav

    # las subclases sobreescriben lo que necesiten
    def al_entrar(self, **kw):
        pass

    def al_atras(self):
        pass

    def widget_inicial(self):
        return None


def boton_ayuda(texto):
    """Un botón '?' con explicación: tooltip al pasar el ratón y también al
    activarlo con el teclado (Espacio/Enter) — así funciona sin ratón."""
    boton = QToolButton()
    boton.setObjectName("help")
    boton.setText("?")
    boton.setToolTip(texto)
    boton.setCursor(Qt.CursorShape.WhatsThisCursor)
    boton.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    boton.clicked.connect(
        lambda: QToolTip.showText(boton.mapToGlobal(boton.rect().bottomLeft()), texto, boton)
    )
    return boton


class FilaAnalisis(QWidget):
    """Una métrica: título en negrita + '?' + explicación breve siempre visible."""

    def __init__(self, titulo, breve, detalle, parent=None):
        super().__init__(parent)
        caja = QVBoxLayout(self)
        caja.setContentsMargins(0, 2, 0, 2)
        caja.setSpacing(1)
        cabecera = QHBoxLayout()
        cabecera.setSpacing(6)
        et = QLabel(f"<b>{titulo}</b>")
        et.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cabecera.addWidget(et)
        cabecera.addWidget(boton_ayuda(detalle))
        cabecera.addStretch()
        caja.addLayout(cabecera)
        sub = QLabel(breve)
        sub.setObjectName("explain")
        sub.setWordWrap(True)
        caja.addWidget(sub)


class MatrizGrid(QFrame):
    """Matriz aumentada como rejilla de etiquetas, con corchetes y regla A│b.

    Permite resaltar una celda (para la entrada guiada)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        contorno = QHBoxLayout(self)
        contorno.setContentsMargins(10, 12, 10, 12)
        self._grid = QGridLayout()
        self._grid.setContentsMargins(4, 4, 4, 4)
        self._grid.setHorizontalSpacing(14)
        self._grid.setVerticalSpacing(8)
        contorno.addStretch()
        contorno.addLayout(self._grid)
        contorno.addStretch()

    def poblar(self, sesion, resaltar=None):
        while self._grid.count():
            w = self._grid.takeAt(0).widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        n = sesion.n_var
        filas = sesion.n_eq
        # columnas:  0 etiqueta | 1 corchete[ | 2..2+n-1 x | 2+n regla | 3+n b | 4+n ]corchete
        col_regla = 2 + n
        col_b = 3 + n
        col_rbrk = 4 + n

        for j in range(n):
            enc = QLabel(f"x{j + 1}")
            enc.setObjectName("hint")
            enc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(enc, 0, 2 + j)
        enc_b = QLabel("b")
        enc_b.setObjectName("hint")
        enc_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._grid.addWidget(enc_b, 0, col_b)

        izq = QLabel()
        izq.setStyleSheet("border:3px solid #153653; border-right:none;"
                          " border-top-left-radius:3px; border-bottom-left-radius:3px;")
        izq.setFixedWidth(10)
        der = QLabel()
        der.setStyleSheet("border:3px solid #153653; border-left:none;"
                          " border-top-right-radius:3px; border-bottom-right-radius:3px;")
        der.setFixedWidth(10)
        self._grid.addWidget(izq, 1, 1, filas, 1)
        self._grid.addWidget(der, 1, col_rbrk, filas, 1)

        regla = QFrame()
        regla.setFrameShape(QFrame.Shape.VLine)
        regla.setStyleSheet("color:#9bd4e6;")
        self._grid.addWidget(regla, 1, col_regla, filas, 1)

        for i in range(filas):
            et_fila = QLabel(f"E{i + 1}")
            et_fila.setObjectName("hint")
            self._grid.addWidget(et_fila, i + 1, 0)
            for j in range(n + 1):
                indice = i * (n + 1) + j
                celda = QLabel(sesion.fmt(sesion.matriz[i][j]))
                celda.setAlignment(Qt.AlignmentFlag.AlignCenter)
                celda.setMinimumWidth(44)
                if resaltar is not None and indice == resaltar:
                    celda.setObjectName("celda_activa")
                    celda.setStyleSheet(
                        "#celda_activa{background:#fff3cf; border:2px solid #e0a400;"
                        " border-radius:6px; padding:2px 8px; font-weight:800;}")
                else:
                    celda.setStyleSheet("padding:2px 8px;")
                self._grid.addWidget(celda, i + 1, (2 + j) if j < n else col_b)


def matriz_widget(filas, sesion, col_barra=True):
    """Devuelve un widget con la matriz 'filas' bien compuesta: imagen si hay
    matplotlib (corchetes y fracciones de verdad), rejilla como alternativa."""
    n_sep = (len(filas[0]) - 1) if (col_barra and filas) else None
    pix = mathrender.matriz_a_pixmap(filas, col_barra=n_sep, modo=sesion.modo, fontsize=17)
    if pix is not None:
        lbl = QLabel()
        lbl.setPixmap(pix)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl
    # alternativa sin matplotlib
    tmp = _SesionVista(sesion, filas)
    grid = MatrizGrid()
    grid.poblar(tmp)
    return grid


class _SesionVista:
    """Adaptador mínimo para reutilizar MatrizGrid.poblar con una matriz dada."""

    def __init__(self, sesion, filas):
        self.n_eq = len(filas)
        self.n_var = len(filas[0]) - 1 if filas else 0
        self.matriz = filas
        self.modo = sesion.modo
        self.fmt = sesion.fmt


class BarraNavegacion(QWidget):
    """[← Atrás]      ...      [texto continuar →].  Enter activa 'Continuar'."""

    atras = pyqtSignal()
    continuar = pyqtSignal()

    def __init__(self, texto_continuar="Continuar  →", mostrar_atras=True, parent=None):
        super().__init__(parent)
        fila = QHBoxLayout(self)
        fila.setContentsMargins(0, 8, 0, 0)
        self.boton_atras = QPushButton("←  Atrás")
        self.boton_atras.setObjectName("secondary")
        self.boton_atras.clicked.connect(self.atras.emit)
        self.boton_atras.setVisible(mostrar_atras)
        self.boton_continuar = QPushButton(texto_continuar)
        self.boton_continuar.clicked.connect(self.continuar.emit)
        self.boton_continuar.setDefault(True)
        self.boton_continuar.setAutoDefault(True)
        fila.addWidget(self.boton_atras)
        fila.addStretch()
        fila.addWidget(self.boton_continuar)

    def set_continuar_habilitado(self, valor):
        self.boton_continuar.setEnabled(valor)

    def set_texto_continuar(self, texto):
        self.boton_continuar.setText(texto)