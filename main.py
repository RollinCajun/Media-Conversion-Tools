import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtGui import QIcon
from widgets import ImageProcessingWidget, VideoProcessingWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Frostbyte Media Tools")

        # Set the application icon
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "defaultIcon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.resize(800, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.image_tab = ImageProcessingWidget()
        self.video_tab = VideoProcessingWidget()

        self.tabs.addTab(self.image_tab, "Image Processing")
        self.tabs.addTab(self.video_tab, "Video Processing")
        layout.addWidget(self.tabs)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Set the Fusion style
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "defaultIcon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())