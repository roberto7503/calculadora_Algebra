"""Pruebas de los textos de clasificación mostrados por la interfaz de consola."""

import io
import unittest
from contextlib import redirect_stdout

from main import resolver_sistema


class TestClasificacionVisible(unittest.TestCase):
    def salida_de(self, coeficientes, terminos):
        salida = io.StringIO()
        with redirect_stdout(salida):
            resolver_sistema(coeficientes, terminos, len(coeficientes[0]))
        return salida.getvalue()

    def test_sistema_consistente_determinado(self):
        salida = self.salida_de([[1, 1], [1, -1]], [4, 0])
        self.assertIn("Sistema CONSISTENTE DETERMINADO", salida)
        self.assertNotIn("Sistema COMPATIBLE", salida)

    def test_sistema_consistente_indeterminado(self):
        salida = self.salida_de([[1, 1], [2, 2]], [2, 4])
        self.assertIn("Sistema CONSISTENTE INDETERMINADO", salida)
        self.assertNotIn("Sistema COMPATIBLE", salida)

    def test_sistema_inconsistente(self):
        salida = self.salida_de([[1, 1], [1, 1]], [2, 5])
        self.assertIn("Sistema INCONSISTENTE", salida)
        self.assertNotIn("Sistema INCOMPATIBLE", salida)


if __name__ == "__main__":
    unittest.main()