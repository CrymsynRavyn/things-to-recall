#!/usr/bin/env python3
"""
Things to Recall - Voice-first reminder app
Backend: Flask + Whisper + Ollama (Gemma)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

app = Flask(__name__)
CORS(app)

# Simple JSON storage
STORAGE_FILE = "reminders.json"
UNDO_TIMEOUT = 10  # seconds before item permanently deleted

def load_reminders():
    """Load reminders from disk"""
    if Path(STORAGE_FILE).exists():
        with open(STORAGE_FILE) as f:
            return json.load(f)
    return {"active": [], "undo_queue": []}

def save_reminders(data):
    """Save reminders to disk"""
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def call_ollama(prompt):
    """
    Call Ollama with Gemma to extract reminder.
    Ollama should be running: ollama run gemma
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma",
                "prompt": prompt,
                "stream": False,
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama error: {e}")
    return None

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """
    1. Receive audio blob
    2. Transcribe with Whisper
    3. Extract reminder with Ollama
    4. Store and return
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]
    
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        audio_file.save(tmp.name)
        temp_path = tmp.name
    
    try:
        # Transcribe with Whisper
        print("Transcribing with Whisper...")
        model = whisper.load_model("base")
        result = model.transcribe(temp_path)
        transcription = result["text"].strip()
        
        if not transcription:
            return jsonify({"error": "Could not transcribe audio"}), 400
        
        print(f"Transcription: {transcription}")
        
        # Extract reminder with Ollama
        print("Extracting reminder with Ollama...")
        extraction_prompt = f"""Extract the core reminder from this transcription. Return ONLY a short, actionable reminder (under 100 chars). Do not add explanations.

Transcription: "{transcription}"

Reminder:"""
        
        reminder_text = call_ollama(extraction_prompt)
        
        if not reminder_text:
            # Fallback: use transcription directly
            reminder_text = transcription[:100]
        
        print(f"Extracted reminder: {reminder_text}")
        
        # Store reminder
        data = load_reminders()
        new_reminder = {
            "id": int(datetime.now().timestamp() * 1000),
            "text": reminder_text,
            "created": datetime.now().isoformat(),
            "completed_at": None
        }
        data["active"].append(new_reminder)
        save_reminders(data)
        
        return jsonify({
            "success": True,
            "transcription": transcription,
            "reminder": reminder_text,
            "id": new_reminder["id"]
        })
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass

@app.route("/api/reminders", methods=["GET"])
def get_reminders():
    """Get all active reminders"""
    data = load_reminders()
    
    # Clean up expired undo items
    now = datetime.now()
    data["undo_queue"] = [
        item for item in data["undo_queue"]
        if datetime.fromisoformat(item["expires_at"]) > now
    ]
    
    save_reminders(data)
    return jsonify(data)

@app.route("/api/complete/<int:reminder_id>", methods=["POST"])
def complete_reminder(reminder_id):
    """Mark reminder as complete (moves to undo queue)"""
    data = load_reminders()
    
    # Find and remove from active
    reminder = None
    for i, r in enumerate(data["active"]):
        if r["id"] == reminder_id:
            reminder = data["active"].pop(i)
            break
    
    if not reminder:
        return jsonify({"error": "Reminder not found"}), 404
    
    # Add to undo queue with expiration
    reminder["completed_at"] = datetime.now().isoformat()
    reminder["expires_at"] = (datetime.now() + timedelta(seconds=UNDO_TIMEOUT)).isoformat()
    data["undo_queue"].append(reminder)
    
    save_reminders(data)
    return jsonify({"success": True, "undo_timeout": UNDO_TIMEOUT})

@app.route("/api/undo/<int:reminder_id>", methods=["POST"])
def undo_complete(reminder_id):
    """Restore a completed reminder"""
    data = load_reminders()
    
    # Find and remove from undo queue
    reminder = None
    for i, r in enumerate(data["undo_queue"]):
        if r["id"] == reminder_id:
            reminder = data["undo_queue"].pop(i)
            break
    
    if not reminder:
        return jsonify({"error": "Reminder not found in undo queue"}), 404
    
    # Remove undo metadata and restore to active
    reminder.pop("completed_at", None)
    reminder.pop("expires_at", None)
    data["active"].append(reminder)
    
    save_reminders(data)
    return jsonify({"success": True})

@app.route("/api/delete/<int:reminder_id>", methods=["POST"])
def delete_reminder(reminder_id):
    """Permanently delete a reminder"""
    data = load_reminders()
    
    # Remove from active
    data["active"] = [r for r in data["active"] if r["id"] != reminder_id]
    
    # Remove from undo queue
    data["undo_queue"] = [r for r in data["undo_queue"] if r["id"] != reminder_id]
    
    save_reminders(data)
    return jsonify({"success": True})

@app.route("/health", methods=["GET"])
def health():
    """Health check + dependency status"""
    status = {"app": "ok"}
    
    # Check Whisper
    try:
        whisper.load_model("base", in_memory=False)
        status["whisper"] = "ok"
    except:
        status["whisper"] = "not available"
    
    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        status["ollama"] = "ok"
    except:
        status["ollama"] = "not running (required)"
    
    return jsonify(status)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Things to Recall - Backend Starting")
    print("="*60)
    print("\nRequired before starting:")
    print("  1. Ollama running: ollama run gemma")
    print("  2. Check health at: http://localhost:5000/health")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
