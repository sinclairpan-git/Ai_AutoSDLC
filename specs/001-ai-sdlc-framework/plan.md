# 实施计划：AI-SDLC 框架 P0

**编号**：`001-ai-sdlc-framework` | **日期**：2026-03-21 | **规格**：specs/001-ai-sdlc-framework/spec.md

## 概述

构建 AI-SDLC 框架 P0 版本：一套 Python CLI 工具 + 规则文件集，支持从 greenfield 项目初始化到单 Agent 闭环执行的完整 SDLC 流程。采用自底向上策略：先搭建核心骨架（模型 + 状态机 + 文件 I/O），再逐层实现路由、Studio、治理、分支、执行引擎、Context Control Plane，最后集成 CLI 入口和端到端测试。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Typer (CLI), PyYAML, Pydantic v2, Jinja2, Rich  
**存储**：文件系统（YAML + JSON + Markdown）  
**测试**：pytest + pytest-mock + pytest-cov  
**目标平台**：macOS + Linux（P0）  
**约束**：见 constitution.md（MVP 优先、可验证、范围声明、状态落盘、代码隔离）

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 仅实现 P0 的 9 个模块，P1 模块不做预埋（除 Protocol 接口） |
| MUST-2 关键路径可验证 | 每个 Phase 完成后立即补充单元测试，gate 模块覆盖率 100% |
| MUST-3 范围声明与回退 | 每个 Phase 独立 commit，可单独 revert |
| MUST-4 状态落盘 | 所有状态通过 YamlStore 持久化，不依赖内存 |
| MUST-5 产品代码隔离 | 产品代码在 `src/ai_sdlc/`，开发框架在工作区根目录 |

## 项目结构

### 文档结构

```text
specs/001-ai-sdlc-framework/
├── spec.md
├── plan.md          ← 本文件
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md         ← Stage 3 生成
```

### 源码结构

```text
src/ai_sdlc/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── main.py              # Typer app 入口
│   ├── init_cmd.py          # ai-sdlc init
│   ├── status_cmd.py        # ai-sdlc status
│   ├── recover_cmd.py       # ai-sdlc recover
│   ├── index_cmd.py         # ai-sdlc index
│   └── gate_cmd.py          # ai-sdlc gate
├── core/
│   ├── __init__.py
│   ├── state_machine.py     # 工作项状态机
│   ├── runner.py            # SDLC Runner（流程编排）
│   ├── yaml_store.py        # YAML 读写封装
│   └── config.py            # 配置加载
├── routers/
│   ├── __init__.py
│   ├── bootstrap.py         # Project Bootstrap Router
│   └── work_intake.py       # Work Intake Router
├── studios/
│   ├── __init__.py
│   └── prd_studio.py        # PRD Studio（P0 仅 readiness review）
├── gates/
│   ├── __init__.py
│   ├── base.py              # GateProtocol + GateResult
│   ├── init_gate.py         # INIT 阶段门禁
│   ├── refine_gate.py       # REFINE 阶段门禁
│   ├── design_gate.py       # DESIGN 阶段门禁
│   ├── decompose_gate.py    # DECOMPOSE 阶段门禁
│   ├── verify_gate.py       # VERIFY 阶段门禁
│   ├── execute_gate.py      # EXECUTE 阶段门禁（批次级）
│   ├── close_gate.py        # CLOSE 阶段门禁
│   └── governance_guard.py  # Governance Freeze 检查
├── context/
│   ├── __init__.py
│   ├── checkpoint.py        # Checkpoint 管理
│   ├── resume.py            # Resume Pack 管理
│   └── working_set.py       # Working Set 管理
├── branch/
│   ├── __init__.py
│   ├── git_client.py        # Git CLI 封装
│   └── branch_manager.py    # Docs/Dev 分支管理
├── generators/
│   ├── __init__.py
│   ├── template_gen.py      # Jinja2 模板生成器
│   └── index_gen.py         # 索引生成器
├── models/
│   ├── __init__.py
│   ├── project.py           # ProjectState, ProjectConfig
│   ├── work_item.py         # WorkItem, WorkType, Severity...
│   ├── governance.py        # GovernanceState
│   ├── execution.py         # ExecutionPlan, Task, Batch
│   ├── context.py           # RuntimeState, WorkingSet, ResumePack
│   ├── checkpoint.py        # Checkpoint model
│   ├── gate.py              # GateResult, GateVerdict
│   └── prd.py               # PrdReadiness
├── utils/
│   ├── __init__.py
│   ├── fs.py                # 文件系统工具（pathlib 封装）
│   ├── time_utils.py        # 时间戳工具
│   └── text.py              # 文本处理工具
├── templates/               # Jinja2 模板（随产品分发）
│   ├── project-state.yaml.j2
│   ├── work-item.yaml.j2
│   └── ...
└── rules/                   # 产品内置规则（随产品分发）
    └── ...

tests/
├── conftest.py              # 共享 fixtures
├── unit/
│   ├── test_models.py
│   ├── test_state_machine.py
│   ├── test_yaml_store.py
│   ├── test_bootstrap_router.py
│   ├── test_work_intake_router.py
│   ├── test_prd_studio.py
│   ├── test_governance_guard.py
│   ├── test_branch_manager.py
│   ├── test_gates.py
│   ├── test_checkpoint.py
│   └── test_resume.py
├── flow/
│   ├── test_init_flow.py
│   ├── test_new_requirement_flow.py
│   └── test_recover_flow.py
└── integration/
    ├── test_cli_init.py
    ├── test_cli_status.py
    └── test_cli_recover.py
```

