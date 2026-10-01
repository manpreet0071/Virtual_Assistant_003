# # =============================================
# # TTS.py – FAST, NON-BLOCKING, CACHED VERSION
# # =============================================

# import asyncio
# import threading
# import time
# import os
# import re
# import unicodedata

# import pygame
# import edge_tts
# from dotenv import load_dotenv

# # --------------------------------------------------
# # ENV
# # --------------------------------------------------
# load_dotenv()
# VOICE = os.getenv("AssistantVoice", "en-IE-EmilyNeural")
# # AUDIO_FILE = "data.mp3"
# # OUTPUT_DIR = "output"
# # os.makedirs(OUTPUT_DIR, exist_ok=True)
# # AUDIO_FILE = os.path.join(OUTPUT_DIR, "data.mp3")

# # --------------------------------------------------
# # ABSOLUTE PATHS
# # --------------------------------------------------

# TTS_BASE_DIR = os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))
# )

# OUTPUT_DIR = os.path.join(TTS_BASE_DIR, "output")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# AUDIO_FILE = os.path.join(
#     OUTPUT_DIR,
#     "data.mp3"
# )

# print("[TTS] Output file:", AUDIO_FILE)


# # --------------------------------------------------
# # INIT AUDIO ONCE
# # --------------------------------------------------
# pygame.mixer.init()

# # --------------------------------------------------
# # INTERNAL STATE
# # --------------------------------------------------
# _last_spoken_text = None
# _tts_lock = threading.Lock()

# # --------------------------------------------------
# # TEXT SANITIZER (FAST + SAFE)
# # --------------------------------------------------
# def sanitize_for_tts(text: str) -> str:
#     text = unicodedata.normalize("NFKD", text)

#     # Remove emojis + symbols
#     text = re.sub(
#         "["
#         "\U0001F600-\U0001F64F"
#         "\U0001F300-\U0001F5FF"
#         "\U0001F680-\U0001F6FF"
#         "\U0001F700-\U0001F77F"
#         "\U0001F780-\U0001F7FF"
#         "\U0001F800-\U0001F8FF"
#         "\U0001F900-\U0001F9FF"
#         "\U0001FA00-\U0001FAFF"
#         "\U00002700-\U000027BF"
#         "\U00002600-\U000026FF"
#         "]+",
#         "",
#         text,
#     )

#     # Remove markdown / junk
#     text = re.sub(r"[#*_~`>|^+=\[\]{}\\/]", " ", text)

#     # Keep speech punctuation only
#     text = re.sub(r"[^\w\s.,!?'-]", " ", text)

#     return re.sub(r"\s+", " ", text).strip()


# # --------------------------------------------------
# # ASYNC TTS
# # --------------------------------------------------
# async def _generate_audio_async(text: str):
#     communicate = edge_tts.Communicate(
#         text=text,
#         voice=VOICE,
#         rate="+15%",   # 🔥 faster generation
#     )
#     await communicate.save(AUDIO_FILE)


# # --------------------------------------------------
# # PLAY AUDIO
# # --------------------------------------------------
# def _play_audio():
#     pygame.mixer.music.load(AUDIO_FILE)
#     pygame.mixer.music.play()

#     while pygame.mixer.music.get_busy():
#         time.sleep(0.05)

#     pygame.mixer.music.stop()
#     pygame.mixer.music.unload()


# # --------------------------------------------------
# # BACKGROUND TTS WORKER
# # --------------------------------------------------
# def _tts_worker(text: str):
#     try:
#         asyncio.run(_generate_audio_async(text))
#         _play_audio()
#     except Exception as e:
#         print(f"TTS Error: {e}")


# # --------------------------------------------------
# # PUBLIC API
# # --------------------------------------------------
# def TTS(text: str):
#     """
#     Fast TTS:
#     - Non-blocking
#     - Cached
#     - Shortened
#     """

#     global _last_spoken_text

#     if not text or len(text.strip()) < 3:
#         return

