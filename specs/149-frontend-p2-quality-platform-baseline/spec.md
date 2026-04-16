# 功能规格：Frontend P2 Quality Platform Baseline

**功能编号**：`149-frontend-p2-quality-platform-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：承接 `145 Track C`，将完整 `visual regression / a11y platform / interaction quality / multi-browser multi-device matrix` 正式 materialize 为下一条前端主线 child work item。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md`、`specs/137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline/spec.md`、`specs/095-frontend-mainline-product-delivery-baseline/spec.md`、`specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline/spec.md`、`specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md`、`specs/147-frontend-p2-page-ui-schema-baseline/spec.md`、`specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md`

> 口径：`145` 已把剩余前端 later-phase capability 拉平成 `Track A -> Track B -> Track C -> Track D -> Track E` 的 canonical child DAG；`147` 已物化 page/ui schema runtime baseline，`148` 已物化 theme/token governance runtime baseline，`071/137` 已完成 P1 visual/a11y foundation，`095/143/144` 已完成 frontend-mainline-delivery 的主链 runtime。`149` 的职责不是重做 foundation，不是重做 browser gate/host remediation，也不是提前做 cross-provider certification 或 provider expansion，而是把“完整质量平台应消费哪些 schema/theme/runtime truth、需要补哪些 richer evidence/quality verdict、当前明确不开放哪些执行面”冻结成 Track C 的单一真值。

## 问题定义

当前仓库已经具备几类关键上游能力：

- `071/137` 已冻结并落地 P1 visual / a11y foundation；
- `095/143/144` 已打通 frontend-mainline-delivery、真实 browser probe、host remediation 与 workspace integration；
- `147` 已提供 provider-neutral 的 `page schema / ui schema / render slot / section anchor` 结构锚点；
- `148` 已提供 `theme governance / token mapping / custom override / style editor boundary` 的共享 theme truth。

但 Track C 仍缺少一条独立 child 去回答以下问题：

- 完整 quality platform 相比 `071/137` 的 foundation，到底新增哪些 visual / a11y / interaction / matrix 能力；
- quality truth 如何直接消费 `147` 的 schema truth 与 `148` 的 theme truth，而不是再围绕 provider 私有 DOM、一次性截图脚本或自由主题输入重建规则；
- richer browser/device matrix、interaction quality、visual regression 与 a11y verdict 应如何被统一表达、验证与下游消费；
- mainline delivery 已有 runtime（`095/143/144`）与 Track C 的质量平台边界在哪里，哪些由 delivery runtime 提供执行底座，哪些才是 quality platform 负责新增的检查与证据；
- Track D `cross-provider consistency` 未来到底应该消费哪一层质量 verdict，而不是各自再造第二套 diff/certification 口径。

如果没有 `149`，后续实现会继续出现几类偏差：

- 把 quality platform 重新塞回 `071/137` foundation 或 `143/144` runtime，导致“基础能力 / 执行底座 / 完整质量平台”三层再次纠缠；
- 让 `cross-provider consistency` 被迫自己重建 visual/a11y/interaction verdict，而不是消费统一 quality truth；
- 在尚未冻结 schema/theme 依赖和 matrix 边界前，先开 provider expansion、React exposure 或开放式 style editor，导致质量平台失去统一输入面。

因此，`149` 的职责是先 formalize Track C 的 canonical boundary、输入输出、执行切片与 downstream handoff，再决定后续 runtime 如何逐批落地。

## 范围

- **覆盖**：
  - 冻结 Track C `quality platform` 的问题定义、单一真值边界与 owner boundary
  - 明确 `071/137` 与 `149` 的 delivered/deferred 边界，避免把 foundation 重新包装成缺口
  - 明确 `095/143/144` 是 Track C 的 runtime 底座，而不是 Track C 自身的替代品
  - 明确 `147` schema truth 与 `148` theme truth 是 quality platform 的直接上游输入
  - 冻结 Track C 至少承接 `visual regression`、`complete a11y platform`、`interaction quality`、`multi-browser/multi-device matrix` 与 `richer evidence platform`
  - 冻结 quality verdict / evidence / certification handoff 应如何被 Track D 直接消费
  - 冻结后续 runtime 推荐切片：models -> artifact/evidence materialization -> validator/matrix -> ProgramService/CLI/verify handoff
