---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
---
# 实施计划：Open Capability Tranche Backlog Baseline

**编号**：`120-open-capability-tranche-backlog-baseline` | **日期**：2026-04-13 | **规格**：`specs/120-open-capability-tranche-backlog-baseline/spec.md`

## 概述

`120` 的目标不是继续审计 root truth，而是把已经确认 open 的能力正式拆成 backlog。推荐做法分四步：先读取 root capability closure truth，再把 7 个 root clusters 展开成 9 条 delivery streams，然后在 `tasks.md` 中为每条 stream 细化 tranche，最后回填 project-state 与 execution log。

## 技术背景

**语言/版本**：文档与 YAML  
**主要依赖**：`program-manifest.yaml` capability closure truth、frontend rollout 文档、各 tranche 对应 spec formal baseline  
**存储**：`specs/120-open-capability-tranche-backlog-baseline/*`、`.ai-sdlc/project/config/project-state.yaml`  
**测试**：文档对账 + `git diff --check`  
**目标平台**：root capability truth 到 implementation queue 的派生层  
**约束**：

- 不新增第二套 machine truth
- 不修改 root open cluster 状态
- 不把 sync/formal carrier 混进 implementation backlog
- 不在 `120` 中偷跑任何 runtime 落地
- 若评审发现 root truth 之外的关键阻塞，只能登记为 `pending_root_truth_update`，不能硬塞进既有 stream

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | 只从 root `capability_closure_audit` 派生，不反向覆盖 manifest |
| 最小改动面 | 仅新增 `120` formal carrier，并推进 `project-state.yaml` |
| 流程诚实 | 明确声明 `120` 只回填 backlog，不代表任何 tranche 已执行 |

## 项目结构

```text
specs/120-open-capability-tranche-backlog-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md

.ai-sdlc/project/config/project-state.yaml
program-manifest.yaml
frontend-program-branch-rollout-plan.md
```

## 拆分方法

### 1. Root cluster 到 delivery stream

先保持 root 7-cluster truth 不动，再按“实现边界是否一致”拆成 9 条 delivery streams。拆分原则：

- 若同一 root cluster 内同时包含 user-visible mainline 与 archive/cleanup 尾链，则拆成两条 stream
- 若同一 root cluster 内同时包含主交付链与 browser gate 尾链，则拆成两条 stream
- 若 child work item 明确是 sync / wording / closeout carrier，则不作为 delivery stream
- 若评审发现跨层阻塞并未出现在当前 root cluster 中，则必须先回写 root truth，再把它纳入正式 stream；`120` 只能先登记 blocker

### 2. Delivery stream 到 tranche

每个 tranche 必须同时满足：

- 对应一组连续的 formal baseline / runtime cut / partial implementation slice
- 共享同一组主要写面和验证面
- 可以在后续 1~2 个 implementation work item 内形成独立里程碑
- 若某个问题当前还不在 root truth 中，但已阻断主线进入，必须先作为 `pending_root_truth_update` 单独登记，不能混进普通 tranche

### 3. 排序规则

推荐顺序不是按 spec 编号，而是按价值和闭环收益：

1. `S9` Agent adapter verified host ingress
2. `S6` Frontend mainline delivery apply
3. `S7` Browser quality gate
4. `S2` Frontend contract / observation / gate foundation
5. `S8` Evidence class lifecycle
6. `S3` Program automation execute/provider/writeback/governance
7. `S5` P1 runtime gaps
8. `S4` Final proof / archive / cleanup
9. `S1` Platform meta foundations

### 4. Excluded carrier rules

以下项目不进入 delivery tranche：

- root sync：`072`、`074`、`075`、`076`
- execute/release wording / status sync：`116`、`117`、`118`
- capability closure truth carrier：`119`
- 当前 backlog carrier：`120`

## 阶段计划

### Phase 0：Canonical truth capture

**目标**：锁定 `program-manifest.yaml` 的 open cluster truth 与代表性 spec 证据  
**产物**：`spec.md` 的问题定义与关键未闭环证据  
**验证方式**：文档对账  
**回退方式**：仅回退 `120` formal carrier

### Phase 1：Delivery stream split

**目标**：把 7 个 root clusters 拆成 9 条 delivery streams  
**产物**：`spec.md` 的 stream 定义  
**验证方式**：逐条对照 root cluster scope  
**回退方式**：回退 `120` 文档，不影响 root truth

### Phase 2：Tranche backlog materialization

**目标**：把 8 条 streams 细化为后续 implementation tranches  
**产物**：`tasks.md` 的 tranche backlog 与 batch 顺序  
**验证方式**：逐条检查来源范围、缺失 carrier、依赖、exit criteria  
**回退方式**：仅回退 tranche backlog 描述

### Phase 3：Formal closeout

**目标**：记录 `120` 只完成 backlog 回填，不声称实现  
**产物**：`task-execution-log.md`、`project-state.yaml`  
**验证方式**：`git diff --check`  
**回退方式**：回退 `120` carrier 与 `project-state.yaml`

## 实施顺序建议

1. 先冻结 root cluster -> delivery stream 的拆分规则
2. 先把 `S9` verified host ingress 放到 tranche backlog 最前
3. 再把高价值主线 `S6/S7` 放到 tranche backlog 最前
4. 再补 contract foundation 与 evidence lifecycle
5. 最后放 final proof/archive 与 platform meta foundations

## 后续执行建议

- `120` 完成后，下一批 implementation 不应再新开“口径同步”工单
- 直接从 `tasks.md` 的 `Batch 0` 开始派生 implementation carrier
- 若后续 tranche 执行过程中改变 root closure state，必须回写 `program-manifest.yaml`，而不是只更新 `120`
