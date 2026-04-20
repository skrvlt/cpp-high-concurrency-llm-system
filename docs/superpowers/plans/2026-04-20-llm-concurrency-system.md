# LLM Concurrency System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first complete version of a graduation-project-grade interactive system with a Web frontend, a Linux C++ high-concurrency gateway, a Python FastAPI AI service, MySQL schema, tests, and thesis/project documentation.

**Architecture:** The system uses a browser frontend for user interaction, a Linux C++ gateway for HTTP access, epoll-based event handling and request forwarding, and a Python FastAPI service for authentication, chat, session history, logs, and model invocation. Data persistence is represented with a MySQL schema and a repository layer that defaults to in-memory mode for local development.

**Tech Stack:** HTML/CSS/JavaScript, C++17, Linux sockets/epoll/threading, Python 3, FastAPI, pytest, MySQL SQL schema, Markdown documentation

---

### Task 1: Create repository structure and baseline docs

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `db/schema.sql`
- Create: `project-overview.md`

- [ ] **Step 1: Write the failing documentation completeness test**

```python
from pathlib import Path

def test_core_project_files_exist():
    root = Path.cwd()
    required = [
        root / "README.md",
        root / "docs" / "architecture.md",
        root / "db" / "schema.sql",
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Missing core files: {missing}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_project_layout.py -v`
Expected: FAIL with missing file assertions

- [ ] **Step 3: Write minimal implementation**

Create the required files with project scope, architecture summary, and baseline schema header.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_project_layout.py -v`
Expected: PASS

### Task 2: Build and test the Python service domain layer

**Files:**
- Create: `services/ai_service/app/models.py`
- Create: `services/ai_service/app/repository.py`
- Create: `services/ai_service/app/service.py`
- Create: `tests/python/test_service.py`

- [ ] **Step 1: Write the failing test**

```python
from services.ai_service.app.service import AppService

def test_login_and_chat_flow():
    service = AppService()
    token = service.login("admin", "admin123")
    assert token
    reply = service.chat(token, "测试问题")
    assert "测试问题" in reply.answer
    history = service.history(token)
    assert len(history) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_service.py::test_login_and_chat_flow -v`
Expected: FAIL with import or attribute errors because service layer does not exist yet

- [ ] **Step 3: Write minimal implementation**

Create an in-memory repository, token store, session/message models, and a deterministic fallback model client.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_service.py::test_login_and_chat_flow -v`
Expected: PASS

### Task 3: Add FastAPI endpoints with test coverage

**Files:**
- Create: `services/ai_service/app/main.py`
- Create: `services/ai_service/app/api.py`
- Create: `tests/python/test_api.py`

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.ai_service.app.main import app

client = TestClient(app)

def test_http_login_and_chat():
    login = client.post("/api/login", json={"username": "admin", "password": "admin123"})
    assert login.status_code == 200
    token = login.json()["token"]
    chat = client.post("/api/chat", json={"token": token, "message": "你好"})
    assert chat.status_code == 200
    assert "answer" in chat.json()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_api.py::test_http_login_and_chat -v`
Expected: FAIL because app routes are missing

- [ ] **Step 3: Write minimal implementation**

Expose `/api/login`, `/api/chat`, `/api/history`, `/api/admin/logs`, and `/api/admin/config`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_api.py -v`
Expected: PASS

### Task 4: Create the frontend pages and browser contract

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/admin.html`
- Create: `frontend/styles.css`
- Create: `frontend/app.js`
- Create: `frontend/admin.js`

- [ ] **Step 1: Write the failing static contract test**

```python
from pathlib import Path

def test_frontend_files_exist_and_reference_api():
    root = Path.cwd()
    app_js = (root / "frontend" / "app.js").read_text(encoding="utf-8")
    assert "/api/login" in app_js
    assert "/api/chat" in app_js
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_frontend_contract.py -v`
Expected: FAIL because files do not exist

- [ ] **Step 3: Write minimal implementation**

Add a login form, chat panel, history panel, admin dashboard, and JavaScript fetch calls against the Python API.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_frontend_contract.py -v`
Expected: PASS

### Task 5: Add the Linux C++ gateway skeleton and forwarding design

**Files:**
- Create: `cpp_gateway/CMakeLists.txt`
- Create: `cpp_gateway/include/http_server.h`
- Create: `cpp_gateway/include/thread_pool.h`
- Create: `cpp_gateway/src/http_server.cpp`
- Create: `cpp_gateway/src/main.cpp`
- Create: `cpp_gateway/README.md`

- [ ] **Step 1: Write the failing layout test**

```python
from pathlib import Path

def test_cpp_gateway_files_exist():
    root = Path.cwd()
    required = [
        root / "cpp_gateway" / "CMakeLists.txt",
        root / "cpp_gateway" / "src" / "main.cpp",
        root / "cpp_gateway" / "src" / "http_server.cpp",
    ]
    assert all(p.exists() for p in required)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cpp_gateway_layout.py -v`
Expected: FAIL because gateway files do not exist

- [ ] **Step 3: Write minimal implementation**

Add a documented C++17 gateway with epoll event loop, thread pool, simple HTTP parsing, and Python-forwarding stubs suitable for Linux compilation.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cpp_gateway_layout.py -v`
Expected: PASS

### Task 6: Complete graduation-project documentation

**Files:**
- Modify: `output/doc/毕业设计说明书初稿.md`
- Create: `docs/runbook.md`
- Create: `docs/test-plan.md`
- Create: `docs/figures-guide.md`

- [ ] **Step 1: Write the failing documentation coverage test**

```python
from pathlib import Path

def test_thesis_contains_required_sections():
    text = (Path.cwd() / "output" / "doc" / "毕业设计说明书初稿.md").read_text(encoding="utf-8")
    for section in ["摘要", "第1章 绪论", "第3章 系统需求分析", "第4章 系统总体设计", "第5章 系统详细实现", "第6章 系统测试与结果分析", "结论"]:
        assert section in text
```

- [ ] **Step 2: Run test to verify it fails if sections are missing**

Run: `pytest tests/test_docs.py -v`
Expected: FAIL only if required sections are missing

- [ ] **Step 3: Write minimal implementation**

Expand the thesis draft, add run instructions, test plan, and figure guidance aligned with the school template.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_docs.py -v`
Expected: PASS

### Task 7: Verify the first version

**Files:**
- Test: `tests/`

- [ ] **Step 1: Run the Python test suite**

Run: `pytest tests -v`
Expected: PASS

- [ ] **Step 2: Run Python syntax verification**

Run: `python -m compileall services`
Expected: exit 0 with compiled files listed

- [ ] **Step 3: Review deliverables**

Confirm the repository contains:
- frontend
- services/ai_service
- cpp_gateway
- db/schema.sql
- output/doc/毕业设计说明书初稿.md
- docs/runbook.md

- [ ] **Step 4: Report actual status**

Summarize what was verified, what remains Linux-only, and what the user can review next.
