"""
mathrender.py

Renderiza expresiones matemáticas a imágenes (``QPixmap``) usando el motor
*mathtext* de Matplotlib. Es *presentación* para la GUI: convierte el LaTeX que
produce ``formato.py`` en algo que se ve como en un libro (barras de fracción de
verdad, subíndices, espaciado matemático), en lugar de texto plano.

matplotlib.mathtext NO soporta los entornos ``pmatrix`` / ``array``; por eso los
vectores columna se dibujan a mano (un ``Axes`` con los elementos y los corchetes
como líneas).

Si Matplotlib no está instalado, ``disponible()`` devuelve ``False`` y la GUI cae
a su representación con rich-text de Qt.
"""

import re

try:  # matplotlib es opcional: la GUI funciona sin él (con menos belleza).
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    _DISPONIBLE = True
except Exception:  # pragma: no cover - depende del entorno
    _DISPONIBLE = False

from PyQt6.QtGui import QImage, QPixmap

from formato import MODO_FRACCION, latex_valor

# Color del texto matemático (coincide con el color de texto de la GUI).
COLOR_TEXTO = "#153653"


def disponible():
    """True si se puede renderizar con Matplotlib."""
    return _DISPONIBLE


def _fig_a_pixmap(fig, escala):
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    ancho, alto = canvas.get_width_height()
    imagen = QImage(bytes(canvas.buffer_rgba()), ancho, alto,
                    QImage.Format.Format_RGBA8888).copy()
    pixmap = QPixmap.fromImage(imagen)
    pixmap.setDevicePixelRatio(float(escala))  # nítido en pantallas HiDPI
    return pixmap


def latex_a_pixmap(expr, fontsize=15, color=COLOR_TEXTO, escala=2, pad=6):
    """
    Renderiza una expresión matemática de una sola línea (sin ``\\\\`` ni
    matrices). 'expr' va sin los ``$`` delimitadores.
    """
    if not _DISPONIBLE:
        return None
    dpi = 100 * escala
    fig = Figure(dpi=dpi)
    fig.patch.set_alpha(0.0)
    texto = fig.text(0.5, 0.5, f"${expr}$", fontsize=fontsize, color=color,
                     ha="center", va="center")
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    caja = texto.get_window_extent(canvas.get_renderer())
    fig.set_size_inches((caja.width + 2 * pad) / dpi, (caja.height + 2 * pad) / dpi)
    return _fig_a_pixmap(fig, escala)


def _ancho_token(token):
    """Ancho aproximado (en caracteres) de un valor ya pasado por latex_valor."""
    if "\\frac" in token:
        partes = re.findall(r"\{([^{}]*)\}", token)
        base = max((len(p) for p in partes), default=1)
        return base + (1 if token.startswith("-") else 0)
    return len(token)


def columna_a_pixmap(componentes, modo=MODO_FRACCION, fontsize=15,
                     color=COLOR_TEXTO, escala=2):
    """Un vector columna entre corchetes, dibujado elemento a elemento."""
    if not _DISPONIBLE:
        return None
    n = len(componentes)
    tokens = [latex_valor(v, modo) for v in componentes]
    dpi = 100 * escala
    fig = Figure(dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)

    for i, token in enumerate(tokens):
        ax.text(0.5, n - i - 0.5, f"${token}$", ha="center", va="center",
                fontsize=fontsize, color=color)

    grosor = max(1.2, fontsize / 11.0)
    oreja = 0.12
    for x0, direccion in ((0.055, 1), (0.945, -1)):
        ax.plot([x0, x0], [0.06, n - 0.06], color=color, lw=grosor,
                solid_capstyle="round")
        ax.plot([x0, x0 + direccion * oreja], [0.06, 0.06], color=color, lw=grosor)
        ax.plot([x0, x0 + direccion * oreja], [n - 0.06, n - 0.06], color=color,
                lw=grosor)

    hay_fraccion = any("\\frac" in t for t in tokens)
    alto_fila = fontsize * (1.95 if hay_fraccion else 1.5) / 72.0
    ancho_max = max((_ancho_token(t) for t in tokens), default=1)
    ancho_pulg = max(0.5, 0.135 * ancho_max + 0.44)
    alto_pulg = alto_fila * n + 0.12
    fig.set_size_inches(ancho_pulg, alto_pulg)
    return _fig_a_pixmap(fig, escala)


def matriz_a_pixmap(filas, col_barra=None, modo=MODO_FRACCION, fontsize=15,
                    color=COLOR_TEXTO, escala=2):
    """
    Una matriz entre corchetes. 'col_barra' (int) dibuja una regla vertical
    fina antes de esa columna (para separar A | b en la matriz aumentada).
    """
    if not _DISPONIBLE or not filas:
        return None
    n = len(filas)
    ncols = len(filas[0])
    tokens = [[latex_valor(v, modo) for v in fila] for fila in filas]
    dpi = 100 * escala
    fig = Figure(dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, n)

    for i, fila in enumerate(tokens):
        for j, token in enumerate(fila):
            ax.text(j + 0.5, n - i - 0.5, f"${token}$", ha="center", va="center",
                    fontsize=fontsize, color=color)

    grosor = max(1.2, fontsize / 11.0)
    oreja = 0.14
    for x0, direccion in ((0.06, 1), (ncols - 0.06, -1)):
        ax.plot([x0, x0], [0.06, n - 0.06], color=color, lw=grosor,
                solid_capstyle="round")
        ax.plot([x0, x0 + direccion * oreja], [0.06, 0.06], color=color, lw=grosor)
        ax.plot([x0, x0 + direccion * oreja], [n - 0.06, n - 0.06], color=color,
                lw=grosor)
    if col_barra is not None and 0 < col_barra < ncols:
        ax.plot([col_barra, col_barra], [0.1, n - 0.1], color=color,
                lw=max(1.0, grosor * 0.7), linestyle=(0, (1, 1)))

    hay_fraccion = any("\\frac" in t for fila in tokens for t in fila)
    alto_fila = fontsize * (2.0 if hay_fraccion else 1.55) / 72.0
    ancho_col = []
    for j in range(ncols):
        ancho_col.append(max(_ancho_token(tokens[i][j]) for i in range(n)))
    ancho_pulg = 0.5 + sum(0.115 * a + 0.34 for a in ancho_col)
    alto_pulg = alto_fila * n + 0.14
    fig.set_size_inches(ancho_pulg, alto_pulg)
    return _fig_a_pixmap(fig, escala)