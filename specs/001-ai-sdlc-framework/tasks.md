# 任务分解：AI-SDLC 框架 P0

**编号**：`001-ai-sdlc-framework` | **日期**：2026-03-21  
**来源**：plan.md (Phase 0–10) + spec.md (FR-001–FR-043) + data-model.md

---

## 分批策略

基于 plan.md 的依赖图，将 Phase 划分为 5 个 Batch（顺序执行），部分 Phase 可在 Batch 内并行。

```
Batch 1: Phase 0 → Phase 1          (串行：脚手架 → 模型)
Batch 2: Phase 2                     (串行：状态机 + Git 客户端)
Batch 3: Phase 3 ‖ Phase 4           (并行：路由器 ‖ PRD Studio + Governance)
Batch 4: Phase 5 → Phase 6 → Phase 7 → Phase 8  (串行：分支 → 门禁 → Context → 模板)
Batch 5: Phase 9 → Phase 10          (串行：CLI 集成 → Runner + 流程测试)
```

---

## Batch 1：项目脚手架 + 核心模型

### Task 1.1 — 创建 pyproject.toml 和项目骨架

- **Phase**：0
- **优先级**：P0
- **依赖**：无
- **输入**：plan.md 项目结构
- **产物**：
  - `pyproject.toml`（name=ai-sdlc, Python>=3.11, 声明 Typer/PyYAML/Pydantic/Jinja2/Rich 运行时依赖 + pytest/ruff/mypy 开发依赖 + `[project.scripts] ai-sdlc = "ai_sdlc.cli.main:app"` 入口）
  - `src/ai_sdlc/__init__.py`
  - 所有子包目录 + `__init__.py`（cli/, core/, routers/, studios/, gates/, context/, branch/, generators/, models/, utils/）
  - `src/ai_sdlc/templates/.gitkeep`
  - `src/ai_sdlc/rules/.gitkeep`
  - `tests/__init__.py`, `tests/unit/__init__.py`, `tests/flow/__init__.py`, `tests/integration/__init__.py`
- **验证**：`uv sync && uv run ai-sdlc --help` 退出码 0
- **关联 FR**：—（基础设施）

### Task 1.2 — Typer CLI 入口与子命令占位

- **Phase**：0
- **优先级**：P0
- **依赖**：Task 1.1
- **输入**：plan.md CLI 子命令列表
- **产物**：
  - `src/ai_sdlc/cli/main.py`：创建 `app = typer.Typer()`，注册 init / status / recover / index / gate 子命令
  - `src/ai_sdlc/cli/init_cmd.py`：占位 `def init_command(): raise typer.Exit()`
  - `src/ai_sdlc/cli/status_cmd.py`：占位
  - `src/ai_sdlc/cli/recover_cmd.py`：占位
  - `src/ai_sdlc/cli/index_cmd.py`：占位
  - `src/ai_sdlc/cli/gate_cmd.py`：占位
- **验证**：`uv run ai-sdlc --help` 显示 5 个子命令；`uv run ai-sdlc init --help` 不报错
- **关联 FR**：FR-001

### Task 1.3 — 基础 conftest 与 fixtures

- **Phase**：0
- **优先级**：P0
- **依赖**：Task 1.1
- **产物**：
  - `tests/conftest.py`：`tmp_project_dir` fixture（创建临时空目录）、`initialized_project_dir` fixture（含 `.ai-sdlc/`）、`git_repo` fixture（临时 git 仓库）
- **验证**：`uv run pytest tests/ --collect-only` 收集到 fixtures，无错误

### Task 1.4 — Pydantic 数据模型：项目级

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.1
- **输入**：data-model.md Section 1
- **产物**：
  - `src/ai_sdlc/models/__init__.py`：re-export 所有模型
  - `src/ai_sdlc/models/project.py`：`ProjectStatus`, `ProjectState`, `ProjectConfig`
- **验证**：`ProjectState()` 默认值正确；`ProjectState.model_validate(yaml_dict)` 反序列化正确
- **关联 FR**：FR-001, FR-070

### Task 1.5 — Pydantic 数据模型：工作项

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.1
- **输入**：data-model.md Section 2
- **产物**：
  - `src/ai_sdlc/models/work_item.py`：`WorkType`, `Severity`, `Source`, `Confidence`, `WorkItemStatus`, `WorkItem`
- **验证**：枚举值正确；`WorkItem(work_item_id="WI-2026-001", title="test", work_type=WorkType.NEW_REQUIREMENT)` 创建成功；`classification_confidence` 默认 0.0
- **关联 FR**：FR-003, FR-005, FR-080, FR-081

### Task 1.6 — Pydantic 数据模型：治理 + 执行 + Context

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.1
- **输入**：data-model.md Section 3, 4, 5, 6
- **产物**：
  - `src/ai_sdlc/models/governance.py`：`GovernanceState`
  - `src/ai_sdlc/models/execution.py`：`TaskStatus`, `Task`, `ExecutionBatch`, `ExecutionPlan`
  - `src/ai_sdlc/models/context.py`：`RuntimeState`, `WorkingSet`, `ResumePack`
  - `src/ai_sdlc/models/checkpoint.py`：`StageRecord`, `FeatureInfo`, `AgentCapabilities`, `Checkpoint`
  - `src/ai_sdlc/models/gate.py`：`GateVerdict`, `GateResult`
  - `src/ai_sdlc/models/prd.py`：`PrdReadiness`
- **验证**：所有模型可实例化，可 `model_dump()` → dict → `model_validate()` 往返
- **关联 FR**：FR-020, FR-040, FR-050, FR-060, FR-010

### Task 1.7 — YamlStore 封装

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.4
- **输入**：research.md Section 3
- **产物**：
  - `src/ai_sdlc/core/yaml_store.py`：`YamlStore` 类，封装 `load(path, model_class) -> T`、`save(path, model_instance)`、原子写入（先写 `.tmp` 再 rename）、损坏文件处理
- **验证**：`test_yaml_store.py`：保存→加载一致；损坏 YAML 抛出 `YamlStoreError`；路径不存在时返回默认值
- **关联 FR**：FR-054, FR-081

### Task 1.8 — 工具函数

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.1
- **产物**：
  - `src/ai_sdlc/utils/fs.py`：`ensure_dir(path)`, `find_project_root() -> Path | None`, `is_git_repo(path) -> bool`
  - `src/ai_sdlc/utils/time_utils.py`：`now_iso() -> str`, `parse_iso(s) -> datetime`
  - `src/ai_sdlc/utils/text.py`：`slugify(text) -> str`, `truncate(text, max_len) -> str`
- **验证**：各函数的基本行为正确
- **关联 FR**：—（基础设施）

### Task 1.9 — 配置加载器

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.7, Task 1.4
- **产物**：
  - `src/ai_sdlc/core/config.py`：`load_project_state(root) -> ProjectState`, `load_project_config(root) -> ProjectConfig`, `save_project_state(root, state)`
- **验证**：在空目录加载返回默认 `ProjectState(status=UNINITIALIZED)`；保存后再加载一致
- **关联 FR**：FR-001, FR-070

### Task 1.10 — 模型单元测试

- **Phase**：1
- **优先级**：P0
- **依赖**：Task 1.4 ~ 1.6
- **产物**：
  - `tests/unit/test_models.py`：覆盖所有模型的实例化、默认值、序列化/反序列化、枚举值、边界情况
  - `tests/unit/test_yaml_store.py`：覆盖 YamlStore 的正常读写、原子写入、损坏处理
- **验证**：`uv run pytest tests/unit/test_models.py tests/unit/test_yaml_store.py -v` 全部通过

---

## Batch 2：状态机 + Git 客户端

### Task 2.1 — 工作项状态机

- **Phase**：2
- **优先级**：P0
- **依赖**：Task 1.5
- **输入**：spec.md 用户故事 5 + data-model.md WorkItemStatus + PRD Section 9.3
- **产物**：
  - `src/ai_sdlc/core/state_machine.py`：
    - `TRANSITIONS: dict[WorkItemStatus, list[WorkItemStatus]]`（12 个合法转换）
    - `transition(current, target) -> WorkItemStatus`（合法则返回 target，非法则抛 `InvalidTransitionError`）
    - `get_valid_transitions(current) -> list[WorkItemStatus]`
    - `class InvalidTransitionError(Exception)`
- **验证**：12 个合法转换全部通过；至少 5 个非法转换正确拒绝
- **关联 FR**：FR-080, FR-081

### Task 2.2 — Git 客户端封装

- **Phase**：2
- **优先级**：P0
- **依赖**：Task 1.8
- **输入**：research.md Section 4
- **产物**：
  - `src/ai_sdlc/branch/git_client.py`：
    - `GitClient(repo_path: Path)` 类
    - 方法：`init()`, `current_branch() -> str`, `branch_exists(name) -> bool`, `create_branch(name, checkout=True)`, `checkout(name)`, `has_uncommitted_changes() -> bool`, `add_and_commit(message, paths)`, `merge(source, target)`
    - 所有操作通过 `subprocess.run` 调用 git CLI，失败抛 `GitError`
- **验证**：在 `git_repo` fixture 中测试所有方法
- **关联 FR**：FR-030, FR-032, FR-043

### Task 2.3 — 状态机 + Git 客户端单元测试

- **Phase**：2
- **优先级**：P0
- **依赖**：Task 2.1, Task 2.2
- **产物**：
  - `tests/unit/test_state_machine.py`：覆盖全部合法/非法转换
  - 扩展 `tests/conftest.py`：`git_repo` fixture 更新（如需要）
- **验证**：`uv run pytest tests/unit/test_state_machine.py -v` 全部通过

---

## Batch 3：路由器 + PRD Studio + Governance（可并行）

### Task 3.1 — Bootstrap Router

- **Phase**：3
- **优先级**：P0
- **依赖**：Task 1.9
- **输入**：spec.md 用户故事 1/2 + PRD Section 8.2
- **产物**：
  - `src/ai_sdlc/routers/bootstrap.py`：
    - `detect_project_state(root: Path) -> str`（返回 `"greenfield"` / `"existing_project_initialized"` / `"existing_project_uninitialized"`）
    - `init_project(root: Path, project_name: str) -> ProjectState`（创建 `.ai-sdlc/` 目录结构 + 写入初始文件）
    - 幂等性：已初始化的项目不覆盖
- **验证**：3 种状态判断 100% 准确；重复 init 不覆盖
- **关联 FR**：FR-001, FR-002, FR-070, BR-001~BR-003

### Task 3.2 — Work Intake Router

- **Phase**：3
- **优先级**：P0
- **依赖**：Task 1.5, Task 1.7
- **输入**：spec.md 用户故事 3 + PRD Section 8.3
- **产物**：
  - `src/ai_sdlc/routers/work_intake.py`：
    - `WorkIntakeRouter` 类 (Protocol-based 可替换设计)
    - `classify(description: str) -> WorkItem`（P0 用关键词匹配：`new_requirement` / `production_issue` / `change_request` / `maintenance_task` / `uncertain`）
    - `generate_work_item_id(seq: int) -> str`（格式 `WI-YYYY-NNN`）
    - `uncertain` 类型返回 `classification_confidence < 0.6` + 需要用户确认
