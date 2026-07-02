# 任务执行日志：Loop Engine Frontend Evidence Loop Runtime

**功能编号**：`195-loop-engine-frontend-evidence-loop-runtime`
**创建日期**：2026-07-01
**状态**：执行中

## 1. 归档规则

- 本文件是 `195-loop-engine-frontend-evidence-loop-runtime` 的固定执行归档文件。
- 每完成一批任务，都在本文件末尾追加新的批次章节。
- 每一批任务开始前，必须先完成固定预读：`spec.md`、`plan.md`、`tasks.md`、宪章、本工作项依赖的上游 loop 文档。
- 每一批任务结束后，必须按固定顺序执行：
  - 完成实现和验证
  - 追加本批结果到本文件
  - 更新 `tasks.md` 状态和 handoff
  - 将本批代码/测试/文档/归档合并为一次 commit
  - 当前批次提交完成后，才进入下一批任务
- 每个任务记录固定包含：
  - 任务编号
  - 任务名称
  - 改动范围
  - 改动内容
  - 新增/调整的测试
  - 执行的命令
  - 测试结果
  - 是否符合任务目标

## 2. 批次记录

### Batch 2026-07-01-001 | Formal baseline freeze

#### 2.1 批次范围

- 覆盖任务：`T11`
- 覆盖阶段：Batch 1 formal baseline freeze and linkage
- 预读范围：`spec.md`、`plan.md`、`tasks.md`、WI-194 implementation loop runtime、现有 frontend browser gate artifact contract

#### 2.2 统一验证命令

- `V1`：`git diff --check`
- `V2`：`uv run ai-sdlc program truth sync --execute --yes`
- `V3`：`uv run ai-sdlc verify constraints`

#### 2.3 任务记录

##### T11 | 冻结 frontend-evidence formal docs

- 改动范围：`specs/195-loop-engine-frontend-evidence-loop-runtime/spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 改动内容：
  - 将初始化模板替换为真实 `frontend-evidence` PRD、计划、任务拆解和执行归档。
  - 明确本 loop 只消费本地 browser gate artifact，不重新实现浏览器探测，不调用模型，不硬编码 GitHub 或单一前端栈。
  - 明确 P0 close gate：质量 blocker fail-closed，advisory 必须显式 `--allow-warnings`。
- 新增/调整的测试：本批为文档冻结，无新增测试文件。
- 执行的命令：
  - `git diff --check`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program frontend-evidence-class-sync --spec-id 195-loop-engine-frontend-evidence-loop-runtime --execute --yes`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `git diff --check`
- 测试结果：diff check passed；frontend evidence class manifest mirror 已更新；truth snapshot refreshed；`verify constraints: no BLOCKERs`。第一次 truth sync 暴露 WI-195 `frontend_evidence_class` mirror missing，已用框架 sync 命令修复后复跑通过。
- 是否符合任务目标：符合；WI-195 formal docs 已从 direct-formal 模板修订为真实 frontend-evidence loop PRD、计划和任务拆解。

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：已对齐；本批只冻结 frontend-evidence loop 文档，不越界到 runtime 实现。
- 代码质量：本批不改运行时代码。
- 测试质量：文档批次已用 diff check、truth sync、frontend evidence class sync 和 verify constraints 覆盖。
- 结论：可以提交文档冻结批次，然后进入 T21 models/store。

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T11 已完成；T21-T42 仍为 todo。
- `related_plan` 同步状态：plan 已替换为 frontend-evidence 实施计划。
- 关联 branch/worktree disposition 计划：提交文档冻结基线后继续 T21。

#### 2.6 批次结论

- WI-195 formal baseline 已冻结；后续按 Batch 2 实现 models/store 和 ingestion runtime。

#### 2.7 归档后动作

- 已完成 git 提交：否
- 提交哈希：待本批提交后生成
- 当前批次 branch disposition 状态：待提交
- 当前批次 worktree disposition 状态：验证已通过，待提交
- 是否继续下一批：验证和提交后继续 T21

### Batch 2026-07-01-002 | Runtime, CLI, status/list, docs constraints

#### 2.8 批次范围

- 覆盖任务：`T21`、`T22`、`T31`、`T32`、`T33`、`T41`
- 覆盖阶段：Batch 2、Batch 3、Batch 4 documentation/constraints
- 改动范围：`src/ai_sdlc/core/frontend_evidence_models.py`、`frontend_evidence_store.py`、`frontend_evidence_loop.py`、`loop_status.py`、`src/ai_sdlc/cli/loop_cmd.py`、`README.md`、`src/ai_sdlc/core/verify_constraints.py`、相关测试

