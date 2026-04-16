# 功能规格：Frontend P2 Cross Provider Consistency Baseline

**功能编号**：`150-frontend-p2-cross-provider-consistency-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：承接 `145 Track D`，将 `cross-provider consistency`、`shared verdict`、`diff surface` 与 `consistency certification` 正式 materialize 为下一条前端主线 child work item。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`、`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`、`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`、`specs/149-frontend-p2-quality-platform-baseline/spec.md`

> 口径：`145` 已把剩余前端 later-phase capability 拉平成 `Track A -> Track B -> Track C -> Track D -> Track E` 的 canonical child DAG；`147` 已物化 page/ui schema runtime baseline，`148` 已物化 theme/token governance runtime baseline，`149` 已冻结 quality platform baseline，`073` 已完成 provider/style 第一阶段 truth。`150` 的职责不是扩 provider roster，不是开放 public provider choice surface，也不是提前进入 React exposure，而是把“现有 provider 集合如何在共享 schema/theme/quality truth 下进行一致性比较、如何输出 machine-verifiable diff/certification、以及如何为 Track E 提供准入门槛”冻结成 Track D 的单一真值。

## 问题定义

当前仓库已经具备 Track D 所需的四类上游能力：

- `073` 已提供 provider/style support、solution snapshot、requested/effective 第一阶段 truth；
- `147` 已提供 provider-neutral 的 `page schema / ui schema / render slot / section anchor` 结构锚点；
- `148` 已提供 `theme pack / token mapping / custom override / style editor boundary` 的共享 theme truth；
- `149` 已冻结 `quality verdict / evidence / matrix` 的统一 handoff 口径。

但 Track D 仍缺少一条独立 child 去回答以下问题：

- enterprise/public 等现有 provider 在同一 schema/theme/quality 输入下，到底如何分别表达最终一致性结论、上游阻塞原因、可比性状态与证据新鲜度，而不是把这些语义混成一个枚举；
- 不同 provider 之间的差异，应该以什么 machine-verifiable diff surface 暴露，而不是靠人工截图对比或散落的运行日志；
- 一致性认证到底消费 `149` 的哪一层 quality verdict，而不是重新发明 visual/a11y/interaction 的判定标准；
- provider 比较中的 coverage gap、upstream blocker、不可比场景、能力缺口与 UX 级别不等价应如何结构化记录，避免被误报为“provider expansion 已经准备就绪”；
- Track E `modern provider expansion` 应该消费哪一层 certification truth，才能知道何时允许扩张 provider roster、公开选择面或 React exposure。

如果没有 `150`，后续实现会继续出现几类偏差：

- 在没有统一 diff/certification truth 的情况下直接扩 provider，导致 Track E 只能靠临时脚本或人工判断决定是否准入；
- 让 provider consistency 自己重建 schema、theme 或 quality 输入，破坏 `147/148/149` 的单一真值分层；
- 把 provider 支持差异、theme 覆盖缺口、quality blocker 与真正的 consistency drift 混在一起，无法回答“到底是不一致，还是上游输入尚未满足”。

因此，`150` 的职责是先 formalize Track D 的 canonical boundary、输入输出、认证语义与 downstream handoff，再决定后续 runtime 如何逐批落地。

## 范围

- **覆盖**：
  - 冻结 Track D `cross-provider consistency` 的问题定义、单一真值边界与 owner boundary
  - 明确 `073`、`147`、`148`、`149` 分别向 Track D 提供 provider/style truth、schema truth、theme truth 与 quality truth
  - 冻结统一的 `consistency state vector / diff surface / certification bundle / coverage gap / UX equivalence` 语义
  - 冻结 provider 对比至少围绕 `073 provider_manifest.style_support_matrix` 派生的 release-eligible provider 组合展开，不以本工单扩张 provider roster
  - 冻结 Track D 至少承接 `shared verdict`、`structured diff surface`、`consistency certification workflow`、`machine-verifiable handoff` 与 `Track E readiness gate`
  - 冻结后续 runtime 推荐切片：models -> diff/certification artifact materialization -> validator/rules -> ProgramService/CLI/verify handoff
