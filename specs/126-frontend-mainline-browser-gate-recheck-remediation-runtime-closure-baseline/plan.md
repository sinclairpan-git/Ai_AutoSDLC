# 实施计划：Frontend Mainline Browser Gate Recheck Remediation Runtime Closure Baseline

**功能编号**：`126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 定义 `126` formal carrier，并把 `120/T14` 回链到新工单
2. 先写红灯测试，锁定 browser gate artifact -> execute gate decision / CLI / runbook continuation
3. 扩展 `frontend_gate_verification`、`ProgramService` 与 `program browser-gate-probe`
4. 做 focused verification，并进入对抗评审

## 边界

- 只补 browser gate artifact consumption 与下游 handoff closure
- 只把 replay 命令收敛到 `program browser-gate-probe --execute`
- 不补新的 browser probe runtime capture 面
