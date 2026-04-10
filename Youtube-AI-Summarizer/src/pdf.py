import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def make_pdf(markdown_text: str, output_path: str) -> None:
    """
    Convert Markdown text to a well-formatted PDF.
    Handles headings (H1, H2, H3), paragraphs, bullet lists, and bold text.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.1 * inch,
        rightMargin=1.1 * inch,
        topMargin=1.1 * inch,
        bottomMargin=1.1 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    style_h1 = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=22, leading=28, spaceAfter=14, spaceBefore=6,
        textColor=colors.HexColor('#111111'), fontName='Helvetica-Bold'
    )
    style_h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=15, leading=20, spaceAfter=8, spaceBefore=18,
        textColor=colors.HexColor('#222222'), fontName='Helvetica-Bold',
        borderPadding=(0, 0, 4, 0)
    )
    style_h3 = ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=12, leading=16, spaceAfter=6, spaceBefore=12,
        textColor=colors.HexColor('#333333'), fontName='Helvetica-BoldOblique'
    )
    style_body = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=11, leading=17, spaceAfter=8,
        fontName='Times-Roman', textColor=colors.HexColor('#1a1a1a')
    )
    style_bullet = ParagraphStyle(
        'Bullet', parent=style_body,
        leftIndent=18, firstLineIndent=0, spaceAfter=4
    )

    story = []

    def clean_inline(text: str) -> str:
        """Convert markdown inline bold/italic to ReportLab tags."""
        # Bold-italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        return text

    lines = markdown_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith('# '):
            story.append(Paragraph(clean_inline(line[2:]), style_h1))
            story.append(HRFlowable(width='100%', thickness=1.5,
                                     color=colors.HexColor('#dddddd'), spaceAfter=8))

        elif line.startswith('## '):
            story.append(Paragraph(clean_inline(line[3:]), style_h2))

        elif line.startswith('### '):
            story.append(Paragraph(clean_inline(line[4:]), style_h3))

        elif line.startswith('- ') or line.startswith('* '):
            bullet_items = []
            while i < len(lines) and (lines[i].startswith('- ') or lines[i].startswith('* ')):
                item_text = clean_inline(lines[i][2:].strip())
                bullet_items.append(ListItem(
                    Paragraph(f"• {item_text}", style_bullet),
                    leftIndent=20
                ))
                i += 1
            story.append(ListFlowable(bullet_items, bulletType='bullet',
                                       leftIndent=12, spaceBefore=4, spaceAfter=4))
            continue  # don't increment i again

        elif line == '' or line == '---':
            story.append(Spacer(1, 8))

        else:
            cleaned = clean_inline(line)
            if cleaned:
                story.append(Paragraph(cleaned, style_body))

        i += 1

    doc.build(story)
