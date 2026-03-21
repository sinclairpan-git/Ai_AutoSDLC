---
description: "AI-Native SDLC 全自动流水线（Cursor 适配器）"
---

读取并严格遵循 `.ai-sdlc/autopilot.md` 中的全部指令执行流水线。
读取 `.ai-sdlc/rules/` 目录下的所有 `.md` 文件作为行为约束。

用户输入的 PRD：

```text
$ARGUMENTS
```

如果 `$ARGUMENTS` 为空，停止并提示用户提供 PRD 内容或文件路径。
