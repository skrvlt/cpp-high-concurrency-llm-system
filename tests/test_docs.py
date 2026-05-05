import unittest
from pathlib import Path

from tools.generate_thesis_docx import (
    FIGURE_ASSETS,
    clean_inline_markdown,
    is_markdown_table_row,
    split_markdown_table_row,
)


class DocsTests(unittest.TestCase):
    def test_thesis_docx_generator_removes_inline_markdown_marks(self):
        text = clean_inline_markdown("**关键词：** `C++` 与 `FastAPI`")

        self.assertEqual("关键词： C++ 与 FastAPI", text)

    def test_thesis_contains_required_sections(self):
        text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for section in [
            "摘要",
            "第1章 绪论",
            "第3章 系统需求分析",
            "第4章 系统总体设计",
            "第5章 系统详细实现",
            "第6章 系统测试与结果分析",
            "结论",
        ]:
            self.assertIn(section, text)

    def test_thesis_mentions_core_figures_and_tables(self):
        text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "图4-1 系统总体结构图",
            "图4-2 智能问答处理流程图",
            "表4-1 用户表结构",
            "表4-2 会话表结构",
            "表6-4 并发性能测试结果表",
        ]:
            self.assertIn(marker, text)

    def test_thesis_mentions_sequence_and_er_guidance(self):
        text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "问答处理时序图",
            "系统 E-R 图",
            "附录B 运行与测试材料索引",
        ]:
            self.assertIn(marker, text)

    def test_thesis_api_appendix_matches_actual_chat_endpoint(self):
        text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("POST /api/chat", text)
        self.assertNotIn("POST /api/ask", text)

    def test_thesis_removes_finalization_placeholders(self):
        text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "正式定稿时",
            "建议将该图",
            "后续补充材料说明",
            "截图位",
            "TODO",
            "占位",
        ]:
            self.assertNotIn(marker, text)

    def test_docx_generator_parses_markdown_table_rows(self):
        self.assertTrue(is_markdown_table_row("| 字段 | 类型 | 备注 |"))
        self.assertFalse(is_markdown_table_row("| --- | --- | --- |"))
        self.assertEqual(
            ["字段", "类型", "备注"],
            split_markdown_table_row("| 字段 | 类型 | 备注 |"),
        )

    def test_thesis_core_figure_assets_exist(self):
        root = Path.cwd()
        for caption in [
            "图3-1 系统用例图",
            "图4-1 系统总体结构图",
            "图4-2 智能问答处理流程图",
            "图4-3 问答处理时序图",
            "图4-4 系统 E-R 图",
        ]:
            with self.subTest(caption=caption):
                self.assertIn(caption, FIGURE_ASSETS)
                self.assertTrue((root / FIGURE_ASSETS[caption]).exists())

    def test_docs_mention_windows_linux_wsl_support(self):
        runbook = (Path.cwd() / "docs" / "runbook.md").read_text(encoding="utf-8")
        platform_doc = (Path.cwd() / "docs" / "platform-support.md").read_text(
            encoding="utf-8"
        )
        thesis = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for text in [runbook, platform_doc, thesis]:
            self.assertIn("Windows", text)
            self.assertIn("Linux", text)
            self.assertIn("WSL", text)

    def test_docs_mention_health_contract_and_env_examples(self):
        readme = (Path.cwd() / "README.md").read_text(encoding="utf-8")
        runbook = (Path.cwd() / "docs" / "runbook.md").read_text(encoding="utf-8")
        platform_doc = (Path.cwd() / "docs" / "platform-support.md").read_text(
            encoding="utf-8"
        )
        thesis = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )
        for text in [readme, runbook, platform_doc, thesis]:
            self.assertIn("/api/health", text)
        for text in [readme, runbook, platform_doc]:
            self.assertIn(".env.example", text)

    def test_docs_mention_requirements_and_storage_mode(self):
        readme = (Path.cwd() / "README.md").read_text(encoding="utf-8")
        runbook = (Path.cwd() / "docs" / "runbook.md").read_text(encoding="utf-8")
        test_plan = (Path.cwd() / "docs" / "test-plan.md").read_text(encoding="utf-8")
        for text in [readme, runbook]:
            self.assertIn("requirements.txt", text)
            self.assertIn("python -m pip install -r requirements.txt", text)
        for text in [readme, runbook, test_plan]:
            self.assertIn("storage_mode", text)
            self.assertIn("APP_STORAGE=sqlite", text)