#### 2.9 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_loop_status.py tests/unit/test_frontend_evidence_loop.py -q`
- `V3`：`uv run pytest tests/integration/test_cli_loop.py -q`
- `V4`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V5`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V6`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V7`：`uv run ai-sdlc verify constraints`

#### 2.10 任务记录

##### T21 | frontend-evidence artifact models and store

- 改动内容：
  - 新增 frontend-evidence input、snapshot、report、close、current pointer、command result 和 artifact ref 模型。
  - 新增 `.ai-sdlc/loops/frontend-evidence/<loop-id>/` path helper、current pointer 解析、source artifact path 安全解析和 artifact readers。
- 新增/调整的测试：`tests/unit/test_frontend_evidence_loop.py`
- 执行的命令：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- 测试结果：6 passed
- 是否符合任务目标：符合

##### T22 | start runtime and browser gate ingestion

- 改动内容：
  - 实现 implementation close gate，要求同一 work item 且 `requires_frontend_evidence=true`。
  - 解析本地 browser gate YAML，校验 schema、work item scope、gate namespace、required receipt decision，并生成 evidence snapshot/report。
  - 支持 default latest artifact、显式 `--artifact-path` 和 `--dry-run`。
- 新增/调整的测试：pass、dry-run、missing artifact、scope mismatch、evidence_missing、advisory scenarios
- 执行的命令：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- 测试结果：6 passed
- 是否符合任务目标：符合

##### T31 | close gate

- 改动内容：
  - 实现 `close_frontend_evidence_loop`。
  - 无 blocker 的 passed report 可关闭；advisory warnings 必须显式 `--allow-warnings`；blocked/needs_fix/malformed/missing report fail-closed。
  - close 后写入 `frontend-evidence-close.json` 并指向 local PR review。
- 新增/调整的测试：`test_close_frontend_evidence_loop_requires_allow_warnings`、`test_frontend_evidence_loop_needs_fix_for_missing_evidence`
- 执行的命令：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- 测试结果：6 passed
- 是否符合任务目标：符合

##### T32 | CLI

- 改动内容：
  - 注册 `ai-sdlc loop frontend-evidence start/status/close`。
  - human 输出包含 Result、Next、Gate status、Blockers、Warnings、Artifacts；JSON 输出使用 Pydantic payload。
- 新增/调整的测试：`test_loop_frontend_evidence_start_status_and_close_json`
- 执行的命令：`uv run pytest tests/integration/test_cli_loop.py -q`
- 测试结果：35 passed
- 是否符合任务目标：符合

##### T33 | loop status/list

- 改动内容：
  - `get_loop_status` 和 `list_loops` 支持 `frontend-evidence`。
  - 新增 `FrontendEvidenceLoopSummary`、current pointer 读取、history 扫描、malformed current target blocker 和 guidance。
- 新增/调整的测试：current、history、closed next action、malformed current target
- 执行的命令：`uv run pytest tests/unit/test_loop_status.py tests/unit/test_frontend_evidence_loop.py -q`
- 测试结果：50 passed
- 是否符合任务目标：符合

##### T41 | docs and verify constraints

- 改动内容：
  - README 增加 Frontend Evidence Loop 用户路径，明确本 loop 不跑 browser gate、不调用模型、不依赖 GitHub/CI/remote preview。
  - `verify_constraints.py` 增加 195 feature contract surfaces。
- 新增/调整的测试：`test_195_feature_contract_surfaces_cover_frontend_evidence_loop_runtime`
- 执行的命令：`uv run pytest tests/unit/test_verify_constraints.py -q`、`uv run ai-sdlc verify constraints`
- 测试结果：focused regression 228 passed；ruff passed；mypy passed；verify constraints no BLOCKERs
- 是否符合任务目标：符合

#### 2.11 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只包装本地 browser gate artifact，未引入模型调用、GitHub 假设、CI 模型请求或前端代码写入。
- 代码质量：models/store/runtime/CLI/status 分层与既有 requirement/design/implementation loop 模式一致；source artifact path、current pointer、gate namespace 均 fail-closed。
- 测试质量：覆盖 P0/P1 行为，包括 passed、advisory、missing evidence、scope mismatch、missing artifact、status/list、CLI JSON 和 docs constraints。
- 结论：进入最终 regression、truth sync、close-check 和 PR 收口。

#### 2.12 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T21、T22、T31、T32、T33、T41 已完成；T42 待最终收口。
- `related_plan` 同步状态：Phase 1-4 的 runtime、CLI、status/list、docs/constraints 已落地。
- 关联 branch/worktree disposition 计划：继续同一分支，完成最终验证后提交并开 PR。

#### 2.13 批次结论

- frontend-evidence loop runtime、CLI、status/list、docs/constraints 已完成 focused 验证。

#### 2.14 归档后动作

- 已完成 git 提交：否
- 提交哈希：待最终验证后生成
- 当前批次 branch disposition 状态：待提交
- 当前批次 worktree disposition 状态：focused 验证通过，待最终验证
- 是否继续下一批：继续 T42 最终回归与 PR 收口

### Batch 2026-07-01-003 | Final regression and PR carrier close-out

#### 3.1 批次范围

- 覆盖任务：`T42`
- 覆盖阶段：Batch 4 final regression, truth sync, close-check, PR carrier preparation
- 改动范围：`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/tasks.md`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`

#### 3.2 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V2`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V3`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V4`：`git diff --check`
- `V5`：`uv run ai-sdlc verify constraints`
- `V6`：`uv run ai-sdlc program truth sync --execute --yes`
- `V7`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 3.3 任务记录

##### T42 | 完成最终回归与 PR 收口

- 改动内容：
  - 完成 focused regression、lint、type check、diff check、verify constraints 和 program truth sync。
  - 刷新 `program-manifest.yaml` truth snapshot，WI-195 program truth 检查通过；全局 source inventory 仍保留既有 migration_pending 状态。
  - 执行 pre-commit close-check，除最新批次缺少 git close-out markers 外，其余检查均 PASS；本批补齐 close-out markers 后复跑。
- 执行的命令：
  - `uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
  - `uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
  - `uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
  - `git diff --check`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`
- 测试结果：
  - pytest focused：228 passed
  - ruff：PASS
  - mypy：PASS，5 source files
  - diff check：PASS
  - verify constraints：PASS，no BLOCKERs
  - truth sync：PASS，written path `program-manifest.yaml`
  - pre-commit close-check：除预期 git close-out marker blocker 外，其余 checks PASS；本批补齐 marker 后复跑
- 是否符合任务目标：源码侧最终验证符合；提交、推送、PR、Codex review、required checks 和 merge 继续通过外部 PR 状态验证。

#### 3.4 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；WI-195 只交付 `frontend-evidence` loop，不重新实现 browser gate，不调用模型，不硬编码 GitHub/CI/remote preview，不写前端业务代码。
- 代码质量：runtime/store/models/status/CLI 沿用既有 loop 分层；artifact path、work item scope、current pointer 和 browser gate namespace 均 fail-closed。
- 测试质量：覆盖 passed、advisory、missing artifact、scope mismatch、missing evidence、status/list、CLI JSON、docs constraints 和既有 loop 不回归。
- 结论：可以提交当前分支，推送并创建 PR，请求 Codex review。

#### 3.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T11、T21、T22、T31、T32、T33、T41、T42 均已完成源码侧收口。
- `related_plan` 同步状态：Phase 1-4 的 runtime、CLI、status/list、docs/constraints、final regression 均已落地。
- 关联 branch/worktree disposition 计划：`feature/195-loop-engine-frontend-evidence-loop-runtime-docs` 作为 PR merge carrier，提交后推送并创建 PR。

#### 3.6 归档后动作

