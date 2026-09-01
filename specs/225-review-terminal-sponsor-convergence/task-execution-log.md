# 任务执行日志：两轮评审终局 Sponsor 决策收敛合同

**功能编号**：`225-review-terminal-sponsor-convergence`
**创建日期**：2026-08-31
**状态**：G1 formal/admission 进行中；规则实现未授权
**验证画像**：`code-change`；唯一测试变更仅同步 Program Truth 固定库存期望，但仍按 `tests/**` 变更运行完整门禁

## 1. 归档规则

- 本文件是 WI225 的 canonical 执行归档；不创建 `development-summary.md` 或第二套总结。
- 本批只允许 classifier 已认可的 formal control、truth、库存期望和 continuity；roadmap/defect 保持只读。
- `AGENTS.md` 规则实现、Local PR Review runtime、schema、状态机和 WI224 均不在本批。
- Formal 合入后的预期终态为 `formal_freeze_only / execution_started=false / contained_in_main=true`。

## 2. 批次记录

### Batch 2026-08-31-001 | T11-T32

#### 2.1 范围与基线

- 真值基线：`origin/main@e8a73ec409a7eb771abc41dcc996dc198c031a5d`。
- 分支：`feature/225-review-terminal-sponsor-convergence-docs`。
- worktree：`.worktrees/225-terminal-sponsor-decision-formal`。
- WI224 处置：产品/主线完成；未创建 WI224 follow-up PR；暂停 heartbeat `monitor-wi224-pr-194` 已删除。GitHub 后续将编号 #196 分配给 WI225 Formal PR，不代表 WI224 续修。
- 固定排除：WI224 历史、runtime、CLI、schema、状态机、workflow、release、P3 其余 11 路、P4、D2 和用户排除的本地材料。

#### 2.2 预读与证据

- 已读：宪章、tech stack、Refine/Design/Decompose/Verify 阶段清单及相关规则。
- 基线验证：`uv run ai-sdlc verify constraints` 无 BLOCKER；`uv run pytest tests/integration/test_repo_program_manifest.py -q` 为 `1 passed in 134.49s`。
- `AGENTS.md` 的 repo-local PR protocol 要求持续 heartbeat，但没有两轮后的 terminal sponsor 分支。
- `LoopPolicyProfile.max_rounds` 默认 2，达到上限会返回 `needs_user`；现有 next action 仍提示增加 `--max-rounds`。
- rerun 已按 severity/file/line/claim/risk 生成 finding signature，写入 `finding-history.json`。
- 现有 close/report/attestation 已支持 `risk_accepted` 和 digest 绑定，无需新建终态 artifact。

#### 2.3 Admission 决策

- 推荐：后续补根 `AGENTS.md` Local Repository PR Protocol，并在现有 `tests/unit/test_verify_constraints.py` 增加一个静态规则标记回归测试；两个文件构成一个语义 delta，直接约束 GitHub PR/heartbeat 实际复发层并防止规则静默回退。
- No-Go：本次不改 Local PR Review runtime；单改 CLI 不能约束 GitHub heartbeat。
- No-Go：不新增 SponsorDecision artifact/schema/command/state。
- 后续候选投入上限：0.5 人日、一个规则实现 PR、无 post-merge records PR。
- 后续候选未授权；本 WI 只完成 formal/admission。

#### 2.4 当前验证回执

| 编号 | 命令 | 结果 |
|---|---|---|
| V0 | `git ls-remote origin refs/heads/main` / `git rev-parse origin/main` | PASS：`e8a73ec409a7eb771abc41dcc996dc198c031a5d` |
| V1 | `uv sync --frozen` | PASS：隔离 worktree 环境完成 |
| V2 | `uv run ai-sdlc verify constraints` | PASS：no BLOCKERs |
| V3 | `uv run pytest tests/integration/test_repo_program_manifest.py -q` | PASS：`1 passed in 134.49s`（改动前基线） |
| V4 | `uv run ai-sdlc program truth sync --dry-run` | PASS：blocked；16 blockers；`1174/1174 mapped`、missing 5、close `218/223` |
| V5 | `uv run ai-sdlc verify constraints`（整改后） | PASS：no BLOCKERs |
| V6 | `uv run ai-sdlc program truth sync --execute --yes`（最终记录刷新后） | PASS：目标提交内 `program-manifest.yaml:truth_snapshot` 为准；仅原 16 blockers，不在规范中固化动态 hash |
| V7 | `uv run ai-sdlc program truth audit` | EXPECTED BLOCKED：snapshot fresh；16 blockers、库存与 V6 一致 |
| V8 | `uv run pytest tests/integration/test_repo_program_manifest.py -q` | PASS：终态 snapshot 后 fresh rerun `1 passed in 127.91s` |
| V9 | `uv run ruff check tests/integration/test_repo_program_manifest.py` | PASS：All checks passed |
| V10 | `uv run pytest -q` | PASS：`3412 passed, 3 skipped in 935.11s` |
| V11 | `uv run ruff check .` | PASS：All checks passed |

