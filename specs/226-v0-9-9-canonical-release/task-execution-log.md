# 任务执行日志：v0.9.9 Canonical Release

**功能编号**：`226-v0-9-9-canonical-release`
**创建日期**：2026-09-03
**当前分类**：`formal_freeze_only`
**execution_started**：`false`

## Batch 2026-09-03-001 | T11 formal baseline

### 范围

- 从精确远端主线 `8f9df406e0a0a8fcb7a3da0be5ab164358918773` 创建隔离 worktree。
- 初始化 WI226 canonical 四件套，并将生成的占位正文替换为终局合议方案 B。
- 在 manifest 中声明 `release_candidate` role 与 WI219/220/221/222/224/225 显式依赖。
- 记录 `v0.9.8@4f3e55c3` 之后 18 个 first-parent carrier；PR #200 仅记为 WI226/R06 partial 组件。
- 还原 `workitem init` 对 `.cursor/rules/ai-sdlc.mdc` 产生的无关生成漂移。

### 已执行的基线命令

- `uv sync`：通过，本地包版本 `0.9.8`。
- `uv run ai-sdlc verify constraints`：通过，无 blocker。
- `uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness'`：`7 passed, 409 deselected`。
- `uv run pytest tests/integration/test_github_workflows.py -q`：`16 passed`。

### Formal 验证结果

- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc program truth sync --dry-run`：PASS；全局 `blocked`，16 blockers，inventory `1179/1179 mapped`、missing `6`、close `218/224`。
- `uv run ai-sdlc program truth sync --execute --yes`：PASS；写入 snapshot `9a147f3448efaa77f0c2a360707d11957f70dbf329f5af4ee1f95e3ec001b1eb`。
- `uv run ai-sdlc verify constraints`：PASS，无 blocker。
- `git diff --check`：PASS；`.cursor/rules/ai-sdlc.mdc` 无 diff。
- WI226 文档占位符检查：零命中。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q` 首轮：FAIL，仅因新增 WI 的五层 inventory 期望仍为旧值 `1174/1174, missing 5, close 218/223`；按实际快照同步为 `1179/1179, missing 6, close 218/224` 后复跑通过（`1 passed`）。

### 决策与边界

- 终局合议为 3:0 APPROVE B；这不是当前实现或发布成功证明。
- 不采用 `e70951c3` 的自动 range inference；不新增第二设计。
- 有界自审删除了原计划中的新聚合 dataclass，改为复用 `ProgramSpecTruthReadinessResult`。
- 实施计划再次审阅并由用户明确批准前，T21-T42 均不得启动。
- 本批只修改 formal/manifest/project-state；`execution_started=false`。

### 当前结论

- T11 已完成并通过 formal 自检。
- T12 已完成用户批准；T21 是唯一待执行的 repository task，生产实现尚未开始。

## Batch 2026-09-03-003 | T21 release-candidate truth readiness

### 范围

- 在 `ProgramService` 增加 release-candidate 显式依赖闭包聚合入口，复用现有 `ProgramSpecTruthReadinessResult` 与逐规格 `build_spec_truth_readiness()`。
- 对根路径唯一匹配、`release_candidate` role、DFS 闭包、成员结果及其 detail/actions/spec ids 做稳定聚合；未读取 Git range、提交消息或 execution log。
- 新增五类 TDD 行为测试：无关全局 blocker、闭包 blocker、stale snapshot、角色缺失、共享传递依赖。

### 实际 TDD 与验证

- RED：`uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'`：`5 failed, 416 deselected`；全部因 `ProgramService` 尚无 `build_release_candidate_truth_readiness`。
- GREEN：同一命令：`5 passed, 416 deselected`。
- 回归：`uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'`：`12 passed, 409 deselected`。
- 静态检查：`uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py`：通过。
- `git diff --check`：通过。

### 当前结论

- T21 已完成；生产代码净新增 149 行，未新增结果类型、schema 或 ledger。
- T22 是唯一 todo；T23、T31、T32 仍保持 blocked。

## Batch 2026-09-03-004 | T21 review repair round 1

### 范围与结果

- 按 review 收敛 T21 聚合为 89 行生产新增；移除前端状态选择，只聚合现有 readiness 的 state、summary、detail、actions 与 matched spec ids。
- 三个 release-candidate 结果测试改为真实临时 ProgramService truth fixture，直接穿过既有 `build_spec_truth_readiness()`；只有共享传递依赖顺序测试保留 interaction double。
- 先对底层 detail 去重再汇总，真实全局 blocker 与 stale snapshot 均验证只保留一条 detail。

