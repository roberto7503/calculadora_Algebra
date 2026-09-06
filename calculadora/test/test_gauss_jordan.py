"""
test_gauss_jordan.py

Pruebas aisaldas para la lógica de Gauss-Jordan (Módulo 2). Valida la
reducción a Forma Escalonada Reducida (RREF) y la extracción de
soluciones paramétricas/vectoriales.
"""

import unittest
from calculadora.algoritmos.gauss import (
    clasificar,
    crear_matriz_aumentada,
    escalonar,
    sustitucion_regresiva,
    verificar_solucion,
)
from calculadora.algoritmos.gauss_jordan import (
    clasificar_forma_escalonada,
    es_forma_escalonada,
    es_forma_escalonada_reducida,
    evaluar_solucion_parametrica,
    reducir_a_escalonada_reducida,
    solucion_general_vectorial,
    solucion_parametrica,
)

def resolver(coeficientes, terminos):
    n = len(coeficientes[0])
    matriz = crear_matriz_aumentada(coeficientes, terminos)
    columnas_pivote = escalonar(matriz, n)
    tipo = clasificar(matriz, n, columnas_pivote)
    return matriz, n, columnas_pivote, tipo

class TestSistemaIndeterminado(unittest.TestCase):
    def test_infinitas_soluciones(self):
        coeficientes = [[1, 1, 1], [2, 2, 2], [1, -1, 0]]
        terminos = [6, 12, 0]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "indeterminado")
        reducir_a_escalonada_reducida(matriz, n, columnas_pivote)
        libres, expresiones = solucion_parametrica(matriz, n, columnas_pivote)
        self.assertEqual(libres, [2])
        for t in (0, 1, -3.5):
            x = evaluar_solucion_parametrica(n, libres, expresiones, [t])
            resultados = verificar_solucion(coeficientes, terminos, x)
            for _, _, coincide in resultados:
                self.assertTrue(coincide)

class TestFormasEscalonadas(unittest.TestCase):
    def test_ref_no_rref(self):
        coeficientes = [[1, 1, 1], [0, 2, 5]]
        terminos = [6, -4]
        matriz, n, columnas_pivote, _ = resolver(coeficientes, terminos)
        self.assertTrue(es_forma_escalonada(matriz, n, columnas_pivote))
        self.assertFalse(es_forma_escalonada_reducida(matriz, n, columnas_pivote))
        self.assertEqual(clasificar_forma_escalonada(matriz, n, columnas_pivote), "REF")

    def test_rref_si_reducida(self):
        coeficientes = [[1, 0, 5], [0, 1, 3]]
        terminos = [2, 4]
        matriz, n, columnas_pivote, _ = resolver(coeficientes, terminos)
        reducir_a_escalonada_reducida(matriz, n, columnas_pivote)
        self.assertTrue(es_forma_escalonada(matriz, n, columnas_pivote))
        self.assertTrue(es_forma_escalonada_reducida(matriz, n, columnas_pivote))
        self.assertEqual(clasificar_forma_escalonada(matriz, n, columnas_pivote), "RREF")

    def test_no_escalonada(self):
        matriz = [[1, 2, 3], [0, 1, 4], [0, 0, 0], [0, 0, 5]]
        columnas_pivote = [0, 1]
        n_incognitas = 3
        self.assertFalse(es_forma_escalonada(matriz, n_incognitas, columnas_pivote))

class TestSolucionVectorial(unittest.TestCase):
    def test_solucion_vectorial_indeterminada(self):
        coeficientes = [[1, 1, 1], [2, 2, 2], [1, -1, 0]]
        terminos = [6, 12, 0]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "indeterminado")
        reducir_a_escalonada_reducida(matriz, n, columnas_pivote)
        libres, expresiones = solucion_parametrica(matriz, n, columnas_pivote)
        result = solucion_general_vectorial(matriz, n, columnas_pivote, libres, expresiones)
        self.assertIn("particular", result)
        self.assertIn("vectores_nulos", result)
        self.assertIn("variables_libres", result)
        verificacion = verificar_solucion(coeficientes, terminos, result["particular"])
        for _, _, coincide in verificacion:
            self.assertTrue(coincide)

    def test_solucion_vectorial_determinada(self):
        coeficientes = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        terminos = [6, -4, 27]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "determinado")
        libres = []
        self.assertEqual(len(libres), 0)

    def test_solucion_vectorial_dos_variables_libres(self):
        coeficientes = [[1, 2, 3, 4, 5], [2, 4, 6, 8, 10]]
        terminos = [15, 30]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "indeterminado")
        reducir_a_escalonada_reducida(matriz, n, columnas_pivote)
        libres, expresiones = solucion_parametrica(matriz, n, columnas_pivote)
        self.assertEqual(len(libres), 4)
        result = solucion_general_vectorial(matriz, n, columnas_pivote, libres, expresiones)
        self.assertEqual(len(result["vectores_nulos"]), 4)

if __name__ == "__main__":
    unittest.main()