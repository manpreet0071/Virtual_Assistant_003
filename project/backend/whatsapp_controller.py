import re
import time
import webbrowser
import pyautogui
import pyperclip
from AppOpener import open as appopen
import cv2
pyautogui.FAILSAFE = True

# Check if OpenCV is available for confidence-based image matching
try:
    import cv2  # noqa: F401
    _cv2_available = True
except Exception:
    _cv2_available = False

# =========================
# UTILITIES
# =========================

def wait(sec=1.0):
    time.sleep(sec)


def safe_locate_on_screen(image_path, confidence=0.75, timeout=8):
    """Try to locate an image on screen. If OpenCV isn't available, fall back to
    Pillow-based locate (no confidence). Returns the location or None.
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            if _cv2_available:
                loc = pyautogui.locateOnScreen(image_path, confidence=confidence)
            else:
                loc = pyautogui.locateOnScreen(image_path)
            if loc:
                return loc
        except TypeError:
            try:
                loc = pyautogui.locateOnScreen(image_path)
                if loc:
                    return loc
            except Exception:
                pass
        except Exception:
            pass
        time.sleep(0.3)
    return None

def clean_name(name: str) -> str:
    return name.strip()

# =========================
# PROMPT PARSER
# =========================

def parse_prompt(prompt: str):
    prompt = prompt.strip()
    if not prompt:
        return None

    lower = prompt.lower()

    if lower.startswith("video call"):
        name = lower.replace("video call", "").replace("whatsapp", "").strip()
        return {"action": "video", "name": name, "message": None}

    if lower.startswith("call"):
        name = lower.replace("call", "").replace("whatsapp", "").strip()
        return {"action": "call", "name": name, "message": None}

    match = re.search(r"(send|message)\s+(.*?)\s+to\s+(.*)", lower)
    if match:
        return {
            "action": "message",
            "message": match.group(2).strip(),
            "name": match.group(3).strip()
        }

    parts = prompt.split()
    if len(parts) == 2:
        return {
            "action": "message",
            "message": parts[0],
            "name": parts[1]
        }

    if len(parts) == 1:
        return {
            "action": "open",
            "name": parts[0],
            "message": None
        }

    return None

# =========================
# WHATSAPP DESKTOP
# =========================

def open_whatsapp_desktop():
    try:
        appopen("whatsapp", match_closest=True, throw_error=True)
        wait(3)
        return True
    except:
        return False

def whatsapp_desktop_search(name):
    pyautogui.hotkey("alt", "k")
    wait(0.6)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyperclip.copy(name)
    pyautogui.hotkey("ctrl", "v")
    wait(1.0)

    pyautogui.press("enter")
    wait(1.2)

def clear_message_box():
    pyautogui.press("down")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    wait(0.2)

def send_message_desktop(message):
    clear_message_box()
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    wait(0.3)
    pyautogui.press("enter")

# =========================
# UNIVERSAL CALL (RESIZE SAFE)
# =========================

import time
import pyautogui

def universal_call(call_type="voice", timeout=8):
    """
    call_type: 'voice' or 'video'
    """

    # Step 1: Call menu button
    call_menu_icon = cv2.imread(r"d:/VIRTUAL _ANIME_ASSISTANT/project_s/backend/Data/call_menu.png")   # camera + call icon (top button)

    # Step 2: Dropdown options
    voice_icon = cv2.imread(r"d:/VIRTUAL _ANIME_ASSISTANT/project_s/backend/Data/voice_call.png")
    video_icon = cv2.imread(r"d:/VIRTUAL _ANIME_ASSISTANT/project_s/backend/Data/video_call.png")

    target_icon = voice_icon if call_type == "voice" else video_icon

    # ---- Open call dropdown ----
    menu_loc = safe_locate_on_screen(call_menu_icon, confidence=0.75, timeout=timeout)
    if not menu_loc:
        print("[ERROR] Call menu not found")
        return False

    pyautogui.moveTo(pyautogui.center(menu_loc), duration=0.25) 
    pyautogui.click()
    time.sleep(0.6)  # allow dropdown to appear

    # ---- Click voice / video button ----
    option_loc = safe_locate_on_screen(target_icon, confidence=0.75, timeout=timeout)
    if option_loc:
        pyautogui.moveTo(pyautogui.center(option_loc), duration=0.25)
        pyautogui.click()
        return True

    print(f"[ERROR] {call_type} call option not found")
    return False


# =========================
# WHATSAPP WEB
# =========================

def open_whatsapp_web():
    webbrowser.open("https://web.whatsapp.com")
    time.sleep(12)

def whatsapp_web_search(name):
    pyautogui.hotkey("ctrl", "alt", "/")
    wait(1)

    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")

    pyperclip.copy(name)
    pyautogui.hotkey("ctrl", "v")
    wait(2)

    pyautogui.press("enter")
    wait(2)

def send_message_web(message):
    clear_message_box()
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    wait(0.4)
    pyautogui.press("enter")

# =========================
# MAIN CONTROLLER
# =========================

def WhatsAppController(prompt):
    parsed = parse_prompt(prompt)
    if not parsed:
        return {"success": False, "error": "Invalid prompt"}

    action = parsed["action"]
    name = clean_name(parsed["name"])
    message = parsed["message"]

    # ---------- DESKTOP ----------
    if open_whatsapp_desktop():
        whatsapp_desktop_search(name)

        if action == "message":
            send_message_desktop(message)
            return {"success": True, "method": "desktop"}

        if action in ("call", "video"):
            call_type = "voice" if action == "call" else "video"
            universal_call(call_type)
            return {"success": True, "method": "desktop"}

        return {"success": True, "method": "desktop"}

    # ---------- WEB FALLBACK ----------
    open_whatsapp_web()
    whatsapp_web_search(name)

    if action == "message":
        send_message_web(message)
        return {"success": True, "method": "web"}

    if action in ("call", "video"):
        call_type = "voice" if action == "call" else "video"
        universal_call(call_type)
        return {"success": True, "method": "web"}

    return {"success": False, "error": "Unhandled action"}

# =========================
# RUN LOOP
# =========================

if __name__ == "__main__":
    while True:
        user_prompt = input("Prompt: ")
        if user_prompt.lower() in ("exit", "quit"):
            break

        print(WhatsAppController(user_prompt))