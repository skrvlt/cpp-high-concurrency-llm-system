import unittest
from pathlib import Path


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
