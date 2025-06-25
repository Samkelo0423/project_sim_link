from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QWidget,
    QHBoxLayout,
    QFrame,
    QApplication
)
from UI_Interface.image_palatte import Palette
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
        self.setGeometry(100, 100, int(screen_width * 0.90), int(screen_height * 0.90))
        self.setMinimumSize(900, 700)

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
        main_layout.addWidget(canvas, 4)        # Canvas gets more space

        # Set main layout for central widget
        central_widget.setLayout(main_layout)

    def createToolPalette(self):

        tool_palette = Palette()
        tool_palette.setFrameShape(QFrame.Box)
        tool_palette.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        tool_palette.show()

        return tool_palette 
    
    def createCanvas(self):
        # Create the main drawing/interaction canvas
        canvas = Canvas()
        # Set frame properties for appearance
        canvas.setFrameShape(QFrame.Box)
        canvas.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        canvas.show()

        return canvas
