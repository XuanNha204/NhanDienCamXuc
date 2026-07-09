import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL,
        Avatar TEXT,
        CreatedAt TEXT NOT NULL
    )
    ''')
    
    # Create EmotionLogs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS EmotionLogs (
        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        Emotion TEXT NOT NULL,
        Confidence REAL NOT NULL,
        ImagePath TEXT,
        CaptureTime TEXT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    ''')
    
    # Create Predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Predictions (
        PredictionID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        PredictedEmotion TEXT NOT NULL,
        Probability REAL NOT NULL,
        PredictTime TEXT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    ''')
    
    # Create Reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reports (
        ReportID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        PdfPath TEXT NOT NULL,
        CreatedAt TEXT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    
    # Seed default users if empty
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_users = [("Nhã", None), ("Phong", None), ("Kiệt", None), ("Sơn", None)]
        cursor.executemany(
            "INSERT INTO Users (FullName, Avatar, CreatedAt) VALUES (?, ?, ?)",
            [(u[0], u[1], now) for u in default_users]
        )
        conn.commit()
        print("Database seeded with default users.")
        
    conn.close()

def add_user(full_name, avatar=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO Users (FullName, Avatar, CreatedAt) VALUES (?, ?, ?)",
        (full_name, avatar, now)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users ORDER BY UserID ASC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def log_emotion(user_id, emotion, confidence, image_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO EmotionLogs (UserID, Emotion, Confidence, ImagePath, CaptureTime) VALUES (?, ?, ?, ?, ?)",
        (user_id, emotion, confidence, image_path, now)
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_recent_logs(user_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM EmotionLogs WHERE UserID = ? ORDER BY CaptureTime DESC LIMIT ?",
        (user_id, limit)
    )
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_logs_in_range(user_id, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Format dates as YYYY-MM-DD
    # Query comparing strings works correctly because dates are saved in ISO-like format: YYYY-MM-DD HH:MM:SS
    cursor.execute(
        "SELECT * FROM EmotionLogs WHERE UserID = ? AND date(CaptureTime) BETWEEN ? AND ? ORDER BY CaptureTime ASC",
        (user_id, start_date, end_date)
    )
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_emotion_distribution(user_id, days=7):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT Emotion, COUNT(*) as count 
        FROM EmotionLogs 
        WHERE UserID = ? AND datetime(CaptureTime) >= datetime('now', ?)
        GROUP BY Emotion
        """,
        (user_id, f"-{days} days")
    )
    dist = {row['Emotion']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return dist

def get_hourly_heatmap_data(user_id):
    """
    Returns counts of emotions classified grouped by Hour and Day of Week (0-6, Sunday to Saturday).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # strftime('%w', ...) returns day of week 0-6 (0 is Sunday)
    # strftime('%H', ...) returns hour 00-23
    cursor.execute(
        """
        SELECT 
            CAST(strftime('%w', CaptureTime) AS INTEGER) as day_of_week,
            CAST(strftime('%H', CaptureTime) AS INTEGER) as hour,
            Emotion,
            COUNT(*) as count
        FROM EmotionLogs
        WHERE UserID = ?
        GROUP BY day_of_week, hour, Emotion
        """,
        (user_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def save_prediction(user_id, predicted_emotion, probability):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO Predictions (UserID, PredictedEmotion, Probability, PredictTime) VALUES (?, ?, ?, ?)",
        (user_id, predicted_emotion, probability, now)
    )
    conn.commit()
    pred_id = cursor.lastrowid
    conn.close()
    return pred_id

def get_latest_prediction(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Predictions WHERE UserID = ? ORDER BY PredictTime DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_report(user_id, pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO Reports (UserID, PdfPath, CreatedAt) VALUES (?, ?, ?)",
        (user_id, pdf_path, now)
    )
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_reports(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Reports WHERE UserID = ? ORDER BY CreatedAt DESC",
        (user_id,)
    )
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports

if __name__ == "__main__":
    init_db()
    print("Database path:", DB_PATH)
