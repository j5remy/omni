import io

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtWidgets import QApplication


def capture_gray_screenshot(screen_selector,  selected_index=None):
    """
    Captures the current screen (based on the screen_selector widget)
    as a grayscale OpenCV image.
    """
    if selected_index is None:
        selected_index = screen_selector.currentIndex()
        
    screens = QApplication.screens()
    screen = screens[selected_index] if selected_index < len(screens) else QApplication.primaryScreen()
    geometry = screen.geometry()

    # Grab the screenshot.
    screenshot = screen.grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())

    # Convert QPixmap to an OpenCV image via an in‑memory buffer.
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    screenshot.save(buffer, "PNG")
    image = Image.open(io.BytesIO(buffer.data()))
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)