import cv2
import pytesseract
from pathlib import Path


def analyze_screen(image_path: str) -> dict:
    try:
        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "success": False,
                "action": "analyze_screen",
                "message": "Screenshot file not found"
            }

        image = cv2.imread(str(image_path))

        if image is None:
            return {
                "success": False,
                "action": "analyze_screen",
                "message": "Unable to read screenshot"
            }

        height, width = image.shape[:2]

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        data = pytesseract.image_to_data(
            processed,
            output_type=pytesseract.Output.DICT,
            config="--psm 6"
        )

        elements = []

        for i in range(len(data["text"])):
            text = data["text"][i].strip()

            if not text:
                continue

            try:
                confidence = float(data["conf"][i])
            except ValueError:
                confidence = -1

            if confidence < 30:
                continue

            x = int(data["left"][i])
            y = int(data["top"][i])
            w = int(data["width"][i])
            h = int(data["height"][i])

            elements.append({
                "text": text,
                "confidence": round(confidence, 2),
                "position": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                },
                "center": {
                    "x": x + w // 2,
                    "y": y + h // 2
                }
            })

        full_text = " ".join(
            element["text"] for element in elements
        )

        return {
            "success": True,
            "action": "analyze_screen",
            "screen": {
                "width": width,
                "height": height
            },
            "element_count": len(elements),
            "elements": elements,
            "full_text": full_text,
            "message": "Screen analysis completed"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "analyze_screen",
            "message": str(error)
        }