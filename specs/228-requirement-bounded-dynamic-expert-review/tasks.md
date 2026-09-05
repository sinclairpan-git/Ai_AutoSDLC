---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---
# 任务分解：Requirement Loop 有界动态专家评审纵向薄片

**编号**：`228-requirement-bounded-dynamic-expert-review` | **日期**：2026-09-05
**来源**：`spec.md` + `plan.md`
**当前边界**：本 docs branch 只完成 Batch 1；Batch 2–4 必须在 formal 合入后的唯一 implementation PR 执行

## 分批策略

```text
Batch 1: formal baseline + adversarial admission review
Batch 2: tests-first Requirement input/execution slice
Batch 3: three blind value replays + Go/No-Go
Batch 4: adversarial implementation review + one terminal PR
```

## Batch 1：Formal 基线与准入

### Task 1.1 冻结现状、边界与方案

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`
- **可并行**：否
- **任务**：
  - [x] 绑定 `origin/main@71e4ff5098505d0c6321c9162c1b9b1647d155d1`。
  - [x] 证明缺口是 Requirement review/digest/round contract，而非现有 freeze bug。
  - [x] 选择 Requirement 专属薄片；拒绝复制通用五阶段 kernel 和纯提示方案。
- **验收标准**：覆盖/排除、兼容策略、瞬时模型、轮次语义、600 gross-added-lines 硬上限和 No-Go 可独立执行。
- **验证**：源码/路线图/参赛版稳定行为对账。

### Task 1.2 完成双专家对抗评审与 formal 归档

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：formal 四件套、Program Truth、canonical/scoped handoff
- **可并行**：是（两个只读专家）
- **任务**：
  - [x] 产品/ROI 专家审查用户价值、三次回放阈值和退出条件；初审 `PRODUCT REJECT`。
  - [x] 架构/代码纯洁专家审查最小实现、兼容、安全、状态与体量边界；初审 `ARCHITECTURE REJECT`。
  - [x] 最多一轮整改复审后取得两个身份同一 formal head 的 PASS；否则 No-Go。
  - [ ] 同步 Program Truth、continuity、验证并创建/合并 formal PR。
- **验收标准**：两位专家在同一文档版本无 Critical/Important；formal PR 不含产品代码或无关 adapter 刷新。
- **验证**：`program validate`、truth sync/audit、constraints、plan-check、manifest regression、`git diff --check`、exact-head review/checks。

## Batch 2：测试先行的 Requirement 薄片

### Task 2.1 固定 review input/execution、角色与只读合同

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12 + formal 已合入
- **文件**：`src/ai_sdlc/core/requirement_review.py`、定向 unit/integration tests
- **可并行**：否
- **任务**：
  - [ ] 先写失败测试固定 canonical projection/digest、一个 primary、可选一个 cross-risk、多风险优先级和严格 execution schema。
  - [ ] 实现瞬时 input/execution 模型与 Requirement 专属构建器，不导入 writer/store 写路径。
  - [ ] 证明 review 命令前后仓库文件内容与集合不变。
- **验收标准**：角色数恒为 1–2；风险原因可解释；相同输入摘要稳定；reviewer 只消费返回 projection；没有新 review artifact。
- **验证**：`tests/unit/test_requirement_review.py` + CLI integration。

### Task 2.2 接入两轮复用与 freeze 漂移保护

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：formal allowlist 内的 requirement writer/CLI/命令 producer/shared rule、现有 requirement tests、用户文档
- **可并行**：否
- **任务**：
  - [ ] 先写失败测试固定 `needs_user` 澄清、round 1→2、幂等不增轮、拒绝第三实质版本及 freeze 关闭 current round。
  - [ ] 新 loop 设 `review_required=true`；旧 artifact 缺字段保持 legacy open/closed freeze 兼容。
  - [ ] freeze 在任何写入前校验临时 execution 的 digest/round/完整角色/completed/no-actionable-findings。
  - [ ] 同步所有冻结命令 producer、共享 active-agent rule 和最短迁移说明。
- **验收标准**：只给 digest、stale/malformed/missing/failed/incomplete/actionable execution 均 fail closed；新 loop 只有当前 clean execution + `--yes` 可关闭；legacy 与现有异常路径不回归。
- **验证**：定向 unit/integration、Ruff、constraints、allowlist 检查；`git diff --numstat <formal-merge-base>...HEAD -- src/ai_sdlc` gross additions ≤600。

## Batch 3：三个盲测价值回放与 Go/No-Go

### Task 3.1 运行隔离盲测回放

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：三个 `/tmp` 隔离项目；把可复核回放证据写入 execution log
- **可并行**：否
- **任务**：
  - [ ] 先冻结三个 baseline writer 输出与隐藏 seed/预期答案，再交给不知道答案的独立专家；至少一个为 clean 负向对照。
  - [ ] 路由合同另行验证基础、安全/权限、数据迁移/兼容三类，不把命中关键词计入 ROI。
  - [ ] 每例归档命令、输入规模、耗时、exit code、baseline、专家原始输出、独立裁决、修订与终态。
  - [ ] finding 只有同时满足 baseline 未覆盖、事实正确、影响验收或风险边界、可执行、独立裁决确认时才计为有效增量。
- **验收标准**：至少两个样例各有一个有效增量 finding；clean 对照和三例合计均无错误 actionable finding；最多一次复审收敛。
- **验证**：真实 CLI、artifact inspection、hash/status no-write、隐藏答案与裁决记录。

### Task 3.2 作出不可回避的 Go/No-Go

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：execution log、tasks、roadmap 状态（仅真实结论需要时）
- **可并行**：否
- **任务**：
  - [ ] 对照 SC-228-007 判定 Go/No-Go。
  - [ ] Go 只允许收口当前 Requirement 薄片；No-Go 必须从候选中移除 runtime 代码，只允许 terminal PR 归档终止事实。
- **验收标准**：结论由三次盲测证据决定，不因已投入而放宽阈值；无论 Go/No-Go 都不产生后续 records PR。
- **验证**：回执与 SC 逐项对账。

## Batch 4：实现评审与唯一 PR 收口

### Task 4.1 双专家实现评审、完整验证与 terminal PR

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32 已作出 Go 或 No-Go
- **文件**：本工作项冻结实现范围、execution log、continuity
- **可并行**：是（两个只读专家）
- **任务**：
  - [ ] 产品/ROI 与架构/纯洁专家对同一 implementation head 对抗评审。
  - [ ] 最多一轮聚焦整改复审；仍不一致或有 Critical/Important 即 No-Go。
  - [ ] Go：运行全量 pytest、Ruff、constraints、program validate、workitem close-check；No-Go：确认 runtime diff 已归零并验证 formal closure truth。
  - [ ] 创建唯一 terminal PR；Go 时为 implementation+closure，No-Go 时仅含 closure；取得 exact-head Codex clean review 与 required checks 后合并。
- **验收标准**：只有一个 terminal PR、没有 post-merge records-only PR、没有新治理机制；fresh-main 验收通过。
- **验证**：命令回执、PR/merge SHA、fresh detached main。

## 硬停止条件

- 从 formal merge base 到候选 HEAD，`src/ai_sdlc/**` gross added lines 大于 600，或产品源码越过 plan 冻结 allowlist。
- 需要新状态机/session/ledger/certificate/attestation/quorum/lease/optimizer/provider registry/阻断式 Lean。
- 需要同时实现第二类 Loop，或用通用平台为未来需求预留。
- Formal 或实现对抗评审最多两轮仍不能一致通过。
- 三个盲测回放未达到有效 finding/零错误 actionable finding 阈值，或任一回放需要第三轮。
- 需要第二个 terminal PR 或额外 records-only closeout PR。

触发任一项即记录 No-Go 并关闭 WI228，不新建延续本轮优化的工作项。
