# Các thuật toán sử dụng trong dự án DeepAI Emotion System

Tài liệu này tổng hợp chi tiết các thuật toán, mô hình toán học và logic xử lý được sử dụng trong hệ thống nhận diện cảm xúc khuôn mặt và nhận dạng danh tính người dùng.

---

## 1. Phát hiện khuôn mặt (Face Detection)

*   **Thuật toán sử dụng**: **Haar Cascade Classifier (Bộ phân lớp thác Haar)**.
*   **Thư viện**: OpenCV (`cv2.CascadeClassifier`).
*   **Nguyên lý hoạt động**:
    1.  **Tính toán Ảnh tích lũy (Integral Image)**: Giúp tính toán nhanh tổng giá trị pixel trong các vùng hình chữ nhật để trích xuất các đặc trưng giống Haar (cạnh, đường, xung quanh tâm).
    2.  **Đặc trưng Haar (Haar-like Features)**: Đo sự chênh lệch độ sáng giữa các vùng kề nhau (ví dụ: vùng mắt thường tối hơn vùng má).
    3.  **Thuật toán AdaBoost**: Lựa chọn ra một số lượng nhỏ các đặc trưng Haar quan trọng nhất từ hàng chục nghìn đặc trưng ban đầu để tạo thành các bộ phân lớp yếu.
    4.  **Cấu trúc thác (Cascade of Classifiers)**: Kết hợp nhiều bộ phân lớp yếu lại thành một chuỗi. Khi quét một ảnh bằng sliding window (khung cửa sổ trượt), nếu một vùng ảnh không vượt qua bộ phân lớp ở mức đầu tiên (không có dấu hiệu của khuôn mặt), nó sẽ bị loại bỏ ngay lập tức. Chỉ các vùng đi qua tất cả các mức của thác mới được kết luận là khuôn mặt.
    5.  **Ứng dụng**: Xác định tọa độ khung chứa khuôn mặt (Bounding Box: $x, y, w, h$).

---

## 2. Nhận dạng danh tính khuôn mặt (Face Recognition)

Hệ thống sử dụng giải pháp kết hợp giữa trích xuất đặc trưng hình học cục bộ và bộ phân lớp học máy:

### A. Trích xuất đặc trưng (Feature Extraction - Face Embedding)
*   **Thuật toán**: **HOG (Histogram of Oriented Gradients - Biểu đồ định hướng Gradients)**.
*   **Thư viện**: Scikit-Image (`skimage.feature.hog`).
*   **Nguyên lý hoạt động**:
    1.  **Tính toán Gradient**: Tính toán độ thay đổi độ sáng (độ dốc gradient) theo trục X và Y tại mỗi pixel để tìm các đường biên và góc.
    2.  **Chia ô (Cells)**: Chia vùng ảnh khuôn mặt đã được chuẩn hóa ($64 \times 64$ pixel) thành các ô nhỏ (ví dụ: $8 \times 8$ pixel).
    3.  **Tích lũy biểu đồ**: Tại mỗi ô, tính toán một biểu đồ hướng gradient gồm 8 hướng (orientations) dựa trên độ lớn của gradient.
    4.  **Chuẩn hóa khối (Blocks)**: Gom các ô thành các khối lớn hơn (ví dụ: $2 \times 2$ ô) để thực hiện chuẩn hóa cường độ sáng cục bộ (L2-norm), giúp triệt tiêu ảnh hưởng của ánh sáng mạnh/yếu.
    5.  **Tạo Vector đặc trưng (Embedding)**: Ghép nối tất cả các biểu đồ đã chuẩn hóa thành một vector phẳng 1 chiều có kích thước $1568$ chiều. Vector này đại diện cho "dấu vân tay" hình học của khuôn mặt.

