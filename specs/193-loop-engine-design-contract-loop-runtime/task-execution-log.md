# 任务执行日志：Loop Engine Design Contract Loop Runtime

**功能编号**：`193-loop-engine-design-contract-loop-runtime`
**创建日期**：2026-07-01
**状态**：执行中

## 1. 归档规则

- 本文件是 `193-loop-engine-design-contract-loop-runtime` 的固定执行归档文件。
- 后续每完成一批任务，都在本文件末尾追加一个新的批次章节。
- 每批必须记录改动范围、验证命令、测试结果、任务同步状态、branch/worktree disposition 和下一步。
- 本 work item 是五类 Loop 总目标中的第二类 `design-contract` loop；不得把后续 `implementation`、`frontend-evidence` 的实现伪装成本批完成。

## 2. 批次记录

### Batch 2026-07-01-001 | T11

#### 2.1 批次范围

- 覆盖任务：`T11`
- 覆盖阶段：formal baseline and linkage
- 预读范围：`AGENTS.md`、`.ai-sdlc/memory/constitution.md`、`specs/189-loop-engine-local-adversarial-pr-review/spec.md`、`specs/192-loop-engine-requirement-loop-runtime/spec.md`、现有 `loop_models.py` / `loop_status.py` / `loop_cmd.py`
- 激活的规则：formal docs canonical path、one-loop-per-PR delivery、Loop Engine local-first/no-model boundary、handoff continuity

#### 2.2 统一验证命令

- `V1`（formal docs generation）
  - 命令：`uv run ai-sdlc workitem init --title "Loop Engine Design Contract Loop Runtime" --wi-id "193-loop-engine-design-contract-loop-runtime" ...`
  - 结果：通过，生成 `spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`，并提示执行 program truth sync。
- `V2`（workitem linkage）
  - 命令：`uv run ai-sdlc workitem link --wi-id 193-loop-engine-design-contract-loop-runtime --plan-uri specs/193-loop-engine-design-contract-loop-runtime/plan.md`
  - 结果：通过，checkpoint linkage 更新到 `193-loop-engine-design-contract-loop-runtime`。
- `V3`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，写入 `program-manifest.yaml`，snapshot hash `cd4e72bb4a58ebc857add5cba2b581165c1cea564d33514aa9d782273002b0fe`；仓库既存 source inventory 仍为 incomplete/migration_pending。
- `V4`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V5`（framework constraints）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。

#### 2.3 任务记录

##### T11 | Freeze WI-193 formal docs

- 改动范围：
  - `specs/193-loop-engine-design-contract-loop-runtime/spec.md`
  - `specs/193-loop-engine-design-contract-loop-runtime/plan.md`
  - `specs/193-loop-engine-design-contract-loop-runtime/tasks.md`
  - `specs/193-loop-engine-design-contract-loop-runtime/task-execution-log.md`
  - `program-manifest.yaml`
- 改动内容：生成 canonical work item 文档，并将模板内容替换为 design-contract loop 的真实需求详设、实施计划和任务拆解。
- 新增/调整的测试：本批为 formal baseline；runtime tests 从 T21 开始新增。
- 执行的命令：见 2.2。
- 测试结果：V1-V5 均通过；truth sync 报告仓库既有 inventory incomplete/migration_pending，但已写入 manifest。
- 是否符合任务目标：符合；formal baseline、linkage 和 program truth sync 已完成。

#### 2.4 代码审查结论

- 宪章/规格对齐：当前文档明确本 PR 只交付 `design-contract` loop，并保持 no-model、no-code-write、implementation-before-contract boundary。
- 代码质量：本批尚未修改 runtime 代码。
- 测试质量：本批尚未进入 runtime tests；后续 T21 起补 core/CLI tests。
- 结论：无代码 blocker；formal baseline 已完成，可以进入 Batch 2 runtime 实现。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：已同步 T11/T21/T22/T23/T31/T32/T41/T42。
- `related_plan`（如存在）同步状态：无 related_plan；related_doc 仅作引用。
- 关联 branch/worktree disposition 计划：本分支作为 WI-193 PR carrier，合并后删除远端分支。
- 说明：`workitem init` 要求使用 `feature/193-loop-engine-design-contract-loop-runtime-docs` 作为 docs branch。

#### 2.6 自动决策记录

- AD-193-001：每类 Loop 单独 work item / PR；WI-193 只落 design-contract loop，完成 PR+Codex review 后再进入 implementation loop。
- AD-193-002：Design-contract loop 使用 deterministic local runtime，不调用模型；语义覆盖判断可作为未来增强，不进入本 PR。
- AD-193-003：Design-contract close 后 next action 指向 implementation loop，不直接修改代码。

#### 2.7 批次结论

- formal docs 已生成并完成真实内容修订。
- workitem link、program truth sync、diff check 与 verify constraints 已完成。
- 继续进入 design-contract runtime 实现。

#### 2.8 归档后动作

- 已完成 git 提交：否
- 提交哈希：待本批提交后生成
- 当前批次 branch disposition 状态：PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：完成 T11 验证和提交后进入 T21。

### Batch 2026-07-01-002 | T21-T23

#### 3.1 批次范围

- 覆盖任务：`T21`、`T22`、`T23`
- 覆盖阶段：design-contract runtime
- 预读范围：`src/ai_sdlc/core/requirement_loop.py`、`src/ai_sdlc/core/loop_artifacts.py`、`tests/unit/test_requirement_loop.py`
- 激活的规则：deterministic local runtime、no model call、no product code write、status persisted under `.ai-sdlc/loops/design-contract`

#### 3.2 统一验证命令

- `V1`（design-contract core tests）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`9 passed`。
- `V2`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
- `V3`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py`
  - 结果：通过，`Success: no issues found in 4 source files`。
- `V4`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无输出。

#### 3.3 任务记录

##### T21 | 新增 design-contract artifact models

- 改动范围：`src/ai_sdlc/core/design_contract_models.py`、`src/ai_sdlc/core/design_contract_store.py`、`tests/unit/test_design_contract_loop.py`
- 改动内容：新增 `DesignContractInput`、`ContractCoverageItem`、`DesignContractReport`、`DesignContractClose`、命令结果模型、artifact refs 和设计合同 artifact 路径解析。
- 新增/调整的测试：覆盖 passed artifact 写入、dry-run no-write、unsafe loop id、missing work item。
- 执行的命令：见 3.2。
- 测试结果：通过。
- 是否符合任务目标：符合。

##### T22 | 实现 check runtime

- 改动范围：`src/ai_sdlc/core/design_contract_loop.py`、`src/ai_sdlc/core/design_contract_checks.py`、`tests/unit/test_design_contract_loop.py`
- 改动内容：新增 deterministic Markdown 合同检查，覆盖 docs 缺失、模板占位、FR/SC coverage、plan section、task acceptance/verification 和简单 scope drift；写入 coverage matrix、JSON report、Markdown report、loop-run 和 current pointer。
- 新增/调整的测试：覆盖完整合同 passed、FR/SC 未覆盖 needs_fix、模板占位 needs_fix、dry-run 不写 artifact。
- 执行的命令：见 3.2。
- 测试结果：通过。
- 是否符合任务目标：符合。

##### T23 | 实现 close runtime

