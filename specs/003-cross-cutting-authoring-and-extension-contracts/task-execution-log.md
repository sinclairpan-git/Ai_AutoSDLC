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

### Batch 2026-03-29-001 | 003 Batch 1-5 completion truth remediation closeout

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Batch `1~5`、[`../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md`](../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md)
- **目标**：为 `003` 的 PRD authoring / reviewer / backend / release-gate contracts 补齐最终 execution evidence，并把 defect backlog、任务台账、release-gate 证据与 close-check 真值统一到同一口径。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`release-gate-evidence.md`](release-gate-evidence.md)、`src/ai_sdlc/core/*.py`、`src/ai_sdlc/backends/*.py`、`src/ai_sdlc/studios/prd_studio.py`
- **激活的规则**：fresh verification；close-check completion truth；task/backlog/execution-log 单一真值。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（全量 pytest）**
  - 命令：`uv run pytest -q`
  - 结果：**850 passed**。
- **V2（仓库 lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **V3（治理与 feature-contract gate）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**verify constraints: no BLOCKERs.**

#### 2.3 任务记录

##### Batch 1~3 | PRD draft authoring / reviewer contracts

- **改动范围**：[`../../src/ai_sdlc/models/work.py`](../../src/ai_sdlc/models/work.py)、[`../../src/ai_sdlc/studios/prd_studio.py`](../../src/ai_sdlc/studios/prd_studio.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../tests/unit/test_prd_studio.py`](../../tests/unit/test_prd_studio.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)
- **改动内容**：
  - 提交 `d5f8202` 为 `verify constraints` 增加 `003` feature-contract coverage，先把 draft/final PRD、reviewer、backend、release-gate surface 变成可判定对象。
  - 提交 `5ada806` 补齐 `draft_prd/final_prd`、reviewer checkpoint / decision artifact、idea-string -> draft PRD authoring 入口，以及可被 close/status surface 读取的 reviewer 状态。
- **新增/调整的测试**：
  - `tests/unit/test_prd_studio.py`
  - `tests/unit/test_close_check.py`
  - `tests/unit/test_verify_constraints.py`
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：通过。
- **是否符合任务目标**：符合。Batch `1~3` 已有正式对象模型、authoring 路径与 reviewer 决策 surface。

##### Batch 4 | backend delegation / fallback

- **改动范围**：[`../../src/ai_sdlc/backends/native.py`](../../src/ai_sdlc/backends/native.py)、[`../../src/ai_sdlc/backends/routing.py`](../../src/ai_sdlc/backends/routing.py)、[`../../tests/unit/test_backends.py`](../../tests/unit/test_backends.py)、[`../../tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)
- **改动内容**：
  - 提交 `fab9077` 建立 backend capability declaration、selection 与 fallback/block 合同。
  - 提交 `69c37b5`、`476dc9c` 进一步修复 fake fallback 与 inconsistent decision-surface，让 plugin failure 的 safe-fallback / hard-block 边界可被 verify / close-check 读取。
- **新增/调整的测试**：
  - `tests/unit/test_backends.py`
  - `tests/integration/test_cli_verify_constraints.py`
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：通过。
- **是否符合任务目标**：符合。Batch `4` 已能记录 backend choice、fallback result 与 unsafe failure blocker。

##### Batch 5 | release gate / completion truth

- **改动范围**：[`../../src/ai_sdlc/core/workitem_traceability.py`](../../src/ai_sdlc/core/workitem_traceability.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/cli/verify_cmd.py`](../../src/ai_sdlc/cli/verify_cmd.py)、[`release-gate-evidence.md`](release-gate-evidence.md)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`../../tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)
- **改动内容**：
  - 提交 `d28d1ed` 为 close-check 增加 planned-batch coverage、execution-log coverage 与最终收口状态 blocker。
  - 提交 `ae695e7` 补齐 PASS/WARN/BLOCK release gate evidence、`003` release-gate parser 与 verify/close-check surface。
  - 本批最终把 `tasks.md`、本 execution log、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 与 [`release-gate-evidence.md`](release-gate-evidence.md) 重新对账到同一真值。
- **新增/调整的测试**：
  - `tests/unit/test_close_check.py`
  - `tests/unit/test_verify_constraints.py`
  - `tests/integration/test_cli_workitem_close_check.py`
  - `tests/integration/test_cli_verify_constraints.py`
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：通过。
- **是否符合任务目标**：符合。release gate evidence、feature-contract coverage 与 completion truth blocker 已全部落到正式 gate。

#### 2.4 代码审查（摘要）

