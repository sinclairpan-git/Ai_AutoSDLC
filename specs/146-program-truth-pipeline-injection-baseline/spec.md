# 功能规格：Program Truth Pipeline Injection Baseline

**功能编号**：`146-program-truth-pipeline-injection-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：将 program/global truth 从可盘点账本提升为 AI-SDLC 各阶段必须注入、必须消费、必须保持 fresh 的流水线基础设施。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/140-program-truth-ledger-release-audit-baseline/spec.md`、`specs/141-program-manifest-root-census-backfill-baseline/spec.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`

> 口径：`140` 已冻结 root ledger / snapshot / release audit，`141` 已补齐 root manifest census，`145` 又证明了“source-complete global truth”仍没有真正进入流水线主链。formal docs 和 `close-check` 即使都通过，program truth 仍可能停在 `stale`，直到操作者手动执行 `program truth sync --execute --yes` 才恢复 `fresh`。`146` 的职责不是再造一套 global truth，而是把既有 root truth 真正注入到 `workitem init / truth sync / close-check / program status / run-stage gate` 的日常路径中，收口“真值会盘点、不会驱动”的框架缺口。

## 问题定义

当前仓库已经具备以下能力：

- 根级 `program-manifest.yaml` 已经是唯一 program-level 聚合入口；
- source inventory 已能统计全仓 `mapped / unmapped / missing`；
- `program truth sync`、`program truth audit`、`program status` 已经能消费 ledger/snapshot；
- `145` 已把剩余前端 deferred capability 纳入 formal planning truth。

但这次推进也暴露出同一个系统性问题：

- `workitem init` 只会创建 `specs/<WI>/` formal docs 并推进 `project-state.next_work_item_seq`，不会把新工单自动纳入根 manifest；
- `program truth sync` 能生成 snapshot，却没有成为 formal workitem 默认 handoff 的一部分；
- `close-check` 能检查 tasks / execution log / verification profile，却不能把 `manifest_unmapped` 与 `truth_snapshot_stale` 明确拆分成不同 remediation；
- `program status` 会告诉操作者 stale，但不会同时给出“下一条必须执行的 truth action”；
- `run --dry-run` 与 stage-level flow 目前也没有把 fresh global truth 当成显式注入前置。

结果就是：全局真值现在已经足够完整，但仍然偏向“audit/reporting layer”，不是“每个阶段都必须消费的基础设施”。只要这条缺口不补，后续任何 formal workitem 都可能再次出现：

- formal docs 已生成，但 manifest 仍未纳管；
- close wording 已通过，但 program truth 仍 stale；
- source inventory 已完整，但 operator 仍要手工判断下一步该跑什么命令。

因此，`146` 的职责是把 global truth 从“能盘点的机器账本”推进为“被 pipeline 强制注入的治理底座”。

## 范围

- **覆盖**：
  - 冻结 `workitem init -> manifest mapping -> truth sync -> close-check -> program status` 的 truth injection handoff contract
  - 明确 `manifest_unmapped`、`truth_snapshot_stale`、`truth_sync_required`、`read_only_surface` 的边界语义
  - 冻结 `program status` / `close-check` / `run` / stage gate 对 truth freshness 的最小消费要求
  - 冻结 truth-only / manifest-only 变更的 verification profile 口径
  - 冻结 stale truth 的 remediation guidance：系统必须告诉操作者“下一步执行什么”，而不是只显示 stale
  - 让 `146` 成为后续实现 `Program Truth Pipeline Injection` 的单一 formal carrier
- **不覆盖**：
  - 不重写 `140` 的 ledger schema、capability closure 词表或 source inventory 统计模型
  - 不新增第二份 dashboard、第二个 manifest 或平行 truth registry
  - 不在本工单中直接推进前端 `page/ui schema`、theme token、quality platform 等业务 capability
  - 不让 read-only surfaces 偷写 snapshot
  - 不把 truth freshness 问题伪装成“只要人工记得多跑一个命令即可”

## 已锁定决策

- global truth 仍以根级 `program-manifest.yaml` + `truth_snapshot` 为唯一 program-level 聚合入口，不新增第二真值；
- `workitem init` 之后，系统必须把“如何进入 global truth”视为 formal handoff，而不是额外的人工经验；
- read-only surfaces 继续保持只读，但必须明确指出 stale / unmapped / next action；
- stale truth 必须被视为 pipeline-level honesty 问题，而不是纯展示问题；
- verification profile 必须允许 truth-only / manifest-only 变更被诚实验证，不能长期借用 `code-change` 画像；
- `146` 的实现边界只覆盖 truth injection pipeline；不得借机扩展到前端业务 capability 或平行真值系统。

## 用户故事与验收

### US-146-1 — Operator 需要被明确引导完成 global truth handoff

作为**操作者**，我希望在创建或更新 formal workitem 后，系统能明确告诉我如何让它进入 global truth，而不是让我在 `program status` stale 之后再靠人工猜命令。

**优先级说明**：P0。`145` 已经证明如果缺少这条 handoff，formal docs、close-check 与 global truth 会再次脱节。

**独立测试**：创建新 workitem 后，系统能把 `manifest mapping / truth sync / next action` 暴露为显式 handoff，而不是只留下一个后来才出现的 stale 状态。

**验收场景**：

1. **Given** 我创建了新的 `specs/<WI>/` formal docs，**When** 它尚未进入 global truth，**Then** 系统必须显式指出缺少 manifest mapping 或 truth sync，而不是静默遗漏
2. **Given** 我刚完成 docs-only freeze，**When** 我查看 program/status 类 surface，**Then** 我能看到下一条 required truth action

