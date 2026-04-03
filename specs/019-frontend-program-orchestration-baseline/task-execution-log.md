# 019-frontend-program-orchestration-baseline 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/019-frontend-program-orchestration-baseline/` 相关的 formal docs freeze、implementation handoff 或 close-out，都在本文件末尾追加新批次章节。
- 本 work item 的 canonical truth，以 [`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件和当前分支提交链共同为准。
- `019` 是 `014` / `018` 之后的 frontend program orchestration formal baseline；后续 `src/` / `tests/` 实现应由本工单或其下游切片承接，而不是回写上游 mother spec。

## 2. 批次记录

### Batch 2026-04-03-001 | 019 Frontend program orchestration formal baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`、`T12`、`T13`、`T21`、`T22`、`T23`、`T31`、`T32`、`T33`
- **目标**：把 `014` / `018` 之后的 program-level frontend orchestration 从零散 downstream suggestion 收敛成独立 child work item，冻结 readiness truth、status/plan/integrate responsibility、execute guard 与 implementation handoff。
- **预读范围**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/plan.md`](../014-frontend-contract-runtime-attachment-baseline/plan.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/plan.md`](../018-frontend-gate-compatibility-baseline/plan.md)、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：single canonical truth；docs-only execute；downstream child-work-item first；verification-before-completion
- **验证画像**：`docs-only`

#### 2.2 统一验证命令

- **V1（Batch 1-3 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/019-frontend-program-orchestration-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 9, 'total_batches': 3, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33']]}`
- **V2（Markdown diff hygiene）**
  - 命令：`git diff --check -- specs/019-frontend-program-orchestration-baseline`
  - 结果：无输出。
- **V3（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 / T13 | 冻结 program frontend truth、non-goals 与 readiness truth linkage

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `019` 正式定义为 `014 / 018` 下游的 frontend program orchestration child work item。
  - 锁定 program-level frontend orchestration 只消费既有 per-spec truth，不新增 program 私有 frontend truth。
  - 锁定 non-goals，包括 auto-scan、auto-attach、auto-fix、registry、cross-spec writeback 与默认 execute side effect。
- **新增/调整的测试**：无代码测试；依赖 parser 结构校验与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T21 / T22 / T23 | 冻结 status / plan / integrate responsibility 与 downstream handoff

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 明确 `program status / plan / integrate --dry-run` 的 frontend responsibility、readiness granularity 与 honesty 规则。
  - 明确 readiness 最小暴露面包括 readiness state、coverage gaps、blockers 与 source linkage。
  - 明确后续实现起点优先是 `program_service.py` readiness aggregation 与 `program_cmd.py` dry-run/status surface，而 execute runtime 仍由下游工单承接。
- **新增/调整的测试**：无代码测试；依赖文档对账与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T31 / T32 / T33 | 冻结 implementation handoff 与 docs-only baseline