- **不覆盖**：
  - 不重写 `071/137` 已完成的 P1 visual/a11y foundation truth
  - 不重写 `095/143/144` 已完成的 delivery runtime、browser probe、host remediation truth
  - 不在本工单中实现 cross-provider consistency、第二公开 Provider、React exposure 或 provider expansion
  - 不开放自由样式编辑、自由 DOM selector 规则或绕过 `148` theme governance 的质量输入面
  - 不把 Track D/E 伪装成已完成

## 已锁定决策

- `149` 是 `145` 已指定的 Track C child，不重新做 capability census；
- `071/137` 仍然是 visual/a11y foundation 的唯一上游真值来源；Track C 只能在其上增加 richer quality plane，不能改写 foundation 范围；
- `095/143/144` 仍然是 frontend-mainline-delivery、browser probe、host remediation 的执行底座；Track C 复用这些 runtime，不重新发明执行基建；
- `147` 的 `page/ui schema` 与 `148` 的 `theme governance` 必须成为 quality platform 的共享输入锚点，禁止回退到 provider-specific DOM path 或自由主题输入；
- Track C 的完整质量平台至少覆盖 visual regression、完整 a11y、interaction quality 与 multi-browser/multi-device matrix，但 v1 仍要求结构化、可验证、可审计，不允许“凭截图人工判断即可”；
- Track C 必须定义 machine-verifiable 的 quality verdict / evidence / matrix contract，供 Track D `cross-provider consistency` 直接消费；
- `149` 当前只做 docs-only formal freeze，不进入 `src/` / `tests/`，不宣称完整质量平台 runtime 已落地；
- `149` 完成后，下一条前端主线默认进入 Track D，而不是回头重新规划 Track C。

## 用户故事与验收

### US-149-1 — Maintainer 需要一个独立的 Track C baseline

作为**框架维护者**，我希望完整质量平台有独立 child work item，这样我不需要继续把 visual/a11y/interaction/matrix 问题散落到 foundation、browser gate runtime 或后续 provider 工单里。

**优先级说明**：P0。`145` 已明确 Track C 必须是独立 child；如果继续缺位，后续质量/一致性主线仍会持续遗漏。

**独立测试**：只阅读 `149/spec.md`，就能知道 Track C 到底解决什么、依赖什么、当前明确不解决什么。

**验收场景**：

1. **Given** 我审阅 `149/spec.md`，**When** 我检查 scope 与 locked decisions，**Then** 我能明确看到 complete quality platform 与 foundation/runtime 的边界
2. **Given** 我对照 `145`，**When** 我检查 child DAG，**Then** 我能确认 `149` 就是 Track C 的正式承接

### US-149-2 — Quality executor 需要共享 schema/theme truth

作为**质量平台执行者**，我希望完整质量平台直接消费 `147` schema truth 与 `148` theme truth，这样我不需要围绕 provider 私有 DOM、自由主题状态或一次性脚本重新定义质量输入。

**优先级说明**：P0。缺少共享 schema/theme truth，会直接导致 Track C 无法为 Track D 输出可复用 verdict。

**独立测试**：`149` 的实体与 upstream/downstream boundary 表可以直接被 runtime 实现和 Track D 引用。

**验收场景**：

1. **Given** 我准备实现 Track C，**When** 我查看 `149`，**Then** 我能找到必须消费的 schema/theme/runtime truth，而不需要重新推导输入
2. **Given** 我检查 `149` 的 non-goals，**When** 我规划实现切片，**Then** 我不会把 provider expansion 或开放式 style editor 混入当前 child

### US-149-3 — Reviewer 需要 foundation 与完整平台的诚实边界

作为**reviewer**，我希望 `149` 明确说明 `071/137` 已经承接了什么、Track C 还缺什么，这样我可以判断后续实现是不是在重复建设或伪造新缺口。

**优先级说明**：P0。用户已经多次指出“缺口盘点不诚实”；Track C 不能再次把已完成内容算作未做。

**独立测试**：阅读 `149` 后，reviewer 能明确说出 foundation、delivery runtime 与 complete quality platform 的分层关系。

**验收场景**：

1. **Given** 我查看 `149` 的 delivered/deferred boundary，**When** 我核对 `071/137/095/143/144`，**Then** 我看不到这些 work item 被重新包装成当前缺口
2. **Given** 我查看 `149` 的范围，**When** 我检查 complete quality platform 的新增面，**Then** 我能明确看到 visual regression / interaction quality / matrix 等 Track C 独有内容

### US-149-4 — Track D executor 需要可消费的质量 verdict

