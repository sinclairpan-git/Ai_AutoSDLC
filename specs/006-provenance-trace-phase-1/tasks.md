---
related_plan: "docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md"
---

# 任务分解：Provenance Trace Phase 1

**编号**：`006-provenance-trace-phase-1` | **日期**：2026-03-31  
**来源**：plan.md + spec.md（FR-006-001 ~ FR-006-018 / SC-006-001 ~ SC-006-006）

---

## 分批策略

```text
Batch 1: formal work item freeze + provenance contract baseline
Batch 2: provenance persistence, writer ordering, and resolver closure
Batch 3: ingress normalization + injected validation matrix baseline
Batch 4: read-only inspection + provenance CLI
Batch 5: non-blocking observer/governance integration
Batch 6: docs close-out + targeted matrix + final verification
```

---

## Batch 1：formal work item freeze + provenance contract baseline

### Task 1.1 冻结正式 work item 真值并挂接 frozen spec/plan

- **任务编号**：T11
- **优先级**：P0
- **依赖**：无
- **文件**：specs/006-provenance-trace-phase-1/spec.md, specs/006-provenance-trace-phase-1/plan.md, specs/006-provenance-trace-phase-1/tasks.md
- **可并行**：否
- **验收标准**：
  1. `006-provenance-trace-phase-1` 从 `docs/superpowers/specs/*.md + plans/*.md` 收敛成 formal work item。
  2. `tasks.md` 使用 parser-friendly 结构，并保留 `related_plan` 对账入口。
  3. formal `spec.md / plan.md / tasks.md` 与 frozen provenance design/plan 不发生语义漂移。
- **验证**：文档对账 + `uv run ai-sdlc verify constraints`

### Task 1.2 冻结 provenance enums、IDs、contracts 与 shape 稳定性

- **任务编号**：T12
- **优先级**：P0
- **依赖**：T11
- **文件**：src/ai_sdlc/telemetry/enums.py, src/ai_sdlc/telemetry/ids.py, src/ai_sdlc/telemetry/contracts.py, src/ai_sdlc/telemetry/provenance_contracts.py, src/ai_sdlc/telemetry/__init__.py, tests/unit/test_telemetry_provenance_contracts.py, tests/unit/test_telemetry_contracts.py
- **可并行**：否
- **验收标准**：
  1. `IngressKind`、`ProvenanceNodeKind`、`ProvenanceRelationKind`、`ProvenanceGapKind`、`ProvenanceCandidateResult` 形成单一 literal truth。
  2. `ProvenanceNodeFact / EdgeFact` 与 `Assessment / GapFinding / GovernanceHook` 的 append-only / mutable 边界清晰。
  3. provenance IDs、refs、enum literals、serialization shape 有 snapshot-stable 断言。
  4. `source_closure_status` 与 `chain_status` 的值域与语义分离。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_contracts.py -q`

---

## Batch 2：provenance persistence、writer ordering 与 resolver closure

### Task 2.1 建立 provenance store、writer 路由与 ingestion_order 真值

- **任务编号**：T21
- **优先级**：P0
- **依赖**：T12
- **文件**：src/ai_sdlc/telemetry/paths.py, src/ai_sdlc/telemetry/store.py, src/ai_sdlc/telemetry/writer.py, src/ai_sdlc/telemetry/provenance_store.py, tests/unit/test_telemetry_provenance_store.py
- **可并行**：否
- **验收标准**：
  1. provenance node/edge append-only 落盘，assessment/gap/hook 走 mutable current + revisions。
  2. `ingestion_order` 由 writer 分配，session-local 单调递增。
  3. same-input replay 的 ordering determinism 稳定，且不因重复 injected replay 隐式抬高 confidence。
  4. `prov://...` locator family 可写入、可解析、可回读。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_store.py -k "write or order or replay or idempotence" -q`

### Task 2.2 建立 resolver、closure 与稳定 failure classes

