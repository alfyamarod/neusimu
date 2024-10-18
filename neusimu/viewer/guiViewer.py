import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QSlider ,QGraphicsView, QGraphicsScene, QGraphicsItem, QPushButton
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter, QPainterPath
from neusimu import Neuron, Simulation
from typing import Optional, List

class NeuronWidget(QGraphicsItem):
    def __init__(self, name, x, y, neuron):
        super().__init__()
        self.name = name
        self.setPos(x, y)
        self.neuron = neuron
        self.setZValue(1)

        def boudingRect(self):
            return QRectF(-10, -10, 20, 20)

        def paint(self, painter, option, widget):
            painter.setBrush(Qt.white)
            painter.drawEllipse(-10, -10, 20, 20)
            if self.show_name:
                painter.setPen(QColor(0, 128, 0))
                painter.drawText(-5, 5, self.name)


class NetworkWidget(QGraphicsView):
    def __init__(self, neurons : List[Neuron], connections = None):
        super().__init__()
        self.setRenderHint(QPainter.RenderHints.Antialiasing)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(0, 0, 800, 800)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        for n in neurons:
            name, x, y, Neuron = n
            nw = NeuronWidget(name, x, y, Neuron)
            self.scene().addItem(nw)

        self.connetions = []


class MainWindow(QMainWindow):
    def __init__(self, simu : Simulation, tmax = 0.0):
        super().__init__()
        self.simu = simu
        self.playing = False


        neurons = simu.neurons
        connections = simu.projections
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


        # Buttons
        button_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        button_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)


        # slider_layout = QHBoxLayout()
        # self.t_slider = QSlider(Qt.Orientation.Horizontal)
        # self.t_slider.setMinimum(0)
        # self.t_slider.setMaximum(tmax - 1)
        # self.t_slider.setValue(0)
        # self.t_slider.valueChanged.connect(self.update_graph)
        # slider_layout.addWidget(self.t_slider)

        self.network_widget = NetworkWidget(neurons = neurons, connections = connections)
        layout.addWidget(self.network_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_t)
        


        
    def play(self):
        if not self.playing:
            self.playing = False
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.timer.start(100)

    def stop(self):
        if self.playing:
            self.playing = True
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.timer.stop()

    def update_t(self):
        t = self.t_slider.value()
        t = (t + 1) % self.tmax
        self.t_slider.setValue(t)


    def update_graph(self):
        t = self.t_slider.value()
        edie_dt = self.network_widget.edges[0].Link.edie_dt
        self.graph_widget.set_t(t)
        self.t_label.setText("{}/{}".format(t*edie_dt, self.tmax*edie_dt))
        
        
            


def simu_viewer(simu):

    app = QApplication(sys.argv)
    wind = MainWindow(simu)
    wind.show()
    sys.exit(app.exec())
