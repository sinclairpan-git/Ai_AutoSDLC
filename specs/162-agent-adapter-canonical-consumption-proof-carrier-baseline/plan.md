# 实施计划：Agent Adapter Canonical Consumption Proof Carrier Baseline

**编号**：`162-agent-adapter-canonical-consumption-proof-carrier-baseline` | **日期**：2026-04-18 | **规格**：specs/162-agent-adapter-canonical-consumption-proof-carrier-baseline/spec.md

## 概述

`162` 处理的是 proof“载体”缺口，不再改 proof 判定规则本身。实现保持最小：在 `adapter` CLI 下增加一个 carrier 子命令，通过当前 canonical 文件计算 digest/path，并以子进程环境变量的形式把 proof 传给目标命令。下游是否判为 `verified` 仍由 `ide_adapter._evaluate_canonical_consumption()` 决定，因此该实现不会自证，也不会绕开 `160/161` 已固定的 program truth gate。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/integrations/ide_adapter.py`、Typer CLI、`subprocess`  
**测试**：`tests/unit/test_ide_adapter.py`、`tests/integration/test_cli_adapter.py`  
**目标平台**：Codex / `AGENTS.md` canonical proof carrier  
**约束**：

- 不改变现有 `adapter status` / `program truth` 的判定条件
- 不把 carrier 写成“自动持久化 verified”
- 命令面要与现有 `trace exec -- <command>` 风格一致，支持 `--` 后透传子命令
- 缺失 canonical 文件或 target 不支持时必须 fail closed

## 阶段计划

### Phase 1：formal freeze

**目标**：冻结 `162` 的问题定义、命令面和边界  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：`uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `specs/162-*` 与 manifest/project-state 派生改动

### Phase 2：carrier red

**目标**：先写失败测试，证明当前 CLI 还没有 canonical proof carrier  
**产物**：失败的 unit / integration tests  
**验证方式**：聚焦 pytest 红灯  
**回退方式**：删除新增测试或恢复断言

### Phase 3：carrier green

**目标**：实现 `adapter exec -- <command>` 的 proof 注入与 fail-closed 边界  
**产物**：CLI 入口、必要 helper、最小实现  
**验证方式**：聚焦 pytest 转绿  
**回退方式**：移除新命令并恢复测试

### Phase 4：repo verification and close-out

**目标**：在当前仓库复跑 adapter/program truth 入口，记录 carrier 对 canonical blocker 的影响  
**产物**：执行日志、必要的 truth sync evidence  
**验证方式**：`python -m ai_sdlc adapter status`、`python -m ai_sdlc run --dry-run`、carrier 现场验证  
**回退方式**：保留实现，回退仅文档/归档误记

## 实施顺序建议

1. 先冻结 formal docs，明确 carrier 只是 proof transport，不是 proof adjudication。
2. 用一个 unit red 钉住 proof payload 计算/命令校验，再用一个 CLI integration red 钉住用户可见行为。
3. 实现尽量收敛在 `adapter_cmd`，把 digest/path 复用已有 canonical path/digest 逻辑。
4. 用当前仓库做现场验证：普通 `adapter status` 仍为 `unverified`，carrier 子命令内变为 `verified`。
