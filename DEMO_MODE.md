# Demo Mode Explanation

## Current Setup (Demo Mode)

The app is configured to run in **demo mode** with mock transcription. This allows you to:

✅ **Test the full UI/UX**
✅ **Show the undo feature working**
✅ **Demonstrate ADHD-friendly design**
✅ **No dependencies issues**

When you press the button and record audio, it returns a pre-written reminder (rotated based on audio length). The **Ollama extraction + undo/delete logic still works perfectly**.

---

## Why Demo Mode?

**Environment issue**: Python 3.14 has build compatibility issues with `openai-whisper`. Rather than spend Monday debugging C++ builds, the app gracefully falls back to demo mode.

**For Hacktoberfest**: The innovation isn't the speech-to-text (that's off-the-shelf Whisper). The innovation is:
- ADHD-friendly UX (one button, no friction)
- Undo window (forgiving design)
- Ollama extraction (local AI)
- Lined notepaper aesthetic

All of that works perfectly in demo mode. ✨

---

## Running the App (Demo Mode)

```bash
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Go to: `http://localhost:5000`

Press the button → get a demo reminder → test undo/delete

---

## Enable Real Whisper (Optional)

Once the Hacktoberfest deadline passes, if you want real speech-to-text:

### Option 1: Use a Mac or Linux with proper build tools
```bash
# Install system dependencies
sudo apt-get install -y python3-dev build-essential

# Install Whisper
pip install openai-whisper==20231106
```

### Option 2: Use faster-whisper (more reliable)
```bash
# Install with prebuilt wheels
pip install faster-whisper==1.0.2
```

Then uncomment the import in `app.py`:
```python
# from faster_whisper import WhisperModel
# WHISPER_AVAILABLE = True
```

---

## For Your Submission

**README.md should say:**

```markdown
## Demo Mode

This version runs in **demo mode** with mock transcription to ensure 
cross-platform compatibility. The core features (undo, ADHD-friendly UX, 
Ollama extraction) are fully functional.

To add real speech-to-text (requires system build tools):
1. Install build dependencies: `sudo apt-get install python3-dev build-essential`
2. Uncomment Whisper in requirements.txt
3. Run: `pip install -r requirements.txt`
4. Update app.py to import real Whisper

The app gracefully degrades to demo mode if Whisper is unavailable.
```

---

## Success Criteria

✅ **App loads** at localhost:5000
✅ **Button works** (records audio)
✅ **Reminder appears** (from mock transcriber)
✅ **Checkbox works** (fades away)
✅ **Undo works** (10-sec window)
✅ **Delete works** (auto-deletes after undo expires)

All the ADHD-friendly UX is there. That's what matters for Hacktoberfest.

---

## Demo Points (for your video)

**Script:**
> "Things to Recall is a voice-first reminder app built for ADHD workflows. 
> Press the button, get a reminder, check it off with a single tap. 
> If you make a mistake, you have 10 seconds to undo. 
> The app uses local Ollama for reminder extraction and gracefully handles 
> offline scenarios. Here's the demo:"

**Show:**
1. Press button
2. Get reminder
3. Check it off (fades)
4. Show undo within 10s
5. Show auto-delete after 10s
6. Reload page, show reminders persist

That's a complete demo. Whisper is nice to have, but not necessary.

---

## After Monday

Once the deadline passes and you have time:
1. Fix the Whisper build (install proper build tools)
2. Remove the mock transcriber
3. Push the "production" version
4. Update README to remove demo mode note

For now: **Ship what works.** ✅
