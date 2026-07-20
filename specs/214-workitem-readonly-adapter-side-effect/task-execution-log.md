# 任务执行日志：Workitem 只读命令 Adapter 副作用隔离

**功能编号**：`214-workitem-readonly-adapter-side-effect`
**创建日期**：2026-07-19
**当前状态**：formal/amendment/implementation 已 merge/fresh-main；lifecycle reconciliation source ready

## 1. 固定归档规则

- 每批开始前预读宪章、WI196、WI213 与 WI214 当前 formal。
- 每批记录 identity、范围、命令、结果、finding disposition、回退和下一步。
- 产品实现必须在 formal fresh-main 后的 dev branch，以测试 RED 开始。
- 任一受审文件变化使 Pascal/Confucius 同轮 verdict 同时失效，不拼接不同身份结论。
- 提交只包含一个逻辑批次；未来 hash 不预写，实际发生后追加。

## 2. Batch 2026-07-19-001：WI214 初始化与非范围 adapter 恢复

### 2.1 基线与命令

- base：`origin/main@d5ad7616f7f39f68365d6d39f8701a86c1f599e7`
- worktree：`.worktrees/214-workitem-readonly-adapter-side-effect`
- branch：`feature/214-workitem-readonly-adapter-side-effect-docs`
- 初始化：`uv run --python 3.11 ai-sdlc workitem init --wi-id 214-workitem-readonly-adapter-side-effect
  --title "Workitem Read-only Adapter Side Effect" --input "独立修复 GAP-15：仅隔离 workitem
  plan-check、guard、close-check、branch-check、truth-check 五个只读命令及其 help/invalid 路径的隐式
  adapter refresh，保持输出、退出码和 clean-tree；完整保留 init/link 在 valid、missing option、dirty、
  no-project、no-checkpoint、hook exception 下的既有写入时序。禁止修改 ProgramService/T66、adapter
  算法、全局 classifier、依赖或版本。" --related-plan
  specs/196-ai-sdlc-lean-code-self-reduction-governance/plan.md --related-doc
  specs/196-ai-sdlc-lean-code-self-reduction-governance/spec.md --related-doc
  specs/213-programservice-bounded-stage-reduction/development-summary.md`

### 2.2 结果

- CLI 创建 canonical 四件套、project sequence `214→215` 与 manifest entry。
- 初始化消费既有写路径并把 Cursor adapter 从 base SHA `d5f04acf...0b6a` 刷新为
  `02d9656d...e134`。该文件不是 WI214 formal scope，已恢复为 base bytes。
- 恢复后 `git diff --exit-code origin/main -- .cursor/rules/ai-sdlc.mdc` 为 0；最终 SHA=
  `d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`。
- root worktree 的用户未提交内容未读取、未复制、未修改。
- 删除注释原因：`.ai-sdlc/state/codex-handoff.md` 的原 `## Local PR Review` 是已归档到 WI213 execution/summary 的上一工作项瞬时状态；切换 WI214 时由本日志与新双评审任务替代，未删除源码注释或历史证据。

### 2.3 边界

- 本批只写 formal/state/manifest；`src/**`、`tests/**`、workflow、provider、依赖、版本均未修改。
- `workitem init` 的 refresh 是既有且受保留的 valid 行为；本 WI 只移除五个 read-only 路径的隐式消费。

## 3. Batch 2026-07-19-002：根因与兼容矩阵冻结

### 3.1 源码事实

- `src/ai_sdlc/cli/main.py` 在 top-level `workitem` 时只把 `run_ide_adapter_if_initialized` 注入 context meta。
- `src/ai_sdlc/cli/workitem_cmd.py::_workitem_before_command` 当前跳过 `None/init`，其余子命令均在
  handler 前执行 hook。
- `workitem_init` 在 root、ID、docs branch 与 clean-tree preflight 后显式执行 hook。
- `workitem_link` 无显式 hook，依赖子应用 callback；handler 内依次执行 option、root、checkpoint、save。

### 3.2 测试库存

- `test_cli_workitem_init.py` 已覆盖 valid、missing title、dirty/wrong branch、duplicate 与部分 adapter 时序；
  其中旧 `non_init` 测试用 `plan-check` 期待 hook 1 次，正是待转为 RED 的错误合同。
- `test_cli_workitem_link.py` 已有 valid、missing option、checkpoint fixture，但 autouse no-op hook 掩盖了调用时序。
- 五个 read-only handler 各有领域 integration tests；WI214 只补分发/bytes/output 证明，不复制业务矩阵。
- 使用 patch 的 Typer 控制流探针确认：五个 read-only 的 help/invalid 会识别子命令并进入当前 callback；
  `link` help/missing 当前消费 hook，`init` help/missing 不消费；未知 subcommand 不消费。

### 3.3 冻结结论

- 最小实现是让一个既有 callback 仅在 `invoked_subcommand == "link"` 时继续；不建立命令名单、
  classifier、registry 或 decorator。
- 15 格只读矩阵的唯一批准差异是 hook `1→0` 及其 receipt/write 消失。
- `init/link` 适用行为全部以 zero-delta 回归保护；`init no-checkpoint` 明确 N/A，不制造伪覆盖。
- 尚未修改产品或测试；必须先完成 formal 双 Agent review 与 mainline/fresh-main。