### B. Bộ phân lớp nhận diện (Classification)
*   **Thuật toán**: **Random Forest Classifier (Rừng ngẫu nhiên)**.
*   **Thư viện**: Scikit-Learn (`sklearn.ensemble.RandomForestClassifier`).
*   **Nguyên lý hoạt động**:
    1.  Huấn luyện trên các vector đặc trưng HOG của các khuôn mặt đã đăng ký và một lớp đặc biệt đại diện cho "Unknown" (tạo từ nhiễu gradient tự nhiên).
    2.  Tạo ra một tập hợp gồm 100 cây quyết định độc lập (Decision Trees). Mỗi cây quyết định được xây dựng trên một tập con ngẫu nhiên của tập dữ liệu huấn luyện (Bootstrapping) và lựa chọn ngẫu nhiên các đặc trưng tại mỗi nút phân tách.
    3.  Khi nhận diện, vector HOG của khuôn mặt mới được đưa qua 100 cây quyết định. Kết quả dự đoán danh tính người dùng và độ tin cậy được tính bằng tỷ lệ số cây bỏ phiếu nhiều nhất (`predict_proba`).

### C. Thuật toán so khớp dự phòng (Fallback - Cosine Similarity)
*   **Thuật toán**: **Độ tương đồng Cosine (Cosine Similarity)**.
*   **Nguyên lý hoạt động**: Khi hệ thống chưa được train mô hình Rừng ngẫu nhiên (chỉ có 1 user đăng ký), hệ thống sử dụng thuật toán Nearest Centroid dựa trên khoảng cách góc giữa các vector đặc trưng.
    *   Tính toán vector trung tâm (Centroid) $\vec{C}$ của các ảnh mẫu đã đăng ký của mỗi user.
    *   Tính toán độ tương đồng Cosine giữa vector khuôn mặt hiện tại $\vec{A}$ và vector trung tâm $\vec{C}$:
        $$\text{Similarity}(\vec{A}, \vec{C}) = \frac{\vec{A} \cdot \vec{C}}{\|\vec{A}\| \|\vec{C}\|}$$
    *   Người dùng có độ tương đồng lớn nhất và vượt qua ngưỡng xác định ($> 0.55$) sẽ được nhận diện.

---

## 3. Nhận dạng cảm xúc khuôn mặt (Facial Emotion Recognition)

*   **Thuật toán**: **Mạng thần kinh nhân tạo tích chập (Convolutional Neural Network - CNN)**.
*   **Bộ suy luận**: ONNX Runtime (`onnxruntime.InferenceSession`).
*   **Kiến trúc mạng**: Mô hình được huấn luyện trên tập dữ liệu **FERPlus** (nhận dạng 8 trạng thái cảm xúc: Neutral, Happy, Surprise, Sad, Angry, Disgust, Fear, Contempt).
    *   **Input**: Vùng khuôn mặt cắt ra, chuyển xám và resize về kích thước $64 \times 64 \times 1$.
    *   **Lớp tích chập (Convolutional Layers)**: Áp dụng các bộ lọc (kernels) trượt trên ảnh để phát hiện các đặc trưng không gian từ đơn giản (cạnh mắt, khóe môi) đến phức tạp (nếp nhăn trán, độ cong nụ cười).
    *   **Lớp gộp (Pooling Layers)**: Giảm kích thước bản đồ đặc trưng (downsampling), giữ lại thông tin quan trọng nhất và giảm số lượng tham số tính toán.
    *   **Lớp phẳng hóa & Lớp liên kết đầy đủ (Flatten & Fully Connected Layers)**: Chuyển các bản đồ đặc trưng thành một vector và phân lớp.
    *   **Lớp đầu ra (Softmax)**: Hàm kích hoạt Softmax được áp dụng ở lớp cuối cùng để chuyển đổi các điểm số thô (logits) $x_i$ thành xác suất phân phối $P_i$ có tổng bằng 1 đại diện cho 8 lớp cảm xúc:
        $$P_i = \text{Softmax}(x_i) = \frac{e^{x_i}}{\sum_{j=1}^{8} e^{x_j}}$$

