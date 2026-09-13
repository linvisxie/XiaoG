# XiaoG / 小G Master Roadmap v2

**版本日期：2026-09-12**  
**定位：当前唯一主路线图 / 新对话接力基线**  
**当前开发状态：Phase 5 进行中；v0.4.0 已完成；v0.4.1 已下发给 Codex，但因 Codex 额度不足暂停执行。**  
**重要：恢复额度后继续 v0.4.1，不重新设计、不跳到 v0.4.2。**

---

# 0. 这份 Roadmap v2 的用途

这份文件取代 2026-09-11 旧版 Master Roadmap 作为后续讨论的主基线。

它合并：

1. 旧 Master Roadmap / Part 2 中仍有效的架构和阶段规划；
2. v0.3.3 ～ v0.4.0 的实际开发进展；
3. 之后新增并已明确确认的需求；
4. 用户多次要求“记住、不要遗漏”的硬要求；
5. 已确认的工程基础建设；
6. 已确认的 16GB 受控双 Codex 并行开发节点；
7. 已明确取消、不再纳入主路线的内容。

以后任何新对话，如需继续 XiaoG 项目，应先以本文件为事实基线，再结合最新 Git / Codex 实际报告更新。

---

# 1. 项目定位

项目名称：

**小G / XiaoG**

目标：

构建一个真正属于用户自己的 **Personal AI Runtime / 个人 AI 控制层**。

XiaoG 不是：

- ChatGPT Clone；
- DeepSeek 套壳；
- 某一个模型的专用前端；
- 单纯聊天机器人。

DeepSeek、GPT-5.6 Terra，以及未来的 Claude / Gemini / Qwen / Kimi / GLM / Grok 等，仅是 XiaoG 可调用的“脑”。

真正属于 XiaoG 自己的能力包括：

- 统一身份 / Persona；
- User Profile；
- Conversation；
- Long-term Memory；
- Auto Router；
- Knowledge Base；
- Projects；
- Files / Artifacts；
- Plugins；
- Skills；
- Tasks / Automations；
- G-BRIDGE；
- Agent；
- Computer Use；
- Remote Control；
- Voice / Live Voice；
- Device Management；
- Permission / Audit；
- Search；
- 用户拥有的数据与配置。

核心原则：

> 模型可以更换，小G不能随模型一起消失。

---

# 2. 当前技术路线

## 2.1 当前模型

### DeepSeek

当前真实模型：

`deepseek-v4-flash`

特点：

- DeepSeek API；
- 当前作为较低成本模型；
- 实际 model_id 由运行配置驱动；
- UI 显示名必须由 Model Registry 解析，不允许散落硬编码。

### GPT-5.6 Terra

当前真实模型：

`gpt-5.6-terra`

通过：

**Codex App Server**

当前架构：

- Long-lived App Server；
- Thread Persistence；
- Resume；
- Context Sync；
- Automatic Reconnect。

上述链路已经是稳定核心，后续阶段不得为了局部功能随意重写。

## 2.2 当前技术栈

前端：

- HTML
- CSS
- JavaScript

后端：

- Python
- FastAPI

数据库：

- SQLite

配置 / 密钥：

- `.env`

版本管理：

- Git

项目主目录：

`D:\XiaoG`

## 2.3 当前不做

目前不部署本地大模型作为主路线。

可以未来增加 Local Provider，但不能破坏当前 Provider-neutral 架构。

---

# 3. 核心架构原则

1. **Provider 与 XiaoG 身份分离。**
2. 模型属于 Provider，XiaoG 拥有用户数据和智能控制层。
3. 所有模型共享 XiaoG 的：
   - System Prompt
   - User Profile
   - Conversation
   - Memory
   - Project Context
   - Tool Context
4. 模型是执行层，XiaoG 是控制层。
5. 新能力优先形成统一 Service / Registry，不允许“一个功能一个临时系统”。
6. 未来能力如果依赖后续阶段：
   - 当前只预留 schema / interface / UI entry / service boundary；
   - 不提前完整实现。
7. 新需求如会改变数据模型、权限、Provider、Memory、Projects、Tools、Devices、Tasks 等核心边界，必须先做架构判断。
8. 数据属于用户。
9. 未知数据必须保持未知，禁止伪造。
10. 稳定 Provider / Thread / Database 核心不可为了 UI 小修随意重构。

统一基础设施方向：

- Search Service
- Notification Service
- Artifact Service
- Scheduler Service
- Extension Registry
- Tool Registry
- Device Registry
- Provider Registry
- Model Registry
- Capability System

---

# 4. ADR：已确认架构决策

## ADR-001 — XiaoG 定位

XiaoG = **Personal AI Runtime**，不是 ChatGPT Clone。

## ADR-002 — Provider Separation

Provider 提供模型能力。

XiaoG 持有：

- 用户数据；
- 身份；
- Memory；
- Projects；
- Tools；
- Permissions；
- Conversation；
- Knowledge。

