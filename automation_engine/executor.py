import time

from automation_engine.actions.app_control import open_application
from automation_engine.actions.keyboard import (
    type_text,
    press_key,
    hotkey
)
from automation_engine.actions.mouse import (
    move_mouse,
    click_mouse,
    double_click,
    scroll_mouse
)
from automation_engine.vision.screenshot import capture_screen
from automation_engine.vision.ocr import extract_text
from automation_engine.vision.screen_analyzer import analyze_screen

from automation_engine.safety.permission_manager import check_permission


# ==========================================================
# GWEN AUTOMATION ENGINE
# CENTRAL ACTION EXECUTOR
# ==========================================================

# Actions that this executor actually implements
ALLOWED_ACTIONS = {
    "open_application",
    "type_text",
    "press_key",
    "hotkey",
    "move_mouse",
    "click_mouse",
    "double_click",
    "scroll_mouse",
    "wait",
    "capture_screen",
    "extract_text",
    "analyze_screen"
}


# ==========================================================
# EXECUTE SINGLE ACTION
# ==========================================================

def execute_action(
    action: dict,
    confirmation_granted: bool = False
) -> dict:

    if not isinstance(action, dict):
        return {
            "success": False,
            "action": None,
            "message": "Action must be a dictionary"
        }

    action_type = action.get("type")

    # ------------------------------------------------------
    # Permission validation
    # ------------------------------------------------------

    permission = check_permission(
        action,
        confirmation_granted=confirmation_granted
    )

    if not permission["allowed"]:
        return {
            "success": False,
            "action": action_type,
            "status": (
                "confirmation_required"
                if permission["requires_confirmation"]
                else "blocked"
            ),
            "message": permission["reason"]
        }

    # ------------------------------------------------------
    # Executor allowlist
    # ------------------------------------------------------

    if action_type not in ALLOWED_ACTIONS:
        return {
            "success": False,
            "action": action_type,
            "status": "unsupported",
            "message": f"Action is not implemented: {action_type}"
        }

    # ------------------------------------------------------
    # Execute validated action
    # ------------------------------------------------------

    try:

        if action_type == "open_application":

            return open_application(
                action["application"]
            )

        elif action_type == "type_text":

            return type_text(
                action["text"]
            )

        elif action_type == "press_key":

            return press_key(
                action["key"]
            )

        elif action_type == "hotkey":

            keys = action["keys"]

            if not isinstance(keys, list) or not keys:
                return {
                    "success": False,
                    "action": action_type,
                    "message": "Hotkey must contain a list of keys"
                }

            return hotkey(*keys)

        elif action_type == "move_mouse":

            return move_mouse(
                action["x"],
                action["y"]
            )

        elif action_type == "click_mouse":

            return click_mouse(
                action["x"],
                action["y"],
                action.get("button", "left")
            )

        elif action_type == "double_click":

            return double_click(
                action["x"],
                action["y"]
            )

        elif action_type == "scroll_mouse":

            return scroll_mouse(
                action["amount"]
            )

        elif action_type == "wait":

            seconds = action.get("seconds", 1)

            if not isinstance(seconds, (int, float)):
                return {
                    "success": False,
                    "action": action_type,
                    "message": "Wait duration must be numeric"
                }

            if seconds < 0 or seconds > 10:
                return {
                    "success": False,
                    "action": action_type,
                    "message": "Wait duration must be between 0 and 10 seconds"
                }

            time.sleep(seconds)

            return {
                "success": True,
                "action": action_type,
                "seconds": seconds,
                "message": f"Waited {seconds} seconds"
            }

        elif action_type == "capture_screen":

            return capture_screen()

        elif action_type == "extract_text":

            image_path = action.get("image_path")

            # Capture screen automatically if no image is supplied
            if not image_path:

                screenshot = capture_screen()

                if not screenshot["success"]:
                    return screenshot

                image_path = screenshot["filepath"]

            return extract_text(image_path)

        elif action_type == "analyze_screen":

            image_path = action.get("image_path")

            # Capture screen automatically if no image is supplied
            if not image_path:

                screenshot = capture_screen()

                if not screenshot["success"]:
                    return screenshot

                image_path = screenshot["filepath"]

            return analyze_screen(image_path)

    except KeyError as error:

        return {
            "success": False,
            "action": action_type,
            "message": f"Missing required parameter: {error}"
        }

    except Exception as error:

        return {
            "success": False,
            "action": action_type,
            "message": str(error)
        }


