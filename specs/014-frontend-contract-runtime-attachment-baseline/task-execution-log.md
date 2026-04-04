# 任务执行记录：Frontend Contract Runtime Attachment Baseline

## 元信息

- work item：`014-frontend-contract-runtime-attachment-baseline`
- 执行范围：`specs/014-frontend-contract-runtime-attachment-baseline/`
- 执行基线：`009` 母规格 + `011` contract baseline + `012` verify integration baseline + `013` observation provider baseline
- 记录方式：append-only

## 批次记录

### Batch 2026-04-03-001 | 014 Runtime attachment formal baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`、`T12`、`T13`、`T21`、`T22`、`T23`、`T31`、`T32`、`T33`
- **目标**：把 frontend contract runtime attachment / orchestration baseline 从 `013` 的后续建议动作正式拆成独立 child work item，冻结 runtime attachment truth、scope/locality、failure honesty 与 implementation handoff。
- **预读范围**：[`specs/009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`specs/009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`specs/011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`specs/011-frontend-contract-authoring-baseline/plan.md`](../011-frontend-contract-authoring-baseline/plan.md)、[`specs/012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`specs/012-frontend-contract-verify-integration/plan.md`](../012-frontend-contract-verify-integration/plan.md)、[`specs/013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`specs/013-frontend-contract-observation-provider-baseline/plan.md`](../013-frontend-contract-observation-provider-baseline/plan.md)、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/cli/run_cmd.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/runner.py`
- **激活的规则**：single canonical formal truth；docs-only execute；child work item first；verification before completion
- **验证画像**：`docs-only`

#### 2.2 统一验证命令

- **V1（Tasks parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/014-frontend-contract-runtime-attachment-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 9, 'total_batches': 3, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33']]}`
- **V2（Markdown diff hygiene）**
  - 命令：`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline`
  - 结果：无输出。
- **V3（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 / T13 | 冻结 runtime attachment truth、entrypoint separation 与 non-goals

- **改动范围**：`spec.md`、`plan.md`
- **改动内容**：
  - 明确 `014` 是 `013` 下游的 runtime attachment child work item，而不是继续在 `013` 内扩张 orchestration scope。
  - 锁定 operator 显式 export 与 runtime attachment 的分层关系，并将 runner/program 作为独立下游责任面。
  - 明确 verify/gate、registry、auto-refresh、auto-fix 与 remediation 仍留在下游 work item。
- **新增/调整的测试**：无新增代码测试；以 formal docs 对账为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T21 / T22 / T23 | 冻结 attachment contract、failure honesty 与 ownership handoff

- **改动范围**：`spec.md`、`plan.md`、`tasks.md`
- **改动内容**：
  - 冻结 active `spec_dir`、artifact locality、attachment trigger 与 cross-spec safety 默认值。
  - 明确 scope 不明、artifact 缺失、provider 失败与 freshness 不可判断时的诚实暴露语义。
  - 锁定 explicit export、runner wiring 与 program orchestration 的 ownership 顺序。
- **新增/调整的测试**：无新增代码测试；以 contract review 为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T31 / T32 / T33 | 冻结 implementation handoff 与 baseline 校验

- **改动范围**：`plan.md`、`tasks.md`、`task-execution-log.md`
- **改动内容**：
  - 给出后续 `core / cli / runner / tests` 的推荐文件面与 ownership 边界。
  - 冻结 explicit export handoff、runner scope resolution、missing/stale artifact honesty 与 program non-goal 的最小测试矩阵。
  - 记录本批 docs-only verification 与 close-out 归档字段。
- **新增/调整的测试**：无新增代码测试；以 tasks parser、`git diff --check` 与 `verify constraints` 为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只冻结 `014` formal baseline，没有越界到 runtime wiring、verify/gate 重写、registry 或 remediation。
- **代码质量**：无代码改动；formal docs 与现有 `011` / `012` / `013` 真值保持分层一致。
- **测试质量**：docs-only fresh 验证覆盖 tasks parser、diff hygiene 与 `verify constraints`。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`已同步`
- 关联 branch/worktree disposition 计划：`retained（沿用当前 009/011/012/013 工作分支）`
- 说明：`014` 当前作为 runtime attachment 的 docs-only baseline 保留在关联分支上；下一步建议从 runtime attachment helper / runner wiring baseline 切片进入实现。`

#### 2.6 自动决策记录（如有）

- AD-001：将 runtime attachment / orchestration baseline 单独拆为 `014` child work item，而不是继续在 `013` 中扩张 export surface。理由：`013` 已完成 provider/export 基线，runtime attachment 应有独立 formal truth 与测试矩阵。
- AD-002：operator 显式 export 与 runtime attachment 被定义为分层关系，而不是同一能力的两个别名。理由：避免因为已有 `scan` export 就误判 runtime 已自动接线。
- AD-003：attachment scope 强制绑定 active `spec_dir` 或等价显式输入。理由：避免 observation artifact 在 runtime 中静默跨 spec 写入。

#### 2.7 批次结论

- `014` 已具备独立可引用的 runtime attachment docs-only formal baseline。
- 后续若继续推进，应优先在 `014` 内实现 runtime attachment helper，再视需要追加 runner wiring。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交预期为 `docs(014): formalize frontend contract runtime attachment baseline`；完整 SHA 以该提交后的 `HEAD`（`git rev-parse HEAD`）为准
- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`、`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **是否继续下一批**：待用户决定（建议转入 runtime attachment helper / runner wiring implementation slice）

### Batch 2026-04-03-002 | 014 Runtime attachment helper slice

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T41`、`T42`、`T43`
- **目标**：在不越界到 `run_cmd.py`、`runner.py`、`program_cmd.py`、registry 或 remediation 的前提下，落下 runtime attachment 的最小共享 helper，稳定 scope resolution、artifact path resolution、missing/invalid artifact honesty、freshness status 与 explicit opt-in write policy。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、`src/ai_sdlc/core/frontend_contract_observation_provider.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/cli/run_cmd.py`、`tests/unit/test_frontend_contract_observation_provider.py`、`tests/unit/test_verify_constraints.py`
- **激活的规则**：TDD red-green；single canonical truth；verification-before-completion
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（Batch 4 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/014-frontend-contract-runtime-attachment-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 12, 'total_batches': 4, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33'], ['T41', 'T42', 'T43']]}`
- **V2（RED：runtime attachment helper 定向测试）**
  - 命令：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q`
  - 结果：失败；`ModuleNotFoundError: No module named 'ai_sdlc.core.frontend_contract_runtime_attachment'`
- **V3（GREEN：runtime attachment helper 定向测试）**
  - 命令：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q`
  - 结果：`7 passed in 0.13s`
- **V4（静态检查）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（Markdown / code diff hygiene）**
  - 命令：`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T41 | 先写 failing tests 固定 runtime attachment helper 语义

- **改动范围**：`tests/unit/test_frontend_contract_runtime_attachment.py`
- **改动内容**：
  - 先定义 checkpoint / explicit `spec_dir` scope resolution、canonical artifact path、missing/invalid artifact honesty、timestamp-only freshness 与 explicit opt-in write policy 的最小行为。
  - 用测试锁定 explicit `spec_dir` 越界 root 的拒绝语义，以及 explicit input 优先于 checkpoint 的优先级。
  - 确认首次执行时因 helper 模块缺失而 RED。
- **新增/调整的测试**：新增 `tests/unit/test_frontend_contract_runtime_attachment.py`
- **测试结果**：RED 已确认。
- **是否符合任务目标**：符合。

##### T42 | 实现最小 runtime attachment helper

- **改动范围**：`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`
- **改动内容**：
  - 新增 `FrontendContractRuntimeAttachmentScope` 与 `FrontendContractRuntimeAttachment` 两个结构化 dataclass。
  - 新增 `resolve_frontend_contract_runtime_attachment_scope()` 与 `build_frontend_contract_runtime_attachment()`，统一 explicit `spec_dir` / checkpoint scope 解析、canonical artifact path 解析与 read-mostly attachment 状态。
  - 显式暴露 `missing_scope`、`scope_outside_root`、`missing_artifact`、`invalid_artifact`、`attached` 五类状态，以及 `timestamp_only` / `verifiable` freshness status。
  - 保持 helper 只做 runtime attachment contract / policy / honesty 聚合，不触碰 `run_cmd.py`、`runner.py`、`program_cmd.py` 或 scanner/provider 写入。
- **新增/调整的测试**：复用 `tests/unit/test_frontend_contract_runtime_attachment.py`
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T43 | Fresh verify 并追加 implementation batch 归档

- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **改动内容**：
  - 将 `014` formal docs 扩到 `Batch 4: runtime attachment helper slice`，并把只放行 `core/` helper 与对应 tests 的边界写死。
  - 记录本批 RED/GREEN、fresh verification 与 helper 的 read-mostly / explicit opt-in 语义。
  - 保持 `014` 不越界到 `run_cmd.py`、`runner.py`、`program_cmd.py`、registry 或 remediation。
- **新增/调整的测试**：无新增测试文件；以本批 fresh verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只进入 runtime attachment helper 切片，没有跨到 `run`/`runner` wiring、verify/gate 重写、registry 或 remediation。
- **代码质量**：helper 只复用 canonical observation artifact contract，没有引入 runner/program 私有 observation 格式。
- **测试质量**：已完成 RED/GREEN、`ruff`、`diff --check` 与 `verify constraints`。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需变更`
- 关联 branch/worktree disposition 计划：`retained（沿用当前 009/011/012/013/014 工作分支）`
- 说明：`014` 已从 docs-only baseline 进入首批 runtime attachment helper slice，但 runner/program wiring 仍未放行。`

#### 2.6 自动决策记录（如有）

- AD-004：首批实现只落 `core/frontend_contract_runtime_attachment.py`，不同时推进 `run_cmd.py`、`runner.py` 或 `program_cmd.py`。理由：先稳住共享 runtime attachment contract，避免跨多个所有权边界。
- AD-005：helper 只提供显式 scope/path/policy/status，不直接触发 scanner/provider 写入。理由：保持当前切片仍是 read-mostly attachment baseline，而不是新的 runtime side-effect surface。
- AD-006：explicit `spec_dir` 若越出 project root，helper 直接拒绝并返回 `scope_outside_root`。理由：防止 runtime attachment 静默跨 spec 或跨项目写入。
- AD-007：当 artifact 只有 `generated_at` 而缺 `source_digest/source_revision` 时，helper 以 `timestamp_only` freshness 与 advisory 暴露，而不是假装 freshness fully verifiable。理由：把 stale/uncertain honesty 留在结构化状态里，供下游 wiring 决策。

#### 2.7 批次结论

- `014` 当前已具备最小 runtime attachment helper，可作为后续 `run_cmd.py` / `runner.py` wiring 的共享 attachment contract。
- 后续若继续推进，应优先进入 runner wiring slice，而不是回头扩张 provider/export 或 program orchestration。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交预期为 `feat(core): add frontend contract runtime attachment helper`；完整 SHA 以该提交后的 `HEAD`（`git rev-parse HEAD`）为准
- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`tests/unit/test_frontend_contract_runtime_attachment.py`
- **是否继续下一批**：待用户决定（建议转入 runner wiring slice，或继续保持 helper-only baseline）

### Batch 2026-04-03-003 | 014 Runner verify-context wiring slice

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T51`、`T52`、`T53`
- **目标**：在不越界到 `run_cmd.py` CLI wording、`program_cmd.py`、registry、scanner/provider 写入或 gate verdict 改写的前提下，把 runtime attachment helper 以 read-only 方式接入 `SDLCRunner` 的 verify-stage context。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_runner_confirm.py`
- **激活的规则**：TDD red-green；single canonical truth；verification-before-completion
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（Batch 5 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/014-frontend-contract-runtime-attachment-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 15, 'total_batches': 5, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33'], ['T41', 'T42', 'T43'], ['T51', 'T52', 'T53']]}`
- **V2（RED：runner verify-context 定向测试）**
  - 命令：`uv run pytest tests/unit/test_runner_confirm.py -q`
  - 结果：失败；`KeyError: 'frontend_contract_runtime_attachment'`
- **V3（GREEN：runner verify-context 定向测试）**
  - 命令：`uv run pytest tests/unit/test_runner_confirm.py -q`
  - 结果：`16 passed in 1.07s`
- **V4（静态检查）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（Markdown / code diff hygiene）**
  - 命令：`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`
- **V7（跨 helper / runner / CLI run 的扩大 fresh 验证）**
  - 命令：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py tests/unit/test_runner_confirm.py tests/integration/test_cli_run.py -q`
  - 结果：`33 passed in 2.32s`

#### 2.3 任务记录

##### T51 | 先写 failing tests 固定 runner verify-context attachment 语义

- **改动范围**：`tests/unit/test_runner_confirm.py`
- **改动内容**：
  - 先定义 active `014` scope 时 `SDLCRunner._build_context("verify", cp)` 必须附带 `frontend_contract_runtime_attachment` payload。
  - 用测试锁定 non-`014` scope 不应被无差别注入该 payload。
  - 确认首次执行时因 verify context 尚未接线而 RED，失败点是缺少 `frontend_contract_runtime_attachment` key。
- **新增/调整的测试**：扩展 `tests/unit/test_runner_confirm.py`
- **测试结果**：RED 已确认。
- **是否符合任务目标**：符合。

##### T52 | 实现最小 runner verify-context wiring

- **改动范围**：`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`
- **改动内容**：
  - 在 `frontend_contract_runtime_attachment.py` 增加 `to_json_dict()` 序列化与 `is_frontend_contract_runtime_attachment_work_item()` scope 判定，避免 runner 内部重复拼装 payload。
  - 在 `SDLCRunner._build_context("verify", cp)` 中，仅当 active checkpoint 属于 `014` 时，注入结构化 `frontend_contract_runtime_attachment` payload。
  - wiring 保持 read-only，不改 gate verdict、CLI wording，也不触发 scanner/provider 写入。
- **新增/调整的测试**：复用 `tests/unit/test_runner_confirm.py`
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T53 | Fresh verify 并追加 implementation batch 归档

- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **改动内容**：
  - 将 `014` formal docs 扩到 `Batch 5: runner verify-context wiring slice`，并把只放行 `core/runner.py`、`core/frontend_contract_runtime_attachment.py` 与 `tests/unit/test_runner_confirm.py` 的边界写死。
  - 记录本批 RED/GREEN、fresh verification 与 read-only runner verify-context 语义。
  - 追加一轮跨 helper / runner / CLI run 的扩大 fresh 验证，证明这批 wiring 没有破坏现有 `run` 主线。
- **新增/调整的测试**：无新增测试文件；以本批 fresh verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只进入 runner verify-context wiring，没有跨到 `run_cmd.py` 用户面、`program_cmd.py`、registry、scanner/provider 写入或 gate verdict 改写。
- **代码质量**：runner 只接入结构化 payload，不引入新的 runtime side effects；scope 判定和 payload 序列化保持在 attachment helper 内聚。
- **测试质量**：已完成 RED/GREEN、扩大 `pytest` 回归、`ruff`、`diff --check` 与 `verify constraints`。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需变更`
- 关联 branch/worktree disposition 计划：`retained（沿用当前 009/011/012/013/014 工作分支）`
- 说明：`014` 已从 helper slice 进入 runner verify-context wiring，但 `run_cmd.py` 用户面与 program orchestration 仍未放行。`

#### 2.6 自动决策记录（如有）

- AD-008：runner wiring 只进入 verify-stage context，不进入 CLI wording 或 gate verdict。理由：先把 runtime attachment 状态接入正式 context，再决定是否扩张用户面或 gate 语义。
- AD-009：non-`014` scope 明确不注入 `frontend_contract_runtime_attachment` payload。理由：保持 scoped attachment，不污染其他 work item 的 verify context。

#### 2.7 批次结论

- `014` 当前已具备 helper + runner verify-context 的最小主链，runtime attachment 状态已能进入正式 pipeline context。
- 后续若继续推进，应优先决定是补 `run_cmd.py` 用户面提示，还是直接结束 `014` 并切到下一个 MVP workstream。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交预期为 `feat(core): wire runtime attachment into runner verify context`；完整 SHA 以该提交后的 `HEAD`（`git rev-parse HEAD`）为准
- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`src/ai_sdlc/core/runner.py`、`tests/unit/test_runner_confirm.py`
- **是否继续下一批**：按用户授权连续推进（下一优先级是 `run_cmd.py` 用户面，或在 `014` 达到 MVP 最小闭环后转入下一个 MVP downstream work item）

### Batch 2026-04-03-004 | 014 Run CLI attachment summary surface slice

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T61`、`T62`、`T63`
- **目标**：把 active `014` scope 的 runtime attachment status 正式暴露到 `ai-sdlc run` 的终端输出，让 operator 不读取 runner 内部 context 也能看到 `attached / missing_artifact` 状态与最小 gap 摘要。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、`src/ai_sdlc/cli/run_cmd.py`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`src/ai_sdlc/core/runner.py`、`tests/integration/test_cli_run.py`
- **激活的规则**：TDD red-green；single canonical truth；verification-before-completion
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（Batch 6 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/014-frontend-contract-runtime-attachment-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 18, 'total_batches': 6, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33'], ['T41', 'T42', 'T43'], ['T51', 'T52', 'T53'], ['T61', 'T62', 'T63']]}`
- **V2（RED：014 run CLI summary 定向测试）**
  - 命令：`uv run pytest tests/integration/test_cli_run.py -q -k "runtime_attachment"`
  - 结果：`2 failed, 10 deselected in 0.34s`
- **V3（GREEN：014 run CLI summary 定向测试）**
  - 命令：`uv run pytest tests/integration/test_cli_run.py -q -k "runtime_attachment"`
  - 结果：`2 passed, 10 deselected in 0.23s`
- **V4（GREEN：run CLI integration 全量回归）**
  - 命令：`uv run pytest tests/integration/test_cli_run.py -q`
  - 结果：`12 passed in 1.33s`
- **V5（静态检查）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V6（Markdown / code diff hygiene）**
  - 命令：`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/cli tests/integration`
  - 结果：无输出。
- **V7（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T61 | 先写 failing tests 固定 runtime attachment 的 run 终端输出语义

- **改动范围**：`tests/integration/test_cli_run.py`
- **改动内容**：
  - 新增 active `014` 且 runtime attachment 已 attached 时的 `run --dry-run` 终端输出断言。
  - 新增 active `014` 且 observation artifact 缺失时的终端输出与最小 `coverage_gaps` 摘要断言。
  - 首次运行定向测试时命中 `2 failed`，证明 `run_cmd.py` 尚未渲染 runtime attachment summary，RED 成立。
- **新增/调整的测试**：扩展 `tests/integration/test_cli_run.py`。
- **测试结果**：RED 成立，失败点集中在 `frontend contract runtime attachment` summary 尚未出现在终端输出。
- **是否符合任务目标**：符合。

##### T62 | 实现最小 run CLI attachment summary 渲染

- **改动范围**：`src/ai_sdlc/cli/run_cmd.py`
- **改动内容**：
  - 在 `run` 命令完成后，对 active `014` scope 读取既有 runtime attachment helper，并输出 `frontend contract runtime attachment: <status>` 行。
  - 在非 attached 路径显示最小 `coverage gaps` 或 blocker 摘要，但不改变 runner context、gate verdict 或任何 runtime side effect。
  - 保持 CLI summary 只消费已冻结的 helper truth，不新增 CLI-only attachment schema。
- **新增/调整的测试**：复用 `tests/integration/test_cli_run.py`
- **测试结果**：`2 passed, 10 deselected in 0.23s`
- **是否符合任务目标**：符合。

##### T63 | Fresh verify 并追加 CLI batch 归档

- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **改动内容**：
  - 将 Batch 6 正式加入 `plan.md / tasks.md`，把 `run CLI attachment summary surface` 的 scope、文件面、验证面和执行护栏写成 formal truth。
  - 回填本批 parser / RED / GREEN / integration / static / diff hygiene / governance 验证结果，并归档 touched files 与 CLI user-surface 边界。
- **新增/调整的测试**：无新增测试文件；以本批 fresh verification 命令为准。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只进入 `run_cmd.py` 的 CLI summary surface，没有越界到 `program_cmd.py`、registry、scanner/provider 写入或新的 gate verdict。
- **代码质量**：runtime attachment summary 复用既有 helper truth，不复制第二套 attachment payload。
- **测试质量**：先 RED 再 GREEN，覆盖 attached 与 missing_artifact 两类终端输出路径，并补 fresh integration、`ruff`、`diff --check` 与 `verify constraints`。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需变更`
- 关联 branch/worktree disposition 计划：`retained（沿用当前 009/011/012/013/014/015/016/017/018 工作分支）`
- 说明：`014` 已经把 runtime attachment status 暴露到 run CLI 终端面，但 `program_cmd.py` 与更重的 orchestration/runtime 工单仍待下游承接。`

#### 2.6 自动决策记录（如有）

- AD-010：CLI slice 只渲染既有 runtime attachment helper 的结构化状态，而不新增 CLI-only attachment schema。理由：保持 helper、runner context 与用户面的真值单一。
- AD-011：非 attached 路径仅输出最小 coverage gap / blocker 摘要，不在 `run` 终端面展开完整 diagnostics。理由：先提供 operator 可见性，再把更重的诊断扩展留给下游 orchestration/runtime 工单。

#### 2.7 批次结论

- `014` 已具备 runtime attachment 的 run CLI user-facing surface，operator 现在可以直接从 `ai-sdlc run` 输出看到 attachment 是否已挂接，以及最小缺口摘要。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本批提交后生成
- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`、`specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`、`src/ai_sdlc/cli/run_cmd.py`、`tests/integration/test_cli_run.py`
- **是否继续下一批**：按用户授权连续推进（优先评估 `program_cmd.py` 用户面，或为 frontend orchestration/runtime 新开下游 child work item）

### Batch 2026-04-04-005 | frontend close-check evidence remediation

#### 1. 准备

- **任务来源**：`框架总览复核 / frontend close-check evidence remediation`
- **目标**：为 `014-frontend-contract-runtime-attachment-baseline` 补齐最新 canonical close-out batch，使 execution log 满足当前框架的 `workitem close-check` 字段契约，不改动已冻结的实现边界。
- **预读范围**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`src/ai_sdlc/core/close_check.py`
- **激活的规则**：close-check execution log fields；verification profile truthfulness；git close-out markers truthfulness。
- **验证画像**：`docs-only`
- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`

#### 2. 统一验证命令

- **V1（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 3. 任务记录

##### Task close-out | 追加 canonical evidence batch

- **改动范围**：`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **改动内容**：
  - 追加符合当前框架的最新 `### Batch ...` 正式批次结构，补齐 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`验证画像` 与 git close-out markers。
  - 保留既有历史执行记录，不改写旧批次；本批只作为最新 canonical close-out evidence。
  - 不新增产品实现，不放宽 `014-frontend-contract-runtime-attachment-baseline` 已冻结的功能边界。
- **新增/调整的测试**：无。本批仅做 docs-only 收口证据回填。
- **执行的命令**：见 V1。
- **测试结果**：`uv run ai-sdlc verify constraints` 通过；其余 `workitem close-check` 复核在真实 git close-out 后统一执行。
- **是否符合任务目标**：符合。

#### 4. 代码审查（摘要）

- **宪章/规格对齐**：本批只补 execution evidence schema，不更改 `014-frontend-contract-runtime-attachment-baseline` 的 spec / plan / task 合同语义。
- **代码质量**：无运行时代码变更。
- **测试质量**：`docs-only` 批次已记录 `uv run ai-sdlc verify constraints`；最终完成态仍以真实 git close-out 后的 `workitem close-check` 复核为准。
- **结论**：允许继续执行真实 git close-out。

#### 5. 任务/计划同步状态

- `tasks.md` 同步状态：`已对账`
- `plan.md` 同步状态：`已对账`
- `spec.md` 同步状态：`已对账`

#### 6. 批次结论

- `014-frontend-contract-runtime-attachment-baseline` 当前补齐的是 close-out evidence schema；实现边界保持不变，最终 pass 仍依赖真实 git close-out 后复核。

#### 7. 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`46b50e0`
- **是否继续下一批**：是；下一步执行真实 git close-out，并复跑 `workitem close-check`
