# 执行记录：078-frontend-contract-sample-selfcheck-fallback-clarification-baseline

## Batch 2026-04-08-001 | sample selfcheck fallback clarification freeze

### 1.1 范围

- **任务来源**：用户指出仓库内已经存在内置 sample 实现，可用于先跑通流程；需要把这条 truth 和 `077` external backfill 口径重新对齐。
- **目标**：冻结“无真实前端源码时可先跑 `065` sample self-check，但不得据此宣称 `068` ~ `071` blocker 已解除”的 clarification baseline。
- **本批 touched files**：
  - `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`
  - `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/plan.md`
  - `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/tasks.md`
  - `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/task-execution-log.md`
  - `.ai-sdlc/project/config/project-state.yaml`

### 1.2 预读与 research inputs

- `specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md`
- `specs/065-frontend-contract-sample-source-selfcheck-baseline/plan.md`
- `specs/077-frontend-contract-observation-backfill-playbook-baseline/spec.md`
- `specs/077-frontend-contract-observation-backfill-playbook-baseline/plan.md`
- `tests/integration/test_cli_scan.py`
- `tests/integration/test_cli_verify_constraints.py`
- `tests/unit/test_frontend_contract_scanner.py`

### 1.3 改动内容

- 新建 `078` formal docs，把 `065` sample self-check、`077` 真实 backfill playbook、以及 `068` ~ `071` root blocker 之间的边界冻结成独立 clarification baseline
- 在 `plan.md` 中给出 `match / empty / missing-root` 的最小 sample self-check 命令矩阵与 honesty guardrails
- 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `77` 推进到 `78`

### 1.4 验证命令

- `uv run pytest tests/unit/test_frontend_contract_scanner.py tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py -q`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/match --frontend-contract-spec-dir /tmp/ai_sdlc_sample_match_spec --frontend-contract-generated-at 2026-04-08T10:00:00Z`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/empty --frontend-contract-spec-dir /tmp/ai_sdlc_sample_empty_spec --frontend-contract-generated-at 2026-04-08T10:05:00Z`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/missing --frontend-contract-spec-dir /tmp/ai_sdlc_sample_missing_spec --frontend-contract-generated-at 2026-04-08T10:10:00Z`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

### 1.5 验证结果

- `uv run pytest tests/unit/test_frontend_contract_scanner.py tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py -q`：退出码 `0`，`59 passed in 3.72s`
- `match` sample scan：退出码 `0`，导出 `2 observations`
- `empty` sample scan：退出码 `0`，导出 `0 observations`
- `missing-root` sample scan：退出码 `2`，显式报错 `is not a directory`
- `uv run ai-sdlc verify constraints`：退出码 `0`，输出 `verify constraints: no BLOCKERs.`
- `git diff --check -- .ai-sdlc/project/config/project-state.yaml specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline`：退出码 `0`

### 1.6 结论

- 仓库当前仍保留一条可运行的 sample self-check 主线，足以证明 scanner/export 流程没有失活
- 这条主线只证明 framework self-check truth，不改变 `068` ~ `071` 仍缺真实 `frontend_contract_observations` 的 root status