## 阶段计划

### Phase 0：项目脚手架

**目标**：创建可运行的 Python 项目骨架，所有模块目录和 `__init__.py` 就位，`ai-sdlc --help` 可执行。

**产物**：
- `pyproject.toml`（依赖 + 入口点）
- 目录结构 + 所有 `__init__.py`
- `src/ai_sdlc/cli/main.py`（Typer app，注册所有子命令占位）
- `tests/conftest.py`（基础 fixtures）

**验证方式**：`uv run ai-sdlc --help` 输出帮助信息；`uv run pytest` 无报错

**回退方式**：`git revert` 该 Phase 的 commit

### Phase 1：核心模型与基础设施

**目标**：实现所有 Pydantic 模型和基础工具（YamlStore、文件系统工具、时间工具）。

**产物**：
- `src/ai_sdlc/models/*.py`（全部 data-model.md 中定义的模型）
- `src/ai_sdlc/core/yaml_store.py`
- `src/ai_sdlc/core/config.py`
- `src/ai_sdlc/utils/*.py`
- `tests/unit/test_models.py`
- `tests/unit/test_yaml_store.py`

**验证方式**：所有模型可实例化、序列化/反序列化、默认值填充正确；YamlStore 读写一致

**回退方式**：`git revert`

### Phase 2：状态机与 Git 客户端

**目标**：实现工作项状态机和 Git 操作封装。

**产物**：
- `src/ai_sdlc/core/state_machine.py`
- `src/ai_sdlc/branch/git_client.py`
- `tests/unit/test_state_machine.py`

**验证方式**：所有 12 个合法转换通过；非法转换抛出 `InvalidTransitionError`；Git 操作在临时仓库中正确执行

**回退方式**：`git revert`

### Phase 3：路由器

**目标**：实现 Bootstrap Router 和 Work Intake Router。

**产物**：
- `src/ai_sdlc/routers/bootstrap.py`
- `src/ai_sdlc/routers/work_intake.py`
- `tests/unit/test_bootstrap_router.py`
- `tests/unit/test_work_intake_router.py`

**验证方式**：Bootstrap Router 对 3 种项目状态判断准确率 100%；Work Intake Router 对测试用例分类准确率 ≥ 80%

**回退方式**：`git revert`

### Phase 4：PRD Studio 与 Governance

**目标**：实现 PRD 就绪检查和治理层冻结。

**产物**：
- `src/ai_sdlc/studios/prd_studio.py`
- `src/ai_sdlc/gates/governance_guard.py`
- `tests/unit/test_prd_studio.py`
- `tests/unit/test_governance_guard.py`

**验证方式**：完整 PRD → readiness=pass；缺失章节 PRD → readiness=fail；governance 6 项检查正确

**回退方式**：`git revert`

### Phase 5：分支管理

**目标**：实现 docs/dev 双分支的创建、切换、合并、基线校验。

**产物**：
- `src/ai_sdlc/branch/branch_manager.py`
- `tests/unit/test_branch_manager.py`

**验证方式**：在临时仓库中完成分支创建→切换→合并全流程；uncommitted changes 拒绝切换；baseline recheck 正确

**回退方式**：`git revert`

### Phase 6：质量门禁

**目标**：实现所有阶段的 Gate 检查器。

**产物**：
- `src/ai_sdlc/gates/base.py`
- `src/ai_sdlc/gates/init_gate.py` ~ `close_gate.py`
- `tests/unit/test_gates.py`

**验证方式**：每个 gate 的 PASS/RETRY/HALT 条件全部覆盖；gate 模块覆盖率 100%

**回退方式**：`git revert`

### Phase 7：Context Control Plane

