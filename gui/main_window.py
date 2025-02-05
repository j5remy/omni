import difflib
import io

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtCore import QBuffer, QIODevice, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QComboBox, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from nlp.generate_notes import generate_notes
from ocr.ocr_worker import OCRWorker


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

        # Timer for periodic screenshots
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_and_process)

        # Configuration values
        self.blur_threshold = 100  # Lower = more sensitive to blurriness
        self.text_similarity_threshold = 0.4 # if similarity ratio is above this, text is too similar

        # State variables
        self.is_processing = False # Flag to prevent overlapping OCR processes
        self.previous_text = "" # Store previously extracted text


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
            self.timer.start(750)  # Capture every 3/4 of a second
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

        # Convert QPixmap to an OpenCV image using an in-memory buffer
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        screenshot.save(buffer, 'PNG')
        current_image = Image.open(io.BytesIO(buffer.data()))
        cv_image = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
        gray_current = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Run OCR
        self.worker = OCRWorker(gray_current, self.blur_threshold)
        self.worker.finished.connect(self.handle_worker_result)
        self.worker.start()

    def handle_worker_result(self, result):
        if "error" in result:
            print(f"Error during OCR: {result['error']}")
        else:
            if result.get("blurry", False):
                print(f"⚠️ Blurry screenshot detected (Laplacian Variance: {result.get('laplacian_var', 'N/A')}). Retaking...")
                QTimer.singleShot(100, self.capture_and_process)
            else:
                print(f"✅ Clear screenshot detected (Laplacian Variance: {result.get('laplacian_var', 'N/A')}). Running OCR...")
                text = result.get("text", "")
                if text.strip():
                    similarity = 0.0
                    if self.previous_text:
                        similarity = difflib.SequenceMatcher(None, self.previous_text, text).ratio()
                        print(f"Text similarity ratio: {similarity:.3f}")
                        if similarity > self.text_similarity_threshold:
                            print("⚡ The extracted text is too similar to the previous processed text. Skipping further processing.")
                            # Note: We do NOT update self.previous_text here.
                            self.is_processing = False
                            return
                    # Process the new text since it is sufficiently different
                    print(f"Extracted Text from Screenshot:\n{text}\n{'-'*50}")
                    
                    # Generate bullet point notes from the OCR text
                    notes = generate_notes(text)
                    if notes:
                        print(f"Notes:\n{notes}\n{'='*50}")
                    else:
                        print("No bullet notes produced.\n" + "="*50)
                    
                    # Only update previous_text when new processing occurs.
                    self.previous_text = text
                else:
                    print("No text detected in this capture.\n" + "-"*50)
        self.is_processing = False