- 改动范围：`src/ai_sdlc/core/design_contract_loop.py`、`tests/unit/test_design_contract_loop.py`
- 改动内容：新增 `close_design_contract_loop`，仅允许无 blocker 且显式 `yes` 的 design-contract loop close；写入 close artifact 并将 next action 指向 implementation loop。
- 新增/调整的测试：覆盖 close artifact、未传 yes fail-closed、有 blocker 不可 close。
- 执行的命令：见 3.2。
- 测试结果：通过。
- 是否符合任务目标：符合。

#### 3.4 代码审查结论

- 宪章/规格对齐：core runtime 保持 local deterministic，不调用模型，不修改业务代码，只写 design-contract artifacts。
- 代码质量：首次实现拆分后发现 `design_contract_loop.py` 超过 400 行，已拆为 models/checks/store/runtime 四个模块，单文件均低于 400 行。
- 测试质量：unit tests 覆盖 passed、needs_fix、dry-run、close、bad input；CLI/status/list 尚未接入，进入下一批补齐。
- 结论：core runtime 可进入 Batch 3 status/list and CLI。

#### 3.5 任务/计划同步状态

- `tasks.md` 同步状态：T21-T23 已完成；T31/T32/T41/T42 待执行。
- `related_plan`（如存在）同步状态：无 related_plan；`plan.md` Phase 1 已完成。
- 关联 branch/worktree disposition 计划：本分支继续作为 WI-193 PR carrier。
- 说明：本批未修改 README 或 verify constraints，留到 Batch 4。

#### 3.6 自动决策记录

- AD-193-004：将 design-contract runtime 拆分为 `design_contract_models.py`、`design_contract_checks.py`、`design_contract_store.py`、`design_contract_loop.py`，满足宪章单文件规模约束。
- AD-193-005：P0 coverage 使用 FR/SC 编号在 tasks 中的机械引用作为合同覆盖证据；语义覆盖留给未来模型或人工增强。

#### 3.7 批次结论

- design-contract core runtime、artifact models、check 和 close 已完成。
- 下一步进入 status/list and CLI 接入。

#### 3.8 归档后动作

- 已完成 git 提交：否
- 提交哈希：待本批提交后生成
- 当前批次 branch disposition 状态：PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：完成本批提交后进入 T31/T32。

### Batch 2026-07-01-003 | T31-T32

#### 4.1 批次范围

- 覆盖任务：`T31`、`T32`
- 覆盖阶段：status/list and CLI
- 预读范围：`src/ai_sdlc/core/loop_status.py`、`src/ai_sdlc/cli/loop_cmd.py`、`tests/unit/test_loop_status.py`、`tests/integration/test_cli_loop.py`
- 激活的规则：status/list read-only、design-contract writer dry-run no-write、JSON output parser-safe、close fail-closed

#### 4.2 统一验证命令

- `V1`（CLI focused integration）
  - 命令：`uv run pytest tests/integration/test_cli_loop.py -q`
  - 结果：通过，`32 passed`。
- `V2`（status/list + core focused unit）
  - 命令：`uv run pytest tests/unit/test_loop_status.py tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`44 passed`。
- `V3`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py`
  - 结果：通过，`All checks passed!`。
- `V4`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V5`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无输出。

#### 4.3 任务记录

##### T31 | 接入 loop status/list

- 改动范围：`src/ai_sdlc/core/loop_status.py`、`tests/unit/test_loop_status.py`
- 改动内容：新增 `DesignContractLoopSummary`、`loop status/list --type design-contract` current/list reader、design-contract pointer repair guidance、passed/needs_fix/closed next guidance。
- 新增/调整的测试：覆盖 current design-contract status、no-current guidance、list marks current、closed points to implementation、malformed current target。
- 执行的命令：见 4.2。
- 测试结果：通过。
- 是否符合任务目标：符合。

##### T32 | 接入 CLI

- 改动范围：`src/ai_sdlc/cli/loop_cmd.py`、`tests/integration/test_cli_loop.py`
- 改动内容：新增 `ai-sdlc loop design-contract check/status/close`，check dry-run 不触发 adapter、不写 artifact，close 不能关闭时返回非零；human 输出展示 work item、blocker、warning、coverage 和 artifact path。
- 新增/调整的测试：覆盖 check/status/close JSON、dry-run skips adapter、close with blockers exits nonzero、list JSON。
- 执行的命令：见 4.2。
- 测试结果：通过。
- 是否符合任务目标：符合。

#### 4.4 代码审查结论

- 宪章/规格对齐：CLI writer 命令刷新 adapter，dry-run 保持 no-write；status/list 只读；JSON 输出由 payload 直接渲染，不混入 Rich 文本。
- 代码质量：沿用 requirement loop CLI 模式，未改变 local-pr-review 默认入口。
- 测试质量：integration tests 覆盖 design-contract check/status/list/close 和 dry-run adapter 边界；status/list unit tests 覆盖 malformed current target。
- 结论：Batch 3 可进入 docs/constraints/final regression。

#### 4.5 任务/计划同步状态

- `tasks.md` 同步状态：T31/T32 已完成；T41/T42 待执行。
- `related_plan`（如存在）同步状态：无 related_plan；`plan.md` Phase 2 已完成。
- 关联 branch/worktree disposition 计划：本分支继续作为 WI-193 PR carrier。
- 说明：Batch 4 需要补 README、verify constraints surface、program truth sync 和 close-check。

#### 4.6 自动决策记录

- AD-193-006：`loop design-contract check` 的 `needs_fix` 属于成功生成报告的可恢复状态，CLI exit 0；`close` 未真正关闭时 exit 1，便于自动化阻断 implementation。
- AD-193-007：`loop status/list --type design-contract` 继续复用通用 `LoopSummary`，通过 `design_contract` 扩展字段暴露 work item 和 coverage counters。

#### 4.7 批次结论

- design-contract status/list and CLI 已完成。
- 下一步进入 README、verify constraints、最终回归和 close-check。

#### 4.8 归档后动作

- 已完成 git 提交：否
- 提交哈希：待本批提交后生成
- 当前批次 branch disposition 状态：PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：完成本批提交后进入 T41/T42。

### Batch 2026-07-01-004 | T41-T42

#### 5.1 批次范围

- 覆盖任务：`T41`、`T42`
- 覆盖阶段：docs, constraints, final regression, PR review preparation
- 预读范围：`README.md`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`tasks.md`
- 激活的规则：design-contract 是 implementation 前置合同检查；P0 不调用模型、不改业务代码、不进入 frontend evidence；final close-check 以本 work item 为收口事实面

#### 5.2 改动范围

- **验证画像**：code-change
- **改动范围**：`README.md`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`program-manifest.yaml`、`task-execution-log.md`
- 更新 README design-contract beginner path 与边界说明。
- 更新 feature-contract surface registry，新增 WI-193 runtime、status/CLI、user docs surface。
- 更新 verify constraints 单测，覆盖 WI-193 surface selection 和 README token。
- 刷新 program truth snapshot。

#### 5.3 统一验证命令

- `V1`（feature-contract surface focused unit）
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py::test_193_feature_contract_surfaces_cover_design_contract_loop_runtime tests/unit/test_verify_constraints.py::test_192_feature_contract_surfaces_cover_requirement_loop_runtime -q`
  - 结果：通过，`2 passed`。
