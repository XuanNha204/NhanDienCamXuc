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

    // Emotion Valence mapping for Line Chart (-1.0 to +1.0)
    const EMOTION_VALENCE = {
        'Happy': 1.0,
        'Surprise': 0.6,
        'Neutral': 0.0,
        'Contempt': -0.3,
        'Sad': -0.6,
        'Fear': -0.7,
        'Disgust': -0.8,
        'Angry': -1.0
    };

    const EMOTION_COLORS = {
        'Happy': '#10b981',
        'Surprise': '#f59e0b',
        'Neutral': '#64748b',
        'Sad': '#3b82f6',
        'Angry': '#ef4444',
        'Disgust': '#84cc16',
        'Fear': '#8b5cf6',
        'Contempt': '#d946ef'
    };

    // DOM Elements
    const userSelect = document.getElementById('dashboard-user-select');
    const btnExportPdf = document.getElementById('btn-export-pdf');
    const noDataAlert = document.getElementById('no-data-alert');
    const dashboardContent = document.getElementById('dashboard-content');
    
    // Key Metrics
    const metricTotalLogs = document.getElementById('metric-total-logs');
    const metricDominantEmotion = document.getElementById('metric-dominant-emotion');
    const metricAvgConf = document.getElementById('metric-avg-conf');
    const metricPredictTomorrow = document.getElementById('metric-predict-tomorrow');

    // Recommendation Cards
    const recStatus = document.getElementById('rec-status');
    const recMessage = document.getElementById('rec-message');
    const recList = document.getElementById('rec-list');

    // Prediction Detail Card
    const predEmoji = document.getElementById('pred-emoji');
    const predTitle = document.getElementById('pred-title');
    const predDesc = document.getElementById('pred-desc');

    // Lists
    const galleryGrid = document.getElementById('gallery-grid');
    const reportsTableBody = document.getElementById('reports-table-body');
    const heatmapGrid = document.getElementById('heatmap-grid');

    // Chart variables
    let distChart = null;
    let trendChart = null;

    // Load users
    loadUsers();

    // Event listeners
    userSelect.addEventListener('change', () => {
        const userId = userSelect.value;
        btnExportPdf.disabled = !userId;
        if (userId) {
            fetchStats(userId);
        } else {
            noDataAlert.classList.remove('d-none');
            dashboardContent.classList.add('d-none');
        }
    });

    btnExportPdf.addEventListener('click', triggerPdfExport);

    async function loadUsers() {
        try {
            const response = await fetch('/api/users');
            const data = await response.json();
            if (data.success && data.users.length > 0) {
                userSelect.innerHTML = '<option value="">-- Chọn Người Dùng --</option>';
                data.users.forEach(u => {
                    userSelect.innerHTML += `<option value="${u.UserID}">${u.FullName}</option>`;
                });
                
                // Select first user by default
                userSelect.selectedIndex = 1;
                userSelect.dispatchEvent(new Event('change'));
            }
        } catch (e) {
            console.error("Error loading users:", e);
        }
    }

    async function fetchStats(userId) {
        try {
            const response = await fetch(`/api/stats/${userId}`);
            const data = await response.json();
            
            if (data.success && data.recent_logs.length > 0) {
                noDataAlert.classList.add('d-none');
                dashboardContent.classList.remove('d-none');
                
                renderMetrics(data);
                renderRecommendations(data.recommendation);
                renderPrediction(data.prediction);
                renderCharts(data);
                renderHeatmap(data.heatmap);
                renderGallery(data.recent_logs);
                renderReports(data.reports);
            } else {
                noDataAlert.classList.remove('d-none');
                dashboardContent.classList.add('d-none');
            }
        } catch (e) {
            console.error("Error fetching stats:", e);
        }
    }

    // Populate Key Metrics Cards
    function renderMetrics(data) {
        const logs = data.recent_logs;
        const rec = data.recommendation;
        const pred = data.prediction;
        
        metricTotalLogs.innerText = logs.length >= 10 ? `${logs.length}+` : logs.length;
        if (logs.length > 0) {
            // Count total in DB is actually in stats API, but we display the count from list or fallback
            metricTotalLogs.innerText = logs.length; 
        }
        
        metricDominantEmotion.innerText = `${EMOJIS[rec.dominant_emotion] || ''} ${rec.dominant_emotion}`;
        
        const avgConf = logs.reduce((acc, log) => acc + log.Confidence, 0) / logs.length;
        metricAvgConf.innerText = `${(avgConf * 100).toFixed(1)}%`;
        
        metricPredictTomorrow.innerText = `${EMOJIS[pred.emotion] || ''} ${pred.emotion}`;
    }

    // Populate Recommendation Cards
    function renderRecommendations(rec) {
        recStatus.innerText = `Trạng thái tinh thần: ${rec.status}`;
        recMessage.innerText = rec.message;
        
        // Color status border based on mood
        const box = document.querySelector('.rec-box');
        if (rec.neg_pct >= 0.5) {
            box.style.borderLeftColor = 'var(--color-angry)';
            box.style.background = 'rgba(239, 68, 68, 0.05)';
        } else if (rec.pos_pct >= 0.5) {
            box.style.borderLeftColor = 'var(--color-happy)';
            box.style.background = 'rgba(16, 185, 129, 0.05)';
        } else {
            box.style.borderLeftColor = 'var(--color-neutral)';
            box.style.background = 'rgba(100, 116, 139, 0.05)';
        }

        recList.innerHTML = '';
        rec.recommendations.forEach(r => {
            recList.innerHTML += `<li>${r}</li>`;
        });
    }

    // Populate Prediction Details
    function renderPrediction(pred) {
        predEmoji.innerText = EMOJIS[pred.emotion] || '😐';
        predTitle.innerText = pred.emotion;
        predDesc.innerText = `Xác suất xảy ra: ${(pred.confidence * 100).toFixed(1)}%`;
    }

    // Render Distribution & Trend Charts using Chart.js
    function renderCharts(data) {
        // 1. Emotion Distribution (Doughnut Chart)
        const distData = data.distribution;
        const labels = Object.keys(distData);
        const counts = Object.values(distData);
        const bgColors = labels.map(emotion => EMOTION_COLORS[emotion] || '#ffffff');

        if (distChart) distChart.destroy();
        const ctxDist = document.getElementById('distribution-chart').getContext('2d');
        distChart = new Chart(ctxDist, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: bgColors,
                    borderColor: 'rgba(9, 13, 22, 0.5)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', font: { family: 'Outfit' } }
                    }
                }
            }
        });

        // 2. Emotion Valence Trend (Line Chart)
        const logs = [...data.recent_logs].reverse(); // Sort chronological
        const timestamps = logs.map(log => {
            const date = new Date(log.CaptureTime);
            return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        });
        
        // Calculate valence values (-1.0 to 1.0) for trend
        const valenceData = logs.map(log => EMOTION_VALENCE[log.Emotion] || 0.0);
        const pointColors = logs.map(log => EMOTION_COLORS[log.Emotion] || '#ffffff');

        if (trendChart) trendChart.destroy();
        const ctxTrend = document.getElementById('timeline-chart').getContext('2d');
        trendChart = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Chỉ số tinh thần',
                    data: valenceData,
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    pointBackgroundColor: pointColors,
                    pointRadius: 5,
                    tension: 0.3,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                    },
                    y: {
                        min: -1.2,
                        max: 1.2,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'Outfit' },
                            callback: function(value) {
                                if (value === 1.0) return 'Tích cực (😊)';
                                if (value === 0.0) return 'Bình thường (😐)';
                                if (value === -1.0) return 'Tiêu cực (😡)';
                                return '';
                            }
                        }
                    }
                }
            }
        });
    }

    // Render Weekly / Hourly Heatmap grid
    function renderHeatmap(heatmapData) {
        const days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
        
        // Create 7x24 grid initialized with 0 counts
        const grid = Array.from({ length: 7 }, () => Array(24).fill(0));
        
        // Populate counts
        // Heatmap counts positive emotions (Happy, Surprise)
        heatmapData.forEach(item => {
            if (item.Emotion === 'Happy' || item.Emotion === 'Surprise') {
                grid[item.day_of_week][item.hour] += item.count;
            }
        });

        // Find max count to scale colors (min 1 to avoid divide by zero)
        const maxCount = Math.max(...grid.flat(), 1);

        heatmapGrid.innerHTML = '';
        
        // Generate grid headers for hours
        let hourHeadersHtml = '<div class="heatmap-row"><div class="heatmap-day-label"></div><div class="heatmap-cells">';
        for (let h = 0; h < 24; h += 2) {
            hourHeadersHtml += `<div class="text-secondary text-center" style="flex-grow: 2; font-size: 10px; min-width: 36px;">${h}h</div>`;
        }
        hourHeadersHtml += '</div></div>';
        heatmapGrid.innerHTML += hourHeadersHtml;

        // Generate rows
        for (let d = 0; d < 7; d++) {
            // Re-order days so Monday is first
            const dayIdx = (d + 1) % 7; // Monday = 1, Saturday = 6, Sunday = 0
            const dayName = days[dayIdx];
            
            let rowHtml = `<div class="heatmap-row"><div class="heatmap-day-label">${dayName}</div><div class="heatmap-cells">`;
            
            for (let h = 0; h < 24; h++) {
                const count = grid[dayIdx][h];
                let level = 0;
                if (count > 0) {
                    const ratio = count / maxCount;
                    if (ratio < 0.25) level = 1;
                    else if (ratio < 0.5) level = 2;
                    else if (ratio < 0.75) level = 3;
                    else level = 4;
                }
                
                rowHtml += `
                    <div class="heatmap-cell level-${level}" 
                         title="${dayName}, ${h}h: ${count} lượt tích cực"
                         data-count="${count}">
                    </div>`;
            }
            rowHtml += '</div></div>';
            heatmapGrid.innerHTML += rowHtml;
        }
    }

    // Populate Snapshots gallery
    function renderGallery(logs) {
        galleryGrid.innerHTML = '';
        const logsWithImage = logs.filter(l => l.ImagePath);
        
        if (logsWithImage.length === 0) {
            galleryGrid.innerHTML = '<div class="text-secondary text-center py-4 w-100">Chưa có ảnh chụp lưu trữ</div>';
            return;
        }
        
        // Display latest 12 snapshots
        logsWithImage.slice(0, 12).forEach(log => {
            const time = new Date(log.CaptureTime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
            galleryGrid.innerHTML += `
                <div class="gallery-item" title="Độ tin cậy: ${(log.Confidence*100).toFixed(0)}%">
                    <img src="/${log.ImagePath}" alt="Face crop">
                    <span class="gallery-tag" style="color: ${EMOTION_COLORS[log.Emotion]}">${EMOJIS[log.Emotion]} ${log.Emotion} (${time})</span>
                </div>
            `;
        });
    }

    // Populate PDF reports history table
    function renderReports(reports) {
        reportsTableBody.innerHTML = '';
        if (reports.length === 0) {
            reportsTableBody.innerHTML = '<tr><td colspan="3" class="text-center text-secondary py-4">Chưa xuất báo cáo nào</td></tr>';
            return;
        }

        reports.forEach(r => {
            const filename = r.PdfPath.split('/').pop();
            const dateStr = new Date(r.CreatedAt).toLocaleString('vi-VN');
            reportsTableBody.innerHTML += `
                <tr>
                    <td class="text-info">${filename}</td>
                    <td>${dateStr}</td>
                    <td>
                        <a href="${r.PdfPath}" target="_blank" class="btn btn-sm btn-secondary py-1 px-2">
                            <i class="fa-solid fa-download"></i> Tải về
                        </a>
                    </td>
                </tr>
            `;
        });
    }

    // Export PDF Trigger API
    async function triggerPdfExport() {
        const userId = userSelect.value;
        if (!userId) return;

        btnExportPdf.disabled = true;
        const originalText = btnExportPdf.innerHTML;
        btnExportPdf.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xuất...';

        try {
            const response = await fetch(`/api/export_pdf/${userId}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                alert("Đã xuất báo cáo PDF thành công!");
                // Open PDF in a new tab
                window.open(data.pdf_url, '_blank');
                // Re-fetch stats to update reports list
                fetchStats(userId);
            } else {
                alert("Lỗi xuất báo cáo: " + data.error);
            }
        } catch (e) {
            console.error("Error exporting PDF:", e);
            alert("Lỗi mạng khi xuất báo cáo.");
        } finally {
            btnExportPdf.disabled = false;
            btnExportPdf.innerHTML = originalText;
        }
    }
});