### 验证

- `uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness'`：`5 passed, 416 deselected`。
- `uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'`：`12 passed, 409 deselected`。
- Ruff 与 `git diff --check`：通过。
- 相对 T21 parent 的生产差异：`89 0`，满足 review 的 `<=90` 新增行目标。

## Batch 2026-09-03-005 | T22 truth audit CLI

### 范围与结果

- 为既有 `program truth audit` 增加可选 `--wi`，仅调用 T21 的 `build_release_candidate_truth_readiness()`。
- 按 WI 路径渲染根 WI、稳定闭包 spec ids、state、detail 和去重后的 next actions；ready 返回 0，其余 readiness 状态返回 1。
- 未携带 `--wi` 时保留既有 truth-ledger surface 路径；manifest 载入失败仍返回 2。

### 实际 TDD 与验证

- RED：`uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate'`：`3 failed, 1 passed, 233 deselected`；三个失败均为 Typer 的预期 `No such option: --wi`，退出码 2。
- GREEN：同一命令：`5 passed, 233 deselected`。
- 回归：`uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit'`：`9 passed, 229 deselected`。

### 当前结论

- T22 已完成；T23 是唯一 todo。
- T31、T32 继续 blocked，未改动工作流、版本或发布真值。

## Batch 2026-09-03-006 | T22 terminal repair round 2/2

### 范围与结果

- 为 release-candidate 聚合的 `manifest_invalid`、项目外路径、零/多 manifest 映射和 `truth_readiness_unavailable` 补齐有界 detail 与 next action；未改 schema、结果类型、helper 或 ready 成功路径。
- 新增真实 CLI 回归：未映射 `README.md` 返回 1 且输出 detail/action；缺失 `--wi` 值返回 2。

### 验证

- RED：`truth_audit and release_candidate` 为 `1 failed, 6 passed, 233 deselected`；仅因未映射路径 detail/action 为空。
- GREEN：同一命令 `7 passed, 233 deselected`；Task2 focused `12 passed, 409 deselected`；全部 audit `11 passed, 229 deselected`。
- Ruff 和 `git diff --check`：通过；累计生产净新增 `129` 行，未超过 `150` 行上限。

## Batch 2026-09-03-002 | Task 1 formal remediation

### 范围

- 将 `tasks.md` 收敛为现有 parser 可识别的 canonical executable-task blocks。
- 如实记录用户对同一 WI226 formal baseline 的批准；不改生产代码、工作流、版本号或发布状态。
- 明确 Task 5 只有在创建真实 `docs/releases/v0.9.9.md` 的同一批次才登记 release source_registry，并同步 manifest inventory 期望。
- 将 repository executable/checklist 工作边界固定在 T32；其后的 GitHub release evidence 仅作 Post-release handoff。

### 真实状态

- T11、T12：done。
- T21：todo，为 guard 唯一可选择的下一条任务。
- T22、T23、T31、T32：blocked，尚未实施。
- 未执行生产代码、工作流、版本号、merge、tag、资产上传、attestation、release smoke 或 12-route 回执。

### 本批验证

