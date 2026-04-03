---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
---
# 任务分解：Frontend Contract Runtime Attachment Baseline

**编号**：`014-frontend-contract-runtime-attachment-baseline` | **日期**：2026-04-03  
**来源**：plan.md + spec.md（FR-014-001 ~ FR-014-016 / SC-014-001 ~ SC-014-005）

---

## 分批策略

```text
Batch 1: runtime attachment truth freeze
Batch 2: attachment contract and failure honesty baseline
Batch 3: implementation handoff and verification freeze
Batch 4: runtime attachment helper slice
Batch 5: runner verify-context wiring slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `014` 不得重新定义 `013` 已冻结的 provider artifact contract、scanner payload 或 canonical file naming。
- `014` 不得改写 `012` 已冻结的 verify mainline、`VerificationGate`、CLI verify 或 gate aggregation。
- `014` 不得在当前 child work item 中直接启用 runner 自动扫描、program auto-integration、registry attachment、auto-refresh、auto-fix 或 remediation workflow。
- `014` 不得默认扩张新的顶层命令面；现有 `scan` export surface 只作为上游显式入口被引用。
- `014` 只冻结 runtime attachment baseline，不默认决定任何未显式授权的 runtime side effect。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`tests/unit/test_frontend_contract_runtime_attachment.py`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`src/ai_sdlc/core/runner.py`、`tests/unit/test_runner_confirm.py`、`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- 当前首批实现只放行 runtime attachment helper，不放行 `run_cmd.py`、`runner.py`、`program_cmd.py`、registry 或 remediation。
- 当前第二批实现只放行 runner verify-context wiring，不放行 `run_cmd.py` CLI wording、`program_cmd.py`、registry、scanner/provider 写入或 gate verdict 改写。
- 只有在用户明确要求进入实现，且 `014` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：runtime attachment truth freeze

### Task 1.1 冻结 work item 范围与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `014` 是 `013` 下游的 runtime attachment child work item
  2. `spec.md` 明确 runtime attachment 位于 `013` export truth 与 future runtime execution truth 之间
  3. `spec.md` 不再依赖临时对话才能解释 `014` 的边界
- **验证**：文档对账

### Task 1.2 冻结 explicit export 与 runtime attachment 的层级关系

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `scan --frontend-contract-spec-dir` 是显式 export surface，而不是自动 runtime attachment
  2. formal docs 明确 runner/program orchestration 仍属于独立下游责任面
  3. 不再出现“既然已有 scan export，就等于 runtime 已接好”的表述
- **验证**：术语一致性检查

### Task 1.3 冻结 non-goals 与下游保留项

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`, `specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 verify/gate、registry、auto-refresh、auto-fix 与 remediation 不属于当前 work item
  2. formal docs 明确当前阶段只冻结 docs-only baseline
  3. formal docs 明确下游实现起点是 runtime attachment helper / runner wiring，而不是重写 `013`
- **验证**：scope review

---

## Batch 2：attachment contract and failure honesty baseline

### Task 2.1 冻结 attachment trigger、scope 与 artifact locality

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 active `spec_dir` 或等价显式输入是 runtime attachment 的 scope 基线
  2. formal docs 明确 attachment 复用 `013` 的 canonical artifact contract 与 locality，而不是另造路径
  3. 不再出现 runtime 可静默跨 spec 写入 observation artifact 的表述
- **验证**：attachment contract review

### Task 2.2 冻结 failure honesty / freshness guard

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 scope 不明、artifact 缺失、provider 失败或 freshness 不可判断时必须诚实暴露
  2. formal docs 明确 attachment 失败不得伪装成 verify success 或 gate clear
  3. formal docs 明确任何自动生成 artifact 的 runtime 行为都需要显式 opt-in 或下游工单授权
- **验证**：语义对账

### Task 2.3 冻结 ownership 顺序与 program handoff

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`, `specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 explicit export、runner wiring 与 program orchestration 的 ownership 顺序
  2. formal docs 明确 `program_cmd.py` 仍是下游保留项，而不是当前 baseline 默认接入面
  3. formal docs 明确 runtime attachment baseline 与 `013` provider/export baseline 保持单一真值关系
- **验证**：handoff review

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / cli / runner / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `013` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/plan.md`, `specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 explicit export handoff、runner scope resolution、missing/stale artifact honesty 与 program non-goal 场景
  2. `tasks.md` 明确 docs baseline 完成后当前仍不直接放行 runner auto-scan、program integration、registry 或 remediation 实现
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/spec.md`, `specs/014-frontend-contract-runtime-attachment-baseline/plan.md`, `specs/014-frontend-contract-runtime-attachment-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 runtime attachment truth、scope/locality、failure honesty 与 handoff 保持单一真值
  3. 当前分支上的 `014` formal docs 可作为后续进入 runtime attachment helper / runner wiring 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：runtime attachment helper slice

### Task 4.1 先写 failing tests 固定 runtime attachment helper 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_contract_runtime_attachment.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 explicit `spec_dir` 与 checkpoint scope resolution、canonical artifact path resolution、missing/invalid artifact honesty 与 freshness 可判断性
  2. 单测明确覆盖 explicit opt-in write policy 与 explicit `spec_dir` 越界 root 的拒绝语义
  3. 首次运行定向测试时必须出现预期失败，证明 runtime attachment helper 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q`

### Task 4.2 实现最小 runtime attachment helper

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`
- **可并行**：否
- **验收标准**：
  1. helper 提供 active `spec_dir` / explicit `spec_dir` scope resolution、canonical artifact path resolution 与结构化 attachment status
  2. helper 显式暴露 missing/invalid artifact honesty、freshness status 与 explicit opt-in write policy
  3. helper 只负责 runtime attachment helper 本身，不引入 `run_cmd.py`、`runner.py`、`program_cmd.py` 或新的 runtime side effects
- **验证**：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：runner verify-context wiring slice

### Task 5.1 先写 failing tests 固定 runner verify-context attachment 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_runner_confirm.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 active `014` scope 时，`SDLCRunner._build_context("verify", cp)` 会附带 `frontend_contract_runtime_attachment` payload
  2. 单测明确覆盖 non-`014` scope 时，不应无差别附带该 payload
  3. 首次运行定向测试时必须出现预期失败，证明 runner wiring 尚未实现
- **验证**：`uv run pytest tests/unit/test_runner_confirm.py -q`

### Task 5.2 实现最小 runner verify-context wiring

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/core/runner.py`, `src/ai_sdlc/core/frontend_contract_runtime_attachment.py`
- **可并行**：否
- **验收标准**：
  1. `SDLCRunner` 在 active `014` scope 的 verify-stage context 中注入结构化 runtime attachment payload
  2. wiring 保持 read-only，不改 gate verdict、CLI wording 或 scanner/provider side effects
  3. non-`014` scope 不应被无差别注入 frontend contract runtime attachment payload
- **验证**：`uv run pytest tests/unit/test_runner_confirm.py -q`

### Task 5.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/014-frontend-contract-runtime-attachment-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_runner_confirm.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_runner_confirm.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/014-frontend-contract-runtime-attachment-baseline src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`
