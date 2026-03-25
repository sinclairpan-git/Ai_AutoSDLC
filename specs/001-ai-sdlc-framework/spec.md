# 功能规格：AI-SDLC 全自动化框架 P0

**功能编号**：`001-ai-sdlc-framework`  
**创建日期**：2026-03-21  
**状态**：草稿  
**输入**：PRD v1.1 全文（Section 1-16），聚焦 Section 14 P0 范围

**范围**：

- **覆盖**：P0 的 9 个模块（Project Bootstrap Router → 测试基线），实现从 greenfield 项目的 init 到单 Agent 闭环执行的完整路径
- **不覆盖**：P1 模块（Existing Project Initialization、Incident/Change/Maintenance Studios、Multi-Agent 并行、Knowledge Refresh）；Web GUI；多仓库联动

---

## 用户场景与测试

### 用户故事 1 — 项目初始化（优先级：P0）

作为**个人开发者**，我希望在一个新项目中运行 `ai-sdlc init`，以便自动创建 `.ai-sdlc/` 目录结构和初始配置，使项目具备进入 SDLC 流程的基础。

**优先级说明**：所有流程的起点，不初始化则无法执行任何后续操作。

**独立测试**：在空的临时目录中运行 `ai-sdlc init`，验证产出的目录结构和文件完整性。

**验收场景**：

1. **Given** 一个空目录且不存在 `.ai-sdlc/`，**When** 运行 `ai-sdlc init`，**Then** 创建完整的 `.ai-sdlc/` 目录结构，包含 `project/config/project-state.yaml`，且 `project-state.yaml` 中 `status = initialized`。

2. **Given** 一个已存在 `.ai-sdlc/` 且 `status = initialized` 的目录，**When** 运行 `ai-sdlc init`，**Then** 输出提示 "Project already initialized" 且不覆盖任何现有文件。

3. **Given** 一个空目录，**When** 运行 `ai-sdlc init`，**Then** `project-state.yaml` 中 `next_work_item_seq = 1`。

---

### 用户故事 2 — 项目状态检测（优先级：P0）

作为**个人开发者**，我希望系统能自动判断当前项目属于 greenfield / existing_initialized / existing_uninitialized，以便进入正确的流程路径。

**优先级说明**：路由的基础判断，Work Intake Router 依赖此结果。

**独立测试**：分别准备三种状态的目录，调用 Bootstrap Router，验证返回值。

**验收场景**：

1. **Given** 目录中无 `.ai-sdlc/` 且无业务代码文件（package.json / pom.xml 等），**When** 调用 Bootstrap Router，**Then** 返回 `greenfield`。

2. **Given** 目录中无 `.ai-sdlc/` 但存在 `package.json`，**When** 调用 Bootstrap Router，**Then** 返回 `existing_project_uninitialized`。

3. **Given** 目录中存在 `.ai-sdlc/` 且 `project-state.yaml` 中 `status = initialized`，**When** 调用 Bootstrap Router，**Then** 返回 `existing_project_initialized`。

4. **Given** Bootstrap Router 返回 `existing_project_uninitialized`，**When** 尝试调用 PRD Studio，**Then** 返回 `ProjectNotInitializedError` 并提示先运行 init。

---

### 用户故事 3 — 工作项分类（优先级：P0）

作为**个人开发者**，我希望输入一段自然语言需求后，系统能自动识别工作类型（new_requirement / production_issue / change_request / maintenance_task / uncertain），以便进入对应的处理流程。

**优先级说明**：工作分流的核心能力，所有 Studio 依赖此路由。

**独立测试**：准备不同类型的输入文本，调用 Work Intake Router，验证分类结果。

**验收场景**：

1. **Given** 输入文本 "我要做一个报名系统"，**When** 调用 Work Intake Router，**Then** 返回 `work_type = new_requirement`，`classification_confidence = high`。

2. **Given** 输入文本 "线上系统 502 了，用户无法访问"，**When** 调用 Work Intake Router，**Then** 返回 `work_type = production_issue`，`severity >= high`。

3. **Given** 输入 "升级 Python 版本到 3.12"，**When** 调用 Work Intake Router，**Then** 返回 `work_type = maintenance_task`。

