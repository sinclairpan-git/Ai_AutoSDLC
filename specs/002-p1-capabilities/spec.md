# 功能规格：AI-SDLC P1 能力扩展

**功能编号**：`002-p1-capabilities`  
**创建日期**：2026-03-21  
**状态**：已实现（P1 capabilities closure）
**输入**：PRD v1.1 Section 8.2, 8.4.2-8.4.4, 8.9, 8.11, 10.1-10.6, 11.1-11.4；P0 代码库

**范围**：

- **覆盖**：P1 的 4 个模块（#10 Existing Project Init, #11 Three Studios, #12 Multi-Agent Parallel, #13 Knowledge Refresh）
- **不覆盖**：Web GUI、多仓库联动、分布式 swarm 级调度

---

## P1 模块总览

| 模块 | 编号 | 依赖 | AC |
|------|------|------|----|
| Existing Project Initialization | #10 | P0 #1 Bootstrap Router | AC-020 |
| Incident / Change / Maintenance Studios | #11 | P0 #2 Work Intake Router | AC-021, AC-022 |
| Multi-Agent Parallel Foundation | #12 | P0 #6, #7 | AC-023 |
| Knowledge Refresh Flow | #13 | #10 | AC-024 |

---

## 用户故事与验收

### US-P1-1 — 存量项目初始化

作为**个人开发者**，我希望在已有代码库中运行 `ai-sdlc init`，系统自动扫描项目结构并生成工程知识基线，以便后续任务能利用项目上下文。

**验收**：
1. Given 含 package.json 的目录，When 运行 init，Then 产出 engineering-corpus.md（含 §1-§10）
2. Given 初始化完成，When 查看 `.ai-sdlc/project/generated/`，Then repo-facts.json + key-files.json + dependency-index.json 存在且非空
3. Given existing_project_uninitialized，When 调用任何 Studio，Then 抛出 ProjectNotInitializedError

### US-P1-2 — Incident Studio 短路径

作为**运维工程师**，我希望提交 incident brief 后系统走短路径生成分析和修复计划，不强制走完整 PRD 流程。

**验收**：
1. Given production_issue 类型工作项，When 路由，Then recommended_flow = incident_studio
2. Given incident brief 输入，When 调用 IncidentStudio，Then 产出 incident-analysis.md + fix-plan.md + tasks
3. Given production_issue 类型，When 尝试路由到 PRD Studio，Then 拒绝并提示走 Incident Studio

### US-P1-3 — Change Request 暂停与影响分析

作为**产品经理**，我希望在开发中途提交变更请求后，系统自动暂停当前流程、冻结状态并生成影响分析。

**验收**：
1. Given dev_executing 状态，When 提交 change_request，Then 当前状态冻结并保存快照
2. Given change_request 处理中，When 影响分析完成，Then 产出 impact-analysis.md + rebaseline-record.md

### US-P1-4 — Maintenance Brief 轻量路径

作为**开发者**，我希望维护任务走轻量路径，不需要完整 PRD/spec 流程。

**验收**：
1. Given maintenance_task 类型，When 调用 MaintenanceStudio，Then 产出 lightweight-brief.md + 任务图（≤10 tasks）

### US-P1-5 — Knowledge Refresh 增量更新

作为**开发者**，我希望任务完成后系统根据变更影响自动刷新项目知识，保持基线最新。

**验收**：
1. Given Level 0 任务完成，When Done Gate 判定，Then 跳过 refresh 直接 completed
2. Given Level 2 任务完成，When Done Gate 判定，Then 索引 + 知识文档刷新后才 completed
3. Given 刷新完成，When 检查日志，Then knowledge-refresh-log.yaml 新增记录

### US-P1-6 — Multi-Agent 并行基础

作为**技术负责人**，我希望可并行的任务由多个 Worker 分支同时执行，汇合后自动检测冲突。

**验收**：
1. Given 2 个 parallelizable 任务声明不同 allowed_paths，When 并行执行，Then 各自在独立分支
2. Given 并行完成，When 汇合，Then overlap detection 无冲突 + merge 成功

---

## 功能需求

### #10 Existing Project Init

