# 实施计划：Loop Engine Status/List Baseline

**编号**：`190-loop-engine-status-list-baseline`
**日期**：2026-06-29
**规格**：`specs/190-loop-engine-status-list-baseline/spec.md`
**状态**：等待执行

## 概述

本计划把 WI-189 P1 中的 `ai-sdlc loop status/list` 落成最小可用的只读 Loop Engine 状态面。实现重点是新增通用 loop summary 读取服务、注册 `ai-sdlc loop` CLI、消费现有 local PR review artifact，并保证 status/list 无模型调用、无 adapter 写入、无 artifact 写入。

第一版只覆盖 local PR review loop。Requirement、Design Contract、Implementation、Frontend Evidence 的专用执行逻辑继续留给后续 work item，但输出模型必须保留通用 loop 字段，避免未来扩展破坏 JSON 结构。

## 技术背景

**语言/版本**：Python 3.11+
**CLI**：Typer + Rich，新增 `src/ai_sdlc/cli/loop_cmd.py` 并在 `src/ai_sdlc/cli/main.py` 注册 `loop`。
**数据模型**：Pydantic，复用 `LoopStatus`、`LoopType`、`ReviewRun`、`ReviewPack`、`ReviewFindings`，新增只读 summary/result 模型。
**存储**：只读读取 `.ai-sdlc/reviews/pr/current-review.json` 与 `.ai-sdlc/reviews/pr/*/review-run.json`；不写入 `.ai-sdlc/`。
**测试**：unit tests 覆盖 summary reader、malformed artifact、read-only 快照；integration tests 覆盖 Typer CLI human/json 和 command discovery。
**目标平台**：macOS/Linux/Windows；路径输出使用 repo-relative 或稳定字符串。
**约束**：不调用模型、不启动 provider、不修改代码、不读取远端 PR diff、不生成新 loop artifact。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MVP 优先，范围严控 | 只做 status/list，只消费 local PR review artifact；其他 loop type 只保留输出扩展位。 |
| 关键路径必须可验证 | 每个命令都有 unit/integration tests，覆盖 no current、valid current、malformed artifact、read-only。 |
| 状态落盘，上下文外化 | 不新增写入；读取 WI-189 已落盘 review-run/current pointer 并外化统一 summary。 |
| 改动声明范围、验证与回退 | 改动集中在 `core/loop_status.py`、`cli/loop_cmd.py`、CLI 注册、tests 与本 spec。 |
| 不伪造证据 | status/list 只报告已存在 artifact；缺失或损坏时 blocked/malformed，不推断通过。 |

## 模块设计

### 模块 A：Loop Status 只读模型与服务

新增建议文件：

```text
src/ai_sdlc/core/loop_status.py
tests/unit/test_loop_status.py
```

职责：

1. 定义 `LoopArtifactRef`、`LoopSummary`、`LocalPRReviewSummary`、`LoopStatusResult`、`LoopListResult`、`MalformedLoopArtifact`。
2. 提供 `get_loop_status(root)` 读取 current pointer 和 `ReviewRun`。
3. 提供 `list_loops(root, loop_type="local-pr-review")` 扫描 `.ai-sdlc/reviews/pr/*/review-run.json`。
4. 使用 `ReviewRun.model_validate` 解析，不用 ad hoc 字符串解析。
5. 对 malformed artifact 返回结构化摘要，不抛出未处理 traceback。
6. 不写入任何文件。

### 模块 B：Loop CLI

新增建议文件：

```text
src/ai_sdlc/cli/loop_cmd.py
tests/integration/test_cli_loop.py
```

调整文件：

```text
src/ai_sdlc/cli/main.py
src/ai_sdlc/cli/command_names.py
src/ai_sdlc/__main__.py
tests/unit/test_command_names.py
```

职责：

1. 注册 `ai-sdlc loop status [--json]`。
2. 注册 `ai-sdlc loop list [--json] [--type local-pr-review]`。
3. human 输出包含 Result、Next、loop type、status、review id、verdict、unresolved counts、artifact paths。
4. JSON 输出使用 Pydantic `model_dump(mode="json")`。
5. 将 `loop` 加入 global callback 的 read-only bypass，避免 adapter 写入。
6. `python -m ai_sdlc --help` fallback 包含 `loop`。

