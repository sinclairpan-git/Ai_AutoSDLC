---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
---
# 任务分解：Frontend P3 Target Project Adapter Scaffold Baseline

**编号**：`153-frontend-p3-target-project-adapter-scaffold-baseline` | **日期**：2026-04-16
**来源**：plan.md + spec.md（FR-153-001 ~ FR-153-007 / SC-153-001 ~ SC-153-004）

## 分批策略

```text
Batch 1: formal scope freeze
Batch 2: models + artifacts + validation + handoff implementation
Batch 3: docs close-out + truth refresh
```

## 执行护栏

- `153` 只实现 Core 侧 scaffold truth，不实现外部 target project runtime code
- `153` 不提前做 `independent-adapter-package` 包化
- `153` 不伪造 evidence ingestion / global truth surfacing 已完成
- `153` 必须继续消费 `151/152` 的 truth，不重新发明 carrier boundary

## Tasks

- [x] **T11 / P0**：冻结 `153` scope 与 non-goals  
  验收：`spec.md` 明确只做 target-project adapter scaffold / boundary receipt / handoff / verify

- [x] **T21 / P0**：实现 runtime adapter scaffold models 与 artifact materializer  
  验收：新增 `frontend_provider_runtime_adapter` models/generator；unit tests 覆盖 contract 与 artifact file set

- [x] **T22 / P0**：实现 runtime adapter validator 与 ProgramService handoff  
  验收：`build_frontend_provider_runtime_adapter_handoff()` 能在 snapshot 缺失时 fail-closed、在 `public-primevue` snapshot 下 ready

- [x] **T23 / P0**：实现 CLI handoff 与 verify attachment  
  验收：`program provider-runtime-adapter-handoff` 可用；`verify constraints` 在 active `153` 时暴露 scoped report

- [x] **T31 / P1**：补齐 execution log / development summary / truth refresh  
  验收：`153` formal docs、program truth sync / audit 与 close-check 可被 current framework 消费
