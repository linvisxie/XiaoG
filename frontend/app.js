const state = {
  conversationId: null, conversationArchived: false, conversationDeleted: false, view: "active",
  abortController: null, generating: false, autoScroll: true, terraEfforts: [],
  terraEffort: localStorage.getItem("xiaog.terraReasoningEffort") || "medium",
  sidebarCollapsed: localStorage.getItem("xiaog.sidebarCollapsed") === "true",
  scrollPositions: new Map(), conversations: [], currentMessages: [], currentTitle: "新聊天", providerStatus: null,
  personalization: {
    theme_mode: "light", color_scheme: "green", assistant_avatar: "default", user_avatar: "default", font_scale: "standard",
    default_model: "deepseek", reasoning_preference: "balanced", chat_density: "comfortable",
    show_message_time: true, enter_to_send: true, animations_enabled: true, ui_language: "zh-CN",
  },
  personalizationSave: Promise.resolve(), menuConversation: null, searchQuery: "", searchResults: [], searchLoading: false, searchRequestId: 0, searchTimer: null,
};
const $ = (selector) => document.querySelector(selector);
const messagesEl = $("#messages"), inputEl = $("#message-input"), sendButton = $("#send-button"), stopButton = $("#stop-button"), modelSelect = $("#model-select"), backToBottom = $("#back-to-bottom");

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail || "请求失败，请稍后重试。"); }
  return response.status === 204 ? null : response.json();
}
function modelLabel(model) { if (model === "gpt-5.6-terra") return "GPT-5.6 Terra"; if ((model || "").toLowerCase().startsWith("deepseek")) return "DeepSeek"; return model || "DeepSeek"; }
function notify(message, type = "system") { const service = window.XiaoGNotification, localized = window.XiaoGI18n?.t(message) || message; if (service?.[type]) return service[type](localized); return service?.system(localized); }
function showToast(message, type = "system") { return notify(message, type); }
function safeHttpUrl(value) { try { const url = new URL(value, window.location.href); return ["http:", "https:"].includes(url.protocol) ? url.href : null; } catch { return null; } }
function renderLinkedText(container, text) {
  const pattern = /\[([^\]\n]+)\]\(([^)\s]+)\)|(https?:\/\/[^\s<]+)/gi; let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > cursor) container.append(document.createTextNode(text.slice(cursor, match.index)));
    const raw = match[0], label = match[1] || match[3], href = safeHttpUrl(match[2] || match[3]);
    if (href) { const link = document.createElement("a"); link.href = href; link.textContent = label; link.target = "_blank"; link.rel = "noopener noreferrer nofollow"; link.dataset.richType = "link"; container.append(link); }
    else container.append(document.createTextNode(raw));
    cursor = match.index + raw.length;
  }
  if (cursor < text.length) container.append(document.createTextNode(text.slice(cursor)));
}
function renderCard(container, templateId, block) {
  const template = $(`#${templateId}`); if (!template) return;
  const fragment = template.content.cloneNode(true), title = fragment.querySelector("strong"), description = fragment.querySelector("p");
  if (title && block.title) title.textContent = block.title;
  if (description && block.description) description.textContent = block.description;
  container.append(fragment);
}
const richContentRenderers = {
  text(container, block) { renderLinkedText(container, block.text || ""); },
  link(container, block) { const href = safeHttpUrl(block.url || ""); if (!href) return; const link = document.createElement("a"); link.href = href; link.textContent = block.label || href; link.target = "_blank"; link.rel = "noopener noreferrer nofollow"; link.dataset.richType = "link"; container.append(link); },
  image(container, block) { renderCard(container, "image-card-template", block); },
  video(container, block) { renderCard(container, "video-card-template", block); },
  file(container, block) { renderCard(container, "file-card-template", block); },
  artifact(container, block) { renderCard(container, "artifact-card-template", block); },
  tool_result(container, block) { renderCard(container, "tool-result-card-template", block); },
};
function renderRichContent(container, content) { container.replaceChildren(); const blocks = Array.isArray(content) ? content : [{ type: "text", text: content || "" }]; for (const block of blocks) (richContentRenderers[block.type] || richContentRenderers.text)(container, block); }