## ADR-003 — 当前不部署本地大模型

当前主线使用云模型 / 官方模型服务。

未来允许通过 Provider Adapter 接入 Local Provider。

## ADR-004 — Terra 使用长期运行 Codex App Server

目的：

降低 Cold Start，保持稳定 Thread / Resume / Context Sync。

## ADR-005 — Conversation Lifecycle

统一生命周期：

`Active → Archive → Trash → Delete`

## ADR-006 — Memory / History / Knowledge 必须分离

- Conversation：发生过什么；
- Memory：用户是谁、长期状态是什么；
- Knowledge：外部资料是什么。

三者不能混成一个系统。

## ADR-007 — Unified Search Service

所有未来搜索能力最终进入统一 Search Service。

包括未来：

- Conversation Search
- File Search
- Knowledge Search
- Memory Search
- Project Search

不能各建一套互不兼容搜索。

## ADR-008 — Unified Content Model

消息内容未来统一采用可扩展 ContentBlock 思路，支持：

- Text
- Image
- Video
- Audio
- File
- Artifact
- Tool Result
- Rich Content

## ADR-009 — Unified Tool Registry

所有工具统一注册、声明 capability / permissions / availability。

## ADR-010 — Permission First

高风险操作必须确认。

权限必须在 Agent / Computer Use / Remote Control 大规模实现前形成统一抽象。

## ADR-011 — Multi-Provider Extensibility

XiaoG 不得假定永远只有 DeepSeek + Terra。

必须形成：

- Provider Registry
- Model Registry
- Provider Adapter
- Capability Metadata

统一 Provider Interface 至少考虑：

- send
- stream
- models
- status
- capabilities
- configuration

Model Metadata 至少考虑：

- provider_id
- model_id
- display_name
- streaming
- reasoning
- vision
- audio
- tool_use
- context
- availability
- cost
- capabilities

未知信息保持 `null / unknown`，禁止伪造。

未来 Claude / Gemini / Qwen / Kimi / GLM / Grok 等不应要求重写全系统。

---

# 5. 数据库与安全硬规则

任何阶段都必须遵守：

- 禁止删除数据库；
- 禁止为了开发方便重建数据库；
- 禁止清空 Conversation；
- 禁止清空 Message；
- 禁止破坏 Archive / Trash 数据；
- Schema 修改必须使用安全 Migration；
- 必须逐步建立 `schema_version / migration history`；
- DB 修改前后应检查数据数量及 SQLite integrity。

敏感数据：

- `.env`
- API Key
- Token
- Cookie
- Credential

不得提交进 Git。

---

# 6. Frontend 永久工程规则

## Frontend Asset Versioning / Cache Busting

这是永久规则。

只要修改核心静态资源，例如：

- `app.js`
- `style.css`
- `i18n.js`

必须同步更新：

- query version；
- hash；
- 或等价 cache-busting 机制。

禁止再次出现：

> 代码已经改了，但浏览器仍运行旧静态资源，形成“假 Bug”。

该规则源自 v0.3.7.1 的真实问题。

---

# 7. 开发角色与协作方式

## 7.1 当前角色

用户：

**Product Owner / 产品负责人**

负责：

- 需求；
- 优先级；
- 最终决策。

ChatGPT / 小G：

**Tech Lead / Architect / Reviewer**

负责：

- 需求拆解；
- Roadmap；
- 架构；
- Codex 指令；
- Codex 报告审查；
- 验收；
- 防止遗漏永久需求。

Codex：

当前主工程师，负责实际：

- 修改代码；
- 创建文件；
- 测试；
- Git；
- 修复问题；
- 输出开发报告。

## 7.2 当前串行流程

`用户需求 → ChatGPT规划 → Codex执行 → Codex报告 → ChatGPT验收 → Git稳定版本`

---

# 8. 当前实际开发状态

## 8.1 已完成阶段

- Phase 0 — 环境与技术路线
- Phase 1 — 基础项目框架
- Phase 2 — DeepSeek
- Phase 3 — Terra 双模型
- Phase 4 — 基础产品体验
- Phase 4.5-A — Terra 性能优化
- Phase 4.5-B1
- Phase 4.5-B2-1
- Phase 4.5-B2-2
- Phase 4.5-B3 — 产品体验最终收尾

## 8.2 最近稳定版本

### v0.3.3

Commit：

`e9f3a3abe22f4870e6c64a62def469ef9bcb62de`

Phase 4.5-B3 基线。

### v0.3.4

Commit：

`c2602b4edfc4c6379f9025067118c3860584d702`

UI Polish。

### v0.3.5

Commit：

`731cb64cd9808c64cc151c6849a2107f4e109420`

Global Search v1：

- title
- user message
- AI message
- archived conversation
- exact message location
- trash excluded

### v0.3.6

Commit：

