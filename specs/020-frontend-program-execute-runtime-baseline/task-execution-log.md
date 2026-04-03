# 020-frontend-program-execute-runtime-baseline 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/020-frontend-program-execute-runtime-baseline/` 相关的 formal docs freeze、implementation handoff 或 close-out，都在本文件末尾追加新批次章节。
- 本 work item 的 canonical truth，以 [`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件和当前分支提交链共同为准。
- `020` 是 `019` 之后的 frontend program execute runtime formal baseline；后续 `src/` / `tests/` 实现应由本工单或其下游切片承接，而不是回写上游 mother spec。

## 2. 批次记录

### Batch 2026-04-03-001 | 020 Frontend program execute runtime formal baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`、`T12`、`T13`、`T21`、`T22`、`T23`、`T31`、`T32`、`T33`
- **目标**：把 `019` 之后的 program-level frontend execute runtime 从 downstream suggestion 收敛成独立 child work item，冻结 execute truth、recheck handoff、remediation hint 与 downstream auto-fix handoff。
- **预读范围**：[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/plan.md`](../018-frontend-gate-compatibility-baseline/plan.md)、[`../019-frontend-program-orchestration-baseline/spec.md`](../019-frontend-program-orchestration-baseline/spec.md)、[`../019-frontend-program-orchestration-baseline/plan.md`](../019-frontend-program-orchestration-baseline/plan.md)、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：single canonical truth；docs-only execute；downstream child-work-item first；verification-before-completion
- **验证画像**：`docs-only`

#### 2.2 统一验证命令

- **V1（Batch 1-3 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/020-frontend-program-execute-runtime-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 9, 'total_batches': 3, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33']]}`
- **V2（Markdown diff hygiene）**
  - 命令：`git diff --check -- specs/020-frontend-program-execute-runtime-baseline`
  - 结果：无输出。
- **V3（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 / T13 | 冻结 execute runtime truth、non-goals 与 execute source linkage

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `020` 正式定义为 `019` 下游的 frontend program execute runtime child work item。
  - 锁定 program execute 只消费 `019` readiness truth 与 `018` recheck boundary，不新增 program 私有 execute truth。
  - 锁定 non-goals，包括 scanner/provider 写入、auto-attach、auto-fix、registry、cross-spec writeback 与默认 execute side effect。
- **新增/调整的测试**：无代码测试；依赖 parser 结构校验与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T21 / T22 / T23 | 冻结 execute preflight、recheck handoff 与 remediation hint 责任

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 明确 `program integrate --execute` 的 frontend preflight、step-level recheck handoff 与 remediation hint responsibility。
  - 明确 execute blocker、recheck_required 与 remediation hint 都按 spec 粒度暴露。
  - 明确 remediation hint 不是 auto-fix engine，未来 auto-fix 仍由下游工单承接。
- **新增/调整的测试**：无代码测试；依赖文档对账与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T31 / T32 / T33 | 冻结 implementation handoff 与 docs-only baseline

- **改动范围**：[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件
- **改动内容**：
  - 锁定 `core / cli / tests` 推荐文件面与 ownership 边界。
  - 锁定最小测试矩阵与 execute runtime 实现前提。
  - 为后续 frontend program execute runtime / auto-fix downstream 主线保留稳定 docs-only baseline。
- **新增/调整的测试**：无代码测试；以本批 docs-only verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只冻结 `020` formal baseline，没有越界到 `program_cmd.py`、`program_service.py` 或 auto-fix runtime 实现。
- **代码质量**：无 `src/` / `tests/` 变更；文档内容围绕 execute truth、recheck handoff 与 remediation hint，不引入第二套 truth。
- **测试质量**：已完成 parser 结构校验、`git diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`已同步`
- 关联 branch/worktree disposition 计划：`retained（沿用当前前端治理连续推进分支）`
- 说明：`020` 当前作为 frontend program execute runtime 的 docs-only baseline 保留在当前分支上；下一步建议在 020 内进入 execute preflight / recheck handoff implementation slice。`

#### 2.6 自动决策记录（如有）

- AD-001：program execute runtime 单独拆为 `020` child work item，而不是继续扩张 `019`。理由：`019` 已完成 readiness aggregation 与 dry-run/status surface，execute runtime 属于新的责任面，应保持独立 formal truth 与测试矩阵。

#### 2.7 批次结论

- `020` 已具备独立可引用的 program-level frontend execute runtime formal baseline。
- 后续若继续推进，应优先在 `020` 内实现 execute preflight、recheck handoff 与 remediation hint surface。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待后续提交生成
- **改动范围**：`specs/020-frontend-program-execute-runtime-baseline/spec.md`、`specs/020-frontend-program-execute-runtime-baseline/plan.md`、`specs/020-frontend-program-execute-runtime-baseline/tasks.md`、`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`
- **是否继续下一批**：按用户授权连续推进（优先转入 `020` 的 execute preflight / recheck handoff implementation slice）

### Batch 2026-04-03-002 | 020 Program frontend execute preflight

#### 3.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T41`、`T42`、`T43`
- **目标**：在 `ProgramService` 中按 spec 粒度引入 frontend execute preflight，使 `program --execute` 正式消费 `019` readiness truth。
- **预读范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **激活的规则**：single canonical truth；test-driven-development；verification-before-completion；no recheck loop / auto-fix expansion
- **验证画像**：`code-change`

#### 3.2 统一验证命令

- **V1（Batch 4 RED 校验）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q -k "frontend_readiness_not_clear or frontend_ready"`
  - 结果：`1 failed, 1 passed`，失败原因为 `evaluate_execute_gates()` 尚未消费 frontend readiness，符合预期 RED。
- **V2（020 tasks parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/020-frontend-program-execute-runtime-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches})"`
  - 结果：`{'total_tasks': 15, 'total_batches': 5}`
- **V3（Batch 4 单测 fresh）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q`
  - 结果：`11 passed`
- **V4（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（diff hygiene）**
  - 命令：`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 3.3 任务记录

##### T41 | failing tests 固定 frontend execute preflight 语义

- **改动范围**：[`tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `020` 的执行基线从 `3 batches / 9 tasks` 扩展为 `5 batches / 15 tasks`，显式放行 Batch 4/5 实现切片。
  - 新增 execute preflight 单测，固定“frontend 不 clear 必须阻断、frontend ready 才能放行”的 program execute 语义。
  - 通过 RED 运行确认旧 `evaluate_execute_gates()` 还没有消费 frontend readiness。
- **新增/调整的测试**：`test_execution_gates_fail_when_frontend_readiness_not_clear`、`test_execution_gates_pass_when_closed_and_frontend_ready`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T42 | 实现最小 frontend execute preflight

- **改动范围**：[`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)
- **改动内容**：
  - 让 `evaluate_execute_gates()` 正式消费 `ProgramSpecStatus.frontend_readiness`。
  - 当 readiness 不为 `ready` 时，按 spec 粒度追加 `frontend execute gate not clear` 失败项。
  - 失败信息中同时保留 `state` 与最小 `coverage_gaps / remediation_hint`，保持 execute honesty。
- **新增/调整的测试**：依赖 `tests/unit/test_program_service.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T43 | fresh verify 并追加 implementation batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 4 的 RED/GREEN 证据、parser 结构校验与 fresh verification 结果。
  - 固化 touched files、验证命令与结论，保持 `020` implementation history append-only。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 3.4 代码审查（Mandatory）

- **宪章/规格对齐**：实现只消费 `019` readiness truth，没有新增 execute 私有 truth，也未越界到 recheck loop / auto-fix runtime。
- **代码质量**：frontend execute preflight 收口在 `ProgramService.evaluate_execute_gates()`，没有改写 dry-run / status truth。
- **测试质量**：已完成 RED 验证、full unit file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 3.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步（15 tasks / 5 batches）`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（继续在当前分支进入 Batch 5）`
- 说明：`Batch 4` 已把 frontend execute preflight 接入 `ProgramService`；下一步转入 execute CLI surface。`

#### 3.6 自动决策记录（如有）

- AD-002：execute preflight 失败项直接复用 readiness state 与 coverage gaps。理由：保持 execute gate 与 `019` readiness truth 单一来源，避免构造第二套解释层。

#### 3.7 批次结论

- `020` 已具备 per-spec frontend execute preflight。
- `program integrate --execute` 已拥有稳定的 frontend gate 数据源，可以继续进入 CLI user-facing surface。

#### 3.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待 Batch 5 合并提交
- **改动范围**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`、`specs/020-frontend-program-execute-runtime-baseline/tasks.md`、`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`
- **是否继续下一批**：是（继续进入 `program` execute CLI frontend gate surface）

### Batch 2026-04-03-003 | 020 Program execute CLI frontend gate surface

#### 4.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T51`、`T52`、`T53`
- **目标**：把 frontend execute preflight 暴露到 `program integrate --execute` 的终端输出，不引入 recheck loop 或 auto-fix runtime。
- **预读范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：test-driven-development；scoped user-facing surface；verification-before-completion
- **验证画像**：`code-change`

#### 4.2 统一验证命令

- **V1（Batch 5 RED 校验）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q -k "frontend_preflight"`
  - 结果：`2 failed`，失败原因为 CLI 尚未显示 `Frontend Execute Preflight` surface，符合预期 RED。
- **V2（Batch 5 集成测试 fresh）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q`
  - 结果：`11 passed`
- **V3（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V4（diff hygiene）**
  - 命令：`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/cli tests/integration`
  - 结果：无输出。
- **V5（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 4.3 任务记录

##### T51 | failing tests 固定 execute CLI frontend gate 输出语义

- **改动范围**：[`tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)
- **改动内容**：
  - 为 execute 失败路径新增 frontend preflight 输出测试，覆盖 `missing_artifact` 与 `frontend_contract_observations`。
  - 为 execute 通过路径新增 frontend preflight 输出测试，覆盖 `ready` 与 gate pass 文案。
  - 通过 RED 运行确认 execute CLI 尚未显示独立 frontend preflight section。
- **新增/调整的测试**：`test_program_integrate_execute_surfaces_frontend_preflight_failure`、`test_program_integrate_execute_surfaces_frontend_preflight_pass`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T52 | 实现最小 execute CLI frontend gate surface

- **改动范围**：[`src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)
- **改动内容**：
  - 在 `program integrate --execute` 的 `--yes` 路径中新增 `Frontend Execute Preflight` section。
  - execute 前直接按 spec 粒度显示 frontend readiness，确保 operator 在真正 evaluate gates 前看到 frontend gate。
  - 保持 dry-run/status surface 语义不变，不引入 recheck loop 或 auto-fix runtime。
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

- **宪章/规格对齐**：CLI 只暴露 execute preflight frontend gate，没有扩张到 recheck loop、auto-fix、writeback 或 scanner/provider 写入。
- **代码质量**：采用 `ProgramService` 的共享 readiness / execute truth；新增 section 只增强 operator 可见性，不改业务真值。
- **测试质量**：已完成 RED 验证、full integration file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 4.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（当前轮次提交后继续沿用）`
- 说明：`020` 的 service truth 与 execute CLI surface 已打通；后续若继续推进，应进入 recheck handoff / remediation runtime 的下游切片。`

#### 4.6 自动决策记录（如有）

- AD-003：execute path 增加独立 `Frontend Execute Preflight` section。理由：execute 前需要显式看到 frontend gate，而不仅是失败后在通用 failed list 中发现一条字符串。

#### 4.7 批次结论

- `program integrate --execute` 已能直接暴露 frontend execute preflight。
- `020` 当前的 program-level frontend execute runtime baseline 已形成从 formal docs 到 core/service 再到 execute CLI surface 的闭环。

#### 4.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本轮提交生成
- **改动范围**：`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`
- **是否继续下一批**：按用户授权连续推进（建议进入 frontend recheck handoff / remediation runtime 的下游 child work item）

### Batch 2026-04-03-004 | 020 Program frontend recheck handoff

#### 5.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T61`、`T62`、`T63`
- **目标**：在 `ProgramService` 中为 execute-ready integration steps 暴露 frontend recheck handoff truth，而不进入 recheck loop runtime。
- **预读范围**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **激活的规则**：single canonical truth；test-driven-development；verification-before-completion；no recheck loop / auto-fix expansion
- **验证画像**：`code-change`

#### 5.2 统一验证命令

- **V1（Batch 6 RED 校验）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q -k "frontend_recheck_handoff"`
  - 结果：`2 failed`，失败原因为 `ProgramIntegrationStep` 尚未暴露 `frontend_recheck_handoff` 字段，符合预期 RED。
- **V2（020 tasks parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/020-frontend-program-execute-runtime-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches})"`
  - 结果：`{'total_tasks': 21, 'total_batches': 7}`
- **V3（Batch 6 单测 fresh）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q`
  - 结果：`13 passed`
- **V4（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（diff hygiene）**
  - 命令：`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 5.3 任务记录

##### T61 | failing tests 固定 frontend recheck handoff 语义

- **改动范围**：[`tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `020` 的执行基线从 `5 batches / 15 tasks` 扩展为 `7 batches / 21 tasks`，显式放行 Batch 6/7 的 recheck handoff 切片。
  - 新增 service 单测，固定 execute-ready step 必须暴露 frontend recheck handoff、not-ready step 不生成 handoff 的语义。
  - 通过 RED 运行确认旧 `ProgramIntegrationStep` 还没有 handoff truth。
- **新增/调整的测试**：`test_build_integration_dry_run_surfaces_frontend_recheck_handoff_when_ready`、`test_build_integration_dry_run_skips_frontend_recheck_handoff_when_not_ready`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T62 | 实现最小 frontend recheck handoff truth

- **改动范围**：[`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)
- **改动内容**：
  - 新增 `ProgramFrontendRecheckHandoff` 聚合对象，并挂接到 `ProgramIntegrationStep`。
  - execute-ready step 现在会暴露 `required / reason / recommended_commands / source_linkage`。
  - handoff 实现只复用既有 readiness truth，不引入 recheck loop 或 auto-fix runtime。
- **新增/调整的测试**：依赖 `tests/unit/test_program_service.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T63 | fresh verify 并追加 implementation batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 6 的 RED/GREEN 证据、parser 结构校验与 fresh verification 结果。
  - 固化 touched files、验证命令与结论，保持 `020` implementation history append-only。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 5.4 代码审查（Mandatory）

- **宪章/规格对齐**：实现只引入 handoff truth，没有越界到 recheck loop、auto-fix、writeback 或 execute gate 真值重写。
- **代码质量**：recheck handoff 收口在 `ProgramService.build_integration_dry_run()` 的 step payload，保持单一 service source。
- **测试质量**：已完成 RED 验证、full unit file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 5.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步（21 tasks / 7 batches）`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（继续在当前分支进入 Batch 7）`
- 说明：`Batch 6` 已把 frontend recheck handoff 接入 `ProgramService`；下一步转入 execute CLI / report surface。`

#### 5.6 自动决策记录（如有）

- AD-004：recheck handoff 推荐命令先统一为 `uv run ai-sdlc verify constraints`。理由：当前仓库已有稳定 frontend verification 聚合入口，先复用单一 operator-facing recheck command。

#### 5.7 批次结论

- `020` 已具备 execute-ready step 的 frontend recheck handoff truth。
- execute CLI / report 已拥有稳定的 recheck data source，可以继续进入 user-facing surface。

#### 5.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待 Batch 7 合并提交
- **改动范围**：`specs/020-frontend-program-execute-runtime-baseline/plan.md`、`specs/020-frontend-program-execute-runtime-baseline/tasks.md`、`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`
- **是否继续下一批**：是（继续进入 execute CLI / report recheck surface）

### Batch 2026-04-03-005 | 020 Program execute CLI/frontend report recheck surface

#### 6.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T71`、`T72`、`T73`
- **目标**：把 frontend recheck handoff 暴露到 `program integrate --execute` 的终端输出与 report，不引入 recheck loop 或 auto-fix runtime。
- **预读范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：test-driven-development；scoped user-facing surface；verification-before-completion
- **验证画像**：`code-change`

#### 6.2 统一验证命令

- **V1（Batch 7 RED 校验）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q -k "recheck_handoff or execute_success"`
  - 结果：`2 failed`，失败原因为 execute CLI / report 尚未显示 `Frontend Recheck Handoff`，符合预期 RED。
- **V2（Batch 7 集成测试 fresh）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q`
  - 结果：`12 passed`
- **V3（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V4（diff hygiene）**
  - 命令：`git diff --check -- specs/020-frontend-program-execute-runtime-baseline src/ai_sdlc/cli tests/integration`
  - 结果：无输出。
- **V5（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 6.3 任务记录

##### T71 | failing tests 固定 execute CLI / report recheck 输出语义

- **改动范围**：[`tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)
- **改动内容**：
  - 为 execute 成功路径新增 frontend recheck handoff 输出测试，覆盖 CLI section、spec id 与验证命令。
  - 为 execute report 新增 recheck handoff 断言，覆盖 `Frontend Recheck Handoff` 与 `uv run ai-sdlc verify constraints`。
  - 通过 RED 运行确认旧 execute CLI / report 尚未渲染 recheck handoff。
- **新增/调整的测试**：`test_program_integrate_execute_surfaces_frontend_recheck_handoff`、`test_program_integrate_execute_success`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T72 | 实现最小 execute CLI / report recheck surface

- **改动范围**：[`src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)
- **改动内容**：
  - execute gate 通过后新增 `Frontend Recheck Handoff` section。
  - report 输出新增 per-step recheck handoff 细节与全局 `Frontend Recheck Handoff` section。
  - handoff 输出采用稳定的纯文本多行格式，避免窄终端折行导致命令不可见。
- **新增/调整的测试**：依赖 `tests/integration/test_cli_program.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T73 | fresh verify 并追加 CLI batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 7 的 RED/GREEN 证据与 fresh verification 结果。
  - 固化 CLI touched files、验证命令与 user-facing surface 的最小结论。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 6.4 代码审查（Mandatory）

- **宪章/规格对齐**：CLI / report 只暴露 recheck handoff，没有扩张到 recheck loop、auto-fix、writeback 或 scanner/provider 写入。
- **代码质量**：采用 `ProgramService` 的共享 handoff truth；输出格式被收敛为稳定纯文本，不引入第二套业务逻辑。
- **测试质量**：已完成 RED 验证、full integration file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 6.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（当前轮次提交后继续沿用）`
- 说明：`020` 的 execute preflight、recheck handoff 与 CLI/report surface 已打通；后续若继续推进，应进入 remediation runtime / auto-fix 下游工单。`

#### 6.6 自动决策记录（如有）

- AD-005：recheck handoff 在 CLI 中采用独立 section 和纯文本 command 行。理由：比在一行里塞入括号命令更抗折行，也更接近 operator 后续动作。

#### 6.7 批次结论

- `program integrate --execute` 与 execute report 已能直接暴露 frontend recheck handoff。
- `020` 当前的 program-level frontend execute runtime baseline 已形成从 formal docs 到 core/service 再到 execute CLI/report surface 的闭环。

#### 6.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本轮提交生成
- **改动范围**：`specs/020-frontend-program-execute-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`
- **是否继续下一批**：按用户授权连续推进（建议进入 remediation runtime / auto-fix 的下游 child work item）
