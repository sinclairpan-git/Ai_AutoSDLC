---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/018-frontend-gate-compatibility-baseline/spec.md"
  - "specs/019-frontend-program-orchestration-baseline/spec.md"
---
# 实施计划：Frontend Program Execute Runtime Baseline

**编号**：`020-frontend-program-execute-runtime-baseline` | **日期**：2026-04-03 | **规格**：specs/020-frontend-program-execute-runtime-baseline/spec.md

## 概述

本计划处理的是 `019` 之后的 program-level frontend execute runtime baseline，而不是继续扩张 `019` 的 dry-run/status responsibility。当前仓库已经在上游锁定并实现了：

- `014`：runtime attachment helper 与 `run` CLI summary
- `018`：frontend gate summary、verify/gate aggregation 与 CLI summary
- `019`：program-level readiness aggregation、`program status` 与 `program integrate --dry-run` frontend surface
- `program integrate --execute`：close/dependency/dirty-tree gate

但最后一段“program execute 如何消费 frontend readiness truth，并在什么时候阻断 / recheck / 仅给 remediation hint”仍缺少独立 child work item 去冻结：

- execute preflight 还没有 formal baseline 说明它应如何消费 per-spec frontend readiness
- step-level recheck handoff 还没有进入 canonical truth
- remediation hint 与 auto-fix engine 的边界还没有被 program execute 语义冻结
- 若继续直接编码，容易把 execute runtime、recheck、remediation 与 auto-fix 混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Program Execute Runtime Baseline`：

- 先冻结 execute runtime 的 truth order 与 non-goals
- 再冻结 execute preflight、recheck handoff 与 remediation hint 的 responsibility
- 最后给出后续 `core / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline、`program frontend execute preflight` 与 execute CLI frontend gate surface 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入下一批实现切片：`program frontend recheck handoff`，先在 `ProgramService` 中落 per-step recheck handoff truth；随后再进入 execute CLI / report surface。当前仍不直接进入 recheck loop runtime 或 auto-fix engine。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`019` frontend program orchestration baseline、`018` gate / recheck baseline、现有 `ProgramService` / `program_cmd.py` execute surface  
**主要约束**：

- execute runtime 只能消费既有 per-spec readiness truth，不得另造 program 私有 execute truth
- 当前阶段不默认启用 scanner/provider 写入、auto-attach、auto-fix、registry 或 cross-spec writeback
- recheck 是 bounded handoff，不是后台 loop
- remediation hint 必须诚实表达，但不等于默认修复

## 项目结构

```text
specs/020-frontend-program-execute-runtime-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── cli/
│   └── program_cmd.py
├── core/
│   ├── frontend_contract_runtime_attachment.py
│   ├── frontend_gate_verification.py
│   └── program_service.py
└── gates/
    └── pipeline_gates.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   └── program_service.py                   # current slice: frontend recheck handoff
└── cli/
    └── program_cmd.py                       # next slice: execute recheck handoff / report surface

tests/
├── unit/test_program_service.py
└── integration/test_cli_program.py
```

## 开始执行前必须锁定的阻断决策

- program execute 只消费 `019` per-spec readiness truth 与 `018` recheck boundary，不另造 program 私有 execute truth
- execute blocker、recheck_required 与 remediation hint 必须按 spec 粒度暴露
- `program integrate --execute` 可以暴露 frontend preflight / recheck handoff，但不得默认触发 scanner/provider 写入
- auto-fix、registry、writeback 与 remediation runtime 仍留在下游 work item
- 当前 baseline 不改写 manifest 语义，只在既有 execute surface 上冻结 frontend responsibility

