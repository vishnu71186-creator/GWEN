import subprocess
import shutil


APP_ALLOWLIST = {
    "text_editor": ["mousepad", "gedit", "kate", "xed"],
    "calculator": ["galculator", "gnome-calculator", "kcalc"],
    "terminal": ["xfce4-terminal", "gnome-terminal", "konsole"],
    "firefox": ["firefox"],
}


def open_application(application: str) -> dict:
    application = application.lower().strip()

    if application not in APP_ALLOWLIST:
        return {
            "success": False,
            "action": "open_application",
            "message": f"Application not allowed: {application}"
        }

    candidates = APP_ALLOWLIST[application]

    executable = None

    for candidate in candidates:
        executable = shutil.which(candidate)

        if executable:
            break

    if executable is None:
        return {
            "success": False,
            "action": "open_application",
            "message": f"No installed application found for {application}"
        }

    try:
        subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return {
            "success": True,
            "action": "open_application",
            "application": application,
            "executable": executable,
            "message": f"Successfully launched {application}"
        }

    except Exception as error:
        return {
            "success": False,
            "action": "open_application",
            "message": str(error)
        }