modules = [
    ('groq','groq'),
    ('dotenv','dotenv'),
    ('rich','rich'),
    ('cohere','cohere'),
    ('requests','requests'),
    ('PIL','PIL'),
    ('serpapi','serpapi'),
    ('pywhatkit','pywhatkit'),
    ('bs4','bs4'),
    ('AppOpener','AppOpener'),
    ('keyboard','keyboard'),
    ('pyautogui','pyautogui'),
    ('pyperclip','pyperclip'),
    ('cv2','cv2'),
    ('pygame','pygame'),
    ('edge_tts','edge_tts'),
    ('groq','groq'),
]

for name, mod in modules:
    try:
        __import__(mod)
        print(f"OK: {name}")
    except Exception as e:
        print(f"FAIL: {name} -> {e}")
