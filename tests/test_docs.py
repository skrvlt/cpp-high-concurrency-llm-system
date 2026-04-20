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
