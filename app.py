import os
import sys
import subprocess

# Auto-execute using virtual environment (.venv) if libraries are missing in current environment
if not os.environ.get("VENV_RERUN"):
    try:
        # pyrefly: ignore [missing-import]
        import flask
        import numpy
        import cv2
    except ImportError:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.name == 'nt':
            venv_python = os.path.join(current_dir, ".venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(current_dir, ".venv", "bin", "python")
        
        if os.path.exists(venv_python):
            os.environ["VENV_RERUN"] = "1"
            sys.exit(subprocess.run([venv_python] + sys.argv).returncode)

import base64
import time
from datetime import datetime
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, jsonify, request, send_from_directory
import numpy as np
import cv2

import database
import model_helper
import face_recognizer
import prediction_engine
import recommendation_engine
import report_generator

app = Flask(__name__)

# Ensure required directories exist
CAPTURED_DIR = os.path.join(app.root_path, "static", "captured_images")
os.makedirs(CAPTURED_DIR, exist_ok=True)

# Initialize database
database.init_db()

# Warm up models
print("Warming up models...")
model_helper.load_face_cascade()
try:
    model_helper.load_emotion_model()
except Exception as e:
    print("Warning: Could not warm up emotion model at startup. It will be downloaded on first request.", e)

def decode_base64_image(base64_str):
    """Decodes a base64 encoded image string into an OpenCV BGR image."""
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/users', methods=['GET'])
def get_users_api():
    try:
        users = database.get_users()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_user_api():
    try:
        data = request.json
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"success": False, "error": "Name is required"}), 400
        
        user_id = database.add_user(name)
        return jsonify({"success": True, "user_id": user_id, "name": name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user_api(user_id):
    try:
        # Delete face directory if exists
        user_faces_dir = os.path.join(face_recognizer.FACES_DIR, f"user_{user_id}")
        if os.path.exists(user_faces_dir):
            import shutil
            shutil.rmtree(user_faces_dir)
            
        database.delete_user(user_id)
        
        # Retrain recognizer to remove deleted user
        face_recognizer.train_face_recognizer()
        
        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/detect', methods=['POST'])
def detect_api():
    try:
        data = request.json
        img_b64 = data.get("image")
        active_user_id = data.get("user_id") # Selected user (can be None)
        save_log = data.get("save_log", False)
        
        if not img_b64:
            return jsonify({"success": False, "error": "No image data provided"}), 400
            
        frame = decode_base64_image(img_b64)
        if frame is None:
            return jsonify({"success": False, "error": "Invalid image data"}), 400
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = model_helper.detect_faces(gray)
        
        results = []
        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            
            # 1. Run Emotion Prediction
            emotion_probs = model_helper.predict_emotion(face_crop)
            dominant, confidence = model_helper.get_dominant_emotion(emotion_probs)
            
            # 2. Run Face Recognition
            recognized_user_id, recognized_conf = face_recognizer.recognize_face(face_crop)
            recognized_name = None
            if recognized_user_id is not None:
                user_info = database.get_user_by_id(recognized_user_id)
                if user_info:
                    recognized_name = user_info['FullName']
            
            # Determine which user ID to log this emotion under.
            # Priority:
            # - If Face Recognition detects a known user with high confidence, use it.
            # - Otherwise, use the manually selected active_user_id (if any).
            log_user_id = recognized_user_id if recognized_user_id is not None else active_user_id
            
            saved_image_path = None
            log_id = None
            
            # 3. Log to DB if requested and we have a valid user
            if save_log and log_user_id is not None:
                # Save face snapshot (Chức năng 1)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"face_{log_user_id}_{timestamp}.jpg"
                filepath = os.path.join(CAPTURED_DIR, filename)
                
                # Save cropped color face for visual quality
                face_color_crop = frame[y:y+h, x:x+w]
                cv2.imwrite(filepath, face_color_crop)
                saved_image_path = f"static/captured_images/{filename}"
                
                # Log to SQLite
                log_id = database.log_emotion(log_user_id, dominant, confidence, saved_image_path)
            
            results.append({
                "box": [int(x), int(y), int(w), int(h)],
                "emotions": emotion_probs,
                "dominant_emotion": dominant,
                "dominant_confidence": float(confidence),
                "recognized_user_id": recognized_user_id,
                "recognized_name": recognized_name,
                "recognized_confidence": float(recognized_conf) if recognized_conf is not None else 0.0,
                "log_id": log_id,
                "image_path": saved_image_path
            })
            
        return jsonify({"success": True, "faces": results})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/register_face', methods=['POST'])
def register_face_api():
    try:
        data = request.json
        img_b64 = data.get("image")
        user_id = data.get("user_id")
        frame_idx = data.get("frame_index")
        
        if not img_b64 or user_id is None or frame_idx is None:
            return jsonify({"success": False, "error": "Missing parameters"}), 400
            
        frame = decode_base64_image(img_b64)
        if frame is None:
            return jsonify({"success": False, "error": "Invalid image"}), 400
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = model_helper.detect_faces(gray)
        
        if len(faces) == 0:
            return jsonify({"success": False, "error": "Không tìm thấy khuôn mặt trong ảnh"}), 400
            
        # Get the largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        face_crop = gray[y:y+h, x:x+w]
        
        # Save snapshot
        file_path = face_recognizer.save_registration_frame(user_id, face_crop, frame_idx)
        
        # If we reached 15 frames, train the model
        trained = False
        if frame_idx >= 14:
            trained = face_recognizer.train_face_recognizer()
            
        return jsonify({
            "success": True, 
            "message": f"Đã lưu frame {frame_idx + 1}/15", 
            "path": file_path,
            "trained": trained
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats/<int:user_id>', methods=['GET'])
def get_stats_api(user_id):
    try:
        user = database.get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
            
        # Get recent 10 logs
        recent_logs = database.get_recent_logs(user_id, limit=10)
        
        # Get emotion distribution (last 7 days)
        dist = database.get_emotion_distribution(user_id, days=7)
        
        # Get hourly heatmap data
        heatmap = database.get_hourly_heatmap_data(user_id)
        
        # Get recommendations
        rec = recommendation_engine.get_recommendation(user_id)
        
        # Get prediction
        pred_emotion, pred_conf = prediction_engine.predict_tomorrow_emotion(user_id)
        
        # Get history of reports
        reports = database.get_reports(user_id)
        
        return jsonify({
            "success": True,
            "user": user,
            "recent_logs": recent_logs,
            "distribution": dist,
            "heatmap": heatmap,
            "recommendation": rec,
            "prediction": {
                "emotion": pred_emotion,
                "confidence": pred_conf
            },
            "reports": reports
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export_pdf/<int:user_id>', methods=['POST'])
def export_pdf_api(user_id):
    try:
        # Default to last 30 days
        pdf_path = report_generator.generate_pdf_report(user_id)
        return jsonify({"success": True, "pdf_url": "/" + pdf_path})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