- **验证**：10+ 测试用例分类准确率 ≥ 80%；uncertain 触发确认
- **关联 FR**：FR-003, FR-004, FR-005, BR-010~BR-013

### Task 3.3 — 路由器单元测试

- **Phase**：3
- **优先级**：P0
- **依赖**：Task 3.1, Task 3.2
- **产物**：
  - `tests/unit/test_bootstrap_router.py`
  - `tests/unit/test_work_intake_router.py`
- **验证**：全部通过

### Task 3.4 — PRD Studio（readiness check）

- **Phase**：4
- **优先级**：P0
- **依赖**：Task 1.6
- **输入**：spec.md 用户故事 4 + PRD Section 8.4.1
- **产物**：
  - `src/ai_sdlc/studios/prd_studio.py`：
    - `check_prd_readiness(prd_path: Path) -> PrdReadiness`
    - 检查项：必需章节存在（目标、范围、用户角色、功能需求、验收标准），无 TBD/TODO 标记，非空
    - 返回 `PrdReadiness(ready=bool, missing=list[str], score=float)`
- **验证**：完整 PRD → ready=True；缺章节 PRD → ready=False + missing 列表正确
- **关联 FR**：FR-010, FR-011, FR-012

### Task 3.5 — Governance Guard

- **Phase**：4
- **优先级**：P0
- **依赖**：Task 1.6
- **输入**：PRD Section 8.5 + BR-020~024
- **产物**：
  - `src/ai_sdlc/gates/governance_guard.py`：
    - `check_governance(root: Path, work_item: WorkItem) -> GateResult`
    - 检查项：
      1. PRD readiness = pass
      2. 治理冻结未过期
      3. 工作项状态合法
      4. 当前分支正确
      5. 无 uncommitted changes
      6. AI 自主决策次数 < 阈值
- **验证**：6 项检查分别测试 pass/fail
- **关联 FR**：FR-020, FR-021, FR-022, FR-023, BR-020~BR-024

### Task 3.6 — PRD Studio + Governance 单元测试

- **Phase**：4
- **优先级**：P0
- **依赖**：Task 3.4, Task 3.5
- **产物**：
  - `tests/unit/test_prd_studio.py`
  - `tests/unit/test_governance_guard.py`
- **验证**：全部通过

---

## Batch 4：分支 → 门禁 → Context → 模板

### Task 4.1 — Branch Manager

- **Phase**：5
- **优先级**：P0
- **依赖**：Task 2.2
- **输入**：PRD Section 8.6 + BR-030~033
- **产物**：
  - `src/ai_sdlc/branch/branch_manager.py`：
    - `BranchManager(git_client: GitClient)` 类
    - `create_docs_branch(work_item_id: str)`：创建 `design/<id>-docs` 分支
    - `create_dev_branch(work_item_id: str)`：创建 `feature/<id>-dev` 分支
    - `switch_to_docs(work_item_id)`：切换到 docs 分支（uncommitted changes 则拒绝）
    - `switch_to_dev(work_item_id)`：切换到 dev 分支
    - `merge_to_main(branch_name)`：合并到 main
    - `check_baseline()`：基线一致性检查
- **验证**：在 `git_repo` fixture 中完成全流程；uncommitted 拒绝切换
- **关联 FR**：FR-030, FR-031, FR-032, FR-033, FR-034, BR-030~BR-033

### Task 4.2 — Branch Manager 单元测试

- **Phase**：5
- **优先级**：P0
- **依赖**：Task 4.1
- **产物**：`tests/unit/test_branch_manager.py`
- **验证**：全部通过

### Task 4.3 — Gate 基础设施 + INIT Gate

- **Phase**：6
- **优先级**：P0
- **依赖**：Task 1.6
- **输入**：PRD Section 9.2 quality-gate 定义
- **产物**：
  - `src/ai_sdlc/gates/base.py`：
    - `class GateProtocol(Protocol)` → `check(context) -> GateResult`
    - `class GateRegistry` → 注册/查找 gate
  - `src/ai_sdlc/gates/init_gate.py`：检查 `.ai-sdlc/` 存在、`project-state.yaml` valid、Git 已初始化
- **验证**：通过/不通过条件各至少 1 个测试用例
- **关联 FR**：FR-060, FR-061

### Task 4.4 — REFINE / DESIGN / DECOMPOSE Gates

- **Phase**：6
- **优先级**：P0
- **依赖**：Task 4.3
- **产物**：
  - `src/ai_sdlc/gates/refine_gate.py`：检查 spec.md 存在、无 NEEDS_CLARIFICATION、所有 FR 有编号
  - `src/ai_sdlc/gates/design_gate.py`：检查 plan.md / research.md / data-model.md 存在、plan 引用 constitution
  - `src/ai_sdlc/gates/decompose_gate.py`：检查 tasks.md 存在、任务有依赖关系、无循环依赖
- **验证**：每个 gate 的 PASS/RETRY 条件至少 1 个测试
- **关联 FR**：FR-060, FR-062

### Task 4.5 — VERIFY / EXECUTE / CLOSE Gates

- **Phase**：6
- **优先级**：P0
- **依赖**：Task 4.3
- **产物**：
  - `src/ai_sdlc/gates/verify_gate.py`：检查任务列表审核通过
  - `src/ai_sdlc/gates/execute_gate.py`：检查当前批次全部任务完成、测试通过
  - `src/ai_sdlc/gates/close_gate.py`：检查全部批次完成、覆盖率达标、lint 通过
- **验证**：每个 gate 的 PASS/RETRY 条件至少 1 个测试
- **关联 FR**：FR-060, FR-063

### Task 4.6 — Gate 单元测试

- **Phase**：6
- **优先级**：P0
- **依赖**：Task 4.3 ~ 4.5
- **产物**：`tests/unit/test_gates.py`：所有 7 个 gate 的 PASS/RETRY/HALT 测试
- **验证**：gate 模块覆盖率 100%

### Task 4.7 — Checkpoint Manager

- **Phase**：7
- **优先级**：P0
- **依赖**：Task 1.7, Task 1.6
- **输入**：spec.md 用户故事 7 + data-model.md Checkpoint
- **产物**：
  - `src/ai_sdlc/context/checkpoint.py`：
    - `save_checkpoint(root, checkpoint: Checkpoint)`
    - `load_checkpoint(root) -> Checkpoint | None`
    - `update_stage(root, stage, artifacts)`
    - 自动备份上一版本（`checkpoint.yml.bak`）
- **验证**：保存/加载一致；损坏文件时加载 `.bak`
- **关联 FR**：FR-050, FR-054

### Task 4.8 — Resume Pack Manager

- **Phase**：7
- **优先级**：P0
- **依赖**：Task 4.7
- **输入**：spec.md 用户故事 8 + data-model.md ResumePack
- **产物**：
  - `src/ai_sdlc/context/resume.py`：
    - `build_resume_pack(root) -> ResumePack`（从 checkpoint + 文件系统重建上下文）
    - `save_resume_pack(root, pack)`
- **验证**：从中断状态正确重建 resume-pack
- **关联 FR**：FR-051, FR-052, FR-053

### Task 4.9 — Working Set Manager

- **Phase**：7
- **优先级**：P0
- **依赖**：Task 1.6
- **输入**：data-model.md WorkingSet
- **产物**：
  - `src/ai_sdlc/context/working_set.py`：
    - `build_working_set(root, stage) -> WorkingSet`（按当前阶段组装所需上下文文件列表）
    - 文件变化时可增量更新
- **验证**：不同阶段返回正确的文件列表
- **关联 FR**：—（基础设施）

### Task 4.10 — Context 单元测试

- **Phase**：7
- **优先级**：P0
- **依赖**：Task 4.7 ~ 4.9
- **产物**：
  - `tests/unit/test_checkpoint.py`
  - `tests/unit/test_resume.py`
- **验证**：全部通过

### Task 4.11 — Jinja2 模板生成器

- **Phase**：8
- **优先级**：P0
- **依赖**：Task 1.4, Task 1.5
- **产物**：
  - `src/ai_sdlc/generators/template_gen.py`：
    - `TemplateGenerator(template_dir: Path)` 类
    - `render(template_name, context: dict) -> str`
    - `render_to_file(template_name, context, output_path)`
  - `src/ai_sdlc/templates/project-state.yaml.j2`
  - `src/ai_sdlc/templates/work-item.yaml.j2`
  - `src/ai_sdlc/templates/project-config.yaml.j2`
- **验证**：渲染产出 YAML 可被 Pydantic 模型解析
- **关联 FR**：FR-082

### Task 4.12 — Index 生成器

- **Phase**：8
- **优先级**：P0
- **依赖**：Task 1.7
- **产物**：
  - `src/ai_sdlc/generators/index_gen.py`：
    - `generate_index(root: Path) -> dict`（扫描 `.ai-sdlc/` 目录生成结构化索引）
    - `save_index(root, index)`
- **验证**：在含 `.ai-sdlc/` 的目录中生成正确索引
- **关联 FR**：FR-083

---

## Batch 5：CLI 集成 + Runner + 流程测试

### Task 5.1 — CLI: init 命令

- **Phase**：9
- **优先级**：P0
- **依赖**：Task 3.1, Task 4.11
- **产物**：
  - `src/ai_sdlc/cli/init_cmd.py`：
    - 调用 `detect_project_state()` → 路由
    - greenfield → `init_project()` → 输出成功信息 (Rich)
    - already initialized → 输出提示信息
  - `tests/integration/test_cli_init.py`
- **验证**：`uv run ai-sdlc init` 在空目录创建 `.ai-sdlc/`；重复运行不覆盖
- **关联 FR**：FR-070, FR-001, AC-001

### Task 5.2 — CLI: status 命令

- **Phase**：9
- **优先级**：P0
- **依赖**：Task 1.9, Task 4.7
- **产物**：
  - `src/ai_sdlc/cli/status_cmd.py`：
    - 读取 `project-state.yaml` + `checkpoint.yml`
    - 输出当前阶段、工作项状态、分支信息 (Rich Table)
  - `tests/integration/test_cli_status.py`
- **验证**：在初始化后的项目中输出正确状态
- **关联 FR**：FR-071

### Task 5.3 — CLI: recover 命令

- **Phase**：9
- **优先级**：P0
- **依赖**：Task 4.8
- **产物**：
  - `src/ai_sdlc/cli/recover_cmd.py`：
    - 加载 checkpoint → build resume-pack → 输出恢复信息
  - `tests/integration/test_cli_recover.py`
- **验证**：在有 checkpoint 的项目中正确恢复
- **关联 FR**：FR-072, AC-009

