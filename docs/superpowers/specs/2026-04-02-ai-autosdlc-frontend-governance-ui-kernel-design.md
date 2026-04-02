# Ai_AutoSDLC 前端治理与 UI Kernel 方案（冻结版）

## 1. 文档信息与阅读约定

### 1.1 文档名称

Ai_AutoSDLC 前端治理与 UI Kernel 方案（冻结版）

### 1.2 版本信息

- 版本：V1.0 Frozen
- 状态：冻结版
- 适用阶段：MVP / P1 / P2 统一规划基线

### 1.3 作者 / 评审人

- 作者：SinclairPan
- 评审人：待定

### 1.4 创建日期 / 更新日期

- 创建日期：2026-04-02
- 更新日期：2026-04-02

### 1.5 适用范围

本文档适用于：

- Ai_AutoSDLC 在前端 Web 场景下的治理与扩展设计
- 公司主流 Vue2 企业项目场景
- 现存项目的渐进治理与迁移场景
- 后续 modern provider、多风格与外部系统能力演进的架构基线

### 1.6 术语说明

- **UI Kernel**：前端标准协议层，定义 `Ui*` 语义组件协议、page recipe 标准本体、状态与交互底线。
- **Provider**：运行时适配层，将 UI Kernel 协议映射到具体技术栈与组件实现。
- **enterprise-vue2 provider**：面向公司主流 Vue2 企业项目的运行时适配层。
- **Contract**：前端实现真值载体，用于承载页面级或模块级结构化约束。
- **recipe declaration**：页面级或模块级对某个 page recipe 的实例化声明。
- **page recipe 标准本体**：由 UI Kernel 定义的页面骨架标准，如 `ListPage / FormPage / DetailPage`。
- **Legacy Boundary**：当前版本中允许存续的历史实现边界。
- **Compatibility Profile**：页面或模块当前所处的兼容档位。
- **Migration Level**：页面或模块当前所处的迁移级别。
- **Migration Scope**：本次变更所涉及的迁移范围。
- **Legacy Adapter**：对老旧组件的受控桥接层。
- **同一套 gate matrix 的兼容执行口径**：不引入第二套 gate 体系，而是根据 `Compatibility Profile / Migration Level / Migration Scope / changed_scope` 调整执行强度的执行层口径。
- **Whitelist**：允许 AI 默认使用的受控 `Ui*` 组件入口集合。
- **Hard Rules**：前端生成中不可突破或仅允许极少数受控例外的硬性规则。
- **Token Rules / Naked-value Rules**：对颜色、阴影、间距等视觉值的最小受控规则。
- **Violation Report**：结构化违规报告。
- **Coverage Report**：结构化覆盖情况报告。
- **Drift Report**：实现与 Contract 漂移报告。
- **Fix Input**：供 Auto-fix 消费的结构化修复输入。
- **Recheck**：用于发现漏项、漂移和修复后偏差的复查机制。
- **Auto-fix**：基于结构化报告进行定向修复的自动修复机制。

### 1.7 核心章节统一写法

本方案中的核心设计章节优先从以下五个视角展开，不强制固定小节名，但后续编排应尽量覆盖这些视角：

- 终局设计
- MVP 边界
- P1 / P2 演进方向
- 工程接入点
- 风险与约束

---

## 2. 执行摘要与关键决策

### 2.1 一句话结论

Ai_AutoSDLC 当前已具备成熟的 stage / gate / artifact 驱动骨架，但尚缺前端标准层与治理闭环。本方案通过引入 **Contract、UI Kernel、enterprise-vue2 provider、前端生成约束体系、Gate / Recheck / Auto-fix**，将前端生成从“自由生成、人工兜底”升级为“输入可约束、生成可收口、结果可检查、问题可回修”的工程型能力。

同时必须明确：

> **Ai_AutoSDLC Core 负责 contract / rule / gate / recheck 机制，provider wrapper 与前端运行时代码落在目标业务前端项目或独立适配包中，而不是把本仓库改造成前端组件运行时仓库。**

### 2.2 核心架构决策

#### 2.2.1 UI Kernel != 公司组件库

本方案中的 UI Kernel 是标准协议层，用于定义：

- `Ui*` 语义组件协议
- page recipe 标准本体
- 状态、交互和最小可访问性底线

UI Kernel 不等于任何现有组件库，也不直接承载运行时代码。

#### 2.2.2 公司组件库 = enterprise-vue2 provider 的能力来源

公司组件库可作为 `enterprise-vue2 provider` 的能力来源，但只能以**白名单核心组件的选择性包装**方式接入。

明确决策：

- 是否允许全量 `Vue.use` 公司组件库：**否**
- Provider 是否只包装白名单核心组件：**是**
- page recipe 是否归 UI Kernel：**是**
- Provider 是否可以直接复用旧 page 级骨架作为标准：**否**

也就是说：

- Provider 可以提炼企业页面模式
- 但 **page recipe 由 UI Kernel 定义**
- Provider 只负责把 recipe 映射到企业实现
- 不直接复用旧 page 骨架作为标准

#### 2.2.3 MVP 先治理闭环，不做终局全量能力

MVP 阶段优先聚焦：

- i18n contract 与漏项治理
- form validation contract 与覆盖治理
- Vue2 hard rules 治理
- 最小 recipe / whitelist / token rules
- enterprise-vue2 provider
- 最小 gate / recheck / auto-fix 闭环

同时明确：

- MVP 规则主要约束 AI 新生成页面代码、Kernel wrapper、Provider adapter 与相关模板/检查链路
- **不追溯治理公司组件库内部历史源码**

#### 2.2.4 不另起独立前端 pipeline

本方案所有前端治理能力均以接入现有 Ai_AutoSDLC `refine / design / decompose / verify / execute / close` 骨架为前提，不新增一套平行的前端交付系统。

### 2.3 关键决策表

| 决策项                                   | 结论        |
| ------------------------------------- | --------- |
| Ai_AutoSDLC Core 是否做前端 runtime 仓库     | 否         |
| 公司组件库是否直接作为 UI Kernel                 | 否         |
| enterprise-vue2 provider 是否采用白名单选择性包装 | 是         |
| 是否允许全量注册公司组件库                         | 否         |
| 是否直接复用公司 Page 级骨架作为标准 recipe          | 否         |
| MVP 规则是否追溯治理公司组件库内部源码                 | 否         |
| 是否另起独立前端 pipeline                     | 否         |
| recipe 标准本体归属                         | UI Kernel |
| recipe declaration 归属                 | Contract  |
| Compatibility 是否是一套新 gate 体系          | 否         |

### 2.4 MVP / P1 / P2 总览

#### 2.4.1 MVP

- 建立最小 Contract 体系
- 建立最小 UI Kernel 协议
- 落地 `enterprise-vue2 provider`
- 建立最小 recipe / whitelist / hard rules / token rules
- 建立最小 Gate / Recheck / Auto-fix 闭环
- 支撑现存项目最小兼容策略

#### 2.4.2 P1

- 扩展 `Ui*` 语义组件集
- 扩展 page recipe 标准本体
- 增强 whitelist / token / 状态覆盖
- 增强 drift 检查、recheck、visual / a11y 初步能力
- 从“正确性止血”走向“体验稳定”

#### 2.4.3 P2

- 引入 `modern provider`
- 支撑多 theme pack / 多风格
- 增强 visual / interaction quality gate
- 面向外部系统输出更现代的前端体验

### 2.5 本文档要解决的问题与不解决的问题

#### 要解决的问题

- 前端 AI coding 的高频失控点如何工程化治理
- 如何在不重构公司组件库的前提下支撑企业 Vue2 项目
- 如何让现存项目中的新增与改动进入新治理链
- 如何保证 UI Kernel、Provider、Contract、Gate 闭环不互相冲突

#### 不解决的问题

- 不在首版重构公司组件库
- 不在首版完成全部存量页面迁移
- 不将 Ai_AutoSDLC Core 演进为前端 runtime monorepo
- 不以 prompt 优化作为主解法

---

## 3. 现状、证据与现实约束

### 3.1 Ai_AutoSDLC 当前机制现状

#### 3.1.1 当前框架的能力重心

Ai_AutoSDLC 当前已经具备较成熟的 **stage / gate / spec / artifact** 驱动能力，其核心价值不在于充当前端运行时仓库，而在于：

- 通过阶段化流程约束研发行为
- 通过 spec / plan / tasks 等结构化产物承载设计与执行上下文
- 通过 gate / verify / quality artifacts 对结果进行校验与闭环
- 通过 artifact 驱动，将“需求、设计、拆解、执行、验证、收口”串成统一流程

结合当前项目现状，Ai_AutoSDLC 更接近一个 **工程治理与交付编排框架**，而不是一个前端组件平台或前端运行时仓库。

因此，前端能力建设必须服从这一现实定位：

> **Ai_AutoSDLC 的职责是定义机制、协议、规则、检查和回修闭环，而不是直接承载前端运行时代码体系。**

#### 3.1.2 当前已有机制对前端治理的可复用基础

从整体架构看，Ai_AutoSDLC 已经具备承接前端治理的若干基础条件：

- 有阶段化入口：
  - `refine`
  - `design`
  - `decompose`
  - `execute / verify`
  - `close / report`
- 有 gate 思维与校验入口：
  前端规则并不需要额外发明一套全新机制，而可以进入现有的：
  - `verify`
  - `quality gate`
  - `violation report`
  - `fix loop`
- 有 artifact 驱动基础：
  前端治理最需要的是将模糊自然语言输入转成结构化产物，而当前框架已有较强的 artifact 思维，这使得：
  - `i18n contract`
  - `validation contract`
  - `frontend hard rules`
  - `recipe metadata`

  这些前端治理对象具备天然落位空间。
- 有 `spec / plan / tasks` 的传递链路：
  前端治理不是“写几个 lint 规则”这么简单，而是可以被纳入：
  - 需求输入
  - 设计展开
  - 任务拆解
  - 开发执行
  - 验证回收

  这一整条链路中。

因此，前端治理在 Ai_AutoSDLC 中的引入方式，是**接入现有 stage / gate / artifact 机制**，新增前端专属的 Contract、Checker、Gate 与 Fix Loop，而**不是另起一套独立于现有 refine / design / decompose / verify / execute 之外的新前端流水线**。

#### 3.1.3 当前缺失的关键能力

虽然 Ai_AutoSDLC 已有成熟的工程治理基础，但在前端方向上存在明确空白：

1. 缺少前端内核层
2. 缺少前端合同化输入层
3. 缺少前端专属 gate 闭环
4. 缺少 provider 隔离层

#### 3.1.4 现状结论

Ai_AutoSDLC 当前**不缺工程治理骨架**，缺的是前端方向上的：

- 协议层
- 合同层
- Provider 层
- 规则链
- Gate 链

因此，本方案不是要另起一套前端框架，而是要在现有 stage/gate/artifact 机制之上，补齐前端治理与 UI Kernel 这一层能力。

### 3.2 前端 AI coding 的真实失控点

#### 3.2.1 国际化定义缺失与回检缺失

当前最典型的问题之一，是 AI 在实现页面国际化时会出现：

- 使用了新的国际化 key，但未同步定义
- 局部替换为 i18n 写法，但遗漏部分用户可见文案
- 初次实现后不主动 recheck，导致最终仍残留漏项
- 对已有 key 的复用能力不足，导致命名混乱或重复定义

这类问题的根因不是“AI 不知道要国际化”，而是：

- 国际化尚未被建模为独立 Contract
- 页面开发流程中缺少 i18n 先行或同步生成步骤
- 生成后缺少 missing key / naked text 的自动检查
- 缺少将 i18n 结果回灌修复的闭环

#### 3.2.2 表单校验依赖自然语言描述，缺少机器可消费规则

第二类高频问题，是表单校验实现不完整、不一致或不稳定，典型表现包括：

- 必填规则遗漏
- 长度限制遗漏
- 类型约束不完整
- 联动校验缺失
- 错误提示语不统一
- 校验触发时机不一致
- 前后端校验含义不一致

这说明当前问题的核心不在“有没有校验组件或 skill”，而在于：

> **产品与设计输入没有将校验规则结构化成 AI 可稳定消费的合同。**

#### 3.2.3 长上下文下突破 Vue2 编码规范

第三类问题，是 AI 在长上下文开发过程中，逐渐偏离项目约束，出现“明知不应如此但仍然这样写”的现象。已暴露的典型例子包括：

- 在不应使用的场景下对 props 使用 `v-model`
- 直接修改 props
- 绕过既定组件协议直接写低层实现
- 忽略既有 Vue2 通信模式
- 在上下文变长后不再严格遵守已声明规则

#### 3.2.4 页面结构与体验层失控

除上述三类强约束问题外，还存在一个更广泛的结果层问题：

> **前端代码逻辑可用，但页面结构、组件使用和体验表现不可交付。**

#### 3.2.5 失控点的共性结论

上述问题虽然表面不同，但共性高度一致：

- 输入不够结构化
- 规则不够硬
- 缺少回检
- 缺少定向修复回路

### 3.3 公司组件库评估结论

#### 3.3.1 评估目标

本节不讨论“公司组件库好不好”，而回答一个更具体的问题：

> **在 Ai_AutoSDLC 前端治理与 UI Kernel 方案中，公司组件库应扮演什么角色。**

#### 3.3.2 组件能力与企业场景承载力：强

从当前已评估的目录结构、README、包定义和组件 API 文档可见，公司组件库覆盖了较完整的企业后台组件盘子，包括：

- Button / Input / Select / Checkbox / Radio / Switch
- Form / Grid / Grid-form
- Drawer / Window / Layer / Popover
- Date-picker / Upload / Tree / Tree-select / Cascader
- Empty / Loading / Progress / Tag / Badge / Card
- Menu / Nav-menu / Toolbar / Search / Layout

其中，Form、Grid、Select 等核心组件具备较强的企业业务承载能力，而非轻量展示型组件。

**结论：从企业项目运行时承载角度看，这套组件库具备较高利用价值。**

#### 3.3.3 工程化基础：具备正式组件库形态

从包定义、README 和目录组织方式可见，该组件库具备正式组件库的基本形态，包括：

- 明确的 npm 包信息与版本管理
- 类型声明与编辑器提示支持
- 全量注册与按需加载说明
- 样式、主题与全局配置接入说明
- demo、docs、tests 等工程化痕迹

这说明它不是零散的页面代码集合，而是一套正式维护的企业组件资产。

#### 3.3.4 不适合作为统一 UI Kernel 的现实原因

虽然公司组件库有较强的运行时能力，但并不适合作为 Ai_AutoSDLC 的统一 UI Kernel，原因主要有四类：

