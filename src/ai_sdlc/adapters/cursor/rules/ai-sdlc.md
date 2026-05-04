---
description: "AI-Native SDLC（可选 Cursor 适配）。处理 specs/ 或 .ai-sdlc/ 下文件时优先遵守本框架；规范真值以 CLI 与包内 rules 为准，不依赖本文件所在编辑器。"
globs: ["**/specs/**", "**/.ai-sdlc/**"]
---

本项目使用 AI-Native SDLC 框架。**本文件为可选 IDE 提示**；与编辑器无关的约定以 `python -m ai_sdlc`、`src/ai_sdlc/rules/`（或已安装包内同名目录）及 `.ai-sdlc/memory/constitution.md` 为准。处理与流水线相关工作时：

1. 遵守产品内置规则：优先阅读 `src/ai_sdlc/rules/`（若作为依赖安装则参考包内 rules）及项目 `.ai-sdlc/memory/constitution.md`；阶段顺序见 `rules/pipeline.md`（含 design→decompose→verify→execute）。框架缺陷 / 违约主 backlog 见 `docs/framework-defect-backlog.zh-CN.md`，历史兼容登记见 `rules/agent-skip-registry.zh.md`。
2. **终端约定**：优先使用用户已安装好的 `ai-sdlc`；聊天里可复制完整命令，但不要假设对话环境已具备 shell PATH。若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`（与 `ai-sdlc` 等价）。不要要求普通用户手动安装 Python、venv、pip 或依赖，除非 CLI 明确报错并给出修复命令。
3. 初始化入口（普通用户先执行）：`ai-sdlc init .` 或 `python -m ai_sdlc init .`。
4. `init` 会在用户选择 AI 代理入口和 shell 后自动执行必要检查与安全预演；正常输出会给出“当前结果 / Result”和“下一步 / Next”。
5. 排查入口（仅当 CLI 明确要求时执行）：`ai-sdlc adapter status`、`ai-sdlc run --dry-run` 或对应 `python -m ai_sdlc ...` 写法。
6. 使用 `ai-sdlc stage show <阶段名>` 按阶段加载清单。
7. 当用户输入任何需求/任务描述时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接推进后续阶段。
8. 产物目录：`specs/<工作项>/` 与 `.ai-sdlc/` 分离；不要混用工程约束目录与产物。

当前 Cursor adapter 以 `.cursor/rules/ai-sdlc.mdc` 作为 canonical path。治理侧以 `materialized / verified_loaded / degraded / unsupported` 为准；只有存在 machine-verifiable 证据时，才可视为 `verified_loaded`。

（本文件由 `ai-sdlc` 首次命令/init 自动安装；若你已自定义同名文件，框架不会覆盖。）
