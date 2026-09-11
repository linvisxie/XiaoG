# 小G学习笔记：Phase 0～3

这不是脱离项目的术语表。请一边打开对应文件，一边看这些解释；每个概念都能在小G里找到实际位置。

## 这一次新增了什么

你现在拥有了一个可以在自己电脑运行的聊天产品骨架：浏览器负责展示，Python 负责处理请求，SQLite 负责长期保存。配置好 DeepSeek API Key 后，用户消息会发送到 DeepSeek 官方接口，答案会一小段一小段显示出来，并被写回你的数据库。

核心文件对应关系：

- `frontend/index.html`：页面的“骨架”，定义侧栏、消息区、输入框和设置弹窗。
- `frontend/style.css`：页面的“外观”，决定颜色、间距、手机适配。
- `frontend/app.js`：页面的“行为”，例如点击发送、读取流式回复、加载历史会话。
- `backend/main.py`：后端的总入口，定义网页可以请求的地址，例如 `/health` 和 `/api/conversations/.../chat`。
- `backend/database/db.py`：创建 SQLite 的表；数据库是一个保存在 `data/xiaog.db` 的文件。
- `backend/services/conversation_service.py`：保存、读取、删除会话和消息；它不是模型厂商的一部分。
- `backend/providers/deepseek.py`：唯一知道 DeepSeek HTTP 接口细节的地方。
- `backend/router/model_router.py`：决定选择哪个模型。现在 Auto 明确选择 DeepSeek。
- `backend/providers/codex_app_server.py`：小G与官方 Codex App Server 的 JSON-RPC 通信小客户端；它不读取登录凭据。`backend/providers/terra.py`：只通过该官方客户端调用 GPT-5.6 Terra。
- `backend/tools/`：未来 G-BRIDGE 的安全工具入口，现在不会控制电脑。

## 1. 前端和后端是什么？

**前端**是你眼前的网页。它运行在浏览器里，不能也不应该保存 DeepSeek 密钥。小G的前端只有 `frontend/` 三个文件。

**后端**是后台运行的 Python 程序。它可以安全读取本机 `.env`，访问数据库，替前端调用 DeepSeek。小G的后端是 `backend/`。FastAPI 是帮助 Python 创建网页接口的工具。

一个有用的类比：前端像餐厅里的菜单和服务员；后端像后厨；数据库像账本；DeepSeek 像外部请来的厨师。服务员不需要、也不该拿到付给外部厨师的银行卡密码。

## 2. 从按下“发送”到答案出现，发生了什么？

1. 你在网页输入文字并按 Enter。`frontend/app.js` 的 `sendMessage()` 接到这个动作。
2. JavaScript 向后端发送一个 HTTP `POST` 请求，地址类似 `/api/conversations/会话ID/chat`。请求内容用 JSON 表示，例如 `{"content":"你好","model_preference":"auto"}`。
3. `backend/main.py` 的 `chat()` 收到它，先由 `ConversationService` 把你的原话写进 SQLite。
4. `ConversationService` 读取最近 30 条本地消息；再加上独立保存在 `settings` 表里的 system prompt 和用户资料。这样即使将来切模型，小G仍保留自己的上下文。
5. `ModelRouter` 选中 DeepSeek，`DeepSeekProvider` 从 `.env` 读取密钥并请求官方 `/chat/completions`。
6. DeepSeek 用 SSE（服务器持续推送的 HTTP 数据流）返回许多小片段。Python 一边收到一边转发；JavaScript 一边收到一边把文字追加到气泡里。
7. 完成时，后端把完整答案、实际模型、官方 token usage、估算费用和延迟写入 SQLite。

## 3. API、HTTP、JSON、SSE 分别是什么？

**API** 是程序之间约定好的“服务窗口”。DeepSeek API 规定：你把模型名和消息按某种格式发过去，它按某种格式返回答案。

**HTTP** 是浏览器和后端、后端和 DeepSeek 之间的运输方式。`GET /health` 是“请给我状态”；`POST /chat` 是“请处理这条新消息”。

