from PyQt5.QtWidgets import QLabel
from  PyQt5.QtCore import Qt ,QPoint , QByteArray , QIODevice ,QMimeData , QBuffer
from PyQt5.QtGui import QPixmap  , QDrag , QPainter, QPen, QColor


class DraggableImageLabel(QLabel):
    
    def __init__(self, image_path):
        super().__init__()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(  100
                               , 100
                               , Qt.KeepAspectRatio)
        self.original_pixmap = pixmap
        self.target_size = 100

    
        self.setPixmap(pixmap)  # Set image and scale it
        self.setAlignment(Qt.AlignCenter)  # Center align the image
        self.setScaledContents(True)  # Enable scaling of the image

    
    def create_bordered_pixmap(self, pixmap: QPixmap) -> QPixmap:

        """Returns a scaled image with a black border."""
        scaled = pixmap.scaled(
            self.target_size,
            self.target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        border_width = 3
        bordered = QPixmap(scaled.width() + 2 * border_width, scaled.height() + 2 * border_width)
        bordered.fill(Qt.transparent)

        painter = QPainter(bordered)
        painter.drawPixmap(border_width, border_width, scaled)

        pen = QPen(QColor("black"))
        pen.setWidth(border_width)
        painter.setPen(pen)
        painter.drawRect(0, 0, bordered.width() - 1, bordered.height() - 1)
        painter.end()

        return bordered

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:

            drag = QDrag(self)
            mime_data = QMimeData()

            # Create a QByteArray to hold the image data'
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.pixmap().save(buffer, "PNG")
            mime_data.setData("image/png", byte_array)  # Set the image as MIME data
            drag.setMimeData(mime_data)

            

            # Set the pixmap for the drag operation to keep at center
            preview = self.create_bordered_pixmap(self.original_pixmap)
            drag.setPixmap(preview)  # Set pixmap for the drag
            drag.setHotSpot(
                QPoint(preview.width() // 2, preview.height() // 2)
            )  # Set hot spot
            drag.exec_(Qt.MoveAction)