### 模块 C：只读与副作用防护

覆盖点：

1. CLI integration test 在命令执行前后快照 `.ai-sdlc/` 重要文件内容。
2. `loop status/list` 不调用 `run_provider_command`、`run_mock_reviewer`、`start_pr_review` 或 `build_review_pack`。
3. 只读命令不写 current pointer，不创建 `.ai-sdlc/reviews/pr/<new-id>`。
4. command discovery 和 `main.py` bypass 同步。

## 工作流设计

### 工作流 1：查看当前 local PR review loop

```text
ai-sdlc pr-review start --provider mock-reviewer
ai-sdlc loop status
ai-sdlc loop status --json
```

预期：

1. `loop status` 展示当前 `local-pr-review`。
2. `Next` 来自 persisted `ReviewRun.next_action`。
3. 没有 current review 时，输出 no current loop 和 `ai-sdlc pr-review start`。

### 工作流 2：列出历史 review runs

```text
ai-sdlc loop list
ai-sdlc loop list --json
```

预期：

1. 列出 `.ai-sdlc/reviews/pr/*/review-run.json`。
2. 标记 `is_current`。
3. 单个 malformed run 不影响其他合法 runs。

### 工作流 3：只读审计

```text
ai-sdlc loop status --json
ai-sdlc loop list --json
```

预期：

1. 不新增/修改 `.ai-sdlc/` artifact。
2. 不触发 provider、模型、review rerun 或 adapter 写入。

## 输出合同

### `LoopStatusResult`

必须包含：

```text
status
result
next_action
current_loop
blocker
```

### `LoopSummary`

必须包含：

```text
loop_id
loop_type
status
is_current
updated_at
next_action
artifacts[]
```

### `LocalPRReviewSummary`

作为 `LoopSummary.local_pr_review` 可选字段，必须包含：

```text
review_id
verdict
unresolved_blockers
unresolved_required
unresolved_advisory
base_ref
head_ref
base_commit
head_commit
provider_id
model_selector
resolved_model
code_egress
```

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| 当前 review status | unit test + CLI integration | 与 `pr-review status` fixture 对账 |
| 历史 run list | unit test 扫描多个 review dirs | JSON snapshot 断言 |
| malformed artifact | unit test 构造坏 JSON/schema | CLI human blocker 断言 |
| read-only boundary | integration before/after 文件内容快照 | mock provider 未调用 patch |
| command registration | command discovery unit test | `python -m ai_sdlc --help` fallback |
| no model/CI boundary | verify constraints + grep tests | 文档 surface 对账 |

## 开放问题

| 问题 | 决策 | 阻塞阶段 |
|------|------|----------|
| 是否在 WI-190 中列出 requirement/design/frontend loops | 否，只保留输出扩展位；实际适配另起 work item | 不阻塞 |
| `loop list` 默认是否只列 current type | P0 默认列 local PR review；保留 `--type local-pr-review` | 不阻塞 |
| malformed artifact 是否让命令整体 exit 1 | `status` 当前指针损坏时 exit 1；`list` 仅部分损坏时 exit 0 但记录 malformed count | execute |
| 是否读取 `LoopRun` 目录 | P0 以 `ReviewRun` 为 truth，因为 WI-189 的 current pointer 和 close-check 已消费该 artifact | 不阻塞 |

## 实施顺序

1. Batch 1：冻结 formal baseline，并同步 manifest/checkpoint。
2. Batch 2：实现 `core/loop_status.py` 只读 summary service。
3. Batch 3：注册 `ai-sdlc loop status/list` CLI 和 command discovery。
4. Batch 4：补充 docs、read-only regression、verify constraints 和执行日志。

## 回退方式

本能力是新增只读命令。若出现风险，可移除 `main.py` 中的 `loop` 注册和相关 tests，保留已落盘的 PR review artifact 不受影响。
