# Harness-Grade Telemetry & Observer Architecture Design

## Goal

为 AI-SDLC 建立一套长期稳定的 `Harness-Grade Telemetry & Observer Architecture`，使框架能够在不增加执行 agent 心智负担、不允许执行者自我美化的前提下，对真实执行行为形成客观、可追溯、可审计、可治理的闭环。

这份文档是全景架构设计，不是 `004` 的补丁，也不是只服务当前问题的临时方案。它先定义长期架构边界，再冻结首期 V1 baseline，并给出后续 planning frame。

## Scope Positioning

- 本文定义一套长期可扩展的 collector / raw trace / observer / governance / gate architecture。
- 本文不把首期实现范围误写成长期架构边界。
- 本文首期 rollout 只覆盖 `self_hosting`，但内核设计必须兼容未来 `external_project`。
- 本文从第一天就要求 `gate-capable`，但自动阻断按收口面分阶段启用。

## 1. Positioning And Constitutional Rules

这份文档定义未来一段时间内 AI-SDLC 的 `Harness-Grade Telemetry & Observer Architecture`。它要长期回答四类问题：

- 谁实际执行了什么。
- 系统客观观测到了什么。
- 哪些结论来自可追溯证据。
- 哪些治理决策可以进入收口面。

系统总体由五个角色组成：

- `Executor`：负责实际实施。
- `Collector`：负责在宿主/CLI/bridge 边界进行确定性采集。
- `Raw Trace Store`：负责保存 append-only 原始事实。
- `Observer`：负责只读事实层并生成结构化治理对象。
- `Gate Consumer`：负责在 `verify / close / release` 等收口面消费高置信、可追溯的治理结论。

### 1.1 Architecture Rules

1. `Raw Trace Store` 是系统唯一事实真值层。所有 `reports`、`incidents`、`evaluations`、`violations`、gate 决策都只能从事实层派生，不得反写、修正或覆盖原始事实。
2. `Collector` 是宿主侧确定性采集器，不是智能体。它只负责稳定采集边界事实，不负责高层解释，不负责治理判断。
3. 事实层可以包含不同采集来源，例如 `auto`、`agent_reported`、`human_reported`，但这些来源的信号强度不同，不应被混同为相同可信度；可信度由上层显式建模，不在事实层隐式抹平。
4. `Observer` 只读事实层，输出结构化治理对象。它的产物必须是机器可消费、可引用证据、可进入 gate 的结构化对象，而不是仅供阅读的自由文本。
5. `Observer` 的输出不是最终真理，而是基于给定 `observer version`、`policy` 与 `profile` 的派生结果；不同版本 observer 可以得出不同解释，但不得改变事实层。
6. `Gate Consumer` 原则上只消费 `Observer` 派生出的结构化治理对象，而不直接扫描 `Raw Trace Store`；只有极少数人工诊断或 fallback 场景才允许工具直接读取事实层。
7. `Gate Consumer` 只消费高置信、可追溯、带来源闭包的 observer 结果。凡是不带 `evidence refs`、不带 `confidence` 分层、不能证明来源链的结论，都不得直接进入收口面的自动阻断路径。
8. `Executor` 不拥有事实层与治理层的最终写权。开发 agent 或 worker 可以执行动作，也可以提供低信任补充说明，但不得拥有 `raw trace`、`evaluation`、`violation`、最终 `incident explanation` 的最终控制权。
9. `self_hosting` 与 `external_project` 必须共用同一套 collector、trace contracts 和 observer framework。差异主要体现在默认启用项、治理强度、gate 策略与 repo policy，而不应演化为两套底层实现。
10. 默认轻量采集常开，解释与治理按阶段升级。V1 在架构上必须 `gate-capable`；在执行策略上，仅在 `verify / close / release` 等收口面启用高置信自动阻断，`execute` 默认不阻断。
11. 缺失观测必须显式暴露为 `coverage_gap / unknown / unobserved`。系统可以拒绝下结论，但不得伪造完整链路。

