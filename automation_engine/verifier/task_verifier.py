from automation_engine.vision.screenshot import capture_screen
from automation_engine.vision.ocr import extract_text


def verify_task(
    expected_text: str,
    image_path: str = None
) -> dict:
    """
    Verify whether expected text is visible on the screen.

    If image_path is not supplied, capture the current screen.
    """

    try:

        if not isinstance(expected_text, str) or not expected_text.strip():
            return {
                "success": False,
                "verified": False,
                "message": "Expected text cannot be empty"
            }

        # Capture current screen if no image is provided
        if image_path is None:

            screenshot = capture_screen()

            if not screenshot["success"]:
                return {
                    "success": False,
                    "verified": False,
                    "message": "Screenshot capture failed",
                    "details": screenshot
                }

            image_path = screenshot["filepath"]

        # Extract visible text
        ocr_result = extract_text(image_path)

        if not ocr_result["success"]:
            return {
                "success": False,
                "verified": False,
                "message": "OCR verification failed",
                "details": ocr_result
            }

        detected_text = ocr_result.get("text", "")

        # Case-insensitive text matching
        expected_normalized = expected_text.strip().lower()
        detected_normalized = detected_text.lower()

        verified = expected_normalized in detected_normalized

        return {
            "success": True,
            "verified": verified,
            "expected_text": expected_text,
            "detected_text": detected_text,
            "verification_method": "ocr_text_matching",
            "message": (
                "Task verified successfully"
                if verified
                else "Expected text was not detected on screen"
            )
        }

    except Exception as error:

        return {
            "success": False,
            "verified": False,
            "message": str(error)
        }


def verify_execution(execution_result: dict) -> dict:
    """
    Verify whether the Action Executor completed all actions successfully.
    """

    if not isinstance(execution_result, dict):
        return {
            "success": False,
            "verified": False,
            "message": "Invalid execution result"
        }

    execution_success = execution_result.get("success", False)

    if not execution_success:

        return {
            "success": True,
            "verified": False,
            "execution_status": execution_result.get("status", "unknown"),
            "message": "Execution was unsuccessful",
            "execution_result": execution_result
        }

    completed = execution_result.get("completed_actions", 0)
    total = execution_result.get("total_actions", 0)

    if completed != total:

        return {
            "success": True,
            "verified": False,
            "completed_actions": completed,
            "total_actions": total,
            "message": "Not all actions were completed"
        }

    return {
        "success": True,
        "verified": True,
        "completed_actions": completed,
        "total_actions": total,
        "message": "All execution actions completed successfully"
    }