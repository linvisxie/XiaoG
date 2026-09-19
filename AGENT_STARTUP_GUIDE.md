# XiaoG Agent Startup Guide

本指南供任何第一次接触 XiaoG 的 Agent、Codex 或开发者使用。它是接管导航，不替代 `XiaoG_MAIN_CODEX_ENTRY.md`、当前 STATUS 或任何已授权 Activation。

## 1. 项目定位

XiaoG 是属于用户自己的 **Personal AI Runtime**。

XiaoG 不是：

- ChatGPT Clone；
- DeepSeek 套壳；
- 单模型前端。

模型提供智能能力；XiaoG 负责用户数据控制、Runtime、Provider、Capability、Memory、Knowledge、Projects、Tools、Agent、Workflow 和 Personalization 等长期产品边界。当前代码、已接受能力和明确授权决定实际可用范围，愿景不等于已经实现。

## 2. 阅读顺序

第一步：

`XiaoG_MAIN_CODEX_ENTRY.md`

第二步：

`governance/core/v3.0/XiaoG_v3.0_Master_Document.md`（逻辑名称）

当前物理文件：

`governance/core/V3.0文档库/XiaoG_v3.0_Master_Document（第三版总纲）.md`

第三步：

`governance/current/`

先读取 `XiaoG_AUTOPILOT_STATUS.md`，再读取它指向的当前 Activation、Handoff、Pause Handoff 或恢复材料。

第四步：

根据任务读取：

- `XiaoG_Master_Roadmap_v3.0_FINAL.md`：阶段与执行路线；
- `XiaoG_Feature_Requirement_Registry_v3.0.md`：功能需求与范围；
- `XiaoG_Project_Governance_Manual_v3.0.md`：授权、修改、验证和交付规范；
- 与任务直接相关的 Architecture、Product Decision、Migration 或历史决策文档。

逻辑名称与当前物理路径以 `governance/INDEX.md` 为准。不要因为历史文档中的旧路径引用而移动或改写权威文件。

## 3. 开发原则

- 不破坏已经接受的架构、数据语义和安全边界。
- 修改前先理解现有设计、真实 Git 状态、运行证据和当前授权。
- 非核心能力优先评估成熟开源复用，但必须完成版本、License、安全、维护性和退出成本验证。
- 用户数据、Provider/Router 主权、权限策略、公开 API 和长期产品事实必须保持由 XiaoG 控制。
- 第三方 Runtime、Harness、Provider 或工具优先通过 XiaoG 自有 Contract / Adapter 隔离，不直接侵入核心。
- 愿景、Roadmap 和 Registry 用于指导；不得把尚未实现的能力描述为当前事实。

详细规则以 `XiaoG_Project_Governance_Manual_v3.0.md` 为准。

## 4. 当前项目状态读取方式

Agent 开始工作前必须确认：

- 当前版本：读取 `product_info.json` 和当前 STATUS；
- 当前阶段：读取 `governance/current/XiaoG_AUTOPILOT_STATUS.md` 及最新 Handoff；
- 当前任务：确认明确的授权 ID、范围、停止条件和禁止项；
- 当前风险：检查 STATUS、Pause/Handoff、已知问题和未验证事项；
- Git 状态：确认 branch、HEAD、tracked/untracked working tree、相关历史和 remote。

事实优先级为：当前 Git 与工作树、可复现测试/运行证据、STATUS 与权威治理文件。聊天记忆仅作辅助。如果这些来源冲突，不得为了匹配文档而修改 Git，应停止并报告冲突。

## 5. 修改纪律

任何代码修改必须：

1. 说明目的和授权来源；
2. 限定修改范围，保留无关文件和用户已有改动；
3. 按风险完成专项测试、回归和必要的运行验证；
4. 明确记录已验证、未验证、风险和回滚方式；
5. 输出结果报告，包括修改文件、测试结果、Git 状态和下一步授权需求。

没有明确授权时，不得修改高权限治理文件、扩大阶段范围、执行外部服务动作或自动进入下一阶段。
