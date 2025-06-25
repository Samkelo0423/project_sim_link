from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QGridLayout, QPushButton, QWidget, QLabel, QScrollArea
)
import os
from PyQt5.QtCore import Qt
from UI_Interface.image_palette_items import DraggableImageLabel

SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        background: #f0f0f0;
        width: 10px;
        margin: 2px 0 2px 0;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #bdbdbd;
        min-height: 30px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #757575;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        background: none;
        border: none;
    }
    QScrollBar:horizontal {
        background: #f0f0f0;
        height: 10px;
        margin: 0 2px 0 2px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background: #bdbdbd;
        min-width: 30px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #757575;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
        background: none;
        border: none;
    }
    QScrollBar::add-page, QScrollBar::sub-page {
        background: none;
    }
"""

class CollapsibleSection(QWidget):
    """
    A collapsible section with a button and a content widget (image grid).

    What it does:
        - Displays a section with a title button that can be expanded/collapsed.
        - Shows a grid of image icons (with labels) when expanded.
        - Used for each image category in the palette.

    How:
        - The button toggles the visibility of the content widget.
        - The content widget contains a grid of DraggableImageLabel icons and their names.
        - Layout and style are set for a modern, clean look.
    """
    def __init__(self, title, image_paths, num_columns=4, font_weight="bold", parent=None):
        super().__init__(parent)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #e0e0e0;
                color: #111;
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
                background-color: #cccccc;
                color: #111;
                border: 1.5px solid #9e9e9e;
            }}
            QPushButton:pressed, QPushButton:checked {{
                background-color: #757575;
                color: #fff;
                border: 1.5px solid #616161;
            }}
        """)
        self.toggle_button.clicked.connect(self.toggle_content)

        # Content widget (image grid)
        self.content_widget = QWidget()
        self.content_layout = QGridLayout()
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setContentsMargins(16, 12, 16, 12)
        self.content_layout.setSpacing(16)
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setVisible(False)

        # Add images to the grid
        image_width = int(60 * 0.80)
        image_height = int(60 * 0.80)
        num_images = len(image_paths)
        num_rows = (num_images + num_columns - 1) // num_columns

        for i, path in enumerate(image_paths):
            row = i // num_columns
            col = i % num_columns

            # Create the icon label (draggable)
            icon_label = DraggableImageLabel(path)
            icon_label.setFixedSize(image_width, image_height)
            icon_label.setStyleSheet("border: 2px solid; border-radius: 0px; background: white;")

            # Create the text label (filename without extension)
            base_name = os.path.splitext(os.path.basename(path))[0]
            text_label = QLabel(base_name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("font-size: 11px; color: #333;")

            # Combine icon and text in a vertical layout, centered
            icon_widget = QWidget()
            icon_widget.setStyleSheet("background: transparent;")
            v_layout = QVBoxLayout(icon_widget)
            v_layout.setContentsMargins(4, 4, 4, 4)
            v_layout.setSpacing(8)
            v_layout.setAlignment(Qt.AlignHCenter)
            v_layout.addWidget(icon_label, alignment=Qt.AlignHCenter)
            v_layout.addWidget(text_label, alignment=Qt.AlignHCenter)
            self.content_layout.addWidget(icon_widget, row, col)

        # Set grid layout spacing for even space between icons
        self.content_layout.setSpacing(12)

        # Set content widget background for contrast (optional)
        self.content_widget.setStyleSheet("background: #e0e0e0; border-radius: 8px;")

        # Dynamically set content_widget height to fit all images
        row_height = image_height + 32  # Space for label and padding
        content_height = num_rows * row_height + 24
        self.content_widget.setFixedHeight(content_height)

        # Main layout with horizontal padding and space below each section
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(8, 0, 8, 12)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

    def toggle_content(self):
        """
        Expands or collapses the section.

        What it does:
            - Shows or hides the content widget (image grid) based on the toggle button state.

        How:
            - Sets the content widget's visibility to match the button's checked state.
        """
        self.content_widget.setVisible(self.toggle_button.isChecked())

class Palette(QFrame):
    """
    Tool palette frame with collapsible categories for draggable image icons.

    What it does:
        - Provides a scrollable panel of collapsible sections, one for each image category.
        - Each section contains a grid of draggable image icons.
        - Categories and images are auto-detected from subfolders in Image_Icons.

    How:
        - Scans the Image_Icons directory for subfolders (categories).
        - For each category, finds all image files and creates a CollapsibleSection.
        - Adds all sections to a vertical layout inside a scrollable area.
        - Applies a modern style to the scrollbars and palette frame.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()

    def setupUI(self):
        """
        Sets up the palette UI.

        What it does:
            - Creates a scrollable area containing collapsible sections for each image category.
            - Each section displays a grid of draggable image icons.

        How:
            - Sets the frame style and background.
            - Creates a main widget and vertical layout for all categories.
            - Scans the Image_Icons directory for subfolders (categories).
            - For each category, lists all image files and creates a CollapsibleSection.
            - Adds all sections to the main layout.
            - Wraps the main widget in a QScrollArea for scrolling.
            - Applies a custom scrollbar style.
        """
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")

        # Main widget and layout for categories
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(1)
        main_layout.setContentsMargins(6, 6, 6, 6)

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

        # Make the whole palette scrollable
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Apply modern scrollbar style
        scroll_area.setStyleSheet(SCROLLBAR_STYLE)

        # Set the scroll area as the layout's only widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(scroll_area)