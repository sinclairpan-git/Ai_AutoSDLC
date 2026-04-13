# 功能规格：Frontend Program Execute Runtime Baseline

**功能编号**：`020-frontend-program-execute-runtime-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../019-frontend-program-orchestration-baseline/spec.md`](../019-frontend-program-orchestration-baseline/spec.md)

> 口径：本 work item 是 `019-frontend-program-orchestration-baseline` 之后的下游 child work item，用于把 `program integrate --execute` 的 frontend runtime boundary、recheck handoff 与 remediation hint 收敛成单一 formal truth。它不是新的 scanner/provider，不是完整 auto-fix engine，也不是跨 spec 的隐式 writeback runtime；它只处理“program execute 何时允许进入、何时必须阻断、何时触发 recheck、何时只留下 remediation hint”这条主线。

## 问题定义

`019` 已经把 per-spec frontend readiness truth 接到了 `ProgramService`、`program status` 与 `program integrate --dry-run`。当前仓库已经具备：

- active spec scope 下的 runtime attachment truth
- verify / gate 层的 frontend gate summary truth
- `program status / integrate --dry-run` 的 frontend readiness / hint surface

但 `program --execute` 仍缺少独立 formal truth：

- 当前 execute gate 只认识 spec close / dep block / dirty tree，还不认识 frontend readiness
- program-level execute runtime 尚未明确什么时候要以 frontend readiness 阻断，什么时候只做 recheck handoff
- `018` 已冻结了 gate / recheck / auto-fix 的边界，但 program execute 还没有 formal baseline 说明如何消费这些边界
- 若继续直接编码，容易把 execute gate、runtime attachment、recheck loop、remediation hint 与 auto-fix engine 混成过宽工单

因此，本 work item 先要解决的不是“立即做 program 级前端自动修复”，而是：

- `program --execute` 的最小 frontend 输入真值是什么
- execute preflight 应如何消费 per-spec frontend readiness truth
- recheck 在 program execute 中的触发时机、粒度与输出是什么
- remediation hint 与 auto-fix engine 的边界如何被诚实暴露

## 范围

