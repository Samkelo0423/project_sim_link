from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtCore import QPoint, Qt 
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
                "resize_corner": None
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
                    position = event.pos() + properties["resizing_offset"]

                    # Calculate the new width and height
                    new_width = abs(properties["position"].x() - position.x())
                    new_height = abs(properties["position"].y() - position.y())

                    # Adjust position and size for diagonal resizing
                    if properties["resize_corner"] in ["top_left", "bottom_right"]:

                        position.setX(min(properties["position"].x(), position.x()))
                        position.setY(min(properties["position"].y(), position.y()))

                    elif properties["resize_corner"] in ["top_right", "bottom_left"]:

                        position.setX(max(properties["position"].x(), position.x()))
                        position.setY(min(properties["position"].y(), position.y()))

                    # Resize and move the image label
                    image_label.setGeometry(

                        position.x(),
                        position.y(),
                        new_width,
                        new_height
                    )

    def mouseReleaseEvent(self, event):
        for image_label, properties in self.current_images.items():
            if event.button() == Qt.LeftButton:
                # Update image properties upon release
                properties["position"] = image_label.pos()
                properties["size"] = image_label.size()
                properties["resizing"] = False