**JSON** 是一种容易读的文本数据格式，像 `{"role":"user","content":"你好"}`。它不是 Python 专用；网页和很多服务都认识。

**SSE** 是一种 HTTP 流。普通请求像寄一封完整的信；SSE 像电话通话，答案还没说完就可以先听到前半句。这就是“流式输出”。

## 4. 函数、模块和类是什么？

**函数**是给一个小任务起名字的一段代码。例如 `create_conversation()` 专门创建会话；你不需要每次重复写创建数据库记录的细节。

**模块**通常就是一个 Python 文件，用来把相关函数放在一起。比如 `pricing.py` 专门存价格计算，避免把价格散落到聊天代码各处。

**类**像一张“能力说明书”加上它的具体实现。`ModelProvider` 说明每个模型适配器都应该会 `health_check()`、`stream_chat()` 等；`DeepSeekProvider` 是按这张说明书制作的 DeepSeek 版本。未来的 Terra、Claude 不必改小G会话核心，只要也遵守这份说明书。

## 5. 数据库为什么重要？

SQLite 是一个轻量数据库，全部数据装在一个本机文件 `data/xiaog.db`。它比把聊天记录随意写进文本文件更可靠：能按会话查询、删除时自动删除相关消息、重启后保留历史。

本版的重要表：

- `conversations`：每段对话的标题和时间。
- `messages`：每一句用户或小G的话，以及实际使用的 provider/model。
- `settings`：统一人格和用户资料。
- `memories`：长期记忆的预留表。
- `model_usage`：每次模型调用的 token、估价、速度。

## 你可以做的安全练习

1. 不配置密钥直接运行：发送消息会收到“DeepSeek API尚未配置”，程序不应崩溃。
2. 在设置页把用户资料填成“我是历史学本科生”，发送一个相关问题；然后重启，确认资料仍在。
3. 新建两个会话，重启后确认它们仍显示在左边。
4. 打开 `backend/router/model_router.py`，观察 Auto 为什么现在只选 DeepSeek。不要急着把 Terra 选项改成可用：Phase 3 要先走官方认证与 `model/list` 验证。

Phase 3 已完成；下一步需要你确认后才进入 Phase 4（更完整的跨模型切换体验），之后才是 Phase 5 的 Auto Router。

## 6. Phase 3：为什么模型能切换却不会“失忆”？

Terra 不是 DeepSeek 的附属功能。`backend/providers/terra.py` 只知道怎样通过官方 Codex App Server 请求 Terra；它不知道数据库怎样保存你的会话。反过来，`ConversationService` 只负责从 SQLite 读出本地的近期消息、人格和资料；它不关心最终由哪个模型回答。

当你选择 Terra 时，`ModelRouter` 先让 `TerraProvider` 调用官方 `model/list`。若你的账户没有真实返回 `gpt-5.6-terra`，小G会明确说不可用，不会假装调用成功。若可用，`build_canonical_context()` 会把小G自己保存的系统提示、此前用户消息和此前回答，整理成一份上下文后传给 Terra。因此一次对话可以是：DeepSeek 回答第一句，Terra 回答第二句，DeepSeek 理解第三句。

这叫做“适配器”设计：同一套小G会话系统，对不同模型使用不同的通信适配器。好处是以后增加模型时，不必把人格、聊天记录或 API 密钥复制到每个模型文件里。

## 7. 官方登录与订阅额度为什么不放进 .env？

DeepSeek 是 API 服务，所以它需要你自己放在 `.env` 的 API Key。Terra 这次走的是另一条正式路径：本机官方 Codex CLI 已有的 ChatGPT 登录状态。`codex app-server` 自己处理登录，XiaoG只发送标准 JSON-RPC 请求，例如“列出模型”“创建线程”“开始回合”。

因此项目不会、也不应该读取浏览器 Cookie、ChatGPT 网页接口或登录 token。Terra 的账本记录 `subscription`，没有逐次美元成本；如果官方返回套餐窗口使用情况，小G显示它；没有返回就留空。诚实地保留“不知道”，比编造一个 token 或价格更重要。