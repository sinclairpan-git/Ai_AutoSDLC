# 任务分解：Loop Engine Status/List Baseline

**编号**：`190-loop-engine-status-list-baseline`
**日期**：2026-06-29
**来源**：`spec.md` + `plan.md`

---

## 分批策略

```text
Batch 1: formal baseline and checkpoint linkage
Batch 2: read-only loop status/list service
Batch 3: ai-sdlc loop CLI registration
Batch 4: docs, verification, and closeout evidence
```

---

## Batch 1：formal baseline and checkpoint linkage

### Task 1.1 Freeze WI-190 formal baseline

- task_id: T11
- status: done
- goal: 冻结 WI-190 的 formal PRD、实施计划、任务分解和 checkpoint linkage
- priority: P0
- depends:
  - none
- scope:
  - specs/190-loop-engine-status-list-baseline/spec.md
  - specs/190-loop-engine-status-list-baseline/plan.md
  - specs/190-loop-engine-status-list-baseline/tasks.md
  - specs/190-loop-engine-status-list-baseline/task-execution-log.md
  - program-manifest.yaml
  - .ai-sdlc/project/config/project-state.yaml
- acceptance:
  - WI-190 formal docs 位于 specs/190-loop-engine-status-list-baseline/
  - PRD 明确 status/list 只读、只消费 local PR review artifact、不调用模型
  - plan 给出 core/CLI/tests 文件面和只读验证策略
  - checkpoint 链接到 190-loop-engine-status-list-baseline
- verify:
  - uv run ai-sdlc program truth sync --execute --yes
  - uv run ai-sdlc workitem link --wi-id 190-loop-engine-status-list-baseline --plan-uri specs/190-loop-engine-status-list-baseline/plan.md
  - git diff --check
- notes:
  - 验收标准见 acceptance 字段。

## Batch 2：read-only loop status/list service

### Task 2.1 Add Loop status summary models and current status reader

- task_id: T21
- status: done
- goal: 新增 Loop status 只读 summary models，并能读取当前 local PR review run
- priority: P0
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/loop_status.py
  - tests/unit/test_loop_status.py
- acceptance:
  - 新增 LoopSummary、LocalPRReviewSummary、LoopStatusResult 等只读输出模型
  - get_loop_status(root) 能读取 .ai-sdlc/reviews/pr/current-review.json 和对应 review-run.json
  - no current、missing pointer target、malformed JSON、schema 不兼容均返回结构化 blocker 和 next action
  - get_loop_status(root) 不写入任何 .ai-sdlc/ 文件
- verify:
  - uv run pytest tests/unit/test_loop_status.py -q
- notes:
  - 验收标准见 acceptance 字段。

### Task 2.2 Add Loop list reader for local PR review runs

- task_id: T22
- status: todo
- goal: 新增 local PR review loop list reader，稳定列出历史 review runs
- priority: P0
- depends:
  - T21
- scope:
  - src/ai_sdlc/core/loop_status.py
  - tests/unit/test_loop_status.py
- acceptance:
  - list_loops(root, loop_type=local-pr-review) 扫描 .ai-sdlc/reviews/pr/*/review-run.json
  - 多个 run 能稳定排序，并正确标记 current item
  - 单个 malformed artifact 不阻断其他合法 runs
  - list result 包含 malformed count 和 artifact error 摘要
- verify:
  - uv run pytest tests/unit/test_loop_status.py -q
- notes:
  - 验收标准见 acceptance 字段。

## Batch 3：ai-sdlc loop CLI registration

### Task 3.1 Register ai-sdlc loop status/list

- task_id: T31
- status: todo
- goal: 注册 ai-sdlc loop status/list CLI，并提供 human/json 输出
- priority: P0
- depends:
  - T21
  - T22
- scope:
  - src/ai_sdlc/cli/loop_cmd.py
  - src/ai_sdlc/cli/main.py
  - src/ai_sdlc/__main__.py
  - tests/integration/test_cli_loop.py
- acceptance:
  - ai-sdlc loop status 和 ai-sdlc loop status --json 可用
  - ai-sdlc loop list 和 ai-sdlc loop list --json 可用
  - human 输出包含 Result、Next、blocker、loop type、review id、status、artifact paths
  - loop 命令加入 CLI read-only bypass，不触发 adapter 写入
  - python -m ai_sdlc --help fallback 包含 loop
- verify:
  - uv run pytest tests/integration/test_cli_loop.py -q
- notes:
  - 验收标准见 acceptance 字段。

### Task 3.2 Update command discovery

- task_id: T32
- status: todo
- goal: 更新 command discovery，确保 loop status/list 被框架发现
- priority: P0
- depends:
  - T31
- scope:
  - tests/unit/test_command_names.py
  - src/ai_sdlc/cli/command_names.py
- acceptance:
  - command discovery 包含 ai-sdlc loop status
  - command discovery 包含 ai-sdlc loop list
  - 不破坏既有 pr-review command discovery
- verify:
  - uv run pytest tests/unit/test_command_names.py -q
- notes:
  - 验收标准见 acceptance 字段。

## Batch 4：docs, verification, and closeout evidence

### Task 4.1 Align docs and verify constraints

- task_id: T41
- status: todo
- goal: 对齐用户文档和 verify constraints，说明 loop status/list 的只读边界
- priority: P1
- depends:
  - T31
  - T32
- scope:
  - README.md
  - docs/pull-request-checklist.zh.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
  - specs/190-loop-engine-status-list-baseline/task-execution-log.md
- acceptance:
  - 用户文档说明 loop status/list 是只读统一状态入口
  - 文档不暗示 loop status/list 会调用模型、修复代码或读取远端 PR
  - verify constraints 或 focused tests 覆盖新增命令的 no-model/no-cloud-review 文档边界
  - task execution log 记录每批命令、结果和 closeout 状态
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints
- notes:
  - 验收标准见 acceptance 字段。

### Task 4.2 Final regression and work item close evidence

- task_id: T42
- status: todo
- goal: 完成最终回归、任务状态同步和 work item close evidence
- priority: P0
- depends:
  - T41
- scope:
  - specs/190-loop-engine-status-list-baseline/tasks.md
  - specs/190-loop-engine-status-list-baseline/task-execution-log.md
- acceptance:
  - 所有 P0 tasks 标记为 done，P1 文档任务按实际完成状态记录
  - focused test matrix、git diff --check、verify constraints 已记录
  - workitem close-check 在干净或明确记录的 closeout 状态下运行
- verify:
  - git diff --check
  - uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_command_names.py -q
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc workitem close-check --wi specs/190-loop-engine-status-list-baseline
- notes:
  - 验收标准见 acceptance 字段。

## 全局约束

1. `loop status/list` 必须只读，不得生成 review pack、findings、resolution、final report 或 current pointer。
2. 不得调用 Codex 云端 PR review。
3. 不得在 CI workflow 中加入 GPT、Claude、DeepSeek、GLM、Codex 或其他模型调用。
4. 不得把 `loop status/list` 输出包装成合规强证明；它只是本地 artifact truth 的索引和状态摘要。
5. 每个 batch 完成后必须更新 `task-execution-log.md` 和 handoff。