## 4. 当前评审与执行状态

- T11～T13：completed。
- T14 formal 双 Agent 对抗评审：pending。
- T15 formal PR/fresh-main：pending。
- T21～T33 implementation/closure：pending。
- GAP-15/T58、T66、GAP-03、WI196、RC-08、release：全部未完成。

## 5. 下一步

1. 最小更新 parent WI196 的 T58 状态为 WI214 formal active，并冻结 parent+child formal-six。
2. 提交 clean formal identity；Pascal/Confucius 分别从 LEAN 与 SAFETY 维度独立评审。
3. 对成立 finding 做最小修订，重算 identity并从零复审，直到同 identity 双 PASS0。
4. 仅在 formal PR/Codex/checks/merge/fresh-main 后进入 dev TDD。

## 6. 提交与 disposition

- 已完成 git 提交：是；authoring commit=`d3acfedea507a23bb30d53d84906c11a0c03c41a`。
- branch：`merge-pending`
- worktree：`retained(formal authoring)`

## 7. Batch 2026-07-19-003：formal 对抗评审 Round 1 双 FAIL

### 7.1 受审身份

- HEAD=`1603d4b1eaa345373fac70c5a9dc207d30f7b3cf`
- tree=`2d109ccd74703dfab5315ae702ada1663a626c71`
- parent+child formal-six=`aa24fb807312573246bbafbe5fc5619b0c041dda6613305811b966de08622f63`
- Pascal/LEAN=`FAIL`、actionable findings=1；Confucius/SAFETY=`FAIL`、actionable findings=4。
- 两人独立核对同一 committed+clean identity，审查期间零编辑、零真实 adapter 调用。

### 7.2 Findings 与处置

1. Pascal P2 成立：child 未冻结具体 targeted 命令和测试布局。处置为唯一新增参数化
   `test_cli_workitem_adapter_dispatch.py`，init/link 只改既有测试文件，并在 plan/tasks 写 V1～V6 精确命令。
2. Confucius P1 成立：implementation fresh-main 后没有合法 PR 承载 closure。新增独立 lifecycle
   reconciliation branch/PR、双审/Codex/checks/fresh-main；回退顺序先重开 truth 再 revert implementation。
3. Confucius P1 成立：旧顺序在双审后才同步 truth/handoff。修订为先 terminal truth/handoff/gates，再冻结
   committed+clean identity 双审；任何后续内容变化都重跑 gate/truth 并让双方从零复审。
4. Confucius P1 成立：hook exception 未区分 project-config `PermissionError` 的 warning+continue 与其他
   exception propagation。新增 production `apply_adapter` 先写、`_persist_config` 失败的 partial-write/输出/
   continuation fixture；其他异常保留原类型/消息与前缀写入，不引入事务化。
5. Confucius P2 成立：sentinel 不能替代 parent 要求的 real-hook byte evidence。五个 normal 增加
   `@pytest.mark.real_ide_hook` 的 byte-identical 临时根、guarded SHA/status/stdout/stderr/exit exact 证明。

### 7.3 结论

- 五项全部接受并做最小合同修订；没有扩到 adapter 算法、root callback、handler、ProgramService/T66、
  依赖、workflow 或版本。
- Round 1 两份 verdict 与 identity 全部退役；修订提交后必须由 Pascal/Confucius 对新身份从零复审。

## 8. Batch 2026-07-19-004：formal 对抗评审 Round 2 双 FAIL

### 8.1 受审身份

- HEAD=`144c8c5080a90f8819639204be0ab1b12a4acd1c`
- tree=`37de73e387fcd55fd19df20909eba04c2500ad1b`
- parent+child formal-six=`53d85b2a46b54deb0b05f53789c2517a17d879ec015f0829fee898ab174b246c`
- Pascal/LEAN=`FAIL`、findings=2；Confucius/SAFETY=`FAIL`、findings=1；同 identity、clean、只读。

### 8.2 Findings 与处置

1. Confucius P2 成立：tasks 完成定义与 FR-007 仍残留两阶段措辞，可能让 lifecycle 修订逃逸重审；
   改为 formal/implementation/lifecycle 三阶段均 mainline/fresh-main且同 identity 双 PASS0，并把 T41
   明确为登记 implementation receipt。
2. Pascal P2 成立：15 格已覆盖同一 callback 分支，再跑五个 production/no-op 双项目是重复乘积；
   real-hook 收敛为原始 `plan-check normal` 一组代表性 A/B，其他四个 normal 由 sentinel 覆盖。
3. Pascal P2 成立：在 init/link 各复制 production partial-write fixture 越过分发边界；共享
   `test_cli_hooks.py` 只补一例 partial-write，init/link 只注入 return/raise outcome 验证继续或中断顺序。

### 8.3 结论

- Round 1 的五项 finding 已被双方确认实质闭合；Round 2 三项新增 finding 全部接受并继续减去重复证据。
- 精确 targeted 命令加入 `tests/unit/test_cli_hooks.py`；仍只有一个新增测试文件，不新增测试 DSL/fixture framework。
- Formal-six 已变化，Round 2 verdict 全部退役；提交后必须对新 identity 进行 Round 3 双审。

