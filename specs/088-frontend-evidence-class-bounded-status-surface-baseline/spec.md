# 功能规格：Frontend Evidence Class Bounded Status Surface Baseline

**功能编号**：`088-frontend-evidence-class-bounded-status-surface-baseline`  
**创建日期**：2026-04-09  
**状态**：已冻结（formal baseline）  
**输入**：[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)

> 口径：`088` 把 `frontend_evidence_class` 的 future bounded status surfacing 冻结成一条 prospective-only baseline。它回答 `program status` 与 `status --json` 最多允许露出什么级别的 summary、两者各自承载到什么粒度、以及哪些 diagnostics 永远不得在 status surface 直接展开；它不实现 runtime，不新增状态字段，不改写 `verify constraints` / `program validate` / `close-check` 的 owning semantics，也不 retroactively 改写 `068` ~ `071`。

## 问题定义

`083` 与 `084` 已经把 detection surface 和 diagnostics contract 冻结好了，但 status surfacing 仍然缺一层更细的边界：

- `program status` 是 program 级表格与 readiness 摘要，理论上适合暴露 per-spec blocker presence
- `status --json` 是 telemetry + active work item bounded read surface，不适合变成 cross-program diagnostics dump
- 若这层不再细化，后续实现很容易出现两种反方向偏差：
  - 把 full diagnostic payload 直接塞进 `program status` 或 `status --json`
  - 让 status surface 自己重解析 `spec.md` footer 或 manifest mirror，偷做 first-detection

这会带来直接后果：

- owning surface 与 summary surface 边界再次漂移
- `status --json` 从 bounded telemetry surface 膨胀成跨 program 的 evidence-class debug API
- reviewer 无法判断 status 输出究竟是 canonical failure 还是 best-effort visibility

因此，`088` 的职责是把两类 status surface 的可见性边界压缩到最小可实现面：`program status` 只允许 per-spec compact summary，`status --json` 只允许 active-work-item scoped 的最小 blocker presence，且二者都只能消费上游 derived truth，不得自行重新定责。

## 范围

- **覆盖**：
  - 新建 `088` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `88`
  - 冻结 `program status` 对 evidence-class 的 bounded summary 粒度
  - 冻结 `status --json` 对 evidence-class 的 bounded summary 粒度
  - 冻结 status surface 允许暴露的最小字段与禁止暴露的 full payload 内容
  - 冻结 status surface 不得承担 first-detection / authoring adjudication
- **不覆盖**：
  - 修改 `src/`、`tests/`、`program-manifest.yaml` 或任一 CLI 输出
  - 冻结具体 JSON key 名、table column 名或 UI 文案
  - 修改 `verify constraints`、`program validate`、`workitem close-check` 的 owning semantics
  - 让 `status --json` 变成 cross-program manifest surface
  - retroactively 改写 `068` ~ `071` 或当前 runtime truth

## 已锁定决策

- `program status` 是 future evidence-class status surfacing 的 **program-scoped compact summary surface**
- `status --json` 是 future evidence-class status surfacing的 **active-work-item bounded summary surface**
- 两类 surface 都只能消费 upstream derived truth，不得自己重解析 `spec.md` footer 或 `program-manifest.yaml`
- 两类 surface 都不得输出足以替代 owning surface 的 full diagnostic payload
- `program status` 可以按 spec 暴露 blocker presence 与 problem-family-level summary，但不得展开 full remediation narrative
- `status --json` 即使 future 暴露 evidence-class 相关信息，也只能限定在当前 active work item，不得扩展成全 program spec 列表

## Status Surface Contract

### 1. `program status` boundary

future `program status` 若暴露 evidence-class 相关信息，只允许承担 **program-scoped compact summary**。

最小允许语义：

- spec 级 blocker presence
- blocker family：
  - `frontend_evidence_class_authoring_malformed`
  - `frontend_evidence_class_mirror_drift`
- 可选的一条 bounded hint，例如单个 `error_kind` 或极短 summary token

不得直接展开：

- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint` 的 full narrative
- 多条 diagnostics 列表
- 可替代 owning surface 的完整错误堆栈

### 2. `status --json` boundary

future `status --json` 若暴露 evidence-class 相关信息，只允许承担 **active-work-item bounded summary**。

最小允许语义：

- 当前 active work item 是否存在 evidence-class blocker
- blocker 所属 problem family
- blocker 对应的 owning surface

约束：

- 不得输出 cross-program spec 列表
- 不得输出 per-spec diagnostics 数组
- 不得因为没有 active work item 就补扫整个 manifest
- 不得把 telemetry surface 扩展成 manifest / validator debug dump

### 3. Source and precedence

两类 status surface 的 future 实现必须遵守：

1. canonical detection 仍以上游 owning surface 为准：
   - `verify constraints` 负责 `frontend_evidence_class_authoring_malformed`
   - `program validate` 负责 `frontend_evidence_class_mirror_drift`
2. status surface 只可消费 derived summary
3. status surface 不得通过重新解析 canonical source 来制造 first-detection

### 4. Allowed bounded summary fields

future status surface 若要表达 evidence-class 摘要，最多只能来自以下 bounded truth：

- `spec_id` 或 active work item identity
- `problem_family`
- `detection_surface`
- blocker presence / blocker count
- 一个极短 summary token（如单个 `error_kind` 或 compact state）

不得直接暴露：

- `spec.md` footer 原文
- manifest mirror 原文
- 多段 remediation prose
- source file path 集合
- full diagnostic payload JSON

### 5. Non-adjudication rule

future `program status` / `status --json` 不承担：

- allowed values 判定
- malformed 与 drift 的首次定责
- severity 重新裁定
- mirror auto-heal

它们只能重述 upstream truth，而不能重写 upstream truth。

## 用户故事与验收

### US-088-1 — Reviewer 需要知道 `program status` 能露出多少

作为 **reviewer**，我希望 `program status` 的 evidence-class 输出被压到 compact summary 级别，这样我不会把表格视图误当成 full validator diagnostics。

**验收**：

1. Given future `program status` 展示 evidence-class blocker，When 我对照 `088`，Then 我知道它最多只应给 spec 级 compact summary
2. Given future `program status` 开始输出完整 remediation narrative，When 我对照 `088`，Then 我知道这已经越界

### US-088-2 — Maintainer 需要防止 `status --json` 膨胀

作为 **future maintainer**，我希望 `status --json` 的 scope 被限制在 active work item 上，这样它不会演变成 cross-program diagnostics API。

**验收**：

1. Given future `status --json` 没有 active work item，When 我对照 `088`，Then 我知道它不应去补扫整个 manifest 以生成 evidence-class summary
2. Given future `status --json` 开始输出 per-spec diagnostics 数组，When 我对照 `088`，Then 我知道这违反 bounded surface contract

### US-088-3 — Author 需要知道 status 不负责第一次发现问题

作为 **author**，我希望 status surface 只做重述，不做首次定责，这样我知道真正的修复入口仍然是 `verify constraints` 或 `program validate`。

**验收**：

1. Given future status surface 报出 evidence-class blocker，When 我对照 `088`，Then 我知道 canonical failure 仍来自 owning surface
2. Given future status surface 自己重新判定 footer 或 manifest，When 我对照 `088`，Then 我知道它已经越界

## 功能需求

| ID | 需求 |
|----|------|
| FR-088-001 | `088` 必须冻结 `program status` 是 future evidence-class 的 program-scoped compact summary surface |
| FR-088-002 | `088` 必须冻结 `status --json` 是 future evidence-class 的 active-work-item bounded summary surface |
| FR-088-003 | `088` 必须明确两类 status surface 只能消费 upstream derived truth，不得自行重解析 `spec.md` footer 或 manifest mirror |
| FR-088-004 | `088` 必须冻结 `program status` 最多只能暴露 spec 级 blocker presence、problem family 与单条 bounded hint |
| FR-088-005 | `088` 必须冻结 `status --json` 最多只能暴露 active-work-item blocker presence、problem family 与 owning surface |
| FR-088-006 | `088` 必须明确 status surface 不得暴露 full diagnostic payload、remediation narrative、path 集合或 cross-program diagnostics dump |
| FR-088-007 | `088` 必须明确 status surface 不承担 first-detection、severity adjudication 或 mirror auto-heal |
| FR-088-008 | `088` 不得冻结具体 JSON key 名、table column 名或 CLI 文案 |
| FR-088-009 | `088` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 runtime truth |
| FR-088-010 | `088` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `87` 推进到 `88` |

## 成功标准

- **SC-088-001**：future maintainer 能直接区分 `program status` 与 `status --json` 的 evidence-class 粒度边界
- **SC-088-002**：reviewer 能直接判断某个 status 输出是否越过 bounded summary 边界
- **SC-088-003**：status surface 不会反客为主，替代 owning surface 的诊断语义
- **SC-088-004**：本轮 diff 仅新增 `088` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "USER_GUIDE.zh-CN.md"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/commands.py"
  - "src/ai_sdlc/telemetry/readiness.py"
frontend_evidence_class: "framework_capability"
---
