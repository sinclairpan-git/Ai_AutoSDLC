# 任务分解：YAML quoted-scalar comment-policy 精确识别

**编号**：`209-yaml-quoted-scalar-comment-policy` | **父任务**：GAP-14 / T57
**规则**：每批单独提交；formal、implementation、acceptance 使用独立分支/PR；内容变化使双 PASS 失效。

## Batch 1：formal truth

### T11 初始化与基线复现（completed）

- **依赖**：WI208 closure PR #144 已合并为 `85bdedac`。
- **文件**：child 五件套、project-state、program manifest、root exact test。
- **验收**：WI209 路径唯一；baseline revision/LOC、single/double 当前 1 finding 和 PyYAML token span 有可执行证据。
- **验证**：只读 Python spike、`git diff --check`、路径白名单。

### T12 冻结 NC/CC、设计和对抗评审（completed）

- **依赖**：T11。
- **验收**：FR/SC/矩阵、old/new path/line、分侧 fail-closed、预算、停止/回退均闭合；Pascal 与 Confucius 按父计划 §9 唯一 recipe，对父/子各 `spec+plan+tasks` 六文件同一 combined hash 均 PASS。
- **停止**：任一 reviewer 有 finding 时修正文档、重算哈希并重开两位评审，直到一致 PASS。

### T13 formal 治理、PR 与合并（completed）

- **依赖**：T12 双 PASS。
- **验收**：父 GAP-14/T57 标为 formal ready；manifest truth `ready/fresh`，root exact、constraints、validate、diff-check 通过；formal PR current-head Codex clean 且 checks 全绿后合并。
- **非目标**：`src/ai_sdlc/` 零差异；除 root exact inventory/close 数值外测试零差异。
- **证据**：formal PR #145 已合并为 `46156c24def705ecd12981d13ca1988d061a4fc7`；implementation 分支从该 merge 独立创建。

## Batch 2：TDD 与最小实现

### T21 提交真实 RED characterization（completed）

- **依赖**：T13 formal merge；从新 main 创建独立 implementation 分支。
- **文件**：`tests/unit/test_comment_policy.py`、`tests/integration/test_cli_verify_constraints.py`。
- **验收**：single/double removed continuation 至少一个参数化 node 在基线失败；added quoted/不可确认 YAML 内容不能替代真实 comment；CLI exit/text 已冻结。
- **验证**：记录精确 pytest node、失败断言和退出码；RED 只含测试。
- **证据**：`6438d589`；unit witness 3/3 RED，CLI witness 2 RED/1 PASS，产品文件零差异。

### T22 实现 path/syntax-aware GREEN（completed）

- **依赖**：T21。
- **文件**：`src/ai_sdlc/core/comment_policy.py`。
- **验收**：保留 `--unified=0`；old/new path/行号、HEAD/worktree sources、PyYAML quoted token span/end column 和分侧保守过滤生效。
- **验证**：RED nodes GREEN；`tests/unit/test_comment_policy.py` 全绿。
- **证据**：`e289057e` 起始 GREEN；后续同文件修订闭合 path/header/source trust findings，未新增产品文件或公共抽象。

### T23 安全矩阵与预算（completed）

- **依赖**：T22。
- **验收**：真实 YAML/Python/Markdown comments、plain/literal/folded、malformed、mixed-extension rename/quoted path、no-follow symlink/reparse/containment、标准 hunk 边界、closing flow suffix/escape、replacement reason 与 CLI exit/text 全部通过；以 `256/134/1799` 为 raw 基线，产品 ≤130、两测试合计 ≤200，三文件 Ruff-normalized 一致满足。
- **停止**：新增模块/公共抽象、预算超限或 blocker 文本变化即回到 T22/设计。
- **证据**：canonical delete+added real-comment 独立反事实已恢复并杀死错误回退 mutant；focused 98 PASS；产品 raw/normalized `+123/+130`、测试合计 `+198/+200`。
- **当前状态**：Round 9 真实 Git 空格路径 finding 已按原范围 GREEN，预算与范围复验通过。
- **GREEN**：Tab 终止单路径 grammar 恢复 old/new trust，双路径 header 仍 fail-closed；focused 100 PASS；产品 raw/normalized `+123/+130`、测试 `+200/+198`。
- **Round 11**：mixed Unicode+C-escape 真实 Git RED/GREEN；focused 100 PASS，产品 raw/normalized
  `+121/+128`、测试 `+200/+198`，安全矩阵与范围复验完成。

## Batch 3：终态证明

### T31 全量与治理门禁（completed）

- **依赖**：T23。
- **验收**：comment-policy、verify-constraints、full、Ruff、constraints、validate、truth、manifest、diff-check 全绿；full 前后 HEAD/tree、resume/handoff/status 无漂移。
- **证据**：Round 10 fresh full `3275 passed, 3 skipped in 703.77s`；Ruff/constraints/validate/diff-check PASS；truth sync/audit 为 `ready/fresh`、inventory `1101/1101`、layers `209/209`，manifest exact `1 passed in 97.46s`。
- **Round 11 证据**：fresh full `3275 passed, 3 skipped in 684.03s`；Ruff/diff-check、constraints、validate
  PASS；truth `ready/fresh 1101/1101 209/209`，manifest exact `1 passed in 101.56s`；base/candidate
  formatter parity 为同 exit 1、同三个批准文件。本 receipt 后在 T32 冻结前再次 terminal sync/audit/manifest。
