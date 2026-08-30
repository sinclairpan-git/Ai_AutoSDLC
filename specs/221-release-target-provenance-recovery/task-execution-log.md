# 任务执行日志：发布目标历史归因恢复

**功能编号**：`221-release-target-provenance-recovery`
**创建日期**：2026-08-30
**状态**：formal admission audit 已合并；records-only closeout receipt 已形成；真实能力补缺 `needs_user`

## Batch 2026-08-30-001 | exact-main carrier census

### 1. 批次范围

- 覆盖任务：`T11`、`T12`、`T13`、`T14` formal portion
- 唯一事实源：`origin/main@263abb3d0171a58762d382e73db9a9a692707268`
- 验证画像：`docs-only / read-only-history-audit`
- 改动范围：WI221 formal docs、`program-manifest.yaml`、project sequence、路线图和 continuity records
- 排除：`src/`、除 `tests/integration/test_repo_program_manifest.py` 外的 tests、16 个历史 work item logs、产品站与本地材料分支/worktree。唯一获批的 test 例外只更新 WI221 注册后的 inventory/close layer 两条固定期望（`1159/1159/0/2`、`220/218`），不改测试结构、不弱化断言

### 2. 基线验证

- `uv sync`：通过。
- `uv run pytest tests/integration/test_cli_workitem_truth_check.py -q`：`40 passed in 28.79s`。
- `uv run ai-sdlc verify constraints`：`no BLOCKERs`。
- exact-main Program Truth：`state=blocked`、snapshot fresh；source inventory `1154/1154` mapped；当前 16 个 release-target blockers 保留。
- WI221 注册后执行 `uv run ai-sdlc program truth sync --execute --yes`：snapshot 仍为 `blocked`，16 个 blockers 原样保留；source inventory `1159/1159` mapped、0 unmapped。
- fresh `uv run ai-sdlc program truth audit`：`state=blocked`、snapshot fresh；两个 release target 均保持 blocked。
- `uv run ai-sdlc workitem plan-check --wi specs/221-release-target-provenance-recovery`：补齐与路线图的 `related_plan` 后 `Pending todos=0`、`Drift=NO`。
- 第二轮记录修正后 fresh `uv run pytest tests/integration/test_cli_workitem_truth_check.py -q`：`40 passed in 27.42s`。
- 提交前 `workitem truth-check --rev HEAD` 诚实返回 formal docs 不存在于旧 `HEAD`；首次提交后对 exact commit 重跑得到 `branch_only_implemented`。该分类只表示 WI221 的审计/路线图收口已执行，不表示 095/098 runtime 已实现；`code_paths=[]`、`test_paths=[]`。

### 3. 逐项 carrier census

审计命令口径：formal anchor 使用 `git log --reverse --format=%H -- specs/<wi>` 的首个提交；载体路径使用
`git show --name-only <carrier>`；祖先关系使用 `git merge-base --is-ancestor <sha> origin/main`。下表的 anchor 与
carrier 均已对 exact `origin/main` 得到退出码 0；`098` 无 carrier，因此只对其 formal anchor 验证祖先关系。