1. 内部依赖与生态耦合较重
2. 存在全局安装与副作用模式
   组件库的典型接入方式包含全量 `Vue.use(...)`、全局配置更新、全量样式引入，以及对全局 i18n、全局配置等运行时前提的依赖。这类模式适合人工主导的企业项目接入，不适合直接作为 AI 生成目标接口。

**一旦以全量 `Vue.use` 方式接入，公司组件库的全局配置、副作用插件、历史兼容扩展点和宽 API 面也会一并进入 AI 生成链路，显著扩大失控面。**

3. 历史技术债与旧能力混杂
4. 页面级骨架不应上升为标准

#### 3.3.5 定位结论

基于以上证据，本方案对公司组件库的定位结论是：

1. 适合作为 `enterprise-vue2 provider` 的底层能力来源
2. 不适合作为统一 UI Kernel
3. 不应直接暴露给 AI 作为生成目标接口
4. 不应通过全量 `Vue.use` 方式接入为 provider
5. 不应复用其旧 page 级骨架作为标准 recipe
6. MVP 通过白名单包装与危险能力隔离来利用其价值，而非追溯治理其内部源码

### 3.4 现实约束与关键假设

#### 3.4.1 现实约束

本方案需同时接受以下现实约束：

1. 公司主流项目仍以 Vue2 为主
2. 公司组件库有现实价值，但带明显历史包袱
3. Ai_AutoSDLC 当前是治理框架，不是前端运行时仓库
4. 前端 AI coding 的问题已具备高频和重复性
5. 首版范围必须可执行

#### 3.4.2 关键假设

本方案建立在以下关键假设之上：

1. 业务侧可接受产品/设计输入更结构化
2. 团队可接受 AI 生成自由度被收紧
3. 可在现有项目流程中接入新的 Contract 与 Gate
4. 首版可接受“先稳定、后美化”的阶段策略
5. 可在目标业务前端项目或独立适配包中承载 provider wrapper 与 kernel wrapper 的运行时实现

### 3.5 为什么不能只做 prompt 修补

#### 3.5.1 prompt 修补的作用边界

prompt、规则文档、review checklist 不是没有价值，但其边界很明显：

- 无法保证执行
- 无法保证长上下文下持续遵守
- 无法自动发现漏项
- 无法形成稳定的工程闭环
- 无法替代结构化输入与自动检查

#### 3.5.2 当前问题已经超出 prompt 可解决范围

当前已暴露的问题有一个共同特点：

> **它们不是“模型一时忘记”，而是“系统没有把约束做成工程机制”。**

#### 3.5.3 必须升级为合同化治理 + gate 化治理

因此，本方案不将 prompt 作为主解法，而将其降级为辅助工具。主解法必须是：

- 用 Contract 约束输入
- 用 whitelist / recipe / hard rules 约束生成
- 用 gate / lint / AST / recheck 检测问题
- 用 auto-fix / review 闭环修复问题

### 3.6 本章结论

基于当前项目与组件库的真实情况，可以明确得出以下结论：

1. Ai_AutoSDLC 当前具备成熟的 stage/gate/artifact 基础，但缺少前端内核层、前端合同层、Provider 层与前端专属治理闭环。
2. 前端 AI coding 的主要问题已经高度重复和机制化，不能继续通过 prompt 补丁和人工兜底解决。
3. 公司组件库具备较强的 Vue2 企业运行时承载力，适合作为 `enterprise-vue2 provider` 的能力来源。
4. 公司组件库不适合作为统一 UI Kernel，也不应被全量注册、全量透出或直接复用其 page 级骨架作为标准。
5. MVP 需要在现有 stage/gate/spec 体系之上，补齐 Contract、Kernel、Provider、Gate 与 Fix Loop，而不是重建一套独立前端平台。
6. 前端治理的正确方向不是 prompt 增量修补，而是合同化治理与 gate 化治理。

---

## 4. 目标、非目标与成功口径

### 4.1 章节目标

本章用于明确本方案要达成什么、不打算在本阶段解决什么，以及如何判断方案是否朝着正确方向落地。

### 4.2 总体目标

本节所述总体目标面向方案终局能力定义，用于明确本方案希望建立的完整前端治理与 UI Kernel 能力边界；具体落地范围按 MVP、P1、P2 分阶段收敛，不以首版一次性全部实现为目标。

#### 4.2.1 建立可控的前端生成主链路

本方案的第一目标，是让 Ai_AutoSDLC 在前端场景中的生成链路从“自由生成、人工兜底”升级为“输入可约束、生成可收口、结果可检查、问题可回修”的工程型能力。

#### 4.2.2 建立独立的 UI Kernel 标准层

本方案的第二目标，是在 Ai_AutoSDLC 中建立独立的 UI Kernel 标准层，用统一语义组件协议、页面骨架协议和最小交互约束，替代当前“直接面向底层组件库或原生结构生成”的状态。

#### 4.2.3 建立面向公司主流 Vue2 项目的企业实现层

本方案的第三目标，是在不重构公司组件库、不推翻现有项目现实的前提下，建立 `enterprise-vue2 provider`，使公司组件库成为受控能力来源，而不是 AI 的直接生成目标接口。

#### 4.2.4 建立前端治理闭环

本方案的第四目标，是把当前最典型的前端 AI coding 失控点纳入治理闭环，包括：

- 国际化定义与回检缺失
- 表单校验规则模糊与漏实现
- 长上下文下突破 Vue2 编码规范
- 页面结构、组件使用和样式表达失控

#### 4.2.5 为后续多 Provider、多风格与外部系统能力预留演进路径

本方案的第五目标，不是在首版一次性完成 modern provider 和现代设计系统，而是在 MVP 阶段就把抽象边界设计正确，使后续能够在不推翻首版方案的情况下，逐步扩展：

- `modern provider`
- 多 theme pack
- 多风格输出
- 面向外部系统的现代化前端生成能力

#### 4.2.6 支撑现存项目的渐进治理与迁移

本方案不仅面向全新页面生成，也必须支撑现存项目中的增量开发与局部改造。因此，本方案的一个重要目标是：

> **对现存项目采取“存量兼容、增量收口、边界隔离、渐进迁移”的治理策略：历史代码与老旧组件允许在 Legacy Boundary 内存续，但所有新增与改动必须通过 Contract、UI Kernel、Provider Adapter 与分级 Gate 进入新治理体系。**

这意味着：

- 历史页面与老旧组件允许在受控边界内暂时存续
- 所有新增页面、改动区域和新增能力必须进入新治理链路
- 对已不维护或高风险的历史组件，通过 Legacy Adapter 和 Compatibility Profile 进行隔离与过渡
- 迁移应以业务改动为触发器，按变更范围逐步推进，而不是以全量重构为前提

### 4.3 阶段性目标

#### 4.3.1 MVP 目标

MVP 的目标不是建设完整前端平台，而是优先解决当前公司主流 Vue2 企业项目中的高频失控问题，让前端生成先稳下来。

MVP 需要达到的状态是：

- AI 生成前端代码时不再直接面向底层 `Sf*` 组件或原生自由拼装
- i18n、表单校验、Vue2 硬规则进入结构化治理链路
- 生成结果具备最小的 page recipe、组件白名单与 token 护栏
- `enterprise-vue2 provider` 能作为企业项目的受控运行时适配层
- gate、recheck 和 auto-fix 能对典型漏项与违规项形成基本闭环

同时，MVP 还需建立现存项目兼容策略的最小闭环，包括：

- 对现存项目采用分级治理模式，而不是一刀切重构
- 对老页面的改动按“变更范围治理”处理
- 对老旧组件建立 Legacy Boundary 与兼容执行口径
- 对已不维护组件通过 Legacy Adapter 做受控接入
- 明确“新增代码必须符合新体系，存量代码逐步收口”的基本原则

并明确：

> **MVP 的治理对象主要覆盖 AI 新生成页面代码、UI Kernel wrapper、Provider adapter，以及相关模板与检查链路；不将公司组件库内部历史源码治理纳入首版正式交付目标。**

#### 4.3.2 P1 目标

P1 的目标是在 MVP 闭环成立后，进一步提升页面结构稳定性、组件使用一致性和基础体验质量。

#### 4.3.3 P2 目标

P2 的目标是在已有治理闭环和 Kernel / Provider 边界稳定的基础上，支撑面向外部系统的现代风格输出和多 Provider 演进。

### 4.4 非目标

#### 4.4.1 不在首版直接建设完整现代设计系统

本方案不以 MVP 为目标去完成 modern provider 全量能力、多主题完整平台、Apple/macOS-like 风格正式运行时实现或高保真现代视觉系统。这些能力属于后续阶段演进内容，不进入首版正式交付承诺。

#### 4.4.2 不直接重构公司组件库

本方案不把“重构公司组件库”作为首版目标，不承担公司组件库内部历史源码治理、`jQuery / widget` 体系改造、内部依赖剥离、历史 API 清理或旧页面级骨架重写。首版只解决如何通过 Provider 层受控利用这些能力。

#### 4.4.3 不将 Ai_AutoSDLC Core 演进为前端运行时仓库

本方案不在 Ai_AutoSDLC Core 中直接建设业务前端运行时代码、项目实际可渲染组件实现、企业 Provider 运行时代码主体或页面级 Vue 组件库。Core 的职责是机制、协议、规则与治理闭环，而不是前端 runtime monorepo。

#### 4.4.4 不把 prompt 优化作为主解法

本方案不把“补 prompt”“补规则文档”“补 review checklist”定义为核心解决路径。这些手段可以作为辅助，但主解法必须是 Contract 化输入、规则工程化、Checker / Gate 化，以及 Recheck / Auto-fix 闭环。

#### 4.4.5 不以首版替代人工视觉设计与复杂交互设计

本方案首版目标是“稳定、可控、可维护”，而不是直接替代设计师完成复杂品牌视觉、复杂动效系统或高保真交互体验设计。首版不会承诺自动产出品牌级现代视觉方案，也不承诺自动达到成熟设计系统的完整度。

#### 4.4.6 不把历史前端代码全面纳入治理首版范围

首版的治理对象主要是：

- AI 新生成页面代码
- UI Kernel wrapper
- Provider adapter
- 模板与检查链路相关产物

#### 4.4.7 不另起独立前端交付流水线

本方案不新增一套独立于 Ai_AutoSDLC 现有 `refine / design / decompose / verify / execute / close` 之外的前端流水线。前端治理以接入现有 stage / gate / artifact 骨架为前提，通过新增前端专属 Contract、Checker、Gate 与 Fix Loop 完成增强，而不是平行建设另一套前端交付系统。

#### 4.4.8 不以首版完成存量项目全面治理

本方案不承诺在 MVP 阶段完成：

- 全量存量页面迁移到 UI Kernel
- 全量历史组件替换
- 全量 legacy page 骨架清理
- 对所有既有前端代码统一应用严格 gate 阻断

首版只要求：

- 为存量项目建立兼容与迁移机制
- 对新增和改动区域实施新治理体系
- 对历史高风险能力设置边界与扩散限制

### 4.5 成功口径

#### 4.5.1 成功不是“做了很多前端抽象”，而是“形成稳定控制面”

本方案是否成功，首先不取决于写了多少 wrapper、多少规则文件或多少 schema，而取决于是否真的形成了稳定控制面。成功的标志是：AI 的生成目标被 UI Kernel 与 Contract 收口，关键违规可以被 Gate 拦截，漏项可以被 Recheck 发现，修复可以进入结构化回路，人工 review 从主控制手段退回为最后兜底。

#### 4.5.2 成功不是“接通公司组件库”，而是“把公司组件库纳入受控利用”

本方案是否成功，不取决于公司组件库是否被“接进来了”，而取决于它是否被正确地放在 Provider 层，并被白名单包装和危险能力隔离。成功的标志是：公司组件库作为 `enterprise-vue2 provider` 的能力来源被利用，AI 不直接生成 `Sf*` 组件代码，也不通过全量 `Vue.use` 方式把宽 API 面直接暴露给 AI 链路。

#### 4.5.3 成功不是“首版就很美”，而是“首版先稳”

MVP 阶段的成功口径，不是页面已经具备现代高保真风格，而是高概率避免明显不可用结果，高概率减少漏定义、漏校验和硬规则违规，高概率让页面结构和组件使用进入最小可控范围，并显著降低人工返修密度。

#### 4.5.4 成功不是“首版做得很多”，而是“每阶段都能继承前一阶段成果”

本方案是否成功，还取决于阶段演进是否连续。成功的标志是：MVP 的 Contract、Kernel、Provider、Gate 边界可以直接被 P1 / P2 继承，P1 / P2 是在同一架构上增强，而不是另起一套体系；enterprise-vue2 provider 不会把后续 modern provider 路线堵死，最小 token / recipe / whitelist 也不会在后续演进时被整体推翻。

#### 4.5.5 成功还取决于工程落位是否正确

本方案是否成功，不仅取决于规则、wrapper 和 gate 是否存在，还取决于这些能力是否按既定边界落位：

- Core 是否仍然聚焦机制、协议和治理闭环
- Provider 是否仍然是受控适配层而非全量透传层
- 业务项目是否通过 Wrapper / Adapter 消费受控能力
- Contract、Rule、Gate、Violation、Fix Artifact 是否真正进入 artifact 链路

#### 4.5.6 成功还取决于存量项目能否在不失控的前提下渐进迁移

本方案是否成功，还取决于它能否在现存项目中以可执行的方式落地，而不是只适用于全新项目。

成功的标志包括：

- 现存项目中的新增与改动区域能够进入新治理体系
- 老旧组件不会继续无边界扩散
- 历史页面不需要整页重构才能承接新需求
- 兼容执行口径与分级 Gate 能在真实项目中跑通
- MVP 结束后，项目整体技术状态开始“停止继续变坏”

#### 4.5.7 成功口径与验收标准的关系

本章定义的是“成功应长什么样”，重点是方向、边界和判断标准。

### 4.6 本章结论

本章确认了以下目标边界：

1. 本方案的总体目标，是在 Ai_AutoSDLC 中建立前端治理闭环与 UI Kernel 标准层，使前端生成从自由生成升级为可控生成。
2. MVP 优先服务公司主流 Vue2 企业项目，重点解决 i18n、表单校验、Vue2 规范和页面结构失控等高频问题。
3. P1 在 MVP 基础上补齐体验稳定层，P2 再正式扩展到 modern provider、多风格和外部系统能力。
4. 本方案不以首版重构公司组件库、不将 Core 演进为 runtime 仓库、不以 prompt 优化作为主解法。
5. 本方案的成功，不以抽象数量、接入深度或视觉完成度为第一标准，而以控制面是否建立、闭环是否成立、阶段能力是否可继承为核心判断依据。

