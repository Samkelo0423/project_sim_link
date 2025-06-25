from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QByteArray, QIODevice, QMimeData, QBuffer
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QPen, QColor
import os


class DraggableImageLabel(QLabel):
    """
    QLabel subclass for draggable image icons in the tool palette.

    What it does:
        - Displays an image icon that can be dragged from the palette onto a canvas.
        - Provides a bordered preview of the image during drag-and-drop.

    How:
        - Loads and scales the image to a standard size for consistent appearance.
        - Implements mousePressEvent to start a drag operation with the image and its label.
        - Uses a helper to create a bordered pixmap for the drag preview.
    """
    def __init__(self, image_path):
        """
        Initializes the draggable image label.

        What it does:
            - Loads the image from the given path and scales it for display in the palette.
            - Stores the scaled pixmap and image path for later use.

        How:
            - Loads the image as a QPixmap and scales it to 100x100 (keeping aspect ratio).
            - Sets the pixmap, alignment, and enables scaling for the label.
        """
        super().__init__()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(
            100,
            100,
            Qt.KeepAspectRatio
        )
        self.original_pixmap = pixmap  # Store the original scaled pixmap
        self.target_size = 100  # Target size for drag preview and display
        self.image_path = image_path  # Store the image path

        self.setPixmap(pixmap)  # Set image and scale it
        self.setAlignment(Qt.AlignCenter)  # Center align the image
        self.setScaledContents(True)  # Enable scaling of the image to fit label

    def create_bordered_pixmap(self, pixmap: QPixmap) -> QPixmap:
        """
        Returns a scaled image with a black border for drag preview.

        What it does:
            - Creates a new pixmap with a black border around the image for visual feedback during drag.

        How:
            - Scales the image to the target size.
            - Paints the image onto a transparent pixmap with extra space for the border.
            - Draws a black rectangle around the image.
        """
        scaled = pixmap.scaled(
            self.target_size,
            self.target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        border_width = 3
        # Create a transparent pixmap with space for the border
        bordered = QPixmap(scaled.width() + 2 * border_width, scaled.height() + 2 * border_width)
        bordered.fill(Qt.transparent)

        # Draw the image and border
        painter = QPainter(bordered)
        painter.drawPixmap(border_width, border_width, scaled)

        pen = QPen(QColor("black"))
        pen.setWidth(border_width)
        painter.setPen(pen)
        painter.drawRect(0, 0, bordered.width() - 1, bordered.height() - 1)
        painter.end()

        return bordered

    def mousePressEvent(self, event):
        """
        Initiates a drag-and-drop operation with a bordered image preview.

        What it does:
            - Starts a drag operation when the user presses the left mouse button on the image.
            - Packages the image data and its label for use in the drop target.
            - Shows a bordered preview of the image under the cursor during drag.

        How:
            - Creates a QDrag object and QMimeData for the image.
            - Saves the image as PNG data in the mime data.
            - Adds the base filename as text in the mime data.
            - Sets the drag pixmap to a bordered version of the image.
            - Sets the drag hotspot to the center of the preview.
            - Executes the drag operation.
        """
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()

            # Add image data
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.pixmap().save(buffer, "PNG")
            mime_data.setData("image/png", byte_array)

            # Add filename as text
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            mime_data.setText(base_name)

            drag.setMimeData(mime_data)
            preview = self.create_bordered_pixmap(self.original_pixmap)
            drag.setPixmap(preview)
            drag.setHotSpot(QPoint(preview.width() // 2, preview.height() // 2))
            drag.exec_(Qt.MoveAction)
