from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search,playonyt
from dotenv import dotenv_values , load_dotenv
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

load_dotenv()
env_vars = dotenv_values(".env")
GroqAPIKey = os.getenv("GroqAPIKey")

# Dry-run mode: when enabled (env DRY_RUN=1 or true), stub out UI/network actions
DRY_RUN = os.getenv("DRY_RUN", "").lower() in ("1", "true", "yes")
if DRY_RUN:
    print("[DRY_RUN] Automation stubs active — no UI or network actions will run")
    def appopen_stub(*a, **k):
        print("[DRY_RUN] appopen", a, k)
        return True
    def close_stub(*a, **k):
        print("[DRY_RUN] close", a, k)
        return True
    def webopen_stub(*a, **k):
        print("[DRY_RUN] webopen", a, k)
        return True
    def playonyt_stub(*a, **k):
        print("[DRY_RUN] playonyt", a, k)
        return True
    def search_stub(*a, **k):
        print("[DRY_RUN] search", a, k)
        return True

    # override imported names with stubs
    appopen = appopen_stub
    close = close_stub
    webopen = webopen_stub
    playonyt = playonyt_stub
    search = search_stub

# print(GroqAPIKey)

classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d","webanswers-webanswers_table_webanswers-table", "dDoNo ikb48b gsrt", "sXLa0e", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


_groq_key = GroqAPIKey or os.getenv('GROQ_API_KEY') or os.getenv('GroqAPI')
if _groq_key:
    client = Groq(api_key=_groq_key)
else:
    client = None
    print('[Automation_engine] Warning: Groq API key not found; content AI features will be limited.')

