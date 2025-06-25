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
    """
    Main application window for the Mineral Processing Flow Editor.

    What it does:
        - Sets up the main window, menu bar, and central layout.
        - Arranges the tool palette and canvas side by side.
        - Handles window sizing and menu actions.

    How:
        - Uses QMainWindow as the base.
        - Creates a menu bar with File actions.
        - Uses a horizontal layout to place the Palette and Canvas widgets.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initializes the main window UI.

        What it does:
            - Sets the window title and size.
            - Creates the menu bar and File menu actions.
            - Sets up the central widget and main layout.

        How:
            - Gets the screen size for responsive window sizing.
            - Adds New, Open, Save, and Exit actions to the File menu.
            - Creates a QWidget as the central widget and applies the main layout.
        """
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
        """
        Sets up the main horizontal layout for the window.

        What it does:
            - Arranges the tool palette on the left and the canvas on the right.

        How:
            - Creates a QHBoxLayout.
            - Adds the tool palette with a smaller stretch factor (less space).
            - Adds the canvas with a larger stretch factor (more space).
            - Sets this layout on the central widget.
        """
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
        """
        Creates and returns the tool palette widget.

        What it does:
            - Instantiates the Palette widget for image categories.
            - Sets frame and background style.

        How:
            - Creates a Palette instance.
            - Applies a box frame and light gray background.
            - Returns the widget for layout.
        """
        tool_palette = Palette()
        tool_palette.setFrameShape(QFrame.Box)
        tool_palette.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        tool_palette.show()
        return tool_palette 
    
    def createCanvas(self):
        """
        Creates and returns the main drawing/interaction canvas.

        What it does:
            - Instantiates the Canvas widget for user interaction.
            - Sets frame and background style.

        How:
            - Creates a Canvas instance.
            - Applies a box frame and light gray background.
            - Returns the widget for layout.
        """
        canvas = Canvas()
        # Set frame properties for appearance
        canvas.setFrameShape(QFrame.Box)
        canvas.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        canvas.show()

        return canvas