## 2. Data Model, Profiles, And Modes

## 2.1 Data Model Layers

### 2.1.1 Fact Objects

`Fact Objects` 记录“发生了什么”。它们是系统的原始事实记录层，承载执行边界上被观测到的事件、证据和上下文，但不承担治理判断职责。

核心对象包括：

- `raw trace event`
- `evidence`
- `execution span`
- `command result`
- `test result`
- `patch result`
- `file write result`
- `trace context`
- `source metadata`

`trace context` 至少要稳定携带：

- `goal_session_id`
- `workflow_run_id`
- `step_id`
- `worker_id`
- `agent_id`
- `parent_event_id`

上述对象可以在实现上表现为统一事件模型加 `evidence/metadata` 扩展，也可以拆成多个专门对象；本节定义的是语义分层，不预设具体代码结构必须一一对应。

事实层虽然不承担治理判断，但仍必须满足统一的 trace contracts，包括：

- 稳定主键链
- 来源标记
- 时间语义
- append-only 写入纪律
- 可引用 evidence 语义

事实层不等于非结构化原始字节堆。`Fact Objects` 仍需满足统一 trace contracts，能被 resolver、observer 和 source closure 机制稳定引用，而不是简单把 stdout、log 文件或任意文本堆积为“事实”。

事实层约束：

- append-only，不允许上层对象回写、覆盖或修正。
- 允许不同 capture source 共存，但不得抹平来源差异。
- 不做可信度归一化，不在这一层判断哪条事实更可信。
- 不直接产出违规、通过、阻断等治理语义。

### 2.1.2 Derived Interpretation Objects

`Derived Interpretation Objects` 表达“基于事实，我们能判断什么，或者不能判断什么”。

典型对象包括：

- `coverage evaluation`
- `constraint finding`
- `anomaly hypothesis`
- `mismatch finding`
- `confidence-bearing interpretation`
- `unknown`
- `unobserved`
- `coverage_gap`

解释层约束：

- 只能从 `Fact Objects` 派生，不能自造脱离事实层的解释。
- 可以输出肯定结论，也可以输出“不足以判断”的结构化结果。
- 必须显式携带 `confidence`、`evidence refs`、`observer version`、`policy`、`profile` 等生成条件。
- 结果允许随 observer 版本、策略和 profile 演进而变化，但不得反向修改事实层。
- 原则上应能从同一事实层在给定 `observer version / policy / profile` 下重复计算得到。
- 它们是可再生派生结果，不是一次性不可追溯结论。

### 2.1.3 Governance Objects

`Governance Objects` 表达“这些判断如何进入治理流程与收口决策”。

典型对象包括：

- `violation`
- `incident report`
- `audit summary`
- `evaluation summary`
- `gate decision payload`

这一层必须区分两类用途：

- 给人和流程看的治理产物：`incident report`、`audit summary`、`evaluation summary`
- 给 gate 消费的治理输入：`gate decision payload`

`gate decision payload` 只是供 `Gate Consumer` 使用的派生对象，不等于 gate 动作已经执行。它至少应携带：

- `decision subject`
- `confidence`
- `evidence refs`
- `source closure status`
- `observer version`
- `policy`
- `profile`
- `mode`

治理层约束：

- 必须满足来源闭包要求。
- 必须带 `source_evidence_refs`、`source_object_refs`、置信度与版本信息。
- 只能追加派生，不得回写事实层。
- 可以具有 `draft / reviewed / published / accepted / fixed` 等生命周期。
- 生命周期变化不得改变其底层来源引用，只能追加状态与派生说明。

### 2.1.4 Layering Summary

- `Fact Objects` 记录“发生了什么”。
- `Derived Interpretation Objects` 表达“基于事实，我们能判断什么 / 不能判断什么”。
- `Governance Objects` 表达“这些判断如何进入治理流程与收口决策”。
- 上层对象可以引用下层对象。
- 下层对象不能被上层对象反向修改。