- frontend-evidence loop 的本地实现与验证已完成；下一步提交、推送、创建 PR、请求 Codex review，并在 required checks 通过后合并。
- **验证画像**：`code-change`
- **改动范围**：`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`、`README.md`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/tasks.md`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`src/ai_sdlc/cli/loop_cmd.py`、`src/ai_sdlc/core/frontend_evidence_models.py`、`src/ai_sdlc/core/frontend_evidence_store.py`、`src/ai_sdlc/core/frontend_evidence_loop.py`、`src/ai_sdlc/core/loop_status.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/integration/test_cli_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/unit/test_loop_status.py`、`tests/unit/test_verify_constraints.py`
- **已完成 git 提交**：是
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：`feature/195-loop-engine-frontend-evidence-loop-runtime-docs` 作为 PR merge carrier，提交后推送并创建 PR
- 当前批次 worktree disposition 状态：提交后进入 PR / Codex review 监控
- 是否继续下一批：提交、推送、PR、Codex review、merge

### Batch 2026-07-01-004 | Codex review receipt artifact remediation

#### 4.1 批次范围

- 覆盖任务：`T42-R1`
- 覆盖阶段：PR #112 Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`

#### 4.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3508505515`
- 问题级别：P1
- 问题摘要：browser gate receipt 引用 artifact IDs 时，frontend-evidence loop 只校验已有 `artifact_records` 的 namespace，没有强制每个 receipt artifact ID 解析到 namespaced record 和真实本地文件，可能让截断或不完整证据误判为 passed。

#### 4.3 修复内容

- `_namespace_blocker` 增加 receipt artifact closure 校验：
  - artifact record id 不得重复。
  - 每个 artifact record 必须位于 `.ai-sdlc/artifacts/frontend-browser-gate/<gate-run-id>/` namespace。
  - 每个 artifact record 解析后的路径必须仍在项目根目录内。
  - 每个 artifact record 必须对应存在的本地文件。
  - 每个 receipt 的 artifact ID 必须能反向解析到 artifact record。
- 单元测试新增两个 fail-closed 场景：
  - receipt 引用缺失的 artifact record。
  - artifact record 存在但本地文件缺失。
- CLI 集成测试 fixture 补齐真实本地 browser artifact 文件，保证正常路径也覆盖文件存在要求。

#### 4.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/integration/test_cli_loop.py -q`
- `V3`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V4`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V5`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V6`：`git diff --check`
- `V7`：`uv run ai-sdlc verify constraints`
- `V8`：`uv run ai-sdlc program truth sync --execute --yes`
- `V9`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 4.5 验证结果

- unit targeted：8 passed
- CLI integration：35 passed
- focused regression：230 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`，snapshot hash `4a242e0caa3dcefae03c6245cd3a8a5f118801e2f7a83aa38877b7b8820b6c4d`
- close-check：PASS，`done_gate PASS ready for completion`
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`，snapshot hash `4667142f28b1c1de60e13688f148e0b246d0466b1ef696cfebbc1372a9312709`
- close-check：PASS，`done_gate PASS ready for completion`
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`，snapshot hash `49479c4b892abae9a259904481c06527ceb12e81312e3575c540473dad247a0a`
- close-check：PASS，`done_gate PASS ready for completion`
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`，snapshot hash `986838eda77e4a0d0bb1aacf4667f7be93f2d6dd69caf6ca609a7303b8270c56`
- close-check：PASS，`done_gate PASS ready for completion`
- truth sync：PASS，written path `program-manifest.yaml`

#### 4.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只修 Codex review 指出的 frontend-evidence evidence integrity 问题，不扩展到 browser gate 重实现、模型调用或 GitHub 专用逻辑。
- 代码质量：新增校验位于 ingestion trust boundary，错误 fail-readable，避免 close gate 接收截断证据。
- 测试质量：新增缺 record 与缺文件回归，并保持 CLI happy path、status/list、docs constraints 不回归。
- 结论：提交后推送 PR #112，重新请求 Codex review 并继续 required checks heartbeat。

#### 4.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 仍为完成状态；本批为 PR review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围；仍只交付 `frontend-evidence` loop。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 4.8 归档后动作

- Codex review P1 已修复并通过 focused regression；下一步提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-02-001 | Provider-first browser evidence readiness guidance

#### 1.1 批次范围

- 覆盖任务：`T51`、`T52`
- 覆盖阶段：PR #113 release gate follow-up；frontend loop 场景补强
- 改动范围：`README.md`、`specs/195-loop-engine-frontend-evidence-loop-runtime/spec.md`、`plan.md`、`tasks.md`、`src/ai_sdlc/core/frontend_evidence_models.py`、`src/ai_sdlc/core/frontend_evidence_loop.py`、`src/ai_sdlc/cli/loop_cmd.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`tests/unit/test_verify_constraints.py`、`scripts/loop_e2e_release_gate.py`

#### 1.2 任务来源

- 用户要求：将“用户可能已有 Codex browser 控制能力、浏览器 MCP/插件，不能硬推 Playwright；若缺浏览器 E2E 能力，应给出具体、用户友好的路径”纳入前端 loop 场景。
- 风险摘要：
  - 只提示安装 Playwright 会误伤 Codex/browser MCP/企业内网 E2E 用户。
  - 缺 artifact 时直接提示 `browser-gate-probe` 会把 provider 选择、artifact 导入和 Playwright 缺失混成一个问题。

#### 1.3 修订内容

- PRD 新增 P0 用户故事 `1A`：浏览器 E2E 能力缺失时 provider-first 指引。
- 新增只读 `ai-sdlc loop frontend-evidence doctor`：
  - `--provider auto|codex-browser|browser-mcp|external-artifact|playwright`
  - `--frontend-dir`
  - `--browser`
  - `--json`
- doctor 推荐顺序改为已有 artifact / 已配置 browser provider / 已安装 Playwright / 用户显式选择后可选安装 Playwright。
- `frontend-evidence start` 缺 browser gate artifact 时，下一步改为 `ai-sdlc loop frontend-evidence doctor`。
- README 新手路径先运行 doctor；Codex browser/browser MCP 用户走 artifact 导入；显式 Playwright 用户通过 doctor 查看 npm/pnpm/yarn 安装命令。
- release gate E2E 脚本新增 provider-first 断言：
  - 缺 artifact 指向 doctor。
  - `--provider codex-browser` 不硬推 Playwright。
  - 写入 artifact 后 auto 推荐 `external-artifact`。

