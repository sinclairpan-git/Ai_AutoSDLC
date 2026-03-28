# 003-cross-cutting-authoring-and-extension-contracts 任务执行归档

> 本文件遵循 [`templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/003-cross-cutting-authoring-and-extension-contracts/` 相关的实现任务，在本文件**末尾**追加新批次章节。
- 批次结束顺序：验证（pytest + ruff + 必要只读校验）→ 归档本文 → git commit。

## 2. 批次记录

### Batch 2026-03-28-001 | 003 Batch 6 Task 6.1-6.3（Telemetry governance backlog remediation）

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `6.1`、Task `6.2`、Task `6.3`；[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-27-011` / `FD-2026-03-27-012`
- **目标**：完成 `003` 第一波 backlog 的 source closure 与 required CCP canonical traceability 收口，并把缺陷状态、任务台账和 execution evidence 统一到同一真值。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、`src/ai_sdlc/telemetry/*.py`
- **激活的规则**：TDD；fresh verification；task/backlog/execution-log 单一真值。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **R1（CCP canonical 伪覆盖红灯）**
  - 命令：`uv run pytest tests/unit/test_telemetry_governance.py -q`
  - 结果：先红后绿；新增“错误 scope/writer 仍被算作 gate/audit CCP”“缺最小 evidence closure 仍被算作 covered”的回归在实现前失败，证明 defect 可复现。
- **V1（telemetry governance / runner / publisher 定向回归）**
  - 命令：`uv run pytest tests/unit/test_telemetry_governance.py tests/unit/test_runner_confirm.py tests/unit/test_telemetry_publisher.py -q`
  - 结果：**41 passed**。
- **V2（registry/contracts + telemetry 回归）**
  - 命令：`uv run pytest tests/unit/test_telemetry_contracts.py tests/unit/test_telemetry_governance.py tests/unit/test_runner_confirm.py tests/unit/test_telemetry_publisher.py -q`
  - 结果：**73 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/telemetry/control_points.py src/ai_sdlc/telemetry/runtime.py src/ai_sdlc/telemetry/governance_publisher.py src/ai_sdlc/telemetry/evaluators.py tests/unit/test_telemetry_governance.py tests/unit/test_runner_confirm.py tests/unit/test_telemetry_publisher.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 2.3 任务记录

##### Task 6.1 | source closure 父链兼容对账收口（FD-2026-03-27-011）

- **改动范围**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 复核当前 `source_chain_compatible()` / publisher 语义已经收敛到 session/run 前缀父链兼容，不再把 run 级 artifact 引用同 run step 来源误判为跨链。
  - 用 Batch 6 的统一 execution evidence 把 `FD-2026-03-27-011`、`tasks.md` 与 execution log 对齐到同一收口口径。
- **新增/调整的测试**：
  - 复用 `tests/unit/test_telemetry_publisher.py` 既有 run->step 正向与跨链负向回归。
- **执行的命令**：见 V1 / V2 / 治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。合法后代链放行与跨链拒绝都已由既有实现和回归证据覆盖。

##### Task 6.2 | required CCP canonical raw traceability（FD-2026-03-27-012）

- **改动范围**：`src/ai_sdlc/telemetry/control_points.py`、`src/ai_sdlc/telemetry/runtime.py`、`src/ai_sdlc/telemetry/governance_publisher.py`、`src/ai_sdlc/telemetry/evaluators.py`、`tests/unit/test_telemetry_governance.py`、`tests/unit/test_runner_confirm.py`、`tests/unit/test_telemetry_publisher.py`
- **改动内容**：
  - 新增 `telemetry/control_points.py`，把 `gate_hit`、`gate_blocked`、`audit_report_generated` 的 canonical event 形状抽成 shared helper，供 runtime / publisher / evaluator 共用。
  - `RuntimeTelemetry.record_gate_control_point()` 与 `GovernancePublisher` 改为复用 shared helper 写 gate / audit 事件，固定 control-point scope、writer 与 evidence 口径。
  - `calculate_ccp_coverage_gaps()` 改为同时校验 canonical raw trace 事件形状和 `minimum_evidence_closure`，不再接受错误 scope/writer 或缺最小证据闭包的伪覆盖。
  - publisher 只对 run-scope audit report 发出 `audit_report_generated` 控制点，避免写出后续无法被 canonical evaluator 证明的 trace。
- **新增/调整的测试**：
  - 新增 CCP canonical shape / minimum closure 负例，证明错误 scope/writer 与缺 closure 的 evidence 不再满足 required CCP。
  - runner / publisher 测试补 canonical 字段断言与 step-scope audit report 负例，固定 writer 侧的真实 event/evidence 形状。
- **执行的命令**：见 R1 / V1 / V2 / Lint / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。required CCP 的 persisted trace 真值、registry 合同与 evaluator 判定已收敛到同一口径。

##### Task 6.3 | Batch 6 backlog/document 收口

- **改动范围**：[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **改动内容**：
  - 创建 `003` 的正式 `task-execution-log.md`，补齐 Batch 6 的验证证据、代码审查与台账同步状态。
  - 将 `FD-2026-03-27-011` / `FD-2026-03-27-012` 在 backlog 与 `tasks.md` 中统一调整为已收口口径。
  - 更新 backlog 顶部“下一波待修优先级”，移除 `003` 线已关闭项，只保留真实未收口的 `004` 项。
- **新增/调整的测试**：无新增运行时代码测试；收口依赖 V1 / V2 / 只读校验结果。
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。Batch 6 的缺陷、任务与 execution evidence 已统一到同一事实。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批把 `003` 中 source closure 与 required CCP 的 contract 缺口收束回正式 work item，不再依赖临时 telemetry governance 文档维持第二份真值。
- **代码质量**：canonical control-point helper 把 gate/audit 的 writer 与 evaluator 规则集中到一处，减少“registry 有名字、writer/evaluator 各自猜语义”的分叉面。
- **测试质量**：先用红灯证明伪覆盖真实存在，再以 governance / runner / publisher / contracts 的组合回归固定 canonical event 形状与 closure 口径。
- **结论**：无新的阻塞项；允许关闭 `FD-2026-03-27-011` / `FD-2026-03-27-012` 并结束 `003` Batch 6。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `6.1` / `6.2` / `6.3` 已补完成说明并统一 Batch 6 收口口径）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-27-011` / `FD-2026-03-27-012` 已关闭，顶部待修清单已移除 `003` 线）。
- `related_plan`（如存在）同步状态：`已对账`（`003` 的 plan/spec/tasks 未发现新的 contract 漂移）。

#### 2.6 自动决策记录（如有）

- AD-001：不再单独为 `FD-2026-03-27-012` 追加 mixed spec，而是把 gate/audit canonical raw traceability 直接挂回 `003` Batch 6 → 理由：当前缺口属于 `003` telemetry governance contracts 的正式 owner 范围，继续另起临时文档只会制造第二份真值。

#### 2.7 批次结论

- `003` Batch 6 已完成 source closure 与 required CCP canonical traceability 的第一波 backlog 收口；`FD-2026-03-27-011` / `FD-2026-03-27-012` 不再属于待修项，下一波只剩 `004` 的 `FD-2026-03-27-013`。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`8fb79b9`（`feat: canonicalize telemetry control point traces`）
- **是否继续下一批**：阻断，待本批代码与归档一并提交后再进入 `004`。
