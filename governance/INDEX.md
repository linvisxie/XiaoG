# XiaoG Governance Index

## Governance 体系说明

`governance/` 用于管理 XiaoG 长期战略、当前状态、开发规范和项目演进记录。

- `governance/core/`：长期稳定核心文档。这里保存项目定义、路线、需求、治理规则、产品决策和长期愿景；高权限文件只能在明确授权下维护。
- `governance/current/`：当前运行状态与阶段记录。这里保存 STATUS、当前授权、计划、Handoff、暂停或恢复入口，以及当前阶段真正需要的治理材料。
- `governance/archive/`：已完成阶段和历史治理材料。归档保留原始历史，不要求逐份改写旧路径引用。

Git、当前 STATUS 和权威治理文件共同决定项目事实；聊天记忆只能辅助理解。发现路径、身份、Hash、Git 或 Handoff 冲突时，应停止推断并按 `XiaoG_MAIN_CODEX_ENTRY.md` 的 Recovery Path 核验。

## v3.0 核心文档导航

v3.0 是当前第三版总纲体系，其核心文档目录为 `governance/core/V3.0文档库/`。以下导航统一使用当前真实文件名和真实路径；在目录结构获得单独授权调整前，不得自行移动或改名。

| 当前文件名 | 当前物理路径 | 定位 |
|---|---|---|
| `XiaoG_v3.0_Master_Document（第三版总纲）.md` | `governance/core/V3.0文档库/XiaoG_v3.0_Master_Document（第三版总纲）.md` | 第三版总纲，最高级项目定义文件；用于理解 XiaoG 为什么存在、当前状态、最终目标与总体推进方式。 |
| `XiaoG_Master_Roadmap_v3.0_FINAL（阶段执行路线）.md` | `governance/core/V3.0文档库/XiaoG_Master_Roadmap_v3.0_FINAL（阶段执行路线）.md` | 阶段执行路线；定义阶段目标、顺序和进入条件。 |
| `XiaoG_Feature_Requirement_Registry_v3.0（功能需求）.md` | `governance/core/V3.0文档库/XiaoG_Feature_Requirement_Registry_v3.0（功能需求）.md` | 功能需求库；用于查找能力需求、范围和归属。 |
| `XiaoG_Project_Governance_Manual_v3.0（治理规范）.md` | `governance/core/V3.0文档库/XiaoG_Project_Governance_Manual_v3.0（治理规范）.md` | 开发治理规范；约束授权、修改范围、验证、报告、Git、架构变更和开源复用。 |
| `XiaoG_v3.0_Migration_Master_Table（迁移记录）.md` | `governance/core/V3.0文档库/XiaoG_v3.0_Migration_Master_Table（迁移记录）.md` | v2→v3 迁移记录；说明旧体系内容在第三版中的去向。 |
| `XiaoG_Historical_Evolution_and_Decision_Log_v3.0（历史决策）.md` | `governance/core/V3.0文档库/XiaoG_Historical_Evolution_and_Decision_Log_v3.0（历史决策）.md` | 历史决策记录；保存演进背景、已作决定和理由。 |
| `XiaoG_Final_Vision_and_Capability_Blueprint_v3.0（最终愿景）.md` | `governance/core/V3.0文档库/XiaoG_Final_Vision_and_Capability_Blueprint_v3.0（最终愿景）.md` | 最终愿景与能力蓝图；定义 XiaoG 长期产品形态和能力边界。 |

`XiaoG_Master_Roadmap_v3.0（旧版）.md` 是历史版本，不是 v3.0 FINAL 阶段执行路线。任何 Agent 使用 v3.0 文档前都应确认所引用的物理文件存在且已纳入当前 Git 基线。

## Agent 阅读顺序

第一次接触 XiaoG：

1. `XiaoG_MAIN_CODEX_ENTRY.md`

   ↓

2. `governance/core/V3.0文档库/XiaoG_v3.0_Master_Document（第三版总纲）.md`

   ↓

3. `governance/current/`：先读最新 STATUS，再读 STATUS 指向的当前 Activation、Handoff 或 Pause Handoff

   ↓

4. `governance/core/V3.0文档库/XiaoG_Feature_Requirement_Registry_v3.0（功能需求）.md`

   ↓

5. 根据任务读取对应 Roadmap、Governance Manual、Architecture、Product Decision 或必要历史材料

正常连续开发仍遵循 `XiaoG_MAIN_CODEX_ENTRY.md` 的 Fast Path；只有首次接管、恢复、身份冲突、重大架构或路线决策等情况才扩大到 Cold Start / Recovery Path。

## Canonical paths

- Core Protocol (immutable): `governance/core/XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
- Master Roadmap (immutable): `governance/core/XiaoG_Master_Roadmap_v2_2026-09-12.md`
- Public Preview Addendum (Tech Lead controlled): `governance/core/XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
- Product Decision (Tech Lead controlled): `governance/core/XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
- Current STATUS: `governance/current/XiaoG_AUTOPILOT_STATUS.md`
- Current Pause Handoff: `governance/current/XiaoG_PAUSE_HANDOFF.md`
- Current WP-5B Handoff: `governance/current/XiaoG_WEB_PREVIEW_WP5B_HANDOFF.md`
- Current WP-5B Deployment Readiness Checklist: `governance/current/WP5B_DEPLOYMENT_READINESS_CHECKLIST.md`
- Retained WP-4 Activation: `governance/current/XiaoG_Autopilot_Activation_Web_Preview_WP4_v1_2026-09-14.md`
- Retained WP-4 Plan: `governance/current/XiaoG_WEB_PREVIEW_WP4_PLAN_2026-09-14.md`
- Retained WP-4 Handoff: `governance/current/XiaoG_WEB_PREVIEW_WP4_HANDOFF.md`

Archives: `governance/archive/wp0`, `wp1`, `wp2`, `wp3`; Foundation: `governance/archive/foundation`.

Historical documents may retain old path references as part of their original record; this index provides the current canonical paths without rewriting history.

Main Codex may maintain STATUS, Handoffs, archive moves, this index, and entry material under explicit Tech Lead authorization. It may not alter the Core Protocol, Master Roadmap, or Product Decision text, initiate an Activation, or advance a phase autonomously.

Use the Fast Path and Cold Start/Recovery Path in `XiaoG_MAIN_CODEX_ENTRY.md`.
