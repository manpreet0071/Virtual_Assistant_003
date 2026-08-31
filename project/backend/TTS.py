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

def _tts_worker(text: str):

    with _generation_lock:

        try:

            asyncio.run(
                _generate_audio_async(text)
            )

        except Exception as e:

            print(
                f"TTS Generation Error: {e}"
            )

            return

    _play_audio()


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def TTS(text: str):

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

    # Don't repeat same response
    if text == _last_spoken_text:
        return

    _last_spoken_text = text

    # Stop currently playing audio
    try:

        if pygame.mixer.music.get_busy():

            pygame.mixer.music.stop()

            try:
                pygame.mixer.music.unload()
            except:
                pass

    except Exception as e:

        print(
            f"[TTS] Stop error: {e}"
        )

    # Start background TTS
    threading.Thread(
        target=_tts_worker,
        args=(text,),
        daemon=True
    ).start()