"""
main.py

Programa interactivo que resuelve sistemas de ecuaciones lineales Ax = b
usando el método de eliminación de Gauss (reducción por filas), muestra
cada paso del proceso y clasifica el sistema según sus soluciones:

  - Consistente determinado   -> solución única.
  - Consistente indeterminado -> infinitas soluciones (solución paramétrica).
  - Inconsistente             -> sin solución.

Toda la lógica del algoritmo vive en gauss.py (sin input/print). Este
archivo solo se encarga de la interacción con el usuario por consola.

Uso:
    python3 main.py                 # valores como fracción exacta (por defecto)
    python3 main.py --decimal       # valores en decimal
"""

import sys

from calculadora.algoritmos.gauss import (
    clasificar,
    copiar_matriz,
    crear_matriz_aumentada,
    escalonar,
    rango_matriz,
    sustitucion_regresiva,
    valor_casi_cero,
    verificar_rango_nulidad,
    verificar_solucion_detallada,
)
from calculadora.algoritmos.gauss_jordan import  (
    clasificar_forma_escalonada,
    evaluar_solucion_parametrica,
    reducir_a_escalonada_reducida,
    solucion_general_vectorial,
    solucion_parametrica,
)
from formato import (
    MODO_DECIMAL,
    MODO_FRACCION,
    formatear_valor,
    generar_latex_solucion,
)

# Modo de presentación numérica; se ajusta según los argumentos de línea de
# comandos en main(). Fracción exacta por defecto (más legible para álgebra).
MODO = MODO_FRACCION


def pedir_entero(mensaje, minimo=1):
    """Pide un entero >= minimo por consola, repitiendo hasta que sea válido."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print("  Por favor ingresa un número entero válido.")
            continue
        if valor < minimo:
            print(f"  Debe ser un entero mayor o igual a {minimo}.")
            continue
        return valor


def pedir_flotante(mensaje):
    """Pide un número (entero o decimal) por consola, repitiendo hasta que sea válido."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            return float(texto)
        except ValueError:
            print("  Por favor ingresa un número válido (usa punto decimal, ej: 3.5).")


def leer_sistema():
    """Lee interactivamente el número de ecuaciones/incógnitas y la matriz aumentada."""
    print("=== Resolución de sistemas de ecuaciones lineales Ax = b ===")
    print("Método: eliminación de Gauss (reducción a forma escalonada)\n")

    m = pedir_entero("Número de ecuaciones (filas): ")
    n = pedir_entero("Número de incógnitas (columnas de A): ")

    coeficientes = []
    terminos = []
    print("\nIngresa los coeficientes de cada ecuación y su término independiente.")
    for i in range(m):
        print(f"\n-- Ecuación {i + 1} --")
        fila = []
        for j in range(n):
            fila.append(pedir_flotante(f"  Coeficiente de x{j + 1}: "))
        b = pedir_flotante(f"  Término independiente (b{i + 1}): ")
        coeficientes.append(fila)
        terminos.append(b)

    return coeficientes, terminos, m, n


def formatear_numero(valor):
    """Formatea un valor según el MODO activo (fracción exacta o decimal)."""
    return formatear_valor(valor, MODO)


def imprimir_matriz(matriz, n_incognitas, titulo=None):
    """Imprime la matriz aumentada [A | b] de forma legible."""
    if titulo:
        print(titulo)
    for fila in matriz:
        coeficientes_str = "  ".join(
            f"{formatear_numero(v):>8}" for v in fila[:n_incognitas]
        )
        termino_str = formatear_numero(fila[n_incognitas])
        print(f"[ {coeficientes_str}  |  {termino_str:>8} ]")


def _con_signo(texto, es_primero):
    """Antepone ' + ' / ' - ' a un valor ya formateado, para encadenar términos."""
    negativo = texto.startswith("-")
    cuerpo = texto[1:] if negativo else texto
    if es_primero:
        return f"-{cuerpo}" if negativo else cuerpo
    return f" - {cuerpo}" if negativo else f" + {cuerpo}"


