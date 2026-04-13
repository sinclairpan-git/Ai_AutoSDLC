# 任务执行日志：Frontend Evidence Class Readiness Gate Runtime Baseline

**功能编号**：`107-frontend-evidence-class-readiness-gate-runtime-baseline`  
**创建日期**：2026-04-13  
**状态**：已完成

## 1. 归档规则

- 本文件是 `107-frontend-evidence-class-readiness-gate-runtime-baseline` 的固定执行归档文件。
- 后续每完成一批任务，都在**本文件末尾追加一个新的批次章节**。
- 后续每一批任务开始前，必须先完成固定预读（PRD + 宪章 + 当前相关 spec 文档）。
- 后续每一批任务结束后，必须按固定顺序执行：
  - 先完成实现和验证
  - 再把本批结果追加归档到本文件
  - **单次提交（FR-097 / SC-022）**：将本批代码/测试与本次追加的归档段落、`tasks.md` 勾选 **合并为一次** `git commit`，避免「先写提交哈希占位、再改代码、再二次更新归档」的噪音
  - 只有在当前批次已经提交完成后，才能进入下一批任务
- 每个任务记录固定包含以下字段：
  - 任务编号
  - 任务名称
  - 改动范围
  - 改动内容
  - 新增/调整的测试
  - 执行的命令
  - 测试结果
  - 是否符合任务目标

## 2. 批次记录

### Batch 2026-04-13-001 | T11-T32

#### 2.1 批次范围

- **覆盖任务**：`Task 1.1` ~ `Task 3.2`
- **覆盖阶段**：formal baseline、red tests、runtime implementation、verification
- **预读范围**：`081`、`092`、`105`、`106`、runtime code 与现有测试
- **激活的规则**：`FR-107-001` ~ `FR-107-007`
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- `R1`（红灯验证，如有 TDD）
  - 命令：
    - `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'framework_capability_when_attachment_missing or fails_closed_when_attachment_missing' -q`
    - `uv run pytest tests/unit/test_program_service.py -k 'waives_observation_gap_for_framework_capability or keeps_observation_gap_for_consumer_adoption or execution_gates_pass_for_closed_framework_capability_without_observations' -q`
    - `uv run pytest tests/integration/test_cli_program.py -k 'waives_observation_gap_for_framework_capability' -q`
  - 结果：
    - 初次红灯分别暴露 `unexpected keyword frontend_evidence_class`、framework 路径仍为 `missing_artifact`、CLI 未出现 `advisory_only`
- `V1`（定向验证）
  - 命令：
    - `uv run pytest tests/unit/test_frontend_gate_verification.py -k 'framework_capability_when_attachment_missing or fails_closed_when_attachment_missing' -q`
    - `uv run pytest tests/unit/test_program_service.py -k 'waives_observation_gap_for_framework_capability or keeps_observation_gap_for_consumer_adoption or execution_gates_pass_for_closed_framework_capability_without_observations' -q`
    - `uv run pytest tests/integration/test_cli_program.py -k 'waives_observation_gap_for_framework_capability or exposes_frontend_readiness' -q`
  - 结果：
    - `2 passed, 14 deselected in 0.61s`
    - `3 passed, 171 deselected in 0.76s`
    - `2 passed, 121 deselected in 1.20s`
- `V2`（全量回归）
  - 命令：
    - `uv run ruff check src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py`
    - `uv run ai-sdlc verify constraints`
    - `uv run ai-sdlc program validate`
    - `uv run ai-sdlc program status`
    - `git diff --check -- src/ai_sdlc/cli/program_cmd.py src/ai_sdlc/core/frontend_gate_verification.py src/ai_sdlc/core/program_service.py tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py program-manifest.yaml specs/107-frontend-evidence-class-readiness-gate-runtime-baseline`
  - 结果：
    - `ruff check` 通过：`All checks passed!`
    - `verify constraints` 通过：`verify constraints: no BLOCKERs.`
    - `program validate` 初次因 `107` 错挂未注册依赖 `092-...` 失败；移除非法 manifest DAG 边后复跑通过
    - `program status` 复跑后显示 `107-frontend-evidence-class-readiness-gate-runtime-baseline: ready / advisory_only`
    - `git diff --check` 通过

