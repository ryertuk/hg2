from PySide6.QtWidgets import QMainWindow, QTabWidget
from app.ui.parties.parties_view import PartiesView
from app.ui.items.items_view import ItemsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        tabs = QTabWidget()
        tabs.addTab(PartiesView(), "Parties")
        tabs.addTab(ItemsView(), "Items")
        self.setCentralWidget(tabs)