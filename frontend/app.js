const API_BASE = "http://127.0.0.1:8000/api";
const LOGIN_ENDPOINT = "/api/login";
const CHAT_ENDPOINT = "/api/chat";
let authToken = "";

function appendMessage(title, content, targetId = "chat-log") {
  const node = document.createElement("article");
  node.className = "message-card";
  node.innerHTML = `<h4>${title}</h4><p>${content}</p>`;
  document.getElementById(targetId).prepend(node);
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
    headers: { "Content-Type": "application/json" },
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
}

async function loadHistory() {
  if (!authToken) return;
  const res = await fetch(`${API_BASE}/history?token=${encodeURIComponent(authToken)}`);
  const data = await res.json();
  const box = document.getElementById("history-list");
  box.innerHTML = "";
  document.getElementById("session-title-value").textContent = data.title || "未生成";
  (data.messages || []).forEach((item, index) => {
    const node = document.createElement("article");
    node.className = "message-card";
    node.innerHTML = `
      <h4>第 ${index + 1} 轮</h4>
      <p><strong>问：</strong>${item.user_message}</p>
      <p><strong>答：</strong>${item.assistant_message}</p>
    `;
    box.appendChild(node);
  });
}

document.getElementById("login-btn").addEventListener("click", login);
document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("load-history-btn").addEventListener("click", loadHistory);
