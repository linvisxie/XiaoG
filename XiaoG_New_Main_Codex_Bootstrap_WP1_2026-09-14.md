# XiaoG New Main Codex Bootstrap — WP-1

你现在接任 XiaoG 项目的 **Main Codex / Integrator**。

这是正常的 Main Codex 换窗，不是 Worker，不是第二个并行 Codex，也不是重新设计项目。

旧 Main Codex 已完成：

- Phase 5 Accepted Stable
- Engineering Foundation Accepted Stable
- WP-0 Web Preview Readiness Audit
- WP-0 最终文档提交：
  `818376df2a62eb20b8f0d7f0ad72f195543d0a03`
- `AUTOPILOT_SCOPE_COMPLETE`
- `HANDOFF_TO_TECH_LEAD_REQUIRED`

Product Owner 与 Tech Lead 已确认：

- Preview v1 采用受邀、隔离、ephemeral / non-persistent 模式；
- DeepSeek 是 Preview v1 第一条 Provider 路径；
- Terra 不取消，但属于 Conditional Preview Provider；
- Terra 只有在未来单独完成 Terra Server-side Readiness / Authentication Audit 并获批准后，才能加入 Preview；
- Terra 延迟或审计失败不得阻塞 DeepSeek Preview。

开始前按顺序完整读取：

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_READINESS_AUDIT.md`
6. `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_ENGINEERING_FOUNDATION_HANDOFF.md`
8. `XiaoG_Autopilot_Activation_Web_Preview_WP1_v1_2026-09-14.md`

若任一必需文件缺失、不可读或身份明显不一致，立即停止，不得依靠旧聊天记忆补写。

随后执行 Mandatory Provenance Check：

- branch
- HEAD
- tracked/untracked working tree
- latest relevant git log
- STATUS
- WP-0 audit
- runtime/config/provider/data-path reality

启动预期仅用于核验：

- branch: `main`
- expected HEAD:
  `818376df2a62eb20b8f0d7f0ad72f195543d0a03`
- expected working tree: clean
- STATUS: `HANDOFF_REQUIRED`
- milestone: `WP_0_WEB_PREVIEW_READINESS_AUDIT_COMPLETE`

如 Git 现实不同，以 Git / working tree / test evidence 为准。
绝不能为了让本指令、STATUS 或 Handoff 看起来一致而修改 Git。

本窗口唯一授权范围：

`XIAOG-AUTOPILOT-WEB-PREVIEW-WP1-2026-09-14-V1`

也就是：

**WP-1 — Release Baseline + Safe Ephemeral Preview Mode**

严格按照 Activation 执行。

特别注意：

- 允许本地 bounded code/config/test/docs changes；
- 不允许 GitHub/remote/push；
- 不允许 hosting/cloud/DNS；
- 不允许 external secrets；
- 不允许 public tunnel/listener；
- 不允许真实 Provider；
- 不允许 Terra server-side integration；
- 不允许 Controlled Dual-Codex / Worker；
- 不允许 DeepSeek Registry maintenance；
- 不允许 Phase 5.5 / Phase 6+。

WP-1 完成后必须停在 `HANDOFF_REQUIRED`，并输出：

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

不要继续进入 WP-2 或任何外部部署动作。

现在先完整读取文件并执行 provenance check，然后开始 WP-1。