---

## 4. Dự báo cảm xúc tương lai (Emotion Prediction)

*   **Thuật toán**: **Xích Markov bậc 1 (First-Order Markov Chain)**.
*   **Nguyên lý hoạt động**:
    1.  **Xác định trạng thái chủ đạo**: Hệ thống gộp dữ liệu log trong ngày và xác định cảm xúc có tần suất xuất hiện cao nhất đại diện cho cảm xúc của ngày đó. Tạo thành chuỗi thời gian các ngày liên tiếp: $S = [s_1, s_2, ..., s_t]$.
    2.  **Tính toán xác suất chuyển trạng thái**: Xích Markov giả định rằng trạng thái ngày mai $s_{t+1}$ chỉ phụ thuộc trực tiếp vào trạng thái ngày hôm nay $s_t$ (Tính chất vô hướng/Markov).
        $$P(X_{t+1} = j \mid X_t = i)$$
    3.  **Tạo ma trận chuyển dịch**: Hệ thống quét chuỗi lịch sử và đếm số lần chuyển dịch từ cảm xúc $i$ sang cảm xúc $j$. Từ đó tính toán ma trận xác suất chuyển trạng thái:
        $$P_{ij} = \frac{\text{Số lần chuyển từ } i \text{ sang } j}{\text{Tổng số lần ở trạng thái } i}$$
    4.  **Dự báo**: Dựa trên cảm xúc chủ đạo của ngày hôm nay ($s_t$), hệ thống tìm hàng tương ứng trong ma trận chuyển dịch và chọn cảm xúc có xác suất xảy ra cao nhất để dự đoán cho ngày mai ($s_{t+1}$).

---

## 5. Hệ thống gợi ý cải thiện tâm lý (Recommendation AI)

*   **Thuật toán**: **Hệ chuyên gia dựa trên luật (Rule-based Expert System)**.
*   **Nguyên lý hoạt động**:
    1.  **Phân tích ngữ cảnh**: Lấy dữ liệu cảm xúc của người dùng trong 24 giờ gần nhất (tối đa 20 bản ghi gần nhất).
    2.  **Tính toán chỉ số nhóm**:
        *   Tỷ lệ cảm xúc tích cực (Happy, Surprise).
        *   Tỷ lệ cảm xúc tiêu cực (Sad, Angry, Fear, Contempt, Disgust).
        *   Tỷ lệ cảm xúc bình thường (Neutral).
    3.  **Đánh giá điều kiện**:
        *   *Luật 1*: Nếu tỷ lệ cảm xúc tiêu cực $\ge 50\%$: Chuyển trạng thái tâm lý thành "Căng thẳng / Cảm xúc tiêu cực", kích hoạt tập luật đề xuất giảm stress (bài tập thở 4-4-4 nếu Angry, nghe nhạc Lofi/đi dạo nếu Sad, tập yoga nếu Fear).
        *   *Luật 2*: Nếu tỷ lệ cảm xúc tích cực $\ge 50\%$: Chuyển trạng thái thành "Tích cực / Hạnh phúc", đưa ra gợi ý phát huy năng lượng sáng tạo, lan tỏa niềm vui.
        *   *Luật 3*: Trường hợp còn lại: Trạng thái "Ổn định / Trung tính", đề xuất giãn cơ nhẹ nhàng, lập kế hoạch công việc và duy trì sức khỏe.

---

## 6. Bản đồ nhiệt khung giờ tích cực (Positive Hourly Heatmap)

