"""
test_gauss.py

Pruebas para la lógica pura de gauss.py. Valida la Forma Escalonada (REF),
clasificación de consistencia y sustitución regresiva.
"""

import unittest
from calculadora.algoritmos.gauss import (
    clasificar,
    crear_matriz_aumentada,
    escalonar,
    rango_matriz,
    sustitucion_regresiva,
    verificar_rango_nulidad,
    verificar_solucion,
    verificar_solucion_detallada,
)

def resolver(coeficientes, terminos):
    n = len(coeficientes[0])
    matriz = crear_matriz_aumentada(coeficientes, terminos)
    columnas_pivote = escalonar(matriz, n)
    tipo = clasificar(matriz, n, columnas_pivote)
    return matriz, n, columnas_pivote, tipo

class TestSistemaDeterminado(unittest.TestCase):
    def test_solucion_unica_3x3(self):
        coeficientes = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        terminos = [6, -4, 27]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "determinado")
        x = sustitucion_regresiva(matriz, n, columnas_pivote)
        self.assertAlmostEqual(x[0], 5)
        self.assertAlmostEqual(x[1], 3)
        self.assertAlmostEqual(x[2], -2)

    def test_requiere_pivoteo_por_cero_inicial(self):
        coeficientes = [[0, 2], [3, 1]]
        terminos = [4, 5]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "determinado")
        x = sustitucion_regresiva(matriz, n, columnas_pivote)
        self.assertAlmostEqual(x[0], 1)
        self.assertAlmostEqual(x[1], 2)

class TestSistemaIncompatible(unittest.TestCase):
    def test_sin_solucion(self):
        coeficientes = [[1, 1], [1, 1]]
        terminos = [2, 5]
        _, _, _, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "incompatible")

    def test_sin_solucion_3x3(self):
        coeficientes = [[1, -1, 1], [2, -2, 2], [1, 1, 1]]
        terminos = [3, 5, 4]
        _, _, _, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "incompatible")

class TestVerificarSolucion(unittest.TestCase):
    def test_solucion_correcta(self):
        coeficientes = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        terminos = [6, -4, 27]
        x = [5, 3, -2]
        resultados = verificar_solucion(coeficientes, terminos, x)
        self.assertEqual(len(resultados), 3)
        for valor_calculado, valor_esperado, coincide in resultados:
            self.assertTrue(coincide)
            self.assertAlmostEqual(valor_calculado, valor_esperado)

    def test_solucion_incorrecta_no_coincide(self):
        coeficientes = [[1, 1], [1, -1]]
        terminos = [4, 0]
        x = [1, 1]
        resultados = verificar_solucion(coeficientes, terminos, x)
        coincidencias = [coincide for _, _, coincide in resultados]
        self.assertFalse(all(coincidencias))

class TestVerificarSolucionDetallada(unittest.TestCase):
    def test_expone_terminos_y_suma(self):
        coeficientes = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        terminos = [6, -4, 27]
        x = [5, 3, -2]
        detalle = verificar_solucion_detallada(coeficientes, terminos, x)
        self.assertEqual(len(detalle), 3)
        self.assertEqual(detalle[0]["terminos"], [(1, 5, 5), (1, 3, 3), (1, -2, -2)])
        self.assertAlmostEqual(detalle[0]["suma"], 6)
        self.assertEqual(detalle[0]["esperado"], 6)
        for fila in detalle:
            self.assertTrue(fila["coincide"])

    def test_marca_incoincidencia(self):
        coeficientes = [[1, 1], [1, -1]]
        terminos = [4, 0]
        detalle = verificar_solucion_detallada(coeficientes, terminos, [1, 1])
        self.assertFalse(all(fila["coincide"] for fila in detalle))

    def test_consistente_con_verificar_solucion(self):
        coeficientes = [[2, 1], [1, 3]]
        terminos = [1, 1]
        x = [0.4, 0.2]
        resumen = verificar_solucion(coeficientes, terminos, x)
        detalle = verificar_solucion_detallada(coeficientes, terminos, x)
        for (suma_r, esp_r, ok_r), fila in zip(resumen, detalle):
            self.assertAlmostEqual(suma_r, fila["suma"])
            self.assertEqual(esp_r, fila["esperado"])
            self.assertEqual(ok_r, fila["coincide"])

class TestRango(unittest.TestCase):
    def test_rango_matriz_determinado(self):
        coeficientes = [[1, 1, 1], [0, 2, 5], [2, 5, -1]]
        terminos = [6, -4, 27]
        matriz, n, columnas_pivote, _ = resolver(coeficientes, terminos)
        rango = rango_matriz(matriz, n)
        self.assertEqual(rango, 3)

    def test_rango_matriz_indeterminado(self):
        coeficientes = [[1, 1, 1], [2, 2, 2], [1, -1, 0]]
        terminos = [6, 12, 0]
        matriz, n, columnas_pivote, _ = resolver(coeficientes, terminos)
        rango = rango_matriz(matriz, n)
        self.assertEqual(rango, 2)

    def test_rango_nulidad(self):
        coeficientes = [[1, 1, 1], [2, 2, 2], [1, -1, 0]]
        terminos = [6, 12, 0]
        matriz, n, columnas_pivote, _ = resolver(coeficientes, terminos)
        result = verificar_rango_nulidad(matriz, n, columnas_pivote)
        self.assertEqual(result["rango"], 2)
        self.assertEqual(result["nulidad"], 1)
        self.assertEqual(result["suma"], 3)
        self.assertTrue(result["es_valido"])

class TestMatricesRectangulares(unittest.TestCase):
    def test_matriz_2x3(self):
        coeficientes = [[1, 2, 3], [4, 5, 6]]
        terminos = [7, 8]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertEqual(tipo, "indeterminado")
        self.assertEqual(len(columnas_pivote), 2)
        self.assertLessEqual(len(columnas_pivote), min(len(coeficientes), n))

    def test_matriz_3x2(self):
        coeficientes = [[1, 2], [3, 4], [5, 6]]
        terminos = [7, 8, 10]
        matriz, n, columnas_pivote, tipo = resolver(coeficientes, terminos)
        self.assertIn(tipo, ["incompatible", "determinado", "indeterminado"])

if __name__ == "__main__":
    unittest.main()