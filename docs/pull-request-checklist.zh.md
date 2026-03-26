# 合并前自检清单（贡献者 / Agent）

复制到 PR 描述中勾选或删除不适用项。

## 框架与仓库约定

- [ ] **本地项目配置**：勿提交 `.ai-sdlc/project/config/project-config.yaml`（仓库已 `.gitignore`）；协作方从 `project-config.example.yaml` 复制或依赖默认加载；详见 `docs/USER_GUIDE.zh-CN.md`。
- [ ] 已阅读 `.ai-sdlc/memory/constitution.md` 与 `src/ai_sdlc/rules/pipeline.md` 中与本次变更相关的条款。
- [ ] 变更与 `specs/<WI>/tasks.md` 中任务对应关系已说明，或已注明「不纳入本 WI」。
- [ ] 若使用 IDE 生成计划文件：相关 **`todos` 状态已更新** 与本次交付一致，或已说明为何保留 `pending`。
- [ ] 若 `tasks.md` / `plan.md` 含 **`related_plan`**：路径仍有效。
- [ ] 自动化：`uv run pytest`（或 CI 等价）与 `uv run ruff check src tests` 已通过（若有 Python 变更）。
- [ ] （可选）`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem plan-check --wi specs/<WI>/`（若本 PR 涉及外部计划或 `related_plan`）。

## 最小验证集（Mandatory）

- [ ] **文档变更（仅 docs/spec/template）**：至少执行 `uv run ai-sdlc verify constraints`；若触及 `related_plan` / 收口文档，补执行 `uv run ai-sdlc workitem close-check --wi specs/<WI>/`（或实现等价命令）并确认无 `BLOCKER`。
- [ ] **代码变更（src/tests）**：执行 `uv run pytest`、`uv run ruff check src tests`、`uv run ai-sdlc verify constraints`；若存在 `related_plan` 或 close 阶段收口改动，补执行 `workitem plan-check` 与 `workitem close-check`（命令名以当前实现为准）并确认无 `BLOCKER`。

## 参考

- 用户手册：[§2.1 交付完成（DoD）与计划 / 任务状态](USER_GUIDE.zh-CN.md#user-guide-dod-plan-sync)
- 框架缺陷 / 违约待办：`docs/framework-defect-backlog.zh-CN.md`
- 历史兼容来源：`src/ai_sdlc/rules/agent-skip-registry.zh.md`