function emptyMessages() {
  if (state.view === "active") {
    messagesEl.innerHTML = `<div class="welcome-state"><div class="empty-logo">G</div><p class="welcome-eyebrow">XiaoG · 你的个人 AI 助手</p><h1>你好，我是小G。</h1><p class="welcome-copy">可以从一个问题、一份资料或一个待办目标开始。</p><div class="welcome-tips"><span>对话会保存在本机</span><span>随时切换 DeepSeek / Terra</span><span>重要信息请再次核对</span></div><div class="example-prompts"><button type="button" data-example-prompt="帮我分析这段资料，并提炼核心观点">让我帮你分析资料<small>粘贴内容后提炼重点</small></button><button type="button" data-coming-soon="附件能力将在 Phase 6.5 开放">上传文件让我处理<small>文件入口已预留</small></button><button type="button" data-example-prompt="帮我把这个目标拆成清晰、可执行的步骤">帮我规划任务<small>拆解目标与下一步</small></button></div></div>`;
    messagesEl.querySelectorAll("[data-example-prompt]").forEach((button) => button.onclick = () => { inputEl.value = button.dataset.examplePrompt; resizeInput(); inputEl.focus(); });
    messagesEl.querySelectorAll("[data-coming-soon]").forEach((button) => button.onclick = () => notify(button.dataset.comingSoon, "system"));
  } else {
    const archived = state.view === "archived";
    messagesEl.innerHTML = `<div class="collection-empty"><div class="collection-empty-icon">${archived ? "▣" : "♲"}</div><h1>${archived ? "暂无已归档会话" : "回收站为空"}</h1><p>${archived ? "归档后的对话会集中显示在这里，并保留全部消息。" : "移入回收站的会话可在永久删除前恢复。"}</p><button type="button" class="secondary" data-return-history>返回历史</button></div>`;
    messagesEl.querySelector("[data-return-history]").onclick = startDraft;
  }
  applyAllAvatars();
}
function isNearBottom() { return messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 96; }
function syncScrollControls() { backToBottom.classList.toggle("hidden", state.autoScroll); }
function scrollToBottom(force = false) { if (force || state.autoScroll) messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "auto" }); }
function rememberScrollPosition() { if (state.conversationId) state.scrollPositions.set(state.conversationId, messagesEl.scrollTop); }
function restoreScrollPosition(id) { const saved = state.scrollPositions.get(id), previous = messagesEl.style.scrollBehavior; messagesEl.style.scrollBehavior = "auto"; messagesEl.scrollTop = saved === undefined ? messagesEl.scrollHeight : saved; messagesEl.style.scrollBehavior = previous; state.autoScroll = isNearBottom(); syncScrollControls(); }
function setSidebarCollapsed(value) { state.sidebarCollapsed = value; $("#app-shell").classList.toggle("sidebar-collapsed", value); $("#sidebar-toggle").textContent = value ? "›" : "‹"; $("#sidebar-toggle").setAttribute("aria-label", value ? "展开历史栏" : "收缩历史栏"); $("#sidebar-toggle").title = value ? "展开历史栏" : "收缩历史栏"; localStorage.setItem("xiaog.sidebarCollapsed", String(value)); }
function setHeaderTitle(title) { state.currentTitle = title || "新聊天"; const displayTitle = window.XiaoGI18n?.t(state.currentTitle) || state.currentTitle; $("#conversation-title").textContent = displayTitle; $("#conversation-title").title = displayTitle; $("#edit-title").disabled = !state.conversationId || state.conversationArchived || state.conversationDeleted || state.generating; }