| WI | Formal anchor | 结论与完整 carrier SHA | 精确 source / test 路径与 semantic carrier | 执行批次 | 祖先证明 |
|---|---|---|---|---|---|
| 095 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **部分**；代表载体 `471a500dfaad629e92d8e8b02a1965871e92a5fa`、`8094d0017e38af2ce968d3b850bc472bcdc5f102`、`db9dbd901670c1857de7dbd226ea20739b843a64`、`93728e4b5305b4588a4308d18bf31a2a434b8afe`、`0605f913de80fe3b508bb263bf34bc47d604d2bc`、`169ca9cfd780e2253794354f1261b40916bbecbd`、`e8fae20bf619af463058acbe8072c6fc8b09c3c2` | `src/ai_sdlc/core/host_runtime_manager.py`；`src/ai_sdlc/core/program_service.py`；`src/ai_sdlc/core/managed_delivery_apply.py`；`src/ai_sdlc/core/frontend_browser_gate_runtime.py`；对应 `tests/unit/test_host_runtime_manager.py`、`tests/unit/test_program_service.py`、`tests/unit/test_managed_delivery_apply.py`、`tests/unit/test_frontend_browser_gate_runtime.py`。host→registry→apply→browser 有载体，但继承 098–101 缺口 | 096 Batch 003/004；123/124/125/126 runtime batches | anchor/carriers `yes (exit 0)` |
| 096 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **deterministic**；`471a500dfaad629e92d8e8b02a1965871e92a5fa`、`bbe610de5db5b2c551d7863b58a284cd111111d0` | `src/ai_sdlc/core/host_runtime_manager.py`、`src/ai_sdlc/models/host_runtime_plan.py`、`src/ai_sdlc/cli/host_runtime_cmd.py`；`tests/unit/test_host_runtime_manager.py`、`tests/integration/test_cli_host_runtime.py`；`build_host_runtime_plan` / `evaluate_current_host_runtime` | 096 Batch 2026-04-13-003/004 | anchor/carriers `yes (exit 0)` |
| 098 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **缺失**；无 carrier | 全仓 `src/` 无五态 posture detector、evidence precedence、`sidecar_root_recommendation` canonical model/runtime/test | 098 只有 formal freeze 与 close normalization，无 implementation batch | anchor `yes (exit 0)`；carrier `N/A` |
| 099 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **部分**；`8094d0017e38af2ce968d3b850bc472bcdc5f102` | `src/ai_sdlc/core/program_service.py`；`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`；`ProgramFrontendDeliveryRegistryHandoff` / `build_frontend_delivery_registry_handoff` 只加载 solution snapshot 并返回静态 posture modes，没有 `ResolverSelectionContext` 或 FR-099-020 posture gate | 099 log 只有 formal/close；载体为后续独立 handoff commit，无完整 resolver batch | anchor/carrier `yes (exit 0)` |
| 100 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **部分**；`db9dbd901670c1857de7dbd226ea20739b843a64` | `src/ai_sdlc/models/frontend_managed_delivery.py`、`src/ai_sdlc/core/program_service.py`；`tests/unit/test_program_service.py`、`tests/unit/test_managed_delivery_apply.py`；`FrontendActionPlanAction`、`DeliveryApplyDecisionReceipt`、`DeliveryActionLedgerEntry` 与 `will_not_touch` 已存在，但 posture/registry 输入链和 FR-100-019 rollback/retry replay 不完整 | 123 Batch 2026-04-13-002 narrow apply runtime | anchor/carrier `yes (exit 0)` |
| 101 | `ace0ed7a8ed9ef8a3de3bdf4fe57d9046e36b55e` | **部分**；`db9dbd901670c1857de7dbd226ea20739b843a64`、`93728e4b5305b4588a4308d18bf31a2a434b8afe` | `src/ai_sdlc/core/managed_delivery_apply.py`、`src/ai_sdlc/models/frontend_managed_delivery.py`；`tests/unit/test_managed_delivery_apply.py`；session/apply/materialization 与 ledger refs 存在，但 runtime 明示 `rollback/retry/cleanup refs recorded only`，没有 FR-101-012/013 的反向依赖 whole-plan rollback 与同 action-id retry | 123 Batch 2026-04-13-002；124 Batch 2026-04-14-001 | anchor/carriers `yes (exit 0)` |
| 102 | `280c2a45971387b5daa4865ec17e717f7f583fa5` | **deterministic**；`0605f913de80fe3b508bb263bf34bc47d604d2bc`、`169ca9cfd780e2253794354f1261b40916bbecbd`、`e8fae20bf619af463058acbe8072c6fc8b09c3c2` | `src/ai_sdlc/models/frontend_browser_gate.py`、`src/ai_sdlc/core/frontend_browser_gate_runtime.py`、`src/ai_sdlc/core/frontend_gate_verification.py`、`scripts/frontend_browser_gate_probe_runner.mjs`；`tests/unit/test_frontend_browser_gate_runtime.py`、`tests/unit/test_program_service.py`、`tests/unit/test_frontend_gate_verification.py`、`tests/integration/test_cli_program.py`；`BrowserQualityGateExecutionContext`、real Playwright runner 与 execute-decision mapping | 125 Batch 2026-04-14-001 + post-batch real-runner carrier；126 Batch 2026-04-14-001/003 | anchor/carriers `yes (exit 0)` |
| 103 | `6f8788556b441404817c756b10f3ba4bbb2eab6d` | **deterministic**；`0605f913de80fe3b508bb263bf34bc47d604d2bc`、`169ca9cfd780e2253794354f1261b40916bbecbd` | `src/ai_sdlc/core/frontend_browser_gate_runtime.py`、`src/ai_sdlc/models/frontend_browser_gate.py`；`tests/unit/test_frontend_browser_gate_runtime.py`、`tests/integration/test_cli_program.py`；`BrowserGateProbeRuntimeSession` / `materialize_browser_gate_probe_runtime` / real runner | 125 Batch 2026-04-14-001 + post-batch real-runner carrier | anchor/carriers `yes (exit 0)` |
| 104 | `2d3be7051acffca4dd34371cd811f2bef6edbb8d` | **deterministic**；`e8fae20bf619af463058acbe8072c6fc8b09c3c2` | `src/ai_sdlc/core/frontend_gate_verification.py`；`tests/unit/test_frontend_gate_verification.py`、`tests/integration/test_cli_program.py`；`FrontendGateVerificationReport` / `build_frontend_gate_execute_decision` fail-closed binding | 126 Batch 2026-04-14-001/003 | anchor/carrier `yes (exit 0)` |
| 105 | `b6c33f8b128fc5051ebf5e0b7a7aea548ab6c2f3` | **deterministic**；`e8fae20bf619af463058acbe8072c6fc8b09c3c2` | `src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`；`tests/unit/test_frontend_gate_verification.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`；post-anchor commit 同时实现 recheck/needs-remediation/fail-closed decision、ProgramService handoff 与 CLI execute-gate 输出 | 126 Batch 2026-04-14-001/003 | anchor/carrier `yes (exit 0)` |
| 121 | `b3d697902b9f3984535e9bc84e1006200f2635f9` | **deterministic**；`fe7a92c57714cb02b094da70854ad63a074f1a33` | `src/ai_sdlc/models/project.py`、`src/ai_sdlc/integrations/ide_adapter.py`；`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`；`AdapterIngressState` 与 activation/ingress 分离的 canonical consumption truth | 122 Batch 2026-04-13-002 runtime implementation | anchor/carrier `yes (exit 0)` |
| 122 | `fe7a92c57714cb02b094da70854ad63a074f1a33` | **deterministic**；`fe7a92c57714cb02b094da70854ad63a074f1a33` | `src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/models/project.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`；adapter unit/integration tests；`_evaluate_canonical_consumption` / verified host ingress | 122 Batch 2026-04-13-002 | anchor/carrier `yes (exit 0)` |
| 123 | `db9dbd901670c1857de7dbd226ea20739b843a64` | **deterministic**；`db9dbd901670c1857de7dbd226ea20739b843a64` | `src/ai_sdlc/core/managed_delivery_apply.py`、`src/ai_sdlc/models/frontend_managed_delivery.py`；`tests/unit/test_managed_delivery_apply.py`、`tests/integration/test_cli_program.py`；契约限定的 narrow apply executor 与 recorded-only recovery boundary | 123 Batch 2026-04-13-002 | anchor/carrier `yes (exit 0)` |
| 124 | `93728e4b5305b4588a4308d18bf31a2a434b8afe` | **deterministic**；`93728e4b5305b4588a4308d18bf31a2a434b8afe` | `src/ai_sdlc/core/managed_delivery_apply.py`、`src/ai_sdlc/core/program_service.py`；`tests/unit/test_managed_delivery_apply.py`、`tests/unit/test_program_service.py`；managed-target dependency install / artifact generation materialization | 124 Batch 2026-04-14-001 | anchor/carrier `yes (exit 0)` |
| 125 | `0605f913de80fe3b508bb263bf34bc47d604d2bc` | **deterministic**；`0605f913de80fe3b508bb263bf34bc47d604d2bc`、`169ca9cfd780e2253794354f1261b40916bbecbd` | `src/ai_sdlc/core/frontend_browser_gate_runtime.py`、`src/ai_sdlc/models/frontend_browser_gate.py`；`tests/unit/test_frontend_browser_gate_runtime.py`、`tests/integration/test_cli_program.py`；probe artifact/session + real Playwright runner | 125 Batch 2026-04-14-001 + post-batch real-runner carrier | anchor/carriers `yes (exit 0)` |
| 126 | `e8fae20bf619af463058acbe8072c6fc8b09c3c2` | **deterministic**；`e8fae20bf619af463058acbe8072c6fc8b09c3c2` | `src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/program_service.py`；`tests/unit/test_frontend_gate_verification.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`；recheck/remediation closure 与 execute handoff | 126 Batch 2026-04-14-001/003 | anchor/carrier `yes (exit 0)` |

