---
related_doc:
  - "specs/140-program-truth-ledger-release-audit-baseline/spec.md"
  - "program-manifest.yaml"
  - "src/ai_sdlc/models/program.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "src/ai_sdlc/cli/workitem_cmd.py"
  - "src/ai_sdlc/core/close_check.py"
  - "src/ai_sdlc/telemetry/readiness.py"
  - "src/ai_sdlc/rules/quality-gate.md"
---
# 实施计划：Program Truth Ledger And Release Audit Baseline

**功能编号**：`140-program-truth-ledger-release-audit-baseline`
**日期**：2026-04-14
**规格**：`specs/140-program-truth-ledger-release-audit-baseline/spec.md`

## 概述

`140` 的目标不是补某一条 runtime 业务链，而是建立一套 program-level 机器账本，让仓库随时都能回答：

- 总目标是什么
- 当前 release target 是什么
- 每个 capability 由哪些 spec 承载
- 每个 spec 属于什么 role
- 任务/测试/CLI/acceptance evidence 到哪里了
- 为什么现在能发或不能发

推荐实现路径是：先冻结 schema 和边界，再补齐全仓索引与 capability mapping，最后把最小 snapshot / audit / gate 接到现有 CLI 和 close/release surfaces。

## 技术背景

**语言/版本**：Python 3.11
**主要依赖**：Pydantic program models、ProgramService、Typer CLI、现有 `workitem truth-check` / `workitem close-check` / readiness surfaces
**存储**：根级 `program-manifest.yaml`
**测试**：unit + integration focused checks
**目标平台**：program-level ledger / snapshot / release audit
**约束**：

- 不引入第二份 manifest 或平行真值文件
- 不改写 `082/087` 已冻结的 field-level canonical source-of-truth contract
- `truth_snapshot` 只能由显式 write surface 更新，read surfaces 保持只读
- snapshot 只持久化最小聚合结果，不复制逐项 runtime truth
- schema 设计必须兼容旧版本升级路径，并能显式暴露 `stale/invalid/legacy_unclassified`
- `140` v1 的 mandatory evidence 只允许来自 truth-check / close-check / verify；不引入新的手工 command/probe registry
- 在实现前，`spec.md` 与 `plan.md` 必须经过两个对抗 agent 两轮评审

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | 继续只保留一个 program-level 入口，并保留既有 field-level ownership |
| 最小改动面 | 先扩 schema / service / CLI / gate，不在本批混入缺失 runtime feature 实现 |
| 流程诚实 | 把 formal close 与 release closure 正式拆开，并让 release audit fail-closed |
| 历史兼容 | 把旧 schema / 缺 entry / stale snapshot 视为显式 blocker，而不是静默降级 |

## 实施批次

### Phase 0：Formal freeze 与对抗评审

**目标**：冻结 `140` 的边界，不让实现阶段再漂移成第二真值系统或手写总账本。

**步骤**：

1. 起草 `spec.md` 与 `plan.md`
2. 交给两个对抗 agent 做第 1 轮评审
3. 根据评审意见修订 spec/plan
4. 再做第 2 轮评审
5. 仅在两轮评审都收敛后进入实现

**产物**：

- `specs/140-program-truth-ledger-release-audit-baseline/spec.md`
- `specs/140-program-truth-ledger-release-audit-baseline/plan.md`

### Phase 1：Schema 与模型层升级

**目标**：把 `ProgramManifest` 从浅层 DAG 模型扩成 ledger 模型，但不破坏既有 field-level ownership。

**步骤**：

1. 为 `program`、`release_targets`、`capabilities[]`、扩展后的 `specs[]` 与最小 `truth_snapshot` 设计严格 schema
2. 在 model 层启用显式枚举与 `extra=forbid`
3. 明确 `closure_state` 与 `audit_state` 的分层，不让 snapshot 另造第二套 closure 词表
4. 保留对旧 schema 的加载兼容，并为 migration blocker 预留状态位

**验证方式**：

- model load / validation unit tests
- 旧 schema fixture 与新 schema fixture 兼容测试

### Phase 2：全仓索引与 capability mapping

**目标**：让 manifest 真正覆盖全仓，而不是部分 spec 子集。

**步骤**：

