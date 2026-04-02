---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Contract Authoring Baseline

**编号**：`011-frontend-contract-authoring-baseline` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-011-001 ~ FR-011-015 / SC-011-001 ~ SC-011-006）

---

## 分批策略

```text
Batch 1: contract truth surface freeze
Batch 2: artifact chain and legacy extension baseline
Batch 3: implementation handoff and verify freeze
```

---

## 执行护栏

- `011` 当前只允许推进 `spec.md / plan.md / tasks.md` 这组 formal docs。
- `011` 不得把 UI Kernel、Provider、Gate 或 runtime 代码混入当前 child work item 的 formal baseline。
- 只有在用户明确要求进入实现，且 `011` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：contract truth surface freeze

### Task 1.1 冻结 Contract 范围与非目标

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `011` 是 `009` 下游的 `Contract` child work item
  2. `spec.md` 明确覆盖对象与非目标，包括 Kernel / Provider / Gate / runtime 不属于当前 work item
  3. `spec.md` 不再依赖临时对话才能解释 `011` 的边界
- **验证**：文档对账

### Task 1.2 冻结 Contract 对象边界与 recipe declaration 归属

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `page/module contract`、`Contract Rule Bundle`、`Contract Legacy Context` 等关键实体可被直接引用
  2. `recipe declaration` 归 Contract、`recipe standard body` 归 UI Kernel 的边界被明确写死
  3. `i18n / validation / hard rules / whitelist / token rules` 被明确纳入 MVP 首批 Contract 对象
- **验证**：文档交叉引用检查

### Task 1.3 冻结 Contract 是实例化 artifact 的单一口径

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Contract 是实例化 artifact，不是补充文档
  2. formal docs 明确 Contract 同时服务于生成、检查与修复
  3. formal docs 明确 Contract 不得退化为 prompt 注释或散落 Markdown
- **验证**：术语一致性检查

---

## Batch 2：artifact chain and legacy extension baseline

### Task 2.1 冻结 Contract 的 stage / artifact 链路

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 Contract 在 `refine / design / decompose / verify / execute / close` 中的落位
  2. formal docs 明确 `decompose / verify` 与后续 Gate 以 Contract 和代码对照，不以 prompt 为准
  3. 不再出现“Contract 只是设计阶段一次性产物”的表述
- **验证**：stage relationship review

### Task 2.2 冻结 Contract drift 处理口径

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确发现漂移后只能 `回写 Contract` 或 `修正实现代码`
  2. formal docs 明确不允许长期 Contract 失真
  3. formal docs 明确“先写代码后补 Contract”不属于允许路径
- **验证**：文档对账

### Task 2.3 冻结 legacy 扩展字段承载路径

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `compatibility_profile / migration_level / legacy_boundary_ref / migration_scope` 被明确收敛为 Contract 扩展字段
  2. formal docs 明确 MVP 不引入第二套迁移专用 artifact 系统
  3. legacy 口径与 `009` 母规格保持一致
- **验证**：全文术语检查

---

## Batch 3：implementation handoff and verify freeze

### Task 3.1 冻结后续实现文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/011-frontend-contract-authoring-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 Contract 模型、artifact 实例化、drift 检查和 Gate 接入的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的后续实现起点清晰，不需要再次回到 `009` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖模型形状、序列化、stage integration、legacy 扩展字段和 drift 正反向场景
  2. `tasks.md` 明确当前仍停在 formal baseline，不直接进入实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/011-frontend-contract-authoring-baseline/spec.md`, `specs/011-frontend-contract-authoring-baseline/plan.md`, `specs/011-frontend-contract-authoring-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 Contract 边界、artifact 链路、legacy 扩展字段和 handoff 口径保持单一真值
  3. 当前分支上的 `011` formal docs 可作为后续继续实现 Contract 主线的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`
