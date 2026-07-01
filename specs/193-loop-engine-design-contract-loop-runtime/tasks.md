---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
  - "specs/192-loop-engine-requirement-loop-runtime/spec.md"
---
# 任务分解：Loop Engine Design Contract Loop Runtime

**编号**：`193-loop-engine-design-contract-loop-runtime` | **日期**：2026-07-01
**来源**：plan.md + spec.md

---

## 分批策略

```text
Batch 1: formal baseline freeze and linkage
Batch 2: design-contract runtime
Batch 3: status/list and CLI
Batch 4: docs, constraints, final regression, PR review
```

---

## Batch 1：formal baseline freeze and linkage

### Task 1.1 冻结 design-contract formal docs

- **任务编号**：T11
- **优先级**：P0
- **依赖**：WI-192 已合并
- **文件**：spec.md, plan.md, tasks.md, task-execution-log.md, program-manifest.yaml, .ai-sdlc/state/checkpoint.yml
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 WI-193 只交付 `design-contract` loop
  2. `plan.md` 覆盖 runtime、CLI、status/list、docs/constraints 四阶段
  3. `tasks.md` 有可执行任务、文件范围和验证命令
  4. work item 已 link，program truth 已 sync
- **验证**：`git diff --check`、`uv run ai-sdlc verify constraints`、`uv run ai-sdlc program truth sync --execute --yes`

---

## Batch 2：design-contract runtime

### Task 2.1 新增 design-contract artifact models

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/core/design_contract_loop.py, tests/unit/test_design_contract_loop.py
- **可并行**：否
- **验收标准**：
  1. `DesignContractInput`、`ContractCoverageItem`、`DesignContractReport`、`DesignContractClose` 均有 schema validation
  2. unsafe loop id、缺失 docs、坏 work item path 均 fail-readable
  3. artifact 写入路径稳定在 `.ai-sdlc/loops/design-contract/<loop-id>/`
- **验证**：`uv run pytest tests/unit/test_design_contract_loop.py -q`

### Task 2.2 实现 check runtime

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/design_contract_loop.py, tests/unit/test_design_contract_loop.py
- **可并行**：否
- **验收标准**：
  1. 完整 docs 生成 passed report、coverage matrix 和 current pointer
  2. `--dry-run` 路径不写任何 design-contract artifact
  3. 缺失 docs、模板占位、FR/SC 未覆盖、任务缺少验收或验证均进入 `needs_fix`
  4. report JSON 与 markdown 都包含 blocker summary 和 next action
- **验证**：`uv run pytest tests/unit/test_design_contract_loop.py -q`

### Task 2.3 实现 close runtime

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/core/design_contract_loop.py, tests/unit/test_design_contract_loop.py
- **可并行**：否
- **验收标准**：
  1. 无 blocker 的最新 report 可 `close --yes`
  2. 有 blocker、缺少 report、未传 `--yes` 均 fail-closed
  3. close 后 loop-run 状态为 `closed`，next action 指向 implementation loop
- **验证**：`uv run pytest tests/unit/test_design_contract_loop.py -q`

---

## Batch 3：status/list and CLI

### Task 3.1 接入 loop status/list

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：src/ai_sdlc/core/loop_status.py, tests/unit/test_loop_status.py
- **可并行**：否
- **验收标准**：
  1. `get_loop_status(..., loop_type="design-contract")` 读取 current pointer
  2. `list_loops(..., loop_type="design-contract")` 列出历史 runs 并标记 current
  3. malformed current target 返回 blocker，不隐藏其他合法历史 run
  4. local-pr-review 与 requirement 既有行为不回归
- **验证**：`uv run pytest tests/unit/test_loop_status.py -q`

### Task 3.2 接入 CLI

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T22, T23, T31
- **文件**：src/ai_sdlc/cli/loop_cmd.py, tests/integration/test_cli_loop.py
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc loop design-contract check/status/close` 可用
  2. `--json` 输出不混入 Rich 文本或 adapter notice
  3. `check --dry-run` 不触发 artifact 写入或 adapter 写入
  4. `close` 在不能关闭时返回非零退出码
  5. `loop status/list --type design-contract` CLI 可读
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
  1. README 说明 design-contract 是 implementation 前置合同检查
  2. verify constraints 能检查 WI-193 runtime、CLI、用户文档 surface
  3. 文档明确 P0 不调用模型、不改业务代码、不进入 frontend evidence
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`、`uv run ai-sdlc verify constraints`

### Task 4.2 完成最终回归与 PR 收口

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：specs/193-loop-engine-design-contract-loop-runtime/task-execution-log.md, program-manifest.yaml, .ai-sdlc/state/codex-handoff.md
- **可并行**：否
- **验收标准**：
  1. focused tests、ruff、mypy、diff check、verify constraints、program truth sync 通过
  2. `uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime` 通过
  3. 分支已提交、推送、开 PR、请求 Codex review
  4. Codex review 无 actionable issues 且 required checks 通过后合并
- **验证**：
  - `uv run pytest tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - `uv run ruff check src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py tests/unit/test_design_contract_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
  - `uv run mypy src/ai_sdlc/core/design_contract_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - `git diff --check`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc workitem close-check --wi specs/193-loop-engine-design-contract-loop-runtime`
