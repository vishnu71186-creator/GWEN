import cv2
import pytesseract
from pathlib import Path


def extract_text(image_path: str) -> dict:
    try:
        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "success": False,
                "action": "extract_text",
                "message": f"Image not found: {image_path}"
            }

        image = cv2.imread(str(image_path))

        if image is None:
            return {
                "success": False,
                "action": "extract_text",
                "message": "Unable to load image"
            }

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Improve text visibility
        processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        # Extract text
        text = pytesseract.image_to_string(
            processed,
            config="--psm 6"
        )

        return {
            "success": True,
            "action": "extract_text",
            "text": text.strip(),
            "message": "OCR completed successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "extract_text",
            "message": str(error)
        }