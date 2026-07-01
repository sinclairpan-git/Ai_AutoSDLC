---
related_doc:
  - "specs/189-loop-engine-local-adversarial-pr-review/spec.md"
  - "specs/190-loop-engine-status-list-baseline/spec.md"
  - "specs/191-loop-engine-next-action-guidance-baseline/spec.md"
---
# 实施计划：Loop Engine Requirement Loop Runtime

**编号**：`192-loop-engine-requirement-loop-runtime` | **日期**：2026-06-30 | **规格**：specs/192-loop-engine-requirement-loop-runtime/spec.md

## 概述

本计划交付五类 Loop 中的第一类 `requirement` loop。实现方式是复用现有 Loop Engine 基础模型和 artifact store，新增 requirement-specific runtime、CLI、status/list 读取扩展、focused tests 和文档约束。该 PR 不进入 design-contract、implementation 或 frontend-evidence 的实现，只在 requirement freeze 后给出下一步。

## 技术背景

**语言/版本**：Python 3.11+，Typer CLI，Pydantic v2。
**主要依赖**：现有 `LoopRun`、`LoopStatus`、`LoopArtifactStore`、`loop status/list`。
**存储**：`.ai-sdlc/loops/requirement/<loop-id>/` 与 `.ai-sdlc/loops/requirement/current-requirement.json`。
**测试**：unit tests 覆盖 core runtime/status，integration tests 覆盖 CLI human/json。
**目标平台**：macOS、Linux、Windows；命令示例使用跨平台 CLI，不要求 POSIX shell。
**约束**：不调用模型、不写业务代码、不硬编码远端 SaaS、不破坏 local-pr-review 默认行为。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Canonical artifact | 只在 `.ai-sdlc/loops/requirement` 写 requirement loop artifact，不创建第二套 formal docs |
| Fail-readable | 缺失输入、坏 pointer、坏 loop-run 必须输出 blocker/next command，不 traceback |
| Local-first | 本 PR 不调用模型，不依赖 CI 或云端 review |
| Stage boundary | Requirement freeze 后只指向 design-contract，不直接进入 implementation |

## 项目结构

### 文档结构

```text
specs/192-loop-engine-requirement-loop-runtime/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/requirement_loop.py      # requirement loop runtime and models
src/ai_sdlc/core/loop_status.py           # status/list requirement support
src/ai_sdlc/cli/loop_cmd.py               # loop requirement CLI and --type status
tests/unit/test_requirement_loop.py       # core runtime tests
tests/unit/test_loop_status.py            # requirement status/list regression
tests/integration/test_cli_loop.py        # CLI integration tests
```

## 阶段计划

### Phase 0：formal baseline and linkage

**目标**：冻结 WI-192 的 PRD、plan、tasks 和初始 execution log。
**产物**：spec.md / plan.md / tasks.md / task-execution-log.md / manifest mapping。
**验证方式**：`git diff --check`、`uv run ai-sdlc program truth sync --execute --yes`、`uv run ai-sdlc workitem link ...`。
**回退方式**：删除 WI-192 文档与 manifest mapping。

### Phase 1：requirement runtime

**目标**：新增 deterministic requirement loop runtime。
**产物**：`requirement_loop.py`、unit tests。
**验证方式**：`uv run pytest tests/unit/test_requirement_loop.py -q`。
**回退方式**：移除 runtime 文件和 tests，不影响 local-pr-review。

### Phase 2：status/list and CLI

**目标**：接入 `ai-sdlc loop requirement` 和 `loop status/list --type requirement`。
**产物**：`loop_cmd.py`、`loop_status.py`、integration tests。
**验证方式**：`uv run pytest tests/unit/test_loop_status.py tests/integration/test_cli_loop.py -q`。
**回退方式**：恢复 `loop status/list` 只支持 local-pr-review。

### Phase 3：docs, constraints, closeout

**目标**：对齐 README/约束检查/执行日志并完成 close-check。
**产物**：README、verify constraints surface、execution log。
**验证方式**：focused suite、ruff、mypy、`uv run ai-sdlc verify constraints`、`workitem close-check`。
**回退方式**：回退文档和 verify surface。

## 工作流计划

### 工作流 A：新需求捕获

**范围**：`loop requirement start` 从 idea 或 input file 写 artifact。
**影响范围**：`.ai-sdlc/loops/requirement`。
**验证方式**：core unit + CLI JSON integration。
**回退方式**：删除当前 loop artifact。

### 工作流 B：需求冻结

**范围**：`loop requirement freeze --yes` 验证 acceptance 并关闭 loop。
**影响范围**：当前 requirement loop run 和 freeze artifact。
**验证方式**：unit test 验证 no-acceptance fail-closed 和 closed summary。
**回退方式**：重新 start 或手工删除 freeze artifact。

### 工作流 C：统一状态读取

**范围**：`loop status/list --type requirement`。
**影响范围**：只读，无写入。
**验证方式**：snapshot tests 验证 status/list 不写 artifact。
**回退方式**：恢复 unsupported loop type blocker。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| start writes artifacts | `tests/unit/test_requirement_loop.py` | CLI JSON test |
| dry-run no writes | unit snapshot | integration test |
| freeze fail-closed | unit test | human output assertion |
| status/list requirement | `tests/unit/test_loop_status.py` | `tests/integration/test_cli_loop.py` |
| local-pr-review no regression | existing loop status tests | focused suite |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 远端需求来源 adapter | 延后到后续 P1，不阻塞本地 requirement loop | 非阻塞 |
| 是否自动生成 formal work item docs | 不在本 PR 实现；requirement loop 只冻结需求 artifact | 非阻塞 |
| 是否由模型辅助澄清问题 | 不在本 PR 实现；当前版本 deterministic/local-only | 非阻塞 |

## 实施顺序建议

1. 冻结 formal docs、link work item、sync program truth。
2. 实现 requirement runtime 和 core tests。
3. 扩展 loop status/list 与 CLI tests。
4. 对齐 README/verify constraints，跑 focused verification 和 close-check。
5. 提交、推送、开 PR、请求 Codex review；review 无 actionable issues 后合并，再进入 design-contract loop。
