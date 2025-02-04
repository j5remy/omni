import cv2


# This function is currently not used
def preprocess_for_ocr(gray_image):
    """
    Preprocess the grayscale image using adaptive thresholding and median blurring.
    This can help improve OCR accuracy.
    """
    # Adaptive thresholding to get a binary image.
    thresh = cv2.adaptiveThreshold(
        gray_image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    # Median blur to reduce noise while preserving edges.
    processed = cv2.medianBlur(thresh, 3)
    return processed