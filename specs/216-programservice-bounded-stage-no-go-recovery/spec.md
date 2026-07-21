# 规范：ProgramService 有界阶段减重 NO-GO 恢复

**Work Item**：`216-programservice-bounded-stage-no-go-recovery`
**状态**：records-only recovery in progress
**父项**：WI-196、WI-213；行为基线来自 WI-214 closure receipt 后的 fresh main

## 1. 目标

把 T66 首次实现尝试及其隔离 spike 的确定性失败结果写回主线真值，防止失败候选被误当作“已减重”或在
后续会话中继续投入。本项只交付可审计的 NO-GO receipt、父项状态修正、program truth、continuity、
两条契约冻结的非合入远端 archive ref，以及 manifest exact 测试的两处机械计数；不合入候选产品、测试逻辑或 proof，
不关闭 GAP-03、WI-196、RC-08，也不发布版本。

## 2. 问题与结论

WI-213 曾为九个 bounded frontend stage 冻结 terminal≤720、净删≥2,918 的正式合同。实现探索证明，
当前两条路线都不能同时满足“补齐阶段抽取缺口”和“框架自身真实减重”：

1. **C2-safe 路线不是减重**：完整产品账本为 `558 LOC / 64 branch`，而对应 legacy 为
   `495 LOC / 63 branch`；产品源码净增 35 LOC，proof 另净增 285 LOC。该路线还引入
   `Protocol/Generic/TypeVar`、15-callable binding bundle 和 manifest object type erasure，最多只能被描述为
   maintainability/type-safety 重构，不能按当前任务宣称减重。
2. **无 DSL 九阶段路线在第二阶段确定失败**：`cross_spec + guarded_registry` 的完整 target 已达到
   `1209 LOC / 164 branch`，高于两阶段 legacy 的 `842/92`，并超过 branch≤90 硬门 74。继续第三阶段
   无法改变已发生的逐阶段 LOC/branch 反向增长。

因此，T66 本次实现尝试状态为 `cancelled_no_go`，而不是 `completed_reduction`。失败的是当前实现路线，
不是业务功能：fresh main 的 legacy 实现保持原样，现有功能与测试不因本项发生变化。

## 3. 持久证据身份

| 证据 | Commit / tree | 关键 blob 或结论 |
|---|---|---|
| 行为基线 | `7922956d3e248a93c3190240259850ab3498ec9f` / `cc3c6b7f7e63dd040034938ff6bb6827f067e41c` | `origin/main`，WI-214 closure receipt 后 fresh main |
| C2-safe records | `70f19275150831ceea89a6c1e006c056ee98c412` / `2fdd9aaa5fde71711f8ec706338f9bdcbfd860e4` | remote archive=`refs/heads/codex/archive/215-programservice-bounded-stage-c2-safe`；engine=`977cad2c25da95b0c2329ca97b9a3b071e70630b`；service=`23a4968b63651f8fbfebc3174bf737dcce40984e` |
| 隔离 spike 产品 | `6c945b40c8b488728f718287dc6458f15db50d96` / `6341bcb20526be9fdfcd1c273fc15f33dac7e5f4` | engine=`4ab00c369a0414b76f6dda4e49a1c9e2b4d97a79`；service=`ddc417c8203b6bce8458587a98258e233f2d79d0` |
| 隔离 spike records | `60dcc4f65f2a332261b765bfe5fff9979397ddc7` / `44420f6d86b55f8995c3a4ffe9e0e3ba7ce7eb00` | remote archive=`refs/heads/codex/archive/215-nine-stage-no-dsl-no-go`；包含产品 ancestor；LEAN/SAFETY 对产品及 records-only 身份均为 `STOP_SPIKE_NO_GO/findings=0` |

C2-safe 与 spike 分支只作审计证据，状态为 `archived_not_merged`；本项不得 cherry-pick、merge 或以
其他方式把其产品、测试、proof 带入交付分支。合并前必须把上述 exact SHA 推送到表中两个远端 archive
branch，并用 `git ls-remote --heads origin <ref>` 验证；archive ref 禁止 force-push、删除、创建候选 PR
或改作发布分支，后续证据只能使用新 ref。这是合同约束，不虚构远端分支保护或技术只读能力；远端可解析
前只能称为“本地已验”，不得称为持久或可复算。

## 4. 允许范围

- 新增 WI216 的 `spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`development-summary.md`。
- 在 WI196 与 WI213 五件套中追加 superseding NO-GO 状态；历史 receipt 不删除、不改写。
- 更新 `program-manifest.yaml` 的 WI216 注册与机械生成的 `truth_snapshot`。
- 更新 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq: 217`，把 WI215 明确定义为未合入
  实验编号，避免 scaffold 重用。
- 更新 root/scoped `codex-handoff.md`，两份必须 byte-identical。
- 只把 `tests/integration/test_repo_program_manifest.py` 的 inventory `1126→1131` 与 close `214→215`
  两处期望机械更新；测试逻辑、fixture 和其他测试文件不变。
