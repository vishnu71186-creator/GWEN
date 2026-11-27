# GWEN Permission Manager
# Controls which automation actions may execute.

SAFE_ACTIONS = {
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

CONFIRMATION_REQUIRED_ACTIONS = {
    "delete_file",
    "delete_folder",
    "shutdown",
    "restart",
    "send_message",
    "send_email",
    "submit_form",
    "install_software"
}

FORBIDDEN_ACTIONS = {
    "run_shell_command",
    "execute_shell",
    "execute_arbitrary_code",
    "disable_security",
    "steal_credentials"
}


def check_permission(action: dict, confirmation_granted: bool = False) -> dict:
    """
    Check whether an action is permitted.

    Returns:
        allowed: whether the action can proceed
        requires_confirmation: whether confirmation is required
        reason: explanation
    """

    if not isinstance(action, dict):
        return {
            "allowed": False,
            "requires_confirmation": False,
            "reason": "Invalid action format"
        }

    action_type = action.get("type")

    # Forbidden actions
    if action_type in FORBIDDEN_ACTIONS:
        return {
            "allowed": False,
            "requires_confirmation": False,
            "reason": f"Forbidden action: {action_type}"
        }

    # Safe actions
    if action_type in SAFE_ACTIONS:
        return {
            "allowed": True,
            "requires_confirmation": False,
            "reason": "Action is classified as safe"
        }

    # Sensitive actions
    if action_type in CONFIRMATION_REQUIRED_ACTIONS:

        if confirmation_granted:
            return {
                "allowed": True,
                "requires_confirmation": True,
                "reason": "User confirmation granted"
            }

        return {
            "allowed": False,
            "requires_confirmation": True,
            "reason": f"User confirmation required for {action_type}"
        }

    # Unknown actions are denied by default
    return {
        "allowed": False,
        "requires_confirmation": False,
        "reason": f"Unknown action denied: {action_type}"
    }


def get_permission_level(action_type: str) -> str:
    """Return the permission classification for an action."""

    if action_type in SAFE_ACTIONS:
        return "safe"

    if action_type in CONFIRMATION_REQUIRED_ACTIONS:
        return "confirmation_required"

    if action_type in FORBIDDEN_ACTIONS:
        return "forbidden"

    return "unknown"