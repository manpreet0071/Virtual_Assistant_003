# from groq import Groq
# from prompts import SYSTEM_PROMPT
# import os, json

# _groq_key = os.getenv("GROQ_API_KEY") or os.getenv('GroqAPI') or os.getenv('GroqAPIKey')
# if _groq_key:
#     client = Groq(api_key=_groq_key)
# else:
#     client = None
#     print('[llm] Warning: GROQ API key not found; ask_llm will return fallback responses.')
# MODEL = "openai/gpt-oss-120b"

# def ask_llm(user_text: str) -> dict:
#     if client is None:
#         print('[llm] GROQ client not configured — returning fallback.')
#         return {
#             "address": "none",
#             "emotion": "calm",
#             "speak": user_text,
#             "display": user_text,
#             "action": {"type": "none", "command": ""}
#         }

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_text}
#         ]
#     )

#     raw = response.choices[0].message.content
#     # Try to parse the LLM output as JSON. If the model returns extra text
#     # before/after the JSON, attempt to extract the first balanced JSON object.
#     try:
#         return json.loads(raw)
#     except Exception:
#         # find first balanced JSON object
#         def extract_json(text: str) -> str | None:
#             start = text.find('{')
#             if start == -1:
#                 return None
#             depth = 0
#             for i, ch in enumerate(text[start:], start=start):
#                 if ch == '{':
#                     depth += 1
#                 elif ch == '}':
#                     depth -= 1
#                     if depth == 0:
#                         return text[start:i+1]
#             return None

#         jtext = extract_json(raw)
#         if jtext:
#             try:
#                 return json.loads(jtext)
#             except Exception:
#                 pass

#     # Fallback: echo the raw text into display/speak fields to avoid crashing.
#     # The assistant will still function but show the raw response.
#     print("[llm] Warning: failed to parse JSON from model output; using fallback.")
#     return {
#         "address": "none",
#         "emotion": "calm",
#         "speak": raw.strip(),
#         "display": raw.strip(),
#         "action": {"type": "none", "command": ""}
#     }

from groq import Groq, AuthenticationError
from prompts import SYSTEM_PROMPT
import os, json
from dotenv import load_dotenv

# Load backend/.env explicitly (relative to this file) instead of relying on
# some other module having already called load_dotenv() first via import order.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

_groq_key = os.getenv("GROQ_API_KEY") or os.getenv('GroqAPI') or os.getenv('GroqAPIKey')
if _groq_key:
    client = Groq(api_key=_groq_key)
else:
    client = None
    print('[llm] Warning: GROQ API key not found; ask_llm will return fallback responses.')
MODEL = "openai/gpt-oss-120b"

_FALLBACK = {
    "address": "none",
    "emotion": "calm",
    "speak": "",
    "display": "",
    "action": {"type": "none", "command": ""}
}

def ask_llm(user_text: str) -> dict:
    if client is None:
        print('[llm] GROQ client not configured — returning fallback.')
        return {
            "address": "none",
            "emotion": "calm",
            "speak": user_text,
            "display": user_text,
            "action": {"type": "none", "command": ""}
        }

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
    except AuthenticationError:
        print('[llm] Groq rejected the API key (401 Invalid API Key). '
              'Check GROQ_API_KEY / GroqAPIKey in backend/.env — it is missing, '
              'expired, revoked, or was copied from _env.example.')
        fallback = dict(_FALLBACK)
        fallback["speak"] = fallback["display"] = user_text
        return fallback
    except Exception as e:
        print(f'[llm] Groq request failed: {e}')
        fallback = dict(_FALLBACK)
        fallback["speak"] = fallback["display"] = user_text
        return fallback

    raw = response.choices[0].message.content
    # Try to parse the LLM output as JSON. If the model returns extra text
    # before/after the JSON, attempt to extract the first balanced JSON object.
    try:
        return json.loads(raw)
    except Exception:
        # find first balanced JSON object
        def extract_json(text: str) -> str | None:
            start = text.find('{')
            if start == -1:
                return None
            depth = 0
            for i, ch in enumerate(text[start:], start=start):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
            return None

        jtext = extract_json(raw)
        if jtext:
            try:
                return json.loads(jtext)
            except Exception:
                pass

    # Fallback: echo the raw text into display/speak fields to avoid crashing.
    # The assistant will still function but show the raw response.
    print("[llm] Warning: failed to parse JSON from model output; using fallback.")
    return {
        "address": "none",
        "emotion": "calm",
        "speak": raw.strip(),
        "display": raw.strip(),
        "action": {"type": "none", "command": ""}
    }