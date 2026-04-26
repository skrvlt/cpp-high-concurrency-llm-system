import unittest
from pathlib import Path
import zipfile
from docx import Document


class DocsTests(unittest.TestCase):
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
            "附录B 后续补充材料说明",
        ]:
            self.assertIn(marker, text)

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

    def test_docs_mention_wsl_build_fallback(self):
        readme = (Path.cwd() / "cpp_gateway" / "README.md").read_text(encoding="utf-8")
        runbook = (Path.cwd() / "docs" / "runbook.md").read_text(encoding="utf-8")
        validation = (Path.cwd() / "docs" / "gateway-validation.md").read_text(
            encoding="utf-8"
        )
        for text in [readme, runbook, validation]:
            self.assertIn("cmake", text)
            self.assertIn("g++", text)
            self.assertIn("validate_gateway_wsl.sh", text)
            self.assertIn("API_MODE", text)

    def test_use_case_tables_are_separated_by_body_text(self):
        lines = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        ).splitlines()
        table_indices = [
            index
            for index, line in enumerate(lines)
            if line.strip() in {
                "表3-2 用户登录用例描述",
                "表3-3 智能问答用例描述",
                "表3-4 管理员配置维护用例描述",
            }
        ]
        self.assertEqual(len(table_indices), 3)

        for left, right in zip(table_indices, table_indices[1:]):
            between = [
                line.strip()
                for line in lines[left + 1 : right]
                if line.strip()
                and line.strip() not in {"[用例表]", "[/用例表]"}
                and not line.strip().startswith("用例")
                and not line.strip().startswith("主参与者")
                and not line.strip().startswith("前置条件")
                and not line.strip().startswith("后置条件")
                and not line.strip().startswith("基本事件流")
                and not line.strip().startswith("异常事件流")
                and not line.strip()[0:2].isdigit()
            ]
            self.assertTrue(
                between,
                "相邻用例描述表之间缺少说明正文",
            )

    def test_generated_doc_use_case_tables_remove_outer_borders(self):
        docx_path = Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.docx"
        with zipfile.ZipFile(docx_path) as zf:
            xml = zf.read("word/document.xml").decode("utf-8")
        self.assertIn('w:left w:val="nil"', xml)
        self.assertIn('w:right w:val="nil"', xml)
        self.assertIn('w:start w:val="nil"', xml)
        self.assertIn('w:end w:val="nil"', xml)
        self.assertIn('w:val="single"', xml)

    def test_generated_doc_use_case_tables_keep_inner_vertical_lines(self):
        docx_path = Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.docx"
        doc = Document(docx_path)
        table_xml = doc.tables[1]._tbl.xml
        self.assertIn('<w:right w:val="single"', table_xml)
        self.assertIn('<w:left w:val="single"', table_xml)
        self.assertIn('<w:left w:val="nil"', table_xml)
        self.assertIn('<w:right w:val="nil"', table_xml)