- **改动范围**：[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件
- **改动内容**：
  - 锁定 `core / cli / tests` 推荐文件面与 ownership 边界。
  - 锁定最小测试矩阵与 execute 前置条件。
  - 通过 parser / diff hygiene / `verify constraints` 将 `019` 固定为可继续实现的 docs-only baseline。
- **新增/调整的测试**：无代码测试；以本批 docs-only verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只冻结 `019` formal baseline，没有越界到 `program_cmd.py`、`program_service.py` 或 execute runtime 实现。
- **代码质量**：无 `src/` / `tests/` 变更；文档内容围绕 program-level frontend readiness、honesty 与 execute guard，不引入第二套 truth。
- **测试质量**：已完成 parser 结构校验、`git diff --check` 与 `verify constraints` fresh 验证。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`已同步`
- 关联 branch/worktree disposition 计划：`retained（沿用当前前端治理连续推进分支）`
- 说明：`019` 当前作为 frontend program orchestration 的 docs-only baseline 保留在当前分支上；下一步建议在 019 内进入 program readiness aggregation / CLI surface implementation slice。`

#### 2.6 自动决策记录（如有）

- AD-001：program-level frontend orchestration 单独拆为 `019` child work item，而不是继续扩张 `014`。理由：`014` 已经完成 runtime attachment baseline，program orchestration 属于新的责任面，应保持独立 formal truth 与测试矩阵。
- AD-002：`019` 当前只冻结 docs-only baseline，不直接进入 execute runtime。理由：先锁定 program-level readiness truth 与 guard，避免过早把 auto-attach / auto-fix 偷渡进 program surface。

#### 2.7 批次结论

- `019` 已具备独立可引用的 program-level frontend orchestration formal baseline。
- 后续若继续推进，应优先在 `019` 内实现 per-spec frontend readiness aggregation 与 `program status / integrate --dry-run` user-facing surface。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待后续提交生成
- **改动范围**：`specs/019-frontend-program-orchestration-baseline/spec.md`、`specs/019-frontend-program-orchestration-baseline/plan.md`、`specs/019-frontend-program-orchestration-baseline/tasks.md`、`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`
- **是否继续下一批**：按用户授权连续推进（优先转入 `019` 的 readiness aggregation / CLI surface implementation slice）

### Batch 2026-04-03-002 | 019 Program frontend readiness aggregation

#### 3.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T41`、`T42`、`T43`
- **目标**：在 `ProgramService` 中按 spec 粒度聚合 frontend readiness，消费 `014` runtime attachment 与 `018` frontend gate truth，并保持只读聚合。
- **预读范围**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`src/ai_sdlc/core/frontend_gate_verification.py`、`tests/unit/test_program_service.py`
- **激活的规则**：single canonical truth；test-driven-development；verification-before-completion；no execute runtime expansion
- **验证画像**：`code-change`

#### 3.2 统一验证命令

- **V1（Batch 4 RED 校验）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q -k "frontend_readiness"`
  - 结果：`2 failed`，失败原因为 `ProgramSpecStatus` 尚无 `frontend_readiness` 字段，符合预期 RED。
- **V2（019 tasks parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/019-frontend-program-orchestration-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches})"`
  - 结果：`{'total_tasks': 15, 'total_batches': 5}`
- **V3（Batch 4 单测 fresh）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q`
  - 结果：`9 passed`
- **V4（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（diff hygiene）**
  - 命令：`git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 3.3 任务记录

##### T41 | failing tests 固定 per-spec frontend readiness aggregation

- **改动范围**：[`tests/unit/test_program_service.py`](tests/unit/test_program_service.py)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `019` 的执行基线从 `3 batches / 9 tasks` 扩展为 `5 batches / 15 tasks`，显式放行 Batch 4/5 实现切片。
  - 新增 frontend-ready spec 与 missing-attachment 两个单测，固定 per-spec readiness 的 `state / coverage_gaps / blockers / source_linkage` 语义。
  - 通过 RED 运行确认实现前 `ProgramService` 尚未暴露 `frontend_readiness`。
- **新增/调整的测试**：`test_build_status_surfaces_ready_frontend_readiness_per_spec`、`test_build_status_surfaces_frontend_readiness_gap_when_attachment_missing`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T42 | 实现最小 program frontend readiness aggregation

- **改动范围**：[`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)
- **改动内容**：
  - 新增 `ProgramFrontendReadiness` 聚合对象，并挂接到 `ProgramSpecStatus` 与 `ProgramIntegrationStep`。
  - 通过 `build_frontend_contract_runtime_attachment(..., explicit_spec_dir=spec_dir)` 读取 per-spec runtime attachment truth。
  - 在 attachment 为 `attached` 时继续消费 `build_frontend_gate_verification_report(...)`，统一形成 `ready / retry / missing_artifact` 等 readiness state。
  - 聚合并去重 `coverage_gaps`、`blockers`，同时暴露 runtime attachment 与 frontend gate 的 source linkage。
- **新增/调整的测试**：依赖 `tests/unit/test_program_service.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T43 | fresh verify 并追加 implementation batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 4 的 RED/GREEN 证据、parser 结构校验与 fresh verification 结果。
  - 固化 touched files、验证命令与结论，保持 `019` implementation history append-only。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 3.4 代码审查（Mandatory）

- **宪章/规格对齐**：实现只读取 `014` runtime attachment 与 `018` frontend gate truth，没有新增 program 私有 truth，也未触发 execute runtime。
- **代码质量**：frontend readiness 聚合封装在 `ProgramService`，且通过 `ProgramIntegrationStep` 复用到后续 dry-run surface，未回写上游 work item。
- **测试质量**：已完成 RED 验证、full unit file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 3.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步（15 tasks / 5 batches）`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（继续在当前分支进入 Batch 5）`
- 说明：`Batch 4` 已把 frontend readiness 真值接入 `ProgramService`；下一步转入 CLI surface。`

#### 3.6 自动决策记录（如有）

- AD-003：`ProgramIntegrationStep` 同步挂接 `frontend_readiness`。理由：避免 CLI dry-run 再次重新聚合，保持 status / integrate 共享同一 service truth。
- AD-004：attachment 未就绪时 frontend gate verdict 采用 `UNRESOLVED`。理由：此时 program 只能诚实暴露未接线状态，不能伪造新的 gate 结果。

#### 3.7 批次结论

- `019` 已具备 per-spec frontend readiness aggregation，且 program-level frontend truth 仍保持只读聚合。
- `program status` 与 `program integrate --dry-run` 已具备稳定的数据源，可以继续进入 CLI user-facing surface。

#### 3.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待 Batch 5 合并提交
- **改动范围**：`specs/019-frontend-program-orchestration-baseline/plan.md`、`specs/019-frontend-program-orchestration-baseline/tasks.md`、`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`、`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`
- **是否继续下一批**：是（继续进入 `program` CLI frontend readiness surface）

### Batch 2026-04-03-003 | 019 Program CLI frontend readiness surface

#### 4.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T51`、`T52`、`T53`
- **目标**：把 per-spec frontend readiness 暴露到 `program status` 与 `program integrate --dry-run` 的终端输出，不引入 execute runtime。
- **预读范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：test-driven-development；scoped user-facing surface；verification-before-completion
- **验证画像**：`code-change`

#### 4.2 统一验证命令

- **V1（Batch 5 RED 校验）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q -k "frontend"`
  - 结果：`2 failed`，失败原因为 CLI 尚未显示 `Frontend` / `Frontend Hint` surface，符合预期 RED。
- **V2（Batch 5 集成测试 fresh）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q`
  - 结果：`9 passed`
- **V3（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V4（diff hygiene）**
  - 命令：`git diff --check -- specs/019-frontend-program-orchestration-baseline src/ai_sdlc/cli tests/integration`
  - 结果：无输出。
- **V5（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 4.3 任务记录

##### T51 | failing tests 固定 program CLI frontend readiness 输出语义

- **改动范围**：[`tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)
- **改动内容**：
  - 为 `program status` 新增 frontend readiness 输出测试，覆盖 ready 与 missing_artifact 两类状态。
  - 为 `program integrate --dry-run` 新增 frontend hint 输出测试，覆盖 `missing_artifact [frontend_contract_observations]` 的最小 hint。
  - 通过 RED 运行确认旧 CLI surface 尚未渲染 frontend readiness。
- **新增/调整的测试**：`test_program_status_exposes_frontend_readiness`、`test_program_integrate_dry_run_exposes_frontend_hint`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T52 | 实现最小 program CLI frontend readiness surface

- **改动范围**：[`src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)
- **改动内容**：
  - 在 `program status` 表格中追加 `Frontend` 列，并在表格下补充稳定的 `Frontend Readiness` 文本摘要。
  - 在 `program integrate --dry-run` 表格中追加 `Frontend Hint` 列，并在表格下补充稳定的 `Frontend Hints` 文本摘要。
  - report 输出同步包含每个 integration step 的 frontend hint。
  - 保持 execute gate 与 manifest 语义不变，仅增加 user-facing 可见性。
- **新增/调整的测试**：依赖 `tests/integration/test_cli_program.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T53 | fresh verify 并追加 CLI batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 5 的 RED/GREEN 证据与 fresh verification 结果。
  - 固化 CLI touched files、验证命令与 user-facing surface 的最小结论。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 4.4 代码审查（Mandatory）

- **宪章/规格对齐**：CLI 只暴露 frontend readiness / hint，没有扩张到 execute runtime、registry、auto-fix 或 writeback。
- **代码质量**：采用 `ProgramService` 的共享 readiness truth；额外文本摘要用于规避窄终端下的表格截断，不引入第二套业务逻辑。
- **测试质量**：已完成 RED 验证、full integration file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 4.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（当前轮次提交后继续沿用）`
- 说明：`019` 的 service truth 与 CLI surface 已打通；后续若继续推进，应进入 execute runtime / recheck / remediation 下游工单。`

#### 4.6 自动决策记录（如有）

- AD-005：在表格之外补充 `Frontend Readiness` / `Frontend Hints` 文本摘要。理由：Rich 表格在测试终端宽度下会压缩长列，文本摘要更稳定且不改变业务真值。

#### 4.7 批次结论

- `program status` 与 `program integrate --dry-run` 已能直接暴露 per-spec frontend readiness 与最小 hint。
- `019` 当前的 program-level frontend orchestration baseline 已形成从 formal docs 到 core/service 再到 CLI surface 的闭环。

#### 4.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本轮提交生成
- **改动范围**：`specs/019-frontend-program-orchestration-baseline/task-execution-log.md`、`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`
- **是否继续下一批**：按用户授权连续推进（建议进入 frontend execute runtime / recheck / remediation 的下游 child work item）
