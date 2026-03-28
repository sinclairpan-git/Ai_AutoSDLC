# 任务分解：AI-SDLC 原 PRD 跨域旧债补充合同

**编号**：`003-cross-cutting-authoring-and-extension-contracts` | **日期**：2026-03-28  
**来源**：plan.md + spec.md（RG-016 ~ RG-019 / FR-003-001 ~ FR-003-015）

---

## 分批策略

```text
Batch 1: contract models              (draft PRD / reviewer / backend / release evidence)
Batch 2: PRD draft authoring          (one-line idea -> draft PRD)
Batch 3: Human Reviewer checkpoints   (approve / revise / block + decision log)
Batch 4: backend delegation / fallback
Batch 5: NFR / release gate surfaces
```

---

## Batch 1：contract models

### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型

- **优先级**：P1
- **依赖**：无
- **输入**：[`src/ai_sdlc/models/work.py`](../../src/ai_sdlc/models/work.py)、[`spec.md`](spec.md)
- **验收标准**：
  1. `draft_prd` 与 `final_prd` 状态可区分。
  2. reviewer checkpoint / decision / next action 可落盘。
  3. release gate evidence / verdict 可结构化表达 PASS / WARN / BLOCK。
- **验证**：新增/扩展模型单测

### Task 1.2 — 定义 backend capability / selection / fallback 合同

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/backends/native.py`](../../src/ai_sdlc/backends/native.py)
- **验收标准**：
  1. backend capability coverage 可枚举。
  2. backend choice 与 fallback result 可被记录。
- **验证**：`uv run pytest tests/unit/test_backends.py -v`

---

## Batch 2：PRD draft authoring

### Task 2.1 — 实现一句话想法 -> draft PRD 生成入口

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/studios/prd_studio.py`](../../src/ai_sdlc/studios/prd_studio.py) 或新增 authoring 模块、[`tests/unit/test_prd_studio.py`](../../tests/unit/test_prd_studio.py)
- **验收标准**：
  1. 一句话输入可生成结构完整的 PRD draft。
  2. 未决项必须显式占位，不得伪装成事实。
  3. 输出包含后续 PRD Gate 可消费的结构化元数据。
- **验证**：定向 unit tests

### Task 2.2 — 保持 readiness review 与 draft authoring 的兼容边界

- **优先级**：P1
- **依赖**：Task 2.1
- **验收标准**：
  1. 现有 readiness review 不被破坏。
  2. draft/final 两条路径的输入输出边界清晰。
- **验证**：`uv run pytest tests/unit/test_prd_studio.py -v`

---

## Batch 3：Human Reviewer checkpoints

### Task 3.1 — 定义 reviewer decision artifact 与状态读取 surface

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：新/扩展 reviewer 决策模块、`close_check.py`、`verify_constraints.py`
- **验收标准**：
  1. `approve` / `revise` / `block` 三种结果都有正式记录。
  2. 记录包含时间、原因、目标对象、下一步动作。
- **验证**：unit tests

### Task 3.2 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前

- **优先级**：P1
- **依赖**：Task 3.1
- **验收标准**：
  1. 至少 3 个关键节点可挂 reviewer decision。
  2. status/recover/close-check 能读取决策状态。
- **验证**：定向 unit + close-check tests

---

## Batch 4：backend delegation / fallback

### Task 4.1 — 实现 backend capability declaration 与选择策略

- **优先级**：P1
- **依赖**：Task 1.2
- **输入**：[`src/ai_sdlc/backends/native.py`](../../src/ai_sdlc/backends/native.py) 与新增 routing/policy 层、[`tests/unit/test_backends.py`](../../tests/unit/test_backends.py)
- **验收标准**：
  1. Native / Plugin 选择理由可记录。
  2. capability 不覆盖时显式 fallback 或 BLOCK。
- **验证**：定向 unit tests

### Task 4.2 — 区分“可安全回退”与“必须阻断”的 backend 失败路径

- **优先级**：P1
- **依赖**：Task 4.1
- **验收标准**：
  1. plugin 失败时不会静默降级。
  2. 决策结果可被 verify / close-check surface 读取。
- **验证**：`uv run pytest tests/unit/test_backends.py -v`

---

## Batch 5：NFR / release gate

### Task 5.1 — 把 recoverability / portability / multi-IDE / stability 变成可测量 release gate

- **优先级**：P1
- **依赖**：Task 1.1
- **输入**：[`src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`src/ai_sdlc/cli/verify_cmd.py`](../../src/ai_sdlc/cli/verify_cmd.py)
- **验收标准**：
  1. release gate 至少输出 PASS / WARN / BLOCK。
  2. 每个 blocker 都有证据来源与原因。
- **验证**：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_verify_constraints.py -v`

### Task 5.2 — 003 traceability / docs / close-check 最终对账

- **优先级**：P1
- **依赖**：Task 5.1
- **验收标准**：
  1. `spec.md`、`plan.md`、`tasks.md` 对齐。
  2. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：全量 `pytest` + `ruff`
