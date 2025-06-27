from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMenu,
)
from PyQt5.QtGui import QGuiApplication, QPixmap ,QPen , QPainterPath
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor

class Canvas(QFrame):
    """
    The main interactive canvas for the flowsheet editor.

    What it does:
        - Provides a workspace for users to visually build, edit, and connect process units.
        - Supports drag-and-drop, zooming, panning, selection, resizing, and connection of units.
        - Manages all graphical elements and user interactions for flowsheet design.

    How:
        - Inherits from QFrame and manages its own widgets, drawing, and event handling.
        - Stores all process units and connections in internal dictionaries and lists.
        - Handles mouse, keyboard, and drag-and-drop events to provide a rich, interactive experience.
    """

    def __init__(self, parent=None):
        """
        Initializes the Canvas widget.

        What it does:
            - Sets up the user interface and enables drag-and-drop for process units.
            - Initializes all attributes for managing images, zoom, grid, panning, and connections.

        How:
            - Calls setupUI() to create control buttons and layouts.
            - Prepares dictionaries and variables for image and connection management.
            - Gets the screen size for scaling and layout purposes.
        """
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setupUI()
        self.images = {}
        self.active_image = None
        self.scaleFactor = 1.0
        self.gridVisible = True
        self.adjust_mode = False
        self.last_pan_point = None
        self.connecting = False
        self.connection_start = None
        self.connection_preview_pos = None
        self.connections = []  # Each: {'start': widget, 'end': widget, 'type': 'data'|'action', 'label': str, 'port': int}
        self.grid_offset = QPoint(0, 0)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.selected_connection = None  # Track selected connection

    def setupUI(self):
        """
        Sets up the user interface controls for the canvas.

        What it does:
            - Creates and arranges the main control buttons (zoom in, zoom out, reset, adjust) at the top of the canvas.
            - Ensures controls are visually consistent and accessible.

        How:
            - Uses a vertical layout for the main widget.
            - Adds a horizontal layout for the buttons.
            - Calls createButton to make styled buttons and adds them to the layout.
        """
        main_layout = QVBoxLayout(self)
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
        main_layout.addStretch(1)

    def createButton(self, text, handler, checkable=False):
        """
        Utility method to create modern, padded, and themed buttons.

        What it does:
            - Creates a QPushButton with a modern style and connects it to a handler function.
            - Optionally makes the button checkable (toggleable) for modes like adjust/pan.

        How:
            - Sets button size, style, and click handler.
            - Applies a custom stylesheet for appearance.
        """
        button = QPushButton(text)
        button.setFixedSize(80, 32)
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

        What it does:
            - Allows users to drag process unit images onto the canvas.
            - Each dropped image is wrapped in a QWidget with a label for easy identification.
            - Images are scaled and centered at the drop location.
            - Stores all properties for later manipulation and interaction.

        How:
            - Loads the image from the drag event.
            - Creates a QLabel for the image and another for the text label.
            - Combines them in a QWidget with a vertical layout.
            - Calculates the logical position (independent of zoom/pan).
            - Stores all properties in the images dictionary.
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

        What it does:
            - Changes the displayed size of an image after it has been dropped on the canvas.
            - Updates the internal metadata to reflect the new size.

        How:
            - Looks up the original pixmap for the image.
            - Calculates the new width and height using the scale factor.
            - Scales the pixmap smoothly and updates the QLabel.
            - Updates the 'size' property in the images dictionary.
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

        What it does:
            - Visually highlights an image label, e.g., to indicate selection or focus.

        How:
            - Sets the QLabel's stylesheet to use the specified color for its border.
        """
        label.setStyleSheet(f"border: 2px solid {color.name()};")

    def dragEnterEvent(self, event):
        """
        Handles drag enter event to accept image drops.

        What it does:
            - Allows the canvas to accept PNG images dragged from outside.

        How:
            - Checks the mime type of the dragged data.
            - Calls acceptProposedAction() if the data is a PNG image.
        """
        if event.mimeData().hasFormat("image/png"):
            event.acceptProposedAction()

    def createImageLabel(self, pixmap, position):
        """
        Utility method to create image labels.

        What it does:
            - Creates a QLabel to display an image at a given position.
            - Ensures images are always visible and on top.

        How:
            - Sets the pixmap, moves the label, shows it, and raises it above other widgets.
        """
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        image_label.move(position)
        image_label.show()
        image_label.raise_()
        return image_label

    def mousePressEvent(self, event):
        """
        Handles mouse press events for selection, resizing, panning, and connection.

        What it does:
            - Selects or deselects images.
            - Initiates resizing of images if a resize corner is clicked.
            - Handles right-click to show the context menu for images or connections.
            - Handles panning if adjust mode is active.
            - Handles connection creation between process units.

        How:
            - If in adjust mode and left mouse button is pressed, starts panning.
            - Otherwise, checks if an image or connection was clicked.
            - If right-click, shows the context menu for that image or connection.
            - If left-click, selects the image, highlights it, and prepares for move/resize.
            - If connecting, handles connection logic between units.
        """

        # --- Check if right-click is on a connection ---
        if event.button() == Qt.RightButton:
            clicked_conn = self.connection_at(event.pos())
            if clicked_conn:
                self.selected_connection = clicked_conn
                self.showConnectionContextMenu(event)
                return

        if self.connecting:
            for container in self.images:
                if container.geometry().contains(event.pos()) and container != self.connection_start:
                    # --- Simulink-style connection logic ---
                    start_props = self.images[self.connection_start]
                    end_props = self.images[container]

                    # Default: solid data line
                    conn_type = 'data'
                    label = ''
                    port = 0
                    total_ports = 1

                    # If block logic for action/dashed lines
                    if start_props.get("text_label") and "if" in start_props["text_label"].text().lower():
                        conn_type = 'action'
                        # Cycle through output ports for If block
                        port = len([c for c in self.connections if c['start'] == self.connection_start])
                        total_ports = 3
                        if port == 0:
                            label = "if(u1 > 0)"
                        elif port == 1:
                            label = "elseif(u2 > 0)"
                        else:
                            label = "else"

                    self.connections.append({
                        'start': self.connection_start,
                        'end': container,
                        'type': conn_type,
                        'label': label,
                        'port': port,
                        'total_ports': total_ports
                    })

                    self.connecting = False
                    self.connection_start = None
                    self.connection_preview_pos = None
                    self.setCursor(Qt.ArrowCursor)
                    self.update()
                    return
            # If not clicked on another object, cancel connection
            self.connecting = False
            self.connection_start = None
            self.connection_preview_pos = None
            self.setCursor(Qt.ArrowCursor)
            self.update()
            return

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
        Handles mouse move events for moving, resizing, panning, and connection preview.

        What it does:
            - Moves or resizes the selected image as the mouse moves.
            - Handles panning if adjust mode is active.
            - Updates connection preview line if connecting.

        How:
            - If in adjust mode and panning, updates the grid offset and all image positions.
            - If an image is selected, moves or resizes it based on the mouse position and updates its logical position.
            - If connecting, updates the preview line position.
        """
        if self.connecting and self.connection_start:
            self.connection_preview_pos = event.pos()
            self.update()
            return


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
                    self.update()

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release events to finalize actions.

        What it does:
            - Finalizes resizing or image position.
            - Resets selection and border color.
            - Ends panning if in adjust mode.

        How:
            - If in adjust mode, ends panning.
            - Otherwise, updates the logical position of the image and resets selection/border color.
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

        What it does:
            - Checks if the mouse is within a small area at each corner of the image’s geometry.
            - Returns the corner name if the mouse is within a corner region.

        How:
            - Uses QRect to define the clickable area for each corner.
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

        What it does:
            - Adjusts the geometry and pixmap of the image label based on mouse movement and which corner is being dragged.
            - Allows users to resize process units interactively.

        How:
            - Sets the appropriate corner of the image’s rectangle to the new mouse position.
            - Updates the pixmap to match the new size.
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
        Handles key press events for keyboard shortcuts.

        What it does:
            - Zooms in/out on '+'/'-' key press.
            - Passes other key events to the base class.

        How:
            - Calls zoomIn or zoomOut on '+' or '-' key presses.
            - Calls the superclass handler for other keys.
        """
        if event.key() == Qt.Key_Plus:
            self.zoomIn()
        elif event.key() == Qt.Key_Minus:
            self.zoomOut()
        else:
            super().keyPressEvent(event)
    
    def connect_line(self, image_label):
        """
        Initiates a connection line from the selected image.

        What it does:
            - Starts a connection line from the center of the selected image.
            - Prepares to draw a preview line as the mouse moves.

        How:
            - Sets connecting to True and stores the start position.
            - Updates the cursor to indicate a connection is being made.
        """
        if image_label in self.images:
            self.connecting = True
            self.connection_start = image_label
            self.connection_preview_pos = None
            self.setCursor(Qt.CrossCursor)
            self.update()

    def zoomIn(self):
        """
        Zooms in by increasing the scale factor.

        What it does:
            - Enlarges all images (process units) and the grid, allowing for detailed editing and alignment.
            - Maintains the relative positions and sizes of all elements for a consistent user experience.

        How:
            - Multiplies the current scaleFactor by a fixed ratio (1.1).
            - Calls updateImageScaling() to recalculate and apply new positions and sizes for all images.
            - Triggers a repaint of the canvas to reflect the new zoom level.
        """
        self.scaleFactor *= 1.1
        self.updateImageScaling()
        self.update()

    def zoomOut(self):
        """
        Zooms out by decreasing the scale factor.

        What it does:
            - Reduces the scale of all process unit images and the alignment grid on the canvas.
            - Provides a wider view of the flowsheet, allowing the user to see more of the workspace at once.
            - Maintains the relative positions and proportions of all elements, so the layout remains consistent.
            - Ensures that all interactive features (drag, drop, connect, etc.) continue to work seamlessly at the new zoom level.

        How:
            - Divides the current scaleFactor by a fixed ratio (1.1), making all elements smaller.
            - Calls updateImageScaling() to recalculate the screen positions and sizes of all process units and their labels based on the new scale.
            - Triggers a repaint of the canvas to visually update the grid, images, and connections at the new zoom level.
            - Keeps the logical positions of all objects unchanged, so zooming does not affect the underlying data or connections.
        """
        self.scaleFactor /= 1.1
        self.updateImageScaling()
        self.update()

    def resetView(self):
        """
        Adjusts the view so all objects are visible within the canvas.

        What it does:
            - Calculates the bounding box of all images and fits them to the view.
            - Adds a margin for better appearance.
            - Useful for quickly locating all elements after extensive editing or navigation.

        How:
            - Finds the bounding rectangle of all images in logical coordinates.
            - Computes a scale and offset to fit everything with a margin.
            - Calls updateImageScaling() and triggers a repaint to apply the new view.
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

        What it does:
            - Ensures that all process units and their labels are correctly positioned and sized after zooming or panning.
            - Maintains visual consistency and alignment on the canvas.

        How:
            - Iterates through all images, recalculating their screen positions and sizes from logical coordinates.
            - Scales the pixmap and updates the QLabel and container widget accordingly.
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
        Handles all custom drawing on the canvas, including the grid and connection lines.

        What it does:
            - Draws the alignment grid and all connection lines between process units.
            - Renders connection labels and arrowheads for clarity.
            - Shows a preview line when the user is in the process of connecting units.

        How:
            - Uses QPainter to render the grid and all connection paths.
            - Applies different styles for data and action connections.
            - Draws labels and arrowheads at appropriate positions.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        self.drawGrid(painter)
        for conn in self.connections:
            start = conn['start']
            end = conn['end']
            conn_type = conn.get('type', 'data')
            label = conn.get('label', '')
            port = conn.get('port', 0)
            total_ports = conn.get('total_ports', 1)

            start_rect = start.geometry()
            end_rect = end.geometry()

            start_pos = (start_rect.right(), start_rect.top() + start_rect.height() // 2)
            end_pos = (end_rect.left(), end_rect.top() + end_rect.height() // 2)

            offset = 24
            gap = 60  # Large enough to always clear the blocks

            path = QPainterPath()
            path.moveTo(*start_pos)

            if start_pos[0] < end_pos[0] - offset:
                # Standard left-to-right
                p1 = (start_pos[0] + offset, start_pos[1])
                p2 = (end_pos[0] - offset, end_pos[1])
                if abs(start_pos[1] - end_pos[1]) < 2 * offset:
                    path.lineTo(*p1)
                    path.lineTo(p1[0], end_pos[1])
                    path.lineTo(*p2)
                else:
                    mid_y = (start_pos[1] + end_pos[1]) // 2
                    path.lineTo(*p1)
                    path.lineTo(p1[0], mid_y)
                    path.lineTo(p2[0], mid_y)
                    path.lineTo(*p2)
                path.lineTo(*end_pos)
                arrow_from = p2
            else:
                # Loopback or feedback
                # Always go above both blocks if possible
                top = min(start_rect.top(), end_rect.top())
                p1 = (start_pos[0] + offset, start_pos[1])
                p2 = (p1[0], top - gap)
                p3 = (end_rect.left() - gap, p2[1])
                p4 = (p3[0], end_pos[1])
                p5 = (end_pos[0] - offset, end_pos[1])
                path.lineTo(*p1)
                path.lineTo(*p2)
                path.lineTo(*p3)
                path.lineTo(*p4)
                path.lineTo(*p5)
                path.lineTo(*end_pos)
                arrow_from = p5

            pen = QPen(QColor(0, 120, 255), 3)
            if conn_type == 'action':
                pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            self.draw_arrow(painter, arrow_from, end_pos)
            if label:
                painter.setPen(QColor(0,0,0))
                painter.drawText(start_pos[0]+10, start_pos[1]-10, label)

         # Draw preview line if connecting
        if self.connecting and self.connection_start and self.connection_preview_pos:
            start_rect = self.connection_start.geometry()
            start_pos = (start_rect.right(), start_rect.top() + start_rect.height() // 2)
            end_pos = (self.connection_preview_pos.x(), self.connection_preview_pos.y())
            offset = 34
            gap = 60
            path = QPainterPath()
            path.moveTo(*start_pos)
            if start_pos[0] < end_pos[0] - offset:
                p1 = (start_pos[0] + offset, start_pos[1])
                p2 = (end_pos[0] - offset, end_pos[1])
                if abs(start_pos[1] - end_pos[1]) < 2 * offset:
                    path.lineTo(*p1)
                    path.lineTo(p1[0], end_pos[1])
                    path.lineTo(*p2)
                else:
                    mid_y = (start_pos[1] + end_pos[1]) // 2
                    path.lineTo(*p1)
                    path.lineTo(p1[0], mid_y)
                    path.lineTo(p2[0], mid_y)
                    path.lineTo(*p2)
                path.lineTo(*end_pos)
                arrow_from = p2
            else:
                above = start_rect.top() > end_pos[1] + gap
                below = start_rect.bottom() + gap < end_pos[1]
                if above:
                    p1 = (start_pos[0] + offset, start_pos[1])
                    p2 = (p1[0], start_rect.top() - gap)
                    p3 = (end_pos[0] - gap, p2[1])
                    p4 = (p3[0], end_pos[1])
                    p5 = (end_pos[0] - offset, end_pos[1])
                    path.lineTo(*p1)
                    path.lineTo(*p2)
                    path.lineTo(*p3)
                    path.lineTo(*p4)
                    path.lineTo(*p5)
                    path.lineTo(*end_pos)
                    arrow_from = p5
                elif below:
                    p1 = (start_pos[0] + offset, start_pos[1])
                    p2 = (p1[0], start_rect.bottom() + gap)
                    p3 = (end_pos[0] - gap, p2[1])
                    p4 = (p3[0], end_pos[1])
                    p5 = (end_pos[0] - offset, end_pos[1])
                    path.lineTo(*p1)
                    path.lineTo(*p2)
                    path.lineTo(*p3)
                    path.lineTo(*p4)
                    path.lineTo(*p5)
                    path.lineTo(*end_pos)
                    arrow_from = p5
                else:
                    p1 = (start_pos[0] + offset, start_pos[1])
                    p2 = (p1[0], start_pos[1] - gap)
                    p3 = (end_pos[0] - gap, p2[1])
                    p4 = (p3[0], end_pos[1])
                    p5 = (end_pos[0] - offset, end_pos[1])
                    path.lineTo(*p1)
                    path.lineTo(*p2)
                    path.lineTo(*p3)
                    path.lineTo(*p4)
                    path.lineTo(*p5)
                    path.lineTo(*end_pos)
                    arrow_from = p5
            pen = QPen(QColor(0, 120, 255), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            self.draw_arrow(painter, arrow_from, end_pos)

    def drawGrid(self, painter):
        """
        Draws the grid lines on the canvas.

        What it does:
            - Provides a visual aid for aligning and positioning process units.
            - The grid spacing and opacity automatically adjust based on the current zoom level.

        How:
            - Uses QPainter to draw faint vertical and horizontal lines at intervals determined by scaleFactor.
            - Applies a consistent color and opacity for a subtle, non-intrusive appearance.
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
        Raises the selected image above all other images on the canvas.

        What it does:
            - Ensures the selected process unit is not visually obscured by others, especially when units overlap.
            - Improves usability by always keeping the active selection on top.

        How:
            - Calls raise_() on the selected image's container widget.
            - Calls lower() on all other image containers to maintain stacking order.
        """
        image_label.raise_()
        for label in self.images:
            if label != image_label:
                label.lower()

    def delete_image(self, image_label):
        """
        Deletes the selected image from the canvas.

        What it does:
            - Removes a process unit from the flowsheet.
            - Updates the display immediately.

        How:
            - Deletes the widget and removes its entry from the images dictionary.
            - Clears the active selection and triggers a repaint.
        """
        if image_label in self.images:
            del self.images[image_label]
            image_label.deleteLater()
            self.active_image = None
            self.update()

    def set_image_border_color(self, image_label, color):
        """
        Sets the border color for the image label.

        What it does:
            - Used for selection highlighting and visual feedback.

        How:
            - Sets the QLabel's stylesheet to use the specified color for its border.
        """
        image_label.setStyleSheet(f"border: 2px solid {color.name()}; border-radius: 0px;")

    def showContextMenu(self, event, image_label):
        """
        Shows a modern context menu next to the right-clicked image for multiple actions.

        What it does:
            - Provides user actions such as Delete and Connect Line for the selected process unit.
            - Uses a custom-styled menu for a modern, visually appealing interface.

        How:
            - Creates a QMenu with relevant actions and separators.
            - Applies a custom stylesheet for appearance.
            - Executes the selected action based on user choice.
        """
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        connect_line = menu.addAction("Connect Line")

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
        elif action == connect_line:
            self.connect_line(image_label)
       

    def toggleAdjustMode(self):
        """
        Toggles the adjust (pan) mode for the canvas.

        What it does:
            - Allows the user to pan (move) the entire flowsheet by dragging the canvas.
            - Disables zoom and reset controls while in adjust mode to prevent conflicts.
            - Changes the mouse cursor to indicate panning is active.

        How:
            - Flips the boolean flag self.adjust_mode.
            - If enabling adjust mode:
                - Sets the cursor to an open hand (Qt.OpenHandCursor) to indicate panning.
                - Disables the zoom in, zoom out, and reset view buttons.
                - Checks the adjust button to show it's active.
            - If disabling adjust mode:
                - Restores the cursor to the default arrow.
                - Enables the zoom and reset buttons.
                - Unchecks the adjust button.
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

    def get_port_pos(self, widget, side, port_idx=0, total_ports=1):
        """
        Calculates the position of a connection port on a unit.

        What it does:
            - Supports multi-port units for advanced flowsheet logic.
            - Used for precise connection line placement.

        How:
            - Computes the position of the port based on the widget geometry, side, and port index.
        """
        rect = widget.geometry()
        if side == 'left':
            y = rect.top() + int((rect.height()/(total_ports+1)) * (port_idx+1))
            return rect.left(), y
        elif side == 'right':
            y = rect.top() + int((rect.height()/(total_ports+1)) * (port_idx+1))
            return rect.right(), y
        elif side == 'bottom':
            x = rect.left() + int((rect.width()/(total_ports+1)) * (port_idx+1))
            return x, rect.bottom()
        return rect.center().x(), rect.center().y()

    def draw_arrow(self, painter, p1, p2):
        """
        Draws an arrow at the end of a connection line.

        What it does:
            - Visual indication of flow direction between units.
            - Consistent arrow style for all connections.

        How:
            - Calculates the angle between two points and draws a filled arrowhead at the end.
        """
        import math
        angle = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        arrow_size = 12
        dx = arrow_size * math.cos(angle - math.pi/6)
        dy = arrow_size * math.sin(angle - math.pi/6)
        dx2 = arrow_size * math.cos(angle + math.pi/6)
        dy2 = arrow_size * math.sin(angle + math.pi/6)
        points = [
            QPoint(p2[0], p2[1]),
            QPoint(int(p2[0] - dx), int(p2[1] - dy)),
            QPoint(int(p2[0] - dx2), int(p2[1] - dy2)),
        ]
        painter.setBrush(QColor(0, 120, 255))
        painter.drawPolygon(*points)

    def connection_at(self, pos):
        """
        Returns the connection under the mouse position, if any.

        What it does:
            - Enables right-click selection and deletion of connection lines.
            - Supports hit-testing for interactive editing.

        How:
            - Checks if the mouse position is near any connection path or segment.
        """
        threshold = 8  # pixels
        for conn in self.connections:
            path = self.connection_path(conn)
            if path and path.contains(QPointF(pos)):
                return conn
            # Fallback: check distance to each segment
            points = [p for p in self.connection_path_points(conn)]
            for i in range(len(points)-1):
                if self.point_near_line(pos, points[i], points[i+1], threshold):
                    return conn
        return None

    def connection_path(self, conn):
        """
        Returns a QPainterPath representing the visual path of a connection line between two process units.

        What it does:
            - Computes the exact path used to visually render a connection line between two units on the canvas.
            - Used for both drawing the connection in paintEvent and for hit-testing (detecting if the user clicked near a connection).
            - Supports both standard (left-to-right, straight or elbow) and loopback (feedback) connections, adapting the path shape accordingly.
            - Ensures that connections visually avoid overlapping units and maintain a clear, readable flowsheet layout.

        How:
            - Retrieves the geometry of the start and end widgets (process units) from the connection dictionary.
            - Determines the appropriate start and end points for the connection, typically at the right edge of the start unit and the left edge of the end unit.
            - Calculates intermediate control points for the path:
                - For standard connections (start to the left of end), creates a path with horizontal and vertical segments, using offsets to avoid overlapping units and to create elbow-style lines.
                - For loopback or feedback connections (start to the right of end), creates a path that loops above the units, with multiple control points to ensure the line does not intersect the units.
            - Uses QPainterPath to construct the path by moving to the start point and adding line segments through all calculated control points to the end point.
            - Returns the completed QPainterPath, which can be used for both drawing and hit-testing.

        Parameters:
            conn (dict): A dictionary containing connection information, including 'start' and 'end' widgets, connection 'type', and port information.

        Returns:
            QPainterPath: The path object representing the connection line between the two units.
        """
        from PyQt5.QtGui import QPainterPath
        start = conn['start']
        end = conn['end']
        conn_type = conn.get('type', 'data')
        port = conn.get('port', 0)
        total_ports = conn.get('total_ports', 1)
        start_rect = start.geometry()
        end_rect = end.geometry()
        start_pos = (start_rect.right(), start_rect.top() + start_rect.height() // 2)
        end_pos = (end_rect.left(), end_rect.top() + end_rect.height() // 2)
        offset = 24
        gap = 60
        path = QPainterPath()
        path.moveTo(*start_pos)
        if start_pos[0] < end_pos[0] - offset:
            p1 = (start_pos[0] + offset, start_pos[1])
            p2 = (end_pos[0] - offset, end_pos[1])
            if abs(start_pos[1] - end_pos[1]) < 2 * offset:
                path.lineTo(*p1)
                path.lineTo(p1[0], end_pos[1])
                path.lineTo(*p2)
            else:
                mid_y = (start_pos[1] + end_pos[1]) // 2
                path.lineTo(*p1)
                path.lineTo(p1[0], mid_y)
                path.lineTo(p2[0], mid_y)
                path.lineTo(*p2)
            path.lineTo(*end_pos)
        else:
            top = min(start_rect.top(), end_rect.top())
            p1 = (start_pos[0] + offset, start_pos[1])
            p2 = (p1[0], top - gap)
            p3 = (end_rect.left() - gap, p2[1])
            p4 = (p3[0], end_pos[1])
            p5 = (end_pos[0] - offset, end_pos[1])
            path.lineTo(*p1)
            path.lineTo(*p2)
            path.lineTo(*p3)
            path.lineTo(*p4)
            path.lineTo(*p5)
            path.lineTo(*end_pos)
        return path

    def connection_path_points(self, conn):
        
        """
        Returns a list of points (tuples) along the connection path.
    
        What it does:
            - Provides the exact coordinates of all key points (corners and endpoints) that make up the visual path of a connection line between two process units.
            - Used for hit-testing (detecting if the user clicked near a connection) and for precise interaction, such as selecting or editing a connection line.
            - Ensures that all segments of the connection path can be checked for proximity to the mouse or other objects, supporting robust user interaction.
    
        How:
            - Retrieves the geometry of the start and end widgets (process units) from the connection dictionary.
            - Determines the appropriate start and end points for the connection, typically at the right edge of the start unit and the left edge of the end unit.
            - Calculates all intermediate control points that define the path:
                - For standard connections (start to the left of end), adds points for horizontal and vertical segments, including elbows if needed.
                - For loopback or feedback connections (start to the right of end), adds multiple points to create a looping path above the units, ensuring the line does not intersect the units.
            - Returns a list of all these points (as tuples), in the order they appear along the path, so each segment can be individually checked or drawn.
        """
        start = conn['start']
        end = conn['end']
        start_rect = start.geometry()
        end_rect = end.geometry()
        start_pos = (start_rect.right(), start_rect.top() + start_rect.height() // 2)
        end_pos = (end_rect.left(), end_rect.top() + end_rect.height() // 2)
        offset = 24
        gap = 60
        points = [start_pos]
        if start_pos[0] < end_pos[0] - offset:
            p1 = (start_pos[0] + offset, start_pos[1])
            p2 = (end_pos[0] - offset, end_pos[1])
            if abs(start_pos[1] - end_pos[1]) < 2 * offset:
                points += [p1, (p1[0], end_pos[1]), p2]
            else:
                mid_y = (start_pos[1] + end_pos[1]) // 2
                points += [p1, (p1[0], mid_y), (p2[0], mid_y), p2]
            points.append(end_pos)
        else:
            top = min(start_rect.top(), end_rect.top())
            p1 = (start_pos[0] + offset, start_pos[1])
            p2 = (p1[0], top - gap)
            p3 = (end_rect.left() - gap, p2[1])
            p4 = (p3[0], end_pos[1])
            p5 = (end_pos[0] - offset, end_pos[1])
            points += [p1, p2, p3, p4, p5, end_pos]
        return points

    def point_near_line(self, pt, p1, p2, threshold):
        """
        Returns True if pt (QPoint) is within threshold pixels of the line segment p1-p2.

        What it does:
            - Supports accurate selection of connection lines for editing.

        How:
            - Calculates the perpendicular distance from pt to the line segment and compares to threshold.
        """
        from PyQt5.QtCore import QPoint
        import math
        x0, y0 = pt.x(), pt.y()
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx == dy == 0:
            return math.hypot(x0 - x1, y0 - y1) <= threshold
        t = max(0, min(1, ((x0-x1)*dx + (y0-y1)*dy) / (dx*dx + dy*dy)))
        proj_x = x1 + t*dx
        proj_y = y1 + t*dy
        return math.hypot(x0 - proj_x, y0 - proj_y) <= threshold

    def showConnectionContextMenu(self, event):
        """
        Shows a context menu for a selected connection (line).

        What it does:
            - Allows users to delete connection lines via right-click.
            - Modern, styled menu for consistency with unit context menus.

        How:
            - Creates a QMenu with a Delete Line action.
            - Shows the menu at the mouse's global position.
            - Removes the connection if Delete Line is selected.
        """
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Line")
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
        """)
        action = menu.exec_(event.globalPos())
        if action == delete_action and self.selected_connection:
            self.connections.remove(self.selected_connection)
            self.selected_connection = None
            self.update()