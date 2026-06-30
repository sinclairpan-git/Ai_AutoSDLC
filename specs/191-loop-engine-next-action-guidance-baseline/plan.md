# 实施计划：Loop Engine Next Action Guidance Baseline

**编号**：`191-loop-engine-next-action-guidance-baseline`
**日期**：2026-06-30
**规格**：`specs/191-loop-engine-next-action-guidance-baseline/spec.md`

## 概述

本计划把 WI-190 的 `next_action` 字符串升级为结构化 Next Action Guidance。实现重点是新增只读 guidance 模型、在 `get_loop_status()` / `list_loops()` 中根据现有 local PR review artifact 推导下一步，并在 CLI human/json 输出中展示可执行命令、原因、影响范围和证据。

本 WI 不改变 `pr-review` 状态机，不新增执行器，不让 `loop status/list` 调用模型或写 artifact。它只把已经落盘的 `ReviewRun.status`、`ReviewRun.next_action`、unresolved counts、artifact paths 和 blocker 转换为更清晰的导航信息。

## 技术背景

**语言/版本**：Python 3.11+  
**CLI**：Typer + Rich，已有入口 `src/ai_sdlc/cli/loop_cmd.py`。  
**模型**：Pydantic v2，新增 guidance 模型放在 `src/ai_sdlc/core/loop_status.py`。  
**存储**：只读读取 `.ai-sdlc/reviews/pr/current-review.json` 与 `.ai-sdlc/reviews/pr/*/review-run.json`；不写入 `.ai-sdlc/`。  
**测试**：`tests/unit/test_loop_status.py`、`tests/integration/test_cli_loop.py`、必要时更新 `tests/unit/test_verify_constraints.py`。  
**约束**：保持 `next_action` 兼容；新增字段必须是 additive JSON change。

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 用户可恢复 | `loop status/list` 输出推荐命令、原因、影响和证据，降低中断恢复成本。 |
| 只读状态面 | guidance 只读推导，不执行下一步、不调用 provider、不写 artifact。 |
| 本地模型边界 | guidance 可标注后续 `pr-review rerun/start` 可能调用本地独立 review agent，但 loop 命令自身不得调用模型。 |
| 兼容与可审计 | 保留 `next_action`，新增 `next_guidance`，所有判断来自 artifact 字段。 |
| 小白友好 | no current 时优先 `doctor`，blocked/needs_user 时优先 blocker 和人工处理动作。 |

## 项目结构

### 文档结构

```text
specs/191-loop-engine-next-action-guidance-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/loop_status.py
src/ai_sdlc/cli/loop_cmd.py
tests/unit/test_loop_status.py
tests/integration/test_cli_loop.py
tests/unit/test_verify_constraints.py
README.md
docs/pull-request-checklist.zh.md
```

## 输出合同

### 结构化 guidance 字段

```text
next_guidance
├── command
├── reason
├── requires_model
├── writes_artifacts
├── writes_code
├── safety
├── evidence[]
└── alternatives[]
```

字段说明：

1. `command`：首选下一步命令；无法安全给出命令时为空字符串。
2. `reason`：面向普通用户的推荐原因。
3. `requires_model`：下一步命令是否可能调用本地独立 review agent / 用户配置模型；仅描述后续命令，不代表当前 `loop` 命令会调用模型。
4. `writes_artifacts`：下一步命令是否会写 `.ai-sdlc/` artifact。
5. `writes_code`：下一步命令是否会直接修改业务代码；本地 PR review P0 预期为 false。
6. `safety`：`safe_read_only`、`writes_review_artifacts`、`may_call_local_review_agent`、`needs_user`、`blocked`、`no_action` 等受控字符串。
7. `evidence`：repo-relative artifact path 或字段依据。
8. `alternatives`：可选命令列表。

## 阶段计划

### Phase 0：formal baseline freeze

**目标**：冻结 WI-191 的 PRD、计划、任务和初始 execution log。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：`uv run ai-sdlc workitem guard` 能发现下一条可执行任务；`git diff --check`。  
**回退方式**：仅回退 `specs/191-loop-engine-next-action-guidance-baseline/` 与 manifest/checkpoint 变更。

### Phase 1：core guidance model

**目标**：新增 guidance 数据模型和推导函数。  
**产物**：`src/ai_sdlc/core/loop_status.py`、`tests/unit/test_loop_status.py`。  
**验证方式**：unit tests 覆盖 no current、fresh needs_fix、post-fix needs_fix、passed、blocked/needs_user、closed、list item。
**回退方式**：移除 additive `next_guidance` 字段和新增测试。