- **不覆盖**：
  - 不重写 `073` 已完成的 provider/style 第一阶段 truth
  - 不重写 `147` schema truth、`148` theme truth、`149` quality truth
  - 不在本工单中扩 provider roster、开放 public provider choice surface、开放 React exposure 或 style editor runtime
  - 不把 Track E `modern provider expansion` 伪装成已完成
  - 不绕过 `149` 的统一质量判定去重新定义 visual/a11y/interaction 通过标准

## 已锁定决策

- `150` 是 `145` 已指定的 Track D child，不重新做 capability census；
- Track D 必须消费 `073` provider/style truth、`147` schema truth、`148` theme truth、`149` quality truth，禁止回退到 provider 私有结构或自由输入；
- Track D 的首批比较范围仅限 `073 provider_manifest.style_support_matrix` 中当前 release-eligible 的 provider/style 组合：`unsupported` 不进入比较，`degraded` 只允许在当前发布策略显式准入时进入比较；
- Track D 必须使用分层的 `consistency state vector`，至少拆分 `final_verdict`、`comparability_state`、`blocking_state`、`evidence_state` 四个维度，避免把 drift、原因、可比性与复检状态折叠成单一 verdict；
- Track D 必须把“用户体验上一致”冻结为显式 contract：至少覆盖关键任务结果、信息架构/结构锚点、关键交互反馈/状态时序，并允许 provider-native 的非关键视觉差异存在；
- Track D 必须定义 machine-verifiable 的 diff/certification artifact root、handoff schema 与 truth surfacing record，供 ProgramService、CLI、verify、program truth 与 Track E 直接消费；
- `150` 当前只做 docs-only formal freeze，不进入 `src/` / `tests/`，不宣称完整 consistency runtime 已落地；
- `150` 完成后，下一条前端主线默认进入 Track E，而不是回头重做 Track D planning。

## 用户故事与验收

### US-150-1 — Maintainer 需要独立的 Track D baseline

作为**框架维护者**，我希望 cross-provider consistency 有独立 child work item，这样我不需要继续把 provider 差异问题散落到 provider/style、quality platform 或 provider expansion 工单里。

**优先级说明**：P0。`145` 已明确 Track D 必须独立存在；如果继续缺位，后续 provider expansion 仍会失去认证准绳。

**独立测试**：只阅读 `150/spec.md`，就能知道 Track D 到底解决什么、依赖什么、当前明确不解决什么。

**验收场景**：

1. **Given** 我审阅 `150/spec.md`，**When** 我检查 scope 与 locked decisions，**Then** 我能明确看到 Track D 与 Track C / Track E 的边界
2. **Given** 我对照 `145`，**When** 我检查 child DAG，**Then** 我能确认 `150` 就是 Track D 的正式承接

### US-150-2 — Consistency executor 需要共享的 schema/theme/quality truth

作为**一致性执行者**，我希望 cross-provider consistency 直接消费 `147` schema truth、`148` theme truth 与 `149` quality truth，这样我不需要重新定义比较输入或通过标准。

**优先级说明**：P0。缺少共享输入真值，会直接导致 Track D 与上游分层失效。

**独立测试**：`150` 的实体与 upstream/downstream boundary 表可以直接被 runtime 实现与 Track E 引用。

**验收场景**：

1. **Given** 我准备实现 Track D，**When** 我查看 `150`，**Then** 我能找到必须消费的 schema/theme/quality/provider truth，而不需要重新推导输入
2. **Given** 我检查 `150` 的 non-goals，**When** 我规划实现切片，**Then** 我不会把 provider expansion 或 React exposure 混进当前 child

### US-150-3 — Reviewer 需要区分 drift、blocker 与 coverage gap

