import os
import webbrowser
import urllib.parse
import subprocess
import shutil
import platform
import re
from typing import Optional


# ============ COMMAND KEYWORDS DATABASE ============

COMMAND_KEYWORDS = {
    "open": ["open", "launch", "start", "run"],
    "chrome": ["chrome", "google chrome", "browser"],
    "edge": ["edge", "microsoft edge"],
    "firefox": ["firefox"],
    "calculator": ["calculator", "calc"],
    "notepad": ["notepad", "note", "text editor"],
    "whatsapp": ["whatsapp", "whatsap", "wa"],
    "send": ["send", "message", "text"],
    "call": ["call", "ring", "dial"],
    "search": ["search", "google", "find", "look for"],
    "code": ["code", "write code", "create code", "make code"],
    "file": ["file", "create file", "write file"],
    "email": ["email", "mail", "compose", "message"],
}


def match_keyword(text: str, keywords: list) -> bool:
    """Check if any keyword matches in text"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def extract_quoted_text(text: str) -> Optional[str]:
    """Extract text within quotes"""
    match = re.search(r'["\'](.+?)["\']', text)
    return match.group(1) if match else None


def extract_recipient(text: str) -> Optional[str]:
    """Extract recipient name or phone number"""
    # Pattern: "to [name/number]"
    match = re.search(r'\bto\s+([\w\s\-\+\.@]+?)(?:\s+(?:on|via)\s+|$)', text, re.I)
    if match:
        return match.group(1).strip()
    return None


# ============ WHATSAPP FUNCTION ============

def send_whatsapp(message: str, phone: Optional[str] = None, contact_name: Optional[str] = None) -> str:
	"""Send WhatsApp message - with clear feedback"""
	quoted = urllib.parse.quote(message or "")

	# Helper to attempt automation
	def try_automation(msg: str, contact: Optional[str]) -> bool:
		try:
			import time
			import pyperclip
			import pyautogui
			time.sleep(1.5)
			if contact:
				pyautogui.typewrite(contact)
				time.sleep(0.2)
				pyautogui.press('enter')
				time.sleep(0.4)
			pyperclip.copy(msg)
			pyautogui.hotkey('ctrl', 'v')
			time.sleep(0.05)
			pyautogui.press('enter')
			return True
		except Exception:
			return False

	# Try protocol handler
	try:
		if phone:
			prot = f"whatsapp://send?phone={phone}&text={quoted}"
		else:
			prot = f"whatsapp://send?text={quoted}"

		if platform.system() == "Windows":
			os.startfile(prot)
		else:
			webbrowser.open(prot)

		target = contact_name or phone or "default"
		if try_automation(message, contact_name):
			return f"✅ WhatsApp message sent to {target}"
		return f"✅ WhatsApp opened. Ready to send to {target}"
	except Exception:
		pass

	# Fallback to web
	if phone:
		url = f"https://wa.me/{phone}?text={quoted}"
	else:
		url = "https://web.whatsapp.com"

	webbrowser.open(url)
	target = contact_name or phone or "selected contact"
	return f"✅ WhatsApp Web opened. Send to {target}"


def make_call(number: str) -> str:
	"""Initiate phone call"""
	url = f"tel:{number}"
	try:
		webbrowser.open(url)
		return f"✅ Calling {number}"
	except Exception as e:
		return f"❌ Failed to call {number}: {e}"


def google_search(query: str) -> str:
	"""Search on Google"""
	url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
	webbrowser.open(url)
	return f"✅ Searching Google for: {query}"


def open_url(url: str) -> str:
	"""Open a specific URL"""
	if not url.startswith("http"):
		url = "https://" + url
	webbrowser.open(url)
	return f"✅ Opened: {url}"


def write_code_in_vscode(path: str, content: str) -> str:
	"""Write code to file and open in VS Code"""
	try:
		os.makedirs(os.path.dirname(path), exist_ok=True)
		with open(path, "w", encoding="utf-8") as f:
			f.write(content)
		try:
			subprocess.Popen(["code", path], shell=True)
			return f"✅ File created and opened in VS Code: {path}"
		except Exception:
			return f"✅ File created: {path}"
	except Exception as e:
		return f"❌ Failed to create file: {e}"


def compose_mail(subject: str, body: str, to: Optional[str] = None) -> str:
	"""Compose email"""
	mailto = "mailto:"
	if to:
		mailto += urllib.parse.quote(to)
	params = {}
	if subject:
		params["subject"] = subject
	if body:
		params["body"] = body
	if params:
		mailto += "?" + urllib.parse.urlencode(params)
	webbrowser.open(mailto)
	return f"✅ Email composer opened {f'to {to}' if to else ''}"


def open_application(name: str) -> str:
	"""Open applications by name"""
	name = name.lower().strip()
	candidates = []

	if match_keyword(name, COMMAND_KEYWORDS["chrome"]):
		candidates = [
			"chrome",
			"google-chrome",
			r"C:\Program Files\Google\Chrome\Application\chrome.exe",
			r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
		]
	elif match_keyword(name, COMMAND_KEYWORDS["edge"]):
		candidates = [
			"msedge",
			r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
			r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
		]
	elif match_keyword(name, COMMAND_KEYWORDS["firefox"]):
		candidates = ["firefox"]
	elif match_keyword(name, COMMAND_KEYWORDS["calculator"]):
		candidates = ["calc.exe"]
	elif match_keyword(name, COMMAND_KEYWORDS["notepad"]):
		candidates = ["notepad.exe"]
	else:
		return f"❌ Unknown app: {name}"

	for candidate in candidates:
		try:
			exe = None
			if os.path.exists(candidate):
				exe = candidate
			else:
				exe = shutil.which(candidate)

			if not exe:
				continue

			if platform.system() == "Windows":
				subprocess.Popen([exe], shell=False)
			else:
				subprocess.Popen([exe])
			return f"✅ Opened {name}"
		except Exception:
			continue

	return f"❌ Could not open {name}"


def perform_action(command: str, raw_text: str = "", model_output: str = "") -> str:
	"""Main command router - understands user intent clearly"""
	lc = command.lower()
	
	print(f"\n🔍 Analyzing command: '{command[:50]}...'")  # Debug output

	# ========== OPENING APPLICATIONS ==========
	if match_keyword(lc, COMMAND_KEYWORDS["open"]):
		if match_keyword(lc, COMMAND_KEYWORDS["chrome"]):
			return open_application("chrome")
		elif match_keyword(lc, COMMAND_KEYWORDS["calculator"]):
			return open_application("calculator")
		elif match_keyword(lc, COMMAND_KEYWORDS["notepad"]):
			return open_application("notepad")
		elif "browser" in lc or "internet" in lc:
			return google_search("google.com")

	# ========== WHATSAPP ==========
	if match_keyword(lc, COMMAND_KEYWORDS["whatsapp"]):
		# Extract message and recipient
		msg = extract_quoted_text(command) or raw_text or "Hello"
		recipient = extract_recipient(command)
		
		# Check if recipient is phone number or name
		phone = None
		contact_name = None
		if recipient:
			if re.match(r'^\d+$', recipient.replace("+", "").replace("-", "")):
				phone = recipient.replace("-", "")
			else:
				contact_name = recipient
		
		print(f"  📱 Message: '{msg[:30]}...'")
		if recipient:
			print(f"  👤 To: {recipient}")
		
		return send_whatsapp(msg, phone=phone, contact_name=contact_name)

	# ========== PHONE CALL ==========
	if match_keyword(lc, COMMAND_KEYWORDS["call"]):
		# Extract phone number
		digits = re.findall(r'\d+', lc)
		if digits:
			number = "".join(digits)
			print(f"  📞 Calling: {number}")
			return make_call(number)
		return "❌ No phone number found"

	# ========== SEARCH ==========
	if match_keyword(lc, COMMAND_KEYWORDS["search"]):
		# Extract search query
		query = raw_text or command.replace("search", "").replace("google", "").strip()
		if extract_quoted_text(command):
			query = extract_quoted_text(command)
		print(f"  🔎 Searching: '{query[:30]}...'")
		return google_search(query)

	# ========== WRITE CODE ==========
	if match_keyword(lc, COMMAND_KEYWORDS["code"]):
		# Extract code block from output
		code_match = re.search(r'```(?:python|js|txt)?\n([\s\S]+?)```', model_output or command)
		
		if code_match:
			content = code_match.group(1)
			filename = "assistant_code.py"
			
			# Try to find filename
			file_match = re.search(r'(?:file|as)\s+[\'\"]?(\S+\.py)[\'\"]?', command, re.I)
			if file_match:
				filename = file_match.group(1)
			
			print(f"  💾 Creating file: {filename}")
			return write_code_in_vscode(filename, content)
		
		return "❌ No code block found to write"

	# ========== EMAIL ==========
	if match_keyword(lc, COMMAND_KEYWORDS["email"]):
		subject = re.search(r'subject[:\s]+["\']?([^"\']+)["\']?', command, re.I)
		body = extract_quoted_text(command) or raw_text
		to = extract_recipient(command)
		
		return compose_mail(
			subject.group(1) if subject else "",
			body or "",
			to
		)

	# ========== OPEN URL ==========
	if "http" in lc or "www" in lc:
		url_match = re.search(r'https?://[\w\-./?=&%]+', command)
		if url_match:
			print(f"  🌐 Opening URL: {url_match.group(0)[:50]}")
			return open_url(url_match.group(0))

	# ========== NO MATCH ==========
	print(f"  ❓ Command not recognized")
	return "❌ Could not understand the command. Try: 'open chrome', 'send whatsapp to john', 'search python', 'call 123456'"
