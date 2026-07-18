# 开发摘要：YAML quoted-scalar comment-policy 精确识别

**功能编号**：`209-yaml-quoted-scalar-comment-policy`
**状态**：implementation adversarial re-review；formal PR #145/merge `46156c24` 已完成；Round 12 双审/Codex clean 因 Windows fixture finding 退役；Round 13 预算、focused/full、final truth/manifest/replay 已通过；Round 13 首个 post-handoff 身份因 lifecycle receipt 滞后双 FAIL，Round 14 又因 T41 残留 Round 13 head 双 FAIL；Round 15 仅修 T41/receipt，等待新身份双审/current-head CI

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
implementation lifecycle，并把 format 合同明确为 lint PASS + base/candidate formatter parity；当时 fresh
focused `100 passed`、full `3275 passed, 3 skipped`、治理门禁与独立 replay 已通过，仅剩同一身份双审。

Round 12 同一冻结身份取得 Pascal/Confucius 双 PASS，PR #146 Codex 对 `2662309e80` 未发现 major issue；
21 项 checks 中 19 项成功，Windows Python 3.11/3.12 full 均只因测试夹具尝试创建含 quote/newline 的
非法 Windows 文件名失败。Round 13 不改产品：真实 Git 回归改用跨平台合法的 raw Unicode+space
路径，mixed raw Unicode+C-escape 改为直接验证既有 decoder；本地精确 node 与 51 个 unit 已 GREEN。
初次 Ruff-normalized 复算因 direct assert 展开而得到测试 `+201`，超预算 1 行；现仅把 witness 的
`file.yaml` 缩短为 `f`，Unicode/space/Tab/newline/quote/backslash 断言完整保留。最终 raw 产品/测试
`+121/+200`、normalized `+128/+198`，focused `100 passed in 12.72s`、full
`3275 passed, 3 skipped in 623.84s`；产品实现保持不变。final truth/audit=`ready/fresh`、inventory/
layers=`1101/1101`、`209/209`、missing/unmapped=`0/0`，manifest exact PASS；candidate `9f460a0d` 与
replay `8cb54228` tree 均为 `553434f5`，两端 clean。

Round 13 首个 post-handoff 身份的两位 reviewer 均未发现产品、安全、预算或覆盖问题，但共同发现
canonical lifecycle 与 handoff 仍把已完成的 final truth/replay 写成待执行/中间身份，verdict 均为 FAIL。
Round 14 修订 lifecycle/final receipt 后，双方确认上一轮 P1 主体已闭合，但唯一共同 P1 是 T41 仍写
“等待 Round 13 新 head”，可能让 PR gate 绑定退役身份，verdict 均为 FAIL。Round 15 仅把 T41 绑定到
评审调用提供的当前精确身份并记录 receipt；产品/测试 blob 不变，当前只剩同一身份双审与 current-head CI。

## 冻结方向

- 保持零上下文 diff；独立解析 old/new path 与 hunk 行号，覆盖 mixed-extension rename、Git quoted path 和标准边界。
- 工作树 YAML 逐组件 no-follow/lstat + root containment；token end column 后忽略后续 quoted intervals，
  仍保留 flow tokens 后的真实 comment。
- removed YAML 不可信时继续报告；added YAML 不可信时不得充当 replacement；非 YAML 保持旧行为。
- 基线 `256/134/1799`；预算产品净新增 ≤130、两个测试文件合计 ≤200，三文件 raw/Ruff-normalized
  同集计算，新增文件/公共抽象均为 0。

## 交付边界

formal PR #145 已以产品代码零差异合并；PR #146 保持打开。final truth/replay 已完成；Round 15 新身份
必须取得同一身份双 PASS、current-head Codex 和全平台 checks；merge 与 fresh-main 全部完成后才能
关闭 GAP-14/T57，并恢复下一原子减重候选。