作为**reviewer**，我希望 `150` 明确区分真正的一致性漂移、上游 blocker、覆盖缺口与不可比场景，这样我可以判断后续认证结果是不是诚实。

**优先级说明**：P0。用户已经多次指出全局真值不能模糊化缺口；Track D 不能再把不同性质的问题折叠成一个“失败”。

**独立测试**：阅读 `150` 后，reviewer 能明确说出 consistency verdict 与 upstream blocker 的分层关系。

**验收场景**：

1. **Given** 我查看 `150` 的 verdict model，**When** 我核对 `073/147/148/149`，**Then** 我能区分输入缺失、执行阻塞与真实 drift
2. **Given** 我查看 `150` 的范围，**When** 我检查 certification 口径，**Then** 我能确认它不会越界到 provider expansion

### US-150-4 — Track E executor 需要可消费的 certification gate

作为**Track E 承接者**，我希望 Track D 先冻结统一的 consistency certification handoff，这样 modern provider expansion 不需要再自己定义“何时允许扩 provider、何时只能 advisory”。

**优先级说明**：P1。Track E 的顺利承接依赖 Track D 先定义统一认证输出。

**独立测试**：`150/plan.md` 可以直接读出 future handoff surface 如何接到 `ProgramService / CLI / verify` 与 Track E。

**验收场景**：

1. **Given** 我审阅 `150/plan.md`，**When** 我检查 future runtime slices，**Then** 我能看到 consistency verdict/diff/certification handoff 的明确顺序
2. **Given** 我对照 `149`，**When** 我检查 downstream boundary，**Then** 我能确认 Track E 只消费 Track D certification，而不是重建 consistency truth

### US-150-5 — UX reviewer 需要明确的一致性等价标准

作为**用户体验评审者**，我希望 `150` 明确什么叫“体验上一致”，这样我不会把 provider-native 的合理差异误判为 drift，也不会把真实的任务分叉误报为通过。

**优先级说明**：P0。没有 UX 等价标准，Track D 会在“像素级一致”和“技术上差不多即可”之间来回漂移。

**独立测试**：阅读 `150` 后，评审者能明确说出关键任务结果、信息架构、关键交互反馈与允许差异的关系。

**验收场景**：

1. **Given** 我审阅 `150/spec.md`，**When** 我查看 UX equivalence contract，**Then** 我能区分“允许的 provider-native 差异”和“阻塞 provider expansion 的真实体验分叉”
2. **Given** 我检查 diff surface，**When** 我对照 `149` 的 interaction quality 输入，**Then** 我能看到关键用户旅程被纳入显式比较单元

### 边界情况

- 某个 provider 因 `149` quality verdict 为 `blocked` 而无法完成对比时，Track D 必须记录为 `upstream-blocked`，不能误报为 provider drift
- 同一 schema/theme 组合仅在个别 viewport 或 interaction flow 上存在差异时，Track D 必须保留维度化 diff，而不能折叠成整体不一致
- 某些 provider 可能暂不覆盖某个 render slot 或 page schema；Track D 必须记录为 `coverage-gap` 或 `not-comparable`，而不是偷渡为 provider expansion 结论
- 当 theme override 自身违反 `148` boundary 时，Track D 不得继续做一致性认证，而应保留上游 blocker 语义
- Track D 不得把对比范围从现有 provider 组合扩到新的 modern provider；这属于 Track E 的责任边界
- provider-native 的非关键视觉/动效差异可被记录为 advisory，但关键任务结果、信息架构、关键交互反馈与 required schema slot 不得只因“看起来差不多”而放行

## 冻结的 Track D 状态与准入模型

### Consistency State Vector

Track D 不使用单一 verdict 枚举，而是使用以下四个并存维度：

