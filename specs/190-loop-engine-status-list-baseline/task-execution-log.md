# 任务执行日志：Loop Engine Status/List Baseline

**功能编号**：`190-loop-engine-status-list-baseline`
**创建日期**：2026-06-29
**状态**：Batch 2 T21 current status reader completed，等待 T22 list reader

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
