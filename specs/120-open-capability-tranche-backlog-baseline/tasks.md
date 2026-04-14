---
related_doc:
  - "program-manifest.yaml"
  - "frontend-program-branch-rollout-plan.md"
  - "specs/120-open-capability-tranche-backlog-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/plan.md"
---
# 任务分解：Open Capability Tranche Backlog Baseline

**编号**：`120-open-capability-tranche-backlog-baseline` | **日期**：2026-04-13
**来源**：`spec.md` + `plan.md`

> 说明：以下不是 `120` 自身的执行任务，而是后续要派生 implementation work item 的 tranche backlog。`120` 的作用是把这些 tranche 固定成可执行队列，避免再次发生“口头知道没闭环，但没有实现清单”的状态。

---

## Delivery Streams

| Stream | 范围 | root closure class | 说明 |
|---|---|---|---|
| `S1` | `005-008` | `formal_only` | 平台元能力基础链 |
| `S2` | `009-018`, `065`, `077-078` | `partial` | Frontend contract / observation / gate 基础链 |
| `S3` | `019-040` | `capability_open` | Program execute / remediation / provider / writeback / governance 主线 |
| `S4` | `041-064` | `capability_open` | Final proof / publication / archive / cleanup 主线 |
| `S5` | `066-071` | `capability_open` | P1 experience stability |
| `S6` | `073`, `093-101` | `capability_open` | P2 solution + Stage 0 / frontend mainline delivery |
| `S7` | `102-106` | `capability_open` | Browser quality gate |
| `S8` | `079-092`, `107-113` | `partial` | Framework-only closure / frontend evidence class 生命周期 |
| `S9` | `010`, `094`, `121` | `partial` | Agent adapter verified host ingress |

---

## Excluded Sync Carriers

- `072`、`074`、`075`、`076`
- `116`、`117`、`118`
- `119`
- `120`

这些工单只负责 root wording / status sync / capability truth sync，不进入 implementation tranche queue。

---

## Batch 0：Agent Adapter Verified Host Ingress

### Task 0.0 Real Adapter Installation And Verification Blocker

- **任务编号**：T00
- **队列状态**：`ready_for_derivation`
- **交付流**：`S9`
- **来源范围**：`010`、`094`、`121`、`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`
- **当前状态**：`partial`
- **派生状态**：已派生 `122-agent-adapter-verified-host-ingress-runtime-baseline`；`122` focused verification 已通过，`T00` 已不再阻塞 Batch 1 派生；实际 mutating delivery 仍继续受当前 adapter ingress truth gate 控制；当前保持 `partial` 仅表示 `S9` root closure 保守态
- **历史阻塞背景（已由 `122` 收束）**：
  - Claude/Codex/VS Code 先前写入的不是官方默认读取入口；`122` 已切换到 canonical path
  - `adapter activate` 先前只是 operator acknowledgement；`122` 已将治理真值迁到 machine-verifiable ingress truth
  - `generic` 仍无统一 verify protocol；像 `TRAE` 这类当前未获厂商公开文档明确支持的目标，继续按 `generic / degraded / unsupported` 诚实处理
- **缺失 carrier**：
  - 无；per-agent official/default ingestion surface registry、host/plugin auto-detection precedence 与 support tier、nonce/probe/evidence 驱动的 verify runtime，以及 `status / doctor / run / init` 的单一 gate truth 已由 `122` 正式收束为现有 runtime closure
- **建议文件面**：`src/ai_sdlc/integrations/ide_adapter.py`、`src/ai_sdlc/integrations/agent_target.py`、`src/ai_sdlc/cli/adapter_cmd.py`、`src/ai_sdlc/cli/run_cmd.py`、`src/ai_sdlc/adapters/*`、对应 unit/integration tests
- **前置要求**：
  1. `121` 已将该缺口回写进 root `capability_closure_audit`
  2. `010/094` 已明确当前 `adapter activate` 只算 acknowledged，不等于 host verified activation
