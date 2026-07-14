---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/tasks.md"
---
# 实施计划：Source Inventory Convergence

**编号**：`201-source-inventory-convergence`
**日期**：2026-07-14
**规格**：`specs/201-source-inventory-convergence/spec.md`
**风险级别**：L2 truth/docs 修复
**实施分支**：formal 评审通过后由 `feature/201-source-inventory-convergence-docs` 切换为 `feature/201-source-inventory-convergence`

## 1. 概述

本计划用最小、可回退的 truth/docs 变更关闭 WI-196 GAP-11/T54：先以仓库集成断言重现 33 unmapped/11 missing，再补 33 个 canonical registry entry、11 个诚实的历史 summary 和 WI-201 summary，最后刷新并审计唯一的 `program-manifest.yaml` truth snapshot。产品运行时代码保持零改动。

## 2. 技术背景与设计决策

- source discovery 和 inventory 构建位于 `src/ai_sdlc/core/program_service.py`；本项只读验证，不修改。
- `source_registry` 现有 schema 仅包含 `path`、`source_type`、`truth_layer`，足以登记全部 33 个 release 文档。
- 每个 manifest spec 固定期望 `spec.md/plan.md/tasks.md/task-execution-log.md/development-summary.md`；因此 11 个 missing 应通过补真实 summary 修复。
- 当前 work item 也会进入 manifest，最终同步前必须有自身 summary，否则 debt 只会从 11 变成 1。
- 现有 inventory `complete` 不检查 missing，audit 又只按整体 ready 决定 exit 0；因此本项用仓库集成断言补足交付门禁，但不在 L2 truth 修复中改变 runtime 语义。
- 不采用 discovery allowlist、warning filter、exception schema 或历史状态重写；这些方案增加分支和第二真值，却没有当前证据需求。

## 3. 宪章与父项门禁

| 门禁 | 计划响应 |
|---|---|
| MUST-1 范围严控 | 只处理 GAP-11 精确 33/11 与 WI-201 自身 summary；产品代码预算 0 |
| MUST-2 关键路径可验证 | 现有仓库集成测试先红后绿，另执行 truth/constraints/full regression |
| MUST-3 范围、验证、回退 | formal docs 冻结 NC/CC、预算、命令、停止条件；单 PR 可 revert |
| MUST-4 状态落盘 | spec/tasks/log、root/scoped handoff、truth snapshot 和 review verdict 全部落盘 |
| MUST-5 产品/框架隔离 | 不修改产品实现；只修仓库治理 truth/docs/test |
| WI-196 FR-08 | 本计划具备进入、非目标、验证、完成、停止、回退和 evidence URI |
| WI-196 FR-10 | formal hash 与最终 HEAD 均需双 agent 同版本 PASS |

## 4. 目标文件结构

```text
program-manifest.yaml                              # 33 registry entries + generated snapshot
tests/integration/test_repo_program_manifest.py   # existing test, completeness assertions
specs/{183,186,188..196}/development-summary.md   # 11 honest historical summaries
specs/201-source-inventory-convergence/
├── spec.md
├── plan.md
├── tasks.md
├── task-execution-log.md
└── development-summary.md
.ai-sdlc/state/codex-handoff.md
.ai-sdlc/work-items/201-source-inventory-convergence/codex-handoff.md
```

`src/ai_sdlc/**`、33 个 `docs/releases/*.md` 正文和公共 schema 不在目标结构内。

## 5. 阶段计划

### Phase 0：基线与 formal freeze

1. 在 `origin/main@c737eda056...` 的隔离 worktree 记录 1061/1028/33/11 和精确路径集合。
2. 完整重写 init 生成的 placeholder 文档，冻结 NC-01～NC-06、CC-01/02/03/06、预算、回退和停止条件。
3. 在仓库根目录使用以下唯一算法计算 formal hash；digest 取输出第一列，不允许改用文件原始字节串联：

   ```text
   for f in specs/201-source-inventory-convergence/spec.md specs/201-source-inventory-convergence/plan.md specs/201-source-inventory-convergence/tasks.md; do shasum -a 256 "$f"; done | sort -k2 | shasum -a 256
   ```

4. 两名 agent 分别从兼容/真实性/回退安全与精简/直接性/过度实现维度对同一 hash 评审；任一 finding 触发修订和双重重审。

**进入 Phase 1 条件**：同一 formal hash 双 PASS，placeholder 检查为零，formal baseline 已提交。

### Phase 1：TDD RED

在 `tests/integration/test_repo_program_manifest.py` 的现有根仓库测试中加入：

- inventory state 为 `complete`；
- `total_sources == mapped_sources`；
- `unmapped_sources == 0`；
- `missing_sources == 0`；
- validation warnings 不含 unmapped truth source 前缀。
- 33 个 release registry entry 的 `path/source_type/truth_layer` 精确匹配，避免“错误 type/layer 仍 mapped”的假绿。

在未修 manifest/summary 的 WI-201 投影运行该测试并记录 33/12 导致的预期失败。禁止为获得红灯而改 runtime 或造临时 fixture。

### Phase 2：最小 truth/docs 修复

1. 在 `source_registry` 现有 release 段逐项新增 33 个 entry，保持既有排序与三字段 schema。
2. 对 11 个历史 WI 逐项读取 spec/tasks/log/commit/PR 证据，写不超过预算的 summary。
3. 写 WI-201 summary，状态只反映当时真实进度，并在最终 execute sync 前完成所有仓库内证据更新；PR/终审/mainline 结果只追加到外部 receipt，不在 sync 后回写该文件。
4. 不触碰产品代码、release 正文和历史状态文件。

