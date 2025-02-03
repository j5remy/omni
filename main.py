import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)

        # Set button style and properties
        button = QPushButton("Screenshot")
        button.setFixedWidth(100)
        button.setFixedHeight(50)
        button.setCursor(Qt.PointingHandCursor)

        layout.addWidget(button)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Set title of window
        self.setWindowTitle('Omni')

        # Set window icon
        self.setWindowIcon(QIcon("/assets/omni.png"))

def main(): 
    # Initiate app
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()