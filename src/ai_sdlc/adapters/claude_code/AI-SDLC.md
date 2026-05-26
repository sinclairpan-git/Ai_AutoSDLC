# AI-SDLC（Claude Code 提示）

本仓库使用 **AI-SDLC**：

- 约束：`.ai-sdlc/memory/constitution.md`
- **终端约定**：优先使用用户已安装好的 `ai-sdlc`；若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`。不要要求普通用户手动安装 Python、venv、pip 或依赖，除非 CLI 明确报错并给出修复命令。
- 按阶段：`ai-sdlc stage show <阶段名>`
- 初始化入口（普通用户先执行）：`ai-sdlc init .` 或 `python -m ai_sdlc init .`
- `init` 会在用户选择 AI 代理入口和 shell 后自动执行必要检查与安全预演；正常输出会给出“当前结果 / Result”和“下一步 / Next”。
- 排查入口（仅当 CLI 明确要求时执行）：`ai-sdlc adapter status`、`ai-sdlc run --dry-run` 或对应 `python -m ai_sdlc ...` 写法。
- 全流程：`ai-sdlc run`

当前 Claude Code adapter 以 `.claude/CLAUDE.md` 作为 canonical path。用户主路径不依赖宿主加载证明；规则安装后，写代码前以当前可执行任务为准。诊断侧仍可能显示 `materialized / verified_loaded / degraded / unsupported`，仅用于排查。

当用户在对话中输入任何需求/任务时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接进入后续设计、分解与实现。

代码实现时，新增注释必须跟随当前或近期用户主要沟通语言；当前对话或近期对话以英文为主则使用英文，否则默认简体中文。保留原有注释；确需删除时，必须在同一变更附近补充等价说明，或在 execution log / handoff 记录删除原因。注释只解释复杂意图、边界、兼容、并发、缓存、错误处理和非显然业务约束，不复述命名已经表达清楚的代码。凡是后续 agent 或人工需要维护的脚本/模块，尤其包含认证、XHR/API 调用、payload 字段映射、加密、阶段流程、重试或副作用边界时，必须补维护契约、关键函数 docstring 或边界注释，并在验证/交付说明中确认这些注释已覆盖。

任务拆解与门禁以 CLI 与 `specs/`、`.ai-sdlc/` 为准。

（自动安装；不覆盖已有自定义内容。）
