# 002-p1-capabilities 任务执行归档

> 本文件遵循 [`templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/002-p1-capabilities/` 相关的实现任务，在本文件**末尾**追加新批次章节。
- 批次结束顺序：验证（pytest + ruff + 必要只读校验）→ 归档本文 → git commit。

## 2. 批次记录

### Batch 2026-03-29-001 | 002 Batch 2-5 runtime contract closure

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `2.1`、Task `2.2`、Task `3.1`、Task `4.2`、Task `5.1`
- **目标**：把 `002` 已有 spec/plan/tasks 中仍停留在“半合同”状态的 P1 能力补成正式真值，重点收口 change pause/resume、maintenance execution path、parallel coordination artifact、incident close postmortem gate 与 status surface。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、`src/ai_sdlc/models/*.py`、`src/ai_sdlc/studios/*.py`、`src/ai_sdlc/parallel/engine.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/cli/commands.py`
- **激活的规则**：TDD；fresh verification；artifact 真值优先于自由文本；status/close surface 必须消费正式产物。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **R1（P1 surface / close context 红灯）**
  - 命令：`uv run pytest tests/unit/test_gates.py::TestCloseGate::test_fail_when_postmortem_is_incomplete tests/unit/test_runner_confirm.py::TestConfirmMode::test_close_context_includes_incident_postmortem_and_refresh_entry tests/integration/test_cli_status.py::TestCliStatus::test_status_shows_p1_artifact_surfaces -q`
  - 结果：先红后绿；实现前分别暴露出 `CloseGate` 未消费 `postmortem_path`、runner close context 未回填 incident/refresh 证据、`status` surface 不显示 `resume-point / execution-path / parallel coordination`。
- **V1（002 targeted runtime / surface regression）**
  - 命令：`uv run pytest tests/unit/test_p1_artifacts.py tests/unit/test_p1_models.py tests/unit/test_studios.py tests/unit/test_parallel.py tests/unit/test_gates.py tests/unit/test_runner_confirm.py tests/flow/test_incident_flow.py tests/flow/test_parallel_flow.py tests/flow/test_knowledge_refresh_flow.py tests/integration/test_cli_status.py tests/integration/test_cli_run.py -q`
  - 结果：**190 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/models/__init__.py src/ai_sdlc/models/state.py src/ai_sdlc/models/work.py src/ai_sdlc/core/p1_artifacts.py src/ai_sdlc/knowledge/engine.py src/ai_sdlc/gates/pipeline_gates.py src/ai_sdlc/core/runner.py src/ai_sdlc/cli/commands.py src/ai_sdlc/parallel/engine.py src/ai_sdlc/studios/change_studio.py src/ai_sdlc/studios/maintenance_studio.py tests/unit/test_p1_artifacts.py tests/unit/test_p1_models.py tests/unit/test_parallel.py tests/unit/test_studios.py tests/unit/test_gates.py tests/unit/test_runner_confirm.py tests/integration/test_cli_status.py`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 2.3 任务记录

##### Task 2.1 | Change runtime pause / resume contract

- **改动范围**：`src/ai_sdlc/models/work.py`、`src/ai_sdlc/core/p1_artifacts.py`、`src/ai_sdlc/studios/change_studio.py`、`tests/unit/test_p1_models.py`、`tests/unit/test_p1_artifacts.py`、`tests/unit/test_studios.py`
- **改动内容**：
  - 新增结构化 `ResumePoint` 合同，并保留从旧字符串 `resume_point` 的向后兼容解析。
  - `ChangeStudio` 不再只写自由文本暂停点，而是持久化 `freeze-snapshot.yaml` / `resume-point.yaml`，并在存在活跃 work item 时把 `dev_executing` / `dev_verifying` 状态切到 `suspended`。
  - 抽出 `core/p1_artifacts.py` 统一承载 P1 artifact 的 YAML 真值写入与读取。
- **新增/调整的测试**：
  - 覆盖 resume point round-trip、legacy string 兼容、`ChangeStudio` 写盘与 work item 挂起。
- **执行的命令**：见 R1 / V1 / Lint / 治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。`change_request` 已具备正式 pause/resume artifact，而非仅靠自由文本提示。

##### Task 2.2 | Maintenance execution path formalization

- **改动范围**：`src/ai_sdlc/models/work.py`、`src/ai_sdlc/core/p1_artifacts.py`、`src/ai_sdlc/studios/maintenance_studio.py`、`tests/unit/test_p1_models.py`、`tests/unit/test_p1_artifacts.py`、`tests/unit/test_studios.py`
- **改动内容**：
  - 新增 `ExecutionPath` / `ExecutionPathStep` 模型，并把 `MaintenancePlan` 扩展为同时持有 task graph 与 execution path。
  - `MaintenanceStudio` 持久化 `execution-path.yaml`，同时在 `maintenance-brief.md` 中回显 execution path，保持文档层与对象层一致。
- **新增/调整的测试**：
  - 覆盖 execution path 模型、YAML round-trip，以及 studio 写盘后的读取一致性。
- **执行的命令**：见 V1 / Lint。
- **测试结果**：通过。
- **是否符合任务目标**：符合。lightweight maintenance path 已具备正式执行顺序真值。

##### Task 3.1 | Parallel coordination artifact

- **改动范围**：`src/ai_sdlc/models/state.py`、`src/ai_sdlc/core/p1_artifacts.py`、`src/ai_sdlc/parallel/engine.py`、`tests/unit/test_p1_artifacts.py`、`tests/unit/test_parallel.py`
- **改动内容**：
  - 新增 `ParallelCoordinationArtifact` 模型，把 group-task mapping、worker assignment、overlap result 与 merge simulation 收敛到单一 artifact。
  - `parallel.engine` 新增 `build_coordination_artifact()`，可将 assignment freeze / merge verify 真值落盘到 `parallel-coordination.yaml`。
- **新增/调整的测试**：
  - 覆盖 coordination artifact 的内存构建与 YAML round-trip。
- **执行的命令**：见 V1 / Lint。
- **测试结果**：通过。
- **是否符合任务目标**：符合。parallel 已从纯 planning helper 前进到可持久化的正式 coordination artifact。

##### Task 4.2 | Incident close consumes postmortem gate

- **改动范围**：`src/ai_sdlc/gates/pipeline_gates.py`、`src/ai_sdlc/knowledge/engine.py`、`src/ai_sdlc/core/runner.py`、`tests/unit/test_gates.py`、`tests/unit/test_runner_confirm.py`
- **改动内容**：
  - `CloseGate` 在 close context 提供 `postmortem_path` 时，显式串联 `PostmortemGate`，不再把 incident close 退化为普通 done gate。
  - runner close context 现在会按 active work item 识别 incident 场景，并自动回填 `.ai-sdlc/work-items/<WI>/postmortem.md` 路径。
  - 新增 `load_refresh_log()`，使 runner close context 可读取当前 work item 的 refresh evidence，并把最新 refresh level/completed 状态注入 Done Gate context。
- **新增/调整的测试**：
  - 覆盖 incomplete postmortem 阻断 close，以及 runner close context 注入 incident/refresh 证据。
- **执行的命令**：见 R1 / V1 / Lint / 治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。incident close 已真正经过 postmortem gate，而不是只在模型里声明。

##### Task 5.1 | Status surface consumes P1 artifacts

- **改动范围**：`src/ai_sdlc/cli/commands.py`、`tests/integration/test_cli_status.py`
- **改动内容**：
  - `ai-sdlc status` 在 active work item 存在时新增 `Resume Point`、`Execution Path`、`Parallel Coordination`、`Parallel Merge Order` surface，直接读取正式 artifact，不要求操作者回忆上下文。
- **新增/调整的测试**：
  - integration 覆盖 `status` 展示三类 P1 artifact surface。
- **执行的命令**：见 R1 / V1 / Lint。
- **测试结果**：通过。
- **是否符合任务目标**：符合。新增 P1 artifact 已从“可落盘”提升到“可被 operator 读取”。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批没有重写 `002` 的整体设计，而是按现有 `spec/plan/tasks` 把仍未产品化的 P1 合同收敛回正式 artifact 与 close/status surface。
- **代码质量**：`core/p1_artifacts.py` 将 resume-point / execution-path / parallel coordination 的真值写盘集中到一处，减少 studio/CLI 各自发明路径。
- **测试质量**：先用三条红灯明确暴露 surface/close 的真实断点，再用 unit + flow + integration 的组合回归固定模型、写盘、runner context 与 CLI surface。
- **结论**：无新增阻塞项；`002` 当前剩余的 close-check 缺口仅为 execution log / git closure 收口，而不是代码合同缺失。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（本批实现覆盖的 Task `2.1` / `2.2` / `3.1` / `4.2` / `5.1` 与当前代码真值一致）。
- `plan.md` 同步状态：`已对账`（实现顺序与现有 Phase 1-4 目标一致，未发现新的结构性漂移）。
- `spec.md` 同步状态：`已对账`（resume-point、execution-path、parallel coordination、postmortem gate 与 surface consumption 均已有正式代码与测试证据）。

#### 2.6 自动决策记录（如有）

- AD-001：本批优先补“artifact 真值 + surface 消费”，暂不引入新的 orchestration DSL 或额外 mixed spec → 理由：`002` 当前缺口是已有合同未完全产品化，不是需求边界不清。

#### 2.7 批次结论

- `002` 当前已完成 P1 runtime contract closure 的核心代码收口；close-check 剩余动作只剩 execution log 与 git closure 对账，不再存在新的代码 blocker。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`7f3f99f`（`feat: close 002 p1 contract gaps`）
- **改动范围**：`src/ai_sdlc/models/__init__.py`, `src/ai_sdlc/models/state.py`, `src/ai_sdlc/models/work.py`, `src/ai_sdlc/core/p1_artifacts.py`, `src/ai_sdlc/knowledge/engine.py`, `src/ai_sdlc/gates/pipeline_gates.py`, `src/ai_sdlc/core/runner.py`, `src/ai_sdlc/cli/commands.py`, `src/ai_sdlc/parallel/engine.py`, `src/ai_sdlc/studios/change_studio.py`, `src/ai_sdlc/studios/maintenance_studio.py`, `tests/unit/test_p1_artifacts.py`, `tests/unit/test_p1_models.py`, `tests/unit/test_parallel.py`, `tests/unit/test_studios.py`, `tests/unit/test_gates.py`, `tests/unit/test_runner_confirm.py`, `tests/integration/test_cli_status.py`, `specs/002-p1-capabilities/task-execution-log.md`
- **是否继续下一批**：阻断，待本批提交哈希回填并通过 `workitem close-check` 后再决定是否继续其他 work item。

### Batch 2026-03-30-001 | 002 final close-truth verification refresh

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `5.2`
- **目标**：以当前主线仓库状态重新复核 `002` 的 P1 runtime contracts、治理门禁与 `close-check` 真值，并把最终 PASS 结果补录回正式台账。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)
- **激活的规则**：fresh verification；docs-only close-truth refresh；task/spec/plan 单一真值。
- **验证画像**：`docs-only`

#### 2.2 统一验证命令

- **V1（002 targeted runtime regression）**
  - 命令：`uv run pytest tests/unit/test_p1_artifacts.py tests/unit/test_p1_models.py tests/unit/test_studios.py tests/unit/test_parallel.py tests/unit/test_gates.py tests/unit/test_runner_confirm.py tests/flow/test_incident_flow.py tests/flow/test_parallel_flow.py tests/flow/test_knowledge_refresh_flow.py tests/integration/test_cli_status.py tests/integration/test_cli_run.py -q`
  - 结果：**195 passed**。
- **V2（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**verify constraints: no BLOCKERs.**
- **V3（002 全文档 close-check）**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/002-p1-capabilities --all-docs`
  - 结果：**PASS**；tasks completion、review gate、verification profile、git closure、completion truth、docs consistency、done gate 均通过。

#### 2.3 任务记录

##### Task 5.2 | final close-truth refresh

- **改动范围**：`specs/002-p1-capabilities/tasks.md`, `specs/002-p1-capabilities/task-execution-log.md`
- **改动内容**：
  - 重新执行 `002` 的 targeted runtime regression、`verify constraints` 与 `close-check --all-docs`，确认此前“只差 git_closure / execution-log 对账”的尾项已在当前主线仓库状态下自然消失。
  - 将 Task `5.2` 的完成说明与本批 fresh verification 结果回填到 `tasks.md` / `task-execution-log.md`，避免 `002` 仍停留在“待再跑一次 close-check”的旧口径。
  - 以提交 `c9ceeea` 对应的当前仓库代码状态作为本轮 close-truth baseline 复核对象；本批仅补录台账，不改动 P1 运行时代码。
- **新增/调整的测试**：无新增运行时代码测试；本批使用 fresh 定向回归与只读门禁复核现有合同。
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：通过。
- **是否符合任务目标**：符合。`002` 现已具备 fresh runtime evidence 与 formal close-check PASS，不再残留未收口的 close truth 尾项。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批没有新增或改写 `002` 的运行时行为，只把最终 close-truth 刷新到当前仓库事实，确保 `spec.md` / `plan.md` / `tasks.md` 与 formal gate 结论一致。
- **代码质量**：无产品代码变更；保持 `002` 的 runtime contract 真值仍由既有 models / studios / runner / gates 承担。
- **测试质量**：使用 fresh 定向 pytest、`verify constraints` 与 `close-check --all-docs` 交叉确认“代码对齐”和“台账对齐”同时成立。
- **结论**：无新的阻塞项；`002` 已具备正式 close 条件。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `5.2` 已补 final close-truth refresh 完成说明）。
- `plan.md` 同步状态：`已对账`（Phase 0~4 的 artifact/runtime/surface 目标与当前仓库状态一致）。
- `spec.md` 同步状态：`已对账`（P1 contracts 仍由 fresh targeted runtime regression 覆盖）。

#### 2.6 自动决策记录（如有）

- AD-002：本轮仅做 docs-only close-truth refresh，不重开 `002` mixed remediation 批次 → 理由：fresh `close-check` 已证明当前缺口不是代码合同缺失，而是旧台账还停留在“待再验证一次”的中间态。

#### 2.7 批次结论

- `002` 当前已满足 targeted runtime regression、`verify constraints` 与 `close-check --all-docs` 三条最终收口验证。
- `002` 不再存在“只差 git_closure / execution-log 对账”的 formal close blocker，可作为已收口 work item 参与后续 `004` 盘点与 Program 级对账。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`c9ceeea`（`fix: harden repo write lock cleanup`，本批 close-truth refresh 复核基线）
- **改动范围**：`specs/002-p1-capabilities/tasks.md`, `specs/002-p1-capabilities/task-execution-log.md`
- **是否继续下一批**：否，`002` 已完成 formal close-truth refresh。
