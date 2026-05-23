# 任务执行日志：生产反馈驱动的任务守卫、注释规范与半途接入优化

**功能编号**：`183-production-feedback-guard-adoption`
**创建日期**：2026-05-23
**状态**：草稿

## 1. 归档规则

- 本文件是 `183-production-feedback-guard-adoption` 的固定执行归档文件。
- 后续每完成一批任务，都在本文件末尾追加一个新的批次章节。
- 每一批任务结束后，必须按固定顺序执行：
  1. 完成实现和 focused verification。
  2. 更新 `tasks.md` 状态和本文件执行记录。
  3. 让两个对抗 agent 评审本批生成物，确认无必须修订项。
  4. 若评审、测试、CI 或 PR review 发现阻塞，修复后重新执行验证和评审。
  5. 再进行本批提交或进入下一批。
- 每个任务记录至少包含：任务编号、改动范围、改动内容、测试命令、测试结果、对抗评审结论、是否符合任务目标。

## 2. 已完成记录

### Batch 2026-05-23-001 | T11

#### 2.1 批次范围

- 覆盖任务：`T11`
- 覆盖阶段：生产反馈归档文档冻结
- 预读范围：用户反馈、两个对抗 agent 初审结论、归档文档
- 激活的规则：AGENTS.md Continuity Protocol、对抗评审约束

#### 2.2 改动记录

- 改动范围：`docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md`
- 改动内容：归档 adapter 口径、next executable task 守卫、注释规范、原注释保护、简体中文 UTF-8 防乱码、brownfield adopt 半途接入方案。
- 新增/调整的测试：无；本批为文档归档。
- 执行的命令：
  - `Get-Content docs/production-feedback-sdlc-guard-adoption-comments.zh-CN.md -TotalCount 80`
  - 两个对抗 agent 二轮评审
- 测试结果：文档可读；两个对抗 agent 均确认无必须修订项，可以进入 formal work item 拆分。
- 是否符合任务目标：是。

#### 2.3 对抗评审结论

- UX 对抗 agent：满意，可以进入下一步细粒度拆分。
- AI-native 对抗 agent：满意，可以进入下一步细粒度拆分。

#### 2.4 任务/计划同步状态

- `tasks.md` 同步状态：`T11` 已标记 done。
- `related_doc` 同步状态：已在 `plan.md` / `tasks.md` frontmatter 记录归档文档。
- 关联 branch/worktree disposition 计划：待最终收口。

#### 2.5 批次结论

- 生产反馈归档文档已冻结为 formal work item 输入。
- 下一步：完成 `T12` formal spec / plan / tasks，并再次通过两个对抗 agent 评审。

## 3. 当前进行中

无。下一步进入 Batch 6：`brownfield adopt`，但必须先通过 Batch 5 对抗评审。

## 4. 已完成记录

### Batch 2026-05-23-002 | T12

#### 4.1 批次范围

- 覆盖任务：`T12`
- 覆盖阶段：formal spec / plan / tasks 拆分与对抗评审
- 预读范围：生产反馈归档文档、第一轮 formal docs 对抗评审结论、第二轮复审结论
- 激活的规则：每一步生成物必须经过两个对抗 agent 评审，无必须修订项后才能继续

#### 4.2 改动记录

- 改动范围：
  - `specs/183-production-feedback-guard-adoption/spec.md`
  - `specs/183-production-feedback-guard-adoption/plan.md`
  - `specs/183-production-feedback-guard-adoption/tasks.md`
  - `specs/183-production-feedback-guard-adoption/task-execution-log.md`
- 改动内容：将生产反馈归档拆成正式 spec、实施 plan、可执行 tasks 和执行日志；修订第一轮对抗评审提出的所有阻塞项；吸收第二轮建议到任务验收边界。
- 新增/调整的测试：无；本批为 formal work item 文档。
- 执行的命令：
  - `uv run ai-sdlc verify constraints`: no BLOCKERs.
- 测试结果：本地约束校验通过。
- 是否符合任务目标：是。

#### 4.3 对抗评审结论

