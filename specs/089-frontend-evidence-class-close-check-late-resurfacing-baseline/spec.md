# 功能规格：Frontend Evidence Class Close-Check Late Resurfacing Baseline

**功能编号**：`089-frontend-evidence-class-close-check-late-resurfacing-baseline`  
**创建日期**：2026-04-09  
**状态**：已冻结（formal baseline）  
**输入**：[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)

> 口径：`089` 把 `frontend_evidence_class` 的 future `workitem close-check` surfacing 冻结成一条 prospective-only baseline。它回答 close-stage recheck 最多允许如何晚期重述 authoring malformed / mirror drift blocker、close-check 在 table / json 两种 read surface 上的 bounded 粒度，以及它明确不能承担哪些 first-detection、mirror writeback 或 full diagnostics 责任；它不实现 runtime，不新增 check，不改写 `verify constraints` / `program validate` / `program status` / `status --json` 的 owning semantics，也不 retroactively 改写 `068` ~ `071`。

## 问题定义

`083`、`084`、`085`、`086`、`087`、`088` 已经依次冻结了 detection surface、diagnostics family、verify/runtime first cut、manifest mirror contract、writeback owner 与 bounded status surface，但 close-stage resurfacing 还缺一层明确约束：

- `workitem close-check` 语义上是 close 前的晚期 truth recheck surface
- 它天然适合复报已经存在的 blocker，但不应该变成新的 first-detection / manifest rewrite 入口
- 如果不把这层边界单独写死，未来实现很容易出现两种偏差：
  - 在 close-check 阶段重新解析 `spec.md` footer 或 manifest mirror，自行生成新的 authoring / drift verdict
  - 把 full diagnostics payload 或 remediation prose 直接塞进 close-check 表格 / JSON，导致 close-stage surface 膨胀成 debug API

这会带来直接后果：

- close-check 与 owning surface 的职责重新缠绕
- close-stage failure 看起来像“新发现的问题”，而不是“晚期复报未解决 blocker”
- reviewer 无法判断 close-check 输出到底是 canonical blocker resurfacing，还是 close-stage 自己重判的结果

因此，`089` 的职责是把 `workitem close-check` 对 evidence-class 的 future surfacing 压缩为 **late resurfacing only**：它只能在 close-stage 重述 upstream blocker presence，并保持 bounded detail；不得承担 first-detection、mirror writeback、severity 重裁或 full diagnostics 展开。

## 范围

- **覆盖**：
  - 新建 `089` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `89`
  - 冻结 `workitem close-check` 对 evidence-class 的 close-stage late resurfacing 边界
  - 冻结 close-check table / json 两种输出面允许表达的最小粒度
  - 冻结 close-check 可复报的 problem family、bounded detail 与禁止展开项
  - 冻结 close-check 不得 first-detect / auto-heal / opportunistic write
- **不覆盖**：
  - 修改 `src/`、`tests/`、`program-manifest.yaml` 或任一 CLI 输出
  - 新增具体 check 名、JSON key 名、table 文案或 error string
  - 修改 `verify constraints`、`program validate`、`program status`、`status --json` 的既有 contract
  - 冻结 close-check 与 done gate / docs consistency / release governance 的交互顺序
  - retroactively 改写 `068` ~ `071` 或当前 runtime truth

## 已锁定决策

- `workitem close-check` 是 future evidence-class 的 **close-stage late resurfacing surface**
- close-check 只能复报 upstream already-detected blocker，不得自己重新解析 canonical source
- close-check table / json 只能承载 bounded blocker resurfacing，不得替代 owning diagnostics
- close-check 不得在 read path 上 opportunistic write `program-manifest.yaml` 或修正 spec footer
- close-check 允许复报的 problem family 仅限：
  - `frontend_evidence_class_authoring_malformed`
  - `frontend_evidence_class_mirror_drift`

## Close-Check Late Resurfacing Contract

### 1. Surface role

future `workitem close-check` 若 surfacing evidence-class 相关问题，只允许承担 **close-stage late resurfacing**。

最小允许语义：

- 当前 work item 是否仍存在 unresolved evidence-class blocker
- blocker 所属 problem family
- blocker 的 upstream owning surface
- 一条 bounded detail，例如单个 compact `error_kind`、`mirror_missing` 之类的极短 token，或“仍未解决”的短说明

close-check 不得表现为：

- canonical first-detection surface
- manifest writer / mirror repair surface
- full diagnostics export surface
- severity 重新判定 surface

### 2. Source and precedence

future close-check 若复报 evidence-class blocker，必须遵守如下优先级：

1. canonical detection 仍以上游 owning surface 为准：
   - `verify constraints` 负责 `frontend_evidence_class_authoring_malformed`
   - `program validate` 负责 `frontend_evidence_class_mirror_drift`
2. close-check 只能消费 upstream derived truth 或明确传递的 blocker summary
3. close-check 不得通过重新解析 `spec.md` footer 或 `program-manifest.yaml` 来创建新的 detection verdict

