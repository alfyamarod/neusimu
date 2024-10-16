
import sys
from PyQt6.QtWidgets import QApplication, QWidget

class MainWindow(QMainWindow):
    def __init__(self, simu):
        super().__init__()
        self.simu = simu

        central_widget = QWidget()
        layout = QVBoxLayout()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
