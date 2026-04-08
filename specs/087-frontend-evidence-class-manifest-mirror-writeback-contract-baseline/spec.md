# 功能规格：Frontend Evidence Class Manifest Mirror Writeback Contract Baseline

**功能编号**：`087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline`  
**创建日期**：2026-04-09  
**状态**：已冻结（formal baseline）  
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md`](../086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`](../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md)

> 口径：`087` 把 `frontend_evidence_class` 的 future manifest mirror generation/writeback contract 冻结成一条 prospective-only baseline。它回答谁可以写 mirror、在什么前置条件下写、允许改 manifest 的哪一小块，以及哪些 surfaces 永远不得 opportunistic write；它不实现 runtime，不冻结具体 CLI 子命令名，不定义 status summary 或 close-stage resurfacing，也不 retroactively 改写 `068` ~ `071`。

## 问题定义

`086` 已经把 mirror placement 与 `program validate` drift semantics 定死，但“谁负责把 canonical footer truth 写回 manifest”仍然留白。若这一层继续不冻结，后续实现很容易走偏到以下方向：

- 让 `program validate` 在发现 drift 时顺手 auto-heal mirror
- 让 `program status` / `status --json` / `workitem close-check` 在读路径上 opportunistic write
- 把 mirror writeback 分散到多个 command family，导致同一规则存在两套 writer
- 在写 mirror 时顺手重排 manifest 或修改 unrelated `specs[]` fields

这类实现虽然短期可跑，但后续一旦要补 diagnostics、status surfacing 或 close-stage resurfacing，就会因为写入口分散、写范围过宽而反复重构。

因此，`087` 的职责是把 future writeback contract 压缩到最小可实现面：

- writeback 只允许来自一个显式的 program-level write surface family
- writeback 只允许把 canonical footer truth 同步到 `program-manifest.yaml` 的 `specs[] .frontend_evidence_class`
- writeback 必须与 read-only validator/status/close-check surface 严格隔离

## 范围

- **覆盖**：
  - 新建 `087` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `87`
  - 冻结 future mirror generation/writeback 的 owning family
  - 冻结 writeback 的前置条件、允许入口与允许 mutation scope
  - 冻结 refresh timing、idempotency 与 overwrite semantics
  - 冻结 forbidden write surfaces，防止 read path 偷写
- **不覆盖**：
  - 修改 `src/`、`tests/`、`program-manifest.yaml` 或任一 CLI 输出
  - 冻结具体 CLI 子命令名、flags、JSON payload 或 help text
  - 修改 `program validate` 的 drift semantics
  - 修改 `program status`、`status --json`、`workitem close-check`
  - retroactively 改写 `068` ~ `071` 或当前 runtime truth

## 已锁定决策

- future mirror writeback 的 owning command family 必须属于 `ai-sdlc program ...` 的显式写入口，而不是 repo-level validator/status/close-check surfaces
- future mirror writeback 必须以 `spec.md` footer metadata 中的 `frontend_evidence_class` 为唯一 canonical source-of-truth
- future writeback 的唯一合法 mutation target 是 `program-manifest.yaml` 中对应 `specs[]` entry 的 `frontend_evidence_class`
- future writeback 必须是 explicit-write action，不得依赖 read path opportunistic repair
- future writeback 必须先通过 `085` 已冻结的 authoring malformed precondition；若 canonical footer truth 无法合法解析，则不得写 mirror
- `087` 不冻结命令名，但冻结 owner family 与 write intent：后续不允许把真实 writer 落到 `verify constraints`、`program status`、`status --json`、`doctor` 或 `workitem close-check`

## Mirror Writeback Contract

### 1. Owning family

future mirror generation/writeback 的唯一 owning family 是 **显式 program-level write surface**。

约束：

- writer 必须位于 `ai-sdlc program ...` 命令族之下
- writer 必须体现明确 write intent，而不是 read-only validate/status/plan 的隐式副作用
- `087` 不要求现在就决定具体子命令名，但要求 future implementation 只能存在一个 canonical writer family

这样做的目的，是把 mirror mutation 留在 program orchestration 语义内，而不是把 manifest 写操作散落到 repo-level governance command。

### 2. Write preconditions

future writer 在对某个 target spec 执行 writeback 前，至少必须满足：

1. 对应 `spec.md` footer metadata 中存在唯一合法的 `frontend_evidence_class`
2. 该值通过 `082` / `085` 已冻结的 authoring contract
3. `program-manifest.yaml` 中存在唯一可归约的 canonical `specs[]` entry
4. 该次 writeback 的 target spec 已能稳定映射到 manifest entry，而不存在 entry ambiguity

若任一条件不成立，future writer 必须停止写入，而不是猜测目标、回退到 body prose、或静默跳过为“已同步”。

### 3. Allowed write modes

future writer 只允许两种模式：

- **targeted sync**：针对单个 spec entry 的显式 mirror refresh
- **bounded bulk sync**：针对一组或全部 manifest `specs[]` entries 的显式 refresh

约束：

- 两种模式必须复用同一套 canonical writer rules
- bulk sync 不得引入第二套 placement 或第二套 value mapping
- bulk sync 只是同一 writer 的扩展批量入口，不得拥有额外 write semantics

### 4. Mutation scope

future writer 对单个 target spec 的允许 mutation scope 必须严格限制为：

- 写入缺失的 `specs[] .frontend_evidence_class`
- 以 canonical footer truth 覆盖过期或冲突的 `specs[] .frontend_evidence_class`

