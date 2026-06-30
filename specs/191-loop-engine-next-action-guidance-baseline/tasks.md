# 任务分解：Loop Engine Next Action Guidance Baseline

**编号**：`191-loop-engine-next-action-guidance-baseline`
**日期**：2026-06-30
**来源**：`spec.md` + `plan.md`

---

## 分批策略

```text
Batch 1: formal baseline and checkpoint linkage
Batch 2: next guidance core model and derivation
Batch 3: ai-sdlc loop CLI guidance output
Batch 4: docs, constraints, and closeout evidence
```

---

## Batch 1：formal baseline and checkpoint linkage

### Task 1.1 Freeze WI-191 formal baseline

- task_id: T11
- status: done
- goal: 冻结 WI-191 的 formal PRD、实施计划、任务分解和初始 execution log
- priority: P0
- depends:
  - none
- scope:
  - specs/191-loop-engine-next-action-guidance-baseline/spec.md
  - specs/191-loop-engine-next-action-guidance-baseline/plan.md
  - specs/191-loop-engine-next-action-guidance-baseline/tasks.md
  - specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md
  - program-manifest.yaml
  - .ai-sdlc/project/config/project-state.yaml
  - .ai-sdlc/state/checkpoint.yml
- acceptance:
  - WI-191 formal docs 位于 specs/191-loop-engine-next-action-guidance-baseline/
  - PRD 明确 next guidance 是只读推导，不执行命令、不调用模型、不写 artifact
  - plan 给出 core/CLI/tests/docs 文件面和 read-only 验证策略
  - tasks.md 存在下一条 status=todo 的可执行任务
  - checkpoint 链接到 191-loop-engine-next-action-guidance-baseline
- verify:
  - uv run ai-sdlc workitem link --wi-id 191-loop-engine-next-action-guidance-baseline --plan-uri specs/191-loop-engine-next-action-guidance-baseline/plan.md
  - uv run ai-sdlc program truth sync --execute --yes
  - uv run ai-sdlc workitem guard
  - git diff --check
- notes:
  - 已完成文档冻结；后续产品代码从 T21 开始。

## Batch 2：next guidance core model and derivation

### Task 2.1 Add Loop next action guidance model

- task_id: T21
- status: done
- goal: 新增结构化 next guidance 模型，并保持 next_action 字符串兼容
- priority: P0
- depends:
  - T11
- scope:
  - src/ai_sdlc/core/loop_status.py
  - tests/unit/test_loop_status.py
- acceptance:
  - 新增 LoopNextActionGuidance 或等价 Pydantic model
  - LoopStatusResult、LoopListResult、LoopSummary 均能输出 next_guidance
  - 现有 next_action 字段仍保留且语义不变
  - no current、uninitialized、malformed pointer、missing review-run 均有结构化 guidance
  - guidance 推导不写入 .ai-sdlc/
- verify:
  - uv run pytest tests/unit/test_loop_status.py -q
- notes:
  - 验收标准见 acceptance 字段。
  - 不可并行；这是 CLI 输出和文档约束的基础。

### Task 2.2 Derive guidance for local PR review states

- task_id: T22
- status: done
- goal: 为 local PR review 的关键状态推导下一步命令、原因、影响和证据
- priority: P0
- depends:
  - T21
- scope:
  - src/ai_sdlc/core/loop_status.py
  - tests/unit/test_loop_status.py
- acceptance:
  - fresh needs_fix 推荐 ai-sdlc pr-review fix，requires_model=false，writes_artifacts=true，writes_code=false
  - post-fix needs_fix 若 next_action 已指向 ai-sdlc pr-review rerun，必须推荐 rerun，requires_model=true
  - passed 推荐 ai-sdlc pr-review close，requires_model=false，writes_artifacts=true，writes_code=false
  - needs_review 或需要复审时推荐 ai-sdlc pr-review rerun，并标明后续命令可能调用本地独立 review agent
  - blocked/needs_user 优先展示 blocker 和人工处理动作，不建议 close
  - closed 标记 no action 或 inspect final report
  - loop list 的 current item 有与自身状态匹配的 actionable guidance
  - loop list 的非 current item 只给 inspect-only guidance，不得推荐 pr-review fix/rerun/close
  - loop list 遇到 malformed current pointer 但存在历史 run 时，顶层 guidance 必须是 blocked repair guidance
- verify:
  - uv run pytest tests/unit/test_loop_status.py -q
- notes:
  - 验收标准见 acceptance 字段。
  - 不可并行；状态矩阵必须先在 core 层稳定。

