import pyautogui
from pathlib import Path
from datetime import datetime

pyautogui.FAILSAFE = True

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def capture_screen() -> dict:
    try:
        screenshot = pyautogui.screenshot()

        filename = datetime.now().strftime("screen_%Y%m%d_%H%M%S.png")
        filepath = SCREENSHOT_DIR / filename

        screenshot.save(filepath)

        return {
            "success": True,
            "action": "capture_screen",
            "filepath": str(filepath),
            "width": screenshot.width,
            "height": screenshot.height,
            "message": "Screenshot captured successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "capture_screen",
            "message": str(error)
        }