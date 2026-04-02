---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：前端治理与 UI Kernel

**编号**：`009-frontend-governance-ui-kernel` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-009-001 ~ FR-009-015 / SC-009-001 ~ SC-009-008）

---

## 分批策略

```text
Batch 1: formal baseline freeze and single-truth alignment
Batch 2: workstream slicing and execution boundary freeze
Batch 3: legacy / compatibility policy freeze and verify handoff
```

---

## 执行护栏

- `009` 当前只允许推进 `spec.md / plan.md / tasks.md` 这组 formal docs。
- 任何 `src/` / `tests/` 实现都必须先创建 downstream child work item，再进入 execute。
- `docs/superpowers/*` 在本 work item 中始终只是 reference-only 输入，不再承担 canonical execute truth。

---

## Batch 1：formal baseline freeze and single-truth alignment

### Task 1.1 冻结 canonical formal spec

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确覆盖范围 / 不覆盖范围
  2. `spec.md` 锁定 `Kernel / Provider / Contract / legacy / compatibility` 五类核心边界
  3. `spec.md` 不再依赖 `docs/superpowers/*` 才能表达 canonical truth
- **验证**：文档对账

### Task 1.2 冻结 canonical formal plan

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/009-frontend-governance-ui-kernel/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 明确当前 work item 先停在 formal baseline，不直接进入代码实现
  2. `plan.md` 明确后续 workstream 切分和执行顺序
  3. `plan.md` 明确 frozen design 只是 `related_doc`，不是第二套 canonical 正文
- **验证**：文档对账

### Task 1.3 冻结 canonical formal tasks

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/009-frontend-governance-ui-kernel/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 使用 parser-friendly 结构
  2. 任务分批遵循 `Batch -> Task -> 验收标准 -> 验证方式` 的可执行格式
  3. 任务默认围绕 formal baseline 与后续拆解，不提前越界到实现代码
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

---

## Batch 2：workstream slicing and execution boundary freeze

### Task 2.1 切分五条主 workstream

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`, `specs/009-frontend-governance-ui-kernel/plan.md`, `specs/009-frontend-governance-ui-kernel/tasks.md`
- **可并行**：否
- **验收标准**：
  1. work item 至少拆分为 `Contract / UI Kernel / enterprise-vue2 provider / 前端生成约束 / Gate-Recheck-Auto-fix` 五条主线
  2. 每条主线都明确写出边界、输入真值和 downstream handoff 目标
  3. 不再把大方案表述为一个不可执行的单块
- **验证**：文档交叉引用检查

### Task 2.2 冻结 MVP / P1 / P2 执行边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`, `specs/009-frontend-governance-ui-kernel/plan.md`
- **可并行**：否
- **验收标准**：
  1. MVP 仅保留 `Vue2 企业项目 + 最小治理闭环 + legacy 轻量兼容` 口径
  2. P1 / P2 继续承接体验稳定层与 modern provider 路线
  3. `spec.md` 与 `plan.md` 都出现同一套 `MVP / P1 / P2` 边界
  4. 不再出现“首版即完成终局能力”的表述
- **验证**：文档对账

### Task 2.3 锁定 formal 真值顺序与执行前提

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`, `specs/009-frontend-governance-ui-kernel/plan.md`
- **可并行**：否
- **验收标准**：
  1. `PRD/spec -> Contract -> code` 真值顺序被明确写死
  2. gate 以 `Contract` 与代码对照，不以 prompt 为准
  3. `recipe standard body != recipe declaration`、`Kernel != Provider` 等核心关系可被直接引用
  4. 后续任何 `src/` / `tests/` 实现都必须先挂到 downstream child work item
- **验证**：文档术语与交叉引用检查

---

## Batch 3：legacy / compatibility policy freeze and verify handoff

### Task 3.1 冻结 legacy 策略与 Compatibility 执行口径

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T23
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`, `specs/009-frontend-governance-ui-kernel/plan.md`, `specs/009-frontend-governance-ui-kernel/tasks.md`
- **可并行**：否
- **验收标准**：
  1. legacy 统一口径明确为“存量兼容、增量收口、边界隔离、渐进迁移”
  2. Compatibility 被表述为同一套 gate matrix 的兼容执行口径，而不是第二套规则系统
  3. MVP legacy 信息优先以 `page/module contract` 扩展字段承载，不引入 artifact 爆炸
- **验证**：全文术语检查

### Task 3.2 建立 verify handoff 基线

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/009-frontend-governance-ui-kernel/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 明确后续 design/decompose/verify 应继续以 `009` formal docs 为入口
  2. work item 不再要求回到 `docs/superpowers/*` 继续固化真值
  3. formal baseline 具备进入下一轮 verify constraints 的最小条件
  4. 只读 handoff 命令至少包含 `uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem truth-check --wi specs/009-frontend-governance-ui-kernel`、`git status --short`
- **验证**：`uv run ai-sdlc verify constraints`

### Task 3.3 只读校验并冻结当前设计/分解基线

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/009-frontend-governance-ui-kernel/spec.md`, `specs/009-frontend-governance-ui-kernel/plan.md`, `specs/009-frontend-governance-ui-kernel/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `git status --short` 在文档提交前保持可解释
  3. 当前关联分支上的 formal docs 可作为后续继续拆解或创建 child work item 的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`
