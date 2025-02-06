import difflib

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QComboBox, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from gui.file_utils import save_text_to_file
from gui.screenshot import capture_gray_screenshot
from nlp.format_notes import format_notes
from nlp.generate_notes import generate_notes
from ocr.ocr_worker import OCRWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._setup_timer()

        # Configuration values
        self.blur_threshold = 100                # Lower = more sensitive to blurriness
        self.text_similarity_threshold = 0.4     # Adjust this based on testing

        # State variables
        self.is_processing = False
        self.previous_text = ""        # Last processed OCR text
        self.accumulated_notes = ""    # All notes collected so far

    def _setup_window(self):
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowTitle("Omni")
        self.setWindowIcon(QIcon("assets/omni.png"))

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.screen_selector = QComboBox(self)
        self.button = QPushButton("Start Session", self)
        self.button.setFixedSize(200, 50)
        self.button.setCursor(self.button.cursor())  # Ensures the pointing hand cursor is applied
        self.button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                border: 2px solid white;
                border-radius: 10px;
            }
            """
        )
        self.button.clicked.connect(self.toggle_ocr)

        layout.addWidget(self.screen_selector)
        layout.addWidget(self.button)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.populate_screen_selector()

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_and_process)

    def populate_screen_selector(self):
        """Populates the screen selector dropdown with available screens."""
        screens = QApplication.screens()
        for index, screen in enumerate(screens):
            self.screen_selector.addItem(f"Screen {index + 1} ({screen.name()})")

    def toggle_ocr(self):
        """Toggles OCR processing on/off. When stopped, saves accumulated notes to file."""
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start OCR")
            formatted_notes = format_notes(self.accumulated_notes)
            save_text_to_file(self, formatted_notes)  # Save notes when stopping OCR
        else:
            self.timer.start(750)  # Capture every 750ms
            self.button.setText("Stop Session")

    def capture_and_process(self):
        """Captures and processes a screenshot if not already processing."""
        if self.is_processing:
            return
        self.is_processing = True

        gray_image = capture_gray_screenshot(self.screen_selector)
        if gray_image is None:
            self.is_processing = False
            return

        self.run_ocr(gray_image)

    def run_ocr(self, gray_image):
        """Starts the OCR worker thread using the provided grayscale image."""
        self.worker = OCRWorker(gray_image, self.blur_threshold)
        self.worker.finished.connect(self.handle_worker_result)
        self.worker.start()

    def handle_worker_result(self, result):
        """
        Processes OCR worker results. Handles errors, blurry images, and valid text.
        For valid text, checks similarity with previous text and generates new notes if different enough.
        """
        if "error" in result:
            print(f"Error during OCR: {result['error']}")
        elif result.get("blurry", False):
            print(f"⚠️ Blurry screenshot detected (Laplacian Variance: {result.get('laplacian_var', 'N/A')}). Retaking...")
            QTimer.singleShot(100, self.capture_and_process)
        else:
            print(f"✅ Clear screenshot detected (Laplacian Variance: {result.get('laplacian_var', 'N/A')}). Running OCR...")
            text = result.get("text", "").strip()
            if text:
                similarity = 0.0
                if self.previous_text:
                    similarity = difflib.SequenceMatcher(None, self.previous_text, text).ratio()
                    print(f"Text similarity ratio: {similarity:.3f}")
                    if similarity > self.text_similarity_threshold:
                        print("⚡ The extracted text is too similar to the previous processed text. Skipping further processing.")
                        self.is_processing = False
                        return

                print(f"Extracted Text from Screenshot:\n{text}\n{'-' * 50}")
                
                # Generate notes using both the new text and the accumulated notes as context.
                new_notes = generate_notes(text, self.accumulated_notes)
                if new_notes.strip():
                    print(f"New Notes:\n{new_notes}\n{'=' * 50}")
                    # Append new notes to the accumulated notes.
                    self.accumulated_notes += "\n" + new_notes
                else:
                    print("No additional notes produced.\n" + "=" * 50)
                
                # Only update previous_text when new processing occurs.
                self.previous_text = text
            else:
                print("No text detected in this capture.\n" + "-" * 50)
        self.is_processing = False
