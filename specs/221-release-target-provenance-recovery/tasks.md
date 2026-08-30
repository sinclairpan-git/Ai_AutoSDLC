---
related_plan: docs/FRAMEWORK_ROADMAP.zh-CN.md
---

# 任务分解：发布目标历史归因恢复

**编号**：`221-release-target-provenance-recovery` | **日期**：2026-08-30
**阶段**：admission audit 已合并；records-only closeout；真实能力补缺 `needs_user`

## Batch 1：基线与 formal

### T11 冻结 exact-main 与边界（P0）

- [x] 记录 `origin/main@263abb3d0171a58762d382e73db9a9a692707268`
- [x] 固定 16 个 release-target blocker 清单
- [x] 明确不改 runtime、历史 log、classifier、版本与 P3
- 验证：Git SHA、Program Truth audit、focused truth-check baseline

## Batch 2：carrier census

### T12 逐项验证 16 个历史引用（P0）

- [x] 检查 formal anchor 与历史叙事
- [x] 检查真实主线 commit、changed path、runtime symbol/test
- [x] 逐个验证 carrier commit 为 `origin/main` 祖先
- 验证：`git log/show/blame/merge-base` 与源码符号检索

## Batch 3：对抗决策与归档

### T13 执行 16/16 admission gate（P0）

- [x] 形成 11/16 deterministic、1/16 缺失、4/16 部分的结论
- [x] 禁止批量历史 log 回填
- [x] 决策标记为 `needs_user`

### T14 同步 formal、路线图与 continuity（P1）

- [x] WI221 spec/plan/tasks/log 对齐审计结果
- [x] 路线图不再把已完成的 P2 写为下一项
- [x] 运行 Program Truth sync、constraints、manifest validation 与 diff scope 验证
- [x] 记录唯一获批的测试例外：只更新 manifest inventory/close layer 两条固定期望，不改其他测试或弱化断言
- [x] 更新 canonical/scoped handoff

### T15 合并后远端真值收口（P1）

- [x] 记录 PR #187 exact head、merge commit、Codex 结论与 required checks
- [x] 将未授权能力改为显式 No-Go 清单，避免被 close-check 误读为待执行任务
- [x] 补齐 latest batch 的 verification profile、统一验证、git lifecycle 与真实主线路径证据
- [x] 保持 Program Truth 的 16 个历史 blocker、11/16 admission 结论和既有测试基线

## 明确未授权任务

- 未授权且未执行：实现 `098` posture detector。
- 未授权且未执行：实现 `099` posture-gated resolver。
- 未授权且未执行：补齐 `100/101` whole-plan rollback、同 action retry 与 honest replay。
- 未授权且未执行：修改 095/098 或其余历史 execution log。
- 未授权且未执行：修改 truth classifier、删除 blocker 或发布 v0.9.9。