1. 按 “包含 `spec.md` 的 `specs/*` 子目录” 口径扫描 repo census
2. 补齐缺失 manifest entries
3. 为每个 spec 标注 role 与 capability refs
4. 为每个 capability 声明 release-required 与 required evidence refs
5. 校验 spec <-> capability 双向引用一致性
6. 给旧 schema / legacy specs 输出最小补齐建议，而不是只报空泛 blocker
7. 将 enforcement 拆成 migration gap 与 release blocker 两层，避免非 release-scope 历史债务在 v1 直接卡死全部发布

**验证方式**：

- truth audit fixture：缺 entry / 重复 entry / orphan entry / missing role / broken capability refs
- focused repo census regression

### Phase 3：Truth snapshot 与 program CLI surfaces

**目标**：建立最小机器快照与显式 sync/audit surfaces。

**步骤**：

1. 实现 `build_truth_ledger()` / `sync_truth_snapshot()` / `validate_truth_ledger()`
2. 增加 `program truth sync --dry-run/--execute`
3. 增加 `program truth audit`
4. 让既有 `program status` 消费 ledger/snapshot
5. 接入 `workitem truth-check`、`workitem close-check`、`verify constraints` 作为 v1 mandatory audit 输入；command/probe refs 仅在已有稳定 machine surface 时按 optional extension 处理
6. task progress 与逐项 evidence 细节保持 read-time derived，不持久化进 snapshot

**验证方式**：

- integration tests：human table / JSON output / dry-run / execute / stale detection
- source hash 变化后的 snapshot invalidation 测试

### Phase 4：Release audit 与 status/readiness integration

**目标**：把 ledger 从“可看见”提升为“能阻断假绿发布”。

**步骤**：

1. 引入 release audit hard gate
2. 将 authoritative `closure_state` 与独立 `audit_state` 接入 close/release 路径，并明确 `audit_state` 是唯一 release 裁决状态
3. 改造 readiness / status surfaces，显式暴露 `invalid/stale`
4. 任何 canonical conflict 必须强制映射为 `audit_state=blocked`
5. 保持 read-only surfaces 不写 snapshot

**验证方式**：

- integration tests：open `closure_state` / non-ready `audit_state` / `stale` / missing evidence fail-closed
- close/release gate focused regression

### Phase 5：Derived views 与迁移收口

**目标**：让人读视图服从 ledger/snapshot，同时为旧仓库升级提供闭环。

**步骤**：

1. 将 rollout / summary / dashboard 改为 derived views
2. 明确 derived view 必须带 `generated_at` / `repo_revision`
3. 提供 migration diagnostics，显式报告旧 schema、缺映射、缺 hashes、legacy roles
4. 补齐用户文档与升级路径说明

**验证方式**：

- integration tests：derived view freshness 标记
- migration fixtures：旧 schema -> 新 ledger 的阻断与 remediation 提示

## 风险与回退

- **风险 1：误把 manifest 变成 field-level truth 的唯一 origin**
  - 回避：明确保留 `082/087` ownership contract，spec 中写死“program-level 入口不改写既有 field-level canonical source”
- **风险 2：read surfaces 偷写 snapshot，复发 split-truth drift**
  - 回避：把 snapshot 写权限收敛到显式 `program truth sync`
- **风险 3：全仓 spec backfill 改动面过大**
  - 回避：先做 schema / audit / fixture，再分批补 manifest entries 与 capability mapping
- **风险 4：旧仓库升级被静默降级**
  - 回避：`stale/invalid/legacy_unclassified` 显式 surfaced，release scope fail-closed

## 验证策略

最小验收命令集至少包括：

- `python -m ai_sdlc adapter status`
- `python -m ai_sdlc run --dry-run`
- `uv run pytest` 的 focused truth-ledger / release-audit suites
- `uv run ruff check` 针对改动文件
- `uv run ai-sdlc program validate`
- `uv run ai-sdlc program truth audit`
- `uv run ai-sdlc workitem truth-check --wi specs/140-program-truth-ledger-release-audit-baseline`

## 退出条件

1. `140` 的 spec/plan 完成两轮对抗评审并收敛
2. ledger schema 能覆盖全仓 spec 索引与 capability mapping
3. snapshot 与 audit 能稳定输出最小状态、blocking refs 与 freshness，详细 progress/evidence 继续由 read-time surface 推导
4. release audit 能阻断假绿发布
5. derived views 与 migration diagnostics 都服从 ledger/snapshot
