# Architecture & Technical Design

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Frontend (index.html)                     │  │
│  │  • MediaRecorder (press-hold to record)              │  │
│  │  • Fetch API (send audio blob)                       │  │
│  │  • DOM rendering (reminder list)                     │  │
│  │  • Undo timer logic                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP / FormData (audio/webm)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (app.py - Flask)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              POST /api/transcribe                    │  │
│  │  1. Receive audio blob                              │  │
│  │  2. Call faster-whisper (speech-to-text)            │  │
│  │  3. Call Ollama + Gemma3:4b (reminder extraction)   │  │
│  │  4. Store in reminders.json                         │  │
│  │  5. Return reminder + ID                            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         GET /api/reminders                          │  │
│  │  • Return active + undo_queue                       │  │
│  │  • Clean expired items                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    POST /api/complete/<id>                          │  │
│  │    POST /api/undo/<id>                              │  │
│  │    POST /api/delete/<id>                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────┬─────────────────┬────────────────────────────────┬─┘
         │                 │                                │
         ▼                 ▼                                ▼
    ┌────────────────┐   ┌──────────────────┐     ┌─────────────────┐
    │faster-whisper  │   │  Ollama +        │     │ reminders.json  │
    │  (int8 CPU)    │   │  Gemma3:4b       │     │  (Local File)   │
    │ Speech-to-Text │   │  Extract         │     │                 │
    │    ~1-2s       │   │  Reminder        │     │ {                │
    │                │   │  ~2-3s           │     │   "active": [.], │
    │ (Local)        │   │  (Local)         │     │   "undo_q": []  │
    │ 75MB model     │   │  4GB model       │     │ }               │
    └────────────────┘   └──────────────────┘     └─────────────────┘
```

---

## Data Flow

### Step 1: Record & Send Audio

```javascript
// Frontend: Web Audio API
1. User holds button
2. navigator.mediaDevices.getUserMedia() → stream
3. MediaRecorder captures audio/webm blob
4. FormData + fetch POST to /api/transcribe
```

**Why webm?** 
- Modern browser standard
- Smaller than WAV
- Whisper handles it natively

---

### Step 2: Transcribe (Backend)

```python
# Backend: app.py
1. Receive audio blob (temp file)
2. model = WhisperModel("base", device="cpu", compute_type="int8")
3. segments, info = model.transcribe(audio_path)
4. transcription = " ".join([segment.text for segment in segments]).strip()

# Example:
# Input: [audio of "remember to call mom"]
# Output: "Remember to call mom on Sunday afternoon"
```

**Model**: `base` (faster-whisper int8 quantized, ~1-2 sec per audio)
**Why int8?**: 4x smaller, 2x faster, no accuracy loss for casual voice input

---

### Step 3: Extract Reminder (AI)

```python
# Backend: app.py line 80
prompt = f"""Extract the core reminder from this transcription. 
Return ONLY a short, actionable reminder (under 100 chars). 
Do not add explanations.

Transcription: "{transcription}"

Reminder:"""

response = requests.post("http://localhost:11434/api/generate", {
    "model": "gemma3:4b",
    "prompt": prompt,
    "stream": False
})
```

**Example:**
- Input: "Remember to call mom on Sunday afternoon if I'm free"
- Output: "Call mom on Sunday"

**Why Gemma3:4b?**
- Very fast (1-2 sec on modern CPU)
- Open-weight (no API key)
- Smaller (4GB download vs 5GB for full Gemma)
- Better instruction-following
- Lower latency than full Gemma

**Why Ollama?**
- Local inference (privacy)
- No cloud calls
- Works offline after first download

---

### Step 4: Store

```json
// reminders.json
{
  "active": [
    {
      "id": 1696353612000,
      "text": "Call mom on Sunday",
      "created": "2026-10-03T14:40:12.000000",
      "completed_at": null
    }
  ],
  "undo_queue": [
    {
      "id": 1696353600000,
      "text": "Pick up milk",
      "created": "2026-10-03T14:39:00.000000",
      "completed_at": "2026-10-03T14:40:12.000000",
      "expires_at": "2026-10-03T14:40:22.000000"
    }
  ]
}
```

**Why JSON?**
- Human-readable (debug easily)
- No database setup (zero dependencies)
- User can edit directly if needed
- Works offline

---

### Step 5: Display & Interact (Frontend)

```javascript
// GET /api/reminders every 5 seconds
// Render with:
// - Checkbox (marks complete)
// - Text
// - Delete timer (undo queue only)

