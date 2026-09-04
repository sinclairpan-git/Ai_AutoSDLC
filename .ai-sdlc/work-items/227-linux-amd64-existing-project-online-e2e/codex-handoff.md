# Continuity Handoff

- Updated: 2026-09-04T15:58:36+00:00
- Reason: T21/T22 完成 RED→GREEN，进入真实 Ubuntu 首验
- Goal: 实施 WI227 R10 Linux AMD64 已有项目在线 E2E
- State: T21/T22 已完成；单 job R06/R10 matrix 本地合同测试通过；T31 待 PR exact-head Ubuntu 验收
- Stage: execute
- Work Item: 227-linux-amd64-existing-project-online-e2e
- Branch: feature/227-linux-amd64-existing-project-online-e2e-dev

## Changed Files
- `.github/workflows/macos-user-guide-e2e.yml`
- `tests/integration/test_github_workflows.py`
- `specs/227-linux-amd64-existing-project-online-e2e/`
- canonical/scoped handoff

## Key Decisions
- 一个 WI、同一分支原地从 docs 重命名为 dev、一个 PR。
- 单 job 两行 R06/R10 matrix；真实 Ubuntu 首验。
- 不修改 runtime、receipt schema、release producer、R02 或其他路线。

## Commands / Tests
- 基线 workflow tests: `18 passed in 1.59s`。
- R10 matrix RED: `KeyError: strategy`，`1 failed in 0.31s`。
- R10 matrix GREEN: `1 passed in 0.29s`。
- 完整 workflow tests: `19 passed in 1.46s`。
- Bash replay syntax: PASS。
- Ruff: PASS。
- Program validate / constraints: PASS / no BLOCKERs。
- Repository inventory: `1 passed in 138.18s`，`1185/1185/0/7`、close `225/218`。

## Blockers / Risks
- 无产品 blocker；API/网络/runner 排队仅为观察态，不消耗修复轮次。

## Local PR Review
- none

## Exact Next Steps
- 完成唯一一次最终 Program Truth sync，随后不再修改 tracked 记录。
- 提交并推送当前单一 dev 分支，创建唯一 PR。
- 以首个 PR exact HEAD 验证真实 Ubuntu R10 partial receipt 与 R06 回归。