`7b4145f0b589db3cdcaea94d0031c67784954eb9`

包括：

- XiaoG Self Status / product info；
- Persona / User Profile → Personalization；
- UI i18n；
- Simplified Chinese / English；
- `ui_language` persistence。

### v0.3.7

Commit：

`6ddf0d88208e4bc2ec3514c8ebdc8f6f98b882e8`

包括：

- assistant avatar unified；
- friendly model display。

### v0.3.7.1

Commit：

`64b86b897e7e3d273de93f07ee0cbe6f999626fc`

Cache Busting hotfix。

### v0.3.7.2

Commit：

`9424e1c3a5a62313b915e33a620ecc91aa1350a0`

Header model area layout stabilization。

Phase 4.5-B3 至此正式关闭。

---

# 9. Phase 5 — Model Intelligence / Auto Router

Phase 5 分成小版本执行。

## 9.1 v0.4.0 — Provider / Model / Capability Registry

**状态：已完成。**

Commit：

`7ddab006a618ede56e3d22d55ba2f212d8f47cd0`

已完成：

- Provider Registry；
- Model Registry；
- Capability System；
- `/api/model-registry`；
- DeepSeek / Terra 真实 model_id；
- UI display_name 从 Registry 读取；
- Terra reasoning metadata；
- DeepSeek reasoning metadata；
- Provider 行为未被破坏。

### Terra 已登记真实 Reasoning Efforts

- low
- medium
- high
- xhigh
- max
- ultra

默认：

`medium`

### DeepSeek 当前 Registry Reasoning Metadata

- none
- low
- high
- max

但截至 v0.4.0：

**真实请求仍是 `thinking=disabled`。**

因此 DeepSeek reasoning 尚不能算功能完成。

---

## 9.2 v0.4.1 — Dynamic Manual Reasoning

**当前状态：已向 Codex 下发完整指令，但因 Codex 额度不足暂停。**

恢复额度后：

> 继续 v0.4.1 原任务，不跳过，不重启 Phase 5，不直接做 Auto Router。

必须完成：

### 动态 Reasoning Selector

前端读取：

`Model Registry → supported_reasoning_efforts`

禁止：

```text
if Terra ...
if DeepSeek ...
```

这种 Provider 专属硬编码。

### Terra

真实支持：

- low
- medium
- high
- xhigh
- max
- ultra

默认：

- medium

用户手动选择必须真实传给 Codex App Server。

不得重写稳定 App Server / Thread / Resume 架构。

### DeepSeek

真实模型：

`deepseek-v4-flash`

目标手动档位：

- none
- low
- high
- max

要求：

- `none` → thinking disabled；
- 其他档位必须基于当前真实 DeepSeek API 文档 / 实际支持字段实现；
- 不能只改 UI；
- 必须验证真实 payload 和 API 接受情况；
- 如果真实 API 与当前 metadata 不一致，修正实现 / Registry，禁止伪造支持。

### Manual Mode

用户明确选择：

`Model + Reasoning Effort`

必须严格执行。

Router 不能覆盖。

### Reasoning Preference

优先设计为：

每个 `model_id` 保存自己的最近 reasoning preference。

模型切换时：

- 恢复该模型可用 preference；
- 不得保留不支持的旧模型档位。

### SSE Metadata

建议返回：

- provider_id
- model_id
- display_name
- reasoning_effort

不得暴露隐藏 Chain-of-Thought。

### 完成后版本

计划：

**v0.4.1**

完成后停下验收，不自动进入 v0.4.2。

---

## 9.3 v0.4.2 — Auto Router v1

目标：

本地规则 Router，不额外调用一个 LLM 只为了路由。

性能目标：

**routing overhead 尽量 < 50ms**

Router 输入考虑：

- task complexity；
- text length；
- context length；
- code；
- analysis / reasoning；
- simple chat；
- structured task；
- model health / availability；
- cost principle。

核心原则：

> 低成本模型足够完成，就不无意义升级。

Router 输出至少：

- selected_provider
- selected_model
- selected_effort
- task_class
- routing_time_ms
- routing_explanation

不得输出隐藏 Chain-of-Thought。

Manual：

严格尊重用户选择。

Auto：

选择：

**Model + Reasoning Effort**

UI 可显示：

- `Auto → DeepSeek V4 Flash`
- `Auto → GPT-5.6 Terra / High`

Router 必须基于 Model Registry / Capability Registry，不允许硬编码“DeepSeek vs Terra 二选一”成为永久架构。

---

## 9.4 v0.4.3 — Provider Management

位置：

`Settings → Models & Intelligence → Provider Management`

每个 Provider 至少考虑：

- Provider Status
- Current Model
- API / Connection Config
- View Usage
- Manage Quota / Credit
- Recharge API Credit ↗
- Open Official Console ↗

第一版只做官方链接跳转，不在 XiaoG 内部造充值 / 支付 / 订单 / 退款系统。

