# Graduation Project Module Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the graduation project moving through independent, testable modules without losing direction.

**Architecture:** The project is split into frontend, Python service, persistence, C++ gateway, validation, thesis, and defense-delivery modules. Each module must produce a runnable or reviewable artifact, update its matching documentation/thesis section, pass verification, and be committed on its own branch.

**Tech Stack:** HTML/CSS/JavaScript, Python FastAPI, SQLite, C++17 epoll gateway, shell/PowerShell scripts, unittest, Markdown/DOCX thesis materials.

---

## Operating Rules

- Each module gets its own branch named `codex/<module-purpose>`.
- Each task starts by checking this roadmap, current git branch, current status, and the latest test result.
- Each task ends by updating this roadmap or the relevant module plan with: completed work, remaining work, next recommended task, verification command, commit hash, and branch name.
- Do not mix unrelated module work in one commit.
- For code changes, write or update tests first where practical, then implement, verify, commit, and push.
- For document-only changes, verify by reading the changed file and, when applicable, regenerating DOCX output.

## Module Status

| Module | Purpose | Status | Evidence | Next Action |
| --- | --- | --- | --- | --- |
| M1 Foundation Runtime | Cross-platform scripts, dependency setup, environment variables, health checks | Mostly done | `README.md`, `.env.example`, `requirements.txt`, `docs/runbook.md` | Keep updated when runtime contracts change |
| M2 Python AI Service | Login, chat, history, logs, config, overview, model fallback | Mostly done | `services/ai_service/app`, `tests/python` | Add stronger admin/session APIs only if needed by frontend or thesis |
| M3 Persistence | Memory repository, SQLite runtime persistence, MySQL thesis schema | Mostly done | `SQLiteRepository`, `APP_STORAGE=sqlite`, `db/schema.sql` | Add screenshots or DB verification material for thesis if needed |
| M4 C++ Gateway | Linux/WSL epoll gateway, forwarding, error behavior, compile/run validation | Partly done | `cpp_gateway`, gateway scripts, validation docs | Strengthen gateway code and WSL/Linux evidence |
| M5 Frontend Demo | User page, admin page, mode switching, polished defense demo | Partly done | `frontend/index.html`, `frontend/admin.html`, contract tests | Improve visual/demo quality and status visibility |
| M6 Testing And Benchmark | Unit tests, API tests, layout tests, runtime checks, gateway benchmark | Partly done | `tests/`, `scripts/benchmark_gateway.py` | Run real WSL/Linux benchmark and store summarized results |
| M7 Thesis And Figures | Full thesis, diagrams, tables, screenshots, experiment sections | Partly done | `output/doc`, `docs/figures-guide.md` | Finish final-version figures, screenshots, and Chapter 4-6 polish |
| M8 Defense Package | PPT, demo script, Q&A notes, explanation checklist | Not started | No dedicated deck/script yet | Create defense outline after code/demo path stabilizes |

## Recommended Module Order

1. M4 C++ Gateway Strengthening
2. M5 Frontend Demo Polish
3. M6 Real Benchmark Evidence
4. M7 Thesis Finalization
5. M8 Defense Package

## M4 C++ Gateway Strengthening Tasks

**Files:**
- Modify: `cpp_gateway/src/http_server.cpp`
- Modify: `cpp_gateway/include/http_server.h`
- Modify: `cpp_gateway/README.md`
- Modify: `docs/gateway-validation.md`
- Test: `tests/test_cpp_gateway_layout.py`

- [ ] **M4-1 Review current gateway implementation**

  Read `cpp_gateway/src/http_server.cpp`, `cpp_gateway/include/http_server.h`, `cpp_gateway/src/main.cpp`, and `cpp_gateway/include/thread_pool.h`.

  Record the gateway behavior in the task notes:

  ```text
  listener port:
  upstream host:
  upstream port:
  epoll usage:
  thread pool usage:
  upstream failure behavior:
  documented validation command:
  ```

- [ ] **M4-2 Add or verify upstream failure contract**

  Desired behavior: when Python service is unavailable, gateway returns an HTTP response whose status line or body clearly indicates `502 Bad Gateway`.

  Add or update a structure/documentation test in `tests/test_cpp_gateway_layout.py`:

  ```python
  def test_cpp_gateway_documents_bad_gateway_behavior(self):
      validation = (Path.cwd() / "docs" / "gateway-validation.md").read_text(encoding="utf-8")
      self.assertIn("502 Bad Gateway", validation)
      self.assertIn("UPSTREAM_HOST", validation)
      self.assertIn("UPSTREAM_PORT", validation)
  ```

  Run:

  ```powershell
  python -m unittest tests.test_cpp_gateway_layout -v
  ```

- [ ] **M4-3 Verify gateway compile path**

  Use WSL/Linux command when available:

  ```bash
  bash scripts/build_gateway_wsl.sh
  ```

  Expected: CMake/g++ build succeeds and produces `cpp_gateway/build/llm_gateway`.

- [ ] **M4-4 Verify gateway runtime path**

  Start Python API, then start gateway:

  ```bash
  bash scripts/start_api.sh
  bash scripts/start_gateway_wsl.sh
  bash scripts/verify_runtime.sh gateway
  bash scripts/verify_gateway_smoke.sh
  ```

  Expected: `/api/health`, `/api/login`, `/api/chat`, and `/api/history` work through port `8080`.

