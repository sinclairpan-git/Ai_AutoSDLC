# Continuity Handoff

- Updated: 2026-08-25T13:22:43+00:00
- Reason: 记录首轮合议 REJECT、事实纠偏与 formal-only 整改边界
- Goal: 整改 WI219 首轮合议阻断，仅冻结 formal 合同并等待 round 2；批准前不进入产品实现
- State: 首轮合议 REJECT 已完成事实裁决。formal 已加入 behind-only remote-ref truth 基准、精确 formal-control classification、完整 active-WI consumer matrix、双模板 semantic-set 验收；已删除 adapter scope escape hatch。
- Stage: close
- Work Item: 219-mainline-truth-roi-contract
- Branch: feature/219-mainline-truth-roi-contract-docs

## Changed Files
- M specs/219-mainline-truth-roi-contract/plan.md
- M specs/219-mainline-truth-roi-contract/spec.md
- M specs/219-mainline-truth-roi-contract/task-execution-log.md
- M specs/219-mainline-truth-roi-contract/tasks.md

## Key Decisions
- 不移动本地 main、不 fetch、不新增状态或解析器。truth base 只在本地 default 落后已有 origin ref 时只读使用 remote；formal-only 仅忽略精确列出的 control paths；任何其他路径仍是 execution evidence。指标只记 cost/risk，越过冻结边界或缺少必要性证据才暂停。

## Commands / Tests
- Round 1: autonomy APPROVE after WI198 correction; hard-guardrail APPROVE_WITH_CONDITIONS; balanced REJECT; chair REJECT
- workitem truth-check at b3665d7e: branch_only_implemented, execute_started=yes, main divergence 221/0
- git main...origin/main: local main c0f333c8 is 220 commits behind origin/main 76252746

## Blockers / Risks
- Round 2 未对同一新 SHA 关闭全部有效 Critical/Important 前禁止实施；若整改需要 GitClient/writer/schema/Runner/ProgramService、新状态或 Markdown parser，立即 No-Go/needs_user。

## Local PR Review
- none

## Exact Next Steps
- 完成 formal 自审与 Program Truth/constraints/manifest 验证，提交新 formal SHA；随后原三席 round 2 审同一 base/head。
