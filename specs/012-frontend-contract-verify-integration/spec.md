# 功能规格：Frontend Contract Verify Integration

**功能编号**：`012-frontend-contract-verify-integration`  
**创建日期**：2026-04-02  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`../011-frontend-contract-authoring-baseline/plan.md`](../011-frontend-contract-authoring-baseline/plan.md)、[`../011-frontend-contract-authoring-baseline/task-execution-log.md`](../011-frontend-contract-authoring-baseline/task-execution-log.md)

> 口径：本 work item 是 `011-frontend-contract-authoring-baseline` 下游的第二个 child work item，用于把 frontend contract 的 verify integration 收敛成单一 formal baseline。它不是 scanner、fix-loop、auto-fix 或新的平行 gate system，而是只处理 `frontend_contract_gate -> verify constraints -> VerificationGate/VerifyGate -> cli verify` 这条正式集成链。

## 问题定义

`011` 已经把 frontend contract 主线拆成可执行对象，并落下了：

- `Frontend Contract Set / Page Contract / Module Contract` 模型
- `contracts/frontend/**` artifact instantiation
- artifact-vs-observation drift helper
- 最小 `frontend_contract_gate` 只读 gate surface

但当前框架仍存在三类 verify integration 缺口：

- `verify constraints` 还没有把 frontend contract 真值面纳入显式 verification source / check object / coverage gap
- `VerificationGate / VerifyGate` 只理解通用 verification surface，还没有冻结 contract-aware aggregation 的正式口径
- 若继续直接编码，很容易把 verify integration、scanner、registry 接线、fix-loop 与 auto-fix 混成一个过宽工单，丢掉 `011` 刚冻结出来的边界

因此，本 work item 要先解决的不是“再多写一个 helper”，而是：

- frontend contract verification 应如何进入现有 `verify constraints` 真值面
- `frontend_contract_gate` 与 `VerificationGate / VerifyGate` 的上下游关系是什么
- 缺失 artifact、缺失 observation、存在 drift 时，verify surface 应如何诚实暴露，而不是静默 PASS
- scanner / fix-loop / auto-fix 哪些必须明确留在下游 work item

## 范围

- **覆盖**：
  - 将 `011` 的最小 contract-aware gate surface 正式接入 `verify constraints -> VerificationGate / VerifyGate -> cli verify` 的产品合同
  - 锁定 frontend contract verification 的 source、check object、coverage gap 与 blocker/advisory 口径
  - 锁定 `frontend_contract_gate`、`verify constraints`、`VerificationGate / VerifyGate` 与 `verify --json` 之间的数据边界
  - 锁定 observation 作为结构化输入边界的单一口径，但不决定 scanner 的具体实现
  - 为后续 core/gates/cli/tests 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现源码 scanner、AST 提取或 observation 自动生产器
  - 实现 fix-loop、auto-fix、contract writeback 或 remediation workflow
  - 新建一套平行于 `VerificationGate` 的 verify stage / gate system
  - 改写 UI Kernel、Provider、runtime 或 frontend code generation 主线
  - 在本 work item 中直接完成全部 verify integration 运行时代码

## 已锁定决策

- frontend contract verification 必须进入现有 `verify constraints` 与 `VerificationGate / VerifyGate` 真值链，不得另起平行校验系统
- `frontend_contract_gate` 是上游只读汇总面，不是 `VerificationGate` 的替代品
- observation 必须以结构化输入进入 verify integration，不得退回 prompt 或自由文本比对
- 若 contract artifact 缺失、observation 缺失或存在 drift，verify surface 必须显式暴露真实状态，不得静默 PASS
- scanner、fix-loop 与 auto-fix 保持在下游 work item，不在 `012` 中混做
- 是否需要 registry 显式挂载新别名，必须以“复用现有 `verify / verification` stage 优先”为基线，不得默认扩张为新 stage

## 用户故事与验收

### US-012-1 — Framework Maintainer 需要 contract truth 进入 verify 主链

作为**框架维护者**，我希望 frontend contract 的 artifact / observation / drift 结果能进入现有 `verify constraints` 与 `VerificationGate` 主链，以便 verify 结论不再只看通用 governance，而能对 contract 真值面给出正式判断。

**验收**：

1. Given 我查看 `012` formal docs，When 我追踪 verify 链路，Then 可以明确看到 `frontend_contract_gate -> verify constraints -> VerificationGate / VerifyGate -> cli verify` 的正式关系  
2. Given contract artifact 缺失、observation 缺失或 drift 未清，When 我查看 `012` formal docs，Then 可以明确看到 verify surface 不能静默 PASS

### US-012-2 — Reviewer 需要 verify integration 与 scanner/fix-loop 解耦

作为**reviewer**，我希望 `012` 明确 verify integration 只负责消费 contract truth，而不顺手承担 scanner、fix-loop 或 auto-fix，以便后续实现不会再次把多个工作流混在一起。

**验收**：

1. Given 我审阅 `012` formal docs，When 我检查 observation 来源，Then 可以明确读到 `012` 只冻结结构化输入边界，不负责 scanner 实现  
2. Given 我审阅 `012` formal docs，When 我检查 remediation 相关范围，Then 不会把 fix-loop、auto-fix 或 contract writeback 误读成当前 work item 的一部分

### US-012-3 — Operator 需要 verify 命令诚实暴露 contract 状态

