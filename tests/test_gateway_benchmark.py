import importlib.util
import sys
import unittest
from pathlib import Path


def load_benchmark_module():
    script_path = Path.cwd() / "scripts" / "benchmark_gateway.py"
    spec = importlib.util.spec_from_file_location("benchmark_gateway", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GatewayBenchmarkTests(unittest.TestCase):
    def test_benchmark_script_exists_and_exposes_cli(self):
        script_path = Path.cwd() / "scripts" / "benchmark_gateway.py"
        self.assertTrue(script_path.exists(), "Missing scripts/benchmark_gateway.py")
        script = script_path.read_text(encoding="utf-8")
        self.assertIn("--base-url", script)
        self.assertIn("--requests", script)
        self.assertIn("--concurrency", script)
        self.assertIn("--scenario", script)
        self.assertIn("--output", script)

    def test_summary_metrics_include_latency_throughput_and_error_rate(self):
        benchmark = load_benchmark_module()
        results = [
            benchmark.RequestResult(True, 200, 0.10, ""),
            benchmark.RequestResult(True, 200, 0.20, ""),
            benchmark.RequestResult(False, 502, 0.30, "bad gateway"),
        ]

        summary = benchmark.summarize_results(results, total_elapsed=0.60)

        self.assertEqual(3, summary["total_requests"])
        self.assertEqual(2, summary["success_count"])
        self.assertAlmostEqual(66.67, summary["success_rate_percent"], places=2)
        self.assertAlmostEqual(0.20, summary["avg_latency_ms"], places=2)
        self.assertAlmostEqual(0.30, summary["p95_latency_ms"], places=2)
        self.assertAlmostEqual(5.00, summary["throughput_rps"], places=2)
        self.assertEqual("bad gateway", summary["errors"][0])

    def test_benchmark_docs_reference_script_and_metrics(self):
        test_plan = (Path.cwd() / "docs" / "test-plan.md").read_text(encoding="utf-8")
        validation = (Path.cwd() / "docs" / "gateway-validation.md").read_text(
            encoding="utf-8"
        )
        thesis = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(
            encoding="utf-8"
        )

        for text in [test_plan, validation, thesis]:
            self.assertIn("scripts/benchmark_gateway.py", text)
            self.assertIn("P95", text)
            self.assertIn("throughput_rps", text)
