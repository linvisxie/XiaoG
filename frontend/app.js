const state = {
  conversationId: null,
  conversationArchived: false,
  view: "active",
  abortController: null,
  generating: false,
  autoScroll: true,
  terraEfforts: [],
  terraEffort: localStorage.getItem("xiaog.terraReasoningEffort") || "medium",
  sidebarCollapsed: localStorage.getItem("xiaog.sidebarCollapsed") === "true",
  scrollPositions: new Map(),
  conversations: [],
  currentTitle: "新聊天",
};
const $ = (selector) => document.querySelector(selector);
const messagesEl = $("#messages"), inputEl = $("#message-input"), sendButton = $("#send-button"), stopButton = $("#stop-button"), modelSelect = $("#model-select"), backToBottom = $("#back-to-bottom");

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "请求失败，请稍后重试。");
  }
  return response.status === 204 ? null : response.json();
}
function modelLabel(model) { if (model === "gpt-5.6-terra") return "GPT-5.6 Terra"; if ((model || "").toLowerCase().startsWith("deepseek")) return "DeepSeek"; return model || "DeepSeek"; }
function emptyMessages() { messagesEl.innerHTML = `<div class="empty-state"><div class="empty-logo">G</div><h1>你好，我是小G。</h1><p>${state.view === "archived" ? "这是已归档会话。恢复后可继续聊天。" : "我会把对话保存在你的电脑里。告诉我今天想一起完成什么？"}</p></div>`; }
function isNearBottom() { return messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 96; }
function syncScrollControls() { backToBottom.classList.toggle("hidden", state.autoScroll); }
function scrollToBottom(force = false) { if (!force && !state.autoScroll) return; messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "auto" }); }
function rememberScrollPosition() { if (state.conversationId) state.scrollPositions.set(state.conversationId, messagesEl.scrollTop); }
function restoreScrollPosition(id) {
  const saved = state.scrollPositions.get(id);
  const previousBehavior = messagesEl.style.scrollBehavior;
  messagesEl.style.scrollBehavior = "auto";
  if (saved === undefined) messagesEl.scrollTop = messagesEl.scrollHeight;
  else messagesEl.scrollTop = saved;
  messagesEl.style.scrollBehavior = previousBehavior;
  state.autoScroll = isNearBottom();
  syncScrollControls();
}
function setSidebarCollapsed(value) {
  state.sidebarCollapsed = value;
  $("#app-shell").classList.toggle("sidebar-collapsed", value);
  $("#sidebar-toggle").textContent = value ? "›" : "‹";
  $("#sidebar-toggle").setAttribute("aria-label", value ? "展开历史栏" : "收缩历史栏");
  $("#sidebar-toggle").title = value ? "展开历史栏" : "收缩历史栏";
  localStorage.setItem("xiaog.sidebarCollapsed", String(value));
}
function setHeaderTitle(title) {
  state.currentTitle = title || "新聊天";
  $("#conversation-title").textContent = state.currentTitle;
  $("#conversation-title").title = state.currentTitle;
  $("#edit-title").disabled = !state.conversationId || state.conversationArchived || state.generating;
}
function messageElement(message, streaming = false) {
  const article = document.createElement("article");
  article.className = `message ${message.role}`;
  const avatar = document.createElement("div"); avatar.className = "message-avatar"; avatar.textContent = message.role === "assistant" ? "G" : "U";
  const body = document.createElement("div"); body.className = "message-body";
  const meta = document.createElement("div"); meta.className = "message-meta"; meta.textContent = message.role === "assistant" ? `小G · ${modelLabel(message.model)}` : "你";
  const content = document.createElement("div"); content.className = "message-content"; content.append(document.createTextNode(message.content || ""));
  if (streaming) { const cursor = document.createElement("span"); cursor.className = "cursor"; content.append(cursor); }
  body.append(meta, content);
  if (message.role === "user") article.append(body, avatar); else article.append(avatar, body);
  return article;
}
function addMessage(message, streaming = false, forceScroll = false) { if (messagesEl.querySelector(".empty-state")) messagesEl.innerHTML = ""; const el = messageElement(message, streaming); messagesEl.append(el); scrollToBottom(forceScroll); return el; }
function renderMessages(messages) { messagesEl.innerHTML = ""; if (!messages.length) emptyMessages(); else messages.forEach((message) => messagesEl.append(messageElement(message))); }
function setComposerArchived(archived) { inputEl.disabled = archived || state.generating; sendButton.disabled = archived || state.generating; inputEl.placeholder = archived ? "已归档会话只能查看；恢复后可继续聊天。" : "给小G发消息…（Enter 发送，Shift+Enter 换行）"; }
function setGenerating(value) { state.generating = value; stopButton.classList.toggle("hidden", !value); setComposerArchived(state.conversationArchived); setHeaderTitle(state.currentTitle); }
function resizeInput() { inputEl.style.height = "auto"; inputEl.style.height = `${Math.min(inputEl.scrollHeight, 180)}px`; }

