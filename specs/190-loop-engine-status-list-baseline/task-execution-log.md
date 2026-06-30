# 任务执行日志：Loop Engine Status/List Baseline

**功能编号**：`190-loop-engine-status-list-baseline`
**创建日期**：2026-06-29
**状态**：Batch 3 T31 CLI registration completed，等待 command discovery

## 1. 归档规则

- 本文件是 `190-loop-engine-status-list-baseline` 的固定执行归档文件。
- 后续每完成一批任务，都在本文件末尾追加新的批次章节。
- 后续每一批任务开始前，必须先完成固定预读：`spec.md`、`plan.md`、`tasks.md`、`.ai-sdlc/memory/constitution.md` 以及当前相关实现入口。
- 后续每一批任务结束后，必须按固定顺序执行：
  - 完成实现和验证。
  - 更新 `tasks.md` 的 task status。
  - 追加本文件的批次记录。
  - 更新 handoff。
  - 将本批代码/测试/文档/执行日志合并为一次提交，避免二次补哈希噪音。
- 每个批次记录至少包含：任务编号、改动范围、改动内容、验证命令、结果、对齐结论、风险与下一步。

## 2. 批次记录

### Batch 2026-06-29-001 | T11 formal baseline

#### 2.1 批次范围

- 覆盖任务：`T11`
- 覆盖阶段：formal baseline and checkpoint linkage
- 预读范围：WI-189 PRD/plan/tasks、当前 `workitem init/link` help、当前 Loop/PR Review 模型与 CLI 入口
- 激活规则：work item direct-formal docs、program truth sync、checkpoint linkage、handoff continuity

#### 2.2 改动范围

- 新增 `specs/190-loop-engine-status-list-baseline/spec.md`
- 新增 `specs/190-loop-engine-status-list-baseline/plan.md`
- 新增 `specs/190-loop-engine-status-list-baseline/tasks.md`
- 新增 `specs/190-loop-engine-status-list-baseline/task-execution-log.md`
- 更新 `program-manifest.yaml`
- 更新 `.ai-sdlc/project/config/project-state.yaml`

#### 2.3 改动内容

- 初始化 WI-190 formal work item，主题为 Loop Engine 只读 `status/list` 基线。
- 将模板 PRD 替换为 WI-190 专属 PRD，明确第一版只消费 local PR review artifact。
- 冻结 P0 范围：`ai-sdlc loop status`、`ai-sdlc loop list`、JSON/human 输出、malformed artifact 处理、read-only/no-model/no-adapter-write 边界。
- 将 implementation 文件面拆为 `core/loop_status.py`、`cli/loop_cmd.py`、CLI 注册、command discovery、focused tests 和 docs/verify surface。
- checkpoint 已链接到 `190-loop-engine-status-list-baseline`。

#### 2.4 执行的命令

- `git switch -c codex/190-loop-engine-status-list-baseline`
  - 结果：创建分支成功，但 `workitem init` 要求 docs branch。
- `git switch -c feature/190-loop-engine-status-list-baseline-docs`
  - 结果：切换到框架要求的 docs branch。
- `git stash push -m "codex preserve 189 runtime handoff before wi190 init" -- .ai-sdlc/state/codex-handoff.md .ai-sdlc/state/resume-pack.yaml .ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`
  - 结果：保留上一轮 runtime handoff，满足 clean working tree 要求。
- `uv run ai-sdlc workitem init --wi-id 190-loop-engine-status-list-baseline --title "Loop Engine status/list baseline" --input "..."`
  - 结果：生成 `spec.md / plan.md / tasks.md / task-execution-log.md`。
- `uv run ai-sdlc program truth sync --execute --yes`
  - 结果：写入 `program-manifest.yaml`；首次 snapshot hash 为 `5076b618a9b22240652a8f8c92f95bb802c9175db95421fb9c4d69fefe13e187`；全局 truth 仍报告历史 migration/audit blocker，不阻断本 WI formal docs。
- `uv run ai-sdlc workitem link --wi-id 190-loop-engine-status-list-baseline --plan-uri specs/190-loop-engine-status-list-baseline/plan.md`
  - 结果：checkpoint linkage 更新到 WI-190。
