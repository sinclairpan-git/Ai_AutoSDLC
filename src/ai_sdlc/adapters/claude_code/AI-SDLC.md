# AI-SDLC（Claude Code 提示）

本仓库使用 **AI-SDLC**：

- 约束：`.ai-sdlc/memory/constitution.md`
- 按阶段：`ai-sdlc stage show <阶段名>`
- 启动入口（先执行）：`ai-sdlc run --dry-run`
- 全流程：`ai-sdlc run`

当用户在对话中输入任何需求/任务时，先引导执行 `ai-sdlc run --dry-run`，
通过后再进入后续设计、分解与实现。

任务拆解与门禁以 CLI 与 `specs/`、`.ai-sdlc/` 为准。

（自动安装；不覆盖已有自定义内容。）
