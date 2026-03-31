# 008-direct-formal-workitem-entry 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/008-direct-formal-workitem-entry/` 相关的 formal freeze、实现或 close-out，都在本文件末尾追加新批次章节。
- 本 work item 的 canonical truth，以 [`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、本文件和当前分支提交链共同为准。
- `docs/superpowers/*` 在本 work item 中最多只应作为 `related_doc / related_plan` reference；不得再生成第二套 canonical docs。

## 2. 批次记录

### Batch 2026-03-31-001 | 008 formal freeze baseline

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11`
- **目标**：把 `FD-2026-03-31-003` 直接收敛成 formal work item，避免再走 `docs/superpowers/* -> specs/<WI>/` 双轨路径。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **激活的规则**：single canonical doc set；formal work item first；design input 不等于 execute 真值。
- **验证画像**：`rules-only`

#### 2.2 统一验证命令

- **V1（formal freeze 校验）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 | 冻结正式 work item 真值并回挂 backlog

- **改动范围**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)
- **改动内容**：把 direct-formal canonical path 正式编号为 `008-direct-formal-workitem-entry`，并把 backlog、spec、plan、tasks 直接落到 formal work item 目录。
- **新增/调整的测试**：无代码测试；以 formal 文档对账和只读治理校验为准。
- **测试结果**：formal freeze 校验通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：formal work item 直接落于 `specs/<WI>/`，没有回到 `docs/superpowers/*` 作为 canonical 落点。
- **代码质量**：本批仅包含 formal truth 与 backlog 真值，无执行代码。
- **测试质量**：只读治理校验通过。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`待最终收口`
- 说明：formal work item baseline 已冻结，后续实现在同一 `specs/008-.../` 真值下继续推进。

#### 2.6 自动决策记录（如有）

- 无

#### 2.7 批次结论

- `008` 已经以 single canonical doc set 形式进入实现准备状态。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`b66f7e6`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`retained（当前执行分支）`
- 是否继续下一批：`是`

### Batch 2026-03-31-002 | 008 direct-formal helper + CLI + docs alignment

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T12`、`T21`、`T22`、`T31`、`T32`、`T41`、`T42`
- **目标**：把 direct-formal scaffold helper、`workitem init`、rules/docs 口径和 focused regression 一次性接入主线候选分支。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../templates/spec-template.md`](../../templates/spec-template.md)、[`../../templates/plan-template.md`](../../templates/plan-template.md)、[`../../templates/tasks-template.md`](../../templates/tasks-template.md)
- **激活的规则**：single canonical doc set；reference-only external design docs；parser-friendly skeleton；verification before completion。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **R1（focused direct-formal suite）**
  - 命令：`uv run pytest tests/unit/test_workitem_scaffold.py tests/integration/test_cli_workitem_init.py tests/unit/test_command_names.py -q`
  - 结果：`8 passed in 0.20s`
- **V1（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：`949 passed in 32.75s`
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T12 | 冻结 direct-formal canonical path 语义

- **改动范围**：[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)、[`../../docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)
- **改动内容**：把新 framework capability 的 canonical 入口收紧为 direct-formal `specs/<WI>/`，并明确 `docs/superpowers/*` 仅为 reference。
- **新增/调整的测试**：通过 focused suite、全量回归与治理校验覆盖规则/CLI/文档对齐。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

##### T21 / T22 | 新增 direct-formal scaffold helper

- **改动范围**：[`../../src/ai_sdlc/core/workitem_scaffold.py`](../../src/ai_sdlc/core/workitem_scaffold.py)、[`../../tests/unit/test_workitem_scaffold.py`](../../tests/unit/test_workitem_scaffold.py)
- **改动内容**：新增 formal work item scaffold helper，直接复用根模板生成 `spec.md / plan.md / tasks.md` skeleton，支持 `related_plan / related_doc` reference 挂接，并保证 parser-friendly tasks 输出稳定。
- **新增/调整的测试**：`tests/unit/test_workitem_scaffold.py`
- **测试结果**：focused suite 通过。
- **是否符合任务目标**：符合。

##### T31 / T32 | 暴露 workitem init 并补齐 command discovery

- **改动范围**：[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`../../tests/integration/test_cli_workitem_init.py`](../../tests/integration/test_cli_workitem_init.py)、[`../../tests/unit/test_command_names.py`](../../tests/unit/test_command_names.py)
- **改动内容**：新增 `ai-sdlc workitem init`，直接创建 canonical formal docs，并把该命令接入 command discovery 与 negative coverage。
- **新增/调整的测试**：`tests/integration/test_cli_workitem_init.py`、`tests/unit/test_command_names.py`
- **测试结果**：focused suite 通过。
- **是否符合任务目标**：符合。

##### T41 / T42 | 文档对齐与 focused regression

- **改动范围**：[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)
- **改动内容**：把用户文档、规则和自迭代约定统一到 direct-formal 入口；不再要求“先写 superpowers 再 formalize”。
- **新增/调整的测试**：通过 focused suite、全量回归、`ruff` 与 `verify constraints` 覆盖。
- **测试结果**：通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：helper、CLI、rules/docs 与 `008` 的 single canonical doc set 目标一致。
- **代码质量**：未引入第二套 canonical 模板或外部 design 正文复制路径；生成与 CLI 逻辑分层明确。
- **测试质量**：覆盖 scaffold shape、parser-friendly tasks、CLI init、duplicate init、command discovery 和全量回归。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`待最终收口`
- 说明：功能与文档均已落在当前分支；formal close 仍需后续 branch disposition 收束。

#### 2.6 自动决策记录（如有）

- AD-001：direct-formal helper 只生成 `spec.md / plan.md / tasks.md`，不额外生成 `task-execution-log.md`，避免在 work item 尚未执行前伪造执行真值。

#### 2.7 批次结论

- `008` 已具备 direct-formal scaffold、CLI discoverability 和 single canonical doc set guardrail。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`c2bd576`
- 当前批次 branch disposition 状态：`待最终收口`
- 当前批次 worktree disposition 状态：`retained（当前执行分支）`
- 是否继续下一批：`阻断`（等待 branch disposition 进入最终收口）