#### 1.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V2`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py scripts/loop_e2e_release_gate.py`
- `V3`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/cli/loop_cmd.py`
- `V4`：`git diff --check`
- `V5`：`uv run ai-sdlc verify constraints`
- `V6`：`uv run python scripts/loop_e2e_release_gate.py`
- `V7`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py -q`

#### 1.5 验证结果

- focused pytest：203 passed
- final focused pytest + workflow tests：211 passed
- ruff：PASS
- mypy：PASS，3 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- local clean-project Loop E2E：PASS，artifact root `.ai-sdlc/artifacts/loop-e2e-release-gate/loop-e2e-20260702T011620Z`

#### 1.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；新增 doctor 是只读 provider readiness，不调用模型、不安装依赖、不写业务代码。
- 代码质量：provider-first 输出避免把 Playwright 设为默认唯一推荐；显式 Playwright 仍给具体安装命令。
- 测试质量：新增单元、CLI 集成和 E2E 脚本断言覆盖 Codex browser、external artifact 和 Playwright 显式路径。
- 结论：可提交到 PR #113 carrier branch，并等待 GitHub macOS/Windows E2E 重新验证。

#### 1.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：新增 Batch 5；T51/T52 done；T53 planned。
- `related_plan` 同步状态：新增 provider-first readiness 工作流 A1。
- 关联 branch/worktree disposition 计划：继续使用 `codex/loop-e2e-release-gate` 和 PR #113。

#### 1.8 归档后动作

- 下一步提交、推送，并让 PR #113 重新跑 Loop E2E Release Gate。
- **验证画像**：`code-change`
- **改动范围**：见 1.1。
- **已完成 git 提交**：否（本 marker 将随 provider-first follow-up commit 一起落盘）
- **提交哈希**：`pending`
- 当前批次 branch disposition 状态：待提交并推送到 PR #113
- 当前批次 worktree disposition 状态：待 GitHub macOS/windows-latest workflow evidence 刷新
- 是否继续下一批：否；等待 PR #113 checks

### Batch 2026-07-02-002 | Frontend evidence explicit skip for unavailable browser control

#### 2.1 批次范围

- 覆盖任务：`T54`
- 覆盖阶段：PR #113 release gate follow-up；frontend loop 不硬卡补强
- 改动范围：`README.md`、`specs/195-loop-engine-frontend-evidence-loop-runtime/spec.md`、`plan.md`、`tasks.md`、`src/ai_sdlc/core/frontend_evidence_models.py`、`src/ai_sdlc/core/frontend_evidence_loop.py`、`src/ai_sdlc/core/loop_status.py`、`src/ai_sdlc/cli/loop_cmd.py`、`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`tests/unit/test_verify_constraints.py`、`scripts/loop_e2e_release_gate.py`

#### 2.2 任务来源

- 用户要求：如果用户没办法安装浏览器插件控制浏览器，前端 loop 必须可以跳过，不能硬卡。
- 风险摘要：
  - 仅提供 provider doctor 仍可能让没有任何 browser control 能力的用户停在 frontend-evidence loop。
  - 直接跳过若无审计，会把质量证据缺失误读为通过。

#### 2.3 修订内容

- 新增 `ai-sdlc loop frontend-evidence skip --wi specs/<work-item> --reason <text> --yes`。
- skip 要求 closed same-work-item implementation loop、明确 reason 和 `--yes`。
- skip 不要求 browser gate artifact，不调用模型、不安装依赖、不写业务代码。
- skip 成功后写入 `frontend-evidence-input/snapshot/report/close/loop-run/current pointer`，其中 close artifact 记录：
  - `skipped=true`
  - `skip_reason`
  - `skip_risk_acknowledgement`
  - `closed_by`
- `loop status --type frontend-evidence` 展示 skipped 和 skip reason，下一步进入 local PR review。
- release E2E 新增缺 browser artifact 时显式 skip 的断言。

#### 2.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V2`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py scripts/loop_e2e_release_gate.py`
- `V3`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V4`：`uv run ai-sdlc verify constraints`
- `V5`：`uv run python scripts/loop_e2e_release_gate.py`
- `V6`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py -q`
- `V7`：`git diff --check`

#### 2.5 验证结果

- focused pytest：206 passed
- final focused pytest + workflow tests：214 passed
- ruff：PASS
- mypy：PASS，4 source files
- verify constraints：PASS，no BLOCKERs
- local clean-project Loop E2E：PASS，artifact root `.ai-sdlc/artifacts/loop-e2e-release-gate/loop-e2e-20260702T013108Z`
- diff check：PASS

#### 2.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；跳过路径是显式风险接受，不把前端证据缺失伪装为 passed。
- 代码质量：skip 使用同一 implementation gate，持久化 closed loop 和 close artifact，status/list 可读 skipped。
- 测试质量：新增 unit、CLI integration、release E2E 覆盖无 browser control 时不硬卡。
- 结论：可提交并推送到 PR #113，等待 GitHub checks 重新验证。

#### 2.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：新增 T54 done。
- `related_plan` 同步状态：新增 Workflow A2 explicit skip。
- 关联 branch/worktree disposition 计划：继续使用 `codex/loop-e2e-release-gate` 和 PR #113。

#### 2.8 归档后动作

- 下一步提交、推送，并让 PR #113 重新跑 Loop E2E Release Gate。
- **验证画像**：`code-change`
- **改动范围**：见 2.1。
- **已完成 git 提交**：否（本 marker 将随 skip follow-up commit 一起落盘）
- **提交哈希**：`pending`
- 当前批次 branch disposition 状态：待提交并推送到 PR #113
- 当前批次 worktree disposition 状态：待 GitHub macOS/windows-latest workflow evidence 刷新
- 是否继续下一批：否；等待 PR #113 checks

### Batch 2026-07-01-013 | Codex review accepted warning reason codes remediation

#### 13.1 批次范围

- 覆盖任务：`T42-R10`
- 覆盖阶段：PR #112 tenth Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_models.py`、`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 13.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509302140`
- 问题级别：P2
- 问题摘要：`passed_with_advisories` 在 `--allow-warnings` close 时，close artifact 只记录 `warning_count`，没有记录被接受的 warning/advisory reason codes。

