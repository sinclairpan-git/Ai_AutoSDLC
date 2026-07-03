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
7. 当用户输入任何需求/任务描述时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接推进后续设计与分解阶段。
8. 产物目录：`specs/<工作项>/` 与 `.ai-sdlc/` 分离；不要混用工程约束目录与产物。
9. 若需求涉及前端需求、UI、页面、组件、浏览器交互或前端工程，进入实现前必须先给出技术栈 / 组件库建议，并等待用户明确确认；确认前不得进入 execute、不得生成前端实现代码、不得运行 managed delivery apply。确认可通过 `program solution-confirm --dry-run` 预览，只有用户确认后才允许 `program solution-confirm --execute --yes`。普通未显式指定 provider 的新前端需求，首个推荐必须是 `frontend_stack=vue3` / `provider_id=public-primevue` / `style_pack_id=modern-saas`，并明确展示 `PrimeVue + @primeuix/themes + primeicons`、`definePreset(Aura) + #1770e6 + darkModeSelector=false`、`Vite + TypeScript + UnoCSS + CSS Variables`、`Pinia + Vue Router + Axios + vee-validate + zod + vue-i18n`、`Playwright + ESLint + Prettier + husky + lint-staged + commitlint` 的默认特性；“企业后台”“中后台”“管理台”“表格”“表单”“审批流”“工作台”等场景词不得被当成 Vue2 信号，仍按 Vue3 public-primevue 默认建议。方案建议必须保留两个层级：小白用户看到默认最优方案，资深用户看到高级可选方案 / 自定义入口；高级可选方案至少覆盖 `enterprise-default`、`data-console`、`high-clarity`、`macos-glass` 等 style pack，以及显式 `vue2` / `enterprise-vue2` 兼容路径。可用 `program solution-confirm --dry-run --mode advanced` 查看候选矩阵，用 `--frontend-stack`、`--provider-id`、`--style-pack-id` 自定义选择；不得丢失需求确定后的技术栈推荐与自定义选择环节。只有当用户明确要求框架自带 Vue2 企业级组件库、历史 Vue2 项目或 `enterprise-vue2` 时，建议才必须包含 `enterprise-vue2` / `vue2`，不得擅自改用 Vue3、React 或 public fallback。
10. 代码实现时，新增注释必须跟随当前或近期用户主要沟通语言；当前对话或近期对话以英文为主则使用英文，否则默认简体中文。保留原有注释；确需删除时，必须在同一变更附近补充等价说明，或在 execution log / handoff 记录删除原因。注释只解释复杂意图、边界、兼容、并发、缓存、错误处理和非显然业务约束，不复述命名已经表达清楚的代码。凡是后续 agent 或人工需要维护的脚本/模块，尤其包含认证、XHR/API 调用、payload 字段映射、加密、阶段流程、重试或副作用边界时，必须补维护契约、关键函数 docstring 或边界注释，并在验证/交付说明中确认这些注释已覆盖。

当前 Cursor adapter 以 `.cursor/rules/ai-sdlc.mdc` 作为 canonical path。规则安装后，写代码前以当前可执行任务为准；内部诊断详情只在排查命令的 `--details` / `--json` 输出中查看。

（本文件由 `ai-sdlc` 首次命令/init 自动安装；若你已自定义同名文件，框架不会覆盖。）
