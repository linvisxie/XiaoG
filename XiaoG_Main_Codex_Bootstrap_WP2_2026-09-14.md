# XiaoG Main Codex Bootstrap — WP-2

继续担任 XiaoG 项目的 **Main Codex / Integrator**。

WP-1 已完成并通过 Tech Lead 审核。不要重新执行 WP-1，也不要自行进入 WP-3。

当前新授权窗口：

`XIAOG-AUTOPILOT-WEB-PREVIEW-WP2-2026-09-14-V1`

目标：

**WP-2 — Isolated Runtime / Data / Secret Boundary**

开始前完整读取：

1. `XiaoG_Autopilot_Core_Protocol_v1.4_FINAL_2026-09-12.md`
2. `XiaoG_Master_Roadmap_v2_2026-09-12.md`
3. `XiaoG_Roadmap_Addendum_Public_Preview_v1_2026-09-13.md`
4. `XiaoG_Public_Preview_Product_Decision_v1_2026-09-14.md`
5. `XiaoG_WEB_PREVIEW_WP1_HANDOFF.md`
6. `XiaoG_AUTOPILOT_STATUS.md`
7. `XiaoG_WEB_PREVIEW_WP2_PLAN_2026-09-14.md`
8. `XiaoG_Autopilot_Activation_Web_Preview_WP2_v1_2026-09-14.md`

如果任一文件缺失或身份不一致，停止并报告。

Mandatory Provenance Check：

- current branch
- HEAD
- tracked/untracked working tree
- recent relevant Git log
- STATUS
- WP-1 Handoff
- current Preview runtime/config/data/session/provider/secret reality

启动预期：

- branch: `main`
- expected HEAD:
  `31bd46ba8335d3893e6cd7d0ae1f924948a5618e`
- working tree: clean
- no remote
- state: `HANDOFF_REQUIRED`
- milestone:
  `WP_1_RELEASE_BASELINE_AND_SAFE_EPHEMERAL_PREVIEW_MODE_COMPLETE`

这些只是预期。Git / working tree / test evidence 才是实时工程事实。
不要为了对齐预期修改 Git。

WP-2 允许本地 bounded code/config/test/docs work，用于：

- Linux/container release contract
- isolated Preview runtime/data/log boundary
- server-side secret interface
- HTTPS/reverse-proxy/SSE requirements
- immutable release identity
- rollback contract
- deterministic local deployment smoke

严格禁止：

- GitHub login/repo/remote/push
- hosting/cloud resources
- DNS/domain
- external secret entry
- public exposure/tunnel
- real Provider/API
- Terra server-side integration
- WP-3/WP-4
- Controlled Dual-Codex/Worker
- DeepSeek Registry maintenance
- Phase 5.5/6+

如果任何一步必须使用外部服务或真实 secret，立即停下并报告需要的最小 Product Owner 授权，不得自行执行。

完成 WP-2 后生成：

`XiaoG_WEB_PREVIEW_WP2_HANDOFF.md`

并停在：

`HANDOFF_REQUIRED`

最终输出：

`AUTOPILOT_SCOPE_COMPLETE`

`HANDOFF_TO_TECH_LEAD_REQUIRED`

现在先读取全部文件并执行 provenance check，然后开始 WP-2。
