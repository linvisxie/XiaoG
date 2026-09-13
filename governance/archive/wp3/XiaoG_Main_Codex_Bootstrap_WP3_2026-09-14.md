# XiaoG Main Codex Bootstrap — WP-3

继续担任 XiaoG 项目的 **Main Codex / Integrator**。

WP-2 已通过 Tech Lead 审核并正式 Accepted / Closed。

当前新授权窗口：

`XIAOG-AUTOPILOT-WEB-PREVIEW-WP3-2026-09-14-V1`

目标：

**WP-3 — Invited Access / Rate / Cost / Abuse Boundary**

开始前按顺序完整读取：

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`
6. `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_WEB_PREVIEW_WP3_PLAN_2026-09-14.md`
8. `XiaoG_Autopilot_Activation_Web_Preview_WP3_v1_2026-09-14.md`

如果任一必需文件缺失、身份无法确认或治理冲突，停止并报告，不得自行补写替代版本。

Mandatory Provenance Check：

- current branch
- current HEAD
- tracked/untracked working tree
- recent relevant Git log
- latest STATUS
- WP-2 Handoff
- Preview runtime/session/data reality
- Preview secret-loading reality
- Provider invocation boundary
- current frontend/API route surface

启动预期：

- branch: `main`
- expected HEAD:
  `4d7eb3271b86661108a485c22a3ef321210498bf`
- accepted WP-2 candidate:
  `da5bb6c27ab3c33b7275eac8e686b16c53e057ad`
- working tree: clean
- no remote

以上仅是预期。
Git object/history > working tree > tests/runtime evidence > STATUS > Handoff > chat memory。
不得为了匹配预期修改 Git。

本轮只允许 WP-3：

- invite-only access
- authenticated Preview session
- per-invite/global rate limits
- per-invite/global concurrency limits
- spend-risk controls
- minimal abuse protection
- minimal invited-access frontend UI
- deterministic local tests/docs/status/handoff

Preview v1 的访问模型应保持简单：

- 每位邀请者使用独立高熵 invite credential
- 不开放注册
- 不做 email/password 用户系统
- 不做 OAuth
- invite secret 只存在于 server-side secret/config boundary
- 成功认证后换取 opaque HttpOnly Preview session
- session 与 invite identity 绑定
- failed auth 不得创建 session SQLite
- quota 应按 invite identity 聚合，而不是只按浏览器 tab

严格禁止：

- GitHub login/repo/remote/push
- hosting/cloud
- DNS/domain
- external secret entry
- 给真实外部用户发邀请码
- public/external access
- tunnel/public listener
- real Provider/API
- provider billing/spend configuration
- container registry publish
- Terra server-side integration
- WP-4
- Controlled Dual-Codex/Worker
- DeepSeek Registry maintenance
- Phase 5.5/6+

所有测试必须使用 fake/local dependencies。

如果任何步骤必须使用外部服务或真实 credential：

立即停止，报告最小 Product Owner 授权需求，不得自行执行。

完成 WP-3 后生成：

`XiaoG_WEB_PREVIEW_WP3_HANDOFF.md`

更新：

`XiaoG_AUTOPILOT_STATUS.md`

停在：

`HANDOFF_REQUIRED`

最终输出：

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

不得自动进入 WP-4 或部署。

现在先完成全部文件读取和 Mandatory Provenance Check，再开始 WP-3。
