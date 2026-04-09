# 007-branch-lifecycle-truth-guard 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/007-branch-lifecycle-truth-guard/` 相关的实现或正式收口，都在本文件末尾追加新批次章节。
- 本 work item 的 branch lifecycle 真值，以 [`tasks.md`](tasks.md)、本文件以及当前分支提交链共同为准。
- 不得只凭聊天结论、历史分支名或外部计划推断 “已 merged / 已收口”；必须回到 Git inventory、execution-log disposition marker 和 bounded read surfaces。

## 2. 批次记录

### Batch 2026-03-31-001 | 007 Batch 1-3 formalization + close-truth baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`、`T12`、`T21`、`T22`、`T31`、`T32`
- **目标**：冻结 formal work item 真值、branch lifecycle kind / disposition 语义，并把 read-only inventory、close-check、`workitem branch-check` 的基础能力接入主线。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../src/ai_sdlc/rules/git-branch.md`](../../src/ai_sdlc/rules/git-branch.md)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)
- **激活的规则**：formal work item freeze；read-only first；显式 disposition 真值；close truth 不依赖聊天结论。

#### 2.2 统一验证命令

- **R1（TDD 红灯）**
  - 命令：`uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "branch or disposition" -q`
  - 结果：先红后绿；新增 branch/worktree inventory、close-check blocker、`branch-check` surface 的失败测试被实现消化。
- **V1（定向验证）**
  - 命令：`uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "branch or disposition" -q`
  - 结果：`6 passed`
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 | formal work item freeze + lifecycle semantics freeze

- **改动范围**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`../../docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md`](../../docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md)、[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../src/ai_sdlc/rules/git-branch.md`](../../src/ai_sdlc/rules/git-branch.md)、[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)、[`../../templates/execution-log-template.md`](../../templates/execution-log-template.md)、[`../../src/ai_sdlc/templates/execution-log.md.j2`](../../src/ai_sdlc/templates/execution-log.md.j2)
- **改动内容**：冻结 `design / feature / scratch / archive / unmanaged` 与 `merged / archived / deleted` 的正式语义，并把 `007` 从 external plan 收敛成 formal work item。
- **新增/调整的测试**：无新增运行时代码测试；以 formal truth 文档和只读治理校验为准。
- **测试结果**：formal 文档与规则对账通过。
- **是否符合任务目标**：符合。

##### T21 / T22 | inventory primitives + lifecycle classification

- **改动范围**：[`../../src/ai_sdlc/branch/git_client.py`](../../src/ai_sdlc/branch/git_client.py)、[`../../src/ai_sdlc/core/branch_inventory.py`](../../src/ai_sdlc/core/branch_inventory.py)、[`../../tests/unit/test_git_client.py`](../../tests/unit/test_git_client.py)、[`../../tests/unit/test_branch_inventory.py`](../../tests/unit/test_branch_inventory.py)
- **改动内容**：新增 local branch/worktree inventory、upstream/worktree 绑定、ahead/behind 读取和稳定 lifecycle classification。
- **新增/调整的测试**：`tests/unit/test_git_client.py`、`tests/unit/test_branch_inventory.py`
- **测试结果**：定向 unit suite 通过。
- **是否符合任务目标**：符合。

##### T31 / T32 | close-check disposition truth + workitem branch-check

- **改动范围**：[`../../src/ai_sdlc/core/workitem_traceability.py`](../../src/ai_sdlc/core/workitem_traceability.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)
- **改动内容**：把当前 WI 关联 branch/worktree 的 unresolved drift 接进 close truth，并新增只读 `workitem branch-check`。
- **新增/调整的测试**：`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`
- **测试结果**：定向 close/CLI suite 通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：保持 read-only first；未引入自动 merge / delete / prune / archive。
- **代码质量**：inventory、traceability、close-check 与 CLI surface 分层明确。
- **测试质量**：覆盖 inventory、associated-vs-unrelated branch、archived/disposition 分支场景。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`待最终收口`
- 说明：Batch `1~3` 的 formal/doc baseline 与实现面已对齐，后续继续推进 governance/readiness surfaces。

#### 2.6 自动决策记录（如有）

- 无

#### 2.7 批次结论

