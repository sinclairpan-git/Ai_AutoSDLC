# 功能规格：Stage 0 Init Dual-Path Project Onboarding Baseline

**功能编号**：`094-stage0-init-dual-path-project-onboarding-baseline`  
**创建日期**：2026-04-11  
**状态**：formal baseline 已冻结；已完成两轮对抗收敛  
**输入**：[`../010-agent-adapter-activation-contract/spec.md`](../010-agent-adapter-activation-contract/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../093-stage0-installed-runtime-update-advisor-baseline/spec.md`](../093-stage0-installed-runtime-update-advisor-baseline/spec.md)、[`../../src/ai_sdlc/routers/bootstrap.py`](../../src/ai_sdlc/routers/bootstrap.py)、[`../../src/ai_sdlc/routers/existing_project_init.py`](../../src/ai_sdlc/routers/existing_project_init.py)、[`../../tests/unit/test_bootstrap_router.py`](../../tests/unit/test_bootstrap_router.py)、[`../../tests/flow/test_existing_project_flow.py`](../../tests/flow/test_existing_project_flow.py)、[`../../USER_GUIDE.zh-CN.md`](../../USER_GUIDE.zh-CN.md)

> 口径：`094` 要冻结的不是“init 命令还能再多做什么”，而是 Stage 0 onboarding 在两类起点上的正式合同。它把“已有项目接入闭环”和“全新项目空仓初始化”拆成双路径真值，解决零文档、低命令接入体验与真实仓库事实之间的张力；但它不重写 `010` 的 adapter activation truth，也不提前吞并 `014` 的 frontend runtime attachment truth。

## 问题定义

当前仓库已经具备一套可以工作的 `init` reality：

- `detect_project_state()` 已把项目分成 `greenfield / existing_project_initialized / existing_project_uninitialized` 三态
- `greenfield` 路径会创建 `.ai-sdlc` 基线与默认 profile
- `existing_project_uninitialized` 路径会执行深扫并生成 knowledge baseline、索引与记忆文件
- `init` 已经与 adapter 安装链路相邻，但 activation 仍由 `010` 单独定义

真正缺的不是“有没有 init”，而是**没有一份冻结的双路径 onboarding contract** 来回答下面五个问题：

- existing project 的 machine truth 应该来自哪里，legacy 文档、仓库证据、默认 bootstrap 文件谁优先
- greenfield project 可以默认生成到哪一步，哪些默认值只是占位，哪些可以被视为正式事实
- `tech-stack.yml` 在 greenfield 和 existing 两条路径上的语义是否一致，还是只能作为 provisional baseline
- init 是否可以顺手替用户完成 frontend attach、方案选择、provider 决策，还是只能留下 handoff
- existing attach 完成后，何时才算“框架接入闭环已建立”，以及它与 `adapter activate`、后续 formal workitem/前端 runtime 之间是什么顺序

如果不把这层先冻结，后续很容易再次漂移成三种互相打架的口径：

- 现有仓库明明完成了深扫，却仍被一个 `bootstrap-default` 的 `tech-stack.yml` 假装成“已识别技术栈”
- greenfield 项目只建了空壳，却被产品文案误说成“已自动完成栈识别与工程方案绑定”
- init 顺手偷做 frontend attach / provider 决策 / adapter 激活，导致 `010`、`014` 和后续前端方案 spec 的 ownership 被混掉

因此，`094` 的目标是冻结一条最小但严格的 Stage 0 dual-path baseline：明确 state classifier、双路径产物、事实层级、handoff 边界与成功标准，为后续 helper machine contract、CLI Stage 0 hook、IDE/AI binding 与 notice surfacing 提供稳定上游。

## 范围

- **覆盖**：
  - `greenfield / existing_project_uninitialized / existing_project_initialized` 的正式语义
  - existing attach path 与 greenfield bootstrap path 的目标、产物与边界
  - project truth hierarchy：operator input、repo evidence、legacy corpus、bootstrap default 的主从关系
  - knowledge baseline、project memory、`tech-stack.yml` 与 initialization metadata 的正式角色
  - init 与 `010` adapter activation、`014` frontend runtime attachment 之间的 handoff 边界
  - “零文档、低命令”接入体验在双路径下的最低可执行合同
- **不覆盖**：
  - 在本 work item 中直接实现新的 stack detector、frontend provider 选择器或 project template market
  - 把 init 升级成自动生成 product spec、plan、tasks 或前端业务页面的入口
  - 重写 `010` 已冻结的 `selected / installed / acknowledged / activated` activation truth
  - 重写 `014` 已冻结的 frontend artifact attachment、runtime auto-scan 或 provider runtime handoff
  - 把 legacy 文档导入、README 解析或业务知识抽取扩张成单独的知识工程产品

## 已锁定决策

- `init` 的正式目标是建立 **Stage 0 onboarding baseline**，不是直接完成开发工作流全部后续步骤
- 双路径必须同时成立：
  - `existing_project_uninitialized` 走 **attach-and-baseline** 路径
  - `greenfield` 走 **bootstrap-and-declare** 路径
- existing path 的 canonical truth 必须优先来自当前仓库的 machine-observable evidence，而不是默认 profile 或 legacy prose
- project truth 必须遵守不可越权的单向 precedence：
  1. operator-confirmed input（仅限 operator-owned choice 或 ambiguity resolution）
  2. current repo evidence
  3. legacy corpus
  4. bootstrap defaults
- operator-confirmed input 只能用于 agent target、显式 scope、operator declaration 等 operator-owned choice，或在 repo evidence 不足时做歧义消解；不得推翻已成立的 observed repo fact
- 低优先级层只能解释、补空或提示 follow-up，不得回写、覆盖或 tie-break 更高优先级层
- greenfield path 允许写入 bootstrap defaults，但这些 defaults 只代表“框架初始声明”，不代表“已识别真实项目技术栈”
- `tech-stack.yml` 在没有 evidence-backed stack resolver 之前，只能被视为 provisional profile；尤其在 existing path 中，不得因为文件存在就宣称“栈已识别完成”
- 当前 reality 下，init 还没有独立的 frontend hint output surface；`094` 只为未来可选的人类可读 follow-up guidance 预留边界，不在本 work item 内引入新的 machine-readable artifact contract
- 若未来输出 frontend follow-up guidance，也只能是只读、临时、human-readable 的提示语；不得默认完成 frontend runtime attachment、provider 选择、solution baseline 绑定、active `spec_dir` 预填或跨 spec 写入
- existing path 完成后，框架只能宣称“接入基线已建立”；是否真正完成 adapter activation，仍以 `010` 为准
- greenfield path 完成后，框架只能宣称“空仓基线已建立”；不得误报“已有工程事实已识别”“已可进入受控开发”或“前后端方案已自动就绪”

## 双路径模型

### 1. ProjectStateClassifier

`init` 的第一步必须是单一 project-state classifier，至少稳定区分：

- `greenfield`
- `existing_project_uninitialized`
- `existing_project_initialized`

该 classifier 的职责只有**判定 onboarding 起点**，不是做完整技术栈识别、业务领域建模或 adapter 激活判断。

### 2. Existing Attach Path

当仓库已存在代码、依赖清单、构建入口或等价工程痕迹，但尚未完成 AI-SDLC formal bootstrap 时，`init` 必须进入 existing attach path。该路径的核心目标是：

- 承认“这是一个已有工程，不是空壳项目”
- 对仓库做深扫并生成 knowledge baseline
- 把 direct repo evidence、结构化索引与 project memory 建成后续 Stage 0 的 canonical baseline
- 不把 legacy 文档或 bootstrap default 冒充成 machine-confirmed truth

### 3. Greenfield Bootstrap Path

当仓库不存在足以证明“已有工程”的代码或构建痕迹时，`init` 必须进入 greenfield bootstrap path。该路径的核心目标是：

- 以最低命令数建立 `.ai-sdlc` 基线与 governance skeleton
- 提供可继续执行显式后续步骤的正式起点；其中受控开发入口的直接前置动作是完成 `010` 定义的最低 adapter gate。当前 reality 下，`adapter activate` 只记录 operator acknowledgement，不证明 host verified activation
- 明确告诉系统和用户：此时多数项目事实仍未被发现，只是完成了框架接入底座

## 用户故事与验收

### US-094-1

作为 **existing project operator**，我希望 `init` 能直接把旧仓库接入 AI-SDLC，而不是要求我先手写一套 formal 文档，这样我才能在零文档、低命令条件下建立可继续演进的基线。

**验收**：

1. Given 仓库存在代码或依赖清单且未初始化，When 我运行 `ai-sdlc init .`，Then 系统必须进入 existing attach path，而不是按空项目处理  
2. Given existing attach 完成，When 我查看 `.ai-sdlc/project/memory/*` 与初始化元数据，Then 可以看到深扫生成的 knowledge baseline，而不是只有空壳 profile  
3. Given existing attach 路径中存在 `bootstrap-default` profile，When 我查看 formal docs，Then `094` 必须明确它不能单独作为“真实技术栈已识别”的证据

### US-094-2

作为 **greenfield operator**，我希望空仓项目只靠少量命令就能建立可继续工作的框架底座，但又不想被误导成“系统已经知道我的实际架构和方案”。

**验收**：

1. Given 仓库为空或只存在极少量非工程痕迹，When 我运行 `ai-sdlc init .`，Then 系统必须进入 greenfield bootstrap path  
2. Given greenfield bootstrap 完成，When 我查看 formal docs，Then 可以明确读到这些 defaults 属于 bootstrap declaration，而不是 evidence-backed project truth  
3. Given greenfield bootstrap 完成，When 我继续执行后续标准路径，Then formal docs 必须明确后续仍需按 `010` 完成 activation，并按 formal workitem / frontend downstream spec 继续推进

### US-094-3

作为 **reviewer / framework maintainer**，我希望能在 formal docs 中直接读到 canonical truth order 与 handoff 边界，这样 init 不会再次演变成“什么都顺手做一点”的模糊入口。

**验收**：

1. Given 我审阅 `094` formal docs，When 我检查事实优先级，Then 可以明确读到 operator input、repo evidence、legacy corpus、bootstrap default 的主从顺序  
2. Given 我审阅 `094` formal docs，When 我检查 frontend handoff，Then 可以明确读到 init 不默认 auto-attach frontend runtime，也不默认写入 frontend solution baseline  
3. Given 我审阅 `094` formal docs，When 我检查 adapter 语义，Then 可以明确读到 existing attach / greenfield bootstrap 都不等于 activation 完成

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-094-001 | `094` 必须把 `init` 正式定义为 Stage 0 dual-path onboarding baseline，而不是泛化的“项目智能启动器” |
| FR-094-002 | `094` 必须明确 `existing_project_uninitialized` 与 `greenfield` 是两条不同目标、不同产物、不同 truth semantics 的路径 |
| FR-094-003 | `094` 必须明确 `existing_project_initialized` 的语义是“formal bootstrap 已建立”，而不是“所有后续 activation / frontend / workitem 都已完成” |
| FR-094-004 | `094` 必须冻结 project truth hierarchy 的硬序列：`operator-confirmed input（限 operator-owned choice / ambiguity resolution） > current repo evidence > legacy corpus > bootstrap defaults` |
| FR-094-005 | operator-confirmed input 不得推翻已成立的 observed repo fact；它只能定义 operator-owned choice 或在 evidence 不足时参与歧义消解 |
| FR-094-006 | 低优先级 truth layer 只能解释、补空或提示 follow-up，不得覆盖、反向修正或作为更高优先级层的 tie-break |

### Existing Attach Contract

| ID | 需求 |
|----|------|
| FR-094-007 | 对 `existing_project_uninitialized`，`init` 必须执行 attach-and-baseline，而不是退化为 greenfield 空壳创建 |
| FR-094-008 | existing attach 必须以 machine-observable repo evidence 为第一事实源，生成可供后续 Stage 0 消费的 knowledge baseline、结构化索引与 project memory |
| FR-094-009 | existing attach 可以吸收 legacy corpus 作为辅助上下文，但不得让 README、历史文档或人工 prose 覆盖 direct repo evidence |
| FR-094-010 | existing attach 结束后，系统必须能明确表达“接入基线已建立，但 activation / frontend attachment / formal workitem 仍是下游步骤” |
| FR-094-011 | existing attach 中生成的 `tech-stack.yml` 或等价 profile，在 evidence-backed stack resolver 缺位时只能是 provisional profile；不得单独作为“真实技术栈已识别完成”的依据 |

### Greenfield Bootstrap Contract

| ID | 需求 |
|----|------|
| FR-094-012 | 对 `greenfield`，`init` 必须建立最小 `.ai-sdlc` bootstrap skeleton，使 operator 无需预先手写 formal docs 即可进入后续标准路径 |
| FR-094-013 | greenfield bootstrap 允许写入默认 governance/profile 文件，但必须明确这些内容是 bootstrap declaration，而不是 observed project fact |
| FR-094-014 | greenfield bootstrap 不得伪造 knowledge baseline、repo evidence 或“已扫描完成”的状态 |
| FR-094-015 | greenfield bootstrap 后，最直接的受控开发前置动作必须是按 `010` 完成最低 adapter gate；当前 `adapter activate` 只能表示 acknowledged，不得被 init 或后续主线误表述为 host verified activation |
| FR-094-016 | greenfield bootstrap 后的其他后续动作必须通过显式命令继续推进；其中 `run --dry-run` 或等价受控执行入口只能在 `010` 认可的 activation 条件满足后出现，`workitem init` 也不得被 init 静默替代 |

### Canonical Artifact And Memory Hierarchy

| ID | 需求 |
|----|------|
| FR-094-017 | `project-state.yaml` 必须是 formal bootstrap 是否建立的 canonical machine state；它不表达 activation 完成与否，也不表达 frontend runtime 是否已接线 |
| FR-094-018 | existing attach 生成的 project memory 与知识索引必须被定义为 Stage 0 canonical onboarding artifacts，而不是“可有可无的附属报告” |
| FR-094-019 | 由 scan 派生的 memory summary 文档必须从属于更底层的 evidence/index truth，不得反向覆盖证据层 |
| FR-094-020 | legacy corpus 若被纳入 onboarding，只能作为辅助引用源；其可信度不得高于当前仓库直接可观察证据 |
| FR-094-021 | bootstrap-default profile、placeholder decisions 或等价默认文件必须被标注为 provisional / operator-to-refine，而不是 observed / verified |

### Frontend And Adapter Handoff Boundary

| ID | 需求 |
|----|------|
| FR-094-022 | `094` 必须明确 adapter selection / activation contract 由 `010` 负责；`init` 在双路径下都不得把“adapter 文件已安装”表述为“治理已激活” |
| FR-094-023 | 当前 work item 不引入新的 frontend hint artifact、machine-readable state 或持久化 surface；若未来补充 follow-up guidance，也只能是 human-readable 提示语 |
| FR-094-024 | 上述 guidance 不得包含具体 provider 推荐、具体 `spec_dir` 建议、runtime attachment state、active scope 预填或任何可被机器消费的 trigger shape |
| FR-094-025 | `094` 必须明确 init 不得自动写入或刷新 frontend solution baseline、provider binding、runtime attachment artifact 或跨 workitem spec 产物 |
| FR-094-026 | `094` 必须明确后续 frontend runtime attachment、artifact locality 与 active `spec_dir` 约束仍以 `014` 及其下游 work item 为准 |

### Idempotence And Honest State

| ID | 需求 |
|----|------|
| FR-094-027 | 对已初始化项目重复执行 `init` 时，系统必须保持幂等，不得把 existing attach 重新伪装成首次 greenfield bootstrap |
| FR-094-028 | 若仓库处于 existing path 但证据不足以确认真实技术栈，系统必须诚实输出“evidence pending / provisional”语义，而不是给出确定性架构结论 |
| FR-094-029 | 若项目只有历史 `.ai-sdlc` 痕迹但 formal bootstrap 缺失，`094` 必须把它纳入需要 reconcile 的 onboarding 入口，而不是视为已完整初始化 |
| FR-094-030 | 双路径的任何失败、缺口或 provisional 状态都必须以 machine-readable state 或显式文案诚实暴露，不得静默冒充“已准备就绪” |

### Implementation Handoff

| ID | 需求 |
|----|------|
| FR-094-031 | `094` 必须为后续 stack detection、Stage 0 hook、IDE/AI notice surfacing 与 frontend downstream specs 提供单一上游 formal baseline |
| FR-094-032 | `094` 必须明确后续实现优先补的是 evidence-backed stack resolver、dual-path CLI guidance 与 handoff metadata，而不是让 init 继续吞并下游能力 |
| FR-094-033 | `094` 必须为测试矩阵保留双路径最小覆盖：state classifier、greenfield no-fake-baseline、existing deep-scan baseline、re-init idempotence、mixed host activation non-equivalence |

## 关键实体

- **ProjectStateClassifier**：把仓库起点判定为 `greenfield / existing_project_uninitialized / existing_project_initialized` 的入口真值
- **Existing Attach Path**：面向已有工程仓库的 attach-and-baseline 流，负责建立 knowledge baseline 与 project memory
- **Greenfield Bootstrap Path**：面向空仓项目的 bootstrap-and-declare 流，负责建立最低治理骨架与后续入口
- **Repo Evidence**：从当前仓库结构、依赖、源码、测试和构建痕迹中直接观察到的 machine-observable facts
- **Legacy Corpus**：README、历史文档、旧说明等可被引用但不能凌驾于 direct repo evidence 的辅助语料
- **Bootstrap Declaration**：在 greenfield 或缺少证据时写入的默认 profile / placeholder 文件，语义上属于待 operator 或后续 detector 收敛的初始声明
- **Onboarding Baseline**：由 `project-state.yaml`、knowledge baseline、project memory 与初始化元数据共同构成的 Stage 0 起点
- **Frontend Follow-Up Guidance**：未来可选的人类可读 init 提示语，用于提醒存在 frontend/full-stack 后续工作；它不是 artifact、本地 machine state，也不是 `014` 的触发器

## 成功标准

- **SC-094-001**：formal docs 能清楚区分 existing attach 与 greenfield bootstrap 的目标、产物与 truth semantics，不再把两条路径混成同一种“init 成功”  
- **SC-094-002**：reviewer 能从 `094` 直接读出 operator input、repo evidence、legacy corpus、bootstrap default 的主从顺序  
- **SC-094-003**：existing path 不会再因为 `bootstrap-default` 的 `tech-stack.yml` 而被误读成“真实技术栈已识别完成”  
- **SC-094-004**：greenfield path 不会再被产品文案误写成“已深扫现有工程”或“已自动决定前后端方案”  
- **SC-094-005**：`010` activation truth 与 `014` frontend attachment truth 不会被 `094` 偷偷重写或提前吞并  
- **SC-094-006**：后续实现团队能够从 `094` 直接得到 dual-path CLI guidance、stack resolver 与 frontend handoff metadata 的优先补位方向

## 两轮对抗收敛

第 1 轮对抗补掉了三类实现漂移风险：

- project truth hierarchy 不再只是“四层并列”，而是冻结成不可越权的单向 precedence
- greenfield bootstrap 不再允许被误读成“已满足 activation gate”或“已可直接进入受控开发”
- frontend follow-up guidance 不再被允许携带 `active spec_dir`、provider 或 runtime trigger

第 2 轮对抗又补掉了三类口径漏洞：

- `operator-confirmed input` 被收紧为 operator-owned choice / ambiguity resolution，不能推翻已成立的 observed repo fact
- frontend guidance 被收回为“未来可选的人类可读提示语”，不在 `094` 中引入新的 artifact、state 或持久化 surface
- spec 明确承认当前 init reality 尚无独立 frontend hint output surface，避免把未来能力伪装成既成事实

---
related_doc:
  - "specs/010-agent-adapter-activation-contract/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/093-stage0-installed-runtime-update-advisor-baseline/spec.md"
  - "src/ai_sdlc/routers/bootstrap.py"
  - "src/ai_sdlc/routers/existing_project_init.py"
frontend_evidence_class: "framework_capability"
init_dual_path_scope: "stage0_onboarding_only"
init_dual_path_status: "formal_baseline"
---
