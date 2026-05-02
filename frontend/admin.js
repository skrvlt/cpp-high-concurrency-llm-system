const adminRuntimeConfig = window.APP_CONFIG || {};
const adminMode = adminRuntimeConfig.mode || "direct";
const adminEndpointConfig =
  (adminRuntimeConfig.endpoints && adminRuntimeConfig.endpoints[adminMode]) ||
  (adminRuntimeConfig.endpoints && adminRuntimeConfig.endpoints.direct) ||
  { API_BASE: "http://127.0.0.1:8000/api", gateway: false };

const ADMIN_API_BASE = adminEndpointConfig.API_BASE;
let adminToken = "";

const overviewLabels = {
  user_count: "用户数",
  session_count: "会话数",
  message_count: "消息数",
  log_count: "日志数",
  model_name: "模型名称",
};

function updateAdminModeBanner() {
  const modeBox = document.getElementById("admin-runtime-mode");
  if (!modeBox) return;
  modeBox.textContent = adminEndpointConfig.gateway ? "网关转发模式" : "直连服务模式";
}

function setAdminText(id, value) {
  const node = document.getElementById(id);
  if (!node) return;
  node.textContent = value === undefined || value === null || value === "" ? "未返回" : value;
}

function renderAdminHealthStatus(data) {
  setAdminText("api-base-value", ADMIN_API_BASE);
  setAdminText("health-runtime-mode", data.runtime_mode);
  setAdminText("health-storage-mode", data.storage_mode);
  setAdminText("health-model-name", data.model_name);
  setAdminText("health-session-count", data.session_count);
}

async function loadAdminHealthStatus() {
  setAdminText("api-base-value", ADMIN_API_BASE);
  try {
    const res = await fetch(`${ADMIN_API_BASE}/health`);
    const data = await res.json();
    if (!res.ok) {
      setAdminText("health-runtime-mode", "接口异常");
      return;
    }
    renderAdminHealthStatus(data);
  } catch (error) {
    setAdminText("health-runtime-mode", "连接失败");
    setAdminText("health-storage-mode", "未连接");
    setAdminText("health-model-name", "未连接");
    setAdminText("health-session-count", "未连接");
  }
}

async function adminLogin() {
  const username = document.getElementById("admin-username").value.trim();
  const password = document.getElementById("admin-password").value.trim();
  const res = await fetch(`${ADMIN_API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    document.getElementById("admin-auth-status").textContent = data.detail || "登录失败";
    return;
  }
  adminToken = data.token;
  document.getElementById("admin-auth-status").textContent = "管理员登录成功";
  await loadAdminHealthStatus();
}

async function loadLogs() {
  if (!adminToken) return;
  const res = await fetch(
    `${ADMIN_API_BASE}/admin/logs?token=${encodeURIComponent(adminToken)}`
  );
  const data = await res.json();
  const box = document.getElementById("logs-box");
  box.innerHTML = "";
  (data.items || []).forEach((item) => {
    const node = document.createElement("article");
    node.className = "message-card";
    node.innerHTML = `<h4>${item.event_type}</h4><p>${item.message}</p><p>${item.created_at}</p>`;
    box.appendChild(node);
  });
}

async function loadOverview() {
  if (!adminToken) return;
  const res = await fetch(
    `${ADMIN_API_BASE}/admin/overview?token=${encodeURIComponent(adminToken)}`
  );
  const data = await res.json();
  const box = document.getElementById("overview-box");
  box.innerHTML = "";
  Object.entries(overviewLabels).forEach(([key, label]) => {
    const node = document.createElement("article");
    node.className = "message-card metric-card";
    node.innerHTML = `<h4>${label}</h4><p>${data[key] ?? "未返回"}</p>`;
    box.appendChild(node);
  });
}

async function loadConfig() {
  if (!adminToken) return;
  const res = await fetch(
    `${ADMIN_API_BASE}/admin/config?token=${encodeURIComponent(adminToken)}`
  );
  const data = await res.json();
  const box = document.getElementById("config-box");
  box.innerHTML = "";
  Object.entries(data).forEach(([key, value]) => {
    const node = document.createElement("article");
    node.className = "message-card";
    node.innerHTML = `<h4>${key}</h4><p>${value}</p>`;
    box.appendChild(node);
  });
}

async function updateConfig() {
  if (!adminToken) return;
  const config_key = document.getElementById("config-key").value.trim();
  const config_value = document.getElementById("config-value").value.trim();
  await fetch(`${ADMIN_API_BASE}/admin/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: adminToken, config_key, config_value }),
  });
  await loadConfig();
  await loadLogs();
  await loadOverview();
  await loadAdminHealthStatus();
}

updateAdminModeBanner();
loadAdminHealthStatus();
document.getElementById("admin-login-btn").addEventListener("click", adminLogin);
document.getElementById("load-overview-btn").addEventListener("click", loadOverview);
document.getElementById("load-logs-btn").addEventListener("click", loadLogs);
document.getElementById("load-config-btn").addEventListener("click", loadConfig);
document.getElementById("update-config-btn").addEventListener("click", updateConfig);
document
  .getElementById("admin-refresh-health-btn")
  .addEventListener("click", loadAdminHealthStatus);
