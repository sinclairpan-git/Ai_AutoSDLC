---
related_doc:
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
---
# 任务分解：Frontend Program Execute Runtime Baseline

**编号**：`020-frontend-program-execute-runtime-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-020-001 ~ FR-020-012 / SC-020-001 ~ SC-020-005）

---

## 分批策略

```text
Batch 1: execute runtime truth freeze
Batch 2: execute / recheck / remediation boundary freeze
Batch 3: implementation handoff and verification freeze
```

---

## 执行护栏

- `020` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `020` 不得改写 `014` 已冻结的 runtime attachment truth。
- `020` 不得改写 `018` 已冻结的 gate / recheck boundary truth。
- `020` 不得改写 `019` 已冻结的 per-spec readiness truth。
- `020` 不得在当前 child work item 中直接启用 scanner/provider 写入、auto-attach、auto-fix、registry 或 cross-spec writeback。
- `020` 不得把 `program --execute` 扩张成新的默认前端自动编排入口。
- 当前 docs baseline 只冻结 execute preflight / recheck / remediation hint 边界，不放行任何 `src/` / `tests/` 实现。

---

## Batch 1：execute runtime truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `020` 是 `019` 下游的 frontend program execute runtime child work item
  2. `spec.md` 明确 execute runtime 只消费 `019` per-spec readiness truth 与 `018` recheck boundary
  3. `spec.md` 不再依赖临时对话才能解释 `020` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 scanner/provider 写入、auto-attach、auto-fix、registry 与 cross-spec writeback 不属于当前 work item
  2. formal docs 明确 recheck 是 bounded handoff，不是后台 loop
  3. 不再出现 execute runtime 被表述成默认修复器的表述
- **验证**：scope review

### Task 1.3 冻结 execute 输入真值与 source linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 execute gate 的输入至少包括 readiness state、blockers、recheck_required、remediation hint 与 source linkage
  2. formal docs 明确这些输入按 spec 粒度暴露，而不是伪全局 verdict
  3. formal docs 明确 `020` 不新增 program 私有 execute truth
- **验证**：truth-order review

---

## Batch 2：execute / recheck / remediation boundary freeze

### Task 2.1 冻结 execute preflight responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `program integrate --execute` 的 frontend preflight 阻断责任
  2. formal docs 明确 close/dependency/dirty-tree gate 与 frontend execute gate 的关系
  3. formal docs 明确 execute preflight 只做只读决策，不默认触发写入
- **验证**：responsibility review

### Task 2.2 冻结 step-level recheck handoff

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 execute step 后何时需要 frontend recheck
  2. formal docs 明确 recheck 的最小输入/输出与提示边界
  3. formal docs 明确 recheck 不会被实现成无限 loop 或默认 auto-fix 入口
- **验证**：语义对账

### Task 2.3 冻结 remediation hint 与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation hint 只做诊断 handoff，不默认触发 auto-fix
  2. formal docs 明确未来 auto-fix engine 仍由下游工单承接
  3. formal docs 明确 `020` 与 `014 / 018 / 019` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `019` / `018` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 execute preflight、recheck handoff、remediation hint 与 downstream auto-fix guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 auto-fix / writeback 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`, `specs/020-frontend-program-execute-runtime-baseline/plan.md`, `specs/020-frontend-program-execute-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 execute runtime、recheck 与 remediation hint 保持单一真值
  3. 当前分支上的 `020` formal docs 可作为后续进入 execute preflight 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`
