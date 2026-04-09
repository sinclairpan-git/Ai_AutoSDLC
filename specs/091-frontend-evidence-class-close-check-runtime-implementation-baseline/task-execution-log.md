# 执行记录：091-frontend-evidence-class-close-check-runtime-implementation-baseline

## Batch 2026-04-09-001 | close-check bounded resurfacing runtime cut

### 1.1 范围

- **任务来源**：`089` 已冻结 close-stage late resurfacing contract，但 docs-only baseline 本身不授权 `src/` / `tests/` 写面，需要新的 implementation carrier 承接 runtime cut。
- **目标**：将 `frontend_evidence_class` 的 bounded late resurfacing 落到 `workitem close-check`，并用 integration regression 固定 authoring malformed / mirror drift 两类 close-stage blocker。
- **本批 touched files**：
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/plan.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/tasks.md`
  - `specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`
  - `src/ai_sdlc/core/close_check.py`
  - `tests/integration/test_cli_workitem_close_check.py`

### 1.2 根因与实现摘要

- `close_check.py` 新增 `frontend_evidence_class` 的 close-stage summary builder：
  - 优先消费 `verify constraints` 已派生的 authoring malformed blocker
  - 再消费 `program validate` 已派生的 mirror drift summary
  - 仅回传 bounded `problem_family`、`detection_surface` 与 compact token
- integration regression 覆盖：
  - `authoring malformed` 在 `--json` surface 的 bounded resurfacing
  - `mirror drift` 在 table surface 的 bounded resurfacing
- 调试中发现 mirror drift 回归最初失败不是 runtime 逻辑错误，而是测试夹具把 `program-manifest.yaml` 写成了非法 YAML；`close-check` 按 bounded contract 吞掉 manifest 解析异常后返回 `None`，因此表现为未 surfacing。当前已将 fixture writer 改为 `dedent + strip`，把夹具错误与 runtime 语义分离。

### 1.3 验证命令

- `uv run pytest tests/integration/test_cli_workitem_close_check.py::TestCliWorkitemCloseCheck::test_exit_1_when_close_check_late_resurfaces_frontend_evidence_class_mirror_drift -vv -s`
- `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

### 1.4 验证结果

- mirror drift 定向回归：通过，`1 passed in 1.13s`
- `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`：通过，`30 passed in 11.51s`
- `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`：通过，`All checks passed!`
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`
- `git diff --check`：通过，无输出
- 提交前 fresh 重跑：
  - `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`：通过，`30 passed in 12.28s`
  - `uv run ruff check src/ai_sdlc/core/close_check.py tests/integration/test_cli_workitem_close_check.py`：通过，`All checks passed!`
  - `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`
  - `git diff --check`：通过，无输出

### 1.5 对账结论

- `091` 已为当前 runtime diff 提供合法写面，消除了“`089` docs-only baseline 却直接改 `src/` / `tests/`”的框架冲突。
- `close_check.py` 当前实现满足 `089` 的 bounded late resurfacing contract：只复报 unresolved blocker，不 first-detect，不 writeback，不泄露 full diagnostics payload。
- integration regression 已固定 table / json 两种 surface，并显式验证不输出 `source_of_truth_path=` 与 `human_remediation_hint=`。

### 1.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`56dc3de`
- 当前 batch 结论：`091` 的首批 close-check runtime cut 已完成实现、fresh verification 与独立提交。
- **下一步动作**：如继续推进 runtime，优先回到 `086/087` 对应的 mirror carrier / `program validate` 路径，补齐 close-check 上游 canonical drift surface。