| ID | 需求 |
|----|------|
| FR-P1-001 | init 检测 existing_project_uninitialized 后触发扫描流程 |
| FR-P1-002 | 扫描器生成 engineering-corpus.md（含 10 个必需章节骨架） |
| FR-P1-003 | 扫描器生成 codebase-summary.md 和 project-brief.md |
| FR-P1-004 | 索引生成器产出 key-files.json, api-index.json, dependency-index.json, test-index.json, risk-index.json |
| FR-P1-005 | 创建 initialization-status.yaml 记录扫描进度 |
| FR-P1-006 | 创建 knowledge-baseline-state.yaml 记录基线版本 |
| FR-P1-007 | 创建治理策略文件：branch-policy.yaml, quality-policy.yaml, parallel-policy.yaml, environment-policy.yaml |
| FR-P1-008 | BR-003：existing_project_uninitialized 状态下调用 Studio 必须抛出 ProjectNotInitializedError |

### #11 Three Studios

| ID | 需求 |
|----|------|
| FR-P1-010 | IncidentStudio 接收 IncidentBrief 产出 analysis + fix-plan + tasks + postmortem 模板 |
| FR-P1-011 | ChangeStudio 冻结当前状态快照、产出 impact-analysis + rebaseline-record + resume-point |
| FR-P1-012 | MaintenanceStudio 产出 lightweight-brief + small task graph（≤10 tasks）+ execution-path |
| FR-P1-013 | 定义 StudioProtocol，所有 Studio（含 P0 PRDStudio）实现统一接口 |
| FR-P1-014 | BR-033：production_issue 必须路由到 IncidentStudio，尝试 PRDStudio 被拒绝 |
| FR-P1-015 | change_request 触发 suspended 状态转换 + ChangeStudio 处理 |
| FR-P1-016 | Incident Postmortem Gate 检查 postmortem 完整性 |

### #12 Multi-Agent Parallel

| ID | 需求 |
|----|------|
| FR-P1-020 | 任务模型扩展 parallelizable, parallel_group, allowed_paths, forbidden_paths, interface_contracts, merge_order 字段 |
| FR-P1-021 | ParallelPolicy 模型管理并行策略 |
| FR-P1-022 | Contract 模型冻结 Worker 间契约 |
| FR-P1-023 | Worker 分支创建（feature/<id>-worker-N） |
| FR-P1-024 | Overlap detection：检测多个 Worker 修改了同一文件 |
| FR-P1-025 | Merge simulation：dry-run merge 检测冲突 |
| FR-P1-026 | Coordinator 逻辑：切片、分配、冻结、汇合验证 |

### #13 Knowledge Refresh

| ID | 需求 |
|----|------|
| FR-P1-030 | RefreshLevel 枚举（L0-L3）及判定逻辑 |
| FR-P1-031 | L0：跳过 refresh，archiving → completed 直接转换（BR-051） |
| FR-P1-032 | L1：仅重生成自动索引（repo-facts, key-files, api-index, dependency-index, test-index, risk-index） |
| FR-P1-033 | L2：L1 + patch engineering-corpus.md 相关章节 |
| FR-P1-034 | L3：局部重初始化（重新扫描受影响模块） |
| FR-P1-035 | Done Gate 集成：Level ≥ 1 时阻止标记 completed 直到刷新完成（BR-050） |
| FR-P1-036 | knowledge-refresh-log.yaml 追加记录（BR-052） |
| FR-P1-037 | CLI `ai-sdlc refresh` 命令手动触发 |

---

## 缺口收敛补充（2026-03-28）

> 本节用于吸收原始 PRD 中已归入 P1 范围、但此前在 `002` 中仍未充分细化或当前实现只完成一半的需求。对应缺口总表 **RG-010 ~ RG-015**。

### 用户故事与验收补充

#### US-P1-7 — Change Request 触发运行态暂停

作为**产品经理 / 技术负责人**，我希望在执行中收到变更请求时，系统不仅生成分析文档，还会正式暂停当前运行态并保留恢复入口。

**验收**：

1. Given `dev_executing` 或 `dev_verifying` 状态，When 提交 `change_request`，Then work item 进入 `suspended`
2. Given 变更分析完成，When 查看产物，Then 能看到 freeze snapshot、impact analysis、rebaseline record 与可消费的 resume point
3. Given 变更处理完成，When 继续执行，Then `recover` / `run` 能从 resume point 恢复主链

