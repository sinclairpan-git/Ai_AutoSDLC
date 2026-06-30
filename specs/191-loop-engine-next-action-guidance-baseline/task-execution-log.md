# 执行记录：Loop Engine Next Action Guidance Baseline

**Work Item**：`191-loop-engine-next-action-guidance-baseline`
**开始时间**：2026-06-30
**当前阶段**：formal baseline prepared

## Batch 2026-06-30-001 | T11 formal baseline

### 1. 准备

- **目标**：创建 WI-191 canonical formal docs，并将需求范围收敛为 `loop status/list` 的结构化 next guidance。
- **上游依据**：
  - `specs/189-loop-engine-local-adversarial-pr-review/spec.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/plan.md`
  - `specs/190-loop-engine-status-list-baseline/spec.md`
  - `specs/190-loop-engine-status-list-baseline/plan.md`
- **关键决策**：
  - 本 WI 只做只读 guidance，不做自动执行器。
  - 保留 `next_action` 字符串，新增 additive `next_guidance`。
  - no current 时首选 `pr-review doctor`，降低小白用户学习成本。
  - `requires_model` 只描述后续 `pr-review start/rerun` 可能调用本地独立 review agent；`loop` 命令本身不得调用模型。

### 2. 变更范围

- `specs/191-loop-engine-next-action-guidance-baseline/spec.md`
- `specs/191-loop-engine-next-action-guidance-baseline/plan.md`
- `specs/191-loop-engine-next-action-guidance-baseline/tasks.md`
- `specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md`
- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`

### 3. 待验证

- `uv run ai-sdlc workitem link --wi-id 191-loop-engine-next-action-guidance-baseline --plan-uri specs/191-loop-engine-next-action-guidance-baseline/plan.md`
- `uv run ai-sdlc program truth sync --execute --yes`
- `uv run ai-sdlc workitem guard`
- `git diff --check`

### 4. 任务/计划同步状态

- T11：formal docs 已准备，等待框架链接和 diff 验证。
- T21：下一条可执行产品任务，待开始。

## Batch 2026-06-30-002 | T21-T22 core guidance

### 1. 准备

- **目标**：新增结构化 next guidance 模型，并根据 local PR review 状态推导下一步命令、原因、影响和证据。
- **激活的规则**：`loop status/list` 必须只读；guidance 不得执行命令，不得调用模型，不得写 artifact。

### 2. 变更范围

- `src/ai_sdlc/core/loop_status.py`
- `tests/unit/test_loop_status.py`

### 3. 改动内容

- 新增 `LoopNextActionGuidance` 与 `LoopNextActionSafety`。
- 在 `LoopSummary`、`LoopStatusResult`、`LoopListResult` 中增加 additive `next_guidance` 字段，同时保留原 `next_action`。
- 为未初始化、no current、malformed pointer、`needs_fix`、`passed`、`needs_review`、`needs_user`、`blocked`、`closed` 等状态推导 guidance。
- 保持 `get_loop_status()` / `list_loops()` 只读，不新增 provider 或模型调用路径。

### 4. 验证

- `uv run pytest tests/unit/test_loop_status.py -q`：18 passed。
- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`：31 passed。
- `git diff --check`：通过。

### 5. 任务/计划同步状态

- T21：已完成。
- T22：已完成。

## Batch 2026-06-30-003 | T31-T32 CLI guidance output

### 1. 准备

- **目标**：让 `ai-sdlc loop status/list` 的 human 输出展示 next guidance，并验证 CLI 不触发 provider 或模型调用。

### 2. 变更范围

- `src/ai_sdlc/cli/loop_cmd.py`
- `tests/integration/test_cli_loop.py`

### 3. 改动内容

- human 输出新增 `Next command`、`Why`、`Model call`、`Writes artifacts`、`Writes code`、`Safety`、`Evidence`、`Alternatives`。
- `loop status` 顶层展示当前推荐 guidance；`loop list` 为每个 item 展示各自 guidance。
- 新增 provider runner 未被调用的集成测试，确认 guidance 输出仍是只读。

### 4. 验证