未锁定上述决策前，不得进入 `020` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| execute preflight gate | 定义 execute 前如何消费 per-spec frontend readiness truth | 不得改写 `019` readiness truth |
| recheck handoff | 定义 execute step 之后的 frontend recheck 触发与提示边界 | 不得把 recheck 扩张成后台 loop |
| remediation hint | 定义失败/未接线时的最小 remediation guidance | 不得默认触发 auto-fix 或 writeback |
| downstream handoff | 定义推荐文件面、测试矩阵与 future auto-fix child work item 边界 | 不得把 auto-fix engine 混进当前 baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend program execute runtime 从 `019` downstream suggestion 收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/020/...` 文档改动。

### Phase 1：Execute truth freeze

**目标**：锁定 program execute runtime 在 `014 / 018 / 019 -> 020 -> future auto-fix` 主线中的 truth order。  
**产物**：execute truth baseline、non-goals baseline、recheck/remediation baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Execute / recheck / remediation responsibility freeze

**目标**：锁定 execute preflight、step-level recheck handoff 与 remediation hint 的 responsibility 与 honesty 语义。  
**产物**：execute baseline、recheck baseline、remediation hint baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、downstream auto-fix handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Program frontend execute preflight slice

**目标**：在 `ProgramService` 中落 per-spec frontend execute gate，统一消费 `019` readiness truth，并将 frontend execute blockers 纳入 `program --execute` preflight。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Program execute CLI frontend gate surface slice

**目标**：把 frontend execute preflight 的阻断与 hint 暴露到 `program integrate --execute` 的终端输出，使 operator 能直接看到 frontend execute gate，不进入 recheck loop runtime。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

### Phase 6：Program frontend recheck handoff slice

**目标**：在 `ProgramService` 中为 execute-ready integration steps 落下 frontend recheck handoff truth，提供 recheck_required、reason、recommended_commands 与 source linkage，而不进入 recheck loop runtime。
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 7：Program execute CLI/frontend report recheck surface slice

**目标**：把 frontend recheck handoff 暴露到 `program integrate --execute` 的终端输出和 report 中，让 operator 在 execute gate 通过后能直接看到后续复查要求，而不进入 recheck loop runtime。
**产物**：`src/ai_sdlc/cli/program_cmd.py`、`tests/integration/test_cli_program.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Execute truth freeze

**范围**：execute truth order、non-goals、spec-granularity execute gate 与 recheck/remediation boundary。  
**影响范围**：后续 `program --execute` 的 frontend guard surface 与 downstream auto-fix child work item。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Execute / recheck / remediation responsibility freeze

**范围**：execute preflight、step-level recheck handoff、failure honesty 与 remediation hint 规则。  
**影响范围**：后续 `program_service.py`、`program_cmd.py` 与 operator-facing execute runtime surface。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 downstream auto-fix handoff。  
**影响范围**：后续 `core / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 auto-fix runtime 实现。

### 工作流 D：Program frontend execute preflight slice

**范围**：per-spec frontend execute gate、frontend execute blockers 与 source linkage reuse。
**影响范围**：后续 `program integrate --execute` 的 frontend preflight data source。
**验证方式**：`tests/unit/test_program_service.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不改 `program_cmd.py` 的 execute surface。

### 工作流 E：Program execute CLI frontend gate surface slice

**范围**：`program integrate --execute` 的 frontend gate 输出与最小 remediation hint。
**影响范围**：operator-facing execute preflight，可见性提升但不新增 auto-fix / recheck loop。
**验证方式**：`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不修改 dry-run / status truth。

### 工作流 F：Program frontend recheck handoff slice

**范围**：per-step frontend recheck handoff、recommended verification commands 与 source linkage reuse。
**影响范围**：后续 execute CLI / report 的 frontend recheck data source。
**验证方式**：`tests/unit/test_program_service.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不改 execute gate verdict 语义。

### 工作流 G：Program execute CLI/frontend report recheck surface slice

**范围**：`program integrate --execute` 的 frontend recheck handoff 输出与 report surface。
**影响范围**：operator-facing execute follow-up guidance，可见性提升但不新增 runtime side effect。
**验证方式**：`tests/integration/test_cli_program.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不进入 recheck loop 或 auto-fix runtime。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| execute truth order | 文档交叉引用检查 | 人工审阅 |
| per-spec execute gate granularity | formal wording review | 人工审阅 |
| recheck handoff clarity | contract review | file-map review |
| remediation hint honesty | formal docs review | 人工审阅 |
| downstream auto-fix handoff clarity | tasks / plan 对账 | `uv run ai-sdlc verify constraints` |
| program frontend execute preflight correctness | `uv run pytest tests/unit/test_program_service.py -q` | execute gate payload / blockers review |
| program execute CLI frontend gate correctness | `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / exit-code review |
| program frontend recheck handoff correctness | `uv run pytest tests/unit/test_program_service.py -q` | recheck payload / source linkage review |
| program execute CLI/frontend report recheck surface correctness | `uv run pytest tests/integration/test_cli_program.py -q` | terminal wording / report review |

## 当前建议的下游实现起点

- 先在 `program_service.py` 定义 per-spec frontend execute gate
- 再把 execute preflight / remediation hint 暴露到 `program integrate --execute`
- 再在 `program_service.py` 定义 execute-ready step 的 frontend recheck handoff
- 最后把 recheck handoff 暴露到 execute CLI / report surface
- auto-fix engine 与 writeback runtime 仍应作为后续 guarded child work item 单独承接
