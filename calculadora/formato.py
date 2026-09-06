"""
formato.py

Capa de PRESENTACIÓN compartida por la consola (``main.py``), la interfaz
gráfica (``gui.py``) y una eventual TUI. No contiene lógica de álgebra: solo
transforma los números que produce ``gauss.py`` en texto legible.

Aporta dos cosas:

1. ``formatear_valor(v, modo)`` — muestra un ``float`` como **fracción exacta**
   (``1/3``, ``-8/3``, ``4``) cuando reconoce una fracción de denominador chico,
   y cae a decimal (``1.4142``) en caso contrario.
2. Helpers de **notación matemática**: subíndices Unicode (``x₁``), signos
   (``·``, ``−``) y fragmentos HTML (vector columna con corchetes, fracción
   apilada) para el rich-text de Qt.

Restricción del ejercicio: igual que ``gauss.py``, este módulo NO importa
``fractions`` ni ninguna otra librería; la conversión a fracción se hace a mano
con el algoritmo de fracciones continuas y el de Euclides.
"""

EPS = 1e-9

# Modos de presentación numérica admitidos.
MODO_FRACCION = "fraccion"
MODO_DECIMAL = "decimal"

# --- Entrada y presentación numérica (ver docs/ADR-0001) --------------------- #
# Sólo se muestran como fracción los valores cuyo denominador reducido no pasa de
# este tope (cubre los recíprocos "de a mano": /2 /3 /4 ... /64). Con denominador
# mayor se muestra el decimal.
MAX_DEN_DISPLAY = 64
# Los decimales que no encajan en una fracción tidy se redondean a esta precisión.
DECIMALES_ENTRADA = 4

_SUBINDICES = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "-": "₋",
}

# Signo menos "de verdad" (U+2212), más ancho y centrado que el guion ASCII.
MENOS = "−"
POR = "·"  # punto centrado para la multiplicación


def _casi_cero(valor):
    return -EPS < valor < EPS


def mcd(a, b):
    """Máximo común divisor por el algoritmo de Euclides (enteros no negativos)."""
    a, b = abs(int(a)), abs(int(b))
    while b:
        a, b = b, a % b
    return a


def a_fraccion(valor, max_den=10000, tol=1e-9):
    """
    Intenta expresar ``valor`` (float) como una fracción exacta ``num/den``.

    Usa la expansión en fracción continua: genera los convergentes sucesivos y
    se queda con el primero que aproxima ``valor`` dentro de ``tol`` sin que el
    denominador pase de ``max_den``.

    Devuelve ``(num, den)`` con ``den > 0`` y la fracción ya reducida, o
    ``None`` si no reconoce ninguna fracción razonable (p. ej. un irracional).
    """
    if valor != valor or valor in (float("inf"), float("-inf")):
        return None

    negativo = valor < 0
    x = abs(float(valor))

    h_prev, h_actual = 0, 1  # numeradores de los convergentes
    k_prev, k_actual = 1, 0  # denominadores
    resto = x

    for _ in range(64):
        entero = int(resto)
        h_prev, h_actual = h_actual, entero * h_actual + h_prev
        k_prev, k_actual = k_actual, entero * k_actual + k_prev

        if k_actual > max_den:
            h_actual, k_actual = h_prev, k_prev
            break
        if k_actual != 0 and abs(x - h_actual / k_actual) <= tol:
            break

        fraccionario = resto - entero
        if fraccionario <= tol:
            break
        resto = 1.0 / fraccionario

    if k_actual == 0 or abs(x - h_actual / k_actual) > tol:
        return None

    divisor = mcd(h_actual, k_actual) or 1
    num, den = h_actual // divisor, k_actual // divisor
    return (-num if negativo else num, den)


def formatear_valor(valor, modo=MODO_FRACCION, decimales=4):
    """
    Representación de ``valor`` como cadena.

      - ``modo="fraccion"`` (por defecto): ``"4"``, ``"1/3"``, ``"-8/3"`` cuando
        se reconoce una fracción; si no, decimal.
      - ``modo="decimal"``: entero si es (casi) entero; si no, ``decimales``
        cifras sin ceros de relleno.
    """
    if modo == MODO_FRACCION:
        fraccion = a_fraccion(valor, max_den=MAX_DEN_DISPLAY)
        if fraccion is not None:
            num, den = fraccion
            return str(num) if den == 1 else f"{num}/{den}"

    redondeado = round(valor)
    if _casi_cero(valor - redondeado):
        return str(int(redondeado))
    return f"{valor:.{decimales}f}".rstrip("0").rstrip(".")