function avatarPreset(value) { return {
  default: ["G", "preset-default", "小G默认头像"], mario: ["M", "preset-mario", "马里奥头像"], pikachu: ["⚡", "preset-pikachu", "皮卡丘头像"], stitch: ["✦", "preset-stitch", "史迪奇头像"],
  compass: ["◈", "preset-compass", "罗盘头像"], cloud: ["☁", "preset-cloud", "云朵头像"], moon: ["☾", "preset-moon", "月亮头像"], spark: ["✧", "preset-spark", "星光头像"],
}[value] || ["G", "preset-default", "小G默认头像"]; }
function applyAvatarElement(element, role) {
  element.replaceChildren(); element.className = "message-avatar";
  if (role === "user") { element.classList.add("user-avatar"); if (state.personalization.user_avatar.startsWith("data:image/")) { const image = document.createElement("img"); image.src = state.personalization.user_avatar; image.alt = "用户头像"; element.append(image); } else element.textContent = "U"; return; }
  const [text, className, title] = avatarPreset(state.personalization.assistant_avatar); element.classList.add(className); element.textContent = text; element.title = title;
}
function applyAllAvatars() {
  document.querySelectorAll(".message.assistant .message-avatar").forEach((el) => applyAvatarElement(el, "assistant"));
  document.querySelectorAll(".message.user .message-avatar").forEach((el) => applyAvatarElement(el, "user"));
  const emptyLogo = $(".empty-logo"); if (emptyLogo) { const [text, className] = avatarPreset(state.personalization.assistant_avatar); emptyLogo.textContent = text; emptyLogo.className = `empty-logo ${className}`; }
  const preview = $("#assistant-avatar-preview"); if (preview) { const [text, className, title] = avatarPreset(state.personalization.assistant_avatar); preview.textContent = text; preview.className = `assistant-avatar-preview ${className}`; preview.title = title; }
}
function formatMessageTime(value) {
  const date = value ? new Date(value) : new Date(); if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(state.personalization.ui_language === "en" ? "en-US" : "zh-CN", { hour: "2-digit", minute: "2-digit", hour12: false }).format(date);
}
async function copyText(text) { try { await navigator.clipboard.writeText(text); showToast("已复制"); } catch { const helper = document.createElement("textarea"); helper.value = text; document.body.append(helper); helper.select(); document.execCommand("copy"); helper.remove(); showToast("已复制"); } }
function sourcePromptAllowed() { if (state.conversationArchived || state.conversationDeleted) { showToast("请先恢复会话再继续操作"); return false; } return !state.generating; }
function createAssistantActions(content, sourcePrompt) {
  const actions = document.createElement("div"); actions.className = "message-actions";
  const definitions = [["复制", "复制回复", () => copyText(content)], ["↻", "重新生成", () => sourcePromptAllowed() && sendMessage(sourcePrompt)], ["✎", "编辑提示词", () => { if (!sourcePromptAllowed()) return; const edited = prompt("编辑提示词", sourcePrompt); if (edited?.trim()) sendMessage(edited.trim()); }], ["⇄", "切换模型重新回答", () => { if (!sourcePromptAllowed()) return; const next = modelSelect.value === "deepseek" ? "terra" : "deepseek", option = modelSelect.querySelector(`option[value="${next}"]`); if (option?.disabled) return showToast("目标模型当前不可用"); modelSelect.value = next; syncTerraControl(); syncModelStatus(); sendMessage(sourcePrompt); }]];
  for (const [label, title, handler] of definitions) { const button = document.createElement("button"); button.type = "button"; button.textContent = label; button.title = title; button.setAttribute("aria-label", title); button.onclick = handler; actions.append(button); }
  return actions;
}
function setExecutionState(article, executionState, retryPrompt = "") {
  const status = article.querySelector(".message-status"); if (!status) return; status.dataset.state = executionState; status.replaceChildren();
  const labels = { parsing: "正在解析", processing: "正在处理", complete: "完成", failed: "失败" }, dot = document.createElement("span"), label = document.createElement("span"); dot.className = "execution-dot"; label.textContent = labels[executionState]; status.append(dot, label);
  if (executionState === "failed") { const again = document.createElement("button"); again.type = "button"; again.textContent = "Again"; again.onclick = () => sourcePromptAllowed() && sendMessage(retryPrompt); status.append(again); }
}
function messageElement(message, streaming = false, sourcePrompt = "") {
  const article = document.createElement("article"); article.className = `message ${message.role}${streaming ? " streaming" : ""}`; article.tabIndex = -1; if (message.id) article.dataset.messageId = message.id;
  const avatar = document.createElement("div"); applyAvatarElement(avatar, message.role);
  const body = document.createElement("div"); body.className = "message-body"; const meta = document.createElement("div"); meta.className = "message-meta";
  const author = document.createElement("span"); author.textContent = message.role === "assistant" ? "小G" : "你"; const timestamp = document.createElement("time"); timestamp.className = "message-time"; timestamp.dateTime = message.created_at || new Date().toISOString(); timestamp.textContent = formatMessageTime(message.created_at); meta.append(author, timestamp);
  const bubble = document.createElement("div"); bubble.className = "message-content"; const rich = document.createElement("div"); rich.className = "rich-content"; renderRichContent(rich, message.content || ""); bubble.append(rich);
  if (message.role === "assistant") { const badge = document.createElement("span"); badge.className = "message-model"; badge.textContent = modelLabel(message.model); bubble.append(badge); const status = document.createElement("div"); status.className = "message-status"; body.append(meta, bubble, status); if (streaming) setTimeout(() => setExecutionState(article, "parsing", sourcePrompt)); else body.append(createAssistantActions(message.content || "", sourcePrompt)); }
  else body.append(meta, bubble);
  if (message.role === "user") article.append(body, avatar); else article.append(avatar, body); return article;
}
function addMessage(message, streaming = false, forceScroll = false, sourcePrompt = "") { if (messagesEl.querySelector(".empty-state")) messagesEl.innerHTML = ""; const element = messageElement(message, streaming, sourcePrompt); messagesEl.append(element); scrollToBottom(forceScroll); return element; }
function renderMessages(messages) { messagesEl.innerHTML = ""; state.currentMessages = messages; if (!messages.length) return emptyMessages(); let lastUserPrompt = ""; for (const message of messages) { if (message.role === "user") lastUserPrompt = message.content; messagesEl.append(messageElement(message, false, message.role === "assistant" ? lastUserPrompt : "")); } }function conversationRestricted() { return state.conversationArchived || state.conversationDeleted; }
function updateComposerHint() { const english = state.personalization.ui_language === "en", shortcut = state.personalization.enter_to_send ? (english ? "Enter to send, Shift+Enter for a new line" : "Enter 发送，Shift+Enter 换行") : (english ? "Ctrl/⌘+Enter to send, Enter for a new line" : "Ctrl/⌘+Enter 发送，Enter 换行"); $("#send-hint").textContent = english ? `XiaoG can make mistakes · ${shortcut}` : `小G可能会犯错 · ${shortcut}`; if (!conversationRestricted()) inputEl.placeholder = english ? `Message XiaoG… (${shortcut})` : `给小G发消息…（${shortcut}）`; }
function setComposerRestricted() { const restricted = conversationRestricted(), english = state.personalization.ui_language === "en"; inputEl.disabled = restricted || state.generating; sendButton.disabled = restricted || state.generating; inputEl.placeholder = state.conversationDeleted ? (english ? "Trash conversations are read-only. Restore one to continue chatting." : "回收站会话只能查看；恢复后可继续聊天。") : state.conversationArchived ? (english ? "Archived conversations are read-only. Restore one to continue chatting." : "已归档会话只能查看；恢复后可继续聊天。") : ""; updateComposerHint(); }
function setGenerating(value) { state.generating = value; stopButton.classList.toggle("hidden", !value); setComposerRestricted(); setHeaderTitle(state.currentTitle); syncModelStatus(value ? "requesting" : undefined); }
function resizeInput() { inputEl.style.height = "auto"; inputEl.style.height = `${Math.min(inputEl.scrollHeight, 180)}px`; }
function closeConversationMenu() { $("#conversation-menu").classList.add("hidden"); $("#conversation-menu").replaceChildren(); state.menuConversation = null; }
function menuButton(label, handler, danger = false) { const button = document.createElement("button"); button.type = "button"; button.role = "menuitem"; button.textContent = label; if (danger) button.classList.add("danger"); button.onclick = async (event) => { event.stopPropagation(); closeConversationMenu(); try { await handler(); } catch (error) { notify(error.message || "操作失败", "error"); } }; return button; }
function openConversationMenu(conversation, x, y) {
  const menu = $("#conversation-menu"); state.menuConversation = conversation; menu.replaceChildren();
  if (state.view === "active") { menu.append(menuButton(conversation.is_pinned ? "取消置顶" : "置顶", () => setPinned(conversation, !conversation.is_pinned))); menu.append(menuButton("重命名", () => renameConversation(conversation))); menu.append(menuButton("归档", () => archiveConversation(conversation.id))); menu.append(menuButton("删除", () => moveToTrash(conversation), true)); }
  else if (state.view === "archived") { menu.append(menuButton("恢复", () => restoreConversation(conversation.id))); menu.append(menuButton("移入回收站", () => moveToTrash(conversation), true)); menu.append(menuButton("永久删除", () => permanentlyDelete(conversation), true)); }
  else { menu.append(menuButton("恢复", () => restoreDeletedConversation(conversation.id))); menu.append(menuButton("永久删除", () => permanentlyDelete(conversation), true)); }
  menu.classList.remove("hidden"); const bounds = menu.getBoundingClientRect(); menu.style.left = `${Math.max(8, Math.min(x, window.innerWidth - bounds.width - 10))}px`; menu.style.top = `${Math.max(8, Math.min(y, window.innerHeight - bounds.height - 10))}px`;
}
function searchMatchLabel(type) { return { title: "标题", user_message: "用户消息", assistant_message: "AI 消息" }[type] || "会话"; }
function renderSearchResults(target) {
  if (state.searchLoading) { const note = document.createElement("p"); note.className = "conversation-empty search-results-status"; note.textContent = "正在搜索…"; target.append(note); return; }
  for (const result of state.searchResults) {
    const item = document.createElement("button"); item.type = "button"; item.className = "search-result"; item.dataset.conversationId = result.conversation_id; if (result.message_id) item.dataset.messageId = result.message_id; item.title = `打开“${result.conversation_title}”`;
    const title = document.createElement("strong"); title.className = "search-result-title"; title.textContent = result.conversation_title;
    const meta = document.createElement("span"); meta.className = "search-result-meta";
    const kind = document.createElement("span"); kind.className = "search-result-kind"; kind.textContent = searchMatchLabel(result.match_type); meta.append(kind);
    if (result.is_archived) { const archived = document.createElement("span"); archived.className = "search-result-archived"; archived.textContent = "已归档"; meta.append(archived); }
    item.append(title, meta);
    if (result.snippet) { const snippet = document.createElement("span"); snippet.className = "search-result-snippet"; snippet.textContent = result.snippet; item.append(snippet); }
    item.onclick = () => openSearchResult(result).catch((error) => notify(error.message || "无法打开搜索结果", "error"));
    target.append(item);
  }
  if (!state.searchResults.length) { const note = document.createElement("p"); note.className = "conversation-empty search-results-status"; note.textContent = "没有匹配的会话或消息"; target.append(note); }
}
function renderConversationList() {
  const target = $("#conversation-list"); target.innerHTML = "";
  const headings = { active: "历史对话", archived: "已归档", trash: "回收站" }, searching = Boolean(state.searchQuery);
  $("#conversation-heading").textContent = searching ? "搜索结果" : headings[state.view]; $("#open-archived").classList.toggle("active", state.view === "archived" && !searching); $("#open-trash").classList.toggle("active", state.view === "trash" && !searching); $("#back-to-history").classList.toggle("hidden", state.view === "active" && !searching); $("#empty-trash").classList.toggle("hidden", state.view !== "trash" || !state.conversations.length || searching);
  if (searching) { renderSearchResults(target); return; }
  for (const conversation of state.conversations) {
    const item = document.createElement("div"); item.className = `conversation ${conversation.id === state.conversationId ? "active" : ""}`; item.oncontextmenu = (event) => { event.preventDefault(); openConversationMenu(conversation, event.clientX, event.clientY); };
    const open = document.createElement("button"); open.className = "conversation-name"; open.title = conversation.title;
    if (state.view === "active" && conversation.is_pinned) { const pin = document.createElement("span"); pin.className = "pin-mark"; pin.textContent = "◆"; pin.setAttribute("aria-label", "已置顶"); open.append(pin); }
    open.append(document.createTextNode(conversation.title)); open.onclick = () => openConversation(conversation.id);
    const more = document.createElement("button"); more.className = "conversation-more"; more.textContent = "⋯"; more.title = "更多操作"; more.setAttribute("aria-label", `${conversation.title}的更多操作`); more.onclick = (event) => { event.stopPropagation(); const rect = more.getBoundingClientRect(); openConversationMenu(conversation, rect.right, rect.bottom + 4); }; item.append(open, more); target.append(item);
  }
  if (!state.conversations.length) { const note = document.createElement("p"); note.className = "conversation-empty"; note.textContent = state.view === "archived" ? "暂无已归档会话" : state.view === "trash" ? "回收站为空" : "暂无历史会话"; target.append(note); }
}
function clearGlobalSearch() {
  clearTimeout(state.searchTimer); state.searchRequestId += 1; state.searchQuery = ""; state.searchResults = []; state.searchLoading = false; $("#history-search").value = "";
}
function scheduleGlobalSearch() {
  const query = $("#history-search").value.trim(), requestId = ++state.searchRequestId; clearTimeout(state.searchTimer); state.searchQuery = query;
  if (!query) { state.searchResults = []; state.searchLoading = false; renderConversationList(); return; }
  state.searchLoading = true; renderConversationList();
  state.searchTimer = window.setTimeout(async () => {
    try {
      const result = await request(`/api/search?query=${encodeURIComponent(query)}`);
      if (requestId !== state.searchRequestId) return;
      state.searchResults = result.results || [];
    } catch (error) {
      if (requestId !== state.searchRequestId) return;
      state.searchResults = []; notify(error.message || "搜索失败", "error");
    } finally {
      if (requestId === state.searchRequestId) { state.searchLoading = false; renderConversationList(); }
    }
  }, 180);
}
async function openSearchResult(result) {
  if (state.generating) return;
  state.view = result.is_archived ? "archived" : "active";
  await openConversation(result.conversation_id, result.message_id || null);
}
function locateMessage(messageId) {
  const target = Array.from(messagesEl.querySelectorAll("[data-message-id]")).find((element) => element.dataset.messageId === messageId);
  if (!target) { notify("未能定位匹配消息", "error"); restoreScrollPosition(state.conversationId); return; }
  const top = target.getBoundingClientRect().top - messagesEl.getBoundingClientRect().top + messagesEl.scrollTop - 22;
  messagesEl.scrollTo({ top: Math.max(0, top), behavior: "auto" }); state.autoScroll = false; syncScrollControls(); target.focus({ preventScroll: true }); target.classList.add("search-target"); window.setTimeout(() => target.classList.remove("search-target"), 1800);
}
async function refreshConversations() { const query = state.view === "archived" ? "archived=true" : state.view === "trash" ? "deleted=true" : ""; state.conversations = await request(`/api/conversations${query ? `?${query}` : ""}`); renderConversationList(); }
function startDraft() { if (state.generating) return; rememberScrollPosition(); clearGlobalSearch(); state.view = "active"; state.conversationId = null; state.conversationArchived = false; state.conversationDeleted = false; state.currentMessages = []; state.autoScroll = true; emptyMessages(); setHeaderTitle("新聊天"); setComposerRestricted(); refreshConversations().catch(console.error); inputEl.focus(); }
async function openConversation(id, targetMessageId = null) { if (state.generating) return; rememberScrollPosition(); const conversation = await request(`/api/conversations/${id}`); state.conversationId = id; state.conversationArchived = Boolean(conversation.archived_at); state.conversationDeleted = Boolean(conversation.deleted_at); renderMessages(conversation.messages); setHeaderTitle(conversation.title); setComposerRestricted(); await refreshConversations(); if (targetMessageId) locateMessage(targetMessageId); else restoreScrollPosition(id); }
function showView(view) { if (state.generating) return; clearGlobalSearch(); return showConversationView(view); }
async function showConversationView(view) { rememberScrollPosition(); state.view = view; state.conversationId = null; state.conversationArchived = view === "archived"; state.conversationDeleted = view === "trash"; state.currentMessages = []; state.autoScroll = true; emptyMessages(); setHeaderTitle(view === "archived" ? "已归档会话" : view === "trash" ? "回收站" : "新聊天"); setComposerRestricted(); await refreshConversations(); }
async function setPinned(conversation, pinned) { await request(`/api/conversations/${conversation.id}/${pinned ? "pin" : "unpin"}`, { method: "POST" }); notify(pinned ? "会话已置顶" : "已取消置顶", "success"); await refreshConversations(); }
async function renameConversation(conversation) { const title = prompt("修改会话标题", conversation.title); if (title === null || !title.trim()) return; const updated = await request(`/api/conversations/${conversation.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: title.trim() }) }); if (state.conversationId === conversation.id) setHeaderTitle(updated.title); notify("会话已重命名", "success"); await refreshConversations(); }
async function archiveConversation(id) { await request(`/api/conversations/${id}/archive`, { method: "POST" }); notify("会话已归档", "success"); if (state.conversationId === id) startDraft(); else await refreshConversations(); }
async function restoreConversation(id) { await request(`/api/conversations/${id}/restore`, { method: "POST" }); notify("会话已恢复", "success"); await refreshConversations(); }
async function moveToTrash(conversation) { if (!confirm(`将“${conversation.title}”移入回收站？`)) return; await request(`/api/conversations/${conversation.id}`, { method: "DELETE" }); notify("会话已移入回收站", "success"); if (state.conversationId === conversation.id) startDraft(); else await refreshConversations(); }
async function restoreDeletedConversation(id) { await request(`/api/conversations/${id}/restore-deleted`, { method: "POST" }); notify("会话已从回收站恢复", "success"); await refreshConversations(); }
async function permanentlyDelete(conversation) { if (!confirm(`永久删除“${conversation.title}”？此操作无法撤销。`)) return; await request(`/api/conversations/${conversation.id}/permanent`, { method: "DELETE" }); notify("会话已永久删除", "success"); if (state.conversationId === conversation.id) await showView(state.view); else await refreshConversations(); }
async function emptyTrash() { if (!state.conversations.length || !confirm("永久删除回收站中的全部会话？此操作无法撤销。")) return; const result = await request("/api/trash", { method: "DELETE" }); notify(`已永久删除 ${result.deleted} 个会话`, "success"); await showView("trash"); }
async function updateCurrentTitle() { const conversation = state.conversations.find((item) => item.id === state.conversationId) || { id: state.conversationId, title: state.currentTitle }; if (!conversation.id || conversationRestricted() || state.generating) return; await renameConversation(conversation); }

function renderTerraEfforts(details = {}) {
  const supported = new Set(details.supported_reasoning_efforts || []), options = [["low", "低"], ["medium", "中"], ["high", "高"]].filter(([value]) => supported.has(value)); state.terraEfforts = options.map(([value]) => value);
  if (!state.terraEfforts.includes(state.terraEffort)) state.terraEffort = state.terraEfforts.includes(details.default_reasoning_effort) ? details.default_reasoning_effort : state.terraEfforts[0] || ""; if (state.terraEffort) localStorage.setItem("xiaog.terraReasoningEffort", state.terraEffort);
  const target = $("#terra-effort-options"); target.innerHTML = "";
  for (const [value, label] of options) { const button = document.createElement("button"); button.type = "button"; button.className = `effort-option ${value === state.terraEffort ? "active" : ""}`; button.textContent = label; button.setAttribute("aria-pressed", String(value === state.terraEffort)); button.onclick = () => { state.terraEffort = value; localStorage.setItem("xiaog.terraReasoningEffort", value); renderTerraEfforts({ supported_reasoning_efforts: state.terraEfforts, default_reasoning_effort: value }); }; target.append(button); }
  syncTerraControl();
}
function syncTerraControl() { $("#terra-effort-control").classList.toggle("reserved", modelSelect.value !== "terra" || !state.terraEfforts.length); }
function syncModelStatus(forcedState) { const key = modelSelect.value, label = key === "terra" ? "Terra" : "DeepSeek", available = state.providerStatus?.[key]?.available !== false, status = forcedState || (available ? "available" : "error"), element = $("#model-status"); element.className = `model-status ${status}`; $("#model-status-label").textContent = label; }
async function loadProviderStatus() { try { const status = await request("/api/provider-status"); state.providerStatus = status; const terra = modelSelect.querySelector('option[value="terra"]'), defaultTerra = $("#default-model-setting")?.querySelector('option[value="terra"]'); terra.disabled = !status.terra.available; if (defaultTerra) defaultTerra.disabled = !status.terra.available; terra.textContent = status.terra.available ? "GPT-5.6 Terra" : "当前账户未提供 GPT-5.6 Terra"; if (!status.terra.available && modelSelect.value === "terra") modelSelect.value = "deepseek"; $("#provider-note").textContent = status.terra.available ? "Terra 可用；可在右侧切换模型。" : status.terra.message; renderTerraEfforts(status.terra.details || {}); syncModelStatus(); } catch { $("#provider-note").textContent = "无法读取模型状态。"; syncModelStatus("error"); notify("模型连接状态读取失败", "error"); } }
async function sendMessage(content) {
  if (!content.trim() || state.generating || conversationRestricted()) return;
  if (!state.conversationId) { const conversation = await request("/api/conversations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) }); state.conversationId = conversation.id; state.currentTitle = conversation.title; await refreshConversations(); }
  state.autoScroll = true; syncScrollControls(); const cleanContent = content.trim(), createdAt = new Date().toISOString(); state.currentMessages.push({ role: "user", content: cleanContent, created_at: createdAt }); addMessage({ role: "user", content: cleanContent, created_at: createdAt }, false, true); inputEl.value = ""; resizeInput(); setGenerating(true);
  const assistant = addMessage({ role: "assistant", content: "", model: modelSelect.value === "terra" ? "gpt-5.6-terra" : "DeepSeek" }, true, true, cleanContent), rich = assistant.querySelector(".rich-content"), modelBadge = assistant.querySelector(".message-model"); state.abortController = new AbortController(); let received = "", failed = false;
  try {
    const response = await fetch(`/api/conversations/${state.conversationId}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content: cleanContent, model_preference: modelSelect.value, terra_reasoning_effort: modelSelect.value === "terra" ? state.terraEffort : null }), signal: state.abortController.signal });
    if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail || "消息发送失败。"); }
    const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = "";
    while (true) {
      const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const blocks = buffer.split("\n\n"); buffer = blocks.pop();
      for (const block of blocks) {
        const lines = block.split("\n"), event = lines.find((line) => line.startsWith("event:"))?.slice(6).trim(), raw = lines.find((line) => line.startsWith("data:"))?.slice(5).trim(); if (!event || !raw) continue; const data = JSON.parse(raw);
        if (event === "meta") { modelBadge.textContent = data.display_name || data.model; setExecutionState(assistant, "processing", cleanContent); }
        if (event === "delta") { received += data.content; renderRichContent(rich, received); const cursor = document.createElement("span"); cursor.className = "cursor"; rich.append(cursor); scrollToBottom(); }
        if (event === "done") setExecutionState(assistant, "complete", cleanContent);
        if (event === "error") { failed = true; renderRichContent(rich, data.message); assistant.classList.add("error"); setExecutionState(assistant, "failed", cleanContent); notify(data.message || "模型连接失败", "error"); }
      }
    }
  } catch (error) { failed = true; const message = error.name === "AbortError" ? "已停止生成。" : error.message || "网络连接失败，请稍后重试。"; renderRichContent(rich, message); assistant.classList.add("error"); setExecutionState(assistant, "failed", cleanContent); notify(message, error.name === "AbortError" ? "system" : "error"); }
  finally {
    rich.querySelector(".cursor")?.remove(); assistant.classList.remove("streaming");
    if (!failed && received) { state.currentMessages.push({ role: "assistant", content: received, model: modelBadge.textContent, created_at: new Date().toISOString() }); assistant.querySelector(".message-body").append(createAssistantActions(received, cleanContent)); }
    state.abortController = null; setGenerating(false); syncModelStatus(failed ? "error" : "available");
    if (state.conversationId) { const conversation = await request(`/api/conversations/${state.conversationId}`); setHeaderTitle(conversation.title); }
    await refreshConversations(); inputEl.focus();
  }
}

