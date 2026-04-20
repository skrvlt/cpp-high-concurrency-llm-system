import unittest
from pathlib import Path


class ProjectLayoutTests(unittest.TestCase):
    def test_core_project_files_exist(self):
        root = Path.cwd()
        required = [
            root / "README.md",
            root / "docs" / "architecture.md",
            root / "db" / "schema.sql",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"Missing core files: {missing}")
