"""
test_vectores.py

Pruebas unitarias para el módulo de propiedades algebraicas en R^n.
Valida las operaciones de suma, multiplicación por escalar y combinaciones lineales.
"""

import unittest
from calculadora.algoritmos.vectores import (
    sumar_vectores,
    multiplicar_escalar,
    combinacion_lineal,
)

class TestOperacionesBasicas(unittest.TestCase):
    def test_sumar_vectores_estandar(self):
        v1 = [1.0, 2.0, 3.0]
        v2 = [4.0, -1.0, 5.0]
        resultado = sumar_vectores(v1, v2)
        self.assertEqual(resultado, [5.0, 1.0, 8.0])

    def test_sumar_vectores_dimensiones_distintas(self):
        v1 = [1.0, 2.0]
        v2 = [1.0, 2.0, 3.0]
        with self.assertRaises(ValueError):
            sumar_vectores(v1, v2)

    def test_multiplicar_escalar_positivo(self):
        v = [2.0, -3.0, 4.0]
        c = 3.0
        resultado = multiplicar_escalar(c, v)
        self.assertEqual(resultado, [6.0, -9.0, 12.0])

    def test_multiplicar_escalar_cero(self):
        v = [1.0, 5.0, -8.0]
        resultado = multiplicar_escalar(0.0, v)
        self.assertEqual(resultado, [0.0, 0.0, -0.0])

class TestCombinacionLineal(unittest.TestCase):
    def test_combinacion_lineal_correcta(self):
        # 2*[1, 2] + 3*[3, 4] = [2+9, 4+12] = [11, 16]
        vectores = [[1.0, 2.0], [3.0, 4.0]]
        escalares = [2.0, 3.0]
        resultado = combinacion_lineal(vectores, escalares)
        self.assertEqual(resultado, [11.0, 16.0])

    def test_combinacion_lineal_con_ceros(self):
        # 0*[1, 1] + 5*[0, 0] = [0, 0]
        vectores = [[1.0, 1.0], [0.0, 0.0]]
        escalares = [0.0, 5.0]
        resultado = combinacion_lineal(vectores, escalares)
        self.assertEqual(resultado, [0.0, 0.0])

    def test_error_cantidad_escalares_vectores(self):
        vectores = [[1.0, 2.0], [3.0, 4.0]]
        escalares = [2.0] # Falta un escalar
        with self.assertRaises(ValueError):
            combinacion_lineal(vectores, escalares)

    def test_error_dimensiones_incompatibles_en_lista(self):
        vectores = [[1.0, 2.0], [3.0, 4.0, 5.0]] # R^2 y R^3 mezclados
        escalares = [2.0, 3.0]
        with self.assertRaises(ValueError):
            combinacion_lineal(vectores, escalares)

    def test_error_lista_vectores_vacia(self):
        with self.assertRaises(ValueError):
            combinacion_lineal([], [])

if __name__ == "__main__":
    unittest.main()