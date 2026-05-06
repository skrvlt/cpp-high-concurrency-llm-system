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
  } catch (error) {
    setDemoText("demo-health-status", "连接失败");
    setDemoText("demo-storage-mode", "未连接");
    setDemoText("demo-model-name", "未连接");
    setDemoText("demo-provider-count", "未连接");
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