def normalizar_entrada(valor):
    """
    Normaliza un número tecleado por el usuario para que la calculadora trate
    igual todas las formas de escribir la misma cantidad (ver docs/ADR-0001):

      - si está a menos de 1e-4 de una fracción de denominador <= MAX_DEN_DISPLAY
        (p. ej. 6.3333 ≈ 19/3, 0.333 ≈ 1/3), se ajusta a esa fracción exacta;
      - si no, se redondea a DECIMALES_ENTRADA decimales.
    """
    fraccion = a_fraccion(valor, max_den=MAX_DEN_DISPLAY, tol=1e-4)
    if fraccion is not None:
        return fraccion[0] / fraccion[1]
    return round(valor, DECIMALES_ENTRADA)


def formatear_display(valor, modo=MODO_FRACCION, decimales=4):
    """Como ``formatear_valor`` pero con el signo menos tipográfico (``−``)."""
    return formatear_valor(valor, modo, decimales).replace("-", MENOS)


def subindice(numero):
    """``1`` -> ``"₁"``. Acepta int o str; cae a los dígitos ASCII si hace falta."""
    return "".join(_SUBINDICES.get(caracter, caracter) for caracter in str(numero))


def var(indice, nombre="x"):
    """Nombre de variable con subíndice Unicode: ``var(1)`` -> ``"x₁"``."""
    return f"{nombre}{subindice(indice + 1)}"


def parametro(indice):
    """Parámetro libre con subíndice: ``parametro(0)`` -> ``"t₁"``."""
    return f"t{subindice(indice + 1)}"


# --------------------------------------------------------------------------- #
# Comprobación explícita: una fila = dict de verificar_solucion_detallada()
#   {"terminos": [(coef, x_j, producto), ...], "suma", "esperado", "coincide"}
# --------------------------------------------------------------------------- #

def _terminos_activos(fila):
    activos = [(c, xj, p) for (c, xj, p) in fila["terminos"] if not _casi_cero(c)]
    return activos or fila["terminos"][:1]


def texto_verificacion(indice, fila, modo=MODO_FRACCION):
    """Una ecuación de la comprobación en texto Unicode:
    ``E₁:  1·(5) + 1·(3) − 1·(2)  =  6  =  6``."""
    partes = []
    for k, (coef, xj, _p) in enumerate(_terminos_activos(fila)):
        if k == 0:
            encabezado = formatear_display(coef, modo)
        else:
            encabezado = f"+ {formatear_display(abs(coef), modo)}" if coef >= 0 \
                else f"{MENOS} {formatear_display(abs(coef), modo)}"
        partes.append(f"{encabezado}{POR}({formatear_display(xj, modo)})")
    rel = "=" if fila["coincide"] else "≠"
    return (f"{var(indice, 'E')}:  " + " ".join(partes)
            + f"  =  {formatear_display(fila['suma'], modo)}"
            + f"  {rel}  {formatear_display(fila['esperado'], modo)}")


def latex_verificacion(indice, fila, modo=MODO_FRACCION):
    """La misma ecuación en LaTeX (para render con mathtext)."""
    partes = []
    for k, (coef, xj, _p) in enumerate(_terminos_activos(fila)):
        signo = "" if k == 0 else ("+ " if coef >= 0 else "- ")
        c = latex_valor(abs(coef) if k else coef, modo)
        partes.append(rf"{signo}{c} \cdot ({latex_valor(xj, modo)})")
    rel = "=" if fila["coincide"] else r"\neq"
    return (rf"\mathrm{{E}}_{{{indice + 1}}}:\;\; " + " ".join(partes)
            + rf" \;=\; {latex_valor(fila['suma'], modo)}"
            + rf" \;{rel}\; {latex_valor(fila['esperado'], modo)}")


# --------------------------------------------------------------------------- #
# Fragmentos HTML para el rich-text de Qt (QLabel / QTextEdit)
# --------------------------------------------------------------------------- #

def _escapar(texto):
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def valor_html(valor, modo=MODO_FRACCION):
    """
    Un número como HTML. Si es una fracción propia, la apila (numerador sobre
    denominador con una regla); si no, texto llano con el menos tipográfico.
    """
    if modo == MODO_FRACCION:
        fraccion = a_fraccion(valor, max_den=MAX_DEN_DISPLAY)
        if fraccion is not None and fraccion[1] != 1:
            num, den = fraccion
            signo = MENOS if num < 0 else ""
            return (
                f'<span style="white-space:nowrap;">{signo}'
                f'<span style="display:inline-block; text-align:center; vertical-align:middle;">'
                f'<span style="display:block; border-bottom:1px solid #153653; padding:0 2px;">{abs(num)}</span>'
                f'<span style="display:block; padding:0 2px;">{den}</span>'
                f'</span></span>'
            )
    return _escapar(formatear_display(valor, modo))


