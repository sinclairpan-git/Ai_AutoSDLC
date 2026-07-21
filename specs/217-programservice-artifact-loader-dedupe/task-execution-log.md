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
- 12 个普通 loader 各一个 service caller；cleanup loader 六个 caller。仓库代码/测试对13个私有名称的
  consumer=0；历史 specs 命中只作记录。
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
- 新 proof=12 caller-label +4 loader states，共16 cases：`16 passed, 406 deselected`。
- 完整 `tests/unit/test_program_service.py`：`422 passed in 37.87s`；Ruff check与`git diff --check` PASS。
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
