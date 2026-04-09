# 功能规格：Frontend Evidence Class Validator Surface Baseline

**功能编号**：`083-frontend-evidence-class-validator-surface-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../082-frontend-evidence-class-authoring-surface-baseline/spec.md`](../082-frontend-evidence-class-authoring-surface-baseline/spec.md)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)、[`../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md`](../../docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md)

> 口径：`083` 在 `082` 的 authoring surface 之上，继续冻结 future runtime 应该先在哪个命令面发现并报告 `frontend_evidence_class` authoring error。它只定义 detection/reporting surface contract，不修改任何现有 CLI、parser、validator 或既有 item 状态。

## 问题定义

`082` 已经回答了“evidence class 写在哪里、写什么”，但还没有回答“未来谁先发现它写错了”：

- 如果缺失或拼错 `frontend_evidence_class`，哪个命令应成为 primary detection surface 尚未冻结
- 如果未来引入 manifest mirror，哪个命令负责检查 mirror 与 spec footer 一致性尚未冻结
- `program status`、`status --json`、`workitem close-check` 是否承担首次定责责任尚未冻结

如果这层不补上，后续 runtime 实现很容易把同一个 authoring error 分散到多个命令面上重复定义，导致：

- author 不知道应该先运行哪个命令自检
- reviewer 难以判断哪个输出才是 canonical failure
- runtime maintainer 容易把只读可见性命令扩展成第一责任检测面

因此 `083` 要冻结的是一条 prospective-only validator surface contract：未来 `frontend_evidence_class` 的 malformed authoring 必须先由一个主检测命令面发现，其他命令只承担镜像一致性、晚期复检或只读可见性职责。

## 范围

- **覆盖**：
  - 新建 `083` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `83`
  - 冻结 `frontend_evidence_class` authoring error 的 primary detection surface
  - 冻结 future manifest mirror consistency 的检测归属
  - 冻结 `program status` / `status --json` / `workitem close-check` 的非主检测职责边界
- **不覆盖**：
  - 修改 `src/` / `tests/` 或当前 `ai-sdlc` CLI
  - 给 `program-manifest.yaml` 新增 mirror 字段
  - retroactively 改写 `068` ~ `071` 或当前 runtime 输出
  - 发明新的 runtime stage 或新 CLI 子命令
  - 修改既有 `082` authoring surface contract

## 已锁定决策

- future `frontend_evidence_class` malformed authoring 的 **primary detection surface** 是 `uv run ai-sdlc verify constraints`
- future 若引入 `program-manifest.yaml` mirror，mirror 与 spec footer 的一致性检查应归属 `uv run ai-sdlc program validate`
- `uv run ai-sdlc program status` 与 `uv run ai-sdlc status --json` 只承担 bounded visibility / summary exposure，不承担 first-detection responsibility
- `uv run ai-sdlc workitem close-check` 可以在 close-stage 重新暴露 malformed authoring 作为 late blocker，但不拥有 primary detection 语义
- 若多个命令同时报告同一 malformed authoring，canonical 定责以 `verify constraints` 的检测语义为准
- `083` 只定义 future implementation target；本轮不要求任何命令已经实现该 contract

## Validator Surface Contract

### 1. Primary detection surface

future runtime 若发现以下任一问题：

- 缺失 `frontend_evidence_class`
- 空值
- 非法值
- 重复键
- footer metadata 与正文声明冲突

则首次定责应发生在：

```bash
uv run ai-sdlc verify constraints
```

约束如下：

- `verify constraints` 是 author / reviewer 的首选自检入口
- malformed `frontend_evidence_class` 必须被归类为 authoring / governance class failure，而不是 close-stage-only failure
- `verify constraints` 的 failure 语义在 future runtime 中应成为其他命令面复用的上游 truth

### 2. Mirror consistency surface

future 若 `program-manifest.yaml` 引入 `frontend_evidence_class` mirror，则：

- mirror 与 `spec.md` footer metadata 的一致性检查，应由 `uv run ai-sdlc program validate` 承担
- `program validate` 负责判断 manifest mirror 是否缺失、过期、冲突或与 spec footer 不一致
- `program validate` 不应重新定义 evidence class 的 allowed values；allowed values 仍沿用 `082`

换言之：

- `verify constraints` 管 primary authoring truth
- `program validate` 管 future derived-index / mirror consistency

### 3. Read-only visibility surfaces

future 即使 `program status` 或 `status --json` 暴露 evidence-class 相关信息，也应遵守以下边界：

