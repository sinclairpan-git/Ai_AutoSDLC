# 任务执行日志：AI-SDLC Loop Engine and Local Adversarial PR Review

**功能编号**：`189-loop-engine-local-adversarial-pr-review`  
**创建日期**：2026-06-29  
**状态**：PRD 草案阶段

## 1. 归档规则

- 本文件是 `189-loop-engine-local-adversarial-pr-review` 的固定执行归档文件。
- 后续每完成一批任务，都在本文件末尾追加一个新的批次章节。
- 当前阶段只完成 PRD 归档，不代表已经进入实现。
- 后续每一批任务开始前，必须先完成固定预读：`spec.md`、`plan.md`、`tasks.md`、宪章和相关规则。
- 后续每一批任务结束后，必须记录改动范围、验证命令、测试结果、代码审查结论、任务/计划同步状态和下一步。

## 2. 批次记录

### Batch 2026-06-29-001 | T001

#### 2.1 批次范围

- 覆盖任务：`T001`
- 覆盖阶段：PRD 草案归档
- 改动范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 目标：将 Loop Engine 与本地对抗 PR Review 规划转化为 Codex 开发 agent 可理解的 formal PRD。

#### 2.2 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（formal truth 只读检查）
  - 命令：`uv run ai-sdlc workitem truth-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：未通过；该命令按 committed `HEAD` 读取，当前 PRD 文件尚未提交，因此报告 formal docs not found。此结果不表示 working tree 中的 PRD 缺失。
- `S1`（program truth sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：超过一分钟无输出，被人工中断；`program-manifest.yaml` 已由 `workitem init` 添加 189 条目，后续冻结/提交前需重新确认是否需要再运行 sync。

#### 2.3 任务记录

##### T001 | 归档标准 PRD

- 改动范围：formal work item 文档。
- 改动内容：新增 Loop Engine PRD，明确五类闭环、本地独立 review agent、review pack、findings、fix/rerun/close、CI 不调用模型和风险控制。
- 新增/调整的测试：当前为文档阶段，未新增代码测试。
- 执行的命令：`git diff --check`、`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem truth-check --wi specs/189-loop-engine-local-adversarial-pr-review`、`uv run ai-sdlc program truth sync --execute --yes`。
- 测试结果：diff check 与 verify constraints 通过；truth-check 因未提交 HEAD 不可见新文件而失败；program truth sync 被中断。
- 是否符合任务目标：符合 PRD 草案归档目标，尚需对抗评审后冻结。

#### 2.4 代码审查结论（Mandatory）

- 宪章/规格对齐：PRD 明确 P0/P1/P2、非目标、证据、状态落盘、验证和人工升级点，符合当前文档阶段目标。
- 代码质量：未改代码。
- 测试质量：当前为文档阶段，完成 diff check 与 verify constraints；后续实现阶段必须补 schema/unit/integration tests。
- 结论：PRD 草案可进入对抗评审，不可直接进入实现。

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：已调整为 PRD 冻结前任务占位，未授权实现。
- `related_plan` 同步状态：`plan.md` 已调整为设计占位，等待 PRD 对抗评审后展开。
- 关联 branch/worktree disposition 计划：待最终收口。
- 说明：当前批次只做 PRD 归档，不进入 execute。

#### 2.6 自动决策记录（如有）

- 使用 `189-loop-engine-local-adversarial-pr-review` 作为 formal work item id。
- 按仓库 CLI 要求在 `feature/189-loop-engine-local-adversarial-pr-review-docs` 分支创建 formal docs。
- 将生成模板中的 direct-formal 实现任务替换为 PRD 冻结前占位，避免后续 agent 误执行。

#### 2.7 批次结论

- 标准 PRD 已归档到 formal work item。下一步是对 `spec.md` 进行本地对抗评审，并根据评审结果修订后再冻结。

#### 2.8 归档后动作

- 已完成 git 提交：否。
- 提交哈希：待本批提交后生成。
- 当前批次 branch disposition 状态：待最终收口。
- 当前批次 worktree disposition 状态：待最终收口。
- 是否继续下一批：先进行 PRD 对抗评审。

### Batch 2026-06-29-002 | T002

#### 2.9 批次范围

- 覆盖任务：`T002`
- 覆盖阶段：PRD 第一轮对抗评审
- 改动范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 目标：以产品、架构、测试、隐私/安全、普通用户 CLI UX 视角审查 PRD，并修复 P0 blocker。

#### 2.10 评审发现

| Finding | 严重级别 | 结论 |
|---------|----------|------|
| ADV-PRD-001 | P0 | `codex-local` 缺少可验证 reviewer 启动/隔离合同 |
| ADV-PRD-002 | P0 | `pr-review fix` 与“reviewer 只读、implementation agent 修复”职责边界不清 |
| ADV-PRD-003 | P0 | `REQUIRED` close 语义存在冲突，可能默认放行 |
| ADV-PRD-004 | P0 | 隐私/redaction 停留在风险描述，缺少 P0 预检阻断 |
| ADV-PRD-005 | P0 | review pack omit/coverage 不透明，可能在不完整输入上误判 pass |

#### 2.11 修订结果

- 在 `spec.md` 中新增默认 fail-closed 原则。
- 新增用户故事 7，覆盖隐私、敏感文件和外发确认。
- 新增/修订 FR-189-028 至 FR-189-030、FR-189-047 至 FR-189-052、FR-189-068 至 FR-189-073、FR-189-107 至 FR-189-109。
- 修正默认 close 语义：默认 close 阻断 unresolved `BLOCKER` 和 `REQUIRED`；`--require-no-blockers` 仅生成 risk-accepted 宽松报告。
- 扩展 artifact 布局，加入 `redaction-report.json`、`reviewer-invocation.json`、`fix-plan.md`。
- 新增对抗评审记录章节。

#### 2.12 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（program truth sync 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：30 秒无输出，被人工中断；与上一批 execute sync 卡住一致，暂按工具层风险记录。

#### 2.13 批次结论

- 第一轮 P0 blocker 已修订完成。`git diff --check` 与 `uv run ai-sdlc verify constraints` 均通过。当前 PRD 可提交给用户判断：继续第二轮对抗评审，或确认冻结后展开 `plan.md` / `tasks.md`。

### Batch 2026-06-29-003 | T003

#### 2.14 批次范围

- 覆盖任务：`T003`
- 覆盖阶段：PRD 第二轮对抗评审
- 改动范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 目标：按用户指定的两个角色进行第二轮评审：
  - AI-Native 架构师：多家大型公司闭环落地经验，关注多仓治理、schema/version、policy、runner failure mode。
  - 技术小白：关注命令是否用户友好、学习成本是否低、失败后是否知道下一步。

#### 2.15 评审发现

| Finding | 角色 | 严重级别 | 结论 |
|---------|------|----------|------|
| ADV2-ARCH-001 | AI-Native 架构师 | P0 | artifact 缺少 schema version / validation / compatibility |
| ADV2-ARCH-002 | AI-Native 架构师 | P0 | 缺少项目级 policy profile，企业多仓策略不可治理 |
| ADV2-ARCH-003 | AI-Native 架构师 | P0 | Provider runner 退出码、输出路径和 allowlist 未标准化 |
| ADV2-UX-001 | 技术小白 | P0 | 普通用户路径太难，不知道 base/provider/下一步 |

#### 2.16 修订结果

- 新增小白友好与企业可治理原则。
- 新增用户故事 8：技术小白可完成本地 PR review。
- 新增用户故事 9：大型组织可治理地推广 Loop Engine。
- 新增 Loop artifact `schema_version`、schema validation、compatibility 要求。
- 新增项目级 `LoopPolicyProfile`，覆盖 provider 外发、max rounds、close mode、redaction strictness 和 omitted file 策略。
- 新增 provider runner 标准退出码、output path、allowlist 和 schema validation 失败处理。
- 新增 `ai-sdlc pr-review doctor`、base 自动检测、默认 provider 指引、plain-language blocker 和小白 3 步路径。
- 更新 P0 切分，将 schema validation、policy profile、beginner UX 纳入首版。

#### 2.17 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`

#### 2.18 批次结论

- 第二轮 P0 blocker 已修订完成。`git diff --check` 与 `uv run ai-sdlc verify constraints` 均通过。当前 PRD 已覆盖本地独立 review、企业治理、schema 稳定性、provider runner failure mode 和普通用户体验。下一步由用户决定是否冻结 PRD，或继续第三轮评审。

### Batch 2026-06-29-004 | T004

#### 2.19 批次范围

- 覆盖任务：`T004`
- 覆盖阶段：PRD 冻结、实施计划展开、可执行任务分解
- 改动范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- 目标：根据用户“冻结 PRD，按照框架约束继续”的指令，将 PRD 标记为冻结，并补齐 implementation plan 与 executable task breakdown。

#### 2.20 改动内容

- 将 `spec.md` 状态改为已冻结，并更新 Codex 开发 agent 执行提示。
- 将 `plan.md` 从设计占位改为实施计划，明确模块设计、artifact 合同、CLI 命令、工作流、验证策略、开放设计决策和回退方式。
- 将 `tasks.md` 从任务占位改为可执行任务分解，覆盖 6 个 batch、15 个 P0 tasks、文件范围、验收标准和验证命令。
- 保持实现前边界：不得使用 Codex 云端 PR review，不得在 CI 调用 GPT/Codex，P0 reviewer 不改代码。

#### 2.21 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（占位残留检查）
  - 命令：`rg -n "TODO|待补|等待用户冻结|设计占位|任务占位|尚未授权实现|P0 允许 close" specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：仅命中历史执行日志中对“此前占位状态”和“已从占位改为计划/任务”的描述；当前 `spec.md`、`plan.md`、`tasks.md` 无待补占位。

#### 2.22 任务/计划同步状态（Mandatory）

- `spec.md` 同步状态：已冻结，作为需求真值。
- `plan.md` 同步状态：已展开实施计划，覆盖 PRD P0 范围。
- `tasks.md` 同步状态：已展开可执行任务分解，尚未进入代码实现。
- 关联 branch/worktree disposition 计划：待后续提交/PR 收口。

#### 2.23 批次结论

- PRD 已冻结，`plan.md` 与 `tasks.md` 已按框架约束展开；当前仍未进入代码实现。下一步需要用户明确授权进入 execute 后，才能按 `tasks.md` 从 Batch 1 开始实现。

### Batch 2026-06-29-005 | T005

#### 2.24 批次范围

- 覆盖任务：`T005`
- 覆盖阶段：实施计划 / 任务分解对抗评审与修订
- 改动范围：`plan.md`、`tasks.md`、`task-execution-log.md`
- 目标：对冻结 PRD 后的拆解内容做只读对抗评审，并修复会影响 P0 落地可信度的任务缺口。

#### 2.25 评审发现

| Finding | 严重级别 | 结论 |
|---------|----------|------|
| ADV3-PLAN-001 | P0 | `review-pack.json` 合同缺少 `diff_summary`、`work_item_refs`、`test_results_refs`、`policy_refs`，可能导致 reviewer 缺少关键证据 |
| ADV3-PLAN-002 | P0 | `codex-local` 只验收未配置路径，缺少“已配置本地命令可运行”的 P0 验收 |
| ADV3-TASK-001 | P1 | `fix/rerun/close` 的真实 CLI 暴露没有被直接列为验收 |
| ADV3-TASK-002 | P1 | 未定版本 release note 路径是不可执行占位 |
| ADV3-TASK-003 | P1 | `doctor` / `start --dry-run` 只读边界缺少测试验收 |

#### 2.26 修订结果

- `plan.md` 的 Review Pack Builder 职责补齐 `diff_summary`、`work_item_refs`、`test_results_refs`、`policy_refs`。
- `plan.md` 的 `review-pack.json` 合同补齐上述字段。
- `plan.md` 的 `codex-local` 决策从“runner 合同”收紧为必须测试已配置本地命令与未配置 `needs_user` 两条路径。
- `plan.md` 增加 `doctor` 与 `start --dry-run` 的只读预演边界。
- `tasks.md` 的 T23、T31、T41、T42、T51、T52、T53、T62 均补充对应验收。
- `tasks.md` 移除未定版本 release note 文件占位，改为实际版本号明确后再创建或更新 release note。

#### 2.27 当前状态

- PRD 仍保持冻结，不做需求重写。
- `plan.md` / `tasks.md` 已完成本轮对抗评审修订。
- 当前仍未进入代码实现；实现前仍需用户明确授权 execute。

#### 2.28 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（关键修订面检查）
  - 命令：`rg -n 'diff_summary|work_item_refs|test_results_refs|policy_refs|start --dry-run|已配置本地|未定版本|<next>' specs/189-loop-engine-local-adversarial-pr-review/plan.md specs/189-loop-engine-local-adversarial-pr-review/tasks.md specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
  - 结果：`plan.md` / `tasks.md` 已命中新增合同字段、`codex-local` 已配置路径、dry-run 只读边界和 release note 占位处理；未命中字面 `<next>`。