- `uv run ai-sdlc workitem guard --wi specs/190-loop-engine-status-list-baseline --json`
  - 结果：初次发现 `tasks.md` 的 executable-task 结构缺少 parser 可识别的 `acceptance`，修订后通过，下一条可执行任务为 `T21`。
- `uv run ai-sdlc recover --reconcile`
  - 结果：active checkpoint 对齐到 `190-loop-engine-status-list-baseline`，当前阶段为 `execute`。
- `git diff --check`
  - 结果：通过。
- `uv run ai-sdlc verify constraints`
  - 结果：初次发现 Task 2.1 缺少文档级验收标记，补充 `notes: 验收标准见 acceptance 字段。` 后通过。
- `uv run ai-sdlc program truth sync --execute --yes`
  - 结果：按最终文档重新写入 `program-manifest.yaml`，snapshot hash 为 `79f44ed92c23579134c6548af448c6aef05d7c49a7d90b0c1a6989da0c4c7ad5`。

#### 2.5 验证结果

- `program truth sync`：完成，最终 snapshot hash 为 `79f44ed92c23579134c6548af448c6aef05d7c49a7d90b0c1a6989da0c4c7ad5`。
- `workitem link`：完成，linked WI 为 `190-loop-engine-status-list-baseline`。
- `recover --reconcile`：完成，active feature 已切换到 WI-190 execute。
- `workitem guard --wi specs/190-loop-engine-status-list-baseline --json`：通过，下一条任务为 `T21`。
- `git diff --check`：通过。
- `uv run ai-sdlc verify constraints`：通过，no BLOCKERs。
- `uv run ai-sdlc status`：未作为最终 gate；在 T11 文件提交前，全局 execute auth 仍可能因 HEAD truth 看不到新 formal docs 而报告 `tasks_truth_missing`。

#### 2.6 对齐结论

- 宪章/规格对齐：WI-190 聚焦只读 status/list，没有扩大到模型调用、自动修复、远端 PR diff 或其他 loop 执行逻辑。
- 代码质量：本批仅 formal docs 和 manifest/checkpoint；暂无代码变更。
- 测试质量：已定义 Batch 2-4 focused test matrix；本批待运行文档/约束验证。
- 风险：全局 program truth 仍有历史 migration/audit blocker，这是既有项目状态，不属于 WI-190 新增 blocker。

#### 2.7 批次结论

- T11 formal baseline 已完成，并已通过 `git diff --check`、`verify constraints` 与 WI-190 task guard。
- 下一步必须先提交本批 formal docs，使 `HEAD` 能被 execute authorization 识别；提交后进入 T21：实现 `src/ai_sdlc/core/loop_status.py` 的只读 summary models 和 current status reader。

### Batch 2026-06-30-002 | T21 current status reader

#### 2.1 批次范围

- 覆盖任务：`T21`
- 覆盖阶段：read-only loop status/list service
- 预读范围：`tasks.md`、`task-execution-log.md`、既有 `LoopArtifactStore`、`LoopStatus`、`ReviewRun` 模型
- 激活规则：只读读取当前 local PR review artifact，不注册 CLI，不调用模型，不写 `.ai-sdlc/`

#### 2.2 改动范围

- 新增 `src/ai_sdlc/core/loop_status.py`
- 新增 `tests/unit/test_loop_status.py`
- 更新 `specs/190-loop-engine-status-list-baseline/tasks.md`
- 更新 `specs/190-loop-engine-status-list-baseline/task-execution-log.md`

#### 2.3 改动内容

- 新增 `LoopStatusCommandStatus`、`LoopArtifactRef`、`LocalPRReviewSummary`、`LoopSummary`、`LoopStatusResult`。
- 新增 `get_loop_status(root)`，只读取 `.ai-sdlc/reviews/pr/current-review.json` 和对应 `review-run.json`。
- 对未初始化项目、无 current pointer、pointer JSON 损坏、pointer 非对象、review-run 缺失、review-run schema/JSON 损坏返回结构化 `status/result/blocker/next_action`。
- 将 local PR review 的 `review_id`、verdict、unresolved counts、base/head、provider/model、code egress、artifact paths 汇总到只读输出。
- 单元测试覆盖 happy path、no current、未初始化、malformed pointer、missing review-run、读取过程不写入 artifact。