- 第一轮 formal docs 对抗评审：发现必须修订项，包括固定批次门禁、PR/CI 修复复审循环、execution log 不一致、自动最小任务补齐、guard advisory 冲突、schema 边界、注释语言信号链路和 brownfield adopt 拆分不足。
- 修订后第二轮 formal docs 对抗评审：UX agent 和 AI-native agent 均通过，无必须修订项，同意进入 Batch 2。
- 建议吸收快速确认：两个 agent 均确认已吸收非 git 项目接入降级、扫描预算、parser 兼容列表、postflight 证据模型、编码检查 blocker/warning 分级和 mojibake 示例白名单，且无新增阻塞。
- 编号卫生快速确认：发现 `182-*` 已被既有 work item 使用后，统一修正为 `183-production-feedback-guard-adoption`，并把 `next_work_item_seq` 调整到 `186`；两个 agent 均确认无新增阻塞。

#### 4.4 任务/计划同步状态

- `tasks.md` 同步状态：`T12` 已标记 done。
- `plan.md` 同步状态：Phase 3/4 已同步编码分级、非 git 项目和扫描预算验证。
- `program-manifest.yaml` 同步状态：已注册 `183-production-feedback-guard-adoption`，避免与既有 `182-*` work item 冲突。
- 下一批入口：`T21` 冻结 executable task schema contract。

#### 4.5 批次结论

- Formal work item 四件套已通过两轮对抗评审并收口。
- 下一步：进入 Batch 2，先实现 `T21` executable task schema contract。

### Batch 2026-05-23-003 | T21-T23

#### 4.6 批次范围

- 覆盖任务：`T21`、`T22`、`T23`
- 覆盖阶段：Batch 2 executable task schema
- 预读范围：`tasks.md` Batch 2、现有 `TasksParser`、`execute_authorization`、`task_ac_checks`
- 激活的规则：代码修改必须绑定已完成 formal task；Batch 完成后必须通过 focused tests、ruff 和两个对抗 agent 评审

#### 4.7 改动记录

- 改动范围：
  - `src/ai_sdlc/core/executable_task.py`
  - `tests/unit/test_executable_task.py`
  - `specs/183-production-feedback-guard-adoption/tasks.md`
  - `specs/183-production-feedback-guard-adoption/task-execution-log.md`
- 改动内容：
  - 新增 executable task parser 和 schema contract。
  - 支持规范 heading、`task_id/status/goal/scope/acceptance/verify/notes` 字段、多行列表、依赖解析和未知字段 warning。
  - 增加重复 task id、缺字段、非法状态、非法 scope、占位内容、example scope 的阻断 finding。
  - 根据对抗评审修正 `first_executable_task()`，当文档存在全局错误时不返回可执行任务。
  - 根据对抗评审降低占位/模板误伤：`README/TODO` 和真实 `templates/tasks-template.md` 不会被当作占位任务；占位错误会指出具体字段和值。
  - 提供 `is_executable` 和 `first_executable_task`，为 Batch 3 guard 使用。
- 新增/调整的测试：
  - 新增 `tests/unit/test_executable_task.py` 覆盖 T21-T23 验收点，并补充 `goal`、`invalid_status`、`blocked`、低误伤模板路径、占位短语、规则说明不误伤和全局错误不放行测试。
- 执行的命令：
  - `uv run pytest tests/unit/test_executable_task.py -q`: 13 passed.
  - `uv run ruff check src/ai_sdlc/core/executable_task.py tests/unit/test_executable_task.py`: All checks passed.
  - `uv run ai-sdlc verify constraints`: no BLOCKERs.
  - parser smoke：当前 `specs/183-production-feedback-guard-adoption/tasks.md` 解析结果为 ok，20 tasks，0 errors，first executable task 为 `T31`。
- 测试结果：focused tests 和 ruff 均通过。
- 是否符合任务目标：是，待两个对抗 agent 对 Batch 2 生成物评审。

#### 4.8 对抗评审结论