### Task 5.4 — CLI: index 命令

- **Phase**：9
- **优先级**：P0
- **依赖**：Task 4.12
- **产物**：
  - `src/ai_sdlc/cli/index_cmd.py`：
    - 调用 `generate_index()` → `save_index()` → 输出摘要
- **验证**：在初始化项目中运行输出索引文件
- **关联 FR**：FR-073

### Task 5.5 — CLI: gate 命令

- **Phase**：9
- **优先级**：P0
- **依赖**：Task 4.3 ~ 4.6
- **产物**：
  - `src/ai_sdlc/cli/gate_cmd.py`：
    - `ai-sdlc gate <stage_name>`
    - 从 GateRegistry 查找 gate → 执行 → 输出 PASS/RETRY/HALT (Rich)
- **验证**：`ai-sdlc gate init` 在已初始化项目中返回 PASS
- **关联 FR**：FR-074

### Task 5.6 — SDLC Runner

- **Phase**：10
- **优先级**：P0
- **依赖**：Task 5.1 ~ 5.5, Task 2.1, Task 3.5
- **输入**：PRD Section 8.11
- **产物**：
  - `src/ai_sdlc/core/runner.py`：
    - `SDLCRunner(root: Path)` 类
    - `run(mode: str = "auto")`：编排 INIT → REFINE → DESIGN → DECOMPOSE → VERIFY → EXECUTE → CLOSE
    - 每阶段：执行 → gate 检查 → checkpoint 保存
    - RETRY 时自修复（最多 3 次） → HALT 时停止
    - 支持从 checkpoint 续跑
- **验证**：dry-run 模式全流程无 HALT
- **关联 FR**：FR-040, FR-041, FR-044, FR-045, FR-080, AC-010

### Task 5.7 — Init 流程测试

- **Phase**：10
- **优先级**：P0
- **依赖**：Task 5.6
- **产物**：`tests/flow/test_init_flow.py`
  - 测试场景：空目录 init → status → 验证
- **验证**：全部通过

### Task 5.8 — New Requirement 闭环流程测试

- **Phase**：10
- **优先级**：P0
- **依赖**：Task 5.6
- **产物**：`tests/flow/test_new_requirement_flow.py`
  - 测试场景：init → intake → PRD check → governance → 状态转换
- **验证**：全部通过

### Task 5.9 — 中断恢复流程测试

- **Phase**：10
- **优先级**：P0
- **依赖**：Task 5.6
- **产物**：`tests/flow/test_recover_flow.py`
  - 测试场景：运行到 DESIGN → 中断 → recover → 从 DESIGN 继续
- **验证**：全部通过

---

## Batch 6（增量）：多平台与 IDE 解耦 — T10 全仓可移植性审计

> 来源：阶段状态 / 防代理跳过 / 可移植性规划合并入本工作项（与 P0 Phase 无编号冲突，作为交付后增量）。

### Task 6.1 — T10：全仓可移植性审计与修订

- **Phase**：增量（文档 + 可选代码）
- **优先级**：P1（可分轮：先文档后代码）
- **依赖**：可与既有 Batch 1–5 并行推进；**建议在**用户指南与可选 IDE 模板相关改动（如 Task 5.x 文档类后续、或独立文档 PR）**收口后再做一次全仓扫尾**
- **输入**：产品约束「规范真值以 CLI、门禁、YamlStore、`src/ai_sdlc/rules`、用户指南为准；各 IDE 仅为可选适配」
- **产物**：
  - **审计表**（Markdown 或 `docs/` 内附件）：列 `路径 | 原表述摘要 | 修订后 | 优先级(P0/P1/延期)`；覆盖全仓依赖 **Cursor 专有特征作为唯一落地依据** 的需求与说明
  - **修订 PR**：将上述项改为多平台、与具体 IDE 解耦的表述与实现（见下）
- **审计范围（执行时补全，非穷尽）**：
  - `docs/**`、`src/ai_sdlc/**`（含 CLI 用户可见字符串、`integrations/ide_adapter` 等）、`templates/**`、`specs/**`、仓库根 `README*`、安装/集成相关脚本
  - 检索词示例：`cursor`、`plan mode`、`.cursor/`（除明确标注「可选示例」的说明外）、将某一编辑器路径或 UI 流程写为**唯一**操作路径的 Agent 规则引用
  - 若代码以 **Cursor 专有 API** 或单一编辑器为条件分支，须评估改为 **CLI/配置驱动**，或拆为**可选插件**并在文档中标明「非必需」
- **验证**：
  - 审计表 P0/P1 项已关闭或已登记显式延期与原因
  - 用户指南与相关 AC：**不得**将 Cursor 专有流程写为唯一路径；凡提及 `.cursor/` 或某 IDE，须同时给出 **终端 + `python -m ai_sdlc`** 等价路径（或与 `USER_GUIDE` 中通用入口一致）
  - 可选：`rg -i "cursor|plan mode" --glob '!**/.cursor/**'` 等命令复核（排除已允许的「可选示例」段落）
- **收口记录（2026-03-24，补做）**：
  - `uv run pytest`：**485 passed**（全量）。
  - `uv run ruff check src tests`：**通过**（本批主要为 Markdown/规则；无新增 Python 行为变更）。
  - 与 **Task 6.1** 验证对齐：审计表 **P1/P2 文档项已关闭**；**根目录 PRD** 仍为延期（见审计表）；**M6**：文档/规则类可移植性收口**已满足**本 Task 对「不将 Cursor 作唯一路径」之要求；PRD 正文改版另排期。
  - 代理偏离 **「先合并文档/规则再补全量测试」** 已记入 [`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../../src/ai_sdlc/rules/agent-skip-registry.zh.md) 登记表（根因 A/B）。
- **关联**：可移植性验收（计划文档 verify 第 7 条）；与 `design → decompose → verify → execute` 流程文档（T8 类任务）互补

### Task 6.2 — P1：工作项 / 外部计划状态对账（仅需求与设计文档，无实现）

- **Phase**：增量（P1 backlog）
- **优先级**：P1
- **依赖**：spec **FR-085～FR-087**；本 plan §增量设计
- **输入**：复盘现象「计划 frontmatter 全 pending 与仓库事实不符」
- **产物（仅文档，禁止本任务内写产品代码）**：
  1. **用户指南** 段落：DoD 含「关联 tasks/计划状态已同步」（FR-085）。
  2. **specs 模板或说明**：`related_plan` 字段约定示例（FR-086）。
  3. **CLI 规格一页**（Markdown）：`plan-check` 行为、退出码、与 preflight 关系（FR-087）——**不写 Python 实现**。
  4. **PR/贡献说明** 模板片段（可置于 `docs/` 或 `.github`）：合并前勾选「已更新计划/todos」。
- **验证**：文档审阅通过；**不包含** pytest（实现阶段另开任务）。
- **关联 FR**：FR-085, FR-086, FR-087
- **文档子产物（已落地，无代码）**：
  1. [`docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md) **§2.1**（DoD / 计划状态 / 指向 plan-check 规格与 PR 清单）。
  2. [`templates/tasks-template.md`](../../templates/tasks-template.md) 增加 **可选 frontmatter `related_plan`** 说明（FR-086）。
  3. [`docs/plan-check-cli-spec.zh.md`](../../docs/plan-check-cli-spec.zh.md)（FR-087，仅规格）。
  4. [`docs/pull-request-checklist.zh.md`](../../docs/pull-request-checklist.zh.md)（合并前自检）。

---

## Batch 7（P1 实现）：框架代码增强 — **须先满足本表 AC 再写代码**

> **工程约束**（与宪章一致）：**不得**在未完成本 Batch 对应 **tasks 分解与 AC** 的情况下直接实现；实现 PR 须 **独立可回退**（MUST-3）、**带 pytest**（MUST-2）。顺序建议：**6.3 → 6.4 → 6.5**（可 6.3∥6.4 若人力分拆）。

### Task 6.3 — 实现 `workitem plan-check`（FR-087）

- **依赖**：[`docs/plan-check-cli-spec.zh.md`](../../docs/plan-check-cli-spec.zh.md)；Task 6.2 文档已合并。
- **验收标准（AC）**：
  1. CLI 注册子命令（名称以 [`docs/plan-check-cli-spec.zh.md`](../../docs/plan-check-cli-spec.zh.md) 为准或等价）。
  2. `--help` 说明只读、不写 `checkpoint`。
  3. 至少一个 **单元/集成** 夹具：`pending` todo + 模拟已变路径 → **非零退出**或 `--json` 报告漂移（与 **SC-011** 一致）。
  4. `uv run pytest` 全量通过；本任务新增测试文件可定位。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-087，SC-011。

### Task 6.4 — Checkpoint 可选关联元数据 + `status` 展示（FR-088）

- **依赖**：ADR 或本 spec 对字段名的最终锁定；Task 6.3 可与本任务 **并行**（不同文件为主）。
- **验收标准（AC）**：
  1. 旧 `checkpoint.yml` **无新字段仍可加载**（默认值或省略）。
  2. 新字段写入经 YamlStore，**原子写**。
  3. `ai-sdlc status` 多一行（或固定表格行）展示 `linked_wi_id` / `linked_plan_uri` / `last_synced_at` 中有值者。
  4. 单元测试覆盖序列化与缺省。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-088；与 SC-013 协同（绑定逻辑若不在本任务则 **另开 6.4b** 须注明）。

### Task 6.5 — 实现 `verify constraints`（FR-089）

- **依赖**：与 pipeline 中「必读」路径表一致（实现时引用 `context/state.py` 或规则清单）。
- **验收标准（AC）**：
  1. 子命令 **只读**，默认不改 checkpoint。
  2. 缺 constitution 或 checkpoint↔specs 冲突夹具上 **非零退出**，stdout/stderr 含 **BLOCKER** 字样或结构化列表。
  3. pytest 覆盖至少 2 个负面路径 + 1 个通过路径。
  4. 与 **preflight** 文档关系在 `--help` 或 `docs/` 中 **一句说清**。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-089，SC-012。

> **Batch 7 代码收口（2026-03-25）**：Task **6.3～6.5** 的验证命令、审查摘要与 git 提交见 [`task-execution-log.md`](task-execution-log.md) 中 **Batch 2026-03-25-001**；主提交 `db1425d260aab6465973ecc34248b1bc26541402`；仅文档跟进 `5f994b7f0b7c0558961db3582403924be73efc9f`（execution-log SHA）、`a1bcbe60b659ac171f06ce9181b23f37448a516f`（tasks.md 收口指针）。未启动的 Task 6.6 及后续批次不在此收口范围。

### Task 6.6 — 仅文档：`pipeline`「已有产物」例外 vs Runner 对照表（可选，可与代码并行）

- **产物**：`specs/001-ai-sdlc-framework/` 下 `adr-001-pipeline-vs-runner.md` 或 `research.md` 附录一节；表格列：规则条文、代码行为、缺口、建议（reconcile / 仅文档）。
- **验证**：审阅通过；无 pytest。
- **关联**：计划 todo `gap-pipeline-rule-vs-code`。