## 2.2 Profile Strategy

### 2.2.1 Shared Kernel

`self_hosting` 与 `external_project` 必须共用同一套底层内核。共享内核至少包括：

- `trace contracts`
- `collector framework`
- `Raw Trace Store`
- `Observer pipeline`
- `Governance Object schema`
- `source closure discipline`
- `gate decision payload` contract

### 2.2.2 self_hosting

`self_hosting` 用于 AI-SDLC 框架仓自身的开发、自举、审计和自演进治理。

默认特点：

- 更完整的 collector
- 更积极的 observer
- `verify / close / release` 更积极消费高置信结论
- 可接 `framework defect backlog` 与 self-evolution governance

### 2.2.3 external_project

`external_project` 用于普通业务仓、产品仓或消费 AI-SDLC 能力的外部项目。

默认特点：

- 更轻的默认策略
- 不默认启用框架自举专属治理
- 不把 `framework defect backlog` 或 self-hosting 语义强加给业务仓

### 2.2.4 Compatibility Rule

profile 不改变底层事实模型。profile 改变的是：

- 默认启用项
- 治理强度
- gate 策略
- repo policy

`self_hosting` 与 `external_project` 的差异主要是默认行为差异，而不是底层语义差异。

## 2.3 Runtime Modes / Governance Modes

`lite`、`strict`、`forensics` 是治理运行档位，不是简单的采集套餐。它们的差异主要是运行策略差异，而不是对象模型差异。

### 2.3.1 Mode Definition

- `lite`：低摩擦日常开发模式。轻量采集常开，解释和治理克制，以 advisory 为主。
- `strict`：正式收口与高纪律治理模式。更严格的 coverage 和更积极的 gate 消费。
- `forensics`：事故调查、争议事件和专项审计模式。提高保留等级、解释深度与证据闭包要求。

### 2.3.2 What Modes Control

mode 至少控制以下维度：

- `collector coverage level`
- `observer depth / aggressiveness`
- `coverage gap strictness`
- `artifact generation scope`
- `gate consumption policy`
- `retention / evidence preservation level`
- `human review expectation`

mode 首先影响解释与治理强度，其次才影响采集强度。

任何 mode 变化都必须留下最小变更记录，至少包括：

- `old_mode`
- `new_mode`
- `changed_at`
- `changed_by`
- `reason`
- `applicable_scope`

### 2.3.3 Typical Combinations

典型组合包括：

- `self_hosting + lite`
- `self_hosting + strict`
- `external_project + lite`
- `external_project + strict`
- `any + forensics`

`forensics` 是专项模式，不默认等于实时常驻 observer。

### 2.3.4 Invariants

mode 不可改变的架构不变量：

- `trace contract`
- `fact semantics`
- `source closure principle`
- `append-only discipline`
- `profile identity`

mode 可以改变采集覆盖度、解释强度、治理动作和保留策略，但不能回写历史事实。

## 3. End-to-End Operational Flow

`profile` 决定系统默认站在哪个治理立场，`mode` 决定在这个立场下采用多强的运行策略，而 `flow` 决定这些策略在运行链路中的什么时点生效。

### 3.1 Runtime Sequence

主链时序固定为：

`Executor -> Collector -> Raw Trace Store -> Observer -> Governance Objects -> Gate Consumer`

顺序约束：

1. `Executor / Collector` 产出事实
2. `Raw Trace Store` append 成功
3. 触发 `Observer`
4. 产出 derived / governance objects
5. 在收口面由 `Gate Consumer` 决策

最重要的顺序原则是：**原始事实落盘成功优先于任何解释开始**。

### 3.2 Trigger Points

系统存在三类不同触发点：

- `collector trigger point`
- `observer async trigger point`
- `gate consumption point`

`collector trigger point` 发生在命令执行、测试结束、patch 应用、文件写入、worker 生命周期变化等边界。

