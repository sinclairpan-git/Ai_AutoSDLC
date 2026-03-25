# 001-ai-sdlc-framework 任务执行归档

> 本文件遵循 [`templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/001-ai-sdlc-framework/` 相关的实现任务，在本文件**末尾**追加新批次章节。
- 批次结束顺序：验证（pytest + ruff）→ 归档本文 → git commit（见 `pipeline.md` / `batch-protocol.md`）。

## 2. 批次记录

### Batch 2026-03-25-001 | Task 6.3–6.5（FR-087～FR-089）

#### 2.1 批次范围

- **覆盖任务**：Task **6.3** `workitem plan-check`；**6.4** checkpoint 关联元数据 + `status`；**6.5** `verify constraints`。
- **覆盖阶段**：EXECUTE（框架产品代码 + 测试 + 用户可见文档）。
- **预读范围**：`specs/001-ai-sdlc-framework/spec.md`（FR-087～089、SC-011～012）、`docs/plan-check-cli-spec.zh.md`、`src/ai_sdlc/rules/pipeline.md`（验证/归档条款）。
- **激活的规则**：`rules/verification.md`（门函数）、`rules/code-review.md`（commit 前自审）。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**509 passed**（2026-03-25，本机/CI 等价环境）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **Smoke（CLI）**
  - 命令：`uv run ai-sdlc workitem plan-check --help`、`uv run ai-sdlc workitem link --help`、`uv run ai-sdlc verify constraints --help`
  - 结果：退出码 0，`--help` 含只读/不写 checkpoint 或与 doctor 关系说明。

#### 2.3 任务记录

##### Task 6.3 | `workitem plan-check`（FR-087 / SC-011）

- **改动范围**：`src/ai_sdlc/core/plan_check.py`、`src/ai_sdlc/cli/workitem_cmd.py`（plan-check）、`src/ai_sdlc/cli/main.py`、`docs/plan-check-cli-spec.zh.md`。
- **新增/调整的测试**：`tests/unit/test_plan_check.py`、`tests/integration/test_cli_workitem_plan_check.py`。
- **是否符合任务目标**：是（AC：CLI、`--help`、漂移夹具非零、pytest + ruff）。

##### Task 6.4 | Checkpoint 关联 + `status`（FR-088）

- **改动范围**：`src/ai_sdlc/models/state.py`、`src/ai_sdlc/cli/workitem_cmd.py`（link）、`src/ai_sdlc/cli/commands.py`。
- **新增/调整的测试**：`tests/unit/test_checkpoint_fr088.py`、`tests/integration/test_cli_workitem_link.py`。
- **是否符合任务目标**：是（旧 checkpoint 可加载；写入经 YamlStore；status 展示有值字段；pytest + ruff）。

##### Task 6.5 | `verify constraints`（FR-089 / SC-012）

- **改动范围**：`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/verify_cmd.py`、`src/ai_sdlc/cli/main.py`。
- **新增/调整的测试**：`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`。
- **是否符合任务目标**：是（只读、BLOCKER、≥2 负例 + 1 正例、help 与 doctor 区分；pytest + ruff）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：实现范围限定于 FR-087～089；无改宪章。
- **安全/质量**：子命令只读路径明确；无随意写 checkpoint（plan-check / verify）；link 显式经 `save_checkpoint`。
- **测试**：覆盖 happy / 边界 / 用户错误（exit 2）路径；集成测试对 IDE hook 做 autouse mock，避免临时仓被写脏。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task **6.3～6.5** 已按 `tasks.md` AC 完成实现、测试与文档对齐；本批次可关闭。

#### 2.6 归档后动作

- **已完成 git 提交**：是（见下方哈希）。
- **提交哈希**：`db1425d260aab6465973ecc34248b1bc26541402`（主题含 `feat(cli): workitem plan-check/link, verify constraints (FR-087..089)`）
- **是否继续下一批**：按 `tasks.md` 进入 **Task 6.6**（可选文档）或 **Batch 8/9** 须**另开会话/PR**，本批次不自动启动未勾选任务。

### Batch 2026-03-25-002 | Task 6.1（T10 可移植性审计收口）

#### 2.1 批次范围

- **覆盖任务**：Task **6.1**（T10 可移植性审计与修订）——本批次仅做**审计表落盘 + 独立收口**，不新增框架行为实现。
- **覆盖阶段**：VERIFY / CLOSE（文档类收口）。
- **预读范围**：`specs/001-ai-sdlc-framework/tasks.md`（Task 6.1 验证条款）、`src/ai_sdlc/rules/pipeline.md`（归档/验证）、`src/ai_sdlc/rules/verification.md`、`src/ai_sdlc/rules/code-review.md`。
- **激活的规则**：完成前验证、归档先于继续、产出语言（中文）。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**509 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.1 | `portability-audit-T10.md`（审计表落盘）

- **改动范围**：`specs/001-ai-sdlc-framework/portability-audit-T10.md`
- **改动内容**：
  - 将 `docs/USER_GUIDE.zh-CN.md` 相关项状态从“已部分完成”收敛为“已关闭”（以仓库事实为准）。
  - 将“Task 6.1 验证条款”收敛为“完成（文档/规则范围）”，明确根目录 PRD 改版为延期项。
  - 追加 2026-03-25 收口记录（本批次归档 + 独立提交）。
- **新增/调整的测试**：无（文档变更，验证使用全量回归 + ruff）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（审计表可追溯、延期明确、收口证据落盘）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章对齐**：未引入新功能；仅落盘审计与证据；不越界。
- **规格对齐**：与 Task 6.1 验收描述一致（文档/规则范围收口；PRD 延期明确）。
- **技术规范/质量**：无代码逻辑变更；避免将 IDE 作为唯一路径的表述回流。
- **测试质量**：文档变更仍跑全量回归与 ruff（满足 `pipeline.md` 禁止项“无回归即提交”）。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.1 审计表已纳入仓库并完成独立收口，可进入后续 Task 6.6。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`9cef32d0c5df7b46806cf84755e64e52e019a63d`
- **是否继续下一批**：是（进入 Task 6.6；若策略选择跳过可在 tasks 中显式标注）。

### Batch 2026-03-25-003 | Task 6.6（pipeline 例外 vs Runner 对照表）

#### 2.1 批次范围

- **覆盖任务**：Task **6.6**（仅文档）：`pipeline`「已有产物」例外 vs Runner 对照表。
- **覆盖阶段**：DESIGN / VERIFY（文档对照与建议，不引入产品行为变更）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.6 条目）。
- **激活的规则**：归档先于继续、完成前必须验证、范围严控（MUST-1）、独立可回退（MUST-3）。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**通过**（见本批次提交前的终端输出）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**通过**。

#### 2.3 任务记录

##### Task 6.6 | 对照表文档

- **改动范围**：`specs/001-ai-sdlc-framework/adr-001-pipeline-vs-runner.md`
- **改动内容**：建立规则条文 vs 当前代码行为的对照表，指出“单独运行某 stage gate 可能绕过链式门禁”的风险，并把建议映射回 Batch 8/9 的后续实现任务。
- **新增/调整的测试**：无（文档变更）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（产物存在、可审阅、可追溯到后续 tasks）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章对齐**：未引入 P0 之外新功能；仅对照与建议，符合 MUST-1。
- **规格对齐**：与 Task 6.6 产物要求一致；不改变 Runner 行为（避免越界）。
- **测试质量**：文档变更仍执行全量回归与 ruff，满足验证协议。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.6 文档产物已落盘；可进入 Batch 8 的 Task 6.7（文档先行）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`3fa371abe636f9771dd18ca67d62dfe788252f4e`
- **是否继续下一批**：是

### Batch 2026-03-25-004 | Task 6.7（FR-090 / SC-014 文档契约）

#### 2.1 批次范围

- **覆盖任务**：Task **6.7**（仅文档）：在 `spec.md` 增补 FR-090 / SC-014；同步 `templates/tasks-template.md` 的任务块约束说明。
- **覆盖阶段**：DECOMPOSE（契约与门禁要求定义）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.7 AC）、`templates/tasks-template.md`。
- **激活的规则**：宪章（MUST-1/2/3）、完成前验证、归档先于继续。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**509 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.7 | FR-090 / SC-014 契约落盘

- **改动范围**：`specs/001-ai-sdlc-framework/spec.md`、`templates/tasks-template.md`
- **改动内容**：
  - 新增 **FR-090**：DECOMPOSE Gate 任务级可验收字段约束（验收标准/AC/验证）。
  - 新增 **SC-014**：缺字段夹具下 `gate check decompose` 非零并定位 Task 标识。
  - 模板补充「任务块必须包含可验收字段」说明，避免分解缺口。
- **新增/调整的测试**：无（本 Task 为文档契约；实现与测试在 Task 6.8）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（spec+模板一致，且为后续 gate 实现提供可测准则）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章对齐**：无新增实现，仅补齐契约；范围受控。
- **规格对齐**：与 tasks Batch 8 的 6.7 AC 一致。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.7 文档契约已完成，可进入 Task 6.8（实现 DecomposeGate）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`67f21289bcec4955297e39d63d62db0ce800ac3f`
- **是否继续下一批**：是

### Batch 2026-03-25-005 | Task 6.8（DecomposeGate 任务级可验收校验）

#### 2.1 批次范围

- **覆盖任务**：Task **6.8**：实现 `DecomposeGate` 任务级 AC/验证字段校验（FR-090 / SC-014）。
- **覆盖阶段**：DECOMPOSE Gate（质量门禁增强）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`specs/001-ai-sdlc-framework/spec.md`（FR-090/SC-014）、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.8 AC）。
- **激活的规则**：TDD（先红后绿）、完成前验证、归档先于继续。

#### 2.2 统一验证命令

- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_gates.py::TestDecomposeGate -v`
  - 结果：通过（RED→GREEN：缺验收字段时 gate RETRY）。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**510 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.8 | `DecomposeGate` 校验实现

- **改动范围**：`src/ai_sdlc/gates/pipeline_gates.py`、`tests/unit/test_gates.py`
- **改动内容**：对 `tasks.md` 按 `### Task` 分段，检查每段是否包含「验收标准 / AC / 验证」任一标记；缺失时 gate RETRY 并指出首个不合规 Task id。
- **新增/调整的测试**：扩展 `TestDecomposeGate` 覆盖通过与缺失验收字段的失败路径。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC：分段校验、失败定位、pytest+ruff）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：仅增强门禁；不引入额外行为；FR-090 定义的关键字集合可追溯。
- **代码质量**：解析逻辑局部封装；失败信息可定位首个 Task。
- **测试质量**：覆盖 happy path + 缺失字段错误路径；避免对全仓副作用。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.8 已完成；下一步进入 Task 6.9（ExecuteGate 前置只读检查）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`d4f5673164e6d190bc7700ddd84e0427bb2f49b7`
- **是否继续下一批**：是

### Batch 2026-03-25-006 | Task 6.9（ExecuteGate 前置只读检查）

#### 2.1 批次范围

- **覆盖任务**：Task **6.9**：`ExecuteGate` 增加对 decompose 前置条件的只读检查（防单独 `gate check execute` 绕过）。
- **覆盖阶段**：EXECUTE Gate（前置约束增强）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.9 AC）。
- **激活的规则**：TDD、完成前验证、归档先于继续。

#### 2.2 统一验证命令

- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_gates.py::TestExecuteGate -v`
  - 结果：通过（新增 2 个前置检查场景）。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**512 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.9 | `ExecuteGate` 前置检查

- **改动范围**：`src/ai_sdlc/gates/pipeline_gates.py`、`tests/unit/test_gates.py`
- **改动内容**：当 context 提供 `spec_dir` 时，`ExecuteGate` 先检查 `tasks.md` 是否存在且通过 FR-090 任务级可验收校验；不满足则 `decompose_prerequisite` 失败并使 gate RETRY。
- **新增/调整的测试**：`TestExecuteGate` 新增“缺验收字段失败”和“验收满足通过”场景。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC：不再允许 execute 在分解未就绪时 PASS）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：实现限定在 Task 6.9 范围；不改 spec/plan 语义。
- **代码质量**：前置检查复用 FR-090 辅助函数；失败信息可定位。
- **测试质量**：新增负面+正面场景，并保留原 execute 行为回归。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.9 已完成；可进入 Task 6.10（可选）或直接转 Batch 9 的 Task 6.11。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`74364f2c7cdac87ccc89077f2cb013481ffd6931`
- **是否继续下一批**：是

### Batch 2026-03-25-007 | Task 6.10（共用 task AC 校验 + verify constraints 对齐 SC-014）

#### 2.1 批次范围

- **覆盖任务**：Task **6.10**（可选）：`task_ac_checks` 共用模块；`collect_constraint_blockers` 在存在 `tasks.md` 时与 **SC-014** / `DecomposeGate` 同规则。
- **覆盖阶段**：EXECUTE（门禁与只读校验一致性）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.10 AC）。
- **激活的规则**：完成前验证、归档先于继续、MUST-2 测试覆盖。

#### 2.2 统一验证命令

- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_task_ac_checks.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**519 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.10 | 共用校验 + `verify constraints`

- **改动范围**：`src/ai_sdlc/gates/task_ac_checks.py`（新）、`src/ai_sdlc/gates/pipeline_gates.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/cli/verify_cmd.py`。
- **改动内容**：抽取 `first_task_missing_acceptance`；`DecomposeGate` / `ExecuteGate` 经共用模块调用；`verify constraints` 在 `feature.spec_dir/tasks.md` 存在时缺任务级 AC 则 **BLOCKER**；CLI `--help` 补充 SC-014 说明。
- **新增/调整的测试**：`tests/unit/test_task_ac_checks.py`；`tests/unit/test_verify_constraints.py`；`tests/integration/test_cli_verify_constraints.py`。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC：共用函数 pytest 覆盖；verify 与 gate decompose 规则一致）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：范围限定 Task 6.10；与 FR-089 / SC-014 一致。
- **代码质量**：单一路径解析任务块，避免 gate 与 verify 双份规则。
- **测试质量**：单元 + 集成负例覆盖 BLOCKER。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.10 已完成；可按 `tasks.md` 进入 **Batch 9 / Task 6.11**。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`fdeb7460b47859943908e345295afb341e488bad`
- **是否继续下一批**：是

### Batch 2026-03-25-008 | Task 6.11（规格与模板：收口约束契约落盘）

#### 2.1 批次范围

- **覆盖任务**：Task **6.11**（仅文档）：spec / execution-log 模板 / PR 清单术语与收口字段对齐。
- **覆盖阶段**：EXECUTE（文档契约先行）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.11 AC）。
- **激活的规则**：MUST-2/3/4/5、归档先于继续、完成前验证。

#### 2.2 统一验证命令

- **V1（本任务相关审阅）**
  - 命令：人工审阅 `spec.md` / `templates/execution-log-template.md` / `docs/pull-request-checklist.zh.md` 术语一致性。
  - 结果：一致（`close-check`、`BLOCKER`、`related_plan` 统一）。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**519 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.11 | 规格与模板收口契约

- **改动范围**：`specs/001-ai-sdlc-framework/spec.md`、`templates/execution-log-template.md`、`docs/pull-request-checklist.zh.md`。
- **改动内容**：
  - `spec.md` 增补 FR-091～094 术语约束说明（`close-check` / `BLOCKER` / `related_plan` 一致）。
  - execution-log 模板新增 mandatory 字段：「代码审查结论」「任务/计划同步状态」，并调整章节顺序。
  - PR 清单新增“最小验证集”分流：文档变更 vs 代码变更，两类分别给出最低验证命令与 `BLOCKER` 约束。
- **新增/调整的测试**：无（文档任务）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC：术语一致；无“命令已实现但文档仍标未实现”矛盾）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：仅文档契约，不扩大产品行为范围。
- **代码质量**：无运行时代码修改。
- **测试质量**：执行全量回归与 lint 作为完成证据。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.11 已完成；可进入 Task 6.12（`workitem close-check` 只读实现）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`d38c7cc65e3eebb01bb441d8fa87c5526267fd41`
- **是否继续下一批**：是

### Batch 2026-03-25-009 | Task 6.12（实现 `ai-sdlc workitem close-check`）

#### 2.1 批次范围

- **覆盖任务**：Task **6.12**：新增只读 `workitem close-check` 与核心聚合检查器。
- **覆盖阶段**：EXECUTE（收口检查实现）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.12 AC）。
- **激活的规则**：TDD（先红后绿）、完成前验证、归档先于继续、代码审查。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：初次失败（`ModuleNotFoundError: ai_sdlc.core.close_check`），证明新行为测试先红。
- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：**7 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**526 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：先发现 `I001` 导入排序；修复后 **All checks passed!**。
- **Smoke（CLI）**
  - 命令：`uv run ai-sdlc workitem close-check --help`
  - 结果：退出码 0，明确 `Read-only`、close-stage 语义与 `--wi/--json`。

#### 2.3 任务记录

##### Task 6.12 | `workitem close-check`（FR-091 / SC-017）

- **改动范围**：`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/cli/workitem_cmd.py`、`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`。
- **改动内容**：
  - 新增只读核心：检查 `tasks.md` 完成度、`related_plan` 漂移（复用 `plan_check`）、`task-execution-log.md` 关键字段完整性；
  - CLI 新增 `ai-sdlc workitem close-check --wi ... [--json]`，机器可读输出包含 `ok/blockers/checks`；
  - 保持默认不写 checkpoint，不修改仓库状态文件。
- **新增/调整的测试**：单元 3 条（2 负面 + 1 正向），集成 4 条（退出码、JSON 字段、help 文案）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC1～AC4 达成）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：仅实现 FR-091 / SC-017 范围；命令为只读。
- **技术规范一致性**：复用现有 `plan_check` 解析与 drift 规则；CLI 保持统一 JSON/退出码习惯。
- **代码质量**：检查项结构化输出，失败原因可定位；无副作用写操作。
- **测试质量**：覆盖 tasks 未完成、related_plan 漂移、全绿路径与 JSON/help。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.12 已完成；下一步可进入 Task 6.13（文档一致性漂移防回归）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`b082c13018d4d59b094f83df492447cfaabbd0ab`
- **是否继续下一批**：是

### Batch 2026-03-25-010 | Task 6.13（文档一致性漂移防回归）

#### 2.1 批次范围

- **覆盖任务**：Task **6.13**：在 `workitem close-check` 增加 docs 一致性子检查。
- **覆盖阶段**：EXECUTE（close-check 规则增强）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.13 AC）。
- **激活的规则**：TDD（先红后绿）、完成前验证、归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：新增 docs 漂移用例先失败（2 failed），证明功能未实现前测试可捕获。
- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：**10 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**529 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.13 | docs 一致性检查（FR-091 / FR-093 / SC-019）

- **改动范围**：`src/ai_sdlc/core/close_check.py`、`tests/unit/test_close_check.py`、`tests/integration/test_cli_workitem_close_check.py`。
- **改动内容**：
  - close-check 新增 `docs_consistency` 子检查：当 `docs/**/*.md` 同时出现“未实现前/未来可能提供”与已注册命令（`ai-sdlc workitem plan-check`、`ai-sdlc verify constraints`）时输出 BLOCKER。
  - 补充正反夹具：覆盖 `plan-check` 与 `verify constraints` 两条命令，且修正文案后可通过。
- **新增/调整的测试**：unit 新增 2 条（负面+正面）；integration 新增 1 条负面。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC1/AC2/AC3 达成）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：仅增强 close-check 只读规则，未引入额外写操作。
- **代码质量**：规则集中于 `close_check.py`，输出 `checks + blockers` 可追踪。
- **测试质量**：先红后绿，覆盖两个指定命令与修复后通过路径。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.13 已完成；下一步可进入 Task 6.14（偏离登记产品化闭环）。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`71d801e4a2febb0ca896d6367805c22a269f011d`
- **是否继续下一批**：是

### Batch 2026-03-25-011 | Task 6.14（偏离登记产品化闭环）

#### 2.1 批次范围

- **覆盖任务**：Task **6.14**：在只读约束检查中加入 skip-registry 到 spec/tasks 的最小映射校验。
- **覆盖阶段**：EXECUTE（verify constraints 规则增强）。
- **预读范围**：`.ai-sdlc/memory/constitution.md`、`src/ai_sdlc/rules/pipeline.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/tasks.md`（Task 6.14 AC）、`src/ai_sdlc/rules/agent-skip-registry.zh.md`。
- **激活的规则**：TDD（先红后绿）、完成前验证、归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：新增「仅登记未映射」用例先失败（2 failed）。
- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：**12 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**532 passed**（2026-03-25）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.14 | skip-registry 映射校验（FR-094 / SC-017 延伸）

- **改动范围**：`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`。
- **改动内容**：
  - `verify constraints` 新增 `_skip_registry_mapping_blockers`：解析 `agent-skip-registry.zh.md` 中 `FR-xxx` 与 `Task x.y` 引用；
  - 最小映射规则：`FR` 必须可在当前 `spec.md` 或 `tasks.md` 找到，`Task` 必须可在当前 `tasks.md` 找到；
  - 未映射时返回 `BLOCKER: skip-registry ... unmapped references ...`。
- **新增/调整的测试**：
  - unit：1 个负面（`FR-999`/`Task 9.9` 未落 spec/tasks）+ 1 个正面（`FR-001`/`Task 1.1` 已映射）；
  - integration：1 个负面（CLI 非零并包含 `skip-registry`）。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合（AC1/AC2 达成）。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：仅增强只读约束检查，未引入写路径。
- **代码质量**：映射规则最小且可解释；未映射明细可定位到 FR/Task 号。
- **测试质量**：覆盖负面与正向夹具，含 CLI 层退出码行为。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Task 6.14 已完成；Batch 9（6.11～6.14）实现项收口完成。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`1f1b3667c9809752005ebbe0ab22b1ba9db6dbae`
- **是否继续下一批**：是

### Batch 2026-03-25-012 | Task 6.16–6.19（FR-095～FR-098 / SC-020～SC-023）

#### 2.1 批次范围

- **覆盖任务**：Task **6.16**（skip-registry `wi_id` 作用域）、**6.17**（close-check 默认 WI+白名单与 `--all-docs`）、**6.18**（归档/批次协议哈希策略）、**6.19**（Typer 枚举命令）。
- **覆盖阶段**：EXECUTE（verify + close-check + 文档契约）。
- **预读范围**：`specs/001-ai-sdlc-framework/tasks.md`（Batch 10）、`spec.md`（FR-095～098）、`agent-skip-registry.zh.md`、`batch-protocol.md`、`execution-log-template.md`。
- **激活的规则**：TDD（先红后绿）、完成前验证、归档与单次提交语义（FR-097）。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_workitem_close_check.py -q`（迭代中按需收窄）。
  - 结果：新增/调整用例先失败再随实现转绿。
- **V1（定向）**
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_command_names.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：**33 passed**（定向套件）。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**543 passed**（2026-03-25，实现完成后）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.16 | skip-registry 按 `wi_id` 过滤（FR-095 / SC-020）

- **改动范围**：`src/ai_sdlc/core/verify_constraints.py`、`tests/unit/test_verify_constraints.py`、`tests/integration/test_cli_verify_constraints.py`。
- **改动内容**：解析登记表中含 **`wi_id`** 列的 Markdown 表；仅当行内 `wi_id` 与 checkpoint 的 `linked_wi_id`（若设）或 `feature.spec_dir` 目录名一致时，才对该行提取 `FR-xxx` / `Task x.y` 做 spec/tasks 映射校验；空 `wi_id` 历史行不参与 BLOCKER。
- **新增/调整的测试**：SC-020 混合夹具（仅当前 WI 行触发）、`linked_wi_id` 优先于目录名。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合。

##### Task 6.17 | close-check 文档范围 + `--all-docs`（FR-096 / SC-021）

- **改动范围**：`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/cli/workitem_cmd.py`、close-check 相关单测与集成测。
- **改动内容**：默认扫描 `specs/<WI>/*.md` 与 `docs/pull-request-checklist.zh.md`、`docs/USER_GUIDE.zh-CN.md`；`--all-docs` 恢复全 `docs/**/*.md` 扫描。
- **新增/调整的测试**：默认忽略深层 `docs/nested` 违规；`--all-docs` 捕获；`--help` 展示开关。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合。

##### Task 6.18 | 归档与批次协议降噪（FR-097 / SC-022）

- **改动范围**：`templates/execution-log-template.md`、`src/ai_sdlc/rules/batch-protocol.md`、`specs/001-ai-sdlc-framework/spec.md`（FR-097 锁死表述）。
- **改动内容**：对齐「默认单次提交 + 哈希于 commit 后填一次 / 可用 `git commit --amend`」策略，消除双提交噪音说明。
- **新增/调整的测试**：无（文档）；全量 pytest/ruff 回归。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合。

##### Task 6.19 | 命令列表从 Typer 枚举（FR-098 / SC-023）

- **改动范围**：新增 `src/ai_sdlc/cli/command_names.py`；`close_check` 移除硬编码命令元组，运行时枚举 CLI。
- **改动内容**：`collect_flat_command_strings()` 遍历 `Typer`/`Click` 组；docs 一致性使用全量叶子命令路径。
- **新增/调整的测试**：`tests/unit/test_command_names.py`；monkeypatch 证明列表非冻结双字符串。
- **执行的命令**：见统一验证命令。
- **测试结果**：见统一验证命令。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（`rules/code-review.md` 摘要）

- **宪章/规格对齐**：实现与 FR-095～098、SC-020～023 一致；`verify` 与 `close-check` 仍为只读。
- **代码质量**：`verify_constraints` 表解析与 wi 作用域集中；`command_names` 懒加载避免 import 环。
- **测试质量**：TDD 顺序；覆盖 wi_id、白名单、`--all-docs`、Typer 枚举与 monkeypatch。
- **结论**：无 Critical 阻塞项。

#### 2.5 批次结论

- Batch 10 实现项 **6.16～6.19** 已完成；`close-check` / `verify constraints` 作用域与真值来源已按契约收敛。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：（本批 `feat(sdlc): Batch 10 Tasks 6.16–6.19` 合并提交；完整 SHA 以 `git rev-parse HEAD` 为准）
- **是否继续下一批**：是

### Batch 2026-03-25-013 | Task 6.6 / 6.10 可选收口 + T10 PRD + 登记表 WIP

#### 2.1 批次范围

- **覆盖任务**：Task **6.6**（`pipeline` vs Runner 对照文档）、Task **6.10**（共用 `task_ac_checks` 与 SC-014 — 代码已存在，本批补 **tasks 收口与证据指认**）、T10 审计表 **根目录 PRD** 延期行关闭、`agent-skip-registry` **WIP → 已关闭**。
- **覆盖阶段**：文档 / 契约收口（无新产品 Python 行为变更）。
- **预读范围**：`tasks.md` Task 6.6/6.10、`portability-audit-T10.md`、`pipeline.md`、`runner.py`、`task_ac_checks.py`。
- **激活的规则**：契约先于声称完成；归档先于继续。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**543 passed**（2026-03-25）
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.6 | pipeline vs Runner 对照表

- **改动范围**：新增 [`research-pipeline-vs-runner.md`](research-pipeline-vs-runner.md)；`tasks.md` 收口块。
- **改动内容**：规则条文与 Runner/Gate 行为对照；明确「已有产物例外」由 checkpoint 体现、非文件自动跳阶段。
- **是否符合任务目标**：符合。

##### Task 6.10 | 共用校验模块（确认收口）

- **改动范围**：`tasks.md` 收口块 + 可选进度勾选（实现已在先：`task_ac_checks.py`、pipeline_gates、verify_constraints、单测）。
- **是否符合任务目标**：符合（AC 追溯完成）。

##### T10 PRD + 登记表

- **改动范围**：根目录 PRD §12.3；`portability-audit-T10.md`；`agent-skip-registry.zh.md` 一行状态；`src/ai_sdlc/rules/pipeline.md` 与 `rules/pipeline.md` 增补与 Runner 对齐说明（与 Task 6.6 互链）。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- 无应用代码语义变更；文档与审计表与 T10 / FR 可移植性表述一致。

#### 2.5 批次结论

- 所列可选/延期/登记项已按框架约束 **落盘关闭**，避免口头「已做」无指针。

#### 2.6 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：（本批 `docs` 收口提交；完整 SHA 以 `git rev-parse HEAD` 为准）
- **是否继续下一批**：是
