# 任务执行日志：v0.9.9 Canonical Release

**功能编号**：`226-v0-9-9-canonical-release`
**创建日期**：2026-09-03
**当前分类**：`formal_freeze_only`
**execution_started**：`false`

## Batch 2026-09-03-001 | T11 formal baseline

### 范围

- 从精确远端主线 `8f9df406e0a0a8fcb7a3da0be5ab164358918773` 创建隔离 worktree。
- 初始化 WI226 canonical 四件套，并将生成的占位正文替换为终局合议方案 B。
- 在 manifest 中声明 `release_candidate` role 与 WI219/220/221/222/224/225 显式依赖。
- 记录 `v0.9.8@4f3e55c3` 之后 18 个 first-parent carrier；PR #200 仅记为 WI226/R06 partial 组件。
- 还原 `workitem init` 对 `.cursor/rules/ai-sdlc.mdc` 产生的无关生成漂移。

### 已执行的基线命令

- `uv sync`：通过，本地包版本 `0.9.8`。
- `uv run ai-sdlc verify constraints`：通过，无 blocker。
- `uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness'`：`7 passed, 409 deselected`。
- `uv run pytest tests/integration/test_github_workflows.py -q`：`16 passed`。

### Formal 验证结果

- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc program truth sync --dry-run`：PASS；全局 `blocked`，16 blockers，inventory `1179/1179 mapped`、missing `6`、close `218/224`。
- `uv run ai-sdlc program truth sync --execute --yes`：PASS；写入 snapshot `9a147f3448efaa77f0c2a360707d11957f70dbf329f5af4ee1f95e3ec001b1eb`。
- `uv run ai-sdlc verify constraints`：PASS，无 blocker。
- `git diff --check`：PASS；`.cursor/rules/ai-sdlc.mdc` 无 diff。
- WI226 文档占位符检查：零命中。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q` 首轮：FAIL，仅因新增 WI 的五层 inventory 期望仍为旧值 `1174/1174, missing 5, close 218/223`；按实际快照同步为 `1179/1179, missing 6, close 218/224` 后复跑通过（`1 passed`）。

### 决策与边界

- 终局合议为 3:0 APPROVE B；这不是当前实现或发布成功证明。
- 不采用 `e70951c3` 的自动 range inference；不新增第二设计。
- 有界自审删除了原计划中的新聚合 dataclass，改为复用 `ProgramSpecTruthReadinessResult`。
- 实施计划再次审阅并由用户明确批准前，T21-T42 均不得启动。
- 本批只修改 formal/manifest/project-state；`execution_started=false`。

### 当前结论

- T11 已完成并通过 formal 自检。
- T12 已完成用户批准；T21 是唯一待执行的 repository task，生产实现尚未开始。

## Batch 2026-09-03-002 | Task 1 formal remediation

### 范围

- 将 `tasks.md` 收敛为现有 parser 可识别的 canonical executable-task blocks。
- 如实记录用户对同一 WI226 formal baseline 的批准；不改生产代码、工作流、版本号或发布状态。
- 明确 Task 5 只有在创建真实 `docs/releases/v0.9.9.md` 的同一批次才登记 release source_registry，并同步 manifest inventory 期望。
- 将 repository executable/checklist 工作边界固定在 T32；其后的 GitHub release evidence 仅作 Post-release handoff。

### 真实状态

- T11、T12：done。
- T21：todo，为 guard 唯一可选择的下一条任务。
- T22、T23、T31、T32：blocked，尚未实施。
- 未执行生产代码、工作流、版本号、merge、tag、资产上传、attestation、release smoke 或 12-route 回执。

### 本批验证

- `uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T21 生产实现" --json`：PASS；精确选择 `T21`。
- `uv run ai-sdlc program validate`：PASS。
- `uv run ai-sdlc verify constraints`：PASS；无 blocker。
- `uv run pytest tests/integration/test_repo_program_manifest.py -q`：PASS，`1 passed in 132.58s`。
- `git diff --check`：PASS。