function normalizePersonalization(value = {}) {
  const boolValue = (candidate, fallback) => typeof candidate === "boolean" ? candidate : candidate === "true" ? true : candidate === "false" ? false : fallback;
  return {
    theme_mode: value.theme_mode === "dark" ? "dark" : "light",
    color_scheme: ["green", "blue", "purple"].includes(value.color_scheme) ? value.color_scheme : "green",
    assistant_avatar: ["default", "mario", "pikachu", "stitch", "compass", "cloud", "moon", "spark"].includes(value.assistant_avatar) ? value.assistant_avatar : "default",
    user_avatar: value.user_avatar?.startsWith("data:image/") ? value.user_avatar : "default",
    font_scale: ["small", "standard", "large", "xlarge"].includes(value.font_scale) ? value.font_scale : "standard",
    default_model: ["deepseek", "terra"].includes(value.default_model) ? value.default_model : "deepseek",
    reasoning_preference: ["fast", "balanced", "deep"].includes(value.reasoning_preference) ? value.reasoning_preference : "balanced",
    chat_density: value.chat_density === "compact" ? "compact" : "comfortable",
    show_message_time: boolValue(value.show_message_time, true),
    enter_to_send: boolValue(value.enter_to_send, true),
    animations_enabled: boolValue(value.animations_enabled, true),
    ui_language: value.ui_language === "en" ? "en" : "zh-CN",
  };
}
function applyPersonalization(value, options = {}) {
  state.personalization = normalizePersonalization(value);
  const root = document.documentElement;
  root.dataset.themeMode = state.personalization.theme_mode;
  root.dataset.colorScheme = state.personalization.color_scheme;
  root.dataset.fontScale = state.personalization.font_scale;
  root.dataset.chatDensity = state.personalization.chat_density;
  root.dataset.showMessageTime = String(state.personalization.show_message_time);
  root.dataset.animations = state.personalization.animations_enabled ? "on" : "off";
  window.XiaoGI18n?.setLanguage(state.personalization.ui_language);
  setHeaderTitle(state.currentTitle);
  if (options.selectDefault) {
    const option = modelSelect.querySelector(`option[value="${state.personalization.default_model}"]`);
    if (option && !option.disabled) { modelSelect.value = state.personalization.default_model; syncTerraControl(); syncModelStatus(); }
  }
  renderPersonalizationControls(); applyAllAvatars(); updateComposerHint();
}
function markSelected(selector, dataKey, selectedValue) {
  document.querySelectorAll(selector).forEach((button) => { const selected = button.dataset[dataKey] === selectedValue; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); });
}
function renderPersonalizationControls() {
  document.querySelectorAll('input[name="theme-mode"]').forEach((input) => { input.checked = input.value === state.personalization.theme_mode; });
  markSelected("#color-scheme-options [data-color-scheme]", "colorScheme", state.personalization.color_scheme);
  markSelected("#assistant-avatar-options [data-assistant-avatar]", "assistantAvatar", state.personalization.assistant_avatar);
  markSelected("#font-scale-options [data-font-scale]", "fontScale", state.personalization.font_scale);
  markSelected("#reasoning-preference-options [data-reasoning-preference]", "reasoningPreference", state.personalization.reasoning_preference);
  markSelected("#chat-density-options [data-chat-density]", "chatDensity", state.personalization.chat_density);
  const defaultModel = $("#default-model-setting"); if (defaultModel) defaultModel.value = state.personalization.default_model;
  const showTime = $("#show-message-time"); if (showTime) showTime.checked = state.personalization.show_message_time;
  const enterSend = $("#enter-to-send"); if (enterSend) enterSend.checked = state.personalization.enter_to_send;
  const animations = $("#animations-enabled"); if (animations) animations.checked = state.personalization.animations_enabled;
  const language = $("#ui-language-setting"); if (language) language.value = state.personalization.ui_language;
  const preview = $("#user-avatar-preview"); if (preview) { preview.replaceChildren(); if (state.personalization.user_avatar.startsWith("data:image/")) { const image = document.createElement("img"); image.src = state.personalization.user_avatar; image.alt = "用户头像预览"; preview.append(image); } else preview.textContent = "U"; }
}
async function loadPersonalization() { applyPersonalization(await request("/api/settings/personalization"), { selectDefault: true }); }
function savePersonalization(successMessage = "设置保存成功") {
  const snapshot = { ...state.personalization }, status = $("#personalization-status"); if (status) status.textContent = "正在保存…";
  state.personalizationSave = state.personalizationSave.catch(() => undefined).then(async () => {
    await request("/api/settings/personalization", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(snapshot) });
    if (status) status.textContent = "设置已保存到这台电脑。"; notify(successMessage, "success");
  }).catch((error) => { console.error(error); if (status) status.textContent = "未能保存设置，请稍后重试。"; notify(error.message || "设置保存失败", "error"); });
  return state.personalizationSave;
}
function choosePersonalization(change, successMessage) { applyPersonalization({ ...state.personalization, ...change }, { selectDefault: Object.hasOwn(change, "default_model") }); return savePersonalization(successMessage); }
async function cropAvatar(file) {
  if (!file || !file.type.match(/^image\/(png|jpeg|webp)$/)) throw new Error("仅支持 PNG、JPEG 或 WebP 图片。");
   if (file.size > 10 * 1024 * 1024) throw new Error("图片不能超过 10MB。");
  const url = URL.createObjectURL(file);
  try {
    const image = new Image(); image.src = url; await image.decode();
    if (!image.naturalWidth || !image.naturalHeight) throw new Error("无法读取这张图片。");
    const side = Math.min(image.naturalWidth, image.naturalHeight), sourceX = (image.naturalWidth - side) / 2, sourceY = (image.naturalHeight - side) / 2, canvas = document.createElement("canvas");
    canvas.width = 256; canvas.height = 256; const context = canvas.getContext("2d"); if (!context) throw new Error("当前浏览器无法处理头像。");
    context.drawImage(image, sourceX, sourceY, side, side, 0, 0, 256, 256); const result = canvas.toDataURL("image/webp", 0.86);
    if (result.length > 400000) throw new Error("处理后的头像仍然过大，请更换图片。"); return result;
  } finally { URL.revokeObjectURL(url); }
}function renderAbout(info) {
  const content = $("#about-content"); content.innerHTML = ""; const rows = [["名称", info.name], ["当前版本", info.version], ["Commit", info.commit], ["当前阶段", info.phase], ["搭载模型", (info.models || []).join(" · ")]], meta = document.createElement("dl"); meta.className = "about-meta";
  rows.forEach(([label, value]) => { const term = document.createElement("dt"), detail = document.createElement("dd"); term.textContent = label; detail.textContent = value || "—"; meta.append(term, detail); });
  const capabilities = document.createElement("div"); capabilities.className = "about-block"; capabilities.innerHTML = "<h4>当前能力</h4>"; const list = document.createElement("ul"); (info.capabilities || []).forEach((item) => { const line = document.createElement("li"); line.textContent = item; list.append(line); }); capabilities.append(list);
  const limitations = document.createElement("div"); limitations.className = "about-block"; limitations.innerHTML = "<h4>当前限制</h4>"; const limitationList = document.createElement("ul"); (info.limitations || []).forEach((item) => { const line = document.createElement("li"); line.textContent = item; limitationList.append(line); }); limitations.append(limitationList);
  const log = document.createElement("div"); log.className = "about-block"; log.innerHTML = "<h4>更新日志</h4>"; (info.changelog || []).forEach((entry) => { const item = document.createElement("div"), title = document.createElement("strong"), entries = document.createElement("ul"); item.className = "changelog-item"; title.textContent = `${entry.version} · ${entry.title}`; (entry.items || []).forEach((text) => { const line = document.createElement("li"); line.textContent = text; entries.append(line); }); item.append(title, entries); log.append(item); }); content.append(meta, capabilities, limitations, log);
}
async function openSettings() { const [settings, about, personalization] = await Promise.all([request("/api/settings"), request("/api/about"), request("/api/settings/personalization")]); $("#system-prompt").value = settings.system_prompt; $("#user-profile").value = settings.user_profile; renderAbout(about); applyPersonalization(personalization); activateSettingsTab("personalization"); $("#settings-dialog").showModal(); }
function activateSettingsTab(name) { document.querySelectorAll("[data-settings-tab]").forEach((tab) => tab.classList.toggle("active", tab.dataset.settingsTab === name)); document.querySelectorAll("[data-settings-panel]").forEach((panel) => panel.classList.toggle("active", panel.dataset.settingsPanel === name)); }

