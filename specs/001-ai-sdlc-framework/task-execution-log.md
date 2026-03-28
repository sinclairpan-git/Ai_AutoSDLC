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
  - 结果：新增 docs 漂移用例先失败（2 failed），证明 TDD 红阶段（功能尚未落地时）测试可捕获。
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
  - close-check 新增 `docs_consistency` 子检查：当 `docs/**/*.md` 同时出现 **SC-019** 漂移关键字（与 `close_check.DOCS_UNIMPLEMENTED_HINTS` 一致）与已注册命令（如 `ai-sdlc` `workitem` `plan-check`、`ai-sdlc` `verify` `constraints`）时输出 BLOCKER。
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

### Batch 2026-03-25-014 | 本地 `project-config.yaml` 不入库 + 示例/默认加载/测

#### 2.1 批次范围

- **覆盖内容**：`.gitignore` 忽略 `.ai-sdlc/project/config/project-config.yaml`；`git rm --cached` 停止跟踪；新增 `project-config.example.yaml`；`load_project_config` / `ProjectConfig` 文档与默认路径行为；`tests/unit/test_project_config.py`；USER_GUIDE / README / `init.yaml` 等与本地配置策略对齐。
- **覆盖阶段**：配置契约 + 可复现交付（避免「每人一份脏 yaml」污染 `git status`）。
- **预读范围**：`tasks.md`（若后续补链）、`data-model.md`、`USER_GUIDE.zh-CN.md` 初始化节。
- **激活的规则**：契约先于声称完成；本地密钥/路径类配置不入库。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**546 passed**（2026-03-25，归档前本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **Build**
  - 命令：`uv build`
  - 结果：**成功**（`ai_sdlc-0.2.3` sdist + wheel）。
- **离线包（可选、联网、与目标机同 OS/CPU 推荐）**
  - 命令：`./packaging/offline/build_offline_bundle.sh`
  - 结果：**成功**（`dist-offline/ai-sdlc-offline-0.2.3.tar.gz` 与 `.zip`；产物目录已 `.gitignore`）。

#### 2.3 任务记录

##### 配置策略 | `project-config` 不入库

- **改动范围**：`.gitignore`、`project-config.example.yaml`、`src/ai_sdlc/...` 加载与模型文档、单测、用户文档与初始化模板。
- **是否符合任务目标**：符合（克隆后无强制提交本地 `project-config.yaml`；示例与默认路径可重建）。

#### 2.4 代码审查（摘要）

- 无扩大写盘攻击面；默认加载路径与忽略规则一致；测试覆盖示例与默认行为。

#### 2.5 批次结论

- 本地配置与可复现交付边界已落盘；可与 **main 作为集成分支** 文档（`4b3f938` 等）一并作为发布前卫生检查依据。

#### 2.6 归档后动作

- **已完成 git 提交**：是（配置策略主提交）
- **提交哈希**：`ad7e3c79d7ba9b6259006fcf15bb36eb9006430c`（`feat(config): gitignore project-config.yaml; example + default load + tests`）
- **是否继续下一批**：按需（版本号 bump / PyPI / 对外发布公告）

### Batch 2026-03-26-015 | 版本 0.2.4 打包与升级（对齐 pyproject / 用户指南 / 离线包）

#### 2.1 批次范围

- **覆盖内容**：`pyproject.toml` / `uv.lock` 版本 **0.2.3 → 0.2.4**；`src/ai_sdlc/__init__.py` 中 `__version__` 改为 **安装态** `importlib.metadata.version("ai-sdlc")`，无分发元数据时回退 **0.2.4**；`docs/USER_GUIDE.zh-CN.md` 中 GitHub 标签与离线包示例路径与 **0.2.4** 一致；按 `packaging/offline/README.md` 执行离线包构建。
- **覆盖阶段**：发布卫生检查（与 Batch 014 同一套：测试 + Lint + Build + 可选离线包）。
- **预读范围**：`packaging/offline/build_offline_bundle.sh`、`docs/USER_GUIDE.zh-CN.md` §3 / §12。

#### 2.2 统一验证命令

- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**546 passed**（2026-03-26，本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **Build**
  - 命令：`uv build`
  - 结果：**成功**（`ai_sdlc-0.2.4` sdist + wheel）。
- **离线包（可选、联网、与目标机同 OS/CPU 推荐）**
  - 命令：`./packaging/offline/build_offline_bundle.sh`
  - 结果：**成功**（`dist-offline/ai-sdlc-offline-0.2.4.tar.gz` 与 `.zip`；产物目录已 `.gitignore`）。
- **治理只读约束**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。
- **`__version__` 冒烟**
  - 命令：`uv run python -c "from ai_sdlc import __version__; assert __version__ == '0.2.4'"`
  - 结果：**通过**。

#### 2.3 任务记录

##### 版本与文档 | 0.2.4

- **改动范围**：`pyproject.toml`、`uv.lock`、`src/ai_sdlc/__init__.py`、`docs/USER_GUIDE.zh-CN.md`（安装示例中的标签与离线目录名）。
- **是否符合任务目标**：符合（单一发布版本号；安装文档与 wheel/离线包名一致；`__version__` 与已安装包版本一致）。

#### 2.4 代码审查（摘要）

- 无新增运行时依赖；`PackageNotFoundError` 回退与可编辑/源码直跑场景兼容。

#### 2.5 批次结论

- **0.2.4** 已完成：sdist/wheel、离线 `tar.gz` / `zip`（本机构建为 **macOS arm64 + cp311** 依赖 wheel 集；Windows 目标机需在同平台重建离线包）。
- **标签与文档**：`v0.2.4` 已推送至 `origin`（见 2.6）；`USER_GUIDE` 中基于标签的安装示例已与该指针对齐。

#### 2.6 归档后动作

- **已完成 git 提交**：是（已推送 `origin/main`）
- **提交哈希**：`218bc79f45c8090764c9d823f65372b2564fa5cf`（`chore(release): bump ai-sdlc to 0.2.4`）
- **远端标签**：`v0.2.4` 已推送至 `origin`
- **是否继续下一批**：按需（PyPI 发布、对外公告；非本仓库强制门）

### Batch 2026-03-27-016 | 框架收口：Telemetry lint 清零 + 开放问题收敛 + Task 6.15 指针补齐

#### 2.1 批次范围

- **覆盖内容**：清理 telemetry / CLI / tests 的 `ruff` 遗留问题；收敛 [`plan.md`](plan.md) 中两个仍标记为“待定”的开放问题；在 [`tasks.md`](tasks.md) 为 **Task 6.15** 增补显式收口说明。
- **覆盖阶段**：VERIFY / CLOSE（工程卫生 + 规格/计划文档收口）。
- **预读范围**：`src/ai_sdlc/rules/batch-protocol.md`、`templates/execution-log-template.md`、`specs/001-ai-sdlc-framework/plan.md`、`specs/001-ai-sdlc-framework/tasks.md`。
- **激活的规则**：完成前验证、代码自审、单次提交语义（FR-097 / SC-022）。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：无（本批为工程卫生与文档收口，未新增行为）。
  - 结果：不适用。