#### 13.3 修复内容

- `FrontendEvidenceClose` 新增 `accepted_warning_reason_codes`。
- `_write_close` 在 `allow_warnings=True` 时写入 report 的 `advisory_reason_codes`。
- 单元测试覆盖 advisory close artifact 必须记录 `low_contrast_text`。

#### 13.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`

#### 13.5 验证结果

- unit targeted：16 passed
- focused regression：239 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`

#### 13.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；close artifact 现在保留 warning acceptance 的 reason-code 证据，便于审计消费者不追溯 report 也能理解接受范围。
- 代码质量：新增字段向后兼容已有 close artifact 读取，不改变 close gate 语义。
- 测试质量：新增 close artifact reason-code assertion，并保持 focused suite 通过。
- 结论：可更新 handoff、提交、推送并重新请求 Codex review。

#### 13.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 tenth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 13.8 归档后动作

- 第十轮 Codex review P2 已修复；下一步 handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_models.py`、`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-014 | Codex review visual regression recheck remediation

#### 14.1 批次范围

- 覆盖任务：`T42-R11`
- 覆盖阶段：PR #112 latest Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 14.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509444007`
- 问题级别：P2
- 问题摘要：browser-gate runtime 在 visual regression 已配置但缺少 baseline/capture 时，会产出合法的 `visual_regression` receipt，`artifact_ids=[]`、`classification_candidate="evidence_missing"`、`recheck_required=true`；frontend-evidence namespace guard 把该可恢复重检误判为 blocked，导致不能写入 intended `needs_fix` 报告。

#### 14.3 修复内容

- `_namespace_blocker` 新增最小白名单：只允许 `visual_regression` 且 `recheck_required=true`、`classification_candidate` 为 `evidence_missing` / `transient_run_failure`、带 blocking reason codes 的 receipt 没有 artifact ids。
- 保留普通空 `artifact_ids` 的 fail-closed 语义，`playwright_smoke` 等通过态空证据仍 blocked。
- 单元测试新增 visual regression recheck 无 artifact ids 时生成 `needs_fix` 报告，并记录 remediation hint 与 reason code。

#### 14.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 14.5 验证结果

- unit targeted：17 passed
- focused regression：240 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 14.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只把 browser-gate runtime 的合法 visual regression recheck 状态映射为 frontend-evidence `needs_fix`，不放宽 passed/ready 证据闭合要求。
- 代码质量：白名单条件收敛到 check name、recheck flag、classification 和 blocking reason codes，避免重新打开空证据通过的风险。
- 测试质量：新增回归覆盖可恢复 visual regression 缺证据场景，同时既有普通空 receipt artifact fail-closed 用例继续通过。
- 结论：可刷新 truth、更新 handoff、提交、推送并重新请求 Codex review。

#### 14.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 latest Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 14.8 归档后动作

- 第十一轮 Codex review P2 已修复；下一步 truth sync、handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-015 | Codex review runtime session scope remediation

#### 15.1 批次范围

- 覆盖任务：`T42-R12`
- 覆盖阶段：PR #112 latest Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 15.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509496266`
- 问题级别：P2
- 问题摘要：`latest.yaml` 若包含当前 `execution_context` / `bundle_input`，但 `runtime_session` 来自其他 work item 或其他 browser entry，现有校验只比较 `gate_run_id`，可能把 stale/mismatched runtime session 当作当前证据并允许 close。

#### 15.3 修复内容

- `_namespace_blocker` 新增 runtime session scope 校验。
- 校验字段覆盖 `apply_result_id`、`solution_snapshot_id`、`spec_dir`、`attachment_scope_ref`、`managed_frontend_target`、`readiness_subject_id`、`browser_entry_ref`。
- 单元测试覆盖 `runtime_session.spec_dir` 和 `runtime_session.browser_entry_ref` 漂移时 fail-closed。

#### 15.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 15.5 验证结果

- unit targeted：18 passed
- focused regression：241 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 15.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；frontend-evidence ingestion 现在按 work item、目标、入口和上游 ids fail-closed，避免 stale runtime session 进入当前 loop。
- 代码质量：scope 校验集中在 namespace trust boundary；与既有 execution context/bundle linkage 校验互补，不改变 browser gate decision mapping。
- 测试质量：新增 scope drift 回归，并保持 visual regression recheck 与普通空证据 fail-closed 用例通过。
- 结论：可刷新 truth、更新 handoff、提交、推送并重新请求 Codex review。

#### 15.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 latest Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 15.8 归档后动作

- 第十二轮 Codex review P2 已修复；下一步 truth sync、handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-016 | Codex review stale browser evidence remediation

#### 16.1 批次范围

- 覆盖任务：`T42-R13`
- 覆盖阶段：PR #112 latest Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 16.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509555985`
- 问题级别：P1
- 问题摘要：同一 work item 的历史 `frontend-browser-gate/latest.yaml` 若已经 passed，implementation loop 新关闭后仍可能被 `frontend-evidence start` 接受，导致 implementation close 之后的 UI 变更没有重新跑 browser gate 就进入 local PR review。

#### 16.3 修复内容

- `frontend-evidence start` 读取当前 implementation loop 的 `implementation-close.json`。
- browser gate artifact 的顶层 `generated_at` 必须不早于 implementation close 的 `closed_at`；否则 fail-closed 并提示重新运行 `ai-sdlc program browser-gate-probe --execute`。
- 新增 ISO timestamp 解析，统一按 UTC 比较，兼容 `Z` 和 offset ISO。
- 单元测试新增 stale browser gate artifact 阻断。
- CLI 集成 fixture 固定 implementation close time 在 browser artifact 之前，避免正常成功用例被 freshness gate 误判。

#### 16.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 16.5 验证结果

- unit targeted：19 passed
- focused regression：242 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 16.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；frontend-evidence 现在绑定 browser evidence 到当前 closed implementation loop 之后的时间点，防止复用旧证据。
- 代码质量：freshness gate 在 build snapshot 早期执行；缺失/非法时间戳 fail-closed；正常 needs_fix 报告路径不受影响。
- 测试质量：新增 stale evidence 阻断，并保持 CLI 成功/needs_fix 回归通过。
- 结论：可刷新 truth、更新 handoff、提交、推送并重新请求 Codex review。