### US-146-2 — Reviewer 需要区分 unmapped、stale 与真正的 capability blocker

作为**reviewer**，我希望 `close-check` 和 `program status` 把“manifest 未映射”“snapshot stale”“capability 未闭环”三类问题分开表达，这样我能知道是 pipeline 注入缺口，还是业务能力确实还没做完。

**优先级说明**：P0。当前最大的误判风险就是把治理注入缺口和业务未完成混在一起。

**独立测试**：对同一个 workitem，`manifest_unmapped`、`truth_snapshot_stale` 与 `capability blocked` 至少要能给出不同诊断与 remediation。

**验收场景**：

1. **Given** formal docs 已存在但 manifest 未纳管，**When** 我运行 `workitem close-check`，**Then** 我得到的是 `manifest_unmapped` 语义，而不是模糊失败
2. **Given** manifest 已纳管但 snapshot 已过期，**When** 我运行 `program status`，**Then** 我得到的是 `truth_snapshot_stale` 与下一步动作

### US-146-3 — Stage/Run Surface 需要消费 truth freshness

作为**框架维护者**，我希望 `run` / stage-level surface 不再把 global truth 当成旁路信息，而是至少在关键节点消费 freshness 与 required truth action。

**优先级说明**：P1。只要 stage flow 不消费 truth freshness，系统仍会回到“审计层知道，执行层不知道”的旧状态。

**独立测试**：当 truth stale 时，关键 stage surface 至少会显式 surfaced，而不是继续表现成“全部正常”。

**验收场景**：

1. **Given** truth snapshot stale，**When** 我执行与 close / status / run 相关的关键 surface，**Then** stale 必须被 surfaced
2. **Given** truth 已 fresh，**When** 我继续下游工单，**Then** 这些 surface 不会再提示额外 truth injection blocker

### 边界情况

- formal docs 已创建，但根 manifest 缺少对应 `specs[]` entry
- manifest entry 已存在，但 `truth_snapshot` 因 authoring change 或 source hash 漂移而 stale
- read-only surface 被要求“顺手修复”，但 contract 明确禁止它偷写 snapshot
- truth-only 改动没有业务代码 diff，但仍需要合适的 verification profile 与 close wording

## 功能需求

### Truth Injection Contract

| ID | 需求 |
|----|------|
| FR-146-001 | 系统必须把 program/global truth freshness 视为 AI-SDLC 流水线的显式治理前提，而不是可选审计输出 |
| FR-146-002 | 在创建新的 `specs/<WI>/` formal docs 后，系统必须要么 materialize 对应 manifest entry，要么明确给出 exact next action；不得静默留下 `manifest_unmapped` |
| FR-146-003 | 系统必须冻结 `workitem init -> manifest mapping -> truth sync -> close-check/program status` 的最小 handoff 顺序 |
| FR-146-004 | `program truth sync` 必须继续是显式写入口，但 `146` 必须让操作者知道何时必须执行该写入口 |

### Diagnostic And Gating Surfaces

| ID | 需求 |
|----|------|
| FR-146-005 | `workitem close-check` 必须能区分 `manifest_unmapped`、`truth_snapshot_stale`、`capability_blocked` 这三类诊断 |
| FR-146-006 | `program status` 必须在 truth 不 fresh 时给出“下一条 required truth action”，而不是只显示 stale |
| FR-146-007 | `run` / stage-related surfaces 必须在关键节点消费 truth freshness 或至少明确 surfaced stale 状态 |
| FR-146-008 | read-only surfaces 必须继续只读；不得通过 `status`、`close-check`、`run` 暗写 snapshot |

### Verification And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-146-009 | 系统必须为 manifest-only / truth-only 改动定义诚实的 verification profile，避免长期借用 `code-change` |
| FR-146-010 | `146` 必须明确区分“pipeline truth injection 缺口”与“业务 capability 真实未完成”，不得继续混淆这两类 blocker |
| FR-146-011 | `146` 必须允许 `145/147` 一类 planning workitem 被 global truth 直接消费，而无需重新手工 census |
| FR-146-012 | `146` 的实现必须只覆盖 truth injection pipeline 本身；不得顺带扩展到前端业务 capability 或平行真值系统 |

## 关键实体

- **Truth Injection Handoff**：从 formal workitem authoring 到 program truth fresh 的受控衔接路径
- **Manifest Mapping Gap**：`specs/<WI>/` 已存在，但根 manifest 尚未声明对应 `specs[]` entry 的状态
- **Truth Freshness Gate**：判断 snapshot 是否仍与当前 authoring / evidence 同步的治理门禁
- **Next Required Truth Action**：系统必须输出给 operator 的明确下一步动作，例如映射 manifest 或执行 truth sync
- **Truth-only Verification Profile**：适用于根 manifest / snapshot / formal planning truth 变更的验证画像

## 成功标准

- **SC-146-001**：新 formal workitem 建立后，系统可以诚实表达其是否已进入 global truth，而不是让 operator 依赖会话记忆
- **SC-146-002**：`manifest_unmapped`、`truth_snapshot_stale`、`capability_blocked` 三类问题有明确区分与 remediation 语义
- **SC-146-003**：关键 pipeline surface 至少会 surfaced stale truth，而不是继续把它当成旁路信息
- **SC-146-004**：truth-only / manifest-only 变更拥有明确 verification 口径
- **SC-146-005**：`146` 的 close 含义是 formal baseline 已建立，不伪造 runtime integration 已完成

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "specs/141-program-manifest-root-census-backfill-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
