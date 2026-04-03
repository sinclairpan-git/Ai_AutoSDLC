---
related_doc:
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
---
# 任务分解：Frontend Program Remediation Runtime Baseline

**编号**：`021-frontend-program-remediation-runtime-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-021-001 ~ FR-021-009 / SC-021-001 ~ SC-021-005）

---

## 分批策略

```text
Batch 1: remediation runtime truth freeze
Batch 2: remediation input / handoff boundary freeze
Batch 3: implementation handoff and verification freeze
```

---

## 执行护栏

- `021` 当前只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `021` 不得改写 `018` 已冻结的 gate / fix-input truth。
- `021` 不得改写 `019` 已冻结的 per-spec readiness truth。
- `021` 不得改写 `020` 已冻结的 execute / recheck truth。
- `021` 不得在当前 child work item 中直接启用 scanner/provider 写入、auto-fix、registry 或 cross-spec writeback。
- `021` 不得把 remediation runtime 扩张成新的默认前端自动编排入口。
- 当前 docs baseline 只冻结 remediation input / fix-input packaging / handoff 边界，不放行任何 `src/` / `tests/` 实现。

---

## Batch 1：remediation runtime truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `021` 是 `020` 下游的 frontend program remediation runtime child work item
  2. `spec.md` 明确 remediation runtime 只消费 `020` execute/recheck truth 与 `018` fix-input boundary
  3. `spec.md` 不再依赖临时对话才能解释 `021` 的边界
- **验证**：文档对账

### Task 1.2 冻结 non-goals 与 explicit guard

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 scanner/provider 写入、auto-fix、registry 与 cross-spec writeback 不属于当前 work item
  2. formal docs 明确 bounded remediation runtime 不等于完整 auto-fix engine
  3. 不再出现 remediation runtime 被表述成默认修复器的表述
- **验证**：scope review

### Task 1.3 冻结 remediation 输入真值与 source linkage

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`, `specs/021-frontend-program-remediation-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation input 的最小暴露面至少包括 remediation state、fix inputs、blockers、suggested actions 与 source linkage
  2. formal docs 明确这些输入按 spec 粒度暴露，而不是伪全局 verdict
  3. formal docs 明确 `021` 不新增 program 私有 remediation truth
- **验证**：truth-order review

---

## Batch 2：remediation input / handoff boundary freeze

### Task 2.1 冻结 remediation input packaging responsibility

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation input / fix-input packaging 的 responsibility
  2. formal docs 明确 input packaging 只做组织和诚实表达，不默认写入代码
  3. formal docs 明确与 `018` fix-input boundary 的关系
- **验证**：responsibility review

### Task 2.2 冻结 remediation handoff 与 operator surface

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation handoff 的最小输入/输出与提示边界
  2. formal docs 明确 operator-facing remediation surface 何时只显示建议、何时需要人工确认
  3. formal docs 明确 handoff 不会被表述成 auto-fix 已执行
- **验证**：语义对账

### Task 2.3 冻结 downstream handoff 与 future auto-fix boundary

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`, `specs/021-frontend-program-remediation-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 remediation runtime 与 future auto-fix engine 的边界
  2. formal docs 明确 writeback / registry 仍由下游工单承接
  3. formal docs 明确 `021` 与 `018 / 020` 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `020` / `018` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/plan.md`, `specs/021-frontend-program-remediation-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 remediation input packaging、handoff surface 与 downstream auto-fix guard
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 auto-fix / writeback 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`, `specs/021-frontend-program-remediation-runtime-baseline/plan.md`, `specs/021-frontend-program-remediation-runtime-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 remediation runtime、fix-input packaging 与 handoff 保持单一真值
  3. 当前分支上的 `021` formal docs 可作为后续进入 remediation input 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`