Provider metadata 预留：

- usage_url
- billing_url
- recharge_url
- console_url

Phase 7 Usage Dashboard 可以提供辅助入口，但 Provider Management 是 Provider 管理主入口。

---

## 9.5 Phase 5 Stable Baseline

v0.4.1 / 0.4.2 / 0.4.3 全部完成并通过：

- API；
- browser；
- DB；
- real provider；
- regression；
- security；
- git clean；

之后建立 Phase 5 稳定基线。

**只有 Phase 5 Stable 后，才进入下面的工程节点。**

---

# 10. Engineering Foundation Gate
## Phase 5 Stable 后、Phase 5.5 前

这是已确认新增的工程基础建设节点。

不是削减产品功能，而是为了让后续大型阶段更稳、更快。

## 10.1 Automated Test Suite

建立正式自动化测试体系，覆盖至少：

- API；
- DB migration；
- Conversation lifecycle；
- Search；
- Settings；
- Provider Registry；
- Model Registry；
- Router；
- 核心回归。

目标：

尽可能形成“一条命令跑核心回归”。

## 10.2 Logging & Diagnostics

统一日志 / 诊断：

- Provider；
- Router；
- DB；
- App Server reconnect；
- Tool；
- Task；
- Extension；
- errors。

默认：

敏感信息脱敏。

未来 Settings / System → Diagnostics 可复用。

## 10.3 Unified Error Model / Error Boundary

统一考虑：

- error code；
- user-readable message；
- technical log；
- retryable；
- Again / Retry。

单模块失败不应拖死整个 Chat。

## 10.4 Database Migration History

建立：

- schema_version；
- migration history；
- safe upgrade path。

## 10.5 Unified Configuration System

明确区分：

- Dev Config；
- Provider Secrets；
- User Settings；
- Product Metadata；
- Runtime State。

## 10.6 Permission Abstraction

在未来 File / Knowledge / Agent / Remote Control 之前形成基础 Permission abstraction。

至少考虑：

- read
- write
- delete
- external action
- sensitive action

但不要提前实现完整 Agent。

## 10.7 Unified Search Service Continuation

未来所有搜索继续进入现有 Search Service。

## 10.8 File / Artifact Lifecycle

必须正式区分：

- Temporary Chat Attachment
- Artifact
- Knowledge File
- Project Asset

并定义：

- ownership；
- persistence；
- deletion；
- project/global scope。

## 10.9 Provider Health / Fallback / Degradation

后续 Router 应逐步考虑：

- provider health；
- temporary unavailable；
- degraded capability；
- fallback。

例如 Terra 不可用时，可按策略考虑其他 Provider。

不得只依赖简单红黄绿 UI。

## 10.10 Backup / Import / Export

用户拥有的数据应可以未来迁移 / 恢复：

- Conversation
- Settings
- Memory
- Knowledge
- Projects

---

# 11. 16GB Controlled Dual-Codex Parallel Development
## 已确认硬节点：Phase 5 Stable 后、Phase 5.5 前搭建

用户已正式确认：

> 必须搭建「16GB 受控双 Codex 并行开发模式」。

该节点不能忘记。

## 11.1 硬件约束

当前电脑大致：

- Ryzen 7 7735
- 16GB RAM
- RTX 4050
- SSD 剩余约 100GB

经济条件暂不支持升级 32GB。

因此采用：

**受控双 Codex，而不是双完整运行环境。**

## 11.2 角色

当前一直开发 XiaoG 的 Codex：

**Main Codex / Integrator / 主工程师**

新开第二个 Codex 聊天：

**Worker Codex**

ChatGPT：

**Tech Lead / Architect / Reviewer**

用户：

**Product Owner**

## 11.3 工作区

主 Codex：

- 主工作区；
- main / integration responsibility；
- 允许启动完整 XiaoG；
- 负责最终联调。

Worker：

- Git Worktree；
- 独立 feature branch；
- 独立子任务。

禁止两个 Codex 直接同时乱改 main。

## 11.4 16GB 低内存规则

只保留一套重型运行环境。

主 Codex 可以负责：

- FastAPI；
- Terra App Server；
- 浏览器；
- full integration test。

Worker 优先负责：

- 独立代码；
- UI；
- test writing；
- static checks；
- limited unit tests；
- Git commit。

避免同时运行：

- 两套 Terra；
- 两套完整浏览器测试；
- 两套完整后端；
- 多个重型测试进程。

重负载测试错峰。

## 11.5 并行工作标准流程

1. 用户提出阶段需求；
2. ChatGPT 判断是否适合并行；
3. ChatGPT 先定义：
   - API Contract
   - Schema
   - file ownership
   - task boundary
4. ChatGPT 给出：
   - Main Codex 指令
   - Worker Codex 指令
