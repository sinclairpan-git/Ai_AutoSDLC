---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/011-frontend-contract-authoring-baseline/spec.md"
  - "specs/011-frontend-contract-authoring-baseline/plan.md"
  - "specs/012-frontend-contract-verify-integration/spec.md"
  - "specs/012-frontend-contract-verify-integration/plan.md"
---
# 实施计划：Frontend Contract Observation Provider Baseline

**编号**：`013-frontend-contract-observation-provider-baseline` | **日期**：2026-04-02 | **规格**：specs/013-frontend-contract-observation-provider-baseline/spec.md

## 概述

本计划处理的是 `012` 下游的 frontend contract observation provider baseline，而不是继续扩张 `012` 的 verify mainline。当前仓库已经在上游锁定并实现了：

- `011`：frontend contract models、artifact instantiation、drift helper、最小 contract-aware gate surface
- `012`：contract-aware verify helper、`verify_constraints` scoped attachment、`VerificationGate / VerifyGate` aggregation、CLI verify summary

但“observation 从哪里来、以什么 provider contract 落盘、scanner 在其中是什么角色”仍缺少独立 child work item 去冻结：

- provider 的最小输入/输出合同还没有正式定义
- `frontend-contract-observations.json` 只有 verify 侧输入边界，没有独立 provider artifact baseline
- scanner、manual export、bridge script 三类来源没有统一到同一 provider truth 下
- 若继续直接编码，很容易把 provider、scanner、verify integration、registry attachment 与 remediation 混成一个过宽工单

因此，本计划的目标是建立统一的 `Frontend Contract Observation Provider` formal baseline：

- 先冻结 provider 的 truth order
- 再冻结 artifact envelope、provenance 与 freshness 语义
- 最后给出后续 `core / scanners / cli / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成，且第一批实现切片已落下 `provider contract / artifact IO`。经用户明确要求继续后，当前只允许进入第二批实现切片：`scanner candidate`，并把 scanner 语义收窄为“扫描源码中的结构化 observation 注释块”；不同时触碰 CLI 或 `012` verify mainline。

## 技术背景

**语言/版本**：Python 3.11+、Typer CLI、Pydantic/dataclass models、Markdown formal docs  
**主要依赖**：`011` contract baseline、`012` verify integration baseline、现有 scanners 与 `scan` CLI 能力  
**现有基础**：

- [`../../src/ai_sdlc/core/frontend_contract_drift.py`](../../src/ai_sdlc/core/frontend_contract_drift.py) 已定义 `PageImplementationObservation`
- [`../../src/ai_sdlc/gates/frontend_contract_gate.py`](../../src/ai_sdlc/gates/frontend_contract_gate.py) 已能消费 observation 与 contract artifact 做 drift 判定
- [`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py) 已消费 `frontend-contract-observations.json` 作为 verify 侧输入边界
- [`../../src/ai_sdlc/scanners/`](../../src/ai_sdlc/scanners/) 已存在通用 project scanners，可作为 frontend contract scanner 设计风格参照
- [`../../src/ai_sdlc/cli/commands.py`](../../src/ai_sdlc/cli/commands.py) 已存在 `scan` command，可作为 observation provider downstream integration 的 CLI surface 参照

**目标平台**：AI-SDLC 框架仓库自身，面向 frontend contract observation provider / scanner baseline  
**主要约束**：

- `013` 只冻结 provider baseline，不回写 `012` 的 verify mainline truth
- observation 输出必须保持结构化，不得退回 prompt 或自然语言摘要
- scanner 只是 candidate provider，不得在 formal docs 中冒充 provider 全体
- provider artifact 需要显式 provenance / freshness 语义，避免过期结果被误用
- 当前阶段只允许 docs-only 落盘，不直接进入 `src/` / `tests/` 实现

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前只冻结 provider/artifact/scanner baseline，不扩张到 verify mainline、registry 或 remediation |
| MUST-2 关键路径可验证 | provider contract、artifact envelope、provenance/freshness 与测试矩阵都必须可被文档和后续测试直接验证 |
| MUST-3 范围声明与回退 | 明确只处理 observation provider 主线，当前变更仅作用于 `specs/013/...` formal docs |
| MUST-4 状态落盘 | 通过 `spec.md / plan.md / tasks.md / task-execution-log.md` 将 provider baseline 落为 canonical truth |
| MUST-5 产品代码与开发框架隔离 | 当前 work item 只处理框架 provider 合同，不引入具体前端 runtime 或 scanner 实现 |

