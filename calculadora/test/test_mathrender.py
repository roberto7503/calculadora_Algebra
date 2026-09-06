"""
test_mathrender.py

Comprueba que el render de LaTeX a imagen (mathrender.py) produce pixmaps
válidos. Se salta automáticamente si matplotlib o PyQt6 no están disponibles
(mathrender está pensado para degradar con elegancia en ese caso).
"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    # QApplication (no QGuiApplication) para poder coexistir con test_ui.py, que
    # necesita widgets.
    from PyQt6.QtWidgets import QApplication

    _APP = QApplication.instance() or QApplication([])
    import mathrender

    _LISTO = mathrender.disponible()
except Exception:  # pragma: no cover - depende del entorno
    _LISTO = False


@unittest.skipUnless(_LISTO, "matplotlib / PyQt6 no disponibles")
class TestMathRender(unittest.TestCase):
    def test_linea_produce_pixmap(self):
        pix = mathrender.latex_a_pixmap(r"x_1 = 3 - \frac{1}{2}\, t_1")
        self.assertIsNotNone(pix)
        self.assertFalse(pix.isNull())
        self.assertGreater(pix.width(), 0)
        self.assertGreater(pix.height(), 0)

    def test_columna_produce_pixmap(self):
        pix = mathrender.columna_a_pixmap([0.4, 0.2, -8 / 3, 5.0])
        self.assertIsNotNone(pix)
        self.assertFalse(pix.isNull())
        # un vector de 4 filas debe ser claramente más alto que ancho
        self.assertGreater(pix.height(), pix.width())

    def test_ancho_token(self):
        self.assertEqual(mathrender._ancho_token("1234"), 4)
        self.assertEqual(mathrender._ancho_token(r"\frac{12}{3}"), 2)
        self.assertEqual(mathrender._ancho_token(r"-\frac{1}{2}"), 2)


if __name__ == "__main__":
    unittest.main()