## 9. Batch 2026-07-19-005：formal Round 3 split verdict

- identity：HEAD=`fb08062a802e8055f6ba87fa87731f49c52b54fb`、tree=
  `a654cd607613d4737ee1917c0ad8a3abd40534f2`、formal-six=
  `c92563fbc12866b57741e10f0ff2125fabb9cf1e9e65384fe36f3350636bee55`；clean、只读。
- Pascal/LEAN=`PASS`、findings=0，确认 15 sentinel + 1 representative real-hook A/B + 1 shared
  partial-write 是最小充分证据，三阶段各有独立职责。
- Confucius/SAFETY=`FAIL`、findings=1：parent plan 仍有一句把 GAP-15 关闭写在 implementation
  fresh-main 后，与 lifecycle closure 合同冲突。Finding 成立，只把该句改为 lifecycle reconciliation
  fresh-main 关闭；不改 child 设计、测试矩阵、源码或路线预算。
- 单行 formal 变化使 Round 3 两份 verdict 同时退役；提交后必须对新 identity 进行 Round 4 双审。

## 10. Batch 2026-07-19-006：formal Round 4 authoring 双 PASS

- identity：HEAD=`3a2b2b6f653a97755eab5d82f2522a1a85a4acc6`、tree=
  `e99e0ef9f0bca54aa55b2b273b67c637d8fae38a`、formal-six=
  `823517573a2522b4496877cb46e4a09b7e3432cfa75ef7d4674b4dec7b199d79`；clean、只读。
- Pascal/LEAN=`PASS`、findings=0；Confucius/SAFETY=`PASS`、findings=0。
- 双方一致确认：link-only 一处谓词；15 sentinel + 1 representative production A/B + 1 shared
  partial-write；init/link outcome；truth-before-review；formal/implementation/lifecycle 三阶段与 truth-first
  rollback 均最小充分且无残余矛盾。
- 本 receipt 证明 authoring contract 已收敛。随后新增 summary、更新 T14/T15、同步 truth/handoff 会改变
  final current identity；Round 4 不得冒充 T15 最终 review，必须在 terminal gates 后再次同身份双 PASS0。

## 11. Batch 2026-07-19-007：closure source 与 truth 预同步

- Closure source commit=`693c5b8e2df658500203e53b6064402d8d5a47d3`，包含 development summary、
  T14 completed/T15 in_progress 与 byte-identical root/scoped handoff；`src/tests` 当时零差异。
- `program truth sync --execute --yes`：state=`ready`、snapshot=
  `096da66288c306bab4218e0823a4283158ba265398048048deeb19827af7b418`、repo revision=`693c5b8e`、
  inventory=`1126/1126`、unmapped/missing=`0/0`、spec/plan/tasks/execution/close=`214/214`。
- Manifest exact 首跑按预期 RED：仍冻结 `1121/1121` 与 close `213/213`；只机械改为 `1126/1126` 和
  `214/214`，不修改 test logic、capability、release registry 或产品断言。
- 本段 receipt 本身会改变 tracked execution source，因此首个 snapshot 只作为预同步证据；提交本段与机械
  test 期望后必须再执行 terminal truth sync，并只以后一 snapshot 进入 final audit/review，避免陈旧自称。

## 12. Batch 2026-07-19-008：formal terminal gates

- Pre-sync receipt 与 manifest exact 机械期望提交=`3510706e`；随后对 clean source 执行 terminal
  `program truth sync --execute --yes`，生成 snapshot=`207390ac6a810121f058ef43ceff0cb4e41eb194c8fcd7a2d75d395fa42d28f7`，
  inventory=`1126/1126`、unmapped/missing=`0/0`、各层=`214/214`，manifest-only 提交=`d655435a`。
- `uv run --python 3.11 pytest tests/integration/test_repo_program_manifest.py -q`：PASS，`1 passed in 103.89s`。
- 既有 formal baseline：`test_cli_workitem_init.py + test_cli_workitem_link.py + test_cli_hooks.py`：PASS，
  `24 passed in 11.57s`；未运行实现期 RED/GREEN。
- `program truth audit`：`ready/fresh`，release-target audit ready，inventory=`1126/1126`、
  unmapped/missing=`0/0`、spec/plan/tasks/execution/close=`214/214`。
- `program validate`：PASS；`verify constraints`：no BLOCKERs；manifest test Ruff：PASS；`git diff --check`：PASS。
- Scope gate：`src/**` 零差异；`tests/**` 仅 manifest exact 两个数值机械 `+2/-2`；root/scoped handoff
  byte-identical；Cursor SHA=`d5f04acf...0b6a` 且相对 `origin/main` diff=0；worktree clean。
- 本 gate receipt 提交后必须再 sync/audit 一次；该次生成的 manifest-only identity 才是 final review target。
  为避免自引用循环，最终 snapshot hash 只进入评审/PR 外部 receipt，不再反写本 tracked execution source。

## 13. Batch 2026-07-19-009：formal final review Round 5 双 FAIL

- Exact reviewed identity：HEAD=`1629723a283bd65a5ab20961f58f33072c99bb0d`、tree=
  `9f07a556a3b1761bc96a6d08fc06fd64da4ffc52`、clean。Pascal/LEAN=`FAIL1`；
  Confucius/SAFETY=`FAIL2`。
