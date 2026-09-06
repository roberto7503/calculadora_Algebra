"""
test_ui.py

Pruebas de humo de la GUI (paquete ui/). Se saltan si PyQt6 no está disponible.
Cubren en particular el bug del doble clic en el menú (issue de regresión):
un gesto que repuebla la lista no debe volver a invocar el handler con un item
ya borrado.
"""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("AQUA_GAUSS_SILENCIAR", "1")

try:
    from PyQt6.QtWidgets import QApplication

    _APP = QApplication.instance() or QApplication([])
    from ui.app import VentanaPrincipal

    _LISTO = True
except Exception:  # pragma: no cover - depende del entorno
    _LISTO = False


@unittest.skipUnless(_LISTO, "PyQt6 no disponible")
class TestMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.win = VentanaPrincipal()

    @classmethod
    def tearDownClass(cls):
        cls.win.close()

    def setUp(self):
        self.win.ir("menu")

    def test_doble_gesto_en_ejemplo_rapido_no_revienta(self):
        menu = self.win.pantallas["menu"]
        menu._poblar_principal()
        item = menu.lista.item(1)  # "Ejemplo rápido"
        # Simula el doble disparo (itemActivated + itemDoubleClicked): el 1er
        # _activar repuebla la lista, el 2º recibiría un item ya borrado.
        menu._activar(item)
        menu._activar(item)          # con el fix: no-op / repoblar, sin crash
        menu._activar(None)          # gesto sobre lista ya cambiada
        self.assertEqual(menu._modo, "ejemplos")

    def test_elegir_ejemplo_salta_a_proceso(self):
        menu = self.win.pantallas["menu"]
        menu._poblar_ejemplos()
        for i in range(menu.lista.count()):
            if menu.lista.item(i).text() == "Variables libres":
                menu._activar(menu.lista.item(i))
                break
        self.assertIs(self.win.stack.currentWidget(), self.win.pantallas["proceso"])
        self.assertEqual(self.win.sesion.origen, "ejemplo")

    def test_iniciar_va_a_dimensiones(self):
        menu = self.win.pantallas["menu"]
        menu._poblar_principal()
        menu._activar(menu.lista.item(0))  # "Iniciar"
        self.assertIs(self.win.stack.currentWidget(), self.win.pantallas["dimensiones"])
        self.assertEqual(self.win.sesion.origen, "manual")


if __name__ == "__main__":
    unittest.main()