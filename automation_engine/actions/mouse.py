import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


def get_screen_size():
    width, height = pyautogui.size()

    return {
        "success": True,
        "width": width,
        "height": height,
        "message": f"Screen resolution: {width}x{height}"
    }


def move_mouse(x: int, y: int) -> dict:
    try:
        width, height = pyautogui.size()

        if not (0 <= x < width and 0 <= y < height):
            return {
                "success": False,
                "action": "move_mouse",
                "message": "Coordinates outside screen boundaries"
            }

        pyautogui.moveTo(x, y, duration=0.5)

        return {
            "success": True,
            "action": "move_mouse",
            "coordinates": {"x": x, "y": y},
            "message": "Mouse moved successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "move_mouse",
            "message": str(error)
        }


def click_mouse(x: int, y: int, button: str = "left") -> dict:
    try:
        width, height = pyautogui.size()

        if not (0 <= x < width and 0 <= y < height):
            return {
                "success": False,
                "action": "click_mouse",
                "message": "Coordinates outside screen boundaries"
            }

        if button not in ["left", "right", "middle"]:
            return {
                "success": False,
                "action": "click_mouse",
                "message": "Invalid mouse button"
            }

        pyautogui.click(x=x, y=y, button=button)

        return {
            "success": True,
            "action": "click_mouse",
            "button": button,
            "coordinates": {"x": x, "y": y},
            "message": f"{button.capitalize()} click successful"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "click_mouse",
            "message": str(error)
        }


def double_click(x: int, y: int) -> dict:
    try:
        width, height = pyautogui.size()

        if not (0 <= x < width and 0 <= y < height):
            return {
                "success": False,
                "action": "double_click",
                "message": "Coordinates outside screen boundaries"
            }

        pyautogui.doubleClick(x=x, y=y)

        return {
            "success": True,
            "action": "double_click",
            "coordinates": {"x": x, "y": y},
            "message": "Double click successful"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "double_click",
            "message": str(error)
        }


def scroll_mouse(amount: int) -> dict:
    try:
        pyautogui.scroll(amount)

        return {
            "success": True,
            "action": "scroll_mouse",
            "amount": amount,
            "message": "Scrolling completed"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "scroll_mouse",
            "message": str(error)
        }