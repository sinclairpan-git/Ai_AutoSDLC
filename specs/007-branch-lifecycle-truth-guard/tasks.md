---
related_plan: "docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md"
---

# 任务分解：Branch Lifecycle Truth Guard

**编号**：`007-branch-lifecycle-truth-guard` | **日期**：2026-03-31  
**来源**：plan.md + spec.md（FR-007-001 ~ FR-007-014 / SC-007-001 ~ SC-007-005）

---

## 分批策略

```text
Batch 1: formal work item freeze + lifecycle semantics freeze
Batch 2: read-only branch/worktree inventory baseline
Batch 3: close-out disposition truth + workitem branch-check
Batch 4: verify/status/doctor governance surfaces
Batch 5: rules/templates/docs close-out + regression
```

---

## Batch 1：formal work item freeze + lifecycle semantics freeze

### Task 1.1 冻结正式 work item 真值并回挂 backlog

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：docs/framework-defect-backlog.zh-CN.md, docs/superpowers/plans/2026-03-31-branch-lifecycle-truth-guard.md, specs/007-branch-lifecycle-truth-guard/spec.md, specs/007-branch-lifecycle-truth-guard/plan.md, specs/007-branch-lifecycle-truth-guard/tasks.md
- **可并行**：否
- **验收标准**：
  1. `FD-2026-03-31-002` 明确挂到 `007-branch-lifecycle-truth-guard`。
  2. external plan 与 formal work item 文档对齐，不再只有 `docs/superpowers/plans/*.md`。
  3. `tasks.md` 使用 parser-friendly 结构，且保留 `related_plan` 对账入口。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 1.2 冻结 lifecycle kind / disposition / close-out 语义

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/rules/git-branch.md, src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, templates/execution-log-template.md, src/ai_sdlc/templates/execution-log.md.j2
- **可并行**：否
- **验收标准**：
  1. `design / feature / scratch / archive / unmanaged` 至少形成单一文本真值。
  2. `merged / archived / deleted` disposition 语义明确，且 `archived != merged`。
  3. execution-log close-out 模板有正式 branch disposition 字段。
- **验证**：规则文档对账 + `uv run ai-sdlc verify constraints`

---

## Batch 2：read-only branch/worktree inventory baseline

### Task 2.1 补齐 Git 只读 inventory primitives

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：src/ai_sdlc/branch/git_client.py, src/ai_sdlc/core/branch_inventory.py, tests/unit/test_git_client.py, tests/unit/test_branch_inventory.py
- **可并行**：否
- **验收标准**：
  1. 能列出 local branch、upstream、worktree 绑定和当前 commit。
  2. 能计算相对 `main` 的 ahead/behind。
  3. inventory 输出稳定排序，适合 snapshot tests。
- **验证**：`uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py -q`

### Task 2.2 冻结 lifecycle classification 与 divergence 判定

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/core/branch_inventory.py, tests/unit/test_branch_inventory.py
- **可并行**：否
- **验收标准**：
  1. `design/*`、`feature/*`、`codex/*`、backup/archive 与 unmanaged 名称能稳定分类。
  2. lifecycle classification 不把 scratch/worktree 分支误认成主线已兑现。
  3. 无法关联到当前 work item 的历史分支只形成非阻断输出。
- **验证**：`uv run pytest tests/unit/test_branch_inventory.py -q`

---

## Batch 3：close-out disposition truth + workitem branch-check

### Task 3.1 把 unresolved branch/worktree 接入 close-check

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/core/close_check.py, src/ai_sdlc/core/workitem_traceability.py, tests/unit/test_close_check.py, tests/integration/test_cli_workitem_close_check.py
- **可并行**：否
- **验收标准**：
  1. 当前 work item 关联 scratch/worktree 分支若仍比 `main` 多提交且未处置，close-check 能显式返回 blocker 或 warning。
  2. `merged / archived / deleted` disposition 能被解析并进入 close truth。
  3. 历史无关分支不会被错误升级成当前 work item blocker。