> **Task 6.6 收口（2026-03-25）**：对照表已落地为 [`research-pipeline-vs-runner.md`](research-pipeline-vs-runner.md)（规则条文 / Runner·Gate 行为 / 缺口 / 建议）；与 `pipeline.md`「已有产物例外」文档对齐结论：**阶段推进以 checkpoint + 门禁为准，Runner 不自动按文件探测跳阶段**。

---

## Batch 8（P1）：可规划 vs 须分解后才能执行 — **原仅见于 Cursor 计划 *Plan vs execute gates***

> **来源**：`.cursor/plans/plan_vs_execute_gates_bab19f77.plan.md`（IDE 路径因环境而异）；本 Batch 将其中条目**全部**拆解为可执行 task + AC。  
> **工程约束**：与 Batch 7 相同——须先满足本表 AC 再写代码；**建议顺序 6.7 → 6.8 → 6.9**（6.10 可与 6.9 并行或后置）。

### Task 6.7 — 规格与模板：FR-090、SC-014（仅文档，无产品代码）

- **依赖**：无（可与 Batch 7 文档任务并行）。
- **产物**：
  1. [`spec.md`](spec.md) **P1 backlog**：新增 **FR-090**——DECOMPOSE Gate（或等效只读校验）须确保 `specs/<WI>/tasks.md` 中每个 `### Task …` 区块含至少一类任务级可验收表述（`验收标准`、`AC`、或与本仓库一致的 `**验证**`）；与 **FR-062**（spec 层）区分。
  2. [`spec.md`](spec.md) 成功标准：新增 **SC-014**——夹具上某 Task 缺上述字段时 `ai-sdlc` `gate` `check` `decompose` **非零退出**，且失败信息指明任务标识。
  3. [`templates/tasks-template.md`](../../templates/tasks-template.md)：注明每个任务块须含 **验证 / 验收标准**，否则 DECOMPOSE 不过。
- **验收标准（AC）**：审阅通过；三处产物互相引用一致。
- **验证**：无 pytest。
- **关联 FR / SC**：FR-090，SC-014。

### Task 6.8 — 实现：`DecomposeGate` 任务级 AC 校验

- **依赖**：Task **6.7**（字段名与匹配规则以 spec 为准）。
- **输入**：[`src/ai_sdlc/gates/pipeline_gates.py`](../../src/ai_sdlc/gates/pipeline_gates.py) 现有 `DecomposeGate`。
- **验收标准（AC）**：
  1. 按 `### Task` 分段解析 `tasks.md`；每段须含 FR-090 锁定的一类「验收」行。
  2. 失败时 `GateCheck.message` 指出**首个**不合规的 Task（从标题提取 id，如 `1.2`）。
  3. pytest：至少 **通过** 与 **缺失 AC** 两个夹具；`uv run ruff check src tests` 通过。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-090，SC-014。

### Task 6.9 — 实现：`ExecuteGate` 前置只读检查（防单独 `gate check execute`）

- **依赖**：Task **6.8**（或与 6.8 同一 PR 若强耦合）。
- **输入**：[`src/ai_sdlc/gates/pipeline_gates.py`](../../src/ai_sdlc/gates/pipeline_gates.py) `ExecuteGate`；[`src/ai_sdlc/cli/sub_apps.py`](../../src/ai_sdlc/cli/sub_apps.py) `_build_context`；[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py) `_enrich_execute_context`。
- **验收标准（AC）**：
  1. 当存在 `spec_dir/tasks.md` 且 DecomposeGate 对同一目录会 **RETRY** 时，ExecuteGate **不得 PASS**（verdict 为 RETRY 或 HALT，**由实现 PR 与 spec 锁死**并写入 FR-090 旁注若需要）。
  2. pytest 覆盖「仅调用 `gate check execute`、tasks 未就绪」场景；不破坏 Runner 在正常进度下注入的 execute 上下文。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-090（延伸）。

### Task 6.10 —（可选）共用校验模块 + `verify constraints` 与 SC-014 对齐

- **依赖**：Task **6.8**；**Task 6.5**（FR-089）已实现或同 PR 协调。
- **产物**：例如 `ai_sdlc/gates/task_ac_checks.py`（名称以 PR 为准），供 `DecomposeGate` 与 `ai-sdlc verify constraints` 共用；避免两套规则漂移。
- **验收标准（AC）**：
  1. `verify constraints` 在缺任务级 AC 的夹具上可报告 **BLOCKER**（或与 gate 行为一致的非零退出），与 **SC-014** 一致。
  2. pytest 覆盖共用函数；文档一句说明与 `gate decompose` 的关系。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-089，SC-014。

> **Task 6.10 收口（2026-03-25）**：共用模块已为 [`src/ai_sdlc/gates/task_ac_checks.py`](../../src/ai_sdlc/gates/task_ac_checks.py)（`first_task_missing_acceptance`）；[`DecomposeGate` / `ExecuteGate`](../../src/ai_sdlc/gates/pipeline_gates.py) 与 [`verify constraints`](../../src/ai_sdlc/core/verify_constraints.py) 均引用同一实现；单测 [`tests/unit/test_task_ac_checks.py`](../../tests/unit/test_task_ac_checks.py)；`ai-sdlc verify constraints --help` 已写明与 **SC-014** / gate decompose 一致。本可选任务按 AC **已完成**。

**Batch 7～8 可选进度（已关闭项）**

- [x] Task **6.6** — `pipeline` vs Runner 对照（见 [`research-pipeline-vs-runner.md`](research-pipeline-vs-runner.md) 与 Task 6.6 收口块）
- [x] Task **6.10** — 共用校验与 `verify constraints` / SC-014 对齐（见 Task 6.10 收口块）

---

## Batch 9（P1）：收口与归档约束硬化（FR-091～FR-094）

> **工程约束**：遵循 MUST-2/3/4/5；先文档契约后代码实现；每个 Task 必须有可验证 AC 与回归命令记录。建议顺序：**6.11 → 6.12 → 6.13**，6.14 并行或收尾执行。

### Task 6.11 — 规格与模板：收口约束契约落盘（仅文档）

- **依赖**：无。
- **产物**：
  1. [`spec.md`](spec.md) 增补 FR-091～FR-094 与 SC-017～SC-019（收口检查、模板字段、清单闭环、偏离产品化）。
  2. `templates/execution-log-template.md`（或等效模板）增加「验证命令」「代码审查结论」「任务/计划同步状态」字段。
  3. `docs/pull-request-checklist.zh.md` 补“最小验证集”说明（文档变更/代码变更两类）。
- **验收标准（AC）**：
  1. spec/模板/清单三处术语一致（close-check、BLOCKER、related_plan）。
  2. 文档中不再出现“已实现命令仍标未实现”的矛盾描述。
- **验证**：人工审阅；必要时 markdown 链接检查。
- **关联 FR / SC**：FR-091～094，SC-018，SC-019。

### Task 6.12 — 实现：`ai-sdlc workitem close-check`（只读）

- **依赖**：Task 6.11。
- **输入**：`src/ai_sdlc/cli/workitem_cmd.py`、新增 `src/ai_sdlc/core/close_check.py`（名称可调整）。
- **验收标准（AC）**：
  1. 子命令只读，默认不改 checkpoint；`--help` 明确与 close 收口关系。
  2. 至少检查并输出 BLOCKER：tasks 完成度、related_plan 漂移、execution-log 关键字段缺失。
  3. 支持 `--json` 机器可读输出（字段至少包含 `ok`、`blockers`、`checks`）。
  4. pytest 覆盖 ≥2 负面 + 1 正向夹具；ruff 通过。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-091，SC-017。

### Task 6.13 — 文档一致性检查：实现状态漂移防回归

- **依赖**：Task 6.12（可复用 close-check 的 docs 子检查）。
- **验收标准（AC）**：
  1. 当 docs 含 **SC-019** 所称漂移关键字组合且命令已注册时，close-check 报 BLOCKER。
  2. 修正文档后同夹具转为通过。
  3. 测试夹具至少覆盖 `workitem plan-check` 与 `verify constraints` 两条命令的文档一致性。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-091，FR-093，SC-019。

### Task 6.14 — 偏离登记产品化闭环（规则 + 自动检查）

- **依赖**：Task 6.11（可并行实现检查脚本）。
- **产物**：在 `verify constraints` 或独立只读检查中加入“skip-registry 新条目未映射到 spec/tasks”的告警或 BLOCKER（策略在实现 PR 锁定）。
- **验收标准（AC）**：
  1. 提供最小映射规则（如登记项含 FR/Task 关键字，或在 tasks 中有对应 batch/task 引用）。
  2. 至少 1 个负面夹具（仅登记未落 spec/tasks）与 1 个正面夹具（已映射）通过测试。
- **验证**：pytest + ruff。
- **关联 FR / SC**：FR-094，SC-017（延伸）。

---

## Batch 10（P1）：规则作用域收敛与工程纪律（FR-095～FR-098）

> **工程约束**：须先完成 **Task 6.15**（契约与登记表结构落盘），再进入 **6.16～6.19** 实现批次；**禁止**在 6.15 未完成时修改 `src/`、`tests/`（与本 Batch 目标相关的代码）。建议顺序：**6.15 → 6.16 → 6.17**（P0），**6.18 → 6.19**（P1，可并行）。

**Batch 10 实现项进度（勾选 = 已满足 AC 与验证）**

- [x] Task **6.16** — `verify constraints` skip-registry 仅校验当前 `wi_id` 行（FR-095 / SC-020）
- [x] Task **6.17** — `close-check` docs 默认 WI+白名单，`--all-docs` 全量（FR-096 / SC-021）
- [x] Task **6.18** — 归档「提交哈希」策略降噪（FR-097 / SC-022）
- [x] Task **6.19** — `close-check` 命令列表从 Typer 枚举（FR-098 / SC-023）

### Task 6.15 — 规格与登记：FR-095～098、SC-020～023 + `wi_id` 列（仅文档）