#### 16.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 latest Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 16.8 归档后动作

- 第十三轮 Codex review P1 已修复；下一步 truth sync、handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-017 | Codex review safe gate run id remediation

#### 17.1 批次范围

- 覆盖任务：`T42-R14`
- 覆盖阶段：PR #112 latest Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 17.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509608542`
- 问题级别：P2
- 问题摘要：hand-supplied browser-gate artifact 若在 `gate_run_id` 中包含 parent path segment，`expected_artifact_root` 会先被污染，后续字符串前缀和 `relative_to` 检查可能接受任意项目内目录作为 captured browser evidence。

#### 17.3 修复内容

- `_namespace_blocker` 在构造 expected artifact root 前校验 execution context、runtime session、bundle 三处 `gate_run_id`。
- 新增 `_is_safe_gate_run_id`，要求 id 非空、不是 `.` / `..`，且不包含 `/` 或 `\`。
- 单元测试新增 `../other-run` gate_run_id 阻断场景。

#### 17.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 17.5 验证结果

- unit targeted：20 passed
- focused regression：243 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 17.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；artifact namespace 的根 id 在使用前必须是安全单段路径，避免路径派生阶段被污染。
- 代码质量：校验发生在 expected artifact root 构造前；三处 gate_run_id 均需安全并保持既有一致性校验。
- 测试质量：新增恶意 gate_run_id 回归，并保持 stale evidence、scope drift、namespace traversal、empty evidence 等边界用例通过。
- 结论：可刷新 truth、更新 handoff、提交、推送并重新请求 Codex review。

#### 17.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 latest Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 17.8 归档后动作

- 第十四轮 Codex review P2 已修复；下一步 truth sync、handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-012 | Codex review ready evidence capture-status remediation

#### 12.1 批次范围

- 覆盖任务：`T42-R9`
- 覆盖阶段：PR #112 ninth Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 12.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509222971`
- 问题级别：P1
- 问题摘要：browser gate artifact 若仍声称 `overall_gate_status=passed` 且 receipts 为 pass，但 receipt 引用的 artifact record 为 `missing` 或 `capture_failed`，frontend-evidence 会跳过 captured-file 校验并允许 close。

#### 12.3 修复内容

- 新增 READY-gate evidence consistency 校验：只有 execute gate 为 `ready` 时，所有 receipt 引用的 artifact record 必须为 `capture_status=captured`。
- non-ready / needs-fix browser gate 仍允许 `missing`、`capture_failed` artifact records 流入 report，保留 remediation evidence。
- 新增单元测试覆盖 otherwise-passed artifact 携带 `missing` receipt evidence 时必须 blocked。

#### 12.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`

#### 12.5 验证结果

- unit targeted：16 passed
- focused regression：239 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`

#### 12.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只修 ready/passed evidence 的一致性，不破坏 failed/missing evidence report 保留。
- 代码质量：READY decision 后增加 capture-status consistency gate，避免 malformed passed bundle 绕过 fail-closed。
- 测试质量：新增 ready + missing evidence 回归，并保持 non-passing missing report 既有测试通过。
- 结论：可更新 handoff、提交、推送并重新请求 Codex review。

#### 12.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 ninth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 12.8 归档后动作

- 第九轮 Codex review P1 已修复；下一步 handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-011 | Codex review blocker status consistency remediation

#### 11.1 批次范围

- 覆盖任务：`T42-R8`
- 覆盖阶段：PR #112 eighth Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 11.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509148587`
- 问题级别：P2
- 问题摘要：browser gate artifact 若携带 `plain_language_blockers` 且 execute gate otherwise ready，report blocker_count 非零但 loop status 仍为 `passed`，导致 start 指向 close，而 close 又拒绝关闭。

#### 11.3 修复内容

- `_loop_status_for_snapshot` 改为 blockers 优先判定；存在 blockers 时不得返回 `passed`。
- execute gate blocked 且有 blockers 时保留 `blocked`，其他 blocker 场景进入 `needs_fix`。
- 新增单元测试覆盖 otherwise-passed artifact 携带 `plain_language_blockers` 时，start 返回 `needs_fix` 且 next guidance 指向重新运行 browser gate probe。

#### 11.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`

#### 11.5 验证结果

- unit targeted：15 passed
- focused regression：238 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`

#### 11.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只修 frontend-evidence report status 与 blocker guidance 一致性，不改变模型、CI、GitHub 或 browser gate 边界。
- 代码质量：blockers now dominate passed/advisory status, avoiding contradictory start/close guidance.
- 测试质量：新增 plain-language blocker 回归，并保持 focused suite 通过。
- 结论：可更新 handoff、提交、推送并重新请求 Codex review。

#### 11.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 eighth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 11.8 归档后动作

- 第八轮 Codex review P2 已修复；下一步 handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-010 | Codex review receipt evidence artifact remediation

#### 10.1 批次范围

- 覆盖任务：`T42-R7`
- 覆盖阶段：PR #112 seventh Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 10.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3509001644`
- 问题级别：P1
- 问题摘要：browser gate artifact 若保留 required receipt 名称，但清空所有 `artifact_ids`、`artifact_records`、截图和 trace refs，frontend-evidence 会把 otherwise passed artifact 误判为 passed，进而允许 `close --yes` 绕过证据闭环。

#### 10.3 修复内容

- `_namespace_blocker` 对每个 browser gate receipt 增加空 `artifact_ids` fail-closed 校验。
- 新增单元测试复现 Codex finding：清空 `artifact_records`、`screenshot_refs`、`playwright_trace_refs` 和所有 receipt `artifact_ids` 后，`start_frontend_evidence_loop` 必须 blocked。
- 修正 CLI integration browser gate fixture，为 `interaction_anti_pattern_checks` 增加 `interaction-snapshot` artifact record 与 receipt artifact id，使 fixture 与真实 runtime 产物一致。

