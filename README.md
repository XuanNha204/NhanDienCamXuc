# 🎭 Hệ thống Nhận diện Cảm xúc & Nhận dạng Khuôn mặt DeepAI

Chào mừng bạn đến với **DeepAI Emotion & Face Recognition System** — một ứng dụng web cao cấp được thiết kế theo phong cách giao diện **Cyberpunk Dark Theme & Glassmorphism** hiện đại. Hệ thống tích hợp xử lý ảnh thời gian thực qua webcam, nhận dạng cảm xúc bằng mô hình học sâu CNN (ONNX), nhận diện danh tính bằng học máy (HOG + Random Forest), phân tích số liệu động, dự báo cảm xúc tương lai và tự động tạo báo cáo sức khỏe tinh thần định dạng PDF chuyên nghiệp.

---

## 🌟 Tính năng nổi bật (10 Modules cốt lõi)

Hệ thống được phát triển toàn diện với 10 module chức năng phối hợp chặt chẽ:

1. **Face Detection (Module 1):** Phát hiện và khoanh vùng khuôn mặt thời gian thực bằng bộ phân lớp Haar Cascade.
2. **Emotion Recognition AI (Module 2):** Sử dụng mô hình học sâu CNN (FERPlus) dạng ONNX để phân loại 8 trạng thái cảm xúc: *Happy, Sad, Angry, Surprise, Fear, Disgust, Contempt, Neutral*.
3. **Snapshot Database (Module 3):** Cơ sở dữ liệu SQLite lưu trữ thông tin người dùng, lịch sử cảm xúc, các kết quả dự đoán và báo cáo. Tự động chụp và lưu ảnh khuôn mặt làm hình đại diện nhỏ (thumbnail).
4. **Emotion Timeline (Module 4):** Ghi lại chi tiết diễn biến trạng thái tinh thần của từng cá nhân theo thời gian thực.
5. **Emotion Analytics (Module 5):** Bảng điều khiển phân tích thông minh hiển thị biểu đồ tròn phân phối cảm xúc, biểu đồ đường theo dõi chỉ số tinh thần (Valence) và bản đồ nhiệt (Heatmap) chỉ ra khung giờ vui vẻ nhất trong tuần.
6. **Emotion Prediction (Module 6):** Dự đoán xu hướng cảm xúc ngày mai dựa trên phân tích chuỗi chuyển trạng thái Markov Chain hoặc phân phối tần suất lịch sử.
7. **Recommendation AI (Module 7):** Hệ chuyên gia phân tích dữ liệu tâm lý trong vòng 24 giờ để đưa ra các lời khuyên chăm sóc sức khỏe tinh thần cá nhân hóa.
8. **PDF Intelligence Report (Module 8):** Xuất báo cáo tổng quan tinh thần định dạng PDF chất lượng cao, hỗ trợ hiển thị biểu đồ dạng bảng và phông chữ tiếng Việt đầy đủ.
9. **Multi-user Management (Module 9):** Hỗ trợ tạo nhiều hồ sơ người dùng riêng biệt để lưu trữ và phân tích dữ liệu độc lập.
10. **Face Recognition (Module 10):** Chế độ đăng ký khuôn mặt động (chụp 15 khung hình góc mặt khác nhau) và tự động nhận dạng danh tính khi đứng trước camera bằng thuật toán HOG kết hợp Random Forest.

---

## 📁 Cấu trúc thư mục dự án

