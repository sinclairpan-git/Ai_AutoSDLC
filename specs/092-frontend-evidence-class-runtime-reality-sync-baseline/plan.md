# 实施计划：Frontend Evidence Class Runtime Reality Sync Baseline

**编号**：`092-frontend-evidence-class-runtime-reality-sync-baseline` | **日期**：2026-04-09 | **状态**：已冻结
**输入**：[`spec.md`](./spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md`](../091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md)

## 目标

把 `frontend_evidence_class` 当前已经存在的 runtime 主链整理成一条合法的 framework honesty-sync carrier，避免后续工作继续把 validate / sync / status / close-check 误判成“尚未实现的 prospective cut”。

## 执行批次

### Batch 1：runtime reality reconciliation

- 回读 `085` ~ `091` 的 contract / carrier 文档
- 回读当前 `verify_constraints.py`、`program_service.py`、`program_cmd.py`、`close_check.py`
- 将 verify / validate / sync / status / close-check 五类 surface 的当前 reality 写入 `092`

### Batch 2：fresh verification and archive

- 运行 frontend evidence class 定向回归：
  - `uv run pytest tests/unit/test_verify_constraints.py -q`
  - `uv run pytest tests/integration/test_cli_program.py -q`
  - `uv run pytest tests/integration/test_cli_status.py -q`
  - `uv run pytest tests/integration/test_cli_workitem_close_check.py -q`
- 运行框架校验：
  - `uv run ai-sdlc verify constraints`
  - `git diff --check`

## 写面限制

- 仅允许修改：
  - `specs/092-frontend-evidence-class-runtime-reality-sync-baseline/*`
  - `.ai-sdlc/project/config/project-state.yaml`
- 不得修改：
  - `src/`
  - `tests/`
  - `program-manifest.yaml`

## 退出条件

- `092` 文档能够清楚说明当前 runtime reality 与 historical docs-only contract 的关系
- 定向回归和框架校验 fresh 通过
- 本轮 diff 保持 docs-only 边界