- 本轮 prompt 误用“路径+原文”得到 `77c8a19f...f075`，不是 parent plan §9 唯一 canonical combined
  算法。按“ordinal path；逐文件 SHA/path 行；整体 SHA”复算同六文件为
  `c31a3aeaf484dc11450fd5633b8cada4091e8ad560d89bb4766ebe38a278ff7d`。内容身份可核对，但本轮不能登记为
  canonical same-identity PASS；后续双方只使用 canonical 算法。
- 两位 reviewer 的重叠成立 finding：WI213/parent current summary、handoff 与两份 append-only execution log
  把 T66 阻断写弱到 implementation fresh-main，可能绕过 T41/T42。Current summary/handoff 直接改为 lifecycle
  reconciliation fresh-main；历史 log 不改旧句，只追加 superseding correction。
- 除上述两类问题外，双方一致确认 link-only 单谓词、15 sentinel + 1 production A/B + 1 shared
  partial-write、init/link outcomes、三阶段与回退合同最小充分；`src/**` 零差异。
- 本轮两份 verdict 全部退役。修正提交后必须重新 truth/gates，并让双方对新 HEAD/tree 与同一 canonical
  combined hash 从零复审；产品实现仍禁止。

## 14. Batch 2026-07-19-010：PR #160 Codex current-head P2

- PR #160 reviewed commit=`88b57c0a`；Codex 在 `plan.md` 指出一个 P2：V1 包含完整
  `test_cli_workitem_init.py`，其中 `test_workitem_non_init_runs_adapter_before_handler_once` 仍固化
  `plan-check` hook=1/receipt，而 formal 只允许既有 init/link 文件补时序，未授权删除或迁移该旧合同。
- 本地核验测试 426～439 行确认 finding 成立：link-only 产品谓词必使旧断言失败；若不改 formal，GREEN
  只能在“保留必红测试”与“越权改测试”之间二选一。
- 最小修正只在 child plan/tasks 显式授权：删除这一条旧非-init 测试，由唯一新 dispatch 文件的参数化
  `plan-check normal` 格承接反转断言；其他 init/link 变更仍限 hook 时序与两类 outcome。
- 不新增测试文件、fixture/DSL、产品抽象或测试笛卡尔积；15 sentinel、代表性 production A/B、共享
  partial-write 与 targeted 命令不变。Formal-six 变化使 Round 6 双 PASS 同时退役，必须重跑 truth/gates/
  双审并推送新头后回复、解决 thread、重新 `@codex review`。

## 15. Batch 2026-07-19-011：formal V4 baseline-delta amendment

- Implementation 预审确认原 V4 在 formal base `d7f8b163` 已不可满足：锁定 Ruff 0.15.7 执行全库
  `ruff format --check src tests` 得到 273 个 formatter-red 文件；把历史文件全部格式化会违反 WI214 的
  单函数产品边界并制造无关 diff。
- Pascal/LEAN 认为产品与矩阵无过度实现；Confucius/SAFETY 将该矛盾定为成立 P2 formal/gate finding。
- 本 amendment 仅把 V4 修正为“新增/可清洁文件严格 format-check + 两个 touched legacy-red 文件
  formatter hunk baseline-delta + 全库 debt 不增加”。不放宽 Ruff lint、测试、constraints 或 diff-check，
  不修改产品、测试、依赖、workflow、版本、GAP-15/T58/T66 状态。
- Amendment pre-commit gates：`program validate` PASS、`verify constraints` no BLOCKERs、manifest exact
  `1 passed in 105.58s`、全库 formatter diagnostic 仍为 `273 red/133 green`、`src/tests/deps/workflow`
  零差异、root/scoped handoff byte-identical、Cursor base SHA/diff 与 `git diff --check` 全绿。

## 16. Batch 2026-07-19-012：V4 amendment final review Round 1 FAIL

- Exact identity：HEAD=`a91bbba3d4c23e69e69b22cd35573c01ed205dbe`、tree=
  `b7203febeb8cd8ce28a36243dad4dd8dc61738c1`、clean；Pascal/LEAN=`FAIL2`、Confucius/SAFETY=`FAIL1`。
- 双方重叠 P2 成立：V4b 使用动态 `origin/main...HEAD`，fresh-main 会退化为空 diff；只比较 273 个 red
  文件也允许路径一增一减抵消或 legacy-red 文件内部新增债务。
- Pascal P3 成立：summary/handoff 仍把已完成的 terminal truth/gates 写成下一步，续接状态陈旧。
- 最小修正冻结 amendment fresh-main `FORMAT_BASE_SHA`，以 exact PowerShell 程序比较规范化 red path set
  subset，并对两个 legacy 文件的 fixed-base changed ranges 执行 Ruff range check；handoff/summary 在新一轮
  terminal sync 后改为 review-ready。Round 1 两份 verdict 同时退役，产品/测试仍零差异。

## 17. Batch 2026-07-19-013：V4 amendment Round 1 correction terminal gates

- Correction source=`389a4ff8`；truth sync snapshot=`5726fa4b...b3f2`，manifest commit=`766fa8c4`。
- `program truth audit`=`ready/fresh`、inventory=`1126/1126`、missing/unmapped=`0/0`、各层=`214/214`；
  `program validate` PASS、`verify constraints` no BLOCKERs、manifest exact=`1 passed in 102.45s`。
