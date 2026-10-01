# from serpapi import GoogleSearch
from groq import Groq
from json import load, dump
import os
from dotenv import load_dotenv, dotenv_values
import datetime
from serpapi import GoogleSearch

# ================= ENV =================
load_dotenv()
env_vars = dotenv_values(".env")

Username = os.getenv("Username") or os.getenv("NickName")
Assistantname = os.getenv("Assistantname") or os.getenv("AssistantName")
GroqAPIKey = os.getenv("GroqAPIKey")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
os.makedirs(DATA_DIR, exist_ok=True)
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# print("SERPAPI Key Loaded:", SERPAPI_KEY)
# print("G Key Loaded:", GroqAPIKey)

_groq_key = GroqAPIKey or os.getenv('GROQ_API_KEY') or os.getenv('GroqAPI')
if _groq_key:
    client = Groq(api_key=_groq_key)
else:
    client = None
    print('[RealtimeSearchEngine] Warning: Groq API key not found; real-time LLM features will be disabled.')

# PERF FIX: match the fast-model default used elsewhere. This call also
# has to wait on a SerpAPI web search first, so keeping the model itself
# fast matters even more here.
CHAT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Same reasoning as chatbot.py / assistant_controller.py — don't resend
# an ever-growing chat log on every request.
MAX_HISTORY_MESSAGES = 20

# ================= SYSTEM =================
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# ================= CHAT LOG =================
try:
    with open(CHATLOG_PATH, "r") as f:
        ChatLog = load(f)
except:
    with open(CHATLOG_PATH, "w") as f:
        dump([], f)

# ================= GOOGLE SEARCH (FIXED) =================
def WebSearch(query):   # 🔹 renamed ONLY to avoid recursion
    params = {
        "engine": "google",
        "q": query,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_KEY,
        "num": 3  # fewer results = smaller prompt = faster reply, still plenty of context
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    Answer = f"The search results for '{query}' are :\n[start]\n\n"

    for r in results.get("organic_results", []):
        Answer += f"Title : {r.get('title','')}\n"
        Answer += f"Description: {r.get('snippet','')}\n\n"

    if "answer_box" in results:
        Answer += f"Answer : {results['answer_box'].get('answer','')}\n\n"

    Answer += "[end]"
    print(Answer)
    return Answer

# ================= ANSWER CLEANER =================
def AnswerModifier(Answer):
    line = Answer.split("\n")
    non_empty_lines = [line for line in line if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# ================= SYSTEM CHAT =================
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I assist you today?"}
]

# ================= TIME INFO =================
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    time = f"{hour}:{minute}:{second}"
    full_date = f"{day}, {month} {date}, {year}"

    data += "Use This Real-time Information if needed :\n"
    data += f"Day : {day}\n"
    data += f"Date : {date}\n"
    data += f"Month : {month}\n"
    data += f"Year : {year}\n"
    data += f"Time : {time}\n"
    data += f"Full Date : {full_date}\n"

    return data

# ================= MAIN ENGINE =================
def RealtimeSearchEngine(UserInput):
    global SystemChatBot, messages

    with open(CHATLOG_PATH, "r") as f:
        messages = load(f)

    if len(messages) > MAX_HISTORY_MESSAGES:
        messages = messages[-MAX_HISTORY_MESSAGES:]

    messages.append({"role": "user", "content": UserInput})

    SystemChatBot.append({
        "role": "system",
        "content": WebSearch(UserInput)   # 🔹 fixed call
    })

    if client is None:
        SystemChatBot.pop()
        return "[RealtimeSearchEngine] Groq client not configured. Set GroqAPIKey or GROQ_API_KEY to enable real-time LLM searches."

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=800,
        top_p=1,
        stream=True
    )

    Answer = ""

    for chunk in completion:
        if getattr(chunk.choices[0].delta, 'content', None):
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(CHATLOG_PATH, "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

# ================= RUN =================
if __name__ == "__main__":
    while True:
        propmt = input("User: ")
        print(RealtimeSearchEngine(UserInput=propmt))
        