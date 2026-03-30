# 实施计划：Harness-Grade Telemetry & Observer V1

**编号**：`005-harness-grade-telemetry-observer-v1` | **日期**：2026-03-30 | **规格**：specs/005-harness-grade-telemetry-observer-v1/spec.md

## 概述

本计划承接 `005` 的 V1 harness-grade telemetry baseline。实现策略不是推翻当前 telemetry，而是沿现有 `runtime-first` 基础做分层升级：先冻结 shared kernel contracts，再绑定 profile/mode/context，再补 deterministic collectors，再补 async observer 和 governance consumption，最后收束 bounded surfaces 与 compatibility smoke。

本计划从第一天就是 `gate-capable`，但不会把 `execute` 变成默认阻断路径；自动 blocker 仅先落在 `verify / close / release`。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Pydantic v2、Typer、Rich、pytest、JSON/NDJSON/YAML  
**现有基础**：`src/ai_sdlc/telemetry/*` 已存在 contracts/store/writer/runtime/evaluators/detectors/generators/readiness 基础实现；`verify constraints`、`telemetry` CLI、bounded `status --json` / `doctor` 已有部分 V1 前置能力  
**目标平台**：先只覆盖 framework `self_hosting`  
**主要约束**：
- 先落 `spec.md / plan.md / tasks.md`，再进入实现
- `Raw Trace Store` 是唯一事实层
- deferred 不得删模型语义
- Gate 不直接读 raw trace

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | V1 只覆盖 self-hosting baseline，不做 external rollout 与实时 observer |
| MUST-2 关键路径可验证 | contracts、collector、observer、gate、fallback 都要求 failing tests + paired positive/negative smoke |
| MUST-3 范围声明与回退 | shared kernel / collector / observer / governance / gate / bounded surfaces 分阶段推进 |
| MUST-4 状态落盘 | facts、derived、governance 分层明确；所有写入都走 canonical writer |
| MUST-5 产品代码隔离 | contracts、policy、collector、observer、governance、CLI/bounded surfaces 分层维护 |

## 项目结构

### 文档结构

```text
specs/005-harness-grade-telemetry-observer-v1/
├── spec.md
├── plan.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/
├── models/project.py                  # project-config defaults (telemetry profile/mode)
├── telemetry/
│   ├── enums.py                       # frozen enums baseline
│   ├── contracts.py                   # trace context / source closure / governance contracts
│   ├── policy.py                      # profile/mode resolution
│   ├── store.py                       # append-only truth + revisions
│   ├── resolver.py                    # source refs / closure resolution
│   ├── writer.py                      # canonical persistence path
│   ├── runtime.py                     # session/run/step binding + async observer triggers
│   ├── collectors.py                  # deterministic collector helpers (new)
│   ├── observer.py                    # reproducible observer rerun pipeline (new)
│   ├── evaluators.py                  # coverage / mismatch interpretation
│   ├── detectors.py                   # violation escalation
│   ├── generators.py                  # audit summary / gate payload
│   ├── governance_publisher.py        # source-closure & lifecycle discipline
│   └── readiness.py                   # bounded status/doctor
├── core/
│   ├── runner.py                      # run binding
│   ├── dispatcher.py                  # step trigger points
│   ├── executor.py                    # execute-stage collected facts
│   ├── verify_constraints.py          # verify consumer
│   ├── close_check.py                 # close consumer
│   └── release_gate.py                # release consumer
├── parallel/engine.py                 # worker lifecycle + worker_id propagation
├── backends/native.py                 # explicit external-agent boundary
└── cli/
    ├── telemetry_cmd.py               # minimal manual telemetry surface
    ├── trace_cmd.py                   # traced wrappers (new)
    ├── verify_cmd.py                  # verify consumer
    ├── doctor_cmd.py                  # bounded readiness
    ├── commands.py                    # bounded status surface
    └── main.py                        # CLI wiring
```

## 开始编码前必须锁定的阻断决策

- V1 manual telemetry surface 锁定为最小 CLI：`open-session`、`close-session`、`record-event`、`record-evidence`、`record-evaluation`、`record-violation`
- `incident report` 在 V1 锁定为 `contract-preserved deferred artifact`

未锁定上述决策前，不得进入 `Task 2+` 的实现。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| contract / normalization | enums、trace context、profile/mode contracts、source-closure enums、gate payload schema | 不得手写 telemetry objects 到磁盘 |
| policy / runtime binding | resolve active profile/mode、bind run context、record explicit mode changes | 不得发明 governance conclusions |
| storage / writer / resolver | append-only persistence、revisions、source resolution、parent-chain validation、closure status | 不得绕过 contracts 或直接写 JSON/NDJSON |
| collector | deterministic command/test/patch/file-write/worker facts、context propagation | 不得产出 observer findings 或 blocker decisions |
| observer / evaluator | coverage、mismatch、unknown-family outputs、reproducible interpretation reruns | 不得回写 facts 或直接发布 gate action |
| governance generator / publisher | `violation`、`audit summary`、`gate decision payload`、source closure gating | 不得绕过 resolver / writer / publisher discipline |
| gate consumer | consume only high-confidence, traceable governance objects at `verify / close / release` | 不得直接扫描 raw trace |
| CLI / bounded surfaces | `trace`、`telemetry`、`verify`、`status --json`、`doctor` | 不得做 deep scan、implicit rebuild、hidden writes |
| smoke / compatibility | paired positive/negative smoke、fallback coverage、profile/mode drift checks | 不得在测试/文档外引入产品行为 |

owner boundary 表示实施主责与验收边界，不等于唯一修改者。允许跨层协作，但不得绕过统一 contracts、canonical writer / publisher discipline 与写入纪律。facts 与 governance objects 的正式落盘都必须经过 canonical writer / publisher discipline，不允许业务代码直接写 JSON/NDJSON。