#### 2.3 任务记录

##### T11-T32 | evidence-class-aware readiness runtime

- 改动范围：
  - `src/ai_sdlc/core/frontend_gate_verification.py`
  - `src/ai_sdlc/core/program_service.py`
  - `src/ai_sdlc/cli/program_cmd.py`
  - `tests/unit/test_frontend_gate_verification.py`
  - `tests/unit/test_program_service.py`
  - `tests/integration/test_cli_program.py`
  - `program-manifest.yaml`
  - `.ai-sdlc/project/config/project-state.yaml`
  - `specs/107-frontend-evidence-class-readiness-gate-runtime-baseline/*`
- 改动内容：
  - 创建 `107` formal carrier，并将 `next_work_item_seq` 推进到 `108`
  - 在 `program_service` 中只从 canonical `spec.md` footer 读取 `frontend_evidence_class`，并把该 truth 接入 frontend readiness / execute gate
  - 在 `frontend_gate_verification` 中为 `framework_capability` 且唯一 observation 缺口为 `frontend_contract_observations` 的场景增加 `ready / advisory_only` 豁免
  - 保持 `consumer_adoption`、footer 缺失/非法、其他真实 gate blocker 的行为不变
  - 调整 CLI frontend readiness 格式化，使 `ready / advisory_only` 在状态输出中可见
  - 将 `107` manifest 依赖修正为仅引用当前图中已注册的 `106`
- 新增/调整的测试：
  - `tests/unit/test_frontend_gate_verification.py`：framework-capability attachment gap 豁免用例
  - `tests/unit/test_program_service.py`：framework-capability 与 consumer-adoption 分流，以及 closed execute gate 行为
  - `tests/integration/test_cli_program.py`：CLI `program status` 显式暴露 `ready / advisory_only`
- 执行的命令：
  - 见本批 `R1`、`V1`、`V2`
- 测试结果：
  - 红灯先失败，证明 runtime 与 CLI surface 存在真实缺口
  - 实现后 focused unit / integration pytest 全部通过
  - `verify constraints`、`ruff check`、`git diff --check` 通过
  - `program validate` 与 `program status` 在修正 manifest 非法依赖后通过
- 是否符合任务目标：是；framework-capability observation gap 已按 `081` prospective contract 落地为 evidence-class-aware runtime，consumer-adoption 语义保持不变

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：运行时只放宽 canonical `framework_capability` + `frontend_contract_observations` 缺口，未扩张到其他 blocker
- 代码质量：改动集中在 readiness chain、execute decision 与 CLI surface，未引入新的 evidence class 或旁路 manifest mirror
- 测试质量：包含红灯到绿灯的 unit / integration coverage，覆盖 framework-capability 放宽、consumer-adoption 保留、CLI 输出可见性
- 结论：符合 `107` 规格，且修复了本批发现的 manifest 非法依赖问题

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：已同步到 close-check 前状态
- `related_plan`（如存在）同步状态：不适用
- 关联 branch/worktree disposition 计划：retained（当前分支保留为本批 truth carrier）
- 说明：formal docs、manifest、runtime、tests 与验证结果已经一致；当前分支与工作树均按 retained 收口

#### 2.6 自动决策记录（如有）

无

#### 2.7 批次结论

- `107` 已把 evidence-class-aware readiness 真实接入 runtime，并让 CLI surface 诚实暴露 `ready / advisory_only`
- framework-capability 不再因缺少真实 observation artifact 直接 fail closed；consumer-adoption 行为保持原状
- 本批中途发现并修复了 `107` manifest 非法依赖 `092` 的 formal 图错误

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一 close-out commit 预期为 `feat(core): wire frontend evidence class readiness gate`；完整 SHA 以该提交后的 `HEAD`（`git rev-parse HEAD`）为准
- 当前批次 branch disposition 状态：retained
- 当前批次 worktree disposition 状态：retained
- 是否继续下一批：否；本批已完成