- **验收标准**：
  1. 安装命令能自动识别宿主/插件并写入官方默认读取入口；无官方入口时只能诚实降级
  2. `adapter verify` 或安装流程内建验证只能依赖机器证据，不能依赖用户人工确认
  3. `generic` 在缺少官方入口或验证协议时只能落为 `degraded / unsupported / spec_pending`；当前 `TRAE` 也只能按 `generic` 处理，直到厂商公开文档明确支持
  4. `run / init / managed delivery` 不再把 `adapter activate` 当作“已接入成功”的充分条件
- **验证**：`uv run pytest tests/unit/test_ide_adapter.py tests/integration/test_cli_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_run.py -q`
- **建议派生工单**：`122-agent-adapter-verified-host-ingress-runtime-baseline`

---

## Batch 1：User-Visible Mainline Closure（在 T00 收口后进入）

### Task 1.1 Managed Delivery Apply Executor

- **任务编号**：T11
- **交付流**：`S6`
- **来源范围**：`095`、`100`、`101`
- **当前状态**：`partial`
- **派生状态**：已派生 `123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline`；`123` focused verification 已通过，且在下游 `T12/T13` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；confirmed `frontend_action_plan` 的 execution session、`delivery_action_ledger` runtime，以及 action ordering / dependency / partial-progress 的首批执行真值已由 `123` 正式收束为现有 runtime closure；更宽 materialization/browser gate 边界继续由 `T12/T13` 承接
- **建议文件面**：`src/ai_sdlc/core/managed_delivery_apply*.py`、`src/ai_sdlc/models/frontend_*`、`src/ai_sdlc/cli/program_cmd.py`、对应 unit/integration tests
- **依赖**：`096`、`098`、`099`、`100`
- **前置门禁**：`T00`；`010` 中 `agent_target + activation_state + support_tier + evidence` 达到允许进入 mutate delivery 的最低阈值
- **验收标准**：
  1. 已确认的 `frontend_action_plan` 能被转成唯一 execution session
  2. `delivery_action_ledger` 在第一个 mutate action 前被创建，并沿用既有 `action_id`
  3. partial progress / failed / blocked / cancelled 能被诚实记录
  4. `installed / acknowledged / verified` 三态不会被混成同一 delivery 前置状态
- **验证**：`uv run pytest tests/unit/test_*delivery* tests/integration/test_cli_program.py -q`
- **建议派生工单**：`123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline`

### Task 1.2 Frontend Provider Adapter/Package And File Writer Actions

- **任务编号**：T12
- **交付流**：`S6`
- **来源范围**：`095`、`099`、`100`、`101`
- **当前状态**：`partial`
- **派生状态**：已派生 `124-frontend-mainline-delivery-materialization-runtime-baseline`；`124` focused verification 已通过，且在下游 `T13/T14` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；`dependency_install` executor、controlled subtree / scaffold file writer，以及 package manager / component library / frontend provider adapter 的首批 materialization runtime 已由 `124` 正式收束；更宽 browser gate / root takeover 边界继续由 `T13/T14` 承接
- **建议文件面**：`src/ai_sdlc/core/frontend_delivery_*`、`src/ai_sdlc/generators/*`、`src/ai_sdlc/cli/program_cmd.py`、对应 tests
- **依赖**：T00、T11
- **验收标准**：
  1. 受控安装与文件写入动作只能来自已确认 action plan
  2. sidecar / managed target 写入与 `will_not_touch` 边界一致
  3. `100/101` 明确排除的 runtime executor / package installer / file writer 缺口被真正补齐
- **验证**：`uv run pytest tests/unit/test_*frontend* tests/integration/test_cli_program.py -q`
- **建议派生工单**：`124-frontend-mainline-delivery-materialization-runtime-baseline`

### Task 1.3 Browser Probe Runtime

- **任务编号**：T13
- **交付流**：`S7`
- **来源范围**：`102`、`103`
- **当前状态**：`partial`
- **派生状态**：已派生 `125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline`；`125` focused verification 已通过，且在下游 `T14` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；shared probe runtime session、gate-run scoped artifact namespace，以及首批 structured evidence materialization 已由 `125` 正式收束；更完整的 replay / recheck / remediation closure 继续由 `T14` 承接
- **建议文件面**：`src/ai_sdlc/core/frontend_browser_gate*`、`tests/unit/test_frontend_gate_verification.py`、`tests/integration/test_cli_program.py`
- **依赖**：T11、T12
- **验收标准**：
  1. 单个 `gate_run_id` 对应唯一 runtime session 与 artifact namespace
  2. evidence missing / transient failure / real blocker 被结构化区分
  3. browser bundle 只消费当前 gate run artifacts
