# 功能规格：Frontend P2 Multi Theme Token Governance Baseline

**功能编号**：`148-frontend-p2-multi-theme-token-governance-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：承接 `145 Track B`，将 `multi-theme pack / token mapping / custom theme token / style editor boundary` 正式 materialize 为下一条前端主线 child work item。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/017-frontend-generation-governance-baseline/spec.md`、`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`、`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`

> 口径：`145` 已把剩余前端 deferred capability 全量拉平，并明确 Track B 必须承接 `multi-theme/token governance`。`073` 已冻结 style pack、provider style support、`solution_snapshot` 与 requested/effective 第一阶段真值；`147` 已把 page/UI schema anchor 物化为 runtime baseline。`148` 的职责不是再造第二套 style truth，也不是提前开放自由样式编辑器，而是把“多主题治理、schema-anchor token mapping、自定义 theme token 边界、style editor boundary”冻结成可继续实现和验证的 canonical baseline，供后续 `quality platform` 与 `cross-provider consistency` 直接消费。

## 问题定义

当前前端主线已经具备三条关键上游能力：

- `017` 已建立 minimal token / naked-value rules 的 generation floor；
- `073` 已建立 `style_pack_manifest`、`provider_manifest.style_support_matrix`、`solution_snapshot`、`resolved_style_tokens` 与 `provider_theme_adapter_config` 的第一阶段 truth；
- `147` 已建立 provider-neutral 的 `page schema / ui schema / render slot / section anchor` 结构 anchor。

但现在仍缺少一个独立的 canonical child，去回答 Track B 的几个关键问题：

- 多个 style pack 如何从“可被选择”升级为“可被治理、可被验证、可被下游消费”的 multi-theme truth；
- token mapping 如何绑定到 `147` 的 page/UI schema anchor，而不是停留在 provider 内部或项目级自由样式实现；
- 自定义 theme token 如何被受控表达、审计、降级与回退，而不是重新回到裸值或 prompt 临时发挥；
- style editor 如果要存在，允许的操作边界是什么，哪些输入必须被禁止；
- `quality platform` 与 `cross-provider consistency` 未来应该消费哪一层 theme truth，而不是各自重新推导主题状态。

如果没有 `148` 这条 child，后续实现会继续出现三类风险：

- 把 theme/token 问题塞回 `073` 的 solution 轨道，导致 provider/style truth 与 theme governance truth 再次纠缠；
- 让 `quality` 或 `consistency` 工单被迫各自重建 theme/token 语义，破坏单一真值；
- 以“开放 style editor”为名重新放开裸样式、provider-specific token 或 DOM selector 级别的不可治理输入。

因此，`148` 的职责是先把 Track B 的单一真值边界 formalize，再给后续 runtime 切片和专家评审一个明确、可对抗审查的基线。

## 范围

- **覆盖**：
  - 冻结 Track B 的 `multi-theme/token governance` 问题定义、单一真值边界与 owner boundary
  - 明确 `073` 的 `style_pack_manifest` / `provider_manifest.style_support_matrix` / `solution_snapshot` 与 `148` 的继承关系
  - 明确 `147` 的 `section anchor / render slot / page/ui schema` 是 theme token mapping 的结构锚点
  - 冻结 `custom theme token` 的受控覆盖边界、允许的命名空间、作用域层级与审计语义
  - 冻结 `style editor boundary`，明确只允许结构化、可验证、可审计的样式修改操作
  - 冻结后续 runtime 的推荐切片顺序：models -> artifacts/validator -> ProgramService/CLI/verify handoff
  - 使 `148` 可作为后续 Track C/D 的 canonical upstream input
- **不覆盖**：
  - 不在本工单中实现新的 provider、quality platform、cross-provider certification 或 provider expansion
  - 不把 `073` 的 `provider_manifest.style_support_matrix` 改写为第二套 theme truth
  - 不把 `147` 的 schema anchor 重新包装成 theme truth 或 provider truth
  - 不开放自由文本 CSS、任意 hex/rgb、DOM selector 级样式编辑器、React exposure 或公开 provider choice surface
  - 不把 Track C/D/E 伪装成已经完成

## 已锁定决策

- `148` 是 `145` 已指定的 Track B child，不重新做 capability census；
- `073` 的 `style_pack_manifest` 仍是 style/theme pack 本体来源，`provider_manifest.style_support_matrix` 仍是 provider 风格支持等级唯一真值来源；
- `147` 的 `section anchor / render slot / page/ui schema` 必须成为 token mapping 的结构锚点，禁止回退到 DOM selector 或 provider-specific component path；
- `017` 的 minimal token / naked-value rules 是 theme governance 的底线，不因 `148` 引入 custom theme token 就被放松；
- `custom theme token` 必须通过结构化 override envelope 表达，允许 requested/effective、scope、reason 与 fallback 被审计；
- `custom theme token` 的 v1 覆盖优先级固定为 `global -> page -> section -> slot`，后续 Track C/D 必须直接消费这一顺序；
- `style editor boundary` 的 v1 形态固定为“只读诊断 + 结构化变更提案”；任何直接写入面、拖拽调参面或视觉 IDE 都属于后续独立 tranche，不在 `148` 内实现；
- `148` 的 multi-theme v1 直接复用 `073` 已存在的五套 style pack 作为受治理主题集合，不额外引入独立 `theme variant` 对象；
- `148` 完成后，后续 `quality platform` 与 `cross-provider consistency` 必须消费其 theme truth，而不是重新定义 token map。

