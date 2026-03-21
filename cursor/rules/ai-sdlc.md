---
description: "AI-Native SDLC 行为约束（Cursor 适配器）。当操作 specs/ 或 .ai-sdlc/ 目录下的文件时自动激活。"
globs: ["**/specs/**", "**/.ai-sdlc/**"]
---

本项目使用 AI-Native SDLC 框架。在处理与开发流水线相关的工作时：

1. 读取并遵守 `.ai-sdlc/rules/` 目录下的所有规则文件
2. 读取 `.ai-sdlc/memory/constitution.md` 作为项目宪章约束；若 `.ai-sdlc/memory/engineering-corpus.md` 存在，处理需求与设计时优先对照该工程认知基线
3. 读取 `.ai-sdlc/config/pipeline.yml` 获取流水线配置
4. 使用 `.ai-sdlc/templates/` 下的模板作为输出格式参考

如需运行完整流水线，使用 `/dev.autopilot` 命令。
