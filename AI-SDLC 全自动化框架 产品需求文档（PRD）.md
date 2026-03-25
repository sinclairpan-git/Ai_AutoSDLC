# AI-SDLC 全自动化框架 产品需求文档（PRD）

**版本**：v1.1  
**文档状态**：PRD 审核完善后，待进入自动化开发  
**产品名称**：AI-SDLC  
**目标版本**：RC1 → v1  
**文档用途**：作为 Agent 自动化开发的唯一产品需求基线  
**产品形态**：混合模式 — 规则/Prompt 文件集 + Python 轻量 CLI 辅助工具  
**实现语言**：Python 3.11+  
**交付方式**：用户手动拷贝文件到项目目录（未来可扩展为 pip install）

---

## 1. 产品概述

AI-SDLC 是一套面向真实软件研发场景的 **AI-Native SDLC 自动化框架**。  
它的目标不是只辅助写代码，而是让 Agent 能够在统一规则、状态、分支、上下文和质量门禁下，完成从需求输入到开发、测试、归档、恢复、并行协作的全流程工作。

### 1.1 产品交付形态

AI-SDLC 以**混合模式**交付：

1. **规则/Prompt 文件集**：一组 Markdown 规则文件、YAML 配置模板和 Prompt 模板，用户拷贝到项目的 `.ai-sdlc/` 目录后，AI Agent（Cursor / Codex / Claude Code 等）读取并遵循执行
2. **Python 轻量 CLI 工具**：提供项目初始化、状态查询、断点恢复、索引生成等辅助命令，不替代 Agent 的核心推理能力，仅处理机械化操作

用户获取与使用流程：
```
git clone ai-sdlc → 拷贝到项目 .ai-sdlc/ → CLI 初始化 → 显式执行启动命令（ai-sdlc run --dry-run）→ Agent 按规则执行 SDLC
```

### 1.2 产品与开发框架的边界

> **重要**：本产品的源代码与开发过程中使用的框架约束（工作区根目录下的 `autopilot.md`、`rules/`、`templates/` 等）严格隔离。前者是**开发产物**，后者是**开发约束**，二者在文件系统上不混用。

### 1.3 产品必须支持的能力

1. 新需求 / 新 PRD 开发
2. 线上问题修复
3. 开发中途需求变更
4. 常规维护任务
5. 已有项目初始化与结构化理解
6. docs/dev 双分支基线治理
7. 单 Agent 闭环执行
8. 多 Agent 并行开发
9. 上下文恢复与中断续跑
10. Native fallback 执行，不依赖第三方工具存活
11. spec-kit / superpowers 等第三方能力可插拔接入

---

## 2. 产品目标

### 2.1 核心目标

构建一套可正式投入使用的 AI-SDLC 自动化框架，使 Agent 能在尽量少的人为中断下完成研发流程。

### 2.2 具体目标

1. 用户输入一句话想法、完整 PRD、线上问题描述或变更请求后，系统可自动识别工作类型并进入对应流程。
2. 对于已有项目，系统可先完成一次工程结构化初始化，形成长期可复用的工程知识基线。
3. 系统可基于 docs/dev 双分支模型建立明确基线，避免文档与开发漂移。
4. 系统可在任意阶段进行自动模式与人工确认模式切换。
5. 系统可在进程中断、上下文超限、窗口关闭等情况下快速恢复。
6. 系统可在模型/运行环境支持时进行多 Agent 并行开发，并保证边界、契约与汇合一致性。
7. 系统必须提供测试、审查、完成定义等质量门禁，避免“代码写了但不能算完成”。

---

## 3. 非目标

以下能力不属于 RC1 必须范围：

1. 多仓库联动编排
2. 企业审批流 / 合规审批系统
3. 分布式 swarm 级并行调度
4. Web 管控台 / 图形化编排平台
5. 复杂 release train 管理
6. 深度绑定某一个 IDE 的私有能力
7. 对所有语言框架进行完整语义级静态分析

---

## 4. 用户与角色

### 4.1 主要用户

#### 4.1.1 个人开发者

希望通过 Agent 完成从需求到实现的闭环开发。

可执行操作：
- 拷贝 AI-SDLC 到项目并运行 `ai-sdlc init` 初始化
- 输入需求（一句话 / PRD / 问题描述）后，先执行 `ai-sdlc run --dry-run` 启动工作流
- 运行 `ai-sdlc status` 查看当前流水线进度与状态
- 运行 `ai-sdlc recover` 从中断点恢复执行
- 在 confirm 模式下审查并确认/拒绝 Agent 产出
- 切换执行模式（auto ↔ confirm）
- 查看、搜索归档的执行日志和知识文档