messagesEl.addEventListener("scroll", () => { rememberScrollPosition(); state.autoScroll = isNearBottom(); syncScrollControls(); });
backToBottom.onclick = () => { state.autoScroll = true; scrollToBottom(true); syncScrollControls(); };
$("#chat-form").addEventListener("submit", (event) => { event.preventDefault(); sendMessage(inputEl.value); });
inputEl.addEventListener("input", resizeInput);
inputEl.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" || event.shiftKey) return;
  const shouldSend = state.personalization.enter_to_send || event.ctrlKey || event.metaKey;
  if (shouldSend) { event.preventDefault(); $("#chat-form").requestSubmit(); }
});
$("#new-chat").onclick = startDraft; $("#open-archived").onclick = () => showView("archived"); $("#open-trash").onclick = () => showView("trash"); $("#back-to-history").onclick = startDraft; $("#empty-trash").onclick = emptyTrash; $("#history-search").addEventListener("input", scheduleGlobalSearch); $("#sidebar-toggle").onclick = () => setSidebarCollapsed(!state.sidebarCollapsed); $("#edit-title").onclick = updateCurrentTitle; stopButton.onclick = () => state.abortController?.abort(); modelSelect.onchange = () => { syncTerraControl(); syncModelStatus(); };
$("#open-settings").onclick = () => openSettings().catch((error) => notify(error.message || "设置加载失败", "error")); $("#close-settings").onclick = () => $("#settings-dialog").close(); document.querySelectorAll("[data-settings-tab]").forEach((tab) => tab.onclick = () => activateSettingsTab(tab.dataset.settingsTab));
document.querySelectorAll('input[name="theme-mode"]').forEach((input) => input.onchange = () => choosePersonalization({ theme_mode: input.value }));
document.querySelectorAll("#color-scheme-options [data-color-scheme]").forEach((button) => button.onclick = () => choosePersonalization({ color_scheme: button.dataset.colorScheme }));
document.querySelectorAll("#assistant-avatar-options [data-assistant-avatar]").forEach((button) => button.onclick = () => choosePersonalization({ assistant_avatar: button.dataset.assistantAvatar }));
document.querySelectorAll("#font-scale-options [data-font-scale]").forEach((button) => button.onclick = () => choosePersonalization({ font_scale: button.dataset.fontScale }));
document.querySelectorAll("#reasoning-preference-options [data-reasoning-preference]").forEach((button) => button.onclick = () => choosePersonalization({ reasoning_preference: button.dataset.reasoningPreference }));
document.querySelectorAll("#chat-density-options [data-chat-density]").forEach((button) => button.onclick = () => choosePersonalization({ chat_density: button.dataset.chatDensity }));
$("#default-model-setting").onchange = (event) => choosePersonalization({ default_model: event.target.value });
$("#show-message-time").onchange = (event) => choosePersonalization({ show_message_time: event.target.checked });
$("#enter-to-send").onchange = (event) => choosePersonalization({ enter_to_send: event.target.checked });
$("#animations-enabled").onchange = (event) => choosePersonalization({ animations_enabled: event.target.checked });
$("#ui-language-setting").onchange = (event) => choosePersonalization({ ui_language: event.target.value }, "界面语言已保存");
$("#reset-assistant-avatar").onclick = () => choosePersonalization({ assistant_avatar: "default" });
$("#user-avatar-input").onchange = async (event) => { const file = event.target.files?.[0]; if (!file) return; try { const avatar = await cropAvatar(file); await choosePersonalization({ user_avatar: avatar }, "头像已裁剪并保存"); } catch (error) { notify(error.message || "头像上传失败", "error"); } finally { event.target.value = ""; } };
$("#reset-user-avatar").onclick = async () => { await choosePersonalization({ user_avatar: "default" }, "用户头像已删除"); };
document.querySelectorAll("[data-coming-soon]").forEach((button) => button.onclick = () => notify(button.dataset.comingSoon, "system"));
$("#settings-form").addEventListener("submit", async (event) => { event.preventDefault(); try { await request("/api/settings", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ system_prompt: $("#system-prompt").value, user_profile: $("#user-profile").value }) }); notify("系统设置保存成功", "success"); } catch (error) { notify(error.message || "系统设置保存失败", "error"); } });document.addEventListener("click", (event) => { if (!event.target.closest("#conversation-menu") && !event.target.closest(".conversation-more")) closeConversationMenu(); }); document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeConversationMenu(); }); window.addEventListener("resize", closeConversationMenu);

(async function boot() { setSidebarCollapsed(state.sidebarCollapsed); setHeaderTitle("新聊天"); emptyMessages(); await Promise.all([refreshConversations(), loadProviderStatus(), loadPersonalization()]); inputEl.focus(); })().catch((error) => { console.error(error); $("#provider-note").textContent = "启动初始化失败，请刷新页面。"; notify(error.message || "XiaoG 初始化失败", "error"); });