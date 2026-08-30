---
related_plan: "docs/FRAMEWORK_ROADMAP.zh-CN.md"
---

# 功能规格：发布目标历史归因恢复

**功能编号**：`221-release-target-provenance-recovery`
**创建日期**：2026-08-30
**状态**：formal admission audit 已完成；`needs_user`
**唯一基线**：`origin/main@263abb3d0171a58762d382e73db9a9a692707268`

## 目标

在不改写历史、不放宽 `formal_freeze_only`、不删除 blocker 的前提下，核对 Program Truth 当前 16 个 release-target blocker 是否都能绑定到真实主线实现载体。该工作只恢复可证明的 provenance；不能把 formal contract、计划或后续相邻能力当作本工作项已经实现。

## 范围

**覆盖**：

- `frontend-mainline-delivery` 的 14 个阻塞引用；
- `agent-adapter-verified-host-ingress` 的 2 个阻塞引用；
- 每项的 formal 创建锚点、真实主线提交、代码/测试路径、执行批次与祖先关系；
- 与 WI221 状态直接耦合的路线图、Program Truth 和 continuity handoff。

**不覆盖**：

- 修改 `src/`、truth classifier 或除 `tests/integration/test_repo_program_manifest.py` 外的测试；该唯一测试例外只允许把 WI221 注册后的 source inventory/close layer 固定期望更新为 `1159/1159/0/2` 与 `220/218`，不得改测试结构或弱化断言；
- 放宽 `formal_freeze_only`、删除 blocker、制造历史执行叙事；
- v0.9.9 版本变更、P3 十二路线、全仓瘦身或产品站/本地材料分支；
- 在缺少真实实现时，仅通过给历史 log 补路径把 formal work item 伪装为已实现。

## 用户场景与验收

### US-221-1 — 发布维护者需要可信的 ready 前置条件（P0）

作为发布维护者，我希望每个 release-target 引用都能追溯到真实主线实现，以便 `ready` 表示能力确实存在，而不是历史 snapshot 或文档归因造成的假阳性。

**独立测试**：在 exact `origin/main` 上复核 16 项清单、提交祖先关系、提交改动路径和运行时符号。

**验收场景**：

1. **Given** 某项具备工作项创建后的真实主线实现，**When** 审计其 commit、path 与批次，**Then** 才允许标为 deterministic carrier。
2. **Given** 某项只有 formal docs 或仅有相邻能力，**When** 审计无法证明本项契约已实现，**Then** 必须继续保留 blocker 并返回 `needs_user`。

### US-221-2 — 评审者需要阻止反向伪造（P0）

作为评审者，我希望归因修复不能靠删 gate、放宽分类器或回填含糊路径完成，以便历史真值仍可复核。

**独立测试**：确认 WI221 formal diff 不含 `src/` 与历史工作项 execution log 修改，且唯一 test diff 是 `tests/integration/test_repo_program_manifest.py` 中获批的两条 inventory/close layer 固定期望更新。

**验收场景**：

1. **Given** 载体提交早于工作项创建，**When** 尝试归因，**Then** 不得作为该工作项执行证据。
2. **Given** 载体只覆盖母规格的一部分，**When** 其余子合同没有实现，**Then** 母规格不得标为 16/16 已归因。

## 功能需求

- **FR-221-001**：审计必须冻结 exact `origin/main` SHA 与 16 个 blocker 清单。
- **FR-221-002**：每个可归因项必须至少记录 `{work item, mainline commit, changed product/test path, semantic carrier, ancestor proof}`。
- **FR-221-003**：历史 formal-only 结论必须保留；只有后续真实实现证据才能显式补充它，不能覆盖原叙事。
- **FR-221-004**：若任一 blocker 缺少 deterministic carrier，provenance-only 实现不得开始，决策必须为 `needs_user`。
- **FR-221-005**：本轮不得修改超过三个 truth 子系统，不得新增 public API、依赖、schema 或持久化状态。
- **FR-221-006**：WI221 只允许一个 formal work item；后续若获批，最多一个 focused implementation PR 与一个必要的 records-only closeout PR。
- **FR-221-007**：两轮评审后仍无法形成确定归因时 No-Go，不继续磨细枝末节。