| Đường dẫn tệp / Thư mục | Chức năng chính |
| :--- | :--- |
| 📄 [app.py](file:///d:/DeepAI/app.py) | Máy chủ Flask chính quản lý luồng xử lý, định tuyến và cung cấp các REST API. |
| 📄 [database.py](file:///d:/DeepAI/database.py) | Khởi tạo cấu trúc cơ sở dữ liệu SQLite và thực thi các truy vấn thêm/xóa/sửa log cảm xúc và người dùng. |
| 📄 [model_helper.py](file:///d:/DeepAI/model_helper.py) | Hỗ trợ phát hiện khuôn mặt và chạy suy luận mô hình học sâu ONNX nhận diện cảm xúc. |
| 📄 [face_recognizer.py](file:///d:/DeepAI/face_recognizer.py) | Quản lý đăng ký khuôn mặt, trích xuất đặc trưng HOG và phân loại danh tính qua Random Forest. |
| 📄 [prediction_engine.py](file:///d:/DeepAI/prediction_engine.py) | Động cơ dự báo cảm xúc ngày mai sử dụng thuật toán Xích Markov và phân phối tần suất. |
| 📄 [recommendation_engine.py](file:///d:/DeepAI/recommendation_engine.py) | Hệ thống luật đưa ra lời khuyên tâm lý cá nhân hóa dựa trên chỉ số cảm xúc 24 giờ. |
| 📄 [report_generator.py](file:///d:/DeepAI/report_generator.py) | Công cụ tạo file báo cáo PDF thông minh sử dụng thư viện `reportlab` hỗ trợ tiếng Việt. |
| 📄 [requirements.txt](file:///d:/DeepAI/requirements.txt) | Danh sách các thư viện Python phụ thuộc cần thiết cho dự án. |
| 📄 [run.bat](file:///d:/DeepAI/run.bat) | File thực thi dạng script để khởi chạy nhanh ứng dụng trên hệ điều hành Windows. |
| 📂 [templates/](file:///d:/DeepAI/templates/) | Thư mục chứa giao diện HTML: [index.html](file:///d:/DeepAI/templates/index.html) (Trang chủ camera) và [dashboard.html](file:///d:/DeepAI/templates/dashboard.html) (Màn hình phân tích). |
| 📂 [static/](file:///d:/DeepAI/static/) | Tài nguyên tĩnh gồm CSS ([style.css](file:///d:/DeepAI/static/css/style.css)), JS điều khiển camera ([main.js](file:///d:/DeepAI/static/js/main.js)), JS vẽ biểu đồ ([dashboard.js](file:///d:/DeepAI/static/js/dashboard.js)), ảnh snapshot khuôn mặt và các tệp báo cáo PDF. |
| 📄 [algorithms_summary.md](file:///d:/DeepAI/algorithms_summary.md) | Tài liệu mô tả chuyên sâu về các mô hình toán học và thuật toán được triển khai trong dự án. |
| 📄 [walkthrough.md](file:///d:/DeepAI/walkthrough.md) | Hướng dẫn kiểm thử và các kịch bản trải nghiệm thực tế kèm ảnh chụp giao diện. |

---

## 🛠️ Công nghệ & Thuật toán sử dụng

Hệ thống được xây dựng dựa trên sự kết hợp giữa các thư viện xử lý ảnh hàng đầu và các thuật toán học máy tối ưu:
* **Phát hiện khuôn mặt:** Thuật toán **Haar Cascade** của OpenCV, giúp xác định nhanh tọa độ khuôn mặt với chi phí tính toán thấp.
* **Đặc trưng khuôn mặt (Embedding):** Thuật toán **HOG (Histogram of Oriented Gradients)** giúp tạo vector đặc trưng hình học $1568$ chiều độc bản cho mỗi khuôn mặt.
* **Nhận dạng danh tính:** **Random Forest Classifier** của Scikit-Learn (gồm 100 cây quyết định độc lập) cho phép phân lớp đa người dùng chính xác. Sử dụng **Gaussian Noise & Gaussian Blur** để tạo dữ liệu tổng hợp làm mẫu âm tính cho lớp "Unknown" giúp loại bỏ người lạ.
* **Suy luận Cảm xúc AI:** Mạng thần kinh tích chập **CNN** được huấn luyện trên tập dữ liệu **FERPlus**, chạy suy luận qua **ONNX Runtime** trực tiếp ở backend.
* **Dự báo xu hướng cảm xúc:** **Xích Markov bậc 1 (First-Order Markov Chain)** mô tả ma trận xác suất chuyển trạng thái tinh thần giữa các ngày liên tiếp.
* **Hệ thống gợi ý cải thiện tâm lý:** **Hệ chuyên gia dựa trên luật (Rule-based Expert System)** tính toán tỷ lệ cảm xúc tích cực/tiêu cực trong 24 giờ để đưa ra liệu pháp phù hợp.
* **Ánh xạ hóa trị cảm xúc:** Chuyển đổi nhãn cảm xúc sang thang đo vô hướng **Valence** từ $-1.0$ (Angry) đến $+1.0$ (Happy) để vẽ biểu đồ biến động trực quan.

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Yêu cầu hệ thống
* Hệ điều hành: Windows, macOS hoặc Linux.
* Phiên bản Python khuyến nghị: **Python 3.10+**
* Webcam kết nối trực tiếp với thiết bị của bạn.

### 2. Cài đặt các thư viện cần thiết
Mở terminal tại thư mục dự án `d:\DeepAI` và chạy lệnh sau để cài đặt dependencies:
```bash
pip install -r requirements.txt
```

*Lưu ý: Dự án tự động hỗ trợ chạy trong môi trường ảo `.venv` nếu môi trường Python hiện tại của bạn thiếu thư viện.*

### 3. Khởi chạy ứng dụng
* **Trên Windows:** Bạn chỉ cần nhấp đúp chuột vào tệp [run.bat](file:///d:/DeepAI/run.bat) để khởi động máy chủ Flask một cách tự động.
* **Chạy bằng dòng lệnh:**
  ```bash
  python app.py
  ```

Sau khi máy chủ khởi động thành công, hãy mở trình duyệt web và truy cập địa chỉ:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 📖 Hướng dẫn sử dụng & Trải nghiệm tính năng

### Bước 1: Tạo tài khoản người dùng
1. Tại góc trên bên phải màn hình trang chủ, nhấn vào nút **Thêm User mới (`+`)**.
2. Nhập tên của bạn (Ví dụ: `Nhã`) và lưu lại.
3. Chọn hồ sơ của bạn từ danh sách dropdown để hệ thống biết đang làm việc với ai.

### Bước 2: Đăng ký nhận diện khuôn mặt
1. Chọn nút **Đăng ký khuôn mặt**.
2. Nhấp **Bắt đầu quét**. Làm theo các hướng dẫn trên màn hình (nhìn thẳng, nghiêng trái, nghiêng phải, mỉm cười...) để hệ thống tự động thu thập đủ 15 khung hình khuôn mặt chất lượng cao.
3. Sau khi quét đủ, hệ thống sẽ tự động chạy tiến trình huấn luyện bộ phân lớp Random Forest để ghi nhớ khuôn mặt của bạn.

### Bước 3: Nhận diện & Ghi log cảm xúc thời gian thực
1. Bật nút **Bắt đầu Camera**. Hệ thống sẽ hiển thị khung hình webcam, tự động đóng khung mặt bạn và gán nhãn tên kèm trạng thái cảm xúc cùng lúc.
2. Bật tùy chọn **Tự động lưu log (3s)** để hệ thống ghi lại lịch sử cảm xúc của bạn vào database sau mỗi 3 giây, hoặc nhấn nút **Chụp Snapshot** để ghi log thủ công kèm ảnh chụp cận cảnh khuôn mặt.

### Bước 4: Xem biểu đồ phân tích & Tải báo cáo PDF
1. Nhấp vào mục **Analytics Dashboard** trên thanh menu điều hướng.
2. Tại đây, bạn sẽ được cung cấp bức tranh toàn cảnh về sức khỏe tinh thần của mình thông qua:
   - Biểu đồ tròn thể hiện phân phối các cảm xúc.
   - Biểu đồ đường trực quan hóa biến đổi tâm trạng (Valence).
   - Bản đồ nhiệt Heatmap hiển thị thời điểm bạn vui tươi nhất.
   - Dự báo trạng thái tinh thần ngày mai.
   - Đề xuất cải thiện tâm lý thời gian thực từ AI.
3. Nhấp vào nút **Xuất Báo cáo PDF** để lưu trữ tài liệu báo cáo tiếng Việt chuyên nghiệp chứa toàn bộ thông số phân tích này về máy tính cá nhân.

---

## 👥 Tác giả & Giấy phép
* **Nhóm phát triển:** DeepAI Team
* **Mã nguồn mở:** Phát hành dưới giấy phép MIT License.
