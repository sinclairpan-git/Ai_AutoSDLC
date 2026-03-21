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

## 任务统计

| Batch | Phase | 任务数 | 可并行 |
|-------|-------|--------|--------|
| 1 | 0-1 | 10 | Task 1.4/1.5/1.6/1.8 可并行 |
| 2 | 2 | 3 | Task 2.1/2.2 可并行 |
| 3 | 3-4 | 6 | Task 3.1~3.3 与 Task 3.4~3.6 可并行 |
| 4 | 5-8 | 12 | Task 4.11/4.12 可并行 |
| 5 | 9-10 | 9 | Task 5.1~5.5 可并行 |
| **合计** | **0-10** | **40** | |

## 关键里程碑

| 里程碑 | 触发条件 | 产物 |
|--------|---------|------|
| M1：骨架可运行 | Batch 1 完成 | `ai-sdlc --help` 可执行，所有模型可实例化 |
| M2：核心引擎就绪 | Batch 2 完成 | 状态机 + Git 客户端全部测试通过 |
| M3：路由 + 治理就绪 | Batch 3 完成 | Bootstrap + Intake + PRD + Governance 全部通过 |
| M4：全模块就绪 | Batch 4 完成 | 分支 + 门禁 + Context + 模板 全部通过 |
| M5：P0 交付 | Batch 5 完成 | CLI 全命令可用 + Runner 全流程 + 流程测试通过 |