// User checks checkbox
// → POST /api/complete/{id}
// → Item moves to undo_queue with 10-sec expiration
// → Frontend shows countdown
// → User can POST /api/undo/{id} within 10s
// → After 10s, POST /api/delete/{id} auto-runs
```

---

## Why This Architecture

| Choice | Rationale |
|--------|-----------|
| Flask | Minimal, no async needed, one file |
| Whisper | OpenAI-maintained, proven, local |
| Ollama | Standard for local LLM inference |
| Gemma | Fast, open, instruction-following |
| JSON | Simple, fast, debuggable |
| Web Audio API | No plugins, works in browser |
| CORS | Frontend on file, backend on 5000 |

---

## Performance

### Latency (Average)

| Step | Time |
|------|------|
| Record audio | User-dependent (1-5 sec) |
| Transcribe (Whisper) | 1-3 seconds |
| Extract (Ollama) | 2-4 seconds |
| Display | <100ms |
| **Total** | ~4-8 seconds |

**First run**: +30 sec (Whisper downloads ~75MB model)
**Subsequent runs**: Same as above

### Storage

- **Whisper model**: 75MB (cache, not in repo)
- **Gemma model**: 2GB (downloaded by Ollama separately)
- **App code**: ~60KB
- **Per reminder**: ~200 bytes (JSON)

---

## API Reference

### POST /api/transcribe

**Request**: FormData with audio blob

```javascript
const formData = new FormData();
formData.append("audio", audioBlob);
fetch("/api/transcribe", { method: "POST", body: formData });
```

**Response**:
```json
{
  "success": true,
  "transcription": "Remember to call mom on Sunday afternoon",
  "reminder": "Call mom on Sunday",
  "id": 1696353612000
}
```

---

### GET /api/reminders

**Response**:
```json
{
  "active": [{ "id": 123, "text": "...", "created": "..." }],
  "undo_queue": [{ "id": 456, "text": "...", "expires_at": "..." }]
}
```

---

### POST /api/complete/{id}

Moves reminder from `active` to `undo_queue` with 10-sec expiration.

**Response**:
```json
{ "success": true, "undo_timeout": 10 }
```

---

### POST /api/undo/{id}

Restores from `undo_queue` to `active`.

**Response**:
```json
{ "success": true }
```

---

### POST /api/delete/{id}

Permanently removes from anywhere.

**Response**:
```json
{ "success": true }
```

---

### GET /health

Checks system dependencies.

**Response**:
```json
{
  "app": "ok",
  "whisper": "ok",
  "ollama": "ok"
}
```

---

## Error Handling

| Error | Frontend Behavior |
|-------|-------------------|
| Ollama not running | Shows ⚠️ warning, uses raw transcription as fallback |
| Backend not running | Shows ⚠️ error, can't proceed |
| Mic permission denied | Browser native prompt (user controls) |
| Audio too quiet | Whisper may return empty, user retries |
| Network timeout | Shows error, can retry |

---

## Security & Privacy

**No external API calls** (after model download)
- Whisper runs locally
- Ollama runs locally
- All storage is local JSON file

**Audio handling:**
- Temp file deleted immediately after transcription
- Not logged or saved
- User's machine only

**Data ownership:**
- User owns `reminders.json` file
- Can delete/backup/share directly
- No cloud sync or backup

---

## Why Open Source Matters Here

1. **Whisper (MIT)** → Can audit, modify, run anywhere
2. **Ollama (MIT)** → Local control, no vendor lock-in
3. **Gemma (Apache 2.0)** → Free, open weights, commercial-friendly
4. **Flask (BSD)** → Simple, transparent
5. **Code (MIT)** → This project is open, remixable

This satisfies Hacktoberfest's "open-source" requirement at every layer.

---

## Possible Extensions (Not Implemented)

- Sync to cloud storage (Dropbox, Google Drive)
- Search/filter reminders
- Categories or tags
- Recurring reminders
- Integration with calendar
- Voice feedback (text-to-speech on reminder)
- Mobile app (React Native, Electron)
- Collaborative (share with caregiver)

**Out of scope for this demo**: MVP is one person, one button, no friction.

---

## Testing

### Manual Test Cases

1. **Record → Extract → Store**
   - Record "call mom"
   - Verify reminder appears in list
   - Check `reminders.json` has entry

2. **Complete → Undo**
   - Check a reminder
   - Verify fades + appears in undo state
   - Tap "Undo" within 5 sec
   - Verify it's back in active list

3. **Auto-delete after 10 sec**
   - Check a reminder
   - Wait 10 seconds
   - Verify it's gone
   - Refresh page, verify it doesn't come back

4. **Offline behavior**
   - Load page while online
   - Kill backend
   - Existing reminders still visible (stored in browser context)
   - Can't record (shows error)
   - Restart backend, can record again

---

## Deployment Notes

**This is a local app** — not designed for multi-user server hosting (yet).

**To demo:**
1. Run on single machine
2. Browser + backend on same machine
3. Ollama + Whisper need ~8GB RAM (can tune model size down)

**To extend for server:**
- Add authentication
- Database instead of JSON
- Per-user namespace
- Consider proprietary LLMs (cost/speed)

---

## Conclusion

This is **intentionally simple**: every feature serves a purpose (ADHD-friendly), every dependency is open-source, and the code is readable enough for someone to build on it in an afternoon.

The result: a working, usable app in ~600 lines that does one thing very well.