5. 两个 Codex 独立开发；
6. 用户把两份开发报告交给 ChatGPT；
7. ChatGPT 分别验收；
8. ChatGPT 输出 Integration / Merge 指令；
9. Main Codex / Integrator：
   - review diff
   - merge
   - resolve conflicts
   - integration test
   - full regression
10. 用户提交最终报告；
11. ChatGPT 最终验收；
12. Stable Baseline。

## 11.6 不强制每一轮都并行

ChatGPT 必须判断：

适合并行才拆。

以下情况不应强行并行：

- 两边都大量修改同一个核心文件；
- DB核心 Schema 高度耦合；
- Conversation 核心模型；
- Router核心接口仍未稳定；
- 合并成本高于节省时间。

## 11.7 试运行

Phase 5.5：

作为双 Codex 小规模试运行阶段。

Phase 6 起：

如果内存和工作流验证正常，正式常态化并行。

---

# 12. Phase 5.5 — Response Versions / Branches / A-B

解决当前线性回答模型。

一个 User Message 可以对应多个 Answer Version。

支持：

- Regenerate；
- Edit Previous Prompt；
- Regenerate from Edited Prompt；
- Switch Model and Re-answer；
- Version Switch；
- Branch / Version Semantics。

不能通过粗暴覆盖旧消息实现。

## Multi-model A/B Test

同一个 Prompt 可发给任意已注册模型。

不是固定：

DeepSeek vs Terra。

而应该支持：

Model A vs Model B

基于 Model Registry。

---

# 13. Phase 6 — Long-term Memory

这是硬阶段。

必须实现真正长期 Memory。

Memory 类型可包括：

- Preferences
- People
- Long-term Goals
- Project Status
- Habits
- Common Information
- Device Information

所有 Provider / Model 共享 XiaoG Memory。

Scope：

- Global
- Project

## 13.1 Global Memory Panel — 硬要求

这是永久需求 #15。

不能只在后端偷偷保存 Memory。

必须提供用户可见 Memory 管理界面：

- View
- Search
- Add
- Edit
- Delete
- Category
- Source
- Scope

至少明确：

- Global Memory
- Project Memory

可采用：

- Side Panel；
- Dedicated View；

但必须真实可操作。

继续坚持：

Memory ≠ Conversation History ≠ Knowledge Base。

---

# 14. Phase 6.2 — Knowledge Base

建立真正资料库。

支持至少：

- PDF
- Word
- Markdown
- TXT
- Web Page
- Code

后续扩展：

- Image
- Video
- richer file types

能力：

- Folder
- Project Library
- Tags
- Full-text Search
- Semantic Search
- Multi-document Q&A
- Summary
- Citation
- Re-index
- Delete Index

核心区别：

- File Search：找到文件；
- Knowledge Base：理解文件。

## 14.1 Chat Attachment ↔ Knowledge Base 联动硬要求

必须保留以下设计：

1. Phase 6.2 Knowledge Base 支持手动上传；
2. Phase 6.5 Chat 支持真实附件上传；
3. Chat Attachment 可手动：
   **Add to Knowledge Base**；
4. 增加设置：
   **Automatically add chat attachments to Knowledge Base**；
5. 推荐默认：
   **OFF**；
6. 用户可自行开启；
7. Project Conversation 中的文件可以加入：
   **Project Knowledge Base**；
   不应总是进入 Global；
8. 临时 Chat Attachment 与长期 Knowledge Indexed Document 必须区分；
9. 禁止所有聊天附件无条件永久索引。

---

# 15. Phase 6.3 — Projects

实现 Project Workspace。

Project 至少考虑：

- Name
- Icon
- Color
- Instructions
- Conversations
- Knowledge Base
- Memory
- Default Model
- Auto Policy
- Plugins
- Skills
- Tasks
- Activity

支持：

把已有 Conversation Move into Project。

重要实体需要提前考虑：

`project_id`

包括：

- Conversation
- Memory
- Knowledge
- Task
- Extension
- Artifact

---

# 16. Phase 6.5 — Multimodal / Real Attachments

## Image

- Upload
- Screenshot
- Multiple Images
- OCR
- UI Understanding
- Table Understanding

## Files

- PDF
- Word
- TXT
- Markdown
- Code

逐步扩展：

- Excel
- PowerPoint

## Video

第一版：

- Key Frames
- Audio
- Subtitle
- Visual Analysis
- Summarize
- Timestamp Location
- Game Footage
- Course
- Screen Recording

## Audio

- Upload
- STT
- Understanding

## Camera / QR

- Camera Input
- QR from camera
- Uploaded QR
- Clipboard image
- URL
- Text
- Device Pairing

## Voice Input

`Mic → STT → Editable Input`

第一阶段默认不要强制自动发送。

## TTS

支持：

- Read This Message
- Auto Read
- Voice Selection
- Preview
- Speed
- Volume
- Output Device

Voice Settings 后续由 Live Voice 复用。

---