以上目标、非目标与成功口径，将作为后续“设计原则”“工程落位边界与职责划分”“总体架构设计”等章节的判断基线；凡与本章边界冲突的实现方案，均不视为本方案的有效落地路径。

---

## 5. 设计原则

### 5.1 章节目标

本章用于定义本方案后续所有设计与实现的共同行为准则，用来回答两个问题：

1. 在存在多种可选实现路径时，优先按什么原则做取舍
2. 如何判断某个局部方案虽然“能做”，但是否违背了本方案的整体方向

### 5.2 终局先行，阶段落地

#### 5.2.1 原则定义

本方案采用：

> **终局架构先定义，阶段能力分步落地。**

#### 5.2.2 采用该原则的原因

如果只围绕 MVP 做局部设计，容易出现两类问题：为了快速落地而直接绑定当前组件库、当前项目结构和当前页面写法，导致 Kernel 抽象不成立、Provider 边界消失；或者阶段之间断层，MVP、P1、P2 彼此割裂，后续每次升级都像重新做一版方案。

#### 5.2.3 设计含义

该原则意味着总体目标可以大于首版范围，首版可以收敛，但不能牺牲关键边界；任何 MVP 取舍都不能以破坏后续演进为代价，后续阶段也不得推翻前一阶段已建立的核心抽象。

### 5.3 Kernel 与 Provider 分离

#### 5.3.1 原则定义

本方案坚持：

> **UI Kernel 定义标准协议，Provider 承担运行时实现。**

#### 5.3.2 采用该原则的原因

如果不做 Kernel 与 Provider 分离，AI 会直接面向底层组件库生成，导致 API 面过宽、历史包袱直接暴露、风险能力不可隔离、规则无法收口。同时，当前企业实现也会绑死未来演进，modern provider 无法平滑接入，外部系统风格能力会被企业组件风格绑定。

#### 5.3.3 设计含义

该原则要求 AI 不直接生成 `Sf*` 组件代码，UI Kernel 必须独立定义 `Ui*` 语义组件和页面协议；Provider 只能做选择性包装，不能退化为透传层；Provider 可以替换，但 Kernel 协议必须保持稳定，page recipe 也必须归 Kernel，而不归 Provider。

### 5.4 合同化优先于自由生成

#### 5.4.1 原则定义

本方案坚持：

> **关键前端输入必须先合同化，再进入代码生成。**

#### 5.4.2 采用该原则的原因

当前真实问题已经证明，纯自然语言输入会导致 i18n key 漏定义、表单校验规则不完整、联动逻辑漏实现、Vue2 规则在长上下文中被突破，以及页面结构随意漂移。这些问题不是“模型不会写”，而是“输入不够结构化”。

#### 5.4.3 设计含义

该原则意味着：

- PRD / Spec 必须补足前端结构化输入要求
- 页面生成前，应先完成 Contract 实例化
- Gate 检查应以 Contract 为依据，而不是只看 prompt
- Fix Loop 的输入也必须基于结构化 violation / Contract 差异生成

> **Contract 不是补充性文档，而必须成为可生成、可校验、可回修的实例化 artifact，并进入现有 Ai_AutoSDLC 的 artifact 流转链路，被生成、检查与修复阶段共同消费。**

### 5.5 正确性优先，体验渐进增强

#### 5.5.1 原则定义

本方案坚持：

> **先解决正确性失控，再逐步提升体验质量。**

#### 5.5.2 采用该原则的原因

当前最急的问题不是“页面不够美”，而是漏项多、违规多、人工返修密度高、页面虽能跑但交付可信度低。如果首版一开始就把重点放在高级视觉系统、完整多主题、复杂动效或 modern provider 上，会稀释最急迫的治理价值，导致首版既不稳也不快。

#### 5.5.3 设计含义

该原则意味着 MVP 先追求“稳”，而不是“很美”；MVP 可以先上最小 recipe / whitelist / token 护栏，P1 再强化体验一致性，P2 再扩展 modern provider 与多风格输出。任何体验增强都不应破坏前面已建立的正确性控制面。

### 5.6 规则必须可执行、可检测、可回修

#### 5.6.1 原则定义

本方案坚持：

> **规则如果不能进入工程执行链，就不算真正成立。**

#### 5.6.2 采用该原则的原因

当前长上下文下突破规范、漏 i18n、漏校验等问题，已经说明规则其实存在，但规则不可执行。只要规则不可执行，AI 就会在复杂上下文里为了局部完成度而突破边界。

#### 5.6.3 设计含义

该原则意味着：

- 重要规则必须被机器可消费
- Gate 不通过时，必须有标准化输出
- Recheck 必须可定位到具体漏项或违规项
- Fix 不应依赖“整页重写”，而应支持定向修复
- 人工 review 是最后兜底，而不是主控制手段

> **规则不仅要能被检测，还必须产出机器可消费的 Violation Report、Fix Input 或等价的结构化结果，否则只能完成发现问题，无法进入标准化回修链路。**

### 5.7 阶段能力必须可继承、可扩展、可替换

#### 5.7.1 原则定义

本方案坚持：

> **每一阶段交付的能力，都必须能被下一阶段继承，而不是被推倒重来。**

#### 5.7.2 采用该原则的原因

如果首版为了快而做成大量临时方案，后续很容易出现：MVP 用 prompt 补丁，P1 再重做 Contract；MVP 直接接公司组件库，P2 再强拆 Kernel；MVP 用页面写法约束，P1 再补 recipe 体系。短期看似跑得快，长期一定带来返工。

#### 5.7.3 设计含义

该原则意味着 MVP 的最小 Contract 必须可扩展，最小 recipe 不应与企业旧骨架绑死，enterprise-vue2 provider 不得堵死 modern provider 路线，token 最小规则要能平滑演进到完整 token 体系，Gate 体系也应从最小矩阵逐步扩展，而不是推翻替换。

### 5.8 增强现有骨架，不另起平行体系

#### 5.8.1 原则定义

本方案坚持：

> **所有前端治理能力，均以接入现有 Ai_AutoSDLC stage / gate / artifact 骨架为前提，不新增一套平行的前端交付系统。**

#### 5.8.2 采用该原则的原因

如果另起一条前端平行体系，会立刻带来流程重复、产物重复、阶段边界冲突、实施成本上升，以及与现有 `spec / plan / tasks / verify / close` 关系混乱。这会削弱 Ai_AutoSDLC 现有 stage / gate / artifact 机制的统一性，也使前端治理难以真正进入主链路。

#### 5.8.3 设计含义

该原则意味着前端治理只做“接入与增强”，不做“平行替代”；前端 Contract 必须进入现有 artifact 链路，前端检查必须进入现有 Gate / Verify 体系，前端 Recheck / Fix Loop 也必须挂接现有闭环，而不是单独存在。

### 5.9 工程落位必须稳定，职责不能漂移

#### 5.9.1 原则定义

本方案坚持：

> **机制层、规则层、适配层、业务运行层必须职责清楚，不能互相吞并。**

#### 5.9.2 采用该原则的原因

如果工程落位不稳，会出现三类典型问题：Core 仓库职责漂移，最终变成半个前端 runtime 仓库；Provider 从选择性包装退化成公司组件库全量透传；业务项目绕过受控入口，直接引用底层组件库，导致白名单、隔离和 recipe 失效。

#### 5.9.3 设计含义

该原则意味着 Ai_AutoSDLC Core 不承载前端运行时代码主体，Provider wrapper / Kernel wrapper 应落在目标业务项目或独立适配包中，业务项目不得绕过 wrapper 直接把公司组件库作为默认入口，检查执行则面向目标项目源码、构建产物和实例化 artifact 进行。

### 5.10 先闭环、后抽象

#### 5.10.1 原则定义

本方案坚持：

> **先在真实项目中形成闭环，再决定是否上升为更高层级抽象。**

#### 5.10.2 采用该原则的原因

如果过早抽象，容易出现“抽象层很多，但真实项目不稳定”“独立包很多，但复用价值尚未被验证”“接口设计过大，首版实现成本失控”“后续又被迫回退到项目内实现”等问题。

#### 5.10.3 设计含义

- MVP 优先在业务项目内落适配层闭环
- **Provider / Wrapper 是否上升为独立适配包，应以 2 个及以上项目验证复用稳定为前提，而不是基于预期复用提前抽象。**
- 首版只抽象真正共性的 Contract / Kernel / Gate 机制
- 不为了“看起来架构完整”而提前拆过多运行时层

### 5.11 存量兼容、增量收口、边界隔离、渐进迁移

#### 5.11.1 原则定义

本方案坚持：

> **对现存项目采取“存量兼容、增量收口、边界隔离、渐进迁移”的治理策略。**

即：

- 历史实现允许在 Legacy Boundary 内存续
- 所有新增与改动必须进入新治理体系
- 老旧组件通过 Legacy Adapter 和 Compatibility Profile 进行过渡
- 迁移应围绕真实业务变更逐步推进，而不是以全量重构为前提

#### 5.11.2 采用该原则的原因

在真实项目中，前端框架面临的不是纯净新项目，而是大量已有页面、大量老旧代码、已不维护但仍被依赖的组件，以及高风险但短期无法替换的历史实现。如果忽略这些现实，方案将只能停留在理想新项目场景中。

#### 5.11.3 设计含义

该原则意味着：

- 不对存量代码做一刀切治理
- 新增代码按新规则，存量代码按风险分级逐步收口
- Legacy Boundary 必须明确
- Legacy Adapter 必须作为 Provider 设计的一部分
- Gate 必须支持**同一套 gate matrix 的兼容执行口径**
- 迁移优先级应围绕高频改动区、高风险区与高收益区展开

### 5.12 不以局部最优破坏整体边界

#### 5.12.1 原则定义

本方案坚持：

> **局部实现即使更快、更省事，也不能以破坏整体边界为代价。**

#### 5.12.2 采用该原则的原因

为了快而直接让 AI 生成 `Sf*`、全量 `Vue.use` 公司组件库、允许业务项目绕过 Kernel、继续依赖自然语言校验描述、或者把问题继续交给人工 review，这些做法在局部上看似高效，但会直接破坏 Kernel / Provider 分离、Contract 驱动、工程落位稳定性和后续 modern provider 预留边界。

#### 5.12.3 设计含义

该原则意味着所有便捷实现都必须先过边界审查；MVP 允许收敛范围，但不允许牺牲关键抽象；后续章节的设计若与本章原则冲突，应优先回退到原则层修正，而不是在局部实现上“先做再说”。

### 5.13 本章结论

本章确立了本方案的核心设计原则：

1. 终局先行，阶段落地
2. Kernel 与 Provider 分离
3. 合同化优先于自由生成
4. 正确性优先，体验渐进增强
5. 规则必须可执行、可检测、可回修
6. 阶段能力必须可继承、可扩展、可替换
7. 增强现有骨架，不另起平行体系
8. 工程落位必须稳定，职责不能漂移
9. 先闭环、后抽象
10. 存量兼容、增量收口、边界隔离、渐进迁移
11. 不以局部最优破坏整体边界

这些原则将作为后续章节的统一判断基线。

---

## 6. 工程落位边界与职责划分

### 6.1 章节目标

本章用于明确本方案中各类能力的**工程归属、实现落点、消费关系与职责边界**。

### 6.2 总体工程分层

上述四层为逻辑职责分层，运行时消费落点由第 6.2.4 层承载。
除标准的新生成链路外，本方案还需面向现存项目的兼容与迁移场景建立对应落位：Legacy Adapter、Compatibility Profile、Migration Scope 与相关检查上下文仍遵循本章定义的职责边界，不另起平行体系。

本方案将整体工程落位划分为四层：

#### 6.2.1 Ai_AutoSDLC Core 机制层

负责：

- stage / gate / artifact 接入
- Contract 规范与 schema 定义
- checker / gate / report / fix loop 机制
- UI Kernel 协议定义
- recipe、whitelist、hard rules 的标准定义
- 生成约束与校验闭环的编排逻辑

不负责：

- 前端页面实际运行时代码
- 具体组件的最终渲染实现
- 公司组件库源码治理
- 业务项目中的运行时接入细节

#### 6.2.2 模板 / Contract / Rule 生成层

负责：

- 将需求、设计、字段规则、页面元数据转为结构化 Contract
- 产出供代码生成使用的约束型 artifact
- 输出 gate 与 recheck 所消费的规则输入

#### 6.2.3 Provider / Wrapper 运行时适配层

负责：

- 将 UI Kernel 语义组件映射为目标运行时实现
- 对公司组件库做白名单包装、收口与隔离
- 承担 Provider adapter、Kernel wrapper 的代码实现
- 向业务前端项目暴露受控运行时接口

#### 6.2.4 业务前端项目消费层

负责：

- 消费 Kernel Wrapper 与 Provider Adapter
- 承载页面级代码、业务逻辑和运行时依赖
- 落地 AI 新生成页面代码
- 集成检查结果、修复结果与最终构建流程

### 6.3 Ai_AutoSDLC Core 内建设内容

#### 6.3.1 Core 的职责定位

Ai_AutoSDLC Core 的职责是：

> **定义前端治理机制与协议，不承载具体前端组件运行时实现。**

#### 6.3.2 Core 内应建设的模块

1. UI Kernel 协议定义
2. Contract 规范与 Schema
3. Rule / Checker / Gate 机制
   其中，**规则定义、schema 与流程编排归 Ai_AutoSDLC Core**；**具体检查执行**则面向目标业务前端项目的源码、构建产物以及实例化 artifact 进行，不在 Core 仓库中直接持有和扫描前端运行时代码。
4. Recheck / Auto-fix 机制
5. 与现有流程的接入适配

#### 6.3.3 Core 内明确不建设的内容

1. 不建设前端运行时组件库实现
2. 不建设公司组件库的历史源码治理工程
3. 不建设业务项目专属运行时逻辑
4. 不将 Core 演进为前端 runtime monorepo

### 6.4 模板 / 规则 / Contract 生成层建设内容

#### 6.4.1 定位

模板 / Contract / Rule 生成层，是连接需求输入与代码生成 / 检查的中间层。其核心职责不是运行页面，而是：

> **把原本模糊、易漏、易漂移的前端要求，转成可生成、可检查、可回修的结构化产物。**

#### 6.4.2 该层承载的主要对象

1. 页面元数据
2. i18n 合同
3. 表单校验合同
4. 前端硬规则
5. 组件白名单 / recipe / token 规则

