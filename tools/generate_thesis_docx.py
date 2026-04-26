from pathlib import Path

from docx import Document

from doc_build_utils import render_markdownish_document
from thesis_figure_builder import ensure_all_figures_generated


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "doc" / "毕业设计说明书初稿.md"
OUTPUT = ROOT / "output" / "doc" / "毕业设计说明书初稿.docx"
FIGURES_DIR = ROOT / "output" / "figures"


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
