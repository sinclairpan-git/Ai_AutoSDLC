# IDE 适配说明

未检测到 Cursor / VS Code / Codex / Claude Code 的专用目录或环境标记；**框架仍可正常使用**。

请手动在所用 AI 助手中引用：

- `.ai-sdlc/memory/constitution.md`
- `ai-sdlc stage --help` 与 `ai-sdlc run --help`

若之后添加 `.cursor/`、`.vscode/`、`.codex/` 或 `.claude/` 目录，下次执行任意 `ai-sdlc` 命令时会自动尝试补齐对应适配文件（不覆盖已有文件）。
