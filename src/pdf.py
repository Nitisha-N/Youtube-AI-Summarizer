import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT


def make_pdf(markdown_text: str, output_path: str) -> None:
    """
    Render a Markdown string to a formatted PDF.
    Handles H1, H2, H3 headings, bullet lists, and bold/italic inline text.
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

    h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=22, leading=28, spaceAfter=14, spaceBefore=6,
        textColor=colors.HexColor("#111111"), fontName="Helvetica-Bold",
    )
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=15, leading=20, spaceAfter=8, spaceBefore=18,
        textColor=colors.HexColor("#222222"), fontName="Helvetica-Bold",
    )
    h3 = ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontSize=12, leading=16, spaceAfter=6, spaceBefore=12,
        textColor=colors.HexColor("#333333"), fontName="Helvetica-BoldOblique",
    )
    body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, leading=17, spaceAfter=8,
        fontName="Times-Roman", textColor=colors.HexColor("#1a1a1a"),
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=body,
        leftIndent=18, firstLineIndent=0, spaceAfter=4,
    )

    def inline(text: str) -> str:
        text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
        return text

    story = []
    lines = markdown_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), h1))
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=colors.HexColor("#dddddd"), spaceAfter=8))

        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), h2))

        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), h3))

        elif line.startswith("- ") or line.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(ListItem(
                    Paragraph(f"- {inline(lines[i][2:].strip())}", bullet_style),
                    leftIndent=20,
                ))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet",
                                      leftIndent=12, spaceBefore=4, spaceAfter=4))
            continue

        elif line in ("", "---"):
            story.append(Spacer(1, 8))

        else:
            cleaned = inline(line)
            if cleaned:
                story.append(Paragraph(cleaned, body))

        i += 1

    doc.build(story)
