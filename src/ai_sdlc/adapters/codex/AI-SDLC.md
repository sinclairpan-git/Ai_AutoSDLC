# AI-SDLC（Codex / OpenAI Codex CLI 提示）

本工程使用 **AI-SDLC** 自动化流水线。

- 宪章：`.ai-sdlc/memory/constitution.md`
- **终端约定**：引导用户在已配置好的终端（venv 已激活、`ai-sdlc` 在 PATH）中执行；Codex 对话环境未必继承该 PATH。若裸命令不可用，使用 `python -m ai_sdlc ...`。
- 分阶段清单：`ai-sdlc stage show <阶段名>`
- 先记录当前 adapter 的人工确认：`ai-sdlc adapter activate`（会写成 `acknowledged`，不是可验证的治理激活）
- 启动入口（先执行）：`ai-sdlc run --dry-run` 或 `python -m ai_sdlc run --dry-run`（安全预演；不证明治理激活）
- 全流程执行：`ai-sdlc run`

当前 Codex adapter 仍是 Markdown / 文件提示面。除非后续接入可核验的宿主握手，否则治理侧都应按 `soft_prompt_only` 理解，而不是“宿主已验证激活”。

当用户在聊天中输入任何需求/任务描述时，优先引导并先执行上述启动入口（两种写法择一，以用户终端能成功为准）。`run --dry-run` 通过后只表示 CLI 预演成功，再进入细化、分解与实现；它本身不构成治理激活证明。

请在修改 `specs/` 与 `.ai-sdlc/` 下文档时遵守上述入口。

（自动安装；不覆盖已有同名自定义文件。）
