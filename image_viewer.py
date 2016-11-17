import sys
import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt


class ImageViewer(QtGui.QMainWindow):

    def __init__(self):
        super(ImageViewer, self).__init__()
        self._init_ui()
        self.show()

    def _init_ui(self):
        self._image_viewer = ImageViewerCentralWidget(self)
        self.setCentralWidget(self._image_viewer)
        self.setGeometry(100, 100, 800, 600)

    @property
    def image(self):
        return self._image_viewer.image

    @image.setter
    def image(self, value):
        self._image_viewer.image = value


class ImageViewerCentralWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ImageViewerCentralWidget, self).__init__(parent=parent)
        self._init_ui()

    def _init_ui(self):
        self._image_viewer = ImageViewerWidget(self)
        self._central_layout = QtGui.QVBoxLayout()
        self._central_layout.addWidget(self._image_viewer)
        self._resolution_slider = QtGui.QSlider(Qt.Horizontal)
        self._resolution_slider.setValue(100)
        self._resolution_slider.valueChanged.connect(self._on_resolution_changed)
        self._central_layout.addWidget(self._resolution_slider)
        self.setLayout(self._central_layout)

    def _on_resolution_changed(self, value):
        self._image_viewer.resolution_scale = 1.0 * value / 100

    @property
    def image(self):
        return self._image_viewer.image

    @image.setter
    def image(self, value):
        self._image_viewer.image = value



class ImageViewerWidget(QtGui.QWidget):

    def __init__(self, image_source=None, parent=None):
        super(ImageViewerWidget, self).__init__(parent=parent)
        self._init_ui()
        self._image_source = image_source
        self._mouse_press_pos = None
        self._mouse_release_pos = None
        self._mouse_image_press_pos = None
        self._mouse_image_release_pos = None
        self._source_rect = None
        self._window_zoom_active = False
        self._resolution_scale = 1.0

    def _init_ui(self):
        pass
        #self.setGeometry(100, 100, 800, 600)

    @property
    def image(self):
        return self._image_source

    @image.setter
    def image(self, value):
        self._image_source = value
        self.repaint()

    @property
    def resolution_scale(self):
        return self._resolution_scale

    @resolution_scale.setter
    def resolution_scale(self, value):
        self._resolution_scale = value
        self.repaint()

    def paintEvent(self, e):
        if self._image_source:
            qp = QtGui.QPainter()
            qp.begin(self)
            self._image = QtGui.QImage(self._image_source)
            g = self.geometry()
            self._target_rect = QtCore.QRect(0, 0, g.width(), g.height())
            if not self._source_rect:
                self._source_rect = QtCore.QRect(0, 0, self._image.width(), self._image.height())
            r = self._source_rect
            hres = self._resolution_scale * g.width()
            if hres < r.width():
                xscale = 1.0 * hres / r.width()
            else:
                xscale = 1.0
            vres = self._resolution_scale * g.height()
            if vres < r.height():
                yscale = 1.0 * vres / r.height()
            else:
                yscale = 1.0
            scaled_width = int(np.round(xscale * self._image.width()))
            scaled_height = int(np.round(yscale * self._image.height()))
            scaled_size = QtCore.QSize(scaled_width, scaled_height)
            transformMode = Qt.SmoothTransformation # Qt.FastTransformation
            scaled_image = self._image.scaled(scaled_size, transformMode=transformMode)
            x = int(np.round(xscale * r.x()))
            y = int(np.round(yscale * r.y()))
            w = int(np.round(xscale * r.width()))
            h = int(np.round(yscale * r.height()))
            scaled_source_rect = QtCore.QRect(x, y, w, h)
            qp.drawImage(self._target_rect, scaled_image, scaled_source_rect)
            if self._window_zoom_active:
                if self._mouse_press_pos and self._mouse_move_pos:
                    rect = QtCore.QRect(self._mouse_press_pos, self._mouse_move_pos)
                    qp.drawRect(rect)
            qp.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._mouse_press_pos = e.pos()
            x = self._mouse_press_pos.x()
            y = self._mouse_press_pos.y()
            g = self.geometry()
            if 0 <= x <= g.width() and 0 <= y <= g.height():
                xr = float(x) / g.width()
                yr = float(y) / g.height()
                r = self._source_rect
                if r:
                    xi = r.x() + int(xr * r.width())
                    yi = r.y() + int(yr * r.height())
                    self._mouse_image_press_pos = QtCore.QPoint(xi, yi)
                    self._window_zoom_active = True
        elif e.button() == Qt.RightButton:
            self._mouse_image_press_pos = None
            self._mouse_image_release_pos = None
            if self._image:
                self._source_rect = QtCore.QRect(0, 0, self._image.width(), self._image.height())
            else:
                self._source_rect = None
            self.repaint()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._mouse_release_pos = e.pos()
            self._mouse_move = self._mouse_release_pos - self._mouse_press_pos
            x = self._mouse_release_pos.x()
            y = self._mouse_release_pos.y()
            g = self.geometry()
            if 0 <= x <= g.width() and 0 <= y <= g.height():
                xr = float(x) / g.width()
                yr = float(y) / g.height()
                r = self._source_rect
                if r:
                    xi = r.x() + int(np.ceil(xr * r.width()))
                    yi = r.y() + int(np.ceil(yr * r.height()))
                    self._mouse_image_release_pos = QtCore.QPoint(xi, yi)
                    self._source_rect = QtCore.QRect(self._mouse_image_press_pos, self._mouse_image_release_pos)
            self._window_zoom_active = False
            self.repaint()

    def mouseMoveEvent(self, e):
        self._mouse_move_pos = e.pos()
        self.repaint()


def main():
    app = QtGui.QApplication(sys.argv)
    iv = ImageViewer()
    iv.image = "Lenna.png"
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()