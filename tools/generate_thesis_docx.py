from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "doc" / "毕业设计说明书初稿.md"
OUTPUT = ROOT / "output" / "doc" / "毕业设计说明书初稿.docx"

FIGURE_ASSETS = {
    "图3-1 系统用例图": "output/doc/figures/figure-3-1-use-case.png",
    "图4-1 系统总体结构图": "output/doc/figures/figure-4-1-architecture.png",
    "图4-2 智能问答处理流程图": "output/doc/figures/figure-4-2-chat-flow.png",
    "图4-3 问答处理时序图": "output/doc/figures/figure-4-3-sequence.png",
    "图4-4 系统 E-R 图": "output/doc/figures/figure-4-4-er.png",
}


def clean_inline_markdown(text):
    return text.replace("**", "").replace("`", "")


def split_markdown_table_row(text):
    return [cell.strip() for cell in text.strip().strip("|").split("|")]


def is_markdown_separator_row(text):
    if not text.startswith("|") or not text.endswith("|"):
        return False
    cells = split_markdown_table_row(text)
    return bool(cells) and all(set(cell.replace(":", "").strip()) <= {"-"} for cell in cells)


def is_markdown_table_row(text):
    return (
        text.startswith("|")
        and text.endswith("|")
        and "|" in text.strip().strip("|")
        and not is_markdown_separator_row(text)
    )


def set_run_font(run, size=12, bold=False):
    from docx.oxml.ns import qn
    from docx.shared import Pt

    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def add_paragraph(doc, text, style="body"):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

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
        run = p.add_run(clean_inline_markdown(text))
        set_run_font(run, size=12, bold=False)
    return p


def add_table(doc, rows):
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.shared import Pt

    if not rows:
        return
    column_count = max(len(row) for row in rows)
    table = doc.add_table(rows=len(rows), cols=column_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    for row_index, row in enumerate(rows):
        for column_index in range(column_count):
            cell = table.cell(row_index, column_index)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            text = row[column_index] if column_index < len(row) else ""
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.line_spacing = 1.25
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)
            run = paragraph.add_run(clean_inline_markdown(text))
            set_run_font(run, size=10.5, bold=(row_index == 0))


def add_figure(doc, figure_path):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches

    path = ROOT / figure_path
    if not path.exists():
        return
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(str(path), width=Inches(5.8))


def build_doc():
    from docx import Document

    doc = Document()
    add_paragraph(doc, "本科毕业设计说明书（论文）初稿", "title")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        if not line:
            doc.add_paragraph()
            index += 1
            continue
        if (
            is_markdown_table_row(line)
            and index + 1 < len(lines)
            and is_markdown_separator_row(lines[index + 1].strip())
        ):
            table_rows = [split_markdown_table_row(line)]
            index += 2
            while index < len(lines) and is_markdown_table_row(lines[index].strip()):
                table_rows.append(split_markdown_table_row(lines[index].strip()))
                index += 1
            add_table(doc, table_rows)
            continue
        if line.startswith("# "):
            add_paragraph(doc, line[2:].strip(), "title")
        elif line.startswith("## "):
            add_paragraph(doc, line[3:].strip(), "h1")
        elif line.startswith("### "):
            add_paragraph(doc, line[4:].strip(), "h2")
        elif line.startswith("#### "):
            add_paragraph(doc, line[5:].strip(), "h3")
        elif line in FIGURE_ASSETS:
            add_figure(doc, FIGURE_ASSETS[line])
            add_paragraph(doc, line, "body")
        else:
            add_paragraph(doc, line, "body")
        index += 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT))


if __name__ == "__main__":
    build_doc()
