import pytesseract
from PyQt5.QtCore import QThread, pyqtSignal


class OCRWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, gray_image, parent=None):
        super().__init__(parent)
        self.gray_image = gray_image

    def run(self):
        try:
            # Extract text from image
            text = pytesseract.image_to_string(self.gray_image, config="--psm 3")
            result = {
                "text": text
            }
        except Exception as e:
            result = {
                "text": "",
                "error": str(e)
            }
        self.finished.emit(result)