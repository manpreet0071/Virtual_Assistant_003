# J4E Assistant — native Python UI

This replaces the Eel/HTML frontend (`spider.html`, `home.html`,
`settings.html`, `eel.js`) with a self-contained PyQt5 desktop app.
No browser, no websocket bridge, no `eel.expose(...)` — everything
runs as plain Python signals/slots.

## Install

```bash
pip install -r requirements.txt
```

`PyAudio` (needed for microphone input) sometimes needs a system
package first:

- **Windows:** `pip install pyaudio` usually just works.
- **macOS:** `brew install portaudio && pip install pyaudio`
- **Linux:** `sudo apt install portaudio19-dev python3-pyaudio`

## Add your avatar video

Put the video you were serving as `avtar/emily_4.mp4` into `assets/`.
Any `.mp4` / `.mov` / `.avi` file dropped in there is auto-detected
and looped — no filename changes needed in code.

## Run

```bash
python main.py
```

## What changed vs. the original

- **Docking / sizing:** the window docks to the bottom-right corner
  of the primary screen and sizes itself to `20%` of the screen's
  available width (clamped between 280–520px), so it scales
  automatically across resolutions and re-docks itself if you switch
  monitors. Tune `WIDTH_FRACTION`, `ASPECT_RATIO`, `EDGE_MARGIN`,
  `MIN_WIDTH`, `MAX_WIDTH` at the top of `ui/main_window.py`.
- **Mic:** `webkitSpeechRecognition` → `SpeechRecognition` running on
  a background `QThread` (`core/speech.py`), so it never freezes the
  UI. Recognized text is routed through `MainWindow.process_command`
  — that's the one method to fill in with your existing
  intent/command logic.
- **TTS:** added via `pyttsx3` since there's no browser `speechSynthesis`
  API to lean on anymore.
- **Camera capture:** `getUserMedia`/`capture()` → `core/camera.py`
  using OpenCV, if you want to wire the capture button back in.
- **Settings:** `settings.html` → `ui/settings_window.py`, a plain
  Qt form for assistant name + recognition language.
- **Dropped:** the `_position_window` behavior in the original
  `eel.js` that force-shrinks the window to 300×100 and blurs it on
  every load. That silently hid an app that's listening to the mic
  and can access the camera, so it isn't reproduced here — this
  version is a normal, visible, draggable window instead.

## Files

```
main.py                 entry point
ui/main_window.py        corner-docked window, video, mic, chat log
ui/settings_window.py    settings dialog
core/speech.py           background STT/TTS threads
core/camera.py           optional webcam feed thread
requirements.txt
assets/                  put your avatar video here
```