不得：

- 重排 `specs[]`
- 修改 `id` / `path` / `depends_on` / `branch_slug` / `owner`
- 在 canonical placement 之外新增 parallel mirror surface
- 借机修复其他 manifest drift

### 5. Refresh timing

future mirror refresh 必须遵循以下 timing contract：

- spec author 完成或修正 `frontend_evidence_class` footer truth 后，mirror 可能暂时处于缺失或 stale 状态
- stale / missing mirror 应由 `program validate` 暴露 drift，而不是自动修复
- mirror 只有在显式 program-level write action 被触发时才允许刷新

因此，`087` 明确禁止：

- validate-time auto-heal
- status-read auto-heal
- close-check read path repair

### 6. Idempotency and overwrite

future writer 必须满足：

- 当 manifest mirror 已等于 canonical footer truth 时，writeback 为 no-op
- 当 manifest mirror 值合法但 stale 时，显式 writeback 应覆盖为 canonical footer truth
- 当 manifest mirror 缺失时，显式 writeback 应补齐 canonical value

同时，future writer 不得：

- 因为 mirror 已合法存在就拒绝刷新 stale value
- 因为发生冲突就静默保留旧值并报告“已同步”

### 7. Forbidden write surfaces

下列 surfaces 在 future runtime 中必须保持 read-only，不得成为 mirror writer：

- `verify constraints`
- `program validate`
- `program status`
- `program plan`
- `status --json`
- `doctor`
- `workitem close-check`

这些 surfaces 可以读取、摘要、诊断或复报，但不得 opportunistic write manifest mirror。

## 用户故事与验收

### US-087-1 — Runtime Maintainer 需要唯一 writer family

作为 **future runtime maintainer**，我希望 mirror writeback 的 owner family 先被定死，这样后续实现不会一边在 `program validate` 偷写，一边又补一个独立 sync path。

**验收**：

1. Given 我阅读 `087`，When 我开始实现 mirror writeback，Then 我知道 writer 必须归属于显式 `ai-sdlc program ...` write family
2. Given 我想在 `verify constraints` 里顺手写 manifest，When 我对照 `087`，Then 我知道这已经越界

### US-087-2 — Reviewer 需要判断写范围是否越界

作为 **reviewer**，我希望 writer 的 mutation scope 和 forbidden write surfaces 被写死，这样我能快速识别“借同步之名修改 manifest 其他字段”的实现。

**验收**：

1. Given future writer 在同步时修改了 `depends_on` 或 `owner`，When 我对照 `087`，Then 我知道该实现越界
2. Given future writer 在 status/read path 中 opportunistic write，When 我对照 `087`，Then 我知道该实现违反 writeback contract

### US-087-3 — Author 需要知道 stale mirror 何时刷新

作为 **author**，我希望 stale mirror 的刷新时机被单独说明，这样我知道 `program validate` 报 drift 不代表工具应自动修好 manifest。

**验收**：

1. Given spec footer truth 已更新但 manifest mirror 仍旧值，When 我对照 `087`，Then 我知道这属于显式 writeback 之前的允许中间态
2. Given 我运行只读 surface，When mirror 被自动刷新，Then 我知道该行为违反 `087`

## 功能需求

| ID | 需求 |
|----|------|
| FR-087-001 | `087` 必须冻结 future mirror generation/writeback 的 owning family 为显式 `ai-sdlc program ...` write surface |
| FR-087-002 | `087` 必须冻结 future writer 的 canonical source-of-truth 为对应 `spec.md` footer metadata 中的 `frontend_evidence_class` |
| FR-087-003 | `087` 必须冻结 future writer 在写入前需通过 authoring malformed precondition 且能唯一映射到 manifest `specs[]` entry |
| FR-087-004 | `087` 必须冻结 future writer 只允许 `targeted sync` 与 `bounded bulk sync` 两种模式，且二者复用同一套 writer rules |
| FR-087-005 | `087` 必须冻结 future writer 的唯一合法 mutation target 为 `program-manifest.yaml` 中对应 `specs[] .frontend_evidence_class` |
| FR-087-006 | `087` 必须冻结 stale / missing mirror 只能通过显式 write action 刷新，不得由 validate/status/close-check read path opportunistic repair |
| FR-087-007 | `087` 必须冻结 future writer 的 no-op / overwrite 行为边界：同值 no-op，stale 值显式覆盖，缺失值显式补齐 |
| FR-087-008 | `087` 必须明确 `verify constraints`、`program validate`、`program status`、`program plan`、`status --json`、`doctor`、`workitem close-check` 都是 forbidden write surfaces |
| FR-087-009 | `087` 不得冻结具体 CLI 子命令名、flags 或 runtime payload；它只冻结 owner family 与 write intent |
| FR-087-010 | `087` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 runtime truth |
| FR-087-011 | `087` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `86` 推进到 `87` |

## 成功标准

- **SC-087-001**：future runtime maintainer 能直接回答 mirror 由谁写、何时写、可写到哪
- **SC-087-002**：reviewer 能直接判断某个实现是否在 read-only surface 偷写 manifest
- **SC-087-003**：当前 baseline 保持 prospective-only，不 retroactively 改写 `068` ~ `071`
- **SC-087-004**：本轮 diff 仅新增 `087` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "specs/086-frontend-evidence-class-program-validate-mirror-contract-baseline/spec.md"
  - "docs/USER_GUIDE.zh-CN.md"
  - "docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md"
frontend_evidence_class: "framework_capability"
---
