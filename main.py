import os
import sys
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.button = QPushButton("Screenshot")
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create centered layout
        layout = QVBoxLayout(central_widget)

        # Set button style and properties
        self.button.setFixedWidth(200)
        self.button.setFixedHeight(100)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setStyleSheet("""
            QPushButton {
                font-size: 28px;
                border: 2px solid white;
                border-radius: 15px;
            }
        """)
        self.button.clicked.connect(self.screenshot)

        layout.addWidget(self.button)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Set title of window
        self.setWindowTitle('Omni')

        # Set window icon
        self.setWindowIcon(QIcon("assets/omni.png"))  # Ensure the correct path

    def screenshot(self):
        screen = QApplication.primaryScreen()
        if screen:
            # Capture the entire screen
            geometry = screen.geometry()
            # Capture only the primary screen using the geometry
            ss = screen.grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())

            # Save the screenshot with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join("screenshots", filename)

            ss.save(filepath, 'png')
            print(f"Screenshot saved as {filename}")

def main(): 
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