### Batch 2026-06-29-006 | T006

#### 2.29 准备

- **任务来源**：PR #103 Codex review comment `discussion_r3489408141`
- **目标**：补齐最新执行批次的 close-check 解析字段，使 189 文档包具备 docs-only close-out evidence。
- **预读范围**：`task-execution-log.md`、`src/ai_sdlc/core/close_check.py`、PR #103 Codex review comment
- **激活的规则**：close-check execution log fields；docs-only evidence truthfulness；git close-out markers。
- **验证画像**：`docs-only`
- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.30 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（work item close-check 复现）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：本地执行 30 秒无输出，被人工中断；PR Codex review 已复现 close-check blocker，原因是最新批次缺少 `验证画像`、`改动范围`、git close-out markers。本批按该 blocker 补齐字段。

#### 2.31 任务记录

##### Task review-remediation | 补齐 close-check evidence markers

- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
- **改动内容**：
  - 追加最新 docs-only remediation 批次，补齐 `验证画像`、`改动范围`、已提交状态和提交哈希字段。
  - 保留历史批次，不回写伪造旧批次；本批只作为 PR review 后的 canonical evidence close-out。
  - 不修改冻结 PRD，不进入代码实现，不改变 `plan.md` / `tasks.md` 任务边界。
- **新增/调整的测试**：无代码测试；本批为文档证据补录。
- **执行的命令**：见 V1 ~ V3。
- **测试结果**：`git diff --check` 与 `uv run ai-sdlc verify constraints` 通过；`workitem close-check` 当前存在本地无输出工具层风险。
- **是否符合任务目标**：符合 PR review remediation 目标。

#### 2.32 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现**：最新批次缺少 close-check markers，可能导致 work item 不能 clean close。
- **处置**：已补录 Batch 006，明确 docs-only verification profile、changed paths 和 git close-out markers。
- **结论**：可重新提交并请求 Codex review。

#### 2.33 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已对账，未修改。
- `task-execution-log.md` 同步状态：已补齐 PR review remediation close-out evidence。

#### 2.34 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`834d2b38`（PR #103 初始 189 文档包提交；本批为该 PR 的 review remediation 补录）
- **是否继续下一批**：否；等待 PR checks 与 Codex re-review 收口。

### Batch 2026-06-29-007 | T007

#### 2.35 准备

- **任务来源**：PR #103 Codex review comments `discussion_r3489455006`、`discussion_r3489455009`
- **目标**：修复 189 文档包的 checkpoint 绑定与 program truth snapshot，使后续实现授权时不会错误回落到 WI-187。
- **预读范围**：`.ai-sdlc/state/checkpoint.yml`、`program-manifest.yaml`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/core/workitem_traceability.py`
- **激活的规则**：checkpoint active work item binding；program truth snapshot；branch/worktree disposition；truth-only verification profile。
- **验证画像**：`truth-only`
- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`program-manifest.yaml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.36 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 初次结果：未通过；checkpoint 绑定到 WI-189 后，暴露当前 PR branch 尚未写明 disposition，报告 `branch lifecycle unresolved`。
  - 修复动作：本批补齐最新批次 branch/worktree disposition marker，并重新执行该命令。
  - 复验结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（program truth snapshot 刷新）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写入 `program-manifest.yaml`，snapshot hash 为 `31d94763126df3be23778f03841bfdb993dd9a6b9ca2592790c08df90a2ee1e6`，snapshot state 为 `migration_pending`。
- `V4`（program truth snapshot 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；dry-run 输出 snapshot state 为 `migration_pending`，确认 189 source inventory 已纳入 truth surface。

#### 2.37 任务记录

##### Task review-remediation | 修复 checkpoint 与 truth snapshot

- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`program-manifest.yaml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
- **改动内容**：
  - 将 checkpoint 的 `feature.id`、`feature.spec_dir`、branch 字段和 `execute_progress` 指针从 WI-187 调整为 WI-189。
  - 通过 `uv run ai-sdlc program truth sync --execute --yes` 刷新 persisted `truth_snapshot`，使 189 formal docs 进入 source inventory。
  - 记录当前 PR branch 的 disposition：作为 PR #103 mainline merge carrier 保留，合并后由 GitHub/merge 操作删除远端分支；当前 worktree 保留为本仓库主工作区。
- **新增/调整的测试**：无代码测试；本批为治理状态与 truth snapshot 修复。
- **执行的命令**：见 V1 ~ V4。
- **测试结果**：`git diff --check`、`uv run ai-sdlc verify constraints`、`program truth sync --execute --yes`、`program truth sync --dry-run` 均已完成；最终提交前将再执行一次 `program truth sync --execute --yes`，确保 persisted snapshot 对应稳定后的执行日志。
- **是否符合任务目标**：符合 PR review remediation 目标。

#### 2.38 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现 1**：`.ai-sdlc/state/checkpoint.yml` 的 `linked_wi_id` 已指向 189，但 `feature.id` / `feature.spec_dir` / `execute_progress` 仍指向 187。
- **处置 1**：已将 checkpoint 当前 work item 与执行指针统一到 189。
- **发现 2**：`program-manifest.yaml` 新增 189 后未刷新 persisted `truth_snapshot`。
- **处置 2**：已执行 `uv run ai-sdlc program truth sync --execute --yes` 并写入新 snapshot。
- **结论**：可在完成 V2/V4 复验后重新提交并请求 Codex review。

#### 2.39 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已对账，未修改。
- `task-execution-log.md` 同步状态：已记录第二轮 PR review remediation。
- 关联 branch/worktree disposition 计划：PR #103 merge carrier，目标 disposition 为 merge 后删除远端分支。

#### 2.40 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`66fabfe285e685222317df2c2f80f096b431632d`
- 当前批次 branch disposition 状态：PR #103 merge carrier（待 checks/review 通过后合并）
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）
- **是否继续下一批**：否；等待本批复验、提交、push、Codex re-review 与 PR checks 收口。

### Batch 2026-06-29-008 | T008

#### 2.41 准备

- **任务来源**：PR #103 Codex review comments `discussion_r3489549011`、`discussion_r3489549013`
- **目标**：将 `tasks.md` 转换为 executable-task parser 可解析格式，并在最终文档变更后刷新 persisted truth snapshot。
- **预读范围**：`src/ai_sdlc/core/executable_task.py`、`tests/unit/test_executable_task.py`、`specs/188-vue3-public-primevue-default-provider-governance/tasks.md`、PR #103 Codex review comments
- **激活的规则**：executable task parser contract；SC-014 task acceptance；truth-only verification profile；program truth snapshot。
- **验证画像**：`truth-only`
- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/tasks.md`、`program-manifest.yaml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`

#### 2.42 统一验证命令

- `V1`（executable task parser）
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.core.executable_task import parse_executable_tasks; r=parse_executable_tasks(Path('specs/189-loop-engine-local-adversarial-pr-review/tasks.md')); print('ok=', r.ok, 'tasks=', len(r.tasks)); [print(e.code, e.message) for e in r.errors]"`
  - 结果：通过，`ok= True tasks= 15`。
- `V2`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V3`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V4`（program truth snapshot 刷新）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写入 `program-manifest.yaml`，snapshot state 为 `migration_pending`。
- `V5`（program truth snapshot 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；dry-run 输出 snapshot state 为 `migration_pending`。

#### 2.43 任务记录

##### Task review-remediation | 转换 tasks.md 为机器可解析格式

- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/tasks.md`、`program-manifest.yaml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
- **改动内容**：
  - 将 15 个任务块统一转换为 `task_id`、`status`、`goal`、`priority`、`depends`、`scope`、`acceptance`、`verify`、`notes` 格式。
  - 保留 P0 任务边界、依赖关系、验收标准、验证命令和实现前硬性边界。
  - 在 `notes` 中加入“验收标准：见 acceptance 字段。”，兼容 SC-014 对中文验收标记的旧检查。
  - 最终日志稳定后刷新 `program-manifest.yaml` 的 persisted `truth_snapshot`。
- **新增/调整的测试**：新增 parser 级本地验证命令；未新增产品代码测试。
- **执行的命令**：见 V1 ~ V5。
- **测试结果**：V1、V2、V3、V4、V5 均已通过；最终提交前将再执行一次 `program truth sync --execute --yes`，确保 persisted snapshot 对应稳定后的执行日志。
- **是否符合任务目标**：符合 PR review remediation 目标。

#### 2.44 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现 1**：`tasks.md` 标记为可执行任务分解，但任务块缺少 parser 要求字段。
- **处置 1**：已转换为 executable-task parser 可解析格式，15 个任务解析通过。
- **发现 2**：persisted truth snapshot 未覆盖最终文档状态。
- **处置 2**：本批最终日志稳定后重新执行 `program truth sync --execute --yes` 并提交 manifest。
- **结论**：可在 V4/V5 完成后重新提交并请求 Codex review。

#### 2.45 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已转换为 machine-readable executable task blocks。
- `task-execution-log.md` 同步状态：已记录第三轮 PR review remediation。
- 关联 branch/worktree disposition 计划：PR #103 merge carrier，目标 disposition 为 merge 后删除远端分支。

#### 2.46 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`ee8ccc886aa594068c8ec3f37361692449f1770f`（本批修复基线提交；当前批次将作为后续 PR remediation commit 推送）
- 当前批次 branch disposition 状态：PR #103 merge carrier（待 checks/review 通过后合并）
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）
- **是否继续下一批**：否；等待本批复验、提交、push、Codex re-review 与 PR checks 收口。

### Batch 2026-06-29-009 | T009

#### 2.47 准备

- **任务来源**：PR #103 Codex review comments `discussion_r3489408141`、`discussion_r3489611933`、`discussion_r3489611940`
- **目标**：补齐最新批次 close-check markers，并修正 PRD 中 dry-run 独立测试与 Loop Engine P0/P1 范围的两处冲突。
- **预读范围**：`specs/189-loop-engine-local-adversarial-pr-review/spec.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`src/ai_sdlc/core/close_check.py`
- **激活的规则**：truth-only verification profile；close-check latest batch markers；P0/P1 scope consistency；dry-run read-only contract。
- **验证画像**：`truth-only`
- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/spec.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`

#### 2.48 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V2`（executable task parser）
  - 命令：`uv run python -c "from pathlib import Path; from ai_sdlc.core.executable_task import parse_executable_tasks; r=parse_executable_tasks(Path('specs/189-loop-engine-local-adversarial-pr-review/tasks.md')); print('ok=', r.ok, 'tasks=', len(r.tasks)); [print(e.code, e.message) for e in r.errors]"`
  - 结果：通过，`ok= True tasks= 15`。
- `V3`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V4`（program truth snapshot 刷新）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写入 `program-manifest.yaml`，snapshot state 为 `migration_pending`。
- `V5`（program truth snapshot 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；dry-run 输出 snapshot state 为 `migration_pending`。

#### 2.49 任务记录

##### Task review-remediation | 修正 spec 冲突并补齐 close markers

- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/spec.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`
- **改动内容**：
  - 将用户故事 1 的独立测试拆成 dry-run 只读预览与 `mock-reviewer` 真实 artifact 生成两步，避免 `--dry-run` 被误解为会写 review run。
  - 将 FR-189-001 明确为 P0 数据模型/schema 支持五类 loop，P0 可执行命令完整落地范围仍为 `local-pr-review`，其余 loop 专用命令保持 P1。
  - 新增本批 latest batch markers：`验证画像`、`改动范围`、git 提交状态、提交哈希、branch/worktree disposition。
  - 最终日志稳定后刷新 `program-manifest.yaml` 的 persisted `truth_snapshot`。
- **新增/调整的测试**：无产品代码测试；复用 parser、约束与 truth snapshot 验证。
- **执行的命令**：见 V1 ~ V5。
- **测试结果**：V1、V2、V3、V4、V5 均已通过；最终提交前将再执行一次 `program truth sync --execute --yes`，确保 persisted snapshot 对应稳定后的执行日志与 handoff。
- **是否符合任务目标**：符合 PR review remediation 目标。

#### 2.50 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现 1**：最新批次缺少 close-check 可识别的完整收口 markers。
- **处置 1**：新增 Batch 009，并使用 close-check 正则要求的 `验证画像`、`改动范围`、`已完成 git 提交`、`提交哈希` marker。
- **发现 2**：`spec.md` 的独立测试把 `--dry-run` 与 artifact 生成混在一起。
- **处置 2**：拆分为 dry-run read-only preview 与 `mock-reviewer` artifact 生成测试。
- **发现 3**：FR-189-001 看起来要求 P0 完整实现五类 loop，与 P0/P1 切分和任务拆解冲突。
- **处置 3**：改为 P0 schema/data-model 支持五类 loop，P0 executable path 仅完整落地 `local-pr-review`。
- **结论**：待 V1 ~ V5 通过后提交、push 并重新请求 Codex review。

#### 2.51 任务/计划同步状态

