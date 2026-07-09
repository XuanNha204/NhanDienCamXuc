import os
import urllib.request
import cv2
import numpy as np
import onnxruntime as ort

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "emotion-ferplus-8.onnx")
MODEL_URL = "https://huggingface.co/onnxmodelzoo/emotion-ferplus-8/resolve/main/emotion-ferplus-8.onnx"

# The 8 output classes from FERPlus
EMOTIONS = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Angry', 'Disgust', 'Fear', 'Contempt']
EMOJIS = {
    'Neutral': '😐',
    'Happy': '😊',
    'Surprise': '😲',
    'Sad': '😢',
    'Angry': '😡',
    'Disgust': '🤢',
    'Fear': '😱',
    'Contempt': '😒'
}

_session = None
_face_cascade = None

def download_model():
    """Downloads the ONNX emotion recognition model if it doesn't exist."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    if not os.path.exists(MODEL_PATH):
        print(f"ONNX model not found. Downloading from {MODEL_URL}...")
        try:
            # Simple download indicator
            def progress(block_num, block_size, total_size):
                percent = int(block_num * block_size * 100 / total_size)
                if percent % 10 == 0:
                    print(f"Downloading model: {percent}% completed...", end="\r")
                    
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH, reporthook=progress)
            print("\nModel downloaded successfully!")
        except Exception as e:
            print(f"\nError downloading model: {e}")
            # Try a fallback URL from Github ONNX Model Zoo
            fallback_url = "https://github.com/onnx/models/raw/main/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx"
            print(f"Trying fallback URL: {fallback_url}...")
            try:
                urllib.request.urlretrieve(fallback_url, MODEL_PATH)
                print("Model downloaded successfully from fallback URL!")
            except Exception as fe:
                print(f"Fallback download failed: {fe}")
                raise fe

def load_emotion_model():
    """Loads the ONNX model session."""
    global _session
    if _session is None:
        download_model()
        # Set providers. CPUProvider is always available.
        _session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    return _session

def load_face_cascade():
    """Loads the OpenCV face cascade classifier."""
    global _face_cascade
    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade

def softmax(x):
    """Computes softmax values for a set of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def detect_faces(gray_frame):
    """Detects faces in a grayscale frame and returns coordinates."""
    cascade = load_face_cascade()
    # scaleFactor=1.1, minNeighbors=5, minSize=(30, 30) are standard values
    faces = cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    return faces

def predict_emotion(gray_face_crop):
    """
    Takes a grayscale cropped face, preprocesses it, 
    and predicts probabilities of the 8 emotions.
    """
    session = load_emotion_model()
    
    # 1. Resize to 64x64
    resized = cv2.resize(gray_face_crop, (64, 64), interpolation=cv2.INTER_AREA)
    
    # 2. Convert to float32 and shape (1, 1, 64, 64)
    input_data = resized.astype(np.float32)
    input_data = np.expand_dims(input_data, axis=0) # shape (1, 64, 64)
    input_data = np.expand_dims(input_data, axis=0) # shape (1, 1, 64, 64)
    
    # Get model input and output names
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    
    # Run prediction
    raw_outputs = session.run([output_name], {input_name: input_data})[0][0]
    
    # Apply softmax to get probabilities
    probabilities = softmax(raw_outputs)
    
    # Map to dictionary
    result = {EMOTIONS[i]: float(probabilities[i]) for i in range(len(EMOTIONS))}
    return result

def get_dominant_emotion(emotion_probs):
    """Returns the name and confidence of the dominant emotion."""
    dominant = max(emotion_probs, key=emotion_probs.get)
    return dominant, emotion_probs[dominant]

if __name__ == "__main__":
    # Test execution
    print("Loading models...")
    load_face_cascade()
    load_emotion_model()
    print("Models loaded successfully.")
    
    # Create a dummy image of a face (64x64) and test predict
    dummy_face = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
    probs = predict_emotion(dummy_face)
    print("Dummy face prediction probabilities:")
    for k, v in probs.items():
        print(f"  {k}: {v*100:.2f}%")
    dom, conf = get_dominant_emotion(probs)
    print(f"Dominant emotion: {dom} ({conf*100:.2f}%)")
