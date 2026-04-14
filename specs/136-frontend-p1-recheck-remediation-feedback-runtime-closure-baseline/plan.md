# 实施计划：Frontend P1 Recheck Remediation Feedback Runtime Closure Baseline

**功能编号**：`136-frontend-p1-recheck-remediation-feedback-runtime-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 核对 `066-070` formal truth 与当前 `ProgramService` / CLI / tests，确认真实缺口是 runtime consumer mismatch，而不是整条 feedback runtime 缺失
2. 通过 TDD 固定 `READY -> recheck handoff`、`non-READY -> remediation input` 的分流
3. 回填 `120/T41`、`project-state.yaml` 与执行日志，并通过 focused verification / 对抗评审固定下游边界

## 边界

- 本批不推进 `071/T42` visual / a11y runtime foundation
- 本批不新增 diagnostics taxonomy，只消费既有 `069/070` truth
- 本批只修正 remediation/recheck handoff 的 routing honesty 与相应 CLI surface