#### 10.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/integration/test_cli_loop.py -q`
- `V3`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V4`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V5`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V6`：`git diff --check`
- `V7`：`uv run ai-sdlc verify constraints`
- `V8`：`uv run ai-sdlc program truth sync --execute --yes`

#### 10.5 验证结果

- unit targeted：14 passed
- CLI integration：36 passed
- focused regression：237 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，写回 `program-manifest.yaml`；truth snapshot state 仍为既有 `migration_pending`
- workitem close-check：PASS，done_gate PASS ready for completion

#### 10.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只强化 frontend-evidence 对 browser gate evidence receipt 的信任边界，不调用模型、不重写 browser gate、不引入 GitHub/远端 PR 假设。
- 代码质量：receipt 无证据 artifact 时直接 fail-closed，避免空证据 passed report 被关闭。
- 测试质量：新增直接复现 Codex P1 的回归，并保持 CLI fixture 与真实 browser gate interaction evidence 一致。
- 结论：可更新 handoff、提交、推送并重新请求 Codex review。

#### 10.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 seventh Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 10.8 归档后动作

- 第七轮 Codex review P1 已修复；下一步 handoff update、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-008 | Codex review missing capture artifact remediation

#### 8.1 批次范围

- 覆盖任务：`T42-R5`
- 覆盖阶段：PR #112 fifth Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 8.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3508836576`
- 问题级别：P2
- 问题摘要：browser gate 在正常 incomplete/transient probe 下可能写入 `capture_status="missing"` 或 `capture_status="capture_failed"` 的 artifact record，这些 record 可合法没有本地截图/trace 文件；frontend-evidence 不应因此提前 blocked，而应生成 `needs_fix` report。

#### 8.3 修复内容

- `_namespace_blocker` 保留 artifact id、gate namespace、project root 和 receipt closure 校验。
- 仅对 `capture_status="captured"` 的 artifact record 强制要求本地文件存在。
- `missing` / `capture_failed` artifact record 允许进入 snapshot/report，由 browser gate decision 生成 `needs_fix`，让用户能通过 `loop status --type frontend-evidence` 看到修复证据。
- 单元测试新增 missing capture record 回归，断言 report/snapshot 仍落盘且状态为 `needs_fix`。

#### 8.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`

#### 8.5 验证结果

- unit targeted：12 passed
- focused regression：235 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs
- truth sync：PASS，written path `program-manifest.yaml`；全局 truth snapshot 仍为既有 `migration_pending`

#### 8.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只修 frontend-evidence artifact ingestion 的失败证据保留逻辑，不改变 browser gate、模型调用或 PR source 假设。
- 代码质量：receipt artifact closure 仍 fail-closed，captured evidence 缺文件仍 blocked；missing/capture_failed evidence 进入 report，避免失败证据丢失。
- 测试质量：新增 missing capture record 回归，并保持 captured 缺文件、missing receipt、runtime state、CLI/status/list 和 constraints focused suite 通过。
- 结论：可更新 handoff、close-check、提交、推送并重新请求 Codex review。

#### 8.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 fifth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 8.8 归档后动作

- 第五轮 Codex review P2 已修复；下一步 handoff update、close-check、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-007 | Codex review non-passing runtime report remediation

#### 7.1 批次范围

- 覆盖任务：`T42-R4`
- 覆盖阶段：PR #112 fourth Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`

#### 7.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3508745049`
- 问题级别：P1
- 问题摘要：真实 browser gate 在 missing evidence 或 actual blocker 时会写 `runtime_session.status` / `probe_runtime_state` 为 `incomplete` 或 `failed`；frontend-evidence 不应在生成 `needs_fix` report 前直接 blocked。

#### 7.3 修复内容

- runtime state 校验移动到 browser gate execute decision 之后。
- 缺失 `probe_runtime_state` 仍然 blocked。
- 显式 non-completed runtime/probe state 仅在 execute decision 仍为 `ready` 时 blocked；若 browser gate decision 已是 non-ready，则允许生成 `needs_fix` / blocked report artifact。
- 既有 missing-evidence 测试改为更贴近真实 browser gate：overall incomplete 时 runtime/probe state 也为 incomplete，但 frontend-evidence 仍产出 `needs_fix`。

#### 7.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 7.5 验证结果

- unit targeted：11 passed
- focused regression：234 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 7.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批保持 frontend-evidence 的职责为包装 browser gate artifact 并记录 non-passing evidence，不把失败 probe 误导为重新运行即可。
- 代码质量：对缺失 runtime state、passed bundle with failed runtime、non-passing bundle with failed runtime 三类情况做了区分。
- 测试质量：保持 passed、blocked、missing field、missing evidence 等路径回归覆盖。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 7.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 fourth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 7.8 归档后动作

- 第四轮 Codex review P1 已修复；下一步 truth sync、close-check、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-009 | Codex review artifact namespace traversal remediation

#### 9.1 批次范围

- 覆盖任务：`T42-R6`
- 覆盖阶段：PR #112 sixth Codex review P2 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts

#### 9.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3508927833`
- 问题级别：P2
- 问题摘要：artifact record 只用字符串前缀校验 gate namespace，`artifact_ref` 含 `../` 时可能解析到 gate-run namespace 外但仍在仓库内。

#### 9.3 修复内容

- `_namespace_blocker` 新增 resolved expected artifact root。
- artifact record 除了字符串前缀与项目根校验外，还必须满足 resolved artifact path 位于 resolved gate-run artifact root 之下。
- 单元测试新增 `../` namespace traversal 回归，断言 loop blocked 且提示 gate namespace escape。

#### 9.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`

#### 9.5 验证结果

- unit targeted：13 passed
- focused regression：236 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 9.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批强化 frontend-evidence artifact namespace trust boundary，不改变 loop 范围或调用模型。
- 代码质量：同时保留字符串 namespace、项目根和 resolved gate root 校验，避免路径 traversal 伪造合法证据。
- 测试质量：新增 traversal 回归，并保持 prior captured/missing/capture_failed artifact 行为覆盖。
- 结论：可刷新 truth、handoff、close-check、提交、推送并重新请求 Codex review。

#### 9.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 sixth Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 9.8 归档后动作

- 第六轮 Codex review P2 已修复；下一步 truth sync、handoff update、close-check、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、handoff artifacts
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；提交后等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-006 | Codex review explicit probe state remediation