# 17. Phase 6.5.1 — Voice Chat MVP
## 新增硬阶段，不能再从 6.5 直接跳 6.6

目标：

实现“对讲机式”语音聊天。

流程：

`用户说一轮 → STT → 发送给 XiaoG → 模型文字回答 → TTS 自动播放 → 等待下一轮`

必须支持：

- Start Voice Chat
- End Voice Chat
- Recording / Transcribing / Thinking / Speaking 等状态
- Transcript 保留进普通 Conversation
- 基础 Retry
- Microphone Permission
- TTS Toggle

这个阶段不是：

- Full Duplex
- VAD realtime dialogue
- Streaming interruption
- 电话式实时通话

这些留到 Phase 8.5。

---

# 18. Phase 6.6 — Artifacts / File Generation

建立：

**Artifact Service**

支持生成：

- DOCX
- XLSX
- PPTX
- PDF
- Markdown
- TXT
- CSV
- JSON
- HTML
- ZIP

Artifact Metadata：

- id
- filename
- type
- MIME
- size
- path
- created_at
- conversation_id
- project_id

聊天中显示 File Card。

操作：

- Download
- Open
- Reveal
- Add to Knowledge Base
- Move into Project
- Reattach

Artifact 必须具有独立生命周期。

未来：

G-BRIDGE 可发送 Artifact。

---

# 19. Phase 7 — Usage / Cost Dashboard

这是主导航页面，不应只藏在 Settings。

统计：

## DeepSeek

- Calls
- Input Tokens
- Output Tokens
- Cost

## Terra

- Call Count
- Effort Distribution
- Latency

## Overall

- Provider Share
- Model Share
- Trend
- Error Rate

重要：

如果 Codex App Server 没有提供 Terra 单次真实 Token / Cost：

`estimated_cost = NULL`

未知就是未知。

禁止猜测、伪造成本。

---

# 20. Phase 7.5 — Plugins / Skills + Real Internet Search
## 这是硬要求，Web Search 不能忘

建立：

**Extension Registry**

## Plugin

外部工具 / API 能力。

支持：

- Installed
- Available
- Disabled
- Install
- Update
- Enable
- Disable
- Uninstall
- Permissions
- Configuration
- Status
- Version
- Author

## Skill

Instruction / Workflow / Tool Sequence。

支持：

- Installed Skills
- My Skills
- Available
- Disabled
- Install
- Edit
- Copy
- Import
- Export
- Delete
- Dependencies
- Permissions

Scope：

- Global
- Project

## 20.1 Real Web Search — 硬要求

Phase 7.5 必须获得真正互联网搜索能力，不是 UI 占位，也不是让模型凭记忆回答。

必须包括：

- Web Search Tool
- actual search provider / API
- structured search result
- source / URL
- timeout handling
- error handling
- no-results handling
- permission / configuration where needed
- Extension Registry integration
- Tool-compatible architecture

验收：

用户问：

> “搜索今天最新的 XXX”

XiaoG 必须真实访问互联网获得当前信息。

## 20.2 Real Video Search

建立：

- Video Search Tool
- real provider / search source
- structured result
- links / metadata / relevant preview information

## 20.3 Renderer

Web / Video 搜索结果通过：

**Rich Content Renderer**

显示：

- sources
- links
- cards
- structured result

未来 Phase 8 Agent 可自动调用这些 Search Tools。

---

# 21. Phase 7.8 — Tasks / Automations

类似 ChatGPT Tasks。

任务类型：

- One-time
- Recurring
- Conditional

建立：

**Scheduler Service**

Task 至少考虑：

- id
- title
- instruction
- schedule
- timezone
- enabled
- type
- model_mode
- created_at
- next_run
- last_run

Task Run：

- start
- end
- status
- result
- error

预留：

`execution_target`

当前本地个人版优先：

- local
- device

注意：

不再把 Cloud Runtime 当作当前主路线规划。

主导航：

Tasks

页面：

- Upcoming
- All
- Paused
- Run History

本地限制：

如果 XiaoG Backend / PC 没运行，本地 Task 无法执行。

---

# 22. Phase 8 — G-BRIDGE / Agent / Computer Use

建立 / 完善：

**Tool Registry**

逐步接入：

- Windows
- iPhone
- Android
- Browser
- Files
- Reminders
- Notes
- Calendar
- Email
- Apps

执行链：

`User → Agent → Tool → Permission → Execution → Result`

## Tool Permission

操作分级：

### Read / Analyze

可以更自动。

### Reversible Action

中等确认。

### Irreversible / High-risk

必须明确确认。

## Execution Pipeline

完整状态：

- Parsing
- Tool Call
- Waiting for Device
- Running
- Success
- Failed

支持：

- Again / Retry

并复用 Notification Service。

现有 G-BRIDGE 经验可作为未来设备执行的一部分，但不能把临时协议直接当最终 Tool Architecture。

---

# 23. Phase 8.2 — Remote Control
## 必须保留，不能遗漏

