"""
test_formato.py

Pruebas de la capa de presentación (formato.py): conversión a fracción exacta,
formateo de valores y generación de LaTeX con fracciones.
"""

import unittest

from formato import (
    MODO_DECIMAL,
    MODO_FRACCION,
    a_fraccion,
    formatear_valor,
    generar_latex_solucion,
    latex_valor,
    mcd,
    normalizar_entrada,
)


class TestMcd(unittest.TestCase):
    def test_casos_basicos(self):
        self.assertEqual(mcd(12, 8), 4)
        self.assertEqual(mcd(7, 0), 7)
        self.assertEqual(mcd(0, 0), 0)
        self.assertEqual(mcd(-12, 8), 4)


class TestAFraccion(unittest.TestCase):
    def test_entero(self):
        self.assertEqual(a_fraccion(4.0), (4, 1))
        self.assertEqual(a_fraccion(-3.0), (-3, 1))
        self.assertEqual(a_fraccion(0.0), (0, 1))

    def test_fracciones_simples(self):
        self.assertEqual(a_fraccion(1 / 3), (1, 3))
        self.assertEqual(a_fraccion(-8 / 3), (-8, 3))
        self.assertEqual(a_fraccion(0.5), (1, 2))
        self.assertEqual(a_fraccion(2.5), (5, 2))
        self.assertEqual(a_fraccion(-2.6), (-13, 5))

    def test_ya_reducida(self):
        # 2/4 debe reducirse a 1/2
        self.assertEqual(a_fraccion(0.5), (1, 2))

    def test_irracional_devuelve_none(self):
        self.assertIsNone(a_fraccion(2 ** 0.5))
        self.assertIsNone(a_fraccion(3.14159265358979))

    def test_denominador_grande_devuelve_none(self):
        # 1/99991 supera max_den por defecto (10000)
        self.assertIsNone(a_fraccion(1 / 99991))


class TestFormatearValor(unittest.TestCase):
    def test_modo_fraccion(self):
        self.assertEqual(formatear_valor(1 / 3, MODO_FRACCION), "1/3")
        self.assertEqual(formatear_valor(4.0, MODO_FRACCION), "4")
        self.assertEqual(formatear_valor(-8 / 3, MODO_FRACCION), "-8/3")

    def test_modo_decimal(self):
        self.assertEqual(formatear_valor(1 / 3, MODO_DECIMAL), "0.3333")
        self.assertEqual(formatear_valor(4.0, MODO_DECIMAL), "4")
        self.assertEqual(formatear_valor(0.5, MODO_DECIMAL), "0.5")

    def test_irracional_cae_a_decimal_en_modo_fraccion(self):
        self.assertEqual(formatear_valor(2 ** 0.5, MODO_FRACCION), "1.4142")


class TestNormalizarEntrada(unittest.TestCase):
    """ADR-0001: distintas formas de teclear la misma cantidad convergen."""

    def _frac(self, v):
        return formatear_valor(normalizar_entrada(v), MODO_FRACCION)

    def test_aproximaciones_de_una_fraccion_convergen(self):
        self.assertEqual(self._frac(6.3333), "19/3")
        self.assertEqual(self._frac(6.333333333), "19/3")
        self.assertEqual(self._frac(19 / 3), "19/3")
        self.assertEqual(self._frac(0.3333), "1/3")

    def test_decimales_sin_fraccion_tidy_se_redondean_a_4(self):
        self.assertEqual(self._frac(6.33), "6.33")            # 633/100: den > 64
        self.assertEqual(self._frac(0.333), "0.333")          # a más de 1e-4 de 1/3
        self.assertEqual(normalizar_entrada(2 ** 0.5), 1.4142)

    def test_enteros_y_fracciones_pequenas_intactos(self):
        self.assertEqual(normalizar_entrada(5.0), 5.0)
        self.assertEqual(self._frac(-2.5), "-5/2")


class TestLatex(unittest.TestCase):
    def test_latex_valor_fraccion(self):
        self.assertEqual(latex_valor(1 / 3), "\\frac{1}{3}")
        self.assertEqual(latex_valor(-1 / 2), "-\\frac{1}{2}")
        self.assertEqual(latex_valor(4.0), "4")

    def test_latex_solucion_incluye_frac_y_no_pierde_ceros(self):
        # x_p = [3, 3, 0]  ->  el 0 debe aparecer, no una cadena vacía
        latex = generar_latex_solucion(
            3, [2], [None, None, None],
            [3.0, 3.0, 0.0], [[-0.5, -0.5, 1.0]], MODO_FRACCION,
        )
        self.assertIn("\\begin{pmatrix} 3 \\\\ 3 \\\\ 0 \\end{pmatrix}", latex)
        self.assertIn("\\frac{1}{2}", latex)


if __name__ == "__main__":
    unittest.main()