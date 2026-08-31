import os
import time
import requests
from random import randint
from PIL import Image
from dotenv import load_dotenv

# =========================
# PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
CONTROL_FILE = os.path.join(BASE_DIR, "..", "Frontend", "Files", "ImageGeneration.data")

os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# ENV
# =========================

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# =========================
# FILE HELPERS
# =========================

def write_file(text):
    with open(CONTROL_FILE, "w") as f:
        f.write(text)

def read_file():
    if not os.path.exists(CONTROL_FILE):
        return ""
    with open(CONTROL_FILE, "r") as f:
        return f.read().strip()

# =========================
# IMAGE API
# =========================

def call_hf(prompt, seed):
    payload = {
        "inputs": prompt,
        "parameters": {
            "seed": seed,
            "width": 1024,
            "height": 1024
        }
    }

    r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=90)

    if r.headers.get("content-type", "").startswith("image"):
        return r.content

    try:
        err = r.json()
        print("HF API error:", err)
        return "PERMISSION_ERROR"
    except:
        return None

# =========================
# GENERATION
# =========================

def generate(prompt):
    safe_prompt = prompt.replace(" ", "_")

    for i in range(4):
        write_file(f"PROGRESS:{int((i / 4) * 100)}")

        result = call_hf(prompt, randint(1, 9999999))

        if result == "PERMISSION_ERROR":
            write_file("ERROR:HF_PERMISSION")
            return False

        if not result:
            print(f"Image {i+1} failed.")
            continue

        path = os.path.join(DATA_DIR, f"{safe_prompt}{i+1}.jpg")

        with open(path, "wb") as f:
            f.write(result)

        try:
            Image.open(path).verify()
        except:
            print("Invalid image:", path)

    return True

# =========================
# MAIN LOOP
# =========================

print("ImageGeneration service running...")

while True:
    data = read_file()

    if not data:
        time.sleep(1)
        continue

    if data.startswith("True"):
        _, prompt = data.split(",", 1)

        success = generate(prompt)

        if success:
            write_file("False,False")
            break
        else:
            write_file("False,False")
            break

    time.sleep(1)