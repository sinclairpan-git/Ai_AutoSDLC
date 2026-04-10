# 功能规格：Frontend Evidence Class Diagnostic Contract Baseline

**功能编号**：`084-frontend-evidence-class-diagnostic-contract-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../083-frontend-evidence-class-validator-surface-baseline/spec.md`](../083-frontend-evidence-class-validator-surface-baseline/spec.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)

> 口径：`084` 在 `083` 的 validator surface contract 之上，继续冻结 future diagnostics/reporting 至少要说清哪些 bounded truth。它只规定问题族群、严重级别边界与最小诊断字段，不规定具体数据结构、测试名或 CLI 渲染格式。

## 问题定义

`083` 已经回答了“哪个命令先发现问题”，但还没有回答“发现之后最低要怎样表达问题”：

- future `verify constraints` 如果发现 malformed `frontend_evidence_class`，应如何命名该问题族群尚未冻结
- future `program validate` 如果发现 manifest mirror drift，是否和 authoring malformed 混成同一种诊断尚未冻结
- `status --json` 若只做 bounded visibility，最少能暴露哪些安全摘要尚未冻结

如果这一层继续留白，后续 runtime 改造很容易出现：

- 同一类问题在不同命令里使用不同措辞
- mirror drift 被误报成 authoring malformed，或者反过来
- `status --json` 暴露过多非 canonical 细节，越过 `083` 的边界

因此 `084` 要冻结的是一条 prospective-only diagnostics contract：future evidence-class validation 至少要区分 authoring malformed 与 mirror consistency drift 两个问题族群，并为每一类规定最小诊断字段和严重级别边界。

## 范围

- **覆盖**：
  - 新建 `084` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `84`
  - 冻结 future evidence-class diagnostics 的问题族群
  - 冻结 owning surface 对应的最低严重级别边界
  - 冻结 bounded summary surface 可暴露的最小字段集合
- **不覆盖**：
  - 修改 `src/` / `tests/` 或当前 CLI 输出
  - 设计 JSON schema、dataclass 字段名或 telemetry 表结构
  - 修改 `083` 已冻结的 detection surface 归属
  - retroactively 改写 `068` ~ `071`
  - 给 `program-manifest.yaml` 新增 mirror 字段

## 已锁定决策

- future diagnostics 必须至少区分两类问题族群：
  - `frontend_evidence_class_authoring_malformed`
  - `frontend_evidence_class_mirror_drift`
- `frontend_evidence_class_authoring_malformed` 的 owning surface 是 `verify constraints`
- `frontend_evidence_class_mirror_drift` 的 owning surface 是 `program validate`
- 在 owning surface 上，这两类问题的最低严重级别都不得低于 `BLOCKER`
- `program status` / `status --json` 只能暴露 bounded summary，不得输出足以取代 owning surface 的 full diagnostic narrative
- `workitem close-check` 若复现同一问题，可沿用问题族群，但其语义来源仍以上游 owning surface 为准

## Diagnostic Contract

### 1. Problem families

future evidence-class validation 至少要区分：

#### A. `frontend_evidence_class_authoring_malformed`

适用于：

- footer 缺失 `frontend_evidence_class`
- 空值
- 非法值
- 重复键
- footer metadata 与正文声明冲突

#### B. `frontend_evidence_class_mirror_drift`

仅适用于 future manifest mirror 已存在时：

- manifest mirror 缺失
- manifest mirror 过期
- manifest mirror 与 spec footer 不一致
- manifest mirror 存在非法派生值或冲突值

### 2. Severity boundary

- 在 `verify constraints` 上，`frontend_evidence_class_authoring_malformed` 必须至少表现为 `BLOCKER`
- 在 `program validate` 上，`frontend_evidence_class_mirror_drift` 必须至少表现为 `BLOCKER`
- `status --json` / `program status` 不承担 severity adjudication，只可暴露 derived summary
- `workitem close-check` 若重报同一问题，可将其作为 close blocker，但不改变问题原始 owning surface 与严重级别归属

### 3. Minimum diagnostic payload

future owning surface 在报告 evidence-class 问题时，最少必须能给出以下 bounded truth：

- `problem_family`
- `detection_surface`
- `spec_path`
- `error_kind`
- `source_of_truth_path`
- `expected_contract_ref`
- `human_remediation_hint`

其中：

