---
related_doc:
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Program Final Proof Archive Project Cleanup Mutation Baseline

**编号**：`051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline` | **日期**：2026-04-04 | **规格**：specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/spec.md

## 概述

本计划不再把 `051` 当作“继续补 real cleanup mutation implementation”的工单，而是把当前事实冻结为 formal baseline：

- `047` 已冻结 orchestration baseline
- `048` 已冻结 archive artifact baseline
- `049` 已冻结 thread archive baseline
- `050` 已冻结 project cleanup request/result/artifact baseline，并明确当前 execute 语义仍是 `deferred`

继续往下做真实 mutation 的前提，本该是“已经存在 explicit cleanup target formal truth”。但对 `050` spec、当前 `ProgramService`/CLI tests、`.ai-sdlc/` 面和现有路径证据做完只读审阅后，没有发现任何被正式批准的 cleanup target 集合。因此，`051` 当前阶段的目标是：

- 冻结 `050 -> 051` truth order
- 冻结 “当前 allowlist 为空集合” 这一结论
- 冻结 future child work item 的接力顺序

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown/YAML artifact  
**主要依赖**：`050` cleanup artifact truth、现有 `ProgramService` / `program_cmd.py` / tests 作为只读证据面  
**主要约束**：

- `051` 只能消费 `050` cleanup artifact truth
- 当前没有任何 formalized cleanup target，可执行 mutation allowlist 必须为空
- `050` 的 deferred honesty boundary 继续有效
- 当前 work item 只写 `specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/`
- `src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py` 仅作为 future touchpoints，不在本批改动

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| Formal docs must be canonical before implementation | 当前先完成边界冻结，不伪造实现 |
| Single-source-of-truth downstream handoff | 明确 `050` cleanup artifact 是唯一上游真值 |
| Explicit confirmation on operator-facing mutation action | 当前没有被批准的 mutation target，因此不会进入真实 execute |
| No hidden side effects in cleanup baseline | 当前 work item 只做文档与只读校验，不触碰 `src/` / `tests/` |

## 项目结构

### 文档结构

```text
specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline/
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

### Phase 0：Formal baseline freeze

**目标**：把 `051` 从“潜在实现项”收紧为单独 canonical boundary-freeze work item。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：formal docs 对账。  
**回退方式**：仅回退 `specs/051/...` 文档改动。

### Phase 1：Evidence review and empty-allowlist freeze

**目标**：审阅 `050` spec、现有 service/tests 与仓库证据面，并冻结“当前 allowlist 为空集合”的结论。  
**产物**：evidence summary、empty allowlist baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md / task-execution-log.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Future handoff freeze

**目标**：给未来 child work item 明确接力条件与真值顺序。  
**产物**：future handoff contract、future touchpoints、next-step sequence。  
**验证方式**：handoff review。  
**回退方式**：仅调整 planning baseline，不写代码。

### Phase 3：Readonly verification freeze

**目标**：用只读校验确认 `051` 当前交付完整，且没有越权实现。  
**产物**：fresh verification records、append-only execution log。  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check -- specs/051-frontend-program-final-proof-archive-project-cleanup-mutation-baseline`。  
**回退方式**：仅回退 `specs/051/...` 文档改动。

## 未来 child work item 的接力顺序

如果后续真的要进入 real cleanup mutation，实现顺序必须先补 formal truth，再补代码：

1. formalize explicit cleanup target truth，并把它纳入 `050` 下游单一真值链
2. 在 `tests/unit/test_program_service.py` 写 failing tests，固定 cleanup target / result 语义
3. 在 `src/ai_sdlc/core/program_service.py` 落最小 service 实现
4. 在 `tests/integration/test_cli_program.py` 写 failing integration tests，固定 operator-facing output
5. 在 `src/ai_sdlc/cli/program_cmd.py` 落 CLI surface

在上述前置条件完成之前，`051` 不进入 `ProgramService`、CLI 或 tests 的任何实现修改。
