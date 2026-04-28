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
            root / "scripts" / "start_gateway_wsl.sh",
            root / "scripts" / "verify_runtime.ps1",
            root / "scripts" / "verify_runtime.sh",
            root / "scripts" / "verify_gateway_smoke.ps1",
            root / "scripts" / "verify_gateway_smoke.sh",
        ]
        missing = [str(p) for p in required if not p.exists()]
        self.assertFalse(missing, f"Missing cross-platform files: {missing}")

    def test_python_runtime_requirements_are_declared(self):
        requirements_path = Path.cwd() / "requirements.txt"
        self.assertTrue(requirements_path.exists(), "Missing requirements.txt")
        requirements = requirements_path.read_text(encoding="utf-8").lower()
        for package in ["fastapi", "uvicorn", "httpx", "pydantic"]:
            self.assertIn(package, requirements)

    def test_windows_scripts_do_not_use_local_python_absolute_path(self):
        root = Path.cwd()
        for script_name in ["start_api.ps1", "start_frontend.ps1"]:
            script = (root / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertNotIn("codex-runtimes", script)
            self.assertNotIn("C:\\Users\\kidosto", script)
            self.assertIn("$env:PYTHON", script)
