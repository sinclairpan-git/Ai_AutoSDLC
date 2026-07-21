# 执行日志：ProgramService artifact loader 精确重复族减重

**功能编号**：`217-programservice-artifact-loader-dedupe`
**状态**：implementation local gates passed / final review pending
**基线**：formal merge `4e4971d4625b5cf7f3381653bb6288a95fb4aa54`

## 1. 归档规则

- 本文件按批次追加 observed facts；不预写未来 commit、review、check 或 merge 成功。
- Product/proof/RC 账本使用 raw Git additions/deletions；AST physical/branch 另列，二者不得混用。
- 每个 reviewer verdict 绑定 exact committed+clean HEAD/tree/formal-six；任何 tracked change 使双方失效。
- formatter-polluted、未纳入最终候选的 worktree 不得作为 RC-06 或净删证据。
- formal、implementation、closure 使用独立 branch/PR；失败状态保持 fail-closed。

## 2. Batch 2026-07-21-001：fresh-main candidate scan

- WI216 reconciliation 已由 PR #166 squash merge=`b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`，detached
  fresh-main acceptance 全绿；因此 replacement candidate 允许从该 SHA 重新选择。
- `src/ai_sdlc/core/program_service.py` 为17,474 physical LOC；AST/文本扫描定位13个同形
  `_load_frontend_*payload`，自然 family=403 physical / branch39。
- 12 个普通 loader 各一个 service caller；cleanup loader 六个 caller。除上述18个内部callsite外，其他
  产品/测试consumer=0；历史specs命中只作记录。
- Option A 最初保留13 wrappers，被 LEAN 以 RC-06 product+proof 合并预算冲突拒绝；修订为12 direct
  binding + cleanup-only wrapper。
- Round 2 LEAN通过，但 SAFETY拒绝20行 proof，要求完整 caller-label 与四态矩阵。控制器没有降低证明面，
  转入 bounded spike 实测。

## 3. Batch 2026-07-21-002：spike 污染发现与排除

- 第一棵 uncommitted spike 在语义补丁后曾得到 product=`+48/-406`，但随后误运行 write-mode Ruff formatter，
  当前 diff 扩大为 `+1103/-924`。SAFETY R3据此拒绝账本。
- 该 finding 成立。第一棵 spike 被明确标为 `excluded_formatter_pollution`：不提交、不推送、不参与 formal
  ledger、review 或实现继承。
- 新建 clean spike branch=`codex/spike/217-artifact-loader-budget-clean`，base exact=`b4d2ce5a`；通过
  apply-patch 重建最小语义 diff，不运行 formatter。

## 4. Batch 2026-07-21-003：clean spike 与统一 option PASS

- Clean current diff 只含两个文件：

  ```text
  48  406  src/ai_sdlc/core/program_service.py
  48    0  tests/unit/test_program_service.py
  ```

- AST terminal：common helper=`33 LOC / branch3`；cleanup wrapper=`11/1`；合计=`44/4`。
- Option-review时的initial proof=12 caller-label +4 loader states，共16 cases：
  `16 passed, 406 deselected`；该proof后来由§7加强并取代。
- Initial完整 `tests/unit/test_program_service.py`：`422 passed in 37.87s`；Ruff check与
  `git diff --check` PASS；当前proof结果以§7为准。
- RC-05=`48≤60`；canonical truth sync实际三行后，RC-06=`48+48+3=99≤floor(406×25%)=101`，
  buffer=2；product net=-358；product+proof+truth net=-307。
- Round 4 exact clean evidence：Pascal/LEAN=`APPROVE A/findings=0`；Confucius/SAFETY=
  `APPROVE A/findings=0`。双方共同选择 common helper +12 direct binding +cleanup-only wrapper，并拒绝
  wrapper保留和builder-family扩张。

## 5. Batch 2026-07-21-004：formal branch 初始化

- 从 fresh-main 创建隔离 formal branch，按 repository workitem gate 改名为
  `feature/217-programservice-artifact-loader-dedupe-docs`。
- `uv run ai-sdlc workitem init --wi-id 217-programservice-artifact-loader-dedupe ...` 创建 canonical
  spec/plan/tasks/log、manifest source mapping，并把 `next_work_item_seq` 推进到218。