def matriz_html(matriz, n_incognitas, modo=MODO_FRACCION, resaltar_columna_b=True):
    """
    La matriz aumentada [A | b] como una tabla HTML con corchetes a los lados y
    una regla vertical antes de la columna de términos independientes.
    """
    filas_html = []
    for fila in matriz:
        celdas = []
        for columna, valor in enumerate(fila):
            estilo = "padding:3px 10px; text-align:center;"
            if resaltar_columna_b and columna == n_incognitas:
                estilo += " border-left:2px solid #153653;"
            celdas.append(f'<td style="{estilo}">{valor_html(valor, modo)}</td>')
        filas_html.append(f"<tr>{''.join(celdas)}</tr>")
    cuerpo = "".join(filas_html)
    return (
        '<table cellspacing="0" cellpadding="0" style="border-collapse:collapse;'
        ' border-left:2px solid #153653; border-right:2px solid #153653;">'
        f"{cuerpo}</table>"
    )


def latex_valor(valor, modo=MODO_FRACCION):
    """Un número como LaTeX: ``\\frac{a}{b}`` si es fracción propia, si no el literal."""
    if modo == MODO_FRACCION:
        fraccion = a_fraccion(valor, max_den=MAX_DEN_DISPLAY)
        if fraccion is not None:
            num, den = fraccion
            if den == 1:
                return str(num)
            if num < 0:
                return f"-\\frac{{{abs(num)}}}{{{den}}}"
            return f"\\frac{{{num}}}{{{den}}}"
    return formatear_valor(valor, MODO_DECIMAL)


def latex_pmatrix(componentes, modo=MODO_FRACCION):
    """Un vector/columna como ``\\begin{pmatrix} … \\end{pmatrix}`` de LaTeX."""
    cuerpo = " \\\\ ".join(latex_valor(v, modo) for v in componentes)
    return f"\\begin{{pmatrix}} {cuerpo} \\end{{pmatrix}}"


def generar_latex_solucion(n_incognitas, libres, expresiones, particular,
                           vectores_nulos, modo=MODO_FRACCION):
    """
    Código LaTeX de la solución general vectorial x = x_p + Σ tₖ vₖ.

    Los valores se emiten como fracciones exactas (``\\frac``) cuando se
    reconocen; ``modo="decimal"`` fuerza la representación decimal.
    """
    lineas = [
        "\\text{Solución particular (variables libres } = 0\\text{):}\\\\",
        f"\\mathbf{{x_p}} = {latex_pmatrix(particular, modo)}\\\\\\\\",
    ]

    if vectores_nulos:
        lineas.append("\\text{Vectores del espacio nulo (base):}\\\\")
        for k, vec in enumerate(vectores_nulos):
            separador = ", \\quad " if k < len(vectores_nulos) - 1 else ""
            lineas.append(
                f"\\mathbf{{v_{{{k + 1}}}}} = {latex_pmatrix(vec, modo)}{separador}\\\\"
            )
        lineas.append("\\\\")
        lineas.append("\\text{Solución general:}\\\\")
        params = " + ".join(f"t_{{{k + 1}}} \\mathbf{{v_{{{k + 1}}}}}"
                            for k in range(len(vectores_nulos)))
        lineas.append(f"\\mathbf{{x}} = \\mathbf{{x_p}} + {params}")

    return "".join(lineas)


def vector_columna_html(componentes, modo=MODO_FRACCION):
    """Un vector como columna entre corchetes."""
    filas = "".join(
        f'<tr><td style="padding:2px 10px; text-align:center;">{valor_html(v, modo)}</td></tr>'
        for v in componentes
    )
    return (
        '<table cellspacing="0" cellpadding="0" style="border-collapse:collapse; display:inline-table;'
        ' vertical-align:middle; border-left:2px solid #153653; border-right:2px solid #153653;">'
        f"{filas}</table>"
    )
def subindice(numero):
    """'12' -> '₁₂'. Acepta int o str y convierte cada dígito a su variante Unicode."""
    return "".join(_SUBINDICES.get(caracter, caracter) for caracter in str(numero))

def var(indice, nombre="x"):
    """Nombre de variable con subíndice Unicode: var(0) -> 'x₁'."""
    return f"{nombre}{subindice(indice + 1)}"

def parametro(indice, nombre="t"):
    """Parámetro libre con subíndice Unicode: parametro(0) -> 't₁'."""
    return f"{nombre}{subindice(indice + 1)}"

def matriz_elem(fila, columna, nombre="a"):
    """Elemento de matriz con subíndices: matriz_elem(0, 1) -> 'a₁₂'."""
    return f"{nombre}{subindice(str(fila + 1) + str(columna + 1))}"