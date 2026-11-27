import pyautogui
import time

# Safety: moving mouse to top-left corner aborts automation
pyautogui.FAILSAFE = True

# Delay between actions
pyautogui.PAUSE = 0.2


def type_text(text: str) -> dict:
    """Type text into the currently focused application."""

    try:
        pyautogui.write(text, interval=0.03)

        return {
            "success": True,
            "action": "type_text",
            "message": "Text typed successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "type_text",
            "message": str(error)
        }


def press_key(key: str) -> dict:
    """Press a single keyboard key."""

    try:
        pyautogui.press(key)

        return {
            "success": True,
            "action": "press_key",
            "key": key,
            "message": f"Pressed {key}"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "press_key",
            "message": str(error)
        }


def hotkey(*keys: str) -> dict:
    """Press a keyboard shortcut."""

    try:
        pyautogui.hotkey(*keys)

        return {
            "success": True,
            "action": "hotkey",
            "keys": list(keys),
            "message": "Shortcut executed successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "hotkey",
            "message": str(error)
        }