## 阶段计划

### Phase 0：Formal work item freeze

**目标**：先把设计输入收敛成正式 `005` work item 真值。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + parser-friendly tasks structure。  
**回退方式**：只改文档，不进入实现。

### Phase 1：Shared kernel contracts

**目标**：冻结 profile / mode / confidence / trigger / source-closure / gate payload contracts，并把 must-before-v1 决策落成单一真值。  
**产物**：`models/project.py`、`telemetry/enums.py`、`telemetry/contracts.py`、相关 tests。  
**验证方式**：contract tests + project config tests。  
**回退方式**：只改 contracts，不动 collector / observer。

### Phase 2：Runtime binding + store hardening

**目标**：绑定 profile/mode/context，明确 mode change records，并把 source-closure / hard-fail 分类落到 store / resolver / writer / publisher。  
**产物**：`telemetry/policy.py`、`runtime.py`、`store.py`、`resolver.py`、`writer.py`、`governance_publisher.py`。  
**验证方式**：runtime / store / publisher / fallback tests。  
**回退方式**：先稳定事实层与治理写纪律，再接 collector。

### Phase 3：Collector baseline

**目标**：打通 deterministic collectors 与 traced wrappers，但不让 collector 越界进入 observer/gate 语义。  
**产物**：`telemetry/collectors.py`、`cli/trace_cmd.py`、`executor.py`、`parallel/engine.py`、`native.py` 增量。  
**验证方式**：collector unit tests + traced CLI integration tests。  
**回退方式**：先 facts，后 interpretations。

### Phase 4：Observer + governance consumption

**目标**：引入 async observer baseline，并把高置信治理对象接到 `verify / close / release`；V1 正式输出仅要求 `violation`、`audit summary`、`gate decision payload`，`evaluation summary` 与 `incident report` 保持 contract-preserved deferred。  
**产物**：`telemetry/observer.py`、`evaluators.py`、`detectors.py`、`generators.py`、`verify_constraints.py`、`verify_cmd.py`、`close_check.py`、`release_gate.py`。  
**验证方式**：observer reproducibility tests + gate consumption tests。  
**回退方式**：先 advisory，再收口面 blocker。

### Phase 5：Bounded surfaces + compatibility smoke

**目标**：确保 `status --json` / `doctor` 仍然 bounded，manual telemetry surface 与 V1 决策一致，并补齐 paired smoke。  
**产物**：`readiness.py`、`doctor_cmd.py`、`commands.py`、`telemetry_cmd.py`、文档与 smoke tests。  
**验证方式**：bounded surface integration + full regression。  
**回退方式**：不扩大 deferred 能力。

## 工作流计划

### 工作流 A：Shared kernel and policy binding

**范围**：contracts、project-config、profile/mode、trace context、mode change record  
**影响范围**：`models/project.py`、`telemetry/enums.py`、`telemetry/contracts.py`、`telemetry/policy.py`、`telemetry/runtime.py`  
**验证方式**：unit tests + CLI runtime binding tests  
**回退方式**：只收 shared kernel，不提前接 consumer

### 工作流 B：Facts first

**范围**：store / resolver / writer / publisher + collectors  
**影响范围**：`telemetry/store.py`、`resolver.py`、`writer.py`、`governance_publisher.py`、`collectors.py`、`trace_cmd.py`、`executor.py`、`parallel/engine.py`  
**验证方式**：store/publisher tests + collector boundary tests  
**回退方式**：facts 完成前，不开始 observer gate 逻辑

### 工作流 C：Observer to gate

**范围**：observer baseline、violation/audit/gate payload、verify/close/release consumption、bounded status/doctor  
**影响范围**：`observer.py`、`evaluators.py`、`detectors.py`、`generators.py`、`verify_constraints.py`、`verify_cmd.py`、`close_check.py`、`release_gate.py`、`readiness.py`、`doctor_cmd.py`、`commands.py`  
**验证方式**：observer reproducibility + gate consumption + bounded integration  
**回退方式**：`execute` 保持 advisory-only

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| shared kernel contracts | `tests/unit/test_telemetry_contracts.py` | `tests/unit/test_project_config.py` |
| mode/profile binding | `tests/unit/test_telemetry_policy.py` | `tests/unit/test_runner_confirm.py` |
| source closure + hard-fail 分类 | `tests/unit/test_telemetry_store.py` | `tests/unit/test_telemetry_publisher.py` + paired positive/negative fallback tests |
| collector baseline | `tests/unit/test_telemetry_collectors.py` | `tests/integration/test_cli_trace.py` |
| observer reproducibility | `tests/unit/test_telemetry_observer.py` | telemetry governance unit tests |
| gate consumption | `tests/unit/test_verify_constraints.py` / `test_close_check.py` | integration verify/status/doctor tests |
| bounded read-only surfaces | `tests/integration/test_cli_status.py` / `test_cli_doctor.py` | docs + regression review |

## 已锁定决策

- `self_hosting first`
- observer 首期 `step / batch end async`
- `gate-capable from day one`
- auto blocking only on `verify / close / release`
- `execute` 默认 advisory-only
- V1 manual telemetry surface 锁定为最小 CLI
- `evaluation summary` 在 V1 维持 `contract-preserved deferred artifact`
- `incident report` 在 V1 维持 `contract-preserved deferred artifact`

## 实施顺序建议

1. 先冻结 `005` 正式文档和 must-before-v1 决策。
2. 再做 shared kernel contracts 与 profile/mode/runtime binding。
3. 然后做 store hardening 与 collector baseline。
4. 最后做 observer、gate consumption、bounded surfaces 与 compatibility smoke。
