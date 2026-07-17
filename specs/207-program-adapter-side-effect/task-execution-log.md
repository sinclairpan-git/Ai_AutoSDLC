# 任务执行日志：Program 治理命令 IDE Adapter 副作用隔离

**功能编号**：`207-program-adapter-side-effect`
**创建日期**：2026-07-16
**当前状态**：formal authoring

## 1. 归档规则

- 本文件按批次追加事实，不把未执行计划写成已完成。
- 精确 Program Truth snapshot/hash 只以终态 `program-manifest.yaml` 为准，避免 authoring 自引用。
- 每批记录范围、命令、结果、findings、回退、branch/worktree disposition 和下一步。
- 产品/测试实现与当批 execution log/tasks 状态使用同一逻辑 commit；PR/merge/fresh-main 事实可在后续
  route writeback 批次追加。

## 2. Batch 2026-07-16-001：T11 只读根因分流

### 2.1 基线

- revision：`origin/main@506e950dee3469248ef7e6b5e1aac664668d18a1`
- worktree：`.worktrees/207-side-effect-diagnosis`，detached、初始 clean
- Python：`uv` 解析 CPython 3.11.15

### 2.2 Program adapter 复现

执行 `uv run ai-sdlc program validate`：

- exit=`0`，业务结果=`program validate: PASS`
- 额外输出=`IDE adapter (cursor): installed 1 file(s)`
- `.cursor/rules/ai-sdlc.mdc`：
  - before=`d5f04acf353c96b7dbd1bfbdd43382f986e8d4ff4413475d46ce46449e260b6a`
  - after=`02d9656d24ae4d77b30d99b2b6accd2623e2b48527305f8f199c3bfb45e4e134`
- `.ai-sdlc/state/resume-pack.yaml` 与 canonical handoff SHA 不变。

随后执行 `uv run ai-sdlc verify constraints`：exit=`0`、`no BLOCKERs`；Cursor、resume-pack、handoff
SHA 均相对 verify 前不变。因此 verify 不是本次 Cursor mutation 来源。

### 2.3 Resume-pack 独立复现

执行 `uv run ai-sdlc status`：exit=`0`，输出 `resume-pack stale; rebuilding from checkpoint`；两份
resume-pack 被同步改写：

- constitution/tech-stack/spec/plan/tasks 从 repo-relative 变为当前 `.worktrees/...` 绝对路径；
- `current_branch: feature/206-model-string-dedupe-dev` 变为 `current_branch: ''`；
- `active_files` 变为空；
- `context_summary` 变为空。

调用链审计确认 program/verify 不调用 `load_resume_pack()`；status/recover/handoff update 才进入
continuity rebuild。因此本症状不属于 WI207。

### 2.4 分流决策

- GAP-12 / WI207：root `program` dispatch implicit adapter side effect + program test isolation，L1。
- GAP-13 / WI208：resume-pack portable/lossless canonical reconstruction source，L2。
- verify telemetry 潜在写入语义：另行登记，不混入 WI207/WI208。

Carver / `wi202_real_spike` 完成独立只读诊断，无文件修改；结论与本地复现一致。

## 3. Batch 2026-07-16-002：T12 canonical formal init

- docs branch：`feature/207-program-adapter-side-effect-docs`
- worktree：`.worktrees/207-program-adapter-side-effect`
- base：`origin/main@506e950d`
- 命令：`uv run ai-sdlc workitem init --wi-id 207-program-adapter-side-effect ...`
- 结果：创建 canonical `spec.md / plan.md / tasks.md / task-execution-log.md`，manifest 增加 WI207，
  `next_work_item_seq` 从 207 更新为 208。
- 已知副作用：workitem init 在当前基线通过既有 hook 刷新 `.cursor/rules/ai-sdlc.mdc`；该 tracked
  文件不属于 formal diff，terminal truth 后使用 `apply_patch` 精确恢复。

## 4. Batch 2026-07-16-003：T13 formal authoring

### 4.1 冻结边界

- 产品：`src/ai_sdlc/cli/main.py` 仅增加一个 `"program"` tuple member。
- 测试：`tests/integration/test_cli_program.py` 增加 autouse isolation 与 real-hook byte-stability。
- 非目标：`ide_adapter.py`、ProgramService/program handlers、resume-pack、verify telemetry。
- 预算：product additions≤1；test additions≤90；新产品/测试文件、函数、公共 API、依赖、config=0。