作为**Track D 承接者**，我希望 Track C 先冻结统一的 quality verdict / evidence handoff，这样 cross-provider consistency 不需要再自己定义“什么叫通过、什么叫差异、什么叫 certification”。

**优先级说明**：P1。Track D 的顺利承接依赖 Track C 先定义统一质量输出。

**独立测试**：`149/plan.md` 可以直接读出 future handoff surface 如何接到 `ProgramService / CLI / verify` 与 Track D。

**验收场景**：

1. **Given** 我审阅 `149/plan.md`，**When** 我检查 future runtime slices，**Then** 我能看到 quality verdict/evidence/matrix handoff 的明确顺序
2. **Given** 我对照 `148`，**When** 我检查 downstream boundary，**Then** 我能确认 Track D 只消费 Track C verdict，而不是重建质量 truth

### 边界情况

- 某些 visual/a11y foundation 已通过，但 richer browser/device matrix 仍可能失败；Track C 需要保留“foundation pass != full platform pass”的分层 verdict
- 同一 page schema 在不同 theme pack、不同浏览器、不同设备密度下可能出现不同质量退化；matrix verdict 必须保留维度信息
- interaction quality 可能因 browser probe 可执行但 evidence 不充分而处于 `advisory`/`needs-recheck`，不能简单折叠成 `pass/fail`
- 如果 theme override 本身违反 `148` 的 governance boundary，Track C 不能静默继续执行质量认证，而应显式依赖上游 blocker
- Track C 在 enterprise/public provider 之外不得擅自扩张到新的 provider roster；否则会提前侵入 Track D/E

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-149-001 | `149` 必须把 Track C 定义为独立的 `quality platform` child baseline，而不是 `071/137` foundation 或 `095/143/144` runtime 的附注 |
| FR-149-002 | `149` 必须明确 Track C 位于 `147` 与 `148` 之后、`Track D` 之前，并继续遵守 `schema -> theme -> quality -> consistency -> provider expansion` 的单一真值顺序 |
| FR-149-003 | `149` 必须明确 `071/137` 已承接 P1 visual/a11y foundation，`095/143/144` 已承接 delivery/browser/host runtime，当前工单不重复这些能力 |
| FR-149-004 | `149` 必须明确当前 work item 的非目标，包括 cross-provider consistency、provider roster expansion、React exposure、开放 style editor runtime 与自由 DOM rule authoring |

### Complete Quality Platform Scope

| ID | 需求 |
|----|------|
| FR-149-005 | `149` 必须明确 Track C 至少承接 `visual regression`、`complete a11y platform`、`interaction quality`、`multi-browser/multi-device matrix` 四类能力 |
| FR-149-006 | `149` 必须明确 `visual regression` 消费 `147` page/ui schema anchor 与 `148` theme governance truth，对关键结构、主题差异、状态反馈与 continuity 进行 richer verdict，而不是只复用 foundation presence check |
| FR-149-007 | `149` 必须明确 `complete a11y platform` 是在 `071/137` foundation 之上的 richer a11y verdict、evidence 与 matrix，不得把 foundation 口径直接当作完整平台 |
| FR-149-008 | `149` 必须明确 `interaction quality` 至少覆盖关键流程的状态稳定性、焦点/输入连续性、反馈时序与 remediation hint，而不是只做静态页面检查 |
| FR-149-009 | `149` 必须明确 `multi-browser/multi-device matrix` 至少包含 browser、viewport/device、theme、page schema 这些维度的组合 truth 与 verdict surfacing |

### Upstream Inputs And Evidence Platform

| ID | 需求 |
|----|------|
| FR-149-010 | `149` 必须明确上游至少依赖 `071/137/095/143/144/147/148`，并说明各自分别提供 foundation、runtime delivery substrate、schema truth 与 theme truth |
| FR-149-011 | `149` 必须明确 Track C 复用 `143` 的真实 browser probe runtime 与 `144` 的 host remediation/workspace integration 底座，而不是重新定义 probe executor |
| FR-149-012 | `149` 必须明确 richer evidence platform 必须是 machine-verifiable 的结构化 evidence，而不是“人工截图判断”或未归档的临时脚本输出 |
| FR-149-013 | `149` 必须明确当上游 schema/theme truth 不完整、provider style support 不可用或 browser runtime 缺失时，Track C 应暴露 blocker/recheck/advisory，而不是静默降级为默认值 |

### Downstream Handoff And Consistency Readiness

