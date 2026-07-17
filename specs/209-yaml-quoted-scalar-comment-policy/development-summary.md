# 开发摘要：YAML quoted-scalar comment-policy 精确识别

**功能编号**：`209-yaml-quoted-scalar-comment-policy`
**状态**：formal ready；Round 5 双对抗 PASS，formal PR delivery in progress；implementation 未开始

## 当前结论

GAP-14 是验证可靠性缺陷，不是减重成果。基线仅按 diff 行前缀判断，single/double quoted multiline
scalar 的 `#...` 内容均被误报。只读 spike 证明现有 PyYAML scanner 可提供准确的 quoted token 行范围。

## 冻结方向

- 保持零上下文 diff；独立解析 old/new path 与 hunk 行号，覆盖 mixed-extension rename、Git quoted path 和标准边界。
- 工作树 YAML 逐组件 no-follow/lstat + root containment；token end column 后忽略后续 quoted intervals，
  仍保留 flow tokens 后的真实 comment。
- removed YAML 不可信时继续报告；added YAML 不可信时不得充当 replacement；非 YAML 保持旧行为。
- 基线 `256/134/1799`；预算产品净新增 ≤130、两个测试文件合计 ≤200，三文件 raw/Ruff-normalized
  同集计算，新增文件/公共抽象均为 0。

## 交付边界

formal PR 只允许文档、manifest/project-state、root exact inventory/close 和 continuity；产品代码零差异。
formal 双审/PR/merge 后才创建独立 implementation 分支。实现须经 RED/GREEN、full、回退、双审、
Codex/checks、merge 与 fresh-main，之后才能关闭 GAP-14/T57 并恢复下一原子减重候选。
