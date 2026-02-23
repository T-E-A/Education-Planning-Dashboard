from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generate_report(chat_history_json, reportName: str):
    try:
        # print(chat_history_json)
        chat_history = chat_history_json

        doc = SimpleDocTemplate(reportName)
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.blue,
            spaceAfter=6
        )

        response_style = ParagraphStyle(
            'ResponseStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12
        )

        timestamp_style = ParagraphStyle(
            'TimestampStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            spaceAfter=4
        )

        for entry in chat_history:

            timestamp = entry.get("timestamp", "")
            question = entry.get("user_input", "")
            response = entry.get("assistant_response", "")

            # Timestamp
            elements.append(Paragraph(f"<b>Timestamp:</b> {timestamp}", timestamp_style))
            elements.append(Spacer(1, 0.1 * inch))

            # Question
            elements.append(Paragraph(f"<b>Question:</b> {question}", question_style))
            elements.append(Spacer(1, 0.1 * inch))

            # Response
            elements.append(Paragraph(f"<b>Response:</b><br/>{response.replace(chr(10), '<br/>')}", response_style))
            elements.append(Spacer(1, 0.3 * inch))

            # Divider line
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
            elements.append(Spacer(1, 0.3 * inch))

        doc.build(elements)

        return reportName

    except Exception as e:
        print(f"Error in generate_report => {e}")
        return None