#### 6.4.3 该层与 Core 的关系

- **Core = 规范与机制**
- **Contract 层 = 规范实例化后的输入产物**

#### 6.4.4 该层的工程落位建议

形态 A：作为 Core 内的模板与 schema 资产
形态 B：作为业务项目或试点项目生成出的实例化 artifact

#### 6.4.5 存量项目迁移相关 artifact

对于现存项目，模板 / Contract / Rule 层还应支持以下迁移相关信息：

- `compatibility_profile`
- `migration_level`
- `legacy_boundary_ref`
- `migration_scope`

MVP 阶段，这些信息优先作为 `page/module contract` 的扩展字段承载。

### 6.5 业务项目 Runtime 层建设内容

#### 6.5.1 定位

业务前端项目 Runtime 层是本方案中承载实际页面运行和 Provider 接入的地方。其职责是：

> **消费 Ai_AutoSDLC 产出的协议、Contract 和检查结果，并承载真正可运行的前端代码。**

#### 6.5.2 Runtime 层应承载的内容

1. 页面运行时代码
2. 项目级运行时依赖
3. provider wrapper / Kernel wrapper 接入
4. 项目级 i18n 与校验资源

对于现存项目，业务 Runtime 层还可能承载：

- Legacy Adapter
- 兼容执行口径下的区域级 Wrapper
- 页面迁移级别标识
- 项目级 Compatibility Profile

#### 6.5.3 Runtime 层不承担的责任

业务项目 Runtime 不应自行重新定义：

- UI Kernel 协议
- 核心 Contract schema
- gate 机制
- 全局 hard rules 规则定义

同时必须明确：

> **业务项目不得绕过 Kernel Wrapper / Provider Adapter，直接引用公司组件库作为页面开发默认入口。**

### 6.6 Provider / Wrapper / 适配包的落位

#### 6.6.1 Provider 的工程定位

`enterprise-vue2 provider` 的本质，是运行时代码层的一个**受控适配层**。

#### 6.6.2 Provider 不应落在 Ai_AutoSDLC Core 仓库中的原因

1. Provider 依赖具体前端技术栈与运行时
2. Provider 属于运行时实现，不属于治理机制
3. Provider 需要跟随业务项目与组件库现实演进

#### 6.6.3 推荐落位方式

方式 A：独立适配包
方式 B：目标业务前端项目内的适配层

从阶段策略上，**MVP 推荐优先采用“目标业务前端项目内适配层”**；当 **2 个及以上项目** 已验证相同 wrapper / adapter 形态具备稳定复用价值后，再考虑将其升级沉淀为**独立适配包**。

#### 6.6.4 Wrapper 的层级划分建议

第一层：Kernel Wrapper
第二层：Provider Adapter

对于现存项目中短期无法替换的老旧组件，还应允许存在 Legacy Adapter / Compatibility Wrapper 这一受控桥接层。

#### 6.6.5 明确禁止的落位方式

1. 直接在业务项目中全量 `Vue.use` 公司组件库作为 Kernel
2. 直接将 `Sf*` 组件作为 AI 输出目标
3. 在 Ai_AutoSDLC Core 中直接维护企业 provider 运行时代码
4. 业务项目绕过 Kernel Wrapper / Provider Adapter，直接引用公司组件库作为页面开发默认入口

### 6.7 Provider / Theme / 外部系统预留边界

#### 6.7.1 终局设计要求

虽然 MVP 只落地 `enterprise-vue2 provider`，但工程边界必须为后续能力预留扩展接口，包括：

- modern provider
- 多 theme pack
- 多风格 token 映射
- 面向外部系统的现代前端输出

#### 6.7.2 MVP 与终局的边界关系

MVP 明确落地：

- UI Kernel 最小协议
- enterprise-vue2 provider
- 相关 wrapper / adapter 运行时承载方式
- 三条主治理链路
- 最小 recipe / whitelist / token rules

MVP 明确保留，不正式实现：

- modern provider
- 完整 design token 平台
- 多主题系统
- Apple/macOS-like 风格运行时落地

### 6.8 为什么需要这层边界来避免后续重构

本章定义的边界不是形式主义，而是为了实质性减少后续返工。

### 6.9 本章结论

本章锁定以下工程边界：

1. **Ai_AutoSDLC Core 负责 Contract、Rule、Gate、Recheck、Fix Loop 和 UI Kernel 协议，不负责前端运行时代码承载。**
2. **模板 / Contract / Rule 层负责将前端约束实例化为结构化 artifact，是连接输入、生成与检查的中间层。**
3. **Provider / Kernel Wrapper 的运行时实现落在目标业务前端项目或独立适配包中，不落在 Ai_AutoSDLC Core 仓库中。**
4. **业务前端项目负责消费受控能力并承载页面运行时代码，不负责重新定义框架级协议和规则。**
5. **enterprise-vue2 provider 是白名单核心组件的选择性包装层，不是公司组件库的全量透传层。**
6. **MVP 的治理对象是 AI 新生成代码、Kernel / Provider 适配层和模板链路，不追溯治理公司组件库内部历史源码。**
7. **modern provider、多主题与外部系统能力在工程边界上预留，但不进入 MVP 运行时交付范围。**

---

## 7. 总体架构设计

### 7.1 章节目标

本章用于从全局视角定义 Ai_AutoSDLC 前端治理与 UI Kernel 方案的总体架构。

### 7.2 总体架构总览

本方案的总体架构由**五个核心架构层**与**一个运行时消费落点**构成：

#### 7.2.1 五个核心架构层

1. 输入层
2. Contract 层
3. UI Kernel 层
4. Provider 层
5. Gate / Recheck / Fix Loop 层

#### 7.2.2 一个运行时消费落点

6. 业务项目 Runtime 消费层

### 7.3 核心架构主线

#### 7.3.1 主线定义

从整体上看，本方案的前端治理主线不是“AI 直接生成页面”，而是：

**需求输入**
→ **Contract 实例化**
→ **UI Kernel 目标约束**
→ **Provider 运行时映射**
→ **页面代码生成**
→ **Gate 检查**
→ **Recheck / Auto-fix**
→ **通过后进入业务项目运行时**

其中，**Contract 定义、规则 schema 与 gate 编排归 Ai_AutoSDLC Core**；**具体检查执行**则面向目标业务前端项目的源码、构建产物与实例化 artifact 进行。

#### 7.3.2 与轻治理方案的区别

与仅依赖 prompt、文档提醒和 review checklist 的轻治理方案相比，本架构的关键差异在于：

- 将关键前端要求变成 Contract
- 将关键约束变成可执行的 checker 与 gate
- 将修复从人工 review 迁移为标准化回修链路
- 将底层组件库能力隔离在 Provider 后面，而不是直接暴露给 AI

#### 7.3.3 存量项目兼容主线

除标准的新生成主线外，现存项目还存在一条兼容主线：

**存量页面 / 旧组件现实**
→ **Legacy Boundary 标识**
→ **Compatibility Profile / Migration Scope 实例化**
→ **Legacy Adapter / Provider Wrapper 承接**
→ **局部改动进入新治理链**
→ **同一套 gate matrix 的兼容执行口径**
→ **逐步收口至标准模式**

### 7.4 各层职责设计

#### 7.4.1 输入层

输入层负责承载前端生成的源头信息，包括产品需求、页面规格、页面类型声明、字段定义、国际化文案来源、表单校验描述、交互要求和约束性规则输入。其特点是来源广、结构不稳定、语义表达偏自然语言，因此不能直接作为代码生成输入，必须先进入 Contract 层完成结构化收敛。

#### 7.4.2 Contract 层

Contract 层是输入与生成之间的治理中间层，其职责是：

- 将模糊前端要求转成结构化约束
- 为代码生成提供稳定输入
- 为 gate / checker 提供检查依据
- 为 fix loop 提供违规回灌格式

首期 Contract 层至少包括：

- `i18n contract`
- `form validation contract`
- `frontend hard rules contract`
- `page metadata / recipe declaration`
- `component whitelist`
- `minimal token / naked-value rules`

并且必须明确：

> **Contract 不是补充性文档，而必须成为可生成、可校验、可回修的实例化 artifact。**

#### 7.4.3 UI Kernel 层

UI Kernel 层是本方案的标准协议层。

#### 7.4.4 Provider 层

Provider 层负责把 UI Kernel 协议映射到具体运行时实现。

在 MVP 中，Provider 层的核心是：

- `enterprise-vue2 provider`

其定位是：

- 选择性包装公司组件库白名单能力
- 提供 `Ui*` 到企业组件实现的受控映射
- 隔离全局副作用、宽 API 面和历史兼容扩展点
- 将历史组件能力收口为可治理接口

Provider 层不是统一内核，也不是底层组件库透传层。MVP 中的 `enterprise-vue2 provider` 采用**白名单核心组件的选择性包装模式**，明确不以全量 `Vue.use` 公司组件库为接入方式，不将其宽 API 面、全局副作用与历史兼容扩展点直接带入 AI 生成链路。

#### 7.4.5 Gate / Recheck / Fix Loop 层

这一层负责把前端规则升级为真正的工程门禁，包括静态检查、lint / AST 规则、recipe 合规检查、whitelist 合规检查、i18n / validation / token 违规检测、Violation Report 生成、Recheck 和 Auto-fix。它是本方案“防错、验错、修错”闭环的核心。

#### 7.4.6 业务项目 Runtime 消费层

Runtime 层承载最终可运行页面代码与项目依赖，主要负责消费 Provider / Wrapper、承载 AI 新生成页面、集成项目级 i18n、API、路由、store，并执行实际构建、运行和验证。该层是最终业务交付落点，但不定义框架级协议和规则。

### 7.5 MVP 架构切线

#### 7.5.1 MVP 必落地内容

MVP 需要形成一个完整但收敛的最小闭环，包含：

- 最小输入约束
- 最小 Contract 体系
- 最小 UI Kernel 协议
- `enterprise-vue2 provider`
- 最小 page recipe
- 最小 component whitelist
- 最小 token 禁裸值规则
- i18n / validation / Vue2 hard rules 主治理链路
- 最小 gate / recheck / auto-fix 闭环

MVP 的治理对象主要覆盖 **AI 新生成页面代码、UI Kernel wrapper、Provider adapter，以及相关模板与检查链路**；**不将公司组件库内部历史源码治理纳入首版正式交付范围**。

MVP 还需建立现存项目的最小兼容链路，包括：

- Legacy Boundary 标识
- Compatibility Profile 基础口径
- 对新增/改动区域实施新治理、对存量区域实施兼容治理的分级策略

#### 7.5.2 MVP 明确不落地内容

MVP 不进入正式交付范围的内容包括：`modern provider`、完整 theme pack 体系、完整 visual regression 平台、完整 a11y 平台、完整 page schema / UI schema，以及公司组件库内部历史源码治理工程。

#### 7.5.3 MVP 的架构边界

MVP 的关键不是做小，而是做成闭环。因此，MVP 的架构要求是：终局结构先定下来，首期只落关键主链路，不把未来能力硬塞进首版交付，也不因首版聚焦而牺牲后续扩展边界。

### 7.6 P1 / P2 演进路径

#### 7.6.1 P1 演进方向

P1 重点是从“正确性止血”走向“体验稳定”。在架构上，P1 主要扩展更完整的 UI Kernel 语义组件集、更完整的 page recipe 集、更严格的 whitelist / token 体系、frontend recheck agent、基础 visual / a11y 检查和更完整的状态覆盖检查。

#### 7.6.2 P2 演进方向

P2 重点是面向外部系统与多风格输出。在架构上，P2 主要扩展 `modern provider`、多 theme pack、多风格 token 映射、更完整的 visual / a11y / interaction quality gate，以及更深的 page schema / UI schema；但仍沿用 MVP 已确立的 Kernel / Provider / Gate 结构，不另起一套体系。

### 7.7 Artifact 流转链路

#### 7.7.1 流转原则

本方案中的 artifact 流转遵循三个原则：结构化输入先于代码生成，规则检查基于实例化 artifact 而不是只依赖 prompt，检查结果必须能回流为 Fix Input。

#### 7.7.2 核心流转链路

核心流转链路如下：需求、页面规格、字段定义、文案和校验规则进入前端分析链路；生成页面级或模块级 Contract artifact；AI 根据 Contract、Kernel 协议和 Provider 约束生成页面代码与适配代码；Checker / Gate 对页面代码、实例化 contract 和项目资源执行检查；Fix Loop 根据报告形成定向修复输入；通过验证后，再将结果进入业务项目构建、验证和最终交付链路。

#### 7.7.3 Artifact 的三类角色

1. 约束型 artifact
2. 检查型 artifact
3. 修复型 artifact

对于现存项目，还应补充一类迁移上下文型 artifact，例如：

- `compatibility_profile`
- `migration_scope`
- `legacy_boundary_ref`
- `migration_level`

#### 7.7.4 Artifact 的落位归属

- **规范型 artifact**：由 Ai_AutoSDLC Core 定义格式与模板；
- **实例化 Contract artifact**：由设计 / 生成链路面向具体页面或模块产出；
- **检查型 artifact**：由面向目标业务前端项目执行的 checker / gate 产出；
- **修复型 artifact**：由 Violation Report 转换或 Recheck / Fix Loop 生成，并回流到生成与修复阶段消费。

### 7.8 与现有 Ai_AutoSDLC 流程的关系

#### 7.8.1 与现有 stage 的关系

本方案不另建一条独立前端 pipeline，而是接入现有阶段体系：

- `refine`：补前端输入收敛要求与页面类型、字段、文案等前置定义。
- `design`：补 Contract、Kernel 映射、recipe declaration 选择和 Provider 适配设计。
- `decompose`：把前端 Contract 落到具体任务拆解和页面实现任务中。
- `verify`：运行 checker、gate、coverage check、drift check、legacy expansion check、recheck 输入生成等校验动作。
- `execute`：承接 Fix Loop、定向修复、再次生成与修复后回写。
- `close / report`：沉淀前端治理结果、违规收敛情况和质量统计。

#### 7.8.2 与现有 artifact 思路的关系

本方案与现有 `spec / plan / tasks / verification` 思路是一致的：

- 不新增平行体系
- 不绕开现有 artifact
- 只在现有 artifact 驱动模式上补前端专属对象

因此，前端治理在 Ai_AutoSDLC 中的引入方式，是对现有 spec / plan / tasks / verify / close 骨架的增强，而不是新增一套平行的前端交付系统。

### 7.9 架构约束与禁止项

为保证总体架构不退化，本方案明确以下约束：