### 4. 对抗复核

- 历史 `blocker-execution-map.yaml` 只证明当时计划和 close sweep，不证明当前真值算法要求的实现归因。
- `098` 规格明确要求五类状态、attachment-first、冲突/不足降级和 sidecar no-touch 边界；在 `src/` 检索这些 canonical 名称与状态，仅发现 registry 的 posture mode 声明，没有 detector runtime。
- `099` FR-099-020 要求在输出 bundle 前消费并校验 posture mode；当前 `build_frontend_delivery_registry_handoff` 只加载 solution snapshot，静态返回 `supported_posture_modes`，因此不是完整 resolver carrier。
- `101` FR-101-012/013 要求反向依赖 whole-plan rollback 与保留失败记录的同 action-id retry；后续 `123` FR-123-008/011 明确只记录 refs 并排除自动 rollback/retry/cleanup，当前 runtime 也输出 `rollback/retry/cleanup refs recorded only`。
- `100` 虽已有 action/receipt/ledger 字段，但其 posture/registry 输入和 FR-100-019 continuity 仍受上述缺口影响；`095` 作为母规格继承这些不完整子合同。
- 第一轮独立评审据此判定原 14/16 结论不成立；整改后结论为 11/16 deterministic、1/16 缺失、4/16 部分。
- 同轮评审要求恢复被越界改动的 P3 状态/前置条件，并补齐 formal anchor、完整 SHA、精确 source/test、execution batch 与祖先证明；两项均已整改。
- 第二轮独立评审确认 11/16 分类、P3 恢复、ROI/授权边界和 diff scope 均正确；另指出 WI102 漏列 real Playwright carrier、WI124 semantic carrier 误含 workspace、handoff 漏列两项状态文件，已做纯记录修正。
- PR Codex review 质疑 WI105 的 post-anchor carrier 未覆盖 CLI。`git show e8fae20bf619af463058acbe8072c6fc8b09c3c2 -- src/ai_sdlc/cli/program_cmd.py tests/integration/test_cli_program.py` 证明该提交同时新增 execute-gate state/next-command CLI 输出及对应 integration regression；census 已补齐精确路径，11/16 结论不降级。
- PR 首轮跨平台 CI 的唯一失败是 source inventory baseline 仍断言 `1154/1154/0/1` 与 close layer `219/218`；WI221 注册后的真实值为 `1159/1159/0/2` 与 `220/218`。用户限权批准后只更新同一测试函数的两条期望，不改生产行为或弱化断言；目标测试由 RED 转为 GREEN。
- 结论：provenance-only 方案未通过 admission gate；多能力补缺粗估 8–13 人日，超出 WI221 边界。