- 第一轮对抗评审：不通过。必须修订项包括 `goal` contract 未实现、`first_executable_task()` 在全局错误下可能放行、占位错误信息不够可操作、缺无效状态测试、placeholder/template 判定误伤真实任务文件。
- 第二轮对抗评审：AI-native 通过；UX 仍阻塞，指出占位识别对 `TODO:` / `placeholder:` / `待补充` 短语拦截不足，且 T23 acceptance 与允许真实模板文件的实现不一致。
- 第三轮对抗评审：UX 通过；AI-native 仍阻塞，指出当前真实 `tasks.md` 的规则说明句被误判为占位，导致 `first_executable_task` 返回 None。
- 第四轮对抗评审：UX 和 AI-native 均通过，无必须修订项，同意进入 Batch 3。
- 修订状态：Batch 2 已通过对抗评审。

#### 4.9 任务/计划同步状态

- `tasks.md` 同步状态：`T21`、`T22`、`T23` 已标记 done。
- `plan.md` 同步状态：无需调整；Batch 2 仍符合 Phase 1 的 schema-first 顺序。
- 下一批入口：两个对抗 agent 对 Batch 2 无必须修订项后，进入 `T31` 自动准备最小任务。

#### 4.10 批次结论

- Batch 2 实现已完成 focused verification。
- 下一步：提交 Batch 2 后进入 Batch 3，先实现 `T31` 自动准备最小任务。

### Batch 2026-05-23-004 | T31-T34

#### 4.11 批次范围

- 覆盖任务：`T31`、`T32`、`T33`、`T34`
- 覆盖阶段：Batch 3 next executable task guard
- 预读范围：`execute_authorization`、`workitem_cmd`、`telemetry/readiness`、Batch 2 parser
- 激活的规则：产品代码修改主路径必须硬阻断 `BLOCK_CODE_PREPARE_TASKS`；普通用户文案不要求理解 checkpoint/stage

#### 4.12 改动记录

- 改动范围：
  - `src/ai_sdlc/core/task_preparation.py`
  - `src/ai_sdlc/core/task_guard.py`
  - `src/ai_sdlc/core/execute_authorization.py`
  - `src/ai_sdlc/cli/workitem_cmd.py`
  - `src/ai_sdlc/telemetry/readiness.py`
  - `tests/unit/test_task_preparation.py`
  - `tests/unit/test_task_guard.py`
  - `tests/unit/test_execute_authorization.py`
  - `tests/integration/test_cli_workitem_guard.py`
  - `specs/183-production-feedback-guard-adoption/tasks.md`
  - `specs/183-production-feedback-guard-adoption/task-execution-log.md`
- 改动内容：
  - 新增最小任务候选生成，不直接修改用户文件。
  - 新增 task guard preflight，支持 `ALLOW_CODE_WITH_TASK` 与 `BLOCK_CODE_PREPARE_TASKS`。
  - 将 execute authorization 接入 task guard；formal docs 不完整或真实 tasks 文件没有可执行任务时硬阻断。
  - 新增 during/postflight 范围检查，覆盖 product、test、doc、snapshot、migration、config、generated 伴随文件分类，并承载 verification commands 与 execution log entry。
  - 新增只读 `ai-sdlc workitem guard` surface，支持 JSON 和表格输出；默认表格显示用户友好文案，JSON 保留机器状态码。
  - status readiness 的 execute authorization next action 增加 task guard 修复建议。
- 新增/调整的测试：
  - `tests/unit/test_task_preparation.py`
  - `tests/unit/test_task_guard.py`
  - `tests/integration/test_cli_workitem_guard.py`
  - 扩展 `tests/unit/test_execute_authorization.py`
- 执行的命令：
  - `uv run pytest tests/unit/test_task_preparation.py tests/unit/test_task_guard.py tests/unit/test_execute_authorization.py tests/integration/test_cli_workitem_guard.py -q`: 20 passed.
  - `uv run ruff check src/ai_sdlc/core/task_preparation.py src/ai_sdlc/core/task_guard.py src/ai_sdlc/core/execute_authorization.py src/ai_sdlc/cli/workitem_cmd.py src/ai_sdlc/telemetry/readiness.py tests/unit/test_task_preparation.py tests/unit/test_task_guard.py tests/unit/test_execute_authorization.py tests/integration/test_cli_workitem_guard.py`: All checks passed.
  - `uv run ai-sdlc verify constraints`: no BLOCKERs.