- Init 同时刷新了既有 Cursor adapter；该 adapter diff 不属于本候选，已用 HEAD exact content 恢复，formal
  scope 中 `.cursor/**` 必须保持零差异。
- Fresh-main pre-authoring baseline：`tests/unit/test_program_service.py`=`406 passed in 35.83s`。
- 当前只进入 formal authoring；product spike 未复制、提交或继承到本 branch。下一硬门是 formal source
  commit、truth sync、同 identity LEAN/SAFETY PASS0、formal PR/checks/merge/fresh-main。

## 6. Batch 2026-07-21-005：Formal Round 1 FAIL3

- Review identity=`45761e2225635aa3c31fd0a95409907f2ec12977` / tree=
  `7e91d433dcef7c64389765218abb06d48f207360` / formal-six=
  `7ad72b08f01c12f26b4dfc16719a230401d8db290d83d061f28d4f8c77e0a19b`，worktree clean。
- Pascal/LEAN=`FAIL2`：spec把18个已知内部caller与“无consumer”写成矛盾；产品/runtime `getattr`禁令
  又误伤plan中的test-only source inspection。
- Confucius/SAFETY=`FAIL1`：formal提前物化child `development-summary.md`并预期close=`216/216`，违反父
  pre-close唯一missing合同，等同伪造完成。
- 三项finding全部成立。最小修复：consumer改为“18个内部callsite之外为0”；禁令限定产品/runtime并
  显式允许T61A test-only inspection；删除WI217 summary，truth目标改为inventory
  `complete 1136/1136`、missing/unmapped=`1/0`、close=`216/215`，closure才物化summary恢复`216/216`。
- 修复改变formal-six与HEAD/tree，Round 1全部verdict失效；提交新clean identity后双方完整复审。

## 7. Batch 2026-07-21-006：Formal Round 2 FAIL2 与 proof 加强

- Review identity=`70df5d92c8258694fc09465e0f68edba19b08c93` / tree=
  `bbfba83d009bcc5a57eb69da1577f01e6a636b16` / formal-six=
  `5891f4030d7d1da56aafa23743bd8f01b2858770dcc2de0b1dcc5c139b6f57b9`，worktree clean。
- Pascal/LEAN=`FAIL1`：本log仍遗留裸`consumer=0`，已改为“18个内部callsite之外为0”。
- Confucius/SAFETY=`FAIL1`：旧proof没有冻结read failure、root外absolute path，也没有在legacy上先捕获
  representative baseline。
- Proof在48 raw LOC硬预算内重构：一个binding case内部逐项断言12对；persistent provider-runtime
  representative在legacy/common helper间切换，同一断言覆盖root外path的missing、invalid YAML、
  non-mapping、valid与directory read failure五态。
- 独立legacy RED worktree实跑=`1 binding failed, 5 behavior passed, 406 deselected`；clean candidate=
  `6 passed, 406 deselected`，full ProgramService=`412 passed in 34.28s`，Ruff PASS。Test additions仍=48；
  product仍`+48/-406`；当时formal reserve按2行记录，implementation canonical truth实测后由§15纠正为99/101。
- 修复改变formal-six与HEAD/tree，Round 2全部verdict失效；新clean identity必须双方完整复审。

## 8. Batch 2026-07-21-007：Formal Round 3 FAIL2 同源修正

- Review identity=`3510fce941953b00f2156061a0d89ed5e7163592` / tree=
  `2342bd22dcca6396482e8c26f419d97d044eda10` / formal-six=
  `1db59fc294ac4e45eac57d42f2587142f5aa149309abb6b3f9276120d2d85c39`，worktree clean。
- Pascal/LEAN=`FAIL1`、Confucius/SAFETY=`FAIL1`，两者指出同一矛盾：atomic revert恢复fresh-main exact
  code/test blobs后，新增proof已经不存在，不能同时要求在revert状态取得legacy 5 GREEN/1 RED。
- 最小修正把5 behavior GREEN/1 binding RED只绑定T61A独立proof-red worktree；disposable clone revert只验
  exact baseline code/test blobs与406 baseline unit，reapply再验exact candidate blobs、6 proof与412 unit。
- 修正改变formal-six与HEAD/tree，Round 3全部verdict失效；提交新clean identity后双方完整复审。

