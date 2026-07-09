# Kết quả hoàn thành: Hệ thống Nhận diện Cảm xúc & Nhận dạng Khuôn mặt thông minh (10 Modules)

Dự án đã được triển khai thành công với đầy đủ **10 Modules** chức năng, kết hợp công nghệ xử lý ảnh (OpenCV), mô hình học sâu nhận diện cảm xúc ONNX, nhận diện danh tính bằng học máy (HOG + Random Forest), thống kê biểu đồ động (Chart.js + Heatmap), đề xuất sức khỏe AI và xuất báo cáo PDF thông minh. Giao diện được thiết kế theo phong cách Cyberpunk Dark Theme / Glassmorphism cao cấp.

---

## 1. Các thành phần đã hoàn thành

### Giao diện và Giao thức Webcam:
- **Giao diện Glassmorphism**: Nền tối sâu với các hiệu ứng kính mờ, phát sáng neon, phối màu nhất quán tương thích với từng cảm xúc.
- **Client-side Streaming**: Webcam hoạt động trực tiếp trên trình duyệt bằng HTML5, chụp frame gửi lên backend qua REST API định kỳ giúp tối ưu tốc độ và không bị lỗi phần cứng ở máy chủ.
- **Biểu đồ cột động**: Phân tích tỷ lệ phần trăm của 8 cảm xúc hiển thị mượt mà theo thời gian thực dưới dạng thanh tiến trình.

### Các Module chức năng đã kiểm thử hoạt động:
1. **Module 1 (Face Detection)**: Định vị khuôn mặt và vẽ khung bao (bounding box) kèm nhãn thông tin.
2. **Module 2 (Emotion Recognition AI)**: Tích hợp mô hình học sâu ONNX FERPlus nhận diện 8 cảm xúc. Tự động tải từ Hugging Face.
3. **Module 3 (Snapshot Database)**: SQLite lưu trữ 4 bảng (`Users`, `EmotionLogs`, `Predictions`, `Reports`). Chụp và lưu ảnh khuôn mặt làm thumbnail.
4. **Module 4 (Emotion Timeline)**: Ghi lại diễn biến cảm xúc theo dòng thời gian phục vụ phân tích.
5. **Module 5 (Emotion Analytics)**: Giao diện dashboard hiển thị biểu đồ tròn (phần trăm cảm xúc), biểu đồ đường (chỉ số tinh thần valence) và bản đồ nhiệt (Heatmap) khung giờ vui vẻ nhất trong tuần.
6. **Module 6 (Emotion Prediction)**: Dự báo cảm xúc ngày mai dựa trên phân tích Markov Chain.
7. **Module 7 (Recommendation AI)**: Đưa ra danh sách lời khuyên chăm sóc tâm lý cá nhân hóa dựa trên dữ liệu cảm xúc 24 giờ.
8. **Module 8 (PDF Intelligence Report)**: Xuất file PDF báo cáo thông minh chứa biểu đồ dạng bảng, chỉ số chính và gợi ý tinh thần từ AI bằng thư viện `reportlab`.
9. **Module 9 (Multi-user)**: Đa người dùng, hỗ trợ chuyển đổi dashboard và dữ liệu riêng biệt.
10. **Module 10 (Face Recognition)**: Đăng ký khuôn mặt động (chụp 15 góc mặt) và tự động nhận diện danh tính khi đứng trước camera sử dụng **HOG + Random Forest**.

---

## 2. Giao diện ứng dụng thực tế

### Giao diện chính (Live Camera & Nhận diện thời gian thực)
Giao diện bao gồm khung hình camera, bảng chọn profile, banner kết quả cảm xúc động, biểu đồ xác suất của 8 cảm xúc, các tùy chọn "Tự động lưu log (3s)", "Chụp Snapshot" và "Đăng ký khuôn mặt".

![Giao diện chính - Live Camera](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/f2dc306e-fda3-4fd7-9336-18d807400425/live_emotion_recognition_homepage_1781837985962.png)

### Giao diện Thống kê (Analytics Dashboard)
Hiển thị khi chuyển sang tab Dashboard. Nếu người dùng chưa có dữ liệu cảm xúc, màn hình cảnh báo thân thiện sẽ xuất hiện để nhắc nhở ghi log trước khi xem số liệu chi tiết.

![Giao diện phân tích - Dashboard](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/f2dc306e-fda3-4fd7-9336-18d807400425/dashboard_no_data_1781838009062.png)

---

## 3. Cấu trúc thư mục dự án

