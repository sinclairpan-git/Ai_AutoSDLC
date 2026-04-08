# 功能规格：Frontend Evidence Class Authoring Surface Baseline

**功能编号**：`082-frontend-evidence-class-authoring-surface-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md`](../081-frontend-framework-only-prospective-closure-contract-baseline/spec.md)、[`../../program-manifest.yaml`](../../program-manifest.yaml)、[`../../templates/program-manifest.example.yaml`](../../templates/program-manifest.example.yaml)

> 口径：`082` 在 `081` 的 prospective-only contract 之上，继续冻结 future frontend item 的 evidence class 应该如何被 authoring、放在哪、写成什么。`082` 明确 canonical source of truth 是各 spec 的 `spec.md` footer metadata，而不是当前 root `program-manifest.yaml`。本轮仍不修改 runtime、manifest 或既有 spec。

## 问题定义

`081` 已经定义了 future framework-only frontend item 必须声明 evidence class，但还缺少 authoring surface：

- author 到底应把该声明写在 `spec.md` 的什么位置，尚未冻结
- 机器未来要读取哪个键名、允许哪些值，尚未冻结
- 如果缺失、拼错、大小写不一致，尚未冻结成 formal authoring error
- `program-manifest.yaml` 当前没有对应字段，若未来要镜像，也需要先知道 source of truth 在哪里

如果这一层不补上，`081` 的 contract 仍然会停留在概念级别，后续 author、reviewer、runtime maintainer 可能各自发明不同写法。

## 范围

- **覆盖**：
  - 新建 `082` formal docs 与 execution log
  - 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `82`
  - 冻结 evidence class 的 canonical authoring surface
  - 冻结字段名、允许值、缺失/非法值的 authoring error 语义
  - 冻结 spec footer 与 future manifest mirror 的主从关系
- **不覆盖**：
  - 修改 `program-manifest.yaml` 或其模板
  - 修改 `src/` / `tests/` 或当前 `ai-sdlc` parser
  - retroactively 给既有 spec 回填 `frontend_evidence_class`
  - 改写 `068` ~ `071` 或任何当前 runtime 输出
  - 发明新的 runtime stage

## 已锁定决策

- future frontend item 的 evidence class canonical source of truth 在各自 `spec.md` 的 footer metadata
- canonical key 名称固定为 `frontend_evidence_class`
- 合法值只允许：
  - `framework_capability`
  - `consumer_adoption`
- 值必须使用全小写 snake_case；不允许别名、缩写、大小写混写
- 对 `082` 之后新增的 future frontend item：
  - 缺失 `frontend_evidence_class` 属于 authoring error
  - 非法值、空值、重复键、同一 spec 内多个互相冲突的声明都属于 authoring error
- future 若需要在 `program-manifest.yaml` 中镜像该字段，manifest 只能是 mirror，不得成为 source of truth

## Authoring Contract

### 1. Canonical declaration location

future frontend item 必须在对应 `spec.md` 末尾 YAML footer 中声明：

```yaml
---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
```

要求如下：

- `frontend_evidence_class` 必须位于 footer metadata 中
- footer 中该键只能出现一次
- body prose、标题、tasks、plan 中出现同名文本，不算正式声明

### 2. Allowed values

只允许两类：

- `framework_capability`
- `consumer_adoption`

语义沿用 `081`：

- `framework_capability`：框架能力、规则、CLI、schema、diagnostics、sample self-check、gate 或等价 framework-side deliverable
- `consumer_adoption`：消费方真实接入、真实 observation backfill、真实 contract alignment evidence

### 3. Authoring error semantics

对 `082` 后新增的 future frontend item，以下都属于 authoring error：

- 缺失 `frontend_evidence_class`
- `frontend_evidence_class: ""`
- 使用未登记值，例如 `framework`, `consumer`, `adoption`, `capability`
- 使用大小写或格式变体，例如 `FrameworkCapability`、`framework-capability`
- 在同一个 `spec.md` 中重复声明该键
- 在 prose 中描述一种 evidence class，但 footer metadata 声明了另一种