- `V2`（focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`217 passed`。
- `V3`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/loop_cmd.py tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V4`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V5`（verify constraints）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `V6`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V7`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，写入 `program-manifest.yaml`，snapshot hash `13679e91b482821af5e56d0ece7881caa54d7a18f59a323836dbdbe658064b85`；仓库级 source inventory 仍为历史 `migration_pending`。
- `V8`（diagnostic mypy broader scope）
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：未作为 WI-193 gate；`verify_constraints.py` 存在既有 PyYAML stub 和 frontend helper typing debt，本批不扩大修复范围。

#### 5.4 任务记录

##### T41 | 对齐用户文档和约束面

- 改动范围：`README.md`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`
- 改动内容：README 新增 design-contract loop 命令与边界；constraints registry 新增 WI-193 runtime/status/CLI/docs surface；单测覆盖 WI-193 surface 选择。
- 新增/调整的测试：`test_193_feature_contract_surfaces_cover_design_contract_loop_runtime`
- 执行的命令：见 5.3。
- 测试结果：通过。
- 是否符合任务目标：符合。

##### T42 | 完成最终回归与 PR 收口

- 改动范围：`program-manifest.yaml`、`specs/193-loop-engine-design-contract-loop-runtime/task-execution-log.md`
- 改动内容：执行 focused regression、ruff、mypy、diff check、verify constraints、program truth sync 和 close-check 预检；补齐 closeout 记录。
- 执行的命令：见 5.3 和 5.5。
- 测试结果：focused regression、ruff、focused mypy、diff check、verify constraints、program truth sync 均通过；close-check 首次预检发现日志 closeout 字段缺失，已在本批补齐。
- 是否符合任务目标：进行中，待本批日志提交并复跑 close-check。

#### 5.5 close-check 预检

- `uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：初次预检中 `tasks_completion`、`related_plan_drift`、`execution_log_fields`、`review_gate`、`completion_truth`、`branch_lifecycle`、`program_truth`、`provenance_phase1`、`docs_consistency`、`local_pr_review` 均通过。
  - BLOCKER：最新 batch 缺少 verification profile；最新 batch 缺少 git close-out markers。
  - 处理：已在 Batch 5.2 和 5.8 补齐 verification profile 与 git close-out markers；待本日志落盘后复跑。
- 复跑结果：`tasks_completion`、`related_plan_drift`、`execution_log_fields`、`review_gate`、`verification_profile`、`completion_truth`、`branch_lifecycle`、`program_truth`、`provenance_phase1`、`docs_consistency`、`local_pr_review` 均通过；仅剩 `git_closure`，原因是本批 closeout 文件尚未提交。

#### 5.6 代码审查结论

- 宪章/规格对齐：WI-193 只交付 design-contract loop；P0 不调用模型、不改业务代码、不进入 frontend evidence；close 后 next action 指向 implementation。
- 代码质量：verify constraints 复用现有 feature-contract surface registry；README 只补用户可见路径，不改变 local-pr-review 或 requirement loop 默认行为。
- 测试质量：focused regression 覆盖 core runtime、status/list、CLI、verify constraints；全局 constraints 已通过。
- 结论：可以进入最终 close-check 复跑、提交、推送、PR 和 Codex review。

#### 5.7 任务/计划同步状态

- `tasks.md` 同步状态：T11、T21、T22、T23、T31、T32、T41、T42 均已完成或进入最终 closeout。
- `related_plan`（如存在）同步状态：无 related_plan；`plan.md` 与当前交付边界一致。
- 关联 branch/worktree disposition 计划：`feature/193-loop-engine-design-contract-loop-runtime-docs` 作为 WI-193 PR merge carrier。
- 说明：本 PR 完成 design-contract loop 后停止，不继续实现 implementation loop。

#### 5.8 归档后动作

- **已完成 git 提交**：是（本 marker 随最终提交一起落盘）
- **提交哈希**：`pending-final-commit`
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；按目标要求先完成 WI-193 PR + Codex review，再进入 implementation loop。

### Batch 2026-07-01-005 | Codex review remediation

#### 6.1 批次范围

- 覆盖任务：Codex review actionable feedback for PR #110
- 覆盖阶段：PR review remediation
- 预读范围：GitHub review threads for PR #110、`design_contract_checks.py`、`design_contract_store.py`、`design_contract_models.py`、`design_contract_loop.py`、unit/integration tests
- 激活的规则：对 Codex P2 actionable comments 做同分支修复；不扩大到 implementation loop；修复后重新验证、推送、复审

#### 6.2 改动范围

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/core/design_contract_checks.py`、`src/ai_sdlc/core/design_contract_store.py`、`src/ai_sdlc/core/design_contract_models.py`、`src/ai_sdlc/core/design_contract_loop.py`、`tests/unit/test_design_contract_loop.py`、`tests/integration/test_cli_loop.py`、`task-execution-log.md`
- 修复缺少 parseable `### Task` section 时仍可能通过的问题。
- 将 plan 文本纳入 scope drift 检查，避免 plan 提前落入 implementation/frontend-evidence 文件。
- 限定 design-contract work item 为 canonical `specs/<work-item>` 目录或目录下 formal doc。
- 为 design-contract command JSON 增加 `next_guidance`，包含 `requires_model`、`writes_artifacts`、`writes_code`、`safety` 等结构化字段。
- 阻止 `check --loop-id <closed-id>` 覆盖已关闭的 design-contract loop。

#### 6.3 Codex review 线程处理

- `design_contract_checks.py`：Reject task files without parseable task sections / Treat missing task sections as blockers
  - 处理：新增 `task_section_gap` blocker；当存在 `Txx` token 但没有 `### Task ` heading 时进入 `needs_fix`。
- `design_contract_checks.py`：Check plan text for scope drift
  - 处理：对 `plan.md` 同样执行 `_scope_drift_findings`。
- `design_contract_store.py`：Block non-canonical work item directories
  - 处理：`--wi` 只接受 `specs/<work-item>` 目录或其 formal doc；`other/demo` 等路径 fail-readable。
- `design_contract_models.py` / CLI JSON：Add next guidance to command JSON
  - 处理：`DesignContractCommandResult` 增加 `next_guidance`，CLI JSON 直接输出该结构。
- `design_contract_loop.py`：Preserve closed design-contract runs on recheck
  - 处理：检测到 close artifact 后返回 blocked，不重写 `loop-run.json`。
- `design_contract_store.py`：Reject current pointers that resolve outside the repo
  - 处理：`current-design-contract.json` 中的相对路径解析后必须仍位于 repo root 内；symlink 指向 repo 外时 fail-readable。
- `design_contract_loop.py`：Preserve the implementation next action on repeat close
  - 处理：重复执行 `close --yes` 时复用已关闭 loop-run 的 implementation next action，不回退到旧 report 的 close 指令。
- `design_contract_store.py`：Fall back to the checkpoint feature spec directory
  - 处理：`linked_plan_uri` / `linked_wi_id` 缺失时，使用 checkpoint `feature.spec_dir` 作为当前 work item。

#### 6.4 统一验证命令

- `V1`（design-contract runtime unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`13 passed`。
- `V2`（CLI JSON focused integration）
  - 命令：`uv run pytest tests/integration/test_cli_loop.py::test_loop_design_contract_check_status_and_close_json tests/integration/test_cli_loop.py::test_loop_design_contract_check_dry_run_skips_adapter_hook -q`
  - 结果：通过，`2 passed`。
