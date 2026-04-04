---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 任务分解：Frontend Program Final Proof Archive Project Cleanup Mutation Baseline

**编号**：`051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline` | **日期**：2026-04-04  
**来源**：plan.md + spec.md（FR-051-001 ~ FR-051-010 / SC-051-001 ~ SC-051-005）

---

## 分批策略

```text
Batch 1: truth-order and scope freeze
Batch 2: evidence review and empty-allowlist freeze
Batch 3: future handoff freeze
Batch 4: readonly verification and append-only log
```

---

## 执行护栏

- `051` 当前只能建立在 `050` cleanup artifact truth 之上，不得引入第二套 cleanup truth。
- `051` 当前必须把 cleanup mutation allowlist 冻结为空集合，不得猜测 target。
- `051` 不得改写 `050` cleanup artifact、`049` thread archive truth 或更上游 truth。
- `051` 不得修改 `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`tests/unit/test_program_service.py` 或 `tests/integration/test_cli_program.py`。
- 当前 work item 只允许写入 `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/` 内文档。
- `task-execution-log.md` 必须保持 append-only，不回写或重写先前结论。

---

## Batch 1：truth-order and scope freeze

### Task 1.1 冻结 work item 定位与真值顺序

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`
- **可并行**：否
- **验收标准**：
  1. `spec.md` 明确 `051` 是 `050` 下游的 boundary-freeze child work item
  2. `spec.md` 明确 `051` 只消费 `050` cleanup artifact truth
  3. `spec.md` 明确当前阶段不进入实现
- **验证**：文档对账

### Task 1.2 冻结空 allowlist 与 non-goals

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`, `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确当前批准的 cleanup mutation allowlist 为 `[]`
  2. formal docs 明确 `.ai-sdlc/`、reports、`written_paths` 与目录命名都不是 cleanup target formal truth
  3. formal docs 明确当前阶段不允许真实 workspace mutation
- **验证**：scope review

---

## Batch 2：evidence review and empty-allowlist freeze

### Task 2.1 记录证据审阅面

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. execution log 记录对 `050` spec、现有 service/tests 与仓库 `.ai-sdlc/` 面的只读审阅
  2. execution log 记录关键 evidence commands
  3. execution log 明确结论是“当前不存在被批准的 cleanup target formal truth”
- **验证**：execution log review

### Task 2.2 冻结 deferred honesty boundary 延续结论

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md`, `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. formal docs 明确 `050` 的 deferred honesty boundary 继续有效
  2. formal docs 明确当前 work item 不伪造 executed cleanup
  3. formal docs 明确没有 code implementation 被当前阶段放行
- **验证**：语义对账

---

## Batch 3：future handoff freeze

### Task 3.1 冻结 future child work item 的前置顺序

- **任务编号**：T31
- **优先级**：P1
- **依赖**：T22
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/plan.md`
- **可并行**：否
- **验收标准**：
  1. `plan.md` 给出 future child work item 的明确顺序
  2. 顺序以 formalize cleanup target truth 为第一步
  3. `ProgramService / CLI / tests` 仅被标记为 future touchpoints
- **验证**：handoff review

### Task 3.2 冻结当前 work item 的写入边界

- **任务编号**：T32
- **优先级**：P1
- **依赖**：T31
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/tasks.md`
- **可并行**：否
- **验收标准**：
  1. `tasks.md` 明确当前只允许修改 `specs/051/...`
  2. `tasks.md` 明确不允许修改 `src/` / `tests/`
  3. `tasks.md` 明确 execution log 保持 append-only
- **验证**：guardrail review

---

## Batch 4：readonly verification and append-only log

### Task 4.1 Fresh verify formal baseline

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：`specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/task-execution-log.md`
- **可并行**：否
- **验收标准**：
  1. `uv run ai-sdlc verify constraints` 通过
  2. `git diff --check -- specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline` 通过
  3. execution log 追加记录 fresh verification 与最终结论
- **验证**：`uv run ai-sdlc verify constraints`, `git diff --check -- specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline`
