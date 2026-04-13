# 任务执行日志：Agent Adapter Verified Host Ingress Runtime Baseline

**功能编号**：`122-agent-adapter-verified-host-ingress-runtime-baseline`
**创建日期**：2026-04-13
**状态**：已完成

## 1. 归档规则

- 本文件是 `122-agent-adapter-verified-host-ingress-runtime-baseline` 的固定执行归档文件。
- `122` 本轮只冻结 runtime baseline 的 formal truth 与实现任务分解；不在本工单中直接落代码。
- 后续 implementation 应直接按 `tasks.md` 的 Batch 1-4 顺序推进。

## 2. 批次记录

### Batch 2026-04-13-001 | Runtime baseline freeze

#### 2.1 批次范围

- 覆盖范围：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`、`program-manifest.yaml`、`specs/120-open-capability-tranche-backlog-baseline/*`、`.ai-sdlc/project/config/project-state.yaml`
- 覆盖目标：
  - 冻结 verified host ingress runtime 的 canonical path / state / gate baseline
  - 将 `120/T00` 从 root-truth blocker 升格为正式 `S9` tranche
  - 推进 project-state 到下一个 work item seq

#### 2.2 统一验证命令

- `V1`（文档/补丁完整性）
  - 命令：`git diff --check`
  - 结果：待本批完成后执行

#### 2.3 任务记录

##### T122-DOC-1 | 冻结 runtime baseline

- 改动范围：`spec.md`、`plan.md`、`tasks.md`
- 改动内容：
  - 锁定明确适配目标、canonical path、ingress state 与 `run` gate 语义
  - 锁定 `TRAE` 当前继续按 `generic` 处理
- 新增/调整的测试：无
- 是否符合任务目标：是

##### T122-DOC-2 | 升格 `120/T00`

- 改动范围：`specs/120-open-capability-tranche-backlog-baseline/spec.md`、`specs/120-open-capability-tranche-backlog-baseline/tasks.md`
- 改动内容：
  - 将 `T00` 从 `pending_root_truth_update` 升格为正式 `S9` / Batch 0 tranche
  - 将 `120` 的 root cluster/stream 数量同步到 `121` 后的新真值
- 新增/调整的测试：无
- 是否符合任务目标：是

##### T122-DOC-3 | Formal closeout

- 改动范围：`program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml`、`task-execution-log.md`
- 改动内容：
  - 更新 root cluster summary source refs
  - 将 `next_work_item_seq` 从 `122` 推进到 `123`
- 新增/调整的测试：无
- 是否符合任务目标：是

#### 2.4 批次结论

- `122` 现在已经把 verified host ingress 的 runtime baseline 冻结成正式实现入口。
- `120` 不再把 `T00` 视为待 root truth 回写的 blocker，而是正式的 `S9` tranche。
- 后续实现可以直接从 `122` 开始改代码与测试，不需要再重复争论 `TRAE` 是否单列或 `adapter activate` 是否算真正激活。

### Batch 2026-04-13-002 | Runtime implementation

#### 2.5 批次范围

- 覆盖范围：`src/ai_sdlc/models/project.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/cli/run_cmd.py`、`src/ai_sdlc/adapters/*`、`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`、`tests/integration/test_cli_init.py`、`tests/integration/test_cli_run.py`、`tests/integration/test_cli_status.py`
- 覆盖目标：
  - 将 adapter canonical path 切换到 `122` 冻结的正式入口
  - 引入 ingress truth：`materialized / verified_loaded / degraded / unsupported`
  - 让 `init / adapter select` 自动落位并尝试 verify
  - 让 `run` 基于 ingress truth 做 dry-run warning 与 mutating gate
  - 让 `status / adapter status` 暴露 ingress truth，而非继续把 `acknowledged` 当治理真值

#### 2.6 统一验证命令

- `V2`（adapter/init/run/status focused 回归）
  - 命令：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py tests/integration/test_cli_status.py -q`
  - 结果：通过（`91 passed`）
- `V3`（补丁完整性）
  - 命令：`git diff --check`
  - 结果：通过

#### 2.7 任务记录

##### T122-IMP-1 | 重构 adapter persisted ingress truth

- 改动范围：`src/ai_sdlc/models/project.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/integrations/ide_adapter.py`
- 改动内容：
  - 新增 persisted ingress 字段：`adapter_ingress_state`、`adapter_verification_result`、`adapter_canonical_path`、`adapter_degrade_reason`、`adapter_verification_evidence`、`adapter_verified_at`
  - 保留旧 `adapter_activation_*` 作为 compatibility/debug surface，但 governance truth 改由 ingress 字段驱动
  - 基于 canonical path materialization 与宿主环境变量证据，自动判定 `verified_loaded` / `materialized` / `degraded` / `unsupported`
- 新增/调整的测试：`tests/unit/test_ide_adapter.py`
- 是否符合任务目标：是

##### T122-IMP-2 | 切 canonical path 并更新 adapter 文案

- 改动范围：`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/adapters/claude_code/AI-SDLC.md`、`src/ai_sdlc/adapters/codex/AI-SDLC.md`、`src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md`、`src/ai_sdlc/adapters/vscode/AI-SDLC.md`
- 改动内容：
  - `Claude Code -> .claude/CLAUDE.md`
  - `Codex -> AGENTS.md`
  - `Cursor -> .cursor/rules/ai-sdlc.mdc`
  - `VS Code -> .github/copilot-instructions.md`
  - 模板文案改为先看 `adapter status`，并明确 `verified_loaded` 才代表 machine-verifiable ingress
- 新增/调整的测试：`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_init.py`
- 是否符合任务目标：是

##### T122-IMP-3 | 接入 CLI auto verify 与 run gate

- 改动范围：`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/commands.py`、`src/ai_sdlc/cli/run_cmd.py`
- 改动内容：
  - `adapter select` 输出 ingress truth；`adapter activate` 明确降级为 compatibility/debug surface
  - `init` 启动提示改为优先查看 ingress truth，而不是先做人工 acknowledgement
  - `run --dry-run` 对未 `verified_loaded` 的 target 只给 warning
  - mutating `run` 对未 `verified_loaded` 的 target 直接阻断
- 新增/调整的测试：`tests/integration/test_cli_adapter.py`、`tests/integration/test_cli_run.py`、`tests/integration/test_cli_status.py`
- 是否符合任务目标：是

#### 2.8 批次结论

- adapter runtime 已从 `installed / acknowledged / activated` 的旧治理表述迁移到 ingress truth。
- `adapter activate` 仍可保留为兼容面，但不再决定 `run` 是否放行。
- `status / adapter status / init / run` 对 canonical path、verification result 与 mutating gate 的口径已经统一。
