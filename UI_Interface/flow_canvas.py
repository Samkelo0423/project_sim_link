from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMenu,
)
from PyQt5.QtGui import QGuiApplication, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QCursor
import os

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
        self.adjust_mode = False
        self.last_pan_point = None
        self.grid_offset = QPoint(0, 0)

        # Get screen size for dynamic scaling 
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

    def setupUI(self):
        """
        Sets up the user interface.
        - Creates zoom and adjust buttons on the same horizontal level.
        """
        main_layout = QVBoxLayout(self)  # Main vertical layout

        button_layout = QHBoxLayout()
        self.zoom_in_button = self.createButton("+", self.zoomIn)
        self.zoom_out_button = self.createButton("-", self.zoomOut)
        self.reset_view_button = self.createButton("Reset", self.resetView)
        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)
        button_layout.addWidget(self.reset_view_button)
        button_layout.addStretch(1)
        self.adjust_button = self.createButton("Adjust", self.toggleAdjustMode)
        button_layout.addWidget(self.adjust_button)

        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)  # Stretch to expand layout

    def createButton(self, text, handler, checkable=False):
        """
        Utility method to create modern, padded, and themed buttons.
        """
        button = QPushButton(text)
        button.setFixedSize(80, 32)  # Fixed size for consistency
        button.clicked.connect(handler)
        button.setCheckable(checkable)
        button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #222;
                border: 1.5px solid;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #cccccc;
                color: #111;
                border: 1.5px solid #9e9e9e;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #757575; 
                color: #fff;
                border: 1.5px solid #616161;
            }
        """)
        return button

    def dropEvent(self, event):
        """
        Handles drop event to add dropped images to the canvas.
        - Loads dropped image and creates a QWidget with image and label.
        - Stores image properties in the dictionary.
        """
        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            original_pixmap = QPixmap()
            original_pixmap.loadFromData(byte_array)

            # Always get the label from the mime text if available
            base_name = event.mimeData().text() or "Image"

            # Create the image label
            image_label = QLabel()
            image_label.setPixmap(original_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            self.set_image_border_color(image_label, QColor("black"))

            # Create the text label
            text_label = QLabel(base_name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("font-size: 11px; color: #333;")

            # Combine image and text in a vertical layout
            container = QWidget(self)
            container.setStyleSheet("background: transparent;")
            v_layout = QVBoxLayout(container)
            v_layout.setContentsMargins(2, 2, 2, 2)
            v_layout.setSpacing(2)
            v_layout.setAlignment(Qt.AlignHCenter)
            v_layout.addWidget(image_label, alignment=Qt.AlignHCenter)
            v_layout.addWidget(text_label, alignment=Qt.AlignHCenter)

            # Resize the image
            scale_factor = 0.80
            new_width = int(original_pixmap.width() * scale_factor)
            new_height = int(original_pixmap.height() * scale_factor)
            scaled_pixmap = original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setFixedSize(scaled_pixmap.size())

            # --- Fix: Resize the container to fit both image and label ---
            container.adjustSize()
            container_width = container.sizeHint().width()
            container_height = container.sizeHint().height()

            # Center the container based on its full size (image + label)
            position = event.pos() - QPoint(container_width // 2, container_height // 2)
            container.move(position)

            # Set the logical position for the dropped object
            logical_x = (position.x() - self.grid_offset.x()) / self.scaleFactor
            logical_y = (position.y() - self.grid_offset.y()) / self.scaleFactor
            logical_position = QPointF(logical_x, logical_y)

            self.images[container] = {
                "pixmap": original_pixmap,
                "size": scaled_pixmap.size(),
                "position": logical_position,  # <-- Use logical position here!
                "resizing_offset": QPoint(),
                "resizing": False,
                "resize_corner": None,
                "original_size": scaled_pixmap.size(),
                "original_position": logical_position,
                "image_label": image_label,
                "text_label": text_label,
            }

            container.show()

    def resizeImageAtDropEvent(self, image_label, scale_factor):
        """
        Resizes the image label based on the scale factor.
        """
        if image_label in self.images:
            data = self.images[image_label]
            original_pixmap = data["pixmap"]

            new_width = int(original_pixmap.width() * scale_factor)
            new_height = int(original_pixmap.height() * scale_factor)

            scaled_pixmap = original_pixmap.scaled(new_width, 
                                                   new_height, 
                                                   Qt.KeepAspectRatio, 
                                                   Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.resize(scaled_pixmap.size())    
            data["size"] = scaled_pixmap.size()  # Update size in metadata

    def set_image_border_color(self, label, color):
        """
        Sets the border color for the image label.
        """
        label.setStyleSheet(f"border: 2px solid {color.name()};")

    def dragEnterEvent(self, event):
        """
        Handles drag enter event to accept image drops.
        """
        if event.mimeData().hasFormat("image/png"):
            event.acceptProposedAction()

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
        if self.adjust_mode and event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.last_pan_point = event.pos()
            return

        for container in self.images:
            if container.geometry().contains(event.pos()):
                

                # If right-click, show context menu
                if event.button() == Qt.RightButton:
                    self.showContextMenu(event, container)
                    return

                self.active_image = container
                self.raise_image(container)
                properties = self.images[container]

                # Adjust the offset for zoom
                mouse_logical_position = (event.pos() - self.grid_offset) / self.scaleFactor
                properties["current_image_offset"] = mouse_logical_position - properties["position"]

                # Set border color to red on select (only on the image label)
                self.set_image_border_color(properties["image_label"], QColor("red"))

                # Check if resizing is initiated by clicking on a resize corner
                if resize_corner := self.get_resize_corner(event.pos(), container):
                    properties["resizing"] = True
                    properties["resize_corner"] = resize_corner
                    properties["resizing_offset"] = (event.pos() - properties["position"]) / self.scaleFactor
                break

    def mouseMoveEvent(self, event):
        """
        Handles mouse move event.
        - Moves or resizes the selected image.
        """
        if self.adjust_mode and self.last_pan_point is not None:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.grid_offset += delta
            self.updateImageScaling()  # Move objects with the grid
            self.update()
            return

        if self.active_image is not None:
            properties = self.images[self.active_image]
            if properties["resizing"]:
                self.resize_image(event.pos(), properties)
            else:
                if event.buttons() == Qt.LeftButton:
                    # Calculate logical position for movement
                    mouse_logical_pos = (event.pos() - self.grid_offset) / self.scaleFactor
                    new_logical_pos = mouse_logical_pos - properties["current_image_offset"]
                    properties["position"] = new_logical_pos  # Update logical position

                    # Calculate new screen position
                    scaled_x = int(new_logical_pos.x() * self.scaleFactor) + self.grid_offset.x()
                    scaled_y = int(new_logical_pos.y() * self.scaleFactor) + self.grid_offset.y()
                    self.active_image.move(scaled_x, scaled_y)

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release event.
        - Finalizes resizing or image position.
        """
        if self.adjust_mode and event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.last_pan_point = None
            return

        if self.active_image is not None:
            properties = self.images[self.active_image]
            widget_pos = self.active_image.pos()
            # Subtract grid_offset before dividing by scaleFactor to get logical position
            logical_x = (widget_pos.x() - self.grid_offset.x()) / self.scaleFactor
            logical_y = (widget_pos.y() - self.grid_offset.y()) / self.scaleFactor
            logical_position = QPointF(logical_x, logical_y)
            if properties["resizing"]:
                properties["resizing"] = False
                properties["size"] = properties["original_size"]
                properties["position"] = logical_position
            else:
                properties["position"] = logical_position

            # Reset the border color to black (only on the image label)
            self.set_image_border_color(properties["image_label"], QColor("black"))
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
        Adjusts the view so all objects are visible within the canvas.
        """
        if not self.images:
            return

        # Find bounding rect of all objects (in logical coordinates)
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        for props in self.images.values():
            pos = props["position"]
            size = props["size"]
            min_x = min(min_x, pos.x())
            min_y = min(min_y, pos.y())
            max_x = max(max_x, pos.x() + size.width())
            max_y = max(max_y, pos.y() + size.height())

        # Add a margin (in logical units)
        margin = 40
        min_x -= margin
        min_y -= margin
        max_x += margin
        max_y += margin

        # Calculate the bounding box size
        bounding_width = max_x - min_x
        bounding_height = max_y - min_y

        # Get the available widget size
        canvas_width = self.width()
        canvas_height = self.height()

        # Compute the scale factor to fit all objects
        if bounding_width == 0 or bounding_height == 0:
            scale = 1.0
        else:
            scale_x = canvas_width / bounding_width
            scale_y = canvas_height / bounding_height
            scale = min(scale_x, scale_y, 1.0)  # Don't zoom in beyond 1.0

        self.scaleFactor = scale

        # Center the bounding box in the canvas
        offset_x = int((canvas_width - (bounding_width * scale)) / 2 - min_x * scale)
        offset_y = int((canvas_height - (bounding_height * scale)) / 2 - min_y * scale)
        self.grid_offset = QPoint(offset_x, offset_y)

        self.updateImageScaling()
        self.update()


    def updateImageScaling(self):
        """
        Updates the size and position of images based on the current scale factor and grid offset.
        """
        for container, properties in self.images.items():
            # Logical position and size
            original_position = properties["position"]
            original_size = properties["size"]

            # Apply scaling and grid offset
            scaled_x = int(original_position.x() * self.scaleFactor) + self.grid_offset.x()
            scaled_y = int(original_position.y() * self.scaleFactor) + self.grid_offset.y()
            scaled_width = int(original_size.width() * self.scaleFactor)
            scaled_height = int(original_size.height() * self.scaleFactor)

            # Scale the image pixmap
            scaled_pixmap = properties["pixmap"].scaled(
                scaled_width,
                scaled_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Update the image label pixmap and size
            image_label = properties["image_label"]
            image_label.setPixmap(scaled_pixmap)
            image_label.setFixedSize(scaled_pixmap.size())

            # Adjust the container size to fit both image and text
            container.adjustSize()
            container_width = container.sizeHint().width()
            container_height = container.sizeHint().height()

            # Move the container to the scaled and offset position
            container.move(scaled_x, scaled_y)

    def paintEvent(self, event):
        """
        Draws the grid on the canvas.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        self.drawGrid(painter)

    def drawGrid(self, painter):
        """
        Draws the grid lines on the canvas.
        """
        grid_color = QColor(60, 70, 80)
        grid_opacity = 0.2
        grid_spacing = int(20 * self.scaleFactor)
        offset = self.grid_offset

        painter.save()
        painter.setPen(grid_color.lighter(90))
        painter.setOpacity(grid_opacity)

        for x in range(offset.x() % grid_spacing, self.width(), grid_spacing):
            painter.drawLine(x, 0, x, self.height())

        for y in range(offset.y() % grid_spacing, self.height(), grid_spacing):
            painter.drawLine(0, y, self.width(), y)

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

    def showContextMenu(self, event, image_label):
        """
        Shows a modern context menu next to the right-clicked image for multiple actions.
        """
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        properties_action = menu.addAction("Properties")

        # Modern style: dark, rounded, with padding and clear separators
        menu.setStyleSheet("""
            QMenu {
                background-color: #232323;
                color: #fff;
                border: 1.5px solid #444;
                border-radius: 10px;
                padding: 10px 0px;
                font-size: 15px;
                min-width: 170px;
            }
            QMenu::item {
                padding: 10px 32px 10px 24px;
                background: transparent;
                margin: 2px 0px;
            }
            QMenu::item:selected {
                background-color: #444;
                color: #fff;
                border-radius: 6px;
            }
            QMenu::separator {
                height: 1px;
                background: #444;
                margin-left: 16px;
                margin-right: 16px;
            }
        """)
        # Show the context menu at the calculated position
        action = menu.exec_(event.globalPos())
        if action == delete_action:
            self.delete_image(image_label)
        elif action == duplicate_action:
            self.duplicate_image(image_label)
        elif action == properties_action:
            self.show_properties_dialog(image_label)

    def toggleAdjustMode(self):
        """
        Toggles the adjust mode on and off.
        """
        self.adjust_mode = not self.adjust_mode
        if self.adjust_mode:
            self.setCursor(Qt.OpenHandCursor)
            # Disable other buttons
            self.zoom_in_button.setDisabled(True)
            self.zoom_out_button.setDisabled(True)
            self.reset_view_button.setDisabled(True)
            self.adjust_button.setChecked(True)
        else:
            self.setCursor(Qt.ArrowCursor)
            # Enable other buttons
            self.zoom_in_button.setDisabled(False)
            self.zoom_out_button.setDisabled(False)
            self.reset_view_button.setDisabled(False)
            self.adjust_button.setChecked(False)
