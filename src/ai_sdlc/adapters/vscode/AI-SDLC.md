# AI-SDLC（VS Code 工作区提示）

本仓库已启用 **AI-SDLC**。在 Copilot Chat / 终端中推进需求时：

- 先读 `.ai-sdlc/memory/constitution.md`。
- **终端约定**：在已激活、已安装 CLI 的 venv 终端中运行；若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`（等价）。
- 按阶段执行：终端运行 `ai-sdlc stage show <init|refine|design|decompose|verify|execute|close>` 查看当前阶段清单。
- 先确认适配已被宿主认可：`ai-sdlc adapter activate`。
- 启动入口（先执行）：`ai-sdlc run --dry-run` 或 `python -m ai_sdlc run --dry-run`。
- 全量门禁编排：`ai-sdlc run`。

当用户输入需求或任务时，先触发上述启动入口（按用户环境选用可执行写法），确认门禁后再继续后续阶段。

（本文件由 `ai-sdlc` 自动安装；若已存在且内容不同，不会被覆盖。）
