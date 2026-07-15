---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
---
# 任务分解：Program Finalization Command Family Reduction Contract

**编号**：`203-finalization-command-family-reduction-contract`
**日期**：2026-07-14
**来源**：`spec.md` + `plan.md`
**当前授权**：只允许 Batch 0；Batch 1～5 必须由后续独立 candidate/deletion WI 执行

## 1. 执行规则

- 每批开始前预读 PRD/宪章/本 WI formal/当前 mainline receipt；
- 所有产品变更先红后绿，先 T61A 再编码；
- 每个 candidate commit 更新 RC-05 ledger；每个保护变更更新 RC-06 ledger；
- 任何 target formal 内容变化使双 PASS 失效；
- candidate、stable release、legacy deletion 均是独立 mainline 交付节点；
- 任务完成证据追加到 `task-execution-log.md`，不得预先勾选未来任务。

## 2. 依赖图

```text
T01 → T02 → T03 → T04
                  ↓
T11 → T12 → T13 → T14
                  ↓
T21 → T22 → T23 → T24
                  ↓
T31 → T32 → T33 → T34
                  ↓
T41 → T42 → T43
                  ↓
T51 → T52 → T53
```

## Batch 0：Formal admission（当前 WI）

### T01 重算候选基线与边界

- **状态**：已完成，待 formal review 复核
- **文件**：`candidate-baseline.json`、`task-execution-log.md`
- **验收**：
  1. baseline revision 固定为 `d19c8b7df66ca43e4fa55a99a6d05fa2d1219586`；
  2. 只含 9 handlers，thread-archive/project-cleanup 排除；
  3. 2,020/207/216/1,804/432 与测试聚类可复算；similarity 按 measurement method 明确排除，
     不作为准入或删除预测；
  4. renderer 仅保护、不迁移、不计成果。
- **验证**：AST/LOC/source reference + targeted baseline tests。
- **追踪**：RC-01、RC-02、GAP-04、WP-07。

### T02 冻结完整 Reduction Contract

- **状态**：已完成，待 formal review 复核
- **文件**：`spec.md`、`plan.md`、`tasks.md`、`candidate-baseline.json`
- **依赖**：T01
- **验收**：
  1. CC-01～CC-08、RC-01～RC-10 无占位/开放决策；
  2. final≤519、net delete≥1,501、shadow≤303、protection claim≤353；
  3. T61A/B、stable release、独立 deletion、两阶段 rollback 明确；
  4. external report path 和 outer hook 行为已冻结；
  5. sponsor 分配为 candidate≤180、WI-202≤170、reserve=3。
- **验证**：文档对账、JSON parse、数字公式复算。
- **追踪**：LP-01～LP-12、FR-04/07/08/10、SC-01～SC-08。

### T03 两个对抗 Agent 同 hash 评审

- **状态**：待执行
- **依赖**：T02
- **可并行**：两个 reviewer 可并行，但必须独立只读
- **维度 A**：兼容/安全——CC、路径、副作用、失败/回退、release truth。
- **维度 B**：精简/效率——重复证据、LOC 数学、抽象成本、RC-04～RC-09。
- **验收**：
  1. 两者独立复算同一 target hash；
  2. findings 全部处置；
  3. 内容变化后旧 verdict 作废并重审；
  4. 最终两者对同一 hash 明确 `PASS`。
- **验证**：execution log 的 agent/dimension/hash/time/findings/disposition/verdict。
- **追踪**：FR-10、SC-01。

### T04 Formal mainline receipt

- **状态**：待执行
- **依赖**：T03
- **验收**：
  1. formal 白名单、constraints、truth audit、diff check 通过；
  2. 单一 formal commit 推送、PR、`@codex review`、heartbeat、required checks；
  3. PR 合入 main 并记录 merge commit；
  4. 无 `src/`、`tests/`、runtime rule、release 变更；
  5. WI-202 只在此后引用 sponsor；登记 `active` owner/handoff/deadline，30 日未进入 T61A
     自动 `revoked`。
- **回退**：revert formal PR，所有 claim 失效。