- **Round 13**：Round 12 PR #146 Windows 3.11/3.12 full 各自仅失败 `test_yaml_quote_path_false`
  `WinError 123`；最小 test-only repair 后 node `1 passed`、unit `51 passed`、focused `100 passed`、full
  `3275 passed, 3 skipped in 623.84s`；初次 normalized 测试 `+201` 超限 1 行后，仅缩短 direct witness
  的非语义文件名并保留全部 escape 场景，最终 raw 产品/测试 `+121/+200`、normalized `+128/+198`；
  产品代码不变；pre-receipt truth/audit=`ready/fresh 1101/1101 209/209`、manifest exact
  `1 passed in 105.89s`，本 receipt 后只需 final sync/audit/manifest freeze。

### T32 回退演练和双对抗终审（completed）

- **依赖**：T31。
- **验收**：逐提交 revert 精确回到 formal merge tree、reapply 精确回到 candidate tree；Pascal/Confucius 对同一 final identity 均 PASS，无未处置 finding。
- **当前状态**：Round 8 replay tree 精确一致，但 Pascal 因测试覆盖稀释 FAIL，Confucius 因 canonical lifecycle 与 continuity receipt 失真 FAIL；两项均须修订后从零双审。
- **Round 9**：Pascal 对修订身份 PASS；Confucius 发现真实 Git 空格路径假 BLOCKER，verdict=FAIL；该身份退役。finding 已 RED/GREEN。
- **Round 10**：fresh full/terminal gates/replay 已完成，但 Pascal 因 parent plan、formatter contract、handoff
  Next FAIL，Confucius 因 mixed Unicode+C-escape 与 handoff Next FAIL；身份与 verdict 退役。
- **Round 11**：findings、fresh full、terminal truth/manifest 与独立 replay 完成；Confucius PASS、Pascal 因
  parent plan/child summary lifecycle 漂移 FAIL，身份与全部 verdict 退役。
- **Round 12**：canonical lifecycle 修订后，同一冻结身份 Pascal/Confucius 双 PASS；PR #146 Codex 对
  `2662309e80` 无 major issue。后续 Windows CI finding 与测试变更使身份和全部 verdict 退役。
- **Round 13**：产品实现不变；跨平台测试与 normalized 预算修复、T31、final truth/manifest/replay
  已完成；首个 post-handoff identity 因 canonical lifecycle receipt 仍称 freeze/replay 待执行而被
  Pascal/Confucius 双 FAIL，该身份退役。
- **Round 14**：canonical lifecycle 主体已闭合，产品/测试 blob 不变；Pascal/Confucius 唯一共同 P1 为
  T41 仍写“等待 Round 13 新 head”，可能把 PR gate 绑定退役身份，verdict 均为 FAIL。
- **Round 15**：只把 T41 绑定到评审调用提供的当前 Round 15 精确身份并记录 receipt；产品/测试 blob
  不变。candidate=`c5c6e94a`、replay=`abad54a6`，tree 均为 `adfc8503`；Pascal/Confucius 对同一身份
  均 PASS、无 finding，产品/测试 blob 与已通过 full 的身份相同。

## Batch 4：交付与关闭

### T41 implementation PR（completed）

- **依赖**：T32。
- **验收**：push/PR/@codex review/heartbeat；Codex 对 current HEAD clean、所有 required checks success 后 merge。
- **证据**：PR #146 的 Codex current-head review 审到 `c5c6e94adc` 且无 major issue；22/22 checks
  success，merge=`31aad572a61d9a0ca952fc8cd12923a5a1c9bbb5`。

### T42 fresh-main acceptance（completed）

- **依赖**：T41 merge。
- **验收**：fresh detached `origin/main` 复跑 focused/full/Ruff/constraints/truth/clean guard；父 GAP-14/T57 只在此后关闭，回退 implementation PR 会重开。
- **证据**：HEAD=`31aad572`；focused=`100 passed in 16.23s`，full=`3275 passed, 3 skipped in
  624.03s`；Ruff、constraints、program validate、truth `ready/fresh 1101/1101 209/209`、manifest exact
  `1 passed in 94.27s`、diff/clean guard 均通过，HEAD 与 `origin/main` 一致。

### T43 恢复下一原子减重选择（queued）

- **依赖**：T42 + 本 closure PR merge。
- **验收**：本 closure PR 合并后，只从 T63/T65/WP-06/WP-07 中按依赖/收益选择一个独立候选；
  不得把 WI209 计入 RC-08 减重。

## 追踪矩阵

| 合同 | 任务 |
|---|---|
| FR-209-01～08 | T21～T23 |
| FR-209-09～11 | T23、T31 |
| FR-209-12 | T13、T21、T41、T42 |
| NC-01～03 | T11、T12、T23 |
| NC-04～06 | T21、T31、T32、T42 |
| SC-209-01～04 | T23、T31 |
| SC-209-05～06 | T12、T32、T41、T42 |