Settings：

`Devices & Tools → Remote Control`

支持：

- Enable
- Authorized Devices
- Pairing
- QR Pairing
- Permissions
- Connection Status
- Sensitive Action Confirmation
- Audit Log
- Emergency Disconnect

抽象：

- Device
- Remote Session
- Pairing
- Permission
- Action
- Approval
- Audit Log

Level 1：

Remote Command

Level 2：

Device Management

Level 3：

- Screen
- Computer Use
- Mouse
- Keyboard

安全红线：

**绝对不能直接把 XiaoG localhost / control port 暴露到公网。**

必须：

- Authentication
- Encryption
- Pairing
- Permissions
- Approval
- Audit

---

# 24. Phase 8.5 — Live Voice

真正“电话式”实时 AI 语音。

不是 Phase 6.5.1 的轮次式 STT + TTS。

必须考虑：

- Full Duplex Audio
- VAD
- Streaming STT
- Streaming TTS
- Interrupt
- Mute
- Speaker
- Hangup
- Captions
- Memory
- Auto Router
- Agent Tool Use
- Call Summary
- Network Recovery

复用：

Phase 6.5 / 6.5.1 建立的 Voice Settings / STT / TTS 基础。

---

# 25. 21 项永久需求追踪表

以下要求必须长期保留，每次大型 Roadmap / Phase 都要检查是否回归。

| # | 要求 | 当前状态 |
|---|---|---|
| 1 | Terra 响应速度优化 | 已做主要优化 |
| 2 | XiaoG 知道自身版本/commit/phase/capabilities/limits/changelog | v0.3.6 基本完成 |
| 3 | 恢复 Conversation scroll position | 已完成 |
| 4 | 完整 Settings 多级系统 | 基础已完成 |
| 5 | Archived page 可返回 History | 已完成 |
| 6 | Header model selector 不横向跳动 | v0.3.7.2 完成 |
| 7 | Green/Blue/Purple + light/dark theme | 基础已完成 |
| 8 | XiaoG/User Avatar | 已完成基础 |
| 9 | Sidebar collapse/expand，按钮替代 logo 位 | 已完成 |
| 10 | History hierarchy + Pin/Rename/Archive/Trash/Restore/Delete + 全文 Search + exact locate | v0.3.5 搜索完成，生命周期基础已完成 |
| 11 | Header 显示 conversation title，auto + manual edit | 已完成 |
| 12 | AI bubble 显示 model name | 已完成 |
| 13 | Attachment + Voice input | UI 预留；真实能力 Phase 6.5 |
| 14 | Execution Status | 基础完成；Phase 8 升级完整 Tool/Agent 状态 |
| 15 | **Global Memory Panel** | **Phase 6 硬要求，未完成** |
| 16 | Dark Mode | 已完成 |
| 17 | Model Status green/yellow/red，禁止高频 ping | 基础已完成 |
| 18 | Auto Tooltip / Auto Router 提示 | Phase 5 |
| 19 | User / AI bubble 区分强化 | 已完成 |
| 20 | AI message action bar Copy/Regenerate/Edit Prompt/Switch Model | 基础完成；Phase 5.5 完成真实 branch semantics |
| 21 | Multi-model A/B Test | Phase 5.5 |

---

# 26. Settings 当前正式结构

一级目录固定：

1. Account
2. Personalization
3. Models & Intelligence
4. Memory
5. Devices & Tools
6. App Settings
7. Data & Privacy
8. System
9. Help
10. About XiaoG

当前已确认：

- Persona / System Prompt → Personalization；
- User Profile → Personalization；
- UI Language → **System → Language**；
- UI language 只控制界面，不强迫模型回答语言。

---

# 27. Search 当前状态与未来规则

v0.3.5 已建立统一 Search Service。

当前 Conversation Search：

- title；
- user message；
- AI message；
- archived conversation；
- exact message locate；
- trash excluded。

未来：

- File Search
- Knowledge Search
- Memory Search
- Project Search

全部逐步进入同一 Search Service。

禁止另建互不兼容搜索架构。

---

# 28. Provider / Model 永久要求

1. 真实 API `model_id` 与 UI `display_name` 分离；
2. Display Name 由 Registry 解析；
3. 如果 `DEEPSEEK_MODEL_ID` 更改，UI 不能仍硬显示旧模型名；
4. Reasoning capability 来自 Registry / Provider metadata；
5. Capability unknown 时不可猜；
6. Future Router / A-B / Usage / Agent 全部基于 `provider_id + model_id + capabilities`；
7. Provider secrets 隔离。

---

# 29. 当前已知问题 / 不应遗忘的风险

## Terra Short SSE Regression

曾观察到：

短请求有时 SSE 只有 meta / 没有 text delta，但 Provider status 仍正常。

该问题存在，但不能因此随意重写稳定：

- App Server
- Thread
- Resume
- Context Sync

