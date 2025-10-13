import sys
from PySide6.QtWidgets import QApplication
from ui_components import MainWindow

def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()