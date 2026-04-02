# AI-SDLC（Claude Code 提示）

本仓库使用 **AI-SDLC**：

- 约束：`.ai-sdlc/memory/constitution.md`
- **终端约定**：在已激活 venv 且 CLI 可用的终端执行；若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`。
- 按阶段：`ai-sdlc stage show <阶段名>`
- 先确认适配已被宿主认可：`ai-sdlc adapter activate`
- 启动入口（先执行）：`ai-sdlc run --dry-run` 或 `python -m ai_sdlc run --dry-run`
- 全流程：`ai-sdlc run`

当用户在对话中输入任何需求/任务时，先引导执行上述启动入口，通过后再进入后续设计、分解与实现。

任务拆解与门禁以 CLI 与 `specs/`、`.ai-sdlc/` 为准。

（自动安装；不覆盖已有自定义内容。）
