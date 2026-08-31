def prepare_speech(data: dict, user_text: str) -> str:
    """Prepare spoken text. Only prepend honorifics when appropriate.

    Heuristics: prepend 'Sir'/'Master' only if the model set the address to that
    AND the user's input appears commanding/formal or explicitly contains the
    honorifics.
    """
    address = data.get("address", "none")
    speak = data.get("speak", "").strip()

    user_l = (user_text or "").lower()

    commanding_keywords = ["open", "send", "message", "call", "search", "execute", "run", "please", "kindly"]
    is_commanding = any(k in user_l for k in commanding_keywords)
    user_used_honorific = user_l.strip().startswith(("sir", "master")) or " sir" in user_l or " master" in user_l

    if address == "sir" and (is_commanding or user_used_honorific):
        speak = f"Sir, {speak}"
    elif address == "master" and (is_commanding or user_used_honorific):
        speak = f"Master, {speak}"

    return speak.strip()