- **V1（定向）**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**691 passed**（2026-03-27）。
- **只读治理校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。
- **Close 收口校验**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`
  - 结果：`tasks_completion` / `related_plan_drift` / `execution_log_fields` / `docs_consistency` **全部 PASS**。

#### 2.3 任务记录

##### 收口项 A | Telemetry / CLI / tests lint 清零

- **改动范围**：`src/ai_sdlc/cli/main.py`、`src/ai_sdlc/cli/verify_cmd.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/telemetry/*.py`、`tests/unit/test_runner_confirm.py`、`tests/unit/test_telemetry_*.py`、`tests/unit/test_verify_constraints.py`。
- **改动内容**：通过 `ruff --fix` 与少量手工修正，完成 import 排序、`typing` / `collections.abc` 迁移、annotation 简化、条件表达式收敛等清理，不改变既有行为语义。
- **新增/调整的测试**：无新增测试；保留并通过现有 telemetry / verify / runner 回归测试。
- **执行的命令**：`uv run ruff check src tests --fix`、`uv run ruff check src tests`、`uv run pytest -q`。
- **测试结果**：lint 全绿；全量 pytest 通过。
- **是否符合任务目标**：符合。

##### 收口项 B | `plan.md` 开放问题收敛

- **改动范围**：`specs/001-ai-sdlc-framework/plan.md`
- **改动内容**：将 “Rich 面板在 CI 环境的降级策略” 与 “产品内置规则文件的初始内容” 从“待定”收敛为仓库事实：前者以 TTY / `--json` / 只读运维面边界为准，后者以内置 `src/ai_sdlc/rules/*.md` 与阶段激活映射为准。
- **新增/调整的测试**：无；证据来自现有 CLI/doctor/status 边界与规则加载实现。
- **执行的命令**：`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`
- **测试结果**：无 BLOCKER；close-check 全 PASS。
- **是否符合任务目标**：符合。

##### 收口项 C | Task 6.15 证据链补齐

- **改动范围**：`specs/001-ai-sdlc-framework/tasks.md`
- **改动内容**：在 **Task 6.15** 下追加“收口说明”，将 `spec.md`、`plan.md`、`agent-skip-registry.zh.md` 三处文档契约与 Batch 10 实现收口建立显式指针，消除“无独立 batch 归档是否算已落地”的歧义。
- **新增/调整的测试**：无（文档收口）。
- **执行的命令**：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`
- **测试结果**：`execution_log_fields` 与 `docs_consistency` 通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **宪章/规格对齐**：本批不扩大需求范围；仅对现有 telemetry/规则/计划文档做工程卫生与证据链收口，符合 MUST-2/3/4。
- **代码质量**：lint 修复限定于格式、导入、typing 与等价逻辑收敛；未引入新的写盘路径或行为分叉。
- **测试质量**：以全量 pytest、lint、`verify constraints`、`close-check` 作为新鲜证据；无“只改代码不验”的漂移。
- **Spec 偏移**：无新增偏移；Task 6.15 的文档前置条件已显式补齐为仓库真值。
- **结论**：无 Critical 阻塞项。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task 6.15 收口说明已落盘；无未勾选 checklist 项）。
- `related_plan`（如存在）同步状态：`已对账`（当前工作项未声明 `related_plan`，close-check 按约定跳过）。
- 说明：本批提交仅纳入“框架收口”直接相关文件；现有 `docs/USER_GUIDE.zh-CN.md` 与新增框架补充文档草稿不并入本批，避免误提交未收口的用户态文档改动。

#### 2.6 自动决策记录（如有）

- AD-001：将 `docs/USER_GUIDE.zh-CN.md` 与未跟踪的框架补充文档排除出本批提交 → 来源：当前工作树已有独立文档改动，且本批 close-check / execution-log 目标不依赖其入库 → 理由：避免把未完成或未核对链接关系的用户文档改动混入本次框架收口提交。

#### 2.7 批次结论

- 本批已完成框架要求的收口动作：lint 清零、开放问题收敛、Task 6.15 证据链补齐、只读约束与 close-check 复验通过；可进入单次提交。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交为 `chore: close framework follow-up and telemetry lint debt`；完整 SHA 以该提交后的 `HEAD` 为准。
- **是否继续下一批**：按需

### Batch 2026-03-27-017 | 框架文档收口：自迭代开发指南接入用户手册

#### 2.1 批次范围

- **覆盖内容**：将框架自迭代开发指南纳入仓库文档；在 [`docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md) 增加入口；新增 [`docs/框架自迭代开发与发布约定.md`](../../docs/框架自迭代开发与发布约定.md)。
- **覆盖阶段**：CLOSE（文档补充与用户入口收敛）。
- **预读范围**：`src/ai_sdlc/rules/batch-protocol.md`、`templates/execution-log-template.md`、`docs/USER_GUIDE.zh-CN.md`、`docs/framework-defect-backlog.zh-CN.md`。
- **激活的规则**：完成前验证、代码自审、文档变更最小验证集。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：无（文档批次，无行为实现）。
  - 结果：不适用。
- **V1（定向）**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。
- **V2（收口校验）**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
  - 结果：`tasks_completion` / `related_plan_drift` / `execution_log_fields` / `docs_consistency` **全部 PASS**。

#### 2.3 任务记录

##### 文档入口 | 用户手册补充

- **改动范围**：`docs/USER_GUIDE.zh-CN.md`
- **改动内容**：在 telemetry 运维边界章节后新增“框架自身开发补充”入口，明确框架仓库内自迭代开发应跳转到独立指南；链接收敛为仓库实际文件名。
- **新增/调整的测试**：无（文档变更）。
- **执行的命令**：`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
- **测试结果**：无 BLOCKER；all-docs close-check 全 PASS。
- **是否符合任务目标**：符合。

##### 新增文档 | 框架自迭代开发与发布约定

- **改动范围**：`docs/框架自迭代开发与发布约定.md`
- **改动内容**：补充框架仓库内自迭代开发的真值来源、`uv run ai-sdlc ...` 用法、push / merge / pull / release 语义边界，以及 trace / backlog / 回归测试闭环的操作说明。
- **新增/调整的测试**：无（文档变更）。
- **执行的命令**：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
- **测试结果**：`docs_consistency` PASS。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **宪章/规格对齐**：仅补充文档入口与开发约定，不扩大产品能力范围；与现有只读运维面、trace/backlog 流程一致。
- **代码质量**：无运行时代码改动。
- **测试质量**：按文档变更最小验证集执行 `verify constraints` 与 `close-check --all-docs`，覆盖用户手册与新增文档路径。
- **Spec 偏移**：无；新增文档为框架自迭代操作说明，不改变 `spec.md` 契约。
- **结论**：无 Critical 阻塞项。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`无需变更`（本批不对应新的执行任务拆分）。
- `related_plan`（如存在）同步状态：`已对账`（当前工作项未声明 `related_plan`，按约定跳过）。
- 说明：本批仅收口文档与入口链接，沿用 `001-ai-sdlc-framework` 的 close-check 作为仓库级文档一致性守卫。

#### 2.6 自动决策记录（如有）

- AD-001：保留新增文档的中文文件名，并将 `USER_GUIDE` 链接收敛到实际仓库路径 → 来源：仓库现有 docs 已同时使用中英文文件名，且当前新增文档已以中文文件名存在 → 理由：避免无意义重命名带来的额外提交噪音，同时消除用户手册中的断链。

#### 2.7 批次结论

- 文档入口与自迭代说明已落盘；用户可从 `USER_GUIDE` 直接跳转到框架仓库的开发/发布操作约定，且全仓 docs 一致性校验通过。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交为 `docs: add framework self-iteration guide`；完整 SHA 以该提交后的 `HEAD` 为准。
- **是否继续下一批**：按需

### Batch 2026-03-28-018 | 001 remediation 收尾：Batch 12 对账清零 + FR-034 最终闭环

#### 2.1 批次范围

- **覆盖内容**：完成 Batch 12（Task **6.27～6.31**）剩余接口漂移清理，并补齐 Task **6.22 / FR-034** 的“统一裸写入口硬拦截”遗留缺口；同步回填 [`implementation-drift-matrix.md`](implementation-drift-matrix.md)、[`tasks.md`](tasks.md)、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 与本归档。
- **覆盖阶段**：EXECUTE / VERIFY / CLOSE（合同实现收尾 + 文档/台账对账）。
- **预读范围**：[`plan.md`](plan.md) remediation 设计节、[`tasks.md`](tasks.md) Batch 11 / 12、[`implementation-drift-matrix.md`](implementation-drift-matrix.md)、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) 中 **FD-2026-03-27-014**。
- **激活的规则**：合同先于实现；测试先于修复；完成前验证；归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest -q tests/unit/test_file_guard.py tests/unit/test_branch_manager.py`
  - 结果：在补丁前新增的 raw write / `open(..., 'w')` / `replace()` 保护断言 **5 failed**，确认 `FR-034` 当时仍为 `partial`。
- **V1（定向）**
  - 命令：`uv run pytest -q tests/unit/test_prd_studio.py tests/unit/test_branch_manager.py tests/unit/test_gates.py tests/integration/test_cli_index_gate.py tests/flow/test_docs_dev_flow.py tests/flow/test_new_requirement_flow.py tests/integration/test_cli_verify_constraints.py tests/unit/test_business_rules.py`
  - 结果：**111 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**721 passed**（2026-03-28，本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。
- **Close 收口校验**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`、`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
  - 结果：`tasks_completion` / `related_plan_drift` / `execution_log_fields` / `docs_consistency` **全部 PASS**。

#### 2.3 任务记录

##### Task 6.27 | PRD Studio 接口与结构化摘要合同

- **改动范围**：`src/ai_sdlc/studios/prd_studio.py`、`tests/unit/test_prd_studio.py`、`tests/flow/test_new_requirement_flow.py`
- **改动内容**：对齐 `PrdStudio.review(prd_content)` / `review_path()` 合同与 `structured_output` 输出；保留 `check_prd_readiness(prd_path)` 兼容入口；同步将 new requirement flow 的 PRD 夹具升级到 Batch 12 要求的 canonical sections。
- **新增/调整的测试**：`tests/unit/test_prd_studio.py` 补 path/content 两条入口与结构化摘要断言；`tests/flow/test_new_requirement_flow.py` 改用完整 PRD 样例并继续验证状态持久化链条。
- **执行的命令**：见 V1 / V2。
- **测试结果**：定向与全量回归均通过。
- **是否符合任务目标**：符合。

##### Task 6.28 + Task 6.22 residual | docs branch / baseline 合同与 `FR-034` 最终闭环

- **改动范围**：`src/ai_sdlc/branch/branch_manager.py`、`src/ai_sdlc/branch/file_guard.py`、`tests/unit/test_branch_manager.py`、`tests/unit/test_file_guard.py`、`tests/flow/test_docs_dev_flow.py`、`tests/unit/test_business_rules.py`
- **改动内容**：对齐 docs branch canonical name `feature/<WI>-docs` 与 baseline recheck 的 `spec.md` / `plan.md` / `tasks.md` 要求；将 `FileGuard` 升级为进程级写拦截，统一守卫 `Path.write_text()` / `Path.write_bytes()` / `open(..., write mode)` / `Path.replace()` / `Path.rename()` 对受保护 `spec.md` / `plan.md` 的写入，消除“只拦模板写入口”的 partial 语义。
- **新增/调整的测试**：`tests/unit/test_file_guard.py` 新增 raw write / bytes / open / replace 负例；`tests/unit/test_branch_manager.py` 新增 direct write negative case；`tests/flow/test_docs_dev_flow.py` 与 `tests/unit/test_business_rules.py` 同步新 branch/baseline 合同。
- **执行的命令**：R1、V1、V2。
- **测试结果**：红灯验证先证明缺口存在；修复后 `tests/unit/test_file_guard.py tests/unit/test_branch_manager.py` **33 passed**，并纳入定向 / 全量回归。
- **是否符合任务目标**：符合。

##### Task 6.29 | INIT / REFINE / EXECUTE Gate 合同补齐

- **改动范围**：`src/ai_sdlc/gates/pipeline_gates.py`、`tests/unit/test_gates.py`
- **改动内容**：补齐 INIT 的 constitution principles / tech-stack source / decisions / source attribution，REFINE 的 acceptance scenario 校验，以及 EXECUTE 的 build prerequisite；PASS / RETRY / HALT 语义改由真实上下文证据驱动。
- **新增/调整的测试**：`tests/unit/test_gates.py` 覆盖 constitution principles 缺失、tech stack source 缺失、用户故事缺 acceptance scenario、execute 缺 build 等负例。
- **执行的命令**：见 V1 / V2。
- **测试结果**：定向与全量回归通过。
- **是否符合任务目标**：符合。

##### Task 6.30 | `index` / `gate` CLI 形态与索引重建合同

- **改动范围**：`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/cli/sub_apps.py`、`tests/integration/test_cli_index_gate.py`、`tests/integration/test_cli_verify_constraints.py`
- **改动内容**：`ai-sdlc index` 现重建 `repo-facts.json` 与 `key-files.json` 等自动索引；`gate` 显式注册 `ai-sdlc gate <stage>` aliases，同时保留 `gate check <stage>` 兼容层；同步修正 verify-constraints 对“缺 constitution”场景的旧夹具假设。
- **新增/调整的测试**：`tests/integration/test_cli_index_gate.py` 覆盖 CLI 形态与索引产物；`tests/integration/test_cli_verify_constraints.py` 改为显式删除 bootstrap 生成的 constitution，再断言 BLOCKER。
- **执行的命令**：见 V1 / V2、治理只读校验。
- **测试结果**：定向集成与只读治理校验通过。
- **是否符合任务目标**：符合。

##### Task 6.31 | 文档 / 计划 / backlog / traceability 最终对账

- **改动范围**：`specs/001-ai-sdlc-framework/tasks.md`、`specs/001-ai-sdlc-framework/implementation-drift-matrix.md`、`docs/framework-defect-backlog.zh-CN.md`、`specs/001-ai-sdlc-framework/task-execution-log.md`
- **改动内容**：将 `FR-034` 从 `deferred` 收口为 `closed`；在 `tasks.md` 追加 Batch 12 收口说明，并把 Batch 11 对 `FR-034` 的 partial 说明改成“后续已补齐”的历史口径；将 backlog 中 **FD-2026-03-27-014** 状态改为 `closed`，并补最终收口验证证据；把本批执行证据追加入归档文件。
- **新增/调整的测试**：无新增代码测试；以 `verify constraints`、`close-check` 与 `close-check --all-docs` 作为文档/台账 fresh evidence。
- **执行的命令**：治理只读校验、Close 收口校验。
- **测试结果**：全部 PASS。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **宪章/规格对齐**：本批围绕 `001` remediation 真值收口，不扩 scope；所有 drift 项均回到 `spec.md` 合同与 `tasks.md` AC 核对后再宣称关闭。
- **代码质量**：`FileGuard` 的硬拦截收敛到统一基础层，避免继续在上层零散补 guard；CLI / gate / studio 变更保持兼容层与 contract tests 同步。
- **测试质量**：`FR-034` 先红后绿；Batch 12 定向 contract suite、全量 pytest、ruff、verify constraints、close-check 与 `--all-docs` 均为新鲜证据。
- **Spec 偏移**：无新增偏移；`implementation-drift-matrix.md` 已无 `open/partial/deferred` 项。
- **结论**：无 Critical 阻塞项。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Batch 11 / 12 收口说明已回填；`M12` 口径与实现一致）。
- `related_plan`（如存在）同步状态：`已对账`（当前工作项未声明 `related_plan`，close-check 按约定跳过）。
- 说明：`001` remediation 已全部收口；新发现的 checkpoint / resume-pack stale-source 缺陷已另行登记为 backlog 条目 **FD-2026-03-28-001**，不混入本批 drift closure 语义。

#### 2.6 自动决策记录（如有）

- AD-001：只有在 `FR-034` 的 raw write / `replace()` 负例、Batch 12 定向 suite、全量 pytest、ruff、verify constraints 与 close-check 全部 fresh pass 后，才将 **FD-2026-03-27-014** 从 `open` 改为 `closed` → 理由：避免“矩阵已写 closed，但 contract 仍只到 partial”的再次漂移。

#### 2.7 批次结论

- `001-ai-sdlc-framework` 相对 `spec.md` 的 remediation drift 已全部收口：`implementation-drift-matrix.md` 全部为 `closed`，`tasks.md` / backlog / execution log / close-check 证据一致，`FR-034` 不再保留 `partial` 尾项。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：N/A（待本批统一提交后填写）
- **是否继续下一批**：按需（`001` drift 已清零；仅剩独立登记的 stale checkpoint/backlog 待办不属于本批）

### Batch 2026-03-28-019 | 001 gap closure Batch 13：intake / governance / branch protocol 合流与归档

#### 2.1 批次范围

- **覆盖内容**：审查并合流分支 `codex/batch13-rg001-rg006` 中对应 Batch 13 的实现（来源提交 `ef63c2a`），补齐 Task **6.32～6.36** 的主线代码、`tasks.md` 收口说明与 execution-log 正式归档。
- **覆盖阶段**：EXECUTE / VERIFY / CLOSE（分支实现审查、主线合流、traceability 归档）。
- **预读范围**：[`spec.md`](spec.md) `RG-001~006`、[`tasks.md`](tasks.md) Batch 13、[`plan.md`](plan.md) gap closure 设计节、`main..codex/batch13-rg001-rg006` 差异。
- **激活的规则**：合同先于实现；完成前验证；代码自审；归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：无（本批以已完成分支实现的审查与合流为主，未额外新增红灯夹具）。
  - 结果：不适用。
- **V1（定向）**
  - 命令：`uv run pytest -q tests/unit/test_work_intake_router.py tests/flow/test_new_requirement_flow.py tests/unit/test_branch_manager.py tests/flow/test_docs_dev_flow.py tests/integration/test_cli_recover.py tests/integration/test_cli_status.py tests/unit/test_business_rules.py`
  - 结果：**87 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**742 passed**（2026-03-28，本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.32 + Task 6.33 | intake 原子分配、推荐流与 uncertain 澄清真值

- **改动范围**：`src/ai_sdlc/routers/work_intake.py`、`src/ai_sdlc/models/work.py`、`tests/unit/test_work_intake_router.py`、`tests/flow/test_new_requirement_flow.py`
- **改动内容**：为 `KeywordWorkIntakeRouter` 增加正式 `intake()` 路径，在同一框架调用中完成 `work_item_id` 分配、`next_work_item_seq` 落盘/回滚与 `WorkItem` 持久化；统一补齐 `recommended_flow`、`severity`、低置信度 `needs_human_confirmation` 输出。`ClarificationState` 新增 `candidate_types` 与 `halt_reason`，并按“连续两轮未收敛后，第 3 次决策 HALT”落实 spec。
- **新增/调整的测试**：`tests/unit/test_work_intake_router.py` 新增 intake 成功、回滚、候选类型与 HALT 原因回归；`tests/flow/test_new_requirement_flow.py` 继续验证 formal intake 落盘链路。
- **执行的命令**：见 V1 / V2。
- **测试结果**：定向与全量回归通过。
- **是否符合任务目标**：符合。

##### Task 6.34 + Task 6.35 | governance freeze 阻断与 docs/dev branch binding

- **改动范围**：`src/ai_sdlc/branch/branch_manager.py`、`src/ai_sdlc/gates/governance_guard.py`、`src/ai_sdlc/context/state.py`、`src/ai_sdlc/cli/commands.py`、`tests/unit/test_branch_manager.py`、`tests/flow/test_docs_dev_flow.py`、`tests/integration/test_cli_recover.py`、`tests/integration/test_cli_status.py`、`tests/unit/test_business_rules.py`
- **改动内容**：`BranchManager` 现会从磁盘读取 `governance.yaml`，在 governance 未冻结时统一阻断 docs/dev 入口，并对冻结输入启用显式文件保护；docs -> dev 切换会记录并刷新 `current_branch`、`docs_baseline_ref`、`docs_baseline_at`，baseline recheck 失败时回滚 checkout，不再留下半更新状态。`status` / `recover` 直接展示 branch、docs baseline 与 governance frozen 绑定。
- **新增/调整的测试**：branch switch、governance-not-frozen、rollback 与 CLI status/recover 绑定展示回归同步补齐。
- **执行的命令**：见 V1 / V2。
- **测试结果**：定向与全量回归通过。
- **是否符合任务目标**：符合。

##### Task 6.36 | Batch 13 traceability / backlog / 主线对账

- **改动范围**：`specs/001-ai-sdlc-framework/tasks.md`、`specs/001-ai-sdlc-framework/task-execution-log.md`、`docs/framework-defect-backlog.zh-CN.md`
- **改动内容**：将 Batch 13 的主线实现、执行证据与里程碑口径重新对齐，消除“分支已实现但主线/归档尚未同步”的漂移。
- **新增/调整的测试**：无新增代码测试；以 V1 / V2 / Lint 作为 Batch 13 合流后的新鲜证据。
- **执行的命令**：见 V1 / V2 / Lint。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **宪章/规格对齐**：逐项核对 `RG-001~006` 与分支实现，确认 formal intake、governance frozen 入口阻断、docs/dev branch binding、status/recover surface 已进入主路径，而不是只存在于局部 helper。
- **代码质量**：`work_intake` / `branch_manager` / CLI surface 的职责边界清晰；澄清轮次边界按 `max_rounds=2` + “第 3 次决策 HALT”与 spec 保持一致。
- **测试质量**：本批以 Batch 13 相关 unit / flow / integration 套件做定向验证，再辅以全量 `pytest` 与 `ruff` 复核。
- **Spec 偏移**：无新增偏移；本批处理的是“分支实现先于主线真值同步”的收口漂移。
- **结论**：无 Critical 阻塞项，允许合入主线。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Batch 13 收口块与 `M13` 已对齐 execution-log 真值）。
- `related_plan`（如存在）同步状态：`已对账`（[`plan.md`](plan.md) 中 Batch 13 对应 gap closure 设计已和主线实现一致）。
- 说明：本批重点收口 Batch 13 的“分支实现 vs 主线/归档真值”漂移，不再保留 `planned` 口径。

#### 2.6 自动决策记录（如有）

- AD-001：保持 Batch 13 的 defect 记录以“主线/归档漂移”而非“实现从未存在”描述 → 来源：代码与测试已明确存在于分支 `codex/batch13-rg001-rg006` → 理由：避免把“未合入主线”误记成“从未实现”，确保 backlog 描述与 Git 真值一致。

#### 2.7 批次结论

- Batch 13（Task **6.32～6.36**）已完成主线合流与正式归档；`RG-001~006` 现在可在主线代码、回归测试、`tasks.md` 与 execution-log 中找到一致映射。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：N/A（待本次 merge commit 统一填写）
- **是否继续下一批**：继续 Batch 14 归档与最终对账

### Batch 2026-03-28-020 | 001 gap closure Batch 14：artifact / gate surface 合流与归档

#### 2.1 批次范围

- **覆盖内容**：审查并合流分支 `codex/batch13-rg001-rg006` 中对应 Batch 14 的实现（来源提交 `f21115a`），补齐 Task **6.37～6.39** 的主线代码、`tasks.md` 收口说明与 execution-log 正式归档。
- **覆盖阶段**：EXECUTE / VERIFY / CLOSE（formal artifact / gate surface 合流、验证与文档对账）。
- **预读范围**：[`spec.md`](spec.md) `RG-007~009`、[`tasks.md`](tasks.md) Batch 14、[`plan.md`](plan.md) gap closure 设计节、`main..codex/batch13-rg001-rg006` 差异。
- **激活的规则**：合同先于实现；完成前验证；代码自审；归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：无（本批以已完成分支实现的审查与合流为主，未额外新增红灯夹具）。
  - 结果：不适用。
- **V1（定向）**
  - 命令：`uv run pytest -q tests/unit/test_executor.py tests/flow/test_recover_flow.py tests/unit/test_gates.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py`
  - 结果：**111 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**742 passed**（2026-03-28，本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。
- **Close 收口校验**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework`、`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
  - 结果：`tasks_completion` / `related_plan_drift` / `execution_log_fields` / `review_gate` / `docs_consistency` / `done_gate` **全部 PASS**。

#### 2.3 任务记录

##### Task 6.37 | active work item artifact 正式真值面

- **改动范围**：`src/ai_sdlc/core/executor.py`、`src/ai_sdlc/context/state.py`、`src/ai_sdlc/models/state.py`、`tests/unit/test_executor.py`、`tests/flow/test_recover_flow.py`、`tests/integration/test_cli_status.py`
- **改动内容**：`Executor` 现会在 active work item 目录持续写入 `execution-plan.yaml`、`runtime.yaml`、`working-set.yaml` 与 `latest-summary.md`；`context.state` 新增这些 formal artifacts 的 load/save path，并在恢复时按 `summary-first` / `working-set-first` 组织 `resume-pack`。
- **新增/调整的测试**：executor artifact 持久化、recover 对 formal artifacts 的优先消费、status 对 execution/runtime/summary surface 的展示回归。
- **执行的命令**：见 V1 / V2。
- **测试结果**：定向与全量回归通过。
- **是否符合任务目标**：符合。

##### Task 6.38 | PRD / Review / Done / Verification Gate surface 显式化

- **改动范围**：`src/ai_sdlc/gates/pipeline_gates.py`、`src/ai_sdlc/gates/registry.py`、`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/close_check.py`、`tests/unit/test_gates.py`、`tests/integration/test_cli_verify_constraints.py`
- **改动内容**：显式新增 `PRDGate`、`ReviewGate`、`DoneGate`、`VerificationGate`，并将其接入 gate registry、runner、CLI 与 JSON/check-object surface；`DoneGate` 对未完成的 Knowledge Refresh 具备正式阻断语义，`close-check` 增补 `review_gate` / `done_gate` 检查项。
- **新增/调整的测试**：gates 单测锁定新 gate surface、Verification Gate check objects、Done Gate block 语义；CLI verify 回归验证 JSON surface。
- **执行的命令**：见 V1 / V2 / 治理只读校验 / Close 收口校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。

##### Task 6.39 | Batch 14 最终对账与里程碑回填

- **改动范围**：`specs/001-ai-sdlc-framework/tasks.md`、`specs/001-ai-sdlc-framework/task-execution-log.md`、`docs/framework-defect-backlog.zh-CN.md`
- **改动内容**：将 Batch 14 的主线实现、执行证据与里程碑口径重新对齐，并将 backlog defect 文案收敛为“分支实现曾存在，但主线/归档真值滞后”的准确历史描述。
- **新增/调整的测试**：无新增代码测试；以 V1 / V2 / 治理只读校验 / Close 收口校验作为最终对账证据。
- **执行的命令**：见 V1 / V2 / 治理只读校验 / Close 收口校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **宪章/规格对齐**：逐项核对 `RG-007~009` 与分支实现，确认 formal artifact 与显式 gate taxonomy 已进入主线磁盘真值、runner/CLI surface 与 close-check/verify surface，而不是只停留在隐式语义。
- **代码质量**：artifact path/load/save 集中在 `context.state`，gate taxonomy 与 close-check 语义集中在 `pipeline_gates` / `verify_constraints` / `close_check`，职责边界清晰。
- **测试质量**：以 Batch 14 相关 unit / flow / integration 套件做定向验证，再辅以全量 `pytest`、`ruff`、`verify constraints` 与 `close-check --all-docs` 复核。
- **Spec 偏移**：无新增偏移；本批处理的是“formal surface 已在分支实现，但主线/归档未同步”的收口漂移。
- **结论**：无 Critical 阻塞项，允许合入主线。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Batch 14 收口块与 `M13` 已对齐 execution-log 真值）。
- `related_plan`（如存在）同步状态：`已对账`（[`plan.md`](plan.md) 中 Batch 14 对应 gap closure 设计已和主线实现一致）。
- 说明：本批完成 `RG-007~009` 的主线合流、artifact / gate surface 对账与 defect 文案纠偏。

#### 2.6 自动决策记录（如有）

- AD-001：将 backlog 文案从“主线未实现”修正为“分支已实现但主线/归档真值滞后” → 来源：`git log` 与 `git branch --contains` 明确显示 `ef63c2a` / `f21115a` 先存在于 `codex/batch13-rg001-rg006` → 理由：保留真实根因，避免用错误叙述覆盖已存在的实现事实。

#### 2.7 批次结论

- Batch 14（Task **6.37～6.39**）已完成主线合流与正式归档；`RG-007~009` 现在可在主线代码、formal artifact、回归测试、`tasks.md` 与 execution-log 中找到一致映射。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：N/A（待本次 merge commit 统一填写）
- **是否继续下一批**：按需

---

### Batch 2026-03-28-021 | FD-2026-03-28-001 checkpoint / resume-pack 对账收口

#### 2.1 准备

- **任务来源**：[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-28-001`
- **目标**：将 `checkpoint.yml` 与 `resume-pack.yaml` 的恢复语义收敛为“checkpoint 为真值、resume-pack 为派生快照”，并完成 `recover/status` 的统一对账入口。
- **预读范围**：[`spec.md`](spec.md) `FR-052, FR-054`、[`tasks.md`](tasks.md) Task `6.24`、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-28-001`、`src/ai_sdlc/context/state.py`、`src/ai_sdlc/cli/commands.py`。
- **激活的规则**：TDD；恢复真值唯一化；可观测性优先；归档先于宣称完成。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest -q tests/unit/test_context_state.py tests/integration/test_cli_recover.py tests/integration/test_cli_status.py`
  - 结果：先红后绿；红灯覆盖 `pack missing/corrupted/stale` 自动重建、checkpoint 不兼容失败、`recover/status` 输出语义与新 batch 生效。
- **V1（恢复链路定向）**
  - 命令：`uv run pytest -q tests/unit/test_context_state.py tests/integration/test_cli_recover.py tests/integration/test_cli_status.py tests/flow/test_recover_flow.py tests/unit/test_branch_manager.py`
  - 结果：**66 passed**。
- **V2（全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：**746 passed**（2026-03-28，本机）。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**

#### 2.3 缺陷收口记录

- **改动范围**：`src/ai_sdlc/models/state.py`、`src/ai_sdlc/context/state.py`、`src/ai_sdlc/cli/commands.py`、`tests/unit/test_context_state.py`、`tests/integration/test_cli_recover.py`、`tests/integration/test_cli_status.py`、`docs/framework-defect-backlog.zh-CN.md`
- **改动内容**：
  - `ResumePack` 新增 `checkpoint_last_updated` 与 `checkpoint_fingerprint`，将 stale 判定从文件存在性提升为稳定的来源对账规则。
  - `load_resume_pack()` 现会先 strict 校验 checkpoint；当 pack 缺失、损坏或 stale 且 checkpoint 有效时，自动重建 root/work-item scoped pack；当 checkpoint 无效或不兼容时直接失败，不再信任旧 pack。
  - `ai-sdlc recover` 与 `ai-sdlc status` 统一消费该入口，并输出 `stale` / `rebuilding from checkpoint` / `rebuilt successfully` 等可观测提示；`status` 只修派生 pack，不推进业务状态。
- **新增/调整的测试**：
  - unit：锁定 pack 缺失、损坏、stale 自动重建，以及 checkpoint 不兼容失败。
  - integration：锁定 `recover/status` 的自动重建输出语义与“重建后使用新 batch，而不是旧内存对象”。
- **测试结果**：定向、恢复链路与全量回归全部通过。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（摘要）

- **规格对齐**：`checkpoint` 已收敛为恢复真值，`resume-pack` 明确退回派生快照角色；`recover/status` 不再独立信任旧 pack。
- **代码质量**：checkpoint↔resume-pack 对账集中在 `context.state`，CLI 仅消费统一入口并负责输出可观测提示，职责边界清晰。
- **测试质量**：已覆盖缺失、损坏、stale、checkpoint 不兼容，以及恢复后显示新 batch 的正反路径。
- **结论**：无阻塞项，`FD-2026-03-28-001` 可收口。

#### 2.5 归档后动作

- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-28-001` 已标记为 `fixed` 并写入收口说明）。
- `001` 归档状态：`已补充`（本批为 001 余留 defect closure，不改动原 Batch 11~14 完成态）。

---

### Batch 2026-03-28-022 | 001 Batch 15 Task 6.40：legacy reconcile / recover 控制流收敛

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `6.40`、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-26-002`
- **目标**：把 legacy checkpoint reconcile 的控制流从“已有提示但仍可能继续走旧 checkpoint / 抛底层错误”收敛为正式行为，并补齐 `specs/<WI>/` 旧布局、blank checkpoint 等兼容回归。
- **预读范围**：[`docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md`](../../docs/defects/2026-03-26-legacy-checkpoint-reconcile.zh-CN.md)、[`tasks.md`](tasks.md) Batch `15`、`src/ai_sdlc/core/reconcile.py`、`src/ai_sdlc/context/state.py`、`src/ai_sdlc/cli/commands.py`、相关 reconcile / CLI tests。
- **激活的规则**：TDD；systematic debugging；恢复真值唯一化；归档先于继续。

#### 2.2 统一验证命令

- **R1（红灯验证）**
  - 命令：`uv run pytest tests/integration/test_cli_status.py::TestCliStatus::test_status_guides_user_when_blank_checkpoint_needs_reconcile tests/integration/test_cli_recover.py::TestCliRecover::test_recover_stops_until_reconcile_is_applied_for_legacy_artifacts -q`
  - 结果：先红后绿；初始失败暴露两类真实问题：`status` 在 blank checkpoint 场景会先报 `Invalid checkpoint`，`recover` 在 stale `init/unknown` checkpoint 场景虽然给出 guidance 却仍继续按旧状态恢复。
- **V1（legacy reconcile 定向回归）**
  - 命令：`uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_recover.py tests/integration/test_cli_run.py tests/integration/test_cli_stage.py -q`
  - 结果：**40 passed**。
- **V2（reconcile / context 单测）**
  - 命令：`uv run pytest tests/unit/test_reconcile.py tests/unit/test_context_state.py -q`
  - 结果：**19 passed**。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 2.3 任务记录

##### Task 6.40 | legacy reconcile / recover backfill 主路径

- **改动范围**：`src/ai_sdlc/context/state.py`、`src/ai_sdlc/core/reconcile.py`、`src/ai_sdlc/cli/commands.py`、`tests/integration/test_cli_status.py`、`tests/integration/test_cli_recover.py`、`tests/unit/test_reconcile.py`
- **改动内容**：
  - `load_checkpoint()` 新增 `warn` 开关；reconcile 探测链改为静默消费损坏/空白 checkpoint，避免在 hint 探测阶段向用户泄露底层解析噪音。
  - `status` 现会先判断 reconcile hint；若 checkpoint 文件存在但处于 blank/missing 可对齐场景，不再急于走 strict resume-pack 恢复，而是优先输出可操作 guidance。
  - `recover` 在检测到 stale `init/unknown` checkpoint 且用户未执行 `--reconcile` 时会直接停止，不再一边提示、一边继续按旧 checkpoint 生成 `Resume Stage: init`。
  - unit / integration tests 新增 `specs/<WI>/` 旧布局探测、blank checkpoint guidance、reconcile 后 `status` 脱离 `unknown/init` 等回归。
- **新增/调整的测试**：
  - integration：blank checkpoint 下 `status` guidance、未 reconcile 时 `recover` 阻断、`specs/<WI>/` 布局对齐后 `status` 真值展示。
  - unit：无 checkpoint 的 `specs/<WI>/` 旧布局 reconcile hint。
- **执行的命令**：见 R1 / V1 / V2 / Lint / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：部分符合。Task 6.40 的控制流与主要兼容夹具已落地，但 Batch 15 仍需 Task 6.41 对账收口后再决定 defect 是否关闭。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批把 defect 文档中的“空白 checkpoint 也应给正式对齐入口”“recover 不得继续沿旧 `init/unknown` 状态误恢复”落实成真实 CLI 行为，而不是只留 guidance 文案。
- **代码质量**：checkpoint 解析噪音被约束在探测层内部，`status` / `recover` 分别负责“只读诊断”和“先对齐再恢复”的清晰职责。
- **测试质量**：红灯用例先证明原缺口真实存在，再补 `specs/<WI>/` layout 与对齐后 `status` 真值回归，避免只测 happy path。
- **结论**：无新的阻塞项；允许进入 Task 6.41 的 execution-log / backlog / close-check 对账。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `6.40` 已追加进展说明，明确“已完成实现，待 6.41 对账”）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-26-002` 已从 `open` 调整为 `in_progress`，并补当前处置边界）。
- `related_plan`（如存在）同步状态：`已对账`（Batch 15 当前仅推进 Task `6.40`，未与既有 `001` 计划产生新漂移）。

#### 2.6 自动决策记录（如有）

- AD-001：本轮只把 `FD-2026-03-26-002` 推进到 `in_progress`，不直接改成 `closed` → 理由：控制流与核心回归已收口，但 Batch 15 尚缺 Task `6.41` 的台账对账与是否补“旧 `project-state.yaml` 残留”专门夹具的最终判断。

#### 2.7 批次结论

- Task **6.40** 已完成第一轮实现与回归，`001` 的 legacy reconcile / recover 主路径不再在 blank checkpoint 或 stale `init/unknown` checkpoint 下给出误导性行为；Batch 15 仍待 Task **6.41** 完成文档与缺陷台账对账。

#### 2.8 归档后动作

- **已完成 git 提交**：否
- **提交哈希**：N/A
- **是否继续下一批**：继续 Task `6.41`

### Batch 2026-03-28-023 | 001 Batch 15 Task 6.41：legacy reconcile backlog/document 收口

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `6.41`、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-26-002`
- **目标**：在 Task `6.40` 主路径落地后，补齐旧 `project-state.yaml` 残留字段回归，并完成 execution-log / backlog / `close-check` 的关单对账。
- **预读范围**：[`tasks.md`](tasks.md) Batch `15`、[`docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)、`tests/unit/test_reconcile.py`、[`task-execution-log.md`](task-execution-log.md)
- **激活的规则**：fresh verification；台账真值唯一化；close 前先补回归再写结论。

#### 2.2 统一验证命令

- **V1（legacy CLI integration 回归）**
  - 命令：`uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_recover.py tests/integration/test_cli_run.py tests/integration/test_cli_stage.py -q`
  - 结果：**40 passed**。
- **V2（reconcile / context 单测）**
  - 命令：`uv run pytest tests/unit/test_reconcile.py tests/unit/test_context_state.py -q`
  - 结果：**20 passed**。
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：**All checks passed!**
- **001 文档收口校验**
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/001-ai-sdlc-framework --all-docs`
  - 结果：**PASS**（`tasks_completion` / `execution_log_fields` / `review_gate` / `docs_consistency` / `done_gate` 全通过）。
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：**无 BLOCKER**。

#### 2.3 任务记录

##### Task 6.41 | Batch 15 backlog/document 收口

- **改动范围**：`tests/unit/test_reconcile.py`、[`tasks.md`](tasks.md)、[`task-execution-log.md`](task-execution-log.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **改动内容**：
  - 新增旧 `project-state.yaml` 残留字段夹具，验证 `reconcile_checkpoint()` 不会被历史 `current_stage/completed_stages/feature` 杂质误导。
  - 将 Batch `15` 的任务进展、execution-log 与 defect backlog 对齐到同一事实，并把 `FD-2026-03-26-002` 从 `in_progress` 收到 `closed`。
  - 更新“下一波待修优先级”，把已收口的 `FD-2026-03-26-002` 从待修清单中移除，避免后续执行时继续把已关闭项当作 backlog。
- **新增/调整的测试**：
  - unit：旧 `project-state.yaml` 残留字段 + stale checkpoint + 旧布局产物的 reconcile regression。
- **执行的命令**：见 V1 / V2 / Lint / 001 文档收口校验 / 治理只读校验。
- **测试结果**：全部通过。
- **是否符合任务目标**：符合。Task `6.41` 的台账、文档与回归证据已经统一，Batch `15` 可正式收口。

#### 2.4 代码审查（摘要）

- **规格对齐**：补上 defect 文档最后缺失的“旧 `project-state.yaml` 字段残留”自动化证据后，Batch `15` 的验收标准已全部有回归或只读校验支撑。
- **代码质量**：本批仅新增回归与文档对账，不扩大运行时代码改动面。
- **测试质量**：Batch `15` 现在同时覆盖根目录旧布局、`specs/<WI>/` 旧布局、blank/stale checkpoint 与 legacy `project-state.yaml` 残留。
- **结论**：允许关闭 `FD-2026-03-26-002`，并进入 Batch `16`。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `6.40` 与 Task `6.41` 已更新为“已完成并收口”口径）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-26-002` 已关闭，顶部待修优先级已移除该项）。
- `related_plan`（如存在）同步状态：`已对账`（Batch `15` 收口后不再残留未声明的 checkpoint / recover 分叉）。

#### 2.6 自动决策记录（如有）

- AD-001：在补齐旧 `project-state.yaml` 残留专门夹具后关闭 `FD-2026-03-26-002`，不再继续维持 `in_progress` → 理由：缺陷文档列出的最后一项回归证据已经补全，且 `001` 的只读 close 校验与全仓约束校验均通过。

#### 2.7 批次结论

- Task **6.41** 已完成，Batch **15** 正式收口；`FD-2026-03-26-002` 不再属于待修 backlog，`001` 下一步进入 Batch **16** 的 Git 写 guardrail / 完成前验证 / 文档优先执行约束。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`6891e11`（`fix: close legacy reconcile backlog batch`）
- **是否继续下一批**：可继续 Task `6.42`

### Batch 2026-03-28-024 | 001 Batch 16 Task 6.43：close-check git 收口阻断

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) Task `6.43`、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-24-003`
- **目标**：把本轮真实暴露的“最终 `git commit` 之前先宣称收口”缺口产品化为 `close-check` blocker，并把违约回挂到 `001` 主线 backlog。
- **预读范围**：[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)、[`../../docs/pull-request-checklist.zh.md`](../../docs/pull-request-checklist.zh.md)、[`tasks.md`](tasks.md) Batch `16`
- **激活的规则**：verification-before-completion；TDD；收口必须落回 Git 真值。

#### 2.2 统一验证命令

- **R1（git close-out 红灯验证）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：先红后绿；初始失败证明当前 `close-check` 不会阻断 latest batch 未提交或工作树 dirty 的收口场景。
- **V1（close-check 定向回归）**
  - 命令：`uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -q`
  - 结果：**21 passed**。
- **Lint**
  - 命令：`uv run ruff check src/ai_sdlc/core/close_check.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py`
  - 结果：**All checks passed!**

#### 2.3 任务记录

##### Task 6.43 | close-check git 收口阻断（第一轮）

- **改动范围**：[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/integration/test_cli_workitem_close_check.py`](../../tests/integration/test_cli_workitem_close_check.py)、[`../../docs/pull-request-checklist.zh.md`](../../docs/pull-request-checklist.zh.md)、[`tasks.md`](tasks.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md)
- **改动内容**：
  - `close-check` 新增 `git_closure` 检查：读取 execution-log latest batch 的 `已完成 git 提交` / `提交哈希` 标记，并在仓库工作树仍 dirty 时直接报 BLOCKER。
  - 新增 unit / integration 回归，覆盖“latest batch 未提交”“latest batch 虽标记已提交但工作树仍脏”两类真实违约。
  - PR checklist 与 backlog / tasks 同步更新，明确 close-check 需要在本轮 git 提交完成后执行，避免再次把“只读检查全绿”误表述为“已收口”。
- **新增/调整的测试**：
  - unit：`run_close_check()` 对 git close-out marker 缺失/为否、dirty worktree 的阻断。
  - integration：CLI `workitem close-check` 对上述两类场景返回 exit code `1`。
- **执行的命令**：见 R1 / V1 / Lint。
- **测试结果**：通过。
- **是否符合任务目标**：部分符合。`close-check` 已能阻断“未 commit 收口”，但 docs-only / rules-only 的最小 fresh verification 分类与 `verify constraints` 协同仍待继续。

#### 2.4 代码审查（摘要）

- **规格对齐**：本批把“最终 `git commit` 前不得声称收口”从规则文本落到了可执行门禁，不再只靠人工自觉。
- **代码质量**：新检查只读依赖 execution-log 最新批次标记和 Git 状态，不引入写副作用。
- **测试质量**：红灯先证明老逻辑确实放过了真实违约，再补两层自动化回归，避免只在文档层补口径。
- **结论**：允许继续推进 Task `6.43` 剩余的 docs-only fresh verification 分类，但不得再把 `FD-2026-03-24-003` 视为“只差文案”。

#### 2.5 任务/计划同步状态

- `tasks.md` 同步状态：`已同步`（Task `6.43` 已补当前进展与残留边界）。
- `framework-defect-backlog.zh-CN.md` 同步状态：`已同步`（`FD-2026-03-24-003` 已转 `in_progress` 并记录本轮真实违约）。
- `related_plan`（如存在）同步状态：`已对账`（当前批次未引入新的 `related_plan` 漂移）。

#### 2.6 自动决策记录（如有）

- AD-001：本轮不重开 `FD-2026-03-25-001`，而是把真实违约回挂到仍处打开状态的 `FD-2026-03-24-003` / Task `6.43` → 理由：当前暴露的根因仍属于“完成前验证 / fresh evidence 未完全产品化”，继续沿既有第二波 backlog 收口更能保持单一真值。

#### 2.7 批次结论

- Task **6.43** 已完成第一轮产品化：`close-check` 会对未 commit 收口直接报 BLOCKER；`FD-2026-03-24-003` 仍保持 `in_progress`，等待 docs-only / rules-only 最小验证集与 `verify constraints` 协同继续补齐。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：本批唯一一次语义提交为 `fix: block uncommitted close-check closures`；完整 SHA 以当前 `HEAD`（`git rev-parse HEAD`）为准。
- **是否继续下一批**：继续 Task `6.43`