- **任务编号**：T22
- **优先级**：P0
- **依赖**：T21
- **文件**：src/ai_sdlc/telemetry/provenance_resolver.py, tests/unit/test_telemetry_provenance_store.py
- **可并行**：否
- **验收标准**：
  1. resolver 能区分 `parse failure` 与 `closure incomplete / unknown`。
  2. 能稳定检出 orphan edge、dangling node、missing telemetry object、missing trace-context。
  3. integrity/closure 失败进入 assessment/gap/finding，不得伪装成 raw fact。
  4. `unsupported` 只作为 gap-kind，不得混入 `chain_status`。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_store.py -k "resolver or closure or orphan or dangling or unsupported" -q`

---

## Batch 3：ingress normalization + injected validation matrix baseline

### Task 3.1 实现 provenance ingress normalization 与四类 adapter

- **任务编号**：T31
- **优先级**：P0
- **依赖**：T22
- **文件**：src/ai_sdlc/telemetry/provenance_ingress.py, src/ai_sdlc/telemetry/provenance_adapters.py, src/ai_sdlc/telemetry/__init__.py, tests/unit/test_telemetry_provenance_ingress.py
- **可并行**：否
- **验收标准**：
  1. `conversation/message`、`skill invocation`、`exec_command bridge`、`rule provenance` 都有 injected adapter 路径。
  2. ingress 不得自行分配 `ingestion_order`，也不得生成 assessment / governance hook。
  3. `unknown` 不得落成 `ProvenanceNodeFact / ProvenanceEdgeFact`。
  4. `target_ref` 缺失会进入 parse failure；bridge inference 不能只凭 command 文本硬推。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_ingress.py -q`

### Task 3.2 锁定 injected / inferred / unknown 的正反样本矩阵基线

- **任务编号**：T32
- **优先级**：P0
- **依赖**：T31
- **文件**：tests/unit/test_telemetry_provenance_ingress.py, tests/unit/test_telemetry_provenance_store.py
- **可并行**：否
- **验收标准**：
  1. 四条 provenance 链都至少有一组 positive sample 与一组 negative sample。
  2. negative sample 至少覆盖 `parse failure`、`unsupported`、`unknown / unobserved`。
  3. inferred 样本都要求显式 basis refs。
  4. duplicate injected replay 不会 silently upgrade confidence。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_ingress.py tests/unit/test_telemetry_provenance_store.py -k "injected or inferred or unknown or unsupported or parse" -q`

---

## Batch 4：read-only inspection + provenance CLI

### Task 4.1 实现 chain / assessment / gap inspection 视图

- **任务编号**：T41
- **优先级**：P0
- **依赖**：T32
- **文件**：src/ai_sdlc/telemetry/provenance_inspection.py, tests/unit/test_telemetry_provenance_inspection.py
- **可并行**：否
- **验收标准**：
  1. inspection 能回答 5 个固定 provenance 审计问题。
  2. assessment view 固定输出 `overall chain status / highest confidence source / key gaps`。
  3. 同一 provenance subgraph 的 `chain / assessment / gap` 视图顺序稳定，适合 snapshot tests。
  4. inspection 保持只读，不做 graph rewrite / repair / rebuild / init。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_inspection.py -q`

### Task 4.2 注册 provenance CLI 并冻结 JSON 输出形状

- **任务编号**：T42
- **优先级**：P0
- **依赖**：T41
- **文件**：src/ai_sdlc/cli/provenance_cmd.py, src/ai_sdlc/cli/main.py, src/ai_sdlc/cli/command_names.py, tests/integration/test_cli_provenance.py, tests/unit/test_command_names.py
- **可并行**：否
- **验收标准**：
  1. `ai-sdlc provenance summary / explain / gaps / --json` 可读且只读。
  2. `--json` 输出结构稳定，优先服务 automation / snapshot tests。
  3. 人类视图与 JSON 表达同一 chain/gap 语义。
  4. command discovery 包含 provenance CLI surface。