| ID | 需求 |
|----|------|
| FR-149-014 | `149` 必须定义 future `quality verdict / evidence / matrix` handoff contract，供 Track D `cross-provider consistency` 直接消费 |
| FR-149-015 | `149` 必须明确 Track D 只消费 Track C 的统一质量输出，不得重新定义 visual/a11y/interaction 通过标准 |
| FR-149-016 | `149` 必须定义 versioned、machine-verifiable 的 future artifact root 与 handoff schema，避免后续 runtime 临时命名或另起目录 |
| FR-149-017 | `149` 必须明确 ProgramService / CLI / verify constraints 未来应如何 surfaced Track C quality truth，而不是让质量平台继续游离在 AI-SDLC 主线之外 |

### Rollout And Verification Honesty

| ID | 需求 |
|----|------|
| FR-149-018 | `149` 必须在 `plan.md` 中给出未来 runtime 推荐切片，至少包括 models、artifact/evidence materialization、validator/matrix、ProgramService/CLI/verify handoff |
| FR-149-019 | `149` 必须清楚区分 docs-only formal freeze、后续 runtime slices 与 truth refresh readiness，不得用“完整质量平台”四个字掩盖尚未实现的事实 |
| FR-149-020 | `149` 当前不得宣称 visual regression/a11y/interaction/matrix runtime 已落地；close 语义只能是“Track C canonical baseline 与 decomposition 已冻结” |

## 关键实体

- **Quality Platform Set**：承载 Track C 顶层 quality truth 的结构化对象，消费 schema/theme/runtime truth 而不复制它们
- **Quality Coverage Matrix**：表达 page schema、theme pack、browser、device/viewport、interaction flow 等维度的质量覆盖组合
- **Quality Verdict Envelope**：表达 visual/a11y/interaction 的 verdict、severity、evidence refs、recheck/advisory 与 blocker 语义
- **Interaction Quality Probe Contract**：表达关键流程的交互质量检查面、状态时序、焦点/输入连续性与 remediation hint 边界
- **Quality Evidence Platform Contract**：表达结构化 screenshots/traces/a11y/interaction evidence 的 artifact root、version 与 payload shape
- **Quality Platform Handoff**：供 Track D、ProgramService、CLI 与 verify 消费的统一 quality surfaced diagnostics

## 推荐的 Track C capability decomposition

| 子域 | 主要职责 | 必须消费的上游 truth | 当前不做 |
|------|----------|----------------------|----------|
| `Visual Regression Layer` | richer visual verdict、continuity、theme-diff surfacing | `071/137`、`147`、`148`、`143` | 不做 provider expansion |
| `Complete A11y Layer` | foundation 之上的 richer a11y verdict、matrix、证据结构 | `071/137`、`147`、`143` | 不重写 foundation |
| `Interaction Quality Layer` | 关键流程的状态时序、焦点/输入连续性、反馈稳定性 | `143/144`、`147`、`148` | 不替代 managed delivery runtime |
| `Browser Device Matrix Layer` | browser/viewport/theme/page schema 组合 verdict | `143`、`147`、`148` | 不直接做 Track D consistency certification |
| `Quality Handoff Layer` | unified verdict/evidence contract for Track D | Track C 前四层输出 | 不扩 provider roster |

## 成功标准

- **SC-149-001**：`149` 能独立表达 Track C 的 scope、non-goals、upstream inputs 与 downstream handoff，而无需重新回到顶层设计临时推断
- **SC-149-002**：`149` 明确隔离 `071/137` foundation、`095/143/144` runtime 底座与 Track C 自身新增质量平台能力，不再误报已完成内容
- **SC-149-003**：`149` 明确要求 Track C 必须消费 `147` schema truth 与 `148` theme truth，不再围绕 provider 私有输入重建质量规则
- **SC-149-004**：`149` 的 `plan.md / tasks.md` 能直接读出后续 runtime 切片与 ProgramService/CLI/verify 接入顺序
- **SC-149-005**：Track D `cross-provider consistency` 能把 `149` 作为统一 quality truth 引用，而不需要重新定义 quality verdict
- **SC-149-006**：`149` formal docs 不再包含模板占位、范围冲突或“foundation/runtime/quality platform”混写的模糊表述

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline/spec.md"
  - "specs/144-frontend-mainline-host-remediation-and-workspace-integration-closure-baseline/spec.md"
  - "specs/147-frontend-p2-page-ui-schema-baseline/spec.md"
  - "specs/148-frontend-p2-multi-theme-token-governance-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
