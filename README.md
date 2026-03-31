# emotion-recognition-using-facial-expressions
A real-time, web-based facial emotion recognition system. This project uses Deep Learning to analyze live camera feeds, identify human emotions, and provide personalized mental health or lifestyle suggestions based on the user's current mood.

# 🚀 Features
**Real-Time Emotion Detection:** Analyzes facial expressions via webcam with a 15 FPS stream.

**Deep Learning Backend:** Utilizes the DeepFace library for high-accuracy emotion classification (Happy, Sad, Angry, Fear, Surprise, Disgust, Neutral).

**Intelligent Suggestions:** Provides dynamic activities and "Therapist Alerts" based on the detected emotion.

**Secure User Authentication:** Full Login/Signup system with scrypt password hashing and SQLite database integration.

**Optimized Performance:** Implements frame-skipping (analyzing every 10th frame) to ensure smooth video playback without lagging the CPU.

# 🛠️ Technical Stack
**Backend:** Python, Flask

**AI/ML:** DeepFace (Ensemble Learning), OpenCV

**Database:** SQLite3

**Security:** Werkzeug Security (Password Hashing)

**Concurrency:** Threading (Mutex Locks for data integrity)

<img width="990" height="671" alt="image" src="https://github.com/user-attachments/assets/33ef13e1-0c51-4391-88ee-6ddae7b8b221" />
# ⚙️ Installation & Setup
# Clone the repository

Bash
git clone https://github.com/yourusername/emotion-recognition-web.git
cd emotion-recognition-web
Install Dependencies

Bash
pip install flask opencv-python deepface tf-keras
Initialize the Database
The application automatically creates faceask.db and the users table upon the first run.

# Run the Application

Bash
python app.py
Access the app at http://127.0.0.1:5000/

# 🧠 System Architecture
**generate_frames():** Captures video, detects faces using Haar Cascades, and triggers the DeepFace.analyze function.

**emotion_lock:** A threading lock used to safely update the current_emotion global variable while the Flask route emotion_data reads it simultaneously.

**/emotion_data Endpoint:** A JSON API that the frontend polls to update the "Suggestions" section without refreshing the entire page.

# 📝 Future Scope
**Emotion Trends:** Adding a dashboard to track a user's mood over a week using Matplotlib.

**Enhanced Security:** Implementing JWT (JSON Web Tokens) for session management.

**Multiple Face Detection:** Expanding the analysis to support multiple people in a single frame.