- 测试结果：focused tests、ruff 和约束校验均通过。
- 是否符合任务目标：是，待两个对抗 agent 对 Batch 3 生成物评审。

#### 4.13 对抗评审结论

- 第一轮对抗评审：不通过。必须修订项包括缺 `plan.md` 时 guard / execute authorization 仍可能放行、postflight 证据模型缺 verification command 和 execution log entry、默认用户文案暴露内部状态。
- 第二轮对抗评审：UX 和 AI-native 均通过，无必须修订项，同意进入 Batch 4。
- 非阻塞备注：旧英文 `review-to-decompose` / `repo truth` 等内部文案将在 Batch 4 adapter/status 用户口径中继续收敛。

#### 4.14 任务/计划同步状态

- `tasks.md` 同步状态：`T31`、`T32`、`T33`、`T34` 已标记 done；T33 集成测试路径同步为实际落地的 `tests/integration/test_cli_workitem_guard.py`。
- `plan.md` 同步状态：无需调整；实现仍符合 Phase 1 guard core。
- 下一批入口：两个对抗 agent 对 Batch 3 无必须修订项后，进入 `T41` adapter / init / status 用户口径。

#### 4.15 批次结论

- Batch 3 实现已完成 focused verification。
- 下一步：提交 Batch 3 后进入 Batch 4，处理 `T41` adapter / init / status 用户口径。

### Batch 2026-05-23-005 | T41

#### 4.16 批次范围

- 覆盖任务：`T41`
- 覆盖阶段：Batch 4 adapter wording and user-facing workflow state
- 预读范围：adapter templates、beginner guidance、status guidance、execute authorization wording、USER_GUIDE
- 激活的规则：用户主路径不依赖不可验证宿主加载证明；排查命令保留为诊断入口

#### 4.17 改动记录

- 改动范围：
  - `AGENTS.md`
  - `src/ai_sdlc/adapters/codex/AI-SDLC.md`
  - `src/ai_sdlc/adapters/vscode/AI-SDLC.md`
  - `src/ai_sdlc/adapters/claude_code/AI-SDLC.md`
  - `src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md`
  - `src/ai_sdlc/cli/beginner_guidance.py`
  - `src/ai_sdlc/cli/adapter_cmd.py`
  - `src/ai_sdlc/cli/status_guidance.py`
  - `src/ai_sdlc/core/execute_authorization.py`
  - `src/ai_sdlc/telemetry/display.py`
  - `USER_GUIDE.zh-CN.md`
  - `tests/unit/test_execute_authorization.py`
  - `tests/integration/test_cli_status.py`
- 改动内容：
  - adapter templates 从“必须证明 verified_loaded”改为“用户主路径不依赖宿主加载证明，写代码前以当前可执行任务为准”。
  - 默认 adapter status 对已安装规则不再引导用户手动 `run --dry-run`，而是回到 AI 对话继续需求。
  - adapter activate/status 指引从 verified_loaded 检查改为规则安装状态排查。
  - `ai-sdlc run` 对 `materialized` adapter 不再因缺 `verified_loaded` 阻断，真正执行授权交给 executable task / formal docs guard。
  - `adapter select` / `shell-select` 不再把 `run --dry-run` 作为普通下一步。
  - execute authorization 和 status display 中旧的 `review-to-decompose` / `repo truth` 用户可见文案改为任务确认文案。
  - USER_GUIDE 将 adapter status 标注为排查入口，并补充 `workitem guard`。
- 新增/调整的测试：
  - 更新 execute authorization/status 断言，保留 JSON 机器状态码但默认文案收敛为用户可理解表达。