- Ruff 0.15.7 全库诊断仍为 `273 red/133 green`；`src/tests/deps/workflow` 零差异、root/scoped parity、
  Cursor base SHA/diff 与 diff-check 全绿。更新本 receipt/summary/handoff 后再做最终 truth sync；最终 snapshot
  不反写 tracked source，避免自引用 stale 循环。

## 18. Batch 2026-07-19-014：V4 amendment final review Round 2 FAIL

- Exact identity：HEAD=`5cad25819114d81387734aafbdf0cb91ddd202dd`、tree=
  `4625216c042bfbf2c881a31efe1c281749aa3d9c`、clean。Pascal/LEAN=`FAIL2`；
  Confucius/SAFETY=`FAIL4`，旧 verdict 全部退役。
- 双方重叠 P1 成立：Ruff `--range` end exclusive，但脚本用 `start+count-1`，单行 hunk 退化为空区间；
  `count=0` 又跳过纯删除边界。修正为非删除 `endExclusive=start+count`，纯删除覆盖 candidate 边界邻行。
- Confucius 的三项 fail-open finding 成立：native Ruff/git failure 未完整判定、dirty candidate 的 working-tree
  修改不进入 fixed-base...HEAD ranges、PowerShell 默认大小写不敏感可折叠 Linux case-only path。修正程序要求
  strict/error-stop、candidate committed+clean 并冻结 SHA、Ruff 仅接受可解释的 exit 0/1 与计数一致输出、
  git/cleanup 失败即阻断、Ordinal red-path subset。
- Pascal P3 成立：summary/handoff 仍把已完成的 Round 1 terminal truth 写入 next steps。修正为如实记录 original
  formal PR #160 已 merge/fresh-main、amendment Round 1 terminal gates 已完成，下一步只保留本 correction 的
  truth/gates 与新身份双审。
- 本轮只修正 child plan/tasks/summary/log 与双 handoff；不修改 src/tests、依赖、workflow、版本或 lifecycle
  状态。Correction 提交后先实跑 exact PowerShell，再重新 truth/audit/gates 并对全新 clean identity 双审。

## 19. Batch 2026-07-19-015：Round 2 correction pre-sync gates

- Correction source commit=`f828a39ea140547b7a12d4839bc485e72020b2ec`；从 plan.md 原始 fenced block
  抽取 exact PowerShell，仅把尚未产生的 amendment fresh-main placeholder 临时替换为当前可达 formal merge
  `d7f8b16371662dd04cfd0e9a6b918cb7f92a5e9f`，执行 PASS；未维护替代脚本。
- `program validate` PASS；`verify constraints` no BLOCKERs；manifest exact=`1 passed in 97.18s`；Ruff 0.15.7
  全库诊断=`273 red/133 green`；`git diff --check` PASS。
- `src/tests/deps/workflow` 相对 formal merge 零差异；root/scoped handoff byte-identical；两份 Cursor rule SHA=
  `d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a` 且相对 formal merge 零差异。
- Pre-sync truth audit 按预期 `stale`，current recompute=`ready`、inventory=`1126/1126`、missing/unmapped=
  `0/0`、各层=`214/214`。提交本 receipt 后执行 terminal truth sync；最终 snapshot 不反写 tracked source。

## 20. Batch 2026-07-19-016：V4 amendment final review Round 3 FAIL

- Exact identity：HEAD=`67455e7e381f0424d9de137fdf094307ad41375c`、tree=
  `be44ca486bc832d81b3e0d08af56c6bc54471815`、clean；Pascal/LEAN 与 Confucius/SAFETY 均=`FAIL1`
  （P3×1），两份 verdict 全部退役。
- 唯一重叠 finding 成立：terminal truth 已 sync 且 audit=`ready/fresh`，但 development summary 与双 handoff
  仍停留在 pre-sync 状态，可能让续接 agent 重复执行 truth。两位 reviewer 对 V4b 语法、end-exclusive、
  deletion boundary、native failure/output、committed+clean frozen candidate、ancestor/diff/cleanup、Ordinal path、
  scope/truth/T66 均未发现额外问题。
- 最小修正只更新 summary、append-only log 与 byte-identical 双 handoff；持久 Exact Next Steps 直接从新身份
  双审开始。该 source commit 后紧跟 terminal truth sync 与 manifest-only commit；最终 snapshot 不再反写 tracked
  source，避免自引用 stale 循环。

## 21. Batch 2026-07-19-017：V4 amendment PASS、PR 与 fresh-main

- Final identity：HEAD=`e4ca3e4276067d832483cad4266783476c3b9ffe`、tree=
  `1bef978ff9f33747b4a9586fb6da3fb28db77769`、clean；Pascal/LEAN 与 Confucius/SAFETY Round 4 同身份
  `PASS0`、actionable findings=0。
- PR #161 Codex reviewed exact `e4ca3e4276` 无 major issue、review threads=0；10 个 required checks 全绿，
  包括 Ubuntu/macOS/Windows Python 3.11/3.12、Windows cmd/pwsh、verify 与 aggregate gate。