Dự án được tạo mới hoàn toàn trong thư mục [DeepAI](file:///d:/DeepAI) với các file cấu trúc như sau:
*   [requirements.txt](file:///d:/DeepAI/requirements.txt): Định nghĩa các thư viện phụ thuộc.
*   [database.py](file:///d:/DeepAI/database.py): Quản lý cơ sở dữ liệu SQLite, khởi tạo các bảng và thực hiện truy vấn.
*   [model_helper.py](file:///d:/DeepAI/model_helper.py): Xử lý mô hình ONNX nhận dạng cảm xúc và phát hiện mặt bằng Haar Cascade.
*   [face_recognizer.py](file:///d:/DeepAI/face_recognizer.py): Đăng ký khuôn mặt, trích xuất HOG đặc trưng và nhận diện danh tính bằng Random Forest.
*   [prediction_engine.py](file:///d:/DeepAI/prediction_engine.py): Dự báo cảm xúc ngày mai dựa trên chuỗi trạng thái Markov Chain.
*   [recommendation_engine.py](file:///d:/DeepAI/recommendation_engine.py): Phân tích lịch sử tâm lý và đưa ra lời khuyên chăm sóc tinh thần từ AI.
*   [report_generator.py](file:///d:/DeepAI/report_generator.py): Sinh file PDF báo cáo thông minh, tương thích tiếng Việt Unicode.
*   [app.py](file:///d:/DeepAI/app.py): Server Flask quản lý định tuyến, API endpoint và tích hợp hệ thống.
*   `templates/`: Chứa mã HTML giao diện
    *   [index.html](file:///d:/DeepAI/templates/index.html)
    *   [dashboard.html](file:///d:/DeepAI/templates/dashboard.html)
*   `static/`: Tài nguyên tĩnh
    *   [css/style.css](file:///d:/DeepAI/static/css/style.css): File CSS Premium Cyberpunk.
    *   `js/`:
        *   [main.js](file:///d:/DeepAI/static/js/main.js): Điều khiển Webcam client, gửi dữ liệu nhận diện và đăng ký mặt.
        *   [dashboard.js](file:///d:/DeepAI/static/js/dashboard.js): Gọi API lấy số liệu và vẽ biểu đồ Chart.js, Heatmap.

---

## 4. Hướng dẫn khởi chạy ứng dụng

Để chạy thử ứng dụng trên máy của bạn, thực hiện các bước sau:

1.  **Mở Terminal** tại thư mục dự án `d:\DeepAI`.
2.  **Kích hoạt môi trường ảo**:
    *   Trên Windows Powershell: `.venv\Scripts\Activate.ps1`
    *   Trên Windows CMD: `.venv\Scripts\activate.bat`
3.  **Khởi chạy Flask Server**:
    ```bash
    python app.py
    ```
4.  **Truy cập trình duyệt**: Mở link `http://localhost:5000`.

---

## 5. Hướng dẫn sử dụng thử nghiệm các tính năng chính

*   **Bước 1: Tạo tài liệu người dùng**
    Nhấp nút `+` (Thêm User mới) ở góc trên bên phải trang chủ, nhập tên của bạn (Ví dụ: "Nhã") và bấm Lưu. Chọn tên của bạn trong danh sách dropdown.
*   **Bước 2: Đăng ký nhận diện mặt**
    Nhấp nút **Đăng ký khuôn mặt**. Bấm **Bắt đầu quét** và làm theo hướng dẫn trên màn hình (nhìn thẳng, nghiêng trái, nghiêng phải, mỉm cười...) để hệ thống thu thập 15 bức ảnh và tự động huấn luyện bộ phân lớp nhận diện mặt.
*   **Bước 3: Chạy nhận diện & Ghi log**
    Bật nút **Bắt đầu Camera**, hệ thống sẽ tự động vẽ bounding box quanh mặt bạn, nhận diện đúng Tên của bạn và hiển thị cảm xúc trực tiếp. Bật nút **Tự động lưu log (3s)** để hệ thống tự động ghi lại lịch sử cảm xúc mỗi 3 giây hoặc nhấp **Chụp Snapshot** để ghi log thủ công kèm ảnh chụp.
*   **Bước 4: Xem phân tích và xuất PDF**
    Nhấp vào liên kết **Analytics Dashboard** trên thanh menu để chuyển sang màn hình biểu đồ. Tại đây bạn sẽ thấy biểu đồ tròn phân phối cảm xúc, biểu đồ đường thể hiện chỉ số tinh thần biến đổi, bản đồ nhiệt Heatmap khung giờ vui vẻ, đề xuất sức khỏe AI và thư viện ảnh chụp khuôn mặt. Nhấp **Xuất Báo cáo PDF** để tải xuống bản báo cáo thông minh.
