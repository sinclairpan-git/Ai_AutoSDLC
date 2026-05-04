# AI-SDLC（Claude Code 提示）

本仓库使用 **AI-SDLC**：

- 约束：`.ai-sdlc/memory/constitution.md`
- **终端约定**：优先使用用户已安装好的 `ai-sdlc`；若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`。不要要求普通用户手动安装 Python、venv、pip 或依赖，除非 CLI 明确报错并给出修复命令。
- 按阶段：`ai-sdlc stage show <阶段名>`
- 初始化入口（普通用户先执行）：`ai-sdlc init .` 或 `python -m ai_sdlc init .`
- `init` 会在用户选择 AI 代理入口和 shell 后自动执行必要检查与安全预演；正常输出会给出“当前结果 / Result”和“下一步 / Next”。
- 排查入口（仅当 CLI 明确要求时执行）：`ai-sdlc adapter status`、`ai-sdlc run --dry-run` 或对应 `python -m ai_sdlc ...` 写法。
- 全流程：`ai-sdlc run`

当前 Claude Code adapter 以 `.claude/CLAUDE.md` 作为 canonical path。治理侧以 `materialized / verified_loaded / degraded / unsupported` 为准；只有存在 machine-verifiable 证据时，才可视为 `verified_loaded`。

当用户在对话中输入任何需求/任务时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接进入后续设计、分解与实现。

任务拆解与门禁以 CLI 与 `specs/`、`.ai-sdlc/` 为准。

（自动安装；不覆盖已有自定义内容。）
