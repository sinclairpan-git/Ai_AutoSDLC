# 需求缺口收敛总表（2026-03-28）

## 目的

本文件用于把以下四类信息收敛为单一需求入口，并给出**全量优先级**与 **spec 去向**：

1. 原始 PRD 中已有，但未被 `001` / `002` 正式拆分的需求
2. 已进入 `001` / `002`，但当前实现仅完成一半、存在合同偏差、或设计仅停留在一句话层面的需求
3. 仓库中已实现、已成为事实标准，但尚未进入正式 spec 体系的新增能力
4. 每个缺口的优先级、归属 spec 与处理策略

> 口径：原始需求真值仍以 [`AI-SDLC 全自动化框架 产品需求文档（PRD）.md`](/Users/sinclairpan/project/Ai_AutoSDLC/AI-SDLC%20全自动化框架%20产品需求文档（PRD）.md) 为准；本文件只负责**缺口收敛与拆分落位**，不替代原 PRD。

## 边界口径

- `001` / `002`：只回写原 PRD 范围内的旧债与合同修正，不承接仓库后续新增能力。
- `003`：只承接**原 PRD 中已有、但不适合继续塞进 `001` / `002`** 的跨域旧债。
- `004`：只承接**原 PRD 之外、但仓库已实现并形成事实标准**的后续新增能力。
- 原 PRD 保持不动，继续作为“当初想要什么”的真值与历史基线。

## 全量优先级（必须补齐）

| Rank | Gap ID | 需求主题 | 来源口径 | 缺口类型 | 目标 spec | 处理动作 |
|------|--------|----------|----------|----------|-----------|----------|
| 1 | RG-001 | Work Intake 的 `work_item_id` 分配与 `next_work_item_seq` 原子落盘 | 原 PRD 旧债 | 已拆分但实现偏差 | `001` 更新 | 补 Routing 合同与验收 |
| 2 | RG-002 | Work Intake 的 `recommended_flow` / `severity` / 低置信度处理 | 原 PRD 旧债 | 已拆分但实现偏差 | `001` 更新 | 补 Routing 合同与验收 |
| 3 | RG-003 | `uncertain` 澄清流程、轮次、HALT 边界与原因落盘 | 原 PRD 旧债 | 已拆分但设计不足 | `001` 更新 | 补 Clarification 合同 |
| 4 | RG-004 | Governance Freeze 结果必须阻断 docs baseline / docs branch 进入 | 原 PRD 旧债 | 已拆分但实现偏差 | `001` 更新 | 补 Governance 与 Branch 联动合同 |
| 5 | RG-005 | frozen governance 输入（constitution / policy / decisions）修改保护 | 原 PRD 旧债 | 已拆分但实现偏差 | `001` 更新 | 补 Governance 保护合同 |
| 6 | RG-006 | docs/dev 切换前后的 checkpoint / runtime / resume / progress 刷新协议 | 原 PRD 旧债 | PRD 有但未完整拆分 | `001` 更新 | 补 Branch protocol 合同 |
| 7 | RG-007 | `task graph` / `execution plan` 作为 planning 必产物的合同 | 原 PRD 旧债 | PRD 有但未拆分 | `001` 更新 | 补 Planning/Execution artifact 合同 |
| 8 | RG-008 | `execution-plan.yaml` / `runtime.yaml` / `working-set.yaml` / `latest-summary.md` 合同 | 原 PRD 旧债 | PRD 有但未拆分 | `001` 更新 | 补 Context artifact 合同 |
| 9 | RG-009 | `PRD Gate` / `Review Gate` / `Done Gate` / `Verification Gate` 的显式合同 | 原 PRD 旧债 | PRD 有但未完整拆分 | `001` 更新 | 补 Gate taxonomy 与成功标准 |
| 10 | RG-010 | Incident Close 必须经过 Postmortem Gate | 原 PRD 旧债 | 已拆分但未接主链 | `002` 更新 | 补 Incident close 合同 |
| 11 | RG-011 | Change Request 触发 `suspended` 状态与 freeze snapshot 主链联动 | 原 PRD 旧债 | 已拆分但实现偏差 | `002` 更新 | 补 Change runtime 合同 |
| 12 | RG-012 | Change Request 的 `resume-point` 必须可被 recover/run 消费 | 原 PRD 旧债 | 已拆分但设计不足 | `002` 更新 | 补 resume integration 合同 |
| 13 | RG-013 | Maintenance Studio 的 `execution-path` 产物与持久化合同 | 原 PRD 旧债 | PRD 有但 `002` 仅一句话 | `002` 更新 | 细化 Maintenance 合同 |
| 14 | RG-014 | Multi-Agent 的 Coordinator / Worker 真实编排合同 | 原 PRD 旧债 | 已拆分但仅 simulation | `002` 更新 | 细化 Parallel runtime 合同 |
| 15 | RG-015 | Knowledge Refresh 自动接入 Done/Close，而非仅手动 CLI | 原 PRD 旧债 | 已拆分但实现偏差 | `002` 更新 | 补 refresh integration 合同 |
| 16 | RG-016 | 一句话想法生成 PRD 草案 | 原 PRD 旧债 | PRD 有但未拆分 | 新建 `003` | 新 spec 承接 |
| 17 | RG-017 | Human Reviewer 的审批点、决策模型与状态记录 | 原 PRD 旧债 | PRD 有但未拆分 | 新建 `003` | 新 spec 承接 |
| 18 | RG-018 | Native / Plugin Backend 的 delegation / fallback 合同 | 原 PRD 旧债 | PRD 有但未拆分 | 新建 `003` | 新 spec 承接 |
| 19 | RG-019 | 原 PRD 非功能需求与发布门槛的可测量合同 | 原 PRD 旧债 | PRD 有但未拆分 | 新建 `003` | 新 spec 承接 |
| 20 | RG-020 | `program-manifest` 与多 spec 编排能力的正式 spec 化 | 原 PRD 外新增能力 | 已实现但未入原 spec 体系 | 新建 `004` | 新 spec 承接 |
| 21 | RG-021 | telemetry 本地证据 / operator surface / bounded status 的正式 spec 化 | 原 PRD 外新增能力 | 已实现但未入原 spec 体系 | 新建 `004` | 新 spec 承接 |
| 22 | RG-022 | `doctor` / `scan` / `stage` / IDE adapter / `project-config` 的 operator contract | 原 PRD 外新增能力 | 已实现但未入原 spec 体系 | 新建 `004` | 新 spec 承接 |
| 23 | RG-023 | 离线打包与分发约束的正式 spec 化 | 原 PRD 外新增能力 | 已实现但未入原 spec 体系 | 新建 `004` | 新 spec 承接 |

