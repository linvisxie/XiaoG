const state = { conversationId: null, abortController: null, generating: false };
const $ = (selector) => document.querySelector(selector);
const messagesEl = $("#messages");
const inputEl = $("#message-input");
const sendButton = $("#send-button");
const stopButton = $("#stop-button");
const modelSelect = $("#model-select");

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "请求失败，请稍后重试。");
  }
  return response.status === 204 ? null : response.json();
}

function modelLabel(model) {
  if (model === "gpt-5.6-terra") return "GPT-5.6 Terra";
  if ((model || "").toLowerCase().startsWith("deepseek")) return "DeepSeek";
  return model || "DeepSeek";
}
function escapeText(text) { return document.createTextNode(text); }
function scrollToBottom() { window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }); }
function emptyMessages() { messagesEl.innerHTML = `<div class="empty-state"><div class="empty-logo">G</div><h1>你好，我是小G。</h1><p>我会把对话保存在你的电脑里。告诉我今天想一起完成什么？</p></div>`; }

function messageElement(message, streaming = false) {
  const article = document.createElement("article");
  article.className = `message ${message.role}`;
  const avatar = document.createElement("div"); avatar.className = "message-avatar"; avatar.textContent = message.role === "assistant" ? "G" : "你";
  const body = document.createElement("div"); body.className = "message-body";
  const meta = document.createElement("div"); meta.className = "message-meta";
  meta.textContent = message.role === "assistant" ? `小G · ${modelLabel(message.model)}` : "你";
  const content = document.createElement("div"); content.className = "message-content"; content.appendChild(escapeText(message.content || ""));
  if (streaming) { const cursor = document.createElement("span"); cursor.className = "cursor"; content.appendChild(cursor); }
  body.append(meta, content); article.append(avatar, body); return article;
}

function addMessage(message, streaming = false) { if (messagesEl.querySelector(".empty-state")) messagesEl.innerHTML = ""; const el = messageElement(message, streaming); messagesEl.append(el); scrollToBottom(); return el; }

async function refreshConversations() {
  const list = await request("/api/conversations"); const target = $("#conversation-list"); target.innerHTML = "";
  for (const conversation of list) {
    const item = document.createElement("div"); item.className = `conversation ${conversation.id === state.conversationId ? "active" : ""}`;
    const open = document.createElement("button"); open.className = "conversation-name"; open.textContent = conversation.title; open.title = conversation.title;
    open.onclick = () => openConversation(conversation.id);
    const remove = document.createElement("button"); remove.className = "delete-chat"; remove.textContent = "×"; remove.title = "删除会话";
    remove.onclick = async (event) => { event.stopPropagation(); if (confirm(`删除“${conversation.title}”？此操作无法撤销。`)) { await request(`/api/conversations/${conversation.id}`, { method: "DELETE" }); if (state.conversationId === conversation.id) { state.conversationId = null; emptyMessages(); } await refreshConversations(); } };
    item.append(open, remove); target.append(item);
  }
}

async function createConversation() { const conversation = await request("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }); state.conversationId = conversation.id; emptyMessages(); await refreshConversations(); inputEl.focus(); return conversation; }

async function openConversation(id) { if (state.generating) return; const conversation = await request(`/api/conversations/${id}`); state.conversationId = id; messagesEl.innerHTML = ""; if (!conversation.messages.length) emptyMessages(); else conversation.messages.forEach(addMessage); await refreshConversations(); }

function setGenerating(value) { state.generating = value; sendButton.disabled = value; stopButton.classList.toggle("hidden", !value); inputEl.disabled = value; }
function resizeInput() { inputEl.style.height = "auto"; inputEl.style.height = `${Math.min(inputEl.scrollHeight, 180)}px`; }

async function sendMessage(content) {
  if (!content.trim() || state.generating) return;
  if (!state.conversationId) await createConversation();
  addMessage({ role: "user", content }); inputEl.value = ""; resizeInput(); setGenerating(true);
  const assistant = addMessage({ role: "assistant", content: "", model: "DeepSeek" }, true);
  const contentEl = assistant.querySelector(".message-content"); const metaEl = assistant.querySelector(".message-meta");
  state.abortController = new AbortController();
  try {
    const response = await fetch(`/api/conversations/${state.conversationId}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content, model_preference: modelSelect.value }), signal: state.abortController.signal });
    if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail || "消息发送失败。"); }
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ""; let received = "";
    while (true) {
      const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n"); buffer = blocks.pop();
      for (const block of blocks) {
        const lines = block.split("\n"); const event = lines.find((x) => x.startsWith("event:"))?.slice(6).trim(); const raw = lines.find((x) => x.startsWith("data:"))?.slice(5).trim(); if (!event || !raw) continue;
        const data = JSON.parse(raw);
        if (event === "meta") metaEl.textContent = `小G · ${data.display_name || data.model}`;
        if (event === "delta") { received += data.content; contentEl.textContent = received; const cursor = document.createElement("span"); cursor.className = "cursor"; contentEl.append(cursor); scrollToBottom(); }
        if (event === "error") { contentEl.textContent = data.message; assistant.classList.add("error"); }
        if (event === "done") { metaEl.textContent = `小G · ${data.display_name || data.model}`; }
      }
    }
  } catch (error) {
    if (error.name === "AbortError") { contentEl.textContent = contentEl.textContent || "已停止生成。"; }
    else { contentEl.textContent = error.message || "网络连接失败，请稍后重试。"; assistant.classList.add("error"); }
  } finally {
    contentEl.querySelector(".cursor")?.remove(); state.abortController = null; setGenerating(false); await refreshConversations(); inputEl.focus();
  }
}

async function loadProviderStatus() { try { const status = await request("/api/provider-status"); const terra = modelSelect.querySelector('option[value="terra"]'); terra.disabled = !status.terra.available; terra.textContent = status.terra.available ? "GPT-5.6 Terra" : "当前账户未提供 GPT-5.6 Terra"; $("#provider-note").textContent = status.terra.available ? "Terra 可用；Auto 默认使用 DeepSeek。" : status.terra.message; } catch { $("#provider-note").textContent = "无法读取模型状态。"; } }

async function openSettings() { const settings = await request("/api/settings"); $("#system-prompt").value = settings.system_prompt; $("#user-profile").value = settings.user_profile; $("#settings-dialog").showModal(); }

$("#chat-form").addEventListener("submit", (event) => { event.preventDefault(); sendMessage(inputEl.value); });
inputEl.addEventListener("input", resizeInput);
inputEl.addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); $("#chat-form").requestSubmit(); } });
$("#new-chat").onclick = createConversation; stopButton.onclick = () => state.abortController?.abort();
$("#open-settings").onclick = openSettings; $("#close-settings").onclick = () => $("#settings-dialog").close(); $("#cancel-settings").onclick = () => $("#settings-dialog").close();
$("#settings-form").addEventListener("submit", async (event) => { event.preventDefault(); await request("/api/settings", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ system_prompt: $("#system-prompt").value, user_profile: $("#user-profile").value }) }); $("#settings-dialog").close(); alert("设置已保存。"); });

(async function boot() { await Promise.all([refreshConversations(), loadProviderStatus()]); inputEl.focus(); })().catch((error) => { console.error(error); $("#provider-note").textContent = "启动初始化失败，请刷新页面。"; });
