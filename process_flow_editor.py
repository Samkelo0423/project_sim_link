from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QWidget,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QApplication
)
from PyQt5.QtCore import Qt
from draggable_image_label import DraggableImageLabel
from canvas import Canvas


class ProcessFlowEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Mineral Processing Flow Editor")
        
        #Getting primary screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Set the window size relative to the screen size
        self.setGeometry( 100,
                          100, 
                          int(screen_width * 0.70), 
                          int(screen_height * 0.70))
        self.setMinimumSize(800, 600)

        # Create actions for menu items
        new_action = QAction("&New", self)
        open_action = QAction("&Open", self)
        save_action = QAction("&Save", self)
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)

        # Create menu bar and add actions
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Create central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set up main layout
        self.setupMainLayout(central_widget)

    def setupMainLayout(self, central_widget):

        # Create the main layout
        main_layout = QHBoxLayout()

        tool_palette = self.createToolPalette()
        canvas = self.createCanvas()


        # Add tool palette and canvas to main layout with stretch factor
        main_layout.addWidget(tool_palette, 1)
        main_layout.addWidget(canvas, 5)

        # Set main layout for central widget
        central_widget.setLayout(main_layout)


    def createToolPalette(self):
        # Create tool palette frame
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        tool_palette = QFrame()


        # Set frame properties
        tool_palette.setFrameShape(QFrame.Box)  # Set frame shape to a box
        tool_palette.setLineWidth(2)  # Set border width
        tool_palette.setStyleSheet(
            "background-color: lightgray; border-radius: 10px;"
        )  # Set background color

        # Add images to the tool palette
        tool_palette_layout = (
            QGridLayout()
        )  # Use QGridLayout to organize images in rows and columns

        tool_palette_layout.setAlignment(Qt.AlignTop)
        # Add draggable images to the tool palette
        image_paths = [
            "jaw_crusher.png",
            "ball_mill.png",
            "jaw_crusher.png",
            "ball_mill.png",
            "jaw_crusher.png",
            "ball_mill.png",
            "jaw_crusher.png",
            "ball_mill.png",
        ]  # Paths to your images

        

        num_columns = 4  # Number of columns for the tool palette
        image_width = int(60 * 0.80)
        image_height = int(60 * 0.80)

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

        canvas = Canvas()
        # Set frame properties
        canvas.setFrameShape(QFrame.Box)
        canvas.setStyleSheet("background-color: lightgray; border-radius: 0px;")
        canvas.show()

        return canvas
