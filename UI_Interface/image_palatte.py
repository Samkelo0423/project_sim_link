from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
)
import os
from PyQt5.QtCore import Qt
from UI_Interface.image_palette_items import DraggableImageLabel

class Palette(QFrame):
    """
    Tool palette frame that displays draggable image icons in a grid.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """
        Initializes the tool palette UI.
        Sets frame style and populates with draggable image icons.
        """
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("background-color: lightgray; border-radius: 10px;")

        # Create and set the grid layout with image icons
        grid_layout = self.createToolPalette()
        self.setLayout(grid_layout)

    def createToolPalette(self):
        """
        Creates and returns a QGridLayout filled with DraggableImageLabel icons.
        """
        tool_palette_layout = QGridLayout()
        tool_palette_layout.setAlignment(Qt.AlignTop)

        # Use relative paths for images in the Image_Icons directory
        base_dir = os.path.dirname(__file__)
        image_dir = os.path.abspath(os.path.join(base_dir, "..", "Image_Icons"))

        # Automatically load all image files in the directory
        image_files = [
            f for f in os.listdir(image_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        image_paths = [os.path.join(image_dir, f) for f in image_files]

        num_columns = 4  # Number of columns for the tool palette
        image_width = int(60 * 0.80)
        image_height = int(60 * 0.80)

        # Add each image as a draggable label to the palette
        for i, path in enumerate(image_paths):
            row = i // num_columns
            col = i % num_columns
            label = DraggableImageLabel(path)
            label.setFixedSize(image_width, image_height)
            label.setStyleSheet("border: 2px solid black; border-radius : 0px")
            tool_palette_layout.addWidget(label, row, col)

        return tool_palette_layout





