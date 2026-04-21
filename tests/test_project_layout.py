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

    def test_cross_platform_docs_and_scripts_exist(self):
        root = Path.cwd()
        required = [
            root / "docs" / "platform-support.md",
            root / "docs" / "gateway-validation.md",
            root / ".env.example",
            root / "scripts" / "start_api.ps1",
            root / "scripts" / "start_frontend.ps1",
            root / "scripts" / "start_api.sh",
            root / "scripts" / "start_frontend.sh",
            root / "scripts" / "build_gateway_wsl.sh",
            root / "scripts" / "verify_runtime.ps1",
            root / "scripts" / "verify_runtime.sh",
            root / "scripts" / "verify_gateway_smoke.ps1",
            root / "scripts" / "verify_gateway_smoke.sh",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"Missing cross-platform files: {missing}")