- **验证**：`uv run pytest tests/unit/test_frontend_gate_verification.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline`

### Task 1.4 Browser Binding, Recheck, Remediation And Footer Closure

- **任务编号**：T14
- **交付流**：`S7`
- **来源范围**：`104`、`105`、`106`
- **当前状态**：`partial`
- **派生状态**：已派生 `126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`；`126` focused verification 已通过，当前保持 `partial`
- **缺失 carrier**：
  - 无；browser gate replay / recheck runtime、remediation input / runbook continuation，以及 footer normalization / gate verdict 的首批 end-to-end closure 已由 `126` 正式收束为现有 runtime closure
- **建议文件面**：`src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、对应 tests
- **依赖**：T13
- **验收标准**：
  1. `recheck_required / needs_remediation / blocked` 在 CLI 与 ProgramService 中完全一致
  2. browser gate 的 replay/recheck 路径不再停留在 baseline wording
  3. `105` 的“首批切片”被推进到整链可用，而不是局部映射
- **验证**：`uv run pytest tests/unit/test_frontend_gate_verification.py tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline`

---

## Batch 2：Contract Foundation And Evidence Inputs

### Task 2.1 Contract Scanner And Observation Producer

- **任务编号**：T21
- **交付流**：`S2`
- **来源范围**：`012`、`013`、`065`、`077`、`078`
- **当前状态**：`partial`
- **派生状态**：已派生 `127-frontend-contract-observation-producer-runtime-closure-baseline`；`127` focused verification 已通过，且在下游 `T22` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；canonical observation scanner / producer、non-sample consumer evidence producer，以及 sample self-check / consumer evidence 的 runtime split 已由 `127` 正式收束为现有 runtime closure；更宽 attachment / verify-gate-readiness 聚合继续由 `T22` 承接
- **建议文件面**：`src/ai_sdlc/core/frontend_contract_*`、`src/ai_sdlc/cli/*scan*`、对应 tests 与 sample fixtures
- **依赖**：无
- **验收标准**：
  1. `012` 明确留白的 scanner implementation 被补齐
  2. `065/077/078` 的 sample fallback 边界在 runtime 中成立
  3. observation producer 能产出 verify / gate 可消费的 canonical artifact
- **验证**：`uv run pytest tests/unit/test_frontend_contract* tests/integration/test_cli_scan.py -q`
- **建议派生工单**：`127-frontend-contract-observation-producer-runtime-closure-baseline`

### Task 2.2 Runtime Attachment And Verify/Gate Closure

- **任务编号**：T22
- **交付流**：`S2`
- **来源范围**：`014`、`015`、`016`、`017`、`018`
- **当前状态**：`partial`
- **派生状态**：已派生 `128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`；`128` focused verification 已通过，且在下游 `T23/T31/T33` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；active `spec_dir` scoped runtime attachment 与 verify/gate/readiness aggregation 的首批真实接线已由 `128` 正式收束；更宽 evidence-class、report/compatibility 后继面与 program automation 继续由 `T23/T31/T33` 承接
- **建议文件面**：`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/frontend_*gate*`、`src/ai_sdlc/core/program_service.py`、对应 tests
- **依赖**：T21
- **验收标准**：
  1. `014` 留给下游的 runtime attachment 正式落地
  2. verify / gate / compatibility 不再只停留在 baseline contract
  3. contract artifacts 与 program/frontend readiness 能进入统一 runtime truth
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`

### Task 2.3 Evidence-Class Validator And Status Runtime Completion

- **任务编号**：T23
- **交付流**：`S8`
- **来源范围**：`083`、`084`、`085`、`086`、`088`、`107`、`108`
- **当前状态**：`partial`
- **派生状态**：已派生 `129-frontend-evidence-class-verify-validate-status-runtime-closure-baseline`；`129` focused verification 已通过，且在下游 `T24` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；`verify constraints` first runtime cut、`program validate` mirror consistency，以及 bounded status surface / legacy-backfill 的统一呈现已由 `129` 正式收束为现有 runtime closure；explicit writeback / close-check 后继闭环继续由 `T24` 承接
- **建议文件面**：`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/core/program_validation*`、`src/ai_sdlc/telemetry/readiness.py`、对应 tests
- **依赖**：T22
- **验收标准**：
  1. `083` 的 primary detection surface 与 `085` 的 first runtime cut 都形成真实 runtime
  2. evidence-class 问题在 verify / validate / status 间维持单一 truth-order
  3. `107/108` 的 backfill 与 runtime surfaces 不再只是局部补丁
- **验证**：`uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_program.py tests/integration/test_cli_status.py -q`
- **建议派生工单**：`129-frontend-evidence-class-verify-validate-status-runtime-closure-baseline`

### Task 2.4 Evidence-Class Mirror Writeback And Close-Check Completion

- **任务编号**：T24
- **交付流**：`S8`
- **来源范围**：`087`、`089`、`090`、`091`、`092`、`109-113`
- **当前状态**：`partial`
- **派生状态**：已派生 `130-frontend-evidence-class-writeback-close-check-runtime-closure-baseline`；`130` focused verification 已通过，且在下游 `T31` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无；explicit program-level mirror write surface、close-check late resurfacing，以及 runtime rollout sequencing / backfill closeout 的首批闭环已由 `130` 正式收束为现有 runtime closure；program automation mainline 继续由 `T31` 承接
- **建议文件面**：`src/ai_sdlc/core/close_check.py`、`src/ai_sdlc/cli/workitem_cmd.py`、`src/ai_sdlc/core/program_*`、对应 tests
- **依赖**：T23
- **验收标准**：
  1. `087` prospective-only writeback contract 形成真实显式写面
  2. `091` 从“首批 implementation slice 进行中”推进到完整 close-check closure
  3. evidence-class lifecycle 从 authoring/validate/status/close-check 到 writeback 形成单链
- **验证**：`uv run pytest tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`130-frontend-evidence-class-writeback-close-check-runtime-closure-baseline`

---

## Batch 3：Program Automation Mainline

### Task 3.1 Execute, Remediation And Materialization Runtime

- **任务编号**：T31
- **交付流**：`S3`
- **来源范围**：`019-024`
- **当前状态**：`partial`
- **派生状态**：已派生 `131-frontend-program-execute-remediation-materialization-runtime-closure-baseline`；`131` focused verification 已通过，且在下游 `T41` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无（就本任务范围）；program automation 下游边界继续由 `T41` 承接
- **建议文件面**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/frontend_*`、对应 tests
- **依赖**：T22、T24
- **验收标准**：
  1. `019-024` 从 orchestration baseline 推进到可执行 program runtime
  2. execute / remediation / writeback 不再只是 formal handoff
  3. `020/022` 留给下游的 runtime 缺口被真正补齐
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`131-frontend-program-execute-remediation-materialization-runtime-closure-baseline`

### Task 3.2 Provider Invocation, Patch Apply And Cross-Spec Writeback Chain

- **任务编号**：T32
- **交付流**：`S3`
- **来源范围**：`025-031`
- **当前状态**：`partial`
- **派生状态**：已派生 `132-frontend-program-provider-patch-writeback-runtime-closure-baseline`；`132` focused verification 已通过，且在下游 `T33` 收口前继续保持 `partial`
- **缺失 carrier**：
  - 无（就本任务范围）；registry / governance / persistence 继续由 `T33` 承接
- **建议文件面**：`src/ai_sdlc/core/program_*provider*`、`src/ai_sdlc/core/program_*patch*`、`src/ai_sdlc/cli/program_cmd.py`、对应 tests
- **依赖**：T31
- **验收标准**：
  1. `025` 的 handoff payload 真正进入 provider invocation
  2. `028-031` 不再停留在 handoff/apply/writeback baseline
  3. cross-spec writeback 不再只是 artifact 契约
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`132-frontend-program-provider-patch-writeback-runtime-closure-baseline`

### Task 3.3 Registry, Governance And Persistence Chain

- **任务编号**：T33
- **交付流**：`S3`
- **来源范围**：`032-040`
- **当前状态**：`partial`
- **派生状态**：已派生 `133-frontend-program-registry-governance-persistence-runtime-closure-baseline`；在 `133` focused verification 通过且下游 `T34` 收口前仍保持 `partial`
- **缺失 carrier**：
  - guarded registry runtime
  - broader/final governance orchestration runtime
  - writeback persistence runtime
- **建议文件面**：`src/ai_sdlc/core/program_*registry*`、`src/ai_sdlc/core/program_*governance*`、`src/ai_sdlc/core/program_*persistence*`、对应 tests
- **依赖**：T32
- **验收标准**：
  1. registry / governance / persistence 不再只存在 artifact/orchestration contract
  2. `032-040` 的执行链能形成稳定 persisted truth
  3. 为 final proof / archive 主线提供真实上游输入
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`133-frontend-program-registry-governance-persistence-runtime-closure-baseline`

### Task 3.4 Final Proof Publication And Archive Runtime

- **任务编号**：T34
- **交付流**：`S4`
- **来源范围**：`041-049`
- **当前状态**：`partial`
- **派生状态**：已派生 `134-frontend-program-final-proof-publication-archive-runtime-closure-baseline`；`134` focused verification 已通过，且在下游 `T35` 收口前继续保持 `partial`
- **缺失 carrier**：
  - final proof publication runtime
  - closure -> archive orchestration runtime
  - archive artifact / thread archive 的 end-to-end closure
- **建议文件面**：`src/ai_sdlc/core/program_*final_proof*`、`src/ai_sdlc/cli/program_cmd.py`、对应 tests
- **依赖**：T33
- **验收标准**：
  1. `041-049` 不再只是 publication/archive contract
  2. `047` 留给下游的 archive artifact persistence 形成真实 runtime
  3. thread archive truth 为 cleanup 提供稳定输入
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`134-frontend-program-final-proof-publication-archive-runtime-closure-baseline`

### Task 3.5 Bounded Cleanup Actualization

- **任务编号**：T35
- **交付流**：`S4`
- **来源范围**：`050-064`
- **当前状态**：`partial`
- **派生状态**：已派生 `135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline`；`135` focused verification 已通过，当前保持 `partial`
- **缺失 carrier**：
  - safe cleanup action set
  - deferred cleanup 到真实 bounded cleanup 的过渡
  - mutation proposal / approval / gating / execution 的 end-to-end closure
- **建议文件面**：`src/ai_sdlc/core/program_*cleanup*`、`src/ai_sdlc/cli/program_cmd.py`、对应 tests
- **依赖**：T34
- **验收标准**：
  1. `050` 的“bounded cleanup”不再长期停留在 deferred
  2. `053/055/057/059/061/063` 的 consumption baseline 被父能力真正吸收
  3. `064` 的 cleanup mutation execution 成为尾链 closure，而不是孤立切片
- **验证**：`uv run pytest tests/unit/test_program_cleanup* tests/integration/test_cli_program.py -q`
- **建议派生工单**：`135-frontend-program-final-proof-archive-project-cleanup-runtime-closure-baseline`

---

## Batch 4：P1 Runtime Gaps And Platform Meta

### Task 4.1 P1 Recheck And Remediation Feedback Runtime

- **任务编号**：T41
- **交付流**：`S5`
- **来源范围**：`066-070`
- **当前状态**：`partial`
- **派生状态**：已派生 `136-frontend-p1-recheck-remediation-feedback-runtime-closure-baseline`；`136` focused verification 已通过，当前保持 `partial`
- **缺失 carrier**：
  - `070` docs-only feedback contract 的 runtime consumer
  - P1 readiness -> remediation/recheck handoff surfaces
  - author-facing bounded runbook materialization
- **建议文件面**：`src/ai_sdlc/core/program_service.py`、`src/ai_sdlc/cli/program_cmd.py`、`src/ai_sdlc/core/frontend_gate_verification.py`、对应 tests
- **依赖**：T22、T31
- **验收标准**：
  1. `070` 不再只是 docs-only baseline
  2. P1 diagnostics / drift 能进入 bounded remediation feedback runtime
  3. program surface 能诚实区分 remediation input 与 recheck handoff
- **验证**：`uv run pytest tests/unit/test_program_service.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`136-frontend-p1-recheck-remediation-feedback-runtime-closure-baseline`

### Task 4.2 P1 Visual/A11y Runtime Foundation

- **任务编号**：T42
- **交付流**：`S5`
- **来源范围**：`071`
- **当前状态**：`partial`
- **派生状态**：已派生 `137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline`；`137` focused verification 已通过，当前保持 `partial`
- **缺失 carrier**：
  - 无；`071` 的 visual / a11y evidence fixtures、gate-compatible visual/a11y checks 与 P1 visual/a11y feedback runtime surface 已由 `137` 正式收束为现有 runtime closure
- **建议文件面**：`src/ai_sdlc/core/frontend_gate_verification.py`、`tests/unit/test_frontend_gate_verification.py`、`tests/integration/test_cli_program.py`
- **依赖**：T13、T14、T41
- **验收标准**：
  1. `071` 从 docs-only baseline 推进到真实检查面
  2. evidence gap /真实质量问题边界在 runtime 中成立
  3. visual/a11y feedback 继续服从既有 gate/report family
- **验证**：`uv run pytest tests/unit/test_frontend_gate_verification.py tests/integration/test_cli_program.py -q`
- **建议派生工单**：`137-frontend-p1-visual-a11y-runtime-foundation-closure-baseline`

### Task 4.3 Harness Telemetry And Provenance Runtime Closure

- **任务编号**：T43
- **交付流**：`S1`
- **来源范围**：`005-006`
- **当前状态**：`partial`
- **派生状态**：已派生 `138-harness-telemetry-provenance-runtime-closure-baseline`；`138` focused verification 已通过，当前保持 `partial`
- **缺失 carrier**：
  - 无；harness-grade telemetry / observer runtime 与 provenance trace runtime / read surfaces 已由 `138` 正式收束为现有 runtime closure
- **建议文件面**：`src/ai_sdlc/telemetry/*`、`src/ai_sdlc/core/*provenance*`、`src/ai_sdlc/cli/provenance*`、对应 tests
- **依赖**：无；可与其他 batch 并行，但不建议先于 `S6/S7`
- **验收标准**：
  1. `005-006` 不再只是 baseline，而形成真实 telemetry / provenance runtime surfaces
  2. platform meta capability 的观测与追踪链进入可交付状态
  3. provenance read surfaces 不再只靠局部 artifact contract
- **验证**：`uv run pytest tests/unit/test_telemetry* tests/unit/test_provenance* tests/integration/test_cli_provenance.py -q`
- **建议派生工单**：`138-harness-telemetry-provenance-runtime-closure-baseline`

### Task 4.4 Branch Lifecycle And Direct Formal Entry Closure

- **任务编号**：T44
- **交付流**：`S1`
- **来源范围**：`007-008`
- **当前状态**：`partial`
- **派生状态**：已派生 `139-branch-lifecycle-direct-formal-runtime-closure-baseline`；`139` 的 focused verification 已通过，当前保持 `partial` 仅表示 tranche/root closure 保守态
- **缺失 carrier**：
  - 无；branch lifecycle bounded runtime、direct-formal scaffold / CLI / tests closure 与 branch guard / direct-formal entry 的 end-to-end repo truth 已由 `139` 正式收束为现有 runtime closure
- **建议文件面**：`src/ai_sdlc/core/*branch*`、`src/ai_sdlc/cli/*workitem*`、`src/ai_sdlc/cli/*formal*`、对应 tests
- **依赖**：无；可与 T43 并行，但不建议先于 `S6/S7`
- **验收标准**：
  1. `007-008` 不再只是 baseline，而形成真实 repo mutation/entry runtime
  2. branch lifecycle 与 direct-formal entry 不再只靠约定或局部 guard
  3. formal entry 与 branch truth 能为后续 work item 主链提供稳定边界
- **验证**：`uv run pytest tests/unit/test_branch_inventory.py tests/unit/test_workitem_scaffold.py tests/unit/test_command_names.py tests/unit/test_verify_constraints.py tests/integration/test_cli_workitem_init.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_workitem_truth_check.py tests/integration/test_cli_workitem_plan_check.py tests/integration/test_cli_workitem_link.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py tests/integration/test_cli_init.py -q`
- **建议派生工单**：`139-branch-lifecycle-direct-formal-runtime-closure-baseline`