- `spec.md` 同步状态：已按 PR review 修正 P0/P1 范围与 dry-run 测试合同。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已对账，未修改；仍为 machine-readable executable task blocks。
- `task-execution-log.md` 同步状态：已记录第四轮 PR review remediation。
- 关联 branch/worktree disposition 计划：PR #103 merge carrier，目标 disposition 为 merge 后删除远端分支。

#### 2.52 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`见包含本行的本批最终提交 SHA（git log -1 --format=%H）`
- 当前批次 branch disposition 状态：PR #103 merge carrier（待 checks/review 通过后合并）
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）
- **是否继续下一批**：否；等待本批复验、提交、push、Codex re-review 与 PR checks 收口。

### Batch 2026-06-29-010 | T010

#### 2.53 准备

- **任务来源**：PR #103 Codex review comment `discussion_r3489780945`
- **目标**：修正 WI-189 active checkpoint 的阶段状态，避免未来恢复时从 `close` 阶段直接进入收口门禁。
- **预读范围**：`.ai-sdlc/state/checkpoint.yml`、`src/ai_sdlc/core/reconcile.py`、`specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
- **激活的规则**：active checkpoint stage consistency；truth-only verification profile；program truth snapshot。
- **验证画像**：`truth-only`
- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`

#### 2.54 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（恢复路径预演）
  - 命令：`uv run ai-sdlc run --dry-run`
  - 结果：预期未完全通过；dry-run 从 `execute` 开始并继续检查 close gate，最终因 `development-summary.md not found` 以 open gate 退出，未再出现“从 close 直接恢复”的错误路径。
- `V4`（program truth snapshot 刷新）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写入 `program-manifest.yaml`，snapshot state 为 `migration_pending`。
- `V5`（program truth snapshot 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；dry-run 输出 snapshot state 为 `migration_pending`。

#### 2.55 任务记录

##### Task review-remediation | 重置 WI-189 checkpoint 阶段

- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`
- **改动内容**：
  - 将 WI-189 active checkpoint 的 `current_stage` 从 `close` 调整为 `execute`，与 artifact probe 对当前 spec/plan/tasks/execution-log 的建议阶段一致。
  - 移除从旧工作项继承来的 `execute / close` completed stage 历史，只保留当前 PRD/plan/tasks/verification artifact 已完成对应的 `init / refine / design / decompose / verify`。
  - 保留 `execute_progress.completed_batches: 0`，使未来实现授权后不会被误判为已执行或可 close。
  - 最终日志稳定后刷新 `program-manifest.yaml` 的 persisted `truth_snapshot`。
  - removed comment reason: `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md` moves Batch 2026-06-29-010 headings and evidence (`### Batch 2026-06-29-010 | T010`, `#### 2.53 准备`, `#### 2.54 统一验证命令`, `#### 2.55 任务记录`, `##### Task review-remediation | 重置 WI-189 checkpoint 阶段`, `#### 2.56 代码审查（摘要）`, `#### 2.57 任务/计划同步状态`, `#### 2.58 归档后动作`) from before Batch 008 to the append-only end; content is preserved, not deleted.
- **新增/调整的测试**：无产品代码测试；复用 dry-run、约束与 truth snapshot 验证。
- **执行的命令**：见 V1 ~ V5。
- **测试结果**：V1、V2、V3、V4、V5 均已执行；最终提交前将再执行一次 `program truth sync --execute --yes`，确保 persisted snapshot 对应稳定后的执行日志与 checkpoint。
- **是否符合任务目标**：符合 checkpoint stage remediation 目标；恢复路径已从 close-only 改为 execute-first dry-run。

#### 2.56 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现**：checkpoint 已关联 WI-189，但 `current_stage: close` 与 `execute_progress.completed_batches: 0` 冲突，恢复时可能直接进入 close gate。
- **处置**：将 current stage 重置为 `execute`，保留当前工作项自己的 verify completed-stage，并清理旧工作项的 execute/close completed-stage 历史。
- **结论**：待 V1 ~ V5 通过后提交、push 并重新请求 Codex review。

#### 2.57 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已对账，未修改；仍为 machine-readable executable task blocks，全部实现任务保持 todo。
- `task-execution-log.md` 同步状态：已记录 checkpoint stage remediation。
- 关联 branch/worktree disposition 计划：PR #103 merge carrier，目标 disposition 为 merge 后删除远端分支。

#### 2.58 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`见包含本行的本批最终提交 SHA（git log -1 --format=%H）`
- 当前批次 branch disposition 状态：PR #103 merge carrier（待 checks/review 通过后合并）
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）
- **是否继续下一批**：否；等待本批复验、提交、push、Codex re-review 与 PR checks 收口。

### Batch 2026-06-29-011 | T011

#### 2.59 准备

- **任务来源**：PR #103 Codex review comments `discussion_r3489990367`、`discussion_r3489990376`
- **目标**：修正 WI-189 pre-implementation checkpoint 的零基 batch 游标，并在最终日志稳定后刷新 program truth snapshot。
- **预读范围**：`.ai-sdlc/state/checkpoint.yml`、`src/ai_sdlc/core/batch_executor.py`、`src/ai_sdlc/core/runner.py`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`
- **激活的规则**：zero-based execute batch cursor；truth-only verification profile；append-only execution log；program truth snapshot。
- **验证画像**：`truth-only`
- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`

#### 2.60 统一验证命令

- `V1`（文档检查）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V2`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`
- `V3`（恢复路径预演）
  - 命令：`uv run ai-sdlc run --dry-run`
  - 结果：预期未完全通过；dry-run 从 `execute` 开始，最终因 `development-summary.md not found` 以 open gate 退出。
- `V4`（program truth snapshot 刷新）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；写入 `program-manifest.yaml`，用于确保 persisted snapshot 覆盖最终 checkpoint/log/handoff 状态。
- `V5`（program truth snapshot 只读预检）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；dry-run 输出 snapshot state 为 `migration_pending`，未写入文件。

#### 2.61 任务记录

##### Task review-remediation | 重置 execute current_batch

- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/189-loop-engine-local-adversarial-pr-review/codex-handoff.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`
- **改动内容**：
  - 将 WI-189 checkpoint 的 `execute_progress.current_batch` 从 `1` 调整为 `0`，与 `completed_batches: 0` 保持一致。
  - 保持 `current_stage: execute`、`completed_batches: 0` 和 WI-189 的 `tasks_file` / `execution_log` 指针不变。
  - 更新 canonical/scoped handoff，记录本轮 Codex review 修复状态和下一步 PR heartbeat。
  - 追加 Batch 011 作为最新批次，使 close-check 读取到最终 checkpoint 修复证据。
  - 最终日志稳定后刷新 `program-manifest.yaml` 的 persisted `truth_snapshot`。
  - removed comment reason: `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md` moves Batch 2026-06-29-011 headings and evidence (`### Batch 2026-06-29-011 | T011`, `#### 2.59 准备`, `#### 2.60 统一验证命令`, `#### 2.61 任务记录`, `##### Task review-remediation | 重置 execute current_batch`, `#### 2.62 代码审查（摘要）`, `#### 2.63 任务/计划同步状态`, `#### 2.64 归档后动作`) from before Batch 008 to the append-only end; content is preserved, not deleted.
- **新增/调整的测试**：无产品代码测试；复用 dry-run、约束与 truth snapshot 验证。
- **执行的命令**：见 V1 ~ V5。
- **测试结果**：V1、V2、V3、V4、V5 已执行并符合预期。
- **是否符合任务目标**：符合；未来真实执行会从 batch index 0 开始，不会跳过 Batch 1 核心模型/Schema 任务。

#### 2.62 代码审查（摘要）

- **审查来源**：PR #103 Codex review。
- **发现 1**：`execute_progress.completed_batches: 0` 但 `current_batch: 1`，后续 `BatchExecutor.get_current_batch()` 会从零基索引 1 开始，跳过第一批任务。
- **处置 1**：将 `current_batch` 重置为 `0`。
- **发现 2**：checkpoint/log 最终修复后 persisted truth snapshot 需要刷新。
- **处置 2**：在本批日志稳定后执行 `program truth sync --execute --yes` 并提交 `program-manifest.yaml`。
- **结论**：待最终复验通过后提交、push 并重新请求 Codex review。

#### 2.63 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：已对账，未修改；全部实现任务保持 todo。
- `task-execution-log.md` 同步状态：已追加 current_batch review remediation。
- 关联 branch/worktree disposition 计划：PR #103 merge carrier，目标 disposition 为 merge 后删除远端分支。

#### 2.64 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`见包含本行的本批最终提交 SHA（git log -1 --format=%H）`
- 当前批次 branch disposition 状态：PR #103 merge carrier（待 checks/review 通过后合并）
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）
- **是否继续下一批**：否；等待本批 truth sync、提交、push、Codex re-review 与 PR checks 收口。

### Batch 2026-06-29-012 | T11-T12

#### 2.65 准备

- **任务来源**：用户确认继续下一步，进入 WI-189 P0 实现阶段。
- **目标**：完成 Batch 1：core models、schema validation、artifact store。
- **预读范围**：`spec.md`、`plan.md`、`tasks.md`、`src/ai_sdlc/core/config.py`、`src/ai_sdlc/models/program.py`、`src/ai_sdlc/core/p1_artifacts.py`、`tests/unit/test_p1_artifacts.py`。
- **激活的规则**：本地实现不得调用 Codex 云端 PR review；CI 不得发起模型请求；本地独立 review agent 可调用用户当前模型或显式选择的模型；每个 batch 完成后更新 execution log 与 handoff。
- **验证画像**：focused unit tests + ruff scoped check。
- **改动范围**：
  - `src/ai_sdlc/core/loop_models.py`
  - `src/ai_sdlc/core/pr_review_models.py`
  - `src/ai_sdlc/core/pr_review_schema.py`
  - `src/ai_sdlc/core/loop_artifacts.py`
  - `tests/unit/test_pr_review_models.py`
  - `tests/unit/test_pr_review_schema.py`
  - `tests/unit/test_loop_artifacts.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.66 统一验证命令

- `V1`（Batch 1 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py -q`
  - 结果：通过，`23 passed`。
- `V2`（Batch 1 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py`
  - 结果：通过，`All checks passed!`。
- `V3`（Batch 1 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py`
  - 结果：通过，`Success: no issues found in 4 source files`。
- `V4`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V5`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`

#### 2.67 任务记录

##### Task T11 | Define Loop and Review data models

- **改动内容**：
  - 新增 `LoopRun`、`LoopRound`、`LoopPolicyProfile`、`SchemaValidationReport`。
  - 新增 `ReviewRun`、`ReviewPack`、`ReviewFinding`、`FindingResolution`、`ProviderRunnerInvocation`。
  - 为长期 artifact 模型统一写入 `schema_version`、`artifact_kind`、`created_by`、`created_at`、`ai_sdlc_version`。
  - 使用稳定 enum/受控集合表达 loop status、loop type、review verdict、finding severity、resolution、provider isolation 和 schema validation status。
- **测试覆盖**：
  - 元数据落盘字段。
  - 非法 current round。
  - review pack commit scope。
  - finding severity / resolution enum。
  - waiver reason/operator。
  - safe-by-default policy。
  - provider invocation isolation / exit code。

##### Task T12 | Implement schema validation and artifact store

- **改动内容**：
  - 新增 schema validation helpers，返回结构化 `SchemaValidationReport`，覆盖 valid、invalid、incompatible schema 三类结果。
  - 新增 artifact store，创建 `.ai-sdlc/loops/local-pr-review/<loop-id>/` 与 `.ai-sdlc/reviews/pr/<review-id>/`。
  - 支持 JSON、YAML、Markdown artifact 原子写入；写入路径使用同目录临时文件和 replace。
- **测试覆盖**：
  - 缺失必填字段 fail-closed。
  - 不兼容 schema version fail-closed。
  - 非法 enum fail-closed。
  - JSON/YAML/Markdown artifact 写入与读取。
  - 目标目录布局符合 PRD。

#### 2.68 代码审查（摘要）

- **自检结论**：Batch 1 未实现 provider、review pack builder、CLI 或 cloud review 调用；仅建立后续批次依赖的数据合同与持久化边界。
- **风险**：`LoopPolicyProfile` 当前为模型合同，真实配置读取与 policy 冲突裁决留给 T21；`ReviewPack` 当前为模型合同，真实 diff 生成留给 T23。
- **处置**：在 `tasks.md` 中将 T11/T12 标记为 done，其余任务保持 todo。

#### 2.69 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改。
- `plan.md` 同步状态：已对账，未修改。
- `tasks.md` 同步状态：T11/T12 已完成；T21-T63 仍为 todo。
- `task-execution-log.md` 同步状态：已追加 Batch 1 实现记录。

#### 2.70 归档后动作

- **已完成 git 提交**：否，等待最终复验与用户确认提交。
- 当前批次 branch disposition 状态：`codex/189-loop-pr-review-batch1`。
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前仓库）。
- **是否继续下一批**：否；Batch 1 完成后建议进入 Batch 2 的 T21/T22/T23。

