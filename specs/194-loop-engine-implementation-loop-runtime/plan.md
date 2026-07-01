# 实施计划：Loop Engine Implementation Loop Runtime

**编号**：`194-loop-engine-implementation-loop-runtime` | **日期**：2026-07-01 | **规格**：specs/194-loop-engine-implementation-loop-runtime/spec.md

## 概述

本计划交付五类 Loop 中的第三类 `implementation` loop。实现方式是复用现有 Loop Engine 基础模型、artifact store、design-contract gate 和 status/list 读取扩展，新增 implementation-specific runtime、CLI、focused tests 和文档约束。该 PR 不进入 frontend-evidence，也不重新实现 local-pr-review，只在 implementation close 后给出下一步。

## 技术背景

**语言/版本**：Python 3.11+，Typer CLI，Pydantic v2。
**主要依赖**：现有 `LoopRun`、`LoopStatus`、`LoopArtifactStore`、`loop status/list`、design-contract loop 的 artifact/next-guidance 模式。
**存储**：`.ai-sdlc/loops/implementation/<loop-id>/` 与 `.ai-sdlc/loops/implementation/current-implementation.json`。
**测试**：unit tests 覆盖 core runtime/status，integration tests 覆盖 CLI human/json。
**目标平台**：macOS、Linux、Windows；命令示例使用跨平台 CLI，不要求 POSIX shell。
**约束**：不调用模型、不写业务代码、不硬编码远端 SaaS、不破坏 local-pr-review / requirement / design-contract 默认行为。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MVP 优先，范围严控 | 本 PR 只交付 implementation loop，不进入 frontend-evidence |
| 关键路径必须可验证 | start/record/close、CLI JSON/human、status/list 接入均有 focused tests |
| 状态落盘，上下文外化 | 所有 implementation 执行证据落在 `.ai-sdlc/loops/implementation` |
| Fail-readable | 上游 design-contract 缺失、坏 pointer、未知 task、缺证据 close 必须输出 blocker/next command |
| Local-first | P0 不调用模型，不依赖 CI 或云端 review |
| Stage boundary | implementation close 后只指向 frontend-evidence 或 local-pr-review，不直接声称完成 |

## 项目结构

### 文档结构

```text
specs/194-loop-engine-implementation-loop-runtime/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/implementation_models.py      # implementation artifact models
src/ai_sdlc/core/implementation_store.py       # implementation artifact paths and readers
src/ai_sdlc/core/implementation_loop.py        # implementation runtime
src/ai_sdlc/core/loop_status.py                # status/list implementation support
src/ai_sdlc/cli/loop_cmd.py                    # loop implementation CLI and --type status/list
tests/unit/test_implementation_loop.py         # core runtime tests
tests/unit/test_loop_status.py                 # implementation status/list regression
tests/integration/test_cli_loop.py             # CLI integration tests
tests/unit/test_verify_constraints.py          # feature contract surface tests
README.md                                      # user-facing command docs
src/ai_sdlc/core/verify_constraints.py         # WI-194 surface registration
```

## 阶段计划

### Phase 0：formal baseline and linkage

**目标**：冻结 WI-194 的 PRD、plan、tasks 和初始 execution log，并将 checkpoint linkage 切到 WI-194。
**产物**：spec.md / plan.md / tasks.md / task-execution-log.md / manifest mapping / checkpoint linkage。
**验证方式**：`git diff --check`、`uv run ai-sdlc workitem link --wi-id 194-loop-engine-implementation-loop-runtime --plan-uri specs/194-loop-engine-implementation-loop-runtime/plan.md`、`uv run ai-sdlc program truth sync --execute --yes`。
**回退方式**：删除 WI-194 文档与 manifest mapping，或重新 link 回上一 work item。

### Phase 1：implementation runtime

**目标**：新增 deterministic implementation loop runtime。
**产物**：`implementation_models.py`、`implementation_store.py`、`implementation_loop.py`、unit tests。
**验证方式**：`uv run pytest tests/unit/test_implementation_loop.py -q`。
**回退方式**：移除 runtime 文件和 tests，不影响 existing loop types。

### Phase 2：status/list and CLI

**目标**：接入 `ai-sdlc loop implementation` 和 `loop status/list --type implementation`。
**产物**：`loop_cmd.py`、`loop_status.py`、integration tests。
**验证方式**：`uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`。
**回退方式**：恢复 status/list 只支持 local-pr-review、requirement 和 design-contract。

### Phase 3：docs, constraints, closeout

**目标**：对齐 README/约束检查/执行日志并完成 close-check。
**产物**：README、verify constraints surface、execution log。
**验证方式**：focused suite、ruff、mypy、`uv run ai-sdlc verify constraints`、`workitem close-check`。
**回退方式**：回退文档和 verify surface。

## 工作流计划

### 工作流 A：启动实现闭环

**范围**：`loop implementation start` 从 closed design-contract 和 `tasks.md` 生成 task snapshot、progress 和 report。
**影响范围**：`.ai-sdlc/loops/implementation`。
**验证方式**：core unit + CLI JSON integration。
**回退方式**：删除当前 implementation loop artifact。

### 工作流 B：记录实现证据

**范围**：`loop implementation record` 更新 task progress、verification evidence 和 report。
**影响范围**：当前 implementation loop run 和 implementation-specific artifacts。
**验证方式**：unit tests 覆盖 done、blocked、unknown task、done-without-evidence。
**回退方式**：重新 record 正确状态；必要时删除当前 loop artifact 后重启 start。

### 工作流 C：关闭实现闭环

**范围**：`loop implementation close --yes` 验证 required task 完成度和证据完整性。
**影响范围**：当前 implementation loop run 和 close artifact。
**验证方式**：unit test 验证 incomplete/blocked/missing-evidence fail-closed 和 closed summary。
**回退方式**：继续 record 缺失证据后再次 close。

### 工作流 D：统一状态读取

**范围**：`loop status/list --type implementation`。
**影响范围**：只读，无写入。
**验证方式**：snapshot tests 验证 status/list 不写 artifact。
**回退方式**：恢复 unsupported loop type blocker。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| start requires closed design-contract | `tests/unit/test_implementation_loop.py` | CLI JSON test |
| start writes artifacts | unit artifact assertions | status recovery test |
| dry-run no writes | unit snapshot | integration test |
| record validates task id/status/evidence | unit table tests | human output assertion |
| close fail-closed | unit test | CLI exit code test |
| status/list implementation | `tests/unit/test_loop_status.py` | `tests/integration/test_cli_loop.py` |
| existing loop no regression | existing local-pr-review/requirement/design-contract tests | focused suite |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否自动运行 verification command | 延后；P0 只记录命令和证据，不自动执行 | 非阻塞 |
| 如何判断是否需要 frontend-evidence | P0 使用 work item 文档和 task 内容的前端/浏览器关键词；后续可接入更强的 stage metadata | 非阻塞 |
| 是否支持外部 task source | 延后到 source adapter；P0 只读 canonical `specs/<wi>/tasks.md` | 非阻塞 |

## 实施顺序建议

1. 冻结 formal docs、link WI-194、sync program truth。
2. 实现 implementation artifact models/store 和 core tests。
3. 实现 start/record/close runtime。
4. 扩展 loop status/list 与 CLI tests。
5. 对齐 README/verify constraints，跑 focused verification 和 close-check。
6. 提交、推送、开 PR、请求 Codex review；review 无 actionable issues 后合并，再进入 frontend-evidence loop。
---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
  - "specs/192-loop-engine-requirement-loop-runtime/spec.md"
  - "specs/193-loop-engine-design-contract-loop-runtime/spec.md"
---
