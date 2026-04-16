# 开发总结：146-program-truth-pipeline-injection-baseline

**功能编号**：`146-program-truth-pipeline-injection-baseline`
**收口日期**：2026-04-16
**收口状态**：`program-close-ready`

## 交付摘要

- `146` 已从 formal baseline 进入实现切片，并把 global truth 真正接入 `workitem init / close-check / program status / program truth audit / runner close context`。
- `workitem init` 现在会在存在 `program-manifest.yaml` 时尝试 materialize `specs[]` entry，并明确提示 `python -m ai_sdlc program truth sync --execute --yes`。
- `close-check` 现在会把 `manifest_unmapped`、`truth_snapshot_stale`、`capability_blocked` 区分为独立 blocker；`program status` / `program truth audit` 也会给出 next required truth action。
- 仓库规则面已新增 `truth-only` verification profile，并与 `verify constraints`、PR checklist、用户手册保持一致。
- root truth 已按新口径刷新：source inventory 维持 `757/757 mapped`，`146`/`147` 继续处于 `ready / advisory_only`，但整体 release target 仍因 frontend mainline 一组 workitem 的 `close_check` blocker 保持 `blocked`。
- `146` 的收口代表：pipeline truth injection 缺口已经落地进入日常主链；它仍不代表任何前端业务 capability 已额外完成。

## 备注

- 本次实现严格限制在 truth injection pipeline 与对应规则/测试面；未顺带扩展到前端业务 capability。
- 根级 truth snapshot 仍保持显式写入边界；`status`、`close-check`、`run` 不会偷写 snapshot。
