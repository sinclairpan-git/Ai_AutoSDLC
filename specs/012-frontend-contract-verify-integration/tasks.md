---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/plan.md"
---
# 任务分解：Frontend Contract Verify Integration

**编号**：`012-frontend-contract-verify-integration` | **日期**：2026-04-02  
**来源**：plan.md + spec.md（FR-012-001 ~ FR-012-018 / SC-012-001 ~ SC-012-005）

---

## 分批策略

```text
Batch 1: verify surface truth freeze
Batch 2: CLI and attachment baseline
Batch 3: implementation handoff and verification freeze
Batch 4: frontend contract verification report slice
Batch 5: verify_constraints scoped attachment slice
```

---

## 执行护栏

- `Batch 1 ~ 3` 只允许推进 `spec.md / plan.md / tasks.md` 与 append-only `task-execution-log.md`。
- `Batch 4` 只允许写入 `src/ai_sdlc/core/frontend_contract_verification.py`、`tests/unit/test_frontend_contract_verification.py`、`specs/012-frontend-contract-verify-integration/task-execution-log.md`，以及为本批边界服务的 `plan.md / tasks.md`。
- `Batch 5` 只允许写入 `src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`specs/012-frontend-contract-verify-integration/task-execution-log.md`，以及为本批边界服务的 `spec.md / plan.md / tasks.md`。
- `012` 不得把 scanner、fix-loop、auto-fix、contract writeback 或 runtime 代码混入当前 child work item 的 formal baseline。
- `012` 不得默认扩张为新的 verify stage / gate system；若需触及 registry，只能作为复用现有 `verify / verification` stage 的附件策略。
- `012` 只冻结 frontend contract verify integration，不回写 `011` 已冻结的 contract truth 本体。
- 当前首批实现只放行 verify report/context helper，不放行 `verify_constraints`、`pipeline_gates.py`、CLI 或 registry 写入。
- 当前第二批实现只放行 active-`012` scoped 的 `verify_constraints` attachment，不放行 `pipeline_gates.py`、CLI、registry 或 scanner。
- 只有在用户明确要求进入实现，且 `012` formal docs 已通过门禁后，才允许进入 `src/` / `tests/` 级实现。

---

## Batch 1：verify surface truth freeze

### Task 1.1 冻结 work item 范围与非目标

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `012` 是 `011` 下游的 verify integration child work item
  2. `spec.md` 明确 scanner、fix-loop、auto-fix 与 runtime 不属于当前 work item
  3. `spec.md` 不再依赖临时对话才能解释 `012` 的边界
- **验证**：文档对账

### Task 1.2 冻结 `frontend_contract_gate -> verify constraints -> VerificationGate / VerifyGate -> cli verify` 真值顺序

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `frontend_contract_gate` 是上游输入面，而不是平行 gate system
  2. formal docs 明确 verify 主链使用现有 `verify constraints` 与 `VerificationGate / VerifyGate`
  3. 不再出现“另起新 verify stage”或“直接把 gate helper 当最终 verify surface”的表述
- **验证**：文档交叉引用检查

### Task 1.3 冻结 observation 输入边界与诚实失败语义

- **任务编号**：T13
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`, `specs/012-frontend-contract-verify-integration/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 observation 以结构化输入进入 verify integration
  2. formal docs 明确 artifact 缺失、observation 缺失与 drift 未清时必须诚实暴露
  3. formal docs 明确 scanner 不属于当前 work item
- **验证**：术语一致性检查

---

## Batch 2：CLI and attachment baseline

### Task 2.1 冻结 verification source / check object / coverage gap 口径

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T13
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 frontend contract verification 的 source、check object 与 coverage gap 最小集合
  2. formal docs 明确 `verify constraints` 如何承载 blocker / advisory / gap 信息
  3. 不再出现“contract 状态只停留在 helper 或自由文本里”的表述
- **验证**：verification surface review

### Task 2.2 冻结现有 stage 复用与 registry attachment 边界

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确优先复用现有 `verify / verification` stage
  2. formal docs 明确 registry 只在确有必要时才允许触碰
  3. formal docs 明确当前 work item 不创建新的 verify stage / gate system
- **验证**：attachment strategy review

### Task 2.3 冻结 terminal / JSON verify surface 口径

- **任务编号**：T23
- **优先级**：P0
- **依赖**：T22
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`, `specs/012-frontend-contract-verify-integration/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 CLI terminal / JSON surface 需要暴露 frontend contract verification 最小摘要
  2. formal docs 明确 verify 输出不得误报 PASS 或掩盖“无法比较”的真实状态
  3. formal docs 明确 contract-aware surface 与现有 verification 输出保持单一真值
- **验证**：命令语义对账

---

## Batch 3：implementation handoff and verification freeze

### Task 3.1 冻结推荐文件面与 ownership 边界

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T23
- **文件**：`specs/012-frontend-contract-verify-integration/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出后续 `core / gates / cli / tests` 的推荐文件面
  2. 文件面之间的 ownership 边界可被后续实现直接采用
  3. 当前 child work item 的实现起点清晰，不需要再次回到 `011` 重新拆分
