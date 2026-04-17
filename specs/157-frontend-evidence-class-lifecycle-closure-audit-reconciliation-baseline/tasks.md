---
related_doc:
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/079-frontend-framework-only-closure-policy-baseline/spec.md"
  - "specs/080-frontend-framework-only-root-policy-sync-baseline/spec.md"
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "specs/090-frontend-evidence-class-runtime-rollout-sequencing-baseline/spec.md"
  - "specs/091-frontend-evidence-class-close-check-runtime-implementation-baseline/spec.md"
  - "specs/092-frontend-evidence-class-runtime-reality-sync-baseline/spec.md"
  - "specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/spec.md"
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
  - "specs/109-frontend-cleanup-archive-evidence-class-backfill-baseline/spec.md"
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
  - "specs/111-frontend-p1-child-close-check-backfill-baseline/spec.md"
  - "specs/112-frontend-072-081-close-check-backfill-baseline/spec.md"
  - "specs/113-frontend-082-092-manifest-mirror-baseline/spec.md"
---
# 任务分解：Frontend Evidence Class Lifecycle Closure Audit Reconciliation Baseline

**编号**：`157-frontend-evidence-class-lifecycle-closure-audit-reconciliation-baseline` | **日期**：2026-04-17  
**来源**：plan.md + spec.md（FR-157-001 ~ FR-157-008 / SC-157-001 ~ SC-157-005）

## 分批策略

```text
Batch 1: formal closure-universe freeze + adversarial guardrails
Batch 2: 079-092 / 107-113 fresh close-evidence sweep
Batch 3: root audit reconciliation + truth refresh
```

## 执行护栏

- `157` 只允许 truth-only 变更：`specs/*.md`、`program-manifest.yaml`、`project-state.yaml`
- `157` 不得修改 `src/` / `tests/`
- `157` 不得在 `079-092`、`107-113` close-check sweep 未通过前提前移除 root cluster
- `157` 不得把 `079/081/092/108-113` 叙述成 capability delivery
- `157` 不得把 `091/107` 叙述成整个 cluster 的单点 closure proof
- `157` 不得顺带关闭其他 open clusters

## Tasks

- [x] **T11 / P0**：冻结 `frontend-evidence-class-lifecycle` 的 closure universe、non-goals 与对抗约束  
  验收：`157/spec.md`、`plan.md`、`tasks.md` 明确 `157` 只做 root truth reconciliation，并固化常驻对抗专家的四条 fail-closed 约束

- [x] **T21 / P0**：执行 `079-092`、`107-113` 的 fresh close-check sweep，并记录 formal/policy、runtime、honesty/backfill 分类  
  验收：`task-execution-log.md` 收录全部 close-check 命令与通过结果，且显式区分 `079/081/083-090`、`091/107`、`092/108-113` 的 truth role

- [x] **T31 / P0**：移除 root `frontend-evidence-class-lifecycle` open cluster，刷新 truth snapshot，并固定本批 truth-only 边界  
  验收：`program-manifest.yaml` 中不再存在 `frontend-evidence-class-lifecycle`；`program truth audit` fresh；`157` close-check 通过；`157` formal docs 显式排除 rollout 汇总同步
