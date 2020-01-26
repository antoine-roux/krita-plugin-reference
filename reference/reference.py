#!/usr/bin/env python3
import sys
import math
import os.path
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPainter, QColor, QCursor, QPen
from PyQt5.QtWidgets import QWidget, QApplication
from krita import *

def trueLength(size):
    return math.sqrt(pow(size.x(), 2) + pow(size.y(), 2));

class ReferenceExtension(Extension):

    def __init__(self, parent):
        #This is initialising the parent, always  important when subclassing.
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        pass

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(ReferenceExtension(Krita.instance()))

class ReferenceViewer(QWidget):
    colorPicked = pyqtSignal(QColor)
    triggerDistance = 10

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(QCursor(Qt.CrossCursor))

        self.image = QImage()
        self.zoom = 1.0
        self.oldZoom = None

        self.origin = QPoint(0, 0)
        self.oldOrigin = None

        self.pressedPoint = None
        self.moving = False
        self.currentColor = None

    def getCurrentColor(self, event):
        if not self.image.isNull():
            pos = (event.pos() - self.origin) / self.zoom
            return self.image.pixelColor(pos)

        return None

    def setImage(self, image=QImage()):
        self.image = image
        self.resetView()

    def resetView(self):
        if self.image.isNull():
            return

        self.zoom = min(self.size().width() / self.image.size().width(),
                        self.size().height() / self.image.size().height())
        overflow = self.size() - (self.image.size() * self.zoom)
        self.origin = QPoint(overflow.width() / 2, overflow.height() / 2)
        self.update()

    def paintEvent(self, event):
        if self.image.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRect(-self.origin / self.zoom, self.size() / self.zoom)
        cropped = self.image.copy(rect)
        image = cropped.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawImage(0, 0, image)

        if self.pressedPoint is not None and not self.moving:
            painter.setPen(QPen(QColor(255, 255, 255, 128), 3.0))
            painter.drawEllipse(self.pressedPoint, self.triggerDistance, self.triggerDistance)

        if self.currentColor is not None:
            painter.fillRect(0, 0, self.size().width(), 20, self.currentColor)

    def mousePressEvent(self, event):
        self.pressedPoint = event.pos()
        self.oldOrigin = self.origin
        self.oldZoom = self.zoom
        self.currentColor = self.getCurrentColor(event)
        self.update()

    def mouseReleaseEvent(self, event):
        self.currentColor = self.getCurrentColor(event)
        if not self.moving and self.currentColor is not None:
            self.colorPicked.emit(self.currentColor)

        self.pressedPoint = None
        self.moving = False
        self.currentColor = None
        self.update()

    def mouseMoveEvent(self, event):
        if self.pressedPoint is not None:
            distance = trueLength(self.pressedPoint - event.pos())
            if distance >= self.triggerDistance:
                self.moving = True

            if self.moving:
                if QApplication.keyboardModifiers() & Qt.ControlModifier:
                    zoomDelta = self.pressedPoint.y() - event.pos().y()
                    centerPos = (self.pressedPoint - self.oldOrigin) / self.oldZoom
                    self.zoom = max(0.01, self.oldZoom + (zoomDelta / 100) * self.oldZoom)
                    self.origin = self.pressedPoint - (centerPos * self.zoom)
                else:
                    self.origin = self.oldOrigin - self.pressedPoint + event.pos()

                self.currentColor = None
            else:
                self.currentColor = self.getCurrentColor(event)

            self.update()

    def wheelEvent(self, event):
        centerPos = (event.pos() - self.origin) / self.zoom

        self.zoom = max(0.01, self.zoom + (event.angleDelta().y() / 500) * self.zoom)
        self.origin = event.pos() - (centerPos * self.zoom)

        self.update()

    def resizeEvent(self, event):
        self.resetView()

    def sizeHint(self):
        return QSize(256, 256)

class ReferenceDocker(DockWidget):

    def __init__(self):
        super().__init__()
        self.currentDir = Application.readSetting('referenceDocker', 'lastdir', '.')

        self.setWindowTitle("Reference Docker")

        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.viewer = ReferenceViewer()
        self.viewer.colorPicked.connect(self.changeColor)
        layout.addWidget(self.viewer)

        buttonLayout = QHBoxLayout(widget)
        self.center = QAction(self)
        self.center.setIconText("Reset view")
        self.center.triggered.connect(self.centerView)
        centerButton = QToolButton()
        centerButton.setDefaultAction(self.center)
        buttonLayout.addWidget(centerButton)

        self.open = QAction(self)
        self.open.setIconText("Open")
        self.open.triggered.connect(self.openImage)
        openButton = QToolButton()
        openButton.setDefaultAction(self.open)
        buttonLayout.addWidget(openButton)

        layout.addLayout(buttonLayout)
        self.setWidget(widget)

        fileName = Application.readSetting('referenceDocker', 'lastref', None)
        if fileName is not None:
            self.viewer.setImage(QImage(fileName))

    def centerView(self):
        self.viewer.resetView()

    def openImage(self):
        fileName, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Open an image", self.currentDir)
        if not fileName:
            return

        Application.writeSetting('referenceDocker', 'lastref', fileName)

        self.currentDir = os.path.dirname(fileName)
        Application.writeSetting('referenceDocker', 'lastdir', self.currentDir)

        self.viewer.setImage(QImage(fileName))

    @pyqtSlot(QColor)
    def changeColor(self, color):
        if (self.canvas()) is not None and self.canvas().view() is not None:
            _color = ManagedColor("RGBA", "U8", "")
            _color.setComponents([color.blueF(), color.greenF(), color.redF(), 1.0])
            self.canvas().view().setForeGroundColor(_color)

    def canvasChanged(self, canvas):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("referenceDocker", DockWidgetFactoryBase.DockRight, ReferenceDocker))
