# 执行日志：ProgramService artifact loader 精确重复族减重

**功能编号**：`217-programservice-artifact-loader-dedupe`
**状态**：formal authoring
**基线**：`b4d2ce5a5bc27b72549dcdf394f277cfbd6a124d`

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
- RC-05=`48≤60`；RC-06=`48+48+truth≤2=98≤floor(406×25%)=101`，buffer≥3；product net=-358；
  product+proof+truth net≤-308。
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
  product仍`+48/-406`，RC-06仍98/101。
- 修复改变formal-six与HEAD/tree，Round 2全部verdict失效；新clean identity必须双方完整复审。