#### 2.4 执行的命令

- `uv run pytest tests/unit/test_loop_status.py -q`
  - 结果：通过，`6 passed in 0.12s`。
- `uv run ruff check src/ai_sdlc/core/loop_status.py tests/unit/test_loop_status.py`
  - 结果：通过，`All checks passed!`。
- `git diff --check`
  - 结果：通过。

#### 2.5 验证结果

- T21 current status reader 的 focused unit tests 已通过。
- T21 新增代码通过 ruff 检查。
- 当前 diff 无 trailing whitespace 或 patch 格式问题。
- `get_loop_status(root)` 未接入 CLI，符合 T21 范围边界；CLI 注册留给 T31。

#### 2.6 对齐结论

- 宪章/规格对齐：本批只消费本地 artifact，不触发 provider/model，不生成 review pack/findings/resolution/final report。
- 代码质量：输出模型集中在 core 层，供后续 CLI human/json 输出复用。
- 测试质量：覆盖主要异常路径和只读性，下一批 T22 需要补充 list reader 的排序、current 标记和 malformed artifact 容错。
- 风险：当前仅支持 current status；历史列表能力尚未实现，`ai-sdlc loop list` 仍需 T22/T31。

#### 2.7 批次结论

- T21 已完成并通过 focused verification。
- 下一步进入 T22：在同一 core 模块新增 `list_loops(root, loop_type=local-pr-review)`，稳定列出本地 review runs 并容忍单个 malformed artifact。

### Batch 2026-06-30-003 | T22 local PR review list reader

#### 3.1 批次范围

- 覆盖任务：`T22`
- 覆盖阶段：read-only loop status/list service
- 预读范围：`loop_status.py`、`test_loop_status.py`、`LoopType`、`ReviewRun`、`LoopArtifactStore`
- 激活规则：只读扫描本地 local PR review artifacts；单个 malformed run 不阻断其他合法 run

#### 3.2 改动范围

- 更新 `src/ai_sdlc/core/loop_status.py`
- 更新 `tests/unit/test_loop_status.py`
- 更新 `specs/190-loop-engine-status-list-baseline/tasks.md`
- 更新 `specs/190-loop-engine-status-list-baseline/task-execution-log.md`

#### 3.3 改动内容

- 新增 `LoopArtifactError` 和 `LoopListResult`，用于表达 list reader 的非致命 artifact 读取错误。
- 新增 `list_loops(root, loop_type=local-pr-review)`，扫描 `.ai-sdlc/reviews/pr/*/review-run.json` 并复用 `LoopSummary` 输出。
- 输出按 `updated_at` 倒序、同时间 `loop_id` 升序稳定排序。
- 读取 `.ai-sdlc/reviews/pr/current-review.json` 标记 current run；pointer 损坏时不阻断历史列表。
- 对单个 malformed `review-run.json` 记录 `artifact_errors` 和 `malformed_count`，继续返回其他合法 runs。
- 保留只读边界：不创建目录，不写 pointer，不生成 review pack/findings/resolution/final report。

#### 3.4 执行的命令

- `uv run pytest tests/unit/test_loop_status.py -q`
  - 结果：通过，`10 passed in 0.13s`。
- `uv run ruff check src/ai_sdlc/core/loop_status.py tests/unit/test_loop_status.py`
  - 结果：通过，`All checks passed!`。
- `git diff --check`
  - 结果：通过。

#### 3.5 验证结果

- list reader 覆盖了多 run 排序、current 标记、malformed artifact 容错、无 run、只读性。
- T21 status reader 的既有 6 个用例仍通过，T22 后该测试文件共 10 个用例通过。
- 当前实现尚未注册 CLI；`ai-sdlc loop status/list` 命令面留给 T31。