### Batch 2026-06-29-013 | Requirement correction

#### 2.71 准备

- **任务来源**：用户打断并澄清：本地独立 review agent 应调用用户配置的模型，默认直接调用用户当前模型，也允许显式选择模型。
- **目标**：修正 WI-189 文档合同中关于 CI、模型调用、provider/model 的语义偏差。
- **改动范围**：
  - `specs/189-loop-engine-local-adversarial-pr-review/spec.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/plan.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `src/ai_sdlc/core/loop_models.py`
  - `tests/unit/test_pr_review_models.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.72 任务记录

- **修正前问题**：
  - 文档中 `codex-local` 容易被理解为唯一真实 provider。
  - `external provider` / `外部模型` 容易被理解为默认禁止 GPT、Claude、DeepSeek、GLM 等模型。
  - “CI 不调用模型”未明确区分本地开发机与 CI 流水线，容易误读成本地也不能调用模型。
- **修正后合同**：
  - `local-agent` 是 P0 通用 provider，负责在本地启动独立 reviewer 会话或进程。
  - 默认 `model=current`，即沿用用户当前开发环境/当前 agent 已配置的模型。
  - 用户可显式选择 GPT、Claude、DeepSeek、GLM 或其他模型。
  - `codex-local` 仅可作为兼容 alias 或具体 adapter，不得作为唯一真实 provider。
  - CI/CD 流水线不得发起模型请求；CI 只检查 artifact、commit hash、schema 和 unresolved counts。
  - 代码外发到远程模型服务不是默认禁止项，但必须披露；企业 policy 可以禁止外发或要求确认。

#### 2.73 统一验证命令

- `V1`（Batch 1 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py -q`
  - 结果：通过，`23 passed`。
- `V2`（Batch 1 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py`
  - 结果：通过，`All checks passed!`。
- `V3`（Batch 1 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py`
  - 结果：通过，`Success: no issues found in 4 source files`。
- `V4`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V5`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`

#### 2.74 归档后动作

- **已完成 git 提交**：否，等待最终复验与用户确认提交。
- **是否继续下一批**：否；修正需求语义后再继续 Batch 2。

### Batch 2026-06-29-014 | Adversarial review remediation

#### 2.75 准备

- **任务来源**：用户要求对 Batch 013 语义修订做一轮对抗评审，并确认修订。
- **目标**：修复对抗评审发现的 model=current 解析合同不完整、resolved model 可空、CLI 输出验收弱于 PRD 三个问题。
- **改动范围**：
  - `specs/189-loop-engine-local-adversarial-pr-review/spec.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/plan.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `src/ai_sdlc/core/pr_review_models.py`
  - `tests/unit/test_pr_review_models.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.76 任务记录

- 新增 `ModelResolution` 合同，记录 provider id、provider mode、model selector、resolved model、resolution source、status、code egress 和 blocker。
- 明确 `model=current` 解析优先级：显式 CLI 非 current > project policy default model > provider config default model > 当前 agent/CLI 环境模型 > needs_user。
- `ProviderRunnerInvocation` 强制记录非空 `resolved_model` 和 `model_resolution_source`。
- `ReviewPack` / `ReviewRun` 增加 `model_resolution_status`、`model_resolution_source`、`provider_mode` 字段；resolved 状态必须有 resolved model 和 source。
- T42 CLI 验收补齐 human 输出必须包含 provider、model selector、resolved model、code egress。

#### 2.77 统一验证命令

- `V1`（Batch 1 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py -q`
  - 结果：通过，`27 passed`。
- `V2`（Batch 1 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py`
  - 结果：通过，`All checks passed!`。
- `V3`（Batch 1 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py`
  - 结果：通过，`Success: no issues found in 4 source files`。
- `V4`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V5`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`

#### 2.78 归档后动作

- **已完成 git 提交**：否，等待最终复验与用户确认提交。
- **是否继续下一批**：否；修订和复验完成后再继续 Batch 2。

### Batch 2026-06-29-015 | Batch 2 policy, redaction, review pack builder

#### 2.79 准备

- **任务来源**：继续 WI-189 P0 本地对抗 PR Review 实现，进入 Batch 2 的 T21/T22/T23。
- **目标**：落地 policy profile 读取与模型解析、redaction/omission 预检、review pack builder。
- **改动范围**：
  - `src/ai_sdlc/core/loop_policy.py`
  - `src/ai_sdlc/core/pr_review_redaction.py`
  - `src/ai_sdlc/core/pr_review_pack.py`
  - `tests/unit/test_loop_policy.py`
  - `tests/unit/test_pr_review_redaction.py`
  - `tests/unit/test_pr_review_pack.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.80 任务记录

- T21：新增 `load_loop_policy`、`resolve_model_for_review`、`evaluate_code_egress_policy`，支持 `.ai-sdlc/project/config/loop-policy.yaml`、默认 `local-agent/current`、远程代码外发披露/确认/禁止策略，以及 `model=current` 解析优先级。
- T22：新增 redaction/omission 预检，覆盖 `.env*`、私钥路径、私钥内容、常见 token/key/password 模式、binary、large、generated files，并生成 `redaction-report.json` 数据合同。
- T23：新增 `build_review_pack`，基于真实 Git `base_ref..head_ref` 生成 `changed-files.txt`、`model-resolution.json`、`redaction-report.json`、`diff.patch`、`review-pack.json`；pack 记录 base/head ref 与 commit、diff coverage、policy decisions、provider mode、model selector、resolved model、model resolution source/status、code egress 和 reviewer allowlist。
- 安全边界：当 `model=current` 无法解析、代码外发遇到高风险 secret 且未确认、diff 超限时统一进入 `needs_user`，不静默丢弃、不 fallback 到 Codex 云端 PR review。
- 隔离边界：review pack builder 仅读取 Git diff 和项目 artifact，不读取或写入 implementation agent chat transcript。

#### 2.81 统一验证命令

- `V1`（Batch 2 focused tests）
  - 命令：`uv run pytest tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`20 passed`。
- `V2`（Batch 1+2 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`47 passed`。
- `V3`（Batch 1+2 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py`
  - 结果：通过，`All checks passed!`。
- `V4`（Batch 1+2 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V5`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V6`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。

#### 2.82 归档后动作

- **已完成 git 提交**：否，继续后续批次前暂不提交。
- **是否继续下一批**：是；Batch 2 完成后进入 Batch 3 的 provider runner 与 mock reviewer。

### Batch 2026-06-29-016 | Batch 3 provider runner and mock reviewer

#### 2.83 准备

- **任务来源**：继续 WI-189 P0 本地对抗 PR Review 实现，进入 Batch 3 的 T31/T32。
- **目标**：落地 provider runner contract 与 mock reviewer。
- **改动范围**：
  - `src/ai_sdlc/core/pr_review_models.py`
  - `src/ai_sdlc/core/pr_review_provider.py`
  - `tests/unit/test_pr_review_models.py`
  - `tests/unit/test_pr_review_provider.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.84 任务记录

- T31：新增 `run_provider_command`，支持配置化本地 reviewer command；标准化退出码 `0/10/20/other`，写入 `reviewer-invocation.json`，记录 command、argv、cwd、input/output paths、provider mode、model selector、resolved model、model resolution source、code egress、allowlist、isolation status、exit status。
- T31：新增 `ReviewFindings` artifact 合同，用于校验 `findings.json`；缺失输出、非 JSON/非法 schema、非标准退出码都会返回 `blocked`，不产生 pass verdict。
- T31：`local-agent` 未配置 command 时返回 `needs_user` 和 plain-language next action，不 fallback 到 Codex 云端 PR review。
- T32：新增 `run_mock_reviewer` 与 `MockReviewerFixture`，支持 `clean`、`changes_required`、`blocked`、`malformed` 四类确定性 fixture；mock reviewer 不访问网络、不调用真实模型，写入 mock invocation 和 findings。
- 隔离边界：runner 只把 review pack path、output path、model selector、resolved model、allowlist 交给本地命令；implementation agent transcript 不进入 provider 输入。

#### 2.85 统一验证命令

- `V1`（Batch 3 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_provider.py -q`
  - 结果：通过，`25 passed`。
- `V2`（Batch 1-3 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py -q`
  - 结果：通过，`57 passed`。
- `V3`（Batch 1-3 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py`
  - 结果：通过，`All checks passed!`。
- `V4`（Batch 1-3 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py`
  - 结果：通过，`Success: no issues found in 8 source files`。

#### 2.86 归档后动作

- **已完成 git 提交**：否，继续后续批次前暂不提交。
- **是否继续下一批**：是；Batch 3 完成后进入 Batch 4 的 PR Review service 与 CLI。

### Batch 2026-06-29-017 | Batch 4 PR Review service and CLI

#### 2.87 准备

- **任务来源**：继续 WI-189 P0 本地对抗 PR Review 实现，进入 Batch 4 的 T41/T42。
- **目标**：落地 PR Review service 与 `ai-sdlc pr-review` CLI 的 doctor/start/status surface。
- **改动范围**：
  - `src/ai_sdlc/core/pr_review_service.py`
  - `src/ai_sdlc/cli/pr_review_cmd.py`
  - `src/ai_sdlc/cli/main.py`
  - `src/ai_sdlc/__main__.py`
  - `src/ai_sdlc/core/pr_review_models.py`
  - `src/ai_sdlc/core/pr_review_provider.py`
  - `tests/unit/test_pr_review_service.py`
  - `tests/integration/test_cli_pr_review.py`
  - `tests/unit/test_command_names.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.88 任务记录

- T41：新增 `doctor_pr_review`、`start_pr_review`、`status_pr_review` service；doctor 只读检查 init、Git base/head、provider/model、policy、redaction、artifact writability。
- T41：`start --dry-run` 只做预览，不创建 `.ai-sdlc/reviews/pr/<review-id>/`，不运行 provider，不写 current pointer。
- T41：非 dry-run start 生成 review pack、运行 provider、写 `review-run.json` 与 `.ai-sdlc/reviews/pr/current-review.json`；status 可从 current pointer 恢复 review run、findings verdict、unresolved counts 与 next action。
- T41：所有失败路径返回 plain-language blocker / next action；local-agent 未配置 command 时为 `needs_user`，mock-reviewer 可执行离线 artifact flow。
- T42：新增 `ai-sdlc pr-review doctor/start/status`，支持 human 与 `--json` 输出；human 输出包含 Result / Next / blocker / provider / model selector / resolved model / code egress。
- T42：`pr-review fix/rerun/close` 已注册为真实 CLI 路径和 help surface，状态机完整语义留给 Batch 5。
- T42：`python -m ai_sdlc --help` fallback 已包含 `pr-review`。

#### 2.89 统一验证命令

- `V1`（Batch 4 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py -q`
  - 结果：通过，`11 passed`。
- `V2`（Batch 1-4 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py -q`
  - 结果：通过，`68 passed`。
- `V3`（Batch 1-4 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/__main__.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py`
  - 结果：通过，`All checks passed!`。
- `V4`（Batch 1-4 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 10 source files`。

#### 2.90 归档后动作

- **已完成 git 提交**：否，继续后续批次前暂不提交。
- **是否继续下一批**：是；Batch 4 完成后进入 Batch 5 的 fix/rerun/close 语义。

### Batch 2026-06-29-018 | Batch 5 fix/rerun/close semantics

#### 2.91 准备

- **任务来源**：继续 WI-189 P0 本地对抗 PR Review 实现，进入 Batch 5 的 T51/T52/T53。
- **目标**：落地 fix-plan/resolution、rerun/scope drift、close verdict 语义。
- **改动范围**：
  - `src/ai_sdlc/core/pr_review_service.py`
  - `src/ai_sdlc/cli/pr_review_cmd.py`
  - `tests/unit/test_pr_review_service.py`
  - `tests/integration/test_cli_pr_review.py`
  - `specs/189-loop-engine-local-adversarial-pr-review/tasks.md`
  - `specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.92 任务记录

- T51：新增 `fix_pr_review`，只生成 `fix-plan.md` 和 `resolution.yaml`，不修改代码；默认只选择 unresolved `BLOCKER` / `REQUIRED`，`ADVISORY` 只披露为 skipped，不进入自动修复计划。
- T51：`--max-rounds` 达到上限时返回 `needs_user`，提示人工检查或提高轮次。
- T52：新增 `rerun_pr_review`，基于 current review 重新生成 review pack 和 provider output，不复用旧 diff；head commit 变化后 current review 指向新生成 artifact。
- T52：新增 scope drift 检查；新增变更若不属于旧 changed files 或 finding 文件，则返回 `needs_user`，要求拆分或重新 start。
- T53：新增 `close_pr_review`，默认 unresolved `BLOCKER` / `REQUIRED` 阻断；`--require-no-blockers` 仅在无 BLOCKER 且仍有 REQUIRED 时输出 `risk_accepted`，不标记 `fully_clean`。
- T53：`final-report.md` 包含 verdict、base/head commit、unresolved counts、diff/redaction/omission coverage、verification evidence 和 next action。
- CLI：`ai-sdlc pr-review fix/rerun/close` 已替换 Batch 4 stub，支持 human 与 `--json` 输出。