*   **Thuật toán**: **Data Binning & Normalization (Gom nhóm dữ liệu và chuẩn hóa tuyến tính)**.
*   **Nguyên lý hoạt động**:
    1.  **Gom nhóm (Binning)**: Truy vấn cơ sở dữ liệu SQLite và phân nhóm toàn bộ các lượt nhận diện cảm xúc tích cực (Happy, Surprise) theo hai chiều thức: Ngày trong tuần (Thứ 2 đến Chủ nhật - 7 nhóm) và Khung giờ trong ngày (0h đến 23h - 24 nhóm). Tạo thành một lưới $7 \times 24$ ô chứa giá trị tần suất $C_{d, h}$.
    2.  **Chuẩn hóa tỷ lệ màu**: Tìm tần suất lớn nhất trên lưới $C_{\max} = \max(C_{d, h})$.
    3.  **Tỷ lệ phân cấp (Scaling)**: Tính tỷ lệ cho mỗi ô $R_{d, h} = \frac{C_{d, h}}{C_{\max}}$ và gán vào 5 mức độ hiển thị trên giao diện:
        *   Mức 0 ($R = 0$): Không sáng màu.
        *   Mức 1 ($0 < R < 0.25$): Xanh lục nhạt (Opacity 20%).
        *   Mức 2 ($0.25 \le R < 0.5$): Xanh lục trung bình (Opacity 40%).
        *   Mức 3 ($0.5 \le R < 0.75$): Xanh lục sáng (Opacity 70%).
        *   Mức 4 ($R \ge 0.75$): Xanh lục rực rỡ (Opacity 100%).

---

## 7. Ánh xạ hóa trị cảm xúc (Emotion Valence Mapping)

*   **Thuật toán**: **Mô hình cảm xúc chiều hướng (Dimensional Emotion Model — trục Valence)**.
*   **Vị trí**: `static/js/dashboard.js` (biểu đồ "Biến động Cảm xúc theo Thời gian").
*   **Nguyên lý hoạt động**:
    1.  Mỗi nhãn cảm xúc rời rạc được ánh xạ sang một giá trị vô hướng trên trục hóa trị (valence) trong khoảng $[-1.0, +1.0]$, thể hiện mức độ tích cực/tiêu cực:
        | Cảm xúc | Valence |
        |---|---|
        | Happy | $+1.0$ |
        | Surprise | $+0.6$ |
        | Neutral | $0.0$ |
        | Contempt | $-0.3$ |
        | Sad | $-0.6$ |
        | Fear | $-0.7$ |
        | Disgust | $-0.8$ |
        | Angry | $-1.0$ |
    2.  Chuỗi log cảm xúc theo thời gian được chuyển thành chuỗi số valence, sau đó vẽ thành biểu đồ đường (Line Chart) bằng Chart.js với nội suy đường cong Bézier (`tension = 0.3`) để làm mượt đường xu hướng "chỉ số tinh thần".

---

## 8. Sinh mẫu âm tính tổng hợp cho lớp "Unknown" (Synthetic Negative Sampling)

*   **Thuật toán**: **Sinh dữ liệu tổng hợp bằng nhiễu ngẫu nhiên + Lọc Gaussian (Gaussian Blur)**.
*   **Vị trí**: `face_recognizer.py` — hàm `train_face_recognizer()`.
*   **Nguyên lý hoạt động**:
    1.  Tạo các ảnh nhiễu ngẫu nhiên đồng nhất (uniform random) kích thước $64 \times 64$ với giá trị pixel $[0, 255]$.
    2.  Áp dụng **bộ lọc tích chập Gaussian** (kernel $5 \times 5$) để làm mờ nhiễu, mô phỏng cấu trúc gradient mềm giống bề mặt khuôn mặt thật thay vì nhiễu muối tiêu thuần túy.
    3.  Trích xuất HOG embedding của các ảnh này và gán nhãn $-1$ (Unknown). Số lượng mẫu âm tính: $\max(20, \frac{N}{2})$ với $N$ là tổng số mẫu khuôn mặt đã đăng ký.
    4.  **Mục đích**: Giúp Random Forest học được ranh giới quyết định giữa "người đã đăng ký" và "không xác định", giảm dương tính giả (false positive) khi người lạ đứng trước camera.

