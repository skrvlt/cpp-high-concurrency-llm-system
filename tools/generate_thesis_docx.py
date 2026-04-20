from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "doc" / "毕业设计说明书初稿.md"
OUTPUT = ROOT / "output" / "doc" / "毕业设计说明书初稿.docx"


def set_run_font(run, size=12, bold=False):
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def add_paragraph(doc, text, style="body"):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(24) if style == "body" else Pt(0)
    p.paragraph_format.line_spacing = 1.5
    if style == "title":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_run_font(run, size=16, bold=True)
    elif style == "h1":
        run = p.add_run(text)
        set_run_font(run, size=14, bold=True)
    elif style == "h2":
        run = p.add_run(text)
        set_run_font(run, size=12, bold=True)
    elif style == "h3":
        run = p.add_run(text)
        set_run_font(run, size=12, bold=True)
    else:
        run = p.add_run(text)
        set_run_font(run, size=12, bold=False)
    return p


def build_doc():
    doc = Document()
    add_paragraph(doc, "本科毕业设计说明书（论文）初稿", "title")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for raw in lines:
        line = raw.strip()
        if not line:
            doc.add_paragraph()
            continue
        if line.startswith("# "):
            add_paragraph(doc, line[2:].strip(), "title")
        elif line.startswith("## "):
            add_paragraph(doc, line[3:].strip(), "h1")
        elif line.startswith("### "):
            add_paragraph(doc, line[4:].strip(), "h2")
        elif line.startswith("#### "):
            add_paragraph(doc, line[5:].strip(), "h3")
        elif line.startswith("|") and line.endswith("|"):
            # Markdown tables remain as plain text in the initial draft.
            add_paragraph(doc, line, "body")
        else:
            add_paragraph(doc, line, "body")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT))


if __name__ == "__main__":
    build_doc()