## 9. Batch 2026-07-21-008：Formal Round 4 handoff 时态修正

- Review identity=`dd2287fdfa57023bb3c5116a4659696c018e9c07` / tree=
  `a53f310b9e5d537610dff0468c6f74cffbbbff46` / formal-six=
  `856e7819ed10515db61387933a59a75178985fc1d63691be722739c18e02a669`，worktree clean。
- Pascal/LEAN=`FAIL1`：root/scoped handoff在source commit后仍称“等待提交”，下一步又要求重复提交；
  Confucius/SAFETY=`PASS0/findings=0`。
- Finding成立；两份handoff改成不依赖未来commit号的稳定状态：formal source已提交，下一步只要求对当前
  committed+clean identity双审。修正改变HEAD/tree但不改变formal-six、产品、预算或行为合同。
- Round 4两个verdict均失效；新clean identity必须由双方完整复审。

## 10. Batch 2026-07-21-009：用户冻结减重路线终局

- 用户明确指定 WI217 是本轮减重专项最后一个 work item；当前 formal 完成后至多一个
  implementation PR 和一个 closure PR，禁止新的减重 work item。
- 用户说明终止原因：专项接近7天仍不知道何时结束，减重效果不透明，持续大量消耗token并影响正常
  特性开发；没有新特性的AI-SDLC只追求减重没有产品意义，减重必须与特性交付均衡。
- 控制器复算已有family ledger产品raw净删653行约占初始107,482行基线0.61%；WI217若GO累计1,011行
  约0.94%。该比例是路线ROI粗算，不伪装为全仓精确净变化。
- GO 路径登记真实净删；NO-GO 路径登记零产品合入且不保留候选。两条路径都由唯一 closure PR
  关闭 WI217/WI196，把 RC-08 记为 `retired_unrealistic_composite_target`，并把剩余结构债转为
  `non_blocking_backlog`，随后恢复正常特性开发。
- 该方向改变了 PR #167 已审 identity 的终态合同，R7 LEAN/SAFETY PASS0、已触发 CI 与 Codex 👀均退役；
  formal 文档、truth、同身份双审和 PR current HEAD 必须重做。本变更不授权版本发布。

## 11. Batch 2026-07-21-010：终局合同 R1/R2 remediation

- 控制器首次把 formal-six 错算为 path-first 行格式；LEAN/SAFETY均独立复算 canonical
  `<sha><two spaces><path>` 为 `c144c69d...70c1`，错误 identity verdict 全部失效，文件未因该错误变化。
- 正确 identity R2：LEAN FAIL1指出handoff会重复提交已完成source；SAFETY FAIL3指出post-merge fresh-main
  失败无合法回退、parent summary仍称独立WI持续推进，以及同一handoff时态问题。
- 修复后唯一closure通常records-only；若implementation已合并后fresh-main失败，则在该closure内精确恢复
  pre-implementation product/proof blobs并登记最终零产品净变化，不新开rollback/implementation PR。
- Parent summary改为只允许WI217当前路线；handoff记录source已提交；“禁止gap/reduction WI”收窄为只禁止
  新减重WI，不阻断正常特性/缺陷工作。修复改变HEAD/tree/formal-six，R2双方verdict失效。

## 12. Batch 2026-07-21-011：terminal formal 双审、合并与 fresh-main

- Source R3 identity=`26d11c44dc63bc239423aec7981f3a6eb1804451` / tree=
  `0b3e9034fac2396c52200009db658ad8e14dd7c5` / formal-six=
  `40c6d928ecd2d903b44cb41e15372e6f8c80d5d378605144fd86286a3e0506a4`，LEAN/SAFETY均
  `PASS0/findings=0`。Truth sync与handoff完成后的最终 review identity=
  `588b3727e768bb2ed67a119535bc9093ef355217` / tree=
  `4e423c93806b7c8966c1496baedf7dc4ae05b760` /同一formal-six，双方R4均`PASS0/findings=0`。
- PR #167 current-head Codex review审到`588b3727e7`并报告无major issues；12项required checks全绿，
  squash merge=`4e4971d4625b5cf7f3381653bb6288a95fb4aa54`，本地formal branch保留。
