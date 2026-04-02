---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Gate Compatibility Baseline

**编号**：`018-frontend-gate-compatibility-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-018-001 ~ FR-018-012 / SC-018-001 ~ SC-018-005）

---

## 分批策略

```text
Batch 1: gate truth freeze
Batch 2: matrix / output / recheck / fix boundary freeze
Batch 3: implementation handoff and verification freeze
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `018` 不得重新定义 `011` Contract truth 或 `017` generation control plane truth。
- `018` 不得在当前 child work item 中直接进入完整 gate runtime、recheck agent、auto-fix engine 或第二套 compatibility rules 实现。
- `018` 只冻结 gate / compatibility baseline，不默认决定任何 `src/` / `tests/` runtime side effect。
- 只有在用户明确要求进入实现，且 `018` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：gate truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `018` 是 `009` 下游的 gate / compatibility child work item
  2. `spec.md` 明确它承接 `verify -> execute -> verify -> close/report` 闭环中的 gate / recheck / auto-fix 口径
  3. `spec.md` 不再依赖临时对话或设计稿才能解释 `018` 的边界
- **验证**：文档对账

### Task 1.2 冻结 Compatibility 与 gate 边界

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Compatibility 是同一套 gate matrix 的执行强度，不是第二套规则或第二套 gate
  2. formal docs 明确 Gate / Recheck / Auto-fix 只能消费上游 truth
  3. 不再出现兼容执行被表述成平行系统的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`, `specs/018-frontend-gate-compatibility-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确完整 gate runtime、recheck agent 与 auto-fix engine 不属于当前 work item
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 gate matrix / compatibility policy / report models，而不是直接写完整闭环执行器
- **验证**：scope review

---

## Batch 2：matrix / output / recheck / fix boundary freeze

### Task 2.1 冻结 MVP gate matrix 与输入来源

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 MVP gate matrix 覆盖 i18n、validation、Vue2 hard rules、recipe、whitelist、token
  2. formal docs 明确 gate 输入来源
  3. formal docs 明确 Compatibility 的三档执行强度
- **验证**：gate-matrix review

### Task 2.2 冻结结构化输出、Recheck 与 Auto-fix 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确检查输出至少包括 `Violation / Coverage / Drift / legacy expansion`
  2. formal docs 明确 Recheck 的定位、触发时机与输出
  3. formal docs 明确 Auto-fix 的输入、定向修复原则与 MVP 范围
- **验证**：语义对账

### Task 2.3 冻结优先级与 downstream handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`, `specs/018-frontend-gate-compatibility-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 gate / recheck / fix 的判定优先级与修复优先级
  2. formal docs 明确 `verify / execute / close` 的接入边界
  3. formal docs 明确 `018` 与 `017` generation control plane 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/018-frontend-gate-compatibility-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `models / reports / gates / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/018-frontend-gate-compatibility-baseline/plan.md`, `specs/018-frontend-gate-compatibility-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 gate matrix、Compatibility policy、结构化输出与 recheck/fix 边界
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行完整 gate runtime / auto-fix engine 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/018-frontend-gate-compatibility-baseline/spec.md`, `specs/018-frontend-gate-compatibility-baseline/plan.md`, `specs/018-frontend-gate-compatibility-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 gate truth、Compatibility、结构化输出与 handoff 保持单一真值
  3. 当前分支上的 `018` formal docs 可作为后续进入 gate matrix 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`
