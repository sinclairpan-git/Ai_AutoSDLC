---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/plan.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
  - "specs/013-frontend-contract-observation-provider-baseline/spec.md"
  - "specs/013-frontend-contract-observation-provider-baseline/plan.md"
---
# 实施计划：Frontend Contract Runtime Attachment Baseline

**编号**：`014-frontend-contract-runtime-attachment-baseline` | **日期**：2026-04-03 | **规格**：specs/014-frontend-contract-runtime-attachment-baseline/spec.md

## 概述

本计划处理的是 `013` 下游的 frontend contract runtime attachment baseline，而不是继续扩张 `013` 的 provider/export truth。当前仓库已经在上游锁定并实现了：

- `011`：frontend contract models、artifact instantiation、drift helper、最小 contract-aware gate surface
- `012`：contract-aware verify helper、`verify_constraints` scoped attachment、`VerificationGate / VerifyGate` aggregation、CLI verify summary
- `013`：provider artifact contract、scanner candidate、canonical consumer migration、`scan` export surface

但“export surface 如何进入更正式的 runtime/orchestration 入口、active `spec_dir` 如何成为 attachment scope、失败和 freshness 如何在 runtime 被诚实暴露”仍缺少独立 child work item 去冻结：

- `scan` export 与 `run`/`runner`/`program` 的职责边界还没有正式定义
- runtime attachment 的安全默认值和禁止项还没有被单独锁定
- attachment scope、artifact locality 与 owner boundary 还没有统一到同一 formal truth 下
- 若继续直接编码，很容易把 provider/export、runtime attachment、verify mainline、program orchestration 与 registry 一起混成过宽工单

因此，本计划的目标是建立统一的 `Frontend Contract Runtime Attachment` formal baseline：

- 先冻结 runtime attachment 的 truth order
- 再冻结 attachment trigger、scope、failure honesty 与 ownership 顺序
- 最后给出后续 `core / cli / runner / tests` 的推荐文件面与测试矩阵

当前 formal baseline、`runtime attachment helper` 与 `runner verify-context wiring` 实现切片已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入下一批实现切片：`run CLI attachment summary surface`，把 runtime attachment 状态正式暴露到 `ai-sdlc run` 的终端用户面；不同时触碰 `program_cmd.py`、registry、scanner/provider 写入或新的 gate verdict。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Markdown formal docs  
**主要依赖**：`011` contract baseline、`012` verify integration baseline、`013` observation provider/export baseline、现有 `run` / `scan` / `program` 入口  
**现有基础**：

