# 执行计划：Frontend Contract Sample Selfcheck Fallback Clarification Baseline

**功能编号**：`078-frontend-contract-sample-selfcheck-fallback-clarification-baseline`  
**创建日期**：2026-04-08  
**状态**：docs-only clarification freeze

## 1. 目标与定位

`078` 的目标不是推进 root close，而是修正当前 operator 口径里的缺口：在没有真实前端源码时，仓库并非完全无事可做，仍可先用 `065` sample fixture 做 framework self-check；但这一步只证明链路可运行，不证明 `068` ~ `071` 已取得真实 unblock evidence。

## 2. 范围

### 2.1 In Scope

- 创建 `078` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `78`
- 冻结 `065` sample self-check 与 `077` external backfill playbook 的职责边界
- 冻结 `match / empty / missing-root` 的最小命令矩阵

### 2.2 Out Of Scope

- 回填任何 active spec 的真实 observation artifact
- 修改 `065`、`077`、root rollout wording、`src/` 或 `tests/`
- 把 sample fixture 写成 active spec close evidence

## 3. 变更文件面

当前批次只允许改以下文件面：

- `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`
- `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/plan.md`
- `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/tasks.md`
- `specs/078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/task-execution-log.md`
- `.ai-sdlc/project/config/project-state.yaml`

## 4. Clarification Freeze

### 4.1 Truth split

- `065`：定义 sample frontend source fixture 的角色、合法落点与自检边界
- `077`：定义真实 frontend observation backfill 的 playbook
- `078`：定义“没有真实输入时可先做 sample self-check，但这不等于真实 unblock”的中间澄清层

### 4.2 最小命令矩阵

在仓库根目录执行：

```bash
uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/match \
  --frontend-contract-spec-dir /tmp/ai_sdlc_sample_match_spec \
  --frontend-contract-generated-at 2026-04-08T10:00:00Z
```

```bash
uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/empty \
  --frontend-contract-spec-dir /tmp/ai_sdlc_sample_empty_spec \
  --frontend-contract-generated-at 2026-04-08T10:05:00Z
```

```bash
uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/missing \
  --frontend-contract-spec-dir /tmp/ai_sdlc_sample_missing_spec \
  --frontend-contract-generated-at 2026-04-08T10:10:00Z
```

预期：

- `match`：成功导出 canonical artifact，且 observation 数量为正
- `empty`：成功导出 canonical artifact，且 `observations == []`
- `missing-root`：CLI 显式失败，报 `is not a directory`

### 4.3 Honesty guardrails

- sample self-check 只能证明 scanner/export 主线仍可运行
- sample artifact 不得拷贝进 `specs/068...071` 冒充真实 backfill
- root `program status` 若仍显示 `missing_artifact [frontend_contract_observations]`，不得因为 sample self-check 成功就改写口径

## 5. 分阶段计划

### Phase 0：research and truth alignment

- 回读 `065`、`077` 与现有 CLI / integration test
- 确认 sample fixture 仍然存在且当前测试通过

### Phase 1：docs-only clarification freeze

- 新建 `078` formal docs
- 将 sample fallback、真实 backfill 与 root blocker 三者关系冻结成单一 truth

### Phase 2：verification and archive

- 运行 sample self-check CLI 命令
- 运行 docs-only 验证
- 记录命令与结果

## 6. 最小验证策略

- `uv run pytest tests/unit/test_frontend_contract_scanner.py tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py -q`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/match --frontend-contract-spec-dir /tmp/ai_sdlc_sample_match_spec --frontend-contract-generated-at 2026-04-08T10:00:00Z`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/empty --frontend-contract-spec-dir /tmp/ai_sdlc_sample_empty_spec --frontend-contract-generated-at 2026-04-08T10:05:00Z`
- `uv run ai-sdlc scan tests/fixtures/frontend-contract-sample-src/missing --frontend-contract-spec-dir /tmp/ai_sdlc_sample_missing_spec --frontend-contract-generated-at 2026-04-08T10:10:00Z`
- `uv run ai-sdlc verify constraints`
- `git diff --check`

## 7. 回滚原则

- 如果 `078` 把 sample self-check 写成 active spec 的真实证据，必须回退
- 如果本轮误改 `065`、`077`、root rollout wording、`src/` 或 `tests/`，必须回退
