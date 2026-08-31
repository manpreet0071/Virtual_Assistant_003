from dotenv import load_dotenv
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE, override=True)

api_key = os.getenv("GROQ_API_KEY")

print("GROQ key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError(f"GROQ_API_KEY not found. Checked: {ENV_FILE}")