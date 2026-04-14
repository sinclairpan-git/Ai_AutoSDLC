# Tasks — 139 Branch Lifecycle Direct Formal Runtime Closure

## Batch A：Truth audit

### Task 139.1 固定 `007/008` 已落地 runtime 的真实覆盖面

- 核对 branch inventory/traceability、close-check、branch-check、verify/status/doctor 与 direct-formal scaffold/CLI/tests
- 明确 `T44` 的真实缺口是 backlog carrier 缺失，而不是 branch lifecycle/direct-formal runtime 仍未实现

## Batch B：Focused verification

### Task 139.2 用 fresh verification 证明 branch lifecycle/direct-formal closure 已成立

- 运行 focused tests，覆盖 branch lifecycle inventory/disposition、direct-formal scaffold、CLI init/close-check/branch-check 与 bounded governance/readiness surfaces
- 确认 read-only / single-canonical 边界在当前工作区依然成立

## Batch C：Formal 回链与评审

### Task 139.3 回填 backlog / project-state 并完成对抗评审

- 将 `120/T44` 的建议派生工单升级为正式 `139`
- 回填 `T44` 的派生状态与当前 closure 结论
- 用对抗 reviewer 固定 “runtime 已闭环，但仍保持 read-only branch truth 与 single canonical entry” 的边界