def _linea_sustitucion(terminos):
    """
    A partir de [(coef, x_j, producto), ...] arma las dos partes de la
    demostración:  '2·(5) + 1·(-3)'   y   '10 - 3'.
    Omite los términos con coeficiente 0 (no aportan nada a la suma).
    """
    activos = [(c, xj, p) for (c, xj, p) in terminos if not valor_casi_cero(c)]
    if not activos:
        activos = terminos[:1]  # todos los coeficientes eran 0: mostrar 0·(x)
    factores = ""
    productos = ""
    for indice, (coef, xj, producto) in enumerate(activos):
        primero = indice == 0
        factores += _con_signo(f"{formatear_numero(coef)}·({formatear_numero(xj)})", primero)
        productos += _con_signo(formatear_numero(producto), primero)
    return factores, productos


def imprimir_verificacion(coeficientes, terminos, x, titulo="Verificación (sustituyendo en el sistema original)"):
    """
    Sustituye 'x' en el sistema original [coeficientes | terminos] y muestra,
    ecuación por ecuación, la DEMOSTRACIÓN completa: los factores coef·(x_j),
    la suma de los productos y la comparación con el término independiente.
    """
    print(f"\n--- {titulo} ---")
    resultados = verificar_solucion_detallada(coeficientes, terminos, x)
    todo_coincide = True
    for i, resultado in enumerate(resultados):
        factores, productos = _linea_sustitucion(resultado["terminos"])
        suma = formatear_numero(resultado["suma"])
        esperado = formatear_numero(resultado["esperado"])
        coincide = resultado["coincide"]
        if not coincide:
            todo_coincide = False
        simbolo = "=" if coincide else "≠"
        estado = "OK" if coincide else "NO coincide"
        print(f"  Ecuación {i + 1}:")
        print(f"    {factores}")
        if productos != suma:
            print(f"    = {productos}")
        print(f"    = {suma} {simbolo} {esperado} (b{i + 1})  ->  {estado}")
    if todo_coincide:
        print("La solución satisface todas las ecuaciones del sistema original.")
    else:
        print("ADVERTENCIA: la solución NO satisface todas las ecuaciones.")