- `uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T21 生产实现" --json`：PASS；精确选择 `T21`。
- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc verify constraints`：PASS；无 blocker。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：PASS，`1 passed in 132.58s`。
- `git diff --check`：PASS。

## Batch 2026-09-03-007 | T23 PR/tag release-candidate truth gate

### 范围与结果

- PR Checks 在 `Verify constraints` 后运行 WI226 release-candidate truth audit。
- Release Build 在 exact-tag checkout、Python/uv setup 后且平台构建前运行同一 audit；步骤也位于 attestation 与 `gh release upload` 之前。
- 两个门禁均为独立无条件步骤，未配置 `if` 或 `continue-on-error`。
- 新增 YAML 合同回归，覆盖精确命令、PR 相对约束门禁的顺序，以及 Release Build 相对 checkout/setup/build/attestation/upload 的顺序。

### 实际 TDD 与验证

- RED：`uv run pytest tests/integration/test_github_workflows.py -q -k 'release_candidate_truth or release_build'`：`1 failed, 4 passed, 12 deselected`；仅因 PR workflow 缺少 truth gate 而失败。
- GREEN：同一命令：`5 passed, 12 deselected`。
- 全量 workflow 合同：`uv run pytest tests/integration/test_github_workflows.py -q`：`17 passed`。
- 静态检查：`uv run ruff check tests/integration/test_github_workflows.py`：通过。
- `git diff --check`：通过。

### 当前结论

- T23 已完成。
- T31 是唯一 todo；T32 继续 blocked。

## Batch 2026-09-03-008 | T31 v0.9.9 release truth

### 范围与结果

- 先将 release-consistency、workflow、offline guidance 与 manifest inventory
  测试目标改为 `0.9.9`，随后同步当前版本入口、离线资产名、默认 release
  tag、constraints 合同与 lockfile；明确的 `post-v0.9.8` 历史路线图叙述保留。
- 新建面向用户的 `docs/releases/v0.9.9.md`，将 18 个主线载体归并为单一
  入口与连续性、可验证的跨平台安装/恢复、以及按显式依赖闭包保护的发布边界。
- 在 release note 存在的同一变更批次，将其以 `release_doc/release` 登记到
  `source_registry`；没有改写 snapshot 或历史 release note。
- `uv lock` 将本地包版本从 `0.9.8` 同步为 `0.9.9`。

### 实际 TDD 与验证

- RED：更新测试后，用户指引仍为 `v0.9.8`，离线 bundle 断言失败；随后完整
  focused suite 也暴露所有尚未同步的当前发布入口。
- GREEN：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q`：`213 passed`。
- Manifest：`uv run pytest tests/integration/test_repo_program_manifest.py -q`：`1 passed`；inventory 为 `1180/1180 mapped`、unmapped `0`、missing `6`，release layer `45`。
- `uv run ai-sdlc verify constraints`：PASS，无 blocker；`uv run ruff check src tests`：PASS；`git diff --check`：PASS。

### 当前结论

- T31 已完成；T32 是唯一 todo。
- 未执行 truth sync、全量 pytest、外部 review、merge、tag、资产上传或 release smoke；这些仍属于 T32 或 Post-release handoff。

## Batch 2026-09-03-009 | T32 final local validation and truth-refresh preparation

### 结构化收口字段

- **验证画像**：`code-change`
- **改动范围**：本 WI 从 `origin/main@8f9df406e0a0a8fcb7a3da0be5ab164358918773` 到当前分支的实现、测试、工作流、v0.9.9 发布真值与 WI226 tracking 文件；本 Batch 本身只更新 tracking/truth。
- **任务/计划同步状态**：T11、T12、T21、T22、T23、T31、T32 均为 done；Sponsor 特批修复已通过真实规模 scoped audit，repository executable/checklist 工作结束。
- **代码审查**：T21、T22、T23、T31 已完成任务级审查与有界整改；`a9140136` 的重复计算 No-Go finding 已由一次性 Sponsor 授权在 `3d2e8c6e` 精确修复，最终候选仍须完成唯一一次 exact-HEAD 复审，未在此预写通过。
- **已完成 git 提交**：是（本地 T32 验证与 truth-refresh 首个载体为 `0df3051bdfe868cd8eee5ac5a09f9d3c5d7ed533`；本结构化字段以 live PR exact HEAD 复核）。
- **提交哈希**：本地 T32 首个载体 `0df3051bdfe868cd8eee5ac5a09f9d3c5d7ed533`；No-Go reviewed candidate `a9140136`；Sponsor 修复 `3d2e8c6e`；首次 fresh-snapshot acceptance head `aca1c283`。
- 关联 branch/worktree disposition 计划：`merged`
- 当前批次 branch disposition 状态：`merge-pending`
- 当前批次 worktree disposition 状态：`retained(PR review)`

### 范围

- 只完成 WI226 的本地 T32 收口：验证、任务状态、执行日志、canonical 与 WI226 scoped handoff，以及随后一次 truth snapshot 刷新。
- 不修改 `src/`、工作流、版本内容或测试逻辑；不执行 push、PR、merge、tag、publish 或任何外部发布操作。

### 统一验证命令与实际结果

