---
description: "AI-Native SDLC（可选 Cursor 适配）。处理 specs/ 或 .ai-sdlc/ 下文件时优先遵守本框架；规范真值以 CLI 与包内 rules 为准，不依赖本文件所在编辑器。"
globs: ["**/specs/**", "**/.ai-sdlc/**"]
---

本项目使用 AI-Native SDLC 框架。**本文件为可选 IDE 提示**；与编辑器无关的约定以 `python -m ai_sdlc`、`src/ai_sdlc/rules/`（或已安装包内同名目录）及 `.ai-sdlc/memory/constitution.md` 为准。处理与流水线相关工作时：

1. 遵守产品内置规则：优先阅读 `src/ai_sdlc/rules/`（若作为依赖安装则参考包内 rules）及项目 `.ai-sdlc/memory/constitution.md`；阶段顺序见 `rules/pipeline.md`（含 design→decompose→verify→execute）。框架缺陷 / 违约主 backlog 见 `docs/framework-defect-backlog.zh-CN.md`，历史兼容登记见 `rules/agent-skip-registry.zh.md`。
2. **终端约定**：引导用户在**已激活且已安装 CLI 的 venv** 的终端里执行命令；聊天里可复制完整命令，但不要假设对话环境已具备 shell PATH。若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`（与 `ai-sdlc` 等价）。
3. 先检查接入真值：`ai-sdlc adapter status`。
4. 启动入口（先执行）：`ai-sdlc run --dry-run` 或 `python -m ai_sdlc run --dry-run`（安全预演；不证明治理激活）；通过后再执行 `ai-sdlc run`。
5. 使用 `ai-sdlc stage show <阶段名>` 按阶段加载清单。
6. 当用户输入任何需求/任务描述时，先引导执行上述启动入口（优先给出用户环境可用的那一种写法），再推进后续阶段。
7. 产物目录：`specs/<工作项>/` 与 `.ai-sdlc/` 分离；不要混用工程约束目录与产物。

当前 Cursor adapter 以 `.cursor/rules/ai-sdlc.mdc` 作为 canonical path。治理侧以 `materialized / verified_loaded / degraded / unsupported` 为准；只有存在 machine-verifiable 证据时，才可视为 `verified_loaded`。

（本文件由 `ai-sdlc` 首次命令/init 自动安装；若你已自定义同名文件，框架不会覆盖。）