#### 4.1.2 技术负责人 / 架构师

希望框架具备治理、恢复、分支、质量控制能力。

可执行操作：
- 配置 `.ai-sdlc/project/config/` 下的 quality-policy、branch-policy、parallel-policy
- 定义并冻结 governance 前置条件（tech profile、constitution、clarify）
- 审查 docs baseline（spec / plan / tasks）
- 配置质量门禁阈值和熔断器参数
- 审查多 Agent 并行的 contract 和 merge 结果

#### 4.1.3 产品经理 / 需求方

希望一句话想法或 PRD 能被自动转化为可执行开发计划。

可执行操作：
- 提交一句话想法、粗略描述或完整 PRD
- 参与 PRD Studio 的交互式引导补全
- 审查生成的 spec 和 task graph
- 提出变更请求（触发 Change Request Studio）

#### 4.1.4 维护 / 运维 / 值班工程师

希望线上问题能直接进入修复流程而非被迫写 PRD。

可执行操作：
- 提交 incident brief（现象 + 影响范围 + 严重程度 + 日志）
- 通过 Incident Studio 生成分析和修复计划
- 跟踪 hotfix 分支的执行进度
- 审查 postmortem 报告

### 4.2 系统角色

#### 4.2.1 Coordinator Agent

负责全局路由、规划、状态推进、并行调度、汇合与质量门禁。

职责与操作：
- 调用 Project Bootstrap Router 判断项目状态
- 调用 Work Intake Router 分类工作项
- 冻结 governance 前置条件
- 在并行模式下：切片任务、分配 Worker、冻结 contract、汇合验证
- 推进每个 gate 检查，决定 PASS / RETRY / HALT
- 维护 runtime.yaml 和 resume-pack.yaml

#### 4.2.2 Worker Agent

负责单个切片任务的实现、验证、摘要与交付。

职责与操作：
- 读取分配的任务切片和 working-set
- 在 allowed_paths 范围内执行代码变更
- 执行 TDD（Red → Green → Verify）
- 生成任务摘要写入 latest-summary.md
- 完成后向 Coordinator 报告状态

#### 4.2.3 Human Reviewer

在 confirm 模式或高风险场景下提供确认与审查。

职责与操作：
- 在确认卡出现时审查 Agent 产出
- 选择：继续 / 自动 / 查看 / 修改 / 终止
- 在高风险 gate（安全、合规、资金相关）上做最终决策
- 标注需要人工干预的 Open Questions

---

## 5. 核心问题定义

当前常见 AI 编程工作流存在以下问题：

1. 只支持“写代码”，不支持完整 SDLC
2. 只能处理新需求，无法优雅处理线上问题、变更请求、维护任务
3. 对已有项目理解不足，导致在存量工程上改动效率低、风险高
4. 上下文容易爆炸，中断后难恢复
5. 分支治理缺失，容易把所有改动堆到主线
6. 多 Agent 并行没有边界约束，容易重复开发、冲突、越界
7. 质量门禁弱，容易出现“看似完成、实际上不可交付”

---

## 6. 产品范围

### 6.1 必须覆盖的工作类型

1. `new_requirement`
2. `production_issue`
3. `change_request`
4. `maintenance_task`
5. `uncertain`

### 6.2 必须覆盖的生命周期

1. 项目判断
2. 已有项目初始化
3. 工作项分类
4. 需求/问题收口
5. 治理层冻结
6. docs baseline 建立
7. dev 执行
8. 测试/验证
9. 归档
10. 知识刷新
11. 恢复/接力

---

## 7. 核心产品原则

1. **Runner-first**：框架自身是主系统，第三方工具只是后端
2. **State authoritative**：运行状态必须 machine-readable
3. **Knowledge lean**：项目知识尽量用单文档 + 自动索引，而不是大量手工知识 YAML
4. **Project before Work**：先理解项目，再处理任务
5. **Baseline before Build**：先冻结 docs baseline，再进入 dev
6. **Parallelism is contractual**：并行必须先冻结 contract、边界、汇合规则
7. **Context externalized**：上下文必须落盘，不能依赖聊天窗口
8. **Quality is gated**：质量不是建议，而是正式 gate
9. **Portable by design**：CLI-first、文件驱动、多 IDE 可迁移

---

## 8. 产品核心能力

### 8.1 Project Bootstrap Router

#### 目标

判断当前项目属于哪种状态，并决定是否必须先做工程初始化。

#### 输入

