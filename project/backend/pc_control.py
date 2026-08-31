import os
import webbrowser
import urllib.parse
import subprocess
import shutil
import platform
import re
import glob
import time
from typing import Optional


# ============ COMMAND KEYWORDS DATABASE ============

COMMAND_KEYWORDS = {
    "open": ["open", "launch", "start", "run"],
    "youtube": ["youtube", "yt", "tube"],
    "spotify": ["spotify", "music"],
    "chrome": ["chrome", "google chrome"],
    "calculator": ["calculator", "calc"],
    "notepad": ["notepad", "note", "text editor"],
    "whatsapp": ["whatsapp", "whatsap", "wa"],
    "send": ["send", "message", "text"],
    "call": ["call", "ring", "dial"],
    "search": ["search", "google"],
    "play": ["play"],
    "code": ["code", "write code", "create code", "make code"],
    "email": ["email", "mail", "compose"],
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
    match = re.search(r'\bto\s+([\w\s\-\+\.@]+?)(?:\s+(?:on|via|saying)\s+|$)', text, re.I)
    if match:
        return match.group(1).strip()
    return None


def extract_whatsapp_message(command: str, raw_text: str = "") -> str:
	"""Extract message from WhatsApp command"""
	
	# 1. Try quoted text first
	quoted = extract_quoted_text(command)
	if quoted:
		return quoted
	
	# 2. Try pattern: "saying [message]" or "message [text]"
	saying_match = re.search(r'(?:saying|message|text)\s+["\']?(.+?)(?:\s+(?:to|on)\s+|$)', command, re.I)
	if saying_match:
		msg = saying_match.group(1).strip()
		if msg:
			return msg
	
	# 3. Try pattern: "to [contact] [message]"
	to_match = re.search(r'\bto\s+[\w\s\-\+\.@]+?\s+(.+?)(?:\s+(?:on|via)\s+|$)', command, re.I)
	if to_match:
		msg = to_match.group(1).strip()
		if msg and not any(kw in msg.lower() for kw in ["whatsapp", "wa", "whatsap"]):
			return msg
	
	# 4. Default fallback
	return raw_text or "Hello"


def extract_search_query(text: str) -> str:
    """Extract search query from text"""
    # Remove command words
    query = text.lower()
    for keyword in COMMAND_KEYWORDS["search"] + COMMAND_KEYWORDS["open"] + COMMAND_KEYWORDS["youtube"] + COMMAND_KEYWORDS["play"]:
        query = query.replace(keyword, "").strip()
    return query.strip()


# ============ MAIN ACTION FUNCTIONS ============

def open_youtube(search_query: str = "") -> str:
	"""Open YouTube - optionally search for something"""
	if search_query:
		url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
		print(f"  ▶️ Playing on YouTube: {search_query}")
	else:
		url = "https://www.youtube.com"
		print(f"  ▶️ Opening YouTube")
	
	webbrowser.open(url)
	return f"✅ Opened YouTube" + (f": {search_query}" if search_query else "")


def open_spotify(search_query: str = "") -> str:
	"""Open Spotify - optionally search for something"""
	if search_query:
		url = f"https://open.spotify.com/search/{urllib.parse.quote(search_query)}"
		print(f"  🎵 Searching Spotify: {search_query}")
	else:
		url = "https://open.spotify.com"
		print(f"  🎵 Opening Spotify")
	
	webbrowser.open(url)
	return f"✅ Opened Spotify" + (f": {search_query}" if search_query else "")


def open_url(url: str) -> str:
	"""Open a specific URL"""
	if not url.startswith("http"):
		url = "https://" + url
	webbrowser.open(url)
	return f"✅ Opened: {url}"


def google_search(query: str) -> str:
	"""Search on Google"""
	url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
	webbrowser.open(url)
	return f"✅ Searching Google for: {query}"


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


def send_whatsapp(message: str, phone: Optional[str] = None, contact_name: Optional[str] = None) -> str:
	"""Send WhatsApp message - with better automation"""
	target = contact_name or phone or "contact"
	print(f"  💬 Sending WhatsApp to {target}...")
	
	# Helper function to automate WhatsApp
	def automate_whatsapp_send(msg: str, contact: Optional[str]) -> bool:
		"""Use pyautogui to automate WhatsApp sending"""
		try:
			import time
			import pyautogui
			import pyperclip
			
			print(f"  🤖 Automating WhatsApp...")
			time.sleep(2)  # Wait for dialog to load
			
			if contact:
				print(f"  🔍 Searching for: {contact}")
				
				# The search box should already be focused in the send dialog
				# Clear it first
				pyautogui.hotkey('ctrl', 'a')
				time.sleep(0.2)
				
				# Type contact name using clipboard (more reliable)
				pyperclip.copy(contact)
				pyautogui.hotkey('ctrl', 'v')
				time.sleep(1.5)
				
				# Wait for results to appear
				# Press down arrow to select first contact
				pyautogui.press('down')
				time.sleep(0.5)
				
				# Press enter to select the contact
				pyautogui.press('enter')
				time.sleep(2)  # Wait for chat to open
			
			# Now we should be in the message input field
			print(f"  ✏️ Typing message: {msg}")
			time.sleep(0.5)
			
			# Type message using clipboard
			pyperclip.copy(msg)
			pyautogui.hotkey('ctrl', 'v')
			time.sleep(0.5)
			
			# Send message
			print(f"  📤 Sending...")
			pyautogui.press('enter')
			time.sleep(1)
			
			print(f"  ✅ Message sent!")
			return True
		except Exception as e:
			print(f"  ⚠️ Automation error: {e}")
			import traceback
			traceback.print_exc()
			return False
	
	# FIRST: Try WhatsApp Protocol + Automation
	try:
		quoted = urllib.parse.quote(message or "")
		if phone:
			prot = f"whatsapp://send?phone={phone}&text={quoted}"
		else:
			prot = f"whatsapp://send?text={quoted}"
		
		print(f"  🚀 Opening via protocol...")
		os.startfile(prot)
		
		# Try automation if contact name provided (and not phone)
		if contact_name and not phone:
			time.sleep(2)
			if automate_whatsapp_send(message, contact_name):
				return f"✅ Message sent to {target}"
		
		return f"✅ WhatsApp opened for {target}"
	except Exception as e:
		print(f"  ℹ️ Protocol method failed: {e}")
	
	# SECOND: Try direct app launch + Automation
	whatsapp_paths = [
		os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\WhatsApp.exe"),
		os.path.expandvars(r"%APPDATA%\WhatsApp\WhatsApp.exe"),
		os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
		r"C:\Program Files\WhatsApp\WhatsApp.exe",
		r"C:\Program Files (x86)\WhatsApp\WhatsApp.exe",
	]
	
	# Try wildcard path for Microsoft Store
	store_pattern = os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\app-*\WhatsApp.exe")
	matching = glob.glob(store_pattern)
	whatsapp_paths.extend(matching)
	
	for app_path in whatsapp_paths:
		if os.path.exists(app_path):
			try:
				print(f"  🚀 Launching: {app_path}")
				subprocess.Popen([app_path])
				
				# Try automation
				time.sleep(2)
				if automate_whatsapp_send(message, contact_name):
					return f"✅ Message sent to {target}"
				
				return f"✅ WhatsApp opened for {target}"
			except Exception as e:
				print(f"  ⚠️ Launch failed: {e}")
				continue
	
	# THIRD: Fallback to WhatsApp Web
	print(f"  ℹ️ Opening WhatsApp Web (no desktop app found)...")
	quoted = urllib.parse.quote(message or "")
	
	try:
		if phone:
			url = f"https://wa.me/{phone}?text={quoted}"
		else:
			url = "https://web.whatsapp.com"

		webbrowser.open(url)
		return f"✅ WhatsApp Web opened for {target}"
	except Exception as e:
		return f"❌ WhatsApp error: {e}"


def make_call(number: str) -> str:
	"""Initiate phone call"""
	try:
		url = f"tel:{number}"
		webbrowser.open(url)
		print(f"  📞 Calling: {number}")
		return f"✅ Calling {number}"
	except Exception as e:
		return f"❌ Failed to call: {e}"


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
	print(f"  📧 Email to {to or 'default'}: {subject}")
	return f"✅ Email composer opened"


# ============ MAIN COMMAND ROUTER ============

def perform_action(command: str, raw_text: str = "", model_output: str = "") -> str:
	"""Main command router - understands user intent clearly"""
	lc = command.lower()
	
	print(f"\n🔍 Analyzing: '{command[:60]}...'")

	# ========== OPEN YOUTUBE + PLAY ==========
	if match_keyword(lc, COMMAND_KEYWORDS["youtube"]) or "youtube" in lc:
		# Extract what to play (everything after "youtube" or "play")
		search_query = ""
		
		# Remove "open youtube" or similar
		for keyword in COMMAND_KEYWORDS["open"] + COMMAND_KEYWORDS["youtube"]:
			lc_temp = lc.replace(keyword, "", 1).strip()
			if len(lc_temp) < len(lc):
				lc = lc_temp
				break
		
		# Get remaining text as search query
		search_query = lc.strip()
		
		return open_youtube(search_query)

	# ========== PLAY MUSIC (YouTube/Spotify) ==========
	if match_keyword(lc, COMMAND_KEYWORDS["play"]):
		# Extract what to play
		search_query = lc.replace("play", "", 1).strip()
		
		# If it mentions spotify, use spotify
		if "spotify" in search_query:
			search_query = search_query.replace("spotify", "").strip()
			return open_spotify(search_query)
		
		# Default to YouTube
		return open_youtube(search_query)

	# ========== OPEN SPOTIFY ==========
	if match_keyword(lc, COMMAND_KEYWORDS["spotify"]):
		search_query = lc.replace("spotify", "").replace("open", "").strip()
		return open_spotify(search_query)

	# ========== OPEN APPLICATIONS ==========
	if match_keyword(lc, COMMAND_KEYWORDS["open"]):
		if match_keyword(lc, COMMAND_KEYWORDS["chrome"]):
			return open_application("chrome")
		elif match_keyword(lc, COMMAND_KEYWORDS["calculator"]):
			return open_application("calculator")
		elif match_keyword(lc, COMMAND_KEYWORDS["notepad"]):
			return open_application("notepad")

	# ========== WHATSAPP ==========
	if match_keyword(lc, COMMAND_KEYWORDS["whatsapp"]):
		# Extract message correctly
		msg = extract_whatsapp_message(command, raw_text)
		recipient = extract_recipient(command)
		
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
		digits = re.findall(r'\d+', lc)
		if digits:
			number = "".join(digits)
			return make_call(number)
		return "❌ No phone number found"

	# ========== GOOGLE SEARCH ==========
	if match_keyword(lc, COMMAND_KEYWORDS["search"]):
		query = extract_search_query(command) or raw_text
		return google_search(query)

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
			return open_url(url_match.group(0))

	# ========== NO MATCH ==========
	print(f"  ❓ Command not recognized")
	return "❌ Command not understood. Try: 'open youtube and play karan aujla', 'send whatsapp to john', 'search python', 'call 123456'"