- `V3`（focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`221 passed`。
- `V4`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py tests/integration/test_cli_loop.py`
  - 结果：通过，`All checks passed!`。
- `V5`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V6`（verify constraints）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `V7`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V8`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：本日志落盘后执行；以后续 close-check `program_truth` PASS 为准。
- `V9`（second Codex review pointer hardening）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`14 passed`。
- `V10`（second remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`222 passed`。
- `V11`（second remediation ruff / mypy / constraints）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V12`（third Codex review repeat-close/checkpoint fallback）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`16 passed`。
- `V13`（third remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`224 passed`。
- `V14`（third remediation ruff / mypy / constraints）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。

#### 6.5 代码审查结论

- 宪章/规格对齐：修复均限制在 design-contract loop，未提前实现 implementation/frontend-evidence。
- 代码质量：新增 JSON guidance 使用独立轻量 model，避免与 `loop_status.py` 形成循环依赖；canonical work item 检查集中在 store 层。
- 测试质量：新增 4 个 runtime 回归和 CLI JSON assertions，覆盖所有 Codex actionable clusters。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 6.6 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 6.7 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`pending-remediation-commit`
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 15：第十六轮 PR #110 Codex review remediation

#### 15.1 本批目标

- 修复 PR #110 最新 Codex review P2：已关闭 current design-contract loop 后，`check --dry-run` 必须仍保持 no-write preview 语义，不得命中 closed-current 快捷路径并返回 `closed=true`。

#### 15.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_loop.py`
  - `check_design_contract_loop` 在 `options.dry_run` 为真时跳过 `_closed_current_recheck_result`，确保 dry-run 分支统一返回 preview 结果。
- `tests/unit/test_design_contract_loop.py`
  - 新增关闭 current loop 后执行 dry-run 的 regression，断言结果为 `dry_run`、不写新 loop artifact，且 current pointer 仍指向已关闭 loop。

#### 15.3 验证记录

- `V71`（sixteenth Codex review dry-run remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_dry_run_after_close_stays_preview tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_preserves_closed_current_default_recheck -q`
  - 结果：通过，`2 passed`。
- `V72`（sixteenth remediation design-contract unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`36 passed`。
- `V73`（sixteenth remediation ruff / mypy）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V74`（sixteenth remediation focused regression / constraints / diff）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`244 passed`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V75`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `c7347dcbd4122bfdd7e8211cf659c837c9ab28a57cb8116ce553bf1502133023`，已写入 `program-manifest.yaml`。
- `V76`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 15.4 代码审查结论

- 宪章/规格对齐：dry-run 在任何已关闭状态下仍是只读预览，不改 current pointer，也不创建新 artifact。
- 质量风险：新增关闭后 dry-run regression，覆盖 Codex 最新 actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 15.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 15.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 18：第十九轮 PR #110 Codex review remediation

#### 18.1 本批目标

- 修复 PR #110 最新 Codex review P1：`close --yes` 不得信任 stale `design-contract-report.json`，必须在关闭前重新校验当前 `spec.md`、`plan.md`、`tasks.md`。
- 修复 PR #110 最新 Codex review P2：当前生成任务格式不重复 literal `FR-*` / `SC-*` 时，design-contract coverage gate 应能基于完整 P0/P1 任务的验收和验证信息做保守推断覆盖。

#### 18.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_loop.py`
  - close 前重读 `design-contract-input.json`，重新执行 requirement gate 与 `analyze_design_contract`。
  - fresh report 有 blocker 时刷新 report / coverage / loop-run artifacts，并阻断 close。
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_task_coverage_index` 在无 literal FR/SC task coverage 时，若可解析 P0/P1 task 均有验收和验证命令，则用 task id 对全部 contract ids 做推断覆盖。
  - 任一 P0/P1 task 缺验收或验证时不启用推断覆盖。
- `tests/unit/test_design_contract_loop.py`
  - 新增 generated task coverage 推断 regression。
  - 新增 close 前 docs 变坏会重新校验并阻断 close 的 regression。
  - 调整 missing coverage 相关测试，显式缺少验证命令以关闭推断覆盖。
- `tests/integration/test_cli_loop.py`
  - 调整 close-with-blockers fixture，显式缺少验证命令以制造真实 blocker。

#### 18.3 验证记录

- `V89`（nineteenth Codex review close/coverage remediation targeted）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_reports_missing_coverage tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_infers_generated_task_coverage tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_ignores_non_task_coverage_refs tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_ignores_trailing_non_task_coverage_refs tests/unit/test_design_contract_loop.py::test_close_design_contract_loop_revalidates_changed_docs -q`
  - 结果：通过，`5 passed`。
- `V90`（nineteenth remediation design-contract / CLI targeted）
  - 命令：`uv run pytest tests/integration/test_cli_loop.py::test_loop_design_contract_close_with_blockers_exits_nonzero tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`41 passed`。
- `V91`（nineteenth remediation ruff / mypy）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py tests/integration/test_cli_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V92`（nineteenth remediation focused regression / constraints / diff）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`249 passed`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V93`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `5226ed535ac695c4050a6ee83dcc796ea8aa04ff221cfb4e3f03ad8c6ec8bcd1`，已写入 `program-manifest.yaml`。
- `V94`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 18.4 代码审查结论

- 宪章/规格对齐：close gate 现在基于当前 docs，而不是 stale report；coverage gate 兼容当前 generated task format，同时仍要求 P0/P1 task 有验收和验证。
- 质量风险：新增 close stale-doc regression 与 inferred coverage regression，覆盖当前 Codex actionable comments。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 18.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 18.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 19：第二十轮 PR #110 Codex review remediation

#### 19.1 本批目标

- 修复 PR #110 最新 Codex review P1：默认 `ai-sdlc loop design-contract check --wi ...` 路径不得在缺少 frozen current requirement loop 时通过。
- 确保无显式 `--requirement-loop-id` 时，design-contract check 会解析 current requirement，并把 frozen requirement loop id 写入 `design-contract-input.json`。
- 确保 close 前 revalidation 对 legacy empty requirement input 也重新执行 requirement gate，不能绕过 requirement freeze。

#### 19.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_loop.py`
  - 新增 `_required_requirement_loop_id`，无显式 requirement id 时读取 current requirement pointer。
  - `check_design_contract_loop` 在分析合同前解析并要求 frozen requirement loop。
  - `_refresh_report_before_close` 在 close 前重新解析 requirement gate，并将 resolved requirement id 写回 fresh input artifact。
- `tests/unit/test_design_contract_loop.py`
  - 新增 missing current requirement、默认 current frozen requirement、默认 current unfrozen requirement regression。
  - design-contract fixture 默认创建 frozen requirement loop；路径/loop id blocker 测试显式关闭该 fixture。
- `tests/unit/test_loop_status.py` / `tests/integration/test_cli_loop.py`
  - design-contract status/CLI fixtures 默认经过 frozen requirement 前置。
  - dry-run 测试改为断言不写 design-contract artifacts，而不是假设 `.ai-sdlc` 完全不存在。

#### 19.3 验证记录

