import collections
import database

def get_recommendation(user_id):
    """
    Analyzes recent logs (last 24 hours or last 20 logs)
    and returns psychological status and lifestyle recommendations.
    """
    logs = database.get_recent_logs(user_id, limit=20)
    
    if not logs:
        return {
            "status": "Chưa có dữ liệu",
            "message": "Hệ thống cần thêm dữ liệu nhận diện cảm xúc để đưa ra đề xuất chính xác.",
            "recommendations": [
                "Hãy bật Camera và ghi nhận cảm xúc của bạn.",
                "Ghi nhận cảm xúc thường xuyên giúp biểu đồ phân tích chính xác hơn."
            ],
            "dominant_emotion": "Neutral",
            "score": 0.0
        }
        
    emotions = [log['Emotion'] for log in logs]
    counter = collections.Counter(emotions)
    total = len(emotions)
    
    # Calculate dominant emotion
    dominant, count = counter.most_common(1)[0]
    dominant_pct = count / total
    
    # Group emotions
    positive_count = counter['Happy'] + counter['Surprise']
    negative_count = counter['Sad'] + counter['Angry'] + counter['Fear'] + counter['Contempt'] + counter['Disgust']
    neutral_count = counter['Neutral']
    
    pos_pct = positive_count / total
    neg_pct = negative_count / total
    
    status = ""
    message = ""
    recommendations = []
    
    # Decide suggestions based on dominant emotion & overall trend
    if neg_pct >= 0.5:
        status = "Căng thẳng / Cảm xúc tiêu cực"
        message = f"Gần đây bạn có tỷ lệ cảm xúc tiêu cực khá cao ({neg_pct*100:.1f}%). Hệ thống nhận thấy bạn có dấu hiệu mệt mỏi hoặc lo âu."
        
        # Specific based on dominant
        if dominant == 'Sad':
            recommendations = [
                "Nghe một playlist nhạc Lofi hoặc Acoustic nhẹ nhàng để xoa dịu tinh thần.",
                "Thực hiện một chuyến đi dạo ngắn ngoài trời hoặc uống một ly nước ấm.",
                "Trò chuyện hoặc chia sẻ cảm xúc với một người thân hay bạn bè.",
                "Tránh làm việc quá sức; hãy cho phép bản thân nghỉ ngơi 15-30 phút."
            ]
        elif dominant == 'Angry':
            recommendations = [
                "Áp dụng phương pháp thở 4-4-4: Hít vào 4 giây, giữ hơi 4 giây, thở ra 4 giây (lặp lại 5 lần).",
                "Rửa mặt bằng nước mát hoặc uống một cốc nước để giảm nhiệt độ cơ thể.",
                "Tạm thời rời mắt khỏi màn hình máy tính và vươn vai thư giãn cơ bắp.",
                "Nghe nhạc không lời hoặc tiếng mưa rơi để hạ nhiệt căng thẳng."
            ]
        elif dominant == 'Fear' or dominant == 'Contempt' or dominant == 'Disgust':
            recommendations = [
                "Nhắm mắt lại và tập trung vào hơi thở để lấy lại sự cân bằng.",
                "Viết các lo lắng ra giấy để giải phóng đầu óc khỏi suy nghĩ tiêu cực.",
                "Tập thể dục nhẹ nhàng (yoga, giãn cơ) để giải tỏa hormone cortisol gây stress.",
                "Sắp xếp lại bàn làm việc sạch sẽ để tạo không gian thoải mái, an tâm."
            ]
        else:
            recommendations = [
                "Dành thời gian nghỉ ngơi hợp lý, tránh stress kéo dài.",
                "Tập thể dục nhẹ nhàng và đảm bảo ngủ đủ giấc (7-8 tiếng/ngày)."
            ]
    elif pos_pct >= 0.5:
        status = "Tích cực / Hạnh phúc"
        message = f"Tinh thần của bạn đang rất tuyệt vời với {pos_pct*100:.1f}% cảm xúc tích cực. Hãy tiếp tục duy trì nguồn năng lượng này nhé!"
        
        recommendations = [
            "Lan tỏa niềm vui bằng cách gửi lời chào hoặc lời chúc tích cực tới đồng nghiệp/bạn bè.",
            "Tận dụng sự hứng khởi hiện tại để thực hiện các công việc cần tính sáng tạo và tập trung cao.",
            "Ghi lại những điều tích cực hôm nay vào nhật ký để lưu giữ năng lượng tốt đẹp.",
            "Tự thưởng cho bản thân một món ăn yêu thích hoặc hoạt động giải trí nhẹ nhàng."
        ]
    else:
        status = "Ổn định / Trung tính"
        message = "Trạng thái cảm xúc của bạn đang cân bằng và ổn định. Đây là thời điểm tốt để làm việc hiệu quả và tập trung."
        
        recommendations = [
            "Uống một tách trà xanh hoặc nước lọc để duy trì sự tỉnh táo.",
            "Thực hiện các động tác kéo giãn vai và cổ sau mỗi 45 phút ngồi làm việc.",
            "Lập kế hoạch công việc rõ ràng cho những giờ tiếp theo để tối ưu hóa năng lượng.",
            "Đảm bảo duy trì chế độ dinh dưỡng lành mạnh trong ngày."
        ]
        
    return {
        "status": status,
        "message": message,
        "recommendations": recommendations,
        "dominant_emotion": dominant,
        "score": float(dominant_pct),
        "pos_pct": float(pos_pct),
        "neg_pct": float(neg_pct),
        "neutral_pct": float(neutral_count / total)
    }

if __name__ == "__main__":
    # Test stub
    print("Recommendation engine loaded.")