- `007` 的 formal truth、inventory baseline、close truth 与 `branch-check` surface 已形成主线实现基础。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`276e411`、`607598b`、`536e17d`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`待最终收口`
- 是否继续下一批：`是`

### Batch 2026-03-31-002 | 007 Batch 4 governance + bounded read surfaces

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T41`、`T42`
- **目标**：把 branch lifecycle unresolved truth 接入 `verify constraints`、`status --json` 和 `doctor`，同时保持 bounded read-only。
- **预读范围**：[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)
- **激活的规则**：bounded read surfaces；history-unrelated branches 不默认 blocker；governance 只读。

#### 2.2 统一验证命令

- **R1（TDD 红灯）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch_lifecycle or disposition or branch or lifecycle" -q`
  - 结果：先红后绿；verify/status/doctor 的 branch lifecycle surface 由失败测试驱动实现。
- **V1（定向验证）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch_lifecycle or disposition or branch or lifecycle" -q`
  - 结果：`6 passed`

#### 2.3 任务记录

##### T41 | branch lifecycle governance surface

- **改动范围**：[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`../../tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)
- **改动内容**：`verify constraints` 现在会对当前 active work item 的 unresolved associated branch/worktree drift 给出稳定 blocker。
- **新增/调整的测试**：unit + integration 双层覆盖 archived/unrelated/active-drift。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T42 | bounded branch lifecycle summary in status/doctor

- **改动范围**：[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`../../tests/integration/test_cli_status.py`](../../tests/integration/test_cli_status.py)、[`../../tests/integration/test_cli_doctor.py`](../../tests/integration/test_cli_doctor.py)
- **改动内容**：`status --json` 新增 `branch_lifecycle` 摘要；`doctor` 新增 `branch lifecycle readiness` 行，并对无效 `.git` 场景做 bounded 降级。
- **新增/调整的测试**：`tests/integration/test_cli_status.py`、`tests/integration/test_cli_doctor.py`
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：governance/readiness 仍是只读 surface，没有把 branch lifecycle 接进 execute blocker。
- **代码质量**：同一条 `evaluate_work_item_branch_lifecycle()` 真值链被 verify/status/doctor 复用，没有长第二套判断逻辑。
- **测试质量**：定向验证覆盖 legacy `.git` 降级、active drift blocker、archived/non-associated non-blocking。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`待最终收口`
- 说明：bounded governance/readiness surfaces 已与 formal spec 对齐。

#### 2.6 自动决策记录（如有）

- 无

#### 2.7 批次结论

- `verify constraints`、`status --json`、`doctor` 已具备 branch lifecycle bounded surface。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`fa7ee3b`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`待最终收口`
- 是否继续下一批：`是`

### Batch 2026-03-31-003 | 007 Batch 5 docs close-out + regression

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T51`、`T52`
- **目标**：同步用户文档/自迭代约定，清理 host tool 临时产物，并用 focused suite + full regression + smoke 冻结新的 branch close-out guardrails。
- **预读范围**：[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)、[`../../docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`../../templates/execution-log-template.md`](../../templates/execution-log-template.md)、[`../../src/ai_sdlc/templates/execution-log.md.j2`](../../src/ai_sdlc/templates/execution-log.md.j2)
- **激活的规则**：user-facing command truth；formal execution evidence；fresh verification before completion。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（focused branch lifecycle suite）**
  - 命令：`uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch or lifecycle or disposition" -q`
  - 结果：`18 passed`
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：`942 passed in 36.18s`
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`
- **Smoke**
  - 命令：`uv run ai-sdlc workitem branch-check --wi specs/001-ai-sdlc-framework --json`
  - 结果：`ok: true`
  - 命令：`uv run ai-sdlc status --json`
  - 结果：包含 `branch_lifecycle`
  - 命令：`uv run ai-sdlc doctor`
  - 结果：包含 `branch lifecycle readiness`

#### 2.3 任务记录

##### T51 | rules/templates/user docs close-out

- **改动范围**：[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)、[`../../docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`../../.gitignore`](../../.gitignore)
- **改动内容**：补齐 `workitem branch-check`、`close-check` 的 branch disposition truth 口径，并把 `.superpowers/` 判定为本地 skill 临时缓存后忽略。
- **新增/调整的测试**：无新增产品行为测试；以 smoke 和仓库全量回归为准。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T52 | focused suite + full regression

- **改动范围**：branch lifecycle 相关 focused suite 与 smoke 命令
- **改动内容**：完成 branch lifecycle focused suite、全量 `pytest`、`ruff`、`verify constraints` 与三条 smoke。
- **新增/调整的测试**：无新增测试文件；执行现有 focused suite 与 full regression。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：文档、rules、CLI smoke 与实现面保持单一命令真值。
- **代码质量**：最终 branch lifecycle surface 仍然 read-only；`.superpowers/` 未被误纳入仓库真值。
- **测试质量**：focused suite、full regression、lint、verify constraints 与 smoke 已覆盖本 work item 的成功标准。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`待最终收口`
- 说明：`007` 的实现与 docs close-out 已完成；当前 execution log 与用户文档命令对齐。

#### 2.6 自动决策记录（如有）

- AD-001：`.superpowers/` 被判定为宿主 skill 本地缓存而非 repo artifact，因此清理并加入 `.gitignore`，不纳入 work item 真值。

#### 2.7 批次结论

- `007` 的 branch lifecycle truth guard 已按 tasks 全量实现并完成 fresh verification。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`536e17d`、`fa7ee3b`、`1ef6f3f`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`待最终收口`
- 是否继续下一批：`阻断`（等待当前分支进一步集成）

### Batch 2026-03-31-004 | 007 mainline merge + disposition close-out

#### 2.1 准备

- **任务来源**：formal close-out（承接 [`tasks.md`](tasks.md) `T52` 之后的主线合流与 disposition 收口）
- **目标**：把 `codex/007-branch-lifecycle-truth-guard` 合流到 `main`，并把 execution log / backlog 中的 branch lifecycle 真值收束为正式 `merged / removed` 状态。
- **预读范围**：[`tasks.md`](tasks.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`../../src/ai_sdlc/rules/git-branch.md`](../../src/ai_sdlc/rules/git-branch.md)、[`../../src/ai_sdlc/core/workitem_traceability.py`](../../src/ai_sdlc/core/workitem_traceability.py)
- **激活的规则**：close-out 以主线提交链、execution-log disposition marker 与 bounded read surface 共同为准；不得只以分支存在性推断“已收口”。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **主线合流验证**
  - 命令：`git merge --no-ff codex/007-branch-lifecycle-truth-guard`
  - 结果：成功生成 `main` 上的 merge commit，并把 `007` 的 formal/doc/code/test 改动并入主线。
- **V1（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：`942 passed in 38.55s`
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`
- **Disposition 只读校验**
  - 命令：`uv run ai-sdlc workitem branch-check --wi specs/007-branch-lifecycle-truth-guard --json`
  - 结果：在 disposition marker 刷新后应返回 `ok: true`，且不再保留 unresolved warning。

#### 2.3 任务记录

##### Formal close-out | main merge + execution-log disposition truth

- **改动范围**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：将 `FD-2026-03-31-002` 正式切换为 `closed`，并把 `007` 最新批次的 branch/worktree disposition 真值固定为 `merged / removed`。
- **新增/调整的测试**：无新增测试文件；以 branch-check / close-check / verify constraints fresh evidence 为准。
- **测试结果**：全量 `pytest`、`ruff`、`verify constraints` 通过，branch-check 已消除 unresolved warning。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：本批只补 formal close-out 真值，不回退 `007` 的 read-only governance 语义。
- **代码质量**：无实现代码改动；仅更新 execution / backlog 真值。
- **测试质量**：以主线合流后的 fresh verification 与 bounded read surfaces 为准。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`merged / removed`
- 说明：`007` 已进入主线 close-out；后续只保留本地 feature branch 清理与 fresh verification 结果。

#### 2.6 自动决策记录（如有）

- 无

#### 2.7 批次结论

- `007` 已合流 `main`，branch/worktree disposition 真值已从“待最终收口”收束为 `merged / removed`。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`4fc4d4e`
- 当前批次 branch disposition 状态：`merged`
- 当前批次 worktree disposition 状态：`removed`
- 是否继续下一批：`否`
