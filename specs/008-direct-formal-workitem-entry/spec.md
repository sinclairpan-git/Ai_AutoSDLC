# 功能规格：Direct Formal Work Item Entry

**功能编号**：`008-direct-formal-workitem-entry`  
**创建日期**：2026-03-31  
**状态**：已冻结（formal work item baseline）  
**输入**：[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-31-003`、[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)、[`../../docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`../../templates/spec-template.md`](../../templates/spec-template.md)、[`../../templates/plan-template.md`](../../templates/plan-template.md)、[`../../templates/tasks-template.md`](../../templates/tasks-template.md)

> 口径：本 work item 不是回头迁移所有历史 `docs/superpowers/*`，而是把“新 framework capability 的 canonical 设计/计划入口应当直接位于 `specs/<WI>/`”落成正式规则、脚手架与 CLI。

## 范围

- **覆盖**：
  - 新 framework capability 的 canonical spec/plan/tasks 直接落于 `specs/<WI>/`
  - direct-formal scaffold/init 路径，使用现有模板一次性生成 parser-friendly formal docs
  - `related_doc` / `related_plan` 等 reference 挂接，允许引用 design input 而不是重复抄写
  - `pipeline.md`、用户约定、用户文档中对“direct-to-formal”入口的统一口径
  - direct-formal CLI / scaffold 的基本测试与 command discoverability
- **不覆盖**：
  - 自动迁移所有历史 `docs/superpowers/*`
  - 修改宿主 superpowers skill 仓库本身的保存路径
  - execute 阶段实现任务本身
  - 把所有 `docs/superpowers/*` 一律视为 formal work item

## 已锁定决策

- 新 framework capability 的 canonical spec/plan/tasks 从一开始就直接写入 `specs/<WI>/`
- `docs/superpowers/*` 如继续存在，只能是 draft / design input / auxiliary reference
- formal work item 是 canonical truth，external design docs 只能被引用，不能要求重复搬运
- 入口应优先通过 direct-formal scaffold/init 形成 parser-friendly skeleton，而不是人工复制粘贴
- 本次只修框架工作流，不改宿主 skill 仓库本体

## 用户故事与验收

### US-008-1 — Framework Maintainer 需要单一 canonical doc set

作为**框架维护者**，我希望新的 framework capability 从一开始就直接生成 formal `spec.md / plan.md / tasks.md`，以便不再先写一套 `docs/superpowers/*` 再补一套 `specs/<WI>/...`。

**验收**：

1. Given 一个新的 framework capability，When 初始化 work item，Then 系统直接在 `specs/<WI>/` 创建 canonical spec/plan/tasks skeleton
2. Given formal docs 已创建，When 继续 review / execute，Then 后续流程只围绕这套 canonical docs 展开

### US-008-2 — Reviewer 需要 design input 可引用而不重复搬运

作为**reviewer**，我希望如果已有外部 design notes，也只是被 formal docs 引用，而不是再复制一整套内容，以便 traceability 清晰且不重复维护。

**验收**：

1. Given 存在外部 design notes，When 初始化 formal work item，Then formal docs 可记录 `related_doc / related_plan` 之类引用
2. Given formal docs 已引用 external design input，When review canonical truth，Then 不需要再维护第二套同内容正文

### US-008-3 — Operator 需要 direct-formal scaffold 可发现且可验证

作为**operator**，我希望有一个明确的 CLI/脚手架入口去初始化 formal work item，并能通过测试验证输出结构稳定，以便 direct-to-formal 成为默认路径而不是口头约定。

**验收**：

1. Given 仓库内执行 direct-formal scaffold 命令，When 命令结束，Then parser-friendly `spec.md / plan.md / tasks.md` 已生成
2. Given 生成后的 formal docs，When 执行只读校验，Then 规则面保持一致，且不会要求“先有 `docs/superpowers/*`”

## 功能需求

### Canonical Entry Path

| ID | 需求 |
|----|------|
| FR-008-001 | 对新 framework capability，canonical spec/plan/tasks 必须直接落在 `specs/<WI>/spec.md`、`plan.md`、`tasks.md` |
| FR-008-002 | `docs/superpowers/specs/*.md` 与 `docs/superpowers/plans/*.md` 若存在，只能作为 design input / auxiliary reference，不得作为必须先写的 canonical 文档 |
| FR-008-003 | formal work item 创建后，后续 review / execute / close 真值必须围绕 `specs/<WI>/...` 展开 |

### Direct-Formal Scaffold

| ID | 需求 |
|----|------|
| FR-008-004 | 系统必须提供 direct-formal scaffold/init 路径，一次性创建 parser-friendly `spec.md / plan.md / tasks.md` skeleton |
| FR-008-005 | scaffold/init 必须复用现有 spec/plan/tasks 模板，而不是另造一套文档模板 |
| FR-008-006 | scaffold/init 必须支持可选的 `related_doc` / `related_plan` 或等价引用挂接，而不是强制复制 external design 内容 |

### Workflow And Docs

| ID | 需求 |
|----|------|
| FR-008-007 | `pipeline.md` 与用户约定必须显式声明 direct-formal 是新 framework capability 的默认 canonical 入口 |
| FR-008-008 | 用户文档与 command discovery 必须暴露 direct-formal scaffold 命令，并说明它替代“先写 superpowers 再 formalize”的旧做法 |
| FR-008-009 | direct-formal 路径不得要求预先存在 `docs/superpowers/*` 才能继续 |

### Explicit Non-Goals

| ID | 需求 |
|----|------|
| FR-008-010 | 本次不要求修改宿主 superpowers skill 仓库或其默认保存路径 |
| FR-008-011 | 本次不自动迁移历史 `docs/superpowers/*` 到 `specs/<WI>/` |
| FR-008-012 | 本次不把所有 design input 自动识别成 formal work item |

## 成功标准

- **SC-008-001**：新 framework capability 可以直接生成 `specs/<WI>/spec.md + plan.md + tasks.md`，不再需要先写 `docs/superpowers/*`
- **SC-008-002**：若存在 external design docs，formal work item 只需引用它们，而不是重复维护第二套 canonical 内容
- **SC-008-003**：direct-formal scaffold 生成的文档结构 parser-friendly，且与现有模板语义一致
- **SC-008-004**：规则文档、用户文档与 CLI discoverability 在“direct-to-formal 是默认入口”这一点上保持一致
- **SC-008-005**：该能力落地后，framework capability 的 formal work item 落盘不再依赖“先产一套 superpowers 文档再补录”
