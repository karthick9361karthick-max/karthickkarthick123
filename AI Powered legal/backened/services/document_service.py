import io
import html
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from fpdf import FPDF


def sanitize_text(text: str) -> str:

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return (
        text
        .replace("\x00", "")
        .strip()
    )


def format_html_preview(text: str) -> str:

    safe = html.escape(
        sanitize_text(text)
    )

    return safe.replace(
        "\n",
        "<br>",
    )


def _is_heading(line: str) -> bool:

    stripped = line.strip()

    if not stripped:
        return False

    if re.match(
        r"^\d+[\.\)]\s+[A-Z][A-Z0-9 &/'()-]+$",
        stripped,
    ):
        return True

    if (
        stripped.isupper()
        and len(stripped) <= 100
    ):
        return True

    return False


def format_docx(
    text: str,
    doc_type: str = "Legal Document",
) -> bytes:

    doc = Document()

    section = doc.sections[0]

    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal = doc.styles["Normal"]

    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)

    title = doc.add_paragraph()

    title.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    run = title.add_run(
        doc_type.upper()
    )

    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    subtitle = doc.add_paragraph()

    subtitle.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    subrun = subtitle.add_run(
        "LegalEase Draft"
    )

    subrun.italic = True
    subrun.font.name = "Times New Roman"
    subrun.font.size = Pt(10)

    for raw_line in (
        sanitize_text(text).splitlines()
    ):

        line = raw_line.strip()

        if not line:

            doc.add_paragraph()
            continue

        if _is_heading(line):

            p = doc.add_paragraph()

            p.paragraph_format.space_before = (
                Pt(10)
            )

            p.paragraph_format.space_after = (
                Pt(4)
            )

            r = p.add_run(line)

            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)

            continue

        p = doc.add_paragraph()

        p.paragraph_format.space_after = (
            Pt(5)
        )

        p.paragraph_format.line_spacing = 1.15

        r = p.add_run(line)

        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

    footer = section.footer.paragraphs[0]

    footer.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    footer_run = footer.add_run(
        "LegalEase - AI-assisted draft. "
        "Review before execution."
    )

    footer_run.font.size = Pt(8)

    buffer = io.BytesIO()

    doc.save(buffer)

    return buffer.getvalue()


class LegalEasePDF(FPDF):

    def __init__(self, doc_type):

        super().__init__()

        self.doc_type = doc_type

        self.set_auto_page_break(
            auto=True,
            margin=18,
        )

    def header(self):

        self.set_font(
            "Helvetica",
            "B",
            12,
        )

        self.cell(
            0,
            8,
            self.doc_type.upper(),
            align="C",
        )

        self.ln(9)

    def footer(self):

        self.set_y(-14)

        self.set_font(
            "Helvetica",
            size=8,
        )

        self.cell(
            0,
            8,
            (
                f"LegalEase - AI-assisted draft | "
                f"Page {self.page_no()}"
            ),
            align="C",
        )


def format_pdf(
    text: str,
    doc_type: str = "Legal Document",
) -> bytes:

    pdf = LegalEasePDF(doc_type)

    pdf.set_title(doc_type)

    pdf.add_page()

    for raw_line in (
        sanitize_text(text).splitlines()
    ):

        line = raw_line.strip()

        if not line:

            pdf.ln(3)

            continue

        if _is_heading(line):

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.multi_cell(
                0,
                6,
                line,
            )

            pdf.ln(1)

        else:

            pdf.set_font(
                "Helvetica",
                size=10,
            )

            pdf.multi_cell(
                0,
                5.5,
                line,
            )

            pdf.ln(1)

    output = pdf.output(
        dest="S"
    )

    if isinstance(output, str):

        return output.encode(
            "latin-1"
        )

    return bytes(output)