- Detached fresh-main tree=`4e423c93806b7c8966c1496baedf7dc4ae05b760`与reviewed tree精确相同；manifest exact=
  `1 passed in 121.32s`，constraints无BLOCKER，validate PASS，truth=`ready/fresh`、mapped=
  `1136/1136`、missing/unmapped=`1/0`、close=`216/215`，handoff parity/diff-check/clean均PASS。

## 13. Batch 2026-07-21-012：正式 TDD RED/GREEN 与原子候选

- 从formal detached fresh-main创建唯一implementation branch=
  `feature/217-programservice-artifact-loader-dedupe`。两个目标文件相对旧spike base与fresh-main blob精确相同，
  product baseline=`7b2ac50725136b6399b74e898f147a0b1fecd9c6`，test baseline=
  `735b505f72c4f2cfb1a378397e4f15faa79ed219`；fresh-main ProgramService=`406 passed in 33.43s`。
- Proof-only RED在未改产品时精确为`1 failed, 5 passed, 406 deselected in 1.28s`；失败只来自12个caller
  尚无exact `artifact_label`，五个payload/error行为全部保持GREEN。
- 最小GREEN实现只含一个33 LOC/branch3 private helper、12个direct exact label binding与11 LOC/branch1
  cleanup wrapper；没有新模块、public API、dependency、registry/reflection/DSL/getattr/type erasure、第二family
  或formatter churn。Proof=`6 passed, 406 deselected`，ProgramService=`412 passed in 30.06s`，Ruff与
  diff-check PASS。
- Atomic candidate commit=`e2752a9b4b8572f828433c4c3fb57cac4a26f0f9` / tree=
  `dbf9fc1415414b4cb97693a7dc9f8a1c976df115`；只含product/proof两个文件。Candidate blobs为product=
  `77827e018ae192e1d33d739310c0c7754309d7a2`、proof=
  `549de823045985161a6c4b2b9a9e2f3e4d1b8a51`；raw ledger product=`+48/-406/net -358`、proof=`+48`、
  combined含canonical truth三行=`99/101`，与clean spike两个product/proof文件逐字相同。

## 14. Batch 2026-07-21-013：完整门禁、基线对照与 rollback/reapply

- CLI program integration=`233 passed in 23.39s`。首次本机full在默认超长pytest临时路径下得到
  `3308 passed, 3 skipped, 1 failed`；唯一失败是enterprise-profile错误信息把`does not exist`在Rich终端
  宽度处换行。候选与未改fresh-main单测都以相同输出失败；分别使用短`--basetemp`后均`1 passed`，证明
  该失败是环境路径包装而非candidate regression。固定`--basetemp=/tmp/wi217-full`后的完整套件=
  `3309 passed, 3 skipped in 807.92s`。
- Constraints无BLOCKER、program validate PASS、truth audit=`ready/fresh`、inventory=`1136/1136`、
  missing/unmapped=`1/0`、close=`216/215`。Wheel/sdist均成功构建；wheel在全新Python 3.14 venv安装后
  `ai-sdlc --version`=`0.9.6`、`--help` exit0。Windows/macOS/Linux与POSIX/Windows offline smoke仍必须
  由implementation PR required checks确认，不在本地伪造跨平台通过。
- Disposable local clone revert commit=`1c66df02a74132b3f522eaf82a5c5aa887fc3c00`，两个blob精确恢复baseline，
  `406 passed in 37.12s`；reapply commit=`f785f43b733a0c4f2d4e0cef44cb28f36653e52f`，两个blob精确恢复candidate，
  proof=`6 passed`、ProgramService=`412 passed in 33.26s`、Ruff PASS。临时clone未推送；legacy RED只绑定
  proof-first worktree，不错误声称atomic revert后仍存在新增proof。

## 15. Batch 2026-07-21-014：Implementation Final Round 1 ledger FAIL1

- Review identity=`1d4d0bf701e4dc42d5ea5b5ea390db437869bc0e` / tree=
  `fb28126dcdca8ec88f9bbd938dd9c2d42d5edcde` / formal-six=
  `fd8d29d0a2bc96d3ab644bed536b888c0515990a6aaed024b26a2d49208683a0`，worktree clean。
- SAFETY=`PASS0/findings=0`；LEAN=`FAIL1`。唯一P2成立：canonical truth sync实际替换
  `generated_at`、`repo_revision`、`snapshot_hash`三行，旧账本却按truth≤2记录98/101，低报1行。