## 项目结构

### 文档结构

```text
specs/013-frontend-contract-observation-provider-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前已存在的上游实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_drift.py
│   ├── frontend_contract_verification.py
│   └── verify_constraints.py
├── gates/
│   └── frontend_contract_gate.py
└── scanners/
    ├── api_scanner.py
    ├── ast_scanner.py
    ├── dependency_scanner.py
    ├── file_scanner.py
    ├── risk_scanner.py
    └── test_scanner.py
```

### 推荐的后续实现触点

```text
src/ai_sdlc/
├── core/
│   ├── frontend_contract_observation_provider.py   # provider contract / artifact IO / provenance helpers
│   └── frontend_contract_drift.py                  # only if observation model baseline truly needs additive extension
├── scanners/
│   └── frontend_contract_scanner.py                # scanner as candidate provider, not provider baseline itself
├── cli/
│   └── commands.py                                 # only when scan/export surface truly needs user-facing wiring
└── gates/
    └── frontend_contract_gate.py                   # downstream consumer only; not owned by current baseline

tests/
├── unit/test_frontend_contract_observation_provider.py
├── unit/test_frontend_contract_scanner.py
└── integration/test_cli_scan.py                    # only if CLI surface is later attached
```

## 开始执行前必须锁定的阻断决策

- observation provider 是 `011` 与 `012` 之间的独立真值层，不是 `012` 的附属 helper
- provider 输出必须统一落到结构化 artifact contract，而不是 scanner 专用内部表示
- `frontend-contract-observations.json` 是 canonical artifact 名称，但具体 active 消费位置由下游集成工单显式确定
- scanner 只是 candidate provider，不得覆盖 manual/export provider 的合法性
- provenance / freshness 必须成为 provider artifact 的正式字段，而不是非结构化备注
- registry、auto-fix、remediation 与 verify mainline 变更保持在下游 work item

未锁定上述决策前，不得进入 `013` 的代码实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| provider contract | 定义 observation provider 的输入/输出、artifact envelope、provenance 与 freshness 语义 | 不得改写 `012` verify mainline 或 `011` contract artifact truth |
| scanner candidate baseline | 定义 scanner 作为 candidate provider 的角色与最小接入面 | 不得把 scanner 写成唯一 provider 来源 |
| artifact IO baseline | 定义 `frontend-contract-observations.json` 的落盘/读取合同 | 不得直接承担 verify aggregation 或 registry attachment |
| CLI handoff | 定义何时允许接到 `scan` 或 export surface | 不得在当前 docs-only batch 中引入新的 runtime command |
| downstream remediation handoff | 明确 registry、auto-fix、remediation 仍在下游 | 不得把 remediation 逻辑混入 provider baseline |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 frontend contract observation provider 从 `012` 的后续建议动作收敛为单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/013/...` 文档改动。

### Phase 1：Provider truth freeze

**目标**：锁定 provider 在 `011 -> 013 -> 012` 主线中的 truth order。  
**产物**：scope baseline、provider role baseline、scanner separation baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Artifact contract freeze

**目标**：锁定 observation artifact envelope、provenance、freshness 与 canonical file naming。  
**产物**：artifact baseline、source/freshness baseline、downstream handoff baseline。  
**验证方式**：artifact contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Provider contract / artifact IO slice

**目标**：落下 observation provider 的最小结构化 artifact contract、canonical path helper 与 JSON read/write 语义，先稳定 envelope、provenance、freshness 与 observation round-trip。
**产物**：`src/ai_sdlc/core/frontend_contract_observation_provider.py`、`tests/unit/test_frontend_contract_observation_provider.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `core/`、`tests/` 与 execution log 变更。

### Phase 5：Scanner candidate slice

