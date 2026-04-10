# 功能规格：Frontend Evidence Class Program Validate Mirror Contract Baseline

**功能编号**：`086-frontend-evidence-class-program-validate-mirror-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md`](../084-frontend-evidence-class-diagnostic-contract-baseline/spec.md)、[`../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md`](../085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md)、[`../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`](../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)

> 口径：`086` 把 `frontend_evidence_class` 的 future manifest mirror follow-up 冻结成一条 prospective-only baseline。它回答 future `program validate` 应在哪个 manifest 槽位读取 mirror、mirror 允许长什么样、何时构成 `frontend_evidence_class_mirror_drift`；它不实现 runtime，不定义自动写回，不修改 `program status` / `close-check`，也不 retroactively 改写 `068` ~ `071`。

## 问题定义

`085` 已把 first runtime cut 收敛到 `verify constraints`，但 mirror 半边仍缺一个足够窄且可实现的 contract：

- future manifest mirror 应挂在 `program-manifest.yaml` 的哪个 canonical 槽位尚未冻结
- mirror 是否复用 `frontend_evidence_class` 原值，还是再造一层 manifest-side alias 尚未冻结
- `program validate` 应如何区分 `mirror_missing`、`mirror_invalid_value`、`mirror_stale` 与 `mirror_value_conflict` 尚未冻结

如果这一层继续留白，后续实现大概率会出现两类重构：

- 先随手把 mirror 放到 manifest 顶层或并行索引里，后面再搬回 `specs[]`
- 先用一套临时 drift 语义上代码，后面再为 placement 迁移或 alias 清理重写判定逻辑

因此，`086` 的职责是把 future `program validate` 的 mirror contract 一次冻结到“刚好足够实现”的程度：既定下 canonical manifest placement，也定下最小 drift 语义，但不把生成/回写链路一并压进当前轮次。

## 范围

- **覆盖**：
  - 新建 `086` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `86`
  - 冻结 future manifest mirror 的 canonical placement
  - 冻结 mirror value shape 与 source-of-truth precedence
  - 冻结 `program validate` 的 mirror drift semantics 与 `error_kind` 解释边界
  - 冻结本轮 non-goals，防止 generation/writeback/status 抢跑
- **不覆盖**：
  - 修改 `src/`、`tests/` 或当前 CLI 输出
  - 真正给 `program-manifest.yaml` 新增 mirror 字段
  - 定义 mirror 自动生成、回写责任人或同步时机
  - 修改 `program status`、`status --json`、`workitem close-check`
  - retroactively 改写 `068` ~ `071` 或当前 runtime truth

## 已锁定决策

- future manifest mirror 的唯一宿主是 `program-manifest.yaml` 中每个 `specs[]` 节点
- future canonical mirror 键名直接复用 `frontend_evidence_class`
- future mirror value 直接复用 `082` 已冻结的枚举：
  - `framework_capability`
  - `consumer_adoption`
- canonical correctness source 仍然只认对应 work item `spec.md` footer metadata；manifest mirror 只是 derived mirror，不是 source-of-truth
- future `program validate` 是 `frontend_evidence_class_mirror_drift` 的 owning surface
- `086` 不允许再引入第二个 manifest-side alias、顶层镜像索引或 parallel mirror surface

## Manifest Mirror Contract

### 1. Canonical placement

future 若 manifest mirror 存在，其唯一合法 placement 为：

```yaml
specs:
  - id: "086-example"
    path: "specs/086-example"
    depends_on: []
    branch_slug: "086-example"
    owner: "codex"
    frontend_evidence_class: "framework_capability"
```

约束如下：

- `frontend_evidence_class` 必须直接挂在单个 `specs[]` entry 上
- 不得新建顶层 `frontend_evidence_class_map`
- 不得把 mirror 写入 `status` artifact、memory artifact 或其他旁路 YAML 作为 canonical manifest mirror
- future model 扩展应优先落在 [program.py](/Users/sinclairpan/project/Ai_AutoSDLC/src/ai_sdlc/models/program.py) 的 `ProgramSpecRef`，而不是另造并行 manifest data class

### 2. Value shape

future manifest mirror 的值形态必须与 `spec.md` footer metadata 完全同构：

- `framework_capability`
- `consumer_adoption`

不得：

- 重命名为 manifest-only alias
- 使用布尔值、缩写或数值编码
- 允许 mirror-only 第三值

### 3. Source-of-truth precedence

future runtime 若同时看到：

- work item `spec.md` footer metadata 的 `frontend_evidence_class`
- `program-manifest.yaml` 中对应 `specs[]` entry 的 mirror

则 precedence 必须固定为：

1. `spec.md` footer metadata：canonical source-of-truth
2. `program-manifest.yaml` mirror：derived mirror for `program validate`

因此：

- `program validate` 只负责判断 mirror 是否与 canonical footer 保持一致
- `program validate` 不得把 mirror 自身提升为 authoring truth
- `086` 不改写 `085` 已冻结的 `verify constraints` 首刀语义

## Mirror Drift Contract

### 1. Problem family

future `program validate` 在 manifest mirror 路径上只允许产出：

- `frontend_evidence_class_mirror_drift`

### 2. Allowed error kinds

future `program validate` 只允许使用以下 bounded `error_kind`：

- `mirror_missing`
- `mirror_invalid_value`
- `mirror_stale`
- `mirror_value_conflict`

### 3. Error-kind semantics

#### A. `mirror_missing`

适用于：

- 对应 spec 的 `spec.md` footer 已声明 `frontend_evidence_class`
- 对应 `program-manifest.yaml` 的 canonical `specs[]` entry 缺失 `frontend_evidence_class`

#### B. `mirror_invalid_value`

适用于：

