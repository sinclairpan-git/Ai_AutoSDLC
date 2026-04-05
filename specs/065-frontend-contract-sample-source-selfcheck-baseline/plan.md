---
related_doc:
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/014-frontend-contract-runtime-attachment-baseline/plan.md"
---
# 实施计划：Frontend Contract Sample Source Selfcheck Baseline

**编号**：`065-frontend-contract-sample-source-selfcheck-baseline` | **日期**：2026-04-06 | **规格**：specs/065-frontend-contract-sample-source-selfcheck-baseline/spec.md

## 概述

本计划处理的是“框架仓库内置 sample frontend source tree 作为显式 self-check 输入源”的 formal baseline，而不是重写 `012` verify、`013` scanner/provider/export、或 `014` runtime attachment。当前仓库已经具备：

- `scan <source-root> --frontend-contract-spec-dir <spec-dir>` 的显式 export surface
- canonical `frontend-contract-observations.json` artifact contract
- `verify constraints` / `program` 对 artifact 的既有消费路径

缺少的是一层独立 formal truth，来冻结“框架仓库如何在不依赖外部前端项目的前提下自包含 self-check，同时又不污染 production semantics”。因此，本计划的目标是：

- 先冻结 sample source 的角色、合法落点、truth order 与 honesty 边界
- 再冻结 fixture 结构、稳定输出语义与 `pass / drift / gap` 自检矩阵
- 最后冻结 remediation wording 与 `program` no-implicit-scan 约束的实现切片

当前允许推进的是 **formal baseline docs-only freeze**。后续进入 `src/` / `tests/` 级实现前，必须继续遵守：sample 只是显式输入源，不是 runtime fallback。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs、最小前端 fixture 源码文件（`.vue` / `.tsx`）  
**主要依赖**：`012` verify integration baseline、`013` scanner/provider/export baseline、`014` runtime attachment baseline、现有 `scan` / `verify` / `program` surface  
**存储**：

- canonical artifact：`specs/<WI>/frontend-contract-observations.json`
- sample fixture：`tests/fixtures/frontend-contract-sample-src/**`

**测试**：`pytest` unit/integration、`uv run ai-sdlc verify constraints`  
**目标平台**：AI-SDLC 框架仓库自身，面向自包含 frontend contract self-check  
**主要约束**：

- sample source 只能位于测试夹具路径；运行时代码不得写死 fixture 默认路径
- scanner/export 必须始终要求显式 `source_root`
- `verify/program` 只消费 artifact，不允许 implicit scan/materialization
- invalid source root、empty observations、missing artifact、drift 语义必须清晰分层
- runtime remediation wording 只能使用 `<frontend-source-root>` 占位符

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 sample-source self-check 主线，不扩张到新命令、新 provider、自动仓库发现或 runtime fallback |
| MUST-2 关键路径可验证 | fixture、scanner、artifact、verify、program wording 都有对应单测/集成测试与 fresh verification 命令 |
| MUST-3 范围声明与回退 | 每个实现批次都锁定精确文件面；回退时可按批次独立回退 |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 冻结 formal truth，并在后续批次追加归档 |
| MUST-5 产品代码与开发框架隔离 | sample source 仅存在于测试夹具，不把仓库自检输入源混成 runtime 默认依赖 |

## 项目结构

### 文档结构

```text
specs/065-frontend-contract-sample-source-selfcheck-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的实现触点

```text
src/ai_sdlc/
├── cli/
│   └── commands.py
├── core/
│   ├── frontend_contract_observation_provider.py
│   ├── frontend_contract_runtime_attachment.py
│   ├── program_service.py
│   └── verify_constraints.py
└── scanners/
    └── frontend_contract_scanner.py

tests/
├── integration/
│   ├── test_cli_program.py
│   ├── test_cli_scan.py
│   └── test_cli_verify_constraints.py
└── unit/
    ├── test_frontend_contract_scanner.py
    └── test_program_service.py
```

### 推荐的后续实现触点

```text
tests/fixtures/frontend-contract-sample-src/
├── match/
│   ├── AccountEdit.tsx
│   └── UserCreate.vue
├── drift/
│   └── UserCreate.vue
└── empty/
    └── Plain.tsx

src/ai_sdlc/
├── core/
│   └── program_service.py
└── scanners/
    └── frontend_contract_scanner.py

tests/
├── integration/
│   ├── test_cli_program.py
│   ├── test_cli_scan.py
│   └── test_cli_verify_constraints.py
└── unit/
    ├── test_frontend_contract_scanner.py
    └── test_program_service.py