- `V95`（twentieth Codex review requirement-gate targeted）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_blocks_missing_current_requirement_loop tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_uses_current_frozen_requirement_by_default tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_blocks_unfrozen_current_requirement_loop tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_writes_passed_artifacts tests/integration/test_cli_loop.py::test_loop_design_contract_check_status_and_close_json tests/integration/test_cli_loop.py::test_loop_design_contract_check_dry_run_skips_adapter_hook tests/integration/test_cli_loop.py::test_loop_requirement_start_dry_run_skips_adapter_hook_and_reports_source -q`
  - 结果：通过，`7 passed`。
- `V96`（twentieth remediation design-contract unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`43 passed`。
- `V97`（twentieth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`252 passed`。
- `V98`（twentieth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/requirement_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V99`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `770ab1988c758ca4e66f086ffa5bab302cea071958ac9548a580fee6d0aa5538`，已写入 `program-manifest.yaml`。
- `V100`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 19.4 代码审查结论

- 宪章/规格对齐：design-contract loop 现在强制承接 frozen requirement loop，不再允许默认路径跳过需求冻结。
- 质量风险：fixture 改为真实 frozen requirement 前置，覆盖默认 check、dry-run、status/list 和 CLI 路径。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 19.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 19.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 20：第二十一轮 PR #110 Codex review remediation

#### 20.1 本批目标

- 修复 PR #110 最新 Codex review P1：literal FR/SC coverage 不能由 P2/deferred task 提供。
- 保持 P2/P3 task detail gap 不阻断实现前合同，但也不能让 backlog task 伪装成 P0/P1 可执行覆盖。

#### 20.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_task_coverage_index` 在 literal FR/SC coverage 统计前解析 task priority。
  - P2/P3 task section 会被跳过，不再贡献 `covered_by`。
- `tests/unit/test_design_contract_loop.py`
  - 新增 P2 task 提到 FR/SC 但 P0 task 缺验证时，coverage 仍为 missing 的 regression。

#### 20.3 验证记录

- `V101`（twenty-first Codex review P2/deferred coverage targeted）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_ignores_p2_task_contract_coverage tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_ignores_p2_task_detail_gaps tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`44 passed`。
- `V102`（twenty-first remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`253 passed`。
- `V103`（twenty-first remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_loop.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V104`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `faee638b6db154f4991f5d4bdd163fc2687f4525b49091526680eb43a62bff7e`，已写入 `program-manifest.yaml`。
- `V105`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 20.4 代码审查结论

- 宪章/规格对齐：coverage gate 现在只接受 P0/P1 task coverage，避免用 deferred/backlog task 满足实现前合同。
- 质量风险：新增 regression 覆盖 P2 literal coverage，保留 P2 detail gap 不阻断的既有行为。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 20.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 20.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 21：第二十二轮 PR #110 Codex review remediation

#### 21.1 本批目标

- 修复 PR #110 最新 Codex review P2：显式 `--requirement-loop-id` 指向其他 work item 的 frozen requirement 时，design-contract check 不得通过。
- 保持空 `RequirementIntake.work_item_id` 可作为通用 requirement；只有记录了具体 work item 时才强制匹配。

#### 21.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_loop.py`
  - `_requirement_loop_gate` 增加 `work_item_id` 参数。
  - gate 在 frozen requirement 通过后读取 `requirement-intake.json`，若 intake work item 与 design-contract work item 不一致则 blocked。
  - `check_design_contract_loop` 与 close 前 revalidation 均传入当前 `contract_input.work_item_id`。
- `tests/unit/test_design_contract_loop.py`
  - 新增 mismatched requirement work item regression。

#### 21.3 验证记录

- `V106`（twenty-second Codex review requirement work item targeted）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_blocks_mismatched_requirement_work_item tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_accepts_frozen_requirement_loop tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_blocks_missing_requirement_loop tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_blocks_unfrozen_requirement_loop -q`
  - 结果：通过，`4 passed`。
- `V107`（twenty-second remediation design-contract unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`45 passed`。
- `V108`（twenty-second remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`254 passed`。
- `V109`（twenty-second remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/requirement_loop.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V110`（twenty-second remediation program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，写入 `program-manifest.yaml`，snapshot hash `13e3c651109f031ec0f9920b6de53b47864031c21011e2a0114b0adc602da001`。
- `V111`（twenty-second remediation pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 21.4 代码审查结论

- 宪章/规格对齐：design-contract loop 现在保持 requirement traceability，不能用其他 work item 的 frozen requirement 进入实现前合同。
- 质量风险：新增 explicit requirement id mismatch regression，覆盖当前 Codex actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 21.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 21.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 22：第二十三轮 PR #110 Codex review remediation

#### 22.1 本批目标

- 修复 PR #110 最新 Codex review P2：`direct-formal` 是合法产品/框架术语，不得被裸词 placeholder pattern 误判为模板占位。
- 保持真正占位信号仍可被拦截：`TODO`、`TBD`、`待补...`、未渲染 `功能规格：{{ ... }}` 等模式继续有效。

#### 22.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - 从 `_PLACEHOLDER_PATTERNS` 移除裸 `direct-formal` 正则。
- `tests/unit/test_design_contract_loop.py`
  - 新增合法 direct-formal 术语回归，覆盖 spec/plan/tasks 中正常出现该术语且合同完整时必须通过。

#### 22.3 验证记录

- `V112`（twenty-third Codex review direct-formal targeted）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_accepts_direct_formal_as_product_term tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_reports_placeholders tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_accepts_filled_feature_spec_title tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_reports_unrendered_feature_spec_title -q`
  - 结果：通过，`4 passed`。
- `V113`（twenty-third remediation ruff / mypy）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_loop.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
- `V114`（twenty-third remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`255 passed`。
- `V115`（twenty-third remediation constraints / diff）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V116`（twenty-third remediation program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，写入 `program-manifest.yaml`，snapshot hash `1ba018c5086865c5f7139012b6ab557ae743f0fa00a72133a75995632a53a442`。
- `V117`（twenty-third remediation pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 22.4 代码审查结论

- 宪章/规格对齐：placeholder gate 继续拦截真实占位文本，但不再把 direct-formal 这样的正常需求术语当作占位。
- 质量风险：新增 direct-formal 术语回归，覆盖当前 Codex actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 22.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 22.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）。
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 17：第十八轮 PR #110 Codex review remediation

#### 17.1 本批目标

- 修复 PR #110 最新 Codex review P2：`loop list --type design-contract` 在 current pointer 指向存在但不是 design-contract loop-run 的文件时，必须 fail-readable 地报告 `current-design-contract-target`，不能静默当作无 current loop。

#### 17.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/loop_status.py`
  - 在 design-contract list 读取 current pointer 后，校验 existing target 是否符合 `.ai-sdlc/loops/design-contract/<loop-id>/loop-run.json` 形态。
  - 对存在但不属于 design-contract loop-run 的目标写入 `current-design-contract-target` artifact error，并清空 current pointer 参与后续 list 汇总。
- `tests/unit/test_loop_status.py`
  - 新增 current design-contract pointer 指向 requirement loop-run 的 regression，断言 valid design-contract history 不被隐藏，同时 blocker/guidance 显示 malformed current pointer。

#### 17.3 验证记录

- `V83`（eighteenth Codex review invalid-current-target remediation）
  - 命令：`uv run pytest tests/unit/test_loop_status.py::test_list_loops_reports_invalid_current_design_contract_target tests/unit/test_loop_status.py::test_list_loops_reports_malformed_current_design_contract_run -q`
  - 结果：通过，`2 passed`。
- `V84`（eighteenth remediation loop-status unit）
  - 命令：`uv run pytest tests/unit/test_loop_status.py -q`
  - 结果：通过，`36 passed`。