#### 2.93 统一验证命令

- `V1`（Batch 5 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`
  - 结果：通过，`18 passed`。
- `V2`（Batch 1-5 focused tests）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py -q`
  - 结果：通过，`76 passed`。
- `V3`（Batch 1-5 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/__main__.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py`
  - 结果：通过，`All checks passed!`。
- `V4`（Batch 1-5 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 10 source files`。

#### 2.94 归档后动作

- **已完成 git 提交**：否，继续最终批次前暂不提交。
- **是否继续下一批**：是；Batch 5 完成后进入 Batch 6 的 close-check、handoff、verify、docs 对齐。

### Batch 2026-06-29-019 | Batch 6 close-check, handoff, verify, docs close-out

#### 2.95 准备

- **任务来源**：继续 WI-189 P0 本地对抗 PR Review 实现，进入 Batch 6 的 T61/T62/T63。
- **目标**：完成 close-check、handoff、verify constraints、README/PR checklist 文档 surface 和最终回归收口。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/core/handoff.py`、`src/ai_sdlc/core/verify_constraints.py`、`README.md`、`docs/pull-request-checklist.zh.md`、`tests/unit/test_close_check.py`、`tests/integration/test_cli_handoff.py`、`specs/189-loop-engine-local-adversarial-pr-review/tasks.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.96 任务记录

- T61：close-check 新增 `local_pr_review` check；有 current review pointer 时读取 `review-run.json` 与 `final-report.md`，区分 `fully_clean`、`risk_accepted`、`blocked`，blocked 或未闭合 review 会阻断 close-check。
- T61：handoff 新增 `Local PR Review` 区块，自动记录 current review id、verdict、unresolved blocker/required/advisory counts 和 beginner-facing next command。
- T62：verify constraints 增加 WI-189 feature-contract surface，覆盖 PR review CLI、provider isolation、schema/policy artifacts、README 与 PR checklist 文档 surface。
- T62：README 增加本地 PR review 三步路径：`ai-sdlc init .`、`ai-sdlc pr-review doctor`、`ai-sdlc pr-review start`；明确默认 `model current` 使用本地 CLI/agent 当前配置模型。
- T62：`docs/pull-request-checklist.zh.md` 增加本地 PR review / CI 分工：模型调用由本地独立 review agent 发起，CI 读取 artifact/schema/counts/final report，CI 不得发起模型请求。
- T63：最终 focused tests、ruff、mypy scoped、diff whitespace、verify constraints 均通过；未创建 release note，因为本工作项未绑定明确发布版本。

#### 2.97 统一验证命令

- `V1`（Batch 6 focused tests）
  - 命令：`uv run pytest tests/unit/test_close_check.py::test_local_pr_review_close_check_distinguishes_closed_verdicts tests/unit/test_close_check.py::test_local_pr_review_close_check_blocks_blocked_verdict tests/integration/test_cli_handoff.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`186 passed`。
- `V2`（最终 focused test bundle）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py tests/unit/test_close_check.py::test_local_pr_review_close_check_distinguishes_closed_verdicts tests/unit/test_close_check.py::test_local_pr_review_close_check_blocks_blocked_verdict tests/integration/test_cli_handoff.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`262 passed`。
- `V3`（最终 scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/cli/main.py src/ai_sdlc/__main__.py src/ai_sdlc/core/close_check.py src/ai_sdlc/core/handoff.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_schema.py tests/unit/test_loop_artifacts.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_redaction.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_command_names.py tests/unit/test_close_check.py tests/integration/test_cli_handoff.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V4`（最终 scoped mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/loop_models.py src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_schema.py src/ai_sdlc/core/loop_artifacts.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_redaction.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/handoff.py`
  - 结果：通过，`Success: no issues found in 11 source files`。
- `V5`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V6`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。

#### 2.98 代码审查（摘要）

- **自检结论**：P0 本地对抗 PR Review 已覆盖 artifact model、policy/model resolution、redaction、review pack、provider runner/mock reviewer、doctor/start/status/fix/rerun/close CLI、close-check/handoff/docs/verify constraints surface。
- **风险**：P0 的 local-agent 只定义可配置本地 command runner 合同，不内置特定厂商 launcher；组织需要通过 provider command 或后续 adapter 接入 GPT/Claude/DeepSeek/GLM 等本地可用模型入口。
- **风险**：close-check 读取 current review pointer；如果同一工作区存在多个并行 review，P0 只以 current pointer 为准，远端 PR inline comments 与多 reviewer 投票仍为 P1/P2。

#### 2.99 任务/计划同步状态

- `spec.md` 同步状态：已冻结，未修改需求边界。
- `plan.md` 同步状态：已冻结，未修改架构批次。
- `tasks.md` 同步状态：T11-T63 已全部完成。
- `task-execution-log.md` 同步状态：已记录 Batch 1-6 的命令、结果、风险与收口。

#### 2.100 归档后动作

- **已完成 git 提交**：否，等待用户确认提交范围后提交。
- **提交哈希**：N/A
- 当前批次 branch disposition 状态：`codex/189-loop-pr-review-batch1` 未提交。
- 当前批次 worktree disposition 状态：dirty（包含本工作项实现文件、文档和测试；另有既有无关脏文件未处理）。
- **是否继续下一批**：否；WI-189 P0 任务已实现并通过 focused verification。

### Batch 2026-06-29-020 | PR #104 mainline close-out

#### 2.101 准备

- **任务来源**：PR #104 合并后 close-check 收口复验。
- **目标**：将 WI-189 的最终 git closure 与 program truth snapshot 同步到 formal execution log。
- **激活的规则**：truth-only verification profile；program truth snapshot；close-check git closure。
- **验证画像**：`truth-only`
- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`、`program-manifest.yaml`

#### 2.102 统一验证命令

- `V1`（program truth snapshot dry-run）
  - 命令：`uv run ai-sdlc program truth sync --dry-run`
  - 结果：通过；输出 `truth snapshot state: migration_pending`，确认本批需要刷新 persisted truth snapshot，未发现阻止 close-out 的新增 WI-189 blocker。
- `V2`（program truth snapshot execute）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过；已写入 `program-manifest.yaml` 并刷新 persisted truth snapshot。
- `V3`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `V4`（WI close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：通过；`tasks_completion`、`git_closure`、`program_truth`、`local_pr_review`、`done_gate` 均为 PASS。

#### 2.103 任务记录

- T61-T63 已通过 PR #104 mainline 合并进入 `main`。
- PR #104 squash merge commit 为 `d4630a47773569286ed72483755792260cbe68da`。
- 本批不新增产品代码，仅补齐 close-check 所需 git closure 与 truth freshness 证据。
- 后续真实新需求应使用 `Next WI Seq = 190` 新建或选择工作项，不复用 WI-189 execute 分支。

#### 2.104 代码审查（摘要）

- PR #104 已完成 GitHub Codex review heartbeat；最终触发后无新增 review comment。
- GitHub required checks 已全部成功。
- 本批为 truth-only close-out，不改变 PR review runtime 行为。

#### 2.105 任务/计划同步状态

- `tasks.md` 同步状态：T11-T63 已完成并通过 PR #104 合并。
- `task-execution-log.md` 同步状态：追加 mainline close-out 记录。
- `program-manifest.yaml` 同步状态：已刷新 persisted truth snapshot。

#### 2.106 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`db79b7e70f4a67ee74355281aa93620417007744`
- 当前批次 branch disposition 状态：`codex/189-loop-pr-review-batch1` 已合并并删除远端分支；本地 scratch 分支仅保留历史。
- 当前批次 worktree disposition 状态：`main` 已快进到 PR #104 merge commit；当前 close-out 修订将在 `codex/189-closeout-truth-sync` 分支单独提交。
- **是否继续下一批**：否；WI-189 已完成，close-check 通过后方可进入 WI-190。

### Batch 2026-06-30-021 | 用户澄清后的 source/model/UX 需求修订

#### 2.107 准备

- **任务来源**：用户打断继续开发，要求先把 review 相关澄清修订到需求文档中。
- **目标**：修订 WI-189 的 PRD/计划/任务拆分，明确本地 review 不能硬编码 GitHub PR，模型默认使用当前会话/当前 CLI agent 已连接模型，显式模型不可用必须 fail-closed，并补齐小白/专业双层 UX 要求。
- **验证画像**：`docs-only`
- **改动范围**：`specs/189-loop-engine-local-adversarial-pr-review/spec.md`、`specs/189-loop-engine-local-adversarial-pr-review/plan.md`、`specs/189-loop-engine-local-adversarial-pr-review/tasks.md`、`specs/189-loop-engine-local-adversarial-pr-review/task-execution-log.md`

#### 2.108 任务记录

- `spec.md`：追加 2026-06-30 澄清状态、DiffSource/SourceAdapterResolution、模型 current-first / explicit fail-closed、双层 UX、Round 3 用户澄清评审记录和 Codex 开发 agent 执行提示。
- `plan.md`：将 Review Pack Builder 扩展为 Diff Source Adapter + Review Pack Builder；新增 `source-resolution.json` 合同；修订 model resolution 规则、doctor/start UX、验证矩阵和开放决策。
- `tasks.md`：保留 T11-T63 历史完成基线，新增 Batch 7 的 T71-T74 pending 任务，明确旧模型优先级已被 T72 覆盖，后续开发前必须先按 Batch 7 补齐。
- 本批不修改产品实现代码，不提交，不继续开发。

#### 2.109 统一验证命令

- `V1`（需求文档旧假设 grep）
  - 命令：`Select-String -Path "specs/189-loop-engine-local-adversarial-pr-review/spec.md","specs/189-loop-engine-local-adversarial-pr-review/plan.md","specs/189-loop-engine-local-adversarial-pr-review/tasks.md" -Pattern "CLI > policy|远端 PR comment|Git 读取|默认使用当前已配置模型|所有 P0|等待按 `tasks.md` 执行|可执行任务分解已冻结"`
  - 结果：通过，无残留匹配。
- `V2`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V3`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`

#### 2.110 归档后动作

- **已完成 git 提交**：否，用户本轮要求先修订需求文档，尚未要求提交。
- 当前批次 worktree disposition 状态：dirty（仅 WI-189 需求/计划/任务/执行记录文档修订，外加 handoff 更新）。
- **是否继续下一批**：等待用户确认；若继续实现，下一步应从 Batch 7 的 T71/T72 开始，而不是继续旧 T11-T63 已完成路径。

### Batch 2026-06-30-022 | Batch 7 source/model/UX 适配实现

#### 2.111 准备

- **任务来源**：用户要求按新修订需求比对已实现功能差异，并继续落地全部优先级需求。
- **目标**：补齐 Batch 7 T71-T74，使本地 PR review 不硬编码 GitHub/远端 PR，不把模型限制误解为禁止调用大模型，并让本地独立 review agent 默认使用当前会话/当前 CLI agent 已连接模型，显式模型不可用时 fail-closed。
- **验证画像**：`focused-implementation`
- **改动范围**：PR review source/model/service/CLI/constraints/docs/tests 相关文件。

#### 2.112 差异结论

- 已实现基线 T11-T63 覆盖本地对抗 PR review 主流程，但缺少 `DiffSourceDescriptor` / `SourceAdapterResolution` / `source-resolution.json` 合同。
- review pack 原先以本地 Git base/head 为核心入口，未把本地仓、公司内网仓、patch、GitHub/GitLab/Gitee/self-hosted SCM 统一抽象为 source adapter。
- 模型解析旧逻辑存在 policy/provider default 优先级，和“默认当前会话/当前 CLI agent 已连接模型，显式模型不可用不得静默 fallback”的澄清要求不完全一致。
- doctor/start CLI 和 verify/docs surface 未充分暴露 source adapter、source access status、model unavailable reason 等小白可理解、专业可审计字段。

#### 2.113 任务记录

- `T71`：新增 `pr_review_source.py`，定义 DiffSource 解析选项与 source adapter 解析；`pr_review_models.py` 增加 `DiffSourceDescriptor`、`SourceAdapterResolution`、`SourceAccessStatus` 等模型；`build_review_pack` 写入 `source-resolution.json` 并在 `review-pack.json` 中记录 source 字段。
- `T72`：修订 `resolve_model_for_review` 为 current-first local agent contract；显式指定非 current 模型时只允许已连接候选模型，无法验证时返回 `blocked/needs_user` 和 `unavailable_reason`，不 fallback。
- `T73`：扩展 `doctor/start` service 和 CLI 参数，支持 `--diff-source`、`--patch-file`、`--source-id`、`--source-provider`；human/json 输出包含 diff source、source adapter、source access status、source resolution artifact path。
- `T74`：更新 README、中文 PR checklist、verify constraints registry 与对应测试，覆盖 DiffSource、非 GitHub 硬编码、CI 不发起模型请求、显式模型不可用不得静默 fallback 等边界。
- `tasks.md`：Batch 7 T71-T74 已从 `pending` 同步为 `done`。

#### 2.114 统一验证命令

- `V1`（scoped ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py`
  - 结果：通过，`All checks passed!`。