### 4.2 Formal 路线写回

- child 五件套已改为可执行合同，无 scaffold placeholder。
- 父项新增 GAP-12/GAP-13 和 T55/T56；WI208 在 WI207 fresh-main 后启动。
- WI206 的 PR/merge/fresh-main 关闭证据进入历史 log/summary；只标记其一个 T63 family
  `completed_reduction`，不关闭父路线。

### 4.3 下一步

1. root exact truth test 已按新增五件套把 inventory `1086→1091`、close `206→207`，不新增测试逻辑；
2. 同步 truth/continuity，并精确恢复 Cursor side effect；
3. 计算六文件 combined hash；
4. Pascal/Confucius 对同一 hash 对抗评审，直到双 PASS。

## 5. Batch 2026-07-16-004：T14/T21 truth 与静态门禁

- `program truth sync --execute --yes`：state ready、source inventory complete、unmapped=0、missing=0；
  精确 snapshot/hash/计数只以当前 `program-manifest.yaml` 为准。
- `program validate`：PASS；`program truth audit`：state ready、snapshot fresh、exit 0。
- `verify constraints`：no BLOCKERs。
- root exact truth node：`1 passed in 78.35s`；新增 WI207 五件套对应 inventory/close 计数已机械对齐。
- `git diff --check`：PASS；formal branch `src/**` product diff 为空；测试 diff 只含 root exact truth 两个
  值替换，无新增测试逻辑或行数。
- 已知 root hook 再次 materialize Cursor managed rule；已用 `apply_patch` 精确恢复 HEAD，
  `.cursor/rules/ai-sdlc.mdc` 不在工作树 diff。
- root/scoped resume-pack 已人工恢复 repo-relative path、active files 与当前 docs branch；这是 GAP-13
  修复前的已知 workaround，不冒充 WI208 产品修复。

T13、T14、T21 完成。下一步冻结 formal combined hash 并执行 T22/T23 对抗评审。

## 6. Batch 2026-07-16-005：T22/T23 Round 1 双 FAIL

- formal combined=`f74a06abb535785e114cadd6f0aca7582729029a677a1e4cc4d9e5753914de75`
- baseline HEAD=`506e950dee3469248ef7e6b5e1aac664668d18a1`；tree=
  `35fa6f37ad4334ed142dc8e8bad4b1d1c71ed06c`
- cached binary diff=`cf90cda7b7f97d342e608330d756c246fb17d926377693feeededa86809f748a`
- cached name-status=`a157355b9951d59a10480ce38cabfaacc0aa3f99ae01c516bd2fa2fc1d8a45cc`
- Pascal / 精简直接性=`FAIL`：父 FR-12/SC-04/tasks 与 root exact truth test 例外冲突；父 NC 矩阵
  漏 T55/T56；子 CC-01/02 映射错误且漏 CC-03；T56 对后续减重未形成任务硬依赖。
- Confucius / 兼容安全=`FAIL`：同意测试例外与 NC 矩阵 finding；另指出 handoff/resume Exact Next
  仍要求重复 truth sync，与“已完成、等待评审”状态矛盾。
- 双方均确认一行产品方案、autouse/real-hook 测试必要性、execute/显式 adapter 兼容与 WI207/WI208
  实现边界本身合理；评审期间未修改文件，起止 hashes/status 一致。

### 6.1 处置

1. 父 FR-12、SC-04、tasks 加入唯一 root exact truth 两值机械例外；
2. 父 §6.1/§6.3/追踪矩阵把 T55/T56 纳入 NC-01～NC-06 + impact CC、RC N/A；
3. 子合同拆正 CC-01 surface、CC-02 exit、CC-03 artifact/schema，并同步追踪；
4. 父 tasks 增加全局恢复门禁：T56 fresh-main 前不得启动任何新 T61/T62/T63～T67 实例；
5. continuity 记录 Round 1 FAIL；下一步改为修订、重跑门禁、恢复 Cursor、冻结新 hash、从零复审。

Round 1 verdict 已失效。T22/T23 评审动作完成但未通过；T24 进入修订中。

### 6.2 Round 1 findings 闭环与 Round 2 前置

