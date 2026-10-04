#!/usr/bin/env python3
"""
Things to Recall - Voice-first reminder app
Backend: Flask + Web Speech API + Ollama (Gemma)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

# Web Speech API transcription is handled by the browser
# No Whisper needed!

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

@app.route("/", methods=["GET"])
def index():
    """Serve the main HTML page"""
    try:
        return send_file("index.html", mimetype="text/html")
    except FileNotFoundError:
        return jsonify({"error": "index.html not found"}), 404

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
    1. Receive transcription from browser Web Speech API
    2. Extract reminder with Ollama
    3. Store and return
    """
    data = request.get_json()
    
    if not data or "transcription" not in data:
        return jsonify({"error": "No transcription provided"}), 400

    transcription = data.get("transcription", "").strip()
    
    if not transcription:
        return jsonify({"error": "Empty transcription"}), 400
    
    print(f"Transcription: {transcription}")
    
    try:
        # Extract reminder with Ollama (optional - use transcription as fallback)
        print("Extracting reminder with Ollama...")
        extraction_prompt = f"""Extract the core reminder from this transcription. Return ONLY a short, actionable reminder (under 100 chars). Do not add explanations.

Transcription: "{transcription}"

Reminder:"""
        
        reminder_text = call_ollama(extraction_prompt)
        
        # If Ollama fails or returns nothing, use transcription directly
        if not reminder_text or reminder_text.isspace():
            print("Ollama unavailable, using transcription as reminder")
            reminder_text = transcription[:100] if transcription else "Reminder"
        
        print(f"Extracted reminder: {reminder_text}")
        
    except Exception as e:
        print(f"Error extracting reminder: {str(e)}")
        reminder_text = transcription[:100]
    
    # Store reminder
    try:
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
    
    except Exception as e:
        print(f"Error storing reminder: {str(e)}")
        return jsonify({"error": "Could not save reminder"}), 500

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
    
    # Check Ollama (Web Speech API is handled by browser)
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
