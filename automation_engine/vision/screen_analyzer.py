import cv2
import pytesseract
import re
from pathlib import Path


def detect_screen_type(text):
    """Classify applications using cross-platform OCR indicators."""

    lower = text.lower()

    terminal_patterns = [
        r"\bterminal\b",
        r"\bconsole\b",
        r"\bcommand prompt\b",
        r"\bcmd\.exe\b",
        r"\bpowershell\b",
        r"\bwindows terminal\b",
        r"\bubuntu\b",
        r"\bkali\b",
        r"\blinux\b",
        r"\bbash\b",
        r"\bzsh\b",
        r"\btraceback\b",
        r"\bcommand not found\b",
        r"\broot@[\w.-]+",
        r"\b[\w.-]+@[\w.-]+",
        r"\bPS\s+[A-Z]:\\",
        r"[A-Z]:\\Windows\\System32",
        r"[A-Z]:\\Users\\",
        r"\bC:\\",
        r"┌",
        r"└",
        r"\$\s+\w",
        r"#\s+\w",
    ]

    if any(re.search(pattern, text, re.IGNORECASE) for pattern in terminal_patterns):
        return "terminal"

    browser_patterns = [
        r"https?://",
        r"\bwww\.",
        r"\bfirefox\b",
        r"\bchrome\b",
        r"\bchromium\b",
        r"\bgoogle chrome\b",
        r"\bmicrosoft edge\b",
        r"\bsafari\b",
        r"\baddress bar\b",
        r"\bsearch the web\b",
    ]

    if any(re.search(pattern, lower) for pattern in browser_patterns):
        return "browser"

    editor_patterns = [
        r"\bmousepad\b",
        r"\bgedit\b",
        r"\bnotepad\b",
        r"\bnotepad\+\+\b",
        r"\bwordpad\b",
        r"\bvisual studio code\b",
        r"\bvs code\b",
        r"\btext editor\b",
        r"\buntitled\b",
        r"\bsyntax\b",
    ]

    if any(re.search(pattern, lower) for pattern in editor_patterns):
        return "text_editor"

    file_manager_patterns = [
        r"\bfile explorer\b",
        r"\bwindows explorer\b",
        r"\bfile manager\b",
        r"\bthunar\b",
        r"\bdolphin\b",
        r"\bnautilus\b",
        r"\bthis pc\b",
        r"\bquick access\b",
        r"\bhome folder\b",
    ]

    if any(re.search(pattern, lower) for pattern in file_manager_patterns):
        return "file_manager"

    desktop_patterns = [
        r"\bapplications\b",
        r"\bdesktop\b",
        r"\btrash\b",
        r"\brecycle bin\b",
        r"\btaskbar\b",
        r"\bstart menu\b",
    ]

    if any(re.search(pattern, lower) for pattern in desktop_patterns):
        return "desktop"

    return "unknown"

def describe_screen(screen_type, lines):
    """Generate a readable rule-based screen description."""

    descriptions = {
        "terminal": (
            "A terminal or command-line window appears to be open. "
            "The screen may contain shell commands, command output, "
            "or a command prompt."
        ),
        "browser": (
            "A web browser appears to be open. "
            "Visible text may contain a webpage, navigation controls, "
            "or a search result."
        ),
        "text_editor": (
            "A text editor appears to be open. "
            "Visible text may contain a document, notes, or code."
        ),
        "file_manager": (
            "A file manager appears to be open. "
            "Visible text may contain files, folders, or navigation locations."
        ),
        "desktop": (
            "The desktop appears to be visible. "
            "Desktop icons, panels, or application shortcuts may be present."
        ),
    }

    if screen_type in descriptions:
        return descriptions[screen_type]

    if lines:
        return (
            "Text was detected, but GWEN could not confidently "
            "identify the application."
        )

    return (
        "No reliable text was detected. "
        "The screen may be empty, graphical, or difficult to read."
    )


def clean_ocr_text(text):
    """Reject obvious OCR fragments while preserving useful text."""

    text = text.strip()

    if not text:
        return False

    # Remove punctuation and symbols for evaluation
    meaningful = re.sub(r'[^A-Za-z0-9]', '', text)

    if len(meaningful) < 2:
        return False

    # Reject symbol-heavy fragments
    if len(meaningful) / max(len(text), 1) < 0.35:
        return False

    # Reject common OCR noise
    noise_patterns = [
        r'^[oO0]{2,}$',
        r'^[iIl|]{2,}$',
        r'^[^A-Za-z0-9]{2,}$',
    ]

    if any(re.fullmatch(pattern, text) for pattern in noise_patterns):
        return False

    return True


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

        # Improve OCR contrast
        gray = cv2.convertScaleAbs(
            gray,
            alpha=1.4,
            beta=10
        )

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
        line_groups = {}

        for i in range(len(data["text"])):
            text = data["text"][i].strip()

            if not text:
                continue

            try:
                confidence = float(data["conf"][i])
            except (ValueError, TypeError):
                confidence = -1

            if confidence < 40:
                continue

            if not clean_ocr_text(text):
                continue

            x = int(data["left"][i])
            y = int(data["top"][i])
            w = int(data["width"][i])
            h = int(data["height"][i])

            element = {
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
            }

            elements.append(element)

            line_key = (
                data["block_num"][i],
                data["par_num"][i],
                data["line_num"][i]
            )

            line_groups.setdefault(line_key, []).append({
                "text": text,
                "x": x,
                "y": y
            })

        readable_lines = []

        for words in line_groups.values():
            words.sort(key=lambda word: word["x"])

            line = " ".join(
                word["text"] for word in words
            ).strip()

            if not clean_ocr_text(line):
                continue

            readable_lines.append({
                "text": line,
                "y": min(word["y"] for word in words)
            })

        readable_lines.sort(key=lambda line: line["y"])

        screen_text = [
            line["text"] for line in readable_lines
        ]

        full_text = " ".join(
            element["text"] for element in elements
        )

        screen_summary = "\n".join(screen_text)

        screen_type = detect_screen_type(screen_summary)

        screen_description = describe_screen(
            screen_type,
            screen_text
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
            "screen_text": screen_text,
            "screen_summary": screen_summary,
            "screen_type": screen_type,
            "screen_description": screen_description,
            "message": "Screen analysis completed"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "analyze_screen",
            "message": str(error)
        }
