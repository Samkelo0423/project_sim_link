import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QGridLayout, QWidget, QHBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtCore import Qt, QMimeData, QPoint, QByteArray, QBuffer, QIODevice


class ProcessFlowEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Mineral Processing Flow Editor")
        self.setGeometry(100, 100, 1600, 900)

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

        # Add tool palette and canvas to main layout with stretch factor
        main_layout.addWidget(self.createToolPalette(), 1)
        main_layout.addWidget(self.createCanvas(), 4)

        # Set main layout for central widget
        central_widget.setLayout(main_layout)

    def createToolPalette(self):
      # Create tool palette frame
      tool_palette = QFrame()

      # Set frame properties
      tool_palette.setFrameShape(QFrame.Box)  # Set frame shape to a box
      tool_palette.setLineWidth(2)  # Set border width
      tool_palette.setStyleSheet(
     "background-color: lightgray; border-radius: 10px;"
      )  # Set background color

      # Add images to the tool palette
      tool_palette_layout = QGridLayout()  # Use QGridLayout to organize images in rows and columns
      tool_palette_layout.setAlignment(Qt.AlignTop)
      # Add draggable images to the tool palette
      image_paths = ["jaw_crusher.png", "ball_mill.png" , "jaw_crusher.png", "ball_mill.png"]  # Paths to your images
      num_columns = 4  # Number of columns for the tool palette
      image_width = 60
      image_height = 60

      for i, path in enumerate(image_paths):
          row = i // num_columns
          col = i % num_columns
          label = DraggableImageLabel(path)
          label.setFixedSize(image_width , image_height)
          label.setStyleSheet("border: 5px solid gray;")
          tool_palette_layout.addWidget(label, row, col)
          

      tool_palette.setLayout(tool_palette_layout)

      return tool_palette


    def createCanvas(self):
        # Create canvas frame
        canvas = Canvas()

        # Set frame properties
        canvas.setFrameShape(QFrame.Box)
        canvas.setStyleSheet(
            "background-color: lightgray; border-radius: 10px;"
        )

        return canvas


class DraggableImageLabel(QLabel):
    def __init__(self, image_path ):
        super().__init__()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)  # Set image and scale it
        self.setAlignment(Qt.AlignCenter)  # Center align the image
        self.setScaledContents(True)  # Enable scaling of the image

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            
            drag = QDrag(self)
            mime_data = QMimeData()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.pixmap().save(buffer, "PNG")
            mime_data.setData("image/png", byte_array)  # Set the image as MIME data
            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap())  # Set pixmap for the drag
            drag.setHotSpot(QPoint(int(self.width() / 2), int(self.height() / 2)))  # Set hot spot
            drag.exec_(Qt.MoveAction)


class Canvas(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.current_images = {}  # Dictionary to track images being moved {QLabel: QPoint}

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/png"):  # Check if the MIME data contains an image
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            image = QPixmap()
            image.loadFromData(byte_array)
            image_label = QLabel(self)
            image_label.setPixmap(image)  # Set pixmap from MIME data
            position = event.pos() - QPoint(int(image_label.width() / 2), int(image_label.height() / 2))
            image_label.move(position)
            image_label.show()
            self.current_images[image_label] = position  # Add the image to the dictionary
   
    def mousePressEvent(self, event):
        for image_label, position in self.current_images.items():
            if image_label.geometry().contains(event.pos()):
                self.current_image_offset = event.pos() - position

    def mouseMoveEvent(self, event):
        for image_label, position in self.current_images.items():
            if event.buttons() == Qt.LeftButton and image_label.geometry().contains(event.pos()):
                image_label.move(event.pos() - self.current_image_offset)

    def mouseReleaseEvent(self, event):
        for image_label, position in self.current_images.items():
            if event.button() == Qt.LeftButton:
                self.current_images[image_label] = image_label.pos()


def main():
    app = QApplication(sys.argv)
    window = ProcessFlowEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
