# 实施计划：Provenance Trace Phase 1

**编号**：`006-provenance-trace-phase-1` | **日期**：2026-03-31 | **规格**：specs/006-provenance-trace-phase-1/spec.md

## 概述

本计划承接 provenance trace 的 frozen architecture/design，不再重新讨论是否要做第二事实系统或是否要立即接入宿主。实现目标是把 provenance Phase 1 收敛成 telemetry 内部正式能力：先冻结 contracts，再补 store/resolver/writer，再补 ingress/adapters、inspection CLI、non-blocking governance，最后用 matrix、docs 与 full verification 收口。

本计划默认保持 **read-only first** 与 **gate-capable but non-blocking**。任何 host-native 全覆盖、默认 blocker、默认 published artifact、execute 面 provenance 阻断，都不在首期范围内。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Pydantic v2、Typer、Rich、pytest、JSON/NDJSON telemetry store  
**现有基础**：现有 telemetry 已提供 `Evidence`、`TraceContext`、store/writer discipline、observer/governance/gate capability baseline；`docs/superpowers/specs/2026-03-31-provenance-trace-architecture-design.md` 与 `docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md` 已冻结 provenance 的对象模型、模块边界与 acceptance matrix  
**目标平台**：框架仓库自迭代主路径  
**主要约束**：
- provenance 只能存在于 telemetry 内部，不能分叉成第二事实系统
- facts append-only；interpretation / governance objects mutable current + revisions
- `unknown` 属于 gap，不属于 fact ingress kind
- Phase 1 生成 candidate/hook，但默认不改变现有 gate verdict
- formal execute 入口以后续 `tasks.md + task-execution-log.md + mainline commits` 为准

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 首期只做 contracts、store/resolver、ingress、inspection、non-blocking governance；不做 host-native full coverage |
| MUST-2 关键路径可验证 | 每个阶段都要求 unit/integration tests，且最终跑 targeted provenance suite + full repo verification |
| MUST-3 范围声明与回退 | Phase 1 与 Phase 2 边界显式冻结；host ingress failure 只能降级，不能回改 contract |
| MUST-4 状态落盘 | provenance facts/assessments/gaps/hooks 都必须进入正式 telemetry truth，不依赖聊天结论 |
| MUST-5 产品代码隔离 | contracts、store/resolver、ingress、inspection、governance、CLI、docs 分层落位 |

## 项目结构

### 文档结构

```text
specs/006-provenance-trace-phase-1/
├── spec.md
├── plan.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/
├── telemetry/
│   ├── enums.py
│   ├── ids.py
│   ├── contracts.py
│   ├── provenance_contracts.py
│   ├── provenance_store.py
│   ├── provenance_resolver.py
│   ├── provenance_ingress.py
│   ├── provenance_adapters.py
│   ├── provenance_inspection.py
│   ├── provenance_observer.py
│   └── provenance_governance.py
├── core/
│   └── provenance_gate.py
└── cli/
    ├── provenance_cmd.py
    ├── main.py
    └── command_names.py
```

## 开始编码前必须锁定的阻断决策

- provenance 继续复用 telemetry `Evidence / TraceContext / writer / resolver` 纪律
- `ingress_kind` 对 facts 固定为 `auto / injected / inferred`
- `chain_status` 固定为 `closed / partial / unknown`
- `unsupported` 固定为 gap-kind，不得混成 chain-status
- Phase 1 provenance candidate 只读可见，不得 hidden-flag 升格成 blocker
- `manual injection` 长期保留作测试/诊断面，但不是默认业务入口

未锁定上述决策前，不得进入 contracts 之后的实现 task。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| provenance contracts | enums、IDs、models、TraceContext/ref semantics | 不得做持久化或生成 assessment |
| persistence/resolution | append-only facts、mutable revisions、closure/integrity、ordering | 不得伪造 observer/governance verdict |
| ingress/adapters | 把 `auto / injected / inferred` 统一映射成 facts + evidence 请求 | 不得生成 assessment / governance hook |
| inspection/CLI | 只读 chain/assessment/gap views 与 stable JSON | 不得 graph rewrite / repair / rebuild / auto-fix |
| observer/governance | provenance enrichments 与 governance-ready hook | 不得 override 现有 evaluation truth 或默认 gate |
| regression/docs | matrix coverage、CLI discoverability、Phase 1 limit docs | 不得扩 scope 到 host-native full coverage 或 execute blocker |

## 阶段计划

### Phase 0：Formal work item freeze

**目标**：把 frozen provenance design/plan 收敛成正式 `006` work item 真值。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：只改 formal 文档，不进入运行时代码。

### Phase 1：Contracts freeze

**目标**：冻结 provenance enums、IDs、contract models、shared validator 纪律。  
**产物**：`enums.py`、`ids.py`、`contracts.py`、`provenance_contracts.py`、contract tests。  
**验证方式**：contract-focused unit tests。  
**回退方式**：不进入 store/resolver。