`observer async trigger point` 是解释开始点，不是阻断动作点。首期 observer 触发策略固定为 `step end / batch end` 后异步启动。

`gate consumption point` 发生在 `verify / close / release` 等收口面。observer 触发点和 gate 消费点不是一回事。

### 3.3 Human Intervention Points

人工介入必须分层：

- 事实层人工补记：`human_reported` 事实、审批记录、人工证据定位、人工说明
- 治理层人工决策：`triage`、`waive`、`accept`、`dismiss`、`publish`、`reviewed`
- 人工 `override / fallback`

人工治理是正式路径，不是系统失败时才出现的例外。

### 3.4 Fallback And Degradation

fallback 必须分层设计。

当 `Collector` 或 `Raw Trace Store` 发生局部故障时：

- 若不影响主任务执行安全，可允许执行链降级继续，但必须显式记录事实层缺口。
- 若破坏事实层最低完整性，不得假装系统仍处于可审计状态。

至少以下场景应视为 `hard fail` 候选，而不是普通 advisory 降级：

- 主键链无法建立
- raw trace 根不可写
- append-only 纪律失效
- 当前处于 `close / release / publish` 等收口面，且 `source closure` 判定器自身损坏

implementation plan 应进一步把这些场景细分为两类：

- `hard-fail default`
- `policy-overridable hard-fail candidate`

这样实现时可以明确哪些属于默认必须中断，哪些只允许在显式 policy 下例外降级。

当 `Observer` 或 `source closure` 相关派生流程发生故障时：

- 可允许执行链继续
- 但应拒绝自动给出高置信治理结论

当 `Gate Consumer` 位于收口面且发现 `source closure` 不成立时：

- 治理对象不得继续升级为 `published`
- 应退回 `reviewed / draft / blocked` 等可追溯状态

### 3.5 Mode / Profile Application Points

`profile` 与 `mode` 必须在运行链路中有明确绑定时点。

- `profile` 应在 `session / run` 启动时绑定到执行上下文。
- `mode` 也应显式绑定，但允许在受控条件下升级。
- 任何 mode 变化都必须留下结构化记录。
- `Gate Consumer` 可以在收口面再次读取 repo policy 决定消费强度，但不得篡改该次 run 已绑定的事实语义。

## 4. Scope, Phasing, And Delivery Roadmap

Section 4 同时定义两层边界：

- `Architecture Scope`
- `Delivery Scope`

全景架构先定义长期边界，不等于首期全部交付。

## 4.1 Architecture Scope

长期覆盖范围包括：

- `self_hosting + external_project`
- `lite / strict / forensics`
- `workflow / tool / evaluation / human / governance`
- `verify / close / release / merge / publish / finalize`
- future multi-agent / external tracing / replay / self-evolution

## 4.2 First Delivery Scope

首期交付范围：

- `self_hosting first`
- `step / batch` 后异步 observer
- `gate-capable` architecture
- automatic blocking only on `verify / close / release`
- high-value control points only
- minimal governance loop

## 4.3 Explicit Deferrals

明确后置的能力包括：

- 全量 `file_read` 自动采集
- 常驻实时 observer
- external tracing backend / remote control plane
- 自动 `improvement proposal` 生成
- 跨 session 全局 viewer
- 更复杂的 root-cause 自动推断
- 多 agent 深度关联分析
- 外部导出 / replay 集成

后置不是删除。后置必须保留：

- schema slots
- payload contracts
- compatible extension points

后置能力默认不得以“实验开关”名义偷偷侵入默认路径，尤其不得影响 `external_project` 的默认体验；任何提前启用都必须以显式 profile / mode / policy 记录为前提。

## 4.4 Phased Roadmap

roadmap 按“基础设施 -> 解释闭环 -> 治理闭环 -> 扩展能力”推进。

- `V1`：事实层与最小闭环
- `V1.5`：更稳定的解释和治理消费
- `V2`：profile rollout 与更强治理
- `V2.5 / V3`：平台化扩展、多 agent 深度分析、external tracing、viewer、自演进