- `uv run pytest tests/integration/test_cli_loop.py -q`：12 passed，后续新增 provider 断言后纳入 combined run。
- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`：31 passed。
- `uv run ruff check src tests`：All checks passed。

### 5. 任务/计划同步状态

- T31：已完成。
- T32：已完成。

## Batch 2026-06-30-004 | T41-T42 docs, constraints, regression

### 1. 准备

- **目标**：对齐 README、PR checklist、verify constraints，并完成 focused regression。

### 2. 变更范围

- `README.md`
- `docs/pull-request-checklist.zh.md`
- `src/ai_sdlc/core/verify_constraints.py`
- `tests/unit/test_verify_constraints.py`
- `specs/191-loop-engine-next-action-guidance-baseline/tasks.md`
- `specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md`

### 3. 改动内容

- README 增加 next guidance 说明：它解释后续命令，但自身不执行命令、不调用模型、不替代本地独立 review agent 或人工判断。
- PR checklist 增加 Loop Next Action Guidance 自检项。
- verify constraints 增加 WI-191 feature-contract surface，覆盖 core model、CLI human 输出和只读用户文档。
- 修复 active checkpoint feature 指针，使默认 `workitem guard` 指向 WI-191。

### 4. 验证

- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`：169 passed。
- `uv run ruff check src tests`：All checks passed。
- `uv run ai-sdlc verify constraints`：no BLOCKERs。
- `git diff --check`：通过。

### 5. 任务/计划同步状态

- T41：已完成。
- T42：已完成，等待 close-check 和 handoff 最终刷新。

### 6. 统一验证命令

- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`169 passed in 10.58s`。
- `uv run ruff check src tests`
  - 结果：通过，`All checks passed!`。
- `uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过，写入 `program-manifest.yaml`，truth snapshot state 为 `migration_pending`，snapshot hash 为 `bbfb941b6d7b230c69e278c182afba0ea13f54862c13e207e78abf1b0b0b1bc2`。
- `git diff --check`
  - 结果：通过。

### 7. 代码审查（摘要）

- 宪章/规格对齐：实现保持 `loop status/list` 只读边界，guidance 只解释后续命令，不执行命令、不调用模型、不写 artifact。
- 代码质量：新增 additive `next_guidance`，保留 `next_action` 兼容；guidance 推导集中在 `loop_status.py`，CLI 只负责渲染。
- 测试质量：unit 覆盖 no current、uninitialized、malformed、needs_fix、passed 和 list item guidance；integration 覆盖 human/JSON 输出和 provider runner 未调用。
- 文档质量：README、PR checklist 和 verify constraints 均明确 next guidance 不是执行器、不是模型调用、不是本地 review agent 或人工判断替代品。
- 结论：允许提交本批 code-change 并进入 PR review / checks。

### 8. branch/worktree disposition

- 关联 branch/worktree disposition 计划：`merge-pending`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`active`

### 9. 当前结论

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/core/loop_status.py`、`src/ai_sdlc/cli/loop_cmd.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_loop_status.py`、`tests/integration/test_cli_loop.py`、`tests/unit/test_verify_constraints.py`、`README.md`、`docs/pull-request-checklist.zh.md`、`.ai-sdlc/state/checkpoint.yml`、`.ai-sdlc/project/config/project-state.yaml`、`program-manifest.yaml`、`specs/191-loop-engine-next-action-guidance-baseline/spec.md`、`specs/191-loop-engine-next-action-guidance-baseline/plan.md`、`specs/191-loop-engine-next-action-guidance-baseline/tasks.md`、`specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md`
- **已完成 git 提交**：是（本批提交后复核）
- **提交哈希**：待本批提交后生成
- **是否继续下一批**：否；提交后执行 close-check、推送分支、打开 PR 并请求 Codex review。

## Batch 2026-06-30-005 | Codex review remediation

### 1. 批次范围

- 覆盖任务：PR #107 Codex review P2 feedback on non-current `loop list` item guidance。
- 覆盖阶段：post-review remediation。
- 预读范围：PR #107 inline comment `discussion_r3496953102`、`list_loops` current pointer behavior、loop list tests。
- 激活规则：`pr-review fix/rerun/close` 只作用于 current review pointer；非 current 历史 item 不得给可执行 PR-review command。

### 2. branch/worktree disposition

- 关联 branch/worktree disposition 计划：`merge-pending`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`active`

### 3. 改动范围

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/core/loop_status.py`、`tests/unit/test_loop_status.py`、`tests/integration/test_cli_loop.py`、`specs/191-loop-engine-next-action-guidance-baseline/spec.md`、`specs/191-loop-engine-next-action-guidance-baseline/plan.md`、`specs/191-loop-engine-next-action-guidance-baseline/tasks.md`、`specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md`

### 4. 改动内容

- 将非 current `loop list` item 的 guidance 改为 inspect-only：`ai-sdlc loop list --json`，不写 artifact、不调用模型、不修改代码。
- 保留 current item 的 actionable guidance；只有 current review 才推荐 `ai-sdlc pr-review fix/rerun/close`。
- 更新 formal docs，明确非 current 历史 item 不得推荐作用于 current pointer 的 PR-review 命令。
- 更新 unit/integration tests，覆盖 non-current inspect-only guidance。

### 5. 统一验证命令

- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`169 passed in 10.87s`。
- `uv run ruff check src tests`
  - 结果：通过，`All checks passed!`。
- `uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `git diff --check`
  - 结果：通过。

