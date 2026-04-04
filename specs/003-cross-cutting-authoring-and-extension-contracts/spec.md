# 功能规格：AI-SDLC 原 PRD 跨域旧债补充合同

**功能编号**：`003-cross-cutting-authoring-and-extension-contracts`  
**创建日期**：2026-03-28  
**状态**：已实现（cross-cutting authoring and extension closure）
**输入**：原始 PRD Section 4.2, 8.4.1, 8.10, 8.12, 12, 13, 14；缺口收敛总表 RG-016 ~ RG-019（仅承接原 PRD 旧债）

> 口径：本 spec 只吸收**原 PRD 已存在、但不适合继续塞进 `001` / `002`** 的跨域需求，不承接仓库在原 PRD 之后新增出的 operator / telemetry / program 能力。

## 范围

- **覆盖**：
  - 原 PRD 中未被 `001` / `002` 承接的跨域旧债
  - 一句话想法生成 PRD 草案
  - Human Reviewer 审批点与决策记录
  - Native / Plugin Backend delegation / fallback 合同
  - 非功能需求与发布门槛的可测量合同
- **不覆盖**：
  - `001` 已有的核心闭环实现细节
  - `002` 已有的 Studios / Parallel / Knowledge Refresh runtime 细节
  - 原 PRD 之外的新增能力
  - Telemetry / Program / Operator CLI 等后续扩展能力

## 用户故事与验收

### US-003-1 — 一句话想法生成 PRD 草案

作为**产品经理 / 需求方**，我希望提交一句话想法后，系统能生成一份带未决假设标记的 PRD 草案，以便快速进入需求澄清。

**验收**：

1. Given 一句话输入，When 进入 PRD Authoring 流程，Then 生成结构完整的 PRD draft
2. Given 关键信息缺失，When 生成 PRD draft，Then 未确定项以显式占位标记输出，而不是静默补全为事实
3. Given draft 生成完成，When 交给后续 PRD Gate，Then 可区分 draft 与 final PRD

### US-003-2 — Human Reviewer 审批点可见

作为**Human Reviewer**，我希望在关键节点拥有清晰的 approve / revise / block 决策点，以便人类审查能够成为正式流程，而不是口头约定。

**验收**：

1. Given 进入 PRD freeze、docs baseline freeze、close/merge 前节点，When 需要人工决策，Then 系统输出明确审批状态
2. Given Reviewer 选择 revise 或 block，When 查看状态与恢复信息，Then 能看到原因、时间与下一步动作

### US-003-3 — Plugin Backend 委托/回退可预测

作为**框架维护者**，我希望当 Plugin Backend 覆盖当前操作时可委托执行，失败时也有明确 fallback / block 规则，以便行为可预测且可审计。

**验收**：

1. Given Native 与 Plugin 都可处理当前动作，When 执行策略允许委托，Then 明确记录选择了哪个 backend 及原因
2. Given Plugin 不可用或能力不覆盖，When 执行，Then 回退到 Native 或显式阻断，而不是静默降级
3. Given Plugin 执行失败，When 判断为不可安全回退，Then 返回 BLOCK，不得继续推进状态

### US-003-4 — NFR 与发布门槛可测量

作为**技术负责人**，我希望可恢复性、可移植性、多 IDE 兼容、稳定性与发布门槛都有明确合同，以便发布标准不再停留在描述性文字。

**验收**：

1. Given 发布前检查，When 评估可恢复性与可移植性，Then 有明确命令或证据项可验证
2. Given 多 IDE 适配路径，When 在非交互环境执行，Then 行为有统一降级策略
3. Given 发布门槛未满足，When 执行发布前检查，Then 输出阻断项而不是模糊提示

## 功能需求

### PRD Authoring

| ID | 需求 |
|----|------|
| FR-003-001 | 系统必须支持“一句话想法 -> PRD 草案”流程，输出结构完整的 draft PRD |
| FR-003-002 | draft PRD 中所有不可推断项必须使用显式占位或假设块标记，不得伪装成已确认事实 |
| FR-003-003 | PRD Authoring 输出必须包含可供后续 PRD Gate / readiness review 消费的结构化元数据 |
| FR-003-004 | 系统必须区分 `draft_prd` 与 `final_prd` 两种状态，避免 draft 直接冒充冻结基线 |

### Human Reviewer

| ID | 需求 |
|----|------|
| FR-003-005 | 系统必须定义 Human Reviewer 的正式审批点：PRD freeze、docs baseline freeze、close / merge 前检查 |
| FR-003-006 | Reviewer 决策必须至少支持 `approve`、`revise`、`block` 三种结果 |
| FR-003-007 | Reviewer 决策必须记录时间、原因、目标对象和下一步动作，并可被 status / recover surface 读取 |

### Backend Delegation

| ID | 需求 |
|----|------|
| FR-003-008 | 系统必须为 Native / Plugin Backend 定义统一的 capability declaration 合同 |
| FR-003-009 | Runner 必须根据 capability coverage、policy 与安全约束决定委托给 Plugin 还是继续由 Native 执行 |
| FR-003-010 | 当 Plugin 不可用、能力不覆盖或策略禁止时，Runner 必须显式选择 Native 或返回 BLOCK |
| FR-003-011 | 当 Plugin 执行失败时，系统必须区分“可安全回退”与“不可安全回退”两类结果，并记录证据 |

### NFR 与 Release Gates

| ID | 需求 |
|----|------|
| FR-003-012 | 系统必须将可恢复性、可移植性、多 IDE 兼容、稳定性定义为可测量合同，而非仅描述性原则 |
| FR-003-013 | 发布门槛必须列出最小验证集合、证据来源与 BLOCK 条件 |
| FR-003-014 | 多 IDE 与非交互环境必须定义一致的降级与帮助输出策略 |
| FR-003-015 | 任何发布前检查结果必须可映射到 PASS / WARN / BLOCK 三类决策 |

## 成功标准

- **SC-003-001**：一句话输入可生成结构完整的 PRD draft，且未决项被显式标注
- **SC-003-002**：Reviewer 审批点在至少 3 个关键节点可被统一建模与展示
- **SC-003-003**：同一操作在 Native / Plugin 之间的选择原因可被记录与复盘
- **SC-003-004**：Plugin 失败时能区分“回退继续”与“阻断停止”两类结果
- **SC-003-005**：至少 4 项 NFR 拥有可测量的发布前检查条目
- **SC-003-006**：发布门槛可输出明确 BLOCKER，而不是仅文本建议
