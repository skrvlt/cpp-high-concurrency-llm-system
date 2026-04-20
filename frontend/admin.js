const adminRuntimeConfig = window.APP_CONFIG || {};
const adminMode = adminRuntimeConfig.mode || "direct";
const adminEndpointConfig =
  (adminRuntimeConfig.endpoints && adminRuntimeConfig.endpoints[adminMode]) ||
  (adminRuntimeConfig.endpoints && adminRuntimeConfig.endpoints.direct) ||
  { API_BASE: "http://127.0.0.1:8000/api", gateway: false };

const ADMIN_API_BASE = adminEndpointConfig.API_BASE;
let adminToken = "";

function updateAdminModeBanner() {
  const modeBox = document.getElementById("admin-runtime-mode");
  if (!modeBox) return;
  modeBox.textContent = adminEndpointConfig.gateway ? "网关转发模式" : "直连服务模式";
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
  Object.entries(data).forEach(([key, value]) => {
    const node = document.createElement("article");
    node.className = "message-card";
    node.innerHTML = `<h4>${key}</h4><p>${value}</p>`;
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
}

updateAdminModeBanner();
document.getElementById("admin-login-btn").addEventListener("click", adminLogin);
document.getElementById("load-overview-btn").addEventListener("click", loadOverview);
document.getElementById("load-logs-btn").addEventListener("click", loadLogs);
document.getElementById("load-config-btn").addEventListener("click", loadConfig);
document.getElementById("update-config-btn").addEventListener("click", updateConfig);
