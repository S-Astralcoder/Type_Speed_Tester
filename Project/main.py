import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from UI import UI_MainWindow



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_MainWindow()
    style_path = Path(__file__).parent / "CSS" / "style.css"
    with open(style_path, "r") as file:
        window.setStyleSheet(file.read())

    window.showMaximized()
    sys.exit(app.exec())