- Squash merge=`8999efcf2feccab88f8b957601b0be379032a1b7`；merge tree 与 reviewed tree 完全一致。Detached
  fresh-main truth=`ready/fresh`、inventory=`1126/1126`、manifest exact=`1 passed in 103.64s`、validate/
  constraints/V4b/parity/Cursor/clean 全绿。
- `FORMAT_BASE_SHA` 自此冻结为 `8999efcf2feccab88f8b957601b0be379032a1b7`；amendment T15 完成，
  只授权 implementation，GAP-15/T58 与 T66 状态不变。

## 22. Batch 2026-07-19-018：implementation RED/GREEN 与 full gates

- Dev branch clean rebase 到 amendment fresh-main；test-only commit=`8f4f63dd`、product commit=`bd8a0de2`。
  Test-only detached replay 精确 RED=`16 failed, 33 passed in 16.27s`：15 个 read-only sentinel case 均因
  legacy hook 被消费而失败，另 1 个 production Cursor A/B 因真实写入失败；其余 init/link/hook 33 项保持绿。
- 产品修正只把 `_workitem_before_command()` 的 guard 改为 `ctx.invoked_subcommand != "link"`；一行产品 diff，
  无 command list、helper/classifier、公共符号、依赖、配置、版本或 handler 变化。
- GREEN targeted=`49 passed in 15.14s`；full=`3302 passed, 3 skipped in 673.22s`；Ruff lint PASS、V4a
  三文件 strict format PASS、constraints no BLOCKERs、`git diff --check` PASS。
- V4b 使用固定 base `8999efcf...a1b7` 与 frozen candidate `bd8a0de2` PASS；candidate red paths 是 base 的
  Ordinal 子集。Emitted exclusive ranges：product=`63-64`；init=`22-23, 167-168, 169-185, 187-189,
  351-352, 353-371, 373-375, 447-453, 454-457, 458-462, 463-468, 469-487`，全部 formatter-clean。
- T21～T24 完成。下一步只做 implementation terminal truth/handoff/gates 与同身份双审；在 T32
  fresh-main 前 GAP-15/T58 仍 active、T66 T61A 仍 blocked。

## 23. Batch 2026-07-19-019：implementation terminal source freeze

- Execution/continuity source commit=`581cf344`；首个 truth sync snapshot=
  `034f346489b0b9a233208098ab453a245928d222bd90040392625193ff80d732`、inventory=`1126/1126`、
  missing/unmapped=`0/0`、各层=`214/214`，manifest-only commit=`e68ae027`。
- 为避免 T31 永久停在 `in_progress` 或 final gate receipt 反写后立即令 truth stale，本 source 把 T31、summary 与
  byte-identical handoff 预置为持久终态：final manifest-only sync 后直接进入同身份双审，不再要求续接 agent
  重复 truth sync。
- 本 source 后必须再次 terminal truth sync，并只在新的 committed+clean identity 上重跑 targeted/full、Ruff
  lint/V4a/V4b、constraints、validate/audit、manifest exact、scope/parity/Cursor/diff-check。任一失败即不得送审；
  成功结果作为 reviewer/PR 外部 receipt，不再修改 tracked source。
- T31 完成边界不关闭 GAP-15/T58；T32 implementation fresh-main 前 lifecycle/T66 继续 blocked。

## 24. Batch 2026-07-19-020：implementation final review Round 1 FAIL

- Exact identity：HEAD=`7b33ec6784548ba624852293c5b79f78883e0a39`、tree=
  `b8d0690c05b8a654335b08c2b5831e401147e114`、clean；Pascal/LEAN=`FAIL1`（P3×1），
  Confucius/SAFETY=`PASS0`。因 identity 将变化，两份 verdict 同时退役。
- Pascal 唯一 finding 成立：本日志顶部仍称“产品代码未修改”，双 handoff 首个 next step 仍要求重复已经通过
  的 terminal gates。最小修正只把状态改为一行实现/T21～T31 completed，并让持久 next step 直接从新身份
  双审开始。
- 两位 reviewer 对产品一行最小性、479 行测试的合同映射、exact output/bytes/write-set/order、V4、truth/scope/
  parity 与 lifecycle/T66 均无其他 finding；Confucius 亲自重跑 targeted=`49 passed in 11.13s`。
- 修正后再次 terminal truth sync，并对新 identity 重跑全部 T31 gates；不得复用本轮 SAFETY PASS。

## 25. Batch 2026-07-19-021：PR #162 跨平台夹具缺陷修正

- Round 2 final identity=`8d09b7bba8e98b5c7858084ee8e6d3c705645e8b`/tree=
  `10e877b573e5568f418535b90841e6626546fe2b`，Pascal/LEAN 与 Confucius/SAFETY 同身份 PASS0；PR #162
  Codex reviewed exact `8d09b7bba8` 未发现 major issue、review threads=0。
- Compatibility Gate 的 Ubuntu 3.11/3.12 与 macOS 3.11/3.12 均只失败
  `test_plan_check_real_cursor_hook_matches_no_op_without_writes`：两个独立 repo 的绝对路径分别含
  `baseline`/`candidate`，Rich 在宽终端输出完整路径并产生不同列宽，`candidate.stdout == baseline.stdout`
  因夹具输入不同而误报；其余 3301 项通过，产品 bytes/tree assertions 在失败前已通过。
