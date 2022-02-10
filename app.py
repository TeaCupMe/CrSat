
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore, QtGui

import source.design as design  # Это наш конвертированный файл дизайна

from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys

class DisplayImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, callback:function = None):
        super(DisplayImageWidget, self).__init__(parent)
        self.setFixedSize(800, 600)
        self.button = QtWidgets.QPushButton('Show picture')
        self.button.clicked.connect(self.show_image)
        self.image_frame = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.image = cv2.imread('placeHolder.png')
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image).scaled(800, 600, QtCore.Qt.KeepAspectRatio))

        self.callback = callback
    @QtCore.pyqtSlot()
    def show_image(self):
        self.callback()
        self.image = cv2.imread('./images/newimage.jpg')
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image).scaled(800, 600, QtCore.Qt.KeepAspectRatio))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    display_image_widget = DisplayImageWidget()
    display_image_widget.show()
    sys.exit(app.exec_())