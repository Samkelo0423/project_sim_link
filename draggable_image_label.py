from PyQt5.QtWidgets import QLabel
from  PyQt5.QtCore import Qt ,QPoint , QByteArray , QIODevice ,QMimeData , QBuffer
from PyQt5.QtGui import QPixmap  , QDrag


class DraggableImageLabel(QLabel):
    
    def __init__(self, image_path):
        super().__init__()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)  # Set image and scale it
        self.setAlignment(Qt.AlignCenter)  # Center align the image
        self.setScaledContents(True)  # Enable scaling of the image

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:

            drag = QDrag(self)
            mime_data = QMimeData()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.pixmap().save(buffer, "PNG")
            mime_data.setData("image/png", byte_array)  # Set the image as MIME data
            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap())  # Set pixmap for the drag
            drag.setHotSpot(
                QPoint(int(self.width() / 2), int(self.height() / 2))
            )  # Set hot spot
            drag.exec_(Qt.MoveAction)
