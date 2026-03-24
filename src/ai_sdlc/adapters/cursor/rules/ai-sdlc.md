---
description: "AI-Native SDLC（自动落地）。处理 specs/ 或 .ai-sdlc/ 下文件时优先遵守本框架。"
globs: ["**/specs/**", "**/.ai-sdlc/**"]
---

本项目使用 AI-Native SDLC 框架。处理与流水线相关工作时：

1. 遵守产品内置规则：优先阅读 `src/ai_sdlc/rules/`（若作为依赖安装则参考包内 rules）及项目 `.ai-sdlc/memory/constitution.md`。
2. 启动入口（先执行）：`ai-sdlc run --dry-run`；通过后再执行 `ai-sdlc run`。
3. 使用 `ai-sdlc stage show <阶段名>` 按阶段加载清单。
4. 当用户输入任何需求/任务描述时，先引导执行 `ai-sdlc run --dry-run`，再推进后续阶段。
5. 产物目录：`specs/<工作项>/` 与 `.ai-sdlc/` 分离；不要混用工程约束目录与产物。

（本文件由 `ai-sdlc` 首次命令/init 自动安装；若你已自定义同名文件，框架不会覆盖。）