### 5. 代码审查结论（Mandatory）

- 宪章/规格对齐：通过；保持真实 blocked，不把 formal 叙事改写为执行事实。
- 代码质量：本批未修改 runtime；test diff 仅为用户限权批准的 manifest inventory/close layer 两条固定期望更新，不涉及其他测试或断言弱化。
- 测试质量：基线 truth-check 40 项通过；constraints、program validate、plan-check、truth sync/audit 均已 fresh 回放。
- 独立评审 Round 1：`changes requested`；原 14/16 分类、证据粒度与 P3 越界改动已按源码事实整改。
- 独立评审 Round 2：`changes requested`；核心决策已通过，1 个 Important 与 2 个 Minor 证据/continuity 精度问题已做纯记录修正。按两轮上限不再启动第三轮本地子评审，最终 exact head 交由 PR 强制 Codex review。
- 结论：`needs_user`。当前不得进入历史归因回填或 runtime 实现。

### 6. 任务/计划同步状态（Mandatory）

- `tasks.md`：T11-T14 已完成；未授权的 runtime/history rewrite 项保持未勾选。
- `plan.md`：已同步 11/16 No-Go 结果；`related_plan=docs/FRAMEWORK_ROADMAP.zh-CN.md` 已对账。
- branch disposition：`merge-pending`；worktree disposition：`retained(pending formal review)`。

### 7. 自动决策记录

- AD-221-001：未采用“给 16 个 log 批量补路径”的最小代码量方案，因为它会把 `098` 的真实实现缺口伪造成 provenance 缺口。
- AD-221-002：未扩大为 detector-only 实现；源码复核证明缺口还覆盖 `099/100/101`，单补 `098` 不能形成 16/16。
- AD-221-003：不在 WI221 内追补多能力 runtime；8–13 人日投入、0.6–0.9 ROI 与跨子系统范围已经触发重新定界和用户授权门。

### 8. 批次结论与归档后动作

- 当前决策：`needs_user`。
- 已完成 git 提交：是（由本批 formal commit 统一承载）。
- 提交哈希：`HEAD`（以 amend 后 exact SHA 重跑 truth-check）。
- 下一步：完成第二轮 formal review；通过后提交 formal PR。不得启动 runtime implementation。

### Batch 2026-08-30-002 | post-merge remote-truth closeout