- `V85`（eighteenth remediation ruff / mypy）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_status.py tests/unit/test_loop_status.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V86`（eighteenth remediation focused regression / constraints / diff）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`247 passed`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V87`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `f37141003f494b2c6de9a8d058874f762b09fc5b53ca520125f1da2fdcc6e97c`，已写入 `program-manifest.yaml`。
- `V88`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 17.4 代码审查结论

- 宪章/规格对齐：design-contract list 的 current pointer 恢复路径保持 fail-readable；坏 current pointer 不隐藏历史可读 loop。
- 质量风险：新增跨 loop-type 错指 target regression，覆盖当前 Codex actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 17.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 17.6 归档后动作

- **已完成 git 提交**：否；本批记录会随 remediation commit 一起落盘。
- **提交哈希**：提交后以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 14：第十五轮 PR #110 Codex review remediation

#### 14.1 本批目标

- 修复 PR #110 最新 Codex review P2：P0/P1 task 只有 `验证` / `Verification` 标签但没有实际命令时，不得视为满足 verification command gate。

#### 14.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_has_task_verification` 从“出现验证标签即可通过”改为“验证标签关联的 inline 或后续行内容必须包含实际命令 token”。
  - 支持常见命令入口：`uv run`、`python`、`pytest`、`ai-sdlc`、`npm/pnpm/yarn/npx`、`playwright`、`ruff`、`mypy`、`git diff --check` 等。
- `tests/unit/test_design_contract_loop.py`
  - 新增空 verification label 触发 `task_verification_gap` 的 regression。

#### 14.3 验证记录

- `V66`（fifteenth Codex review verification-command remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`35 passed`。
- `V67`（fifteenth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`243 passed`。
- `V68`（fifteenth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V69`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `17df686643c1befea1705b374a08fd8310d7711735674940bac18958908384b7`，已写入 `program-manifest.yaml`。
- `V70`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 14.4 代码审查结论

- 宪章/规格对齐：本批继续收紧 design-contract 对 P0/P1 task 的验证命令要求，避免无可执行验证步骤的合同进入 close。
- 质量风险：新增空 verification label regression，覆盖 Codex 最新 actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 14.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 14.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 16：第十七轮 PR #110 Codex review remediation

#### 16.1 本批目标

- 修复 PR #110 最新 Codex review P2：placeholder 检测不得把已填写的旧版中文标题 `# 功能规格：<name>` 误判为模板占位；只应阻断未渲染模板变量或明确占位词。

#### 16.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - 收窄 `功能规格：` placeholder pattern，仅匹配 `{{ ... }}`、`<...>`、`${...}`、`TODO`、`TBD`、`待补/待填/待定/待确认` 等未填写形态。
- `tests/unit/test_design_contract_loop.py`
  - 新增合法 `# 功能规格：Frontend Program Demo` 标题通过的 regression。
  - 新增未渲染 `# 功能规格：{{ project_name }}` 标题仍产生 placeholder blocker 的 regression。

#### 16.3 验证记录

- `V77`（seventeenth Codex review placeholder remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_reports_placeholders tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_accepts_filled_feature_spec_title tests/unit/test_design_contract_loop.py::test_check_design_contract_loop_reports_unrendered_feature_spec_title -q`
  - 结果：通过，`3 passed`。
- `V78`（seventeenth remediation design-contract unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`38 passed`。
- `V79`（seventeenth remediation ruff / mypy）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V80`（seventeenth remediation focused regression / constraints / diff）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`246 passed`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V81`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `68f3bd6505e575cf3923d00338803706b639dd02ae0c2efe13f439144ed72b8b`，已写入 `program-manifest.yaml`。
- `V82`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 16.4 代码审查结论

- 宪章/规格对齐：design-contract placeholder gate 继续阻断未填写模板，但兼容仓库既有已填写中文规格标题。
- 质量风险：新增正反样例 regression，避免后续再次把旧版合法规格标题误判为占位。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 16.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 16.6 归档后动作

- **已完成 git 提交**：否；本批记录会随 remediation commit 一起落盘。
- **提交哈希**：提交后以 `git log -1` 为准。
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier。
- 当前批次 worktree disposition 状态：retained（主工作区）。
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 13：第十四轮 PR #110 Codex review remediation

#### 13.1 本批目标

- 修复 PR #110 最新 Codex review P2：`--requirement-loop-id` 不能只写入 design-contract input artifact；必须验证 upstream requirement loop 已存在且已冻结，否则不得返回 ready/passed。

#### 13.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_loop.py`
  - 在 design-contract check 写入任何 passed artifacts 前增加 requirement loop gate。
  - 显式 requirement loop id 必须可解析、存在 requirement `loop-run.json`、`LoopRun.status == closed`，且 `requirement-freeze.json` 可验证并匹配同一 loop id。
  - 缺失、未冻结、id mismatch 或 freeze artifact malformed 时 fail-closed 到 `blocked`，并给出 requirement start/freeze/status 下一步。
- `tests/unit/test_design_contract_loop.py`
  - 新增缺失 requirement loop 阻断 regression。
  - 新增未 freeze requirement loop 阻断 regression。
  - 新增 frozen requirement loop 允许通过并写入 `requirement_loop_id` 的 regression。

#### 13.3 验证记录

- `V61`（fourteenth Codex review requirement-freeze gate remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`34 passed`。
- `V62`（fourteenth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`242 passed`。
- `V63`（fourteenth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V64`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `a0701c375bee9a0a069867fb866999debe4f1971bea16041859faec78efa522f`，已写入 `program-manifest.yaml`。
- `V65`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 13.4 代码审查结论

- 宪章/规格对齐：本批把 requirement freeze gate 接入 design-contract runtime，防止 requirement loop 未冻结时提前进入实现前合同通过状态。
- 质量风险：新增 missing / unfrozen / frozen 三类回归，覆盖 Codex 最新 actionable comment。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 13.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 13.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 2026-07-01-006 | Codex review summary/coverage remediation

#### 7.1 批次范围

- 覆盖任务：PR #110 latest Codex review P2 feedback for commit `a83c0c1dc8`
- 覆盖阶段：PR review remediation
- 预读范围：GitHub review threads for PR #110、`design_contract_checks.py`、`design_contract_models.py`、`design_contract_loop.py`、unit/integration tests
- 激活的规则：只修复 latest Codex actionable comments；不 resolve GitHub review threads；不扩大到 implementation/frontend-evidence loop

#### 7.2 改动范围

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/core/design_contract_checks.py`、`src/ai_sdlc/core/design_contract_models.py`、`src/ai_sdlc/core/design_contract_loop.py`、`tests/unit/test_design_contract_loop.py`、`tests/integration/test_cli_loop.py`、`task-execution-log.md`
- 将 FR/SC coverage extraction 限定到 canonical contract sections：需求、功能需求、成功标准、验收标准及英文等价章节。
- 排除用户故事、示例、验收场景、测试、fixture 和 fenced code block 中的 illustrative FR/SC ID。
- 在 `DesignContractCommandSummary` 中补齐 `status`、`coverage_matrix_path`、`report_path`，满足 `check --json` 文档合同。
- 为 dry-run/check/close 三类 design-contract command result 填充一致的 summary 字段。

#### 7.3 Codex review 线程处理

