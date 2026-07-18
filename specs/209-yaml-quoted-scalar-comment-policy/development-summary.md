# 开发摘要：YAML quoted-scalar comment-policy 精确识别

**功能编号**：`209-yaml-quoted-scalar-comment-policy`
**状态**：implementation adversarial review；formal PR #145/merge `46156c24` 已完成；Round 10 双审 FAIL，Round 11 修订与 fresh verification 进行中

## 当前结论

GAP-14 是验证可靠性缺陷，不是减重成果。实现已限定在 `comment_policy.py`，用 old/new hunk 行号、
受信路径与 PyYAML quoted token span 消除 single/double quoted multiline scalar 的 `#...` 误报，
同时保持真实注释、删除文件、malformed path/header 与 added-side fail-closed 合同。

Round 8 产品修复与回放证据通过，但双审发现 canonical delete+added 用例被压缩掉，以及 child/parent
lifecycle、execution receipt 和 handoff 与实现事实不同步。两类 finding 已按原范围修订并重新通过
focused/full/预算门禁；GAP-14/T57 仍等待新身份双 PASS，不扩展产品范围。

Round 9 Pascal 已 PASS；Confucius 用真实 Git 证明含空格路径的歧义 `diff --git` header 虽正确失信，
但后续带终止 Tab 的单路径 `---/+++` header 也被同一 grammar 拒绝，导致 quoted scalar 假 BLOCKER。
修复只允许从该可消歧 header 恢复路径，不放宽双路径 header；默认 ASCII 空格与
`core.quotePath=false` 非 ASCII 空格真实 Git 回归均已 GREEN。

Round 10 fresh full 为 `3275 passed, 3 skipped`；Ruff、constraints、validate、diff-check、truth
`ready/fresh 1101/1101`、manifest exact 与 replay 均通过，但双审发现 mixed Unicode+C-escape、parent
plan lifecycle、formatter contract 与 continuity Next 四项问题，Round 10 身份和 verdict 已退役。

Round 11 用真实 Git RED/GREEN 覆盖 raw Unicode 与 Tab/newline/quote/backslash/space 混合路径，decoder
未新增 helper/文件，预算降为产品 raw/normalized `+121/+128`、测试 `+200/+198`。两份 plan 已同步
implementation lifecycle，并把 format 合同明确为 lint PASS + base/candidate formatter parity；fresh
focused `100 passed`、full `3275 passed, 3 skipped` 与治理门禁已通过，terminal replay 与双审仍待完成。

## 冻结方向

- 保持零上下文 diff；独立解析 old/new path 与 hunk 行号，覆盖 mixed-extension rename、Git quoted path 和标准边界。
- 工作树 YAML 逐组件 no-follow/lstat + root containment；token end column 后忽略后续 quoted intervals，
  仍保留 flow tokens 后的真实 comment。
- removed YAML 不可信时继续报告；added YAML 不可信时不得充当 replacement；非 YAML 保持旧行为。
- 基线 `256/134/1799`；预算产品净新增 ≤130、两个测试文件合计 ≤200，三文件 raw/Ruff-normalized
  同集计算，新增文件/公共抽象均为 0。

## 交付边界

formal PR #145 已以产品代码零差异合并；独立 implementation 分支正在完成 Round 11 fresh verification，
当前仍处于 implementation adversarial review。只有新身份双 PASS、implementation PR/Codex/checks/merge 与 fresh-main
全部完成后才能关闭 GAP-14/T57，并恢复下一原子减重候选。