1. 不允许绕过 UI Kernel 直接把底层组件库暴露给 AI 作为默认生成目标。
2. 不允许把 `enterprise-vue2 provider` 退化为公司组件库全量透传层。
3. 不允许在 `Ai_AutoSDLC Core` 中承载业务前端运行时代码。
4. 不允许把 page recipe 绑定为企业组件库的旧页面骨架。
5. 不允许把前端治理退化成仅依赖 prompt 和 review checklist 的软约束体系。

### 7.10 本章结论

本章确定了本方案的总体架构主线：

- 输入先收敛为 Contract
- Contract 驱动 UI Kernel 目标生成
- Provider 承担运行时映射与隔离
- Gate / Recheck / Fix Loop 构成治理闭环
- Runtime 层负责最终消费与运行

同时，本章也明确了：

- MVP 只落最小闭环，不做终局全量能力
- P1 / P2 在同一架构下渐进增强
- 前端治理接入现有 Ai_AutoSDLC stage / gate / artifact 体系，而不是另起新系统

---

## 8. 输入规格与 Contract 体系设计

### 8.1 章节目标

本章用于定义 Ai_AutoSDLC 前端治理方案中的**输入收敛规则**与**Contract 体系**。

### 8.2 设计目标与边界

#### 8.2.1 目标

1. 将前端高频失控点前移到输入阶段收敛
2. 将关键前端要求从自然语言描述提升为结构化 Contract
3. 让 Contract 成为可生成、可校验、可回修的实例化 artifact
4. 为第 9 章 UI Kernel、第 11 章前端生成约束、第 12 章 Gate / Recheck / Auto-fix 提供统一输入基础

#### 8.2.2 边界

本章不解决：

- UI 语义组件协议的具体定义
- Provider 的具体映射实现
- 具体 checker / lint / AST 的技术实现细节
- 视觉 token 体系的完整平台化设计

### 8.3 输入规格扩展要求

#### 8.3.1 为什么必须扩展输入规格

当前前端 AI coding 的高频问题已经证明，仅依赖自然语言 PRD / 设计描述会带来 i18n key 漏定义、表单校验规则缺失或边界不一致、页面类型和页面结构漂移、Vue2 规范在长上下文中被突破，以及组件使用和样式表达失控。因此，前端输入不能停留在“描述页面要做什么”，还必须回答页面属于什么类型、采用什么 recipe、需要哪些文案、校验规则是什么，以及受哪些硬规则和样式底线约束。

#### 8.3.2 输入收敛原则

输入规格扩展遵循以下原则：先约束高频失控点，不追求一次覆盖所有前端细节；先定义结构化对象，再谈生成与校验；标准定义与实例化声明分离；能进入 artifact 链路的内容优先结构化；MVP 只结构化当前最影响交付稳定性的前端要求。

#### 8.3.3 首期必须结构化的输入对象

MVP 阶段，至少要求以下对象进入结构化输入：

- 页面元数据（page metadata）
- recipe declaration
- i18n contract
- form validation contract
- frontend hard rules contract
- component whitelist 引用
- minimal token / naked-value rules 引用

#### 8.3.4 源头优先级与真值顺序

为避免前端需求、Contract 与实现代码之间出现冲突时缺少裁决基线，本方案明确以下真值顺序：

1. 业务真值来源：PRD / spec
2. 前端实现真值来源：Contract
3. 页面代码必须服从 Contract
4. gate 以 Contract 与代码对照，不以 prompt 为准

### 8.4 Contract 体系总览

#### 8.4.1 Contract 分层

本方案中的 Contract 体系分为两类：

1. 标准定义型
2. 实例声明型

#### 8.4.2 Contract 的核心组成

MVP 阶段的 Contract 体系至少包括：

1. `page metadata`
2. `recipe declaration`
3. `i18n contract`
4. `form validation contract`
5. `frontend hard rules contract`
6. `component whitelist reference`
7. `minimal token rules reference`

#### 8.4.3 Contract 在架构中的定位

Contract 在本方案中既不是补充文档，也不是临时中间结果，而是：

> **生成前的约束输入、检查时的判定依据、修复时的回灌基础。**

因此必须明确：

> **Contract 不是补充性文档，而必须成为可生成、可校验、可回修的实例化 artifact。**

#### 8.4.4 Contract 作用域

本方案中的 Contract 实例化 artifact 按作用域分为三层：

1. `work-item` 级
2. `module` 级
3. `page` 级

`page` 级 Contract 是 MVP 阶段前端生成、检查与修复的主要执行单元。

对于现存项目，`page` 级 Contract 仍然是主要执行单元；但页面还可附带：

- `compatibility_profile`
- `migration_level`
- `legacy_boundary_ref`
- `migration_scope`

### 8.5 页面元数据与 Recipe 声明

#### 8.5.1 页面元数据的作用

页面元数据用于回答“当前页面是什么”和“当前页面要受哪些上位约束”。它至少应描述 `page_id`、`page_type`、所属模块、是否表单页 / 列表页 / 详情页、是否包含主操作、是否包含筛选区 / 详情区 / 状态区、是否涉及表单校验、异步加载和 i18n 文案输出。它的作用是把页面的类型与责任先说清，而不是让 AI 在代码层自由猜测。

#### 8.5.2 Recipe Declaration 的作用

Recipe declaration 用于声明：

- 当前页面选用哪一种 page recipe
- 该 recipe 在当前页面上的必要参数或变体
- 当前页面哪些区域是必需的
- 当前页面是否存在例外配置

需要特别强调：

> **page recipe 的标准定义归 UI Kernel 层；Contract 层只承载页面级或模块级的 recipe declaration，用于声明当前页面选择哪一种 recipe 及其必要参数。**

#### 8.5.3 MVP 对页面元数据与 recipe declaration 的要求

MVP 阶段至少要求：每个 AI 新生成页面必须声明 `page_type`，每个页面必须绑定一个 `recipe declaration`，未声明 recipe 的页面不得作为正式生成目标，且 recipe declaration 必须进入 artifact 链路，供生成与检查共同使用。

#### 8.5.4 例外声明必须结构化

若页面存在以下例外情况，必须以**结构化声明**进入 Contract：

- recipe declaration 例外
- component whitelist 豁免
- minimal token / naked-value rules 豁免
- hard rules 特殊豁免

这些例外不允许只存在于自然语言描述、备注文字或口头说明中。

### 8.6 i18n Contract

#### 8.6.1 设计目标

i18n contract 用于解决文案裸写、key 使用未定义、key 命名混乱、生成后缺少回检，以及多页面重复定义与复用关系不清等问题。

#### 8.6.2 i18n Contract 至少应包含的内容

每个页面或模块级的 i18n contract 至少应包含 `namespace`、key 列表、默认文案、文案语义说明、是否允许复用既有 key、当前页面引用哪些已有 key，以及当前页面新增哪些 key。MVP 不要求首版完成复杂术语平台，但必须至少做到 key 使用有来源、新 key 有定义、裸文案可被识别和回检。

#### 8.6.3 i18n Contract 的输入来源

来源可以包括 PRD / 页面规格中的文案清单、页面结构中的标题、按钮、字段标签、提示语，以及校验错误文案、空态 / 错态 / 成功态文案。这意味着 i18n 不能被视为页面开发后的补充动作，而必须前置进入 contract。

#### 8.6.4 MVP 对 i18n Contract 的要求

MVP 阶段至少要求：用户可见文案必须进入 i18n contract 或明确引用已有 key；页面生成前应具备页面级 i18n artifact；生成后必须能对照 code usage 与 key definition 做检查；缺失 key、裸文案应进入 Violation Report。

### 8.7 Form Validation Contract

#### 8.7.1 设计目标

form validation contract 用于解决校验规则只存在于模糊自然语言中、AI 自行猜测边界、联动校验缺失、前后端校验含义不一致，以及错误提示不统一等问题。

#### 8.7.2 Validation Contract 至少应包含的内容

每个表单字段的 contract 至少应支持描述字段名、字段类型、是否必填、长度 / 范围、格式 / pattern、联动依赖、错误提示、校验触发时机、是否条件必填，以及是否有默认值约束。MVP 不要求首版就覆盖全部复杂规则语法，但必须覆盖当前最常见的企业表单校验场景。

#### 8.7.3 Validation Contract 的作用边界

Validation Contract 不是替代具体校验实现，而是作为前端生成的稳定输入、校验覆盖检查的依据、后续前后端一致性校验的基础，以及测试用例生成的上游输入。

#### 8.7.4 MVP 对 Validation Contract 的要求

MVP 阶段至少要求：表单页若存在字段校验，则必须生成 validation contract；无 validation contract 的表单页，不进入正式 AI 页面生成；生成后必须能检查 contract 已定义的规则是否被页面实现；校验遗漏、联动规则缺失、错误提示缺失应进入 Violation Report。

### 8.8 Frontend Hard Rules Contract

#### 8.8.1 设计目标

frontend hard rules contract 用于解决长上下文下规则漂移、Vue2 编码规范失守、AI 为完成局部任务直接突破底线，以及项目已有约束只停留在文档层的问题。

#### 8.8.2 Hard Rules 的对象范围

MVP 首期重点覆盖：禁止直接修改 props、禁止不合规地对 props 使用 `v-model`、禁止绕过 Kernel / Wrapper 直接使用底层组件、禁止裸文案、禁止裸视觉值，以及禁止绕过 recipe 或 whitelist 约束。这些规则属于“不可突破底线”，不是建议项。

#### 8.8.3 Hard Rules Contract 的作用

其作用不是重复写编码规范文档，而是把“必须遵守”的规则变成可实例化引用、可静态检查、可输出 violation、可触发 fix loop 的结构化输入。

#### 8.8.4 MVP 对 Hard Rules Contract 的要求

MVP 阶段至少要求：每个 AI 新生成页面默认继承一组基础 hard rules；允许页面声明额外规则，但不得绕开基础规则；hard rules 必须进入 Gate 检查链；违规必须输出机器可消费的 Violation Report / Fix Input。

### 8.9 Component Whitelist 与 Minimal Token Rules 引用

#### 8.9.1 Whitelist 的作用

component whitelist 的作用是限制 AI 只能使用受控的 `Ui*` 语义组件，阻止直接自由拼接底层 `Sf*`，并为 Provider 与 Checker 提供共享的组件控制面。

#### 8.9.2 Minimal Token Rules 的作用

minimal token / naked-value rules 的作用是阻止明显失控的裸颜色、裸阴影和裸间距写法，为后续完整 token 体系预留升级路径，并让首版页面至少不至于视觉值完全自由发挥。

#### 8.9.3 在 Contract 中的承载方式

MVP 阶段，whitelist 与 token rules 不一定要在每页重复完整定义，但至少要在页面 contract 中声明引用哪一版 whitelist、哪一组 minimal token rules，如存在例外也必须显式声明并纳入检查。

### 8.10 Contract 产物清单与格式约束

#### 8.10.1 MVP 产物清单

MVP 阶段建议至少形成以下实例化 artifact：`page.metadata.yaml`、`page.recipe.yaml` 或等价 recipe declaration artifact、`page.i18n.yaml`、`form.validation.yaml`、`frontend.rules.yaml`、`component-whitelist.ref.yaml`、`token-rules.ref.yaml`。实际文件命名可按项目约定调整，但语义职责必须保留。

#### 8.10.2 格式约束原则

所有 Contract artifact 应满足：可由机器读取、可被 Checker / Gate 消费、可被 Fix Loop 回引用、可定位到页面或模块级责任对象、且不依赖自然语言段落才能理解核心约束。

#### 8.10.3 格式边界

格式层面建议保持字段命名稳定、层级尽量浅、避免与具体组件库 API 强绑定、避免混入运行时代码实现细节，并支持后续 schema 扩展而不破坏已有 artifact。

#### 8.10.4 元数据字段要求

为支持 schema 演进、来源追踪与检查链稳定运行，每类 Contract artifact 至少应具备以下元数据字段：

- `schema_version`
- `scope`
- `owner` 或 `page_id`
- `source_ref`

### 8.11 Contract 与现有 Ai_AutoSDLC artifact 链路的关系

#### 8.11.1 与 refine / design 的关系

`refine` 阶段负责补足页面类型、字段定义、文案来源和基础交互要求；`design` 阶段负责将这些输入实例化为页面或模块级 Contract，使后续生成与校验有稳定输入真值。

#### 8.11.2 与 decompose 的关系

`decompose` 阶段将 Contract 转化为可执行任务。任务不再只是“写页面”，而是“按 Contract 实现页面并通过对应 Gate”，从而把前端约束真正落到任务拆解层。

#### 8.11.3 与 verify / execute 的关系

- `verify` 阶段对 Contract、代码与项目资源进行对照检查
- `execute` 阶段承接 Fix Loop、回修与修复后回写

#### 8.11.4 与 close / report 的关系

`close / report` 阶段沉淀 Contract 完整性、违规收敛情况与规则命中情况，并可基于 Contract 与 Violation 数据输出治理质量报告，为后续规则演进和优先级调整提供依据。

#### 8.11.5 Contract 漂移检查

Contract 不应成为一次性生成后即失效的中间产物。

当发现漂移时，流程应要求二选一：

1. **回写 Contract**
2. **修正实现代码**

禁止 Contract 长期失真、仅作为生成阶段的临时材料存在。

对于现存项目，还应识别另一类漂移：

> **页面已声明进入增量治理，但本次改动区域仍继续引入新的 legacy 用法。**

### 8.12 本章结论

本章确定了输入规格与 Contract 体系的核心边界：

1. 前端高频失控点必须前移到输入阶段收敛。
2. Contract 是实例化 artifact，不是补充文档。
3. page recipe 的标准定义归 UI Kernel，Contract 层只承载 recipe declaration。
4. i18n、validation、hard rules、whitelist、token rules 是 MVP 首批必须进入 Contract 体系的对象。
5. Contract 必须同时服务于生成、检查与修复，而不是只服务于生成。
6. Contract 体系接入现有 Ai_AutoSDLC artifact 链路，不另起平行体系。

---

## 9. UI Kernel 设计

### 9.1 章节目标

本章用于定义 Ai_AutoSDLC 前端治理方案中的 **UI Kernel 标准层**。

### 9.2 Kernel 定位与职责

#### 9.2.1 Kernel 的定位

UI Kernel 是 Ai_AutoSDLC 前端方案中的**标准协议层**。它不等于任何一套现有组件库，也不是一个直接可运行的前端组件仓库，而是：

> **面向 AI 生成、规则检查和跨 Provider 演进的统一前端标准接口。**

#### 9.2.2 Kernel 的职责