#### 6.1 批次范围

- 覆盖任务：`T42-R3`
- 覆盖阶段：PR #112 third Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`

#### 6.2 任务来源

- 审查来源：PR #112 Codex review inline comment `3508675706`
- 问题级别：P1
- 问题摘要：`probe_runtime_state` 缺失时不应 fallback 到 `runtime_session.status`；browser gate writer 会输出该顶层字段，ingestion 必须要求它显式存在且为 `completed`。

#### 6.3 修复内容

- `_runtime_state_blocker` 去掉 `probe_runtime_state or session_status` fallback。
- 缺失 `probe_runtime_state` 时返回 blocked，并提示重新运行 browser gate probe。
- 单元测试新增缺失 `probe_runtime_state` 的 fail-closed 回归。

#### 6.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V3`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V4`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V5`：`git diff --check`
- `V6`：`uv run ai-sdlc verify constraints`
- `V7`：`uv run ai-sdlc program truth sync --execute --yes`
- `V8`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 6.5 验证结果

- unit targeted：11 passed
- focused regression：234 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 6.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只强化 browser gate artifact ingestion 的显式 runtime state 约束。
- 代码质量：缺失顶层 `probe_runtime_state` 不再被 session status 掩盖，截断 artifact fail-closed。
- 测试质量：新增缺失字段回归，并保持 focused suite 通过。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 6.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 third Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 6.8 归档后动作

- 第三轮 Codex review P1 已修复；下一步 truth sync、close-check、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`tests/unit/test_frontend_evidence_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；等待 PR #112 Codex review、required checks 与合并

### Batch 2026-07-01-005 | Codex review runtime-state and CLI exit remediation

#### 5.1 批次范围

- 覆盖任务：`T42-R2`
- 覆盖阶段：PR #112 second Codex review P1 remediation
- 改动范围：`src/ai_sdlc/core/frontend_evidence_loop.py`、`src/ai_sdlc/cli/loop_cmd.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`

#### 5.2 任务来源

- 审查来源：PR #112 Codex review inline comments `3508603519`、`3508603526`
- 问题级别：P1
- 问题摘要：
  - `frontend-evidence start --json` 在 browser gate 为 `needs_fix` 时仍以 exit code 0 退出，脚本可能误判质量阻断为成功。
  - runtime ingestion 未在构建 execute decision 前校验 `runtime_session.status` / `probe_runtime_state`，截断 artifact 可能用 failed/incomplete session 搭配 passed bundle 误判通过。

#### 5.3 修复内容

- CLI start exit code 改为仅 `ready` / `dry_run` 返回 0；`needs_fix`、`needs_user`、`blocked` 均返回 1。
- `_build_snapshot` 在调用 `build_frontend_browser_gate_execute_decision` 前校验：
  - `runtime_session.status == "completed"`
  - effective `probe_runtime_state == "completed"`
  - 任一非 completed 均 fail-closed，并提示重新运行 `ai-sdlc program browser-gate-probe --execute`。
- 单元测试新增 failed runtime session 与 failed probe runtime state 两个 blocked 场景。
- CLI 集成测试新增 `frontend-evidence start` 在 `needs_fix` JSON 输出下 exit code 为 1 的回归。

#### 5.4 统一验证命令

- **验证画像**：`code-change`
- `V1`：`uv run pytest tests/unit/test_frontend_evidence_loop.py -q`
- `V2`：`uv run pytest tests/integration/test_cli_loop.py -q`
- `V3`：`uv run pytest tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py -q`
- `V4`：`uv run ruff check src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_frontend_evidence_loop.py tests/unit/test_loop_status.py tests/integration/test_cli_loop.py tests/unit/test_verify_constraints.py`
- `V5`：`uv run mypy src/ai_sdlc/core/frontend_evidence_models.py src/ai_sdlc/core/frontend_evidence_store.py src/ai_sdlc/core/frontend_evidence_loop.py src/ai_sdlc/core/loop_status.py src/ai_sdlc/cli/loop_cmd.py`
- `V6`：`git diff --check`
- `V7`：`uv run ai-sdlc verify constraints`
- `V8`：`uv run ai-sdlc program truth sync --execute --yes`
- `V9`：`uv run ai-sdlc workitem close-check --wi specs/195-loop-engine-frontend-evidence-loop-runtime`

#### 5.5 验证结果

- unit targeted：10 passed
- CLI integration：36 passed
- focused regression：233 passed
- ruff：PASS
- mypy：PASS，5 source files
- diff check：PASS
- verify constraints：PASS，no BLOCKERs

#### 5.6 代码审查结论（Mandatory）

- 宪章/规格对齐：符合；本批只修 frontend-evidence runtime trust boundary 和 CLI exit semantics，不扩展到模型调用、远端 PR 或 browser gate 重实现。
- 代码质量：failed/incomplete probe state 在 evidence ingestion 入口即 fail-closed；CLI exit code 与不可关闭状态保持一致。
- 测试质量：新增 runtime state 和 CLI exit 回归，并保持 focused suite 通过。
- 结论：可刷新 truth、close-check、提交、推送并重新请求 Codex review。

#### 5.7 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：T42 完成；本批为 PR #112 second Codex review remediation。
- `related_plan` 同步状态：不改变 WI-195 范围。
- 关联 branch/worktree disposition 计划：继续使用 PR #112 carrier branch。

#### 5.8 归档后动作

- 第二轮 Codex review P1 已修复；下一步 truth sync、close-check、提交、推送并重新请求 Codex review。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/frontend_evidence_loop.py`、`src/ai_sdlc/cli/loop_cmd.py`、`tests/unit/test_frontend_evidence_loop.py`、`tests/integration/test_cli_loop.py`、`program-manifest.yaml`、`specs/195-loop-engine-frontend-evidence-loop-runtime/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md`
- **已完成 git 提交**：是（本 marker 随 remediation commit 一起落盘）
- **提交哈希**：`HEAD`
- 当前批次 branch disposition 状态：提交后推送到 PR #112 并重新请求 Codex review
- 当前批次 worktree disposition 状态：提交后继续 PR #112 heartbeat
- 是否继续下一批：否；等待 PR #112 Codex review、required checks 与合并
