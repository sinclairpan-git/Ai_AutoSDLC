# AI-SDLC（Codex / OpenAI Codex CLI 提示）

本工程使用 **AI-SDLC** 自动化流水线。

- 宪章：`.ai-sdlc/memory/constitution.md`
- 分阶段清单：`ai-sdlc stage show <阶段名>`
- 启动入口（先执行）：`ai-sdlc run --dry-run`
- 全流程执行：`ai-sdlc run`

当用户在聊天中输入任何需求/任务描述时，优先引导并先执行：
`ai-sdlc run --dry-run`
通过后再进入细化、分解与实现。

请在修改 `specs/` 与 `.ai-sdlc/` 下文档时遵守上述入口。

（自动安装；不覆盖已有同名自定义文件。）
