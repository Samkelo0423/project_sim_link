from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QPixmap

class Canvas(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.current_images = {}  # Dictionary to track images being moved {QLabel: {"position": QPoint, "size": QSize, "resizing": bool, "resizing_offset": QPoint, "resize_corner": str}}

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/png"):
            event.acceptProposedAction()

    def dropEvent(self, event):

        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            image = QPixmap()
            image.loadFromData(byte_array)
            image_label = QLabel(self)
            image_label.setPixmap(image)
            image_label.setStyleSheet("border: 2px solid black; border-radius : 0px ;")

            position = event.pos() - QPoint(
                int(image_label.width() / 2), int(image_label.height() / 2)
            )
            image_label.move(position)
            image_label.show()

            # Store image properties in the dictionary
            self.current_images[image_label] = {
                "position": position,
                "size": image.size(),
                "resizing": False,
                "resizing_offset": QPoint(),
                "resize_corner": None,
                "pixmap": image
            }

    def mousePressEvent(self, event):

        for image_label, properties in self.current_images.items():
            if image_label.geometry().contains(event.pos()):
                # Reset resizing status and offset
                properties["resizing"] = False
                properties["resizing_offset"] = QPoint()
                # Calculate the offset for dragging
                properties["current_image_offset"] = event.pos() - properties["position"]

                # Check if resizing is requested
                position = properties["position"]
                size = properties["size"]

                corners = [
                    (position, "top_left"),
                    (position + QPoint(size.width(), 0), "top_right"),
                    (position + QPoint(0, size.height()), "bottom_left"),
                    (position + QPoint(size.width(), size.height()), "bottom_right"),
                ]
                for corner, corner_name in corners:
                    # Check if the mouse press is on a corner for resizing
                    if abs(corner.x() - event.pos().x()) <= 8 and abs(corner.y() - event.pos().y()) <= 8:

                        properties["resizing"] = True
                        properties["resizing_offset"] = corner - event.pos()
                        properties["resize_corner"] = corner_name

    def mouseMoveEvent(self, event):
      for image_label, properties in self.current_images.items():
        if event.buttons() == Qt.LeftButton and image_label.geometry().contains(event.pos()):
            if not properties["resizing"]:
                # Move the image label if not resizing
                image_label.move(event.pos() - properties["current_image_offset"])
            else:
                # Resize the image label if resizing
                new_size = (properties["size"] + QSize(event.pos().x() - properties["position"].x() - properties["resizing_offset"].x(), event.pos().y() - properties["position"].y() - properties["resizing_offset"].y())).expandedTo(QSize(1, 1))

                # Adjust position and size for diagonal resizing
                if properties["resize_corner"] in ["top_left", "bottom_right"]:
                    new_position = QPoint(min(properties["position"].x(), event.pos().x()), min(properties["position"].y(), event.pos().y()))
                elif properties["resize_corner"] in ["top_right", "bottom_left"]:
                    new_position = QPoint(max(properties["position"].x(), event.pos().x()), max(properties["position"].y(), event.pos().y()))

                # Resize and move the image label
                image_label.setGeometry(
                    new_position.x(),
                    new_position.y(),
                    new_size.width(),
                    new_size.height()
                )

                image_label.setPixmap(properties["pixmap"].scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mouseReleaseEvent(self, event):
        for image_label, properties in self.current_images.items():
            if event.button() == Qt.LeftButton:
                # Update image properties upon release
                properties["position"] = image_label.pos()
                properties["size"] = image_label.size()
                properties["resizing"] = False


