# 合并前自检清单（贡献者 / Agent）

复制到 PR 描述中勾选或删除不适用项。

## 框架与仓库约定

- [ ] **本地项目配置**：勿提交 `.ai-sdlc/project/config/project-config.yaml`（仓库已 `.gitignore`）；协作方从 `project-config.example.yaml` 复制或依赖默认加载；详见 `USER_GUIDE.zh-CN.md`。
- [ ] 已阅读 `.ai-sdlc/memory/constitution.md` 与 `src/ai_sdlc/rules/pipeline.md` 中与本次变更相关的条款。
- [ ] 变更与 `specs/<WI>/tasks.md` 中任务对应关系已说明，或已注明「不纳入本 WI」。
- [ ] 若使用 IDE 生成计划文件：相关 **`todos` 状态已更新** 与本次交付一致，或已说明为何保留 `pending`。
- [ ] 若 `tasks.md` / `plan.md` 含 **`related_plan`**：路径仍有效。
- [ ] 自动化：`uv run pytest`（或 CI 等价）与 `uv run ruff check src tests` 已通过（若有 Python 变更）。
- [ ] （可选）`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem plan-check --wi specs/<WI>/`（若本 PR 涉及外部计划或 `related_plan`）。
- [ ] 若本 PR 涉及 release / 安装包 / 版本号：已同步核对 `README.md`、`docs/releases/v0.9.1.md`、`USER_GUIDE.zh-CN.md`、`packaging/offline/README.md` 与 release 资产文案，确保版本入口、平台资产分工、普通用户主路径和排障话术一致（当前 published release `v0.9.1`：`ai-sdlc-offline-0.9.1-windows-amd64.zip`、`ai-sdlc-offline-0.9.1-macos-arm64.tar.gz`、`ai-sdlc-offline-0.9.1-linux-amd64.tar.gz`）。不得只同步版本号/资产名而保留旧的 venv/pip、`adapter status` 主路径、`materialized only` 等历史话术。
- [ ] 若本 PR 涉及离线 bundle 的 `python-runtime/`、在线/离线安装器或“无需预装 Python”口径：已按 `packaging/offline/RELEASE_CHECKLIST.md` 逐项核对，并在 PR 或 execution log 中留下 manifest / smoke / CLI 验证证据。
- [ ] 若本 PR 修改既有用户可见能力、CLI 输出、adapter 指引、配置字段、生成模板或文档主路径：已列出旧能力 / 旧入口 / 旧选项影响面，并提供旧能力未退化的回归测试或真实命令证据；若有废弃或破坏性变更，已在 PRD / spec / migration note 中明确声明。
- [ ] **本地 PR review**：若本 PR 使用 `ai-sdlc pr-review`，模型调用必须由开发机上的本地独立 review agent 发起，默认使用用户当前配置模型，也可显式选择模型；CI 只读取 review artifacts、schema、commit hash、unresolved counts 和 final report，CI 不得发起模型请求，也不得替代本地对抗 review agent。
- [ ] **Loop status/list**：若本 PR 使用 `ai-sdlc loop status` / `ai-sdlc loop list`，必须确认它们只是只读读取 `.ai-sdlc/reviews/pr/current-review.json` 与本地 `review-run.json` artifacts；不得发起模型请求，不得调用 GPT / Claude / DeepSeek / GLM / Codex，不得启动 provider，不得生成 review pack / findings / resolution / final report，不得修复代码或读取远端 PR diff；其 JSON 输出只能作为 artifact 索引与状态证据，不能替代本地对抗 review agent 或最终人工判断。

## 最小验证集（Mandatory）

- [ ] `docs-only`：仅改 `docs/**`、`specs/**.md`、`task-execution-log.md`、`tasks.md` 等 Markdown/收口文档；至少执行 `uv run ai-sdlc verify constraints`。若触及 `related_plan` / 收口文档，需在**完成本轮 git 提交后**执行 `uv run ai-sdlc workitem close-check --wi specs/<WI>/`（或等价命令）并确认无 `BLOCKER`。
- [ ] `rules-only`：仅改 `src/ai_sdlc/rules/**.md` 与相关文档；至少执行 `uv run ai-sdlc verify constraints`。若混入 `src/**/*.py` 或 `tests/**`，必须改按 `code-change` 执行。
- [ ] `truth-only`：仅改 `program-manifest.yaml`、`.ai-sdlc/**`、`specs/**.md`、`docs/**.md` 等全局真值与 formal carrier；执行 `uv run ai-sdlc verify constraints`、`python -m ai_sdlc program truth sync --dry-run`。若需要恢复 fresh snapshot，补执行 `python -m ai_sdlc program truth sync --execute --yes`；若混入 `src/**/*.py` 或 `tests/**`，必须改按 `code-change` 执行。
- [ ] `code-change`：涉及 `src/**/*.py`、`tests/**`、运行时行为或生成逻辑；执行 `uv run pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`。若存在 `related_plan` 或 close 阶段收口改动，补执行 `workitem plan-check` 与 `workitem close-check`（命令名以当前实现为准）并确认无 `BLOCKER`；不得用 `docs-only` / `rules-only` / `truth-only` 伪装代码改动。
- [ ] latest batch 已在 `task-execution-log.md` 记录 `验证画像`、对应 fresh verification 命令，以及 `已完成 git 提交 / 提交哈希`；若工作树仍 dirty，视为收口未完成。

## 参考

- 用户手册：[交付完成（DoD）与计划 / 任务状态](../USER_GUIDE.zh-CN.md#user-guide-dod-plan-sync)
- 框架缺陷 / 违约待办：`docs/framework-defect-backlog.zh-CN.md`
- 历史兼容来源：`src/ai_sdlc/rules/agent-skip-registry.zh.md`