- **依赖**：Task 6.14（已实现初版 skip-registry 映射，本任务对其 **收窄策略** 定契约）。
- **产物**：
  1. [`spec.md`](spec.md) 已含 **FR-095～FR-098**、**SC-020～023**（若批次外有修订，本任务负责审阅一致）。
  2. [`plan.md`](plan.md) 已含「规则作用域收敛与工程纪律」设计节（本任务负责与 spec 术语对齐）。
  3. [`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../../src/ai_sdlc/rules/agent-skip-registry.zh.md)：登记表表头含 **`wi_id`**；**工程纪律复盘**节与 SDLC 映射可追溯至本 Batch。
  4. （可选）[`templates/execution-log-template.md`](../../templates/execution-log-template.md) 与 [`src/ai_sdlc/rules/batch-protocol.md`](../../src/ai_sdlc/rules/batch-protocol.md)：为 **FR-097** 预留表述修订点（具体改文可在 Task 6.18 执行）。
- **验收标准（AC）**：
  1. `spec` / `plan` / `tasks`（本 Batch）三处对「wi_id 过滤」「默认 WI+白名单 docs」「单 commit / 哈希可选」「Typer 枚举命令」表述一致、无内部矛盾。
  2. 登记表 **新行**示例已含 **`wi_id=001-ai-sdlc-framework`**（元纪律记录）；历史行 `wi_id` 可为空且文档说明其行为（不参与 FR-095 自动 BLOCKER）。
  3. 明确 **FR-094** 与 **FR-095** 关系：095 为 094 的 **作用域收窄**，不删除 094 的「产品化闭环」目标。
- **验证**：人工审阅；必要时 markdown 表格列对齐检查。
- **关联 FR / SC**：FR-095～FR-098，SC-020～023（文档层）。

> **Task 6.15 收口说明（2026-03-27）**：本任务未单列独立 implementation batch；其文档契约已分别落盘于 [`spec.md`](spec.md) 的 **FR-095～098 / SC-020～023**、[`plan.md`](plan.md) 的「规则作用域收敛与工程纪律」设计节，以及 [`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../../src/ai_sdlc/rules/agent-skip-registry.zh.md) 的 **`wi_id`** 表头与「工程纪律复盘」条目。以这些产物为真值，可视为 Batch 10 实施前置条件已满足；后续实现收口见下方 Task **6.16～6.19** 与 [`task-execution-log.md`](task-execution-log.md) **Batch 2026-03-25-012**。

### Task 6.16 — 实现：`verify constraints` skip-registry **仅校验当前 wi_id 行**（FR-095 / SC-020）

