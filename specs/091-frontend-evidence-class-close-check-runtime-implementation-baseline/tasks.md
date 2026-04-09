# 任务分解：Frontend Evidence Class Close-Check Runtime Implementation Baseline

**编号**：`091-frontend-evidence-class-close-check-runtime-implementation-baseline` | **日期**：2026-04-09  
**来源**：plan.md + spec.md（FR-091-001 ~ FR-091-008 / SC-091-001 ~ SC-091-004）

---

## 分批策略

```text
Batch 1: close-check bounded resurfacing implementation
Batch 2: integration regression, verification, archive
```

---

## 执行护栏

- `091` 只允许写 `src/ai_sdlc/core/close_check.py`、`tests/integration/test_cli_workitem_close_check.py`、`specs/091/...` 与 `.ai-sdlc/project/config/project-state.yaml`
- `091` 不得修改 `program validate`、`program status`、`status --json`、`program-manifest.yaml`
- `091` 不得重新定义 `089` 的 docs-only contract，只能实现其 bounded late resurfacing slice
- `091` 不得让 close-check 变成 first-detection、writeback 或 full diagnostics surface

## Batch 1：close-check bounded resurfacing implementation

### Task 1.1 实现 close-stage summary builder

- [x] 在 `close_check.py` 增加 `frontend_evidence_class` 的 late resurfacing summary builder
- [x] 先读取 `verify constraints` 的 authoring malformed blocker，再读取 `program validate` 的 mirror drift summary
- [x] 只暴露 bounded `problem_family` / `detection_surface` / compact token

**完成标准**

- `workitem close-check` 对 `082+` frontend subject 可以复报 unresolved evidence-class blocker，但不展开 full diagnostics

### Task 1.2 接入 close-check checks/blockers 输出

- [x] 在 `run_close_check()` 中追加 `frontend_evidence_class` check
- [x] close-stage blocker wording 保持 bounded late resurfacing
- [x] 不新增 writeback、severity 重裁或 source-of-truth 修复

**完成标准**

- close-check table / json 都只显示 bounded resurfacing truth

## Batch 2：integration regression, verification, archive

### Task 2.1 补 authoring malformed / mirror drift 回归

- [x] 在 integration test 增加 `authoring malformed` 的 close-check `--json` 回归
- [x] 在 integration test 增加 `mirror drift` 的 close-check table 回归
- [x] 修复 manifest fixture 写法，保证 YAML 合法

**完成标准**

- 两条回归都能稳定证明 close-check 只做 late resurfacing

### Task 2.2 运行 fresh verification 并归档

- [x] 运行 `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- [x] 运行 `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`
- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check`
- [x] 追加 `task-execution-log.md`

**完成标准**

- verification fresh 通过，execution log 记录 runtime cut、fixture root cause 与验证结果
