document.addEventListener('DOMContentLoaded', () => {
    // Emojis mapping
    const EMOJIS = {
        'Neutral': '😐',
        'Happy': '😊',
        'Surprise': '😲',
        'Sad': '😢',
        'Angry': '😡',
        'Disgust': '🤢',
        'Fear': '😱',
        'Contempt': '😒'
    };

    // DOM Elements
    const video = document.getElementById('webcam-video');
    const canvas = document.getElementById('overlay-canvas');
    const ctx = canvas.getContext('2d');
    const cameraPlaceholder = document.getElementById('camera-placeholder');
    const btnStartCameraPlaceholder = document.getElementById('btn-start-camera-placeholder');
    const btnToggleCamera = document.getElementById('btn-toggle-camera');
    const btnSnapshot = document.getElementById('btn-snapshot');
    const btnRegisterFace = document.getElementById('btn-register-face');
    const toggleAutolog = document.getElementById('toggle-autolog');
    const userSelect = document.getElementById('user-select');
    const btnAddUser = document.getElementById('btn-add-user');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const sessionLogsBody = document.getElementById('session-logs-body');
    
    // Emotion Banner Elements
    const bannerEmoji = document.getElementById('banner-emoji');
    const bannerName = document.getElementById('banner-name');
    const identityBadge = document.getElementById('identity-badge');
    const identityName = document.getElementById('identity-name');

    // Modals
    const modalAddUser = document.getElementById('modal-add-user');
    const btnCloseAddModal = document.getElementById('btn-close-add-modal');
    const btnCancelAddUser = document.getElementById('btn-cancel-add-user');
    const btnSaveUser = document.getElementById('btn-save-user');
    const inputUserName = document.getElementById('input-user-name');

    const modalRegisterFace = document.getElementById('modal-register-face');
    const btnCloseRegModal = document.getElementById('btn-close-reg-modal');
    const btnCancelReg = document.getElementById('btn-cancel-reg');
    const btnStartReg = document.getElementById('btn-start-reg');
    const regProgressFill = document.getElementById('reg-progress-fill');
    const regStatus = document.getElementById('reg-status');
    const regInstruction = document.getElementById('reg-instruction');

    // State Variables
    let stream = null;
    let detectionInterval = null;
    let isCameraOn = false;
    let usersList = [];
    let lastLogTime = 0;
    const AUTOLOG_COOLDOWN = 3000; // 3 seconds
    let isRegistering = false;

    // Initialize Page
    loadUsers();

    // Event Listeners
    btnStartCameraPlaceholder.addEventListener('click', toggleCamera);
    btnToggleCamera.addEventListener('click', toggleCamera);
    btnSnapshot.addEventListener('click', triggerManualSnapshot);
    btnRegisterFace.addEventListener('click', openRegisterModal);
    
    // Add User Modal events
    btnAddUser.addEventListener('click', () => { modalAddUser.style.display = 'flex'; });
    btnCloseAddModal.addEventListener('click', closeAddModal);
    btnCancelAddUser.addEventListener('click', closeAddModal);
    btnSaveUser.addEventListener('click', saveNewUser);

    // Register Face Modal events
    btnCloseRegModal.addEventListener('click', closeRegModal);
    btnCancelReg.addEventListener('click', closeRegModal);
    btnStartReg.addEventListener('click', startFaceRegistration);

    // Enable/disable buttons based on selection
    userSelect.addEventListener('change', () => {
        const userId = userSelect.value;
        btnRegisterFace.disabled = !userId || !isCameraOn;
    });

    // Fetch and populate users
    async function loadUsers() {
        try {
            const response = await fetch('/api/users');
            const data = await response.json();
            if (data.success) {
                usersList = data.users;
                // Save selected value to restore it
                const selectedVal = userSelect.value;
                
                userSelect.innerHTML = '<option value="">-- Chọn User Profile --</option>';
                usersList.forEach(u => {
                    userSelect.innerHTML += `<option value="${u.UserID}">${u.FullName}</option>`;
                });
                
                if (selectedVal) userSelect.value = selectedVal;
            }
        } catch (e) {
            console.error("Error loading users:", e);
        }
    }

    // Toggle Camera On/Off
    async function toggleCamera() {
        if (isCameraOn) {
            stopCamera();
        } else {
            await startCamera();
        }
    }

    // Start Webcam
    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: "user" }
            });
            video.srcObject = stream;
            
            // Wait for video metadata to load to size the canvas overlay
            video.onloadedmetadata = () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            };

            cameraPlaceholder.classList.add('d-none');
            video.classList.remove('d-none');
            
            isCameraOn = true;
            btnToggleCamera.innerHTML = '<i class="fa-solid fa-power-off"></i> Tắt Camera';
            btnToggleCamera.classList.replace('btn-primary', 'btn-danger');
            btnSnapshot.disabled = false;
            
            const userId = userSelect.value;
            btnRegisterFace.disabled = !userId;

            // Status Indicator active
            statusDot.className = 'status-dot active';
            statusText.innerText = 'Camera Live';

            // Start processing loop (5 frames per second)
            detectionInterval = setInterval(processFrame, 200);
        } catch (err) {
            console.error("Error accessing webcam:", err);
            alert("Không thể truy cập camera. Vui lòng kiểm tra webcam và quyền truy cập camera của trình duyệt.");
        }
    }

    // Stop Webcam
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
        clearInterval(detectionInterval);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        cameraPlaceholder.classList.remove('d-none');
        video.classList.add('d-none');
        
        isCameraOn = false;
        btnToggleCamera.innerHTML = '<i class="fa-solid fa-video"></i> Bật Camera';
        btnToggleCamera.classList.replace('btn-danger', 'btn-primary');
        btnSnapshot.disabled = true;
        btnRegisterFace.disabled = true;

        // Status Indicator inactive
        statusDot.className = 'status-dot inactive';
        statusText.innerText = 'Camera Off';
    }

    // Capture current frame as base64 JPEG
    function captureFrame() {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 640;
        tempCanvas.height = 480;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Draw video frame mirrored to canvas
        tempCtx.translate(640, 0);
        tempCtx.scale(-1, 1);
        tempCtx.drawImage(video, 0, 0, 640, 480);
        
        return tempCanvas.toDataURL('image/jpeg', 0.85);
    }

    // Send frame to API for detection
    async function processFrame() {
        if (!isCameraOn || isRegistering) return;

        const base64Img = captureFrame();
        const activeUserId = userSelect.value || null;
        
        // Check auto-log condition
        let saveLog = false;
        const now = Date.now();
        if (toggleAutolog.checked && activeUserId && (now - lastLogTime >= AUTOLOG_COOLDOWN)) {
            saveLog = true;
            lastLogTime = now;
        }

        try {
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64Img,
                    user_id: activeUserId,
                    save_log: saveLog
                })
            });

            const data = await response.json();
            if (data.success) {
                drawBoundingBoxes(data.faces);
                if (data.faces.length > 0) {
                    // Update probability bars and banner with the first face
                    updateEmotionResults(data.faces[0]);
                    
                    // If a user was auto-identified, switch the dropdown if none active
                    const detectedUserId = data.faces[0].recognized_user_id;
                    if (detectedUserId && !userSelect.value) {
                        userSelect.value = detectedUserId;
                        btnRegisterFace.disabled = false;
                    }
                    
                    // If a log was saved, update session history
                    if (saveLog && data.faces[0].log_id) {
                        addSessionLogToTable(data.faces[0]);
                    }
                } else {
                    // Reset if no face detected
                    identityBadge.classList.add('d-none');
                }
            }
        } catch (e) {
            console.error("Error processing frame:", e);
        }
    }

    // Draw Face Bounding Boxes
    function drawBoundingBoxes(faces) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        faces.forEach(face => {
            const [x, y, w, h] = face.box;
            
            // Neon cyan borders for detections
            ctx.strokeStyle = '#06b6d4';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#06b6d4';
            
            ctx.strokeRect(x, y, w, h);
            
            // Reset shadows for text drawing
            ctx.shadowBlur = 0;
            
            // Label box
            let label = face.dominant_emotion;
            if (face.recognized_name) {
                label = `${face.recognized_name} (${face.dominant_emotion})`;
                // Change border color to green for identified users
                ctx.strokeStyle = '#10b981';
                ctx.shadowColor = '#10b981';
                ctx.shadowBlur = 10;
                ctx.strokeRect(x, y, w, h);
                ctx.shadowBlur = 0;
            }
            
            ctx.fillStyle = face.recognized_name ? 'rgba(16, 185, 129, 0.85)' : 'rgba(6, 182, 212, 0.85)';
            ctx.font = 'bold 15px Outfit';
            const textWidth = ctx.measureText(label).width;
            
            // Draw background label tag
            ctx.fillRect(x - 1, y - 28, textWidth + 16, 28);
            
            // Draw text
            ctx.fillStyle = '#ffffff';
            ctx.fillText(label, x + 8, y - 9);
        });
    }

    // Update real-time probability bars
    function updateEmotionResults(face) {
        const probs = face.emotions;
        const dominant = face.dominant_emotion;
        const confidence = face.dominant_confidence;
        
        // Update Banner
        bannerEmoji.innerText = EMOJIS[dominant] || '😐';
        bannerName.innerHTML = `${dominant} <span class="text-secondary fs-5">(${(confidence * 100).toFixed(1)}%)</span>`;
        
        // Update Identity
        if (face.recognized_name) {
            identityName.innerText = face.recognized_name;
            identityBadge.classList.remove('d-none');
        } else {
            identityBadge.classList.add('d-none');
        }

        // Update probability bars
        Object.keys(probs).forEach(emotion => {
            const bar = document.getElementById(`bar-${emotion}`);
            const valSpan = document.getElementById(`val-${emotion}`);
            if (bar && valSpan) {
                const percent = (probs[emotion] * 100).toFixed(0);
                bar.style.width = `${percent}%`;
                valSpan.innerText = `${percent}%`;
            }
        });
    }

    // Trigger Manual Snapshot
    async function triggerManualSnapshot() {
        if (!isCameraOn) return;
        
        const activeUserId = userSelect.value;
        if (!activeUserId) {
            alert("Vui lòng chọn hoặc thêm User Profile trước khi chụp snapshot.");
            return;
        }

        const base64Img = captureFrame();
        btnSnapshot.disabled = true;

        try {
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: base64Img,
                    user_id: activeUserId,
                    save_log: true
                })
            });

            const data = await response.json();
            if (data.success && data.faces.length > 0) {
                const face = data.faces[0];
                if (face.log_id) {
                    addSessionLogToTable(face);
                    alert(`Đã lưu Snapshot thành công cho cảm xúc ${face.dominant_emotion}!`);
                }
            } else {
                alert("Không phát hiện khuôn mặt nào trong ảnh chụp để lưu log.");
            }
        } catch (e) {
            console.error("Error saving manual snapshot:", e);
            alert("Lỗi khi lưu snapshot.");
        } finally {
            btnSnapshot.disabled = false;
        }
    }

    // Add captured snapshot record to HTML table
    function addSessionLogToTable(face) {
        // Clear placeholder if any
        if (sessionLogsBody.rows[0] && sessionLogsBody.rows[0].cells[0].colSpan > 1) {
            sessionLogsBody.innerHTML = '';
        }

        const row = sessionLogsBody.insertRow(0);
        const cellThumb = row.insertCell(0);
        const cellTime = row.insertCell(1);
        const cellEmotion = row.insertCell(2);
        const cellConf = row.insertCell(3);

        const imgPath = face.image_path || '/static/captured_images/placeholder.jpg';
        cellThumb.innerHTML = `<img src="/${imgPath}" class="log-face-thumb" alt="Face thumb">`;
        
        const nowStr = new Date().toLocaleTimeString('vi-VN');
        cellTime.innerText = nowStr;
        
        const colorVar = `var(--color-${face.dominant_emotion.toLowerCase()})`;
        cellEmotion.innerHTML = `
            <span class="log-emotion-tag" style="background-color: rgba(255,255,255,0.05); color: ${colorVar};">
                ${EMOJIS[face.dominant_emotion] || '😐'} ${face.dominant_emotion}
            </span>
        `;
        cellConf.innerText = `${(face.dominant_confidence * 100).toFixed(1)}%`;
    }

    // Close user creation modal
    function closeAddModal() {
        modalAddUser.style.display = 'none';
        inputUserName.value = '';
    }

    // Save New User Profile
    async function saveNewUser() {
        const name = inputUserName.value.trim();
        if (!name) {
            alert("Vui lòng nhập tên người dùng.");
            return;
        }

        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            const data = await response.json();
            if (data.success) {
                await loadUsers();
                userSelect.value = data.user_id;
                closeAddModal();
                alert(`Đã tạo hồ sơ cho người dùng "${name}" thành công!`);
                // Enable face registration button since user selected
                if (isCameraOn) btnRegisterFace.disabled = false;
            } else {
                alert("Lỗi: " + data.error);
            }
        } catch (e) {
            console.error("Error creating user:", e);
            alert("Lỗi mạng khi tạo user.");
        }
    }

    // Face Registration Modal controls
    function openRegisterModal() {
        if (!userSelect.value) return;
        modalRegisterFace.style.display = 'flex';
        regProgressFill.style.width = '0%';
        regStatus.innerText = 'Sẵn sàng thu thập: 0/15 ảnh';
        regInstruction.innerText = 'Hãy nhìn thẳng vào camera và nhấn nút bắt đầu.';
        btnStartReg.disabled = false;
    }

    function closeRegModal() {
        modalRegisterFace.style.display = 'none';
        isRegistering = false;
    }

    // Handle interactive face scanning loop
    async function startFaceRegistration() {
        const userId = userSelect.value;
        if (!userId) return;

        btnStartReg.disabled = true;
        isRegistering = true;
        
        let count = 0;
        const totalFrames = 15;
        
        const instructions = [
            "Hãy nhìn thẳng vào camera...",
            "Nghiêng mặt nhẹ sang bên trái...",
            "Nghiêng mặt nhẹ sang bên phải...",
            "Hơi cúi mặt xuống thấp một chút...",
            "Ngước mặt lên cao một chút...",
            "Mỉm cười nhẹ trước ống kính...",
            "Thực hiện biểu cảm ngạc nhiên...",
            "Giữ nguyên tư thế và nhìn thẳng..."
        ];

        // Run capturing loop every 600ms
        const regInterval = setInterval(async () => {
            if (count >= totalFrames || !isRegistering) {
                clearInterval(regInterval);
                if (count >= totalFrames) {
                    regStatus.innerText = "Hoàn thành 15/15 ảnh! Đang huấn luyện...";
                    regInstruction.innerText = "Hệ thống đang huấn luyện mô hình nhận dạng khuôn mặt. Vui lòng chờ...";
                    
                    // Give a brief delay for training completion
                    setTimeout(() => {
                        alert("Đăng ký nhận dạng khuôn mặt thành công! Hệ thống đã ghi nhớ cấu trúc mặt của bạn.");
                        closeRegModal();
                    }, 1200);
                }
                return;
            }

            // Select instruction based on count
            const instIdx = Math.min(Math.floor(count / 2), instructions.length - 1);
            regInstruction.innerText = instructions[instIdx];

            const base64Img = captureFrame();
            
            try {
                const response = await fetch('/api/register_face', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: base64Img,
                        user_id: userId,
                        frame_index: count
                    })
                });

                const data = await response.json();
                if (data.success) {
                    count++;
                    const percent = (count / totalFrames) * 100;
                    regProgressFill.style.width = `${percent}%`;
                    regStatus.innerText = `Đã thu thập: ${count}/${totalFrames} ảnh`;
                } else {
                    regInstruction.innerText = `Lỗi: ${data.error}. Thử lại khung hình này...`;
                }
            } catch (e) {
                console.error("Error capturing registration frame:", e);
                regInstruction.innerText = "Lỗi đường truyền. Đang thử lại...";
            }

        }, 700);
    }
});