- **依赖**：Task **6.15**。
- **输入**：[`src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)。
- **验收标准（AC）**：
  1. 解析登记表时仅对 **`wi_id` 与当前 checkpoint 工作项匹配** 的数据行提取 `FR-xxx` / `Task x.y` 并做 spec/tasks 映射；**不匹配或无 wi_id 的行**不触发该项 BLOCKER。
  2. pytest：**混合夹具**（多行历史 + 一行当前 WI 未映射）仅因当前行失败（**SC-020**）；**仅历史行未映射**时通过。
  3. `uv run ruff check src tests` 通过。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-095，SC-020。

### Task 6.17 — 实现：`close-check` docs 默认 **WI+白名单**，`--all-docs` 全量（FR-096 / SC-021）

- **依赖**：Task **6.15**；Task 6.12（已有 `close-check`）。
- **输入**：[`src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`src/ai_sdlc/cli/workitem_cmd.py`](../../src/ai_sdlc/cli/workitem_cmd.py)、[`tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)。
- **验收标准（AC）**：
  1. 默认仅扫描 `specs/<WI>/` 下 `*.md` 与 **白名单**（至少含 `docs/pull-request-checklist.zh.md`、`docs/USER_GUIDE.zh-CN.md`；路径以 `--wi` 解析结果为锚）。
  2. 新增 `--all-docs`：启用当前实现中的 **全 `docs/**` 扫描**行为（或等价命名，须在 `--help` 说明）。
  3. pytest 覆盖 **SC-021**（默认跳过深层违规、加开关后失败）；`ruff` 通过。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-096，SC-021。

### Task 6.18 — 文档与模板：归档「提交哈希」策略降噪（FR-097 / SC-022）

- **依赖**：Task **6.15**。
- **产物**：[`templates/execution-log-template.md`](../../templates/execution-log-template.md)、[`src/ai_sdlc/rules/batch-protocol.md`](../../src/ai_sdlc/rules/batch-protocol.md)（及必要时 [`spec.md`](spec.md) 一句交叉引用）。
- **验收标准（AC）**：
  1. 模板与 `batch-protocol` 对 **「提交哈希是否必填 / 是否允许单次 commit 含归档」** 表述一致（**SC-022**）。
  2. 选定策略写清：**推荐单次 commit** 或 **批次末一次回填** 二选一，不在同一文档混用两种默认说法。
- **验证**：人工审阅；全量 `pytest` + `ruff` 作为回归（文档变更仍跑门函数）。
- **关联 FR / SC**：FR-097，SC-022。

### Task 6.19 — 实现：`close-check` 命令列表从 Typer 枚举（FR-098 / SC-023）

- **依赖**：Task **6.15**；Task 6.17（可与 6.17 同 PR 若强耦合，须注明）。
- **输入**：[`src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py) 或经批准的单一注册入口；[`src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)。
- **验收标准（AC）**：
  1. `REGISTERED_COMMANDS` 硬编码移除或降级为 **仅测试夹具**；运行时使用 **Typer 遍历**得到 `ai-sdlc …` 全名集合。
  2. pytest：**SC-023**——模拟新增子命令后 docs 检查能识别（或文档豁免规则与代码一致且单测锁定）。
  3. `ruff` 通过。
- **验证**：`uv run pytest`；`uv run ruff check src tests`。
- **关联 FR / SC**：FR-098，SC-023。

> **Batch 10 实现收口（2026-03-25）**：Task **6.16～6.19** 已完成（FR-095～098 / SC-020～SC-023）。验证命令、审查摘要与归档见 [`task-execution-log.md`](task-execution-log.md) 中 **Batch 2026-03-25-012**；**`uv run pytest`：543 passed**；**`uv run ruff check src tests`：通过**；主提交 `3eafdf871cd11485882a5b47127402129d876e78`；本段为 `tasks.md` 收口指针（与上表 **Batch 10 实现项进度** 勾选一致）。

---

## Batch 11（P1 remediation 第一批）：001 spec 核心闭环修复

> **工程约束**：先以 [`implementation-drift-matrix.md`](implementation-drift-matrix.md) 冻结偏差真值，再进入代码修复。每个 Task 必须先补 contract-level 测试，再写实现；本批收口必须同时回填 drift matrix、traceability 与 backlog。

### Task 6.20 — 001 spec 全量偏差总表与 remediation 批次冻结（仅文档）

- **依赖**：无。
- **产物**：
  1. [`implementation-drift-matrix.md`](implementation-drift-matrix.md)：登记当前全部合同级偏差、证据文件、修复批次、状态。
  2. [`plan.md`](plan.md)：新增 remediation 设计节，写明 Batch 11 / 12 的范围与验证协议。
  3. [`tasks.md`](tasks.md)：新增 remediation Batch 与 AC。
- **验收标准（AC）**：
  1. drift matrix 仅登记相对 `spec.md` 仍存在的偏差，未列 FR 默认视为当前已对齐。
  2. Batch 11 范围严格限定为：`FR-020~023`、`FR-034`、`FR-040~045`、`FR-052/054`、`FR-081`（recover CLI 合同随 `FR-052/054` 一并修复）。
  3. Batch 12 明确承接剩余接口形态漂移、文档/计划回填与 close-check 对账。
- **验证**：人工审阅；链接与批次编号一致。

> **Task 6.20 收口说明（2026-03-27）**：本任务产物已落盘于 [`implementation-drift-matrix.md`](implementation-drift-matrix.md)、[`plan.md`](plan.md) remediation 设计节与本文件 Batch 11 / 12；后续代码修复与状态回填均以这些文档为真值。

### Task 6.21 — 修复 Governance Freeze 合同（FR-020~023）

- **依赖**：Task 6.20。
- **输入**：[`src/ai_sdlc/gates/governance_guard.py`](../../src/ai_sdlc/gates/governance_guard.py)、相关 models / store、[`tests/unit/test_governance_guard.py`](../../tests/unit/test_governance_guard.py)。
- **验收标准（AC）**：
  1. 提供与 spec 对齐的 `GovernanceGuard.check()` / `freeze()`（命名可通过兼容层过渡，但对外合同必须成立）。
  2. 6 项检查项对齐 `tech_profile / constitution / clarify / quality_policy / branch_policy / parallel_policy`；缺项时列出全部缺失项。
  3. `freeze()` 成功写入 `governance.yaml`，至少包含 `frozen=true`、`frozen_at` 与 6 项检查结果。
  4. contract-level 测试覆盖：全通过写盘、单项缺失失败、未冻结时阻断后续依赖路径。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-020~023，SC-005。

### Task 6.22 — 修复 dev 分支 docs 写保护硬拦截（FR-034）

- **依赖**：Task 6.20。
- **输入**：[`src/ai_sdlc/branch/file_guard.py`](../../src/ai_sdlc/branch/file_guard.py)、[`src/ai_sdlc/branch/branch_manager.py`](../../src/ai_sdlc/branch/branch_manager.py)、相关写文件入口与测试。
- **验收标准（AC）**：
  1. `spec.md` / `plan.md` 的保护不再只是内存标记，必须接入统一写文件路径或等价的真实拦截层。
  2. 在 dev 分支尝试写入受保护文档时，实际写操作被拒绝并保留可辨识错误。
  3. 不破坏 docs 分支正常编辑与非受保护文件写入。
  4. contract-level 测试覆盖真实写入正反路径。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-034，SC-006（延伸到 docs 保护）。

### Task 6.23 — 修复 execute 主闭环与批次收口（FR-040~045）

- **依赖**：Task 6.20。
- **输入**：[`src/ai_sdlc/core/executor.py`](../../src/ai_sdlc/core/executor.py)、[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py)、[`src/ai_sdlc/cli/run_cmd.py`](../../src/ai_sdlc/cli/run_cmd.py)、[`tests/unit/test_executor.py`](../../tests/unit/test_executor.py)、[`tests/flow/test_execution_flow.py`](../../tests/flow/test_execution_flow.py)。
- **验收标准（AC）**：
  1. 存在对外 `Executor.run(tasks_file)` 或等价执行入口，真正按 `tasks.md` / 批次驱动执行，而不是只跑 gate。
  2. 批次完成后写入 `task-execution-log.md`、执行 `git commit`，并把日志时间与 commit 顺序纳入 gate / 测试约束。
  3. 调试轮数上限与连续 HALT 熔断仍生效，且由主闭环真实驱动。
  4. CLOSE 前生成 `development-summary.md`。
  5. contract-level 测试覆盖：正常批次执行、单任务超限 HALT、连续 HALT 熔断、收尾 summary 生成。
- **验证**：定向 pytest + flow tests + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-040~045，SC-010。

### Task 6.24 — 修复 resume-pack load / checkpoint 校验 / recover 合同（FR-052, FR-054）

- **依赖**：Task 6.20。
- **输入**：[`src/ai_sdlc/context/state.py`](../../src/ai_sdlc/context/state.py)、[`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`tests/unit/test_context_state.py`](../../tests/unit/test_context_state.py)、[`tests/integration/test_cli_recover.py`](../../tests/integration/test_cli_recover.py)。
- **验收标准（AC）**：
  1. 提供 `load_resume_pack()` 或等价恢复入口，语义与 spec 对齐，不再仅靠 `build_resume_pack()` 重建。
  2. 缺失 `resume-pack.yaml`、损坏 `resume-pack.yaml`、非法 `checkpoint.yml` 时返回 spec 级错误语义。
  3. `checkpoint.yml` 加载至少校验 YAML 语法、`current_stage` 合法性、`spec_dir` 存在性。
  4. `recover` CLI 以加载恢复包为主路径；reconcile 只能作为兼容扩展，不得替代主合同。
  5. contract-level 测试覆盖：正常加载、无恢复包、损坏恢复包、非法 checkpoint、legacy reconcile 兼容。
- **验证**：定向 pytest + 集成 recover tests + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-052，FR-054，SC-007。

### Task 6.25 — 修复 `work-item.yaml` 状态持久化（FR-081）

- **依赖**：Task 6.20。
- **输入**：[`src/ai_sdlc/core/state_machine.py`](../../src/ai_sdlc/core/state_machine.py)、相关 work item store / template / CLI 路径、[`tests/unit/test_state_machine.py`](../../tests/unit/test_state_machine.py)。
- **验收标准（AC）**：
  1. 状态转换不再停留在纯内存返回值，必须把新状态写入 `work-item.yaml.status`。
  2. 非法转换时不得落盘；合法转换时内存态与磁盘态一致。
  3. 至少 1 条跨阶段转换链在文件系统夹具中证明 `created -> ... -> completed` 的状态持久化行为。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-081，SC-009（状态持久化子合同）。

### Task 6.26 — Batch 11 收口：contract-level 回归、traceability 与 backlog 回填

- **依赖**：Task 6.21 ~ 6.25。
- **产物**：
  1. Batch 11 对应的定向 contract-level 测试记录。
  2. [`implementation-drift-matrix.md`](implementation-drift-matrix.md) 状态回填。
  3. [`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 与 traceability 对账更新。
- **验收标准（AC）**：
  1. Batch 11 覆盖的 FR 在 drift matrix 中不再为 `open`；若仍有余项，必须显式改成 `partial` 并写清残留。
  2. backlog 条目与实际修复结果一致，不允许只改代码不改台账。
  3. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：定向 contract tests + 全量 `pytest` + `ruff`。

> **Batch 11 实现收口（2026-03-28）**：Task **6.21～6.26** 已完成。核心闭环修复包括：`GovernanceGuard.check()/freeze()` + `governance.yaml`、dev 分支受保护文档真实写拦截（统一裸写入口硬拦截已于下方 Batch 12 收口块补齐）、`Executor.run()` 批次执行/日志/commit/summary、`load_resume_pack()` + strict checkpoint 校验 + recover 主路径、`work-item.yaml` 状态持久化。定向 contract suite **217 passed**；全量 **`uv run pytest -q`：707 passed**；**`uv run ruff check src tests`：通过**。本批 traceability 回填见 [`implementation-drift-matrix.md`](implementation-drift-matrix.md)，backlog 回填见 [`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 中 **FD-2026-03-27-014**。

## Batch 12（P1 remediation 第二批）：剩余接口漂移与文档对账清理

> **工程约束**：仅在 Batch 11 收口完成后启动。本批重点是“把剩余偏差收干净”，包含接口形态漂移、门禁语义缩减、文档/计划回填与 close-check 对账。

### Task 6.27 — 修复 PRD Studio 接口与结构化摘要合同（FR-010~012）

- **依赖**：Task 6.26。
- **验收标准（AC）**：
  1. PRD Studio 对外合同与 `spec.md` 对齐，必要时通过兼容层同时保留旧入口。
  2. PRD 通过就绪检查后，输出结构化摘要（JSON/YAML 或等价 canonical object），至少包含项目名、目标、角色、功能、验收标准。
  3. contract-level 测试覆盖 path-based 与 content-based 输入、通过/失败两类结果。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-010~012，SC-004。

### Task 6.28 — 修复 docs 分支命名与 baseline recheck 合同（FR-030, FR-033）

- **依赖**：Task 6.26。
- **验收标准（AC）**：
  1. docs 分支命名与 spec 对齐；若选择兼容旧分支名，必须有显式迁移与兼容策略。
  2. baseline recheck 至少覆盖 `spec.md`、`plan.md`、`tasks.md` 等 docs baseline 核心产物。
  3. 分支相关单元 / flow 测试覆盖命名、切换、baseline 失败阻断。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-030，FR-033，SC-006。

### Task 6.29 — 修复 INIT / REFINE / EXECUTE Gate 合同缩减（FR-061~063）

- **依赖**：Task 6.26。
- **验收标准（AC）**：
  1. INIT Gate 对齐 constitution / tech-stack / decisions / principles / source attribution 等 spec 合同。
  2. REFINE Gate 校验每个用户故事具备验收场景。
  3. EXECUTE Gate 不只依赖调用方布尔值，能够证明测试、构建、归档、commit 等执行前提。
  4. contract-level 测试锁定 PASS / RETRY / HALT 语义。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-061~063。

### Task 6.30 — 修复 `index` / `gate` CLI 形态与索引重建合同（FR-073, FR-074）

- **依赖**：Task 6.26。
- **验收标准（AC）**：
  1. `ai-sdlc index` 能重建 spec 所需的自动索引集合，至少覆盖 `repo-facts.json`、`key-files.json`。
  2. `ai-sdlc gate <stage>` 的对外合同与文档对齐；若内部继续保留 `check` 子命令，必须通过兼容 alias 满足 spec 形态。
  3. 集成测试覆盖 CLI 对外形态与索引产物。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-073，FR-074，FR-083。

### Task 6.31 — Batch 12 收口：文档/计划回填、close-check 对账、最终 traceability 更新

- **依赖**：Task 6.27 ~ 6.30。
- **验收标准（AC）**：
  1. [`implementation-drift-matrix.md`](implementation-drift-matrix.md) 中全部偏差状态已回填为 `closed` 或显式 `deferred`。
  2. `plan.md` / `tasks.md` / backlog / close-check 规则文本与实际实现一致。
  3. `close-check` 能在夹具上证明“实现已变更但文档未回填”会失败。
  4. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：定向 close-check / traceability tests + 全量 `pytest` + `ruff`。

> **Batch 12 实现收口（2026-03-28）**：Task **6.27～6.31** 已完成，并补齐了 Task **6.22** 遗留的 `FR-034` 统一写拦截缺口。PRD Studio 结构化摘要、docs branch/baseline、INIT / REFINE / EXECUTE Gate、`index` / `gate` CLI 形态、drift matrix / backlog / close-check 对账均已落盘；`FileGuard` 现统一拦截 `Path.write_text()` / `Path.write_bytes()` / `open(..., write mode)` / `Path.replace()` / `Path.rename()` 对受保护 `spec.md` / `plan.md` 的写入。定向 contract suite **111 passed**；全量 **`uv run pytest -q`：721 passed**；**`uv run ruff check src tests`：通过**；**`uv run ai-sdlc verify constraints`：无 BLOCKER**；**`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`** 与 **`--all-docs`**：全部 PASS。至此 [`implementation-drift-matrix.md`](implementation-drift-matrix.md) 中 `001` remediation 项全部为 `closed`，[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 中 **FD-2026-03-27-014** 已收口。

## Batch 13（P0 gap backfill 第一批）：RG-001 ~ RG-006 主链真值硬化

> **目标**：把 2026-03-28 新补入 `spec.md` 的 intake / governance / branch protocol 合同落成可执行 backlog，优先修补会影响主闭环真值的一阶缺口。
>
> **当前状态（2026-03-28 收口）**：Task **6.32～6.36** 已完成；主线代码、回归结果与 execution-log 证据见下方收口块及 [`task-execution-log.md`](task-execution-log.md) Batch **2026-03-28-019**。

### Task 6.32 — 修补 intake 原子分配与推荐流输出（RG-001, RG-002）

- **依赖**：Task 6.31。
- **输入**：[`src/ai_sdlc/routers/work_intake.py`](../../src/ai_sdlc/routers/work_intake.py)、[`src/ai_sdlc/models/work.py`](../../src/ai_sdlc/models/work.py)、[`tests/unit/test_work_intake_router.py`](../../tests/unit/test_work_intake_router.py)、[`tests/flow/test_new_requirement_flow.py`](../../tests/flow/test_new_requirement_flow.py)。
- **验收标准（AC）**：
  1. 正式 intake 路径在一次框架调用中完成 `work_item_id` 分配、`next_work_item_seq` 自增落盘与 `WorkItem` 持久化更新。
  2. `recommended_flow`、`severity`、`needs_human_confirmation` 的输出与 spec 新口径对齐，不再依赖调用方补写。
  3. 低置信度处理适用于所有类型，而不只 `uncertain`。
  4. flow / unit tests 覆盖成功路径、失败回滚路径与低置信度路径。
- **验证**：`uv run pytest tests/unit/test_work_intake_router.py tests/flow/test_new_requirement_flow.py -v` + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-006~009（其中 intake 输出部分），SC-024，SC-025。

### Task 6.33 — 修补 uncertain 澄清轮次、HALT 原因与可恢复记录（RG-003）

- **依赖**：Task 6.32。
- **输入**：[`src/ai_sdlc/routers/work_intake.py`](../../src/ai_sdlc/routers/work_intake.py)、[`src/ai_sdlc/models/work.py`](../../src/ai_sdlc/models/work.py)、[`tests/unit/test_work_intake_router.py`](../../tests/unit/test_work_intake_router.py)。
- **验收标准（AC）**：
  1. `ClarificationState` 至少持久化 `round_count`、候选类型、用户回应与 HALT 原因。
  2. 连续两轮澄清后仍不确定时，第三次决策进入 HALT，并留下可被 `recover` / `status` 读取的原因记录。
  3. 重新分类成功时，clarification 状态与 work item 主状态同步收口。
- **验证**：定向 pytest + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-009，SC-025。

### Task 6.34 — 修补 governance freeze 对 docs baseline 入口的硬阻断与冻结输入保护（RG-004, RG-005）

- **依赖**：Task 6.31。
- **输入**：[`src/ai_sdlc/gates/governance_guard.py`](../../src/ai_sdlc/gates/governance_guard.py)、[`src/ai_sdlc/branch/branch_manager.py`](../../src/ai_sdlc/branch/branch_manager.py)、[`tests/unit/test_governance_guard.py`](../../tests/unit/test_governance_guard.py)、[`tests/unit/test_branch_manager.py`](../../tests/unit/test_branch_manager.py)、[`tests/flow/test_docs_dev_flow.py`](../../tests/flow/test_docs_dev_flow.py)。
- **验收标准（AC）**：
  1. docs branch 创建与 docs baseline stage 在 governance 未冻结时统一阻断。
  2. `constitution`、`clarify/decisions`、治理 policy 等冻结输入存在显式保护，不允许静默覆盖。
  3. governance 冻结结果可被 branch/status/recover surface 读取，而不是只在会话上下文中判断。
- **验证**：定向 pytest + flow tests + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-024~026，SC-026。

### Task 6.35 — 修补 docs/dev 切换后的 runtime / resume / status 绑定协议（RG-006）

- **依赖**：Task 6.34。
- **输入**：[`src/ai_sdlc/branch/branch_manager.py`](../../src/ai_sdlc/branch/branch_manager.py)、[`src/ai_sdlc/context/state.py`](../../src/ai_sdlc/context/state.py)、[`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`tests/unit/test_context_state.py`](../../tests/unit/test_context_state.py)、[`tests/integration/test_cli_status.py`](../../tests/integration/test_cli_status.py)、[`tests/integration/test_cli_recover.py`](../../tests/integration/test_cli_recover.py)。
- **验收标准（AC）**：
  1. docs -> dev 切换前，checkpoint 至少记录当前分支、spec dir、最近 docs baseline 引用与时间戳。
  2. 切换成功后，runtime / resume / progress / working-set 全部刷新，不再遗留旧分支信息。
  3. baseline recheck 失败时，切换整体失败，不留下半更新状态。
  4. `status` / `recover` 能看到当前 branch 与 docs baseline 的绑定关系。
- **验证**：定向 pytest + integration status/recover + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-035~039，SC-027。

### Task 6.36 — Batch 13 收口：主链回归、traceability 与 backlog 回填

- **依赖**：Task 6.32 ~ 6.35。
- **验收标准（AC）**：
  1. RG-001 ~ RG-006 在 `spec.md`、本文件与实现之间存在可追踪映射。
  2. 关键 flow / integration 回归覆盖 intake、governance、branch switch、status / recover。
  3. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：定向 tests + 全量 `pytest` + `ruff`。

> **Batch 13 实现收口（2026-03-28）**：Task **6.32～6.36** 已完成。`KeywordWorkIntakeRouter` 现已提供正式 `intake()` 路径，在一次框架调用中完成 `work_item_id` 分配、`next_work_item_seq` 落盘、自增回滚保护，以及 `recommended_flow` / `severity` / 低置信度 `needs_human_confirmation` 的统一输出；`ClarificationState` 新增候选类型与 `halt_reason`，连续两轮澄清后第三次决策才进入 HALT，并保持 work item 主状态同步收口。`BranchManager` 会从磁盘读取 `governance.yaml`，在 governance 未冻结时统一阻断 docs/dev 入口，并对冻结输入启用显式文件保护；docs -> dev 切换现已在 baseline recheck 失败时回滚 checkout，不再留下半更新状态，同时刷新 checkpoint / resume-pack 中的 `current_branch`、`docs_baseline_ref`、`docs_baseline_at`。`status` / `recover` surface 也已直接展示 branch、docs baseline 与 governance frozen 绑定。Batch 13 定向回归 **87 passed**；全量 **`uv run pytest -q`：742 passed**；**`uv run ruff check src tests`：通过**。对应归档见 [`task-execution-log.md`](task-execution-log.md) Batch **2026-03-28-019**。

## Batch 14（P0 gap backfill 第二批）：RG-007 ~ RG-009 artifact / gate surface 收口

> **目标**：把 planning/context artifact 与显式 gate taxonomy 从“隐含存在”提升为正式真值面，并让 verify/close surface 能稳定消费。
>
> **当前状态（2026-03-28 收口）**：Task **6.37～6.39** 已完成；主线代码、回归结果与 execution-log 证据见下方收口块及 [`task-execution-log.md`](task-execution-log.md) Batch **2026-03-28-020**。

### Task 6.37 — 建立 planning / context artifact 正式真值面（RG-007, RG-008）

- **依赖**：Task 6.36。
- **输入**：[`src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py)、[`src/ai_sdlc/core/executor.py`](../../src/ai_sdlc/core/executor.py)、[`src/ai_sdlc/context/state.py`](../../src/ai_sdlc/context/state.py)、[`src/ai_sdlc/models/state.py`](../../src/ai_sdlc/models/state.py)、[`tests/unit/test_executor.py`](../../tests/unit/test_executor.py)、[`tests/flow/test_execution_flow.py`](../../tests/flow/test_execution_flow.py)、[`tests/flow/test_recover_flow.py`](../../tests/flow/test_recover_flow.py)。
- **验收标准（AC）**：
  1. `task graph`、`execution-plan`、`runtime`、`working-set`、`latest-summary` 中至少各有一个正式真值面，并可被 `recover` / `status` 消费。
  2. active work item 的 artifact 写入与更新时机在 runner / executor 主链中锁定。
  3. recover 加载遵循 `summary-first`、`working-set-first` 的新合同，且测试证明可恢复。
- **验证**：定向 pytest + flow tests + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-046~049，SC-028。

### Task 6.38 — 显式化 PRD / Review / Done / Verification Gate surface（RG-009）

- **依赖**：Task 6.37。
- **输入**：[`src/ai_sdlc/gates/pipeline_gates.py`](../../src/ai_sdlc/gates/pipeline_gates.py)、[`src/ai_sdlc/gates/registry.py`](../../src/ai_sdlc/gates/registry.py)、[`src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`tests/unit/test_gates.py`](../../tests/unit/test_gates.py)、[`tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)。
- **验收标准（AC）**：
  1. PRD Gate、Review Gate、Done Gate、Verification Gate 在文档与实现层都可被明确引用。
  2. Done Gate 对“需 Knowledge Refresh 但未完成”的 completed 转换具备正式阻断语义。
  3. Verification Gate 与 CLI / runner surface 的检查对象清单对齐。
- **验证**：定向 pytest + integration verify + 全量 `pytest` + `ruff`。
- **关联 FR / SC**：FR-064~067，SC-029。

### Task 6.39 — Batch 14 收口：最终对账与里程碑回填

- **依赖**：Task 6.37 ~ 6.38。
- **验收标准（AC）**：
  1. RG-007 ~ RG-009 已在 `plan.md` / `tasks.md` / 相关 traceability 文档中显式回填。
  2. `verify constraints` / `close-check` 的夹具可以区分“artifact 缺失 / gate surface 缺失 / 真值面完整”三种状态。
  3. 全量 `uv run pytest` 与 `uv run ruff check src tests` 通过。
- **验证**：定向 contract tests + 全量 `pytest` + `ruff`。

> **Batch 14 实现收口（2026-03-28）**：Task **6.37～6.39** 已完成。`Executor` 现会在 active work item 目录持续写入 `execution-plan.yaml`、`runtime.yaml`、`working-set.yaml` 与 `latest-summary.md`；`build_resume_pack()` 已按 `summary-first` / `working-set-first` 读取这些真值面，`status` 也会直接显示 execution plan / runtime updated / latest summary。与此同时，`pipeline_gates`、`registry`、gate CLI、runner、`verify constraints` 与 `close-check` 已显式公开 `PRD Gate`、`Review Gate`、`Done Gate`、`Verification Gate` surface；`DoneGate` 对 `knowledge_refresh_level > 0 && knowledge_refresh_completed = false` 具备正式阻断语义，`verify constraints --json` 会声明 Verification Gate 的 check objects，`workitem close-check` 会输出 `review_gate` / `done_gate`。Batch 14 定向 contract suite **111 passed**；**`uv run ai-sdlc verify constraints`：无 BLOCKER**；**`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`** 与 **`--all-docs`**：全部 PASS；全量 **`uv run pytest -q`：742 passed**；**`uv run ruff check src tests`：通过**。对应归档见 [`task-execution-log.md`](task-execution-log.md) Batch **2026-03-28-020**。

## Batch 15（P0 backlog remediation 第一波）：legacy reconcile / recover 兼容收口

> **目标**：优先收口最直接阻断继续执行的 `001` backlog 项：`FD-2026-03-26-002`。本批只把 backlog 重新挂回 `001` 主线，不再新开混合 spec。

### Task 6.40 — 兼容旧产物布局的 checkpoint reconcile / recover backfill 主路径（FD-2026-03-26-002）

- **依赖**：Task 6.39。
- **输入**：[`docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md`](../../docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md)、[`src/ai_sdlc/core/reconcile.py`](../../src/ai_sdlc/core/reconcile.py)、[`src/ai_sdlc/context/state.py`](../../src/ai_sdlc/context/state.py)、[`src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py)、[`tests/unit/test_reconcile.py`](../../tests/unit/test_reconcile.py)、[`tests/unit/test_context_state.py`](../../tests/unit/test_context_state.py)、[`tests/integration/test_cli_status.py`](../../tests/integration/test_cli_status.py)、[`tests/integration/test_cli_recover.py`](../../tests/integration/test_cli_recover.py)、[`tests/integration/test_cli_run.py`](../../tests/integration/test_cli_run.py)、[`tests/integration/test_cli_stage.py`](../../tests/integration/test_cli_stage.py)。
- **验收标准（AC）**：
  1. 给定“旧版根目录产物 + 空白/过时 checkpoint”的夹具时，系统能识别真实 work item / stage，或给出唯一正式 reconcile 入口，而不是长期停留在 `init/unknown`。
  2. `status`、`recover`、`run --dry-run`、`stage run` 复用同一套 reconcile/backfill 真值，不再各自漂移。
  3. 当输入状态不足以安全推断阶段时，CLI 输出明确阻断与下一步提示，而不是静默回落到 `init/unknown`。
- **验证**：定向 unit + integration 回归；必要时补 `workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 只读复核。

> **Task 6.40 进展（2026-03-28）**：第一轮实现与回归已完成。blank checkpoint 下 `status` 不再先报 `Invalid checkpoint`，而是直接给出 reconcile guidance；`recover` 在 stale `init/unknown` checkpoint 且未执行 `--reconcile` 时会停止而不是继续按旧状态恢复；`specs/<WI>/` 旧布局与无 checkpoint 探测已进入自动化回归。Task **6.41** 随后已完成 execution-log / backlog / close-check 对账，并补上旧 `project-state.yaml` 残留回归，**FD-2026-03-26-002** 已在 Batch 15 收口。

### Task 6.41 — Batch 15 收口：001 第一波 backlog 对账

- **依赖**：Task 6.40。
- **验收标准（AC）**：
  1. `FD-2026-03-26-002` 的 backlog、`tasks.md` 与 execution-log 指向同一收口事实。
  2. `verify constraints` 与 `workitem close-check --wi specs/001-ai-sdlc-framework --all-docs` 在兼容夹具落地后保持可用。
  3. 后续若继续推进第二波 backlog，本批不会留下新的 checkpoint / recover 真值分叉。
- **验证**：定向 integration + `verify constraints` + `close-check --all-docs`。

> **Task 6.41 完成（2026-03-28）**：已补旧 `project-state.yaml` 残留字段的 reconcile regression，并完成 execution-log / backlog / `close-check --all-docs` / `verify constraints` 对账；Batch 15 真值已统一，`FD-2026-03-26-002` 已关闭。

## Batch 16（P1 backlog remediation 第二波）：Git 写 guardrail / 完成前验证 / 文档优先执行约束

> **目标**：收口第二波 backlog：`FD-2026-03-28-004`、`FD-2026-03-24-003`、`FD-2026-03-26-001`。其中后两项来自 migrated 条目，但现状仅属部分覆盖，继续按 `001` 主线任务推进。

### Task 6.42 — Git 写命令互斥 guardrail 与 stale-lock 判断（FD-2026-03-28-004）

- **依赖**：Task 6.41。
- **输入**：[`src/ai_sdlc/branch/git_client.py`](../../src/ai_sdlc/branch/git_client.py)、[`src/ai_sdlc/rules/multi-agent.md`](../../src/ai_sdlc/rules/multi-agent.md)、[`src/ai_sdlc/rules/batch-protocol.md`](../../src/ai_sdlc/rules/batch-protocol.md)、[`docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)。
- **验收标准（AC）**：
  1. 同一仓库内的 `git add`、`git commit`、`git merge`、`git checkout`、`git branch -d/-D`、`git worktree remove` 等写命令被统一分类为互斥临界区，不得并行发起。
  2. 遇到 `.git/index.lock` 时，流程先区分“活跃 Git 进程持锁”与“可清理 stale lock”，禁止把删锁当成默认恢复动作。
  3. 收口顺序在规则和 helper 中统一为 `git add -> git status/diff -> git commit -> git push`，不再允许并行工具打包这些步骤。
- **验证**：规则/流程回归 + 只读文档校验；如实现命令封装，补对应单测。

### Task 6.43 — fresh verification evidence 协议覆盖文档 / 规则变更（FD-2026-03-24-003）

- **依赖**：Task 6.42。
- **输入**：[`src/ai_sdlc/rules/verification.md`](../../src/ai_sdlc/rules/verification.md)、[`docs/pull-request-checklist.zh.md`](../../docs/pull-request-checklist.zh.md)、[`src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)、[`tests/integration/test_cli_verify_constraints.py`](../../tests/integration/test_cli_verify_constraints.py)。
- **验收标准（AC）**：
  1. 文档/规则类变更拥有明确的最小 fresh verification 集合，不再依赖“这是 docs 改动所以可以口头完成”的隐含例外。
  2. `close-check` / `verify constraints` 能区分“缺少新鲜验证证据的完成声明”与“符合 docs-only 协议的收口”。
  3. execution-log / checklist 能记录 docs-only 的 fresh evidence，而不伪装成完整代码回归。
- **验证**：定向 close-check / verify 集成测试 + 只读文档校验。

### Task 6.44 — “先落需求 / 先文档”指令的 design/decompose 前置判定（FD-2026-03-26-001）

- **依赖**：Task 6.43。
- **输入**：[`src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)、[`src/ai_sdlc/rules/agent-skip-registry.zh.md`](../../src/ai_sdlc/rules/agent-skip-registry.zh.md)、[`src/ai_sdlc/gates/task_ac_checks.py`](../../src/ai_sdlc/gates/task_ac_checks.py)、[`src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)。
- **验收标准（AC）**：
  1. 当用户明确要求“先文档 / 先需求 / 先 spec-plan-tasks”时，默认动作必须收敛到 design/decompose，而不是进入 execute。
  2. 执行前判定能够识别“仅文档 / 仅需求沉淀”任务，并阻断对 `src/`、`tests/` 的默认改动冲动。
  3. 规则文本、任务清单与验证提示使用统一术语，不再一边要求先落盘、一边鼓励直接编码。
- **验证**：规则/门禁回归 + `verify constraints` 只读校验。

### Task 6.45 — Batch 16 收口：001 第二波 backlog 对账

- **依赖**：Task 6.42 ~ 6.44。
- **验收标准（AC）**：
  1. `FD-2026-03-28-004`、`FD-2026-03-24-003`、`FD-2026-03-26-001` 在 backlog、`tasks.md` 与后续 execution-log 中保持单一真值。
  2. `verify constraints`、`workitem close-check --wi specs/001-ai-sdlc-framework` 与 `--all-docs` 仍能作为第二波收口证据。
  3. 若其中任一项仍只完成部分覆盖，收口块必须显式写明残留，不得重新回到“migrated/已完成”的模糊状态。
- **验证**：定向 docs/rules/close-check 回归 + `verify constraints` + `close-check --all-docs`。

---

## 任务统计

| Batch | Phase | 任务数 | 可并行 |
|-------|-------|--------|--------|
| 1 | 0-1 | 10 | Task 1.4/1.5/1.6/1.8 可并行 |
| 2 | 2 | 3 | Task 2.1/2.2 可并行 |
| 3 | 3-4 | 6 | Task 3.1~3.3 与 Task 3.4~3.6 可并行 |
| 4 | 5-8 | 12 | Task 4.11/4.12 可并行 |
| 5 | 9-10 | 9 | Task 5.1~5.5 可并行 |
| 6 | 增量 | 2 | Task 6.1 与 6.2；可与 1–5 并行 |
| 7 | P1 实现 | 4 | 6.3∥6.4 可并行；6.5 建议在后 |
| 8 | P1 分解门禁 | 4 | 6.7 文档先行；6.8→6.9；6.10 共用校验收口已于 2026-03-25 确认（见 Task 6.10 收口块） |
| 9 | P1 收口硬化 | 4 | 6.11 文档先行；6.12→6.13；6.14 可并行 |
| 10 | P1 规则收敛 | 5 | 6.15 文档先行；6.16→6.17；6.18∥6.19 |
| 11 | P1 remediation 第一批 | 7 | 6.20 文档先行；6.21∥6.22 可并行；6.23/6.24/6.25 视写入层耦合顺序推进；6.26 收口 |
| 12 | P1 remediation 第二批 | 5 | 6.27∥6.28 可并行；6.29→6.30；6.31 最终对账 |
| 13 | P0 gap backfill 第一批 | 5 | 6.32→6.33；6.34∥6.35；6.36 收口 |
| 14 | P0 gap backfill 第二批 | 3 | 6.37→6.38；6.39 最终对账 |
| 15 | P0 backlog remediation 第一波 | 2 | 6.40→6.41 |
| 16 | P1 backlog remediation 第二波 | 4 | 6.42→6.44；6.45 最终对账 |
| **合计** | **0-16 + 增量 + P1×7 + P0 gap×3** | **85** | |

## 关键里程碑

> **口径（框架约束）**：触发条件以 `tasks.md` **Task 收口块**、**Batch 收口引用**及 [`task-execution-log.md`](task-execution-log.md) 批次记录为证；里程碑表格仅作索引，**不替代**上述真值。

| 里程碑 | 触发条件 | 产物 |
|--------|---------|------|
| M1：骨架可运行 | Batch 1 完成 | `ai-sdlc --help` 可执行，所有模型可实例化 |
| M2：核心引擎就绪 | Batch 2 完成 | 状态机 + Git 客户端全部测试通过 |
| M3：路由 + 治理就绪 | Batch 3 完成 | Bootstrap + Intake + PRD + Governance 全部通过 |
| M4：全模块就绪 | Batch 4 完成 | 分支 + 门禁 + Context + 模板 全部通过 |
| M5：P0 交付 | Batch 5 完成 | CLI 全命令可用 + Runner 全流程 + 流程测试通过 |
| M6：可移植性（T10） | Task 6.1 文档/规则收口完成；[`portability-audit-T10.md`](portability-audit-T10.md) 主表 P1/P2 已关闭 | 审计表可追溯；根目录 PRD **§12.3** 已补充多平台示例与规范真值（延期行 **已关闭**，2026-03-25）；**不将** Cursor/单一 IDE 作唯一操作路径 |
| M7：P1 框架增强（代码） | Task 6.3～6.5 完成 | plan-check、可选 checkpoint 元数据、verify constraints；SC-011～013 |
| M8：P1 分解门禁 | Task 6.7～6.9 完成；Task **6.10** 共用校验与 `verify constraints` / **SC-014** 对齐已于 **2026-03-25** 收口（见 Task 6.10 收口块 + `tests/unit/test_task_ac_checks.py`） | **FR-090** / **SC-014**；DecomposeGate + ExecuteGate 前置；`task_ac_checks` 与 `verify constraints` 同规则，防双轨漂移 |
| M9：P1 收口硬化 | Task **6.11～6.14** 完成（见 [`task-execution-log.md`](task-execution-log.md) **Batch 2026-03-25-011**；6.14 为 **FR-094** `verify constraints`↔skip-registry 映射） | close-check、文档一致性、偏离登记产品化闭环；SC-017～019 |
| M10：P1 规则作用域收敛 | Task **6.15～6.19** 完成（见 **Batch 2026-03-25-012** 收口块）；**延伸文档收口**（Task **6.6**、`pipeline` 与 Runner 对照、登记表/T10 余项）见 **Batch 2026-03-25-013** | **FR-095～098**；**SC-020～023**；skip-registry / close-check / verify 作用域收敛；[`research-pipeline-vs-runner.md`](research-pipeline-vs-runner.md) 对齐 `pipeline.md` 与 Runner |
| M11：001 核心闭环修复 | Task **6.21～6.26** 完成 | Governance Freeze、execute 主闭环、resume-pack load、`work-item.yaml` 状态持久化、Batch 11 traceability/backlog 回填 |
| M12：001 偏差清零与最终对账 | Task **6.27～6.31** 完成 | PRD Studio / branch / gate / index / gate CLI 残余漂移修复；drift matrix、plan/tasks、close-check、backlog 全面对齐 |
| M13：001 新增 gap contracts 收口 | Task **6.32～6.39** 完成（见 [`task-execution-log.md`](task-execution-log.md) Batch **2026-03-28-019** / **2026-03-28-020**） | intake / governance / branch protocol / context artifacts / gate taxonomy 与 2026-03-28 新补 spec 合同对齐 |
| M14：001 第一波 backlog 兼容恢复收口 | Task **6.40～6.41** 完成 | legacy root artifacts / stale checkpoint reconcile 真值统一到 `status` / `recover` / `run` / `stage` |
| M15：001 第二波 backlog 规则与发布卫生收口 | Task **6.42～6.45** 完成 | Git 写互斥 guardrail、docs-only fresh verification protocol、文档优先执行前置判定进入正式 contract |

> **延伸（发布卫生 / 本地配置，2026-03-26）**：`.ai-sdlc/project/config/project-config.yaml` 不入库与示例/默认加载见 [`task-execution-log.md`](task-execution-log.md) **Batch 2026-03-25-014**（主提交 `ad7e3c79d7ba9b6259006fcf15bb36eb9006430c`）；**0.2.4** 版本、`v0.2.4` 标签与离线包构建见 **Batch 2026-03-26-015**（主提交 `218bc79f45c8090764c9d823f65372b2564fa5cf`）。里程碑表仅作索引；批次证据以 `task-execution-log.md` 为准。