function renderConversationList() {
  const archived = state.view === "archived";
  const query = $("#history-search").value.trim().toLocaleLowerCase();
  const list = state.conversations.filter((conversation) => !query || conversation.title.toLocaleLowerCase().includes(query));
  const target = $("#conversation-list");
  target.innerHTML = "";
  $("#conversation-heading").textContent = archived ? "已归档" : "历史对话";
  $("#open-archived").classList.toggle("active", archived);
  $("#back-to-history").classList.toggle("hidden", !archived);
  for (const conversation of list) {
    const item = document.createElement("div"); item.className = `conversation ${conversation.id === state.conversationId ? "active" : ""}`;
    const open = document.createElement("button"); open.className = "conversation-name"; open.textContent = conversation.title; open.title = conversation.title; open.onclick = () => openConversation(conversation.id);
    const action = document.createElement("button"); action.className = "conversation-action"; action.textContent = archived ? "恢复" : "归档"; action.title = archived ? "恢复会话" : "归档会话";
    action.onclick = async (event) => { event.stopPropagation(); if (archived) await restoreConversation(conversation.id); else await archiveConversation(conversation.id); };
    const remove = document.createElement("button"); remove.className = "conversation-action delete"; remove.textContent = "×"; remove.title = "删除会话";
    remove.onclick = async (event) => { event.stopPropagation(); if (confirm(`删除“${conversation.title}”？此操作无法撤销。`)) { await request(`/api/conversations/${conversation.id}`, { method: "DELETE" }); if (state.conversationId === conversation.id) startDraft(); await refreshConversations(); } };
    item.append(open, action, remove); target.append(item);
  }
  if (!list.length) { const note = document.createElement("p"); note.className = "conversation-empty"; note.textContent = query ? "没有匹配的会话" : archived ? "暂无已归档会话" : "暂无历史会话"; target.append(note); }
}
async function refreshConversations() { state.conversations = await request(`/api/conversations?archived=${state.view === "archived"}`); renderConversationList(); }
function startDraft() { if (state.generating) return; rememberScrollPosition(); state.view = "active"; state.conversationId = null; state.conversationArchived = false; state.autoScroll = true; emptyMessages(); setHeaderTitle("新聊天"); setComposerArchived(false); refreshConversations().catch(console.error); inputEl.focus(); }
async function openConversation(id) {
  if (state.generating) return;
  rememberScrollPosition();
  const conversation = await request(`/api/conversations/${id}`);
  state.conversationId = id; state.conversationArchived = Boolean(conversation.archived_at);
  renderMessages(conversation.messages); setHeaderTitle(conversation.title); setComposerArchived(state.conversationArchived);
  await refreshConversations();
  restoreScrollPosition(id);
}
async function archiveConversation(id) { await request(`/api/conversations/${id}/archive`, { method: "POST" }); if (state.conversationId === id) startDraft(); await refreshConversations(); }
async function restoreConversation(id) { await request(`/api/conversations/${id}/restore`, { method: "POST" }); if (state.conversationId === id) startDraft(); await refreshConversations(); }
async function showArchived() { if (state.generating) return; rememberScrollPosition(); state.view = "archived"; state.conversationId = null; state.conversationArchived = false; state.autoScroll = true; emptyMessages(); setHeaderTitle("已归档会话"); setComposerArchived(true); await refreshConversations(); }
async function updateCurrentTitle() {
  if (!state.conversationId || state.conversationArchived || state.generating) return;
  const title = prompt("修改会话标题", state.currentTitle);
  if (title === null) return;
  const cleanTitle = title.trim();
  if (!cleanTitle) return;
  const conversation = await request(`/api/conversations/${state.conversationId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: cleanTitle }) });
  setHeaderTitle(conversation.title); await refreshConversations();
}

function renderTerraEfforts(details = {}) {
  const supported = new Set(details.supported_reasoning_efforts || []);
  const options = [["low", "低"], ["medium", "中"], ["high", "高"]].filter(([value]) => supported.has(value));
  state.terraEfforts = options.map(([value]) => value);
  if (!state.terraEfforts.includes(state.terraEffort)) state.terraEffort = state.terraEfforts.includes(details.default_reasoning_effort) ? details.default_reasoning_effort : state.terraEfforts[0] || "";
  if (state.terraEffort) localStorage.setItem("xiaog.terraReasoningEffort", state.terraEffort);
  const target = $("#terra-effort-options"); target.innerHTML = "";
  for (const [value, label] of options) { const button = document.createElement("button"); button.type = "button"; button.className = `effort-option ${value === state.terraEffort ? "active" : ""}`; button.textContent = label; button.setAttribute("aria-pressed", String(value === state.terraEffort)); button.onclick = () => { state.terraEffort = value; localStorage.setItem("xiaog.terraReasoningEffort", value); renderTerraEfforts({ supported_reasoning_efforts: state.terraEfforts, default_reasoning_effort: value }); }; target.append(button); }
  syncTerraControl();
}
function syncTerraControl() { $("#terra-effort-control").classList.toggle("reserved", modelSelect.value !== "terra" || !state.terraEfforts.length); }
async function loadProviderStatus() {
  try { const status = await request("/api/provider-status"); const terra = modelSelect.querySelector('option[value="terra"]'); terra.disabled = !status.terra.available; terra.textContent = status.terra.available ? "GPT-5.6 Terra" : "当前账户未提供 GPT-5.6 Terra"; $("#provider-note").textContent = status.terra.available ? "Terra 可用；可在右侧切换模型。" : status.terra.message; renderTerraEfforts(status.terra.details || {}); }
  catch { $("#provider-note").textContent = "无法读取模型状态。"; }
}

async function sendMessage(content) {
  if (!content.trim() || state.generating || state.conversationArchived) return;
  if (!state.conversationId) { const conversation = await request("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }); state.conversationId = conversation.id; state.currentTitle = conversation.title; await refreshConversations(); }
  state.autoScroll = true; syncScrollControls();
  const cleanContent = content.trim(); addMessage({ role: "user", content: cleanContent }, false, true); inputEl.value = ""; resizeInput(); setGenerating(true);
  const assistant = addMessage({ role: "assistant", content: "", model: "DeepSeek" }, true, true); const contentEl = assistant.querySelector(".message-content"), metaEl = assistant.querySelector(".message-meta");
  state.abortController = new AbortController();
  try {
    const response = await fetch(`/api/conversations/${state.conversationId}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content: cleanContent, model_preference: modelSelect.value, terra_reasoning_effort: modelSelect.value === "terra" ? state.terraEffort : null }), signal: state.abortController.signal });
    if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail || "消息发送失败。"); }
    const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = "", received = "";
    while (true) {
      const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const blocks = buffer.split("\n\n"); buffer = blocks.pop();
      for (const block of blocks) {
        const lines = block.split("\n"), event = lines.find((line) => line.startsWith("event:"))?.slice(6).trim(), raw = lines.find((line) => line.startsWith("data:"))?.slice(5).trim(); if (!event || !raw) continue;
        const data = JSON.parse(raw);
        if (event === "meta") metaEl.textContent = `小G · ${data.display_name || data.model}`;
        if (event === "delta") { received += data.content; contentEl.textContent = received; const cursor = document.createElement("span"); cursor.className = "cursor"; contentEl.append(cursor); scrollToBottom(); }
        if (event === "error") { contentEl.textContent = data.message; assistant.classList.add("error"); }
      }
    }
  } catch (error) {
    if (error.name === "AbortError") contentEl.textContent = contentEl.textContent || "已停止生成。";
    else { contentEl.textContent = error.message || "网络连接失败，请稍后重试。"; assistant.classList.add("error"); }
  } finally {
    contentEl.querySelector(".cursor")?.remove(); state.abortController = null; setGenerating(false);
    if (state.conversationId) { const conversation = await request(`/api/conversations/${state.conversationId}`); setHeaderTitle(conversation.title); }
    await refreshConversations(); inputEl.focus();
  }
}

