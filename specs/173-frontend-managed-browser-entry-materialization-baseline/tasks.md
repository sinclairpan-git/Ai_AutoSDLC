# 任务分解：Frontend Managed Browser Entry Materialization Baseline

**编号**：`173-frontend-managed-browser-entry-materialization-baseline` | **日期**：2026-04-19

## Batch 1：red tests

- [x] 补 `index.html` materialization 红灯测试
- [x] 补 runner 可导航 `index.html` 红灯测试

## Batch 2：implementation

- [x] 在 truth-derived `artifact_generate` 中新增 `index.html`
- [x] 让 `index.html` 渲染最小 delivery context 入口

## Batch 3：verification

- [x] 跑定向 pytest
- [x] 跑 `git diff --check`
- [x] truth sync
- [x] repo dry-run