- `design_contract_checks.py`：Restrict coverage IDs to real contract sections
  - 处理：新增 heading-aware contract source extraction，只在 contract source section 内收集 FR/SC；新增测试覆盖用户故事/示例/code block 中的 ID 不进入 coverage。
- `design_contract_models.py`：Expose the documented JSON summary fields
  - 处理：`design_contract` summary 直接暴露 `status`、`coverage_matrix_path`、`report_path`；core unit 和 CLI integration 均增加断言。
- `design_contract_checks.py`：Treat Exit Criteria as contract sections
  - 处理：将 `exit criterion` / `exit criteria` 纳入 canonical contract section token；新增测试覆盖 `## Exit Criteria` 下的 `SC-*` 会进入 coverage matrix。
- `design_contract_store.py`：Prevent closing non-current design contracts
  - 处理：`close --loop-id` 必须与 `current-design-contract.json` 指向的 loop 一致；历史 passed loop 不能在当前 loop 有 blocker 时被显式关闭。
- `design_contract_checks.py`：Accept generated Chinese task headings
  - 处理：任务 parser 同时接受 `### Task ...` 与仓库模板生成的 `### 任务 ...`；真正非标准 heading 仍触发 `task_section_gap`。
- `design_contract_loop.py`：Add standard metadata to coverage artifacts
  - 处理：新增 `DesignContractCoverageMatrix` 和 `DesignContractCurrentPointer`，coverage matrix 与 current pointer 都通过 `LoopArtifactModel` 写入标准 `created_by`、`created_at`、`ai_sdlc_version`。
- `design_contract_checks.py`：Block local-review scope drift
  - 处理：将 `ai-sdlc pr-review` 命令与 `pr_review_*` 源文件信号纳入 design-contract scope drift 检查；保留普通 no-regression 文本不误伤。
- `design_contract_checks.py`：Accept English task labels
  - 处理：任务 acceptance / verification 检查同时接受 `Acceptance Criteria`、`Verification` 和 `Validation`。
- `design_contract_checks.py`：Block frontend-evidence commands in scope drift
  - 处理：将 `ai-sdlc loop frontend-evidence` 和 `ai-sdlc loop implementation` 命令纳入 design-contract scope drift 检查。

#### 7.4 统一验证命令

- `V15`（latest remediation design-contract runtime unit）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`17 passed`。
- `V16`（latest remediation CLI JSON focused integration）
  - 命令：`uv run pytest tests/integration/test_cli_loop.py::test_loop_design_contract_check_status_and_close_json tests/integration/test_cli_loop.py::test_loop_design_contract_check_dry_run_skips_adapter_hook -q`
  - 结果：通过，`2 passed`。
- `V17`（latest remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`225 passed`。
- `V18`（latest remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py tests/integration/test_cli_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V19`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：本日志落盘后执行；最终以 `program-manifest.yaml` 当前 snapshot 为准。
- `V20`（work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：本日志落盘和 truth sync 后执行；提交前如仅剩 `git_closure` 属预期，提交后需复跑至 PASS。
- `V21`（fourth Codex review exit-criteria remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`18 passed`。
- `V22`（fourth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`226 passed`。
- `V23`（fourth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V24`（fifth Codex review current-close / Chinese task heading remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`20 passed`。
- `V25`（fifth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`228 passed`。
- `V26`（fifth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V27`（sixth Codex review artifact metadata remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`20 passed`。
- `V28`（sixth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`228 passed`。
- `V29`（sixth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V30`（seventh Codex review local-pr-review scope drift remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`21 passed`。
- `V31`（seventh remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`229 passed`。
- `V32`（seventh remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V33`（eighth Codex review English labels / frontend command remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`23 passed`。
- `V34`（eighth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`231 passed`。
- `V35`（eighth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。

#### 7.5 代码审查结论

- 宪章/规格对齐：修复均来自 PR #110 latest Codex review；design-contract loop 仍保持 deterministic local runtime，不调用模型、不改业务代码、不进入下一类 loop。
- 代码质量：coverage source extraction 使用 Markdown heading 与 fenced-code 过滤，避免全局字符串扫描导致示例 ID 被提升为合同项。
- 测试质量：新增 example/code-block coverage regression，并对 command JSON summary 的 documented fields 做 unit/integration 双层断言。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 7.6 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 7.7 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`pending-remediation-commit`
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 8：第九轮 PR #110 Codex review remediation

#### 8.1 本批目标

- 修复 PR #110 最新 Codex review P1：design-contract coverage 不得把 `tasks.md` 非任务段、延期说明或代码块中的 FR/SC 原始字符串误判为已覆盖。
- 将 coverage source 限定为 parseable `### Task` / `### 任务` sections，并在 `covered_by` 中记录实际覆盖合同项的任务编号。
- 保持本批范围只限 design-contract loop deterministic check，不进入 implementation / frontend-evidence / local-pr-review loop。

#### 8.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_coverage_items_for_spec` 改为消费 task coverage index。
  - 新增 `_task_coverage_index`，只从可解析 task section 中提取 FR/SC，并记录覆盖任务 ID。
  - 新增 `_without_fenced_blocks`，避免 task section 内 fenced code block 里的 FR/SC 被计为覆盖。
- `tests/unit/test_design_contract_loop.py`
  - happy path 断言 `covered_by` 为 `T11`。
  - 新增非任务段 / fenced code block FR/SC 不算 coverage 的 regression。

#### 8.3 验证记录

- `V36`（ninth Codex review task-scoped coverage remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`24 passed`。
- `V37`（ninth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`232 passed`。
- `V38`（ninth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V39`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `3d84b5cab666857b98f903a262818f59121a6781ad31779210381f7cd16b742e`，已写入 `program-manifest.yaml`。
- `V40`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 8.4 代码审查结论

- 宪章/规格对齐：本批修复只收紧 design-contract coverage 的证据来源，不改变 loop 顺序，也不提前进入 implementation。
- 质量风险：已覆盖“FR/SC 只出现在非任务段或代码块”时不得通过的 regression；正常任务覆盖仍可通过并记录 `covered_by=["T11"]`。
- 结论：可提交、复跑 close-check、推送并重新请求 Codex review。

#### 8.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 8.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 9：第十轮 PR #110 Codex review remediation

#### 9.1 本批目标

- 修复 PR #110 最新 Codex review P1：scope drift 检查不能用固定 deny-list 把未来 implementation / frontend-evidence / pr-review 自身 work item 的合法命令或模块名拦截掉。
- 将 scope drift 改为 token family + 当前 work item allowed family 机制：普通 design-contract work item 仍拦越界 token；当前 work item 若明确属于 implementation-loop / frontend-evidence / local-pr-review，则允许对应 family。
- 保持 WI-193 自身仍不允许提前进入 implementation / frontend-evidence / local-pr-review。

#### 9.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_scope_drift_findings` 接收 `DesignContractInput`，按 family 判断 token 是否越界。
  - 新增 `_allowed_scope_families`，从 `work_item_id` / path 派生 implementation、frontend-evidence、pr-review 的合法 scope。
- `tests/unit/test_design_contract_loop.py`
  - 新增 active work item scope regression：`specs/implementation-loop-runtime` 可以合法出现 `ai-sdlc loop implementation` 与 `implementation_loop.py`。
  - 既有 demo contract scope drift tests 继续保证普通 work item 仍阻断越界。