CLI 预读中曾使用大写阶段名，实际 CLI 明确只接受小写；随后以 `refine/design/decompose/verify` 成功读取清单。该纠正没有产生文件修改，也未扩大 G1 范围。

首次 truth execute 在 constraints receipt 刷新前运行，因此临时多出 `verify constraints` blocker；随后 constraints 又准确指出新 defect entry 缺少必填 `middleware` 字段。整改只补 `middleware: not-applicable` 及原因，之后必须重跑 constraints、truth execute/audit 和回归，不把首次 snapshot 当终态证据。

#### 2.5 任务与 git lifecycle

- `tasks.md`：T11-T31 与 T32 的验证/continuity/本地独立评审子项已完成；Formal PR #196 已创建，等待 Codex P1 聚焦修复的 exact-head re-review。
- `related_plan`：`docs/FRAMEWORK_ROADMAP.zh-CN.md` 仅作为只读关联路线图；WI225 formal/admission 与规则 execute 未授权均由本工作项归档。
- 当前批次 branch disposition：`merge-pending`。
- 当前批次 worktree disposition：`retained(formal-admission-review)`。
- 是否继续规则实现：否；必须等待 Formal PR 合并和新的用户 execute 授权。

#### 2.6 独立评审与聚焦复核

- 初次独立 formal/ROI 评审只发现一个 Important：continuity 仍包含已完成验证和无关 Cursor drift 的过时 next steps。
- 聚焦整改只刷新 `tasks.md`、execution log、canonical/scoped handoff 与 resume context，并恢复 CLI 自动生成的无关 Cursor adapter 漂移；未修改规则、runtime 或 WI224。
- 唯一一次 focused re-review 只复核该 stable finding 及其直接回归面，结论为：`未发现可操作问题；Ready`。
- 回归面：canonical/scoped continuity 成对一致、两份 resume YAML 可解析、changed-files 与 `git status` 一致、`git diff --check` 通过、禁止路径为空。

#### 2.7 GitHub Codex review round 1

- PR #196 exact head `9ac797bb78f5fe63ba410e2e961b46d112b17307` 的 Codex review 提出一个 P1：roadmap 与 defect backlog 不属于 `_formal_control_paths()`，导致 Formal 被分类为 `branch_only_implemented / execution_started=true`。
- 复现：`uv run ai-sdlc workitem truth-check --wi specs/225-review-terminal-sponsor-convergence --rev HEAD --json` 在该 head 返回 `branch_only_implemented`，finding 成立。
- 聚焦决策：不修改 classifier/runtime；恢复 roadmap 与 defect backlog 到 exact base，只把完整 admission 决策保存在 WI225 formal carrier 内，并同步 continuity。该修复让 PR 聚合路径严格限制在既有 formal control set。
- 删除注释原因：从 `docs/framework-defect-backlog.zh-CN.md` 删除本分支新增的标题及整条字段说明；被删标题摘要 token 为 `# F D - 2 0 2 6 - 0 8 -`，主题是“两轮评审后缺少终局 Sponsor 分支，导致关闭流程递归”。该路径不在现有 Formal 控制集；相同问题、决策、投入与验证合同已完整保留在 WI225 spec/plan/tasks/log，故不丢失治理真值。摘要分隔书写是为了避免把已删除编号重新登记为有效 backlog 引用。
- 聚焦验证：PR 聚合路径相对 exact base 的 `extra=[]`；constraints 无 blocker；plan-check drift NO；program validate PASS；Program Truth audit 为 fresh/blocked，保留原 16 blockers 与 `1174/1174 mapped`、missing 5、close `218/223`；manifest regression `1 passed in 138.53s`；`git diff --check` PASS。
- 本次计为第 1 个 GitHub review repair round；不得借此引入 G1 rules execute。