### 6. 代码审查（摘要）

- 宪章/规格对齐：修复后 `loop list` 仍是只读索引；非 current item 不再暗示可直接修复/复审/关闭历史 run。
- 代码质量：用 `is_current` 在 summary 构造点分流，避免 CLI 层猜测 current pointer 语义。
- 测试质量：unit 覆盖 list 中 current/non-current item 的不同 guidance；integration 覆盖 human 和 JSON 输出。
- 结论：Codex P2 已修复，可同步 truth、提交 remediation commit 并重新请求 Codex review。

### 7. 任务/计划同步状态

- `tasks.md` 同步状态：已补充非 current item inspect-only acceptance。
- `plan.md` 同步状态：已补充 list item current actionable / non-current inspect-only 验证策略。
- `spec.md` 同步状态：已补充 FR/SC 与用户故事，防止后续实现回退。
- `task-execution-log.md` 同步状态：已追加本轮 Codex remediation 记录。

### 8. 当前结论

- PR #107 Codex P2 已修复。
- **已完成 git 提交**：是（Codex remediation commit 后复核）
- **提交哈希**：待 Codex remediation commit 生成
- **是否继续下一批**：否；提交后重新请求 Codex review/checks 并继续 heartbeat。

## Batch 2026-06-30-006 | Codex post-fix rerun guidance remediation

### 1. 批次范围

- 覆盖任务：PR #107 第二轮 Codex review P2 feedback on post-fix `needs_fix` guidance。
- 覆盖阶段：post-review remediation。
- 预读范围：PR #107 inline comment `discussion_r3497055655`、`fix_pr_review` 写入的 persisted `next_action`、`loop_status` guidance 推导逻辑。
- 激活规则：当前 review 已生成 fix plan / resolution scaffold 后，即使 `ReviewRun.status` 仍为 `needs_fix`，也必须尊重持久化 `next_action` 并推荐 `ai-sdlc pr-review rerun`。

### 2. branch/worktree disposition

- 关联 branch/worktree disposition 计划：`merge-pending`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`active`

### 3. 改动范围

- **验证画像**：code-change
- **改动范围**：`src/ai_sdlc/core/loop_status.py`、`tests/unit/test_loop_status.py`、`tests/integration/test_cli_loop.py`、`specs/191-loop-engine-next-action-guidance-baseline/spec.md`、`specs/191-loop-engine-next-action-guidance-baseline/plan.md`、`specs/191-loop-engine-next-action-guidance-baseline/tasks.md`、`specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md`

### 4. 改动内容

- 在 current `needs_fix` guidance 中优先识别 persisted `next_action` 是否已指向 `ai-sdlc pr-review rerun`。
- 对 post-fix `needs_fix` 输出 `ai-sdlc pr-review rerun`，并标记后续命令 `requires_model=true`、`safety=may_call_local_review_agent`。
- 保留 fresh `needs_fix` 的 `ai-sdlc pr-review fix` guidance。
- 更新 unit/integration tests，覆盖 post-fix `needs_fix` 的 JSON guidance。
- 更新 formal docs，明确 `needs_fix` guidance 分为 fresh fix 与 post-fix rerun 两态。

### 5. 统一验证命令

- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`
  - 结果：通过，`33 passed in 1.10s`。
- `uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - 结果：通过，`171 passed in 10.29s`。
- `uv run ruff check src tests`
  - 结果：通过，`All checks passed!`。
- `uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `git diff --check`
  - 结果：通过。

### 6. 代码审查（摘要）

- 宪章/规格对齐：修复后 guidance 尊重 local PR review 的持久化状态，不再把 post-fix 状态误导回 fix plan 生成步骤。
- 代码质量：在 core guidance 层识别 `next_action` 中的 rerun 命令，避免 CLI 层解析业务状态。
- 测试质量：unit 覆盖 core guidance；integration 覆盖 CLI JSON 输出和 evidence。
- 结论：第二轮 Codex P2 已修复，可同步 truth、提交 remediation commit 并重新请求 Codex review。

### 7. 任务/计划同步状态

- `tasks.md` 同步状态：已补充 post-fix `needs_fix` rerun acceptance。
- `plan.md` 同步状态：已补充 fresh fix / post-fix rerun 验证策略。
- `spec.md` 同步状态：已补充 FR/SC 与用户故事验收，防止后续实现回退。
- `task-execution-log.md` 同步状态：已追加本轮 Codex remediation 记录。

### 8. 当前结论

- PR #107 第二轮 Codex P2 已修复。
- **已完成 git 提交**：是（Codex remediation commit 后复核）
- **提交哈希**：待 Codex remediation commit 生成
- **是否继续下一批**：否；提交后重新请求 Codex review/checks 并继续 heartbeat。