**停止条件**：任一 summary 无证据可写、registry 需要 schema 扩展、出现基线外 debt，立即返回设计评审。

### Phase 3：GREEN、证据冻结与最终 truth sync

按顺序执行：

1. targeted integration test、`uv run pytest`、`uv run ruff check src tests`；
2. `uv run ai-sdlc program validate`、`uv run ai-sdlc verify constraints`；
3. `uv run ai-sdlc program truth sync --dry-run`，确认 12 份 summary 已齐且预期为 1066/1066/0/0；
4. 检查预算、placeholder、重复 registry、`git diff --check` 和 Cursor 零 diff；把 RED/GREEN、测试、预算、dry-run、回退步骤写入 execution log/summary/handoff，形成 evidence-freeze commit；
5. 在 evidence-freeze clean HEAD 只复跑 targeted、validate、constraints、truth dry-run、预算、diff check 与 Cursor 检查；full pytest/Ruff 已在同一候选的步骤 1 完成，不重复执行；任何失败都先修复仓库证据并重新冻结；
6. 仅在全部仓库内证据冻结后执行唯一一次 `uv run ai-sdlc program truth sync --execute --yes`，提交只包含最终 manifest snapshot；
7. 从此禁止修改 inventory-covered 文件；在 snapshot-only final clean HEAD 只读运行 targeted、validate、audit、truth dry-run、constraints 与 diff check，确认 snapshot fresh、幂等和受 snapshot 影响的门禁；不重复 full pytest/Ruff。

目标 differential：migration pending count `33→0` 及有限 pending-source 预览消失、audit exit `1→0`、inventory `incomplete→complete`、program `migration_pending→ready`；最终 source=`1066/1066/0/0`、close=`202/202`，两个 capability 均保持 `closed/ready/[]`；其余 CLI/schema/runtime 行为零未批准差异。

### Phase 4：双终审与 mainline 交付

1. 在 final clean HEAD 创建临时 clean worktree，对冻结基线 `c737eda056b2c86a6110ab32db237c417ee19a04..HEAD` 的全部候选提交按逆序执行 `git revert --no-commit`；验证回退态 tree 等于冻结基线、source=1061/1028/33/11、audit 因且仅因 33 个 unmapped source 退出 1、独立断言 missing=11、两个 capability=`closed/ready/[]`，记录命令、退出码和 tree hash 后删除临时 worktree。
2. 两名既有对抗 agent 对同一 final clean HEAD 和 rollback receipt 独立终审；任一修订使两份 PASS 同时失效。verdict 保留在外部 task receipt，禁止回写分支。
3. 推送分支、创建 PR，将 formal/final verdict、rollback receipt、snapshot 三元组和 reviewed HEAD 写入 PR comment，随后请求 `@codex review`；约五分钟 heartbeat 监控 Codex 与 required checks。
4. actionable finding 在同分支聚焦修复后必须从 Phase 3 evidence freeze 重新开始，并重做 rollback、双审和 Codex review；全部通过后合并。
5. 在 fresh `origin/main` checkout 记录 PR merge SHA，验证 reviewed HEAD 与 merge SHA 在本 PR 相关路径上 tree/diff 等价，复跑 targeted、truth audit、constraints；外部 PR receipt 记录 `repo_revision/generated_at/snapshot_hash`、1066/1066/0/0、202/202、两个 `closed/ready/[]` 和各命令退出码。

## 6. 验证命令

```text
uv run pytest tests/integration/test_repo_program_manifest.py::test_root_program_manifest_covers_specs_and_host_ingress_canonical_evidence -q
uv run ai-sdlc program validate
uv run ai-sdlc program truth sync --dry-run
uv run ai-sdlc program truth sync --execute --yes
uv run ai-sdlc program truth audit
uv run ai-sdlc verify constraints
uv run pytest
uv run ruff check src tests
git diff --check
```

仓库首选 PowerShell；当前机器 `pwsh` 在命令执行前因 `System.Text.RegularExpressions Version=10.0.0.0` 加载失败，因此本 worktree 使用已登记的 zsh fallback。最后一次 execute sync 前的命令与结果写入仓库 execution log；execute sync 后的 clean-HEAD 复验、rollback、双审、PR/CI 和 mainline 结果只写外部 immutable task/PR receipt，禁止再修改 branch 内 log、summary、handoff 或其他 inventory-covered 文件。

## 7. 回退、owner 与风险

- **owner**：AI-SDLC framework maintainers。
- **代码/文档回退**：revert WI-201 单一 PR；预合并在临时 clean worktree 演练整个冻结基线 `c737eda056...HEAD` 反向提交集，必须恢复相同 base tree、1061/1028/33/11，且不影响两个 capability。
- **artifact 恢复**：在目标 revision 重新执行 truth sync，禁止手工拼装 snapshot。
- **主要风险**：summary 夸大历史完成度、当前 WI 制造新 missing、CLI 副作用污染 Cursor、snapshot 与目标 commit 不一致。
- **控制**：逐项证据、sync 前 evidence freeze、Cursor exact restore、final clean-HEAD 只读 audit、整分支 rollback drill、外部双 agent/PR receipt。

## 8. 开放问题

无。若实施证据表明存在真正不可补齐的 source，才新增独立设计问题；本计划不预造例外机制。
