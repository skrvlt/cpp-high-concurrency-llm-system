import unittest
from pathlib import Path

from docx import Document
from PIL import Image

from tools.doc_build_utils import render_markdownish_document
from tools.thesis_figure_builder import ensure_all_figures_generated


class ThesisFigureTests(unittest.TestCase):
    def test_render_document_inserts_picture_for_figure_caption(self):
        figure_dir = Path.cwd() / ".runtime_logs" / "test-figures"
        figure_dir.mkdir(parents=True, exist_ok=True)
        figure_path = figure_dir / "图3-1.png"
        Image.new("RGB", (40, 20), "white").save(figure_path)

        try:
            doc = Document()
            lines = [
                "## 第3章 系统需求分析",
                "图3-1 系统角色与核心用例图",
            ]

            render_markdownish_document(
                doc,
                lines,
                "测试文档",
                figures_dir=figure_dir,
            )

            self.assertEqual(len(doc.inline_shapes), 1)
            self.assertIn("图3-1 系统角色与核心用例图", [p.text for p in doc.paragraphs])
        finally:
            if figure_path.exists():
                figure_path.unlink()

    def test_figure_generator_outputs_required_assets(self):
        figure_dir = Path.cwd() / ".runtime_logs" / "generated-figures"
        figure_dir.mkdir(parents=True, exist_ok=True)
        ensure_all_figures_generated(figure_dir)
        expected = [
            "图3-1.png",
            "图3-2.png",
            "图3-3.png",
            "图4-1.png",
            "图4-2.png",
            "图4-3.png",
            "图4-4.png",
        ]
        missing = [name for name in expected if not (figure_dir / name).exists()]
        self.assertEqual(missing, [])