4. **Given** 输入 "我也不知道该怎么分类这个需求"，**When** 调用 Work Intake Router，**Then** 返回 `work_type = uncertain`，`needs_human_confirmation = true`。

5. **Given** `work_type = uncertain` 且连续 2 轮澄清仍无法确定，**When** 系统尝试第 3 次分类，**Then** 返回 HALT 状态。

6. **Given** 调用 Work Intake Router 成功，**Then** 返回的 `work_item_id` 格式为 `WI-YYYY-NNN`，且 `project-state.yaml` 的 `next_work_item_seq` 自增 1。

---

### 用户故事 4 — PRD 处理与就绪检查（优先级：P0）

作为**个人开发者**，我希望提交一份完整的 PRD 后，系统能自动进行就绪检查（readiness review），以便确认 PRD 质量足以进入后续规划阶段。

**优先级说明**：new_requirement 流程的核心入口。P0 仅支持完整 PRD 输入，多轮引导为 P1。

**独立测试**：提交一份符合模板的 PRD 和一份缺失关键章节的 PRD，验证就绪检查结果。

**验收场景**：

1. **Given** 一份包含所有必填章节的完整 PRD，**When** 提交到 PRD Studio，**Then** 返回 `readiness = pass`，输出结构化摘要（项目名、目标、角色、核心功能、验收标准数量）。

2. **Given** 一份缺少"业务规则"和"验收标准"章节的 PRD，**When** 提交到 PRD Studio，**Then** 返回 `readiness = fail`，并列出缺失项和改进建议。

3. **Given** PRD Studio 返回 `readiness = pass`，**Then** 输出可直接进入 spec/plan/tasks 生成阶段的结构化输入（JSON/YAML 格式）。

---

### 用户故事 5 — 治理层冻结（优先级：P0）

作为**技术负责人**，我希望在进入规划阶段前，系统能检查并冻结所有治理前置条件（tech profile / constitution / clarify / quality policy / branch policy / parallel policy），以便确保后续开发在约束范围内进行。

**优先级说明**：planning 的门禁，不冻结则不允许创建 docs 分支。

**独立测试**：分别测试所有项齐全和缺失任意项的场景。

**验收场景**：

1. **Given** 6 项治理前置条件全部存在且非空，**When** 执行 Governance Freeze，**Then** 返回 `PASS`，写入 `governance.yaml` 并标记 `frozen = true`。

2. **Given** constitution.md 缺失，**When** 执行 Governance Freeze，**Then** 返回 `FAIL`，错误信息包含 "constitution.md missing"。

3. **Given** Governance Freeze 未通过（frozen = false），**When** 尝试创建 docs 分支，**Then** 抛出 `GovernanceNotFrozenError`。

4. **Given** Governance Freeze 已通过，**When** 尝试修改 constitution.md，**Then** 操作被拒绝，提示 "constitution is frozen"。

---

### 用户故事 6 — Docs/Dev 双分支管理（优先级：P0）

作为**个人开发者**，我希望系统能自动管理 docs 分支（存放 spec/plan/tasks）和 dev 分支（存放代码实现），以便文档基线和代码实现严格隔离。

**优先级说明**：Baseline before Build 原则的核心实现。

**独立测试**：在测试仓库中模拟分支创建、切换、合并流程。

**验收场景**：

1. **Given** Governance Freeze 已通过，**When** 系统创建 docs 分支，**Then** 分支名为 `feature/<work-item-id>-docs`，从 main 创建。

2. **Given** 当前在 docs 分支且 spec/plan/tasks 已完成，**When** 系统切换到 dev 分支，**Then**：a) docs 分支所有变更已 commit；b) dev 分支名为 `feature/<work-item-id>-dev`；c) dev 分支可访问 docs 产物。

3. **Given** 当前工作区有未提交的变更，**When** 尝试切换分支，**Then** 切换被拒绝，提示 "uncommitted changes detected"。

4. **Given** 当前在 dev 分支，**When** 尝试写入 `spec.md` 或 `plan.md`，**Then** 操作被拒绝，提示 "spec/plan modifications not allowed on dev branch"。

5. **Given** 切换到 dev 分支完成，**Then** 自动执行 baseline recheck，确认 docs 产物完整可访问。

---

### 用户故事 7 — 单 Agent 执行闭环（优先级：P0）

