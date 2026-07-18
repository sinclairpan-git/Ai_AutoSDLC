# 开发摘要：YAML quoted-scalar comment-policy 精确识别

**功能编号**：`209-yaml-quoted-scalar-comment-policy`
**状态**：implementation adversarial review；formal PR #145/merge `46156c24` 已完成；Round 8 findings 修订中

## 当前结论

GAP-14 是验证可靠性缺陷，不是减重成果。实现已限定在 `comment_policy.py`，用 old/new hunk 行号、
受信路径与 PyYAML quoted token span 消除 single/double quoted multiline scalar 的 `#...` 误报，
同时保持真实注释、删除文件、malformed path/header 与 added-side fail-closed 合同。

Round 8 产品修复与回放证据通过，但双审发现 canonical delete+added 用例被压缩掉，以及 child/parent
lifecycle、execution receipt 和 handoff 与实现事实不同步。当前只修复这些证据缺口，不扩展产品范围。

## 冻结方向

- 保持零上下文 diff；独立解析 old/new path 与 hunk 行号，覆盖 mixed-extension rename、Git quoted path 和标准边界。
- 工作树 YAML 逐组件 no-follow/lstat + root containment；token end column 后忽略后续 quoted intervals，
  仍保留 flow tokens 后的真实 comment。
- removed YAML 不可信时继续报告；added YAML 不可信时不得充当 replacement；非 YAML 保持旧行为。
- 基线 `256/134/1799`；预算产品净新增 ≤130、两个测试文件合计 ≤200，三文件 raw/Ruff-normalized
  同集计算，新增文件/公共抽象均为 0。

## 交付边界

formal PR #145 已以产品代码零差异合并；独立 implementation 分支已完成 RED/GREEN、full 与回放，
当前仍处于双审 finding 修订。只有新身份双 PASS、implementation PR/Codex/checks/merge 与 fresh-main
全部完成后才能关闭 GAP-14/T57，并恢复下一原子减重候选。
