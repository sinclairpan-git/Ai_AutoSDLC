# 任务执行日志：R10 Linux AMD64 已有项目在线 E2E

**功能编号**：`227-linux-amd64-existing-project-online-e2e`  
**创建日期**：2026-09-04  
**当前状态**：T21/T22 本地 RED→GREEN 完成，T31 真实 Ubuntu 首验待执行

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
