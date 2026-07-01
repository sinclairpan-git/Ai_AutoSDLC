# 任务分解：Loop Engine Implementation Loop Runtime

**编号**：`194-loop-engine-implementation-loop-runtime` | **日期**：2026-07-01
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline freeze and linkage
Batch 2: implementation runtime
Batch 3: status/list and CLI
Batch 4: docs, constraints, final regression, PR review
```

## 当前任务状态

- [x] `T11` 冻结 implementation formal docs
- [x] `T21` 新增 implementation artifact models and store
- [x] `T22` 实现 start runtime
- [x] `T23` 实现 record runtime
- [x] `T24` 实现 close runtime
- [x] `T31` 接入 loop status/list
- [x] `T32` 接入 CLI
- [x] `T41` 对齐用户文档和约束面
- [x] `T42` 完成最终回归与 PR 收口准备（本地验证已通过；后续按本仓 PR 协议执行提交、PR、Codex review、checks、merge）

---

## Batch 1：formal baseline freeze and linkage

### Task 1.1 冻结 implementation formal docs

- **任务编号**：T11
- **优先级**：P0
- **依赖**：WI-193 已合并
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md, program-manifest.yaml, .ai-sdlc/state/checkpoint.yml
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 WI-194 只交付 `implementation` loop
  2. `plan.md` 覆盖 runtime、CLI、status/list、docs/constraints 四阶段
  3. `tasks.md` 有可执行任务、文件范围和验证命令
  4. work item 已 link，program truth 已 sync
- **验证**：`git diff --check`、`uv run ai-sdlc workitem link --wi-id 194-loop-engine-implementation-loop-runtime --plan-uri specs/194-loop-engine-implementation-loop-runtime/plan.md`、`uv run ai-sdlc program truth sync --execute --yes`

---

## Batch 2：implementation runtime

### Task 2.1 新增 implementation artifact models and store

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/core/implementation_models.py, src/ai_sdlc/core/implementation_store.py, tests/unit/test_implementation_loop.py
- **可并行**：否
- **验收标准**：
  1. `ImplementationInput`、`ImplementationTaskItem`、`ImplementationTaskProgress`、`ImplementationReport`、`ImplementationClose` 均有 schema validation
  2. unsafe loop id、缺失 work item、坏 design-contract id 均 fail-readable
  3. artifact 写入路径稳定在 `.ai-sdlc/loops/implementation/<loop-id>/`
- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`

### Task 2.2 实现 start runtime

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/implementation_loop.py, tests/unit/test_implementation_loop.py
- **可并行**：否
- **验收标准**：
  1. closed design-contract + parseable tasks 生成 created/running implementation loop
  2. `--dry-run` 路径不写任何 implementation artifact
  3. missing/unclosed/mismatched design-contract 均 blocked
  4. tasks snapshot 只把 P0/P1 作为 required
- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`

### Task 2.3 实现 record runtime

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/core/implementation_loop.py, tests/unit/test_implementation_loop.py
- **可并行**：否
- **验收标准**：
  1. known task 可记录 pending/in_progress/done/blocked
  2. done 必须携带 evidence 或 verification command
  3. unknown task、非法 status、坏 current pointer 均 blocked
  4. record 后刷新 progress、verification-evidence、report 和 loop-run
- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`

### Task 2.4 实现 close runtime

- **任务编号**：T24
- **优先级**：P0
- **依赖**：T23
- **文件**：src/ai_sdlc/core/implementation_loop.py, tests/unit/test_implementation_loop.py
- **可并行**：否
- **验收标准**：
  1. required tasks 全部 done 且有证据后可 `close --yes`
  2. incomplete、blocked、missing evidence、未传 `--yes` 均 fail-closed
  3. close 后 loop-run 状态为 `closed`，next action 指向 frontend-evidence 或 local-pr-review
- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`

---

## Batch 3：status/list and CLI

### Task 3.1 接入 loop status/list

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：src/ai_sdlc/core/loop_status.py, tests/unit/test_loop_status.py
- **可并行**：否
- **验收标准**：
  1. `get_loop_status(..., loop_type="implementation")` 读取 current pointer
  2. `list_loops(..., loop_type="implementation")` 列出历史 runs 并标记 current
  3. malformed current target 返回 blocker，不隐藏其他合法历史 run
  4. local-pr-review、requirement 与 design-contract 既有行为不回归
- **验证**：`uv run pytest tests/unit/test_loop_status.py -q`

### Task 3.2 接入 CLI

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T22, T23, T24, T31
- **文件**：src/ai_sdlc/cli/loop_cmd.py, tests/integration/test_cli_loop.py
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc loop implementation start/record/status/close` 可用
  2. `--json` 输出不混入 Rich 文本或 adapter notice
  3. `start --dry-run` 不触发 artifact 写入或 adapter 写入
  4. `close` 在不能关闭时返回非零退出码
  5. `loop status/list --type implementation` CLI 可读
- **验证**：`uv run pytest tests/integration/test_cli_loop.py -q`

---

## Batch 4：docs, constraints, final regression, PR review

### Task 4.1 对齐用户文档和约束面

- **任务编号**：T41
- **优先级**：P1
- **依赖**：T31, T32
- **文件**：README.md, src/ai_sdlc/core/verify_constraints.py, tests/unit/test_verify_constraints.py
- **可并行**：否
- **验收标准**：
  1. README 说明 implementation loop 是 design-contract 后的实现证据闭环
  2. verify constraints 能检查 WI-194 runtime、CLI、用户文档 surface
  3. 文档明确 P0 不调用模型、不写业务代码、不进入 frontend evidence 的实现执行
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`、`uv run ai-sdlc verify constraints`

### Task 4.2 完成最终回归与 PR 收口

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：specs/194-loop-engine-implementation-loop-runtime/task-execution-log.md, program-manifest.yaml, .ai-sdlc/state/codex-handoff.md
- **可并行**：否
- **验收标准**：
  1. focused tests、ruff、mypy、diff check、verify constraints、program truth sync 通过
  2. `uv run ai-sdlc workitem close-check --wi specs/194-loop-engine-implementation-loop-runtime` 通过
  3. 分支已提交、推送、开 PR、请求 Codex review
  4. Codex review 无 actionable issues 且 required checks 通过后合并
- **验证**：
  - `uv run pytest tests/unit/test_implementation_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - `uv run ruff check src/ai_sdlc/core/implementation_models.py src/ai_sdlc/core/implementation_store.py src/ai_sdlc/core/implementation_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py tests/unit/test_implementation_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
  - `uv run mypy src/ai_sdlc/core/implementation_models.py src/ai_sdlc/core/implementation_store.py src/ai_sdlc/core/implementation_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - `git diff --check`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc workitem close-check --wi specs/194-loop-engine-implementation-loop-runtime`

---

## 全局约束

- 本 work item 不得声称 frontend-evidence 或五类 Loop 全部完成。
- implementation loop runtime 不得调用模型，不得硬编码 GitHub 或远端 PR。
- 所有新增用户可见注释和文档默认使用简体中文；代码注释仅解释复杂边界。