**目标**：实现 checkpoint、resume-pack、working-set 管理。

**产物**：
- `src/ai_sdlc/context/checkpoint.py`
- `src/ai_sdlc/context/resume.py`
- `src/ai_sdlc/context/working_set.py`
- `tests/unit/test_checkpoint.py`
- `tests/unit/test_resume.py`

**验证方式**：checkpoint 保存/加载一致；resume-pack 恢复到正确位置；损坏的 YAML 被正确处理

**回退方式**：`git revert`

### Phase 8：模板与索引生成器

**目标**：实现 Jinja2 模板生成器和项目索引生成器。

**产物**：
- `src/ai_sdlc/generators/template_gen.py`
- `src/ai_sdlc/generators/index_gen.py`
- `src/ai_sdlc/templates/*.j2`

**验证方式**：模板生成产出文件内容正确；索引生成扫描目录正确

**回退方式**：`git revert`

### Phase 9：CLI 命令集成

**目标**：将所有模块集成到 Typer CLI 命令中。

**产物**：
- `src/ai_sdlc/cli/init_cmd.py`
- `src/ai_sdlc/cli/status_cmd.py`
- `src/ai_sdlc/cli/recover_cmd.py`
- `src/ai_sdlc/cli/index_cmd.py`
- `src/ai_sdlc/cli/gate_cmd.py`
- `tests/integration/test_cli_*.py`

**验证方式**：每个 CLI 命令可运行且退出码正确

**回退方式**：`git revert`

### Phase 10：Runner 编排与流程测试

**目标**：实现 SDLC Runner（编排 init → refine → ... → close 全流程），添加流程测试。

**产物**：
- `src/ai_sdlc/core/runner.py`
- `tests/flow/test_init_flow.py`
- `tests/flow/test_new_requirement_flow.py`
- `tests/flow/test_recover_flow.py`

**验证方式**：端到端 dry-run 全流程无 HALT；中断恢复测试通过

**回退方式**：`git revert`

## 工作流计划

### 工作流 A：Init 流程

**范围**：`ai-sdlc init` → Bootstrap Router → 创建 `.ai-sdlc/` 目录 → 写入初始配置  
**影响范围**：`cli/init_cmd.py`, `routers/bootstrap.py`, `generators/template_gen.py`, `models/project.py`  
**验证方式**：`test_init_flow.py` 在空目录中运行 init 验证  
**回退方式**：删除 `.ai-sdlc/` 目录

### 工作流 B：New Requirement 闭环

**范围**：intake → PRD Studio → governance → docs branch → (spec/plan/tasks) → dev branch → execute → archive  
**影响范围**：几乎所有模块  
**验证方式**：`test_new_requirement_flow.py` 端到端  
**回退方式**：`git revert` feature branch

### 工作流 C：中断恢复

**范围**：checkpoint 保存 → 中断 → `ai-sdlc recover` → resume-pack 加载 → 继续执行  
**影响范围**：`context/`, `cli/recover_cmd.py`, `core/runner.py`  
**验证方式**：`test_recover_flow.py` 模拟中断场景  
**回退方式**：删除 checkpoint 重新运行

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| Bootstrap Router 正确分类 | 单元测试 3 种状态 | 集成测试 `ai-sdlc init` |
| Work Intake Router 分类 | 单元测试 10+ 输入 | 流程测试端到端 |
| Governance Freeze 阻断 | 单元测试缺失项 | 流程测试跳过 governance |
| 分支切换安全 | 单元测试 uncommitted 拒绝 | 集成测试真实 git 操作 |
| 状态机转换正确 | 单元测试所有合法/非法转换 | 流程测试全生命周期 |
| Checkpoint 恢复一致 | 单元测试保存/加载 | 流程测试中断恢复 |
| Gate 检查不可绕过 | 单元测试 PASS/RETRY/HALT | 流程测试跳阶段尝试 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| Rich 面板在 CI 环境的降级策略 | 待定 | Phase 9 |
| 产品内置规则文件的初始内容 | 待定 | Phase 8 |

## 实施顺序建议

```
Phase 0（脚手架）
  → Phase 1（模型 + 基础设施）
    → Phase 2（状态机 + Git 客户端）
      → Phase 3（路由器）
      → Phase 4（PRD Studio + Governance）  ← 可与 Phase 3 并行
        → Phase 5（分支管理）
          → Phase 6（质量门禁）
            → Phase 7（Context Control Plane）
              → Phase 8（模板 + 索引生成器）
                → Phase 9（CLI 集成）
                  → Phase 10（Runner + 流程测试）
```

## 增量设计（P1 backlog）— 工作项与外部计划状态对账