1. 定义语义组件协议
2. 定义页面骨架协议
3. 定义状态与交互底线
4. 定义 AI 前端生成的标准目标接口
5. 隔离 Provider 差异

#### 9.2.3 Kernel 不承担的职责

UI Kernel 不负责：

- 具体 Vue2 / Vue3 / React 运行时实现
- 具体组件库的 API 透传
- 页面业务逻辑本身
- 项目级路由、store、服务层
- 公司组件库源码治理

### 9.3 Kernel 与其他层的关系

#### 9.3.1 Kernel 与 Contract 的关系

> **Contract 负责声明“当前页面使用什么”，Kernel 负责定义“这些东西本身是什么”。**

#### 9.3.2 Kernel 与 Provider 的关系

> **Provider 不能反过来定义 Kernel。**

#### 9.3.3 Kernel 与业务项目 Runtime 的关系

业务项目可以：

- 实现页面内容
- 绑定业务逻辑
- 填充 Contract 声明的具体信息

但不应绕开 Kernel 标准自由重定义基础协议。

#### 9.3.4 Kernel 与 Theme / Token 的边界

UI Kernel 负责定义：

- 页面结构
- 语义组件
- 状态语义
- 交互底线
- 最小可访问性底线

Theme / token 则负责定义：

- 颜色、间距、字号、阴影、圆角、密度、视觉表达差异

因此必须明确：

> **Kernel 不直接定义企业风或现代风的视觉本体。**

### 9.4 语义组件协议设计

#### 9.4.1 为什么需要语义组件协议

当前前端 AI coding 的一个核心问题是模型经常直接生成原生结构、低层组件调用、项目历史写法或临时样式拼装。这会导致 API 面失控、组件使用不一致、页面结构漂移，以及后续无法做 whitelist / recipe / gate 治理。因此必须通过 `Ui*` 语义组件协议，将“页面要用什么能力”与“底层怎么实现”切开。

#### 9.4.2 语义组件协议的定义原则

语义组件协议遵循四条原则：定义语义而不透出底层实现细节；优先收口高频页面所需能力；协议稳定优先于能力完整；面向 AI 生成与治理，而不是为低层灵活性服务。

#### 9.4.3 标准化 value / props / event 语义

每个 `Ui*` 协议除语义用途外，还应定义**标准化的 value / props / event 语义边界**。

#### 9.4.4 MVP 语义组件范围

MVP 阶段建议首批定义以下语义组件协议：

- `UiButton`
- `UiInput`
- `UiSelect`
- `UiForm`
- `UiFormItem`
- `UiTable`
- `UiPageHeader`
- `UiDialog`
- `UiDrawer`
- `UiEmpty`
- `UiSpinner`

#### 9.4.5 语义组件协议的边界

每个 `Ui*` 组件协议至少应定义组件语义用途、MVP 支持的最小能力面、可接受的主要 props / state / event 形态、不应透出的底层能力、与 Provider 的映射边界，以及与 page recipe 的关系。Kernel 负责定义协议本身，运行时 wrapper 和 Provider adapter 再决定如何把这些协议落到具体实现上。

#### 9.4.6 语义组件协议不等于运行时代码组件

这里必须明确：

> **UI Kernel 中的 `Ui*` 语义组件协议，不等于 Core 仓库中的实际 Vue 组件源码。**

### 9.5 Page Recipe 标准本体设计

#### 9.5.1 为什么需要 Page Recipe 标准本体

如果没有 page recipe 标准，AI 会倾向于从空白页面自由拼装、自己决定区域结构、自己决定操作区放哪、自己决定状态区如何表现，最终导致同类页面结构不一致、表单页节奏混乱、列表页操作区和筛选区漂移，以及详情页层次模糊。因此，UI Kernel 必须定义 page recipe 标准本体，把“页面怎么组织”先规范下来。

#### 9.5.2 Recipe 标准本体与 Recipe Declaration 的分工

> **Kernel 负责定义 recipe 是什么，Contract 负责声明当前页面选哪个 recipe declaration。**

#### 9.5.3 MVP Page Recipe 范围

MVP 阶段建议先定义三个标准本体：

- `ListPage`
- `FormPage`
- `DetailPage`

#### 9.5.4 Recipe 区域约束模型

每个 page recipe 标准本体除定义页面区域外，还应进一步区分：

- `required area`
- `optional area`
- `forbidden pattern`

### 9.6 ListPage 标准本体

#### 9.6.1 适用场景

`ListPage` 适用于查询列表页、资源列表页、管理台列表页，以及带筛选和主操作的数据页。它是企业中后台最高频的页面模式之一，也是当前最需要优先收口结构与交互的页面类型。

#### 9.6.2 必备区域

1. `PageHeader`
2. `Filter / Search Area`
3. `Primary Action Area`
4. `Content Area`
5. `State Area`
6. `Pagination Area`

#### 9.6.3 基础交互要求

`ListPage` 至少满足：列表加载中时有明确 loading 表达，数据为空时有 empty 表达，查询失败时有 error 表达，主操作与筛选区语义不混用，列表主体不得被任意原生结构替代以绕开 `UiTable`。

### 9.7 FormPage 标准本体

#### 9.7.1 适用场景

`FormPage` 适用于创建页、编辑页、配置页，以及带明显表单提交目标的页面。它强调数据录入、校验、提交反馈和动作角色的清晰分离。

#### 9.7.2 必备区域

`FormPage` 在 Kernel 层至少定义以下必备区域：`PageHeader`、`Form Content Area`、`Action Area` 与 `State Area`。其中表单主体必须由 `UiForm / UiFormItem` 承载，可按需要包含分组区域、帮助信息区域与提交反馈区。

#### 9.7.3 基础交互要求

`FormPage` 至少满足：表单字段必须受 validation contract 驱动，校验失败有明确反馈，提交动作与取消动作语义清晰，不允许通过自然语言备注替代结构化校验定义，也不允许绕开 `UiForm / UiFormItem` 自由拼装形成“伪表单页”。

### 9.8 DetailPage 标准本体

#### 9.8.1 适用场景

`DetailPage` 适用于资源详情页、配置详情页、记录查看页，以及只读为主、操作为辅的信息页。它强调信息分区、页面级操作分离和状态可感知。

#### 9.8.2 必备区域

`DetailPage` 在 Kernel 层至少定义以下必备区域：`PageHeader`、`Summary Area`、`Detail Content Area`、`Action Area` 与 `State Area`。详情区可进一步分为基础信息、扩展信息和关联信息等分区，但页面级操作不得与内容区混淆。

#### 9.8.3 基础交互要求

`DetailPage` 至少满足：信息展示分区明确，页面级操作不与内容区混淆，只读场景下不强行套用表单交互，详情页的空态 / 异常态明确可感知。

### 9.9 状态、交互与可访问性底线

#### 9.9.1 状态底线

Kernel 层应统一定义最小状态要求。MVP 阶段至少包括：

- `loading`
- `empty`
- `error`
- `disabled`
- `no-permission`

#### 9.9.2 状态归属与优先级

Kernel 层定义的 `loading / empty / error / no-permission` 等状态，应以**页面级或 recipe 级状态语义**为主，并明确与组件局部状态之间的归属边界及优先级关系。

#### 9.9.3 交互底线

MVP 阶段至少定义以下交互底线：主操作与次操作语义清晰，表单提交、取消、返回等行为边界清晰，校验错误必须有明确反馈，危险动作应有确认机制，页面不得通过随意布局破坏 recipe 基本区域语义。

#### 9.9.4 最小可访问性底线

MVP 不建设完整 a11y 平台，但 Kernel 层应至少定义最小底线：表单错误提示可感知，基础状态变化可感知，不允许完全依赖视觉位置表达关键状态，交互性组件应保留最基本的可识别语义。这些底线将在第 12 章中转换为可检查规则或后续扩展方向。

### 9.10 MVP / P1 / P2 组件范围演进

#### 9.10.1 MVP

MVP 首批语义组件包括 `UiButton`、`UiInput`、`UiSelect`、`UiForm`、`UiFormItem`、`UiTable`、`UiDialog`、`UiDrawer`、`UiEmpty`、`UiSpinner`、`UiPageHeader`。MVP 首批 page recipe 包括 `ListPage`、`FormPage`、`DetailPage`。

#### 9.10.2 P1

P1 可扩展的语义组件包括 `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiResult`、`UiSection`、`UiToolbar`、`UiPagination`、`UiCard`；可扩展的 page recipe 包括 `DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage`。

#### 9.10.3 P2

P2 可继续扩展更丰富的语义组件集、与 modern provider 匹配的新交互容器、面向外部系统的更现代 page recipe，以及更完整的状态和体验标准，但这些扩展都应建立在 MVP / P1 已经稳定的 Kernel 边界之上，而不是推翻现有协议。

### 9.11 Kernel 设计的约束与禁止项

1. 不允许用底层组件库 API 直接替代 `Ui*` 语义组件协议。
2. 不允许把企业组件库的历史 page 骨架直接抬升为 recipe 标准本体。
3. 不允许在 Kernel 层混入具体运行时实现、业务逻辑或项目构建细节。
4. 不允许将 recipe declaration 与 recipe 标准本体混写。
5. 不允许为追求局部灵活性而把 `Ui*` 协议设计成底层 API 的简单透传。
6. **不允许通过页面级例外声明或 Provider 层实现，实质性重写 UI Kernel 的语义组件协议或 page recipe 标准本体。**

### 9.12 本章结论

本章确定了 UI Kernel 的核心边界：

1. **UI Kernel 是标准协议层，不是运行时组件库。**
2. **`Ui*` 语义组件协议负责定义页面应使用什么能力，而不是直接暴露底层实现。**
3. **page recipe 标准本体归 UI Kernel，Contract 只承载 recipe declaration。**
4. **MVP 首批 recipe 标准本体为 `ListPage / FormPage / DetailPage`。**
5. **状态、交互与最小可访问性底线应先在 Kernel 层定义，再在后续 Gate 中工程化。**
6. **Kernel 必须保持 Provider 无关性，为 `enterprise-vue2 provider` 与未来 `modern provider` 共同服务。**

---

## 10. enterprise-vue2 Provider 设计

### 10.1 章节目标

本章用于定义 `enterprise-vue2 provider` 的定位、职责边界、映射原则与风险隔离策略。

### 10.2 Provider 定位与职责边界

#### 10.2.1 Provider 的定位

`enterprise-vue2 provider` 是本方案在 MVP 阶段落地的**企业项目运行时实现层**。其定位不是统一内核，也不是公司组件库的别名，而是：

> **将 UI Kernel 标准协议映射到公司主流 Vue2 企业项目现实中的受控适配层。**

#### 10.2.2 Provider 的职责

`enterprise-vue2 provider` 至少承担以下职责：

1. 运行时映射职责
2. 协议收口职责
3. 风险隔离职责
4. 企业实现承接职责
5. 演进桥接职责

> **Provider 应吸收公司组件库对全局 i18n、全局配置、插件初始化和样式入口的前置假设，不将这些假设直接暴露给页面开发层。**

##### 10.2.2.6 Legacy Adapter 吸收职责

对于现存项目中短期无法替换、且仍会在改动中被触达的老旧组件，Provider 还应承担 Legacy Adapter 吸收职责。Legacy Adapter 的定位是**过渡桥与受控桥接层**，不是长期默认入口。

其职责包括：

- 将 legacy 组件包装为受控桥接入口
- 屏蔽其危险默认行为与历史扩展点
- 禁止页面层直接新增 legacy 调用
- 为后续替换为标准 `Ui*` 或新 provider 实现保留出口

#### 10.2.3 Provider 不承担的职责

1. 不定义 UI Kernel 标准
2. 不透传公司组件库全量能力
3. 不复用旧 page 级骨架作为标准
4. 不承担公司组件库内部历史源码治理
5. 不在 Core 仓库内长期承载运行时代码主体

### 10.3 为什么公司组件库只能作为 Provider 能力来源

#### 10.3.1 现实价值：适合承载企业 Vue2 运行时能力

公司组件库覆盖了企业后台常用组件能力，`Form / Grid / Select` 等核心组件业务承载力较强，且与公司现有 Vue2 企业项目现实兼容。因此，完全绕开这套组件库重新从零做企业实现，在 MVP 阶段既不现实，也不必要。

#### 10.3.2 现实局限：不适合作为统一内核

公司组件库运行方式明显绑定公司内部生态与历史依赖，不适合作为跨项目、跨 Provider 的统一标准层；其全局安装与副作用风险较高，若直接全量接入，会把全局配置、副作用插件、历史兼容扩展与宽 API 面一并暴露给 AI 生成链路；同时，底层 `Sf*` 组件的 props / event / 扩展方式也更适合人工资深前端使用，而不适合作为 AI 统一生成协议。

#### 10.3.3 结论

因此，本方案对公司组件库的使用方式只能是：

> **作为 `enterprise-vue2 provider` 的能力来源，被选择性包装、受控暴露和风险隔离。**

### 10.4 `Ui* -> Sf*` 映射原则

#### 10.4.1 映射总原则

`enterprise-vue2 provider` 的映射必须遵循：

> **向上对齐 UI Kernel，向下吸收企业组件能力；不允许由底层实现反向主导 Kernel 协议。**

#### 10.4.2 映射应满足的基本要求

1. 语义对齐
2. value / props / event 语义对齐
3. 风险能力默认不透出
4. Wrapper 必须可被 checker 感知
5. 不破坏后续 Provider 可替换性

`Ui*` 到企业实现的映射可以是一对一、一对多或多对一，但必须保持**向上协议稳定、向下实现可替换**。

#### 10.4.3 首批映射建议

MVP 阶段建议首批映射如下：

- `UiButton -> SfButton`
- `UiInput -> 企业输入类实现`
- `UiSelect -> SfSelect`
- `UiForm -> SfForm`
- `UiFormItem -> SfFormItem`
- `UiTable -> SfGrid`
- `UiDialog -> 企业弹层确认类实现`
- `UiDrawer -> 企业抽屉/侧滑容器实现`
- `UiEmpty -> 企业空态实现`
- `UiSpinner -> 企业加载实现`
- `UiPageHeader -> 企业页面头组合实现`

### 10.5 白名单包装策略

#### 10.5.1 为什么必须白名单包装

如果不做白名单包装，Provider 很容易退化成“底层组件名改个前缀、全量 props 透出、全量事件透出、历史兼容行为全部保留”的透传层。这种做法虽然接入快，但会直接破坏 UI Kernel 协议稳定性、Checker 判定基础、AI 生成可控性，以及后续 modern provider 的可替换性。

