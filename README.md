# Things to Recall 🎤

A voice-first, distraction-free reminder app for ADHD-friendly workflows.

**One button. Talk. Reminders appear. Done.**

---

## What It Does

1. **Press the big button** → speak what you need to remember
2. **AI listens** → Whisper transcribes it → Gemma extracts the core reminder
3. **Reminders appear** on a simple list
4. **Check them off** → they fade away
5. **Undo within 10 seconds** if you checked by mistake

No settings, no menus, no friction.

---

## Tech Stack

- **Frontend**: HTML/CSS/JS with MediaRecorder
- **Backend**: Python Flask
- **Speech-to-Text**: faster-whisper (int8 CPU, 1-2 sec)
- **Reminder Extraction**: Ollama + Gemma3:4b (local LLM, open-weight)
- **Storage**: Local JSON file (no cloud, no databases)

**All inference is local. No API keys. No closed services.**

---

## How It Works

1. **Press and hold the button** → Browser records audio via MediaRecorder
2. **Release** → Audio blob uploads to Flask backend
3. **faster-whisper transcribes** → Speech converted to text on the server
4. **Ollama extracts** → Gemma3:4b refines transcription into clean reminder
5. **Reminder appears** → In your list, ready to check off
6. **Undo window** → 10 seconds to change your mind before deletion

---

## Setup (15 minutes)

### Prerequisites

- **macOS / Linux / Windows (WSL2)**
- **Python 3.9+** → [Install here](https://www.python.org/)
- **Ollama** → [Install here](https://ollama.ai/)

### Step 1: Install Ollama

Download and install Ollama from https://ollama.ai/

This runs the Gemma language model locally on your machine.

### Step 2: Start Ollama

Open a terminal and run:

```bash
ollama run gemma3:4b
```

This downloads Gemma (first time is ~2GB, takes a few minutes) and starts the Ollama server.

**Leave this terminal open** — it needs to run in the background.

### Step 3: Set Up Python Backend

In a **new terminal**, navigate to this project folder:

```bash
cd path/to/things-to-recall
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python app.py
```

You should see:

```
Things to Recall - Backend Starting
============================================================

Required before starting:
  1. Ollama running: ollama run gemma3:4b
  2. Check health at: http://localhost:5000/health

============================================================
```

**Leave this terminal running.**

### Step 4: Open the Web App

1. Open your browser
2. Go to: `http://localhost:5000` 
3. Or open `index.html` directly (but the backend won't connect)

That's it! 🎉

---

## How to Use

### Recording a Reminder

1. **Press and hold the big blue circle** (🎤)
2. **Speak clearly** — say what you need to remember
3. **Release the button** — the app thinks
4. **Reminder appears** in the list below

### Completing a Reminder

1. **Tap the checkbox** next to the reminder
2. Item fades away
3. **Within 10 seconds**, if you tap "↶ Undo", it comes back
4. **After 10 seconds**, it's gone forever (intentional — less clutter)

---

## Troubleshooting

### "Ollama not running"

**Error**: You see ⚠️ Ollama not running in the status bar

**Fix**: Open a terminal and run `ollama run gemma3:4b`, then refresh the browser

### "Backend not running"

**Error**: Status shows ⚠️ Backend not running

**Fix**: Open a terminal in this folder and run `python app.py`, then refresh

### "Microphone access denied"

**Error**: App asks for mic permission and you denied it

**Fix**: 
- **Chrome**: Settings → Privacy → Site Settings → Microphone → Allow localhost:5000
- **Safari**: Settings → Websites → Microphone → Allow
- Then refresh the page

### Audio doesn't transcribe

**Why**: Whisper can fail on very quiet or poor audio

**Fix**: 
- Speak a bit louder
- Get closer to the mic
- Check system mic volume (not muted)

### Reminders appear but are gibberish

**Why**: Gemma sometimes extracts poorly (rare)

**Fix**: Try speaking more clearly, shorter sentences

### It's slow on first run

**Why**: Whisper downloads the model on first use (~75MB, one-time)

**Fix**: Wait ~30 seconds the first time, subsequent runs are fast

---

## Files

- **app.py** — Python backend (Flask, Whisper, Ollama calls, storage)
- **index.html** — Frontend (HTML/CSS/JS, all in one file)
- **reminders.json** — Your reminders (created automatically)

---

## For the Hacktoberfest Write-Up

### Open-Source Components Used

- **Whisper** (OpenAI): Speech-to-text
- **Ollama**: Local LLM inference
- **Gemma** (Google): Open-weight language model
- **Flask**: Python web framework
- **All code**: Built from scratch, no copileft concerns

### Why This Matters

This demo shows:
1. **Local AI inference** — no cloud dependency, privacy-first
2. **Open-weight models** — Gemma instead of GPT
3. **Accessible design** — ADHD-friendly UX (one button, clear feedback)
4. **Minimal code** — ~400 lines frontend, ~200 lines backend

### Demo Points

- Start Ollama
- Start Flask backend
- Open browser
- Record 3–4 reminders (different topics)
- Show undo feature (complete + undo before 10s)
- Show that reminders persist in JSON
- Show health check: `curl http://localhost:5000/health`

---

## Customization (Optional)

### Change the Model

In **app.py**, line 60, change:

```python
"model": "gemma",  # Try: ollama run mistral, ollama run orca, etc.
```

Run `ollama run <model>` first to download it.

### Change Colors

In **index.html**, lines 16-24, edit the CSS variables:

```css
--blue-dark: #2c5aa0;
--blue-mid: #4a7ba7;
/* etc */
```

### Change Undo Timeout

In **app.py**, line 12:

```python
UNDO_TIMEOUT = 10  # seconds
```

---

## Limitations (Intentional)

- **No history** → Done means gone (user request: less anxiety about "what was I supposed to do")
- **One user** → No login, no sync (scope: ADHD adult at home)
- **No mobile app** → Web is faster to build and deploy
- **Simple extraction** → Gemma is fast but not perfect (trades speed for accuracy)

---

## License

MIT. Build on it, fork it, make it yours.

---

**Built for Hacktoberfest 2026** 🎃

One big button. That's the whole app.
