# Phase 0：截至 2026-09-11 的官方可行性记录

## DeepSeek（本轮已实现）

官方资料显示，OpenAI 兼容 API Base URL 为 `https://api.deepseek.com`。当前模型页列出 `deepseek-v4-flash` 与 `deepseek-v4-pro`；小G v0.1 默认使用前者，且始终允许在 `.env` 改 ID，而不是在业务代码里写死。

官方 Chat Completions：`POST /chat/completions`；`stream: true` 使用数据型 SSE，最终 `[DONE]` 前的 chunk 带完整 `usage`。`usage` 包含 `prompt_tokens`、`completion_tokens`、缓存命中/未命中 token。工具调用与 JSON 输出均受支持；上下文长度为 1M，最大输出 384K（具体输出还受请求设置约束）。错误结束原因包括 `stop`、`length`、`content_filter`、`tool_calls`、`insufficient_system_resource`。模型页所示峰时 Flash 价格为每百万 token：缓存命中输入 $0.014、未命中输入 $0.44、输出 $1.32；非峰时半价。并发上限为每账户 Flash 2500，超限 HTTP 429。

实现决定：使用官方 Chat Completions（而非只支持部分模型的 Responses API），`stream_options.include_usage=true`，并且把价格集中在 `backend/pricing.py`。

来源：[Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)；[Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)；[Rate Limit & Isolation](https://api-docs.deepseek.com/quick_start/rate_limit/)。

## OpenAI Codex App Server（仅调查，尚未实现）

官方 App Server 文档确认可行的未来路线：Windows 上先通过官方 Codex CLI / ChatGPT 登录取得官方授权；由小G后端启动 `codex app-server`（默认 stdio，也可监听本机 WebSocket）；每条连接先发送 JSON-RPC `initialize`，随后通知 `initialized`。然后必须调用 `model/list` 获取**实际账户**模型列表，只有确实包含 `gpt-5.6-terra` 时，前端才可宣称 Terra 可用。

会话按 `thread/start` / `thread/resume`，消息按 `turn/start`。回复通过 `item/agentMessage/delta` 逐步到达，`turn/completed` 表示完成；`turn/interrupt` 可停止。App Server 的 `account/read` / `account/rateLimits/read` 可在 Phase 3 时按当前安装版本的 schema 验证账号和额度。官方建议用 `codex app-server generate-json-schema` 或 `generate-ts` 生成与本机 CLI 精确匹配的协议 schema。

本轮故意不启动它、不读取账户、不创建线程，也没有声明 Terra 可用。Phase 3 会先检查 Codex CLI 安装、Windows运行、官方登录和真实 `model/list`，并记录为订阅额度而非 API 费用。不会读取 Cookie、抓取网页私有接口或绕过额度。

来源：[Codex App Server 官方文档](https://learn.chatgpt.com/zh-Hans/docs/app-server)。
