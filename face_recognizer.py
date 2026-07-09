import os
import cv2
import numpy as np
import pickle
from datetime import datetime

# We will import skimage.feature.hog and sklearn dynamically in functions 
# to avoid import errors if they are still installing when this file is analyzed.

FACES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "faces")
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
RECOGNIZER_PATH = os.path.join(MODEL_DIR, "face_recognizer.pkl")

# Ensure directories exist
for d in [FACES_DIR, MODEL_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

def get_face_embedding(gray_face_crop):
    """
    Extracts HOG features from a grayscale face crop, 
    normalizing it to unit length (L2 norm) as a face embedding.
    """
    from skimage.feature import hog
    
    # 1. Resize to standard size 64x64
    resized = cv2.resize(gray_face_crop, (64, 64), interpolation=cv2.INTER_AREA)
    
    # 2. Extract HOG features
    features = hog(
        resized, 
        orientations=8, 
        pixels_per_cell=(8, 8), 
        cells_per_block=(2, 2), 
        visualize=False
    )
    
    # 3. L2 Normalize features to get a unit-length embedding
    norm = np.linalg.norm(features)
    if norm > 0:
        features = features / norm
        
    return features

def save_registration_frame(user_id, gray_face_crop, frame_index):
    """Saves a cropped face to the user's registration directory."""
    user_dir = os.path.join(FACES_DIR, f"user_{user_id}")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        
    # Standardize image size
    face_img = cv2.resize(gray_face_crop, (128, 128), interpolation=cv2.INTER_AREA)
    file_path = os.path.join(user_dir, f"face_{frame_index}.jpg")
    cv2.imwrite(file_path, face_img)
    return file_path

def train_face_recognizer():
    """
    Loads all registered faces, extracts HOG embeddings,
    and trains a RandomForestClassifier to recognize users.
    """
    from sklearn.ensemble import RandomForestClassifier
    
    X = []
    y = []
    
    # Scan user folders
    user_dirs = [d for d in os.listdir(FACES_DIR) if d.startswith("user_") and os.path.isdir(os.path.join(FACES_DIR, d))]
    
    if len(user_dirs) == 0:
        print("No registered users found for face recognition.")
        if os.path.exists(RECOGNIZER_PATH):
            os.remove(RECOGNIZER_PATH)
        return False
        
    # Read images and extract embeddings
    for d in user_dirs:
        try:
            user_id = int(d.split("_")[1])
        except ValueError:
            continue
            
        user_path = os.path.join(FACES_DIR, d)
        for f in os.listdir(user_path):
            if f.endswith(".jpg") or f.endswith(".png"):
                img_path = os.path.join(user_path, f)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    emb = get_face_embedding(img)
                    X.append(emb)
                    y.append(user_id)
                    
    # Generate some dummy "Unknown" samples to teach the classifier
    # what unregistered faces/noise look like.
    # This prevents false positives when a new person stands in front of the camera.
    num_unknown = max(20, len(X) // 2)
    for _ in range(num_unknown):
        # Noise/random gradient embeddings
        random_face = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        # Apply slight blur to simulate a face
        random_face = cv2.GaussianBlur(random_face, (5, 5), 0)
        emb = get_face_embedding(random_face)
        X.append(emb)
        y.append(-1) # -1 stands for Unknown
        
    X = np.array(X)
    y = np.array(y)
    
    # Train Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X, y)
    
    # Save the trained recognizer
    with open(RECOGNIZER_PATH, 'wb') as f:
        pickle.dump(clf, f)
        
    print(f"Face recognizer trained successfully with {len(user_dirs)} users and saved.")
    return True

def recognize_face(gray_face_crop, threshold=0.55):
    """
    Extracts HOG embedding from the face crop and predicts UserID.
    Returns:
        user_id (int) or None if Unknown.
        confidence (float).
    """
    if not os.path.exists(RECOGNIZER_PATH):
        # If no trained model, try basic similarity fallback
        return fallback_distance_recognition(gray_face_crop, threshold)
        
    try:
        with open(RECOGNIZER_PATH, 'rb') as f:
            clf = pickle.load(f)
            
        emb = get_face_embedding(gray_face_crop).reshape(1, -1)
        
        # Predict probability
        probs = clf.predict_proba(emb)[0]
        classes = clf.classes_
        
        max_idx = np.argmax(probs)
        pred_user_id = classes[max_idx]
        confidence = probs[max_idx]
        
        # If class is -1 (Unknown) or probability is below threshold, return None
        if pred_user_id == -1 or confidence < threshold:
            return None, float(confidence)
            
        return int(pred_user_id), float(confidence)
    except Exception as e:
        print(f"Error during face recognition: {e}")
        return None, 0.0

def fallback_distance_recognition(gray_face_crop, threshold=0.55):
    """
    Fallback nearest-centroid face recognition using cosine similarity of HOG embeddings.
    Allows recognition to work even before multiple users are trained with Random Forest.
    """
    emb = get_face_embedding(gray_face_crop)
    
    best_user_id = None
    best_similarity = -1.0
    
    user_dirs = [d for d in os.listdir(FACES_DIR) if d.startswith("user_") and os.path.isdir(os.path.join(FACES_DIR, d))]
    
    for d in user_dirs:
        try:
            user_id = int(d.split("_")[1])
        except ValueError:
            continue
            
        user_path = os.path.join(FACES_DIR, d)
        user_embs = []
        
        for f in os.listdir(user_path):
            if f.endswith(".jpg") or f.endswith(".png"):
                img_path = os.path.join(user_path, f)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    user_embs.append(get_face_embedding(img))
                    
        if len(user_embs) > 0:
            # Calculate centroid (average embedding)
            centroid = np.mean(user_embs, axis=0)
            centroid = centroid / np.linalg.norm(centroid) # normalize
            
            # Cosine similarity
            similarity = np.dot(emb, centroid)
            if similarity > best_similarity:
                best_similarity = similarity
                best_user_id = user_id
                
    # Normalize similarity from [-1, 1] to [0, 1]
    confidence = (best_similarity + 1.0) / 2.0
    
    # Check if confidence passes the threshold
    if best_user_id is not None and confidence > threshold:
        return best_user_id, confidence
        
    return None, confidence

if __name__ == "__main__":
    # Test compilation
    print("FACES_DIR:", FACES_DIR)
    print("RECOGNIZER_PATH:", RECOGNIZER_PATH)