作为**个人开发者**，我希望系统能按 tasks.md 中的任务列表逐批执行（TDD：Red → Green → Verify），自动归档每个批次，最终生成 development-summary.md，以便完成从设计到交付的闭环。

**优先级说明**：核心执行能力，整个框架的价值交付点。

**独立测试**：准备一个简单的 tasks.md（3-5 个任务），验证执行流程完整性。

**验收场景**：

1. **Given** tasks.md 包含 Phase 1（2 个任务）和 Phase 2（3 个任务），**When** 启动执行，**Then** 按 Phase 分批执行，每批完成后写入 `task-execution-log.md` 并 git commit。

2. **Given** 某个任务的测试失败，**When** 触发调试流程，**Then** 最多重试 3 轮；超过 3 轮则标记任务为 HALT。

3. **Given** 连续 2 个任务 HALT，**When** 检查熔断器，**Then** 触发熔断，流水线暂停，输出阻断面板。

4. **Given** 所有任务执行完成，**When** 进入 CLOSE 阶段，**Then** 生成 `development-summary.md`，包含任务统计、测试覆盖、commit 记录。

5. **Given** 每个批次完成，**Then** `task-execution-log.md` 记录包含：任务 ID、执行状态、测试结果、耗时。

---

### 用户故事 8 — 上下文持久化与中断恢复（优先级：P0）

作为**个人开发者**，我希望在流水线执行过程中意外中断后，能通过 `ai-sdlc recover` 从断点恢复执行，以便不丢失已完成的进度。

**优先级说明**：Context externalized 原则的核心实现，直接影响用户体验。

**独立测试**：在执行中途手动中断，然后运行 recover，验证恢复位置正确。

**验收场景**：

1. **Given** 流水线在 execute 阶段 batch 3 完成后中断（checkpoint 记录 `current_batch = 4`），**When** 运行 `ai-sdlc recover`，**Then** 从 batch 4 继续执行，不重复 batch 1-3。

2. **Given** `resume-pack.yaml` 存在且完整，**When** 运行 `ai-sdlc recover`，**Then** 恢复 working-set，输出恢复面板（中断位置、已完成阶段、执行模式）。

3. **Given** `resume-pack.yaml` 不存在，**When** 运行 `ai-sdlc recover`，**Then** 输出错误提示 "No resume pack found. Run ai-sdlc init to start fresh."，退出码非零。

4. **Given** `resume-pack.yaml` 中 YAML 语法损坏，**When** 运行 `ai-sdlc recover`，**Then** 输出错误提示 "Resume pack corrupted"，建议手动检查。

5. **Given** `ai-sdlc status` 被调用，**When** 流水线在任意阶段，**Then** 输出当前状态面板（阶段进度、当前任务、AI 决策计数）。

---

### 边界情况

- **空 PRD 输入**：Work Intake Router 收到空字符串 → 返回 `uncertain`，`classification_confidence = low`
- **超大 PRD**（> 100KB）：PRD Studio 截断到前 50KB 处理，标记 WARNING
- **并发 init**：两次 `ai-sdlc init` 同时运行 → 第二次检测到锁文件等待或失败
- **Git 未安装**：`ai-sdlc init` 检测到 git 不可用 → 明确报错 "git is required"
- **非 UTF-8 文件**：YAML 读取遇到编码错误 → 跳过该文件，记录 WARNING
- **磁盘空间不足**：文件写入失败 → 捕获 OSError，输出友好提示
- **分支名冲突**：创建 docs/dev 分支时同名分支已存在 → 提示用户选择：复用 / 删除重建 / 改名
- **checkpoint.yml 指向不存在的 spec_dir**：recover 校验失败 → 提示重新运行而非静默跳过

---

## 需求

### 功能需求

#### 路由层

