from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QWidget,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QApplication
)
import os
from PyQt5.QtCore import Qt
from UI_Interface.image_palette_items import DraggableImageLabel
from UI_Interface.flow_canvas import Canvas


class ProcessFlowEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Mineral Processing Flow Editor")
        
        # Get primary screen size for responsive window sizing
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Set the window size relative to the screen size
        self.setGeometry(100, 100, int(screen_width * 0.70), int(screen_height * 0.70))
        self.setMinimumSize(800, 600)

        # Create actions for menu items (File menu)
        new_action = QAction("&New", self)
        open_action = QAction("&Open", self)
        save_action = QAction("&Save", self)
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)

        # Create menu bar and add actions to File menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Create central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set up main layout (tool palette + canvas)
        self.setupMainLayout(central_widget)

    def setupMainLayout(self, central_widget):
        # Create the main horizontal layout
        main_layout = QHBoxLayout()

        # Create tool palette (left) and canvas (right)
        tool_palette = self.createToolPalette()
        canvas = self.createCanvas()

        # Add tool palette and canvas to main layout with stretch factor
        main_layout.addWidget(tool_palette, 1)  # Tool palette gets less space
        main_layout.addWidget(canvas, 5)        # Canvas gets more space

        # Set main layout for central widget
        central_widget.setLayout(main_layout)

    def createToolPalette(self):
        # Create tool palette frame
        tool_palette = QFrame()

        # Set frame properties for appearance
        tool_palette.setFrameShape(QFrame.Box)
        tool_palette.setLineWidth(2)
        tool_palette.setStyleSheet("background-color: lightgray; border-radius: 10px;")

        # Layout for arranging image icons
        tool_palette_layout = QGridLayout()
        tool_palette_layout.setAlignment(Qt.AlignTop)

        # Use relative paths for images in the Image_Icons directory
        base_dir = os.path.dirname(__file__)
        image_dir = os.path.abspath(os.path.join(base_dir, "..", "Image_Icons"))
        
        # Automatically load all image files in the directory
        image_files = [
            f for f in os.listdir(image_dir) 
            if f.endswith(('.png', '.jpg', '.jpeg'))
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

        tool_palette.setLayout(tool_palette_layout)

        return tool_palette
    
    def createCanvas(self):
        # Create the main drawing/interaction canvas
        canvas = Canvas()
        # Set frame properties for appearance
        canvas.setFrameShape(QFrame.Box)
        canvas.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        canvas.show()

        return canvas
