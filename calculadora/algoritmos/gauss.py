"""
gauss.py

Implementación "a mano" del método de eliminación de Gauss (reducción por
filas / forma escalonada) para resolver sistemas de ecuaciones lineales
Ax = b.

Este módulo contiene la lógica para alcanzar la Forma Escalonada por Filas (REF).
La lógica para la Forma Escalonada Reducida (RREF) y la clasificación
de columnas pivote se encuentra en gauss_jordan.py.
"""

EPS = 1e-9

def valor_casi_cero(valor):
    """Indica si 'valor' debe tratarse como cero dada la tolerancia EPS."""
    return -EPS < valor < EPS

def crear_matriz_aumentada(coeficientes, terminos_independientes):
    """Construye la matriz aumentada [A | b]."""
    aumentada = []
    for i in range(len(coeficientes)):
        fila = list(coeficientes[i]) + [terminos_independientes[i]]
        aumentada.append(fila)
    return aumentada

def copiar_matriz(matriz):
    """Devuelve una copia independiente (deep copy manual) de la matriz."""
    return [list(fila) for fila in matriz]

def intercambiar_filas(matriz, i, j):
    """Intercambia dos filas de la matriz, in place."""
    matriz[i], matriz[j] = matriz[j], matriz[i]

def _formato_por_defecto(valor):
    """Formato simple para los multiplicadores en las descripciones de pasos."""
    return f"{valor:.4g}"

def escalonar(matriz, n_incognitas, registrar_paso=None, formato_numero=None):
    """Reduce la matriz a forma escalonada por filas (REF) con pivoteo parcial."""
    fmt = formato_numero or _formato_por_defecto
    m = len(matriz)
    columnas_pivote = []
    fila_actual = 0

    for col in range(n_incognitas):
        if fila_actual >= m:
            break

        fila_max = fila_actual
        valor_max = abs(matriz[fila_actual][col])
        for r in range(fila_actual + 1, m):
            if abs(matriz[r][col]) > valor_max:
                valor_max = abs(matriz[r][col])
                fila_max = r

        if valor_casi_cero(valor_max):
            continue

        if fila_max != fila_actual:
            intercambiar_filas(matriz, fila_actual, fila_max)
            if registrar_paso:
                registrar_paso(
                    f"F{fila_actual + 1} <-> F{fila_max + 1} (pivoteo parcial)",
                    matriz,
                )

        pivote = matriz[fila_actual][col]
        for r in range(fila_actual + 1, m):
            if valor_casi_cero(matriz[r][col]):
                continue
            factor = matriz[r][col] / pivote
            for c in range(col, n_incognitas + 1):
                matriz[r][c] -= factor * matriz[fila_actual][c]
            matriz[r][col] = 0.0
            if registrar_paso:
                registrar_paso(
                    f"F{r + 1} <- F{r + 1} - ({fmt(factor)}) * F{fila_actual + 1}",
                    matriz,
                )

        columnas_pivote.append(col)
        fila_actual += 1

    return columnas_pivote

def clasificar(matriz, n_incognitas, columnas_pivote):
    """Clasifica el sistema ya reducido a forma escalonada."""
    for fila in matriz:
        coeficientes_cero = all(valor_casi_cero(v) for v in fila[:n_incognitas])
        termino_no_cero = not valor_casi_cero(fila[n_incognitas])
        if coeficientes_cero and termino_no_cero:
            return "incompatible"

    rango = len(columnas_pivote)
    if rango == n_incognitas:
        return "determinado"
    return "indeterminado"

def sustitucion_regresiva(matriz, n_incognitas, columnas_pivote):
    """Calcula la solución única x = [x1, ..., xn] por sustitución hacia atrás."""
    x = [0.0] * n_incognitas
    for i in range(len(columnas_pivote) - 1, -1, -1):
        col = columnas_pivote[i]
        suma = matriz[i][n_incognitas]
        for j in range(col + 1, n_incognitas):
            suma -= matriz[i][j] * x[j]
        x[col] = suma / matriz[i][col]
    return x

def verificar_solucion_detallada(coeficientes, terminos_independientes, x):
    resultados = []
    for fila, b_i in zip(coeficientes, terminos_independientes):
        terminos = []
        suma = 0.0
        for coef, xj in zip(fila, x):
            producto = coef * xj
            suma += producto
            terminos.append((coef, xj, producto))
        resultados.append({
            "terminos": terminos,
            "suma": suma,
            "esperado": b_i,
            "coincide": valor_casi_cero(suma - b_i),
        })
    return resultados

def verificar_solucion(coeficientes, terminos_independientes, x):
    return [
        (r["suma"], r["esperado"], r["coincide"])
        for r in verificar_solucion_detallada(coeficientes, terminos_independientes, x)
    ]

def rango_matriz(matriz, n_incognitas):
    rango = 0
    for fila in matriz:
        tiene_pivote = any(not valor_casi_cero(fila[col]) for col in range(n_incognitas))
        if tiene_pivote:
            rango += 1
    return rango

def verificar_rango_nulidad(matriz, n_incognitas, columnas_pivote):
    rango = len(columnas_pivote)
    nulidad = n_incognitas - rango
    suma = rango + nulidad
    return {
        "rango": rango,
        "nulidad": nulidad,
        "suma": suma,
        "es_valido": suma == n_incognitas
    }

def es_forma_escalonada(matriz, n_incognitas, columnas_pivote):
    if not columnas_pivote:
        return all(all(valor_casi_cero(v) for v in fila[:n_incognitas]) for fila in matriz)

    num_filas_nulas = sum(1 for fila in matriz if all(valor_casi_cero(v) for v in fila[:n_incognitas]))
    num_filas_no_nulas = len(matriz) - num_filas_nulas

    if num_filas_no_nulas != len(columnas_pivote):
        return False

    primera_fila_nula = -1
    for i, fila in enumerate(matriz):
        es_nula = all(valor_casi_cero(v) for v in fila[:n_incognitas])
        if es_nula and primera_fila_nula == -1:
            primera_fila_nula = i
        elif not es_nula and primera_fila_nula != -1:
            return False

    for i in range(len(columnas_pivote)):
        if i > 0 and columnas_pivote[i] <= columnas_pivote[i - 1]:
            return False
        if valor_casi_cero(matriz[i][columnas_pivote[i]]):
            return False

    return True