- 父 FR-12/SC-04/tasks 已加入唯一 root exact truth 两值机械例外；
- 父 NC 非减重范围、§6.3 适用矩阵和追踪矩阵均已覆盖 T55/T56，RC 明确 N/A；
- 子合同已按父定义拆分 CC-01 surface、CC-02 exit、CC-03 artifact/schema；
- 父 tasks 已增加 T56 fresh-main 的全局恢复硬门禁；
- root/scoped handoff 与 resume-pack 已记录 Round 1 FAIL，不再要求恢复者重复旧 terminal sync。

修订后门禁：truth sync/validate/audit ready/fresh；constraints 无 BLOCKER；root exact truth node重新通过；
working/cached diff-check通过；Cursor rule精确恢复HEAD。下一步只冻结Round 2新hash并从零双审；若双PASS，
不再修改formal target，进入formal PR。

## 7. Batch 2026-07-16-006：T24 Round 2 双 FAIL 与顶层范围闭环

- Round 2 combined=`262d2613990f9b92e57e7777e95d97cef244f07e2ad22bd84029d672e089682d`
- cached binary=`aa59134598b473211d94ccc4cfb8f6c1146477ae696d9ab8cb4377a58116a599`
- Pascal=`FAIL`：父 tasks 顶层仍写“四件套”，与合法 staged 的 child/parent 五件套及 WI196/WI206/WI207
  development summary 冲突。
- Confucius=`FAIL`：父 spec 顶层仍说测试只能由后续 WI 修改，与 FR-12/SC-04 的 root exact truth 唯一
  例外冲突。
- 双方确认 Round 1 的 NC/CC、测试例外主体、T56 全局门禁和 continuity findings 已闭环；产品方案、
  测试设计、execute/adapter 兼容和 WI207/WI208 边界无其他 finding。

处置：父 spec 顶层明确引用 FR-12 唯一测试例外；父 tasks 顶层精确允许 current child/parent 五件套、
被关闭前项 execution/summary 与 truth/continuity。Round 2 verdict 作废；terminal sync/restore 后冻结
Round 3，新目标只做从零双审。

## 8. Batch 2026-07-16-007：PR #139 Codex P2 与 formal 兼容重开

- 首轮 formal PR #138 合入 `main@5c7c46c9`，implementation PR #139 的 naive 一行 bypass 已完成
  read-only RED/GREEN、focused/full、rollback 与 Pascal/Confucius final PASS。
- Codex review 在 PR #139 指出全族 bypass 会取消 mutating program 的 adapter refresh；Pascal 与
  Confucius 独立复核后共同接受核心 finding，但把影响收窄为真正依赖持久化 host ingress 的
  `managed-delivery-apply` 与 `solution-confirm --execute --continue`。
- 真实状态依赖：普通终端 init 可只记录 `materialized`；进入匹配 AI 宿主后的旧 root hook 会持久化
  `verified_loaded`，managed delivery 以此解除 `host_ingress_below_mutate_threshold`。现有 execute
  tests 直接预置 verified 状态，未覆盖首次迁移。
- 按 spec §7 stop rule，PR #139 转为 draft，旧 formal/final verdict 全部失效；docs branch 从已合并
  formal fast-forward 到 `main@5c7c46c9`，重新冻结 L2/CC-05 合同。
- 修订方案严格限制为 4 行产品 additions：main bypass、program_cmd 一个既有 hook import、两个局部
  调用；禁止通用 execute 分类器、ide_adapter/ProgramService/第三个 handler 改动。
- TDD 改为双轴：原始基线 read-only RED/ingress GREEN，naive bypass read-only GREEN/ingress RED，
  corrected candidate 两轴 GREEN。下一步重跑 formal 静态门禁并冻结 Round 4 combined hash。
- 删除注释原因：`specs/207-program-adapter-side-effect/plan.md` 原注释“**停止**：RED 原因不是 root dispatch，或 GREEN 需要修改第二个产品文件。”会错误阻断已验证必须修改 `program_cmd.py` 的兼容修复；同位置已替换为限制 `ide_adapter.py`、ProgramService、第三个 handler、helper/分类器及四行预算的更精确停止条件。

## 9. Batch 2026-07-16-008：Round 4 双 FAIL 与两阶段刷新合同

- Round 4 combined=`8cc93382f8886dd6f7613cca3b4c705fa935de94f830e1ee11a4ffa4f1dcdeae`；Pascal 与 Confucius
  均独立重算一致并给出 FAIL，评审期间六文件未变。
- 共同 finding：父 CC-05 未登记 managed dry-run 唯一例外；parent T55 仍残留旧范围；naive 阶段
  program-local binding 尚不存在，fixture 必须使用 `create=True`，否则 RED 来自 import/patch 失败。
