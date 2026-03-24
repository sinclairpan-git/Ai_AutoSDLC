---
description: "AI-Native SDLC（自动落地）。处理 specs/ 或 .ai-sdlc/ 下文件时优先遵守本框架。"
globs: ["**/specs/**", "**/.ai-sdlc/**"]
---

本项目使用 AI-Native SDLC 框架。处理与流水线相关工作时：

1. 遵守产品内置规则：优先阅读 `src/ai_sdlc/rules/`（若作为依赖安装则参考包内 rules）及项目 `.ai-sdlc/memory/constitution.md`。
2. **终端约定**：引导用户在已激活 venv 且 CLI 可用的终端执行；若 `ai-sdlc` 不在 PATH，使用 `python -m ai_sdlc ...`（与 `ai-sdlc` 等价）。
3. 启动入口（先执行）：`ai-sdlc run --dry-run` 或 `python -m ai_sdlc run --dry-run`；全量编排使用 `ai-sdlc run`。
4. 使用 `ai-sdlc stage show <阶段名>` 按阶段加载清单。
5. 产物目录：`specs/<工作项>/` 与 `.ai-sdlc/` 分离；不要混用工程约束目录与产物。

（本文件由 `ai-sdlc` 首次命令/init 自动安装；若你已自定义同名文件，框架不会覆盖。）
