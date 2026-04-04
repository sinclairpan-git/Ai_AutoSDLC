---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Program Final Proof Archive Explicit Cleanup Targets Baseline

**编号**：`052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline` | **日期**：2026-04-04 | **规格**：specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md

## 概述

`046 -> 047 -> 048 -> 049 -> 050` 已经把 final proof archive 的 closure artifact、orchestration、archive artifact、thread archive 与 project cleanup baseline 依次固定。`051` 则冻结了当前边界：由于缺少显式 cleanup target truth，cleanup mutation allowlist 仍为空集合。

`052` 的任务不是继续写 cleanup code，而是先把 cleanup target formal truth 设计清楚，确保下一子项在进入 failing tests 前已经拥有单一、可审计、可消费的 target truth surface。当前 work item 因此保持 docs-only：

- 明确 `cleanup_targets` 必须并入 `050` cleanup artifact
- 明确 cleanup target entry 的字段与校验约束
- 明确 missing / empty / listed 三种 target truth 语义
- 明确 future implementation 的 test-first handoff

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`050` cleanup artifact baseline、`051` boundary freeze、canonical `workitem init` scaffold  
**主要约束**：

- `052` 不得新建第二套 cleanup artifact truth
- `052` 不得越权修改 `ProgramService`、CLI 或 tests
- cleanup target 必须是显式字段，不允许实现阶段推断
- 当前 work item 只写 `specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/`

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Formal docs must be canonical before implementation | 当前先冻结 cleanup target truth，代码修改继续后移 |
| Single-source-of-truth downstream handoff | `cleanup_targets` 被固定到 `050` cleanup artifact，不创建旁路 truth |
| Explicit confirmation on operator-facing mutation action | 本 work item 只定义 truth；未来执行仍需显式确认 |
| No hidden side effects in cleanup baseline | 当前只补 formal docs 与只读验证，不执行 mutation |

## 项目结构

### 文档结构

```text
specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### Future Touchpoints

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：Scaffold and scope freeze

**目标**：用 canonical `workitem init` 生成 `052`，并把 work item 范围收紧到 cleanup target formal truth。  
**产物**：scaffolded docs、scope freeze。  
**验证方式**：目录与文档对账。  
**回退方式**：仅回退 `specs/052/...` 文档改动。

### Phase 1：Cleanup target truth shape freeze

**目标**：冻结 `cleanup_targets` 的归属、字段、排序与 target-state 语义。  
**产物**：truth surface、field contract、missing/empty/listed semantics。  
**验证方式**：`spec.md` / `plan.md` / `tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Approval and non-inference freeze

**目标**：冻结 provenance / approval 口径，并明确禁止 inferred cleanup target。  
**产物**：non-goals、guardrails、future review baseline。  
**验证方式**：formal docs review。  
**回退方式**：仅调整 `specs/052/...` 文档。

### Phase 3：Future implementation handoff

**目标**：把后续实现顺序固定为 test-first handoff。  
**产物**：future touchpoints、implementation order、verification plan。  
**验证方式**：handoff review。  
**回退方式**：不修改任何代码面。

### Phase 4：Readonly verification

**目标**：确认 `052` 已按框架完成 formal truth freeze，且没有越界到实现。  
**产物**：fresh verification records、append-only execution log。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check -- specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline`。  
**回退方式**：仅回退 `specs/052/...` 文档改动。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `cleanup_targets` 被固定为 `050` cleanup artifact truth | `spec.md` 对账 | `plan.md` 对账 |
| missing / empty / listed 语义被明确区分 | `spec.md` 对账 | `tasks.md` 对账 |
| 当前 work item 未越界到代码实现 | `git diff --check -- specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline` | execution log review |

## 后续实现顺序

如果继续往下推进 real cleanup mutation，顺序必须是：

1. 在 `tests/unit/test_program_service.py` 写 failing tests，固定 `cleanup_targets` 消费语义与 `missing/empty/listed` 分支
2. 在 `src/ai_sdlc/core/program_service.py` 落最小 service 实现
3. 在 `tests/integration/test_cli_program.py` 写 failing integration tests，固定 operator-facing 输出与确认文案
4. 在 `src/ai_sdlc/cli/program_cmd.py` 落 CLI 实现
5. 仅在上述完成后，再讨论真实 mutation 的更细粒度 guardrail

在此之前，`052` 不触碰 `src/` 或 `tests/`。