- 执行只读验证、本地双 Agent 对抗评审、PR required checks、merge 与 detached fresh-main 验收。

## 5. 禁止范围

- 不修改 `src/**`、测试逻辑/fixture、workflow、依赖、版本、release、adapter 或共享 CLI；`tests/**`
  唯一例外是 manifest exact 的 `1126→1131`、`214→215` 两个计数标量。
- 不合入 C2-safe / spike 的产品、测试、proof 或 selector。
- 不把净增或职责移动描述为减重，不用将来九阶段复用摊销当前超限。
- 不把 T66、GAP-03、WI196、RC-08、路线发布或版本发布标记完成。
- 不为满足旧预算压缩可读性、引入反射/DSL/type erasure、删除兼容行为或跳过结构硬门。

## 6. 状态转换

| 对象 | 本项前 | 本项后 |
|---|---|---|
| WI-215 / T66 本次实现尝试 | isolated experiment | `cancelled_no_go`；`next_work_item_seq=217` |
| C2-safe / no-DSL spike | local reviewed evidence | 远端 exact archive 后 `archived_not_merged` |
| legacy ProgramService 行为 | mainline active | unchanged |
| GAP-03 / WI196 / RC-08 / release | open | open |
| 后续 T66 | 旧路线待实施 | 禁止复用；只有新的 formal WI 证明自然实现净删、复杂度下降和完整兼容预算后才能重启 |

## 7. 功能需求

- **FR-001**：NO-GO receipt 必须绑定完整 commit/tree/blob、契约冻结的非合入 remote archive ref，以及可复算的
  before/after LOC/branch 与稳定净增值；不记录依赖 diff 工具分段方式的不稳定 `+N/-M` 口径。
- **FR-002**：交付 diff 对 `src/**`、测试逻辑/fixture、workflow、依赖、版本和 release 必须为零；
  `tests/**` 只允许 manifest exact 两个计数标量。
- **FR-003**：父项必须明确 T66 本次实现 `cancelled_no_go`，同时保持 GAP-03/WI196/RC-08/release open。
- **FR-004**：C2-safe 与 spike 必须被标为 `archived_not_merged`，不得形成可发布产品声明。
- **FR-005**：新的实现候选必须另立 formal WI，并以完整自然产品账本证明净源代码删除和分支复杂度下降；
  不得继承 WI215 的 GO、hash、预算或 reviewer receipt。
- **FR-006**：Pascal/LEAN 与 Confucius/SAFETY 必须对同一 committed+clean formal-nine 和最终 HEAD/tree
  均给出 findings=0 的一致通过结论；任一身份变化使双方 verdict 同时失效。
- **FR-007**：root/scoped handoff 必须 byte-identical，program truth 必须 ready/fresh、inventory exact、
  missing/unmapped=0。
- **FR-008**：`next_work_item_seq` 必须为217；任何 merge/revert 故障都必须保持 T66 fail-closed，不得恢复
  旧“可进入实现”状态。

## 8. 成功标准

- **SC-001**：最终分支仅包含本规范允许的 records/truth/continuity/project-state 与 manifest exact 两处
  测试计数；产品和测试逻辑 diff 为零。
- **SC-002**：C2 `558/64 vs 495/63`、产品净增35、proof净增285 与 spike
  `1209/164 vs 842/92` 均在记录中存在，且两个 remote archive ref 可解析到 exact SHA。
- **SC-003**：T66 本次实现为 `cancelled_no_go`；GAP-03/WI196/RC-08/release 仍 open，无虚假关闭。
- **SC-004**：constraints、program validate/truth、manifest exact、scope、handoff parity 与 clean tree 全绿。
- **SC-005**：同一身份 LEAN/SAFETY PASS0、required checks 全绿、PR merge 与 detached fresh-main 验收完成。
- **SC-006**：任何产品文件或非白名单测试变更进入 diff、archive ref 不可解析、任一 reviewer 不通过、
  truth 不新鲜或父项状态矛盾时，本项不得合入。

## 9. 冻结决策

1. 用户不评审本项原则、计划和任务；Pascal/LEAN 与 Confucius/SAFETY 代行对抗内容评审。
2. “隔离”是为了让失败实验不污染主线和功能基线；隔离授权不等于允许合入失败候选。
3. 本项采用 records-only recovery；不把 C2 改名为 maintainability/type-safety 项后合入，因为这超出
   “补缺口并减重”的当前授权。
4. 结构硬门失败后省略耗时 full/A-B 合法：这些行为验证不能修复已经确定的 LOC/branch 反向增长；
   遗留实现未变，因此本项只验证 records-only scope 与治理真值。
5. 本项关闭后用户原始“补缺口并减重”目标仍未完成；后续只能从新 formal 候选继续，不能把本
   records receipt 当作产品完成或 release 授权。
