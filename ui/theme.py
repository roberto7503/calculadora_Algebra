"""Hoja de estilo, paleta y fuente de la aplicación."""

from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette

APP_INFO = {
    "nombre": "Aqua Gauss",
    "version": "2.0.0",
    "resumen": ("Resuelve y analiza sistemas de ecuaciones lineales Ax = b por "
                "eliminación de Gauss, paso a paso y sin librerías de álgebra."),
    "autores": "Andrés Castillo y Fátima Zogaib (Grupo 7)",
    "licencia": "MIT",
    "repo": "github.com/acr301/alg-lineal-I",
}

# No se declara 'font-family' aquí: se fija por código en aplicar_tema() eligiendo
# una familia que exista en el sistema (evita el warning 'missing font family').
STYLESHEET = """
QWidget { color: #153653; font-size: 14px; }
#pantalla { background: transparent; }
QFrame#hero { background: #0874a4; border-radius: 16px; }
QLabel#title { color: white; font-size: 26px; font-weight: 800; }
QLabel#subtitle { color: #eafcff; font-size: 13px; }
QLabel#h1 { font-size: 20px; font-weight: 800; color: #0874a4; }
QLabel#hint { color: #41738c; font-size: 12px; }
QLabel#explain { color: #5a7d92; font-size: 12px; }
QLabel#pie { color: #7fa0b3; font-size: 11px; }
QLabel#prompt { font-size: 17px; font-weight: 700; color: #0874a4; }
QLabel#status { padding: 8px 12px; border-radius: 9px; font-weight: 800; }
QGroupBox { background: rgba(255,255,255,0.88); border: 1px solid #a7dce9;
    border-radius: 14px; margin-top: 14px; padding: 14px 12px 12px; font-weight: 700; color: #0874a4; }
QGroupBox::title { subcontrol-origin: margin; left: 13px; padding: 0 5px; }
QFrame#card { background: rgba(255,255,255,0.92); border: 1px solid #a7dce9; border-radius: 14px; }
QSpinBox, QComboBox, QLineEdit { background: white; border: 1px solid #86cde3;
    border-radius: 9px; padding: 8px; min-height: 22px; selection-background-color: #9de6f2; }
QLineEdit#cell { font-size: 22px; font-weight: 700; padding: 12px; }
QSpinBox:focus, QComboBox:focus, QLineEdit:focus { border: 2px solid #087fca; }

/* --- AQUÍ SE QUITARON LOS DEGRADADOS DE LOS BOTONES --- */
QPushButton { background: #0685cc; color: white; border: 1px solid #0572b2; 
    border-radius: 10px; padding: 9px 16px; font-weight: 700; }
QPushButton:hover { background: #059ae9; }
QPushButton:pressed { background: #056da8; }
QPushButton:focus { border: 2px solid #08405f; }
QPushButton:disabled { background: #bcd9e6; color: #eef; border-color: #a7c7d6; }

QPushButton#secondary { background: white; color: #0874a4; border: 1px solid #86cde3; }
QPushButton#secondary:hover { background: #eafaff; }
QPushButton#ghost { background: transparent; color: #0874a4; border: none; font-weight: 700; }
QPushButton#ghost:hover { color: #04628c; text-decoration: underline; }
QToolButton#help { background: #0874a4; color: white; border-radius: 9px;
    font-weight: 800; font-size: 11px; min-width: 18px; min-height: 18px; border: none; }
QToolButton#help:hover { background: #04628c; }
QToolButton#help:focus { border: 2px solid #08405f; }
QListWidget { background: transparent; border: none; }
QListWidget::item { background: white; border: 1px solid #86cde3; border-radius: 10px;
    padding: 14px; margin: 4px 0; font-weight: 700; color: #0874a4; }
QListWidget::item:selected { background: #0685cc; color: white; border-color: #0572b2; }
QTableWidget { background: rgba(255,255,255,0.95); alternate-background-color: #edfaff;
    border: 1px solid #9bd4e6; border-radius: 10px; gridline-color: #c5e9f1;
    selection-background-color: #9de6f2; font-size: 15px; }
QHeaderView::section { background: #d7f5fa; color: #096f99; border: 0;
    border-bottom: 1px solid #9bd4e6; padding: 7px; font-weight: 800; }
QScrollArea { border: none; background: transparent; }
QTextEdit { background: white; border: 1px solid #86cde3; border-radius: 10px; }
"""


def _familia_disponible():
    try:
        familias = set(QFontDatabase.families())
    except Exception:
        return None
    for candidata in ("Avenir Next", "Helvetica Neue", "Helvetica", "Segoe UI",
                      "Arial", "DejaVu Sans"):
        if candidata in familias:
            return candidata
    return None


def aplicar_tema(app):
    """Fija estilo, paleta y una fuente concreta que exista en el sistema."""
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    familia = _familia_disponible()
    if familia:
        fuente = QFont(familia)
        fuente.setPointSize(10)
        app.setFont(fuente)

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#dff7ff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#0f3e59"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    app.setPalette(palette)