#### 10.5.2 白名单包装的对象范围

MVP 首批白名单包装对象与第 9 章的首批 `Ui*` 协议一致，至少包括 `UiButton`、`UiInput`、`UiSelect`、`UiForm`、`UiFormItem`、`UiTable`、`UiDialog`、`UiDrawer`、`UiEmpty`、`UiSpinner`、`UiPageHeader`。只有这些经过包装的 `Ui*` 才允许作为页面开发默认入口。

#### 10.5.3 白名单包装的方式

白名单包装至少包括三类收口：

1. API 收口
2. 能力收口
3. 依赖收口

### 10.6 危险能力隔离与封禁清单

> **危险能力默认关闭，不因底层组件已有能力而默认开放；只有满足例外开放原则时，才允许经 Provider 包装后受控启用。**

#### 10.6.1 隔离原则

本方案对公司组件库的使用，不以“全部保留能力”为目标，而以“先让 AI 可控生成，再逐步评估是否需要开放例外能力”为原则。任何可能放大失控面的底层能力，都应优先隔离，并按受控例外方式逐步开放。

#### 10.6.2 首批应隔离或封禁的能力类型

1. 全局安装能力
2. 宽 API 面
3. 危险渲染能力
4. 历史 page 级骨架能力
5. 与当前治理目标无关的低频灵活能力
6. 已不维护的 legacy 组件默认入口
- 已不维护组件不得作为新页面默认入口
- 已不维护组件不得在新增代码中直接继续扩散
- 若业务必须临时使用，只能通过 Legacy Adapter 且进入结构化例外声明

#### 10.6.3 例外开放原则

如确有业务需要开放某项底层能力，必须满足：

1. 不能直接修改 Kernel 标准协议
2. 必须通过 Provider 层受控包装开放
3. 必须在 Contract 层做结构化例外声明
4. 必须进入 checker / gate 可识别范围
5. 不能破坏其他项目对同一 `Ui*` 的稳定理解

对于已不维护的 legacy 组件，例外开放还必须额外满足：

- 本次改动无法在合理成本内切换到标准 `Ui*`
- 已建立 Legacy Adapter
- 已声明迁移级别与后续替换意图
- 不因一次例外而形成新的默认模式

### 10.7 Page Recipe 到企业实现的承接方式

#### 10.7.1 承接原则

Page recipe 的标准本体归 UI Kernel 定义，Provider 只负责承接其在企业项目中的运行时实现方式。

> **Provider 可以提炼企业页面模式，但不能把企业旧 page 骨架上升为 recipe 标准。**

> **Provider 承接 page recipe 时，重点承接的是区域语义、交互角色与状态要求，而不是对企业旧页面布局进行逐像素复刻。**

#### 10.7.2 承接方式

1. 区域承接
2. 组件承接
3. 状态承接

#### 10.7.3 不允许的承接方式

- 直接把旧 `Page.vue` 或同类历史 page 容器作为标准 recipe 实现
- 因企业旧页面习惯而修改 Kernel recipe 标准本体
- 在页面层通过自由原生结构绕过 recipe 区域约束
- 用底层组件能力替代 recipe 语义区

### 10.8 为什么不能全量 `Vue.use` 公司组件库

#### 10.8.1 全量接入的表面优势

全量 `Vue.use` 看起来有几个表面优势：接入快、可直接复用全部组件能力、老项目兼容成本低、前端改造量少。但这些优势只在“人工直接使用底层组件库”的前提下成立。

#### 10.8.2 对本方案的实质风险

一旦把公司组件库全量 `Vue.use` 接入 AI 生成链路，会带来全局副作用直接上推、底层宽 API 面失控、历史兼容扩展点进入默认路径、Checker / Gate 判定基础被破坏，以及 future modern provider 路线被堵死等风险。

#### 10.8.3 结论

因此，本方案明确：

> **`enterprise-vue2 provider` 不允许以全量 `Vue.use` 公司组件库的方式作为 AI 生成的默认运行时入口。**

### 10.9 MVP / P1 / P2 演进边界

#### 10.9.1 MVP

MVP 阶段，`enterprise-vue2 provider` 的目标是：

- 建立首批 `Ui* -> Sf*` 映射闭环
- 形成白名单包装机制
- 隔离全量安装、副作用与危险扩展
- 承接 `ListPage / FormPage / DetailPage`
- 为 checker / gate 提供稳定的运行时协议面

MVP 不追求：

- 覆盖企业组件库全部能力
- 覆盖全部页面类型
- 覆盖所有历史兼容场景

MVP 阶段，Provider 还需支持最小的 legacy 兼容策略：

- 允许少量 Legacy Adapter 存在
- 允许老页面在 Compatibility Profile 下做局部改动
- 禁止新增代码直接复制 legacy 用法
- 以边界隔离 + 新增收口为主，不以全面替换为首版目标

> **MVP 阶段优先在业务项目内闭环，待 2 个及以上项目验证同形态 wrapper / adapter 稳定复用后，再考虑独立适配包化。**

#### 10.9.2 P1

P1 可在 MVP 基础上继续扩展更多 `Ui*` 语义组件映射、更完整的 page recipe 承接、更细化的受控例外能力、更成熟的 wrapper 层复用方式，以及与 Recheck / Auto-fix 更紧密的协同。

#### 10.9.3 P2

P2 的重点不是继续扩大 enterprise-vue2 provider，而是保持其边界稳定，为 modern provider 并存提供参考实现，并证明 Kernel 协议可以同时服务企业实现与现代实现。企业 provider 的价值更多在于作为“企业实现参考基线”，而不是继续膨胀成长期唯一实现。

### 10.10 本章结论

本章确定了 `enterprise-vue2 provider` 的核心边界：

1. **`enterprise-vue2 provider` 是运行时适配层，不是统一内核。**
2. **公司组件库只能作为 Provider 能力来源，被选择性包装、受控暴露与风险隔离。**
3. **`Ui* -> Sf*` 映射必须由 Kernel 协议主导，不能由底层实现反向主导协议。**
4. **Provider 必须采用白名单核心组件包装策略，不能退化为全量透传层。**
5. **page recipe 的标准本体归 UI Kernel，Provider 只负责企业实现承接，不复用旧 page 骨架作为标准。**
6. **全量 `Vue.use` 公司组件库不允许作为 AI 生成默认入口。**
7. **MVP 以建立可控映射闭环和风险隔离为目标，不追求覆盖企业组件库全部能力。**

---

## 11. 前端生成约束体系

### 11.1 章节目标

本章用于定义 Ai_AutoSDLC 在前端生成阶段的**直接约束体系**。

### 11.2 约束体系的定位

#### 11.2.1 为什么需要前端生成约束体系

仅有 PRD / spec、Contract、UI Kernel 和 Provider 还不足以保证生成结果稳定。AI 在真实 coding 过程中仍可能出现页面结构自由漂移、绕过 wrapper 直接用底层组件、偏离 validation contract、继续写裸样式，以及在长上下文下突破 hard rules 等问题。因此需要在生成阶段建立一套直接作用于页面实现的受控约束面。

#### 11.2.2 约束体系的作用

前端生成约束体系的作用是减少 AI 自由度、把常见偏差前置拦住、为后续 Checker / Gate 提供稳定判定对象、让 Contract 与 Kernel 真正进入代码生成主链路，并把例外控制在可追踪、可检查、可修复的范围内。

#### 11.2.3 约束体系在整体架构中的位置

从总体架构看，本章的约束体系位于 `Contract -> UI Kernel -> 前端生成约束体系 -> 代码生成 -> Gate / Recheck / Fix Loop`。它关注的是在代码真正被生成出来之前与生成过程中，AI 能做什么、不能做什么、只能在什么条件下做什么。

#### 11.2.4 治理对象范围

本章定义的前端生成约束，主要作用于以下对象：

- AI 新生成页面代码
- UI Kernel wrapper
- Provider adapter
- 与页面生成直接相关的模板与生成链路

本章约束**不追溯治理公司组件库内部历史源码**，也不将所有既有前端存量代码默认纳入同一治理范围。

对于现存项目，本章约束体系的默认作用方式是：

- 对新增页面和新增区域采用标准模式
- 对存量页面的改动区域采用增量约束模式
- 对未改动 legacy 区域以兼容执行口径记录与观察，不默认要求一次性整改

### 11.3 约束体系总览

MVP 阶段，前端生成约束体系由五类约束组成：

1. page recipe 约束
2. component whitelist
3. frontend hard rules
4. minimal token / naked-value 规则
5. 例外声明与豁免机制

#### 11.3.1 约束生效阶段分层

前端生成约束并非在同一阶段同时生效，而应按生成链路分为三层：

1. 生成前置条件
2. 生成中限制
3. 生成后校验输入

对于现存项目，生成中限制和生成后校验还应结合 `compatibility_profile` 判断执行强度：

- 标准模式页面：严格执行全部约束
- 增量约束页面：对新增/改动区域严格，对存量区域记录但不一刀切阻断
- 采用兼容执行口径的页面：以发现问题和阻止扩散为主

#### 11.3.2 约束引用必须显式可追踪

页面生成阶段不允许依赖不可见、不可追踪的隐式全局默认值来决定约束集合。每个页面至少应能够解析出明确的：

- `recipe declaration`
- `component whitelist ref`
- `token rules ref`
- `hard rules set`

### 11.4 Page Recipe 约束

#### 11.4.1 Page Recipe 约束的作用

page recipe 约束用于确保页面不从空白结构自由拼装、同类页面有统一骨架、页面区域角色不混乱、页面状态表达有基本一致性，并让 Checker 能基于 recipe declaration 做结构对照。

#### 11.4.2 生成阶段必须遵守的基本规则

MVP 阶段至少要求：

1. 每个 AI 新生成页面必须绑定一个 recipe declaration
2. 页面结构必须以声明的 page recipe 标准本体为主
3. 不允许以自由原生结构替代 recipe 语义区
4. 页面区域必须服从 recipe 定义的 `required / optional / forbidden` 边界
5. 页面若存在例外，必须通过结构化 Contract 声明

#### 11.4.3 MVP 首批 Recipe 约束范围

- `ListPage`
- `FormPage`
- `DetailPage`

#### 11.4.4 Recipe 约束与页面例外的关系

> **例外可以存在，但 recipe 不能被页面实例反向重写。**

### 11.5 Component Whitelist

#### 11.5.1 Whitelist 的作用

component whitelist 用于限制 AI 的默认组件入口，确保页面只通过受控 `Ui*` 协议生成，不直接面向 `Sf*` 组件，也不大面积使用原生结构手搓基础组件，从而让 Provider 与 Checker 能共享同一组件控制面。

#### 11.5.2 MVP 首批白名单范围

MVP 阶段首批白名单至少包括 `UiButton`、`UiInput`、`UiSelect`、`UiForm`、`UiFormItem`、`UiTable`、`UiDialog`、`UiDrawer`、`UiEmpty`、`UiSpinner`、`UiPageHeader`。这批组件足以支撑首批 `ListPage / FormPage / DetailPage` 的生成闭环。

#### 11.5.3 白名单约束规则

MVP 阶段至少要求：

1. 页面生成默认只能使用白名单中的 `Ui*` 组件
2. 不允许把 `Sf*` 组件作为页面开发默认入口
3. 不允许通过原生结构手搓替代基础语义组件
4. 若某页面必须使用非白名单能力，必须通过例外声明进入 Contract
5. 非白名单能力不能直接作为“临时方便做法”进入默认路径
6. 已不维护的 legacy 组件不得作为新增代码默认入口；如业务必须临时使用，只能通过 Legacy Adapter 且需进入结构化例外声明。

#### 11.5.4 白名单的阶段演进

MVP 先控制最核心的高频组件入口；P1 再扩展到 `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiToolbar`、`UiPagination`、`UiSection`、`UiCard` 等更多结构型与页面型语义组件；P2 再根据 modern provider 的实际需求扩展，但仍保持“先定义 Kernel 协议，再进入 whitelist，再进入 Provider 承接”的顺序。

### 11.6 Frontend Hard Rules

#### 11.6.1 Hard Rules 的定位

Hard Rules 是前端生成中**不可突破的底线规则**。

#### 11.6.2 Hard Rules 分类

MVP 阶段的 Hard Rules 分为两类：

##### 1. 绝对禁止类

默认不可豁免，一旦出现即直接视为违规。例如：

- 直接修改 props
- 绕过 Kernel Wrapper / Provider Adapter，直接使用底层 `Sf*` 组件作为默认入口
- 通过页面实现反向重写 UI Kernel 标准协议
- 在已声明进入新治理链的区域继续引入新的 legacy 组件依赖或 legacy page 结构
- 新增代码继续直接复制 legacy 组件用法

##### 2. 受控例外类

这类规则原则上应遵守，但在极少数情况下，可通过结构化例外声明进行受控偏差。例如：

- 少量 whitelist 受控扩展
- 少量 token / layout 受控豁免
- 经 Provider 包装后开放的少量非默认能力

即使是受控例外，也必须满足：

- 结构化声明
- 可追踪
- 可被 checker / gate 感知
- 不得反向修改标准本体

#### 11.6.3 Hard Rules 的生成约束作用

Hard Rules 在生成阶段的作用包括：

1. 限制模型默认输出路径
2. 明确告诉 AI 哪些局部便利不可接受
3. 为后续 lint / AST / gate 提供硬判定基线
4. 防止长上下文中因局部完成度而突破底线

必须强调：

> **Hard Rules 不是建议项，而是默认必须成立的生成边界。**

> **Hard Rules 的“不可突破”主要指对默认生成路径而言；仅极少数被明确定义为可例外的规则，才允许在结构化、可追踪、可检查前提下受控偏差。**

### 11.7 Minimal Token / Naked-value 规则

#### 11.7.1 为什么首期必须有 token / naked-value 规则

当前前端生成的一个突出问题是样式表达失控，例如裸 `hex / rgb / rgba` 颜色、裸阴影、大面积裸间距、大量内联 `style`，以及页面之间视觉语言漂移。首期虽然不建设完整 token 平台，但必须至少建立最小样式底线，否则页面会继续表现为“逻辑能跑、结构大致对、但视觉极不稳定”。

#### 11.7.2 MVP 规则范围

MVP 阶段至少要求禁止裸 `hex` 颜色、裸 `rgb / rgba` 颜色、裸阴影值、大面积裸 spacing / 尺寸值，以及在页面层使用内联 `style` 写核心视觉表达。这里的“核心视觉表达”主要指色彩、阴影、间距、边框和密度等直接影响页面一致性的值。

#### 11.7.3 规则作用边界

