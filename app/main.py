from PySide6.QtWidgets import QApplication, QMainWindow
from app.ui.main_window import MainWindow  # در مراحل بعدی گسترش
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  # شامل PartiesView
    window.show()
    sys.exit(app.exec())