#     # 🔥 HARD LIMIT SPEECH LENGTH (BIG SPEED BOOST)
#     text = text.strip()[:220]

#     text = sanitize_for_tts(text)

#     # 🔥 CACHE (do not repeat same speech)
#     if text == _last_spoken_text:
#         return

#     _last_spoken_text = text

#     # Stop current audio instantly
#     if pygame.mixer.music.get_busy():
#         pygame.mixer.music.stop()
#         pygame.mixer.music.unload()

#     # 🔥 RUN TTS IN BACKGROUND THREAD
#     threading.Thread(
#         target=_tts_worker,
#         args=(text,),
#         daemon=True
#     ).start()





# # --------------------------------------------------------------------------------------------------------
# # =============================================
# # TTS.py – FAST + CLEAN (NO GLITCHES)
# # =============================================

# # import asyncio
# # import threading
# # import os
# # import re
# # import unicodedata
# # import time

# # import pygame
# # import edge_tts
# # from dotenv import load_dotenv

# # # --------------------------------------------------
# # # ENV
# # # --------------------------------------------------
# # load_dotenv()
# # VOICE = os.getenv("AssistantVoice", "en-IE-EmilyNeural")

# # OUTPUT_DIR = "output"
# # os.makedirs(OUTPUT_DIR, exist_ok=True)
# # AUDIO_FILE = os.path.join(OUTPUT_DIR, "tts.mp3")

# # # --------------------------------------------------
# # # LOW LATENCY AUDIO INIT
# # # --------------------------------------------------
# # pygame.mixer.pre_init(
# #     frequency=22050,
# #     size=-16,
# #     channels=2,
# #     buffer=256
# # )
# # pygame.mixer.init()

# # # --------------------------------------------------
# # # STATE
# # # --------------------------------------------------
# # _last_spoken_text = None
# # _stop_flag = threading.Event()

# # # --------------------------------------------------
# # # SANITIZE
# # # --------------------------------------------------
# # def sanitize_for_tts(text: str) -> str:
# #     text = unicodedata.normalize("NFKD", text)
# #     text = re.sub(r"[^\w\s.,!?'-]", " ", text)
# #     return re.sub(r"\s+", " ", text).strip()

# # # --------------------------------------------------
# # # STREAM TTS TO FILE
# # # --------------------------------------------------
# # async def _stream_tts(text: str):
# #     communicate = edge_tts.Communicate(
# #         text=text,
# #         voice=VOICE,
# #         rate="+15%"
# #     )

# #     with open(AUDIO_FILE, "wb") as f:
# #         async for chunk in communicate.stream():
# #             if _stop_flag.is_set():
# #                 return
# #             if chunk["type"] == "audio":
# #                 f.write(chunk["data"])

# # # --------------------------------------------------
# # # PLAY AUDIO
# # # --------------------------------------------------
# # def _play_audio():
# #     pygame.mixer.music.load(AUDIO_FILE)
# #     pygame.mixer.music.play()

# #     while pygame.mixer.music.get_busy():
# #         time.sleep(0.03)

# #     pygame.mixer.music.stop()
# #     pygame.mixer.music.unload()

# # # --------------------------------------------------
# # # WORKER
# # # --------------------------------------------------
# # def _tts_worker(text: str):
# #     try:
# #         asyncio.run(_stream_tts(text))
# #         _play_audio()
# #     except Exception as e:
# #         print(f"TTS Error: {e}")

# # # --------------------------------------------------
# # # PUBLIC API
# # # --------------------------------------------------
# # def TTS(text: str):
# #     global _last_spoken_text

# #     if not text or len(text.strip()) < 3:
# #         return

# #     text = sanitize_for_tts(text.strip()[:220])

# #     if text == _last_spoken_text:
# #         return

# #     _last_spoken_text = text

# #     _stop_flag.set()
# #     pygame.mixer.stop()
# #     _stop_flag.clear()

# #     threading.Thread(
# #         target=_tts_worker,
# #         args=(text,),
# #         daemon=True
# #     ).start()