- 只展示 bounded summary、derived visibility 或 blocker presence
- 不定义 malformed authoring 的 canonical failure semantics
- 不承担 first-failure responsibility
- 不要求 author 仅通过 `program status` 才能发现 evidence class 问题

### 4. Late-stage recheck surface

future `uv run ai-sdlc workitem close-check` 可以：

- 在 work item 进入 close-stage 前重新验证 `frontend_evidence_class` authoring 是否仍然合法
- 将 malformed authoring 作为 close blocker 再次暴露

但不得：

- 取代 `verify constraints` 成为首个检测面
- 把 authoring error 重新定义成“只在 close 时才成立”的晚期问题

### 5. Multi-surface precedence

future 如果多个命令都报告同一问题，应遵守以下 precedence：

1. `verify constraints`：primary authoring failure truth
2. `program validate`：future mirror consistency truth
3. `workitem close-check`：late-stage resurfacing / close blocker
4. `program status` / `status --json`：summary visibility only

## 用户故事与验收

### US-083-1 — Author 需要知道先跑哪个命令检查 evidence class

作为 **author**，我希望 malformed `frontend_evidence_class` 有一个固定的首检命令面，这样我不会在 `program status`、`close-check` 和其他命令之间猜哪个才是正式入口。

**验收**：

1. Given 我阅读 `083`，When 我想自检 evidence class authoring，Then 我知道未来应先跑 `uv run ai-sdlc verify constraints`
2. Given 未来多个命令都能显示问题，When 我对照 `083`，Then 我知道 canonical failure 语义来自 `verify constraints`

### US-083-2 — Runtime Maintainer 需要区分 primary truth 与 mirror consistency

作为 **future runtime maintainer**，我希望 evidence class 的 primary authoring truth 与 future manifest mirror consistency 是两个不同检测面，这样后续实现不会让同一个命令同时承担两种责任。

**验收**：

1. Given future manifest 引入 mirror 字段，When 我阅读 `083`，Then 我知道 mirror consistency 应落在 `program validate`
2. Given 我实现 `program validate`，When 我对照 `083`，Then 我知道它不应重新定义 `082` 的 allowed values

### US-083-3 — Reviewer 需要确保 status 只做 bounded visibility

作为 **reviewer**，我希望 `program status` / `status --json` 不被偷偷升级成 primary detection surface，这样只读可见性与正式 authoring failure 语义不会混淆。

**验收**：

1. Given 我阅读 `083`，When 我检查 future status 输出，Then 我知道它至多展示 summary / blocker presence
2. Given `workitem close-check` 复现同一问题，When 我对照 `083`，Then 我知道它只是晚期复检，不是首次定责

## 功能需求

| ID | 需求 |
|----|------|
| FR-083-001 | `083` 必须明确 `verify constraints` 是 future `frontend_evidence_class` malformed authoring 的 primary detection surface |
| FR-083-002 | `083` 必须明确 future manifest mirror consistency 归属 `program validate`，而不是 `verify constraints` 之外的 status surface |
| FR-083-003 | `083` 必须明确 `program status` 与 `status --json` 只承担 bounded visibility / summary 职责 |
| FR-083-004 | `083` 必须明确 `workitem close-check` 仅可作为 late-stage recheck / close blocker 暴露面 |
| FR-083-005 | `083` 必须明确多命令同时报告时，以 `verify constraints` 的 authoring failure 语义为 canonical truth |
| FR-083-006 | `083` 必须保持 prospective-only，不 retroactively 改写 `068` ~ `071` 或当前 runtime 输出 |
| FR-083-007 | `083` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或既有 spec authoring surface |
| FR-083-008 | `083` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `82` 推进到 `83` |

## 成功标准

- **SC-083-001**：future author 能直接从 `083` 知道 malformed `frontend_evidence_class` 应由 `verify constraints` 首先发现
- **SC-083-002**：future runtime maintainer 能区分 primary authoring detection 与 manifest mirror consistency detection
- **SC-083-003**：reviewer 不会误把 `program status` / `status --json` 当作 first-detection surface
- **SC-083-004**：本轮 diff 仅新增 `083` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/082-frontend-evidence-class-authoring-surface-baseline/spec.md"
  - "USER_GUIDE.zh-CN.md"
  - "docs/SPEC_SPLIT_AND_PROGRAM.zh-CN.md"
frontend_evidence_class: "framework_capability"
---