### 3. Allowed bounded resurfacing detail

future close-check 若在 table / json 输出 evidence-class 相关摘要，最多只能暴露以下 bounded truth：

- current work item identity
- blocker presence
- `problem_family`
- `detection_surface`
- 单个 compact `error_kind` / drift token / ultra-short detail

不得直接展开：

- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint` 的完整 prose
- footer / manifest 原文
- 多条 diagnostics 数组
- 可替代 owning surface 的 full payload JSON

### 4. Table / JSON parity boundary

future `workitem close-check` 即使同时支持 table 与 `--json`：

- 两种 surface 都只能表达 late resurfacing 的 bounded blocker truth
- `--json` 不得因为 machine-readable 就升级成 full diagnostics dump
- table 不得因为 close-stage 可读性需要而追加长段 remediation narrative

允许的差异只应体现在承载形式，不应体现在职责膨胀。

### 5. Non-healing and non-adjudication rule

future close-check 不承担：

- footer authoring 合法值判定
- mirror drift 的首次裁定
- missing mirror 的自动补写
- stale mirror 的 opportunistic refresh
- severity 重新分级
- source of truth 的修正写回

close-check 只能晚期重述“这个 blocker 仍然存在”，不能把自己变成修复入口。

## 用户故事与验收

### US-089-1 — Reviewer 需要知道 close-check 只是晚期复报

作为 **reviewer**，我希望 `workitem close-check` 对 evidence-class 只承担 late resurfacing，这样我不会把 close-stage blocker 误读成 close-check 自己新发现的问题。

**验收**：

1. Given future close-check 输出 evidence-class blocker，When 我对照 `089`，Then 我知道 canonical failure 仍来自上游 owning surface
2. Given future close-check 重新解析 footer 或 manifest 并自己给出 verdict，When 我对照 `089`，Then 我知道这已经越界

### US-089-2 — Maintainer 需要限制 close-check JSON 负载

作为 **future maintainer**，我希望 close-check 的 table / JSON 都只承载 bounded resurfacing，这样它不会膨胀成 close-stage diagnostics API。

**验收**：

1. Given future `workitem close-check --json` 输出 full payload JSON，When 我对照 `089`，Then 我知道这违反 bounded resurfacing contract
2. Given future close-check table 输出长段 remediation prose，When 我对照 `089`，Then 我知道它已经替代 owning diagnostics

### US-089-3 — Author 需要知道 close-stage 不是修复入口

作为 **author**，我希望 close-check 不偷写 manifest、不 auto-heal mirror，这样我知道修复仍然应回到 verify / validate / explicit writeback surface。

**验收**：

1. Given future close-check 发现 mirror missing，When 我对照 `089`，Then 我知道它最多只能复报 blocker，而不能顺手写回 mirror
2. Given future close-check 对 malformed / drift 重新判 severity，When 我对照 `089`，Then 我知道这违反 non-adjudication 规则

## 功能需求

| ID | 需求 |
|----|------|
| FR-089-001 | `089` 必须冻结 `workitem close-check` 是 future evidence-class 的 close-stage late resurfacing surface |
| FR-089-002 | `089` 必须明确 close-check 只能复报 upstream already-detected blocker，不得 first-detect `frontend_evidence_class` 问题 |
| FR-089-003 | `089` 必须冻结 close-check 允许复报的 problem family 仅限 `frontend_evidence_class_authoring_malformed` 与 `frontend_evidence_class_mirror_drift` |
| FR-089-004 | `089` 必须冻结 close-check table / json 最多只能暴露 blocker presence、problem family、detection surface 与单个 bounded detail |
| FR-089-005 | `089` 必须明确 close-check 不得暴露 full diagnostic payload、footer / manifest 原文、多条 remediation prose 或跨 work item diagnostics dump |
| FR-089-006 | `089` 必须明确 close-check 不得 opportunistic write `program-manifest.yaml`、refresh stale mirror、auto-heal missing mirror 或修正 spec footer |
| FR-089-007 | `089` 必须明确 close-check 不承担 severity 重新裁定或 source-of-truth 修复职责 |
| FR-089-008 | `089` 不得冻结具体 check 名、JSON key 名、table column 名、error string 或 check execution order |
| FR-089-009 | `089` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 runtime truth |
| FR-089-010 | `089` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `88` 推进到 `89` |

## 成功标准

- **SC-089-001**：future maintainer 能直接区分 close-check 的 late resurfacing 与 owning surface 的 first-detection
- **SC-089-002**：reviewer 能直接判断某个 close-check 输出是否越过 bounded resurfacing 边界
- **SC-089-003**：author 能直接判断 mirror 修复是否被错误塞进 close-check read path
- **SC-089-004**：本轮 diff 仅新增 `089` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "docs/USER_GUIDE.zh-CN.md"
  - "src/ai_sdlc/cli/workitem_cmd.py"
  - "src/ai_sdlc/core/close_check.py"
frontend_evidence_class: "framework_capability"
---
