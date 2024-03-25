from PyQt5.QtWidgets import QFrame , QLabel
from PyQt5.QtCore import QPoint , Qt 
from PyQt5.QtGui import QPixmap


class Canvas(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.current_images = (
            {}
        )  # Dictionary to track images being moved {QLabel: QPoint}

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(
            "image/png"
        ):  # Check if the MIME data contains an image
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            image = QPixmap()
            image.loadFromData(byte_array)
            image_label = QLabel(self)
            image_label.setPixmap(image)  # Set pixmap from MIME data
            position = event.pos() - QPoint(
                int(image_label.width() / 2), int(image_label.height() / 2)
            )
            image_label.move(position)
            image_label.show()
            self.current_images[image_label] = (
                position  # Add the image to the dictionary
            )

    def mousePressEvent(self, event):
        for image_label, position in self.current_images.items():
            if image_label.geometry().contains(event.pos()):
                self.current_image_offset = event.pos() - position

    def mouseMoveEvent(self, event):
        for image_label, position in self.current_images.items():
            if event.buttons() == Qt.LeftButton and image_label.geometry().contains(
                event.pos()
            ):
                image_label.move(event.pos() - self.current_image_offset)

    def mouseReleaseEvent(self, event):
        for image_label, position in self.current_images.items():
            if event.button() == Qt.LeftButton:
                self.current_images[image_label] = image_label.pos()
