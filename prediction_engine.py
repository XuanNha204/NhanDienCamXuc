import collections
import numpy as np
from datetime import datetime, timedelta
import database

# The list of possible emotions
EMOTIONS = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Angry', 'Disgust', 'Fear', 'Contempt']

def get_daily_dominant_emotions(user_id):
    """
    Retrieves the daily dominant emotion for the user from history.
    Returns a list of tuples: (date_str, emotion) sorted by date.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Group by date and find the most frequent emotion for each day
    cursor.execute(
        """
        WITH DailyCounts AS (
            SELECT 
                date(CaptureTime) as log_date,
                Emotion,
                COUNT(*) as count
            FROM EmotionLogs
            WHERE UserID = ?
            GROUP BY log_date, Emotion
        ),
        RankedDaily AS (
            SELECT 
                log_date,
                Emotion,
                count,
                ROW_NUMBER() OVER (PARTITION BY log_date ORDER BY count DESC) as rank
            FROM DailyCounts
        )
        SELECT log_date, Emotion
        FROM RankedDaily
        WHERE rank = 1
        ORDER BY log_date ASC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [(row['log_date'], row['Emotion']) for row in rows]

def predict_tomorrow_emotion(user_id):
    """
    Predicts the user's emotion for tomorrow based on history.
    Uses a Markov Chain transition model if history is small (< 15 days),
    and can use Random Forest if history is larger.
    Returns:
        predicted_emotion (str)
        confidence (float)
    """
    history = get_daily_dominant_emotions(user_id)
    
    if len(history) < 2:
        # Fallback 1: No history or only 1 day. Use overall distribution.
        logs = database.get_recent_logs(user_id, limit=50)
        if not logs:
            return "Neutral", 1.0
            
        emotions = [log['Emotion'] for log in logs]
        counter = collections.Counter(emotions)
        most_common = counter.most_common(1)[0]
        return most_common[0], float(most_common[1] / len(emotions))
        
    # Extract the sequence of emotions
    sequence = [item[1] for item in history]
    today_emotion = sequence[-1]
    
    # Fallback 2: Compute Markov Chain transition probabilities
    # We want to find: P(tomorrow_emotion | today_emotion)
    transitions = collections.defaultdict(list)
    for i in range(len(sequence) - 1):
        state_from = sequence[i]
        state_to = sequence[i+1]
        transitions[state_from].append(state_to)
        
    # If we have transition data for today's emotion, use it
    if today_emotion in transitions:
        next_states = transitions[today_emotion]
        counter = collections.Counter(next_states)
        predicted_emotion, count = counter.most_common(1)[0]
        probability = count / len(next_states)
        
        # Save to DB
        database.save_prediction(user_id, predicted_emotion, probability)
        return predicted_emotion, float(probability)
    else:
        # If today's emotion is new and has no transition history,
        # predict the most frequent transition overall or today's emotion.
        # Let's predict today's emotion with average probability.
        counter = collections.Counter(sequence)
        probability = counter[today_emotion] / len(sequence)
        
        # Save to DB
        database.save_prediction(user_id, today_emotion, probability)
        return today_emotion, float(probability)

if __name__ == "__main__":
    # Test stub
    print("Prediction engine loaded.")
