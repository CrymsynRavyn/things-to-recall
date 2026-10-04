# Quick Start (5 Minutes)

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Ollama installed** → Get it at https://ollama.ai/
- [ ] **Python 3.9+** → Check with `python --version` in terminal
- [ ] **This folder** → Downloaded and unzipped

---

## Start Here

### Terminal Window #1: Ollama

```bash
ollama run gemma3:4b
```

**Wait for it to say "listening on 127.0.0.1:11434"**

*Leave this running. Do NOT close this window.*

---

### Terminal Window #2: Backend

Navigate to this folder:

```bash
cd path/to/things-to-recall
```

Install once:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python app.py
```

*You should see green startup text. Leave this running. Do NOT close this window.*

---

### Browser: Open the App

Go to:

```
http://localhost:5000
```

(Or just open `index.html` in your browser — but the backend server won't connect without the Python app running)

---

## You're Done!

Press the 🎤 button. Talk. Reminders appear. ✨

---

## If Something Doesn't Work

| Problem | Solution |
|---------|----------|
| "Ollama not running" | Run `ollama run gemma3:4b` in Terminal #1 |
| "Backend not running" | Run `python app.py` in Terminal #2 |
| Microphone won't work | Browser permission denied. Allow localhost:5000 to use mic |
| App is slow | First run downloads Whisper model (~30 sec). After that, it's fast. |

---

See **README.md** for full troubleshooting and customization.
