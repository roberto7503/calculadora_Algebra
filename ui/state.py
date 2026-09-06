"""Estado compartido entre pantallas: dimensiones, notación, matriz y resultado."""

from calculadora.algoritmos.vectores import (
    combinacion_lineal
)
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
from calculadora.algoritmos.gauss_jordan import (
    clasificar_forma_escalonada,
    evaluar_solucion_parametrica,
    reducir_a_escalonada_reducida,
    solucion_general_vectorial,
    solucion_parametrica,
)
from calculadora.formato import (
    MODO_FRACCION,
    formatear_valor,
    generar_latex_solucion,
    latex_pmatrix,
    matriz_elem,       # NUEVO
    subindice          # NUEVO
)



EJEMPLOS = {
    "Solución única": [[1, 1, 1, 6], [0, 2, 5, -4], [2, 5, -1, 27]],
    "Variables libres": [[1, 1, 1, 6], [2, 2, 2, 12], [1, -1, 0, 0]],
    "Sistema inconsistente": [[1, 1, 2], [1, 1, 5]],
}


class Sesion:
    """Contenedor mutable con todo lo que las pantallas necesitan compartir."""

    def __init__(self):
        self.n_eq = 3
        self.n_var = 3
        self.modo = MODO_FRACCION
        self.metodo = "gauss" # NUEVO: Valor por defecto
        self.matriz = self._matriz_ceros(3, 3)
        self.resultado = None  # dict tras resolver(), o None
        self.origen = "manual"  # "manual" (flujo completo) | "ejemplo" (salta a proceso)

    def calcular_combinacion_lineal(self, vectores, escalares):
        """Calcula c1*v1 + ... + cp*vp usando el módulo vectores.py"""
        return combinacion_lineal(vectores, escalares)

    # ---- helpers de forma -------------------------------------------------- #

    @staticmethod
    def _matriz_ceros(n_eq, n_var):
        return [[0.0] * (n_var + 1) for _ in range(n_eq)]

    def redimensionar(self, n_eq, n_var):
        """Cambia las dimensiones conservando los valores que quepan."""
        nueva = self._matriz_ceros(n_eq, n_var)
        for i in range(min(n_eq, len(self.matriz))):
            for j in range(min(n_var + 1, len(self.matriz[i]))):
                nueva[i][j] = self.matriz[i][j]
        self.n_eq, self.n_var, self.matriz = n_eq, n_var, nueva
        self.resultado = None

    def cargar_ejemplo(self, nombre):
        datos = EJEMPLOS[nombre]
        self.n_eq = len(datos)
        self.n_var = len(datos[0]) - 1
        self.matriz = [[float(v) for v in fila] for fila in datos]
        self.resultado = None
        self.origen = "ejemplo"

    def iniciar_manual(self):
        self.origen = "manual"
        self.resultado = None

    def fmt(self, valor):
        """Formatea un número según la notación elegida (fracción o decimal)."""
        return formatear_valor(valor, self.modo)

    # ---- celdas de la matriz aumentada ----------------------------------- #

    def total_celdas(self):
        return self.n_eq * (self.n_var + 1)

    def etiqueta_celda(self, indice):
        """Nombre de la celda con subíndices Unicode reales (a₁₁, b₁)."""
        fila, col = divmod(indice, self.n_var + 1)
        if col == self.n_var:
            return f"b{subindice(fila + 1)}", f"término independiente de la ecuación {fila + 1}"
        return (matriz_elem(fila, col),
                f"coeficiente de x{subindice(col + 1)} en la ecuación {fila + 1}")

    def set_celda(self, indice, valor):
        fila, col = divmod(indice, self.n_var + 1)
        self.matriz[fila][col] = valor
        self.resultado = None

    def get_celda(self, indice):
        fila, col = divmod(indice, self.n_var + 1)
        return self.matriz[fila][col]

    # ---- resolución ----------------------------------------------------- #

    def resolver(self):
        """Corre la eliminación de Gauss sobre self.matriz y guarda el resultado."""
        n = self.n_var
        coeficientes = [fila[:n] for fila in self.matriz]
        terminos = [fila[n] for fila in self.matriz]
        matriz = crear_matriz_aumentada(coeficientes, terminos)

        pasos = [("Matriz aumentada inicial", copiar_matriz(matriz))]

        def registrar(descripcion, actual):
            pasos.append((descripcion, copiar_matriz(actual)))

        fmt = self.fmt
        pivotes = escalonar(matriz, n, registrar_paso=registrar, formato_numero=fmt)
        pasos.append(("Forma escalonada final", copiar_matriz(matriz)))
        tipo = clasificar(matriz, n, pivotes)

        info_rn = verificar_rango_nulidad(matriz, n, pivotes)
        datos = {
            "tipo": tipo,
            "rango": rango_matriz(matriz, n),
            "nulidad": info_rn["nulidad"],
            "suma": info_rn["suma"],
            "n": n,
            "forma": clasificar_forma_escalonada(matriz, n, pivotes),
            "solucion": None,
            "parametrica": None,   # (libres, expresiones)
            "vectorial": None,     # {particular, vectores_nulos}
            "verificacion": None,  # (encabezado, filas_detalladas)
            "latex": "",
        }

        if tipo == "determinado":
            if getattr(self, 'metodo', 'gauss') == "gauss_jordan":
                # Aplicamos Gauss-Jordan para llegar a RREF
                reducir_a_escalonada_reducida(matriz, n, pivotes,
                                              registrar_paso=registrar, formato_numero=fmt)
                pasos.append(("Forma escalonada reducida", copiar_matriz(matriz)))
                # Extraemos la solución directa de la última columna
                x = [matriz[i][n] for i in range(n)]
            else:
                # Método clásico de Gauss: sustitución regresiva
                x = sustitucion_regresiva(matriz, n, pivotes)

            datos["solucion"] = x
            datos["latex"] = "\\mathbf{x} = " + latex_pmatrix(x, self.modo)

            # --- ASIGNACIÓN VITAL PARA EVITAR EL CRASH ---
            datos["verificacion"] = (
                "Comprobación (sustituyendo en el sistema original)",
                verificar_solucion_detallada(coeficientes, terminos, x),
            )
        elif tipo == "indeterminado":
            reducir_a_escalonada_reducida(matriz, n, pivotes,
                                          registrar_paso=registrar, formato_numero=fmt)
            pasos.append(("Forma escalonada reducida", copiar_matriz(matriz)))
            libres, expresiones = solucion_parametrica(matriz, n, pivotes)
            datos["parametrica"] = (libres, expresiones)
            datos["vectorial"] = solucion_general_vectorial(
                matriz, n, pivotes, libres, expresiones)
            datos["latex"] = generar_latex_solucion(
                n, libres, expresiones, datos["vectorial"]["particular"],
                datos["vectorial"]["vectores_nulos"], self.modo)
            x_ej = evaluar_solucion_parametrica(n, libres, expresiones, [0.0] * len(libres))
            etiqueta = ", ".join(f"t{k + 1} = 0" for k in range(len(libres))) or "sin parámetros"
            datos["verificacion"] = (
                f"Comprobación con {etiqueta}",
                verificar_solucion_detallada(coeficientes, terminos, x_ej),
            )

        datos["pasos"] = pasos
        datos["libres"] = datos["parametrica"][0] if datos["parametrica"] else []
        self.resultado = datos
        return datos