- 当前仓库
- 项目目录
- 现有 `.ai-sdlc/` 状态
- 代码仓库扫描结果

#### 输出

- `greenfield`
- `existing_project_initialized`
- `existing_project_uninitialized`

#### 规则

- 如果是 `existing_project_uninitialized`，必须先执行 Existing Project Initialization Flow
- 未完成初始化时，不允许直接进入需求开发、问题修复或变更流程

---

### 8.2 Existing Project Initialization Flow

#### 目标

把“已有但未结构化的项目”转化为可长期复用的工程知识基线。

#### 核心原则

- **不可推导知识**：写入主文档
- **可推导事实**：自动生成索引
- **不要维护大量手写知识 YAML**

#### 结构化输出

##### A. 给 Agent 优先读取

位于：

- `.ai-sdlc/project/config/`
- `.ai-sdlc/project/bootstrap/`
- `.ai-sdlc/project/generated/`

包括：

- `project-state.yaml`
- `initialization-status.yaml`
- `knowledge-baseline-state.yaml`
- `knowledge-refresh-log.yaml`
- `project-config.yaml`
- `branch-policy.yaml`
- `quality-policy.yaml`
- `parallel-policy.yaml`
- `environment-policy.yaml`
- `repo-facts.json`
- `key-files.json`
- `api-index.json`
- `dependency-index.json`
- `test-index.json`
- `risk-index.json`

##### B. 给人和 Agent 共读

位于：

- `.ai-sdlc/project/memory/`

包括：

- `engineering-corpus.md`
- `codebase-summary.md`
- `project-brief.md`

#### `engineering-corpus.md` 必须包含

1. 一页摘要
2. 仓库地图
3. 模块边界与职责
4. 关键入口与关键文件
5. 核心数据模型 / 领域模型
6. 架构决策与理由
7. 非显式约定 / 代码规范
8. 外部集成说明
9. 已知风险与技术债
10. Open Questions

---

### 8.3 Work Intake Router

#### 目标

自动识别当前输入属于哪种工作类型，并进入对应流程。

#### 输入类型

- 自然语言需求
- 上传的 PRD
- 线上问题描述
- 变更请求
- 维护任务说明

#### 输出结构

```yaml
work_item_id: WI-YYYY-NNN     # YYYY = 4位年份, NNN = 当年自增序号（从 001 开始）
work_type: new_requirement | production_issue | change_request | maintenance_task | uncertain
severity: low | medium | high | critical
source: text | prd_upload | issue_report | manual
recommended_flow: prd_studio | incident_studio | change_studio | maintenance_studio | clarification
needs_human_confirmation: true | false
classification_confidence: high | medium | low   # 分类置信度
```

#### ID 生成规则

- `WI-YYYY-NNN` 中 YYYY 为当前年份，NNN 为当年全局自增序号
- 序号从 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 字段读取并递增
- 每次生成后立即写回，保证唯一性

#### 规则

- `uncertain` 不允许直接进入执行，必须进入**澄清流程**：
  1. 向用户展示分类困难的原因和可能的类型选项
  2. 用户选择后重新分类；若用户也不确定，标记为 `needs_human_confirmation: true` 并暂停
  3. 超过 2 轮仍无法确定 → HALT，记录原因，等待人工介入
- `production_issue` 不允许强行走完整 PRD 流程，必须走 Incident Studio 短路径
- `change_request` 必须触发暂停、影响分析和 rebaseline
- `classification_confidence: low` 时自动设置 `needs_human_confirmation: true`

---

### **8.4 Completion Studio**

#### **8.4.1 PRD Studio**

支持：

- 一句话想法 → PRD 草案

- 完整 PRD → readiness review

输出：

- PRD readiness

- 进入 spec/plan/tasks 的结构化输入

#### **8.4.2 Incident Studio**

输入：

- 现象

- 影响范围

- 严重程度

- 报错/日志

- 复现线索

输出：

- incident brief

- incident analysis

- incident fix plan

- incident tasks

- postmortem

#### **8.4.3 Change Request Studio**

输入：

- 变更描述（自然语言或结构化）
- 当前 work item 的 runtime 状态
- 当前 docs baseline 快照
- 变更原因和优先级

输出：

- 当前流程暂停确认
- 当前状态冻结快照
- change request 记录（含变更 ID、原因、影响范围）
- impact analysis（受影响的 spec/plan/tasks 条目列表）
- rebaseline record（新旧基线 diff）
- resume point（恢复位置和所需上下文）

#### **8.4.4 Maintenance Brief Studio**

输入：

