# Tasks — 136 Frontend P1 Recheck Remediation Feedback Runtime Closure

## Batch A：Truth audit

### Task 136.1 固定 `066-070` 已落地 runtime 与真实缺口

- 核对 remediation input、recheck handoff、CLI integrate surface 与 writeback preservation 的现状
- 明确 `T41` 的真实缺口是 `070` consumer mismatch，而不是 feedback runtime 完全缺失

## Batch B：Routing hardening

### Task 136.2 用 TDD 关闭 remediation / recheck 分流偏差

- 先写 red tests 固定 `070/FR-070-006`：只有 `READY` 进入 recheck handoff
- 修复 `ProgramService` 的分流逻辑，让 `recheck_required` / stable empty / evidence gap 回到 remediation input
- 确认 CLI integrate surface 与 remediation handoff 文案同步更新

## Batch C：Formal 回链与评审

### Task 136.3 回填 backlog / project-state 并完成 focused verification / 对抗评审

- 将 `120/T41` 的建议派生工单升级为正式 `136`
- 回填 `T41` 的派生状态与当前 closure 结论
- 用 focused verification 与 reviewer 固定 `T41 -> T42` 的边界
