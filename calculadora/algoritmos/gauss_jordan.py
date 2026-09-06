"""
gauss_jordan.py

Módulo 2: Reducción a RREF (Gauss-Jordan) e identificación de columnas pivote.
Contiene la lógica para llevar una matriz de REF a RREF y extraer
las soluciones paramétricas y vectoriales.
"""

from calculadora.algoritmos.gauss import (
    valor_casi_cero,
    _formato_por_defecto,
    es_forma_escalonada
)

def reducir_a_escalonada_reducida(matriz, n_incognitas, columnas_pivote,
                                  registrar_paso=None, formato_numero=None):
    """A partir de una matriz REF, la lleva a RREF (Gauss-Jordan)."""
    fmt = formato_numero or _formato_por_defecto
    for i in range(len(columnas_pivote) - 1, -1, -1):
        col = columnas_pivote[i]
        pivote = matriz[i][col]
        if not valor_casi_cero(pivote - 1.0):
            for c in range(col, n_incognitas + 1):
                matriz[i][c] /= pivote
            if registrar_paso:
                registrar_paso(f"F{i + 1} <- F{i + 1} / {fmt(pivote)}", matriz)

        for r in range(i):
            factor = matriz[r][col]
            if valor_casi_cero(factor):
                continue
            for c in range(col, n_incognitas + 1):
                matriz[r][c] -= factor * matriz[i][c]
            matriz[r][col] = 0.0
            if registrar_paso:
                registrar_paso(
                    f"F{r + 1} <- F{r + 1} - ({fmt(factor)}) * F{i + 1}",
                    matriz,
                )

def es_forma_escalonada_reducida(matriz, n_incognitas, columnas_pivote):
    if not es_forma_escalonada(matriz, n_incognitas, columnas_pivote):
        return False

    for i, col in enumerate(columnas_pivote):
        if not valor_casi_cero(matriz[i][col] - 1.0):
            return False
        for j in range(len(matriz)):
            if i != j and not valor_casi_cero(matriz[j][col]):
                return False
    return True

def clasificar_forma_escalonada(matriz, n_incognitas, columnas_pivote):
    if es_forma_escalonada_reducida(matriz, n_incognitas, columnas_pivote):
        return "RREF"
    elif es_forma_escalonada(matriz, n_incognitas, columnas_pivote):
        return "REF"
    else:
        return "ninguna"

def solucion_parametrica(matriz, n_incognitas, columnas_pivote):
    libres = [v for v in range(n_incognitas) if v not in columnas_pivote]
    expresiones = [None] * n_incognitas

    for i, col in enumerate(columnas_pivote):
        termino_independiente = matriz[i][n_incognitas]
        partes = []
        for v in libres:
            coef = matriz[i][v]
            if not valor_casi_cero(coef):
                partes.append((-coef, v))
        expresiones[col] = (termino_independiente, partes)

    return libres, expresiones

def evaluar_solucion_parametrica(n_incognitas, libres, expresiones, valores_libres):
    x = [0.0] * n_incognitas
    for indice_libre, valor in zip(libres, valores_libres):
        x[indice_libre] = valor

    for v in range(n_incognitas):
        if expresiones[v] is None:
            continue
        termino_independiente, partes = expresiones[v]
        valor = termino_independiente
        for coef, indice_libre in partes:
            valor += coef * x[indice_libre]
        x[v] = valor
    return x

def solucion_general_vectorial(matriz, n_incognitas, columnas_pivote, libres, expresiones):
    particular = evaluar_solucion_parametrica(n_incognitas, libres, expresiones, [0] * len(libres))
    vectores_nulos = []
    for k, indice_libre in enumerate(libres):
        vec = [0.0] * n_incognitas
        vec[indice_libre] = 1.0
        valores_libres_temp = [0.0] * len(libres)
        valores_libres_temp[k] = 1.0
        x_temp = evaluar_solucion_parametrica(n_incognitas, libres, expresiones, valores_libres_temp)
        for i in range(n_incognitas):
            vec[i] = x_temp[i] - particular[i]
        vectores_nulos.append(vec)

    return {
        "particular": particular,
        "vectores_nulos": vectores_nulos,
        "variables_libres": libres,
        "expresion_str": _construir_expresion_string(particular, vectores_nulos, libres)
    }

def _construir_expresion_string(particular, vectores_nulos, variables_libres):
    if not variables_libres:
        return f"x = {particular}"
    parts = [f"x = {particular}"]
    for k, (vec, var_idx) in enumerate(zip(vectores_nulos, variables_libres)):
        parts.append(f" + t{k + 1} * {vec}")
    return "".join(parts)