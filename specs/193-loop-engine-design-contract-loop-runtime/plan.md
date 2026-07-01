---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
  - "specs/192-loop-engine-requirement-loop-runtime/spec.md"
---
# 实施计划：Loop Engine Design Contract Loop Runtime

**编号**：`193-loop-engine-design-contract-loop-runtime` | **日期**：2026-07-01 | **规格**：specs/193-loop-engine-design-contract-loop-runtime/spec.md

## 概述

本计划交付五类 Loop 中的第二类 `design-contract` loop。实现方式是复用现有 Loop Engine 基础模型和 artifact store，新增 design-contract-specific runtime、CLI、status/list 读取扩展、focused tests 和文档约束。该 PR 不进入 implementation、frontend-evidence 或 local-pr-review 的新实现，只在 design-contract close 后给出下一步。

## 技术背景

**语言/版本**：Python 3.11+，Typer CLI，Pydantic v2。
**主要依赖**：现有 `LoopRun`、`LoopStatus`、`LoopArtifactStore`、`loop status/list`、requirement loop 的 artifact/next-guidance 模式。
**存储**：`.ai-sdlc/loops/design-contract/<loop-id>/` 与 `.ai-sdlc/loops/design-contract/current-design-contract.json`。
**测试**：unit tests 覆盖 core runtime/status，integration tests 覆盖 CLI human/json。
**目标平台**：macOS、Linux、Windows；命令示例使用跨平台 CLI，不要求 POSIX shell。
**约束**：不调用模型、不写业务代码、不硬编码远端 SaaS、不破坏 local-pr-review 和 requirement 默认行为。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MVP 优先，范围严控 | 本 PR 只交付 design-contract loop，不进入 implementation/frontend |
| 关键路径必须可验证 | 每个 core check、CLI JSON/human、status/list 接入均有 focused tests |
| 状态落盘，上下文外化 | 所有 check/close/status 证据落在 `.ai-sdlc/loops/design-contract` |
| Fail-readable | 缺失 docs、坏 pointer、坏 loop-run、close blocker 必须输出 blocker/next command |
| Local-first | P0 不调用模型，不依赖 CI 或云端 review |
| Stage boundary | design-contract close 后只指向 implementation loop，不直接修改代码 |

## 项目结构

### 文档结构

```text
specs/193-loop-engine-design-contract-loop-runtime/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/design_contract_loop.py   # design-contract runtime and models
src/ai_sdlc/core/loop_status.py            # status/list design-contract support
src/ai_sdlc/cli/loop_cmd.py                # loop design-contract CLI and --type status
tests/unit/test_design_contract_loop.py    # core runtime tests
tests/unit/test_loop_status.py             # design-contract status/list regression
tests/integration/test_cli_loop.py         # CLI integration tests
tests/unit/test_verify_constraints.py      # feature contract surface tests
README.md                                  # user-facing command docs
src/ai_sdlc/core/verify_constraints.py     # WI-193 surface registration
```

## 阶段计划

### Phase 0：formal baseline and linkage

**目标**：冻结 WI-193 的 PRD、plan、tasks 和初始 execution log。
**产物**：spec.md / plan.md / tasks.md / task-execution-log.md / manifest mapping。
**验证方式**：`git diff --check`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc workitem link ...`。
**回退方式**：删除 WI-193 文档与 manifest mapping。

### Phase 1：design-contract runtime

**目标**：新增 deterministic design-contract loop runtime。
**产物**：`design_contract_loop.py`、unit tests。
**验证方式**：`uv run pytest tests/unit/test_design_contract_loop.py -q`。
**回退方式**：移除 runtime 文件和 tests，不影响 existing loop types。

### Phase 2：status/list and CLI

**目标**：接入 `ai-sdlc loop design-contract` 和 `loop status/list --type design-contract`。
**产物**：`loop_cmd.py`、`loop_status.py`、integration tests。
**验证方式**：`uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`。
**回退方式**：恢复 status/list 只支持 local-pr-review 与 requirement。

### Phase 3：docs, constraints, closeout

**目标**：对齐 README/约束检查/执行日志并完成 close-check。
**产物**：README、verify constraints surface、execution log。
**验证方式**：focused suite、ruff、mypy、`uv run ai-sdlc verify constraints`、`workitem close-check`。
**回退方式**：回退文档和 verify surface。

## 工作流计划

### 工作流 A：合同检查

**范围**：`loop design-contract check` 从 work item docs 生成 coverage matrix 和 report。
**影响范围**：`.ai-sdlc/loops/design-contract`。
**验证方式**：core unit + CLI JSON integration。
**回退方式**：删除当前 loop artifact。

### 工作流 B：合同关闭

**范围**：`loop design-contract close --yes` 验证最近 report 无 blocker 并关闭 loop。
**影响范围**：当前 design-contract loop run 和 close artifact。
**验证方式**：unit test 验证 blocker fail-closed 和 closed summary。
**回退方式**：重新 check 或手工删除 close artifact。

### 工作流 C：统一状态读取

**范围**：`loop status/list --type design-contract`。
**影响范围**：只读，无写入。
**验证方式**：snapshot tests 验证 status/list 不写 artifact。
**回退方式**：恢复 unsupported loop type blocker。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| check writes artifacts | `tests/unit/test_design_contract_loop.py` | CLI JSON test |
| dry-run no writes | unit snapshot | integration test |
| missing FR/SC coverage | unit fixture | human output assertion |
| close fail-closed | unit test | CLI exit code test |
| status/list design-contract | `tests/unit/test_loop_status.py` | `tests/integration/test_cli_loop.py` |
| existing loop no regression | existing local-pr-review/requirement tests | focused suite |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否自动解析外部需求来源 | 延后到 source adapter，不阻塞本地 specs work item | 非阻塞 |
| 是否运行测试命令来验证 coverage | 不在 P0；P0 只检查验证命令是否声明 | 非阻塞 |
| 是否由模型判断语义覆盖 | 不在 P0；当前版本 deterministic/local-only | 非阻塞 |

## 实施顺序建议

1. 冻结 formal docs、link work item、sync program truth。
2. 实现 design-contract runtime 和 core tests。
3. 扩展 loop status/list 与 CLI tests。
4. 对齐 README/verify constraints，跑 focused verification 和 close-check。
5. 提交、推送、开 PR、请求 Codex review；review 无 actionable issues 后合并，再进入 implementation loop。