function renderAbout(info) {
  const content = $("#about-content"); content.innerHTML = "";
  const rows = [["名称", info.name], ["当前版本", info.version], ["Commit", info.commit], ["当前阶段", info.phase], ["搭载模型", (info.models || []).join(" · ")]];
  const meta = document.createElement("dl"); meta.className = "about-meta";
  rows.forEach(([label, value]) => { const term = document.createElement("dt"); term.textContent = label; const detail = document.createElement("dd"); detail.textContent = value || "—"; meta.append(term, detail); });
  const capabilities = document.createElement("div"); capabilities.className = "about-block"; capabilities.innerHTML = "<h4>当前能力</h4>"; const list = document.createElement("ul"); (info.capabilities || []).forEach((item) => { const line = document.createElement("li"); line.textContent = item; list.append(line); }); capabilities.append(list);
  const log = document.createElement("div"); log.className = "about-block"; log.innerHTML = "<h4>更新日志</h4>"; (info.changelog || []).forEach((entry) => { const item = document.createElement("div"); item.className = "changelog-item"; const title = document.createElement("strong"); title.textContent = `${entry.version} · ${entry.title}`; const entries = document.createElement("ul"); (entry.items || []).forEach((text) => { const line = document.createElement("li"); line.textContent = text; entries.append(line); }); item.append(title, entries); log.append(item); });
  content.append(meta, capabilities, log);
}
async function openSettings() {
  const [settings, about] = await Promise.all([request("/api/settings"), request("/api/about")]);
  $("#system-prompt").value = settings.system_prompt; $("#user-profile").value = settings.user_profile; renderAbout(about); activateSettingsTab("personalization"); $("#settings-dialog").showModal();
}
function activateSettingsTab(name) { document.querySelectorAll("[data-settings-tab]").forEach((tab) => tab.classList.toggle("active", tab.dataset.settingsTab === name)); document.querySelectorAll("[data-settings-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.settingsPanel === name)); }

messagesEl.addEventListener("scroll", () => { rememberScrollPosition(); state.autoScroll = isNearBottom(); syncScrollControls(); });
backToBottom.onclick = () => { state.autoScroll = true; scrollToBottom(true); syncScrollControls(); };
$("#chat-form").addEventListener("submit", (event) => { event.preventDefault(); sendMessage(inputEl.value); }); inputEl.addEventListener("input", resizeInput); inputEl.addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); $("#chat-form").requestSubmit(); } });
$("#new-chat").onclick = startDraft; $("#open-archived").onclick = showArchived; $("#back-to-history").onclick = startDraft; $("#history-search").addEventListener("input", renderConversationList); $("#sidebar-toggle").onclick = () => setSidebarCollapsed(!state.sidebarCollapsed); $("#edit-title").onclick = updateCurrentTitle; stopButton.onclick = () => state.abortController?.abort(); modelSelect.onchange = syncTerraControl;
$("#open-settings").onclick = openSettings; $("#close-settings").onclick = () => $("#settings-dialog").close(); document.querySelectorAll("[data-settings-tab]").forEach((tab) => tab.onclick = () => activateSettingsTab(tab.dataset.settingsTab));
$("#settings-form").addEventListener("submit", async (event) => { event.preventDefault(); await request("/api/settings", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ system_prompt: $("#system-prompt").value, user_profile: $("#user-profile").value }) }); alert("设置已保存。"); });
(async function boot() { setSidebarCollapsed(state.sidebarCollapsed); setHeaderTitle("新聊天"); await Promise.all([refreshConversations(), loadProviderStatus()]); inputEl.focus(); })().catch((error) => { console.error(error); $("#provider-note").textContent = "启动初始化失败，请刷新页面。"; });