## 拆分结果

### 更新 `001-ai-sdlc-framework`

承接核心闭环与 P0 真值收敛：

- RG-001 ~ RG-009
- 重点补足 Routing / Governance / Branch / Context / Gate taxonomy

### 更新 `002-p1-capabilities`

承接原 P1 模块但尚未闭环的设计：

- RG-010 ~ RG-015
- 重点补足 Incident / Change / Maintenance / Parallel / Knowledge Refresh 的 runtime 合同

### 新建 `003-cross-cutting-authoring-and-extension-contracts`

承接原 PRD 中未进入 `001` / `002` 的跨域旧债：

- RG-016 ~ RG-019
- 重点补足 PRD Draft Authoring / Human Reviewer / Plugin Backend / NFR & Release Gates
- 不承接仓库在原 PRD 之后新增出的 operator / telemetry / program 能力

### 新建 `004-operator-surfaces-and-post-prd-extensions`

承接原 PRD 之外、仓库当前已实现且需要正式建制的后续新增能力：

- RG-020 ~ RG-023
- 重点补足 Program / Telemetry / Operator CLI / IDE Adapter / Offline Distribution
- 不承担原 PRD 旧债回填职责

## 评审关注点

本轮只完成**需求收敛与 spec 拆分**，不进入实现。

评审时建议重点确认：

1. `001` 与 `002` 的边界是否仍符合你的产品分期
2. `003` 是否仅承接原 PRD 旧债，而未混入后续新增能力
3. `004` 是否只承接原 PRD 外新增能力，而未反向承担旧债回填
