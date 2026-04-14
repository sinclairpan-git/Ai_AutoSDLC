# Tasks — 137 Frontend P1 Visual A11y Runtime Foundation Closure

## Batch A：Truth audit

### Task 137.1 固定 `071` 已落地 runtime foundation 的真实覆盖面

- 核对 policy model、gate verification、verify/program surfaces 与相关 tests
- 明确 `T42` 的真实缺口是 backlog carrier 缺失，而不是 visual/a11y runtime 仍未实现

## Batch B：Focused verification

### Task 137.2 用 fresh verification 证明 `071` runtime closure 已成立

- 运行 focused tests，覆盖 visual/a11y policy truth、gate verification、verify CLI 与 program feedback surfaces
- 确认 evidence gap / stable empty / actual issue 的 runtime 边界仍然成立

## Batch C：Formal 回链与评审

### Task 137.3 回填 backlog / project-state 并完成对抗评审

- 将 `120/T42` 的建议派生工单升级为正式 `137`
- 回填 `T42` 的派生状态与当前 closure 结论
- 用对抗 reviewer 固定 “runtime 已闭环，但仍非完整质量平台” 的边界
