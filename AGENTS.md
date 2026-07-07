# AI-SDLC（Codex / OpenAI Codex CLI 提示）

本工程使用 **AI-SDLC** 自动化流水线。

- 宪章：`.ai-sdlc/memory/constitution.md`
- **终端约定（普通用户项目）**：优先使用用户已安装好的 `ai-sdlc`；若裸命令不可用，使用 `python -m ai_sdlc ...`。不要要求普通用户手动安装 Python、venv、pip 或依赖，除非 CLI 明确报错并给出修复命令。
- 分阶段清单：`ai-sdlc stage show <阶段名>`
- 初始化入口（普通用户先执行）：`ai-sdlc init .` 或 `python -m ai_sdlc init .`
- `init` 会在用户选择 AI 代理入口和 shell 后自动执行必要检查与安全预演；正常输出会给出“当前结果 / Result”和“下一步 / Next”。
- 排查入口（仅当 CLI 明确要求时执行）：`ai-sdlc adapter status`、`ai-sdlc run --dry-run` 或对应 `python -m ai_sdlc ...` 写法。
- 全流程执行：`ai-sdlc run`

当前 Codex adapter 以 `AGENTS.md` 作为 canonical path。规则安装后，写代码前以当前可执行任务为准；内部诊断详情只在排查命令的 `--details` / `--json` 输出中查看。

当用户在聊天中输入任何需求/任务描述时，如果项目尚未初始化，先引导用户执行 `init`。如果 `init` 已完成且 CLI 输出的下一步是切换到 AI 对话，则不要再要求用户手动执行 `adapter status` 或 `run --dry-run`；直接进入需求细化与分解。`run --dry-run` 仅作为异常排查入口，普通需求路径无需手动运行。

若需求涉及前端需求、UI、页面、组件、浏览器交互或前端工程，进入实现前必须先给出技术栈 / 组件库建议，并等待用户明确确认；确认前不得进入 execute、不得生成前端实现代码、不得运行 managed delivery apply。确认可通过 `program solution-confirm --dry-run` 预览，只有用户确认后才允许 `program solution-confirm --execute --yes`。普通未显式指定 provider 的新前端需求，首个推荐必须是 `frontend_stack=vue3` / `provider_id=public-primevue` / `style_pack_id=modern-saas`，并明确展示 `PrimeVue + @primeuix/themes + primeicons`、`definePreset(Aura) + #1770e6 + darkModeSelector=false`、`Vite + TypeScript + UnoCSS + CSS Variables`、`Pinia + Vue Router + Axios + vee-validate + zod + vue-i18n`、`Playwright + ESLint + Prettier + husky + lint-staged + commitlint` 的默认特性；前端规范输出必须区分 `规范正文`、`可选建议`、`已经落地`，不得把建议项或未验证依赖写成当前项目事实；Vue3 public-primevue 主题必须同时覆盖 `primary / surface / highlight`，`theme.ts 是主题预设唯一入口`，浅色页面中的普通信息载体必须与页面主体保持同一视觉体系，新项目默认使用 `pages/`，历史项目可沿用 `views/`，不得同时新建 `pages/` 和 `views/`。“企业后台”“中后台”“管理台”“表格”“表单”“审批流”“工作台”等场景词不得被当成 Vue2 信号，仍按 Vue3 public-primevue 默认建议。方案建议必须保留两个层级：小白用户看到默认最优方案，资深用户看到高级可选方案 / 自定义入口；高级可选方案至少覆盖 `enterprise-default`、`data-console`、`high-clarity`、`macos-glass` 等 style pack，以及显式 `vue2` / `enterprise-vue2` 兼容路径。可用 `program solution-confirm --dry-run --mode advanced` 查看候选矩阵，用 `--frontend-stack`、`--provider-id`、`--style-pack-id` 自定义选择；不得丢失需求确定后的技术栈推荐与自定义选择环节。只有当用户明确要求框架自带 Vue2 企业级组件库、历史 Vue2 项目或 `enterprise-vue2` 时，建议才必须包含 `enterprise-vue2` / `vue2`，不得擅自改用 Vue3、React 或 public fallback。

代码实现时，新增注释必须跟随当前或近期用户主要沟通语言；当前对话或近期对话以英文为主则使用英文，否则默认简体中文。保留原有注释；确需删除时，必须在同一变更附近补充等价说明，或在 execution log / handoff 记录删除原因。注释只解释复杂意图、边界、兼容、并发、缓存、错误处理和非显然业务约束，不复述命名已经表达清楚的代码。

请在修改 `specs/` 与 `.ai-sdlc/` 下文档时遵守上述入口。

（自动安装；不覆盖已有同名自定义文件。）

<!-- AI-SDLC managed shell guidance -->
Project preferred shell: PowerShell.
Use PowerShell syntax for commands, env vars, pipes, and filesystem operations. Do not start with POSIX shell syntax and then retry in PowerShell.

## Continuity Protocol

For long-running Codex/ChatGPT tasks, maintain `.ai-sdlc/state/codex-handoff.md`.
When a checkpoint is linked to an active work item, also keep the scoped copy at
`.ai-sdlc/work-items/<wi-id>/codex-handoff.md`.

Update the handoff with the active AI-SDLC CLI for the current context:

- In ordinary user projects, use `ai-sdlc handoff update` or
  `python -m ai_sdlc handoff update`.
- In this Ai_AutoSDLC repository's self-development workflow, use the
  repository source entrypoint: `uv run ai-sdlc handoff update`.

Update the handoff:

- after any meaningful code or document change batch
- after running tests or debugging a failure
- before reading or producing very large logs
- whenever the task direction changes
- before handing off after an interruption or context compaction
- at least every 20 minutes during extended work

The handoff must include:

- current goal
- current state
- changed files
- key decisions
- commands/tests run and results
- blockers or risks
- exact next steps

When resuming interrupted work, first run `ai-sdlc handoff show` or read
`.ai-sdlc/state/codex-handoff.md`, then continue from its exact next steps.
Keep the handoff concise enough for a fresh thread to read quickly.

## Local Repository PR Protocol

This section is for development of this AI-SDLC repository itself. Do not copy
it into external user guidance or framework runtime rules.

For this repository's self-development workflow, treat the checked-out source as
the active framework implementation. Use `uv run ai-sdlc ...` for SDLC
governance, AgentOps, handoff, work item, verify, and run commands. A globally
installed `ai-sdlc` may be older and is only a distribution/user-install smoke
target, not the controlling framework for local repository development.

When a Codex change is ready for mainline:

- Push the branch and open a PR.
- Request Codex review on the PR.
- Immediately create or keep a heartbeat at about five-minute intervals for the
  PR. The heartbeat must monitor Codex review results and required GitHub check
  status until the PR is merged or a user-input blocker is reached.
- If review finds actionable issues, implement focused fixes on the same branch,
  rerun relevant local tests, push, re-request Codex review, and continue the
  heartbeat monitoring loop.
- If Codex review reports no actionable issues and all required checks pass,
  mark the PR ready when needed and merge it into `main`.
- This protocol is a local development rule for this repository only; do not
  copy it into external user guidance or AI-SDLC framework runtime rules.
