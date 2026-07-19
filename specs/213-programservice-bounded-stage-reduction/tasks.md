---
related_plan: "specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md"
related_doc:
  - "specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md"
  - "specs/212-reduction-candidate-selection/development-summary.md"
---
# 任务分解：ProgramService 九阶段精益减重正式合同

**编号**：`213-programservice-bounded-stage-reduction`
**交付类型**：formal-only；本 WI 禁止产品 execute
**完成定义**：formal mainline receipt + detached fresh-main；不等于 T66 产品完成

## Batch 1：current-main 准入基线

### T11 初始化隔离 formal work item

- **状态**：completed
- **范围**：`main@e184c8e2`、独立 worktree/branch、canonical 四件套、manifest/project sequence。
- **验收**：分支=`feature/213-programservice-bounded-stage-reduction-docs`；root dirty changes 未带入；
  `workitem init` 的非范围 Cursor adapter refresh 已恢复到 base bytes。
- **回退**：移除 formal branch/worktree；不影响产品。

### T12 复算目标、调用与测试基线

- **状态**：completed
- **依赖**：T11
- **范围**：九 stage × 五 family；physical/executable/header/branch、fan-in/out、产品/测试 LOC、runtime。
- **验收**：45=`3638/3305/333/386`；public=`2928/2703/225`；private=`710/602/108`；
  18 private outside-service refs=0；165=`106 unit + 59 integration` 实跑通过。
- **验证**：Python3.11 AST/Call recipe、精确 pytest selector、`wc -l`。

### T13 冻结 CC 与 GAP-09～11 影响分析

- **状态**：completed
- **依赖**：T12
- **验收**：CC-01～03/05～08 direct，CC-04 indirect；inheritance/adapter 不改，source inventory 必须映射；
  任一 blocker/unmapped/unexpected missing source 均 fail-closed 重开对应 GAP。
- **验证**：spec §6 与 parent CC/GAP 对账。

### T14 登记 GAP-15 workitem 只读 adapter side effect

- **状态**：completed
- **依赖**：T11
- **范围**：只记录 current-main A/B、根因边界、恢复动作和独立 T58 顺序，不修改 runtime/source。
- **验收**：`program validate` 前后 SHA=`d5f04acf...0b6a`；`workitem plan-check --json` 后 SHA=
  `02d9656d...e134` 且 adapter `+18/-6`；恢复后相对 base diff=0；parent GAP-15/T58 已登记。
- **后续门禁**：WI213 fresh-main 后先关闭 T58；其 fresh-main 前不得创建 T66 implementation WI/T61A。

## Batch 2：正式 Reduction Contract

### T21 冻结最小源码设计与预算

- **状态**：completed
- **依赖**：T12～T14
- **验收**：一个 private module≤360；candidate facade addition≤72；terminal facade body≤45；
  typed/path binding+glue≤90；product shadow≤522；product+proof≤712；terminal≤720；net delete≥2918；
  ProgramService target responsibility reduction≥3278；
  branch proxy≤90；每函数≤50。
- **停止**：反射、循环 import、stage-name branch、DSL、DTO 搬迁、第二领域、公共开关或预算不可达即 RC-09。

### T22 冻结 T61A/B 与 readiness gate

- **状态**：completed
- **依赖**：T21
- **验收**：T61A 在产品编码前；双临时根、raw evidence、异常/写序/副作用/中断/重试、≥20次 p50/p95；
  Python-surface manifest 分为 public surface/behavior、DTO hook source/behavior（source unreadable 即阻断）、allowlisted
  `builtins.list/dict` factory tag，未知 callable fail-closed 且禁用 identity/address repr；execute/writer
  late-bound `self` dispatch 覆盖 `None`/truthy/falsey request/result 与 `generated_at=None/""/固定值` 的
  clock spy 矩阵，保持 legacy truthiness；
  LEAN/SAFETY 同 proof identity 双 GO 后才可编码；T61B 绑定 candidate commit/tree，零未批准差异。
- **回退**：T61A NO-GO 先固化 commit/tree/raw hash/verdict/closure receipt，保留唯一证据；运行时零改动。

### T23 冻结 candidate、稳定周期、deletion 与 release 顺序

- **状态**：completed
- **依赖**：T22
- **验收**：candidate 先 legacy 后 candidate；candidate merge legacy retained；主线预发布稳定周期无版本；
  wheelhouse `--no-index` 断网安装 wheel/sdist；deletion 独立 PR；删除 merge 后对精确 merge commit actual
  revert + selector rollback/reapply，再回 deletion fresh-main；RC-08 全局终态前不发布。
- **停止**：平台/build/install/offline/sibling/rollback 任一失败不得 deletion/close。

### T24 同步父 WI196 当前路线

- **状态**：completed
- **依赖**：T21～T23
- **范围**：parent `spec.md / plan.md / tasks.md`，必要时 execution/summary 只写当前事实。
- **验收**：记录 WI213 formal active、退役 WI212 预备 691/2947 及早期草案701/2937，冻结720/2918新合同；
  登记 GAP-15/T58 顺序；不宣称 formal merge、T58、T61A、candidate、deletion、GAP-03 或 release 已完成。

## Batch 3：双 Agent 对抗评审

### T31 冻结 formal-six identity

- **状态**：completed
- **依赖**：T24
- **范围**：parent+child 各 `spec.md + plan.md + tasks.md`；父 plan §9 canonical hash。
- **验收**：committed+clean HEAD/tree、六个 file hash 与 combined SHA-256 可复算；审查期间只读。

### T32 LEAN/YAGNI 独立审查