- `problem_family` 只能来自本 baseline 已冻结的问题族群
- `detection_surface` 必须与 `083` 保持一致
- `spec_path` 应指向具体 work item spec 目录或其 `spec.md`
- `error_kind` 应来自 bounded 枚举，不得自由文本泛化
- `source_of_truth_path` 对 authoring malformed 应指向 `spec.md` footer；对 mirror drift 应同时指出 spec footer 与 mirror 所在文件
- `expected_contract_ref` 应至少能回指 `082` 或 `083`
- `human_remediation_hint` 只给最小修复提示，不替代 full design guidance

### 4. Allowed error kinds

对 `frontend_evidence_class_authoring_malformed`，future runtime 至少应支持以下 `error_kind`：

- `missing_footer_key`
- `empty_value`
- `invalid_value`
- `duplicate_key`
- `body_footer_conflict`

对 `frontend_evidence_class_mirror_drift`，future runtime 至少应支持以下 `error_kind`：

- `mirror_missing`
- `mirror_stale`
- `mirror_value_conflict`
- `mirror_invalid_value`

### 5. Bounded status exposure

future `program status` / `status --json` 即使展示 evidence-class 相关摘要，也只能暴露以下级别的信息：

- 是否存在 evidence-class blocker
- blocker 属于 authoring malformed 还是 mirror drift
- 关联的 spec 标识

不得在 status surface 直接展开：

- 完整 remediation narrative
- 多条自由文本堆栈
- 足以替代 owning surface 的 full diagnostic payload

## 用户故事与验收

### US-084-1 — Runtime Maintainer 需要稳定的问题族群

作为 **future runtime maintainer**，我希望 evidence-class 相关问题至少有两个稳定的问题族群，这样我实现 `verify constraints` 和 `program validate` 时不会再自由发挥命名或混淆问题边界。

**验收**：

1. Given 我阅读 `084`，When 我实现 authoring malformed 检查，Then 我知道应归类为 `frontend_evidence_class_authoring_malformed`
2. Given future manifest mirror 存在，When 我实现 mirror drift 检查，Then 我知道不能把它继续混写成 authoring malformed

### US-084-2 — Reviewer 需要知道哪些字段是最小真值

作为 **reviewer**，我希望 future diagnostics 至少总能给出同一组 bounded 字段，这样我在不同命令面看到的问题可以稳定对账。

**验收**：

1. Given 我阅读 `084`，When future diagnostics 出现 evidence-class 错误，Then 我知道至少应能看到 `problem_family`、`detection_surface`、`spec_path` 与 `error_kind`
2. Given future owning surface 只输出泛化文本，When 我对照 `084`，Then 我知道它仍不满足最小 diagnostics contract

### US-084-3 — Status Surface 需要保持克制

作为 **author**，我希望 `status --json` 与 `program status` 只提供 bounded summary，而不是替代真正的诊断命令，这样命令边界不会再次漂移。

**验收**：

1. Given 我阅读 `084`，When 我看 future status surface，Then 我知道它最多只说“哪类 blocker 存在、关联哪个 spec”
2. Given 我需要完整 remediation 提示，When 我对照 `084`，Then 我知道应回到 owning surface 查看

## 功能需求

| ID | 需求 |
|----|------|
| FR-084-001 | `084` 必须冻结 `frontend_evidence_class_authoring_malformed` 与 `frontend_evidence_class_mirror_drift` 两个 future 问题族群 |
| FR-084-002 | `084` 必须明确两类问题在 owning surface 上的最低严重级别为 `BLOCKER` |
| FR-084-003 | `084` 必须冻结 owning surface 的最小 diagnostics payload 字段集合 |
| FR-084-004 | `084` 必须冻结两类问题各自允许的 bounded `error_kind` |
| FR-084-005 | `084` 必须明确 `program status` / `status --json` 只能暴露 bounded summary，不得替代 full diagnostic payload |
| FR-084-006 | `084` 必须保持 prospective-only，不 retroactively 改写当前 runtime truth 或既有 spec |
| FR-084-007 | `084` 不得修改 `src/`、`tests/`、`program-manifest.yaml` 或 `083` 已冻结的 detection surface 归属 |
| FR-084-008 | `084` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `83` 推进到 `84` |

## 成功标准

- **SC-084-001**：future runtime maintainer 能直接区分 authoring malformed 与 mirror drift 两类问题族群
- **SC-084-002**：reviewer 能直接判断 future diagnostics 是否包含最低 bounded truth 字段
- **SC-084-003**：status surface 的信息边界不会再次侵入 owning surface
- **SC-084-004**：本轮 diff 仅新增 `084` formal docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/083-frontend-evidence-class-validator-surface-baseline/spec.md"
  - "docs/framework-defect-backlog.zh-CN.md"
  - "USER_GUIDE.zh-CN.md"
frontend_evidence_class: "framework_capability"
---
