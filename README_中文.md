# 小G / XiaoG v0.1

## 核心回归测试

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe .\run_core_tests.py
```

该命令只运行本地、确定性的核心回归；不会发送真实 Provider 请求，也不会改动 `data/xiaog.db`。

这是一个属于你的个人 AI 助手，而不是某一家模型的聊天网页。小G自己保存人格、用户资料、会话和长期记忆接口；DeepSeek 只是当前接入的第一个“大脑”。

当前版本已完成 Phase 0、1、2、3：本机聊天界面、SQLite 历史会话、统一人格、DeepSeek 官方 API 流式回答、Token/费用记录，以及通过官方 Codex App Server 接入的 GPT-5.6 Terra。

## 第一次启动（Windows）

1. 安装 [Python 3.11 或更新版本](https://www.python.org/downloads/windows/)，安装时勾选 **Add python.exe to PATH**。
2. 双击 `D:\XiaoG\setup_windows.bat`。它会在 `D:\XiaoG\.venv` 创建独立运行环境、安装依赖、创建 `.env` 和数据库。
3. 用记事本打开 `D:\XiaoG\.env`，在这一行等号后粘贴你自己的密钥：`DEEPSEEK_API_KEY=你的密钥`。
4. 双击 `D:\XiaoG\run_windows.bat`。浏览器会自动打开 `http://127.0.0.1:8000`。

以后只需双击 `run_windows.bat`。关闭它弹出的命令窗口会停止后端。

## 安全说明

- 密钥只应放在 `.env`；它被 `.gitignore` 排除，不会进入 Git。
- 网页和 JavaScript 从不读取或显示 API Key；浏览器访问 `/ .env`（去掉其中空格后即 `/.env`）不会被 FastAPI 静态目录提供。
- SQLite 数据库在 `D:\XiaoG\data\xiaog.db`，日志在 `D:\XiaoG\data\logs\xiaog.log`。日志不记录完整 API Key。
- 请不要把 `.env` 发给任何人或上传到 GitHub。

## 当前模型与费用

默认模型可由 `.env` 中的 `DEEPSEEK_MODEL_ID` 指定；初始值是官方当前模型 `deepseek-v4-flash`。请求使用 DeepSeek 官方 OpenAI 兼容 Chat Completions API 和 SSE 流；每次请求末尾的官方 usage 会被保存。

`backend/pricing.py` 是唯一的估价位置。价格会变动，当前代码采用 2026-09-11 查到的 DeepSeek V4 Flash 峰时美元价格；它只是本地估算，不替代 DeepSeek 账单。

## 项目结构

```text
D:\XiaoG
├─ backend/                 FastAPI 后端与小G核心
│  ├─ providers/            模型适配层（DeepSeek / Terra预留）
│  ├─ database/             SQLite 表与连接
│  ├─ services/             会话和记忆服务
│  ├─ router/               模型选择策略
│  └─ tools/                未来 G-BRIDGE 工具注册表
├─ frontend/                浏览器界面（HTML/CSS/JS）
├─ data/                    你的本机数据库和日志
├─ .env                     你的私密配置（本机创建，不提交）
├─ setup_windows.bat        第一次安装
└─ run_windows.bat          日常启动
```

## 已知边界

- GPT-5.6 Terra 已通过官方 Codex App Server 接入。只有当前 ChatGPT 账户的 `model/list` 真实包含 `gpt-5.6-terra` 时，前端才可选；否则显示“当前账户未提供 GPT-5.6 Terra”。
- Auto 目前仍透明地默认选择 DeepSeek；复杂任务自动路由留到 Phase 5。
- 长期记忆表和服务边界已创建；语义检索/向量数据库留到 Phase 6。
- 当前没有真实系统控制工具，避免在没有用户确认机制时触碰 Windows。

## 官方资料（Phase 0 调查）

- DeepSeek 的 [模型、上下文、功能与价格](https://api-docs.deepseek.com/quick_start/pricing/)；[Chat Completions 流、usage、工具调用与错误结束原因](https://api-docs.deepseek.com/api/create-chat-completion/)；[并发与 429 行为](https://api-docs.deepseek.com/quick_start/rate_limit/)。
- OpenAI 官方 [Codex App Server 文档](https://learn.chatgpt.com/zh-Hans/docs/app-server)：`codex app-server` 采用 JSON-RPC，先 `initialize` / `initialized`，再 `model/list` 检查账户实际模型，并通过 `thread/start`、`turn/start` 和 `item/agentMessage/delta` 管理流式对话。Phase 3 将按此路径验证 Windows 上的 CLI、登录和实际 `gpt-5.6-terra` 可用性，绝不使用 Cookie 或私有接口。

## GPT-5.6 Terra（Phase 3）

Terra 不使用 OpenAI API Key，也不使用网页 Cookie 或私有接口。XiaoG 在本机启动官方 `codex app-server`，由已登录的官方 Codex CLI 处理 ChatGPT 身份验证；项目不会读取、保存或输出其登录凭据。

启动网页时，小G会通过官方 JSON-RPC 调用 `account/read`、`model/list` 和可用时的 `account/rateLimits/read`。只有 `model/list` 实际返回 `gpt-5.6-terra`，下拉菜单才会启用 Terra。聊天采用 `thread/start`、`turn/start` 与 `item/agentMessage/delta` 流式事件；XiaoG自己的 SQLite 会话历史会被规范化地传入，因此 DeepSeek 与 Terra 切换后仍能理解同一会话。

Terra 的 `model_usage` 记录为 `provider = openai_codex`、`billing_type = subscription`、`estimated_cost = NULL`。官方 App Server 本次没有提供逐次 token usage，所以不会伪造 input/output token 或美元价格；若账户允许读取套餐额度，模型状态接口会显示该额度。
