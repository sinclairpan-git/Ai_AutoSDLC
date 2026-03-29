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
Batch 6: backlog remediation          (source closure + CCP traceability)
```

## 实施进展复核（2026-03-29）

- `2026-03-29` 已补齐 `003` 的 Batch 1~5 代码、测试与 release-gate evidence，close-out 真值不再仅依赖 Batch 6 的 telemetry backlog 记录。
- Batch `1~3`（Task `1.1`、`2.1`、`2.2`、`3.1`、`3.2`）已由提交 `5ada806` 收口：完成 `draft_prd/final_prd`、reviewer checkpoint / decision artifact、idea-string PRD authoring 入口与 status-readable reviewer surface。
- Batch `4`（Task `1.2`、`4.1`、`4.2`）已由提交 `fab9077`、`69c37b5`、`476dc9c` 收口：完成 backend capability declaration、selection/fallback/block 决策合同，以及 fake fallback / inconsistent decision-surface 修复。
- Batch `5`（Task `5.1`、`5.2`）已由提交 `ae695e7` 与本批最终 traceability close-out 收口：完成 release gate evidence parser、`verify constraints` / `close-check` surface、`release-gate-evidence.md` 与 003 execution evidence 全量回填。
- `FD-2026-03-29-001 ~ 003` 已在本轮框架修复中关闭；后续不应再把局部 batch 绿灯外推成整个 work item 收口。

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

---

## Batch 6：backlog remediation（Telemetry governance contracts）

> **说明**：本批承接原临时 telemetry governance 设计里尚未收口、但必须挂回正式 work item 的 contract 缺口：`FD-2026-03-27-011`、`FD-2026-03-27-012`。不再另开 mixed spec，真值以 backlog 与本文件 AC 为准。

### Task 6.1 — source closure 父链从“step_id 全等”收敛到“合法后代链”（FD-2026-03-27-011）

- **优先级**：P0
- **依赖**：Task 5.2
- **输入**：[`src/ai_sdlc/telemetry/governance_publisher.py`](../../src/ai_sdlc/telemetry/governance_publisher.py)、[`src/ai_sdlc/telemetry/writer.py`](../../src/ai_sdlc/telemetry/writer.py)、[`tests/unit/test_telemetry_publisher.py`](../../tests/unit/test_telemetry_publisher.py)、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **验收标准**：
  1. run 级 artifact 可以合法引用同一 `workflow_run_id` 下 step 级 evidence / evaluation，不再因 `step_id` 不相等被误判为跨链。
  2. 跨 session / 跨 run 的 source 仍然被拒绝，不能因放宽父链兼容而放松真实闭包约束。
  3. writer / publisher 复用同一套 closure helper，避免“一个接受、一个拒绝”的双轨语义。
- **验证**：`uv run pytest tests/unit/test_telemetry_publisher.py -v`

> **Task 6.1 完成（2026-03-28）**：当前 `writer` / `publisher` 已收敛到 session/run 前缀父链兼容，run 级 artifact 可合法引用同 run 下 step 级 source，跨链引用仍被拒绝。该行为已由 `tests/unit/test_telemetry_publisher.py` 与 Batch 6 综合 telemetry 回归复核，`FD-2026-03-27-011` 已关闭。

### Task 6.2 — required CCP 在 raw trace 中具备 canonical 可证明形状（FD-2026-03-27-012）

- **优先级**：P0
- **依赖**：Task 6.1
- **输入**：[`src/ai_sdlc/telemetry/registry.py`](../../src/ai_sdlc/telemetry/registry.py)、[`src/ai_sdlc/telemetry/contracts.py`](../../src/ai_sdlc/telemetry/contracts.py)、[`src/ai_sdlc/telemetry/runtime.py`](../../src/ai_sdlc/telemetry/runtime.py)、[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py)、[`src/ai_sdlc/telemetry/governance_publisher.py`](../../src/ai_sdlc/telemetry/governance_publisher.py)、[`src/ai_sdlc/telemetry/evaluators.py`](../../src/ai_sdlc/telemetry/evaluators.py)
- **验收标准**：
  1. `gate_hit`、`gate_blocked`、`audit_report_generated` 都有稳定的 persisted trace 事件形状与最小证据引用，不再只存在于 registry 声明中。
  2. coverage evaluator 只基于 canonical raw trace 判定 required CCP 是否已证明，不再接受“registry 有名字但 trace 无真值”的伪覆盖。
  3. gate / audit 写入路径、registry 合同与 evaluator 测试长期共用同一套控制点命名和证据规则。
- **验证**：定向 telemetry governance / evaluator tests

> **Task 6.2 完成（2026-03-28）**：新增 [`../../src/ai_sdlc/telemetry/control_points.py`](../../src/ai_sdlc/telemetry/control_points.py) 作为 gate/audit canonical control-point helper；[`../../src/ai_sdlc/telemetry/runtime.py`](../../src/ai_sdlc/telemetry/runtime.py) 与 [`../../src/ai_sdlc/telemetry/governance_publisher.py`](../../src/ai_sdlc/telemetry/governance_publisher.py) 复用同一套 event 形状；[`../../src/ai_sdlc/telemetry/evaluators.py`](../../src/ai_sdlc/telemetry/evaluators.py) 改为同时校验 canonical raw trace 与 `minimum_evidence_closure`。定向回归 **41 passed**、扩大 telemetry/contracts 回归 **73 passed**，`FD-2026-03-27-012` 已关闭。

### Task 6.3 — 003 第一波 backlog 对账收口

- **优先级**：P0
- **依赖**：Task 6.1, Task 6.2
- **验收标准**：
  1. `FD-2026-03-27-011` / `FD-2026-03-27-012` 在 backlog、`tasks.md` 与后续 execution evidence 中保持同一状态口径。
  2. source closure 与 CCP traceability 的回归测试能同时证明“合法闭包放行”和“无证据控制点拒绝”。
  3. 本批收口后，不再需要回到临时 telemetry governance 文档补写第二份任务真值。
- **验证**：定向 pytest + `verify constraints`

> **Task 6.3 完成（2026-03-28）**：[`task-execution-log.md`](task-execution-log.md) 已创建并补齐 Batch 6 的真实执行证据；[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 与本文件现已对齐关闭 `FD-2026-03-27-011` / `FD-2026-03-27-012`；第一波 backlog 的 `003` 线正式收口，下一步切到 `004` 的 `FD-2026-03-27-013`。
