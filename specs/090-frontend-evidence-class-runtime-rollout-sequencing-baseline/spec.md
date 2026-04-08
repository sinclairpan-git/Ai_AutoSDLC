# 功能规格：Frontend Evidence Class Runtime Rollout Sequencing Baseline

**功能编号**：`090-frontend-evidence-class-runtime-rollout-sequencing-baseline`  
**创建日期**：2026-04-09  
**状态**：已冻结（formal baseline）  
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md`](../088-frontend-evidence-class-bounded-status-surface-baseline/spec.md)、[`../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md`](../089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/models/program.py`](../../src/ai_sdlc/models/program.py)

> 口径：`090` 把 `frontend_evidence_class` 的 future runtime rollout 顺序冻结成一条 prospective-only baseline。它回答在不 retroactive 改写历史 item、且尽量减少后续重构的前提下，verify / manifest mirror / writeback / validate / status / close-check 应按什么依赖顺序实现；它不实现 runtime，不新增字段，不修改当前 CLI 或 machine truth。

## 问题定义

到 `089` 为止，`frontend_evidence_class` 的 authoring surface、diagnostics family、verify first cut、manifest mirror contract、writeback owner、status surface 与 close-stage resurfacing 都已经各自冻结，但“未来到底先实现哪一层、后实现哪一层”还没有形成统一 rollout order。

如果这层继续留白，后续实现极容易出现这些返工模式：

- 先做 `program status` / `status --json` / `workitem close-check` surfacing，之后才补 owning surfaces，导致 summary surface 反客为主
- 先做 `program validate` drift verdict，但还没有 mirror writeback path，造成 drift 只能报不能修
- 先把 mirror 塞进 manifest / model，再回头改 `verify constraints` 的 canonical parse，导致 source precedence 漂移
- 多个 surface 在不同时间各自接一部分 diagnostics payload，最后需要统一压缩

因此，`090` 的职责是把 future runtime rollout 收敛成一条 **最小返工顺序**：先做 authoring first-detection，再做 mirror carrier 与 explicit writeback，再做 drift validation，最后才做 summary 与 close-stage resurfacing。

## 范围

- **覆盖**：
  - 新建 `090` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `90`
  - 冻结 future `frontend_evidence_class` runtime rollout 的推荐实现顺序
  - 冻结各阶段的先后依赖、允许激活的 surface 与禁止抢跑的 surface
  - 冻结“上游 owning surface 未就绪时，下游 surface 不得抢跑”的 rollout 规则
- **不覆盖**：
  - 修改 `src/`、`tests/`、`program-manifest.yaml`
  - 新增 runtime flags、manifest 字段、JSON keys、table columns 或 error strings
  - 定义具体实现 PR 切分、工时或负责人
  - retroactively 改写 `068` ~ `071` 或任何历史 spec 的当前 truth

## 已锁定决策

- future runtime rollout 必须遵守 **owner-first, summary-last**
- `verify constraints` 的 authoring malformed first cut 必须先于 mirror drift / status / close-check 落地
- manifest mirror 的承载与 explicit writeback path 必须先于 `program validate` drift enforcement 落地
- `program status` / `status --json` 只能在上游 owning surfaces 已能稳定产出 derived summary 后再接入
- `workitem close-check` 只能最后接入 late resurfacing，不能早于 owning surfaces 与 status surface 抢跑

## Runtime Rollout Sequence Contract

### Phase 1. Authoring first-detection

第一阶段只允许实现 `085` 定义的 first runtime cut：

- 在 `verify constraints` 读取 `spec.md` footer 中的 canonical `frontend_evidence_class`
- 产出 `frontend_evidence_class_authoring_malformed`
- 维持 `BLOCKER` 级别与 `084` 冻结的最小 payload

这一阶段不得同步实现：

- mirror drift verdict
- manifest writeback
- status surfacing
- close-check resurfacing

原因：canonical source 与 malformed diagnostics 必须先稳定，后续所有 mirror / summary surface 才有可信上游。

### Phase 2. Mirror carrier and explicit writeback

第二阶段才允许实现 mirror 承载与显式写回：

- `program-manifest.yaml` 的 `specs[] .frontend_evidence_class` placement
- 与之对应的 model / parser 接纳面
- 一个显式 `ai-sdlc program ...` writeback family，负责把 footer truth 同步到 manifest mirror

这一阶段不得让 read-only surfaces opportunistic write。

原因：若 mirror placement 与 writer 不先稳定，后续 `program validate` 很容易在没有 canonical repair path 时提前报 drift。

### Phase 3. Mirror drift validation

第三阶段才允许接入 `086` 冻结的 `program validate` drift semantics：

- `mirror_missing`
- `mirror_invalid_value`
- `mirror_value_conflict`
- `mirror_stale`

前提：

- Phase 1 的 authoring malformed 已存在
- Phase 2 的 mirror carrier 与 explicit writeback 已存在

原因：drift 语义天然依赖 canonical source、mirror placement 与 repair path 三者同时成立。

### Phase 4. Bounded status surfacing

第四阶段才允许接入 `088` 冻结的 status surface：

- `program status` 的 program-scoped compact summary
- `status --json` 的 active-work-item bounded summary

前提：

- 至少一个 owning surface 已能稳定产出可消费的 derived summary
- `status` 仍只做 bounded resurfacing，不做 first-detection

