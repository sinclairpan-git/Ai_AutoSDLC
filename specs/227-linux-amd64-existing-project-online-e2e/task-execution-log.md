# 任务执行日志：R10 Linux AMD64 已有项目在线 E2E

**功能编号**：`227-linux-amd64-existing-project-online-e2e`  
**创建日期**：2026-09-04  
**当前状态**：T31/T32 已完成；R10 以 `partial` 合并，等待未来正常发布自然复验

## Batch 2026-09-04-001 | T11

- 基线：`origin/main@8a3973a555c4fe463cc31cdec1021a1c76b7f3a8`
- 决策：双专家对抗合议 2/2 `APPROVE`，用户批准执行。
- 范围：R10-only；复用并参数化 R06 consumer；一个 WI、一个分支、一个 PR。
- 基线验证：`.venv/bin/python -m pytest tests/integration/test_github_workflows.py -q` → `18 passed in 1.59s`。
- 工具环境：uv 默认缓存目录被沙箱拒绝、隔离缓存网络受限；改用已安装依赖的工作树 `.venv`。两次均为环境观察失败，不是候选失败、不消耗修复轮次。
- Scaffold 副作用：保留 WI227、manifest 映射和项目序号；Cursor adapter 自动刷新不属于范围，已撤销。
- 结论：T11 完成；下一步只执行 T21 测试 RED。

## 固定归档规则

后续每个批次只追加实际发生的命令、exit code、耗时、exact HEAD/CI run 与 receipt；不预写成功，不以 API/网络/排队替代候选结论。代码、测试、任务勾选和本批日志在同一逻辑提交中对齐。

## Batch 2026-09-04-002 | T21-T22

- 改动范围：`.github/workflows/macos-user-guide-e2e.yml`、`tests/integration/test_github_workflows.py`。
- RED：`.venv/bin/python -m pytest tests/integration/test_github_workflows.py::test_macos_user_guide_e2e_runs_r06_and_r10_in_one_posix_matrix -q` → exit 1，`KeyError: 'strategy'`，`1 failed in 0.31s`；GREEN 后仅将测试名收敛为 `test_posix_user_guide_e2e_runs_r06_and_r10_in_one_matrix`。
- 实现：在唯一 `existing-project-online-install` job 中增加 R06/macOS arm64 与 R10/Linux AMD64 两行矩阵；route、runner、OS、architecture、asset suffix、fresh shell、receipt 和 artifact 动态绑定同一 replay。
- GREEN：新测试 → `1 passed in 0.29s`；完整 workflow 合同测试 → `19 passed in 1.42s`。
- 仓库级 RED：`.venv/bin/python -m pytest tests/integration/test_repo_program_manifest.py -q` → exit 1，实际 inventory `1185/1185/0/7` 与旧期望 `1180/1180/0/6` 不同，耗时 `137.55s`；只同步直接 inventory/close 期望为 `1185/1185/0/7`、`225/218`。
- 仓库级 GREEN：同一命令 → exit 0，`1 passed in 138.18s (0:02:18)`。
- 范围核对：未创建第二个 workflow/helper；未修改 runtime、schema、release producer、installer、USER_GUIDE 或 R02。
- 结论：T21/T22 完成；下一步只提交并推送当前候选，执行 T31 真实 Ubuntu 首验。

## Batch 2026-09-04-003 | T31-T32

- **验证画像**：`truth-only`
- **改动范围**：`specs/227-linux-amd64-existing-project-online-e2e/tasks.md`、`specs/227-linux-amd64-existing-project-online-e2e/task-execution-log.md`、`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/work-items/227-linux-amd64-existing-project-online-e2e/codex-handoff.md`、`program-manifest.yaml`。
- **统一验证命令**：`uv run ai-sdlc verify constraints`、`uv run ai-sdlc program truth sync --dry-run`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc program validate`、`uv run ai-sdlc workitem close-check --wi specs/227-linux-amd64-existing-project-online-e2e`、`uv run pytest tests/integration/test_repo_program_manifest.py -q`、`git diff --check`。
- **代码审查**：PR #204 对精确 head `1d3ceafd` 的 Codex review 无可操作问题；PR #205 对精确 head `250d04b222cf94d7c70ac6f5804df00b7ffc3d15` 提出 3 项仅涉及记录真实性与 continuity 的 P2，本批次只在既定六文件范围内一次性修正，不重新开启实现架构。
- **任务/计划同步状态**：T11、T21、T22、T31、T32 均为 done；plan 的 R10 `partial` 目标与 execution evidence 一致，R09 仍未准入。
- **已完成 git 提交**：是（本 records-only envelope 由 live PR `HEAD` 承载，不自引用未来 squash SHA）。
- **提交哈希**：`HEAD`（以 live records-only PR exact head 为准）；implementation reviewed head `1d3ceafdef8f5fab3d87fe85023d1869bcd8344c`；main merge `67ac544355356f912e30aa0adf208bc5ae872e5a`。
- 关联 branch/worktree disposition 计划：`deleted`
- 当前批次 branch disposition 状态：`deleted`
- 当前批次 worktree disposition 状态：`removed`
- **生命周期边界**：上述 disposition 指 WI227 原 implementation branch/worktree，均已在 PR #204 合并与树一致性核验后删除；当前 `codex/r10-records-closeout` 只是无 WI 序号的 records transport，不作为实现分支归因。
- **单 PR 合同例外**：原“一个 WI、一个分支、一个 PR”绝对合同未被完整满足。PR #204 合并后才取得的终态 evidence 无法回写已合并候选，因此在向用户明确说明冲突并获准“继续”后，创建 PR #205 作为一次 records-only 例外。该例外不改变实现范围，但仍是第二个 branch/PR；此处显式记录治理违约，不再以 transport 命名掩盖。
- PR：[#204](https://github.com/sinclairpan-git/Ai_AutoSDLC/pull/204)，base `8a3973a555c4fe463cc31cdec1021a1c76b7f3a8`，reviewed head `1d3ceafdef8f5fab3d87fe85023d1869bcd8344c`。
- 真实环境：GitHub Actions run `33893698367` 的 R10/Linux AMD64 job 通过（41 秒）；同矩阵 R06/macOS arm64 回归通过（47 秒）。
- R10 receipt：artifact `9944905601`，artifact digest `sha256:34fd8a24656bea559c83c4371332d505f392cb5ff94e6e854e1c935142a1352c`；`route_id=R10`、`os=linux`、`architecture=amd64`、`status=partial`，install/init/adopt/recover 与业务文件保护均通过。
- 候选验收：23 项 GitHub checks 全绿；Codex 对精确 head 无可操作问题；未消耗确定性修复轮次。
- 合并：PR #204 squash merge 为 `origin/main@67ac544355356f912e30aa0adf208bc5ae872e5a`；候选树与主线树均为 `badddda235b01154eaa2dd1a593b7a9471a817ab`。
- 主线真值：WI226 范围审计在精确主线返回 `ready`；Program Truth 保持 fresh，`1185/1185` mapped、missing `7`、close `218/225`，16 个无关历史 blocker 保留。
- WI227 close-check：在 clean exact head `250d04b222cf94d7c70ac6f5804df00b7ffc3d15` 执行 `uv run ai-sdlc workitem close-check --wi specs/227-linux-amd64-existing-project-online-e2e`，exit `0`；全部检查为 `PASS`，`done_gate=ready for completion`。同一候选的 `program validate` 为 PASS、constraints 无 blocker、manifest 测试 `1 passed in 142.65s`。
- 结论：WI227 完成；R10 不越权提升为 `proven`。下一项仅推荐 R09，仍需独立 formal admission 与用户批准。
