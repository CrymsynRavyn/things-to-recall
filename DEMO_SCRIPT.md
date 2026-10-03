# Demo Script for Hacktoberfest 🎃

Use this to film your demo video. Keep it under 2 minutes.

---

## Setup (shown in video)

1. **Terminal 1 - Start Ollama**
   ```
   $ ollama run gemma
   ```
   (Show: "serving on 127.0.0.1:11434")

2. **Terminal 2 - Start Backend**
   ```
   $ python app.py
   ```
   (Show: startup banner with health check reminder)

3. **Browser - Open App**
   ```
   localhost:5000
   ```
   (Show: empty notepad UI with big blue button)

---

## Demo Flow (Record This)

### Scene 1: Voice Recording (15 seconds)

**Narration**: "Press and hold the big button. Speak what you need to remember."

**Action**:
1. Press and hold the 🎤 button
2. Say: "Remember to call mom on Sunday"
3. Release button
4. Show status changing: "Listening" → "Thinking" → "✓ Saved!"
5. Show reminder appear in the list

**Why this matters**: Shows end-to-end: speech → transcription → extraction

---

### Scene 2: Multiple Reminders (20 seconds)

**Narration**: "Add a few more reminders."

**Action**:
1. Press and hold button
2. Say: "Pick up milk at the store"
3. Release, watch it appear
4. Repeat twice more with different reminders:
   - "Fix the bathroom light"
   - "Email the team about the report"

**Why this matters**: Shows it handles multiple items, persists, feels natural

---

### Scene 3: Completing a Reminder (10 seconds)

**Narration**: "When you're done, tap the checkbox. It fades away."

**Action**:
1. Tap the checkbox next to "Pick up milk at the store"
2. Show item fade out
3. Show it appears in yellow "undo" state below
4. Show countdown: "Deletes in 9s... 8s..."

**Why this matters**: Shows undo feature, low-stakes design

---

### Scene 4: Undo (10 seconds)

**Narration**: "If you tap something by mistake, just undo. You have 10 seconds."

**Action**:
1. Show an item in undo state
2. Click the "↶ Undo" button
3. Show it restore to the main list
4. Now complete it again to show deletion

**Why this matters**: Shows forgiveness, ADHD-friendly design (no anger about mistakes)

---

### Scene 5: Technical Detail (Optional, 15 seconds)

**Narration**: "This all runs locally. No cloud services, no API keys. Just Whisper for speech, Gemma for extraction."

**Action**:
1. Open browser dev tools (F12)
2. Go to Network tab
3. Record a reminder
4. Show: all requests go to `localhost:5000`, nothing external
5. Optional: show `reminders.json` file in editor (plain text, human-readable)

**Why this matters**: Proves "open-source at core" for Hacktoberfest judges

---

## Total Runtime: ~90 seconds

---

## What to Say in Your Write-Up

### Problem Solved
"ADHD brains think in fragments. Existing note apps require navigation, menus, decisions. This removes every friction point: one button, speak, done."

### Open-Source Advantage
"Built with Whisper (OpenAI) + Gemma (Google) running locally via Ollama. Zero dependency on proprietary APIs. User data never leaves their machine."

### Code Quality
- Backend: ~200 lines (readable, well-commented)
- Frontend: ~400 lines (one HTML file, no build step)
- No external dependencies beyond Flask, Whisper, requests
- All AI inference is local; no network calls during runtime (after model load)

### Design Philosophy
"If it needs an explanation, it's too complicated. This app has one button and checkboxes. Done."

---

## Key Stats for Your Pitch

| Metric | Value |
|--------|-------|
| Setup Time | 15 minutes (first time) |
| Code Lines | ~600 total |
| Models Used | 2 (Whisper: 75MB, Gemma: 2GB) |
| API Calls | 0 (all local) |
| Files | 4 (app.py, index.html, requirements.txt, reminders.json) |
| Time to First Reminder | 3 seconds (after speak) |

---

## Talking Points

1. **"This is for someone who can't use a to-do app"** → Relatable pain point
2. **"One button is the whole UX"** → Shows design thinking
3. **"All inference is local"** → Impresses open-source judges
4. **"Built this weekend"** → Velocity matters
5. **"Runs on any computer"** → No cloud lock-in

---

## If Something Breaks During Demo

**Contingency Plan A**: Pre-record it. Much easier.

**Contingency Plan B**: If live demo, script it:
- Have reminders.json pre-populated
- Just show the UI and undo feature
- Talk through the architecture

**Contingency Plan C**: Show screenshots + architecture diagram

---

## Success Criteria (What Judges Look For)

✅ **Open-source stack** → Whisper + Ollama + Gemma (all OSS) ✓
✅ **Working demo** → Records audio, shows reminders, undo works ✓
✅ **ADHD-friendly design** → Single button, no friction ✓
✅ **Local inference** → No API keys or cloud ✓
✅ **Clean code** → Well-commented, readable ✓
✅ **Solves a real problem** → Accessibility for neurodivergent users ✓

---

## Last Minute Tips

- **Test mic permissions** before filming
- **Film in quiet room** (clean audio = better transcriptions)
- **Pre-load Whisper model** before demo (first run is slow)
- **Show the reminders.json** to prove persistence
- **Talk slower than you think** (background music helps engagement)

---

Good luck! 🚀
