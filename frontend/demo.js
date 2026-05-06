const demoRuntimeConfig = window.APP_CONFIG || {};
const demoMode = demoRuntimeConfig.mode || "direct";
const demoEndpointConfig =
  (demoRuntimeConfig.endpoints && demoRuntimeConfig.endpoints[demoMode]) ||
  (demoRuntimeConfig.endpoints && demoRuntimeConfig.endpoints.direct) ||
  { API_BASE: "http://127.0.0.1:8000/api", gateway: false };

const DEMO_API_BASE = demoEndpointConfig.API_BASE;

function demoApiUrl(endpoint) {
  const base = DEMO_API_BASE.replace(/\/+$/, "");
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  if (base.endsWith("/api") && (path === "/api" || path.startsWith("/api/"))) {
    return `${base}${path.slice(4)}`;
  }
  if (!base.endsWith("/api") && !path.startsWith("/api")) {
    return `${base}/api${path}`;
  }
  return `${base}${path}`;
}

function setDemoText(id, value) {
  const node = document.getElementById(id);
  if (!node) return;
  node.textContent = value === undefined || value === null || value === "" ? "未返回" : String(value);
}

function createDemoElement(tag, text, className = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = text === undefined || text === null ? "" : String(text);
  return node;
}

function renderHealthBars(items) {
  const box = document.getElementById("demo-health-bars");
  if (!box) return;
  box.replaceChildren();
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "health-bar-row";
    const label = createDemoElement("span", item.label);
    const track = document.createElement("div");
    track.className = "health-bar-track";
    const fill = document.createElement("div");
    fill.className = "health-bar-fill";
    fill.style.width = `${item.score}%`;
    track.appendChild(fill);
    const value = createDemoElement("strong", item.value);
    row.append(label, track, value);
    box.appendChild(row);
  });
}

function renderHealthVisualization(data) {
  const healthy = data.status === "ok";
  const hasStorage = Boolean(data.storage_mode);
  const hasModel = Boolean(data.model_name);
  const providerCount = Number(data.provider_count || 0);
  const sessionCount = Number(data.session_count || 0);
  const score =
    (healthy ? 35 : 0) +
    (hasStorage ? 20 : 0) +
    (hasModel ? 20 : 0) +
    (providerCount > 0 ? 15 : 0) +
    (Number.isFinite(sessionCount) ? 10 : 0);

  const ring = document.getElementById("demo-health-ring");
  if (ring) {
    ring.style.setProperty("--score", `${score}%`);
    ring.classList.toggle("is-healthy", healthy);
  }
  setDemoText("demo-health-score", score);
  setDemoText("demo-health-title", healthy ? "Python FastAPI 服务运行正常" : "后端服务异常");
  setDemoText(
    "demo-health-detail",
    `运行模式：${data.runtime_mode || "未知"}，存储：${data.storage_mode || "未知"}，模型：${data.model_name || "未知"}`
  );
  setDemoText("demo-session-count", data.session_count);
  const jsonBox = document.getElementById("demo-health-json");
  if (jsonBox) jsonBox.textContent = JSON.stringify(data, null, 2);
  renderHealthBars([
    { label: "服务连通", score: healthy ? 100 : 0, value: data.status || "failed" },
    { label: "存储模式", score: hasStorage ? 100 : 0, value: data.storage_mode || "missing" },
    { label: "模型配置", score: hasModel ? 100 : 0, value: data.model_name || "missing" },
    { label: "供应商数", score: Math.min(providerCount * 50, 100), value: providerCount },
    { label: "会话记录", score: sessionCount > 0 ? 100 : 30, value: sessionCount },
  ]);
}

function renderHealthFailure(error) {
  const ring = document.getElementById("demo-health-ring");
  if (ring) {
    ring.style.setProperty("--score", "0%");
    ring.classList.remove("is-healthy");
  }
  setDemoText("demo-health-score", 0);
  setDemoText("demo-health-title", "后端服务未连接");
  setDemoText("demo-health-detail", error.message || "无法读取 /api/health");
  setDemoText("demo-session-count", "未连接");
  const jsonBox = document.getElementById("demo-health-json");
  if (jsonBox) {
    jsonBox.textContent = JSON.stringify({ error: error.message || String(error) }, null, 2);
  }
  renderHealthBars([
    { label: "服务连通", score: 0, value: "failed" },
    { label: "存储模式", score: 0, value: "unknown" },
    { label: "模型配置", score: 0, value: "unknown" },
    { label: "供应商数", score: 0, value: "unknown" },
    { label: "会话记录", score: 0, value: "unknown" },
  ]);
}

