from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QCursor

class Canvas(QFrame):
    def __init__(self, parent=None):
        """
        Initializes the Canvas widget.
        - Sets up the UI.
        - Initializes attributes for managing images.
        """
        super().__init__(parent)
        self.setAcceptDrops(True)  # Allows dropping images onto the canvas
        self.setupUI()  # Sets up the user interface
        self.images = {}  # Dictionary to store images and their properties
        self.active_image = None  # Currently selected image label
        self.scaleFactor = 1.0  # Zoom level
        self.gridVisible = True  # Flag to control grid visibility

    def setupUI(self):
        """
        Sets up the user interface.
        - Creates zoom buttons.
        """
        main_layout = QVBoxLayout(self)  # Main vertical layout
        zoom_buttons_layout = QHBoxLayout()  # Layout for zoom buttons
        zoom_in_button = self.createButton("+", self.zoomIn)  # Button to zoom in
        zoom_out_button = self.createButton("-", self.zoomOut)  # Button to zoom out
        reset_view_button = self.createButton("Reset", self.resetView)  # Button to reset zoom
        zoom_buttons_layout.addWidget(zoom_in_button)
        zoom_buttons_layout.addWidget(zoom_out_button)
        zoom_buttons_layout.addWidget(reset_view_button)
        zoom_buttons_layout.addStretch(1)  # Align buttons to the right
        main_layout.addLayout(zoom_buttons_layout)
        main_layout.addStretch(1)  # Stretch to expand layout

    def createButton(self, text, handler):
        """
        Utility method to create buttons.
        """
        button = QPushButton(text)
        button.setFixedSize(60, 30)
        button.clicked.connect(handler)
        button.setStyleSheet("border: 2px solid black; background-color: white;")
        return button

    def dragEnterEvent(self, event):
        """
        Handles drag enter event to accept image drops.
        """
        if event.mimeData().hasFormat("image/png"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """
        Handles drop event to add dropped images to the canvas.
        - Loads dropped image and creates a QLabel to display it.
        - Stores image properties in the dictionary.
        """
        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            image = QPixmap()
            image.loadFromData(byte_array)

            position = event.pos() - QPoint(int(image.width() / 2), int(image.height() / 2))

            image_label = QLabel(self)
            image_label.setPixmap(image)
            self.set_image_border_color(image_label, QColor("black"))  # Set the default border color
            image_label.move(position)
            image_label.show()

            self.images[image_label] = {
                "position": position,
                "size": image.size(),
                "resizing": False,
                "resizing_offset": QPoint(),
                "resize_corner": None,
                "pixmap": image,
            }

    def createImageLabel(self, pixmap, position):
        """
        Utility method to create image labels.
        """
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        image_label.move(position)
        image_label.show()
        image_label.raise_()  # Raise the image label to place it on top of the grid
        return image_label

    def mousePressEvent(self, event):
        """
        Handles mouse press event.
        - Selects/deselects images.
        - Initiates resizing of images.
        """
        for image_label in self.images:
            if image_label.geometry().contains(event.pos()):
                if event.button() == Qt.RightButton:
                    self.showDeleteButton(event, image_label)  # Show delete button on right-click
                    return

                if self.active_image is not None:
                    self.set_image_border_color(self.active_image, QColor("black"))
                self.active_image = image_label
                self.raise_image(image_label)
                properties = self.images[image_label]
                properties["current_image_offset"] = event.pos() - properties["position"]
                self.set_image_border_color(image_label, QColor("red"))  # Highlight the selected image

                # Check if resizing is initiated by clicking on a resize corner
                if resize_corner := self.get_resize_corner(event.pos(), image_label):
                    properties["resizing"] = True
                    properties["resize_corner"] = resize_corner
                    properties["resizing_offset"] = event.pos() - properties["position"]
                break

    def mouseMoveEvent(self, event):
        """
        Handles mouse move event.
        - Moves or resizes the selected image.
        """
        if self.active_image is not None:
            properties = self.images[self.active_image]
            if properties["resizing"]:
                self.resize_image(event.pos(), properties)  # Resize the image
            else:
                if event.buttons() == Qt.LeftButton:
                    self.active_image.move(event.pos() - properties["current_image_offset"])
                    self.raise_image(self.active_image)

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release event.
        - Finalizes resizing or image position.
        """
        if self.active_image is not None:
            properties = self.images[self.active_image]
            if properties["resizing"]:
                properties["resizing"] = False
                properties["size"] = self.active_image.pixmap().size()
                properties["position"] = self.active_image.pos()
            else:
                properties["position"] = self.active_image.pos()
            self.set_image_border_color(self.active_image, QColor("black"))  # Reset the border color
            self.active_image = None

    def get_resize_corner(self, pos, image_label):
        """
        Determines which resize corner is clicked.
        """
        rect = image_label.geometry()
        corner_size = 10
        if QRect(rect.x(), rect.y(), corner_size, corner_size).contains(pos):
            return "top_left"
        elif QRect(rect.x() + rect.width() - corner_size, rect.y(), corner_size, corner_size).contains(pos):
            return "top_right"
        elif QRect(rect.x(), rect.y() + rect.height() - corner_size, corner_size, corner_size).contains(pos):
            return "bottom_left"
        elif QRect(rect.x() + rect.width() - corner_size, rect.y() + rect.height() - corner_size, corner_size, corner_size).contains(pos):
            return "bottom_right"
        return None

    def resize_image(self, pos, properties):
        """
        Resizes the selected image.
        """
        resize_corner = properties["resize_corner"]
        rect = self.active_image.geometry()
        new_rect = rect

        if resize_corner == "top_left":
            new_rect.setTopLeft(pos - properties["resizing_offset"])
        elif resize_corner == "top_right":
            new_rect.setTopRight(pos - properties["resizing_offset"])
        elif resize_corner == "bottom_left":
            new_rect.setBottomLeft(pos - properties["resizing_offset"])
        elif resize_corner == "bottom_right":
            new_rect.setBottomRight(pos - properties["resizing_offset"])
            self.active_image.setGeometry(new_rect)
            scaled_pixmap = properties["pixmap"].scaled(new_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.active_image.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        """
        Handles key press events.
        - Zooms in/out on '+'/'-' key press.
        """
        if event.key() == Qt.Key_Plus:
            self.zoomIn()
        elif event.key() == Qt.Key_Minus:
            self.zoomOut()
        else:
            super().keyPressEvent(event)

    def zoomIn(self):
        """
        Zooms in by increasing the scale factor.
        """
        self.scaleFactor *= 1.1
        self.updateImageScaling()
        self.update()

    def zoomOut(self):
        """
        Zooms out by decreasing the scale factor.
        """
        self.scaleFactor /= 1.1
        self.updateImageScaling()
        self.update()

    def resetView(self):
        """
        Resets the view to the original zoom level.
        """
        self.scaleFactor = 1.0
        for image_label, properties in self.images.items():
            original_size = properties["size"]
            original_position = properties["position"]
            pixmap = properties["pixmap"]
            image_label.setPixmap(pixmap)
            image_label.setGeometry(
                original_position.x(),
                original_position.y(),
                original_size.width(),
                original_size.height(),
            )
        self.update()

    def updateImageScaling(self):
        """
        Updates the size and position of images based on the current scale factor.
        """
        for image_label, properties in self.images.items():
            scaled_pixmap = properties["pixmap"].scaled(
                properties["size"] * self.scaleFactor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            new_size = scaled_pixmap.size()
            new_position = properties["position"] * self.scaleFactor

            # Update image size and position
            image_label.setGeometry(
                new_position.x(),
                new_position.y(),
                new_size.width(),
                new_size.height(),
            )

            image_label.setPixmap(scaled_pixmap)

    def paintEvent(self, event):
        """
        Draws the grid on the canvas.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.scale(self.scaleFactor, self.scaleFactor)
        self.drawGrid(painter)

    def drawGrid(self, painter):
        """
        Draws the grid lines on the canvas.
        """
        grid_color = QColor(60, 70, 80)
        grid_opacity = 0.2
        start_x, start_y, grid_spacing = 0, 0, 20

        painter.save()
        painter.setPen(grid_color.lighter(90))
        painter.setOpacity(grid_opacity)

        for x in range(start_x, 1000000, grid_spacing):
            painter.drawLine(x, 0, x, 1000000)

        for y in range(start_y, 1000000, grid_spacing):
            painter.drawLine(0, y, 1000000, y)

        painter.restore()

    def raise_image(self, image_label):
        """
        Raises the selected image above other images.
        """
        image_label.raise_()
        for label in self.images:
            if label != image_label:
                label.lower()

    def delete_image(self, image_label):
        """
        Deletes the selected image from the canvas.
        """
        if image_label in self.images:
            del self.images[image_label]
            image_label.deleteLater()
            self.active_image = None
            self.update()

    def set_image_border_color(self, image_label, color):
        """
        Sets the border color for the image label.
        """
        image_label.setStyleSheet(f"border: 2px solid {color.name()}; border-radius: 0px;")

    def showDeleteButton(self, event, image_label):
        """
        Shows a delete button near the cursor for deleting an image.
        """
        # Create and position the delete button
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: red; color: white;")
        delete_button.clicked.connect(lambda: self.delete_image(image_label))

        button_pos = event.globalPos() + QPoint(20, 20)  # Offset to position the button near the cursor
        delete_button.move(self.mapFromGlobal(button_pos))
        delete_button.show()

        # Create a custom event to remove the button when it loses focus
        class DeleteButtonFocusOutEvent(QEvent):

            def __init__(self, delete_button):
                super().__init__(QEvent.FocusOut)
                self.delete_button = delete_button

            def remove_button(self):
                self.delete_button.deleteLater()

        def focus_out_event_handler(event):
            if event.type() == QEvent.FocusOut:
                custom_event = DeleteButtonFocusOutEvent(delete_button)
                custom_event.remove_button()

        delete_button.focusOutEvent = focus_out_event_handler