- 执行的命令：
  - `uv run pytest tests/integration/test_cli_run.py::TestRunCommand::test_run_non_dry_run_continues_when_adapter_is_materialized tests/integration/test_cli_run.py::TestRunCommand::test_run_non_dry_run_does_not_suggest_fake_env_for_generic_adapter tests/unit/test_execute_authorization.py tests/integration/test_cli_status.py::test_status_json_includes_execute_authorization_blocker_before_execute_stage tests/integration/test_cli_adapter.py -q`: 29 passed.
  - `uv run ruff check ...`: All checks passed.
  - `uv run ai-sdlc verify constraints`: no BLOCKERs.
- 测试结果：focused tests、ruff 和约束校验均通过。
- 是否符合任务目标：是，待两个对抗 agent 对 Batch 4 生成物评审。

#### 4.18 对抗评审结论

- 第一轮对抗评审：不通过。必须修订项包括 `ai-sdlc run` 非 dry-run 主路径仍以 `verified_loaded` 为硬门禁、测试仍固定旧行为、`adapter select/shell-select` 仍把 `run --dry-run` 作为普通下一步、USER_GUIDE 升级后普通步骤仍要求 `adapter status`。
- 第二轮对抗评审：AI-native 通过；UX 仍阻塞，指出 beginner UX 测试仍固定旧 `run --dry-run` 输出，且非 ready adapter 恢复文案仍把 dry-run 放进普通路径。
- 第三轮对抗评审：UX 通过，无必须修订项；Batch 4 已满足两个对抗视角。

#### 4.19 任务/计划同步状态

- `tasks.md` 同步状态：`T41` 已标记 done。
- `plan.md` 同步状态：无需调整；实现符合 Phase 2 adapter 口径。
- 下一批入口：两个对抗 agent 对 Batch 4 无必须修订项后，进入 `T51` 注释语言信号链路。

#### 4.20 批次结论

- Batch 4 实现已完成 focused verification。
- 下一步：提交 Batch 4 后进入 Batch 5，处理 `T51` 注释语言信号链路。

### Batch 2026-05-23-006 | T51-T53

#### 4.21 批次范围

- 覆盖任务：`T51`、`T52`、`T53`
- 覆盖阶段：Batch 5 comment and text quality policies
- 预读范围：归档文档注释规范、`rules/code-review.md`、verify constraints、adapter/task 模板
- 激活的规则：注释语言跟随当前/近期用户主要沟通语言，默认简体中文；保留原注释；新增/修改文本必须 UTF-8 且无乱码

#### 4.22 改动记录

- 改动范围：
  - `src/ai_sdlc/core/comment_policy.py`
  - `src/ai_sdlc/core/text_quality.py`
  - `src/ai_sdlc/core/verify_constraints.py`
  - `rules/code-review.md`
  - `src/ai_sdlc/rules/code-review.md`
  - `templates/tasks-template.md`
  - `tests/unit/test_comment_policy.py`
  - `tests/unit/test_text_quality.py`
  - `specs/183-production-feedback-guard-adoption/tasks.md`
  - `specs/183-production-feedback-guard-adoption/task-execution-log.md`
- 改动内容：
  - 新增注释语言决策：当前用户文本优先、近期用户文本次之、项目默认兜底；默认简体中文。
  - adapter prompt / AGENTS 明确约束新增注释语言跟随当前/近期用户主语言，默认简体中文。
  - 新增注释策略：复杂逻辑/边界/并发/缓存/错误处理应注释，显而易见复述型注释应避免。
  - 新增原注释保护：`verify constraints` 接入统一 diff 检查；删除原注释时必须同 hunk 有替代注释，或 execution log / handoff 记录删除原因。
  - 新增文本质量检查：UTF-8 decode failure、替换字符、高置信 mojibake 为 blocker；BOM 和疑似繁体为 warning，支持繁体项目例外。
  - `verify constraints` 接入 changed text quality blocker，检查 tracked diff 新增行和 untracked 新文件；支持 `.ai-sdlc/project/config/text-quality-allowlist.txt` 白名单。
  - code-review 规则和 tasks 模板增加注释/文本质量约束。
- 新增/调整的测试：
  - `tests/unit/test_comment_policy.py`
  - `tests/unit/test_text_quality.py`