作为**operator**，我希望 `ai-sdlc verify constraints` 与其 JSON/terminal surface 能诚实显示 frontend contract 是否可验证、是否存在 drift 或覆盖缺口，以便不会被误导成“verify 全绿但 contract 其实未接线”。

**验收**：

1. Given frontend contract artifact 存在但 observation 缺失，When 我执行 verify，Then verify surface 应明确暴露“无法比较”的真实状态，而不是隐式忽略  
2. Given frontend contract drift 已被检测，When 我执行 verify，Then formal docs 能明确说明这会反映到 verification surface，而不是停留在单独 helper 内部

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-012-001 | `012` 必须作为 `011` 下游的 verify integration child work item 被正式定义，而不是继续把 verify 细节堆回 `011` |
| FR-012-002 | `012` 必须明确 frontend contract verification 进入现有 `verify constraints -> VerificationGate / VerifyGate -> cli verify` 真值链 |
| FR-012-003 | `012` 必须明确 `frontend_contract_gate` 是上游 contract-aware surface，不是新的平行 gate system |
| FR-012-004 | `012` 必须明确当前 work item 的非目标，包括 scanner、fix-loop、auto-fix、contract writeback 与完整运行时代码实现 |

### Verification Surface Contract

| ID | 需求 |
|----|------|
| FR-012-005 | `012` 必须定义 frontend contract verification 的最小 source、check object 与 coverage gap 口径 |
| FR-012-006 | `012` 必须明确 contract artifact 缺失、observation 缺失与 drift 未清时，verification surface 的诚实暴露规则 |
| FR-012-007 | `012` 必须明确 `verify constraints` 如何承载 contract-aware blocker / advisory / gap 信息 |
| FR-012-008 | `012` 必须明确 `VerificationGate / VerifyGate` 如何消费 frontend contract verification 结果，而不破坏现有显式 verification surface 结构 |

### Input Boundary And Integration Attachment

| ID | 需求 |
|----|------|
| FR-012-009 | `012` 必须明确 observation 以结构化输入边界进入 verify integration，不得退回自由文本 prompt 比对 |
| FR-012-010 | `012` 必须明确 scanner 只是下游 observation provider 的一种候选实现，不属于当前 work item 的正式范围 |
| FR-012-011 | `012` 必须明确优先复用现有 `verify / verification` stage，而不是默认新增 stage 或 gate registry 分支 |
| FR-012-012 | `012` 必须明确 CLI terminal / JSON surface 需要暴露 frontend contract verification 的最小摘要 |
| FR-012-016 | 当前 `verify_constraints` 切片只允许在 active work item 命中 `012` 时挂接 frontend contract verification，不得把 contract 缺口升级成所有仓库默认 blocker |
| FR-012-017 | 当前 `verify_constraints` 切片必须从 active `012` spec 目录下的 `frontend-contract-observations.json` 消费结构化 observation 输入；该文件只定义输入边界，不等价于 scanner 实现 |
| FR-012-018 | 若 active `012` 下缺失 `frontend-contract-observations.json`，`verify_constraints` 必须把它诚实暴露为 `frontend_contract_observations` coverage gap，而不是静默跳过 |

### Implementation Handoff

| ID | 需求 |
|----|------|
| FR-012-013 | `012` 必须为后续 `core / gates / cli / tests` 的实现提供单一 formal baseline |
| FR-012-014 | `012` 必须明确最小验证面至少覆盖 PASS、artifact 缺失、observation 缺失、drift 未清与 CLI/JSON surface 场景 |
| FR-012-015 | `012` 必须明确 verify integration 不得把 `011` 已冻结的 contract truth 重新复制为第二套规则实现 |

## 关键实体

- **Frontend Contract Verification Report**：承载一次 verify 对 frontend contract 状态的结构化汇总结果
- **Frontend Contract Verification Source**：承载 verify surface 中 contract-aware 结论的 source 名称与来源边界
- **Frontend Contract Check Object**：承载 `verify constraints` / `VerificationGate` 中与 frontend contract 相关的显式检查对象
- **Frontend Contract Coverage Gap**：承载“无法比较”或“未接线”的结构化缺口，而不是静默忽略
- **Observation Input Boundary**：承载 `PageImplementationObservation` 或等价结构化输入的消费边界
- **Frontend Contract Observation Input File**：承载 active `012` spec 目录下 `frontend-contract-observations.json` 的最小结构化 observation 输入边界
- **Verify Integration Attachment Strategy**：承载 frontend contract verification 挂接到 `verify constraints`、`VerificationGate / VerifyGate` 与 CLI 的正式方式

## 成功标准

- **SC-012-001**：`012` formal docs 可以独立表达 frontend contract verify integration 的边界，而无需回到 `011` 临时推断
- **SC-012-002**：contract artifact 缺失、observation 缺失与 drift 未清三类状态在 formal docs 中都具有诚实的 verification 口径
- **SC-012-003**：`verify constraints`、`VerificationGate / VerifyGate` 与 CLI surface 的关系在 formal docs 中保持单一真值
- **SC-012-004**：reviewer 能从 `012` 直接读出 scanner / fix-loop / auto-fix 不属于当前 work item，而是下游扩展
- **SC-012-005**：后续实现团队能够从 `012` 直接读出 `core / gates / cli / tests` 的最小文件面与验证矩阵

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