- **验证**：file-map review

### Task 3.2 冻结最小测试矩阵与执行前提

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/012-frontend-contract-verify-integration/plan.md`, `specs/012-frontend-contract-verify-integration/tasks.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确最小验证面至少覆盖 PASS、artifact 缺失、observation 缺失、drift 未清与 CLI/JSON surface 场景
  2. `tasks.md` 明确 formal baseline 完成后当前仍不直接放行 scanner / fix-loop / auto-fix
  3. formal docs 明确进入实现前至少要先通过 `uv run ai-sdlc verify constraints`
- **验证**：测试矩阵对账

### Task 3.3 只读校验并冻结当前 child work item baseline

- **任务编号**：T33
- **优先级**：P1
- **依赖**：T32
- **文件**：`specs/012-frontend-contract-verify-integration/spec.md`, `specs/012-frontend-contract-verify-integration/plan.md`, `specs/012-frontend-contract-verify-integration/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 可通过
  2. `spec.md / plan.md / tasks.md` 对 verify truth、attachment、CLI 口径和 handoff 保持单一真值
  3. 当前分支上的 `012` formal docs 可作为后续进入 verify integration 实现的稳定基线
- **验证**：`uv run ai-sdlc verify constraints`, `git status --short`

---

## Batch 4：frontend contract verification report slice

### Task 4.1 先写 failing tests 固定 verify report / context 语义

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T33
- **文件**：`tests/unit/test_frontend_contract_verification.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖 PASS、artifact 缺失、observation 缺失与 drift 未清时的 report / context 输出
  2. 单测明确覆盖 `source_name / check_objects / blockers / coverage_gaps` 的最小翻译合同
  3. 首次运行定向测试时必须出现预期失败，证明 report/context helper 尚未实现
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`

### Task 4.2 实现最小 frontend_contract_verification helper

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：`src/ai_sdlc/core/frontend_contract_verification.py`
- **可并行**：否
- **验收标准**：
  1. helper 提供结构化 verify report 与 context builder，可消费 `frontend_contract_gate` 结果
  2. helper 明确输出 frontend contract verification 的 source、check objects、blockers 与 coverage gaps
  3. helper 只负责 report/context 翻译，不引入 `verify_constraints`、`pipeline_gates`、CLI 或 registry 改动
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`

### Task 4.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T43
- **优先级**：P0
- **依赖**：T42
- **文件**：`specs/012-frontend-contract-verify-integration/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_frontend_contract_verification.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/012-frontend-contract-verify-integration src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录当前 implementation batch 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_frontend_contract_verification.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/012-frontend-contract-verify-integration src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`

---

## Batch 5：verify_constraints scoped attachment slice

### Task 5.1 先写 failing tests 固定 active-012 scoped attachment 语义

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T43
- **文件**：`tests/unit/test_verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. 单测明确覆盖非 `012` work item 不激活 frontend contract verification 的隔离语义
  2. 单测明确覆盖 active `012` 下缺失 `frontend-contract-observations.json` 时的 `coverage_gaps / blockers / verification_sources` 行为
  3. 单测明确覆盖 active `012` 下 observation 文件存在且匹配 contract artifact 时的 PASS 路径
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`

### Task 5.2 实现最小 verify_constraints attachment

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：`src/ai_sdlc/core/verify_constraints.py`
- **可并行**：否
- **验收标准**：
  1. `verify_constraints.py` 仅在 active work item 命中 `012` 时挂接 frontend contract verification
  2. `verify_constraints.py` 复用 `frontend_contract_verification` helper，并从 active spec 目录下的 `frontend-contract-observations.json` 读取结构化 observation 输入
  3. `verify_constraints.py` 将 frontend contract source、check objects、coverage gaps 与 blocker/context payload 接入现有结构，而不触碰 `pipeline_gates.py`、CLI、registry 或 scanner
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`

### Task 5.3 Fresh verify 并追加 implementation batch 归档

- **任务编号**：T53
- **优先级**：P0
- **依赖**：T52
- **文件**：`specs/012-frontend-contract-verify-integration/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run pytest tests/unit/test_verify_constraints.py -q` 通过
  2. `uv run ruff check src tests`、`git diff --check -- specs/012-frontend-contract-verify-integration src/ai_sdlc/core tests/unit` 与 `uv run ai-sdlc verify constraints` 通过
  3. `task-execution-log.md` 追加记录 active-`012` scoped attachment 的 touched files、验证命令与结论
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py -q`, `uv run ruff check src tests`, `git diff --check -- specs/012-frontend-contract-verify-integration src/ai_sdlc/core tests/unit`, `uv run ai-sdlc verify constraints`