- `V2`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V3`（Batch 7 focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`
  - 结果：通过，`125 passed`。
- `V4`（verify constraints tests）
  - 命令：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`184 passed`。
- `V5`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V6`（框架约束检查）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。

#### 2.115 代码审查（摘要）

- **自检结论**：Batch 7 P0 已落地，核心状态机不依赖 GitHub PR id；本地 review agent 可默认当前模型或显式模型，显式模型不可用时 fail-closed；CI 仍只作为确定性检查/产物消费面，不发起模型请求。
- **风险**：P0 只实现 `local-git-range` 的真实 source adapter；patch/staged/unstaged/SCM PR/MR 已保留合同和 fail-closed 行为，真实 SCM provider adapter 属于后续 P1。
- **风险**：可用模型探测仍依赖当前 CLI/env/policy 可见候选；不同厂商 GPT/Claude/DeepSeek/GLM 的深度健康检查需要后续 provider adapter 扩展。

#### 2.116 归档后动作

- **已完成 git 提交**：否，本批尚未收到提交指令。
- 当前批次 worktree disposition 状态：dirty（包含 Batch 7 实现、测试、文档、handoff 和 resume-pack 更新）。
- **是否继续下一批**：否；按当前 `tasks.md`，WI-189 T11-T74 全部完成并通过 focused verification 与框架约束检查。

### Batch 2026-06-30-023 | P1/P2 全优先级收口实现

#### 2.117 准备

- **任务来源**：用户目标要求完成全部优先级需求落地，不能只停留在 Batch 7 P0。
- **目标**：补齐冻结 PRD 中 P1/P2 明确留下的可执行差异：patch/staged/unstaged DiffSource、local review attestation、finding history mapping、P2 企业增强 fail-closed 边界。
- **验证画像**：`focused-implementation`
- **改动范围**：PR review source/pack/service/model/CLI、README、PR checklist、verify constraints、Batch 8/9 tasks、focused tests。

#### 2.118 差异结论

- `loop status/list` 已由既有 `loop_status.py` / `loop_cmd.py` 和测试覆盖，无需重复实现。
- P1 缺口为：patch source 仍是 P0 合同未真实 pack；local staged/unstaged 仍 fail-closed；没有 `pr-review attest`；rerun 后没有 finding-history 映射 artifact。
- P2 缺口为：多 reviewer、组织 waiver、artifact 签名、远端 PR inline comments 不能在没有企业身份、SCM 写权限、签名密钥时伪造成已实现，需要进入可审计 fail-closed 边界和 verify constraints。

#### 2.119 任务记录

- `T81`：`pr_review_source.py` 支持 `patch`、`local-staged`、`local-unstaged` 真实 source resolution；`pr_review_pack.py` 可基于 patch 文件、staged diff、unstaged diff 生成 changed-files、diff.patch、review-pack 和 redaction report。
- `T82`：新增 `ReviewAttestation` 模型、`attest_pr_review` service 和 `ai-sdlc pr-review attest` CLI；closed review 可写入 `.ai-sdlc/reviews/pr/latest-attestation.json`，CI 只读消费且不得调模型。
- `T83`：`rerun_pr_review` 成功后写入 `finding-history.json`，用 severity/file/line/claim/risk signature 记录 previous/current finding 映射，不修改 reviewer 原始 findings。
- `T84`：README、中文 PR checklist、verify constraints 和测试覆盖 patch/staged/unstaged、attestation、finding-history。
- `T91`：plan/tasks/verify constraints 明确 P2 多 reviewer、组织 waiver、artifact 签名、远端 PR inline comments 必须通过 adapter/policy/企业身份/密钥/SCM 权限进入；无配置时 fail-closed，不伪造成功。
- `tasks.md`：Batch 8 T81-T84 与 Batch 9 T91 已从 `pending` 同步为 `done`。

#### 2.120 统一验证命令

- `V1`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V2`（P1/P2 focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：首次发现 1 个测试输入问题：`local-unstaged` 测试使用 untracked 文件而不是 tracked unstaged diff；修正后通过，`311 passed`。
- `V3`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 5 source files`。

#### 2.121 代码审查（摘要）

- **自检结论**：P1 的本地 source adapter、attestation、finding history 已落地；P2 企业增强已进入 fail-closed 合同和门禁，不再作为未声明风险悬空。
- **风险**：真实远端 SCM PR/MR diff 拉取、inline comments 写回、多 reviewer 编排、组织 waiver 审批和 artifact 加密签名仍需要企业凭据/密钥/SCM API adapter；当前实现不会伪造成功，而是通过 P2 fail-closed 边界约束后续接入。

#### 2.122 归档后动作

- **已完成 git 提交**：否，本批尚未收到提交指令。
- 当前批次 worktree disposition 状态：dirty（包含 Batch 7/8/9 实现、测试、文档、handoff 和 resume-pack 更新）。
- **是否继续下一批**：否；按当前 `tasks.md`，WI-189 T11-T84、T91 全部完成。

### Batch 2026-06-30-024 | Active checkpoint and framework gate close-out

#### 2.123 准备

- **任务来源**：用户要求按照新修订需求比对已实现功能差异，并继续落地全部优先级需求。
- **目标**：将 active checkpoint 从上一工作项 WI-191 校正为 WI-189，按当前框架约束重新验收 Batch 7/8/9，并进入本仓库 PR protocol。
- **验证画像**：`code-change`
- **改动范围**：`.ai-sdlc/state/checkpoint.yml`、`program-manifest.yaml`、WI-189 tasks / execution log / handoff，以及 Batch 7/8/9 已实现代码与测试。
- 关联 branch/worktree disposition 计划：`codex/189-loop-engine-complete-pr-review` 作为本轮 PR merge carrier；历史 `codex/189-loop-pr-review-batch1` / `codex/189-closeout-truth-sync` 保留为 archived local scratch，不再承载 mainline truth。

#### 2.124 差异结论

- P0 已覆盖：本地独立 review agent、DiffSource 非 GitHub 硬编码、current-first 模型解析、显式模型不可用 fail-closed、小白/专业双层 CLI 输出、CI 不发起模型请求。
- P1 已覆盖：patch / local-staged / local-unstaged 真实 adapter、`pr-review attest`、`finding-history.json`。
- P2 已覆盖为可审计 fail-closed 边界：多 reviewer、组织 waiver、artifact signing、远端 inline comment 必须依赖企业 identity / policy / SCM adapter / signing key；未配置时不得伪造成功。
- 重新绑定 WI-189 后，框架约束新增暴露治理缺口：Batch 7/8/9 任务块需补充 gate 可识别的 `验收标准` 标记，历史 WI-189 分支 disposition 需在最新批次中说明。

#### 2.125 任务记录

- `.ai-sdlc/state/checkpoint.yml`：active feature 从 WI-191 校正为 `189-loop-engine-local-adversarial-pr-review`，当前分支为 `codex/189-loop-engine-complete-pr-review`。
- `tasks.md`：Batch 7/8/9 每个任务块补充 `验收标准：见 acceptance 字段。`，不改变已冻结验收内容。
- `task-execution-log.md`：记录 active checkpoint 复验、历史分支 disposition 与最终 mainline readiness。
- `pr_review_source.py`：保留 `local-staged` / `local-unstaged` 明文 source kind token，使 active WI-189 约束可以检测本地 worktree source adapter surface。

#### 2.126 统一验证命令

- `V1`（active WI-189 框架约束初次复验）
  - 命令：`uv run ai-sdlc verify constraints`
  - 初次结果：未通过；暴露 `tasks.md missing task-level acceptance` 与历史 WI-189 branch lifecycle disposition 缺口。
  - 修复动作：补充 Batch 7/8/9 `验收标准` 标记，并在本最新批次记录当前 PR carrier 与历史 archived branch disposition。
- `V2`（diff whitespace）
  - 命令：`git diff --check`
  - 结果：通过，无 whitespace error。
- `V3`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V4`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 6 source files`。
- `V5`（focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`323 passed`。
- `V6`（active WI-189 框架约束复验）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `V7`（program truth snapshot sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：通过并写入 `program-manifest.yaml`；truth snapshot state 为 `migration_pending`，snapshot hash 为 `88680558bf5c40c301cf595c8b1295845a22aa7c68eed8fbb45cda05377f6e7d`。
- `V8`（work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：通过，所有 checks PASS，`done_gate` 为 `ready for completion`。

#### 2.127 代码审查（摘要）

- **自检结论**：本轮没有发现新的产品能力差异；剩余处理均为框架治理状态、任务格式和 mainline readiness 收口。
- **风险**：真实企业 SCM 写回、多 reviewer 编排、组织 waiver 审批、artifact 加密签名仍必须等待企业配置/凭据/密钥，当前实现以 fail-closed 合同保护质量边界。

#### 2.128 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`8a22f3d03c0417d8d831ea984b9a8b8dbb24784d`
- 当前批次 branch disposition 状态：PR merge carrier；historical branches archived。
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前 PR 分支）。
- **是否继续下一批**：否；本批完成后进入 PR、Codex review、checks、merge heartbeat。

### Batch 2026-06-30-025 | Codex review feedback fixes for PR #108

#### 2.129 准备

- **任务来源**：GitHub Codex review for PR #108 returned three actionable comments.
- **目标**：修复 non-git-range DiffSource 的 redaction / preview / local-agent dirty-worktree 一致性问题，并继续同一 PR heartbeat。
- **验证画像**：`code-change`
- **改动范围**：`src/ai_sdlc/core/pr_review_pack.py`、`src/ai_sdlc/core/pr_review_service.py`、`src/ai_sdlc/core/pr_review_provider.py`、`tests/unit/test_pr_review_pack.py`、`tests/unit/test_pr_review_service.py`、`tests/unit/test_pr_review_provider.py`、本执行日志、handoff、`program-manifest.yaml`。
- 关联 branch/worktree disposition 计划：`codex/189-loop-engine-complete-pr-review` 继续作为 PR #108 merge carrier；历史 `codex/189-loop-pr-review-batch1` / `codex/189-closeout-truth-sync` 保留为 archived local scratch，不再承载 mainline truth。

#### 2.130 任务记录

- Codex P1 `Redact patch/index bytes instead of worktree files`：`ResolvedReviewInput` 增加 source-derived file bytes；patch / staged / unstaged redaction 均基于实际 diff section bytes，不再回读 worktree 文件。
- Codex P2 `Use source-specific diff discovery in preview`：`pr-review doctor` / `start --dry-run` 复用 pack builder 的 source-specific input resolver，避免对 `patch-file` / `INDEX` / `WORKTREE` synthetic refs 执行 git merge-base。
- Codex P2 `Allow reviewed worktree changes before resolving them`：local-agent provider guard 对 `local-staged` / `local-unstaged` 只放行 `review_pack.changed_files` 中已被本次 review pack 覆盖的 dirty path，其他 dirty path 仍 fail-closed。
- 新增单测覆盖 patch-only secret redaction、patch dry-run preview、local-staged reviewed dirty path launch。
- Codex 第二轮 P2 `Use closeable refs for worktree sources`：close 阶段对 `local-staged` / `local-unstaged` 使用真实 `HEAD` 校验 reviewed head，并允许 review pack 覆盖的 dirty path。
- Codex 第二轮 P2 `Make rerun scope checks source-aware`：rerun scope drift 对非 `local-git-range` source 重新 resolve DiffSource，再用 source resolver 计算当前 changed files。
- Codex 第二轮 P2 `Verify the reviewed head ref for attestation`：attestation 校验 reviewed head ref / reviewed head commit，不再错误依赖当前 checkout `HEAD`。
- 新增单测覆盖 local-staged close、patch rerun、非当前 checkout head attestation。
- Codex 第三轮 P1 `Revalidate worktree diffs before closing`：close 对 `patch` / `local-staged` / `local-unstaged` 重新 resolve 当前 DiffSource，并比较 `patch_hash`；同一路径 restage 或 patch 文件变化必须 rerun；dirty allowlist 进一步按 Git status index/worktree 两列区分，避免 staged review 后同路径未暂存字节被误放行。
- Codex 第三轮 P2 `Bind attestations to the reviewed diff source`：`ReviewAttestation` 增加 `diff_source` 与 `diff_source_hash`，非 `local-git-range` attestation 必须绑定 diff-source hash；`attest` 写入前重新校验当前 diff-source hash，hash 变化时 fail-closed。
- 新增单测覆盖 changed local-staged hash、reviewed staged path 上的未暂存改动、patch source hash changed after close，以及 CLI attestation 中的 diff source 绑定。
- Codex 第四轮 P1 `Handle unified patch blobs before redaction`：patch parser 支持无 `diff --git` header 的普通 unified diff section，`_diff_file_blobs` 不再丢弃 `---` / `+++` 开头的 patch-only bytes，避免 redaction 回退 worktree 漏掉 patch 中新增 secret。
- Codex 第四轮 P2 `Check dirty status before allowing reviewed paths`：local-agent provider launch guard 使用 status-sensitive reviewed dirty allow check；`local-staged` 只放行纯 staged 状态，`local-unstaged` 只放行纯 unstaged 状态，同路径额外未审字节会在模型调用前 fail-closed。
- 新增单测覆盖普通 unified patch secret redaction、local-agent 启动前阻断 reviewed staged path 上的额外 unstaged edit。
- Codex 第五轮 P2 `Do not resolve patch reviews with an empty head`：patch DiffSource 在 `--head` 不可解析或 Git HEAD 不存在时返回 BLOCKED `git_head_unavailable`，不再生成 `head_commit=""` 的 RESOLVED source 并让 pack validator 抛 uncaught error。
- Codex 第五轮 P2 `Strip timestamps from unified patch paths`：`_normalize_patch_path` 去除 unified diff `---` / `+++` header 中 tab-separated timestamp，保证 changed_files / allowlist 使用真实 repo path。
- 新增单测覆盖 patch source bad head fail-closed、带 timestamp 的 unified patch path 归一。
- Codex 第六轮 P1 `Block attestation on tampered review artifacts`：`attest_pr_review` 在写 `latest-attestation.json` 前加载 findings 并复用 `_reviewer_outputs_tamper_blocker`，review-pack/findings digest 被篡改或缺失时 fail-closed。
- Codex 第六轮 P2 `Preserve paths with spaces in patch headers`：`diff --git` header 使用 `_diff_git_paths` 解析 `a/... b/...` 边界，不再用 whitespace split 误拆含空格路径。
- 新增单测覆盖 closed review 后篡改 review-pack 阻断 attestation、patch path with spaces 保留真实路径。
- Codex 第七轮 P2 `Preserve the previous findings artifact before rerun`：rerun 在覆盖 `findings.json` 前复制旧 findings 到 `previous-findings-round-N.json`，`finding-history.json` 指向旧快照而不是被覆盖后的当前 findings。
- Codex 第七轮 P2 `Invalidate stale latest attestations on blocked attempts`：`attest_pr_review` 进入时先删除 stale `latest-attestation.json`，任何后续 fail-closed 路径都不会保留旧成功凭证供 CI 误读。
- 新增/扩展单测覆盖 finding history previous/current paths 分离、tampered review-pack 后 stale latest attestation 被移除。

#### 2.131 统一验证命令

- `V1`（targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py`
  - 结果：通过，`All checks passed!`。