## Batch 1：T61A 旧行为与保护预算（后续 candidate WI）

### T11 固定运行环境与 surface manifest

- **状态**：未开始
- **依赖**：T04
- **验收**：Python/Typer/Rich/PyYAML、OS/locale/encoding/width/color、update-check 环境、
  33 commands 和 9 help/options/docstrings 全部落盘；`--manifest` default/relative/nested/
  absolute/`../` 解析矩阵与 outer-hook 七场景全部冻结。
- **追踪**：CC-01、CC-02、CC-07。

### T12 捕获行为、artifact 和副作用矩阵

- **状态**：未开始
- **依赖**：T11
- **验收**：9 commands × truth/mode matrix；exit/stdout/stderr/call order/tree/mode/raw bytes/
  `.git`/external sentinel/subprocess/network；完整 9-stage chain；在 step/artifact/renderer/report
  边界注入 KeyboardInterrupt/SystemExit/进程终止并验证残留+重跑；执行 Unicode/locale 路径矩阵。
- **追踪**：CC-02、CC-03、CC-05、CC-06。

### T13 冻结 renderer 与 normalizer

- **状态**：未开始
- **依赖**：T12
- **验收**：
  1. 9 renderer source segment hash；
  2. width 40/80/120、color off、逐字符输出；
  3. dry-run/load-validation-failure/execute-no-yes/executor-writer-failure=0次；writer-success=1次
     （含 incomplete）；report-failure=1次，顺序=`executor→writer→renderer→report`；
  4. renderer normalizer 为空；全局 normalizer 只含显式 allowlist。

### T14 捕获 runtime 并结算 RC-06

- **状态**：未开始
- **依赖**：T13
- **验收**：固定采样命令、warmup、p50/p95；T61A/B 预测新增≤180；超限则缩小或 No-Go。

## Batch 2：TDD 与 staged handler migration（后续 candidate WI）

### T21 写 characterization/differential 红灯

- **状态**：未开始
- **依赖**：T14
- **验收**：legacy 通过、未实现 candidate seam 失败；不复制 9 套 snapshots；测试场景不减少。

### T22 实现单一私有 runner module

- **状态**：未开始
- **依赖**：T21
- **文件**：`src/ai_sdlc/cli/_program_finalization_runner.py`
- **验收**：module≤230、initial module+glue≤233；helper≤50；公共抽象=0；无 command-name 分支/
  optional writer/reflection；首个 stage 变绿。
- **追踪**：RC-03、RC-05、RC-07、RC-09。

### T23 建立 9 个 candidate route 并保留 legacy

- **状态**：未开始
- **依赖**：T22
- **验收**：
  1. 9 个 route adapters+internal selector≤70，import/glue≤3；三者连同 module 聚合≤303；
  2. 每 commit ledger peak≤303，完整 legacy body/route 始终保留；
  3. internal selector 先指 legacy，逐 stage 验证后切 candidate；无 public flag；
  4. renderer/ProgramService/DTO hash 不变；
  5. 每步 targeted green，全部后 full green；Phase 3 不删除 legacy body。

### T24 证明 candidate route 与删除后终态预测

- **状态**：未开始
- **依赖**：T23
- **验收**：candidate+route 新增≤303；独立 deletion 后 family≤519、net delete≥1,501、
  mirror drop≥70%、migrated responsibility≤83、full-responsibility handlers=0；不达标立即 No-Go。

## Batch 3：T61B 与 candidate PR（后续 candidate WI）

### T31 固定 candidate hash 并运行隔离 differential

- **状态**：未开始
- **依赖**：T24
- **验收**：两份 byte-identical clone；全部 matrix、9-stage chain、renderer hash、raw bytes、
  side-effect tree 零未批准差异；candidate p95 退化≤10%；renderer 调用次数按 T13 的成功/
  precondition/executor-writer/report-failure 矩阵逐项一致。

### T32 删除前 route rollback rehearsal

- **状态**：未开始
- **依赖**：T31
- **验收**：无 public flag；切回 legacy 后 9 transcript/artifact/side-effect tree 恢复。

