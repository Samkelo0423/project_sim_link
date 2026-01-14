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


class DraggableIconPalette(QFrame):
    """
    Single public palette class that builds collapsible "sections" internally.

    What it does:
        - Provides a scrollable list of collapsible category widgets.
        - Each category contains a grid of draggable image icons.
        - Scans the Image_Icons directory for categories and builds UI dynamically.

    Design:
        - Keeps the public API as a single class for ease of use.
        - Uses small internal helper methods to keep the code readable and testable.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def collapsible_section_icons(self, title, image_paths, num_columns=4, font_weight="bold"):
        
        toggle_button = QPushButton(title)
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.setStyleSheet(f"""
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

        content_widget = QWidget()
        content_layout = QGridLayout()
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(16)
        content_widget.setLayout(content_layout)
        content_widget.setVisible(False)

        # Add images to the grid
        image_width = int(60 * 0.80)
        image_height = int(60 * 0.80)
        num_images = len(image_paths)
        num_rows = (num_images + num_columns - 1) // num_columns

        for i, path in enumerate(image_paths):
            row = i // num_columns
            col = i % num_columns

            icon_label = DraggableImageLabel(path)
            icon_label.setFixedSize(image_width, image_height)
            icon_label.setStyleSheet("border: 2px solid; border-radius: 0px; background: white;")

            base_name = os.path.splitext(os.path.basename(path))[0]
            text_label = QLabel(base_name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("font-size: 11px; color: #333;")

            icon_widget = QWidget()
            icon_widget.setStyleSheet("background: transparent;")
            v_layout = QVBoxLayout(icon_widget)
            v_layout.setContentsMargins(4, 4, 4, 4)
            v_layout.setSpacing(8)
            v_layout.setAlignment(Qt.AlignHCenter)
            v_layout.addWidget(icon_label, alignment=Qt.AlignHCenter)
            v_layout.addWidget(text_label, alignment=Qt.AlignHCenter)
            content_layout.addWidget(icon_widget, row, col)

        content_layout.setSpacing(12)
        content_widget.setStyleSheet("background: #e0e0e0; border-radius: 8px;")

        row_height = image_height + 32
        content_height = num_rows * row_height + 24
        content_widget.setFixedHeight(content_height)

        # Connect toggle behaviour
        toggle_button.clicked.connect(lambda checked, w=content_widget: w.setVisible(checked))

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setSpacing(0)
        wrapper_layout.setContentsMargins(8, 0, 8, 12)
        wrapper_layout.addWidget(toggle_button)
        wrapper_layout.addWidget(content_widget)
        return wrapper

    def setup_ui(self):
        """Set up the palette UI using internal helper to create sections."""
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(1)
        main_layout.setContentsMargins(6, 6, 6, 6)

        base_dir = os.path.dirname(__file__)
        image_icons_dir = os.path.abspath(os.path.join(base_dir, "..", "Image_Icons"))

        for category in sorted(os.listdir(image_icons_dir)):
            category_path = os.path.join(image_icons_dir, category)
            if os.path.isdir(category_path):
                image_files = [
                    os.path.join(category_path, f)
                    for f in os.listdir(category_path)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                collapsible_section_widgets = self.collapsible_section_icons(category, image_files, num_columns=2, font_weight="600")
                main_layout.addWidget(collapsible_section_widgets)
        main_layout.addStretch(1)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(SCROLLBAR_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(scroll_area)