```

## 开始执行前必须锁定的阻断决策

- sample source 不是 runtime fallback；`verify` 与 `program` 不得感知 fixture 路径
- `scan` export 必须继续要求显式 `source_root`
- invalid source root、valid-but-empty source root、missing artifact、drift 必须保持独立语义
- `recommended_commands` 不得继续使用 `scan .`
- `tests/fixtures/frontend-contract-sample-src/**` 只属于测试和文档示例，不得泄漏到运行时默认路径

未锁定上述决策前，不得进入 `src/` / `tests/` 级实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| sample fixture set | 提供最小正例、drift 反例与 empty source root | 不得把 fixture 提升为 runtime 默认输入 |
| scanner/export semantics | 维持显式 `source_root`、稳定排序与 empty-result envelope | 不得偷偷 fallback 到 sample 或静默吞掉 invalid source root |
| verify/program consumers | 继续只消费 `spec_dir` 中的 canonical artifact | 不得因为 fixture 存在而自动 materialize 或自动转绿 |
| remediation wording | 用 `<frontend-source-root>` 诚实表达 operator 输入要求 | 不得泄漏 fixture 实际路径或继续暗示 `scan .` |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 sample-source self-check 语义收敛为独立 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/065/...` 文档改动。

### Phase 1：Sample fixture and scanner stability

**目标**：落下最小 sample source fixture，并固定 scanner 的稳定排序与 empty-result 语义。  
**产物**：`tests/fixtures/frontend-contract-sample-src/**`、`tests/unit/test_frontend_contract_scanner.py`。  
**验证方式**：定向 `pytest` + `git diff --check`。  
**回退方式**：仅回退 fixture 与 scanner 单测改动。

### Phase 2：CLI scan / verify self-check matrix

**目标**：固定 `scan` export 对 sample fixture 的显式行为，并覆盖 invalid source root、empty artifact、pass/drift/gap 集成语义。  
**产物**：`tests/integration/test_cli_scan.py`、`tests/integration/test_cli_verify_constraints.py`。  
**验证方式**：定向 `pytest` + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退相关集成测试改动。

### Phase 3：Program honesty and remediation wording

**目标**：把 `program` remediation wording 从 `scan .` 收紧为显式 `<frontend-source-root>`，并证明 `program` 层不会隐式 scan/materialize。  
**产物**：`src/ai_sdlc/core/program_service.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py`。  
**验证方式**：定向 `pytest`、`uv run ai-sdlc verify constraints`、`git diff --check`。  
**回退方式**：仅回退 `program_service` 与相关测试改动。

### Phase 4：Fresh verification and archive

**目标**：执行 fresh verification，更新 execution log，并为后续 execute/close 提供稳定基线。  
**产物**：`task-execution-log.md`。  
**验证方式**：定向 `pytest`、`uv run ai-sdlc verify constraints`、必要的 `ruff` / `git diff --check`。  
**回退方式**：不引入新实现，仅补归档。

## 工作流计划

### 工作流 A：Formal truth freeze

**范围**：sample source 角色、合法落点、truth order、non-goals、honesty guardrails。  
**影响范围**：后续 fixture、scanner、verify、program self-check 实现。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不触发代码实现。

### 工作流 B：Sample fixture and scanner behavior

**范围**：`tests/fixtures/frontend-contract-sample-src/**`、stable ordering、stable empty-result envelope。  
**影响范围**：scanner/export 对 sample source 的最小自检主线。  
**验证方式**：`uv run pytest tests/unit/test_frontend_contract_scanner.py -q`。  
**回退方式**：不改 verify/program runtime semantics。

### 工作流 C：Self-check matrix on scan and verify

**范围**：invalid source root、empty artifact、pass/drift/gap 集成行为。  
**影响范围**：`scan` export surface 与 `verify constraints` 的主线自检证明。  
**验证方式**：`uv run pytest tests/integration/test_cli_scan.py tests/integration/test_cli_verify_constraints.py -q`。  
**回退方式**：不引入新 CLI 命令。

### 工作流 D：Program honesty and remediation wording

**范围**：`program_service` 推荐命令占位符、`program` no-implicit-scan 保证。  
**影响范围**：`program status / plan / integrate --dry-run` 的 operator 提示面。  
**验证方式**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`。  
**回退方式**：不改变 `verify` 与 `program` 的 truth model。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| sample source 合法落点与 non-goals | formal docs review | 人工审阅 |
| scanner stable ordering / empty-result envelope | `uv run pytest tests/unit/test_frontend_contract_scanner.py -q` | artifact 对账 |
| invalid source root 显式失败 | `uv run pytest tests/integration/test_cli_scan.py -q` | CLI output review |
| pass / drift / gap 语义分离 | `uv run pytest tests/integration/test_cli_verify_constraints.py -q` | verification report review |
| program no-implicit-scan | `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q` | CLI output review |
| remediation placeholder honesty | `uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q` | source diff review |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| 是否额外补一份 fixture 目录 README 解释 sample 角色 | 可选 | 不阻塞 Phase 1 |

## 实施顺序建议

1. 先冻结 `065` formal docs，确保 guardrail、file map、验证矩阵不再依赖对话记忆
2. 再落 sample fixture 与 scanner 稳定性测试
3. 然后补 `scan` / `verify` 的 `pass / drift / gap` 自检矩阵
4. 最后收紧 `program_service` remediation wording，并证明 `program` 不会隐式 scan