| 维度 | 允许值 | 含义 |
|------|--------|------|
| `final_verdict` | `consistent` / `drifted` | 最终是否通过一致性比较 |
| `comparability_state` | `comparable` / `coverage-gap` / `not-comparable` | 当前 provider pair 是否覆盖了被要求比较的范围 |
| `blocking_state` | `ready` / `upstream-blocked` | 是否因 schema/theme/quality/provider truth 缺失而无法继续 |
| `evidence_state` | `fresh` / `advisory` / `needs-recheck` | 当前证据是否足以支持最终判断 |

约束：

- `final_verdict` 只表达最终结论，不承载 blocker、gap 或复检语义；
- `coverage-gap` 与 `not-comparable` 进入 `comparability_state`，不得编码进 `final_verdict`；
- `upstream-blocked` 进入 `blocking_state`，不得伪装成 drift；
- `advisory` 与 `needs-recheck` 进入 `evidence_state`，不得单独作为“已通过”或“已失败”的替代。

### UX Equivalence Contract

Track D 的“一致性”至少包含以下显式比较单元：

1. **关键任务结果一致**：同一用户旅程在各 provider 上必须产出相同任务结果与完成状态。
2. **信息架构与结构锚点一致**：`147` 中 required page/ui schema、section anchor、render slot 不得发生实质缺失或重排漂移。
3. **关键交互反馈一致**：`149` 中关键 interaction flow 的状态反馈、焦点/输入连续性、错误与成功反馈时序不得出现阻塞性分叉。
4. **允许的 provider-native 差异**：在不影响前三项的前提下，非关键视觉细节、provider-native 呈现差异可记录为 advisory，而不是直接判定 drift。

### Track E Readiness Gate

Track E 只能消费 Track D 的认证矩阵，不得自行重写准入规则：

| gate_state | 准入条件 | Track E 动作 |
|------------|----------|--------------|
| `ready` | `final_verdict=consistent`、`comparability_state=comparable`、`blocking_state=ready`，且 `evidence_state` 为 `fresh` 或仅存在非关键 advisory | 允许进入 provider expansion 评审 |
| `conditional` | `final_verdict=consistent`，但存在有限 `coverage-gap` 或非关键 advisory，且不影响 required user journeys / required schema slots | 仅允许受限评审，不得默认开放 public choice surface |
| `blocked` | 任一 required 维度出现 `drifted`、`upstream-blocked`、`needs-recheck` 或不可接受的 `coverage-gap/not-comparable` | 禁止进入 provider expansion |

## 冻结的 Track D handoff contract

### Canonical artifact root

```text
governance/frontend/cross-provider-consistency/
├── consistency.manifest.yaml
├── handoff.schema.yaml
├── truth-surfacing.yaml
├── readiness-gate.yaml
└── provider-pairs/
    └── <pair_id>/
        ├── diff-summary.yaml
        ├── certification.yaml
        └── evidence-index.yaml
```

### Frozen handoff schema

- `consistency.manifest.yaml`：声明 schema version、producer version、provider pair roster ref、artifact root ref。
- `handoff.schema.yaml`：声明 `final_verdict / comparability_state / blocking_state / evidence_state / diff_refs / certification_state / truth_surface` 的字段面。
- `truth-surfacing.yaml`：声明 Track D 输出进入 AI-SDLC program truth 时的 `consistency_state`、`gate_state`、`roster_scope_ref`、`artifact_root_ref` 与 `certification_ref`。
- `readiness-gate.yaml`：声明 `ready / conditional / blocked` 的裁决规则与 required/optional coverage 面。
- `provider-pairs/<pair_id>/diff-summary.yaml`：记录结构化 diff surface。
- `provider-pairs/<pair_id>/certification.yaml`：记录 Track E 可直接消费的认证结果。
- `provider-pairs/<pair_id>/evidence-index.yaml`：记录指向 `149` quality evidence 与 Track D 衍生证据的 repo-relative refs。

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-150-001 | `150` 必须把 Track D 定义为独立的 `cross-provider consistency` child baseline，而不是 `073`、`148`、`149` 的附注 |
| FR-150-002 | `150` 必须明确 Track D 位于 `147/148/149` 之后、`Track E` 之前，并继续遵守 `schema -> theme -> quality -> consistency -> provider expansion` 的单一真值顺序 |
| FR-150-003 | `150` 必须明确 `073` 提供 provider/style truth，`147` 提供 schema truth，`148` 提供 theme truth，`149` 提供 quality truth，当前工单不重复这些能力 |
| FR-150-004 | `150` 必须明确当前 work item 的非目标，包括 provider roster expansion、public provider choice surface、React exposure、开放 style editor runtime 与重新定义 quality 规则 |

