import os
from datetime import datetime
import database
import recommendation_engine
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "reports")
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# Register Vietnamese fonts from Windows System
FONT_NAME = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

# Try to register Unicode Segoe UI or Arial from Windows System fonts
try:
    font_path_regular = "C:\\Windows\\Fonts\\segoeui.ttf"
    font_path_bold = "C:\\Windows\\Fonts\\segoeuib.ttf"
    if os.path.exists(font_path_regular) and os.path.exists(font_path_bold):
        pdfmetrics.registerFont(TTFont('SegoeUI', font_path_regular))
        pdfmetrics.registerFont(TTFont('SegoeUI-Bold', font_path_bold))
        FONT_NAME = 'SegoeUI'
        FONT_BOLD = 'SegoeUI-Bold'
except Exception as e:
    print("Could not load SegoeUI font, trying Arial...", e)
    try:
        font_path_regular = "C:\\Windows\\Fonts\\arial.ttf"
        font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"
        if os.path.exists(font_path_regular) and os.path.exists(font_path_bold):
            pdfmetrics.registerFont(TTFont('Arial', font_path_regular))
            pdfmetrics.registerFont(TTFont('Arial-Bold', font_path_bold))
            FONT_NAME = 'Arial'
            FONT_BOLD = 'Arial-Bold'
    except Exception as ae:
        print("Could not load Arial font, falling back to Helvetica.", ae)

def generate_pdf_report(user_id, start_date=None, end_date=None):
    """
    Generates a beautiful, detailed PDF emotion report for the selected user.
    """
    user = database.get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
        
    # Default range: last 30 days
    if not start_date or not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
    logs = database.get_logs_in_range(user_id, start_date, end_date)
    rec = recommendation_engine.get_recommendation(user_id)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"report_{user_id}_{timestamp}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    # 1. Setup Document
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Define Custom Styles to support registered font and look premium
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'), # Dark slate
        alignment=1, # Center
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#3B82F6'), # Neon Blue
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155') # Gray 700
    )
    
    body_bold_style = ParagraphStyle(
        'DocBodyBold',
        parent=body_style,
        fontName=FONT_BOLD
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B')
    )
    
    story = []
    
    # Title Block
    story.append(Paragraph("BÁO CÁO PHÂN TÍCH CẢM XÚC THÔNG MINH", title_style))
    story.append(Spacer(1, 10))
    
    # User Profile Info Table
    info_data = [
        [
            Paragraph("<b>Người dùng:</b>", body_style), Paragraph(user['FullName'], body_style),
            Paragraph("<b>Ngày lập báo cáo:</b>", body_style), Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), body_style)
        ],
        [
            Paragraph("<b>Từ ngày:</b>", body_style), Paragraph(datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y"), body_style),
            Paragraph("<b>Đến ngày:</b>", body_style), Paragraph(datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y"), body_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[80, 180, 120, 150])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    story.append(Table([[colors.HexColor('#E2E8F0')]], colWidths=[530], rowHeights=[1])) # Divider
    story.append(Spacer(1, 15))
    
    # 2. Key Metrics Summary
    story.append(Paragraph("1. Tóm tắt các chỉ số chính", h1_style))
    
    total_logs = len(logs)
    dominant_emotion = rec['dominant_emotion']
    avg_confidence = np.mean([log['Confidence'] for log in logs]) * 100 if logs else 0.0
    
    # Group logs by positivity
    positive_emotions = {'Happy', 'Surprise'}
    negative_emotions = {'Sad', 'Angry', 'Fear', 'Contempt', 'Disgust'}
    pos_count = sum(1 for log in logs if log['Emotion'] in positive_emotions)
    neg_count = sum(1 for log in logs if log['Emotion'] in negative_emotions)
    
    pos_pct = (pos_count / total_logs) * 100 if total_logs > 0 else 0
    neg_pct = (neg_count / total_logs) * 100 if total_logs > 0 else 0
    neutral_pct = 100 - pos_pct - neg_pct if total_logs > 0 else 0
    
    metrics_data = [
        [
            Paragraph("<b>Tổng số lượt phân tích:</b>", body_style), Paragraph(str(total_logs), body_bold_style),
            Paragraph("<b>Cảm xúc chủ đạo:</b>", body_style), Paragraph(f"{dominant_emotion} ({rec['score']*100:.1f}%)", body_bold_style)
        ],
        [
            Paragraph("<b>Độ tin cậy trung bình:</b>", body_style), Paragraph(f"{avg_confidence:.1f}%", body_style),
            Paragraph("<b>Tỉ lệ Tích cực / Tiêu cực:</b>", body_style), Paragraph(f"{pos_pct:.1f}% / {neg_pct:.1f}%", body_style)
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[150, 110, 150, 120])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # 3. Recommendations Card
    story.append(Paragraph("2. Đánh giá sức khỏe tinh thần & Đề xuất từ AI", h1_style))
    
    rec_box_data = [
        [Paragraph(f"<b>Trạng thái tâm lý: {rec['status']}</b>", card_title_style)],
        [Paragraph(rec['message'], body_style)],
        [Paragraph("<b>Các lời khuyên cải thiện tinh thần đề xuất:</b>", body_bold_style)]
    ]
    for r in rec['recommendations']:
        rec_box_data.append([Paragraph(f"• {r}", body_style)])
        
    rec_table = Table(rec_box_data, colWidths=[530])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')), # Light blue card
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -2), 6),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 15))
    
    # 4. Logs History Table
    story.append(Paragraph("3. Nhật ký cảm xúc gần đây", h1_style))
    
    table_headers = [
        Paragraph("<b>STT</b>", body_bold_style),
        Paragraph("<b>Thời gian ghi nhận</b>", body_bold_style),
        Paragraph("<b>Cảm xúc nhận diện</b>", body_bold_style),
        Paragraph("<b>Độ tin cậy</b>", body_bold_style)
    ]
    
    table_rows = [table_headers]
    display_logs = logs[-15:] # Show latest 15 logs in the PDF
    
    for idx, log in enumerate(display_logs):
        dt = datetime.strptime(log['CaptureTime'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        table_rows.append([
            Paragraph(str(idx + 1), body_style),
            Paragraph(dt, body_style),
            Paragraph(log['Emotion'], body_style),
            Paragraph(f"{log['Confidence']*100:.1f}%", body_style)
        ])
        
    logs_table = Table(table_rows, colWidths=[40, 190, 180, 120])
    logs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(logs_table)
    
    if len(logs) > 15:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<i>* Báo cáo chỉ hiển thị tối đa 15 dòng nhật ký gần nhất. Tổng số bản ghi trong khoảng này: {total_logs}.</i>", body_style))
        
    # Build Document
    doc.build(story)
    
    # Save Report details to DB
    relative_path = f"static/reports/{pdf_filename}"
    database.save_report(user_id, relative_path)
    
    return relative_path

if __name__ == "__main__":
    # Test stub
    print("Report generator loaded.")
