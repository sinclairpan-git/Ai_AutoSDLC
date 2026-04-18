# 实施计划：Agent Adapter Verified Host Ingress Closure Audit Finalization Baseline

**编号**：`163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline` | **日期**：2026-04-18 | **规格**：`specs/163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline/spec.md`

## 概述

`163` 是一个 truth-only reconciliation work item。目标不是继续实现 adapter 功能，而是消费 `121/122/158/159/160/161/162` 已经形成的 fresh close evidence，移除 root `capability_closure_audit` 中过时的 `agent-adapter-verified-host-ingress` open cluster，并在刷新 truth snapshot 后让 release capability 真值转为 `ready`。

## 技术背景

**语言/版本**：Python 3.13  
**主要依赖**：Typer CLI、Pydantic models、`program-manifest.yaml` truth ledger  
**存储**：仓库内 YAML/Markdown formal docs  
**测试**：`workitem close-check`、`program truth audit/sync`、`python -m ai_sdlc run --dry-run`、`uv run ai-sdlc verify constraints`  
**目标平台**：本地 AI-SDLC CLI 仓库  
**约束**：

- 只允许消费现有 machine-verifiable evidence
- 不新增第二份 closure ledger
- root cluster 关闭必须以移除 `open_clusters` 条目表达
- 若 truth/provenance 仍不一致，必须保持 fail-closed

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一 canonical truth | 仅改写 `program-manifest.yaml` 与 `specs/163-*`，不新增旁路台账 |
| 证据先于结论 | 先跑 close sweep / truth audit，再决定是否移除 cluster |
| fail-closed | 任一关键 close evidence 不 fresh 就保持 `partial` |
| 直接 formal | `spec/plan/tasks/task-execution-log` 直接作为 canonical work item 文档 |

## 项目结构

### 文档结构

```text
specs/163-agent-adapter-verified-host-ingress-closure-audit-finalization-baseline/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
```

### 真值结构

```text
program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
specs/121-*/... specs/122-*/... specs/158-162-*/...
```

## 阶段计划

### Phase 0：正式边界冻结

**目标**：将 `163` 从模板脚手架替换为可执行的 closure-audit finalization 文档  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：`uv run ai-sdlc verify constraints`  
**回退方式**：撤回 `specs/163-*` 文档变更并重新生成

### Phase 1：证据宇宙审计

**目标**：确认 cluster close 需要消费的 fresh evidence 与 manifest provenance 边界  
**产物**：close sweep 结果、manifest provenance 决策、execution log 批次记录  
**验证方式**：`python -m ai_sdlc workitem close-check --wi ...`、`python -m ai_sdlc program truth audit`  
**回退方式**：若任一 work item 未 ready，则不改写 root cluster，只记录 blocker

### Phase 2：Root Truth Finalization

**目标**：移除过时 open cluster，刷新 truth snapshot，并验证 release capability ready  
**产物**：更新后的 `program-manifest.yaml`、fresh truth snapshot、close-ready execution log  
**验证方式**：`python -m ai_sdlc program truth sync --execute --yes`、`python -m ai_sdlc program truth audit`、`python -m ai_sdlc run --dry-run`  
**回退方式**：恢复 cluster 条目并重新 sync truth

## 工作流计划

### 工作流 A：Close Evidence Sweep

**范围**：`121/122/158/159/160/161/162` 的 current close-check grammar 复核  
**影响范围**：只读审计；必要时补充 execution-log grammar 或 provenance 说明  
**验证方式**：逐项 `workitem close-check` + `verify constraints`  
**回退方式**：保留 `partial`，把 blocker 明确写入 163 execution log

### 工作流 B：Manifest Reconciliation

**范围**：`program-manifest.yaml > release_capabilities[]` 与 `capability_closure_audit`  
**影响范围**：cluster removal、source/spec provenance 对齐、truth snapshot refresh  
**验证方式**：`program truth sync --execute --yes`、`program truth audit`、`run --dry-run`  
**回退方式**：重新加回 open cluster，并恢复到最近一次 truth-consistent manifest

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| formal docs 可被框架消费 | `uv run ai-sdlc verify constraints` | `git diff --check` |
| 关键 work item close evidence fresh | `python -m ai_sdlc workitem close-check --wi ...` | `program truth audit` |
| root cluster removal 后真值 ready | `python -m ai_sdlc program truth sync --execute --yes` | `python -m ai_sdlc run --dry-run` |
| 163 自身可关闭 | `python -m ai_sdlc workitem close-check --wi specs/163-...` | clean tree + fresh truth |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| `release_capabilities[].spec_refs` 是否需要纳入 `161/162/163` 作为正式 provenance | 已解决：纳入 `spec_refs`，但不扩张 `required_evidence` | 已关闭 |
| `run --dry-run` 在 cluster 关闭后是否直接转为 close-ready，还是仍有其他非 capability gate | 待验证 | Phase 2 |

## 实施顺序建议

1. 先冻结 `163` formal docs，避免后续执行时继续沿用脚手架占位
2. 对 `121/122/158/159/160/161/162` 做 fresh close sweep，并确定 manifest provenance 需要的最小改写
3. 仅在证据完整时移除 root cluster、刷新 truth，并用 `run --dry-run` / `163 close-check` 做最终确认