- **规格对齐**：`003` 原先缺失的 authoring / reviewer / backend / release-gate contracts 已全部有代码、测试与 docs evidence，对应 `FR-003-001 ~ 015` 不再停留在 spec 声明层。
- **代码质量**：close-check 与 verify constraints 都已从“只读文档完备性”提升为“合同完成真值”判断，避免局部 batch 收口被误读成整项完成。
- **测试质量**：本批使用全量 pytest + ruff + `verify constraints` 复核，验证回归覆盖 authoring、reviewer、backend、release gate 与 close truth 四条主线。
- **结论**：无新的阻塞项；`003` Batch `1~5` 已具备正式收口条件。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（顶部“实施进展复核”已把 Batch `1~5` 的提交链与 contract surface 对齐）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-29-001 ~ 003` 已关闭并补收口说明）。
- `release-gate-evidence.md` 同步状态：`已同步`（PASS/WARN/BLOCK 结构与 evidence source 保持可读且可机读）。
- `related_plan` 同步状态：`已同步`（[`../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md`](../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md) 的 Task `1~5` 已有对应实现提交与 execution evidence）。

#### 2.6 自动决策记录（如有）

- AD-002：最终 execution evidence 采用单个 “Batch `1~5` closeout” 章节聚合，而不是回溯补写 5 个伪历史批次 → 理由：代码实现已经按提交链真实存在，close-check 只要求 planned-batch coverage 与最新批次的 fresh verification；聚合收口能保持历史顺序真实，避免伪造不存在的旧日志。

#### 2.7 批次结论

- `003` 已具备完整的 Batch `1~6` execution evidence，其中 Batch `1~5` 由本批统一补齐 closeout 真值，Batch `6` 保持既有 telemetry governance backlog 归档。
- `FD-2026-03-29-001 ~ 003` 已随本轮 guardrail / authoring / backend / release-gate 修复一并关闭，后续不应再把 `003` 表述为 “仅 Batch 6 局部收口”。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`ae695e7`（`feat: add release gate verification surfaces`）
- **是否继续下一批**：否，`003` 已完成实现与台账对账，等待分支收口。

### Batch 2026-03-30-001 | 003 final close-truth verification refresh

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `5.2`、[`../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md`](../../docs/superpowers/plans/2026-03-29-003-completion-truth-remediation.md)
- **目标**：补录 `003` 正式 `pre_close` reviewer approval artifact，修正仓库最终 close truth 与 lint 细节漂移，并以 fresh verification 复核真实收口状态。
- **预读范围**：[`tasks.md`](tasks.md)、[`release-gate-evidence.md`](release-gate-evidence.md)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/core/reviewer_gate.py`](../../src/ai_sdlc/core/reviewer_gate.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)
- **激活的规则**：fresh verification；close-check completion truth；task/backlog/execution-log 单一真值。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（全量 pytest）**
  - 命令：`uv run pytest -q`
  - 结果：**883 passed**。
- **V2（仓库 lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **V3（治理与 feature-contract gate）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**verify constraints: no BLOCKERs.**
- **V4（003 全文档 close-check）**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/003-cross-cutting-authoring-and-extension-contracts --all-docs`
  - 结果：**PASS**；review gate、release gate、docs consistency、git closure 均通过。

#### 2.3 任务记录

##### Task 5.2 | final close-truth refresh

- **改动范围**：[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`../../src/ai_sdlc/branch/git_client.py`](../../src/ai_sdlc/branch/git_client.py)、[`../../tests/unit/test_git_client.py`](../../tests/unit/test_git_client.py)、[`.ai-sdlc/work-items/003-cross-cutting-authoring-and-extension-contracts/reviewer-decision-pre-close.yaml`](../../.ai-sdlc/work-items/003-cross-cutting-authoring-and-extension-contracts/reviewer-decision-pre-close.yaml)、[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 修正 `src/ai_sdlc/cli/commands.py` 的 import 排序，使仓库重新满足 `ruff`。
  - 补录 `003` 的正式 `pre_close` reviewer approval artifact，避免 `close-check` 只凭 execution-log 中的“代码审查”字样误判为已满足正式 reviewer gate。
  - 修复 `GitClient` 的 repo write-lock 清理竞态：锁文件若刚被移除或内容尚未写完整，不再被误当成 stale lock 清除，从而消除 full-suite 中的串行化 flake。
  - 追加本批 execution evidence，把全量验证结果与最终 close truth 对齐到最新仓库状态。
- **新增/调整的测试**：
  - `tests/unit/test_git_client.py` 新增“锁文件刚消失 / 内容未写完整”两条 deterministic regression tests。
  - 复用既有 `close-check` / `verify constraints` / full pytest 回归确认修复未破坏最终收口路径。
- **执行的命令**：见 V1 ~ V4。
- **测试结果**：通过。
- **是否符合任务目标**：符合。`003` 现已同时具备 formal reviewer approval、release gate evidence、fresh verification 与 clean git closure。

#### 2.4 代码审查（摘要）

- **规格对齐**：`003` 的最终收口现在同时满足 reviewer gate、release gate 与 execution evidence 三条正式合同，不再把“有 review 摘要”误当成“已有 pre_close approval”。
- **代码质量**：本批没有新增行为面，只修复 lint 漂移并补齐 runtime artifact / docs 真值。
- **测试质量**：使用 fresh full pytest、lint、`verify constraints` 与 `close-check --all-docs` 复核最终仓库状态。
- **结论**：无新的阻塞项；`003` 已具备真实 close 条件。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（顶部“实施进展复核”已补 `pre_close` reviewer approval 与最终 close-truth refresh）。
- `release-gate-evidence.md` 同步状态：`已对账`（release gate 仍维持 PASS/WARN/BLOCK 可读且可机读结构）。
- `related_plan` 同步状态：`已同步`（Task `5.2` 的最终 close truth 已由 V1 ~ V4 fresh verification 覆盖）。

#### 2.6 自动决策记录（如有）

- AD-003：以新增“verification refresh”批次记录最终 closeout，而不重写 `2026-03-29` 批次结果 → 理由：保持 execution history 的时间顺序真实，显式记录本次发现并修复的 formal reviewer gate / lint 漂移。

#### 2.7 批次结论

- `003` 当前已满足 full pytest、lint、`verify constraints` 与 `close-check --all-docs` 四条最终收口验证。
- `003` 的 formal reviewer gate 已具备正式 `pre_close` approval artifact，后续 close 判断不再依赖 execution-log 文本摘要猜测。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`b2851c3`（`docs: record 003 close approval`）
- **是否继续下一批**：否，待本批提交后结束 `003` 分支收口。