professional_responses = [
    "your satisfaction is my priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]

messages = []

_username = os.getenv("Username") or os.getenv("NickName") or "User"
SystemChatBot = [{"role" : "system", "content" : f"Hello,I am {_username},You are content writer.You have to write content for me like letters,application,story,text,youtube descriptions,code ,essays,notes,songs,poems ,etc. Be professional and polite while writing content. Use formal tone."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

# GoogleSearch("yt")

def Content(Topic):
    
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        if DRY_RUN:
            print(f"[DRY_RUN] Would open notepad with {File}")
            return
        subprocess.Popen([default_text_editor, File])
        
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        if client is None:
            # Fallback: return the prompt echoed — user can still get a file with the prompt
            print('[Automation_engine] Groq client not configured; returning prompt as content fallback.')
            return f"{prompt}"

        completion = client.chat.completions.create(
            model = "llama-3.1-8b-instant",
            messages = SystemChatBot + messages,
            max_tokens = 2048,
            temperature = 0.7,
            top_p = 1,
            stream = True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if getattr(chunk.choices[0].delta, 'content', None):
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>","")
        messages.append({"role": "assistant", "content": Answer})

        return Answer

    Topic: str = Topic.replace("Content ","")
    ContentByAI = ContentWriterAI(Topic)

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{Topic.lower().replace(' ','')}.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True

# Content("write an application for sick leave")
def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic.replace(' ','+')}"
    webbrowser.open(Url4Search)
    return True

def YoutubePlay(query):
    playonyt(query)
    return True
# YoutubePlay("hare rama hare krishna")


def OpenApp(app, sess=requests.Session()):
    # quick direct mappings for common sites/apps
    name_low = app.strip().lower()
    if name_low in ("youtube", "yt", "youtube.com"):
        try:
            webopen("https://www.youtube.com")
            return True
        except Exception:
            pass
    if name_low in ("google", "google.com"):
        try:
            webopen("https://www.google.com")
            return True
        except Exception:
            pass

    # 1️⃣ Try opening installed app
    try:
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except:
        pass  # app not installed → go web

    # 2️⃣ Google search (spell mistakes handled by Google)
    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {
            "User-Agent": useragent,
            "Accept-Language": "en-US,en;q=0.9"
        }
        r = sess.get(url, headers=headers, timeout=10)
        return r.text if r.status_code == 200 else None

    # 3️⃣ Extract first REAL website link
    def extract_first_link(html):
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("a"):
            href = a.get("href")
            if href and href.startswith("/url?q="):
                clean = href.split("/url?q=")[1].split("&")[0]
                if clean.startswith("http"):
                    return clean
        return None

    html = search_google(app)

    if html:
        link = extract_first_link(html)
        if link:
            webopen(link)
            return True

    # 4️⃣ Absolute fallback (never fails)
    webopen(f"https://www.google.com/search?q={app}")
    return True

# OpenApp("instagram")
# OpenApp("facebook")
# OpenApp("github")

def CloseApp(app):
    # BUG FIX: this used to silently fall through with no return value
    # (implicit None) for Chrome, instead of a proper True/False, which
    # made callers unable to tell whether the "close" actually happened.
    # Chrome is still deliberately skipped here (closing it can kill
    # unrelated tabs/windows), but we now report that clearly.
    if "chrome" in app:
        print(f"[Automation_engine] Skipping close for '{app}' (Chrome close via AppOpener is unreliable).")
        return False

    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[Automation_engine] Could not close '{app}': {e}")
        return False
        
# CloseApp("whatsapp")
        
def System(command):
    
    def mute():
        keyboard.press_and_release("volume mute")
        
    def unmute():
        keyboard.press_and_release("volume mute")
    def volume_up():
        keyboard.press_and_release("volume up")
    def volume_down():
        keyboard.press_and_release("volume down")
    def shutdown():
        os.system("shutdown /s /t 1")
    def restart():
        os.system("shutdown /r /t 1")
    def signout():
        os.system("shutdown /l")
    commands = {
        "mute": mute,
        "unmute": unmute,
        "volume up": volume_up,
        "volume down": volume_down,
        "shutdown": shutdown,
        "restart": restart,
        "signout": signout
    }
    if command in commands:
        commands[command]()
        return True
    else:
        return False
    
async def TranslateAndExecute(commands:list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp,command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp,command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(YoutubePlay,command.removeprefix("play "))
            funcs.append(fun)
            
        elif command.startswith(("google search ", "search ")):
            prefix = "google search " if command.startswith("google search ") else "search "
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix(prefix))
            funcs.append(fun)


        elif command.startswith(("youtube search ", "search on youtube ")):
            prefix = "youtube search " if command.startswith("youtube search ") else "search on youtube "
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix(prefix))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System,command.removeprefix("system "))
            funcs.append(fun)

        elif command.startswith(("write ", "code ", "make ")):
            for prefix in ("write ", "code ", "make "):
                if command.startswith(prefix):
                    fun = asyncio.to_thread(Content, command.removeprefix(prefix))
                    break
            funcs.append(fun)

        else:
            print(f"No Function found. For {command}")
    
    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result,str):
            yield result
        else:
            yield result
            
async def Automation(commands:list[str]):

    results = []
    async for result in TranslateAndExecute(commands):
        results.append(result)
    return results


def Run(commands):
    """Synchronous convenience wrapper around Automation() for callers
    (e.g. Main.py) that don't want to manage asyncio themselves.

    Accepts either a single command string or a list of command strings.
    Safe to call from a thread that has no running event loop (e.g. the
    voice-listener thread in Main.py).
    """
    if isinstance(commands, str):
        commands = [commands]

    try:
        asyncio.get_running_loop()
        # We're already inside an event loop (e.g. called from async code) —
        # schedule on a fresh loop in a separate thread to avoid conflicts.
        result_holder = {}

        def _runner():
            result_holder["result"] = asyncio.run(Automation(commands))

        import threading
        t = threading.Thread(target=_runner)
        t.start()
        t.join()
        return result_holder.get("result", [])
    except RuntimeError:
        # No running loop in this thread — safe to use asyncio.run directly.
        return asyncio.run(Automation(commands))


# if __name__ == "__main__":
    # asyncio.run(Automation(["open yt","open insta","open telegram","play hanuman chilsa","search rcb","write a poem"]))