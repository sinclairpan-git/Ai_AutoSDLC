# 任务执行日志：Workitem 只读命令 Adapter 副作用隔离

**功能编号**：`214-workitem-readonly-adapter-side-effect`
**创建日期**：2026-07-19
**当前状态**：formal terminal gates 已通过；final current-identity 双审待执行；产品代码未修改

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
