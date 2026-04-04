# 021-frontend-program-remediation-runtime-baseline 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/021-frontend-program-remediation-runtime-baseline/` 相关的 formal docs freeze、implementation handoff 或 close-out，都在本文件末尾追加新批次章节。
- 本 work item 的 canonical truth，以 [`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件和当前分支提交链共同为准。
- `021` 是 `020` 之后的 frontend program remediation runtime formal baseline；后续 `src/` / `tests/` 实现应由本工单或其下游切片承接，而不是回写上游 mother spec。

## 2. 批次记录

### Batch 2026-04-03-001 | 021 Frontend program remediation runtime formal baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`、`T12`、`T13`、`T21`、`T22`、`T23`、`T31`、`T32`、`T33`
- **目标**：把 `020` 之后的 program-level frontend remediation runtime 从 downstream suggestion 收敛成独立 child work item，冻结 remediation truth、fix-input packaging、handoff 与 downstream auto-fix handoff。
- **预读范围**：[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/plan.md`](../020-frontend-program-execute-runtime-baseline/plan.md)、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：single canonical truth；docs-only execute；downstream child-work-item first；verification-before-completion
- **验证画像**：`docs-only`

#### 2.2 统一验证命令

- **V1（Batch 1-3 parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/021-frontend-program-remediation-runtime-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 9, 'total_batches': 3, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33']]}`
- **V2（Markdown diff hygiene）**
  - 命令：`git diff --check -- specs/021-frontend-program-remediation-runtime-baseline`
  - 结果：无输出。
- **V3（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 / T13 | 冻结 remediation runtime truth、non-goals 与 remediation source linkage

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 将 `021` 正式定义为 `020` 下游的 frontend program remediation runtime child work item。
  - 锁定 program remediation runtime 只消费 `020` execute/recheck truth 与 `018` fix-input boundary，不新增 program 私有 remediation truth。
  - 锁定 non-goals，包括 scanner/provider 写入、auto-fix、registry、cross-spec writeback 与默认 remediation side effect。
- **新增/调整的测试**：无代码测试；依赖 parser 结构校验与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T21 / T22 / T23 | 冻结 remediation input packaging、handoff 与 downstream auto-fix 边界

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：
  - 明确 remediation input、fix-input packaging 与 operator-facing handoff responsibility。
  - 明确 bounded remediation runtime 不等于完整 auto-fix engine。
  - 明确 writeback / registry 仍由下游工单承接。
- **新增/调整的测试**：无代码测试；依赖文档对账与治理只读校验。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T31 / T32 / T33 | 冻结 implementation handoff 与 docs-only baseline

- **改动范围**：[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件
- **改动内容**：
  - 锁定 `core / cli / tests` 推荐文件面与 ownership 边界。
  - 锁定最小测试矩阵与 remediation runtime 实现前提。
  - 为后续 remediation input / handoff implementation 保留稳定 docs-only baseline。
- **新增/调整的测试**：无代码测试；以本批 docs-only verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只冻结 `021` formal baseline，没有越界到 `program_cmd.py`、`program_service.py` 或 auto-fix runtime 实现。
- **代码质量**：无 `src/` / `tests/` 变更；文档内容围绕 remediation truth、fix-input packaging 与 handoff，不引入第二套 truth。
- **测试质量**：已完成 parser 结构校验、`git diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`已同步`
- 关联 branch/worktree disposition 计划：`retained（沿用当前前端治理连续推进分支）`
- 说明：`021` 当前作为 frontend program remediation runtime 的 docs-only baseline 保留在当前分支上；下一步建议在 021 内进入 remediation input packaging / handoff implementation slice。`

#### 2.6 自动决策记录（如有）

- AD-001：program remediation runtime 单独拆为 `021` child work item，而不是继续扩张 `020`。理由：`020` 已完成 execute/recheck runtime baseline，remediation orchestration 属于新的责任面，应保持独立 formal truth 与测试矩阵。

#### 2.7 批次结论

- `021` 已具备独立可引用的 program-level frontend remediation runtime formal baseline。
- 后续若继续推进，应优先在 `021` 内实现 remediation input packaging 与 CLI/report handoff surface。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待后续提交生成
- **改动范围**：`specs/021-frontend-program-remediation-runtime-baseline/spec.md`、`specs/021-frontend-program-remediation-runtime-baseline/plan.md`、`specs/021-frontend-program-remediation-runtime-baseline/tasks.md`、`specs/021-frontend-program-remediation-runtime-baseline/task-execution-log.md`
- **是否继续下一批**：按用户授权连续推进（优先转入 `021` 的 remediation input packaging / handoff implementation slice）

### Batch 2026-04-03-002 | 021 Program remediation input packaging

#### 3.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T41`、`T42`、`T43`
- **目标**：在 `ProgramService` 中为 frontend-not-ready integration steps 暴露 remediation input / fix-input packaging，保持 packaging-only，不进入 auto-fix 或 writeback runtime。
- **预读范围**：[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`
- **激活的规则**：test-driven-development；single canonical truth；packaging-only；verification-before-completion
- **验证画像**：`code-change`

#### 3.2 统一验证命令

- **V1（Batch 4 RED 校验）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q -k "frontend_remediation_input"`
  - 结果：`2 failed, 13 deselected`，失败原因为 `ProgramIntegrationStep` 尚未暴露 `frontend_remediation_input` 字段，符合预期 RED。
- **V2（021 tasks parser 结构校验）**
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.generators.doc_gen import TasksParser; plan = TasksParser().parse(Path('specs/021-frontend-program-remediation-runtime-baseline/tasks.md')); print({'total_tasks': plan.total_tasks, 'total_batches': plan.total_batches, 'batches': [batch.tasks for batch in plan.batches]})"`
  - 结果：`{'total_tasks': 15, 'total_batches': 5, 'batches': [['T11', 'T12', 'T13'], ['T21', 'T22', 'T23'], ['T31', 'T32', 'T33'], ['T41', 'T42', 'T43'], ['T51', 'T52', 'T53']]}`
- **V3（Batch 4 单测 fresh）**
  - 命令：`uv run pytest tests/unit/test_program_service.py -q`
  - 结果：`15 passed`
- **V4（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V5（diff hygiene）**
  - 命令：`git diff --check -- specs/021-frontend-program-remediation-runtime-baseline src/ai_sdlc/core tests/unit`
  - 结果：无输出。
- **V6（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 3.3 任务记录

##### T41 | failing tests 固定 remediation input packaging 语义

- **改动范围**：[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)
- **改动内容**：
  - 将 `021` 从 docs-only baseline 扩展为 `5 batches / 15 tasks`，显式放行 Batch 4/5 的 implementation slices。
  - 新增 service 单测，固定 frontend not-ready step 必须暴露 remediation input、frontend ready step 不生成 remediation input。
  - 通过 RED 运行确认旧 `ProgramIntegrationStep` 还没有 remediation packaging truth。
- **新增/调整的测试**：`test_build_integration_dry_run_surfaces_frontend_remediation_input_when_not_ready`、`test_build_integration_dry_run_skips_frontend_remediation_input_when_ready`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T42 | 实现最小 remediation input / fix-input packaging

- **改动范围**：[`src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)
- **改动内容**：
  - 新增 `ProgramFrontendRemediationInput` 聚合对象，并挂接到 `ProgramIntegrationStep`。
  - frontend not-ready step 现在会暴露 `state / fix_inputs / blockers / suggested_actions / source_linkage`。
  - remediation payload 只复用既有 readiness / gate truth，保持 packaging-only，不引入 auto-fix、writeback 或 provider runtime。
- **新增/调整的测试**：依赖 `tests/unit/test_program_service.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T43 | fresh verify 并追加 implementation batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 4 的 RED/GREEN 证据、`021` parser 结构校验与 fresh verification 结果。
  - 固化 remediation packaging touched files、验证命令与结论，保持 implementation history append-only。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 3.4 代码审查（Mandatory）

- **宪章/规格对齐**：实现只新增 remediation input packaging truth，没有越界到 auto-fix、writeback、provider runtime 或 execute gate 真值重写。
- **代码质量**：remediation input 收口在 `ProgramService.build_integration_dry_run()` 的 step payload，保持单一 service source。
- **测试质量**：已完成 RED 验证、full unit file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 3.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步（15 tasks / 5 batches）`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（继续在当前分支进入 Batch 5）`
- 说明：`Batch 4` 已把 remediation input packaging 接入 `ProgramService`；下一步转入 execute CLI / report remediation handoff surface。`

#### 3.6 自动决策记录（如有）

- AD-002：`fix_inputs` 默认优先复用 readiness 的 `coverage_gaps`，为空时才回退到 readiness `state`。理由：program remediation input 需要优先暴露可操作的 gap truth，而不是退化成抽象状态字符串。

#### 3.7 批次结论

- `021` 已具备 frontend not-ready step 的 remediation input / fix-input packaging truth。
- execute CLI / report 已拥有稳定的 remediation data source，可以继续进入 operator-facing handoff surface。

#### 3.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待 Batch 5 合并提交
- **改动范围**：`specs/021-frontend-program-remediation-runtime-baseline/plan.md`、`specs/021-frontend-program-remediation-runtime-baseline/tasks.md`、`specs/021-frontend-program-remediation-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`
- **是否继续下一批**：是（继续进入 execute CLI / report remediation handoff surface）

### Batch 2026-04-03-003 | 021 Program execute CLI/frontend report remediation surface

#### 4.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T51`、`T52`、`T53`
- **目标**：把 remediation input / suggested actions 暴露到 `program integrate --execute` 的失败路径和 report 中，让 operator 能直接看到 bounded remediation handoff。
- **预读范围**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`、`src/ai_sdlc/core/program_service.py`
- **激活的规则**：test-driven-development；scoped user-facing surface；no auto-fix side effect；verification-before-completion
- **验证画像**：`code-change`

#### 4.2 统一验证命令

- **V1（Batch 5 RED 校验）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q -k "remediation_handoff"`
  - 结果：`2 failed, 12 deselected`，失败原因为 execute CLI / failure report 尚未显示 `Frontend Remediation Handoff`，符合预期 RED。
- **V2（Batch 5 集成测试 fresh）**
  - 命令：`uv run pytest tests/integration/test_cli_program.py -q`
  - 结果：`14 passed`
- **V3（lint）**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **V4（diff hygiene）**
  - 命令：`git diff --check -- specs/021-frontend-program-remediation-runtime-baseline src/ai_sdlc/cli tests/integration`
  - 结果：无输出。
- **V5（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 4.3 任务记录

##### T51 | failing tests 固定 remediation handoff 输出语义

- **改动范围**：[`tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)
- **改动内容**：
  - 为 execute 失败路径新增 remediation handoff 输出测试，覆盖 section 标题与最小 suggested actions。
  - 为 execute failure report 新增 remediation handoff 断言，覆盖 `Frontend Remediation Handoff` 与 `re-run ai-sdlc verify constraints`。
  - 通过 RED 运行确认 execute CLI / report 尚未渲染 remediation handoff。
- **新增/调整的测试**：`test_program_integrate_execute_surfaces_frontend_remediation_handoff`、`test_program_integrate_execute_failure_report_surfaces_remediation_handoff`
- **测试结果**：RED 阶段符合预期。
- **是否符合任务目标**：符合。

##### T52 | 实现最小 execute CLI / report remediation handoff surface

- **改动范围**：[`src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)
- **改动内容**：
  - execute gates failed 时新增独立 `Frontend Remediation Handoff` section，按 spec 粒度暴露 remediation state 与 suggested actions。
  - execute report 新增全局 remediation handoff section，复用同一组 remediation payload。
  - user-facing surface 只增强 operator 可见性，不触发 auto-fix、writeback 或 provider runtime。
- **新增/调整的测试**：依赖 `tests/integration/test_cli_program.py` fresh 结果。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T53 | fresh verify 并追加 CLI batch 归档

- **改动范围**：[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 记录 Batch 5 的 RED/GREEN 证据与 fresh verification 结果。
  - 固化 CLI touched files、验证命令与 remediation handoff surface 的最小结论。
- **新增/调整的测试**：无新增测试；以本批 verification 命令为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 4.4 代码审查（Mandatory）

- **宪章/规格对齐**：CLI / report 只暴露 remediation handoff，没有扩张到 auto-fix、writeback、scanner/provider 写入或新的 execute truth。
- **代码质量**：report 与终端输出共用同一 remediation payload formatting，保持 `ProgramService` 为单一数据源。
- **测试质量**：已完成 RED 验证、full integration file、`ruff`、`diff --check` 与 `verify constraints` fresh 校验。
- **结论**：`无 Critical 阻塞项`

#### 4.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步（15 tasks / 5 batches）`
- `plan.md` 同步状态：`已同步`
- `spec.md` 同步状态：`无需修改`
- 关联 branch/worktree disposition 计划：`retained（当前轮次提交后继续沿用）`
- 说明：`021` 已形成 docs -> service packaging -> execute CLI/report remediation handoff 的闭环；下游若继续推进，应拆 bounded remediation runtime / auto-fix child work item。`

#### 4.6 自动决策记录（如有）

- AD-003：remediation handoff 先落在 execute failure path 与 report summary，而不是每个 step 的冗长明细。理由：当前阶段目标是给 operator 最小可执行的 remediation next actions，不把 report 扩成新的 remediation planner。

#### 4.7 批次结论

- `program integrate --execute` 失败路径已能直接暴露 frontend remediation handoff。
- `021` 当前的 frontend remediation runtime baseline 已形成从 formal docs 到 service payload 再到 execute CLI/report surface 的闭环。

#### 4.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本轮提交生成
- **改动范围**：`specs/021-frontend-program-remediation-runtime-baseline/task-execution-log.md`、`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`
- **是否继续下一批**：按用户授权连续推进（建议下游拆 bounded remediation runtime / auto-fix child work item）

### Batch 2026-04-04-004 | frontend close-check evidence remediation

#### 1. 准备

- **任务来源**：`框架总览复核 / frontend close-check evidence remediation`
- **目标**：为 `021-frontend-program-remediation-runtime-baseline` 补齐最新 canonical close-out batch，使 execution log 满足当前框架的 `workitem close-check` 字段契约，不改动已冻结的实现边界。
- **预读范围**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`src/ai_sdlc/core/close_check.py`
- **激活的规则**：close-check execution log fields；verification profile truthfulness；git close-out markers truthfulness。
- **验证画像**：`docs-only`
- **改动范围**：`specs/021-frontend-program-remediation-runtime-baseline/task-execution-log.md`

#### 2. 统一验证命令

- **V1（治理只读校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 3. 任务记录

##### Task close-out | 追加 canonical evidence batch

- **改动范围**：`specs/021-frontend-program-remediation-runtime-baseline/task-execution-log.md`
- **改动内容**：
  - 追加符合当前框架的最新 `### Batch ...` 正式批次结构，补齐 `统一验证命令`、`代码审查`、`任务/计划同步状态`、`验证画像` 与 git close-out markers。
  - 保留既有历史执行记录，不改写旧批次；本批只作为最新 canonical close-out evidence。
  - 不新增产品实现，不放宽 `021-frontend-program-remediation-runtime-baseline` 已冻结的功能边界。
- **新增/调整的测试**：无。本批仅做 docs-only 收口证据回填。
- **执行的命令**：见 V1。
- **测试结果**：`uv run ai-sdlc verify constraints` 通过；其余 `workitem close-check` 复核在真实 git close-out 后统一执行。
- **是否符合任务目标**：符合。

#### 4. 代码审查（摘要）

- **宪章/规格对齐**：本批只补 execution evidence schema，不更改 `021-frontend-program-remediation-runtime-baseline` 的 spec / plan / task 合同语义。
- **代码质量**：无运行时代码变更。
- **测试质量**：`docs-only` 批次已记录 `uv run ai-sdlc verify constraints`；最终完成态仍以真实 git close-out 后的 `workitem close-check` 复核为准。
- **结论**：允许继续执行真实 git close-out。

#### 5. 任务/计划同步状态

- `tasks.md` 同步状态：`已对账`
- `plan.md` 同步状态：`已对账`
- `spec.md` 同步状态：`已对账`

#### 6. 批次结论

- `021-frontend-program-remediation-runtime-baseline` 当前补齐的是 close-out evidence schema；实现边界保持不变，最终 pass 仍依赖真实 git close-out 后复核。

#### 7. 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：待本批真实提交后补录
- **是否继续下一批**：是；下一步执行真实 git close-out，并复跑 `workitem close-check`
