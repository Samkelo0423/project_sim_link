from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor


class Canvas(QFrame):

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.current_images = {}
        self.gridVisible = False

    def showGrid(self, visible):
        self.gridVisible = visible
        self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/png"):
            event.acceptProposedAction()

    def dropEvent(self, event):

        if event.mimeData().hasFormat("image/png"):
            byte_array = event.mimeData().data("image/png")
            image = QPixmap()
            image.loadFromData(byte_array)
            image_label = QLabel(self)
            image_label.setPixmap(image)
            image_label.setStyleSheet("border: 2px solid black; border-radius : 0px ;")

            position = event.pos() - QPoint(
                int(image_label.width() / 2), int(image_label.height() / 2)
            )
            image_label.move(position)
            image_label.show()

            self.current_images[image_label] = {
                "position": position,
                "size": image.size(),
                "resizing": False,
                "resizing_offset": QPoint(),
                "resize_corner": None,
                "pixmap": image,
            }

    def mousePressEvent(self, event):
        for image_label, properties in self.current_images.items():
            if image_label.geometry().contains(event.pos()):
                properties["resizing"] = False
                properties["resizing_offset"] = QPoint()
                properties["current_image_offset"] = (
                    event.pos() - properties["position"]
                )

                position = properties["position"]
                size = properties["size"]

                corners = [
                    (position, "top_left"),
                    (position + QPoint(size.width(), 0), "top_right"),
                    (position + QPoint(0, size.height()), "bottom_left"),
                    (position + QPoint(size.width(), size.height()), "bottom_right"),
                ]
                for corner, corner_name in corners:
                    if (
                        abs(corner.x() - event.pos().x()) <= 8
                        and abs(corner.y() - event.pos().y()) <= 8
                    ):
                        properties["resizing"] = True
                        properties["resizing_offset"] = corner - event.pos()
                        properties["resize_corner"] = corner_name

    def mouseMoveEvent(self, event):
        min_size = QSize(20, 20)
        max_size = QSize(1000, 1000)

        for image_label, properties in self.current_images.items():
            if event.buttons() == Qt.LeftButton and image_label.geometry().contains(
                event.pos()
            ):
                if properties["resizing"]:
                    new_size = properties["size"] + QSize(
                        event.pos().x()
                        - properties["position"].x()
                        - properties["resizing_offset"].x(),
                        event.pos().y()
                        - properties["position"].y()
                        - properties["resizing_offset"].y(),
                    ).expandedTo(min_size)

                    if (
                        new_size.width() > properties["size"].width()
                        or new_size.height() > properties["size"].height()
                    ):
                        new_size = new_size.boundedTo(max_size)

                    if event.modifiers() & Qt.ControlModifier:
                        new_size.setHeight(
                            event.pos().y()
                            - properties["position"].y()
                            - properties["resizing_offset"].y()
                        )
                    elif event.modifiers() & Qt.ShiftModifier:
                        new_size.setWidth(
                            event.pos().x()
                            - properties["position"].x()
                            - properties["resizing_offset"].x()
                        )
                    else:
                        pass

                    if properties["resize_corner"] in ["top_left", "bottom_right"]:
                        new_position = QPoint(
                            min(properties["position"].x(), event.pos().x()),
                            min(properties["position"].y(), event.pos().y()),
                        )
                    elif properties["resize_corner"] in ["top_right", "bottom_left"]:
                        new_position = QPoint(
                            max(properties["position"].x(), event.pos().x()),
                            max(properties["position"].y(), event.pos().y()),
                        )

                    image_label.setGeometry(
                        new_position.x(),
                        new_position.y(),
                        new_size.width(),
                        new_size.height(),
                    )
                    image_label.setPixmap(
                        properties["pixmap"].scaled(
                            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                    )
                else:
                    image_label.move(event.pos() - properties["current_image_offset"])

    def mouseReleaseEvent(self, event):
        for image_label, properties in self.current_images.items():
            if event.button() == Qt.LeftButton:
                properties["position"] = image_label.pos()
                properties["size"] = image_label.size()
                properties["resizing"] = False

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.gridVisible:
            painter = QPainter(self)
            self.drawGrid(painter)

    def drawGrid(self, painter):

        grid_color = QColor(60, 70, 80)
        grid_opacity = 0.7
        start_x = 0
        start_y = 0
        grid_spacing = 20

        painter.save()
        painter.setPen(grid_color.lighter(90))
        painter.setOpacity(grid_opacity)

        for x in range(start_x, self.width(), grid_spacing):
            painter.drawLine(x, 0, x, self.height())

        for y in range(start_y, self.height(), grid_spacing):
            painter.drawLine(0, y, self.width(), y)

        painter.restore()