def resolver_sistema(coeficientes, terminos, n):
    """Ejecuta el flujo completo (escalonar, clasificar, mostrar) para un sistema dado."""
    matriz = crear_matriz_aumentada(coeficientes, terminos)
    imprimir_matriz(matriz, n, "\nMatriz aumentada [A | b] inicial:")

    pasos = []

    def registrar(descripcion, matriz_actual):
        pasos.append((descripcion, copiar_matriz(matriz_actual)))

    print("\n--- Proceso de eliminación (reducción por filas) ---")
    columnas_pivote = escalonar(matriz, n, registrar_paso=registrar,
                                formato_numero=formatear_numero)

    if not pasos:
        print("(La matriz ya estaba en forma escalonada, no hizo falta ninguna operación.)")
    for descripcion, matriz_paso in pasos:
        imprimir_matriz(matriz_paso, n, f"\nPaso: {descripcion}")

    imprimir_matriz(matriz, n, "\nForma escalonada final:")

    tipo = clasificar(matriz, n, columnas_pivote)

    # Información sobre rango, nulidad y forma escalonada
    rango = rango_matriz(matriz, n)
    info_rango_nulidad = verificar_rango_nulidad(matriz, n, columnas_pivote)
    forma_esc = clasificar_forma_escalonada(matriz, n, columnas_pivote)

    print("\n--- Análisis de la matriz ---")
    print(f"Rango(A): {rango}")
    print(f"Nulidad(A) (variables libres): {info_rango_nulidad['nulidad']}")
    print(f"Verificación rango-nulidad: {rango} + {info_rango_nulidad['nulidad']} = {info_rango_nulidad['suma']} (esperado: {n})")
    print(f"Forma escalonada: {forma_esc}")

    print("\n--- Clasificación del sistema ---")
    if tipo == "incompatible":
        print("Sistema INCONSISTENTE: no tiene solución.")
        print("(Una fila quedó de la forma 0 = c, con c distinto de 0.)")

    elif tipo == "determinado":
        print("Sistema CONSISTENTE DETERMINADO: tiene solución única.")
        x = sustitucion_regresiva(matriz, n, columnas_pivote)
        print("\nSolución:")
        for j in range(n):
            print(f"  x{j + 1} = {formatear_numero(x[j])}")

        imprimir_verificacion(coeficientes, terminos, x)

    else:
        print("Sistema CONSISTENTE INDETERMINADO: tiene infinitas soluciones.")

        pasos_rref = []

        def registrar_rref(descripcion, matriz_actual):
            pasos_rref.append((descripcion, copiar_matriz(matriz_actual)))

        print("\n--- Reducción adicional a forma escalonada reducida ---")
        print("(para expresar la solución en función de las variables libres)")
        reducir_a_escalonada_reducida(matriz, n, columnas_pivote,
                                      registrar_paso=registrar_rref,
                                      formato_numero=formatear_numero)
        for descripcion, matriz_paso in pasos_rref:
            imprimir_matriz(matriz_paso, n, f"\nPaso: {descripcion}")

        libres, expresiones = solucion_parametrica(matriz, n, columnas_pivote)

        nombres_libres = [f"x{v + 1}" for v in libres]
        print("\nVariables libres (parámetros):", ", ".join(nombres_libres))

        print("\nSolución paramétrica:")
        for v in range(n):
            if v in libres:
                indice_parametro = libres.index(v) + 1
                print(f"  x{v + 1} = t{indice_parametro}   (variable libre)")
            else:
                termino, partes = expresiones[v]
                texto = formatear_numero(termino)
                for coef, indice_libre in partes:
                    signo = "+" if coef >= 0 else "-"
                    indice_parametro = libres.index(indice_libre) + 1
                    texto += f" {signo} {formatear_numero(abs(coef))}*t{indice_parametro}"
                print(f"  x{v + 1} = {texto}")

        # Solución vectorial
        print("\n--- Solución general vectorial ---")
        solucion_vec = solucion_general_vectorial(matriz, n, columnas_pivote, libres, expresiones)
        print("x = xp + t1*v1 + t2*v2 + ... + tk*vk")
        print("\nDonde:")
        print("xp (solución particular) =", [f"{formatear_numero(v)}" for v in solucion_vec["particular"]])
        for k, vec in enumerate(solucion_vec["vectores_nulos"]):
            print(f"v{k + 1} =", [f"{formatear_numero(v)}" for v in vec])

        # LaTeX de la solución
        print("\n--- Código LaTeX (para copiar) ---")
        latex_code = generar_latex_solucion(n, libres, expresiones,
                                            solucion_vec["particular"],
                                            solucion_vec["vectores_nulos"], MODO)
        print(latex_code)

        valores_ejemplo = [0.0] * len(libres)
        x_ejemplo = evaluar_solucion_parametrica(n, libres, expresiones, valores_ejemplo)
        asignaciones = ", ".join(
            f"t{k + 1} = {formatear_numero(v)}" for k, v in enumerate(valores_ejemplo)
        )
        titulo = f"Verificación con un ejemplo concreto ({asignaciones})"
        imprimir_verificacion(coeficientes, terminos, x_ejemplo, titulo)


def main():
    global MODO
    if "--decimal" in sys.argv:
        MODO = MODO_DECIMAL
    elif "--fraccion" in sys.argv:
        MODO = MODO_FRACCION
    etiqueta = "decimal" if MODO == MODO_DECIMAL else "fracción exacta"
    print(f"(Los valores se muestran en {etiqueta}; usa --decimal o --fraccion para cambiar.)\n")

    while True:
        coeficientes, terminos, m, n = leer_sistema()
        resolver_sistema(coeficientes, terminos, n)

        respuesta = input("\n¿Deseas resolver otro sistema? (s/n): ").strip().lower()
        if respuesta != "s":
            print("¡Hasta luego!")
            break


if __name__ == "__main__":
    main()