- 维护任务描述（依赖升级、代码清理、性能优化等）
- 影响范围（涉及的模块/文件）
- 紧急程度

输出：

- lightweight brief（简化版需求摘要）
- small task graph（任务依赖图，通常 ≤ 10 个任务）
- execution path（推荐的执行顺序）

---

### **8.5 Governance Freeze**

#### **目标**

在 planning 前冻结治理层前置条件。

#### **必须冻结**

- tech profile

- constitution

- clarify

- quality policy

- branch policy

- parallel policy

#### **规则**

任意缺失时，不允许继续进入 docs baseline 或 dev execution。

---

### **8.6 Docs / Dev 双分支模型**

#### **分支类型**

- main

- feature/<id>-docs

- feature/<id>-dev

- feature/<id>-dev-aN

- hotfix/*

- release/*

#### **规则**

1. docs 分支负责：
   
   - spec
   
   - plan
   
   - tasks
   
   - task graph
   
   - docs baseline freeze

2. dev 分支负责：
   
   - 实现
   
   - 测试
   
   - 验证

3. 切分支前必须：
   
   - freeze 当前状态
   
   - commit / stash / checkpoint
   
   - 刷新 runtime / resume

4. 切换后必须：
   
   - baseline recheck
   
   - refresh working set
   
   - refresh progress

---

### **8.7 Planning & Execution**

#### **目标**

从治理层冻结后的输入，生成执行计划并驱动实现。

#### **必须产出**

- spec

- plan

- tasks

- task graph

- execution plan

#### **必须支持**

- dry-run

- real-run

- verify

- archive

- resume

---

### **8.8 Context Control Plane**

#### **目标**

保障上下文可控、任务可恢复。

#### **Work Item 核心状态文件**

每个 work item 最少保留：

1. work-item.yaml

2. governance.yaml

3. execution-plan.yaml

4. runtime.yaml

5. working-set.yaml

6. resume-pack.yaml

7. latest-summary.md

#### **规则**

- 不默认回放完整历史

- 不默认全仓扫描

- summary-first

- working-set-first

- 恢复优先使用：
  
  - resume-pack.yaml
  
  - working-set.yaml
  
  - latest-summary.md
  
  - project-brief.md

---

### **8.9 Multi-Agent Parallel Foundation**

#### **目标**

在模型/执行环境支持时，提高开发效率，同时保证边界与一致性。

#### **并行前置条件**

task graph 每个可并行任务必须声明：

- parallelizable

- parallel_group

- allowed_paths

- forbidden_paths

- interface_contracts

- merge_order

#### **角色**

- **Coordinator Agent**：切片、分配、冻结 contract、汇合验证

- **Worker Agent**：只处理自己的切片

#### **并行流程**

1. 串行冻结：
   
   - docs baseline
   
   - contract
   
   - assignment

2. 并行执行：
   
   - 多个 worker 分支

3. 汇合验证：
   
   - overlap detection
   
   - contract consistency
   
   - merge simulation
   
   - integration verify

---

### **8.10 Quality Gates**

必须内建以下 gate：

1. PRD Gate

2. Constitution / Clarify Gate

3. Review Gate

4. Done Gate

5. Verification Gate

6. Incident Postmortem Gate

#### **Done Gate 规则**

一个任务完成，不只要求：

- 代码实现

- 测试通过

- archive 已写

还要求：

- 若影响项目知识基线，则 **Knowledge Refresh 完成**

---

### **8.11 Knowledge Refresh Flow**

#### **背景**

已有项目初始化不是一次性动作。

每次任务结束后，面对的是“新的已存在项目状态”，因此项目知识必须增量更新。

#### **触发时机**

流程位置：

Execution
  -> Review / Done Gate
  -> Archive
  -> Knowledge Refresh
  -> Merge / Cleanup
  -> Handoff / Recover



#### **刷新分级**

##### **Level 0**

无需刷新项目知识

例如：文案、注释、小测试

##### **Level 1**

仅刷新自动生成索引

例如：少量文件、API、测试分布变化

##### **Level 2**

刷新索引 + 局部 patch 主知识文档

例如：模块职责变化、新增接口、新风险出现

##### **Level 3**

局部重初始化 / 基线重建

例如：大重构、模块拆分、技术栈迁移

#### **必须更新的文件**

- knowledge-baseline-state.yaml

- knowledge-refresh-log.yaml

按需更新：

- engineering-corpus.md

- codebase-summary.md

- project-brief.md

自动重生成：

- repo-facts.json

- key-files.json

- api-index.json

- dependency-index.json

- test-index.json

- risk-index.json

---

### **8.12 Native Backend（内置执行引擎）**

#### **目标**

提供一套基于文件系统的内置执行引擎，使 AI-SDLC 的核心流程在不依赖任何第三方插件（spec-kit、superpowers 等）的情况下可完整运行。Native backend 是框架的"默认后端"，第三方工具作为可选增强。

#### **核心能力**

1. **状态机驱动**：基于 `.ai-sdlc/` 下的 YAML 状态文件驱动流程推进，所有状态转换持久化到文件系统
2. **模板生成器**：从内置模板生成 spec、plan、tasks、execution-log 等产物骨架
3. **索引生成器**：扫描项目目录自动生成 repo-facts.json、key-files.json、api-index.json 等索引文件
4. **Gate 检查器**：读取 quality-policy 配置，自动检查每个阶段的 PASS / RETRY / HALT 条件
5. **Resume 引擎**：从 resume-pack.yaml 恢复执行上下文，重建 working-set
6. **Branch 管理器**：执行 docs/dev 双分支的创建、切换、合并操作（底层调用 git）

#### **CLI 命令（Python 实现）**

| 命令 | 作用 |
|------|------|
| `ai-sdlc init` | 初始化项目，创建 `.ai-sdlc/` 目录结构 |
| `ai-sdlc status` | 输出当前流水线状态面板 |
| `ai-sdlc recover` | 从断点恢复，加载 resume-pack |
| `ai-sdlc index` | 重新生成自动索引文件 |
| `ai-sdlc gate <stage>` | 手动运行指定阶段的门禁检查 |
| `ai-sdlc refresh` | 触发 Knowledge Refresh |

#### **与第三方后端的关系**

```
AI Agent 请求 → AI-SDLC Runner
                  ├── Native Backend（默认，文件系统驱动）
                  └── Plugin Backend（可选，spec-kit / superpowers / 自定义）
```

Runner 优先使用 Native Backend；当检测到已配置的 Plugin Backend 且其能力覆盖当前操作时，可委托给 Plugin 执行。Plugin 不可用时自动 fallback 到 Native。

---

## **9. 系统状态模型**

### **9.1 项目级**

- 配置

- 初始化状态

- 知识基线状态

- 知识刷新日志

- 工程知识主文档

- 自动生成索引

### **9.2 工作项级**

- 工作项状态
- 治理状态
- 执行计划
- 运行时状态
- 工作集
- 恢复包
- 最新摘要
- 产出物
- 归档

### **9.3 工作项状态转换**

```
created → intake_classified → governance_frozen → docs_baseline → dev_executing
                                                                      ↓
                                                                dev_verifying → dev_reviewed → archiving → knowledge_refreshing → completed
                                                                      ↓
                                                                  suspended (中断/变更请求)
                                                                      ↓
                                                                  resumed → dev_executing (回到执行)
```

| 转换 | 触发条件 | Guard |
|------|---------|-------|
| created → intake_classified | Work Intake Router 完成分类 | work_type ≠ uncertain，或 uncertain 已澄清 |
| intake_classified → governance_frozen | Governance Freeze 完成 | 所有 6 项治理前置条件已冻结 |
| governance_frozen → docs_baseline | docs 分支上 spec/plan/tasks 完成 + VERIFY gate PASS | CRITICAL = 0 |
| docs_baseline → dev_executing | 切换到 dev 分支，基线校验通过 | feature branch 已创建，baseline recheck PASS |
| dev_executing → dev_verifying | 所有批次执行完成 | 全量回归通过，构建成功 |
| dev_verifying → dev_reviewed | Review Gate PASS | Code review 六维度通过 |
| dev_reviewed → archiving | Archive 写入完成 | execution-log 已归档 |
| archiving → knowledge_refreshing | Archive 完成 | Done Gate 判定需要 Knowledge Refresh |
| archiving → completed | Archive 完成 | Done Gate 判定无需 Knowledge Refresh（Level 0） |
| knowledge_refreshing → completed | Knowledge Refresh 完成 | 相应 level 的文件已更新 |
| dev_executing → suspended | 用户请求暂停 / 中断 / change_request | resume-pack 已写入 |
| suspended → resumed | 用户触发恢复 / change_request 处理完毕 | resume-pack 校验通过 |
| 任意状态 → failed | 熔断器触发 / HALT 无法自修复 | 错误已记录，断点已保存 |

---

## **10. 核心业务规则（可测试）**

以下规则必须在系统中强制执行，每条均可直接编写自动化测试。

### **10.1 路由规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-001 | 当 `.ai-sdlc/` 目录不存在且项目根目录无业务代码时，Bootstrap Router 必须返回 `greenfield` | 给定空目录，断言输出 = greenfield |
| BR-002 | 当 `.ai-sdlc/` 目录不存在但项目根目录有业务代码（存在 `package.json` / `pom.xml` / `go.mod` 等）时，必须返回 `existing_project_uninitialized` | 给定含 package.json 的目录，断言输出 = existing_project_uninitialized |
| BR-003 | 当 `existing_project_uninitialized` 时，调用任何 Studio 必须被拦截并返回错误 "project not initialized" | 断言 Studio 调用抛出 ProjectNotInitializedError |
| BR-004 | Work Intake Router 对包含"线上"、"故障"、"P0"等关键词的输入，必须分类为 `production_issue` | 给定含关键词的文本，断言 work_type = production_issue |
| BR-005 | Work Intake Router 对 `uncertain` 分类的工作项，`needs_human_confirmation` 必须为 true | 断言字段值 |
| BR-006 | Work Intake Router 对 `uncertain` 连续 2 轮澄清仍无法确定时，必须返回 HALT | 模拟 2 轮澄清失败，断言状态 = HALT |

### **10.2 治理规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-010 | Governance Freeze 要求 6 项（tech profile, constitution, clarify, quality policy, branch policy, parallel policy）全部非空时才返回 PASS | 缺少任意一项，断言返回 FAIL |
| BR-011 | Governance Freeze 未通过时，创建 docs 分支的请求必须被拒绝 | 断言 branch 创建抛出 GovernanceNotFrozenError |
| BR-012 | Constitution 冻结后不可修改（仅允许在 init 阶段创建） | 在非 init 阶段尝试写入 constitution，断言被拒绝 |

### **10.3 分支规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-020 | 切换分支前必须无未提交的变更（uncommitted changes = 0） | 模拟脏工作区，断言切换被拒绝 |
| BR-021 | 从 docs 分支切换到 dev 分支后，必须执行 baseline recheck 且结果为 PASS | 断言切换后 recheck 被调用且返回 PASS |
| BR-022 | dev 分支上不允许修改 spec.md 或 plan.md | 在 dev 分支尝试写入 spec.md，断言被拒绝 |

### **10.4 执行规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-030 | 单个任务调试超过 3 轮仍失败时，必须标记为 HALT | 模拟 3 轮调试失败，断言状态 = HALT |
| BR-031 | 连续 2 个任务 HALT 时，必须触发熔断器 | 模拟 2 个连续 HALT，断言熔断器激活 |
| BR-032 | 每个批次完成后必须先写 execution-log 再 commit | 断言 log 写入时间 < commit 时间 |
| BR-033 | production_issue 的修复必须通过 Incident Studio 而非 PRD Studio | 给定 production_issue 类型，断言路由到 Incident Studio |

### **10.5 恢复规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-040 | resume-pack.yaml 存在时，`ai-sdlc recover` 必须恢复到中断时的确切阶段和批次 | 写入 resume-pack 指向 execute batch 3，断言恢复后从 batch 3 继续 |
| BR-041 | resume-pack.yaml 不存在或损坏时，recover 必须提示用户重新运行而非静默失败 | 删除 resume-pack，断言输出包含错误提示 |
| BR-042 | 恢复后的 working-set 必须与中断前一致 | 对比中断前后的 working-set.yaml 内容 |

### **10.6 知识刷新规则**

| ID | 规则 | 测试方法 |
|----|------|---------|
| BR-050 | Done Gate 判定 Knowledge Refresh Level ≥ 1 时，任务不可标记为 completed 直到刷新完成 | 设置 level=2 但未刷新，断言状态 ≠ completed |
| BR-051 | Level 0 的任务可跳过 Knowledge Refresh 直接进入 completed | 设置 level=0，断言直接转为 completed |
| BR-052 | Knowledge Refresh 完成后 `knowledge-refresh-log.yaml` 必须追加一条记录 | 执行刷新后，断言 log 文件新增 entry |

---

## **11. 核心流程定义**


### **11.1 new_requirement**

idea / prd
  -> prd readiness
  -> governance freeze
  -> feature/<id>-docs
  -> spec / plan / tasks
  -> docs baseline freeze
  -> feature/<id>-dev
  -> execution
  -> verify
  -> review
  -> archive
  -> knowledge refresh



### **11.2 production_issue**

incident brief
  -> severity
  -> analysis
  -> fix plan / tasks
  -> hotfix/fix branch
  -> execute
  -> regression
  -> postmortem
  -> archive
  -> knowledge refresh



### **11.3 change_request**

pause current flow
  -> freeze current state
  -> impact analysis
  -> rebaseline
  -> refresh docs baseline
  -> refresh dev execution
  -> resume



### **11.4 maintenance_task**

lightweight brief
  -> small plan / task graph
  -> execution
  -> verify
  -> archive
  -> knowledge refresh (if needed)

## **12. 非功能需求**

### **12.1 可恢复性**

- 任意时点中断后可恢复

- 不依赖聊天上下文持久化

### **12.2 可移植性**

- CLI-first

- 文件驱动

- 不依赖特定 IDE

### **12.3 多 IDE 兼容**

> **可移植性（T10）**：下列为**示例性**宿主环境，**不表示**唯一操作路径或产品绑定。规范真值以 **CLI**（`ai-sdlc …`）、仓库内 **`src/ai_sdlc/rules/`**（及安装后的规则副本）、**[`docs/USER_GUIDE.zh-CN.md`](docs/USER_GUIDE.zh-CN.md)** 为准；各 IDE 目录下规则仅为**可选适配**（与可移植性审计表一致）。

必须兼容（示例列举，可扩展）：

- Codex CLI / App

- Cursor

- Claude Code 类环境

- VS Code + terminal

### **12.4 可维护性**

- 一个事实只有一个 source of truth

- 知识主文档尽量单一

- 可推导信息自动生成

- runtime state 结构化

### **12.5 可扩展性**

- spec-kit / superpowers 可接成后端

- future backend 可插拔

### **12.6 稳定性**

- 所有关键主流程必须有测试

- 所有关键 gate 必须可验证

---

## **13. 测试与验收标准**

### **13.1 必须通过的测试层**

#### **单元测试**

覆盖：

- router

- initializer

- studio

- guards

- planner

- context

- branch

- parallel

#### **流程测试**

覆盖：

- new requirement flow

- production issue flow

- change request flow

- maintenance flow

- docs/dev 流

- interrupt → recover → resume

- archive → knowledge refresh

#### **集成测试**

覆盖：

- native generator

- native executor

- orchestrator run

- run_loop

- archive / commit

#### **并行测试**

覆盖：

- parallel split

- allowed_paths enforcement

- contract freeze

- overlap detection

- merge validation

- integration verify

### **13.2 功能验收标准（可量化）**

#### P0 验收（必须全部通过才可发布 RC1）

| ID | 验收项 | 验证方法 | 通过标准 |
|----|--------|---------|---------|
| AC-001 | greenfield 项目可完成 init → 产出 `.ai-sdlc/` 目录 | 在空目录运行 `ai-sdlc init` | 目录结构完整，project-state.yaml 存在 |
| AC-002 | 一句话输入可被 Work Intake Router 正确分类 | 提交 10 条不同类型的输入 | 分类准确率 ≥ 80%（8/10） |
| AC-003 | new_requirement 流程可从 PRD 走到 execution 完成 | 用示例 PRD 端到端执行 | 所有阶段 gate PASS，产出物完整 |
| AC-004 | Governance Freeze 缺失任意项时阻断后续流程 | 删除 constitution 后尝试创建 docs 分支 | 返回 GovernanceNotFrozenError |
| AC-005 | docs/dev 分支切换前后状态一致 | 切换分支后对比 working-set | diff = 0 |
| AC-006 | 中断后可通过 `ai-sdlc recover` 从断点恢复 | 在 execute 阶段杀进程，再 recover | 从中断批次继续，不重复已完成任务 |
| AC-007 | `ai-sdlc status` 输出当前状态面板 | 在各阶段运行 status | 输出包含当前阶段、进度、产物列表 |
| AC-008 | 单 Agent 闭环执行一个完整 feature | 从 init 到 close 全流程 | 全流程无 HALT，产出 summary |
| AC-009 | 所有 BR-xxx 业务规则测试通过 | 运行 `pytest tests/rules/` | 0 failures |
| AC-010 | CLI 命令 help/init/status/recover/index/gate 均可正常运行 | 运行每个命令 | 退出码 = 0（或预期的非零） |

#### P1 验收（P0 发布后迭代验证）

| ID | 验收项 | 验证方法 | 通过标准 |
|----|--------|---------|---------|
| AC-020 | 存量项目可完成初始化并产出 engineering-corpus.md | 在已有代码库运行 init | corpus 包含 §1-§10，Tier 对应章节非空 |
| AC-021 | production_issue 可走 Incident Studio 短路径 | 提交 incident brief | 产出 incident analysis + fix plan |
| AC-022 | change_request 可触发暂停 + 影响分析 + rebaseline | 在 execute 阶段提交变更 | 当前状态冻结，impact analysis 产出 |
| AC-023 | 多 Agent 并行可正确分配和汇合 | 2 个 Worker 并行执行不重叠任务 | 无冲突，merge 成功 |
| AC-024 | Knowledge Refresh 在 Done Gate 触发后正确执行 | 完成影响模块边界的任务 | corpus 相应章节已更新 |

### **13.3 发布门槛**

必须全部满足：

- unit tests 全绿
- flow tests 全绿
- integration tests 全绿
- parallel tests 全绿（P1）
- demo dry-run 全绿
- 至少 1 条 end-to-end real-run 全绿
- `ai-sdlc status` 可用
- `ai-sdlc recover` 可用
- 所有 P0 验收标准（AC-001 ~ AC-010）通过

---

## **14. RC1 范围**

### **P0：核心闭环（不实现则 MVP 无法运行）**

| 序号 | 模块 | 依赖 | 说明 |
|:----:|------|------|------|
| 1 | Project Bootstrap Router | 无 | 入口判断，所有流程的起点 |
| 2 | Work Intake Router | #1 | 工作类型分流，依赖项目状态已知 |
| 3 | PRD Studio | #2 | 最核心的 new_requirement 流程 |
| 4 | Governance Freeze | #3 | 治理前置条件，planning 的门禁 |
| 5 | docs/dev 双分支模型 | #4 | 基线管理，执行前必须建立 |
| 6 | 单 Agent 执行闭环（Planning & Execution） | #5 | 核心执行能力 |
| 7 | Context Control Plane | #6 | 状态持久化与中断恢复 |
| 8 | Native Backend（内置执行引擎） | #1-#7 | 驱动所有模块的底层引擎 |
| 9 | 测试与发布基线 | #1-#8 | 质量保障 |

### **P1：完善能力（P0 闭环后迭代补充）**

| 序号 | 模块 | 依赖 | 说明 |
|:----:|------|------|------|
| 10 | Existing Project Initialization Flow | #1 | 存量项目初始化，P0 仅需支持 greenfield |
| 11 | Incident / Change / Maintenance 三类 Studio | #2 | 非核心流程的三种 Studio |
| 12 | Multi-Agent 并行基础版 | #6, #7 | 增强能力，需单 Agent 闭环稳定后再启用 |
| 13 | Knowledge Refresh Flow | #10 | 依赖初始化流程产出的知识基线 |

### **模块依赖图**

```
#1 Project Bootstrap Router
 └─► #2 Work Intake Router
      └─► #3 PRD Studio
           └─► #4 Governance Freeze
                └─► #5 docs/dev 双分支模型
                     └─► #6 单 Agent 执行闭环
                          └─► #7 Context Control Plane
                               └─► #8 Native Backend (贯穿 #1-#7)
                                    └─► #9 测试与发布基线

P1 扩展：
#1 ──► #10 Existing Project Initialization
#2 ──► #11 Incident / Change / Maintenance Studios
#6 + #7 ──► #12 Multi-Agent 并行
#10 ──► #13 Knowledge Refresh
```

### **推荐实现顺序**

P0 按依赖链从底向上实现：
1. 先实现 Native Backend 的核心骨架（状态机、文件 I/O、CLI 框架）
2. 再逐个实现 #1 → #2 → #3 → #4 → #5 → #6 → #7
3. 每个模块实现后立即补充单元测试
4. 全部 P0 模块完成后运行端到端流程测试

### **暂不做**

1. 多仓库联动
2. 审批流 / 合规系统
3. 高级 GUI 编排平台
4. 分布式 swarm
5. 复杂发布 train

---

## **15. 关键风险**

1. 存量工程初始化不充分，导致后续任务基线失真

2. 分支治理执行不严格，导致 docs/dev 漂移

3. 多 Agent 并行边界不清，导致冲突和重复开发

4. 上下文恢复链不完整，导致中断后恢复失败

5. Knowledge Refresh 未接入 done gate，导致工程知识快速过时

---

## **16. 最终完成定义**

AI-SDLC 被视为“可正式试运行”，必须同时满足：

1. 已有项目可初始化并形成知识基线

2. 四类工作类型都可进入正确流程

3. docs/dev 双分支模型可运行

4. 单 Agent 闭环可运行

5. 多 Agent 并行基础版可运行

6. Context Control Plane 可恢复

7. Quality Gates 生效

8. Knowledge Refresh 已并入生命周期

9. 所有关键测试通过




