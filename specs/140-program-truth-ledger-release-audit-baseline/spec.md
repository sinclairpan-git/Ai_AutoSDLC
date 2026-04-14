# 功能规格：Program Truth Ledger And Release Audit Baseline

**功能编号**：`140-program-truth-ledger-release-audit-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 起草中（待两轮对抗评审）
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md`](../087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md)、[`../119-capability-closure-truth-baseline/spec.md`](../119-capability-closure-truth-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)、[`../../src/ai_sdlc/models/program.py`](../../src/ai_sdlc/models/program.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/telemetry/readiness.py`](../../src/ai_sdlc/telemetry/readiness.py)、[`../../src/ai_sdlc/rules/quality-gate.md`](../../src/ai_sdlc/rules/quality-gate.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)

> 口径：`140` 解决的不是某一条功能链的局部实现，而是“全仓总目标、拆分能力、spec 索引、任务进度、发布闭环、历史兼容”长期缺少单一程序级聚合入口的问题。`140` 允许继续复用根级 `program-manifest.yaml` 作为唯一 program-level 聚合入口，但不推翻既有 field-level canonical truth contract；像 `frontend_evidence_class` 这类已冻结 ownership 的字段，canonical source 仍在各自 spec/footer，manifest/snapshot 只能聚合、镜像与审计，不得 override。`140` 冻结的是 program-level ledger schema、最小 machine-computed snapshot、release audit hard gate 与 migration contract。

## 问题定义

当前仓库已经证明：仅靠现有 `close`、`development-summary.md`、`tasks.md` 全勾选、局部 close wording，并不能回答“是否真的能发版”。

当前缺口至少包括：

- `program-manifest.yaml` 还不是全仓总索引；当前 `specs/` 目录数量大于 manifest `specs[]` entry 数量，导致 agent 与 operator 仍需人工盘点
- `119` 引入了 `capability_closure_audit`，但它明确不是 hard blocker，因此“看得到 open cluster”并不等于“发布会被阻断”
- `program validate` 当前只校验 `id/path/depends_on/cycle` 与局部 mirror drift，不校验 release closure、snapshot freshness、evidence completeness
- `status` / readiness 对 capability closure 仍有 fail-open 路径，真值读取失败时可能直接消失，而不是显式暴露 `invalid/stale`
- 现有 CLOSE 规则只对 formal docs、测试、构建、tasks 与 commit 负责，不对“release-required capability 是否闭环”负责
- 老版本升级后，manifest / docs / status / backlog / code/test surfaces 没有单一机器账本，容易反复出现 split-truth drift

用户和 agent 因而会持续遇到同一种问题：要回答“总目标是什么、拆了多少、做到哪里、还有哪些 blocker、能不能发布”，仍需要重新通读 `specs/`、`src/`、测试、`development-summary.md` 与 backlog。

`140` 的职责是把这件事一次性冻结为 program-level contract：

- 用一个入口回答 program goal / release targets / capabilities / specs / progress / blockers
- 明确哪些信息由人工维护，哪些信息只能由机器生成
- 让 release audit 成为 hard gate，杜绝“流程 close 了但发布不可信”
- 对老仓库升级提供可验证的 migration/staleness contract，避免以后再做全仓人工盘点

## 范围

- **覆盖**：
  - 升级根级 `program-manifest.yaml` 为 program-level truth ledger 的唯一聚合入口
  - 冻结 ledger 的两层结构：`authoring intent` 与 `machine-computed truth snapshot`
  - 冻结全仓 spec 索引完整性要求：每个 `specs/*` 目录都必须有且只有一个 manifest entry
  - 冻结 capability / spec role / required evidence 的声明 contract
  - 冻结 `program truth sync`、`program truth audit` 与 `program status` 消费 ledger/snapshot 的职责边界
  - 冻结 release audit hard gate：release-required capability 不闭环时必须 fail-closed
  - 冻结 snapshot freshness / source hash / stale detection contract
  - 冻结 derived dashboard / summary 只能是派生视图，不得成为第二真值
  - 冻结旧版本升级与 legacy spec 迁移边界
- **不覆盖**：
  - 不在本 spec 内补完 `098/099/100` 等尚未实现的 runtime 缺口
  - 不改写 `082/087` 已冻结的 field-level source-of-truth ownership
  - 不新增第二份 program manifest、第二套账本或平行 dashboard truth
  - 不让 read-only status / validate / close-check surfaces 偷写 snapshot
  - 不承诺靠文档层改动掩盖真实 runtime blocker

## 已锁定决策

- `program-manifest.yaml` 是 **唯一 program-level 聚合入口**，但不是所有 field-level truth 的唯一 origin；既有 field-level canonical owner 继续生效
- 当聚合入口与既有 field-level canonical source 冲突时，必须以前者对应的 canonical owner 为准；manifest/snapshot 只能暴露冲突，不能覆盖冲突
- ledger 必须拆成两层：
  - `authoring intent`：人工维护的 program goal / release targets / capabilities / spec index / role / required evidence
  - `truth_snapshot`：只能由显式 program-level write surface 生成的机器快照
- `truth_snapshot` 只能由显式 `program truth sync` 一类写入口落盘；`program validate`、`program status`、`status --json`、`workitem truth-check`、`workitem close-check` 等 read surfaces 必须保持只读
- 每个 `specs/*` 目录都必须有且只有一个 manifest entry；缺失、重复、孤儿 entry 都属于 ledger blocker
- 在 migration mode 下，非 release-scope 的缺失/未分类 spec entry 必须先以 `migration_pending` surfaced；release-scope 内的缺失/未分类仍为 hard blocker
- 每个 spec 都必须有 program-level role；至少支持：
  - `formal_contract`
  - `runtime_carrier`
  - `sync_carrier`
  - `release_doc`
  - `legacy_unclassified`
- 每个 release-required capability 都必须声明 required evidence，至少覆盖：
  - `truth_check_refs`
  - `close_check_refs`
  - `verify_refs`
- `command_surface_ref` 与 `artifact_probe_ref` 只允许在仓库内已经存在稳定 machine-readable surface 时作为可选扩展；`140` 的 v1 不得引入新的手工 registry 作为 release blocker
- capability 的 `closure_state` 必须与既有 closure truth 保持单一映射；发布是否允许则由独立的 `audit_state` 表达，不能混成第二套 closure 状态体系
- derived Markdown dashboard / development summary / rollout plan 只能引用 ledger/snapshot，不得成为平行真值
- 旧仓库升级允许存在 migration 过程，但 release scope 内若仍有 `legacy_unclassified`、`migration_pending`、`stale`、`invalid` 或 evidence 缺失，release audit 必须失败

## Ledger Contract

### 1. Single aggregated entrypoint, layered truth

根级 `program-manifest.yaml` 必须升级为 program-level ledger，并至少包含：

- `program`
- `release_targets`
- `capabilities[]`
- `specs[]`
- `truth_snapshot`

其中：

- `program` / `release_targets` / `capabilities[]` / `specs[]` 属于人工维护的 authoring intent
- `truth_snapshot` 属于机器生成区，禁止手写与 opportunistic write
- 对于已在其他 contract 中冻结了 canonical owner 的字段，ledger 只能引用或镜像，不能重新夺权
- 若 `specs[]` mirror 与 field-level canonical truth 冲突，`truth_snapshot` 必须把该冲突暴露为 blocker，并以 canonical owner 的值继续计算
- 任一 canonical conflict 一旦存在，release audit 必须强制把对应 capability 的 `audit_state` 置为 `blocked`

### 2. Program intent layer

`program` 必须至少回答：

- 总目标是什么
- 当前声明的 release targets 是什么
- 每个 capability 的目标、范围、依赖 spec 集、是否属于 release-required

`capabilities[]` 至少包含：

- `id`
- `title`
- `goal`
- `release_required`
- `spec_refs`
- `required_evidence`

其中 `required_evidence` 必须引用现有可验证 surface，而不是手工清单。至少允许：

- `truth_check_ref`
- `close_check_ref`
- `verify_ref`

在 `140` 的 v1 中：

- `truth_check_ref`、`close_check_ref`、`verify_ref` 是唯一允许作为 mandatory gate input 的 evidence refs
- `command_surface_ref`、`artifact_probe_ref` 仅在仓库内已经有稳定 machine-readable source 时作为 optional extension 使用
- 不允许为满足 `140` 而新建手工维护的 command/probe registry

### 3. Spec index layer

`specs[]` 必须是全仓完整索引，而不是局部 program 子集。

这里的 “spec 目录” 指至少包含 `spec.md` 的 `specs/*` 子目录；不含 `spec.md` 的辅助目录不进入 spec index 审计。

每个 spec entry 至少包含：

- `id`
- `path`
- `depends_on`
- `owner`
- `branch_slug`
- `roles`
- `capability_refs`

并遵守：

- 一个 spec 目录只能对应一个 manifest entry
- manifest entry 不能指向不存在目录
- spec entry 若声称属于某 capability，则 capability `spec_refs` 与 spec `capability_refs` 必须双向一致

### 4. Truth snapshot layer

`truth_snapshot` 必须由显式 program-level sync 生成，并至少记录：

- `generated_at`
- `generated_by`
- `generator_version`
- `repo_revision`
- `authoring_hash`
- `source_hashes`
- `snapshot_hash`
- `computed_capabilities`
- `state`

其中 `computed_capabilities` 至少应暴露：

- `closure_state`
- `audit_state`
- `blocking_refs`
- `stale_reason`

其中：

- `closure_state` 必须直接从 `program-manifest.yaml` 中 authoritative `capability_closure_audit` 机械镜像；若某 capability 不在 open clusters 中，则视为 `closed`
- `audit_state` 只负责回答 `ready / blocked / stale / invalid / migration_pending`
- task progress、close readiness、逐项 evidence 细节保持为 read-time derived surface，不持久化进 snapshot

### 5. Freshness and staleness

`truth_snapshot` 不得被长期信任为静态文本。

至少以下情况必须把 snapshot 视为 `stale` 或 `invalid`：

- `program-manifest.yaml` 的 authoring intent 发生变化
- 任一被引用 spec、truth-check/close-check/verify 依赖面、命令面或 artifact probe 集合发生变化
- snapshot 缺少 source hash / repo revision / generator version

### 6. Read vs write boundary

下列 surfaces 必须保持 read-only，不得写 `truth_snapshot`：

- `program validate`
- `program status`
- `status --json`
- `workitem truth-check`
- `workitem close-check`
- readiness telemetry

唯一允许写 snapshot 的，必须是显式 program-level write surface。

### 7. Release audit hard gate

系统必须引入 program-level release audit。

release audit 必须以两层信息共同判断：

- `closure_state`：沿用既有 capability closure truth 的 authoritative 映射
- `audit_state`：由 release audit 计算出的发布可行性状态

其中：

- `closure_state` 继续回答能力闭环处于 `formal_only / partial / capability_open / closed` 的哪一类
- `audit_state` 只回答 `ready / blocked / stale / invalid / migration_pending`
- `audit_state` 是 release 决策的唯一裁决状态；`closure_state` 只负责解释为什么 `audit_state` 被判定为 `ready` 或 `blocked`，不得反向 override release audit 结果

当 release-required capability 出现以下任一情况时，release audit 必须 fail-closed：

- `audit_state != ready`
- 存在 unresolved canonical conflict
- 缺失 required evidence
- 缺失 spec index / role / capability mapping
- authoritative `closure_state` 仍指向 open 状态，且未被 machine-verifiable evidence 消解

这条 gate 的目标不是“让状态更好看”，而是阻断假绿发布。

### 8. Derived human views

允许生成人读视图，如 dashboard、rollout summary、development summary 补充段落，但它们必须：

- 显式声明自己是 derived view
- 引用 snapshot 的 `generated_at` / `repo_revision`
- 不得比 ledger/snapshot 拥有更多 authority

## 用户故事与验收

### US-140-1 — Operator 需要一个入口看到总目标、拆分目标与当前进展

作为 **operator**，我希望只读一个 program-level ledger，就知道总目标、release targets、capabilities、spec 覆盖、任务进度和 blocker，而不是每次都重新盘点全仓。

**验收**：

1. Given 我打开 `program-manifest.yaml`，When 查看 program/capabilities/specs/truth snapshot，Then 我能知道总目标、拆分目标、当前 blocker 与 release 口径
2. Given 某个 spec 还没纳入 manifest，When 运行 truth audit，Then 它必须被报告为 blocker，而不是静默遗漏

### US-140-2 — Maintainer 需要发布闭环由机器阻断，而不是靠 close wording

作为 **maintainer**，我希望 release-required capability 的 closure state 与 required evidence 都由机器校验，这样 formal docs close 不能再冒充实现闭环。

**验收**：

1. Given 某个 release-required capability 的 `audit_state` 不是 `ready`，When 运行 release audit，Then 命令失败
2. Given tasks 全部勾选、summary 已生成，但 required evidence 缺失，When 运行 release audit，Then 命令仍失败
3. Given ledger mirror 与 field-level canonical truth 冲突，When 运行 release audit，Then 对应 capability 必须被阻断

### US-140-3 — Agent 需要机器可读的 spec-to-capability-to-evidence 图谱

作为 **agent**，我希望直接读取 capability、spec role、required evidence 与 computed snapshot，而不是从自然语言 summary 猜当前状态。

**验收**：

1. Given agent 读取 ledger，When 需要判断某 capability 为什么不能发布，Then 它能直接看到 blockers 与 missing evidence
2. Given snapshot 过期，When agent 读取 status surface，Then 会看到 `stale/invalid`，而不是空白或假绿

### US-140-4 — 旧版本升级用户需要兼容迁移而不是重新全仓盘点

作为 **升级用户**，我希望旧仓库升级到新 ledger 后，系统能直接指出哪些 spec 缺 entry、哪些 role 未分类、哪些 snapshot 过期，而不是让我人工从零盘点。

**验收**：

1. Given 老仓库的 manifest 仍是旧 schema，When 运行 truth audit，Then 我能看到缺失映射与迁移 blocker 清单
2. Given release scope 内仍有 `legacy_unclassified` 或 `migration_pending`，When 运行 release audit，Then 发布必须被阻断
3. Given 非 release-scope 的历史 spec 暂未补齐映射，When 运行 truth audit，Then 它们必须被 surfaced 为 migration gap，而不是静默忽略

## 功能需求

| ID | 需求 |
|----|------|
| FR-140-001 | 系统必须把根级 `program-manifest.yaml` 升级为 program-level truth ledger 的唯一聚合入口 |
| FR-140-002 | ledger 必须同时承载人工维护的 `authoring intent` 与机器生成的 `truth_snapshot`，且二者职责分离 |
| FR-140-003 | 系统必须检测每个包含 `spec.md` 的 `specs/*` 目录；在 migration mode 下，非 release-scope 缺失 entry 以 `migration_pending` surfaced，release-scope 缺失 entry 必须 hard fail |
| FR-140-004 | 每个 spec entry 必须声明 role 与 capability refs，并与 capability 侧引用保持一致 |
| FR-140-005 | 每个 release-required capability 必须声明 required evidence，且 `140` v1 的 mandatory gate inputs 只允许绑定到现有 machine-verifiable surfaces（truth-check、close-check、verify）；command/probe refs 仅为 optional extension |
| FR-140-006 | `truth_snapshot` 必须记录 `generated_at`、`generated_by`、`generator_version`、`repo_revision`、`authoring_hash`、`source_hashes` 与 `snapshot_hash` |
| FR-140-007 | `truth_snapshot` 只允许持久化最小聚合结果；task progress、close readiness 与逐项 evidence 明细必须保持 read-time derived，而不是写入 snapshot |
| FR-140-008 | read-only surfaces 不得写入 `truth_snapshot`；snapshot 只能由显式 program-level write surface 更新 |
| FR-140-009 | 系统必须提供 `program truth sync`、`program truth audit`，并让既有 `program status` 消费 ledger/snapshot |
| FR-140-010 | release audit 必须基于 authoritative `closure_state` 与独立 `audit_state` fail-closed；其中 `audit_state` 是唯一 release 裁决状态，且任何 canonical conflict 都必须强制 `audit_state=blocked` |
| FR-140-011 | status/readiness surfaces 在 ledger 或 snapshot 读取失败时，必须显式暴露 `invalid/stale`，不得 fail-open 或静默隐藏 |
| FR-140-012 | derived dashboard / summary / rollout 文档只能引用 ledger/snapshot，不得成为第二真值 |
| FR-140-013 | 旧 schema / 老仓库升级必须有明确 migration contract；缺 entry、缺 role、缺 hashes、缺 evidence mapping 都必须被显式报告，并给出最小补齐路径 |
| FR-140-014 | task progress 必须来源于 `tasks.md`、`workitem truth-check`、`workitem close-check` 等机器可读 surface，而不是手工重复维护 |

## 成功标准

- **SC-140-001**：operator 能从单一 program-level 入口看到总目标、release targets、capabilities、spec 覆盖、任务进度与 blocker
- **SC-140-002**：truth audit 能稳定暴露 manifest 缺失 spec entry、role 映射、capability 映射或 evidence mapping；release-scope 缺口必须 hard fail，非 release-scope 缺口必须 surfaced 为 migration gap
- **SC-140-003**：release-required capability 未闭环时，release audit 不能再被 close wording、summary 或 tasks 勾选绕过
- **SC-140-004**：status/readiness 在 snapshot 失效或读取异常时暴露 `stale/invalid`，不再 fail-open
- **SC-140-005**：derived dashboard 与 summary 变成 ledger/snapshot 的只读派生，而不是第二真值

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/087-frontend-evidence-class-manifest-mirror-writeback-contract-baseline/spec.md"
  - "specs/119-capability-closure-truth-baseline/spec.md"
  - "program-manifest.yaml"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/workitem_cmd.py"
  - "src/ai_sdlc/core/close_check.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/rules/quality-gate.md"
  - "docs/framework-defect-backlog.zh-CN.md"
frontend_evidence_class: "framework_capability"
---