- 时序分歧经主 Agent 收敛为命令既有的两阶段语义：solution confirmation 先在 `--execute --yes`
  下完成持久化；只有 preflight、continue 和 effective-change ack 全部通过后，才紧邻 managed request
  前单行刷新。这样未授权/失败路径零 adapter 写入，且无需第五行条件或布尔短路表达式。
- 批准差分：solution-confirm continue 的 adapter notice/hook 从 root 前置阶段后移到 solution 已持久化
  之后、managed guard 之前；hook 失败可保留已确认 solution artifact，但不得生成 managed
  request/artifact。managed-delivery-apply dry-run 继续作为唯一幂等 host-verification 写入例外。
- 已同步父/子 CC、FR、SC、plan 与 tasks，并加入 missing yes/preflight/no-continue/missing ack 的零调用/
  零写入验收。Round 4 verdict 全部作废；重跑 truth/constraints/root exact 后冻结 Round 5。

## 10. Batch 2026-07-16-009：Round 5 一 PASS 一 FAIL 与既有 preflight 语义显式化

- Round 5 combined=`0ed22f058ae9dd4ca53684894e03768f60c074f5bab78e1fcafeafb0cfc631f0`；Pascal PASS，
  Confucius FAIL；双方独立重算一致，六文件在评审期间未变。
- Confucius 指出三处遗漏：批准差分未覆盖 truth sync execute/solution no-continue 等所有非 managed
  program 路径；父 CC-05 未区分 WI207 adapter delta 与既有 truth-derived request 物化/缺 yes preflight；
  “hook 失败”未区分传播异常和 project-config lock 的 warning-and-continue。
- Round 6 维持四行产品边界，不改变代码方案；只把既有行为写成可执行合同并要求回归：非两个 managed
  入口全部移除 root hook；direct apply missing yes 保留 adapter/request preflight、禁止 mutate/apply；
  `RuntimeError` 停止 managed phase，config-lock 软失败继续并可据旧 ingress 产生 blocker/artifact。
- Round 5 两个 verdict 均作废；完成 terminal sync 后冻结 Round 6 新 combined hash，从零双审。

## 11. Batch 2026-07-16-010：Round 6 同哈希双 PASS

- review target：parent/child `spec.md + plan.md + tasks.md` 六文件；combined SHA-256=
  `2eaa2c0fa7aa18f9cd3598a89dbb85db78d0369d4f9342182f027bd0fedf5fcd`。
- Pascal / lean-directness；time=`2026-07-16T20:24:50Z`；findings=`none`；disposition=`PASS`；确认四行
  产品边界、两入口、代表性测试和既有 preflight/异常合同直接且无范围蔓延。
- Confucius / compatibility-safety；time=`2026-07-16T20:24:50Z`；findings=`none`；disposition=`PASS`；
  确认授权、副作用、direct missing-yes、传播/软失败、回退和 fresh-main 合同一致。
- 两位 Agent 均独立重算完整 hash，评审期间六文件、HEAD 与工作树内容未漂移；用户不承担 formal
  逐条评审。Round 6 后六文件冻结，不再修改；下一步只记录 receipt、同步 truth 并进入 formal PR。

## 12. Batch 2026-07-16-011：PR #140 Codex P2 与 Round 7 机械状态双 PASS

- PR #140 Codex review 对 `tasks.md` 提出 P2：T22～T25 仍停留在复审前状态，与 Round 6 双 PASS、
  handoff 和已创建 PR 的事实矛盾；finding 接受。
- 最小修订仅更新四个状态：T22/T23=Round 6 PASS，T24=已完成并引用 §11，T25=PR #140
  review/required checks 进行中；合同正文、实现预算、测试和依赖未改。
- 新 combined=`4394016e7d7af59090bf0a8ecaea82be0286c1fbbafaf5976467a3bf99ebc8c5`。
- Pascal/lean 与 Confucius/safety 均独立重算并 PASS，findings=`none`；确认状态真值、T24/T25 依赖和
  T35 formal-mainline 硬门禁一致。Round 6 hash 退役，Round 7 成为当前冻结 formal receipt。

## 13. Batch 2026-07-16-012：第二轮 Codex P2 与自失效 receipt 修复

