---
related_plan: docs/FRAMEWORK_ROADMAP.zh-CN.md
---

# 实施计划：发布目标历史归因恢复

**编号**：`221-release-target-provenance-recovery` | **日期**：2026-08-30 | **规格**：`specs/221-release-target-provenance-recovery/spec.md`

## 概述

本阶段只完成 WI221 formal 建项和半天 admission audit。退出结果是可复核的 Go/No-Go，不是自动进入历史记录回填；发现任何真实实现缺口即停在用户决策门前。

## 技术背景

- **基线**：`origin/main@263abb3d0171a58762d382e73db9a9a692707268`
- **主要工具**：Git history/path inspection、`uv run ai-sdlc workitem truth-check`、`program truth audit/sync`
- **测试**：truth-check integration baseline、governance constraints、manifest validation、diff scope inspection
- **约束**：只读归因；不改 `src/`、历史 execution log 或 classifier。唯一获批的 test 例外是 `tests/integration/test_repo_program_manifest.py` 中两条 WI221 注册后 inventory/close layer 固定期望更新（`1159/1159/0/2`、`220/218`），不得扩张到其他测试或弱化断言

## 宪章检查

| 门禁 | 计划响应 |
|---|---|
| 主线事实优先 | 所有证据固定为 exact `origin/main`，忽略本地材料/产品站分支与 worktree |
| 不伪造执行 | formal-only 叙事保留；缺实现时返回 `needs_user` |
| ROI 与有界投入 | admission audit 小于 0.5 人日；未通过 16/16 不启动 3–6 人日历史回填 |
| 抑制实现膨胀 | 不新增 schema、命令、ledger、waiver、classifier 或第二套 truth |

## 项目结构

```text
specs/221-release-target-provenance-recovery/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
tests/integration/test_repo_program_manifest.py  # 仅更新获批的两条固定期望
```

无源码结构变更。

## 阶段计划

### Phase 0：exact-main 基线冻结

- 冻结 SHA、16 个 blockers、基线测试与 Program Truth 状态。
- 验证：`git rev-parse origin/main`、truth audit、focused truth-check tests。

### Phase 1：16 项 carrier census

- 对每项检查 formal anchor、后续主线 commit、changed paths、runtime symbols、tests 和祖先关系。
- 历史 blocker map 只作为查找索引，不作为实现证据。

### Phase 2：对抗决策

- 只有 16/16 全部确定且无真实能力缺口才允许提出 records-only 实现方案。
- 当前结果为 11/16；`098` 缺失，`095/099/100/101` 部分。停止历史回填并进入 `needs_user`。

## 关键路径验证策略

| 关键路径 | 主验证 | 补充验证 |
|---|---|---|
| 提交属于远端主线 | `git merge-base --is-ancestor <sha> origin/main` | `git show --name-only <sha>` |
| 工作项创建后才实现 | work item path history + commit date/order | execution log formal-only statement |
| 语义确实匹配 | runtime symbol/path inspection | 对应 unit/integration tests |
| 无膨胀 | `git diff --name-only origin/main...HEAD` | 不含 `src/`、历史 log；test diff 仅为具名文件中的两条获批固定期望更新 |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|---|---|---|
| 是否另行批准一个覆盖 `098/099/100/101` 真实缺口的重新定界实现批次 | `needs_user` | execute |
| 若不批准，是否接受 v0.9.9 继续被 Program Truth 阻断 | `needs_user` | release |

## 后续顺序

1. 合并 WI221 formal/admission record。
2. 默认保持 release target blocked，不在 WI221 内启动 runtime。
3. 若用户明确要求解除发布门，先建立并评审覆盖 posture、resolver/action 与 apply continuity 的新范围；仅在批准且真实实现通过后回填可证明的 provenance。
4. release target `ready` 后再进入 v0.9.9。
