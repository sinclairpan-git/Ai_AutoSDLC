# 功能规格：Harness Telemetry Provenance Runtime Closure Baseline

**功能编号**：`138-harness-telemetry-provenance-runtime-closure-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime closure 已完成并通过 focused verification
**输入**：[`../005-harness-grade-telemetry-observer-v1/spec.md`](../005-harness-grade-telemetry-observer-v1/spec.md)、[`../005-harness-grade-telemetry-observer-v1/task-execution-log.md`](../005-harness-grade-telemetry-observer-v1/task-execution-log.md)、[`../006-provenance-trace-phase-1/spec.md`](../006-provenance-trace-phase-1/spec.md)、[`../006-provenance-trace-phase-1/task-execution-log.md`](../006-provenance-trace-phase-1/task-execution-log.md)、[`../../src/ai_sdlc/telemetry/runtime.py`](../../src/ai_sdlc/telemetry/runtime.py)、[`../../src/ai_sdlc/telemetry/observer.py`](../../src/ai_sdlc/telemetry/observer.py)、[`../../src/ai_sdlc/telemetry/writer.py`](../../src/ai_sdlc/telemetry/writer.py)、[`../../src/ai_sdlc/telemetry/provenance_resolver.py`](../../src/ai_sdlc/telemetry/provenance_resolver.py)、[`../../src/ai_sdlc/telemetry/provenance_inspection.py`](../../src/ai_sdlc/telemetry/provenance_inspection.py)、[`../../src/ai_sdlc/cli/telemetry_cmd.py`](../../src/ai_sdlc/cli/telemetry_cmd.py)、[`../../src/ai_sdlc/cli/provenance_cmd.py`](../../src/ai_sdlc/cli/provenance_cmd.py)、[`../../tests/integration/test_cli_telemetry.py`](../../tests/integration/test_cli_telemetry.py)、[`../../tests/integration/test_cli_provenance.py`](../../tests/integration/test_cli_provenance.py)

> 口径：`138` 是 `120/T43` 的 implementation carrier。它不重写 `005/006` 的 formal truth，而是把当前仓库里已经落地的 telemetry/provenance runtime 正式收束为 backlog 可消费的单一 closure carrier。

## 问题定义

`005` 与 `006` 当前都不是“只有 formal baseline”。现有仓库已经具备一条完整而稳定的 runtime 链：

- `src/ai_sdlc/telemetry/*` 已提供 contracts、store、writer、runtime、collectors、observer、governance/publisher 等 telemetry 主链
- `src/ai_sdlc/telemetry/provenance_*` 已提供 provenance contracts、ingress、resolver、inspection、observer/governance enrichment 与 read-only inspection surfaces
- `src/ai_sdlc/cli/telemetry_cmd.py` 与 `src/ai_sdlc/cli/provenance_cmd.py` 已提供 bounded manual telemetry CLI 与 read-only provenance CLI
- `tests/unit/test_telemetry*`、`tests/integration/test_cli_telemetry.py`、`tests/integration/test_cli_provenance.py` 已持续锁定 runtime、CLI 与 non-blocking governance 边界

因此 `120/T43` 的真实缺口不再是“尚未形成 telemetry/provenance runtime surface”，而是 backlog 仍然停在 `formal_only`，缺少一个正式 carrier 来诚实表达：

- `005-006` 已经形成真实 telemetry / provenance runtime surfaces
- platform meta capability 的观测与追踪链已经进入可交付状态
- provenance read surfaces 已不再只靠局部 artifact contract，而是有正式 resolver / inspection / CLI surfaces

`138` 的职责就是把这条已存在的 runtime closure 挂回 `T43`，避免后续继续把 `005/006` 误导成尚未进入 machine truth。

## 范围

- **覆盖**：
  - 回收 `005/006` 已落地的 telemetry / provenance runtime truth
  - 固定 telemetry runtime、observer/governance、manual telemetry CLI、read-only provenance inspection CLI 的 closure 边界
  - 固定 provenance 保持 `gate-capable but non-blocking` 与 `read-only first` 的事实
  - 回链 `120/T43`，并将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `138` 推进到 `139`
- **不覆盖**：
  - 改写 `005/006` formal wording
  - 推进 `007-008/T44` repo mutation / direct formal entry 主线
  - 新增 host-native ingress、第二事实系统或默认 provenance blocker
  - 扩张为跨 session viewer / replay 平台或重型 graph viewer

## 已锁定决策

- `005/006` 的 runtime 继续以 `telemetry facts -> observer/governance -> bounded gate consumption` 的单链消费
- provenance 继续作为 telemetry 内部事实扩展，而不是第二事实系统
- manual telemetry CLI 继续保持最小 bounded surface；provenance CLI 继续保持 read-only inspection surface
- provenance-specific governance 继续保持 `gate-capable but non-blocking`，不能 override 既有 evaluation/gate truth
- 本批是 closure carrier / backlog honesty 收束，不引入新的 production 行为

## 功能需求

| ID | 需求 |
|----|------|
| FR-138-001 | `138` 必须明确 `005/006` 已通过现有代码进入真实 runtime，而不是继续停留在 formal baseline |
| FR-138-002 | `138` 必须明确 `telemetry runtime/store/writer/observer` 与 `provenance resolver/inspection/CLI` 共同构成 `T43` 的运行时主链 |
| FR-138-003 | `138` 必须明确 manual telemetry CLI 与 read-only provenance CLI 已形成稳定对外 surface |
| FR-138-004 | `138` 必须明确 provenance inspection/read surfaces 不再只靠局部 artifact contract |
| FR-138-005 | `138` 必须明确 provenance governance 保持 `gate-capable but non-blocking`，未被 closure carrier 夸大为默认 blocker |
| FR-138-006 | `138` 必须回链 `120/T43`，让 `005-006` 不再被 backlog 表述为 `formal_only` |

## Runtime Closure Completion（2026-04-14）

- `src/ai_sdlc/telemetry/runtime.py`、`writer.py`、`observer.py`、`governance_publisher.py` 与相关 store/contracts 已形成 harness-grade telemetry runtime 主链。
- `src/ai_sdlc/telemetry/provenance_resolver.py`、`provenance_inspection.py`、`provenance_observer.py`、`provenance_governance.py` 已形成 Phase 1 provenance resolution / inspection / enrichment 主链。
- `src/ai_sdlc/cli/telemetry_cmd.py` 已提供最小 manual telemetry CLI surface；`src/ai_sdlc/cli/provenance_cmd.py` 已提供 read-only `summary / explain / gaps / --json` provenance CLI。
- unit 与 integration tests 已覆盖 telemetry/provenance contracts、runtime、inspection、CLI 与 non-blocking governance 边界。
- 当前批次不需要新增 production 代码；所做的是将已有 telemetry/provenance runtime closure 正式收束到 `T43` carrier，并用 fresh verification 重新确认其成立。

## Exit Criteria

- **SC-138-001**：reviewer 可以从 `138` 直接读出 `005/006` 已进入真实 telemetry/provenance runtime，而不是继续误判为 formal-only
- **SC-138-002**：`120/T43` 不再停留在缺少 implementation carrier 的 `formal_only`
- **SC-138-003**：manual telemetry CLI 与 read-only provenance CLI 有 fresh verification 作为证据
- **SC-138-004**：provenance 的 read-only / non-blocking 边界仍保持清晰，没有被 closure carrier 擅自放大

---
related_doc:
  - "specs/005-harness-grade-telemetry-observer-v1/spec.md"
  - "specs/005-harness-grade-telemetry-observer-v1/task-execution-log.md"
  - "specs/006-provenance-trace-phase-1/spec.md"
  - "specs/006-provenance-trace-phase-1/task-execution-log.md"
  - "src/ai_sdlc/telemetry/runtime.py"
  - "src/ai_sdlc/telemetry/observer.py"
  - "src/ai_sdlc/telemetry/writer.py"
  - "src/ai_sdlc/telemetry/provenance_resolver.py"
  - "src/ai_sdlc/telemetry/provenance_inspection.py"
  - "src/ai_sdlc/cli/telemetry_cmd.py"
  - "src/ai_sdlc/cli/provenance_cmd.py"
  - "tests/integration/test_cli_telemetry.py"
  - "tests/integration/test_cli_provenance.py"
frontend_evidence_class: "framework_capability"
---
