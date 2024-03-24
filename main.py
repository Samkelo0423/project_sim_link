import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QHBoxLayout, QFrame, QLabel


class ProcessFlowEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Mineral Processing Flow Editor')
        self.setGeometry(100, 100, 800, 600)

        # Create actions for menu items
        new_action = QAction('&New', self)
        open_action = QAction('&Open', self)
        save_action = QAction('&Save', self)
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(self.close)

        # Create menu bar and add actions
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
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

        # Add tool palette and canvas to main layout
        main_layout.addWidget(self.createToolPalette())
        main_layout.addWidget(self.createCanvas())

        # Set main layout for central widget
        central_widget.setLayout(main_layout)



    def createToolPalette(self):
        # Create tool palette frame
        tool_palette = QFrame()
        tool_palette_layout = QVBoxLayout()
        tool_palette_layout.addWidget(QLabel('Tool Palette'))
        tool_palette.setLayout(tool_palette_layout)

        
        return tool_palette

    def createCanvas(self):
        # Create canvas frame
        canvas = QFrame()
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(QLabel('Canvas'))
        canvas.setLayout(canvas_layout)
        return canvas


def main():
    app = QApplication(sys.argv)
    window = ProcessFlowEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