- **FR-001**：系统必须提供 `BootstrapRouter.detect(project_path) → ProjectStatus` 函数，返回 `greenfield | existing_project_initialized | existing_project_uninitialized`
- **FR-002**：`BootstrapRouter` 必须检查以下文件指纹判断业务代码存在性：`package.json, pom.xml, build.gradle, go.mod, Cargo.toml, requirements.txt, pyproject.toml, setup.py, Gemfile, *.csproj`，以及 `src/` 或 `app/` 目录
- **FR-003**：系统必须提供 `WorkIntakeRouter.classify(input_text, source) → WorkItem` 函数，返回结构化的工作项分类结果
- **FR-004**：`WorkIntakeRouter` 必须使用关键词匹配 + 模式识别判断工作类型；production_issue 关键词包括但不限于：生产、线上、P0、P1、故障、告警、宕机、502、OOM、数据不一致、回滚
- **FR-005**：`WorkIntakeRouter` 对 `uncertain` 类型必须自动设置 `needs_human_confirmation = true`

#### PRD Studio

- **FR-010**：系统必须提供 `PrdStudio.review(prd_content) → PrdReadiness` 函数，检查 PRD 的 7 项必填门禁
- **FR-011**：`PrdStudio.review()` 必须返回结构化结果，包含 `readiness: pass|fail`、`missing_sections: list`、`recommendations: list`
- **FR-012**：PRD 通过就绪检查后，必须输出结构化摘要（JSON/YAML），包含项目名、目标、角色列表、功能列表、验收标准

#### 治理层

- **FR-020**：系统必须提供 `GovernanceGuard.check() → GateResult` 函数，检查 6 项前置条件
- **FR-021**：`GovernanceGuard` 的 6 项检查项为：tech_profile, constitution, clarify, quality_policy, branch_policy, parallel_policy
- **FR-022**：任何一项缺失时 `GovernanceGuard.check()` 返回 `FAIL`，并在结果中列出所有缺失项
- **FR-023**：`GovernanceGuard.freeze()` 成功后写入 `governance.yaml`，标记 `frozen = true, frozen_at = <timestamp>`

#### 分支管理

- **FR-030**：系统必须提供 `BranchManager.create_docs_branch(work_item_id) → str` 创建 docs 分支
- **FR-031**：系统必须提供 `BranchManager.switch_to_dev(work_item_id) → str` 从 docs 切换到 dev 分支
- **FR-032**：分支切换前必须检查 uncommitted changes，有则拒绝
- **FR-033**：从 docs 切换到 dev 后必须执行 `baseline_recheck()` 验证 docs 产物可访问
- **FR-034**：`BranchManager` 必须在 dev 分支上拦截对 spec.md 和 plan.md 的写操作

#### 执行引擎

- **FR-040**：系统必须提供 `Executor.run(tasks_file) → ExecutionResult` 驱动批次执行
- **FR-041**：`Executor` 按 Phase 分批执行，每批最大任务数由 `pipeline.yml` 的 `batch.max_tasks_per_batch` 控制
- **FR-042**：每个批次完成后必须写入 `task-execution-log.md`
- **FR-043**：每个批次完成后必须执行 `git commit`
- **FR-044**：单个任务调试超过 `circuit_breaker.max_debug_rounds_per_task` 轮 → HALT
- **FR-045**：连续 `circuit_breaker.consecutive_failure_limit` 个任务 HALT → 熔断

#### Context Control Plane

- **FR-050**：系统必须在每个阶段完成后写入 `checkpoint.yml`，记录当前阶段、已完成阶段、execute 进度
- **FR-051**：系统必须提供 `ContextManager.save_resume_pack()` 保存恢复包
- **FR-052**：系统必须提供 `ContextManager.load_resume_pack() → ResumeContext` 加载恢复包
- **FR-053**：`resume-pack.yaml` 必须包含：current_stage, current_batch, last_committed_task, working_set_snapshot
- **FR-054**：`checkpoint.yml` 加载时必须校验：YAML 语法、current_stage 合法性、spec_dir 存在性

#### Quality Gates

- **FR-060**：系统必须为每个阶段提供 `Gate.check(stage) → GateResult(PASS|RETRY|HALT)`
- **FR-061**：INIT Gate 检查：constitution 存在 + tech-stack 存在 + decisions 存在 + 宪章 ≥ 3 原则 + 技术栈有来源标注
- **FR-062**：REFINE Gate 检查：spec.md 存在 + user_stories ≥ 1 + 每个 US 有验收场景 + FR 列表非空 + 无 NEEDS_CLARIFICATION
- **FR-063**：EXECUTE Gate（每批次）检查：测试通过 + 构建成功 + 已归档 + 已 commit

#### CLI