- **覆盖**：
  - 将 frontend program execute runtime 正式定义为 `019` 下游独立 child work item
  - 锁定 program execute 的 frontend 输入真值，包括 `019` per-spec readiness 与 `018` gate / recheck baseline
  - 锁定 execute preflight、step-level recheck handoff 与 remediation hint 的责任边界
  - 锁定 failure honesty、只读诊断与 explicit guard 的 formal baseline
  - 为后续 `core / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 在本 work item 中直接实现完整 auto-fix engine、cross-spec writeback、registry orchestration 或 provider 写入
  - 改写 `014` runtime attachment truth、`018` frontend gate truth 或 `019` readiness aggregation truth
  - 将 `program --execute` 扩张成默认启用的 scanner / attach / auto-fix 入口
  - 新增第二套 program-level frontend execute truth、第二套 recheck system 或第二套 remediation pipeline

## 已锁定决策

- program execute 只能消费 `019` 已聚合的 per-spec frontend readiness truth，不得另造 program 私有 execute truth
- execute preflight 必须按 spec 粒度暴露 frontend blockers，不得把多 spec 压成伪全局“可以执行”
- recheck 是 program execute 的 bounded handoff，不是后台无限 loop
- remediation hint 只用于诚实暴露下一步，不等于默认 auto-fix
- scanner/provider 写入、auto-attach、auto-fix、registry 与 cross-spec writeback 仍留在下游 work item

## 用户故事与验收

### US-020-1 — Framework Maintainer 需要 program execute 有独立 frontend runtime 真值层

作为**框架维护者**，我希望 `program --execute` 的 frontend runtime 在 formal docs 中有独立 child work item，以便 execute gate、recheck 与 remediation hint 不再混在 `019` 或 `018` 的临时实现里。

**验收**：

1. Given 我查看 `020` formal docs，When 我追踪 frontend 主线，Then 可以明确看到它位于 `019` 下游  
2. Given 我审阅 `020` formal docs，When 我确认输入真值，Then 可以明确读到 execute 只消费 per-spec readiness truth 与 `018` recheck boundary

### US-020-2 — Operator 需要在 execute 前知道哪些 spec 会被 frontend 阻断

作为**operator**，我希望 `program integrate --execute` 在正式执行前能明确说明哪些 spec 的 frontend readiness 不清晰、哪些需要 recheck、哪些只能给 remediation hint，以便不会误把 dry-run 的 hint 当成 execute 已自动接线。

**验收**：

1. Given 我运行 `program integrate --execute`，When 某个 spec frontend readiness 不 clear，Then `020` formal docs 已明确它必须如何阻断或暴露 hint  
2. Given 某个 spec 通过 execute preflight 但需要复查，When program execute 结束该 spec 的 integration step，Then `020` formal docs 已明确 recheck handoff 的存在与边界

### US-020-3 — Reviewer 需要 execute runtime 不偷渡 auto-fix

作为**reviewer**，我希望 `020` 明确 program execute 不会默认触发 auto-fix、writeback 或 scanner/provider 写入，以便后续实现不会把 execute runtime 扩张成隐式修复器。

**验收**：

1. Given 我检查 `020` formal docs，When 我确认 non-goals，Then 可以明确读到 auto-fix、writeback、registry 与 scanner/provider 写入仍是下游保留项  
2. Given 我查看 `020` 的 plan/tasks，When 我准备进入实现，Then 可以直接获得推荐文件面与最小测试矩阵

## 功能需求

| ID | 需求 |
|----|------|
| FR-020-001 | `020` 必须作为 `019` 下游的 frontend program execute runtime child work item 被正式定义 |
| FR-020-002 | `020` 必须明确 execute runtime 只消费 `019` per-spec frontend readiness truth 与 `018` gate / recheck 边界 |
| FR-020-003 | `020` 必须定义 per-spec frontend execute gate 的最小暴露面，包括 execute state、blockers、recheck_required、remediation hints 与 source linkage |
| FR-020-004 | `020` 必须明确 `program integrate --execute` 的 frontend preflight 责任与阻断条件 |
| FR-020-005 | `020` 必须明确 step-level frontend recheck 的触发时机、粒度与输出边界 |
| FR-020-006 | `020` 必须明确 remediation hint 只做诊断 handoff，不默认触发 auto-fix |
| FR-020-007 | `020` 必须明确 execute 失败、未接线、来源不明与 invalid readiness 必须诚实暴露 |
| FR-020-008 | `020` 必须明确 execute runtime 不默认启用 scanner/provider 写入、auto-attach、registry、auto-fix 或 cross-spec writeback |
| FR-020-009 | `020` 必须明确 readiness / recheck / remediation 都按 spec 粒度暴露，不得压成伪全局 verdict |
| FR-020-010 | `020` 必须为后续 `core / cli / tests` 的实现提供单一 formal baseline |
| FR-020-011 | `020` 必须明确实现起点优先是 execute preflight / recheck handoff，而不是直接进入 auto-fix engine |
| FR-020-012 | `020` 必须明确 `program status` / `integrate --dry-run` 的只读 surface 不等于 execute runtime 已启用 |

## 关键实体

- **Program Frontend Execute Gate**：承载每个 spec 在 execute preflight 的 frontend gate state
- **Program Frontend Recheck Handoff**：承载 step-level execute 后需要复查的 frontend recheck 输入与提示
- **Program Frontend Remediation Hint**：承载 execute 失败或未接线时的最小 remediation guidance
- **Frontend Execute Source Linkage**：承载 execute gate 与 `019` readiness / `018` gate-recheck baseline 的链接关系

## 成功标准

- **SC-020-001**：`020` formal docs 可以独立表达 program execute runtime 的 scope、truth order 与 non-goals  
- **SC-020-002**：execute preflight、recheck handoff 与 remediation hint 在 formal docs 中具有单一真值  
- **SC-020-003**：reviewer 能从 `020` 直接读出 execute runtime 不会默认开启 auto-fix、writeback 或 scanner/provider 写入  
- **SC-020-004**：后续实现团队能够从 `020` 直接读出 `core / cli / tests` 的推荐文件面与最小测试矩阵  
- **SC-020-005**：`020` formal baseline 不会回写或冲掉 `014`、`018`、`019` 已冻结的既有 truth

---
related_doc:
  - "specs/110-frontend-foundation-mainline-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