#### 9.3 验证记录

- `V41`（tenth Codex review active-scope remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`25 passed`。
- `V42`（tenth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`233 passed`。
- `V43`（tenth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V44`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `37d77b2b9e68bc9d61f8d7cd0e63a3f673121c220166ec440020145e305f667a`，已写入 `program-manifest.yaml`。
- `V45`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 9.4 代码审查结论

- 宪章/规格对齐：本批修复使 design-contract loop 能服务后续 implementation / frontend-evidence / pr-review work item，而不是把 WI-193 的边界硬编码成全局规则。
- 质量风险：allowed family 只从当前 work item id/path 派生，普通 demo/design-contract work item 仍会阻断越界命令。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 9.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 9.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 10：第十一轮 PR #110 Codex review remediation

#### 10.1 本批目标

- 修复 PR #110 最新 Codex review P2：draft spec 检测不能只识别精确 `**状态**：草稿` 文本。
- 支持常见状态行变体：中文半角冒号 `**状态**: 草稿` 与英文 `**Status**: Draft`。
- 保持 draft spec 在 design-contract close 前必须阻断，不进入 implementation。

#### 10.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - 新增 `_DRAFT_STATUS` 正则和 `_is_draft_spec` helper。
  - `analyze_design_contract` 改用 helper 判断 draft spec。
- `tests/unit/test_design_contract_loop.py`
  - 新增参数化 regression，覆盖中文半角冒号和英文 Draft 状态。

#### 10.3 验证记录

- `V46`（eleventh Codex review draft-status remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`27 passed`。
- `V47`（eleventh remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`235 passed`。
- `V48`（eleventh remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V49`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `6cdfc23fda0960ffc6fb8c42220caa4f651e3093d6db5a6ed4fadf8e5598f166`，已写入 `program-manifest.yaml`。
- `V50`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 10.4 代码审查结论

- 宪章/规格对齐：本批只增强 draft spec 阻断识别，符合 design-contract gate 的 pre-implementation 质量边界。
- 质量风险：新增中英文状态行 regression，避免状态格式差异绕过 draft blocker。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 10.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 10.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 11：第十二轮 PR #110 Codex review remediation

#### 11.1 本批目标

- 修复 PR #110 最新 Codex review P1：task section 不能把最终 task 后面的非任务 heading 内容吸收为该 task 的 coverage。
- 修复 PR #110 最新 Codex review P2：用户无 `--loop-id` 重跑同一 work item 的已关闭 current design-contract check 时，不能新建 passed loop 并覆盖 current pointer。
- 保持 closed current loop 的 implementation next action 和 current pointer 稳定。

#### 11.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_task_sections` 在下一个 task heading 或下一个 `#` 到 `###` peer heading 处截断。
  - 新增 `_next_peer_heading_start`，避免尾部 `## Coverage matrix` 等非任务段被计入上一 task。
- `src/ai_sdlc/core/design_contract_loop.py`
  - `check_design_contract_loop` 在无显式 loop id 时优先识别同一 work item 的 closed current loop。
  - 新增 `_closed_current_recheck_result`，返回 closed result、implementation next action 和 include-close artifacts，不覆盖 current pointer。
- `tests/unit/test_design_contract_loop.py`
  - 新增尾部 coverage matrix 不算 task coverage 的 regression。
  - 新增默认 recheck 已关闭 current loop 不新建/不覆盖 pointer 的 regression。

#### 11.3 验证记录

- `V51`（twelfth Codex review task-tail / closed-current remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`29 passed`。
- `V52`（twelfth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`237 passed`。
- `V53`（twelfth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_loop.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V54`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `5b4292f048161c804f1ec56bc5ccc41834f7bef3c000bf313c4c5720a5a93d82`，已写入 `program-manifest.yaml`。
- `V55`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 11.4 代码审查结论

- 宪章/规格对齐：本批继续收紧 design-contract close 前证据，且保留已关闭合同的状态真值，不进入下一类 loop。
- 质量风险：新增 task-tail coverage 和 default closed recheck 两条回归，覆盖 Codex 最新 actionable comments。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 11.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 11.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。

### Batch 12：第十三轮 PR #110 Codex review remediation

#### 12.1 本批目标

- 修复 PR #110 最新 Codex review P2：checkpoint 同时存在外部 `linked_plan_uri` 和 `linked_wi_id` 时，design-contract no-`--wi` 路径应优先使用 canonical `specs/<linked_wi_id>`。
- 修复 PR #110 最新 Codex review P2：task acceptance/verification 必填 gate 只强制 P0/P1；P2/P3 backlog task 不应阻断 implementation-ready contract。

#### 12.2 变更范围

- **验证画像**：code-change
- `src/ai_sdlc/core/design_contract_store.py`
  - `_current_work_item_path` 仅当 `linked_plan_uri` 指向 canonical `specs/<wi>/plan.md` 时优先 plan parent；否则优先 `linked_wi_id`。
- `src/ai_sdlc/core/design_contract_checks.py`
  - `_task_findings` 解析 task priority，P2/P3 task 跳过 acceptance / verification 必填 blocker。
  - 新增 `_task_priority`。
- `tests/unit/test_design_contract_loop.py`
  - 新增 checkpoint external plan + linked_wi_id regression。
  - 新增 P2 task 缺少 acceptance / verification 不阻断的 regression。

#### 12.3 验证记录

- `V56`（thirteenth Codex review checkpoint/P2-task remediation）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py -q`
  - 结果：通过，`31 passed`。
- `V57`（thirteenth remediation focused regression）
  - 命令：`uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`239 passed`。
- `V58`（thirteenth remediation ruff / mypy / constraints / diff）
  - 命令：`uv run ruff check src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py tests/unit/test_design_contract_loop.py`
  - 结果：通过，`All checks passed!`。
  - 命令：`uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/design_contract_models.py src/ai_sdlc/core/design_contract_checks.py src/ai_sdlc/core/design_contract_store.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
  - 命令：`git diff --check`
  - 结果：通过，无输出。
- `V59`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，snapshot hash `1059cf3a0b3607539e0d11a8ddcd63f01606718ac7388b74b85053ae428515c7`，已写入 `program-manifest.yaml`。
- `V60`（pre-commit work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
  - 结果：除 `git_closure` 因当前修复尚未提交而 BLOCKER 外，其余检查 PASS；提交后需复跑至 PASS。

#### 12.4 代码审查结论

- 宪章/规格对齐：本批修复 no-`--wi` 当前 work item 解析和低优先级 backlog task gate，保持 design-contract loop 可服务真实用户项目。
- 质量风险：新增 checkpoint 和 P2 task regression，避免把外部 plan URI 或 backlog 任务误判成 blocker。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 12.5 任务/计划同步状态

- `tasks.md` 同步状态：T41/T42 保持完成；本批为 PR review remediation，不新增交付范围。
- `related_plan`（如存在）同步状态：无 related_plan；plan 边界仍为 design-contract loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #110 head branch。

#### 12.6 归档后动作

- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：当前 close-out commit，以 `git log -1` 为准
- 当前批次 branch disposition 状态：`feature/193-loop-engine-design-contract-loop-runtime-docs` 为 PR merge carrier
- 当前批次 worktree disposition 状态：retained（主工作区）
- 是否继续下一批：否；需完成 PR #110 Codex re-review 和 checks 后再进入 implementation loop。