- **FR-070**：`ai-sdlc init` 创建 `.ai-sdlc/` 目录结构和初始配置文件
- **FR-071**：`ai-sdlc status` 读取 checkpoint.yml 并输出当前状态面板（Rich 格式化）
- **FR-072**：`ai-sdlc recover` 加载 resume-pack 并输出恢复面板
- **FR-073**：`ai-sdlc index` 重新生成自动索引文件（repo-facts.json 等）
- **FR-074**：`ai-sdlc gate <stage>` 手动运行指定阶段的门禁检查
- **FR-075**：所有 CLI 命令必须有 `--help` 说明和合理的退出码（0=成功，1=失败，2=用户错误）

#### Native Backend

- **FR-080**：系统必须提供基于文件系统的状态机，驱动 work item 从 `created` 到 `completed` 的完整生命周期
- **FR-081**：状态机的所有转换必须持久化到 `work-item.yaml` 的 `status` 字段
- **FR-082**：系统必须提供模板生成器，从 Jinja2 模板生成 spec、plan、tasks 等产物骨架
- **FR-083**：系统必须提供索引生成器，扫描项目目录生成 `repo-facts.json`、`key-files.json`
- **FR-084**：Plugin Backend 接口预留：定义 `BackendProtocol`（Python Protocol），Native 为默认实现

#### 工作项与外部计划状态一致性（P1 backlog，MUST-4 延伸）

> 来源：2026-03-24 复盘——仓库已实现变更，但 **Cursor/IDE 计划文件** frontmatter `todos` 长期为 `pending`，与事实不对齐；与「checkpoint vs project-state」同类元问题。

- **FR-085（P1）**：框架须在 **用户指南** 中定义 **交付完成（DoD）** 的一条：**关联工作项** `specs/<WI>/tasks.md` 或 **已声明绑定的外部计划** 中的待办状态已与本次变更同步更新，或已登记延期原因；与「状态落盘」一致，禁止仅依赖会话记忆。
- **FR-086（P1）**：`specs/<WI>/` 下 **plan.md 或 tasks.md frontmatter** 宜支持可选字段 `related_plan:`（URI 或相对路径），指向仓库内或工具生成的计划文件，便于人工与后续 **对账脚本** 引用（**本条目仅为数据契约与文档约定，实现可后置**）。
- **FR-087（P1）**：框架路线图包含可选 CLI：**`ai-sdlc workitem plan-check`（名称待定）**——**只读**比对「计划待办 pending」与「Git 已变更路径 / tasks 勾选」的差异，输出报告；**默认不写库**；实现须符合 MUST-2/3。
- **FR-088（P1）**：`Checkpoint`（或经 ADR 批准的并列 YAML）可**可选**记录 `linked_wi_id`、`linked_plan_uri`、`last_synced_at`；`ai-sdlc status` 只读展示一行；**须向后兼容**既有 `checkpoint.yml`；实现须 YamlStore + 单元测试（MUST-2）。
- **FR-089（P1）**：`ai-sdlc verify constraints`（名称可调整）：只读检查必读治理文件、checkpoint 与 `specs/` 目录一致性等，输出 BLOCKER 列表；**默认不写库**；退出码约定见实现 PR；须 pytest（MUST-2）。

#### 执行收口与归档约束硬化（P1 backlog，MUST-2/3/4/5 延伸）

> 来源：2026-03-25 复盘——实现 `FR-087/088/089` 时出现「命令与文档状态漂移、归档证据未结构化、会话中声称完成与收口动作分离」现象。

- **FR-091（P1）**：框架应提供只读命令（名称待定，如 `ai-sdlc workitem close-check`），在合并前检查以下收口项并输出 BLOCKER 列表：  
  1) `specs/<WI>/tasks.md` 完成度；  
  2) 若存在 `related_plan`，计划 `todos` 与 Git 事实是否一致；  
  3) `task-execution-log.md` 是否含本批次验证/自审证据（可由模板约定字段）；  
  4) `docs/` 中是否存在“未实现前”且与已实现 CLI 冲突的陈述（可先做规则化关键字检查）。