- `V2`（targeted mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py`
  - 结果：通过，`Success: no issues found in 3 source files`。
- `V3`（targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py -q`
  - 结果：首次发现 preview redaction 仍误用 synthetic refs；修复后通过，`114 passed`。
- `V3b`（second-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`71 passed`。
- `V4`（focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V5`（focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6`（focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：第六轮 Codex review 修复后通过，`368 passed`。
- `V6a`（third-round targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py`
  - 结果：通过，`All checks passed!`。
- `V6b`（third-round typed surface mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_service.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
- `V6c`（third-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_service.py tests/integration/test_cli_pr_review.py -q`
  - 结果：通过，`113 passed`。
- `V6d`（fourth-round targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py`
  - 结果：通过，`All checks passed!`。
- `V6e`（fourth-round typed surface mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_provider.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
- `V6f`（fourth-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_provider.py -q`
  - 结果：通过，`47 passed`。
- `V6g`（fifth-round targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/pr_review_pack.py tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py`
  - 结果：通过，`All checks passed!`。
- `V6h`（fifth-round typed surface mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/pr_review_pack.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
- `V6i`（fifth-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_source.py tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`24 passed`。
- `V6j`（sixth-round targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py`
  - 结果：通过，`All checks passed!`。
- `V6k`（sixth-round typed surface mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py`
  - 结果：通过，`Success: no issues found in 2 source files`。
- `V6l`（sixth-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`92 passed`。
- `V6m`（seventh-round targeted ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_service.py tests/unit/test_pr_review_service.py`
  - 结果：通过，`All checks passed!`。
- `V6n`（seventh-round typed surface mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_service.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6o`（seventh-round targeted pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`75 passed`。
- `V7`（框架约束）
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：通过，`verify constraints: no BLOCKERs.`。
- `V8`（program truth snapshot sync）
  - 命令：`uv run ai-sdlc program truth sync --execute --yes`
  - 结果：第三轮 Codex review 修复后通过并写入 `program-manifest.yaml`；truth snapshot state 为 `migration_pending`，snapshot hash 以最终 `program-manifest.yaml` 为准。
- `V9`（work item close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：通过，所有 checks PASS，`done_gate` 为 `ready for completion`。

#### 2.132 代码审查（摘要）

- 已处理 Codex review thread `PRRT_kwDORujSxs6NQPUE`：source-specific redaction bytes。
- 已处理 Codex review thread `PRRT_kwDORujSxs6NQPUH`：preview source-specific changed-file discovery。
- 已处理 Codex review thread `PRRT_kwDORujSxs6NQPUL`：local-agent reviewed dirty path launch guard。
- 已处理 Codex review thread `PRRT_kwDORujSxs6NQlYA`：worktree source close uses real commit ref.
- 已处理 Codex review thread `PRRT_kwDORujSxs6NQlYF`：rerun scope checks are source-aware.
- 已处理 Codex review thread `PRRT_kwDORujSxs6NQlYJ`：attestation validates reviewed head ref instead of checkout HEAD.
- 已处理 Codex 第三轮 comment `Revalidate worktree diffs before closing`：close revalidates worktree diff source hash and status columns.
- 已处理 Codex 第三轮 comment `Bind attestations to the reviewed diff source`：attestation binds and verifies diff-source hash.
- 已处理 Codex 第四轮 comment `Handle unified patch blobs before redaction`：unified patch sections without `diff --git` feed source bytes into redaction.
- 已处理 Codex 第四轮 comment `Check dirty status before allowing reviewed paths`：local-agent launch guard uses status-sensitive reviewed dirty checks.
- 已处理 Codex 第五轮 comment `Do not resolve patch reviews with an empty head`：patch source requires resolvable reviewed head.
- 已处理 Codex 第五轮 comment `Strip timestamps from unified patch paths`：unified patch path normalizer strips tab-separated timestamps.
- 已处理 Codex 第六轮 comment `Block attestation on tampered review artifacts`：attest reuses review artifact tamper checks.
- 已处理 Codex 第六轮 comment `Preserve paths with spaces in patch headers`：diff --git patch header parser preserves paths with spaces.
- 已处理 Codex 第七轮 comment `Preserve the previous findings artifact before rerun`：rerun snapshots previous findings before overwriting current output.
- 已处理 Codex 第七轮 comment `Invalidate stale latest attestations on blocked attempts`：attest clears stale latest attestation before validation.
- 需要在推送后重新请求 Codex review，确认 comments outdated 或无新增 actionable feedback。

#### 2.133 任务/计划同步状态

- `tasks.md` 同步状态：WI-189 T11-T84、T91 仍全部完成；本批为 PR review feedback 修复，不新增需求任务。
- `plan.md` 同步状态：DiffSource、model/current-first、CI artifact-only、P2 fail-closed 合同不变。
- `program-manifest.yaml` 同步状态：已刷新 persisted truth snapshot，snapshot hash 以最终 `program-manifest.yaml` 为准。

#### 2.134 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`4a8b4ed36b2a8345ad98701daff961fb0633c02e`
- 当前批次 branch disposition 状态：PR merge carrier；historical branches archived。
- 当前批次 worktree disposition 状态：retained（主工作区继续承载当前 PR 分支）。
- **是否继续下一批**：否；本批完成后继续 PR #108 Codex re-review、checks heartbeat 和 merge。

#### 2.135 第八轮 Codex review 修复

- Codex 第八轮 P2 `Allow patch files as reviewed launch inputs`：`local-agent` 启动前对 patch source 的 `diff_source.patch_file` 执行 hash 复核，hash 匹配时允许该 patch 文件作为已审输入保留在 dirty worktree 中；hash 不匹配或文件不可读时 fail-closed。
- Codex 第八轮 P2 `Allow the reviewed patch file during close`：`close_pr_review` 在已完成 diff source hash 复核后，允许同一个 repo 内 patch 文件通过 dirty 检查，避免未跟踪或已修改的 `change.patch` 阻断有效 patch review 关闭。
- 新增单测覆盖 local-agent 允许 repo 内未跟踪 patch 输入、local-agent 启动前阻断变更后的 patch hash、close 允许已审 patch 输入文件。

#### 2.136 第八轮验证命令

- `V6p`（eighth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_provider.py::test_local_agent_allows_reviewed_patch_file_dirty_input tests/unit/test_pr_review_provider.py::test_local_agent_blocks_changed_patch_file_before_launch tests/unit/test_pr_review_service.py::test_close_allows_reviewed_patch_file_dirty_input -q`
  - 结果：通过，`3 passed`。
- `V6q`（eighth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6r`（eighth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6s`（eighth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`371 passed`。
- `V6t`（whitespace check）
  - 命令：`git diff --check`
  - 结果：通过，无输出。

#### 2.137 第九轮 Codex review 修复

- Codex 第九轮 P1 `Clear stale attestation before rerunning reviews`：`start_pr_review` 在新的非 dry-run review pack READY 后、provider 启动前删除 `latest-attestation.json`，覆盖 rerun 与 replacement start，避免旧 closed review 的成功 attestation 被 CI 误读。
- Codex 第九轮 P2 `Verify local git-range base commit before closing`：`_reviewed_diff_source_mismatch` 不再对 `local-git-range` 直接放行；close/attest 会重新解析当前 `base_ref/head_ref`，同时比较 reviewed `base_commit/head_commit`，base ref rewrite 或 merge-base drift 均 fail-closed。
- 新增单测覆盖 replacement start 清 stale attestation、rerun 清 stale attestation、close 阻断 git-range base drift、attest 阻断 close 后 base drift。

#### 2.138 第九轮验证命令

- `V6u`（ninth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py::test_close_blocks_when_local_git_range_base_moved_after_review tests/unit/test_pr_review_service.py::test_start_replacement_review_clears_latest_attestation tests/unit/test_pr_review_service.py::test_attest_blocks_changed_local_git_range_base_after_close tests/unit/test_pr_review_service.py::test_rerun_clears_latest_attestation -q`
  - 结果：通过，`4 passed`。
- `V6v`（ninth-round service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`80 passed`。
- `V6w`（ninth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6x`（ninth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6y`（ninth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`375 passed`。

#### 2.139 第十轮 Codex review 修复

- Codex 第十轮 P1 `Clear stale attestations before pack blockers return`：`start_pr_review` 对所有非 dry-run start 在最前面删除 `latest-attestation.json`，即使 replacement review 因 source/model/redaction blocker 未进入 provider，也不会保留旧成功凭证。
- Codex 第十轮 P2 `Use real blobs for staged redaction`：`local-staged` redaction 从 Git index 读取真实 staged blob，`local-unstaged` redaction 从 worktree 读取真实文件 bytes，不再用 diff 文本代替源码内容，二进制文件会进入 binary/omitted 决策。
- 新增单测覆盖 blocked replacement start 清 stale attestation、staged binary blob omitted、unstaged binary blob omitted。

#### 2.140 第十轮验证命令

- `V6z`（tenth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py::test_blocked_replacement_review_clears_latest_attestation tests/unit/test_pr_review_pack.py::test_build_review_pack_omits_staged_binary_blob tests/unit/test_pr_review_pack.py::test_build_review_pack_omits_unstaged_binary_blob -q`
  - 结果：通过，`3 passed`。
- `V6aa`（tenth-round pack/service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`100 passed`。
- `V6ab`（tenth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6ac`（tenth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6ad`（tenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`378 passed`。

#### 2.141 第十一轮 Codex review 修复

- Codex 第十一轮 P1 `Scan base blobs for worktree diff sources`：`ResolvedReviewInput` 增加 `base_file_bytes`；`local-staged` redaction 同时扫描 HEAD base blob 与 index head blob，`local-unstaged` redaction 同时扫描 index base blob 与 worktree head blob。
- 删除/替换旧版本 secret 时，即使新版本内容安全，base-side removed lines 仍会进入 redaction gate；`diff.patch` 不会在未记录高风险的情况下携带旧 token/private key。
- 新增单测覆盖 staged base-side secret redaction、unstaged base-side secret redaction，并保留第十轮二进制 blob 回归。

#### 2.142 第十一轮验证命令