### Consistency Scope And Verdict Model

| ID | 需求 |
|----|------|
| FR-150-005 | `150` 必须明确 Track D 至少承接 `shared verdict`、`structured diff surface`、`consistency certification workflow`、`coverage gap surfacing` 四类能力 |
| FR-150-006 | `150` 必须明确 provider 对比以共享 `page/ui schema`、`theme pack`、`quality matrix` 为输入锚点，而不是 provider 私有 DOM 或一次性脚本输出 |
| FR-150-007 | `150` 必须把 Track D 状态模型拆成 `final_verdict`、`comparability_state`、`blocking_state`、`evidence_state` 四个维度或等价分层，而不是单一 verdict 枚举 |
| FR-150-008 | `150` 必须明确 diff surface 至少能表达关键用户旅程、schema slot、theme token、quality dimension、severity、evidence refs 与 remediation hint |
| FR-150-009 | `150` 必须明确 consistency drift 不得替代 `149` quality verdict；Track D 只消费统一质量输出，不得重新定义 visual/a11y/interaction 通过标准 |
| FR-150-010 | `150` 必须冻结 UX equivalence contract，至少覆盖关键任务结果、信息架构/结构锚点、关键交互反馈与允许的 provider-native 差异边界 |

### Upstream Inputs And Certification Handoff

| ID | 需求 |
|----|------|
| FR-150-011 | `150` 必须明确上游至少依赖 `073/147/148/149`，并说明各自分别提供 provider/style truth、schema truth、theme truth 与 quality truth |
| FR-150-012 | `150` 必须明确首批对比范围只覆盖 `073 provider_manifest.style_support_matrix` 派生的 release-eligible provider/style 组合，不得借 consistency 名义提前扩 provider roster |
| FR-150-013 | `150` 必须明确 machine-verifiable 的 diff/certification artifact root，而不是人工截图判断、临时日志拼接或未归档脚本输出 |
| FR-150-014 | `150` 必须明确当上游 schema/theme/quality/provider truth 不完整时，Track D 应暴露 blocker/gap/recheck/advisory，而不是静默降级为默认一致 |
| FR-150-015 | `150` 必须定义 future `consistency certification bundle`，供 Track E `modern provider expansion` 直接消费 |
| FR-150-016 | `150` 必须冻结 Track E readiness gate 的裁决矩阵，明确 `ready / conditional / blocked` 的判断条件与对应准入动作 |

### Program Surfacing And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-150-017 | `150` 必须明确 ProgramService / CLI / verify constraints 未来如何 surfaced consistency verdict、diff summary 与 certification state，而不是让 Track D 游离在 AI-SDLC 主线之外 |
| FR-150-018 | `150` 必须定义 versioned、machine-verifiable 的 future artifact root 与 handoff schema，避免后续 runtime 临时命名或另起目录 |
| FR-150-019 | `150` 必须定义 Track D 输出进入 AI-SDLC global truth 的 truth surfacing record，包括 `consistency_state`、`gate_state`、`roster_scope_ref`、`artifact_root_ref` 与 `certification_ref` |
| FR-150-020 | `150` 必须在 `plan.md` 中给出未来 runtime 推荐切片，至少包括 models、artifact/certification materialization、validator/rules、ProgramService/CLI/verify handoff |
| FR-150-021 | `150` 必须清楚区分 docs-only formal freeze、后续 runtime slices 与 truth refresh readiness，不得用“一致性认证”掩盖尚未实现的事实 |
| FR-150-022 | `150` 当前不得宣称 shared verdict、diff engine、certification runtime 已落地；close 语义只能是“Track D canonical baseline 与 decomposition 已冻结” |
| FR-150-023 | `150` 必须明确 Track E 只消费 Track D certification truth，不得回头重建 consistency baseline |
| FR-150-024 | `150` 必须把 `python -m ai_sdlc program truth sync --execute --yes` 与 `python -m ai_sdlc program truth audit` 纳入 Track D close-out 的强制真值门禁，而不是笼统表述为 truth refresh |

