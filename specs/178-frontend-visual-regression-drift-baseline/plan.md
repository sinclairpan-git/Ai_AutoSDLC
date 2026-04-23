# 实施计划：Frontend Visual Regression Drift Baseline

**编号**：`178-frontend-visual-regression-drift-baseline` | **日期**：2026-04-23 | **规格**：[`spec.md`](./spec.md)

## 1. 目标

把 browser gate 已有的 screenshot 采集升级成 contract-backed 的 visual regression truth，并让这条 truth 真正驱动 `visual_verdict`、`program status`、truth ledger 与 dry-run 收口。

## 2. 范围

### In Scope

- visual regression matrix / viewport truth 向 browser gate execution context 透传
- managed frontend 的 diff comparator bootstrap 与 deterministic screenshot compare
- `visual_regression` receipt、artifact 和 bundle `visual_verdict` 接线
- runtime artifact ref 规范化，消除 `artifact:` 前缀导致的 namespace drift
- baseline / bootstrap / browser gate / truth sync 的真实仓库验证
- 178 formal docs 补齐并接回 canonical manifest / source inventory

### Out Of Scope

- keyboard traversal / tab-order 自动化
- 主观审美评分器
- 多浏览器矩阵扩展
- baseline 自动 bless

## 3. 验证

- `uv run python -m pytest tests/unit/test_frontend_browser_gate_runtime.py tests/unit/test_program_service.py -k "browser_gate or visual_regression or active_visual_regression or marks_delivery_verified_when_browser_gate_passes" -q`
- `python -m ai_sdlc program browser-gate-probe --execute`
- `python -m ai_sdlc program truth sync --execute --yes`
- `python -m ai_sdlc program status`
- `python -m ai_sdlc verify constraints`
- `python -m ai_sdlc run --dry-run`