- **FR-092（P1）**：`templates/execution-log-template.md`（或等效模板）应新增收口小节：最少包含「验证命令」「代码审查结论」「相关任务/计划同步状态」三项，避免仅口头完成。
- **FR-093（P1）**：`docs/pull-request-checklist.zh.md` 应纳入可执行闭环：`pytest`、`ruff`、`verify constraints`、（如适用）`workitem plan-check` / `close-check`；并区分“文档变更”与“代码变更”的最低验证集合。
- **FR-094（P1）**：当 `agent-skip-registry.zh.md` 新增偏离条目后，须在同一工作项的 `spec/plan/tasks` 中形成对应条目（FR 或 Task），禁止只登记不产品化。

### 关键实体

- **ProjectState**：项目级状态（status, next_work_item_seq, initialized_at, last_updated）
- **WorkItem**：工作项（work_item_id, work_type, severity, source, recommended_flow, needs_human_confirmation, classification_confidence, status）
- **GovernanceState**：治理状态（frozen, frozen_at, items: dict[str, bool]）
- **Checkpoint**：断点（pipeline, current_stage, feature, multi_agent, prd_source, completed_stages, execute_progress, ai_decisions_count, execution_mode）
- **ResumePack**：恢复包（current_stage, current_batch, last_committed_task, working_set_snapshot, timestamp）
- **GateResult**：门禁结果（result: PASS|RETRY|HALT, details: list[str], failures: list[str]）
- **ExecutionBatch**：执行批次（batch_id, phase, tasks: list, status, started_at, completed_at）
- **PrdReadiness**：PRD 就绪检查（readiness: pass|fail, score, missing_sections, recommendations, structured_output）

---

## 成功标准

### 可度量结果

- **SC-001**：`ai-sdlc init` 在空目录中 < 2 秒内完成，产出完整 `.ai-sdlc/` 目录结构
- **SC-002**：Bootstrap Router 对 3 种项目状态的判断准确率 = 100%（确定性逻辑，无概率）
- **SC-003**：Work Intake Router 对 10 条测试输入的分类准确率 ≥ 80%
- **SC-004**：PRD Studio 对符合模板的完整 PRD 返回 `readiness = pass`，对缺失 2 个以上必填章节的 PRD 返回 `fail`
- **SC-005**：Governance Freeze 缺失任意 1 项时 100% 返回 FAIL
- **SC-006**：分支切换在有 uncommitted changes 时 100% 被拒绝
- **SC-007**：`ai-sdlc recover` 从 checkpoint 恢复后，执行位置与中断前一致（batch 号、task 号精确匹配）
- **SC-008**：全量 BR-xxx 业务规则测试通过率 = 100%
- **SC-009**：全量 AC-xxx 验收标准通过率 = 100%（P0 部分）
- **SC-010**：单 Agent 闭环可执行一个 3-Phase 的 tasks.md 从头到尾，无 HALT

##### P1 框架增强（与 FR-085～FR-089 / tasks Batch 7 对应）

- **SC-011**：`ai-sdlc workitem plan-check`（实现名以 PR 为准）在夹具中：当外部计划某 todo 为 `pending` 且 Git 已包含对应路径变更时，以**非零退出码**退出（或 `--json` 中报告漂移，由实现 PR 与 spec 锁定）。
- **SC-012**：`ai-sdlc verify constraints` 在缺少 `.ai-sdlc/memory/constitution.md` 或 checkpoint 与 `specs/` 明显冲突的夹具上**失败（非零）**。
- **SC-013**：在存在 `specs/WI-*` 且完成 **FR-088** 绑定流程后的夹具中，`ai-sdlc status` 展示的 Feature ID **不为** `unknown`（若绑定为可选则用户指南说明豁免条件）。

##### P1 收口与归档约束硬化（与 FR-091～FR-094 对应）

- **SC-017**：`ai-sdlc workitem close-check`（实现名以 PR 为准）在夹具中：任一收口项缺失（如 tasks 未完成、`related_plan` 漂移、execution-log 缺验证段）时**非零退出**并包含 `BLOCKER`。
- **SC-018**：更新后的 `execution-log` 模板在至少 1 个集成夹具中被实际使用，且能被 `close-check` 识别出「验证命令 / 审查结论 / 状态同步」字段。
- **SC-019**：当文档仍含“未实现前”但对应命令已存在时，`close-check` 或等效校验可发现并失败；修复后通过。
