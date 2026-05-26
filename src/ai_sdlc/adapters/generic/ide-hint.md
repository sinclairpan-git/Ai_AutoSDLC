# IDE 适配说明

未检测到 Cursor / VS Code / Codex / Claude Code 的专用目录或环境标记；**框架仍可正常使用**。

请手动在所用 AI 助手中引用：

- `.ai-sdlc/memory/constitution.md`
- `ai-sdlc stage --help` 与 `ai-sdlc run --help`（若 `ai-sdlc` 不在 PATH，请用已安装该包的 Python：`python -m ai_sdlc ...`）

代码实现时，新增注释必须跟随当前或近期用户主要沟通语言；当前对话或近期对话以英文为主则使用英文，否则默认简体中文。保留原有注释；确需删除时，必须在同一变更附近补充等价说明，或在 execution log / handoff 记录删除原因。凡是后续 agent 或人工需要维护的脚本/模块，尤其包含认证、XHR/API 调用、payload 字段映射、加密、阶段流程、重试或副作用边界时，必须补维护契约、关键函数 docstring 或边界注释，并在验证/交付说明中确认这些注释已覆盖。

若之后添加 `.cursor/`、`.vscode/`、`.codex/` 或 `.claude/` 目录，下次执行任意 `ai-sdlc` 命令时会自动尝试补齐对应适配文件（不覆盖已有文件）。