## 关键实体

- **Provider Consistency Matrix**：承载 Track D 对 provider pair、page schema、theme、quality dimension 的结构化比较视图
- **Consistency State Vector**：表达 `final_verdict`、`comparability_state`、`blocking_state`、`evidence_state` 四个维度的组合状态
- **UX Equivalence Contract**：表达关键任务结果、信息架构、关键交互反馈与允许差异边界
- **Diff Surface Record**：表达 provider 间的关键用户旅程、schema slot、theme token、quality dimension 与行为差异
- **Consistency Certification Bundle**：表达 Track D 对 Track E、ProgramService、CLI、verify 与 program truth 输出的统一认证摘要与证据引用
- **Coverage Gap Record**：表达当前 provider 组合尚未覆盖的 schema/theme/flow 范围，以及为何属于 gap 而非 drift
- **Provider Expansion Readiness Gate**：表达 Track E 准入判断应消费的 certification state，而不是临时规则
- **Truth Surfacing Record**：表达 Track D 输出如何进入 AI-SDLC global truth 的稳定字段面与引用关系

## 推荐的 Track D capability decomposition

| 子域 | 主要职责 | 必须消费的上游 truth | 当前不做 |
|------|----------|----------------------|----------|
| `Shared Verdict Layer` | 统一 provider consistency verdict 与状态分层 | `073`、`147`、`148`、`149` | 不扩 provider roster |
| `Structured Diff Layer` | user journey/schema/theme/quality 维度化 diff surface | `147`、`148`、`149` | 不重建 schema/theme truth |
| `Coverage Gap Layer` | 记录不可比场景、能力缺口与 blocker | `073`、`147`、`149` | 不把 gap 伪装成 drift |
| `Certification Handoff Layer` | 形成 Track E / ProgramService 可消费的 certification bundle | Track D 前三层输出 | 不开放 public provider choice surface |
| `Program Surfacing Layer` | surfaced consistency verdict、diff summary、readiness gate、truth surface | Track D 前四层输出 | 不进入 provider expansion runtime |

## 成功标准

- **SC-150-001**：`150` 能独立表达 Track D 的 scope、non-goals、upstream inputs 与 downstream handoff，而无需重新回到顶层设计临时推断
- **SC-150-002**：`150` 明确隔离 `073/147/148/149` 已提供 truth 与 Track D 自身新增的一致性能力，不再误报已完成内容
- **SC-150-003**：`150` 明确要求 Track D 必须消费共享 schema/theme/quality truth，不再围绕 provider 私有输入重建比较规则
- **SC-150-004**：`150` 的 `plan.md / tasks.md` 能直接读出后续 runtime 切片与 ProgramService/CLI/verify 接入顺序
- **SC-150-005**：Track E `modern provider expansion` 能把 `150` 作为统一 certification truth 引用，而不需要重新定义 readiness gate
- **SC-150-006**：`150` formal docs 不再包含模板占位、范围冲突或“consistency/provider expansion”混写的模糊表述
- **SC-150-007**：`150` 明确冻结 multi-axis consistency state model、UX equivalence contract、artifact root 与 truth surfacing record，避免后续 runtime 再发明第二套规则

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
  - "specs/149-frontend-p2-quality-platform-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