## 4.5 Rollout Strategy

rollout 策略固定为：

- `self_hosting first`
- `external_project later`

这是一种部署顺序，不是内核分叉。

外部仓 rollout 必须坚持：

- backward compatibility
- lazy adoption
- no forced burden from self-hosting semantics

## 5. Design Principles, Risks, And Architectural Guardrails

Section 5 把这套架构为什么要这样设计、最容易在哪里做歪、以及为了防止做歪必须遵守哪些硬规则写成架构宪法。

## 5.1 Design Principles

- `facts first`
- `derived never rewrites facts`
- `gate-capable from day one`
- `shared kernel, differentiated policy`
- `minimize rewrite pressure`
- `auditability over convenience`
- `staged governance escalation`
- `human governance is first-class`

## 5.2 Primary Risks

最容易做歪的方向包括：

- `collector/observer boundary collapse`
- `raw trace bypass`
- `governance object direct write by executor`
- `advisory-to-blocker drift`
- `external_project burden creep`
- `observer overreach / false certainty`
- `contract erosion under deferred features`

## 5.3 Architectural Guardrails

必须硬性遵守的规则包括：

- gate never directly consumes raw trace
- executor never owns final governance writes
- inferred never alone blocks high-risk closure
- source closure required before published
- deferred != deleted model semantics
- profile differences must not fork core contracts
- mode changes must be explicit and recorded
- bounded surfaces must remain read-only
- auditability over convenience

## 5.4 Failure Signals

说明架构开始跑偏的信号包括：

- `published` artifact without resolvable source refs
- `coverage_gap` 被静默吞掉
- `external_project` 默认出现 `framework defect backlog`
- `status / doctor` 开始做深扫或隐式 rebuild
- collector 中出现高层解释逻辑
- execute 默认路径出现常态化自动阻断
- observer 在证据不足时仍输出高置信根因
- deferred feature 要求修改核心 trace contract
- gate payload 缺少最小字段
- 人工 override 被实现成改写历史事实

## 6. Concrete Design Baseline For V1

Section 6 不重新定义架构，它只冻结全景架构下首期必须实现的最小切片。

## 6.1 V1 Baseline Positioning

V1 baseline 是全景架构的首期冻结切片，不是另一套简化版架构。它要证明：

- 事实层、解释层、治理层、gate 消费层已经是同一套体系
- 首期虽只覆盖部分 collector 和部分治理消费点，但这些能力沿着 shared kernel 工作
- 后续扩展不需要推倒事实模型、主键链、source closure discipline 或 gate payload contract

V1 必须是 `gate-capable but staged enablement`：

- contract 上支持 gate decision payload、confidence、evidence refs、source closure
- 自动阻断先只落在 `verify / close / release`
- `execute` 默认 advisory-only

## 6.2 Must Freeze In V1

V1 必须冻结：

- trace contract
- 主键链
- source refs
- source closure
- append-only discipline
- gate-capable payload contract
- shared kernel
- bounded `status / doctor`
- `self_hosting first`

同时明确：

- `Must Freeze In V1`
- `Deferred But Contract-Preserved`

## 6.3 Collector Baseline

V1 collector baseline 的明确边界：

- `command execution`
- `test result`
- `patch apply`
- `file write`
- `worker lifecycle`
- `trace context propagation`

V1 首期明确不强制自动采集的 collector 面包括：

- `full file_read`
- `complete conversation capture`
- `real-time observer-side capture expansion`

如纳入人工输入，只能以明确事实边界纳入，例如：

- `human approval`
- `manual note`
- `human_reported fact`

## 6.4 Observer Baseline

解释层在 V1 至少必须产出：

- `coverage evaluation`
- `constraint finding / mismatch finding`
- `unknown / unobserved / coverage_gap`