- **验证**：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "branch or disposition" -q`

### Task 3.2 增加只读 workitem branch-check surface

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：src/ai_sdlc/cli/workitem_cmd.py, src/ai_sdlc/core/branch_inventory.py, tests/integration/test_cli_workitem_close_check.py
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc workitem branch-check --wi <specs/...>` 能回答当前 work item 尚有哪些未处置 branch/worktree。
  2. 输出保持 read-only，不触发任何 Git 清理动作。
  3. 输出结构稳定，可被后续 docs 和 smoke 复用。
- **验证**：`uv run pytest tests/integration/test_cli_workitem_close_check.py -k "branch_check" -q`

---

## Batch 4：verify / status / doctor governance surfaces

### Task 4.1 把 branch lifecycle 接入 verify constraints

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：src/ai_sdlc/core/verify_constraints.py, tests/unit/test_verify_constraints.py, tests/integration/test_cli_verify_constraints.py
- **可并行**：否
- **验收标准**：
  1. `verify constraints` 有正式 branch lifecycle governance surface。
  2. 当前 work item unresolved branch/worktree truth 能输出稳定 failure class。
  3. archived-but-explicit 与 unrelated-historical 两类场景不会被误判成同等 blocker。
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "branch_lifecycle or disposition" -q`

### Task 4.2 在 status --json / doctor 暴露 bounded branch lifecycle 摘要

- **任务编号**：T42
- **优先级**：P1
- **依赖**：T41
- **文件**：src/ai_sdlc/telemetry/readiness.py, src/ai_sdlc/cli/commands.py, src/ai_sdlc/cli/doctor_cmd.py, tests/integration/test_cli_status.py, tests/integration/test_cli_doctor.py
- **可并行**：否
- **验收标准**：
  1. `status --json` 能输出 bounded branch inventory summary。
  2. `doctor` 能显示 branch lifecycle readiness rows。
  3. 两个 read surface 都不触发 fetch/prune/rebuild/write 副作用。
- **验证**：`uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch or lifecycle" -q`

---

## Batch 5：rules/templates/docs close-out + regression

### Task 5.1 收紧规则、模板和用户文档

- **任务编号**：T51
- **优先级**：P1
- **依赖**：T42
- **文件**：src/ai_sdlc/rules/git-branch.md, src/ai_sdlc/rules/pipeline.md, docs/框架自迭代开发与发布约定.md, docs/USER_GUIDE.zh-CN.md, templates/execution-log-template.md, src/ai_sdlc/templates/execution-log.md.j2
- **可并行**：否
- **验收标准**：
  1. `git-branch.md` 不再只描述“如何开 design/feature 分支”，而是包含 lifecycle kind 与 disposition 语义。
  2. `pipeline.md` 明确 close 前需要 branch disposition truth。
  3. 用户文档与 execution-log 模板使用同一套 branch-check / disposition 语义。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 5.2 跑完整回归并冻结新的 branch close-out guardrails

- **任务编号**：T52
- **优先级**：P1
- **依赖**：T51
- **文件**：tests/unit/test_git_client.py, tests/unit/test_branch_inventory.py, tests/unit/test_verify_constraints.py, tests/unit/test_close_check.py, tests/integration/test_cli_verify_constraints.py, tests/integration/test_cli_workitem_close_check.py, tests/integration/test_cli_status.py, tests/integration/test_cli_doctor.py, docs/USER_GUIDE.zh-CN.md
- **可并行**：否
- **验收标准**：
  1. branch lifecycle focused suite 全部通过。
  2. 全量 `pytest`、`ruff`、`verify constraints` 通过。
  3. `ai-sdlc workitem branch-check --wi specs/001-ai-sdlc-framework`、`ai-sdlc status --json`、`ai-sdlc doctor` 三类 smoke 与文档命令保持一致。
- **验证**：`uv run pytest -q`, `uv run ruff check src tests`, `uv run ai-sdlc verify constraints`