应独立诊断。

---

# 30. 明确从 Roadmap v2 删除的旧规划

用户已明确：

> 以后不打算做网页和 EXE，不需要保留相关规划。

因此 Roadmap v2 不再把以下内容作为未来主路线：

- Windows EXE / Installer；
- Desktop Packaging 相关阶段；
- Public Cloud Web 版本；
- Phase 9 Cloud / Multi-user / Commercialization；
- Dual Runtime / Desktop-vs-Cloud 架构规划。

如果未来用户主动重新提出，再重新做架构评估。

不得自行把这些旧计划重新带回 Roadmap。

---

# 31. 当前最近的唯一正确下一步

当前：

**Phase 5 / v0.4.0 已稳定完成。**

当前 Codex 正在进行的任务：

**v0.4.1 — Dynamic Manual Reasoning**

但因：

**Codex 额度不足**

暂时停止。

因此恢复额度后的正确动作是：

1. 回到当前 Main Codex；
2. 继续执行已下发的 v0.4.1 指令；
3. 不重新开一个不同设计；
4. 完成真实 DeepSeek / Terra Manual Reasoning；
5. 输出开发报告；
6. ChatGPT 验收；
7. 若通过，建立 v0.4.1 commit；
8. 再进入 v0.4.2 Auto Router；
9. 再进入 v0.4.3 Provider Management；
10. Phase 5 Stable；
11. **Engineering Foundation Gate + 16GB Controlled Dual-Codex Setup**；
12. Phase 5.5 开始试运行双 Codex。

---

# 32. 后续主阶段顺序（最终版）

```text
Phase 5
├─ v0.4.0 Provider / Model / Capability Registry ✅
├─ v0.4.1 Dynamic Manual Reasoning ← 当前暂停点
├─ v0.4.2 Auto Router v1
├─ v0.4.3 Provider Management
└─ Phase 5 Stable Baseline

        ↓

Engineering Foundation Gate
+
16GB Controlled Dual-Codex Parallel Development Setup

        ↓

Phase 5.5
Response Versions / Branches / Multi-model A/B
（双 Codex 小规模试运行）

        ↓

Phase 6
Long-term Memory + Global Memory Panel

        ↓

Phase 6.2
Knowledge Base

        ↓

Phase 6.3
Projects

        ↓

Phase 6.5
Multimodal + Real Attachments + STT/TTS foundation

        ↓

Phase 6.5.1
Voice Chat MVP

        ↓

Phase 6.6
Artifacts / File Generation

        ↓

Phase 7
Usage / Cost Dashboard

        ↓

Phase 7.5
Plugins / Skills
+
REAL Web Search
+
REAL Video Search

        ↓

Phase 7.8
Tasks / Automations

        ↓

Phase 8
G-BRIDGE / Agent / Computer Use

        ↓

Phase 8.2
Remote Control

        ↓

Phase 8.5
Live Voice
```

---

# 33. 新对话接力最短摘要

如果新对话没有足够上下文，先告诉 ChatGPT：

> 这是 XiaoG / 小G 项目。请以我上传的 `XiaoG_Master_Roadmap_v2_2026-09-12.md` 为唯一主路线基线。  
> 当前停在 Phase 5：v0.4.0 已完成，commit `7ddab006a618ede56e3d22d55ba2f212d8f47cd0`；v0.4.1 Dynamic Manual Reasoning 已向当前主 Codex 下发，但 Codex 因额度不足暂停。恢复后要继续 v0.4.1，不跳阶段。  
> 当前这个老 Codex 将长期作为 Main Codex / Integrator。Phase 5 Stable 后、Phase 5.5 前必须搭建 16GB Controlled Dual-Codex Parallel Development。  
> 不要遗漏：21项永久需求、Global Memory Panel、Phase 6.5.1 Voice Chat MVP、Knowledge Base 与 Chat Attachment 联动、Phase 7.5 真正 Web/Video Search、Provider Management 官方充值/额度链接、工程基础十项、Frontend Cache Busting、ADR-011 Multi-Provider Extensibility。  
> 不要把 EXE / Cloud Web / Phase 9 商业云路线重新加回来。

---

# 34. Roadmap 维护规则

以后任何新增需求：

先判断它是否影响：

- Data Model
- Provider
- Model Capability
- Permission
- Memory
- Knowledge
- Projects
- Search
- Tool / Plugin
- Task
- Device
- Artifact
- Remote Control

如果影响底层：

先预留架构。

如果只是 UI：

进入附近小版本。

如果依赖未来能力：

不要提前硬实现。

如果明显改变全路线：

更新 Master Roadmap。

每次大型阶段结束：

- 更新版本；
- 更新 commit；
- 更新 phase；
- 更新 known issues；
- 更新 requirement traceability；
- 建立 Git Stable Baseline。

---

**END — XiaoG Master Roadmap v2 / 2026-09-12**