### Phase 2：CLI human/json 输出

**目标**：让 `loop status/list` human 输出展示 next guidance，同时 JSON 稳定输出新增字段。  
**产物**：`src/ai_sdlc/cli/loop_cmd.py`、`tests/integration/test_cli_loop.py`。  
**验证方式**：integration tests 断言 human 包含 `Next command`、`Why`、`Model call`、`Writes artifacts`、`Writes code`、`Evidence`。  
**回退方式**：恢复 CLI 输出为 WI-190 格式，但保留 core additive model 可单独回退。

### Phase 3：docs and constraints

**目标**：对齐 README、PR checklist 和 verify constraints，说明 guidance 只读边界。  
**产物**：`README.md`、`docs/pull-request-checklist.zh.md`、`src/ai_sdlc/core/verify_constraints.py`、相关测试。  
**验证方式**：`uv run pytest tests/unit/test_verify_constraints.py -q`、`uv run ai-sdlc verify constraints`。  
**回退方式**：回退文档和 constraints surface，不影响 core guidance。

### Phase 4：final regression and closeout

**目标**：完成 focused regression、execution log、handoff 和 close-check。  
**产物**：`task-execution-log.md`、`tasks.md` 状态同步、handoff。  
**验证方式**：focused test matrix、`git diff --check`、`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem close-check --wi specs/191-loop-engine-next-action-guidance-baseline`。  
**回退方式**：若 regression 失败，回退最新 batch 并保留 execution log 记录。

## 工作流计划

### 工作流 A：用户查看当前下一步

```text
ai-sdlc loop status
ai-sdlc loop status --json
```

预期：

1. human 输出保留 `Result` / `Next`，并新增 guidance 说明。
2. JSON 顶层有 `next_action` 和 `next_guidance`。
3. 当前 loop summary 内也有 `next_guidance`。

### 工作流 B：用户列出历史 run

```text
ai-sdlc loop list
ai-sdlc loop list --json
```

预期：

1. 每个合法 item 展示独立 guidance；current item 可以显示 PR-review follow-up，非 current item 只显示 inspect-only guidance。
2. malformed artifact 仍通过 `artifact_errors` 暴露，并提供顶层 guidance。
3. list 仍不写入 `.ai-sdlc/`。

### 工作流 C：本地模型边界说明

```text
ai-sdlc loop status
```

预期：

1. 如果下一步是 `pr-review rerun/start`，guidance 标明后续命令可能调用本地独立 review agent。
2. 当前 `loop status` 本身不调用模型，不解析用户当前模型，不启动 provider。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| no current guidance | unit test 覆盖 status 和有历史 run 的 list 顶层 guidance | CLI JSON integration |
| needs_fix guidance | unit test 覆盖 fresh fix / post-fix rerun | human output assertion |
| passed/closed guidance | unit test | final report path fixture |
| blocked/needs_user guidance | unit test | malformed pointer fixture |
| list current pointer repair guidance | unit test | `loop list --json` integration |
| list item guidance | unit test 覆盖 current actionable / non-current inspect-only | `loop list --json` integration |
| read-only boundary | before/after snapshot test | provider runner patch 未调用 |
| docs constraints | verify constraints unit test | `uv run ai-sdlc verify constraints` |

## 开放问题

| 问题 | 决策 | 阻塞阶段 |
|------|------|----------|
| no current 时是否直接建议 start | 否，首选 doctor，start 作为 alternative。 | 不阻塞 |
| guidance 是否执行下一步 | 否，本 WI 只做只读导航。 | 不阻塞 |
| 是否新增 loop resume 命令 | 否，另起 work item。 | 不阻塞 |
| 是否为 requirement/design/frontend loop 生成专用 guidance | 本 WI 仅保证通用模型可扩展，专用逻辑另起 work item。 | 不阻塞 |

## 实施顺序建议

1. 冻结 formal docs，链接 checkpoint，确认 `workitem guard` 进入 T21。
2. 在 `loop_status.py` 增加 guidance 模型和推导函数。
3. 扩展 unit tests 覆盖状态矩阵和 read-only snapshot。
4. 扩展 `loop_cmd.py` human 输出和 integration tests。
5. 更新 README/checklist/verify constraints。
6. 执行 focused regression、constraints、close-check，更新 execution log 和 handoff。