### T33 L3 本地双 Agent 与 Codex review

- **状态**：未开始
- **依赖**：T32
- **验收**：两个维度对 candidate commit/tree hash PASS；Codex 无 actionable finding；变更后重审。

### T34 Candidate PR mainline merge

- **状态**：未开始
- **依赖**：T33
- **验收**：targeted/full/ruff/constraints/truth/platform checks green；heartbeat 到 merge；记录 merge commit。

## Batch 4：Stable release（后续 release WI/批次）

### T41 发布 candidate stable `Vn`

- **状态**：未开始
- **依赖**：T34
- **验收**：版本/README/release note/workflow/token 同步；wheel/sdist 构建；GitHub candidate
  stable `Vn` 发布；candidate route 生效、完整 legacy 保留。

### T42 安装产物、平台、离线与 sibling smoke

- **状态**：未开始
- **依赖**：T41
- **验收**：Windows/macOS/Linux、PowerShell、offline、bare global `ai-sdlc`；每 OS 两个 clean
  root 完整 9-stage chain（共54 stage executions）；至少2个代表性 sibling help/dry-run/隔离
  execute chain；3次独立 release-smoke job；不得用 repo source 冒充发布验证。

### T43 稳定期准入 deletion

- **状态**：未开始
- **依赖**：T42
- **验收**：零未批准差异/新 violation、truth fresh、p95退化≤10%、T42全部样本通过、release
  receipt 完整，才允许 deletion PR；用上述样本阈值替代主观日历等待。

## Batch 5：Legacy deletion 与关闭（独立 PR）

### T51 删除失活 legacy body/route

- **状态**：未开始
- **依赖**：T43
- **验收**：独立 deletion PR 删除 9 个 legacy bodies/legacy route；renderer hash 不变；最终
  family≤519、净删≥1,501、full-responsibility handlers=0；发布 deletion stable `Vn+1` 并重算
  LOC/complexity。

### T52 删除后验证与真实 rollback rehearsal

- **状态**：未开始
- **依赖**：T51
- **验收**：targeted/full/platform/offline/installed/sibling 全绿；从已安装 `Vn+1` 回滚到 `Vn`，
  只宣称恢复 legacy code/route 可用性；再在精确 `Vn` tag 上应用已记录的 selector-only rollback
  commit `Rlegacy`，构建带 commit+SHA256 唯一标识的非发布安装 artifact，实际以 legacy route
  验证 9 transcript/artifact/side-effect tree；最后重装 `Vn+1` 并恢复 deletion 状态。

### T53 关闭 candidate 与更新路线图

- **状态**：未开始
- **依赖**：T52
- **验收**：
  1. RC-10 evidence 完整；
  2. 状态=`completed_reduction`；
  3. 只结算实际净删除和实际 RC-06 claim；
  4. renderer/report-path/RC-08 债务仍为 open；
  5. sponsor 必须进入 `settled`；按 actual deletion/protection LOC 结算并永久覆盖既有 claim、
     停止 freshness timer，超额 claim 已替代/缩减/revert；`revoked` 只属于取消/No-Go 路径，
     不得与 `completed_reduction` 同时出现；
  6. handoff 指向下一个独立候选。

## 3. 追踪矩阵

| 合同 | 任务 |
|---|---|
| RC-01～RC-02 | T01、T11～T14 |
| RC-03～RC-05 | T02、T22～T24、T51 |
| RC-06 | T02、T14、T21、T31、T53 |
| RC-07～RC-09 | T02、T22～T24、T31～T34 |
| RC-10 | T31～T34、T41～T43、T51～T53 |
| CC-01～CC-03 | T11～T13、T21、T31、T52 |
| CC-04 | T02、T23（不影响证明） |
| CC-05～CC-06 | T12～T13、T21、T31～T32、T52 |
| CC-07～CC-08 | T11、T34、T41～T43、T52 |
| LP-01～LP-12 | T02、T22～T24、T41～T53 |
| FR-04/07/08/10 | T01～T04、T11～T53 |
| SC-01～SC-08 | T03～T04、T24、T31～T53 |