**目标**：落下 frontend contract scanner 的最小候选实现，扫描源码中的结构化 observation 注释块，并复用 provider artifact contract 物化 canonical artifact。
**产物**：`src/ai_sdlc/scanners/frontend_contract_scanner.py`、`tests/unit/test_frontend_contract_scanner.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `scanners/`、`tests/` 与 execution log 变更。

## 工作流计划

### 工作流 A：Provider truth freeze

**范围**：provider truth order、scope、non-goals、scanner separation。  
**影响范围**：后续 provider/scanner 子工单与 `012` observation consumer 边界。  
**验证方式**：formal docs truth-order review。  
**回退方式**：不触发代码实现。

### 工作流 B：Artifact envelope freeze

**范围**：`frontend-contract-observations.json` canonical naming、payload envelope、provenance 与 freshness 语义。  
**影响范围**：provider artifact IO、downstream verify consumption 与 future export surfaces。  
**验证方式**：artifact contract review。  
**回退方式**：不创建 runtime artifact writer。

### 工作流 C：Implementation handoff freeze

**范围**：推荐文件面、ownership 边界、测试矩阵与下游 registry/remediation handoff。  
**影响范围**：后续 `core / scanners / cli / tests` 实现路线。  
**验证方式**：file-map review + tests matrix review。  
**回退方式**：不进入 scanner/provider runtime。

### 工作流 D：Provider contract / artifact IO slice

**范围**：定义 canonical artifact 文件名、artifact envelope、provenance/freshness dataclass 与 JSON read/write helper。
**影响范围**：后续 scanner candidate、manual/export provider 与下游 verify consumer 的共享 observation artifact 合同。
**验证方式**：`tests/unit/test_frontend_contract_observation_provider.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 scanner runtime、CLI、registry 或 `012` verify mainline 写入。

### 工作流 E：Scanner candidate slice

**范围**：扫描 `.js/.jsx/.ts/.tsx/.vue` 源码中的 `ai-sdlc:frontend-contract-observation` 结构化注释块，生成 `PageImplementationObservation` 列表并可复用 provider helper 物化 artifact。
**影响范围**：后续 scanner provider、manual/export provider 对齐的 observation source，以及 downstream consumer 可复用的 canonical artifact writer。
**验证方式**：`tests/unit/test_frontend_contract_scanner.py` + fresh `ruff` / `verify constraints`。
**回退方式**：不触发 CLI、registry 或 `012` verify mainline 写入。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| provider truth order | 文档交叉引用检查 | 人工审阅 |
| scanner vs provider separation | formal wording review | 人工审阅 |
| artifact envelope completeness | artifact contract review | 实体清单对账 |
| provenance/freshness honesty | 语义对账 | 测试矩阵回挂 |
| downstream handoff clarity | file-map review | 人工审阅 |
| provider artifact contract correctness | `uv run pytest tests/unit/test_frontend_contract_observation_provider.py -q` | artifact payload review |
| scanner candidate correctness | `uv run pytest tests/unit/test_frontend_contract_scanner.py -q` | scanned observation/artifact review |

## 已锁定决策

- `013` 是 `012` 下游的 observation provider child work item，不继续在 `012` 内混做 provider/scanner
- provider 输出必须是结构化 observation artifact，不是 scanner 私有输出
- `frontend-contract-observations.json` 只先冻结 canonical artifact naming/envelope，不在当前 work item 中重写 `012` 的 active consumer attachment
- scanner 只是 candidate provider；manual/export provider 同样合法
- 当前第一批实现只放行 `core/frontend_contract_observation_provider.py` 与 `tests/unit/test_frontend_contract_observation_provider.py`，不放行 scanner candidate、CLI、registry 或 `012` verify mainline
- 当前第二批实现只放行 `scanners/frontend_contract_scanner.py` 与 `tests/unit/test_frontend_contract_scanner.py`，并复用已有 provider helper 物化 artifact；不放行 CLI、registry 或 `012` verify mainline

## 实施顺序建议

1. 先冻结 `013` formal spec/plan/tasks，确保 observation provider 有独立 canonical truth。  
2. 再冻结 artifact envelope、provenance/freshness 与 scanner separation 的 wording。  
3. 最后给出 `core / scanners / cli / tests` 推荐文件面与测试矩阵，准备下游实现 child batch。  
4. 只有在用户明确要求继续实现、且 `013` formal docs 通过门禁后，才允许进入 provider/scanner 代码切片。