### Phase 2：Persistence + Resolver

**目标**：完成 provenance append-only persistence、mutable revision storage、writer ordering、resolver closure/integrity。  
**产物**：`provenance_store.py`、`provenance_resolver.py`、writer/store/paths integration。  
**验证方式**：storage/resolver tests。  
**回退方式**：不接 ingress/inspection。

### Phase 3：Ingress + Inspection

**目标**：完成四条 provenance ingress contract 与 read-only inspection/CLI。  
**产物**：`provenance_ingress.py`、`provenance_adapters.py`、`provenance_inspection.py`、`provenance_cmd.py`、CLI registration。  
**验证方式**：ingress tests + inspection/CLI tests。  
**回退方式**：不接 observer/governance。

### Phase 4：Non-Blocking Governance

**目标**：完成 provenance assessment/gap enrichments、governance hook/candidate 与 future gate placeholder，但不改变默认 blocker。  
**产物**：`provenance_observer.py`、`provenance_governance.py`、`core/provenance_gate.py` 与相关 non-regression tests。  
**验证方式**：observer/governance tests + verify/close/gates non-regression。  
**回退方式**：保持 inspection-only。

### Phase 5：Matrix + Docs + Final Verification

**目标**：补齐正反样本矩阵、用户文档、CLI discoverability，并跑 targeted provenance suite 与 repo-level verification。  
**产物**：matrix-aligned tests、用户文档、final regression evidence。  
**验证方式**：targeted provenance suite、`ruff`、`pytest -q`、`verify constraints`。  
**回退方式**：不扩展产品行为，只收口文档与测试。

## 工作流计划

### 工作流 A：Contracts before storage

**范围**：enum / IDs / contract models / shared validators  
**影响范围**：`telemetry/enums.py`、`telemetry/ids.py`、`telemetry/contracts.py`、`telemetry/provenance_contracts.py`  
**验证方式**：`tests/unit/test_telemetry_provenance_contracts.py`  
**回退方式**：未完成 contracts 前，不写 store/resolver

### 工作流 B：Storage before inspection

**范围**：writer、store、resolver、closure、ordering  
**影响范围**：`telemetry/provenance_store.py`、`telemetry/provenance_resolver.py`、`telemetry/writer.py`  
**验证方式**：`tests/unit/test_telemetry_provenance_store.py`  
**回退方式**：未完成 parse/closure/integrity 前，不接 CLI

### 工作流 C：Inspection before governance

**范围**：ingress/adapters、inspection、CLI、command discovery  
**影响范围**：`telemetry/provenance_ingress.py`、`telemetry/provenance_adapters.py`、`telemetry/provenance_inspection.py`、`cli/provenance_cmd.py`  
**验证方式**：ingress/inspection/CLI tests  
**回退方式**：未稳定输出 shape 前，不接 governance hook

### 工作流 D：Governance enrich only

**范围**：observer/governance integration、future gate placeholder、docs/matrix/final verification  
**影响范围**：`telemetry/provenance_observer.py`、`telemetry/provenance_governance.py`、`core/provenance_gate.py`、docs/tests  
**验证方式**：observer/governance tests + repo regression  
**回退方式**：不改变现有 default blocker path

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| contracts + IDs | `tests/unit/test_telemetry_provenance_contracts.py` | `tests/unit/test_telemetry_contracts.py` |
| persistence + resolver | `tests/unit/test_telemetry_provenance_store.py` | snapshot-style failure-class assertions |
| ingress + adapters | `tests/unit/test_telemetry_provenance_ingress.py` | matrix-aligned positive/negative fixtures |
| inspection + CLI | `tests/unit/test_telemetry_provenance_inspection.py` | `tests/integration/test_cli_provenance.py` |
| governance non-regression | `tests/unit/test_telemetry_provenance_governance.py` | `tests/unit/test_verify_constraints.py` / `tests/unit/test_close_check.py` / `tests/unit/test_gates.py` |
| final rollout evidence | targeted provenance suite | `uv run ruff check src tests` + `uv run pytest -q` + `uv run ai-sdlc verify constraints` |

## 已锁定决策

- provenance remains inside telemetry
- Phase 1 is gate-capable but read-only
- `unknown` is gap semantics, not fact ingress
- `manual injection` stays diagnostic, not default product workflow
- no hidden flag / env toggle may promote provenance into default blocker semantics
- Phase 2 only replaces ingress, never Phase 1 contracts

## 实施顺序建议

1. 先冻结 `006` formal work item 文档，结束“只有 superpowers plan、没有 formal tasks”的状态。
2. 再按 contracts → store/resolver → ingress → inspection CLI → governance → docs/regression 的顺序推进。
3. 所有阶段都先写 failing tests，再做最小实现，再回到 focused verification。
4. 只有 targeted provenance suite 与 repo-level verification 都为绿后，才允许进入 execution close-out。
