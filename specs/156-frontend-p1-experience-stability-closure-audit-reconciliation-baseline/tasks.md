---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/155-frontend-program-automation-chain-closure-audit-reconciliation-baseline/spec.md"
  - "specs/066-frontend-p1-experience-stability-planning-baseline/spec.md"
  - "specs/067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/069-frontend-p1-governance-diagnostics-drift-baseline/spec.md"
  - "specs/070-frontend-p1-recheck-remediation-feedback-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/072-frontend-p1-root-rollout-sync-baseline/spec.md"
  - "specs/076-frontend-p1-root-close-sync-baseline/spec.md"
---
# 任务分解：Frontend P1 Experience Stability Closure Audit Reconciliation Baseline

**编号**：`156-frontend-p1-experience-stability-closure-audit-reconciliation-baseline` | **日期**：2026-04-17  
**来源**：plan.md + spec.md（FR-156-001 ~ FR-156-008 / SC-156-001 ~ SC-156-005）

## 分批策略

```text
Batch 1: formal closure-universe freeze + adversarial guardrails
Batch 2: 066-072 / 076 fresh close-evidence sweep
Batch 3: root audit reconciliation + truth refresh
```

## 执行护栏

- `156` 只允许 truth-only 变更：`specs/*.md`、`program-manifest.yaml`、`project-state.yaml`
- `156` 不得修改 `src/` / `tests/`
- `156` 不得在 `066-072`、`076` close-check sweep 未通过前提前移除 root cluster
- `156` 不得把 `072/076` 叙述成 capability delivery
- `156` 不得顺带关闭其他 open clusters

## Tasks

- [x] **T11 / P0**：冻结 `frontend-p1-experience-stability` 的 closure universe、non-goals 与对抗约束  
  验收：`156/spec.md`、`plan.md`、`tasks.md` 明确 `156` 只做 root truth reconciliation，并固化常驻对抗专家的三条 fail-closed 约束

- [x] **T21 / P0**：执行 `066-072`、`076` 的 fresh close-check sweep，并记录 child carrier / sync carrier 分类  
  验收：`task-execution-log.md` 收录全部 close-check 命令与通过结果，且显式区分 `067-071` 与 `072/076` 的 truth role

- [x] **T31 / P0**：移除 root `frontend-p1-experience-stability` open cluster，刷新 truth snapshot，并固定本批 truth-only 边界
  验收：`program-manifest.yaml` 中不再存在 `frontend-p1-experience-stability`；`program truth audit` fresh；`156` close-check 通过；`156` formal docs 显式排除 rollout 汇总同步
