"""Interfaz gráfica para resolver sistemas por eliminación de Gauss.

Punto de entrada. La interfaz está organizada por pantallas en el paquete
``ui/`` (menú → dimensiones → entrada guiada → proceso → solución vectorial).
Toda la lógica de álgebra vive en ``gauss.py``.

Uso (dentro del entorno de uv, para que se rendericen las fórmulas):
    uv sync
    uv run python gui.py
"""

import os
import sys

# Permite ejecutar `python gui.py` desde cualquier carpeta: añade este directorio
# (donde están gauss.py, formato.py, mathrender.py y el paquete ui/) al path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import main  # noqa: E402


if __name__ == "__main__":
    main()