async function loadDemoHealth() {
  setDemoText("demo-api-base", DEMO_API_BASE);
  const healthLink = document.getElementById("health-link");
  if (healthLink) healthLink.href = demoApiUrl("/api/health");
  try {
    const response = await fetch(demoApiUrl("/api/health"));
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "health failed");
    setDemoText("demo-health-status", data.status);
    setDemoText("demo-storage-mode", data.storage_mode);
    setDemoText("demo-model-name", data.model_name);
    setDemoText("demo-provider-count", data.provider_count);
    renderHealthVisualization(data);
  } catch (error) {
    setDemoText("demo-health-status", "连接失败");
    setDemoText("demo-storage-mode", "未连接");
    setDemoText("demo-model-name", "未连接");
    setDemoText("demo-provider-count", "未连接");
    renderHealthFailure(error);
  }
}

function metricValue(data, keys, fallback = "未提供") {
  for (const key of keys) {
    if (data && data[key] !== undefined && data[key] !== null) {
      return data[key];
    }
  }
  return fallback;
}

function formatMetric(value, suffix = "") {
  if (typeof value === "number") {
    return `${Number.isInteger(value) ? value : value.toFixed(2)}${suffix}`;
  }
  return `${value}${suffix}`;
}

async function loadBenchmarkFile(fileName, title) {
  const response = await fetch(`../output/benchmark/${fileName}`);
  if (!response.ok) throw new Error(`${fileName} not found`);
  const data = await response.json();
  return {
    title,
    fileName,
    successRate: metricValue(data, ["success_rate", "successRate", "success_ratio"], 1),
    throughput: metricValue(data, ["requests_per_second", "throughput", "rps"], 0),
    p95: metricValue(data, ["p95_ms", "p95_latency_ms", "p95"], 0),
    total: metricValue(data, ["total_requests", "requests", "total"], 0),
  };
}

function renderBenchmark(items) {
  const box = document.getElementById("demo-benchmark-box");
  if (!box) return;
  box.replaceChildren();
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "benchmark-visual-card";
    card.appendChild(createDemoElement("h3", item.title));
    card.appendChild(createDemoElement("p", item.fileName, "hint"));

    const metrics = document.createElement("div");
    metrics.className = "benchmark-mini-grid";
    [
      ["成功率", formatMetric(Number(item.successRate) * 100, "%")],
      ["吞吐量", formatMetric(item.throughput, " req/s")],
      ["P95 延迟", formatMetric(item.p95, " ms")],
      ["请求数", formatMetric(item.total)],
    ].forEach(([label, value]) => {
      const metric = document.createElement("div");
      metric.appendChild(createDemoElement("span", label));
      metric.appendChild(createDemoElement("strong", value));
      metrics.appendChild(metric);
    });
    card.appendChild(metrics);
    box.appendChild(card);
  });
}

async function loadDemoBenchmarks() {
  const box = document.getElementById("demo-benchmark-box");
  if (box) {
    box.replaceChildren(createDemoElement("p", "正在加载压测结果...", "hint"));
  }
  try {
    const items = await Promise.all([
      loadBenchmarkFile("gateway-health.json", "网关健康检查压测"),
      loadBenchmarkFile("gateway-chat.json", "网关聊天接口压测"),
    ]);
    renderBenchmark(items);
  } catch (error) {
    if (box) {
      box.replaceChildren(createDemoElement("p", "压测结果暂不可读取，请确认 output/benchmark 下存在 JSON 文件。", "hint"));
    }
  }
}

document.getElementById("demo-refresh-btn").addEventListener("click", loadDemoHealth);
document.getElementById("demo-benchmark-btn").addEventListener("click", loadDemoBenchmarks);

loadDemoHealth();
loadDemoBenchmarks();