---

## 9. Dự báo dự phòng theo tần suất (Frequency-based Fallback Prediction)

*   **Thuật toán**: **Ước lượng theo phân phối tần suất — chọn Mode (giá trị xuất hiện nhiều nhất)**.
*   **Vị trí**: `prediction_engine.py` — hàm `predict_tomorrow_emotion()`.
*   **Nguyên lý hoạt động**: Đây là 2 nhánh dự phòng khi Xích Markov (Mục 4) không đủ dữ liệu:
    1.  *Trường hợp lịch sử < 2 ngày*: Đếm tần suất cảm xúc trên tối đa 50 log gần nhất (`collections.Counter`), chọn cảm xúc phổ biến nhất; độ tin cậy = tần suất tương đối của cảm xúc đó.
    2.  *Trường hợp cảm xúc hôm nay chưa từng có dữ liệu chuyển trạng thái*: Dự đoán chính cảm xúc hôm nay lặp lại vào ngày mai, với xác suất bằng tần suất xuất hiện của nó trong toàn bộ chuỗi lịch sử.

---

## 10. Truy vấn xếp hạng xác định cảm xúc chủ đạo theo ngày (SQL Window Ranking)

*   **Thuật toán**: **Hàm cửa sổ `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` (xếp hạng phân vùng)**.
*   **Vị trí**: `prediction_engine.py` — hàm `get_daily_dominant_emotions()` (truy vấn SQLite dùng CTE).
*   **Nguyên lý hoạt động**:
    1.  Gom nhóm log theo cặp (ngày, cảm xúc) và đếm tần suất (`GROUP BY`).
    2.  Với mỗi ngày (mỗi phân vùng `PARTITION BY log_date`), xếp hạng các cảm xúc theo tần suất giảm dần và chỉ giữ lại hàng có `rank = 1` — chính là cảm xúc chủ đạo của ngày đó.
    3.  Kết quả tạo thành chuỗi thời gian đầu vào cho Xích Markov ở Mục 4.

---

## 11. Các thuật toán tiền xử lý ảnh (Image Preprocessing)

Các phép biến đổi ảnh chuẩn được dùng xuyên suốt pipeline nhận diện:

*   **Chuyển ảnh xám (Grayscale Conversion)**: `cv2.cvtColor(BGR2GRAY)` — tổ hợp tuyến tính có trọng số theo độ nhạy sáng của mắt người: $Y = 0.299R + 0.587G + 0.114B$. Áp dụng cho mọi frame trước khi phát hiện khuôn mặt.
*   **Thu phóng ảnh bằng nội suy vùng (Area Interpolation Resize)**: `cv2.resize(..., INTER_AREA)` — lấy trung bình có trọng số các pixel trong vùng nguồn, cho chất lượng tốt nhất khi thu nhỏ ảnh (chuẩn hóa khuôn mặt về $64 \times 64$ cho cả HOG và CNN, $128 \times 128$ khi lưu ảnh đăng ký).
*   **Chuẩn hóa L2 toàn cục (Global L2 Normalization)**: Ngoài chuẩn hóa theo khối của HOG, toàn bộ vector embedding được chia cho chuẩn Euclid $\|\vec{v}\|_2$ để đưa về vector đơn vị — giúp phép so khớp Cosine (Mục 2C) tương đương với tích vô hướng đơn giản.
*   **Softmax ổn định số học (Numerically Stable Softmax)**: `model_helper.py` cài đặt Softmax dạng $\frac{e^{x_i - \max(x)}}{\sum_j e^{x_j - \max(x)}}$ (trừ giá trị lớn nhất trước khi lấy mũ) để tránh tràn số (overflow) khi logits lớn.
*   **Chọn khuôn mặt lớn nhất (Largest-Face Heuristic)**: Khi đăng ký khuôn mặt, nếu phát hiện nhiều khuôn mặt, hệ thống chọn khuôn mặt có diện tích khung $w \times h$ lớn nhất — giả định người đứng gần camera nhất là người đang đăng ký.