- 本地 `COLUMNS=200` 精确复现=`1 failed in 1.01s`。最小修正删除 `shutil.copytree` 与第二套 repo，让 no-op
  与真实 hook 在同一 repo 顺序运行；首轮 no-op 后先验证 guarded bytes/tree 未变，因此第二轮输入严格相同，
  exact stdout/stderr/exit 合同保持且测试净删 13 行，产品、依赖、workflow、版本均零变化。
- 修正后宽终端单测=`1 passed in 0.96s`、targeted=`49 passed in 16.00s`、Ruff lint/format PASS。旧双审和
  Codex review 随 identity 变化退役；提交 continuity/test、terminal truth 与全部 gate 后必须同身份重新双审，
  再 push PR #162 并重新请求 Codex current-head review。

## 26. Batch 2026-07-19-022：夹具修正 terminal gates 与 LEAN continuity FAIL

- Test/continuity correction=`ffdd9cef`，truth snapshot=
  `bf71628554e3ec1ab8b99d339249e53200e071c38921f947532aad5ef8ae447a`，manifest-only commit=
  `33a37b53df52ac9daec93225d4b78c32ff8d9ebc`、tree=`90e5e9509a1c78d96e12fbd74320c619470b1bba`。
- Exact identity terminal gates：`COLUMNS=200` targeted=`49 passed in 15.82s`、full=
  `3302 passed, 3 skipped in 674.46s`；Ruff lint/V4a/V4b、constraints、validate、truth=`ready/fresh`
  1126/1126、manifest exact=`1 passed in 102.03s`、11-file scope/handoff parity/Cursor/clean 全绿。
- LEAN Round 3=`FAIL1`（P3×1）：双 handoff 和 summary 仍把上述已完成 gates 写成下一步；代码与测试本身、
  同 repo A/B 防假绿、产品一行最小性和净删 13 行均通过。Finding 成立，只修正文档/continuity 并刷新
  terminal truth；旧 LEAN verdict 与已中止的 SAFETY 审查全部退役，新 identity 必须从零双审。

## 27. Batch 2026-07-19-023：SAFETY 双项目隔离 finding 与修正

- Continuity correction 后 identity=`551d90b93f615b85a6145aa4fa72d9e32b641fe0`/tree=
  `99b0168b2ddf4043c5799b40383b0b7a50f252c7`，truth/manifest/targeted/Ruff/V4/constraints/scope 均通过，
  且相对宽终端 full-pass identity `33a37b53` 的 src/tests/tooling 零差异。
- SAFETY Round 4=`FAIL1`（P3×1）：同 repo 顺序 A/B 与 plan §5.2 的“两份 byte-identical 临时项目”不一致，
  不能独立隔离 Git 内部状态。Finding 成立，不修改 formal；恢复两个隔离 repo，并把目录名设为等长的
  `control/subject`，防止 Rich 表格列宽受路径长度影响。
- stdout/stderr 仅把各自绝对根路径归一为 `<repo>` 后做完整相等比较；exit、guarded bytes、全 tree/status
  仍严格比较，其他字符、空格、表格边界或 receipt 差异不会被吞掉。80/200/300 列单测均通过，宽终端
  targeted=`49 passed in 15.51s`，Ruff lint/format PASS。
- 相对 PR 首轮 reviewed identity `8d09b7bb`，该测试 correction 是 `+9/-4`，未新增公共 fixture/DSL/产品
  抽象；产品代码仍只有一行。提交测试/continuity、刷新 truth并重跑 terminal full/gates 后重新双审。

## 28. Batch 2026-07-19-024：双项目 correction terminal gates

- Source correction=`c2c9bc03`，truth snapshot=
  `b9686071fe78277207f7b78bdf9face0d122f1e024a20538e8a3e1c3f00401b6`，manifest-only identity=
  `36f49b6268d8bea543d2681a47b32b3e7f3691c0`/tree=`04ae4bea9474a30a15c80e16b97769d8f39de64c`。
- Exact identity：80/200/300 列 real-hook A/B 单测 PASS；`COLUMNS=200` targeted=`49 passed in 16.47s`、
  full=`3302 passed, 3 skipped in 683.70s`；Ruff lint/V4a/V4b、constraints、validate、truth=`ready/fresh`
  1126/1126、manifest exact=`1 passed in 110.91s`、11-file scope/handoff parity/Cursor/clean 全绿。
- 本 continuity correction 只把已完成证据写入 summary/log 与 byte-identical handoff，并把唯一 next step 设为
  新 identity 双审；提交后刷新 truth并重跑相关治理门禁，src/tests/tooling 不再变化。

## 29. Batch 2026-07-19-025：最终本地审查测试证据收口

- PR #162 current identity=`98b7c6f25df420d8cb7f3be6e9e516a7dc343441`/tree=
  `6316f459fa31143c8dcbedfa792cc6ed7165e9fa`、clean；Pascal/LEAN=`PASS0`，Confucius/SAFETY=
  `FAIL2`。两项 finding 均成立，旧 verdict 全部退役。