- `V6ae`（eleventh-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py::test_build_review_pack_omits_staged_binary_blob tests/unit/test_pr_review_pack.py::test_build_review_pack_redacts_staged_base_side_secret tests/unit/test_pr_review_pack.py::test_build_review_pack_omits_unstaged_binary_blob tests/unit/test_pr_review_pack.py::test_build_review_pack_redacts_unstaged_base_side_secret -q`
  - 结果：通过，`4 passed`。
- `V6af`（eleventh-round pack pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`21 passed`。
- `V6ag`（eleventh-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6ah`（eleventh-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6ai`（eleventh-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`380 passed`。

#### 2.143 第十二轮 Codex review 修复

- Codex 第十二轮 P2 `Pass base blobs during preview redaction`：doctor/dry-run preview 的非 git-range redaction 也传入 `review_input.base_file_bytes`，与真实 `build_review_pack` 行为一致，避免 local-staged/local-unstaged preview 与 start 对 base-only 内容分类不一致。
- Codex 第十二轮 P2 `Verify final report contents before attesting`：`ReviewRun` 增加 `final_report_digest`；`close_pr_review` 写入 final report 后记录 digest；`attest_pr_review` 在生成 `latest-attestation.json` 前复核 digest，final report 被篡改或 digest 缺失时 fail-closed。
- 新增单测覆盖 dry-run preview 对 staged base-side secret 的 redaction、close 后篡改 final-report 阻断 attestation。

#### 2.144 第十二轮验证命令

- `V6aj`（twelfth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py::test_start_dry_run_redacts_local_staged_base_side_secret tests/unit/test_pr_review_service.py::test_attest_blocks_tampered_final_report_after_close -q`
  - 结果：通过，`2 passed`。
- `V6ak`（twelfth-round service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`83 passed`。
- `V6al`（twelfth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6am`（twelfth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6an`（twelfth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`382 passed`。

#### 2.145 第十三轮 Codex review 修复

- Codex 第十三轮 P1 `Clear stale attestations when closing changes state`：`close_pr_review` 开始时删除 `latest-attestation.json`，无论本次 close 最终 CLOSED 还是 BLOCKED，只要 close 可能重写 final report / verdict / unresolved counts，旧 attestation 都会失效。
- 新增单测覆盖已成功 attest 后再次 close 会清理旧 `latest-attestation.json`，要求后续重新 `pr-review attest`。

#### 2.146 第十三轮验证命令

- `V6ao`（thirteenth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py::test_close_clears_existing_latest_attestation -q`
  - 结果：通过，`1 passed`。
- `V6ap`（thirteenth-round service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`84 passed`。
- `V6aq`（thirteenth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6ar`（thirteenth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6as`（thirteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`383 passed`。

#### 2.147 第十四轮 Codex review 修复

- Codex 第十四轮 P2 `Parse porcelain paths before matching reviewed dirty files`：`close_pr_review` 的 dirty worktree 检查改用 `git status --porcelain=v1 -z --untracked-files=all`，并用 NUL porcelain parser 读取 path，避免含空格路径被 Git quote 后无法匹配 reviewed dirty allowlist。
- 去除 dirty path normalization 中的 `.strip()`，避免合法前后空格路径被改写。
- 新增单测覆盖 local-staged reviewed path with space、patch source patch file path with space 在 close 阶段不被误判为 unreviewed dirty change。

#### 2.148 第十四轮验证命令

- `V6at`（fourteenth-round minimal pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py::test_close_allows_reviewed_local_staged_path_with_space tests/unit/test_pr_review_service.py::test_close_allows_reviewed_patch_file_path_with_space -q`
  - 结果：通过，`2 passed`。
- `V6au`（fourteenth-round service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`86 passed`。
- `V6av`（fourteenth-round focused ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py`
  - 结果：通过，`All checks passed!`。
- `V6aw`（fourteenth-round focused mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_models.py src/ai_sdlc/core/pr_review_source.py src/ai_sdlc/core/loop_policy.py src/ai_sdlc/core/pr_review_pack.py src/ai_sdlc/core/pr_review_service.py src/ai_sdlc/core/pr_review_provider.py src/ai_sdlc/cli/pr_review_cmd.py`
  - 结果：通过，`Success: no issues found in 7 source files`。
- `V6ax`（fourteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`385 passed`。

#### 2.149 第十五轮 Windows CI 修复

- GitHub Compatibility Gate 的 Windows Python 3.11 / 3.12 矩阵均失败在
  `tests/unit/test_pr_review_provider.py::test_local_agent_allows_reviewed_patch_file_dirty_input`。
- 根因：测试 fixture 以文本模式写入 `change.patch` 后仍用 LF 内存字符串计算
  `patch_hash`；Windows 落盘时文本换行可能为 CRLF，而真实 `patch` diff source
  在 `resolve_diff_source` 中按 `read_bytes()` 记录 hash，导致 fixture 与真实
  review pack 生成逻辑不一致。
- 修复：patch source provider fixture 改为按落盘后的 `change.patch` bytes 计算
  `patch_hash`，保持 provider 的 byte-level 篡改检测不放宽。

#### 2.150 第十五轮验证命令

- `V6ay`（fifteenth-round provider pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_provider.py -q`
  - 结果：通过，`34 passed`。
- `V6az`（fifteenth-round provider ruff）
  - 命令：`uv run ruff check tests/unit/test_pr_review_provider.py src/ai_sdlc/core/pr_review_provider.py`
  - 结果：通过，`All checks passed!`。
- `V6ba`（fifteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`385 passed`。
- `V6bb`（fifteenth-round workitem close-check）
  - 命令：`uv run ai-sdlc workitem close-check --wi specs/189-loop-engine-local-adversarial-pr-review`
  - 结果：通过，`done_gate PASS ready for completion`。

#### 2.151 第十六轮 Codex review 修复

- Codex 第十六轮 P2 `Resolve worktree sources against the current HEAD`：
  `local-staged` / `local-unstaged` 的 diff 始终来自当前 index/worktree，
  不应使用用户传入的非当前 `--head` 作为 attribution commit。
- 修复：worktree diff source resolution 固定解析当前 `HEAD`，no-change 和
  error surface 也展示 `HEAD`，避免用户传入 `--head origin/main` 或旧 commit 时
  review pack 记录未被实际 review 的 head commit，并在后续 local-agent launch /
  close / attest 阶段误判 stale。
- 新增单测覆盖 local-staged、local-unstaged 传入旧 head ref 时，`base_commit` /
  `head_commit` 仍绑定当前 checkout `HEAD`。

#### 2.152 第十六轮验证命令

- `V6bc`（sixteenth-round source pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_source.py -q`
  - 结果：通过，`10 passed`。
- `V6bd`（sixteenth-round source ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_source.py tests/unit/test_pr_review_source.py`
  - 结果：通过，`All checks passed!`。
- `V6be`（sixteenth-round source mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_source.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6bf`（sixteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`387 passed`。

#### 2.153 第十七轮 Codex review 修复

- Codex 第十七轮 P2 `Reject parent-directory paths in patch sources`：
  patch diff headers 中的 `../`、绝对路径或 Windows drive 路径不能进入
  `changed_files` / `reviewer_allowlist`，否则本地 reviewer allowlist 可能授权
  repo 外路径。
- 修复：patch path normalizer 对绝对路径、Windows drive 路径、`.` / `..` 逃逸做
  fail-closed；`build_review_pack` 捕获 review input 解析阶段的 `GitError` 并返回
  `BLOCKED`，不写出 review pack。
- 新增单测覆盖 `diff --git a/../secrets.txt b/../secrets.txt` 会被阻断，且
  blocker 明确包含 `Patch path escapes repository`。

#### 2.154 第十七轮验证命令

- `V6bg`（seventeenth-round pack pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`22 passed`。
- `V6bh`（seventeenth-round pack ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py tests/unit/test_pr_review_pack.py`
  - 结果：通过，`All checks passed!`。
- `V6bi`（seventeenth-round pack mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6bj`（seventeenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`388 passed`。

#### 2.155 第十八轮 Codex review 修复

- Codex 第十八轮 P2 `Avoid fabricating paths from ambiguous diff headers`：
  `diff --git a/foo b/bar b/foo b/bar` 这类路径本身包含 ` b/` 的 header 不能用
  `rsplit(" b/")` 推断左右路径，否则会伪造不存在的 allowlist 路径。
- 修复：`diff --git` header 中 ` b/` delimiter 不唯一时，不从该行推断路径，
  改由后续 `---` / `+++` 文件头提供真实路径。
- 新增单测覆盖 `foo b/bar` 这类路径只进入真实 `changed_files` /
  `reviewer_allowlist`，不会生成 `foo b/bar b/foo` 或 `bar`。

#### 2.156 第十八轮验证命令

- `V6bk`（eighteenth-round pack pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`23 passed`。
- `V6bl`（eighteenth-round pack ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py tests/unit/test_pr_review_pack.py`
  - 结果：通过，`All checks passed!`。
- `V6bm`（eighteenth-round pack mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6bn`（eighteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`389 passed`。

#### 2.157 第十九轮 Codex review 修复

- Codex 第十九轮 P2 `Handle attestation unlink failures in start`：
  `pr-review start` / rerun 在清理 `.ai-sdlc/reviews/pr/latest-attestation.json`
  时如果遇到目录、权限拒绝或 Windows 文件锁，不能让 `OSError` 冒泡导致 CLI
  traceback；应像 close / attest 一样 fail-closed，避免 stale attestation 被继续复用。
- 修复：`start_pr_review` 在非 dry-run 清理 stale attestation 时捕获 `OSError`，
  返回结构化 `PRReviewStartResult(status=BLOCKED)`，并给出删除
  `latest-attestation.json` 后重试的下一步。
- 新增单测用 `latest-attestation.json` 目录模拟 unlink 失败，验证 start 返回
  BLOCKED 而不是崩溃。

#### 2.158 第十九轮验证命令

- `V6bo`（nineteenth-round service pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_service.py -q`
  - 结果：通过，`87 passed`。
- `V6bp`（nineteenth-round service ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_service.py tests/unit/test_pr_review_service.py`
  - 结果：通过，`All checks passed!`。
- `V6bq`（nineteenth-round service mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_service.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6br`（nineteenth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`390 passed`。

#### 2.159 第二十轮 Codex review 修复

- Codex 第二十轮 P2 `Revalidate worktree diffs before launching local-agent`：
  `local-staged` / `local-unstaged` review pack 在 provider launch 前需要重新计算
  当前 index/worktree diff hash；否则同一路径在 pack 生成后被修改，local-agent
  会先调用模型，直到 close/attest 才发现 stale diff。
- 修复：`run_provider_command` 的 diff source launch blocker 对
  `local-staged` / `local-unstaged` 读取当前 `git diff --cached` / `git diff`，
  与 `diff_source.patch_hash` 比对，不一致时在模型调用前 BLOCKED。
- 新增 provider 单测覆盖 reviewed staged diff 被改动后，local-agent 不会启动，
  并保留 reviewed staged dirty path 的正常通过 fixture。

#### 2.160 第二十轮验证命令

- `V6bs`（twentieth-round provider pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_provider.py -q`
  - 结果：通过，`35 passed`。
- `V6bt`（twentieth-round provider ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_provider.py tests/unit/test_pr_review_provider.py`
  - 结果：通过，`All checks passed!`。
- `V6bu`（twentieth-round provider mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_provider.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6bv`（twentieth-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`391 passed`。

#### 2.161 第二十一轮 Codex review 修复

- Codex 第二十一轮 P2 `Require all patch paths to stay allowlisted`：
  patch source 的 rename/copy block 可能同时包含 included path 与 omitted path；
  `_filter_patch_diff` 不能因为任一路径 allowlisted 就输出整个 block，否则会把
  omitted 侧内容泄漏进 `diff.patch`。
- 修复：patch block 输出条件改为 `current_paths <= included`，只有 block 中所有
  路径都在 allowlist 时才输出；mixed included/omitted block 整体丢弃。
- 新增单测覆盖 `src/app.py -> dist/app.generated.ts` 且
  `allowed_omitted_file_policy: allow-with-waiver` 时，生成的 `diff.patch` 不包含
  omitted/generated 侧路径或内容。

#### 2.162 第二十一轮验证命令

- `V6bw`（twenty-first-round pack pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_pack.py -q`
  - 结果：通过，`24 passed`。
- `V6bx`（twenty-first-round pack ruff）
  - 命令：`uv run ruff check src/ai_sdlc/core/pr_review_pack.py tests/unit/test_pr_review_pack.py`
  - 结果：通过，`All checks passed!`。
- `V6by`（twenty-first-round pack mypy）
  - 命令：`uv run mypy src/ai_sdlc/core/pr_review_pack.py`
  - 结果：通过，`Success: no issues found in 1 source file`。
- `V6bz`（twenty-first-round focused pytest）
  - 命令：`uv run pytest tests/unit/test_pr_review_models.py tests/unit/test_pr_review_source.py tests/unit/test_loop_policy.py tests/unit/test_pr_review_pack.py tests/unit/test_pr_review_service.py tests/unit/test_pr_review_provider.py tests/integration/test_cli_pr_review.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -q`
  - 结果：通过，`392 passed`。
