import difflib

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox, QMainWindow,
                             QMenu, QPushButton, QSystemTrayIcon, QVBoxLayout,
                             QWidget)

from gui.file_utils import save_text_to_file
from gui.screenshot import capture_gray_screenshot
from nlp.generate_notes import generate_notes
from ocr.ocr_worker import OCRWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._setup_timer()
        self._setup_tray_icon()  # Set up the tray icon

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
        self.button.setCursor(self.button.cursor())
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

    def _setup_tray_icon(self):
        """Sets up the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/omni.png"))

        # Create the tray context menu.
        tray_menu = QMenu(self)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.show)  # Show the main window
        tray_menu.addAction(open_action)

        start_action = QAction("Start Session", self)
        start_action.triggered.connect(self.toggle_ocr)  # Toggle the OCR session
        tray_menu.addAction(start_action)

        # Create a submenu for screen selection.
        screen_menu = QMenu("Select Screen", self)
        screens = QApplication.screens()
        for index, screen in enumerate(screens):
            action = QAction(f"Screen {index + 1} ({screen.name()})", self)
            action.triggered.connect(lambda checked, idx=index: self.set_selected_screen(idx))
            screen_menu.addAction(action)
        tray_menu.addMenu(screen_menu)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def set_selected_screen(self, index):
        """Updates the selected screen index in the application and, optionally, the UI."""
        print(f"Selected screen: {index + 1}")

        self.selected_screen_index = index

        # Update screen selector dropdown
        self.screen_selector.setCurrentIndex(index)

    def populate_screen_selector(self):
        """Populates the screen selector dropdown with available screens."""
        screens = QApplication.screens()
        for index, screen in enumerate(screens):
            self.screen_selector.addItem(f"Screen {index + 1} ({screen.name()})")

    def toggle_ocr(self):
        """Toggles OCR processing on/off. When stopped, formats and saves accumulated notes."""
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start Session")
            # When stopping, save the notes.
            save_text_to_file(self, self.accumulated_notes)
        else:
            self.timer.start(750)  # Capture every 750ms
            self.button.setText("Stop Session")

    def capture_and_process(self):
        """Captures and processes a screenshot if not already processing."""
        if self.is_processing:
            return
        self.is_processing = True

        selected_idx = getattr(self, "selected_screen_index", None)
        gray_image = capture_gray_screenshot(self.screen_selector, selected_idx)
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

    def closeEvent(self, event):
        """
        Overrides the close event so that closing the window hides it
        (leaving the app running in the tray) instead of quitting.
        """
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Omni Running",
            "The application is still running in the system tray.",
            QSystemTrayIcon.Information,
            2000
        )