#### US-P1-8 — Maintenance Studio 输出显式 execution path

作为**开发者**，我希望 Maintenance Studio 不仅给出 task graph，还给出明确 execution path，以便轻量任务也有正式执行顺序合同。

**验收**：

1. Given maintenance brief，When 处理完成，Then 输出 small task graph + execution path
2. Given 查看持久化产物，When 检查文档或结构化对象，Then execution path 与 task 依赖顺序一致

#### US-P1-9 — Multi-Agent 从 planning 进入 runtime orchestration

作为**技术负责人**，我希望可并行任务不仅能被切片和模拟，还能由 Coordinator 正式编排 worker 生命周期与汇合验证。

**验收**：

1. Given parallelizable 任务集合，When 进入并行执行，Then Coordinator 持久化 assignment 与 contract freeze 结果
2. Given 多个 worker branch 已生成，When 汇合，Then overlap detection、merge simulation 与 integration verify 都可见

#### US-P1-10 — Knowledge Refresh 接入 Done / Close 主链

作为**开发者**，我希望刷新不是一个手动补动作，而是 Done / Close 的正式门禁环节。

**验收**：

1. Given Level 0 任务，When 进入 Done / Close，Then 可直接 completed
2. Given Level 1+ 任务，When 进入 Done / Close，Then 未完成 refresh 前不得 completed
3. Given refresh 完成，When 进入 close 收口，Then 相关 evidence 与 refresh log 可被读取

#### US-P1-11 — Incident Close 必须通过 Postmortem Gate

作为**维护 / 值班工程师**，我希望 incident 的收口必须经过 postmortem 完整性检查，以便事故闭环成为正式门禁。

**验收**：

1. Given incident fix 已完成，When 准备 close，Then 必须先通过 Postmortem Gate
2. Given postmortem 缺关键章节，When close，Then 返回 BLOCKER 而不是静默通过

### 功能需求补充

| ID | 需求 |
|----|------|
| FR-P1-017 | `change_request` 必须把活跃 work item 从 `dev_executing` / `dev_verifying` 转为 `suspended`，并持久化 freeze snapshot |
| FR-P1-018 | ChangeStudio 产出的 `resume-point` 必须可被 `recover` / `run` 主链消费，而不只是写进自由文本 |
| FR-P1-019 | MaintenanceStudio 必须输出并持久化 `execution-path`，使轻量维护路径具备正式执行顺序真值 |
| FR-P1-027 | Multi-Agent Coordinator 必须编排 contract freeze、assignment 持久化、worker branch 生命周期与汇合验证 |
| FR-P1-028 | 并行执行必须存在正式 coordination artifact，至少记录 group、worker、allowed/forbidden paths、merge order 与校验结果 |
| FR-P1-029 | Worker branch 命名与 merge order 必须可被 status / report surface 读取，而不只是内存中的临时对象 |
| FR-P1-038 | Level ≥ 1 的 Knowledge Refresh 义务必须正式接入 Done / Close Gate，而非仅依赖手动 `ai-sdlc refresh` |
| FR-P1-039 | Close 收口必须能读取 refresh evidence / refresh log，并将其纳入 completion truth |
| FR-P1-040 | Incident close path 必须在 completed 前通过 Postmortem Gate |
| FR-P1-041 | Postmortem Gate 失败时必须指出缺失章节与阻断原因，供 incident recover / close-check 使用 |

### 补充验收标准

- **AC-025**：收到 `change_request` 后，work item 状态与 snapshot artifact 同步落盘，而不是仅生成文档产物
- **AC-026**：`resume-point` 至少能被一个 recover / run 夹具直接消费并恢复执行
- **AC-027**：Maintenance Studio 的 execution path 在对象层与落盘层都可读
- **AC-028**：并行执行除 planning/simulation 外，至少具备 assignment freeze 与 integration verify 的正式合同面
- **AC-029**：Level 1+ refresh 未完成时，Done / Close 不允许 completed
- **AC-030**：refresh 完成后，close 收口能读取 refresh evidence 并解除阻断
- **AC-031**：incident close 在 postmortem 缺章节时返回 BLOCKER，修复后可通过
