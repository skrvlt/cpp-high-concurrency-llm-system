from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class RequestResult:
    ok: bool
    status_code: int
    latency_ms: float
    error: str


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * ratio + 0.999999) - 1))
    return ordered[index]


def summarize_results(
    results: list[RequestResult], total_elapsed: float, concurrency: int | None = None
) -> dict[str, Any]:
    latencies = [result.latency_ms for result in results]
    success_count = sum(1 for result in results if result.ok)
    total_requests = len(results)
    error_count = total_requests - success_count
    throughput = total_requests / total_elapsed if total_elapsed > 0 else 0.0
    summary = {
        "total_requests": total_requests,
        "concurrency": concurrency,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate_percent": round(success_count / total_requests * 100, 2)
        if total_requests
        else 0.0,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
        "p95_latency_ms": round(percentile(latencies, 0.95), 2),
        "max_latency_ms": round(max(latencies), 2) if latencies else 0.0,
        "throughput_rps": round(throughput, 2),
        "errors": [result.error for result in results if result.error][:5],
    }
    return summary


def request_json(
    method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 10.0
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else {}


def run_one_health(base_url: str, timeout: float) -> RequestResult:
    return timed_request("GET", f"{base_url}/api/health", None, timeout)


def run_one_chat(base_url: str, token: str, timeout: float, index: int) -> RequestResult:
    return timed_request(
        "POST",
        f"{base_url}/api/chat",
        {"token": token, "message": f"网关压测请求 {index}"},
        timeout,
    )


def timed_request(
    method: str, url: str, payload: dict[str, Any] | None, timeout: float
) -> RequestResult:
    started = time.perf_counter()
    try:
        status, _ = request_json(method, url, payload, timeout)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestResult(200 <= status < 400, status, elapsed_ms, "")
    except HTTPError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestResult(False, exc.code, elapsed_ms, str(exc))
    except (URLError, TimeoutError, OSError) as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestResult(False, 0, elapsed_ms, str(exc))


def login_for_token(base_url: str, username: str, password: str, timeout: float) -> str:
    status, body = request_json(
        "POST",
        f"{base_url}/api/login",
        {"username": username, "password": password},
        timeout,
    )
    if status != 200 or "token" not in body:
        raise RuntimeError(f"login failed with status {status}: {body}")
    return str(body["token"])


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    base_url = args.base_url.rstrip("/")
    token = None
    if args.scenario == "chat":
        token = login_for_token(base_url, args.username, args.password, args.timeout)

    started = time.perf_counter()
    results: list[RequestResult] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = []
        for index in range(args.requests):
            if args.scenario == "health":
                futures.append(executor.submit(run_one_health, base_url, args.timeout))
            else:
                futures.append(
                    executor.submit(run_one_chat, base_url, token, args.timeout, index + 1)
                )
        for future in as_completed(futures):
            results.append(future.result())

    total_elapsed = time.perf_counter() - started
    summary = summarize_results(results, total_elapsed, args.concurrency)
    summary.update(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "base_url": base_url,
            "scenario": args.scenario,
        }
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark the C++ gateway or Python API HTTP endpoints."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--scenario", choices=["health", "chat"], default="health")
    parser.add_argument("--username", default="student")
    parser.add_argument("--password", default="student123")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", help="Optional JSON result file path.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.requests <= 0:
        parser.error("--requests must be greater than 0")
    if args.concurrency <= 0:
        parser.error("--concurrency must be greater than 0")

    summary = run_benchmark(args)
    output = json.dumps(summary, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    return 0 if summary["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