**背景**：见 spec **FR-085～FR-087**；根因为 **无单一真值**、计划 YAML **无门禁**、交付 **未绑定**「更新待办」步骤。

**设计要点**（仅文档层，实现见 tasks Task 6.2）：

1. **契约**：工作项 `tasks.md` / `plan.md` 可选 `related_plan`；DoD 显式包含「状态已同步或延期已登记」。
2. **可选 CLI**：`plan-check` 只读 diff，失败策略由项目 CI 策略决定（建议：警告非阻断，直至稳定后改为阻断）。
3. **流程**：PR / 合并说明模板中增加一行：「关联计划 id / tasks 条目：___；frontmatter 已更新：是/否」。

**宪章对齐**：MUST-4（状态外化）、MUST-1（P1 范围独立可回退批次）。

## 增量设计（P1 backlog）— 收口与归档约束硬化

**背景**：见 spec **FR-091～FR-094**；复盘显示仅“实现命令 + 跑测试”不足以防止交付收口漂移，需把“验证证据、代码审查、文档状态一致性、偏离产品化”做成可检查对象。

**设计要点**：

1. **收口检查器（只读）**：新增 `workitem close-check`（命名可调整），统一检查 tasks 完成度、related_plan 对账、execution-log 结构化证据、文档实现状态一致性，输出 BLOCKER。
2. **模板先行**：先扩展 execution-log 模板字段，再让 close-check 按模板字段识别，避免自由文本难校验。
3. **检查清单闭环**：PR 清单从“建议动作”升级为“最小验证集”，根据文档/代码变更类型要求不同命令集合。
4. **偏离登记产品化**：将 `agent-skip-registry` 作为需求输入源，要求“登记->spec/plan/tasks”同迭代闭环。

**验证策略**：

- 单元：close-check 各子检查器（tasks / plan / docs / log）独立夹具。
- 集成：一个 `specs/<WI>/` 最小仓库夹具覆盖 2 个失败路径 + 1 个通过路径。
- 回归：`uv run pytest` + `uv run ruff check src tests`。

**宪章对齐**：MUST-2（可验证）、MUST-3（独立可回退批次）、MUST-4（状态落盘）、MUST-5（规则与产品能力一致）。

## 增量设计（P1 backlog）— 规则作用域收敛与工程纪律

**背景**：见 spec **FR-095～FR-098** 与 `agent-skip-registry.zh.md`「工程纪律复盘（2026-03-26）」。首轮实现中已出现「全局登记表 + 全量 docs 扫描」导致 **误报与流程摩擦** 的风险；同时「归档哈希二次提交」增加审阅噪音。

**设计要点**：

1. **skip-registry 与 WI 绑定**：登记表增加 **`wi_id` 列**（已实现表头迁移见规则文件）；`verify constraints` 仅解析 **当前 WI 行** 的 FR/Task 引用做映射 BLOCKER；历史无 `wi_id` 行跳过自动阻断。
2. **close-check 文档扫描分层**：默认 **WI 目录 + 文档白名单**；`--all-docs` 显式扩大至全 `docs/**`，避免日常迭代被无关文档绊倒。
3. **归档与提交**：优先 **单 commit 携带 execution-log**；若保留哈希字段，则模板与 `batch-protocol.md` 同步改为「可选或批次末一次回填」，避免默认双提交。
4. **命令真值来源**：从 Typer `app` 遍历 command / typer 子树生成「完整子命令路径」集合，供 docs 漂移检查；单测覆盖「注册变更即检查同步」。

**阶段映射（杜绝先动手）**：

| 错误做法 | 对应误闯阶段 | 正确做法 |
|----------|--------------|----------|
| 直接改 `verify_constraints.py` / `close_check.py` | execute 抢跑 | 先 **decompose**：`tasks.md` Batch 10 任务与 AC 落盘 |
| 口头同意「缩小作用域」 | refine 未冻结 | 先 **spec**：FR-095～098、SC-020～023 写入 `spec.md` |
| 仅改代码不测历史行 | verify 不足 | **pytest** 夹具含「历史行不阻断」「白名单默认通过」 |

**验证策略**：

- 单元：`collect_constraint_blockers` 在混合登记表文本下的过滤逻辑；`close_check` 默认路径与 `--all-docs` 分支。
- 集成：CLI 层 `verify constraints`、`workitem close-check` 各至少 1 条回归。
- 全量：`uv run pytest` + `uv run ruff check src tests`。

**宪章对齐**：MUST-1（独立批次可回退）、MUST-2（可验证）、MUST-3（范围声明）、MUST-4（复盘与登记落盘）。