- canonical mirror key 已存在
- 但值为空、非法，或不在 `082` 已冻结的允许枚举中

#### C. `mirror_stale`

适用于：

- canonical mirror key 已存在
- 值本身属于允许枚举
- 但其值与当前 `spec.md` footer 的 canonical truth 不一致

这类问题表示 mirror 落后于 source-of-truth，而不是 source-of-truth 本身写错。

#### D. `mirror_value_conflict`

适用于：

- manifest 中出现多个并行 mirror claim，导致同一 spec 无法归约到唯一 manifest-side mirror truth
- 或出现 canonical placement 之外的 manifest-side alias / parallel mirror surface，与 `specs[] .frontend_evidence_class` 形成竞争解释

这类问题用于拦截 future schema 漂移，而不是替代 `mirror_stale`。

### 4. Severity boundary

future `program validate` 一旦命中上述任一 drift 条件，最低严重级别不得低于 `BLOCKER`。

### 5. Minimum payload inheritance

future `program validate` 在 mirror drift 路径上应沿用 `084` 的最小 payload 边界，至少包含：

- `problem_family`
- `detection_surface`
- `spec_path`
- `error_kind`
- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint`

其中 `source_of_truth_path` 至少应同时指出：

- 对应 work item `spec.md`
- 对应 `program-manifest.yaml`

## Non-Goals

`086` 明确不冻结以下内容：

- 谁负责写入 manifest mirror
- mirror 何时自动生成或刷新
- 是否存在批量 writeback 命令
- `program status` / `status --json` 如何展示 mirror drift 摘要
- `workitem close-check` 是否二次复报 mirror drift

这些内容都留给后续 baseline；`086` 只先把 placement 与 drift semantics 定死。

## 用户故事与验收

### US-086-1 — Runtime Maintainer 需要稳定的 manifest placement

作为 **future runtime maintainer**，我希望 mirror 的唯一宿主与键名先被定死，这样我后续给 `ProgramSpecRef` 扩字段和写 `program validate` 时不用先做一版临时 schema 再搬家。

**验收**：

1. Given 我阅读 `086`，When 我开始扩 manifest model，Then 我知道 mirror 应放在 `specs[] .frontend_evidence_class`
2. Given 我想新增顶层 mirror map，When 我对照 `086`，Then 我知道这已经越界

### US-086-2 — Reviewer 需要区分 mirror mismatch 与 schema drift

作为 **reviewer**，我希望 `mirror_stale` 与 `mirror_value_conflict` 的边界被单独写清，这样后续实现不会把“值没同步”与“schema 出现第二套真值”混成同一类错误。

**验收**：

1. Given manifest mirror 值合法但落后于 spec footer，When 我对照 `086`，Then 我知道它应被归类为 `mirror_stale`
2. Given manifest 出现并行 alias 或多处 mirror claim，When 我对照 `086`，Then 我知道它应被归类为 `mirror_value_conflict`

### US-086-3 — Author 需要知道 `program validate` 管哪一类问题

作为 **author**，我希望 `program validate` 的 mirror 职责只管 derived consistency，而不是重新定义 authoring truth，这样我能区分什么时候先修 `spec.md`，什么时候只需修 manifest mirror。

**验收**：

1. Given 我阅读 `086`，When `program validate` 报 mirror drift，Then 我知道 canonical source 仍在 `spec.md` footer
2. Given 我看到 mirror drift，When 我对照 `086`，Then 我知道它不代表 `085` 的首刀语义被改写

## 功能需求

| ID | 需求 |
|----|------|
| FR-086-001 | `086` 必须冻结 future manifest mirror 的唯一宿主为 `program-manifest.yaml` 的 `specs[]` 节点 |
| FR-086-002 | `086` 必须冻结 future canonical mirror 键名为 `frontend_evidence_class` |
| FR-086-003 | `086` 必须冻结 future mirror value 直接复用 `framework_capability` / `consumer_adoption`，不得引入 manifest-only alias |
| FR-086-004 | `086` 必须明确 canonical correctness source 仍是对应 work item `spec.md` footer metadata |
| FR-086-005 | `086` 必须冻结 future `program validate` 为 `frontend_evidence_class_mirror_drift` 的 owning surface |
| FR-086-006 | `086` 必须冻结 `mirror_missing`、`mirror_invalid_value`、`mirror_stale`、`mirror_value_conflict` 的 bounded 语义 |
| FR-086-007 | `086` 必须明确 `mirror_value_conflict` 用于拦截并行 alias / parallel mirror surface，而不是替代 `mirror_stale` |
| FR-086-008 | `086` 必须沿用 `084` 的 minimum payload 与 owning-surface `BLOCKER` severity boundary |
| FR-086-009 | `086` 必须明确 generation/writeback/status/close-check 都不属于本轮 |
| FR-086-010 | `086` 必须保持 prospective-only，不 retroactively 改写 `068` ~ `071` 或当前 runtime truth |
| FR-086-011 | `086` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 CLI 输出 |
| FR-086-012 | `086` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `85` 推进到 `86` |

## 成功标准

- **SC-086-001**：future runtime maintainer 能直接扩 `ProgramSpecRef` 而不用先设计第二套 mirror schema
- **SC-086-002**：reviewer 能稳定区分 `mirror_stale` 与 `mirror_value_conflict`
- **SC-086-003**：author 能明确区分 canonical authoring truth 与 manifest mirror consistency
- **SC-086-004**：本轮 diff 仅新增 `086` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "specs/084-frontend-evidence-class-diagnostic-contract-baseline/spec.md"
  - "specs/085-frontend-evidence-class-verify-first-runtime-cut-baseline/spec.md"
  - "docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md"
  - "program-manifest.yaml"
frontend_evidence_class: "framework_capability"
---
