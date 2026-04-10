# 功能规格：Frontend Evidence Class Verify First Runtime Cut Baseline

**功能编号**：`085-frontend-evidence-class-verify-first-runtime-cut-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`](../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md)、[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-08-frontend-evidence-class-verify-first-runtime-cut-design.md`](../../docs/superpowers/specs/2026-04-08-frontend-evidence-class-verify-first-runtime-cut-design.md)

> 口径：`085` 把 `frontend_evidence_class` 的首个 future runtime cut 冻结成一条 prospective-only baseline。它只回答 `verify constraints` 应该先从哪里读取 canonical truth、应在什么边界内产出哪一类 authoring malformed diagnostics；它不实现 runtime，不定义 manifest mirror，不改写 `program status`，也不 retroactively 改写 `068` ~ `071`。

## 问题定义

`081` ~ `084` 已经分别冻结了：

- `framework_capability` / `consumer_adoption` 的 prospective split
- `frontend_evidence_class` 的 authoring surface
- future detection surface 的 owning command
- problem family / severity / minimum payload 的 diagnostics contract

但还有一个关键空档没有冻结：future runtime 第一刀到底插在哪里。若这层继续留白，后续实现很容易出现：

- 先把 footer 读取逻辑塞进 frontend observation gate，导致 authoring truth 和 consumer artifact truth 混层
- 先去做 manifest mirror，再反过来定义 `verify constraints` 的 authoring malformed 语义
- 在不同模块里重复解析 `spec.md` footer，形成多份非 canonical 读路径

因此，`085` 的职责是只冻结一件事：future `verify constraints` 的 first runtime cut 应如何读取 `frontend_evidence_class`、如何产出 `frontend_evidence_class_authoring_malformed`，以及哪些内容必须明确排除在当前 cut 之外。

## 范围

- **覆盖**：
  - 新建 `085` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `85`
  - 冻结 `verify constraints` first runtime cut 的 canonical source-of-truth
  - 冻结 future reader/helper 的推荐落点与职责边界
  - 冻结 `frontend_evidence_class_authoring_malformed` 在首个 runtime cut 内的 allowed `error_kind`
  - 冻结当前 cut 的 non-goals，防止 mirror/status/close-stage 语义抢跑
- **不覆盖**：
  - 修改 `src/`、`tests/` 或任一 CLI 输出
  - 设计 manifest mirror schema、同步时机或 drift 判定逻辑
  - 修改 `program status`、`status --json`、`workitem close-check`
  - retroactively 改写 `068` ~ `071` 或既有 runtime truth
  - 新增 frontend-only validator command

## 已锁定决策

- future first runtime cut 只属于 `verify constraints`
- future first runtime cut 只认 work item `spec.md` footer metadata 中的 `frontend_evidence_class` 为 canonical source-of-truth
- future reader/helper 应落在 `verify constraints` 的治理读路径附近，而不是 frontend observation gate
- future first runtime cut 只允许产出 `frontend_evidence_class_authoring_malformed`
- allowed `error_kind` 只限：
  - `missing_footer_key`
  - `empty_value`
  - `invalid_value`
  - `duplicate_key`
  - `body_footer_conflict`
- 当前 cut 的最低严重级别边界仍沿用 `084`：在 owning surface 上不得低于 `BLOCKER`
- 当前 cut 不读取 `program-manifest.yaml`，不引入 mirror semantics，不向 status surface 投放 full diagnostics

## Runtime Cut Contract

### 1. Owning surface

future first runtime cut 的 owning surface 是 `verify constraints`。

原因：

- `083` 已冻结 authoring malformed 的 first owning surface 就是 `verify constraints`
- 该命令天然承接 repo-level governance / authoring truth 校验
- 当前问题属于 spec authoring truth，不依赖外部实现 artifact

### 2. Canonical source-of-truth

future runtime 在当前 cut 中只认 future work item `spec.md` footer metadata：

```md
frontend_evidence_class: "framework_capability"
```

本 cut 不允许把以下对象提升为 correctness source：

- `program-manifest.yaml`
- `status --json`
- frontend observation artifact
- 任一 body prose mirror

### 3. Reader placement

future 实现应在 [/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/verify_constraints.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/verify_constraints.py) 的现有治理读取路径附近增加一个 bounded helper。

该 helper 只负责：

- 定位 target work item 的 `spec.md`
- 读取 footer metadata
- 提取 `frontend_evidence_class`
- 返回合法 canonical value，或返回结构化 malformed diagnostics 输入

该 helper 不负责：

- 读取 `program-manifest.yaml`
- 构建 status summary
- 读取 frontend observation artifacts
- 做 close-stage adjudication

### 4. Separation from frontend contract gate

future implementation 不得把本 cut 塞进 [/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/frontend_contract_verification.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/core/frontend_contract_verification.py)。

原因：

- frontend contract gate 负责的是 consumer observation 与 drift
- `frontend_evidence_class` 属于 spec authoring truth
- 若两者混层，后续 mirror/adoption semantics 会被错误绑定到 observation lifecycle

## Diagnostic Contract

### 1. Problem family

future first runtime cut 只允许产出：

- `frontend_evidence_class_authoring_malformed`

### 2. Allowed error kinds

future `verify constraints` 在当前 cut 里只允许使用以下 bounded `error_kind`：

- `missing_footer_key`
- `empty_value`
- `invalid_value`
- `duplicate_key`
- `body_footer_conflict`

### 3. Minimum payload

future emitted diagnostic 最少必须包含：

- `problem_family`
- `detection_surface`
- `spec_path`
- `error_kind`
- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint`

### 4. Severity boundary

future first runtime cut 若命中上述 malformed 条件，owning surface 上最低严重级别不得低于 `BLOCKER`。

`085` 不定义 warning mode、compatibility escape hatch 或 status-side severity 推断。

## 用户故事与验收

### US-085-1 — Runtime Maintainer 需要知道第一刀插在哪里

作为 **future runtime maintainer**，我希望 first runtime cut 的读取位置与 owning surface 被单独冻结，这样我实现 `frontend_evidence_class` 时不会一开始就扩散到 mirror 或 observation gate。

**验收**：

1. Given 我阅读 `085`，When 我开始实现 first runtime cut，Then 我知道应从 `verify constraints` 进入，而不是从 `program validate` 或 frontend contract gate 进入
2. Given 我需要读取 canonical truth，When 我对照 `085`，Then 我知道当前 cut 只认 `spec.md` footer metadata

### US-085-2 — Reviewer 需要判断实现是否越界

作为 **reviewer**，我希望 first runtime cut 的 allowed `error_kind`、payload 和 non-goals 都被写死，这样我能快速判断某个实现是不是过度扩张。

**验收**：

1. Given 我阅读 `085`，When future实现开始读取 manifest mirror，Then 我知道该实现已经越出当前 cut
2. Given future实现开始输出 status full diagnostics，When 我对照 `085`，Then 我知道这不属于本轮 scope

## 功能需求

| ID | 需求 |
|----|------|
| FR-085-001 | `085` 必须冻结 future first runtime cut 的 owning surface 为 `verify constraints` |
| FR-085-002 | `085` 必须冻结 future first runtime cut 的 canonical source-of-truth 为 future work item `spec.md` footer metadata 中的 `frontend_evidence_class` |
| FR-085-003 | `085` 必须冻结 future reader/helper 的推荐落点为 `src/ai_sdlc/core/verify_constraints.py` 的治理读路径附近 |
| FR-085-004 | `085` 必须明确 future first runtime cut 不得落到 `frontend_contract_verification.py` |
| FR-085-005 | `085` 必须冻结当前 cut 只允许产出 `frontend_evidence_class_authoring_malformed` |
| FR-085-006 | `085` 必须冻结当前 cut 允许的 `error_kind` 仅为 `missing_footer_key`、`empty_value`、`invalid_value`、`duplicate_key`、`body_footer_conflict` |
| FR-085-007 | `085` 必须沿用 `084` 的 minimum payload 与 owning-surface `BLOCKER` severity boundary |
| FR-085-008 | `085` 必须明确 mirror、status、close-check 与 retroactive migration 都属于当前 cut 的 non-goals |
| FR-085-009 | `085` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 runtime truth |
| FR-085-010 | `085` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `84` 推进到 `85` |

## 成功标准

- **SC-085-001**：future runtime maintainer 能直接回答 “first runtime cut 应从哪里读、在哪里报”
- **SC-085-002**：reviewer 能直接判断某个实现是否错误侵入 manifest mirror、status 或 frontend observation gate
- **SC-085-003**：当前 baseline 保持 prospective-only，不 retroactively 改写 `068` ~ `071`
- **SC-085-004**：本轮 diff 仅新增 `085` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-08-frontend-evidence-class-verify-first-runtime-cut-design.md"
frontend_evidence_class: "framework_capability"
---