### 4. Source-of-truth priority

future runtime 若要读取 evidence class，应遵守以下优先级：

1. `spec.md` footer metadata 中的 `frontend_evidence_class`
2. future manifest mirror 或其他派生索引，只能作为缓存/镜像，不得覆盖 spec footer

因此：

- 本轮不要求给 `program-manifest.yaml` 新增字段
- future 如果引入 manifest mirror，必须与 spec footer 保持一一对应
- 若 future 出现 manifest mirror 与 spec footer 冲突，spec footer 为准

### 5. Applicability boundary

`082` 的 authoring surface 仅对 `082` 之后新增的 frontend item 生效，不 retroactive 套用到既有 spec。`068` ~ `071` 以及其他既有项不会因为本 baseline 自动变成 malformed。

## 用户故事与验收

### US-082-1 — Author 需要知道 evidence class 写在哪里

作为 **author**，我希望 future frontend item 的 evidence class 有一个唯一、固定、机器可读的声明位置，这样我在写 spec 时不会猜应该写在正文、plan、task 还是 manifest。

**验收**：

1. Given 我阅读 `082`，When 我新建 frontend spec，Then 我知道必须在 `spec.md` footer metadata 中写 `frontend_evidence_class`
2. Given 我在 prose 中写了 evidence class，但 footer 没写，When reviewer 对照 `082`，Then 该 spec 仍应被视为 authoring incomplete

### US-082-2 — Runtime Maintainer 需要固定的键名和值域

作为 **future runtime maintainer**，我希望 future parser 读取的是一个固定键名和封闭值域，这样后续实现不会反复处理别名和语义漂移。

**验收**：

1. Given 我阅读 `082`，When 我规划 parser，Then 我知道要读取 `frontend_evidence_class`
2. Given 我看到 `framework-capability` 或 `FrameworkCapability`，When 我按 `082` 判断，Then 我知道它们都不是合法值

### US-082-3 — Reviewer 需要判断 manifest 只是 mirror

作为 **reviewer**，我希望 `082` 说明 spec footer 才是 canonical source of truth，这样 future manifest 字段不会和原始 spec 抢主语义。

**验收**：

1. Given 我阅读 `082`，When 我比较 future spec footer 与 manifest mirror，Then 我知道冲突时以 spec footer 为准

## 功能需求

| ID | 需求 |
|----|------|
| FR-082-001 | `082` 必须明确 future frontend item 的 evidence class canonical declaration location 是 `spec.md` footer metadata |
| FR-082-002 | `082` 必须把 canonical key 冻结为 `frontend_evidence_class` |
| FR-082-003 | `082` 必须把合法值限制为 `framework_capability` 与 `consumer_adoption` |
| FR-082-004 | `082` 必须明确缺失、空值、非法值、重复键与冲突声明都属于 authoring error |
| FR-082-005 | `082` 必须明确 `program-manifest.yaml` 未来最多只是 mirror，不得覆盖 spec footer |
| FR-082-006 | `082` 必须保持 prospective-only，不 retroactively 要求既有 spec 回填该字段 |
| FR-082-007 | `082` 不得修改 `program-manifest.yaml`、`src/`、`tests/` 或当前 runtime behavior |
| FR-082-008 | `082` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `81` 推进到 `82` |

## 成功标准

- **SC-082-001**：future author 能直接从 `082` 知道 evidence class 应写在 `spec.md` footer 的哪个键
- **SC-082-002**：future parser/validator maintainer 能直接复用 `frontend_evidence_class` 与其封闭值域
- **SC-082-003**：reviewer 能明确判断 manifest 不是 evidence class 的 primary truth
- **SC-082-004**：本轮 diff 仅新增 `082` docs 并推进 `project-state.yaml`

---
related_doc:
  - "specs/081-frontend-framework-only-prospective-closure-contract-baseline/spec.md"
  - "program-manifest.yaml"
  - "templates/program-manifest.example.yaml"
frontend_evidence_class: "framework_capability"
---