#### 2.8 GitHub Codex review round 2（终局修复轮）

- exact head `c481cf21a89062646be8e5459a48b8affec2a6b6` 的 Codex re-review 提出一个 P2：`FR-225-008` 仍指示 formal 更新 roadmap/defect，与同一规格和计划的只读边界冲突，未来执行会重引入 round 1 P1。
- 聚焦修复只改 `FR-225-008`，把允许写入面精确收窄到 WI225 spec/plan/tasks/task-execution-log、Program Truth 固定库存期望和 continuity；roadmap/defect 明确只读。
- 终局验证：normative scope 只保留 formal controls，聚合路径 `extra=[]`；constraints 无 blocker；plan-check drift NO；program validate PASS；truth audit fresh/blocked 且原 16 blockers、`1174/1174 mapped`、missing 5、close `218/223` 不变；manifest regression `1 passed in 131.35s`；`git diff --check` PASS。
- exact head `194eb0ea40ae5e7e6b77d61a0780533c6cbda8f6` 的终局 re-review 又指出 `tasks.md` Batch 3 总览仍写“同步 roadmap”。该项与前述 P1/P2 具有相同签名和风险面，是 round 2 未完成的语义残留，不是第三个新 finding。
- 轮次纠偏：repair round 只有在同一 stable finding 的规范、任务、总览和直接回归面完成穷尽闭包后才算完成；把漏修残留另计一轮属于错误。用户授权完成 round 2，本次只删除 Batch 3 总览中的 roadmap 写入指令。
- 闭包验证：穷尽扫描 WI225 spec/plan/tasks 的 11 处 roadmap/defect 引用，危险写入指令为 0；Formal 聚合路径 `extra=[]`；constraints 无 blocker；plan-check drift NO；program validate PASS；truth audit fresh/blocked 且原 16 blockers、`1174/1174 mapped`、missing 5、close `218/223` 不变；manifest regression `1 passed in 148.57s`；`git diff --check` PASS。
- round 2 完成后只允许一次稳定 finding 终局复审；若出现不同签名的新问题，进入 terminal sponsor decision，不扩大本次修复。

#### 2.9 Terminal sponsor decision：不同签名 P2

- exact head `1751db25c3de773c94c3eef2b45c6fa51e6af396` 的终局复审提出不同签名 P2：后续候选禁止测试逻辑，但 FR-225-002 至 FR-225-005 是行为规则；只写 `AGENTS.md` 会缺少自动化回归保护，与宪章 MUST-2 冲突。
- 技术核验：现有 `verify constraints` 只覆盖 `AGENTS.md` 的启动路径标记，没有覆盖两轮上限或 terminal sponsor 字段；finding 成立，但不需要修改 runtime。
- Sponsor 授权只修正 Formal admission，不授权现在实现规则：
  - `unique_delta`：未来实现候选只允许根 `AGENTS.md` 加现有 `tests/unit/test_verify_constraints.py` 中一个静态规则标记回归测试；不得修改 `src/`。
  - `effort_cap`：本次 Formal 修正不超过 1 小时、一个语义提交；未来实现仍不超过 0.5 人日、一个 PR。
  - `terminal_outcome`：只再进行一次针对该 P2 及直接回归面的 exact-head 复核；PASS 即合并，新的可操作 finding 则记为 known-blocked/No-Go，不申请第二次例外。
- 改动边界：只同步 WI225 spec/plan/tasks/log、continuity 与 fresh Program Truth snapshot；`AGENTS.md`、测试逻辑、`src/`、roadmap、defect backlog 和 Program Truth blocker 均不修改。
- 改动前基线：`uv run pytest tests/integration/test_repo_program_manifest.py -q` 为 `1 passed in 151.00s`。
- focused verification：constraints 无 blocker；plan-check drift NO；program validate PASS；truth audit 为 fresh/blocked，仍为原 16 blockers 与 `1174/1174 mapped`、missing 5、close `218/223`；manifest regression 为 `1 passed in 150.46s`；resume YAML 可解析；`git diff --check` PASS；聚合 PR 路径仍全部属于既有 Formal 控制集。

#### 2.10 下一步

1. 完成 Formal 文档与 continuity 同步，运行范围、真值、计划和固定库存回归验证。
2. 提交并推送同一 PR，回复该 P2 inline thread并请求一次 terminal sponsor exact-head re-review。