- **验证**：`uv run pytest tests/integration/test_cli_provenance.py tests/unit/test_command_names.py -q`

---

## Batch 5：non-blocking observer / governance integration

### Task 5.1 增加 provenance observer enrichments

- **任务编号**：T51
- **优先级**：P0
- **依赖**：T42
- **文件**：src/ai_sdlc/telemetry/provenance_observer.py, src/ai_sdlc/telemetry/observer.py, tests/unit/test_telemetry_provenance_observer.py
- **可并行**：否
- **验收标准**：
  1. provenance assessment / gap finding 能 enrich 现有 observer/evaluation surface。
  2. provenance-specific finding 不得 override 现有 evaluation 主结果。
  3. provenance 缺口只能补解释维度，不能伪装成默认 blocker。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_observer.py -q`

### Task 5.2 增加 governance-ready hook 与 Phase 1 provenance_gate placeholder

- **任务编号**：T52
- **优先级**：P0
- **依赖**：T51
- **文件**：src/ai_sdlc/telemetry/provenance_governance.py, src/ai_sdlc/core/provenance_gate.py, src/ai_sdlc/core/verify_constraints.py, src/ai_sdlc/core/close_check.py, src/ai_sdlc/core/release_gate.py, tests/unit/test_telemetry_provenance_governance.py, tests/unit/test_verify_constraints.py, tests/unit/test_close_check.py, tests/unit/test_gates.py
- **可并行**：否
- **验收标准**：
  1. provenance hook / candidate 能生成，并带齐 gate-capable 字段。
  2. Phase 1 candidate 不得进入 published artifact 语义。
  3. hidden flag / env toggle / experimental path 不得把 provenance 提升成默认 blocker。
  4. `core/provenance_gate.py` 在 Phase 1 可以只有 contract-only/read-only 适配层。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_governance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py -q`

---

## Batch 6：docs close-out + targeted matrix + final verification

### Task 6.1 收口 CLI discoverability、用户文档与 Phase 1 边界

- **任务编号**：T61
- **优先级**：P1
- **依赖**：T52
- **文件**：USER_GUIDE.zh-CN.md, tests/integration/test_cli_provenance.py
- **可并行**：否
- **验收标准**：
  1. 用户文档明确 `summary / explain / gaps` 是日常 read-only surface。
  2. manual injection 被明确写成测试/诊断/回放面，而不是默认业务入口。
  3. docs、integration smoke、command discovery 三者使用同一组 provenance CLI 命令。
- **验证**：文档对账 + `uv run pytest tests/integration/test_cli_provenance.py -k "summary or explain or gaps" -q`

### Task 6.2 跑 targeted provenance suite 与仓库级回归收口

- **任务编号**：T62
- **优先级**：P1
- **依赖**：T61
- **文件**：tests/unit/test_telemetry_provenance_contracts.py, tests/unit/test_telemetry_provenance_store.py, tests/unit/test_telemetry_provenance_ingress.py, tests/unit/test_telemetry_provenance_inspection.py, tests/unit/test_telemetry_provenance_observer.py, tests/unit/test_telemetry_provenance_governance.py, tests/integration/test_cli_provenance.py, tests/unit/test_verify_constraints.py, tests/unit/test_close_check.py, tests/unit/test_gates.py, tests/unit/test_command_names.py, USER_GUIDE.zh-CN.md
- **可并行**：否
- **验收标准**：
  1. targeted provenance suite 全部通过。
  2. 全量 `ruff`、`pytest -q`、`verify constraints` 通过。
  3. provenance CLI smoke 与文档例子一致，且 Phase 1 默认不改变 blocker 路径。
- **验证**：`uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_provenance_store.py tests/unit/test_telemetry_provenance_ingress.py tests/unit/test_telemetry_provenance_inspection.py tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/integration/test_cli_provenance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/unit/test_command_names.py -q`, `uv run ruff check src tests`, `uv run pytest -q`, `uv run ai-sdlc verify constraints`
