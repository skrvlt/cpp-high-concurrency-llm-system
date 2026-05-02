import unittest
from pathlib import Path


class DefensePackageTests(unittest.TestCase):
    def test_defense_material_files_exist(self):
        root = Path.cwd()
        for path in [
            root / "docs" / "defense" / "demo-script.md",
            root / "docs" / "defense" / "qa-notes.md",
            root / "output" / "presentation" / "答辩PPT大纲.md",
        ]:
            with self.subTest(path=path):
                self.assertTrue(path.exists())

    def test_demo_script_covers_runnable_project_path(self):
        text = (Path.cwd() / "docs" / "defense" / "demo-script.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "python -m pip install -r requirements.txt",
            "scripts/start_api.ps1",
            "scripts/start_frontend.ps1",
            "http://127.0.0.1:8000/api/health",
            "?mode=gateway",
            "output/benchmark/gateway-chat.json",
        ]:
            self.assertIn(marker, text)

    def test_qa_notes_cover_core_defense_questions(self):
        text = (Path.cwd() / "docs" / "defense" / "qa-notes.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "为什么使用 C++ 网关",
            "为什么 Python 服务适合承载模型调用",
            "为什么 epoll 不承诺 Windows 原生运行",
            "SQLite 与 MySQL 的关系",
            "多模型调用不等于多 Agent",
        ]:
            self.assertIn(marker, text)

    def test_ppt_outline_contains_complete_defense_flow(self):
        text = (Path.cwd() / "output" / "presentation" / "答辩PPT大纲.md").read_text(
            encoding="utf-8"
        )
        for marker in [
            "研究背景",
            "需求分析",
            "系统架构",
            "关键实现",
            "测试结果",
            "创新点",
            "总结与展望",
        ]:
            self.assertIn(marker, text)
