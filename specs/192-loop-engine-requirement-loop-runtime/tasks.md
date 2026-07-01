---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
---
# 任务分解：Loop Engine Requirement Loop Runtime

**编号**：`192-loop-engine-requirement-loop-runtime` | **日期**：2026-06-30
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline and linkage
Batch 2: requirement loop runtime
Batch 3: loop status/list and CLI integration
Batch 4: docs, constraints, verification, closeout
```

---

## Batch 1：formal baseline and linkage

### Task 1.1 Freeze WI-192 formal docs

- task_id: T11
- status: done
- goal: 冻结 requirement loop 的 PRD、实施计划、任务拆解和初始执行日志
- priority: P0
- depends:
  - none
- scope:
  - specs/192-loop-engine-requirement-loop-runtime/spec.md
  - specs/192-loop-engine-requirement-loop-runtime/plan.md
  - specs/192-loop-engine-requirement-loop-runtime/tasks.md
  - specs/192-loop-engine-requirement-loop-runtime/task-execution-log.md
  - program-manifest.yaml
  - .ai-sdlc/project/config/project-state.yaml
- acceptance:
  - formal docs 位于 canonical `specs/192-loop-engine-requirement-loop-runtime/`
  - spec 明确本 PR 只交付 requirement loop，不越界到 design/implementation/frontend
  - plan 给出 core/CLI/tests/docs 文件面
  - tasks.md 存在可执行任务并明确验证命令
- verify:
  - uv run ai-sdlc workitem link --wi-id 192-loop-engine-requirement-loop-runtime --plan-uri specs/192-loop-engine-requirement-loop-runtime/plan.md
  - uv run ai-sdlc program truth sync --execute --yes
  - git diff --check

## Batch 2：requirement loop runtime

### Task 2.1 Add requirement loop artifact models and start flow

- task_id: T21
- status: done
- goal: 新增 requirement intake/freeze 数据模型和 start runtime
- priority: P0
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/requirement_loop.py
  - tests/unit/test_requirement_loop.py
- acceptance:
  - `start_requirement_loop` 支持 idea 与 input file
  - 写入 loop-run、requirement-intake、brief、clarification questions、acceptance checklist、current pointer
  - `--dry-run` 等价 core option 不写文件
  - 缺少 idea/input、文件不可读、空需求均 fail-readable
  - 无 acceptance 时状态为 `needs_user`
- verify:
  - uv run pytest tests/unit/test_requirement_loop.py -q

### Task 2.2 Add requirement freeze flow

- task_id: T22
- status: done
- goal: 实现 requirement loop 显式冻结和 fail-closed 验收门禁
- priority: P0
- depends:
  - T21
- scope:
  - src/ai_sdlc/core/requirement_loop.py
  - tests/unit/test_requirement_loop.py
- acceptance:
  - `freeze_requirement_loop` 要求当前 loop 和 `--yes`
  - 无 acceptance criteria 时不得冻结
  - 成功冻结后写入 requirement-freeze.json，loop-run 状态为 `closed`
  - 冻结后 next action 指向 design-contract loop
  - freeze 不调用模型、不改代码
- verify:
  - uv run pytest tests/unit/test_requirement_loop.py -q

## Batch 3：loop status/list and CLI integration

### Task 3.1 Extend loop status/list for requirement type

- task_id: T31
- status: done
- goal: 让统一 loop status/list 支持 `--type requirement`
- priority: P0
- depends:
  - T21
  - T22
- scope:
  - src/ai_sdlc/core/loop_status.py
  - tests/unit/test_loop_status.py
- acceptance:
  - `get_loop_status(root, loop_type=requirement)` 读取 current requirement pointer
  - `list_loops(root, loop_type=requirement)` 扫描 requirement loop-run
  - malformed requirement artifact 不隐藏其他合法 run
  - 默认 local-pr-review 行为保持不变
- verify:
  - uv run pytest tests/unit/test_loop_status.py -q

### Task 3.2 Add ai-sdlc loop requirement CLI

- task_id: T32
- status: done
- goal: 注册 `ai-sdlc loop requirement start/status/freeze`
- priority: P0
- depends:
  - T31
- scope:
  - src/ai_sdlc/cli/loop_cmd.py
  - tests/integration/test_cli_loop.py
- acceptance:
  - start/status/freeze human 输出包含 Result / Next
  - start/status/freeze `--json` 输出可解析
  - `loop status --type requirement` 和 `loop list --type requirement` 可用
  - command help 不破坏既有 status/list
- verify:
  - uv run pytest tests/integration/test_cli_loop.py -q

## Batch 4：docs, constraints, verification, closeout

### Task 4.1 Align README and verify constraints

- task_id: T41
- status: done
- goal: 对齐用户文档和约束检查，防止 requirement loop 被误解为模型/实现执行器
- priority: P1
- depends:
  - T32
- scope:
  - README.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
  - specs/192-loop-engine-requirement-loop-runtime/task-execution-log.md
- acceptance:
  - README 说明 requirement loop 的 start/status/freeze 和设计边界
  - verify constraints 覆盖 command/docs surface
  - 文档明确 freeze 后下一步是 design-contract loop
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints

### Task 4.2 Final regression and closeout

- task_id: T42
- status: done
- goal: 完成 focused regression、任务状态同步、execution log 和 close-check
- priority: P0
- depends:
  - T41
- scope:
  - specs/192-loop-engine-requirement-loop-runtime/tasks.md
  - specs/192-loop-engine-requirement-loop-runtime/task-execution-log.md
  - program-manifest.yaml
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/work-items/192-loop-engine-requirement-loop-runtime/codex-handoff.md
- acceptance:
  - 所有 tasks 状态符合实际完成情况
  - focused pytest、ruff、mypy、verify constraints、close-check 均记录
  - PR 可以进入 Codex review
- verify:
  - git diff --check
  - uv run pytest tests/unit/test_requirement_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q
  - uv run ruff check src/ai_sdlc/core/requirement_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py tests/unit/test_requirement_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py
  - uv run mypy src/ai_sdlc/core/requirement_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc workitem close-check --wi specs/192-loop-engine-requirement-loop-runtime

## 全局约束

1. 本 PR 只交付 `requirement` loop，不实现 design-contract、implementation、frontend-evidence。
2. Requirement loop 不得调用模型、provider、Codex 云端 review 或 CI 模型请求。
3. Requirement loop 不得修改业务代码或前端代码。
4. Freeze 必须显式确认；无 acceptance criteria 不得冻结。
5. 每批完成后必须更新 execution log 和 handoff。