## 用户故事与验收

### US-148-1 — Maintainer 需要一个独立的 Track B baseline

作为**框架维护者**，我希望 `multi-theme/token governance` 有独立 child work item，这样我不需要再把主题治理问题继续塞进 `073`、`147` 或后续质量工单里。

**优先级说明**：P0。`145` 已明确它是 Track B 的正式承接；如果继续缺位，前端主线还会再次漏项。

**独立测试**：只阅读 `148/spec.md`，就能知道 Track B 要解决什么、依赖什么、当前明确不解决什么。

**验收场景**：

1. **Given** 我审阅 `148/spec.md`，**When** 我检查 scope 与 locked decisions，**Then** 我能明确看到 multi-theme/token governance、自定义 token 与 style editor boundary 的边界
2. **Given** 我对照 `145`，**When** 我检查 child sequence，**Then** 我能确认 `148` 就是 Track B 的正式承接

### US-148-2 — Downstream executor 需要共享 theme truth

作为**后续 child 的执行者**，我希望 theme/token 先被 formalize，这样 `quality platform` 与 `cross-provider consistency` 可以消费同一套 theme truth，而不是各自临时推导主题状态。

**优先级说明**：P0。缺少共享 theme truth，会直接导致 Track C/D 各自重写 style/token 语义。

**独立测试**：`148` 的 scope、实体与 downstream boundary 表能直接被 Track C/D 引用。

**验收场景**：

1. **Given** 我准备进入 Track C 或 Track D，**When** 我查看 `148`，**Then** 我能找到可引用的 theme/token governance anchor，而不需要重新定义 token map
2. **Given** 我检查 `148` 的边界，**When** 我阅读 non-goals，**Then** 我不会把 quality execution、cross-provider certification 或 provider expansion 混进当前 child

### US-148-3 — UX reviewer 需要有边界的自定义与 style editor

作为**用户体验 reviewer**，我希望 `148` 明确 style editor 和 custom token 的允许范围，这样我可以判断后续主题能力会不会重新放开失控样式输入。

**优先级说明**：P0。用户已经明确要求后续要经受 UX 专家对抗评审；如果边界不清晰，后续实现很容易退化为“有个编辑器就行”。

**独立测试**：阅读 `148` 后，reviewer 能明确说出哪些 theme 操作允许、哪些被禁止、哪些必须被审计。

**验收场景**：

1. **Given** 我查看 `148` 的 style editor boundary，**When** 我核对允许的输入面，**Then** 我看不到开放式 CSS / 裸值 / DOM selector 式操作
2. **Given** 我查看 custom theme token 语义，**When** 我评估 override boundary，**Then** 我能明确看到 requested/effective、作用域与降级语义

### US-148-4 — AI-Native framework reviewer 需要主题治理进入流水线

作为**AI-Native 开发框架 reviewer**，我希望 `148` 明确 theme truth 应如何接入 models、artifacts、validators、ProgramService 与 CLI，这样后续主题治理不会再次游离在 AI-SDLC 主链之外。

**优先级说明**：P1。用户已明确指出“全局真值没有真正融入整个 AI-SDLC 流水线”，Track B 不能再重复这个问题。

**独立测试**：`148/plan.md` 可以直接读出未来 runtime 切片如何接到 `src/` / `tests/` / `program truth`，而不是停留在口头说明。

**验收场景**：

1. **Given** 我审阅 `148/plan.md`，**When** 我检查 implementation slices，**Then** 我能看到 models、artifacts、validator、ProgramService/CLI 的明确顺序
2. **Given** 我检查 `148` 的 handoff 设计，**When** 我对照 `017/073/147`，**Then** 我能确认 Track B 不会再另起一套 theme 流水线

### 边界情况

- 同一个 style pack 在不同 provider 上可能拥有不同 fidelity status，theme governance 不得覆盖 `provider_manifest.style_support_matrix`
- page/ui schema version 演进后，旧 token map 可能引用失效 anchor，必须有结构化 blocker
- custom theme token 可能只作用于页面或 section 级别，而不是全局；其 scope 必须被显式表达
- 高级模式允许用户显式选择 `degraded` 风格，但必须保留 requested/effective 差异与降级原因
- style editor 如果尝试写入裸颜色、裸阴影、裸间距或 provider-specific token key，必须被拒绝或转为结构化 exception/override

## 功能需求

### Theme Truth Contract