- Codex 在当前提交 `7196234c` 指出：T22/T23/T24 仍绑定 Round 6 / `2eaa2c0f...`，而同一提交已经
  宣布 Round 6 退役、Round 7 为当前 formal；finding 成立。
- 根因不是合同内容，而是把动态 round/hash 写进参与 combined hash 的 `tasks.md`，每次机械写回都会
  产生新的 formal hash。修订后 T22～T24 只引用 execution log 最新终态回执，并明确 Round 6/7 为
  历史；具体 combined/verdict 继续记录在不参与六文件 combined 的本日志。
- Round 7 receipt 退役；重新计算固定六文件 combined，并由 Pascal/Confucius 从零复审。双 PASS、
  terminal gates 与新 Codex review 完成前，PR #140 不合并，PR #139 保持 draft。

## 14. Batch 2026-07-16-013：Round 8 双 FAIL 与假完成消除

- Round 8 combined=`484441ac7477f935fd595a8fcafe0c072c4ca38696d600a5c947d34415fbe735`；Pascal 与
  Confucius 均独立重算一致并判定 `FAIL`。
- 共同 finding：T22～T24 虽已把动态 hash 外置，仍提前声明“已完成/有效 PASS”，与 summary/log 的
  “当前重新双审”矛盾，形成可证性假完成。
- 最小修订只替换三行状态：由 execution log 最新 formal 同哈希终态回执决定；formal 文件不再
  内嵌动态 round/hash/verdict，也不预先声明完成。Round 8 退役，新 combined 从零双审。

## 15. Batch 2026-07-16-014：Round 9 回执（已作废）

- 当时按 child spec 的重复编码记录 combined=
  `6a661de80c947fde2c7f73ee3d29fd21b9e041cd052ed11e2bf584eef46473b4`；该值不是父计划 §9
  canonical recipe 的结果。
- Pascal / lean-directness 与 Confucius / compatibility-safety 当时均对该非 canonical 标识给出
  `PASS`；PR #140 当前 HEAD 的 Codex P1 与双方独立复算证明回执身份错误，两个 PASS 同时退役。
- 结论统一：T22～T24 的状态由本日志最新 formal 同哈希终态回执决定，不再自引用或假完成；四行
  产品合同、110 行测试预算、授权/异常/回退/fresh-main 边界均未改变。
- 本节只保留历史审计，不是当前终态回执。

## 16. Batch 2026-07-16-015：Round 9 terminal gates

- `uv run ai-sdlc verify constraints`：no BLOCKERs。
- `uv run ai-sdlc program truth sync --execute --yes`：ready；目标提交的动态 truth 三元组以
  `program-manifest.yaml` 为准，不在版本化日志中硬编码；inventory `1091/1091 mapped`、
  unmapped/missing=`0/0`。
- `uv run ai-sdlc program validate`：PASS；`program truth audit`：ready/fresh。
- root exact truth node：`1 passed in 77.31s`；`git diff --check`：PASS。
- 已知 GAP-12 导致 terminal program 命令刷新 tracked Cursor rule；已使用 `apply_patch` 精确恢复 HEAD，
  `.cursor/rules/ai-sdlc.mdc` 最终无 diff。root/scoped handoff 与 resume-pack 分别字节一致；resume-pack
  已恢复 repo-relative path、当前 branch 与 13 项 active files。
- terminal gate 结果保留为历史执行证据；其不能修复错误 review-target 身份。Round 9 双 PASS 已失效，
  T22～T24 重新打开。

## 17. Batch 2026-07-16-016：canonical recipe 单一化

- Codex 在 PR #140 当前 HEAD 提出 P1：父计划 §9 与 child spec §8 定义了两套互斥组合算法。
- Pascal 与 Confucius 分别按父计划独立复算，均得到修订前 canonical combined=
  `68829454a346c885b6e5ab731d715e48dee05eaee9a63513e73abdfc2292ceb8`，并一致 `FAIL`；旧
  `6a661de8...73b4` 回执明确退役。
- 最小修订只删除 child spec 的重复编码并引用父计划 §9 唯一 recipe；完成终态门禁后冻结新 combined，
  两位 reviewer 必须从零复审同一新哈希。

## 18. Batch 2026-07-16-017：canonical Round 10 terminal gates

- `uv run ai-sdlc verify constraints`：no BLOCKERs。
- `uv run ai-sdlc program truth sync --execute --yes`：ready；动态 truth 三元组以目标提交
  `program-manifest.yaml` 为准；inventory `1091/1091 mapped`，unmapped/missing=`0/0`。