- **状态**：completed
- **依赖**：T31
- **Reviewer**：Pascal
- **检查**：范围是否最窄、是否过度实现/纯移动、预算是否真实、设计是否直接、删除是否闭环。
- **通过**：明确 `PASS` 且 actionable findings=0。

### T33 SAFETY/COMPAT 独立审查

- **状态**：completed
- **依赖**：T31
- **Reviewer**：Confucius
- **检查**：DTO/CLI/artifact/授权/异常/恢复/平台/安装/offline/sibling/rollback/truth/release 边界。
- **通过**：明确 `PASS` 且 actionable findings=0。

### T34 处置 finding 并同 identity 复审

- **状态**：completed
- **依赖**：T32、T33
- **规则**：正确 finding 做最小修正；错误或扩范围建议记录拒绝证据；formal-six 任一变化同时废止两 verdict。
- **完成**：Round 5 HEAD=`e00aea25`、tree=`f17e24ba`、formal-six=`674407cf...cf27` 上双方
  PASS0/findings=0；closure material 改变 formal-six 后，本 receipt 退为 authoring PASS，T44 仍须对最终
  current identity 双审，不得拼接不同 round/identity。

## Batch 4：formal truth、PR 与 fresh-main

### T41 完成 formal-only closure materials

- **状态**：completed
- **依赖**：T34
- **范围**：child execution log/development summary、parent writeback、root/scoped handoff。
- **验收**：summary 只声明正式合同完成；handoff byte-identical；唯一下一步是创建 T58/GAP-15 WI；
  不声明产品、T66、GAP-03、WI196、RC-08 或 release 完成。

### T42 绑定 program truth

- **状态**：completed
- **依赖**：T41
- **步骤**：只在 terminal source identity 上执行一次 truth sync；机械更新 manifest exact inventory/close 两值。
- **验收**：inventory complete、unmapped/missing=0/0、close=N/N、snapshot fresh；测试 diff 仅两值 `+2/-2`，
  不增逻辑/LOC；WI213 depends_on WI196。
- **完成**：最终 source commit=`a638be64`，snapshot=`7038d31f...48e2e`，inventory/close=`1121/1121`/
  `213/213`，unmapped/missing=`0/0`；manifest test 仅 `+2/-2`。

### T43 运行最终本地门禁

- **状态**：completed
- **依赖**：T42
- **验证**：constraints、program validate/truth、manifest exact、165 baseline、diff-check、scope whitelist、
  handoff parity、formal 未决标记/traceability、clean worktree。
- **完成**：constraints/validate/truth、`165 passed`、manifest exact、scope/parity/Cursor/clean 全绿。

### T44 双 review current HEAD、PR 与 merge

- **状态**：completed
- **依赖**：T43
- **验收**：两位本地 reviewer 对 current HEAD/tree/formal-six PASS0；Codex reviewed current head 无 actionable
  finding；required checks 100% success；squash merge。任一文件变化回 T31。
- **完成**：Round 9 HEAD/tree=`94acfdf4`/`9d1c0f69`、formal-six=`283b623b...f099`，Pascal/Confucius
  双 PASS0；PR #158 current-head Codex 的成立 P2 已修正，错误 provenance P2 经本地/GitHub DAG 与双 Agent
  一致证伪；两线程 resolved，13/13 checks success，squash merge=`450d4988`。

### T45 detached fresh-main 验收

- **状态**：completed
- **依赖**：T44
- **验收**：merge tree=reviewed tree；constraints/validate/truth/manifest/scope/parity/clean 全绿；版本仍不变。
- **唯一后续**：创建独立 T58/GAP-15 WI；T58 fresh-main 后才创建 T66 implementation WI，从 T61A 开始。
- **完成**：detached `450d4988` tree=`9d1c0f69` 与 reviewed tree 相同；Python 3.14 targeted=`165 passed`、
  manifest exact=`1 passed`，constraints/validate/truth=`ready/fresh 1121/1121`、scope/parity/Cursor/clean 全绿；
  版本未变。

## 下游强制 handoff（不属于 WI213 完成任务）

| 顺序 | 下游 gate | 必须满足 |
|---:|---|---|
| 1 | T58/GAP-15 | standalone RED/GREEN；五只读+help/invalid bytes stable；init/link 负路径时序；fresh-main |
| 2 | T61A | no product code；Python surface/late-bound baseline + proof budget + dual readiness GO |
| 3 | candidate shadow | default legacy；逐 stage TDD；product≤522 |
| 4 | T61B/candidate PR | zero delta；selector round-trip；legacy retained |
| 5 | pre-release stability | platform/build/clean/offline/sibling；无公开版本 |
| 6 | deletion PR | terminal≤720/net≥2918；merge 后 exact-merge actual rollback |
| 7 | T66 close | deletion fresh-main 后才 completed_reduction |
| 8 | release | 仅 WI196/RC-08 全部完成后 |

## 追踪矩阵

| 规范 | 任务 |
|---|---|
| FR-001、SC-002 | T11～T14、T43 |
| FR-002、FR-007、SC-002 | T21、T32、T34 |
| FR-003 | T13、T22、T23、T33 |
| FR-004 | T22、T33、T45 |
| FR-005～FR-006 | T23、T32～T34 |
| FR-008、SC-003 | T31～T34、T44 |
| FR-009 | T44～T45 |
| FR-010、SC-005～SC-006 | T23～T24、T41、T45 |
| FR-011、SC-001、SC-004 | T11、T14、T24、T41～T45 |
| FR-012、SC-007、GAP-15 | T14、T24、T41、T45 |
| RC-01～RC-10 | T12～T23、T32～T34 |
| CC-01～CC-08、GAP-09～11 | T13、T22～T23、T33 |
