# 功能规格：AI-SDLC P1 能力扩展

**功能编号**：`002-p1-capabilities`  
**创建日期**：2026-03-21  
**状态**：草稿  
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