# =============================================
# TTS.py – FAST + SAFE + NON-BLOCKING
# =============================================

import asyncio
import threading
import time
import os
import re
import queue
import unicodedata

import pygame
import edge_tts
from dotenv import load_dotenv


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH, override=True)

VOICE = os.getenv(
    "AssistantVoice",
    "en-IE-EmilyNeural"
)


# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

AUDIO_FILE = os.path.join(
    OUTPUT_DIR,
    "data.mp3"
)

print("[TTS] Audio file:", AUDIO_FILE)


# --------------------------------------------------
# AUDIO INITIALIZATION
# --------------------------------------------------

pygame.mixer.init()


# --------------------------------------------------
# INTERNAL STATE
# --------------------------------------------------

_last_spoken_text = None

_tts_lock = threading.Lock()

_generation_lock = threading.Lock()

# BUG FIX / PERF: chatbot.py now calls TTS() once per finished sentence
# so speech can start before the whole reply has finished generating.
# The old TTS() stopped whatever was currently playing and jumped
# straight into the new text on every call — fine for "speak this one
# reply", but wrong for "speak these sentences in order without
# chopping each other off". A small queue + one persistent worker
# thread lets sentences play back-to-back in order, while a single new
# *reply* (see TTS_interrupt()) can still cut in and clear anything
# still queued from a previous, no-longer-relevant reply.
_speech_queue: "queue.Queue[str]" = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


def _speech_worker():
    while True:
        text = _speech_queue.get()
        try:
            asyncio.run(_generate_audio_async(text))
            _play_audio()
        except Exception as e:
            print(f"TTS Generation/Playback Error: {e}")
        finally:
            _speech_queue.task_done()


def _ensure_worker_running():
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            threading.Thread(target=_speech_worker, daemon=True).start()
            _worker_started = True


def TTS_interrupt():
    """Clear any not-yet-spoken sentences (e.g. a brand new question
    came in while the previous answer was still being read out)."""
    try:
        while True:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
    except queue.Empty:
        pass
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception:
        pass


# --------------------------------------------------
# TEXT SANITIZER
# --------------------------------------------------

def sanitize_for_tts(text: str) -> str:

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    # Remove emojis
    text = re.sub(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U00002600-\U000026FF"
        "]+",
        "",
        text
    )

    # Remove markdown characters
    text = re.sub(
        r"[#*_~`>|^+=\\[\]{}]",
        " ",
        text
    )

    # Keep speech characters
    text = re.sub(
        r"[^\w\s.,!?'-]",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


# --------------------------------------------------
# GENERATE AUDIO
# --------------------------------------------------

async def _generate_audio_async(text: str):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="+15%"
    )

    await communicate.save(
        AUDIO_FILE
    )


# --------------------------------------------------
# PLAY AUDIO
# --------------------------------------------------

def _play_audio():

    with _tts_lock:

        if not os.path.exists(AUDIO_FILE):
            print(
                "[TTS] ERROR: Audio file was not created:"
            )
            print(AUDIO_FILE)
            return

        try:

            pygame.mixer.music.load(
                AUDIO_FILE
            )

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.03)

            pygame.mixer.music.stop()

            try:
                pygame.mixer.music.unload()
            except:
                pass

        except Exception as e:

            print(
                f"TTS Playback Error: {e}"
            )


# --------------------------------------------------
# WORKER
# --------------------------------------------------

# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def TTS(text: str):
    """Queue text to be spoken. Safe to call multiple times quickly in a
    row (e.g. once per sentence as an LLM reply streams in) — each call
    is spoken in order after the previous one finishes, instead of
    interrupting it.
    """

    global _last_spoken_text

    if not text:
        return

    text = text.strip()

    if len(text) < 3:
        return

    # Limit speech
    text = text[:220]

    # Clean text
    text = sanitize_for_tts(text)

    if not text:
        return

    # Don't repeat same sentence twice in a row
    if text == _last_spoken_text:
        return

    _last_spoken_text = text

    _ensure_worker_running()
    _speech_queue.put(text)