- [ ] **M4-5 Update thesis support**

  Update `output/doc/毕业设计说明书初稿.md` Chapter 5 gateway implementation section with actual gateway validation results and command names. Regenerate DOCX:

  ```powershell
  & 'C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_thesis_docx.py
  ```

- [ ] **M4-6 Commit and push**

  Verification:

  ```powershell
  python -m unittest discover -s tests -v
  python -m compileall services tests scripts
  ```

  Commit:

  ```bash
  git add -A
  git commit -m "feat: strengthen gateway validation support"
  git push -u origin codex/gateway-validation-hardening
  ```

## M5 Frontend Demo Polish Tasks

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/admin.html`
- Modify: `frontend/app.js`
- Modify: `frontend/admin.js`
- Modify: `frontend/styles.css`
- Test: `tests/test_frontend_contract.py`

- [ ] **M5-1 Add visible runtime mode**

  Show current API mode and base URL in the user and admin pages.

- [ ] **M5-2 Add health/status panel**

  Display `/api/health` fields: `runtime_mode`, `storage_mode`, `model_name`, `session_count`.

- [ ] **M5-3 Improve admin overview presentation**

  Make user count, session count, message count, log count, and model name obvious for defense demonstration.

- [ ] **M5-4 Preserve direct/gateway mode switching**

  Ensure `?mode=gateway` still routes frontend requests through port `8080`.

- [ ] **M5-5 Verify frontend contract**

  Run:

  ```powershell
  python -m unittest tests.test_frontend_contract -v
  python -m unittest discover -s tests -v
  ```

## M6 Real Benchmark Evidence Tasks

**Files:**
- Use: `scripts/benchmark_gateway.py`
- Modify: `docs/test-plan.md`
- Modify: `docs/gateway-validation.md`
- Modify: `output/doc/毕业设计说明书初稿.md`
- Create: `output/benchmark/*.json` only if the file is intentionally kept as experiment evidence

- [ ] **M6-1 Run health benchmark through gateway**

  ```bash
  python scripts/benchmark_gateway.py --base-url http://127.0.0.1:8080 --scenario health --requests 1000 --concurrency 100 --output output/benchmark/gateway-health.json
  ```

- [ ] **M6-2 Run chat benchmark through gateway**

  ```bash
  python scripts/benchmark_gateway.py --base-url http://127.0.0.1:8080 --scenario chat --requests 300 --concurrency 30 --output output/benchmark/gateway-chat.json
  ```

- [ ] **M6-3 Convert JSON results into thesis table values**

  Extract `avg_latency_ms`, `p95_latency_ms`, `throughput_rps`, `success_rate_percent`, and `error_count`.

- [ ] **M6-4 Update Chapter 6**

  Replace example-only language with actual measured environment, commands, and results.

## M7 Thesis Finalization Tasks

**Files:**
- Modify: `output/doc/毕业设计说明书初稿.md`
- Modify: `output/doc/毕业设计说明书初稿.docx`
- Possibly modify: `tools/generate_thesis_docx.py`
- Possibly modify: figure assets under `output/doc/figures/`

- [ ] **M7-1 Remove remaining draft wording**

  Search for `建议`, `后续`, `正式定稿`, `补充`, `示例` in thesis body and replace with final-delivery wording where appropriate.

- [ ] **M7-2 Finish Chapter 4 figures**

  Ensure architecture diagram, flow diagram, sequence diagram, and E-R diagram are referenced consistently.

- [ ] **M7-3 Finish Chapter 5 implementation explanation**

  Tie frontend, Python service, repository, C++ gateway, and benchmark script to actual code paths.

- [ ] **M7-4 Finish Chapter 6 test evidence**

  Add measured environment, test commands, benchmark results, screenshots placeholders, and result analysis.

- [ ] **M7-5 Regenerate and inspect DOCX**

  Use bundled document Python:

  ```powershell
  & 'C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_thesis_docx.py
  ```

## M8 Defense Package Tasks

**Files:**
- Create: `docs/defense/demo-script.md`
- Create: `docs/defense/qa-notes.md`
- Optionally create: `output/presentation/答辩PPT大纲.md`

- [ ] **M8-1 Write five-minute demo script**

  Include startup commands, login flow, chat flow, admin overview, gateway mode, and benchmark evidence.

- [ ] **M8-2 Write likely Q&A**

  Cover why C++ gateway, why Python service, why epoll is Linux/WSL-only, how persistence works, how tests prove correctness, and what limitations remain.

- [ ] **M8-3 Create PPT outline**

  Recommended structure: background, requirements, architecture, implementation, test results, innovation points, summary.

## End-Of-Task Review Template

After every task, update this section in the next commit or in the module-specific plan.

```text
Date:
Branch:
Commit:
Completed:
Verification:
Remaining:
Next recommended task:
Risk or blocker:
```

## Current Snapshot

Date: 2026-04-28
Branch: `codex/project-module-roadmap`
Completed:
- M1 foundation runtime mostly completed.
- M2 Python service first version completed.
- M3 SQLite persistence support completed in `ad87350`.
- M6 benchmark script support completed in `4a6bb87`.
Remaining:
- M4 gateway hardening and real WSL/Linux evidence.
- M5 frontend defense polish.
- M6 actual benchmark result capture.
- M7 final thesis polish and DOCX review.
- M8 defense package.
Next recommended task:
- Start M4-1 gateway implementation review, then create branch `codex/gateway-validation-hardening`.
Risk or blocker:
- WSL/Linux validation depends on local WSL availability and network/port state.