#### 3.6 对齐结论

- 宪章/规格对齐：T22 只读取本地 artifact，不调用模型，不触发本地 review agent，不访问远端 PR。
- 代码质量：`get_loop_status` 与 `list_loops` 共用 summary 构造，减少后续 CLI human/json 输出分叉。
- 测试质量：异常路径覆盖到单 artifact 损坏但不覆盖 unsupported loop type CLI 展示；后续 T31 通过 CLI 测试补齐。
- 风险：list reader 当前仅支持 `local-pr-review`，其他 loop type 会返回结构化 unsupported blocker，符合本版 PRD 范围。

#### 3.7 批次结论

- T22 已完成并通过 focused verification。
- 下一步进入 T31：注册 `ai-sdlc loop status/list` CLI，并提供 human/json 输出。

### Batch 2026-06-30-004 | T31 loop status/list CLI

#### 4.1 批次范围

- 覆盖任务：`T31`
- 覆盖阶段：ai-sdlc loop CLI registration
- 预读范围：`main.py`、`__main__.py`、`pr_review_cmd.py`、`test_cli_pr_review.py`、`test_cli_module_invocation.py`
- 激活规则：CLI 只读输出本地 Loop artifact truth；不得触发 adapter 写入、模型调用或 provider runner

#### 4.2 改动范围

- 新增 `src/ai_sdlc/cli/loop_cmd.py`
- 更新 `src/ai_sdlc/cli/main.py`
- 更新 `src/ai_sdlc/__main__.py`
- 新增 `tests/integration/test_cli_loop.py`
- 更新 `specs/190-loop-engine-status-list-baseline/tasks.md`
- 更新 `specs/190-loop-engine-status-list-baseline/task-execution-log.md`

#### 4.3 改动内容

- 注册 `ai-sdlc loop status` 和 `ai-sdlc loop list`。
- 支持 `--json` 输出，直接序列化 `LoopStatusResult` / `LoopListResult`。
- 支持 human 输出，包含 `Result`、`Next`、blocker、loop type、loop id、review id、status、base/head、provider/model、code egress、artifact paths。
- 将 `loop` 加入 CLI read-only bypass，避免查询命令触发 IDE adapter 写入。
- 将 `loop` 加入 `python -m ai_sdlc --help` fallback 命令列表。
- 集成测试覆盖 help、status JSON、status human、list JSON + malformed artifact、missing project JSON、module fallback help。

#### 4.4 执行的命令

- `uv run pytest tests/integration/test_cli_loop.py tests/unit/test_loop_status.py -q`
  - 结果：通过，`16 passed in 0.91s`。
- `uv run ruff check src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/__main__.py src/ai_sdlc/core/loop_status.py tests/integration/test_cli_loop.py tests/unit/test_loop_status.py`
  - 结果：通过，`All checks passed!`。
- `git diff --check`
  - 结果：通过。

#### 4.5 验证结果

- `ai-sdlc loop status --json` 能返回 current local PR review summary。
- `ai-sdlc loop status` human 输出包含用户可读的当前 loop、review 与 artifact 信息。
- `ai-sdlc loop list --json` 能返回历史 runs、current 标记、malformed artifact 摘要。
- missing project 时 JSON 输出结构化 blocker，退出码为 1。
- `python -m ai_sdlc --help` fallback 已包含 `loop`。

#### 4.6 对齐结论

- 宪章/规格对齐：CLI 只读取 T21/T22 core reader 结果，不调用模型、不调用 Codex 云端 review、不写 `.ai-sdlc/` artifact。
- 代码质量：CLI human/json 输出与 `pr-review` 命令风格一致，且注册为 read-only bypass。
- 测试质量：T31 focused integration 覆盖核心命令面；T32 还需补 command discovery 专项断言。
- 风险：human 输出格式是首版简洁文本，后续可按用户反馈优化，但不影响 JSON 合约。

#### 4.7 批次结论

- T31 已完成并通过 focused verification。
- 下一步进入 T32：更新 command discovery 测试，确认 `ai-sdlc loop status/list` 被框架自动发现。