## 审计结论

- 可确定归因：`11/16`（`096`、`102`–`105`、`121`–`126`）。
- 不可按 provenance-only 收口：
  - `098-frontend-mainline-posture-detector-baseline`：**缺失**。主线没有契约要求的五态 detector、evidence precedence 与 `sidecar_root_recommendation` 实现；全仓 `src/` 搜索没有对应 canonical model/runtime symbol。
  - `099-frontend-mainline-delivery-registry-resolver-baseline`：**部分**。主线 handoff 只读取 solution snapshot 并返回静态 `supported_posture_modes`，没有消费 `098` posture mode，也没有执行 FR-099-020 的 posture gate。
  - `100-frontend-mainline-action-plan-binding-baseline`：**部分**。主线具备 action、decision receipt、ledger 字段和 no-touch 投影，但其 posture/registry 输入链不完整，且 FR-100-019 要求的 whole-plan rollback、同 action retry 与 honest replay 没有形成完整载体。
  - `101-frontend-mainline-managed-delivery-apply-runtime-baseline`：**部分**。后续 `123/124` 实现了窄版 apply/materialization，但 `123` 明确把自动 rollback/retry/cleanup 排除在外；当前 runtime 仅记录相关 refs，未满足 FR-101-012/013 的反向依赖整计划回滚与保留原 action id 的重试。
  - `095-frontend-mainline-product-delivery-baseline`：**部分**。host/browser 与部分 registry/action/apply 链路有真实载体，但母规格继承 `098`–`101` 的上述缺口，不能独立宣称完整交付。
- 决策：`needs_user`。当前禁止对 16 个历史 log 执行批量路径回填；WI221 也不得把整改扩大为 runtime 实现。若业务仍要求解除发布门，必须由用户另行批准一个重新估算、覆盖 posture detector、posture-gated resolver、action/ledger continuity 与 apply rollback/retry 的多能力实现批次。

## ROI 与实现边界

1. **用户可观察收益**：避免 v0.9.9 以假 `ready` 发布；恢复 release target 的可信度。
2. **现状证据**：exact main 的 Program Truth 为 blocked；11 项有完整主线载体，4 项只有部分载体，`098` 无实现载体。
3. **最小方案**：本轮只做 formal + admission audit。直接批量改历史 log 虽更小，但会把缺失能力伪造成已实现，因此拒绝。
4. **投入**：本轮审计小于 0.5 人日。若另行批准真实补缺，粗估 posture detector 2–3 人日、posture-gated resolver 1–2 人日、action/apply rollback-retry continuity 4–6 人日、真值收口与评审 1–2 人日，合计 8–13 人日；按价值 7.5/10 计，ROI 约 0.6–0.9。
5. **退出条件**：不得新增第二套 posture truth；不得扩张为前端主线重写；该补缺已跨越 detector、resolver/action plan、apply runtime 与 truth closeout，超过 WI221 的 provenance-only 边界，必须重新定界并单独获批。
6. **决策**：`needs_user`；11/16 不满足发布 ready 的全量前置条件，当前推荐保持 blocked，不为赶 v0.9.9 在 WI221 内追补多能力特性。

## 成功标准

- **SC-221-001**：16 项均有逐项 census，且所有“可归因”提交均为 `origin/main` 祖先。
- **SC-221-002**：审计能明确区分 11 项完整载体、1 项缺失实现和 4 项部分载体。
- **SC-221-003**：本轮没有修改 runtime、历史 execution log 或 blocker 判定规则；测试改动仅限获批的 manifest inventory/close layer 固定期望更新。
- **SC-221-004**：路线图和 handoff 不再把已完成的 P2 写为固定下一项。