- **验证画像**：`truth-only`
- **改动范围**：`docs/FRAMEWORK_ROADMAP.zh-CN.md`、`specs/221-release-target-provenance-recovery/spec.md`、`specs/221-release-target-provenance-recovery/plan.md`、`specs/221-release-target-provenance-recovery/tasks.md`、`specs/221-release-target-provenance-recovery/task-execution-log.md`、`program-manifest.yaml`、`.ai-sdlc/state/codex-handoff.md`、`.ai-sdlc/state/resume-pack.yaml`、`.ai-sdlc/work-items/221-release-target-provenance-recovery/codex-handoff.md`
- **真实执行路径说明**：`docs/FRAMEWORK_ROADMAP.zh-CN.md` 是 WI221 建立后由 PR #187 实际修改并合入的非 formal-control 路径，用于归档 P2 已完成和 P3 独立排队的审计结果；该证据只证明 WI221 admission audit 已执行，不表示 095/098 runtime 已实现。
- **本批 records-only 实际改动**：WI221 spec/plan/tasks/log、Program Truth snapshot 与 continuity handoff；不新增 `development-summary.md`，不改 `src/`、tests、历史 work-item log、classifier、P3 或 16 个 blocker，也不改变已批准的 inventory/close layer 基线 `1159/1159/0/2`、`220/218`。
- **统一验证命令**：
  - `uv run ai-sdlc workitem truth-check --wi specs/221-release-target-provenance-recovery --rev HEAD --json`
  - `uv run pytest tests/integration/test_cli_workitem_truth_check.py -q`
  - `uv run pytest tests/integration/test_repo_program_manifest.py -q`
  - `uv run ai-sdlc verify constraints`
  - `uv run ai-sdlc program validate`
  - `uv run ai-sdlc workitem plan-check --wi specs/221-release-target-provenance-recovery`
  - `uv run ai-sdlc program truth sync --dry-run`
  - `uv run ai-sdlc program truth sync --execute --yes`
  - `uv run ai-sdlc program truth audit`
  - clean clone 中执行 `git fetch origin refs/heads/archive/221-release-target-provenance-recovery-pr187:refs/remotes/origin/archive/221-release-target-provenance-recovery-pr187`
  - `git rev-parse refs/remotes/origin/archive/221-release-target-provenance-recovery-pr187`（必须等于 `66bb40994ab75131a64eca57484ec841bf83016f`）
  - clean clone 中执行 `git branch archive/221-release-target-provenance-recovery-pr187 refs/remotes/origin/archive/221-release-target-provenance-recovery-pr187`
  - `uv run ai-sdlc workitem close-check --wi specs/221-release-target-provenance-recovery --json`
  - `git diff --check`
- **代码审查**：PR #187 reviewed head=`66bb40994ab75131a64eca57484ec841bf83016f`；Codex 返回无重大问题；13 项 required/aggregate checks 全部通过；merge commit=`6e21daaa028e477092696c9b70cc1b85f4580035`。
- **任务/计划同步状态**：T11-T15 已完成；五项 runtime/history/classifier/release 内容改为明确的“未授权且未执行”No-Go 清单，不再使用会被 close-check 当成未完成任务的 checkbox。spec/plan 保持 11/16 与 `needs_user`，没有把 release target 写成 ready。
- **主线后验事实**：隔离远端副本的 exact `main@6e21daaa` 与 `git ls-remote origin refs/heads/main` 一致。closeout 前 truth-check 诚实返回 `formal_freeze_only`、`execution_started=false`、`contained_in_main=true`，原因是 latest batch 未以结构化路径记录已合入的 WI221 路线图执行载体；close-check 同时报出任务表达、验证画像、统一验证与 git lifecycle 字段缺口。本批只补真实 receipt，不修改 truth-check 规则。
- **Program Truth**：closeout sync/audit 保持 snapshot fresh、source inventory `1159/1159` mapped、0 unmapped、missing 2、close `218/220`；两个 release target 继续由原 16 个历史 truth refs honest-blocked。
- **ROI 裁决**：该 closeout 只消除归档歧义，不追求文案或细节优化。11/16 不足以解除发布门；8–13 人日真实能力补缺仍需单独定界和用户批准。
- **已完成 git 提交**：是（PR #187 implementation/audit source 与评审整改已提交；本 closeout receipt envelope 不自引用自身）
- **提交哈希**：reviewed head=`66bb40994ab75131a64eca57484ec841bf83016f`；main merge=`6e21daaa028e477092696c9b70cc1b85f4580035`
- 关联 branch/worktree disposition 计划：`archived(PR #187 squash carrier retained locally)`
- 当前批次 branch disposition 状态：`archived(PR #187 squash carrier retained locally)`
- 当前批次 worktree disposition 状态：`removed`
- **生效边界**：上述最终 disposition 与 `mainline_merged` 只在本 records-only closeout PR 合入远端 `main` 后成立；用户排除的本地材料/产品站分支和 worktree 不属于本批范围。