- 控制器先在隔离clone测试更严格的truth=0方案：恢复formal fresh-main manifest后truth audit明确
  `stale/blocked`，因此不得删除canonical snapshot diff。最小修正按真实三行计费为
  `48 product + 48 proof + 3 truth = 99/101`、buffer=2、路线累计≤283/1500；combined硬上限101不放宽。
- 修正只改现有records/handoff，不改atomic candidate、product/proof blobs、测试、package或rollback receipt。
  Round 1两份verdict均失效；truth重新sync、治理门禁和同identity双审必须从零执行。

## 16. Batch 2026-07-21-015：Implementation PR Windows proof portability remediation

- Corrected final identity=`8919cbc04aa7afe9ec5a6f202119f5d3063ec37e` / tree=
  `2ba38e808a3055575ea797241e334c7aeb5fb3ce` / formal-six=
  `182edb5e75139c0070231e8bb3fbf8648cb6d60bbfaa4b7fcc9e4ee97940fe77`，LEAN/SAFETY Round 2均
  `PASS0/findings=0`。唯一implementation PR #168已创建；Codex审到该commit并报告无major issues。
- Required CI中19项先通过；Windows Python 3.11/3.12 full pytest分别在约21/20分钟后失败。两者均只有
  新增proof的四个case失败：产品保持既有`_relative_to_root_or_str(...).as_posix()`正斜杠合同，proof却用
  `Path.__str__()`在Windows构造反斜杠期望；3.11汇总=`4 failed, 3304 passed, 4 skipped`，不是产品回归。
- 最小修复只把该proof期望路径改为`artifact_path.as_posix()`；产品、public API、依赖、结构与行数账本
  均不变化。修复后focused proof=`6 passed, 406 deselected`，Ruff与diff-check通过。
- 本tracked修复使旧HEAD的Codex结论、CI与LEAN/SAFETY verdict全部失效。必须在同一PR完成本地门禁、
  truth/handoff、同一新identity双审，再只触发一次current-head Codex review与required CI。

## 17. Batch 2026-07-21-016：Final Round 3 FAIL2 与 portable atomic candidate refresh

- R3 review identity=`8b0850f03ae876ea73ac5b74f31452f2310321a0` / tree=
  `c1919a111643d0f6382e7b22926a39dc6ff409ef` / formal-six=
  `182edb5e75139c0070231e8bb3fbf8648cb6d60bbfaa4b7fcc9e4ee97940fe77`；LEAN/SAFETY均`FAIL2`且
  独立指出相同两项：旧T24 receipt只覆盖pre-portability proof blob，无法回退当前pair；handoff下一步重复
  已完成动作，且把canonical close=`216/215`倒写成`215/216`。
- 为保持最终产品树不变且重新建立可独立回退的原子边界，先用commit=`9f4d3e47`把product/proof精确恢复
  fresh-main blobs，再以新atomic candidate=`eb8dc0f8bc726816e97cd5bb0f027e35216651c0`一次提交当前portable
  pair。该commit仍严格为product=`+48/-406`、proof=`+48/0`；最终product blob=
  `77827e018ae192e1d33d739310c0c7754309d7a2`、proof blob=
  `25ef1acdd616f89b001b96973ced37fdf5f073ff`，与已通过full gate的最终blobs一致。
- 新disposable clone=`/tmp/wi217-rollback-reapply-r3`，未推送。Revert commit=
  `12d9bd5eafcfecb3be881ec4110430b75bc4e9b7`，精确恢复baseline product=
  `7b2ac50725136b6399b74e898f147a0b1fecd9c6`、proof=
  `735b505f72c4f2cfb1a378397e4f15faa79ed219`，ProgramService=`406 passed in 31.56s`。
  Reapply commit=`ef04298e2187e4a9d37c49417674d206610f2271`，精确恢复当前两个candidate blobs，
  focused proof=`6 passed`、ProgramService=`412 passed in 28.28s`、Ruff PASS、clone clean。
- 由于最终product/proof blobs未从R3 full gate后变化，`3309 passed, 3 skipped`与package/CLI证据继续精确
  绑定同一代码内容；不重复运行昂贵full。Records/truth/handoff提交后必须以新clean identity从零双审。