| ID | 需求 |
|----|------|
| FR-148-001 | `148` 必须把 Track B 定义为独立的 `multi-theme/token governance` child baseline，而不是 `073` 或 `147` 的附属说明 |
| FR-148-002 | `148` 必须定义基于 `073 style_pack_manifest` 的 multi-theme/theme-pack 治理语义，不得另造第二套 style pack inventory |
| FR-148-003 | `148` 必须定义 schema-anchor-bound 的 token mapping contract，使 theme token 与 `147` 的 `page schema / ui schema / render slot / section anchor` 建立稳定关联 |
| FR-148-004 | `148` 必须定义 `custom theme token override` 的结构化 envelope，至少包含 scope、allowed namespace、requested/effective、reason 与 fallback 语义 |
| FR-148-005 | `148` 必须保持 `provider_manifest.style_support_matrix` 是 provider 风格支持等级、降级原因与兼容状态的唯一真值来源 |
| FR-148-006 | `148` 必须明确 theme selection 与 custom override 如何继承 `solution_snapshot` 的 requested/effective 审计语义，而不是另起平行快照 |

### Style Editor Boundary And UX Safety

| ID | 需求 |
|----|------|
| FR-148-007 | `148` 必须把 `style editor boundary` 定义为结构化、可验证、可审计的操作面，不允许默认开放自由文本 CSS、裸颜色/阴影/间距或 DOM selector 级操作 |
| FR-148-008 | `148` 必须定义用户可见 diagnostics 的 canonical IA，至少明确 `theme list -> effective state summary -> diff/override drawer -> revert/approve path` 的阅读与回退路径，并区分 operator summary 与 audit detail |
| FR-148-009 | `148` 必须明确 `017` 的 minimal token / naked-value rules 仍是底线，Track B 只能在此之上增加 theme-aware governance，不得回退到 prompt-only 样式控制 |
| FR-148-010 | `148` 必须明确 custom token 只能作用于受控 scope（如 global/page/section/slot），不得直接引用 provider-specific 内部 token 名或运行时 DOM path |

### Upstream / Downstream Boundary

| ID | 需求 |
|----|------|
| FR-148-011 | `148` 必须明确上游至少依赖 `017/073/145/147`，并说明各自分别提供 generation floor、style solution truth、Track B planning boundary 与 schema anchor |
| FR-148-012 | `148` 必须明确下游 `quality platform` 与 `cross-provider consistency` 应消费其 theme truth，而不是重新定义 token map、style editor boundary 或 custom override 规则 |
| FR-148-013 | `148` 当前不得实现 quality execution、cross-provider certification、provider roster expansion、React exposure、公开 provider choice surface 或开放式 style editor runtime |
| FR-148-014 | `148` 必须明确 owner boundary：`073` 负责 provider/style truth，`147` 负责 schema truth，`148` 负责 theme/token governance，Track C/D 只消费这些上游 truth |

### Rollout And Verification Honesty

| ID | 需求 |
|----|------|
| FR-148-015 | `148` 必须在 `plan.md` 中给出未来 runtime 的推荐切片顺序，至少包括 models、artifact materialization、validator/guardrails、ProgramService/CLI/verify handoff |
| FR-148-016 | `148` 必须把 docs-only formal freeze、对抗专家评审、后续 runtime slices 与 truth refresh readiness 清晰分离，不得用一句“后续实现”模糊带过 |
| FR-148-017 | `148` 必须定义版本化、machine-verifiable 的 future artifact/handoff schema 与固定 artifact root，确保后续 runtime 不会再临时命名或另起目录 |
| FR-148-018 | `148` 的 close 语义必须诚实表达为“Track B canonical baseline 与 implementation decomposition 已冻结”；在 runtime slices 未落地前，不得伪造 theme governance 已实现 |

## 关键实体

- **Theme Governance Set**：承载 Track B 顶层 theme/token governance truth 的结构化对象，继承现有 style pack inventory，而不复制它
- **Theme Token Mapping**：把 theme semantic token 映射到 `147` 的 schema anchor / render slot / page scope 的结构化映射关系
- **Custom Theme Token Override Envelope**：承载受控 override 的 requested/effective、scope、allowed namespace、reason、fallback 与 audit 语义
- **Style Editor Boundary Contract**：定义允许的 theme 编辑操作、禁止的自由输入以及 diagnostics / approval surface
- **Theme Governance Handoff**：供 Track C/D、ProgramService 与 CLI 消费的 theme truth surfaced diagnostics
- **Theme Governance Handoff Schema**：描述 Track B handoff 的版本、artifact root、payload shape 与 downstream compatibility 的 machine-verifiable contract

## 成功标准

- **SC-148-001**：`148` 独立成为 `145 Track B` 的 canonical child baseline，不再依赖会话记忆说明其存在
- **SC-148-002**：`148` 明确区分 `017` token floor、`073` style solution truth、`147` schema truth 与 `148` theme governance truth，不再出现第二套真值来源
- **SC-148-003**：`148` 明确冻结 custom theme token 与 style editor boundary，后续实现者不能再把“自由样式编辑”包装成 Track B
- **SC-148-004**：`148` 的 `plan.md / tasks.md` 能直接读出后续 runtime 切片、对抗专家评审门禁与 truth refresh readiness
- **SC-148-005**：`quality platform` 与 `cross-provider consistency` 能把 `148` 作为共享 theme/token truth 引用，而不必重新定义 token map
- **SC-148-006**：`148` 的 formal docs 不再包含模板占位、范围冲突或含糊的 deferred gap 描述

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