这些规则的目的不是首版就完成完整 design token 治理，而是先挡住最明显的视觉失控，为 P1 / P2 的完整 token 体系预留升级路径，并让 Checker 能识别“明显不受控的样式实现”。因此，MVP 的 minimal token / naked-value 规则是底线约束，不是完整视觉设计系统。

### 11.8 例外声明与豁免机制

#### 11.8.1 为什么必须存在例外机制

如果没有例外机制，约束体系会过于僵硬，无法处理现实项目中的特殊页面结构、特定业务组件需求、必要的非白名单能力、特定 token / layout 例外和历史兼容场景的过渡处理。但如果例外机制不受控，又会反过来破坏整个治理体系。

#### 11.8.2 例外机制的基本原则

例外必须同时满足：

1. 结构化声明
2. 受控范围
3. 可被 checker 识别
4. 可追踪责任对象
5. 默认关闭，按需开启

#### 11.8.3 例外可作用的对象

MVP 阶段允许受控例外的对象主要包括 recipe declaration 偏差、component whitelist 豁免、token / naked-value 特殊豁免、hard rules 的极少数受控例外，以及经 Provider 包装后的特定扩展能力开放。

#### 11.8.4 不允许的例外

以下做法在本方案中明确禁止：

- 通过例外声明实质性重写 UI Kernel 语义组件协议
- 通过例外声明实质性重写 page recipe 标准本体
- 通过备注文字临时说明替代结构化豁免
- 用例外机制长期掩盖底层实现失控
- 将本应进入 whitelist 的能力长期放在“临时例外”路径上

#### 11.8.5 例外的优先级与覆盖边界

为避免例外机制破坏整体控制面，本方案明确以下优先级顺序：

1. **UI Kernel 标准本体 + 不可豁免 Hard Rules**
2. **页面声明的 recipe declaration / whitelist / token rules / hard rules set**
3. **结构化例外声明**

其含义是：

- 例外声明只能在已声明 scope 内，对页面或模块做受控偏差
- 例外声明不能覆盖 UI Kernel 标准本体
- 例外声明不能覆盖不可豁免 Hard Rules
- 例外声明只能对可例外对象生效，并接受 checker / gate 检查

对于 legacy 相关例外，还必须满足：

- 例外仅在声明的 `scope` 内有效
- 例外不能把 legacy 用法从局部扩展为默认模式
- 例外不能覆盖“禁止继续扩散 legacy 依赖”这一底线

### 11.9 生成阶段的约束执行顺序

#### 11.9.1 执行顺序原则

前端生成约束不应无序叠加，而应按以下顺序形成控制面：

1. Contract 先确定页面是什么
2. Kernel 先确定页面应该怎么组织
3. Whitelist 决定能用什么组件入口
4. Hard Rules 决定哪些底线不能突破
5. Token Rules 决定视觉表达底线
6. 例外声明决定哪些偏差被受控承认

#### 11.9.2 为什么需要顺序

如果没有这一顺序，容易出现“先写代码，再补 Contract”“先用底层组件，再补 whitelist”“先违反 hard rules，再靠备注豁免”“先写裸样式，再补 token 解释”等做法，这会让生成约束失去“前置控制面”的意义。

### 11.10 MVP / P1 / P2 演进边界

#### 11.10.1 MVP

MVP 约束体系目标是先建立 recipe / whitelist / hard rules / token rules / 例外机制的最小闭环，优先控制高频失控点，不追求一次性把所有前端规范全部规则化。MVP 更强调可执行、可检查、可回修，以及可与现有项目流程接上。

#### 11.10.2 P1

P1 将在 MVP 基础上增强更完整的 recipe 合规约束、更大的 whitelist 覆盖面、更细粒度的 token 规则、更丰富的状态与交互要求，以及更成熟的例外分类机制。

#### 11.10.3 P2

P2 重点不是继续堆规则，而是让约束体系能够同时服务 `enterprise-vue2 provider`、`modern provider`、多 theme pack 和更复杂的外部系统页面，验证这套约束体系既 Provider 无关，也可以承载多风格输出。

### 11.11 本章结论

本章确定了前端生成约束体系的核心边界：

1. **page recipe 约束页面结构，且页面必须服从 recipe declaration。**
2. **component whitelist 约束默认组件入口，页面不得直接面向底层 `Sf*` 组件生成。**
3. **Hard Rules 是不可突破底线，不是建议项。**
4. **minimal token / naked-value 规则用于建立首期最小视觉控制面，而不是完整设计系统。**
5. **所有例外都必须结构化声明，并接受 checker / gate 约束。**
6. **前端生成约束必须按 Contract → Kernel → Whitelist → Hard Rules → Token Rules → Exceptions 的顺序形成控制面。**
7. **MVP 只建立最小闭环，P1 / P2 在同一约束骨架上扩展。**

本章主要约束新增与改动，不对所有存量代码一刀切；例外是受控偏差，不是标准重写权。

---

## 12. Gate / Recheck / Auto-fix 设计

### 12.1 章节目标

本章用于定义 Ai_AutoSDLC 前端治理方案中的**检查、回检与修复闭环**。

### 12.2 闭环定位与设计目标

#### 12.2.1 闭环定位

Gate / Recheck / Auto-fix 不是附加能力，而是本方案真正从“规则文档”升级为“工程治理系统”的关键层。

#### 12.2.2 设计目标

本章闭环设计的目标是：

1. 让规则可执行
2. 让违规可识别
3. 让漏项可回检
4. 让修复可定向进行
5. 让结果可重新验证

### 12.3 闭环总体主线

闭环主线如下：

**页面 / wrapper / adapter 生成完成**
→ **checker / gate 执行**
→ **生成 violation / coverage / drift 报告**
→ **recheck 发现漏项或偏差**
→ **转换为 fix input**
→ **auto-fix 定向修复**
→ **重新 verify**
→ **通过后进入 close / report**

### 12.4 MVP Gate Matrix

#### 12.4.1 MVP Gate 的定位

MVP 阶段不追求完整前端质量平台，而是建立最小但有效的 gate 矩阵，优先覆盖高频失控点和已合同化对象，让规则从“文档说明”真正进入可阻断、可报告、可修复的工程链路。

#### 12.4.2 MVP 首批 Gate 范围

MVP 阶段建议至少包括以下 gate：

1. i18n Missing Key Check
2. Validation Coverage Check
3. Vue2 Hard Rule Check
4. Recipe Compliance Check
5. Component Whitelist Check
6. Minimal Token / Naked-value Check

#### 12.4.3 MVP Gate 的输入来源

MVP Gate 的输入至少包括：

- 页面代码
- UI Kernel wrapper
- Provider adapter
- `page metadata`
- `recipe declaration`
- `i18n contract`
- `validation contract`
- `hard rules set`
- `whitelist ref`
- `token rules ref`
- 结构化例外声明

#### 12.4.4 兼容执行口径

对于现存项目，MVP 阶段不新增第二套 gate 体系，而是在同一套 gate matrix 上引入兼容执行口径。

其目标不是对所有历史问题一刀切阻断，而是：

- 识别新增/改动区域是否继续引入 legacy 用法
- 识别是否绕过 Legacy Boundary 新增危险依赖
- 识别是否在应进入新治理链的区域继续复制旧模式
- 对存量历史问题做记录、分级和迁移跟踪

其基本原则是：

- 对新增和改动严格
- 对存量和未改动区域先记录、后分级推进
- 重点阻止“继续变坏”

建议统一执行强度为三档：

- **Strict**：新页面 / 标准模式页面
- **Incremental**：改动区域严格、存量区域记录
- **Compatibility**：以阻止继续变坏和记录债务为主

### 12.5 检查输出设计

#### 12.5.1 输出类型

前端检查输出至少分为四类：

1. `Violation Report`
2. `Coverage Report`
3. `Drift Report`
4. `legacy expansion report`

`legacy expansion report` 用于描述：

- 本次改动是否引入了新的 legacy 依赖
- 是否扩大了 Legacy Boundary
- 是否在可迁移区域继续复制旧模式
- 是否违反了“新增与改动必须收口”的基本原则

#### 12.5.2 输出必须机器可消费

检查输出不能只是自然语言诊断，而必须是机器可消费的结构化结果。至少应包含：

- `rule_id`
- `severity`
- `scope`
- `owner/page_id`
- `source_ref`
- `target_file / target_block`
- `message`
- `expected_fix_type`
- `related_contract_ref`

### 12.6 Recheck 设计

#### 12.6.1 Recheck 的定位

Recheck 不是重复执行一次相同 Gate，而是用于发现生成阶段未显性暴露的漏项、Contract 与实现之间的隐性漂移、修复后引入的新偏差，以及例外声明与实际实现不一致等问题。

#### 12.6.2 Recheck 的触发时机

MVP 阶段至少建议在以下时机触发 Recheck：初次生成完成后进入 `verify` 前、Gate 失败并完成 fix 后再次进入 `verify` 前、`execute` 之后准备 `close / report` 前，以及必要时在关键页面或关键变更上做额外复查。

#### 12.6.3 Recheck 的重点检查对象

MVP 阶段 Recheck 重点关注：

- i18n 漏项
- validation 漏实现
- recipe 偏差
- whitelist 漏控
- Contract 漂移
- 结构化例外是否已正确声明并落地
- 是否在本次改动后扩大了 legacy 用法范围
- 是否在声明进入新治理链的区域中仍存在未被替换的新增 legacy 入口

#### 12.6.4 Recheck 输出

Recheck 输出仍然必须是机器可消费的结构化 artifact，例如：

- `recheck.report.json`
- `recheck.fix-input.json`

### 12.7 Auto-fix 设计

#### 12.7.1 Auto-fix 的定位

Auto-fix 用于对 Gate / Recheck 输出的结构化问题进行定向修复。它的目标不是重新生成整页，而是在保持页面主结构与已通过部分稳定的前提下，修复指定违规项与漏项。

#### 12.7.2 Auto-fix 的输入

Auto-fix 至少应基于以下输入：Violation Report、Coverage Report、Drift Report、Recheck 输出、相关 Contract refs，以及涉及页面 / wrapper / adapter 的目标文件定位。只有这样，修复才能聚焦到明确 rule、明确文件和明确 contract 差异。

#### 12.7.3 Auto-fix 的基本原则

1. 定向修复，不整页重写
2. 优先修复硬违规
3. 不允许修复时实质性改写 Kernel 标准本体
4. 修复后必须重新 verify

对于 legacy 场景，Auto-fix 的默认目标不是自动完成大规模迁移重构，而是：

- 修复新增/改动区域中的明显违规
- 将直接 legacy 调用替换为 Legacy Adapter 或 `Ui*` 入口
- 补齐 Contract / 例外声明 / 边界标识
- 阻止 legacy 继续扩散

不以首版自动修复全面替换历史组件为目标。

#### 12.7.4 MVP Auto-fix 范围

MVP 阶段建议优先支持以下类型的修复：

- i18n key 缺失补齐
- validation contract 覆盖缺失补齐
- 裸文案替换为 i18n key
- 裸颜色 / 裸阴影 / 内联视觉值替换
- 非白名单入口替换为 `Ui*` wrapper
- props / `v-model` 类 Vue2 违规修复
- 缺失例外声明补齐或违规实现回退

### 12.8 例外、违规与修复的优先级关系

#### 12.8.1 判定优先级

在 gate / recheck / fix 中，优先级顺序应保持与第 11 章一致：

1. **UI Kernel 标准本体 + 不可豁免 Hard Rules**
2. **页面声明的 recipe declaration / whitelist / token rules / hard rules set**
3. **结构化例外声明**
4. **具体实现代码**

#### 12.8.2 修复优先级

MVP 阶段建议按以下顺序处理：

1. 绝对禁止类 Hard Rule 违规
2. recipe / whitelist 违规
3. i18n / validation 漏项
4. token / naked-value 违规
5. 受控例外与 Contract 漂移问题

### 12.9 与现有 Ai_AutoSDLC 阶段的接入

#### 12.9.1 与 verify 的接入

`verify` 阶段负责：

- 运行 checker / gate
- 生成 Violation Report / Coverage Report / Drift Report / legacy expansion report
- 触发 Recheck
- 生成 Fix Input

#### 12.9.2 与 execute 的接入

`execute` 阶段负责：

- 消费 Fix Input
- 执行定向修复
- 回写页面 / Wrapper / Adapter
- 将修复结果重新送回 verify

#### 12.9.3 与 close / report 的接入

`close / report` 阶段负责：

- 沉淀违规收敛情况
- 沉淀 Contract 覆盖情况
- 输出治理效果指标
- 发现长期高频违规类型与 legacy 扩散类型，为后续规则优化提供依据

### 12.10 MVP / P1 / P2 演进边界

#### 12.10.1 MVP

MVP 阶段重点是：

- 建立最小 gate matrix
- 建立最小 Recheck
- 建立针对高频问题的 Auto-fix
- 形成 verify → execute → verify 的最小闭环

MVP 阶段，前端治理闭环还需支持存量项目的最小兼容能力，包括：

- **同一套 gate matrix 的兼容执行口径**
- `legacy expansion report`
- 新增/改动区域优先治理
- 对存量历史问题以报告和迁移索引为主

#### 12.10.2 P1

P1 可增强更完整的 recipe compliance、更强的 drift 检查、更成熟的 Recheck agent、更广的 Auto-fix 覆盖面，以及初步 visual / a11y 检查接入。

#### 12.10.3 P2

P2 可继续增强面向 modern provider 的统一 gate、更完整的 multi-theme / token 检查、更强的 visual / interaction quality gate，以及更成熟的跨 Provider 一致性检查。

### 12.11 本章结论

本章确定了 Gate / Recheck / Auto-fix 的核心边界：

1. **Gate / Recheck / Auto-fix 是前端治理闭环的核心，不是附加检查步骤。**
2. **MVP 先建立最小 gate matrix，优先覆盖 i18n、validation、Vue2 hard rules、recipe、whitelist、token 违规。**
3. **检查输出必须机器可消费，才能真正进入 Fix Loop。**
4. **Recheck 用于发现漏项、漂移与修复后偏差，不是简单重复 gate。**
5. **Auto-fix 以定向修复为原则，不以整页重写为默认路径。**
6. **verify / execute / close 将共同承接前端治理闭环，而不是另起前端 pipeline。**
7. **P1 / P2 在同一闭环架构上增强，而不是重建另一套治理系统。**

至此，围绕：

- 输入规格与 Contract
- UI Kernel
- enterprise-vue2 Provider
- 前端生成约束
- Gate / Recheck / Auto-fix

的核心设计章节已经完整闭环。