---

## 12. Công nghệ sử dụng trong dự án (Technology Stack)

### A. Backend
| Công nghệ | Vai trò |
|---|---|
| **Python 3** (chạy trong `.venv`) | Ngôn ngữ chính của toàn bộ backend |
| **Flask** | Web framework: REST API (`/api/detect`, `/api/users`, `/api/stats`, ...) và render giao diện qua Jinja2 template |
| **OpenCV** (`opencv-python`) | Giải mã ảnh, chuyển ảnh xám, resize, Gaussian Blur, Haar Cascade phát hiện khuôn mặt, lưu ảnh chụp |
| **NumPy** | Xử lý mảng/vector, tính toán đại số tuyến tính (norm, dot product, softmax) |
| **ONNX Runtime** (`onnxruntime`, CPUExecutionProvider) | Bộ suy luận chạy mô hình CNN nhận dạng cảm xúc `emotion-ferplus-8.onnx` (tự động tải từ Hugging Face / ONNX Model Zoo lần chạy đầu) |
| **Scikit-Learn** | Huấn luyện và dự đoán Random Forest Classifier cho nhận dạng danh tính |
| **Scikit-Image** | Trích xuất đặc trưng HOG (`skimage.feature.hog`) |
| **ReportLab** | Sinh báo cáo PDF (Platypus: Table, Paragraph); đăng ký font TTF hệ thống (Segoe UI / Arial) để hiển thị tiếng Việt Unicode |
| **Pickle** (thư viện chuẩn) | Lưu/nạp mô hình Random Forest đã huấn luyện (`models/face_recognizer.pkl`) |

### B. Lưu trữ dữ liệu
| Công nghệ | Vai trò |
|---|---|
| **SQLite** (`sqlite3`, file `database.db`) | CSDL quan hệ nhúng: 4 bảng `Users`, `EmotionLogs`, `Predictions`, `Reports`; dùng CTE, Window Function, `strftime` cho thống kê |
| **Hệ thống file** | Lưu ảnh khuôn mặt đăng ký (`static/faces/user_<id>/`), ảnh chụp cảm xúc (`static/captured_images/`), báo cáo PDF (`static/reports/`) |

### C. Frontend
| Công nghệ | Vai trò |
|---|---|
| **HTML5 + Jinja2** | Cấu trúc trang (`templates/index.html`, `templates/dashboard.html`) |
| **Bootstrap 5.3** (CDN) | Bố cục responsive, component giao diện |
| **Font Awesome** (CDN) | Bộ biểu tượng |
| **Chart.js** (CDN) | Vẽ biểu đồ Doughnut (phân bố cảm xúc) và Line Chart (xu hướng valence) |
| **JavaScript thuần (Vanilla JS)** | Toàn bộ logic client (`static/js/main.js`, `dashboard.js`), không dùng framework SPA |
| **WebRTC — `getUserMedia`** | Truy cập webcam trực tiếp trong trình duyệt |
| **Canvas API** | Chụp frame video, lật gương (mirror), vẽ khung nhận diện đè lên video (overlay) |
| **Base64 / JPEG** | Mã hóa frame ảnh (chất lượng 0.85) gửi lên server qua JSON, chu kỳ 200ms/frame |

### D. Vận hành
| Công nghệ | Vai trò |
|---|---|
| **Virtual Environment** (`.venv`) | Cô lập thư viện Python; `app.py` tự phát hiện và chạy lại bằng Python trong `.venv` nếu thiếu thư viện |
| **`run.bat`** | Script khởi chạy ứng dụng trên Windows |
| **Flask Dev Server** | Chạy tại `0.0.0.0:5000`, chế độ debug |

> *Ghi chú*: `pandas` có trong `requirements.txt` nhưng hiện không được sử dụng trong mã nguồn.
