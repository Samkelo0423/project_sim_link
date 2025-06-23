from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QGridLayout, QPushButton, QWidget
)
import os
from PyQt5.QtCore import Qt
from UI_Interface.image_palette_items import DraggableImageLabel

class CollapsibleSection(QWidget):
    """
    A collapsible section with a button and a content widget (image grid).
    """
    def __init__(self, title, image_paths, num_columns=4, font_weight="bold", parent=None):
        super().__init__(parent)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        # Modern flat grey style with customizable font weight and padding
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #e0e0e0;   /* Light grey */
                color: #111;                 /* Black text */
                border: 1.5px solid;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: {font_weight};
                letter-spacing: 1px;
                margin-left: 1px;
                margin-right: 1px;
                margin-top: 6px;
            }}
            QPushButton:hover {{
                background-color: #cccccc;   /* Slightly darker grey */
                color: #111;
                border: 1.5px solid #9e9e9e;
            }}
            QPushButton:pressed, QPushButton:checked {{
                background-color: #757575;   /* Medium/dark grey */
                color: #fff;
                border: 1.5px solid #616161;
            }}
        """)
        self.toggle_button.clicked.connect(self.toggle_content)

        # Content widget (image grid)
        self.content_widget = QWidget()
        self.content_layout = QGridLayout()
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setVisible(False)

        # Add images to the grid
        image_width = int(60 * 0.80)
        image_height = int(60 * 0.80)
        for i, path in enumerate(image_paths):
            row = i // num_columns
            col = i % num_columns
            label = DraggableImageLabel(path)
            label.setFixedSize(image_width, image_height)
            label.setStyleSheet("border: 2px solid; border-radius: 0px; background: white;")
            self.content_layout.addWidget(label, row, col)

        # Main layout with horizontal padding
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(8, 0, 8, 0)  # left, top, right, bottom
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

    def toggle_content(self):
        self.content_widget.setVisible(self.toggle_button.isChecked())

class Palette(QFrame):
    """
    Tool palette frame with collapsible categories for draggable image icons.
    Categories and images are auto-detected from subfolders in Image_Icons.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Base directory for images
        base_dir = os.path.dirname(__file__)
        image_icons_dir = os.path.abspath(os.path.join(base_dir, "..", "Image_Icons"))

        # List all subfolders (categories)
        for category in sorted(os.listdir(image_icons_dir)):
            category_path = os.path.join(image_icons_dir, category)
            if os.path.isdir(category_path):
                # List all image files in the category folder
                image_files = [
                    os.path.join(category_path, f)
                    for f in os.listdir(category_path)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                # Always add section, even if empty
                section = CollapsibleSection(category, image_files, num_columns=2, font_weight="600")
                main_layout.addWidget(section)
        main_layout.addStretch(1)