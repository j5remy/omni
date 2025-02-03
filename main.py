import io
import sys

import cv2
import numpy as np
import pytesseract
from PIL import Image
from PyQt5.QtCore import QBuffer, QIODevice, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QComboBox, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)
from skimage.metrics import structural_similarity as compare_ssim


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle('Omni')
        self.setWindowIcon(QIcon("assets/omni.png"))

        self.button = QPushButton("Start OCR")
        self.screen_selector = QComboBox()

        self.initUI()
        self.populate_screen_selector()

        # Timer for periodic screenshots (1-second interval)
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_and_process)

        self.previous_image = None
        self.change_threshold = 0.98  # SSIM threshold (1.0 = identical images)

        # Blur detection threshold
        self.blur_threshold = 100  # Lower = more sensitive to blurriness

        # Flag to prevent overlapping OCR processes
        self.is_processing = False

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.button.setFixedSize(200, 50)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                border: 2px solid white;
                border-radius: 10px;
            }
        """)
        self.button.clicked.connect(self.toggle_ocr)

        layout.addWidget(self.screen_selector)
        layout.addWidget(self.button)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

    def populate_screen_selector(self):
        screens = QApplication.screens()
        for index, screen in enumerate(screens):
            self.screen_selector.addItem(f"Screen {index + 1} ({screen.name()})")

    def toggle_ocr(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start OCR")
        else:
            self.timer.start(1000)  # Capture every 1 second
            self.button.setText("Stop OCR")

    def capture_and_process(self):
        if self.is_processing:
            return
        self.is_processing = True

        selected_screen_index = self.screen_selector.currentIndex()
        screens = QApplication.screens()
        screen = screens[selected_screen_index] if selected_screen_index < len(screens) else QApplication.primaryScreen()

        geometry = screen.geometry()
        screenshot = screen.grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())

        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        screenshot.save(buffer, 'PNG')

        current_image = Image.open(io.BytesIO(buffer.data()))
        cv_image = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        gray_current = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # ✅ Compare with the previous screenshot
        if self.previous_image is not None:
            (score, _) = compare_ssim(self.previous_image, gray_current, full=True)
            print(f"Change Detection SSIM Score: {score}")

            if score > self.change_threshold:
                print("⚡ No significant change detected. Skipping OCR.")
                self.is_processing = False
                return  # Skip OCR if the screen hasn't changed significantly

        self.previous_image = gray_current  # Update for next comparison

        if self.is_blurry(cv_image):
            print("⚠️ Blurry screenshot detected. Retaking...")
            self.is_processing = False
            QTimer.singleShot(100, self.capture_and_process)
        else:
            print("✅ Clear screenshot detected. Running OCR...")
            text = pytesseract.image_to_string(gray_current, config="--psm 3")

            if text.strip():
                print(f"Extracted Text from Screenshot:\n{text}\n{'-'*50}")
            else:
                print("No text detected in this capture.\n" + "-"*50)

            self.is_processing = False


    def is_blurry(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Laplacian operator for blur detection
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        print(f"Laplacian Variance: {laplacian_var}")
        return laplacian_var < self.blur_threshold

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
