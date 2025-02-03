import cv2
import pytesseract
from PyQt5.QtCore import QThread, pyqtSignal

from ocr.utils import preprocess_for_ocr


class OCRWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, gray_image, blur_threshold, parent=None):
        super().__init__(parent)
        self.gray_image = gray_image
        self.blur_threshold = blur_threshold

    def run(self):
        try:
            # Compute Laplacian variance for blur detection.
            laplacian_var = cv2.Laplacian(self.gray_image, cv2.CV_64F).var()
            if laplacian_var < self.blur_threshold:
                result = {
                    "text": "",
                    "blurry": True,
                    "laplacian_var": laplacian_var
                }
            else:
                # Preprocess the image before OCR.
                # processed = preprocess_for_ocr(self.gray_image)
                text = pytesseract.image_to_string(self.gray_image, config="--psm 3")
                result = {
                    "text": text,
                    "blurry": False,
                    "laplacian_var": laplacian_var
                }
        except Exception as e:
            result = {
                "text": "",
                "blurry": False,
                "error": str(e)
            }
        self.finished.emit(result)