- 执行的命令：
  - `uv run pytest tests/unit/test_comment_policy.py tests/unit/test_text_quality.py -q`: 18 passed.
  - `uv run pytest tests/integration/test_cli_verify_constraints.py -q`: 46 passed.
  - `uv run ruff check src/ai_sdlc/core/comment_policy.py src/ai_sdlc/core/text_quality.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_comment_policy.py tests/unit/test_text_quality.py`: All checks passed.
  - `uv run ai-sdlc verify constraints`: no BLOCKERs.
- 测试结果：focused tests、ruff 和约束校验均通过。
- 是否符合任务目标：是，待两个对抗 agent 对 Batch 5 修订后生成物复审。

#### 4.23 对抗评审结论

- 第一轮 AI-native 评审：不通过。必须修订项包括注释语言 helper 未接入真实 adapter prompt、原注释删除保护未进入门禁且替代判断过宽、文本质量检查全文件扫描且缺少白名单/繁体例外、`verify constraints` 漏检 untracked、tasks/log 状态提前完成。
- 已修订：
  - `AGENTS.md`、Codex / VS Code / Claude Code / Cursor / generic adapter prompt 均增加注释语言、保留原注释和高价值注释约束。
  - `verify constraints` 增加原注释删除 blocker。
  - 原注释替代判断从“同 hunk 任意新增注释”改为按删除/新增注释数量配对；无法配对时要求 execution log / handoff 记录删除原因。
  - 文本质量检查改为 diff-based：tracked 文件只检查新增行，untracked 文件检查全量新内容；UTF-8 解码仍按文件检查。
  - 增加 `.ai-sdlc/project/config/text-quality-allowlist.txt` 白名单支持和繁体项目例外参数。
  - 测试覆盖中文噪音注释、原注释删除门禁、diff-based 检查、untracked 检查、allowlist 和繁体例外。
- 第二轮 UX 评审：不通过。必须修订项包括 tracked 文件仍先整文件 UTF-8 decode，可能误卡历史 GBK 文件；原注释删除原因记录是全局关键词豁免，缺路径、注释摘要和逐条对应。
- 已二次修订：
  - tracked 文件不再整文件 decode；只检查 diff 新增行，历史非 UTF-8 内容不会阻塞当前干净改动。
  - untracked 新文件仍做整文件 UTF-8 decode，因为全量内容都是本次新增。
  - 原注释删除原因记录改为逐条匹配：新增 log / handoff 行必须包含删除原因 token、被删注释所在路径和被删注释摘要。
  - 新增回归测试覆盖历史 GBK tracked 文件新增 ASCII 不阻塞，以及泛化删除注释原因不能绕过门禁。
- 第二轮 UX 复审：通过，无必须修订项；建议 blocker 文案提示记录原因需包含文件路径和被删注释摘要。
- 第二轮 AI-native 复审：不通过。必须修订项为被删注释摘要会压缩空格，但 log 行未同样归一化，导致自然写法 `explains payment idempotency` 被误卡。
- 已三次修订：
  - 原注释删除原因匹配时对 log 行做同样 whitespace compact，支持自然空格写法。
  - blocker 文案明确提示记录原因需包含文件路径和被删注释摘要。
  - 回归测试改为自然空格写法，避免固化不自然规避格式。
- 第三轮 UX 复审：通过，无必须修订项，同意进入 Batch 6。
- 第三轮 AI-native 复审：通过，无必须修订项，同意进入 Batch 6。
- 复审状态：通过。

#### 4.24 任务/计划同步状态

- `tasks.md` 同步状态：`T51`、`T52`、`T53` 已在第三轮复审通过后标记 done。
- `plan.md` 同步状态：无需调整；实现符合 Phase 3 注释与中文编码质量底线。
- 下一批入口：两个对抗 agent 对 Batch 5 无必须修订项后，进入 `T61` adoption models 与 source discovery。

#### 4.25 批次结论

- Batch 5 修订实现已完成 focused verification，并通过 UX 与 AI-native 三轮对抗复审。
- 下一步：提交 Batch 5 后进入 Batch 6：brownfield adopt。
