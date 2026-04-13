---
related_doc:
  - "program-manifest.yaml"
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "src/ai_sdlc/integrations/agent_target.py"
  - "src/ai_sdlc/integrations/ide_adapter.py"
  - "src/ai_sdlc/cli/adapter_cmd.py"
  - "src/ai_sdlc/cli/run_cmd.py"
---
# 实施计划：Agent Adapter Verified Host Ingress Truth Baseline

**编号**：`121-agent-adapter-verified-host-ingress-truth-baseline` | **日期**：2026-04-13 | **规格**：`specs/121-agent-adapter-verified-host-ingress-truth-baseline/spec.md`

## 概述

`121` 的目标不是立即实现 adapter verify runtime，而是把“真实 adapter 安装/验证”正式提升为 root truth。推荐做法分三步：先冻结 formal carrier 与明确适配矩阵，再把 open cluster 回写到 `program-manifest.yaml`，最后推进 `project-state.yaml` 与 backlog handoff，让后续 implementation carrier 不再停留在 `pending_root_truth_update`。

## 技术背景

**语言/版本**：Markdown + YAML  
**主要依赖**：`program-manifest.yaml` capability closure truth、`010` activation contract、`094` Stage 0 boundary、`120` backlog blocker  
**存储**：`specs/121-agent-adapter-verified-host-ingress-truth-baseline/*`、`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`  
**测试**：文档对账 + `git diff --check`  
**目标平台**：root truth + follow-up implementation backlog  
**约束**：

- 不在本工单中直接改 adapter runtime 行为
- 不在厂商公开支持不明确时单列新 target
- 不把 `generic` 误写成“弱化的明确适配”
- 不把 `adapter activate` 重新写成 verified success

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | 先把 adapter verified ingress 提升为 root manifest truth |
| 最小改动面 | 仅新增 `121` formal carrier，回写 manifest 与 project-state |
| 流程诚实 | 不宣称 runtime 已实现，只冻结支持矩阵与状态边界 |

## 项目结构

```text
specs/121-agent-adapter-verified-host-ingress-truth-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

program-manifest.yaml
.ai-sdlc/project/config/project-state.yaml
```

## 阶段计划

### Phase 0：Formal carrier freeze

**目标**：冻结明确适配列表、`generic`/`TRAE` 边界与 verified host ingress 状态语义  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：文档对账  
**回退方式**：只回退 `121` carrier

### Phase 1：Root truth sync

**目标**：把 `agent-adapter-verified-host-ingress` 回写进 `program-manifest.yaml`  
**产物**：manifest open cluster truth  
**验证方式**：YAML 对账  
**回退方式**：只回退 manifest cluster

### Phase 2：Backlog handoff

**目标**：推进 `project-state.yaml`，为后续 implementation carrier 建立正式起点  
**产物**：`project-state.yaml`、`task-execution-log.md`  
**验证方式**：`git diff --check`  
**回退方式**：回退 `project-state.yaml` 与 `121` 归档

## 实施顺序建议

1. 先冻结“什么才算明确适配”的 formal truth
2. 再把该 truth 升成 root open cluster
3. 最后推进 next work item seq，交给后续 implementation carrier 落地

## 后续执行建议

- `121` 完成后，下一条 implementation carrier 不再需要重复证明“为什么这算独立 capability”
- 后续 adapter runtime 改造必须同时消费 `010` 的 activation truth 与 `121` 的 verified host ingress truth
- 在厂商公开支持尚不明确前，不得把 `TRAE` 从 `generic` 中提前拆出