- [`../../src/ai_sdlc/core/frontend_contract_observation_provider.py`](../../src/ai_sdlc/core/frontend_contract_observation_provider.py) 已冻结 canonical observation artifact path/envelope
- [`../../src/ai_sdlc/scanners/frontend_contract_scanner.py`](../../src/ai_sdlc/scanners/frontend_contract_scanner.py) 已提供 scanner candidate provider
- [`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py) 已存在 `scan --frontend-contract-spec-dir` 的显式 export surface
- [`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py) 已能消费 canonical observation artifact
- [`../../src/ai_sdlc/cli/run_cmd.py`](../../src/ai_sdlc/cli/run_cmd.py) 与 [`../../src/ai_sdlc/core/runner.py`](../../src/ai_sdlc/core/runner.py) 已提供正式 pipeline/runtime 入口
- [`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py) 已提供 program-level orchestration surface

**目标平台**：AI-SDLC 框架仓库自身，面向 frontend contract runtime attachment / orchestration baseline  
**主要约束**：

- `014` 只冻结 runtime attachment baseline，不回写 `013` 的 provider/export truth
- runtime attachment 只能复用 canonical artifact contract，不得创造 runner/program 私有 observation 格式
- attachment scope 必须绑定 active `spec_dir` 或等价显式输入，不得静默跨 spec 写入
- attachment failure、artifact 缺失与 freshness 不可判断必须诚实暴露
- 当前阶段只允许 docs-only 落盘，不直接进入 `src/` / `tests/` 实现

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 runtime attachment 主线，不扩张到 registry、auto-fix、verify mainline 重写或 program execute 细节 |
| MUST-2 关键路径可验证 | attachment trigger、scope、failure honesty 与测试矩阵都必须可被文档和后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 runtime attachment 主线，当前变更仅作用于 `specs/014/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 将 runtime attachment baseline 落为 canonical truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 runtime attachment 合同，不引入具体前端 runtime 或项目级自动化写入 |

## 项目结构

### 文档结构

```text
specs/014-frontend-contract-runtime-attachment-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── cli/
│   ├── commands.py
│   ├── program_cmd.py
│   └── run_cmd.py
├── core/
│   ├── frontend_contract_observation_provider.py
│   ├── runner.py
│   └── verify_constraints.py
└── scanners/
    └── frontend_contract_scanner.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_runtime_attachment.py      # scope resolution / attachment policy / orchestration helper
│   └── runner.py                                    # verify-stage runtime attachment context
├── cli/
│   ├── commands.py                                  # only if explicit export handoff needs refinement
│   ├── run_cmd.py                                   # current slice: runtime attachment CLI summary surface
│   └── program_cmd.py                               # downstream only; not owned by first implementation slice
└── integrations/
    └── ...                                          # reserved for downstream work items only

tests/
├── unit/test_frontend_contract_runtime_attachment.py
├── unit/test_runner_confirm.py
├── integration/test_cli_run.py
└── integration/test_cli_program.py                  # downstream only if program-level attachment is explicitly enabled
```

## 开始执行前必须锁定的阻断决策

- runtime attachment 是 `013` provider/export truth 的下游独立真值层，不是 `013` 的附属 helper
- operator 显式 export 不等于 runtime attachment 已完成；自动化接线必须由下游实现工单显式承担
- attachment 只能复用 canonical artifact contract，并以 active `spec_dir` 作为 locality/scope 基线
- runtime 不得静默跨 spec 写入 observation artifact，不得在 scope 不明时自动扫描
- attachment failure、missing artifact 与 freshness 不可判断必须作为显式状态暴露
- program orchestration、registry 与 remediation 保持在下游 work item

未锁定上述决策前，不得进入 `014` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| runtime attachment policy | 定义 attachment 何时允许触发、何时只读消费、何时必须拒绝 | 不得改写 `013` provider contract 或 `012` verify truth |
| scope/locality baseline | 定义 active `spec_dir`、artifact locality 与 cross-spec safety 默认值 | 不得默许无 scope 自动写入 |
| explicit export handoff | 定义 `scan` export 面与 runtime attachment 的边界 | 不得把显式 export 直接冒充自动 orchestration |
| runner wiring baseline | 定义 `run` / `SDLCRunner` 若后续接入时的推荐触点与 guard | 不得在当前 docs-only batch 中引入真实 runtime side effects |
| program orchestration handoff | 明确 `program` surface 是否属于下游保留项 | 不得在当前 baseline 中默认启用 program-level attachment |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend contract runtime attachment 从 `013` 的后续建议动作收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/014/...` 文档改动。

### Phase 1：Runtime attachment truth freeze

**目标**：锁定 runtime attachment 在 `013 -> 014 -> future runtime execution` 主线中的 truth order。  
**产物**：scope baseline、entrypoint baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Attachment contract and failure honesty freeze

**目标**：锁定 attachment trigger、active `spec_dir`、artifact locality、failure honesty 与 ownership 顺序。  
**产物**：attachment contract baseline、scope/locality baseline、runtime guard baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Runtime attachment helper slice

**目标**：落下 runtime attachment 的最小共享 helper，先稳定 active `spec_dir` scope resolution、canonical artifact path resolution、missing/invalid artifact honesty、freshness 可判断性与显式 opt-in policy。
**产物**：`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`tests/unit/test_frontend_contract_runtime_attachment.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Runner verify-context wiring slice

**目标**：把 runtime attachment helper 以 read-only 方式接入 `SDLCRunner` 的 verify-stage context，让 active `014` scope 的 runtime attachment status 进入正式 pipeline context，但不改 gate verdict、CLI wording 或 program orchestration。
**产物**：`src/ai_sdlc/core/runner.py`、`src/ai_sdlc/core/frontend_contract_runtime_attachment.py`、`tests/unit/test_runner_confirm.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 6：Run CLI attachment summary surface slice

**目标**：把 active `014` scope 的 runtime attachment status 暴露到 `ai-sdlc run` 的终端输出，让 operator 在不读取 runner internal context 的前提下也能看到 `attached / missing_artifact / invalid_artifact` 等状态与最小 gap 摘要。
**产物**：`src/ai_sdlc/cli/run_cmd.py`、`tests/integration/test_cli_run.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `cli/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Runtime attachment truth freeze

**范围**：runtime attachment truth order、scope、non-goals、entrypoint separation。  
**影响范围**：后续 runtime attachment 子工单与 `013` export surface 边界。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Attachment contract and safety default freeze

**范围**：active `spec_dir`、artifact locality、attachment trigger、freshness/failure honesty 与 opt-in guard。  
**影响范围**：future runner wiring、explicit export reuse 与 runtime failure semantics。  
**验证方式**：contract review。  
**回退方式**：不创建 runtime side effects。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与 program/registry/remediation handoff。  
**影响范围**：后续 `core / cli / runner / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 runtime wiring 实现。

### 工作流 D：Runtime attachment helper slice

**范围**：active `spec_dir` 解析、canonical artifact path 解析、invalid/missing artifact honesty、freshness 可判断性与 explicit opt-in write policy。
**影响范围**：后续 `run_cmd.py` / `runner.py` wiring、read-only attachment consumption 与 runtime-side failure surfacing。
**验证方式**：`tests/unit/test_frontend_contract_runtime_attachment.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 scanner/provider 写入，不引入 `run` / `program` runtime side effects。

### 工作流 E：Runner verify-context wiring slice

**范围**：active `014` scope 的 runtime attachment payload 进入 `SDLCRunner._build_context("verify", ...)`，保持 read-only，不改 gate verdict 或 CLI surface。
**影响范围**：runner verify-stage context、后续 gate/runtime consumer 的 context 可见性，以及 active/non-active work item 的 scoped attachment 行为。
**验证方式**：`tests/unit/test_runner_confirm.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不修改 `run_cmd.py` / `program_cmd.py` 用户面，不触发 scanner/provider 写入。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| runtime attachment truth order | 文档交叉引用检查 | 人工审阅 |
| explicit export vs runtime attachment separation | formal wording review | 人工审阅 |
| active `spec_dir` scope/locality clarity | contract review | 文件面/路径对账 |
| failure honesty / freshness guard | 语义对账 | 测试矩阵回挂 |
| downstream handoff clarity | file-map review | 人工审阅 |
| runtime attachment helper correctness | `uv run pytest tests/unit/test_frontend_contract_runtime_attachment.py -q` | attachment status / policy review |
| runner verify-context attachment correctness | `uv run pytest tests/unit/test_runner_confirm.py -q` | verify context payload review |
| run CLI attachment summary correctness | `uv run pytest tests/integration/test_cli_run.py -q -k "runtime_attachment"` | terminal wording / scoped rendering review |

## 当前建议的下游实现起点

- 先落 `core/frontend_contract_runtime_attachment.py`，把 scope resolution、artifact path resolution、missing/stale honesty 与 opt-in policy 固定成共享 helper
- 再决定是否把该 helper 接到 `run_cmd.py` / `runner.py`
- `program_cmd.py` 仍应作为后续保留项，除非前两步已经把 ownership 和 guard 明确稳定