- `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_repo_program_manifest.py -q`：`875 passed in 216.73s (0:03:36)`。
- `uv run ruff check src tests`：通过，输出 `All checks passed!`。
- `uv run pytest -q`：`3428 passed, 3 skipped in 865.14s (0:14:25)`。
- `uv run ai-sdlc verify constraints`：通过，输出 `verify constraints: no BLOCKERs.`。
- `git diff --check`：通过，退出码 `0`。
- Sponsor RED：`uv run pytest tests/unit/test_program_service.py::test_release_candidate_truth_readiness_builds_one_surface_for_seven_members -q` 为 `1 failed`，精确显示期望 1 次、实际调用 `build_truth_ledger_surface` 7 次。
- Sponsor GREEN：同一测试 `1 passed`；`uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'` 为 `13 passed, 409 deselected`；Ruff 与 `git diff --check` 通过。
- 生产修复只修改 `program_service.py` 与直接单测，Sponsor 净增 14 行；WI226 生产净增 `143/150`。闭包成员复用一次 shared truth surface，现有 ready/blocked/stale/CLI 语义保持不变。
- 首次真实规模验收：clean `aca1c283` 上 `uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release` 返回 `ready`、exit 0，耗时 `159.234s`，闭包为 root 加 6 个显式依赖；全局 16 个历史 blocker 不变。

### 收口边界

- `a9140136` 的 No-Go 仅否决当时的候选，不代表目标无解；用户随后明确批准一次、同分支、两文件、剩余 21 行预算内的终局 Sponsor 修复。该例外已消费，不再允许第二个修复波次。
- 最终 tracked truth 写回后，必须在最终 clean exact HEAD 重跑 scoped audit 并保持 `ready/0` 与不超过 3 分钟，再进行唯一一次 exact-HEAD 复审；任一失败即终止，不扩范围。
- 上一套未进入远端主线的本地 `feature/226-git-local-cache-exclusion-concurrency-contract-docs` 候选仍不作为 WI226 v0.9.9 发布证据，也不在本批删除或改写。

## Batch 2026-09-03-010 | T33 F-TRUTH-SCOPE-01 stabilization

### 激活与范围

- 用户批准在同一 WI、同一分支和原 PR 上执行一次同根稳定化；没有创建新 WI、设计稿、分支或 PR。
- `plan.md` 与 `tasks.md` 只增加 T33 激活记录，并明确 4 小时主动工程投入、150 行生产净新增和唯一 exact-HEAD 认证上限。
- 生产修复仅修改 `program_service.py`，测试仅修改直接单测；没有新增 schema、ledger、waiver、缓存或状态机。

### 根因与 TDD 证据

- 根因：`build_spec_truth_readiness()` 在消费调用方传入的共享 truth surface 前先进入 persisted fast path；这既让七成员闭包形成 `1+N` 次 snapshot 构建，也让成员投影在 matched capability rows 已 ready 时仍被无关的全局 `blocked` 状态否决。
- RED：`uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness'` 返回 `3 failed, 12 passed`。失败分别为七成员实际调用 `build_truth_snapshot()` 8 次、matched row ready 仍返回 blocked、预期 capability row 缺失仍返回 ready。
- GREEN：同一命令返回 `15 passed, 409 deselected`。
- 完整服务单测：`uv run pytest tests/unit/test_program_service.py -q` 返回 `424 passed in 35.86s`。
- Focused 预认证：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/integration/test_repo_program_manifest.py -q` 返回 `878 passed in 219.88s (0:03:39)`。
- 全量预认证：`uv run pytest -q` 返回 `3431 passed, 3 skipped in 891.23s (0:14:51)`。
- 静态检查：`uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py` 通过。
- 全仓静态与合同检查：`uv run ruff check src tests`、`uv run ai-sdlc program validate`、`git diff --check` 均通过。
- `verify constraints` 首次运行只因本批精简 handoff 时遗漏既有 `## Local PR Review` 标题而失败；恢复该既有章节后，同一命令通过且无 blocker。该记录格式修正未修改生产代码或测试行为。
- 当前生产代码总净新增 `149/150` 行。

### 当前状态

- Program Truth sync 已执行：全局保持 `blocked`，16 项历史 blocker 原样保留；inventory 为 `1180/1180 mapped`、unmapped `0`、missing `6`、close `218/224`。
- 真实规模 scoped audit：`uv run ai-sdlc program truth audit --wi specs/226-v0-9-9-canonical-release` 返回 `ready`、exit `0`、耗时 `138.984s`；闭包为根 WI 加六个显式依赖，detail 明确闭包外 release targets 仍 blocked。
- T33 已完成。最终 tracked 记录仍须再做一次 truth sync 并提交；exact-HEAD 认证与评审尚未执行，不预写通过。