- P2：既有 `init` missing-state 测试已创建 `.ai-sdlc/project/config`，不能证明 §3.2 的真实 no-project
  `root is None` 路径。最小新增一例空目录 CLI 测试，冻结 exit=`1`、逐字输出、hook=`0`、scaffolder=`0`
  与目录零写入；临时把 hook 移到 root check 前，得到预期 RED（`calls=['adapter']`），随后恢复产品源码。
- P3：config-lock partial-write 测试先 `split/join` 再比较，会吞掉空格与换行漂移。最小改为稳定相对
  `project-config.yaml` error path、固定 Console width=`500`，并直接比较 `console.export_text()` 与完整期望
  字符串（含末尾换行）；临时把 warning 增加一个空格，得到预期 RED，随后恢复产品源码。
- 修复态两项=`2 passed`，`COLUMNS=200` targeted=`50 passed in 15.58s`，80/200/300 列 real-hook A/B
  均 PASS，Ruff lint、可清洁 hook unit format、diff-check 与产品源码零差异断言全绿。此前 full 在收到
  finding 后于 67% 主动中止；当时 `2285 passed, 3 skipped` 只作诊断，不作为验收，final identity 必须完整重跑。
- OpenAI 官方 Codex PR review 事故仍在进行。用户明确批准 PR #162 的一次性治理例外：不再无限等待
  GitHub Codex，改以 final current-identity 本地 LEAN + SAFETY 双 PASS0、完整本地验证与远端 22/22
  required checks 共同作为 merge 门槛；本例外不自动扩展到 lifecycle 或发布阶段。

## 30. Batch 2026-07-19-026：本地审查修正 terminal gates

- Test/continuity source=`a71c3c3e`，truth refresh 后 terminal identity=
  `56367d966b6f7755f9388da5b56702a01146ed30`/tree=`64305f84a0004951ee15d1b5b00e0fb1672a92b6`、clean。
- Exact identity：`COLUMNS=200` targeted=`50 passed in 16.79s`、full=`3303 passed, 3 skipped in
  644.45s`；80/200/300 列 real-hook A/B PASS；Ruff lint/V4a PASS；fixed-base V4b 的 base/candidate
  formatter-red subset 与 13 个 emitted range 全绿；constraints no BLOCKERs；program validate PASS；truth=
  `ready/fresh`、inventory=`1126/1126`、missing/unmapped=`0/0`、各层=`214/214`；manifest exact=
  `1 passed in 92.54s`；diff/scope/handoff parity/Cursor/clean 全绿。
- 本 continuity-only receipt 只把已完成门禁与唯一 next step 固化进 summary/log/byte-identical handoff，不改
  src/tests/tooling。提交后必须再次 terminal truth sync，并在新 committed+clean identity 重验完整门禁；成功后
  不再反写 tracked source，直接交 Pascal/LEAN 与 Confucius/SAFETY 同身份复审。

## 31. Batch 2026-07-19-027：implementation 双 PASS、mainline 与 fresh-main

- 最终 reviewed identity HEAD/tree=`75d6037514930c587e6138f833d8a99ec78ca604`/
  `03b4a1ffc3d5997d2856e71f145d3fea6db51cf3`、clean；Pascal/LEAN 与 Confucius/SAFETY 同身份
  `PASS0`，actionable findings=0。
- Exact identity 本地 full=`3303 passed, 3 skipped in 707.62s`、targeted=`50 passed`，80/200/300 列
  real-hook A/B、Ruff/V4a/fixed-base V4b、constraints、validate、truth=`ready/fresh 1126/1126`、manifest
  exact、scope/parity/Cursor/clean 全绿；PR #162 required checks=`22/22 success`、review threads=0。
- OpenAI 官方 Codex PR review 事故期间，用户批准本 PR 一次性治理例外：以 exact-head 本地双 PASS0、
  完整本地门禁与 22/22 checks 替代 current-head GitHub Codex 回执。该例外不自动扩展到 lifecycle 或发布。
- PR #162 squash merge=`2845fedcf46859b3945f327b8d8b96e9c7ca0dab`，implementation 分支未删除；
  detached fresh-main tree 与 reviewed tree 相同，full=`3303 passed, 3 skipped in 707.39s`、targeted=
  `50 passed in 16.42s`，其余实现门禁全绿。

## 32. Batch 2026-07-19-028：lifecycle reconciliation source

- 从 exact main `2845fedc` 创建 `codex/214-workitem-readonly-adapter-side-effect-lifecycle`；只对账
  WI214/WI196/WI213 lifecycle docs、root/scoped handoff 与 truth/manifest，`src/tests` 零差异。
- 本 source 将 GAP-15/T58 标记为以 lifecycle merge/fresh-main 生效的 closed/completed，并把 T66 从
  implementation blocked 改为 ready；唯一授权是另建 T66 implementation WI，T61A 双 readiness GO 前
  不得写产品代码。
- T66、GAP-03、WI196、RC-08 与 release 仍为 open；不得创建版本/tag/GitHub Release/PyPI 或更新共享 CLI。
- 下一步：提交 source、truth sync、治理/manifest/scope/parity/clean 门禁，再由 Pascal/LEAN 与
  Confucius/SAFETY 对同一 committed+clean identity 从零双审；双 PASS0 前不得 push。