在固定 `observer_version + policy + profile + mode` 条件下，V1 observer baseline 产出的 `coverage / mismatch / unknown-family` 结果应可重复计算并得到相同结构化输出。

治理层在 V1 至少必须产出：

- `violation`
- `audit summary`
- `gate decision payload`

`evaluation summary` 在 V1 不作为必须正式启用的治理产物；如首期不启用，应视为 `contract-preserved deferred artifact`。

`incident report` 可以后置，但 contract 必须保留。

## 6.5 Gate Consumption Baseline

V1 首期只有以下收口面允许消费 observer 的高置信 blocker 结论：

- `verify`
- `close`
- `release`

`execute` 默认仍 advisory-only。

V1 gate 消费的对象必须满足：

- 带 `confidence`
- 带 `evidence refs`
- 带 `source closure` 状态
- 带 `observer version / policy / profile / mode`
- 能映射到当前收口对象

## 6.6 Rollout Baseline

V1 rollout 起点固定为：

- `profile = self_hosting`
- observer trigger = `step / batch end async`
- gate consumption = `verify / close / release only`
- `external_project later`

所有 deferred capability 满足原则：

- 推迟交付
- 不推迟内核兼容

## 7. Implementation Planning Frame

Section 7 不新增 scope；它把 V1 baseline 转成施工框架，同时保持架构顺序、降低未来重构压力，并让验收标准始终对齐全景设计。

## 7.1 Planning Dimensions

V1 至少拆成这 8 个实施维度：

- `contracts`
- `collector`
- `raw trace store`
- `observer`
- `governance objects`
- `gate consumption`
- `CLI / bounded surfaces`
- `rollout / compatibility`

实施 owner boundary 至少包括：

- `contract / normalization owner`
- `collector owner`
- `store / writer / resolver owner`
- `observer / evaluator owner`
- `governance generator owner`
- `gate consumer owner`
- `CLI / doctor / status owner`
- `smoke / compatibility owner`

这里的 owner boundary 用于实施主责和验收边界，不等于唯一修改者；跨层协作允许存在，但不得绕过统一接口、contract 和分层纪律。

## 7.2 Task Ordering Principles

优先级原则固定如下：

- `facts before interpretation`
- `interpretation before governance`
- `governance before rollout breadth`
- `self_hosting before external_project`
- `async observer before real-time ambition`

## 7.3 Work Breakdown Model

任务拆解应同时满足：

- `by layer`
- `by dependency`
- `by minimal vertical slice`
- `by smoke-testable milestone`

推荐的垂直切片：

- `contracts + store + writer`
- `collector baseline + raw trace append`
- `observer baseline + unknown-family outputs`
- `violation / audit summary / gate decision payload`
- `verify / close / release consumption`

## 7.4 Acceptance Framework

验收标准必须闭环导向。每一阶段至少证明：

- 事实层是否稳定落盘
- 解释层是否可再生、可拒绝下结论
- 治理层是否满足来源闭包与生命周期规则
- 收口面是否只消费满足最小条件的结果

以下边界默认 failing tests 先行：

- `trace contract`
- `parent-chain / source closure`
- `append-only vs mutable`
- `collector baseline`
- `observer baseline`
- `gate consumption baseline`
- `fallback / negative smoke`

每个关键 capability 最好同时具备 paired positive / negative smoke，尤其是：

- `source closure`
- `gate consumption`
- `mode / profile drift`
- `collector boundary`

## 7.5 Planning Guardrails

implementation plan 必须显式禁止：

- 业务模块或 executor 直接写最终治理对象
- gate 直接扫描 raw trace
- deferred feature 通过删模型、删字段、删语义来“先落地”
- 把 `self_hosting` 专属治理语义硬塞进 `external_project` 默认路径
- 把 execute 默认策略偷偷改成阻断优先
- 在 collector 层塞入高层解释逻辑
- 缺少最小字段的结果直接进入收口 blocker
- mode/profile 在运行中隐式漂移而不留记录

## 8. Open Questions / Decision Log

