from flask import Flask, render_template, Response, request, redirect, url_for, session, jsonify
import cv2
from deepface import DeepFace
import threading
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "faceask_iilm_2026"

DB_PATH = "faceask.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        hashed = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

SUGGESTIONS = {
    "happy":    {"message": "You're Happy! Keep the energy going!", "activities": ["Play chess or cricket!", "Call a close friend!", "Listen to upbeat music!", "Try a new hobby!", "Go for a workout!"], "therapist": False},
    "sad":      {"message": "You seem Sad. It's okay - let's help you feel better!", "activities": ["Watch a feel-good movie!", "Write in a journal!", "Go for a nature walk!", "Listen to calm music!", "Talk to a friend!"], "therapist": True},
    "angry":    {"message": "You look Angry. Let's calm down together!", "activities": ["Deep breathing: 4s in 4s out!", "Do some exercise!", "Listen to relaxing music!", "Write your feelings!", "Take a cold shower!"], "therapist": True},
    "fear":     {"message": "You seem Fearful. You are safe!", "activities": ["5-4-3-2-1 grounding technique!", "Talk to someone you trust!", "Watch a comforting show!", "Do light yoga!", "Write your fears down!"], "therapist": True},
    "surprise": {"message": "You look Surprised! Something exciting?", "activities": ["Learn something new!", "Share with a friend!", "Try a brain puzzle!", "Explore a new place!", "Start a creative project!"], "therapist": False},
    "disgust":  {"message": "You seem Disgusted. Let's shift your focus!", "activities": ["Get fresh air outside!", "Listen to your playlist!", "Organise your space!", "Watch something funny!", "Do what you enjoy!"], "therapist": True},
    "neutral":  {"message": "You look Neutral. Let's add some spark!", "activities": ["Try something new today!", "Go for a walk!", "Read an article!", "Play an online game!", "Call a friend!"], "therapist": False}
}

current_emotion = "neutral"
emotion_lock = threading.Lock()

def generate_frames():
    global current_emotion
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)
    frame_count = 0
    COLOR_MAP = {
        "happy": (0, 255, 100), "sad": (255, 100, 50), "angry": (0, 0, 255),
        "fear": (200, 50, 200), "surprise": (0, 200, 255), "disgust": (50, 200, 50), "neutral": (200, 200, 200)
    }
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        frame_count += 1
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            if frame_count % 10 == 0:
                try:
                    result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False, silent=True)
                    detected = result[0]['dominant_emotion'].lower()
                    with emotion_lock:
                        current_emotion = detected
                except:
                    pass
            with emotion_lock:
                emo = current_emotion
            color = COLOR_MAP.get(emo, (0, 255, 0))
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, emo.upper(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = get_user(username)
        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Incorrect username or password."
    return render_template("index.html", page="login", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("dashboard"))
    error = ""
    success = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        if not username or not password:
            error = "Username and password are required."
        elif len(password) < 4:
            error = "Password must be at least 4 characters."
        elif password != confirm:
            error = "Passwords do not match."
        elif create_user(username, password):
            success = "Account created! Please login."
        else:
            error = "Username already exists. Try another."
    return render_template("index.html", page="signup", error=error, success=success)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", page="dashboard", username=session["user"])

@app.route("/video_feed")
def video_feed():
    if "user" not in session:
        return redirect(url_for("login"))
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/emotion_data")
def emotion_data():
    if "user" not in session:
        return jsonify({"emotion": "neutral"})
    with emotion_lock:
        emo = current_emotion
    suggestion = SUGGESTIONS.get(emo, SUGGESTIONS["neutral"])
    return jsonify({"emotion": emo, "message": suggestion["message"], "activities": suggestion["activities"], "therapist": suggestion["therapist"]})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