## Batch 3：ai-sdlc loop CLI guidance output

### Task 3.1 Render next guidance in loop human output

- task_id: T31
- status: done
- goal: 在 ai-sdlc loop status/list human 输出中展示小白友好的 guidance
- priority: P0
- depends:
  - T21
  - T22
- scope:
  - src/ai_sdlc/cli/loop_cmd.py
  - tests/integration/test_cli_loop.py
- acceptance:
  - loop status human 输出包含 Next command、Why、Model call、Writes artifacts、Writes code、Evidence
  - loop list human 输出为每个合法 loop item 展示 guidance，非 current item 只显示 inspect-only guidance
  - blocked/no_current human 输出也展示 guidance，不输出 Python traceback
  - JSON 输出只新增字段，不混入 Rich 文本
- verify:
  - uv run pytest tests/integration/test_cli_loop.py -q
- notes:
  - 验收标准见 acceptance 字段。
  - 可在 T21/T22 完成后落地；不改变 pr-review 命令语义。

### Task 3.2 Preserve read-only boundary in CLI integration

- task_id: T32
- status: done
- goal: 验证 loop guidance 输出不触发 provider、模型调用或 artifact 写入
- priority: P0
- depends:
  - T31
- scope:
  - tests/integration/test_cli_loop.py
  - tests/unit/test_loop_status.py
- acceptance:
  - loop status/list 前后 .ai-sdlc/ 文件快照不变
  - provider runner 或 local-agent mock 未被调用
  - guidance 中的 requires_model 只描述后续 pr-review 命令，不代表当前 loop 命令调用模型
- verify:
  - uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q
- notes:
  - 验收标准见 acceptance 字段。
  - 不可省略；这是 WI-190 只读边界的回归保护。

## Batch 4：docs, constraints, and closeout evidence

### Task 4.1 Align docs and verify constraints

- task_id: T41
- status: done
- goal: 对齐用户文档和 verify constraints，说明 next guidance 的只读导航边界
- priority: P1
- depends:
  - T31
  - T32
- scope:
  - README.md
  - docs/pull-request-checklist.zh.md
  - src/ai_sdlc/core/verify_constraints.py
  - tests/unit/test_verify_constraints.py
  - specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md
- acceptance:
  - README 说明 loop status/list 会展示 next guidance，但不会执行下一步
  - PR checklist 说明 guidance 不是云端 review、不是模型调用、不是合规强证明
  - verify constraints 覆盖新增文档边界
  - task execution log 记录每批命令、结果和 closeout 状态
- verify:
  - uv run pytest tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints
- notes:
  - 验收标准见 acceptance 字段。
  - 可与最终回归前半段并行准备，但必须在 closeout 前完成。

### Task 4.2 Final regression and work item close evidence

- task_id: T42
- status: done
- goal: 完成最终回归、任务状态同步和 work item close evidence
- priority: P0
- depends:
  - T41
- scope:
  - specs/191-loop-engine-next-action-guidance-baseline/tasks.md
  - specs/191-loop-engine-next-action-guidance-baseline/task-execution-log.md
  - .ai-sdlc/state/codex-handoff.md
  - .ai-sdlc/work-items/191-loop-engine-next-action-guidance-baseline/codex-handoff.md
  - program-manifest.yaml
- acceptance:
  - 所有 P0 tasks 标记为 done，P1 文档任务按实际完成状态记录
  - focused test matrix、git diff --check、verify constraints 已记录
  - workitem close-check 在干净或明确记录的 closeout 状态下运行
  - handoff 包含当前 goal、state、changed files、tests、risks 和下一步
- verify:
  - git diff --check
  - uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q
  - uv run ai-sdlc verify constraints
  - uv run ai-sdlc workitem close-check --wi specs/191-loop-engine-next-action-guidance-baseline
- notes:
  - 验收标准见 acceptance 字段。
  - closeout 前不得遗漏 handoff 更新。

## 全局约束

1. `loop status/list` 必须只读，不得生成 review pack、findings、resolution、final report 或 current pointer。
2. 不得调用 Codex 云端 PR review。
3. 不得在 CI workflow 中加入 GPT、Claude、DeepSeek、GLM、Codex 或其他模型调用。
4. guidance 可说明后续命令可能调用用户本地独立 review agent，但当前 loop 命令不得调用模型。
5. 不得把 guidance 输出包装成合规强证明；它只是本地 artifact truth 的导航说明。
6. 每个 batch 完成后必须更新 `task-execution-log.md` 和 handoff。