Section 8 只做两件事：

- 记录尚未锁死、但后续必须决策的问题
- 记录已经锁死、且会影响架构或 rollout 的关键决策

Open Questions 不得反向打开已在 Sections 1-7 冻结的边界。Decision Log 只记录会影响 contract、layering、rollout、gate strategy、compatibility 的关键决策。

## 8.1 Open Questions

以下问题保留为后续决策项，但不得反向打开已冻结边界：

- `can-after-v1` `forensics` 模式首期是否允许更强 retention 默认值
- `can-after-v1` `external_project` rollout 的最小门槛是什么
- `can-after-v1` `human approval / manual note` 首期是否作为 V1 baseline collector input 强制纳入
- `can-after-v1` `gate decision payload` 与现有 release / merge / finalize 等收口面的统一适配层形态

## 8.2 Decision Log

以下关键决策已冻结：

- 采用独立 spec，不回写 `004`
- `self_hosting first`
- observer 首期 `step / batch end async`
- `gate-capable from day one`
- automatic blocking only on `verify / close / release`
- `Raw Trace Store` 是唯一事实层
- profile 与 mode 是正交维度
- `self_hosting` 与 `external_project` 共用共享内核
- `execute` 默认 advisory-only
- V1 manual input surface 保持最小 CLI 形态：`open-session`、`close-session`、`record-event`、`record-evidence`、`record-evaluation`、`record-violation`
- V1 中 `incident report` 保持 `contract-preserved deferred artifact`，不作为必须正式启用的治理产物
- deferred capability 必须 `contract-preserved`

## Appendices

## Appendix A. Frozen Enums Baseline

V1 附录基线至少冻结以下 enum 语义：

- `profile`: `self_hosting | external_project`
- `mode`: `lite | strict | forensics`
- `confidence`: `low | medium | high`
- `capture_mode`: `auto | agent_reported | human_reported | inferred`
- `trace_layer`: `workflow | agent_action | tool | human | evaluation`
- `trigger_point_type`: `collector | observer_async | gate_consumption`
- `root_cause_class`: `prompt | context | rule_policy | middleware | workflow | tool | eval | model_behavior | human_process`
- `suggested_change_layer`: `prompt | context | rule_policy | middleware | workflow | tool | eval`
- `evaluation.status`: `pending | passed | failed | waived`
- `violation.status`: `open | triaged | accepted | fixed | dismissed`
- `artifact.status`: `draft | generated | reviewed | published | archived`
- `governance_review_status`: `draft | reviewed | accepted | fixed | dismissed | waived`
- `source_closure_status`: `unknown | incomplete | closed`
- `gate_decision_result`: `advisory | allow | warn | block`

Appendix A 是 V1 的单一枚举语义基线来源；实现不得要求调用方再回正文中拼装这些最小枚举集合。

## Appendix B. Critical Control Points Baseline

V1 必须覆盖的最小高价值 control point 语义：

- command execution completed
- test result recorded
- patch applied
- file written
- worker started
- worker finished
- worker failed
- coverage gap emitted
- high-confidence violation emitted
- gate decision evaluated

附录定义的是语义基线，不要求当前代码结构必须一一对应命名。

## Appendix C. Gate-Capable Minimum Payload

最小 `gate decision payload` 必须包含：

- `decision_subject`
- `decision_result`
- `confidence`
- `evidence_refs`
- `source_closure_status`
- `observer_version`
- `policy`
- `profile`
- `mode`
- `generated_at`

## Appendix D. Failure Signals Checklist

架构 review / code review 时优先检查：

- 是否出现 raw trace bypass
- 是否出现 executor direct governance write
- 是否出现 collector 层高阶解释逻辑
- 是否出现 external_project burden creep
- 是否出现 coverage gap 被吞掉
- 是否出现 source closure 不成立仍 published
- 是否出现 mode/profile 漂移未记录
- 是否出现 deferred feature 侵蚀 contract