- `uv run ai-sdlc program validate`：PASS；`program truth audit`：ready/fresh；root exact truth node：
  `1 passed in 76.33s`；`git diff --check`：PASS。
- 已知 GAP-12 Cursor 非目标刷新已用 `apply_patch` 精确恢复；worktree blob 与 HEAD 均为
  `ec0ed427a1db1d14370e1518a0c0fd2b8880384b`，无 Cursor diff。
- 冻结 canonical combined=
  `2d19a12ce90d85b0838a53f6efdcf8454d36c7e5c242625c78802c2792ac4fa9`；下一步只允许
  Pascal/Confucius 对该哈希从零只读复审，任一 finding 都使本轮 target 失效。

## 19. Batch 2026-07-16-018：canonical Round 10 同哈希双 PASS

- Pascal / lean-directness=`PASS`、Confucius / compatibility-safety=`PASS`；双方独立按父计划 §9
  复算同一 combined=
  `2d19a12ce90d85b0838a53f6efdcf8454d36c7e5c242625c78802c2792ac4fa9`，findings=`none`。
- 起止 HEAD/status 与六文件逐文件摘要一致，formal target 无漂移；双方均确认 child spec 已只引用
  父 canonical recipe，旧 dual-algorithm finding 闭环。
- 双方意见统一：四行产品/110 行测试预算、授权与异常顺序、测试隔离、回滚、fresh-main 和 GAP-13
  分流合同充分且直接；旧 `6a661...`/`688294...` verdict 继续退役。
- 动态回执落盘后的终态复验已完成：constraints no BLOCKER；truth ready/fresh、inventory
  `1091/1091`、unmapped/missing=`0/0`；validate PASS；root exact=`PASS`；diff-check PASS。运行耗时只保留
  在原始命令输出，不作为动态回执身份字段。
  已知 GAP-12 Cursor 非目标刷新已精确恢复。下一步可 amend/push PR #140，并恢复 current-head
  review/check heartbeat。

## 20. Batch 2026-07-16-019：Codex P2 与 Round 10 退役

- PR #140 current HEAD `e14dd07b` 的 Codex review 指出：T31 标记“已完成”，但其验收要求
  implementation worktree 基于 formal merge main，且同一状态又说明 PR #139 仍待 rebase。
- finding 有效：该矛盾可能让 implementation 从旧 formal baseline 提前推进。最小修订只把 T31 改为
  “部分完成”，并明确 T25 完成及 formal merge 后 rebase 前不得 completed；实现边界与产品预算不变。
- `tasks.md` 属于 formal target，Round 10 `2d19a12c...4fa9` 双 PASS 同时退役。重跑终态门禁后冻结
  Round 11 新 combined，Pascal/Confucius 必须从零复审。

## 21. Batch 2026-07-16-020：Round 11 terminal gates 与冻结

- canonical combined=
  `46b63b1c923a5d382bd38650157dd04e7ffb4f8720e68b136057a8738fdc2efb`。
- constraints no BLOCKER；truth ready/fresh、inventory `1091/1091`、unmapped/missing=`0/0`；validate
  PASS；root exact=`PASS`；diff-check PASS。已知 GAP-12 Cursor 非目标刷新已精确恢复。
- 下一步只允许 Pascal/Confucius 对该同一 combined 从零只读复审；任一 formal 变化使双方 verdict
  同时失效。

## 22. Batch 2026-07-16-021：Round 11 同哈希双 PASS

- Pascal / lean-directness=`PASS`、Confucius / compatibility-safety=`PASS`；双方独立按父计划 §9
  复算同一 combined=
  `46b63b1c923a5d382bd38650157dd04e7ffb4f8720e68b136057a8738fdc2efb`，findings=`none`。
- 起止 formal 摘要、HEAD/tree/status 一致，target 无漂移；双方确认 T31 生命周期依赖、四行产品预算、
  测试/授权/异常/回退/fresh-main 与 WI208 分流合同一致且未提前完成。
- 动态 PASS receipt 落盘后的 final gates 已全绿：constraints no BLOCKER；truth ready/fresh、inventory
  `1091/1091`、unmapped/missing=`0/0`；validate PASS；root exact=`PASS`；diff-check PASS；已知 GAP-12
  Cursor 非目标刷新已精确恢复。下一步更新 PR #140 current HEAD；formal merge 前不恢复 PR #139。