# ==========================================================
# EXECUTE COMPLETE ACTION PLAN
# ==========================================================

def execute_plan(plan: dict) -> dict:

    if not isinstance(plan, dict):
        return {
            "success": False,
            "status": "invalid_plan",
            "message": "Plan must be a dictionary"
        }

    task_id = plan.get("task_id", "unknown")

    actions = plan.get("actions")

    # ------------------------------------------------------
    # Validate action list
    # ------------------------------------------------------

    if not isinstance(actions, list):

        return {
            "success": False,
            "task_id": task_id,
            "status": "invalid_plan",
            "message": "Plan actions must be a list",
            "results": []
        }

    # ------------------------------------------------------
    # Plan-level confirmation
    # ------------------------------------------------------

    requires_confirmation = plan.get(
        "requires_confirmation",
        False
    )

    confirmation_granted = plan.get(
        "confirmation_granted",
        False
    )

    if requires_confirmation and not confirmation_granted:

        return {
            "success": False,
            "task_id": task_id,
            "status": "confirmation_required",
            "completed_actions": 0,
            "total_actions": len(actions),
            "results": [],
            "message": "User confirmation required before execution"
        }

    # ------------------------------------------------------
    # Sequential execution
    # ------------------------------------------------------

    results = []

    for index, action in enumerate(actions):

        step_number = index + 1

        print(
            f"\n[GWEN] Checking action "
            f"{step_number}/{len(actions)}"
        )

        # Validate action structure
        if not isinstance(action, dict):

            result = {
                "success": False,
                "action": None,
                "message": "Invalid action format"
            }

            results.append({
                "step": step_number,
                "action": None,
                "result": result
            })

            return {
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "completed_actions": index,
                "total_actions": len(actions),
                "results": results,
                "message": f"Invalid action at step {step_number}"
            }

        action_type = action.get("type")

        # --------------------------------------------------
        # Permission check
        # --------------------------------------------------

        permission = check_permission(
            action,
            confirmation_granted=confirmation_granted
        )

        print(
            f"[GWEN] Permission: "
            f"{permission['reason']}"
        )

        if not permission["allowed"]:

            status = (
                "confirmation_required"
                if permission["requires_confirmation"]
                else "blocked"
            )

            return {
                "success": False,
                "task_id": task_id,
                "status": status,
                "completed_actions": index,
                "total_actions": len(actions),
                "results": results,
                "blocked_action": action_type,
                "message": permission["reason"]
            }

        # --------------------------------------------------
        # Execute action
        # --------------------------------------------------

        print(
            f"[GWEN] Executing: {action_type}"
        )

        result = execute_action(
            action,
            confirmation_granted=confirmation_granted
        )

        # Record result
        results.append({
            "step": step_number,
            "action": action_type,
            "result": result
        })

        # --------------------------------------------------
        # Stop if action failed
        # --------------------------------------------------

        if not result.get("success", False):

            return {
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "completed_actions": index,
                "total_actions": len(actions),
                "results": results,
                "failed_action": action_type,
                "message": (
                    f"Execution stopped at step {step_number}: "
                    f"{result.get('message', 'Unknown error')}"
                )
            }

    # ------------------------------------------------------
    # Successful completion
    # ------------------------------------------------------

    return {
        "success": True,
        "task_id": task_id,
        "status": "completed",
        "completed_actions": len(results),
        "total_actions": len(actions),
        "results": results,
        "message": "Automation plan executed successfully"
    }