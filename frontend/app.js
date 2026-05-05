const runtimeConfig = window.APP_CONFIG || {};
const mode = runtimeConfig.mode || "direct";
const endpointConfig =
  (runtimeConfig.endpoints && runtimeConfig.endpoints[mode]) ||
  (runtimeConfig.endpoints && runtimeConfig.endpoints.direct) ||
  { API_BASE: "http://127.0.0.1:8000/api", gateway: false };

const API_BASE = endpointConfig.API_BASE;
const LOGIN_ENDPOINT = "/api/login";
const CHAT_ENDPOINT = "/api/chat";
let authToken = "";

function createTextElement(tag, text, className = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = text === undefined || text === null ? "" : String(text);
  return node;
}

function authHeaders() {
  return { Authorization: `Bearer ${authToken}` };
}

function appendMessage(title, content, targetId = "chat-log") {
  const node = document.createElement("article");
  node.className = "message-card";
  node.appendChild(createTextElement("h4", title));
  node.appendChild(createTextElement("p", content));
  document.getElementById(targetId).prepend(node);
}

function createMessageLine(label, text) {
  const line = document.createElement("p");
  const strong = createTextElement("strong", label);
  line.appendChild(strong);
  line.appendChild(document.createTextNode(text === undefined || text === null ? "" : String(text)));
  return line;
}

function updateModeBanner() {
  const modeBox = document.getElementById("runtime-mode-value");
  if (!modeBox) return;
  modeBox.textContent = endpointConfig.gateway ? "网关转发模式" : "直连服务模式";
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (!node) return;
  node.textContent = value === undefined || value === null || value === "" ? "未返回" : value;
}

function renderHealthStatus(data) {
  setText("api-base-value", API_BASE);
  setText("health-runtime-mode", data.runtime_mode);
  setText("health-storage-mode", data.storage_mode);
  setText("health-model-name", data.model_name);
  setText("health-session-count", data.session_count);
}

async function loadHealthStatus() {
  setText("api-base-value", API_BASE);
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    if (!res.ok) {
      setText("health-runtime-mode", "接口异常");
      return;
    }
    renderHealthStatus(data);
  } catch (error) {
    setText("health-runtime-mode", "连接失败");
    setText("health-storage-mode", "未连接");
    setText("health-model-name", "未连接");
    setText("health-session-count", "未连接");
  }
}

async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const res = await fetch(`${API_BASE}${LOGIN_ENDPOINT.replace("/api", "")}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) {
    document.getElementById("auth-status").textContent = data.detail || "登录失败";
    return;
  }
  authToken = data.token;
  document.getElementById("auth-status").textContent = `登录成功，角色：${data.role}`;
  appendMessage("系统", "已建立会话，可以开始提问。");
  await loadHealthStatus();
}

async function sendMessage() {
  if (!authToken) {
    document.getElementById("auth-status").textContent = "请先登录";
    return;
  }
  const message = document.getElementById("message").value.trim();
  if (!message) return;

  appendMessage("我", message);
  const res = await fetch(`${API_BASE}${CHAT_ENDPOINT.replace("/api", "")}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ token: authToken, message }),
  });
  const data = await res.json();
  if (!res.ok) {
    appendMessage("错误", data.detail || "发送失败");
    return;
  }
  appendMessage("系统回答", data.answer);
  document.getElementById("message").value = "";
  await loadHistory();
  await loadHealthStatus();
}

async function loadHistory() {
  if (!authToken) return;
  const res = await fetch(`${API_BASE}/history`, { headers: authHeaders() });
  const data = await res.json();
  const box = document.getElementById("history-list");
  box.replaceChildren();
  document.getElementById("session-title-value").textContent = data.title || "未生成";
  (data.messages || []).forEach((item, index) => {
    const node = document.createElement("article");
    node.className = "message-card";
    node.appendChild(createTextElement("h4", `第 ${index + 1} 轮`));
    node.appendChild(createMessageLine("问：", item.user_message));
    node.appendChild(createMessageLine("答：", item.assistant_message));
    box.appendChild(node);
  });
}

updateModeBanner();
loadHealthStatus();
document.getElementById("login-btn").addEventListener("click", login);
document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("load-history-btn").addEventListener("click", loadHistory);
document.getElementById("refresh-health-btn").addEventListener("click", loadHealthStatus);