原因：若 status 先于 owner 落地，后续一定要回头拆解责任与 payload。

### Phase 5. Close-stage late resurfacing

第五阶段才允许接入 `089` 冻结的 `workitem close-check` late resurfacing：

- close-stage 复报 unresolved evidence-class blocker
- table / json 两种 surface 均保持 bounded resurfacing

前提：

- Phase 1 与 Phase 3 的 owning surfaces 已存在
- Phase 4 的 bounded summary contract 已有稳定上游

原因：close-check 本质上是晚期复报 surface；若前面没有稳定 owner 与 summary，它只能被迫自做判定，直接违背 `089`。

## Rollout Guardrails

### 1. Owner-first rule

任何 future implementation 都不得先实现 summary surface，再回头补 owning surface。

若 `verify constraints` / `program validate` 尚未稳定产出 canonical / derived truth，则：

- `program status`
- `status --json`
- `workitem close-check`

都不得单独上线 evidence-class 相关 surfacing。

### 2. Writeback-before-drift rule

任何 future implementation 都不得在没有 explicit writeback path 的前提下，把 mirror drift enforcement 作为主路径上线。

若没有明确 write surface，则 drift 只能导致堆积，无法有框架内 canonical repair path。

### 3. Summary-last rule

`program status`、`status --json`、`workitem close-check` 必须视为 rollout 的后置层，而不是前置层。

这些 surface 只能消费已冻结、已稳定的上游 truth；它们的职责永远是重述，不是定义。

### 4. Non-retroactive rule

future rollout sequencing 只约束后续 implementation cut，不 retroactively 改写历史 item 的解释或当前 runtime truth。

## 用户故事与验收

### US-090-1 — Maintainer 需要一条少返工的实现顺序

作为 **future runtime maintainer**，我希望 evidence-class 的落地顺序被提前冻结，这样我不会先做 summary 或 drift，再回头重构 owner / writer。

**验收**：

1. Given 我准备开始实现 `frontend_evidence_class`，When 我对照 `090`，Then 我知道应先落 `verify constraints`，而不是先落 `status` 或 `close-check`
2. Given 我准备在 `program validate` 加 drift，When 我对照 `090`，Then 我知道 mirror placement 与 explicit writeback 必须先到位

### US-090-2 — Reviewer 需要判断某个实现 cut 是否抢跑

作为 **reviewer**，我希望能直接判断某个 future implementation 是否违反 rollout 顺序，这样我可以在代码阶段就挡掉高返工路径。

**验收**：

1. Given 某个 PR 先做 `status --json` surfacing，再补 `verify constraints` malformed，When 我对照 `090`，Then 我知道它违反 owner-first rule
2. Given 某个 PR 先报 `mirror_stale`，但没有 explicit writeback surface，When 我对照 `090`，Then 我知道它违反 writeback-before-drift rule

### US-090-3 — Author 需要知道 close-check 为什么要最后接

作为 **author**，我希望 close-check 的接入时机被写死，这样我不会把 close-stage 误当成最早实现入口。

**验收**：

1. Given 我想先在 close-check 暴露 evidence-class blocker，When 我对照 `090`，Then 我知道它必须晚于 owner 与 status surface
2. Given close-check 需要自做判断才能工作，When 我对照 `090`，Then 我知道 rollout 顺序已经错了

## 功能需求

| ID | 需求 |
|----|------|
| FR-090-001 | `090` 必须冻结 future runtime rollout 遵守 `owner-first, summary-last` |
| FR-090-002 | `090` 必须冻结 `verify constraints` authoring malformed first cut 为 rollout 的第一阶段 |
| FR-090-003 | `090` 必须冻结 manifest mirror carrier 与 explicit writeback 为 `program validate` drift 之前置阶段 |
| FR-090-004 | `090` 必须冻结 `program validate` mirror drift validation 只能在 canonical source、mirror placement 与 writeback path 均存在后接入 |
| FR-090-005 | `090` 必须冻结 `program status` / `status --json` 只能在上游 owning surfaces 已稳定产出 derived summary 后接入 |
| FR-090-006 | `090` 必须冻结 `workitem close-check` 只能作为最后阶段的 late resurfacing surface 接入 |
| FR-090-007 | `090` 必须明确 summary 与 close-stage surfaces 不得抢跑 owner / writer / validator |
| FR-090-008 | `090` 不得修改 `src/`、`tests/`、`program-manifest.yaml`、当前 CLI 或历史 runtime truth |
| FR-090-009 | `090` 不得定义具体 PR 拆分、工时估算、负责人或实现日期 |
| FR-090-010 | `090` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `89` 推进到 `90` |

## 成功标准

- **SC-090-001**：future maintainer 能直接用 `090` 排出一条少返工的 implementation order
- **SC-090-002**：reviewer 能直接判断某个 future implementation 是否让 summary / close-stage surface 抢跑
- **SC-090-003**：author 能直接判断 mirror drift 是否在没有 repair path 时被过早引入
- **SC-090-004**：本轮 diff 仅新增 `090` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/088-frontend-evidence-class-bounded-status-surface-baseline/spec.md"
  - "specs/089-frontend-evidence-class-close-check-late-resurfacing-baseline/spec.md"
  - "src/ai_sdlc/core/verify_constraints.py"
  - "src/ai_sdlc/core/close_check.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/models/program.py"
frontend_evidence_class: "framework_capability"
---
