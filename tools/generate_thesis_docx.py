from pathlib import Path

from docx import Document

try:
    from .doc_build_utils import clean_inline_markdown, render_markdownish_document
    from .thesis_figure_builder import ensure_all_figures_generated
except ImportError:
    from doc_build_utils import clean_inline_markdown, render_markdownish_document
    from thesis_figure_builder import ensure_all_figures_generated


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "doc" / "毕业设计说明书初稿.md"
OUTPUT = ROOT / "output" / "doc" / "毕业设计说明书初稿.docx"
FIGURES_DIR = ROOT / "output" / "figures"

FIGURE_ASSETS = {
    "图3-1 系统用例图": "output/doc/figures/figure-3-1-use-case.png",
    "图4-1 系统总体结构图": "output/doc/figures/figure-4-1-architecture.png",
    "图4-2 智能问答处理流程图": "output/doc/figures/figure-4-2-chat-flow.png",
    "图4-3 问答处理时序图": "output/doc/figures/figure-4-3-sequence.png",
    "图4-4 系统 E-R 图": "output/doc/figures/figure-4-4-er.png",
}


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


def build_doc():
    doc = Document()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    ensure_all_figures_generated(FIGURES_DIR)
    render_markdownish_document(
        doc,
        lines,
        "本科毕业设计说明书（论文）初稿",
        figures_dir=FIGURES_DIR,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT))


if __name__ == "__main__":
    build_doc()
