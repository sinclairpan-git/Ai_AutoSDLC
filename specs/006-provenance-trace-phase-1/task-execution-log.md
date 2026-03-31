# 006-provenance-trace-phase-1 任务执行归档

> 本文件遵循 [`../../templates/execution-log-template.md`](../../templates/execution-log-template.md) 的批次追加约定。

## 1. 归档规则

- 每完成一批与 `specs/006-provenance-trace-phase-1/` 相关的实现或正式收口，都在本文件末尾追加新批次章节。
- 批次结束顺序：验证（targeted suite / full regression / 必要只读校验）→ 归档本文 → git commit。
- 本 work item 的 Batch `1~6` 真值，以本文件、[`tasks.md`](tasks.md) 与当前分支提交链共同为准；不得只凭聊天结论或局部实现片段外推“已正式收口”。
- Provenance Phase 1 在本批以 `archived / retained（对照保留）` 收束当前 `codex/006-provenance-trace-phase-1` scratch branch/worktree；该 disposition 不等于 `merged`，也不表示 `main` 已承载本 work item 的主线兑现真值。

## 2. 批次记录

### Batch 2026-03-31-001 | 006 Batch 1-6 formal close-out

#### 2.1 准备

- **任务来源**：[`tasks.md`](tasks.md) `T11` ~ `T62`
- **目标**：把 provenance Phase 1 的 contracts、store/resolver、ingress/adapters、inspection CLI、non-blocking governance、docs 与最终回归证据正式补录为 execution truth，并将当前关联 branch/worktree disposition 固定为 `archived / retained（对照保留）`。
- **预读范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md`](../../docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../src/ai_sdlc/core/workitem_traceability.py`](../../src/ai_sdlc/core/workitem_traceability.py)
- **激活的规则**：fresh verification before completion；formal execution truth；branch/worktree explicit disposition；read-only first；gate-capable but non-blocking。
- **验证画像**：`code-change`

#### 2.2 统一验证命令

- **V1（targeted provenance suite）**
  - 命令：`uv run pytest tests/unit/test_telemetry_provenance_contracts.py tests/unit/test_telemetry_provenance_store.py tests/unit/test_telemetry_provenance_ingress.py tests/unit/test_telemetry_provenance_inspection.py tests/unit/test_telemetry_provenance_observer.py tests/unit/test_telemetry_provenance_governance.py tests/integration/test_cli_provenance.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/unit/test_gates.py tests/unit/test_command_names.py -q`
  - 结果：`167 passed in 10.37s`
- **V2（仓库级全量回归）**
  - 命令：`uv run pytest -q`
  - 结果：`997 passed in 39.71s`
- **Lint**
  - 命令：`uv run ruff check src tests`
  - 结果：`All checks passed!`
- **治理只读校验**
  - 命令：`uv run ai-sdlc verify constraints`
  - 结果：`verify constraints: no BLOCKERs.`

#### 2.3 任务记录

##### T11 / T12 | formal work item freeze + provenance contract baseline

- **改动范围**：[`spec.md`](spec.md)、[`plan.md`](plan.md)、[`tasks.md`](tasks.md)、[`../../src/ai_sdlc/telemetry/enums.py`](../../src/ai_sdlc/telemetry/enums.py)、[`../../src/ai_sdlc/telemetry/ids.py`](../../src/ai_sdlc/telemetry/ids.py)、[`../../src/ai_sdlc/telemetry/contracts.py`](../../src/ai_sdlc/telemetry/contracts.py)、[`../../src/ai_sdlc/telemetry/provenance_contracts.py`](../../src/ai_sdlc/telemetry/provenance_contracts.py)、[`../../src/ai_sdlc/telemetry/__init__.py`](../../src/ai_sdlc/telemetry/__init__.py)、[`../../tests/unit/test_telemetry_provenance_contracts.py`](../../tests/unit/test_telemetry_provenance_contracts.py)、[`../../tests/unit/test_telemetry_contracts.py`](../../tests/unit/test_telemetry_contracts.py)
- **改动内容**：
  - 冻结 `IngressKind`、`ProvenanceNodeKind`、`ProvenanceRelationKind`、`ProvenanceGapKind`、`ProvenanceCandidateResult` 的 literal truth 与 provenance ID/ref shape。
  - 明确 `source_closure_status` 与 `chain_status` 的值域和语义分离，禁止把 provenance gap 语义混成 telemetry fact/status。
  - 将 superpowers 设计计划收敛为 formal `006` work item 文档，并保留 `related_plan` 对账入口。
- **新增/调整的测试**：[`../../tests/unit/test_telemetry_provenance_contracts.py`](../../tests/unit/test_telemetry_provenance_contracts.py)、[`../../tests/unit/test_telemetry_contracts.py`](../../tests/unit/test_telemetry_contracts.py)
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：contracts、enum literals、ID/serialization shape、shared validator 纪律均被 targeted provenance suite 锁定。
- **是否符合任务目标**：符合。

##### T21 / T22 | provenance persistence、writer ordering 与 resolver closure

- **改动范围**：[`../../src/ai_sdlc/telemetry/paths.py`](../../src/ai_sdlc/telemetry/paths.py)、[`../../src/ai_sdlc/telemetry/store.py`](../../src/ai_sdlc/telemetry/store.py)、[`../../src/ai_sdlc/telemetry/writer.py`](../../src/ai_sdlc/telemetry/writer.py)、[`../../src/ai_sdlc/telemetry/provenance_store.py`](../../src/ai_sdlc/telemetry/provenance_store.py)、[`../../src/ai_sdlc/telemetry/provenance_resolver.py`](../../src/ai_sdlc/telemetry/provenance_resolver.py)、[`../../tests/unit/test_telemetry_provenance_store.py`](../../tests/unit/test_telemetry_provenance_store.py)
- **改动内容**：
  - 建立 provenance append-only node/edge 持久化与 assessment/gap/hook current + revisions 语义。
  - 将 `ingestion_order` 固定为 writer 分配的 session-local 单调顺序，并锁住 replay determinism / duplicate injected replay 不静默升级 confidence。
  - resolver 稳定区分 `parse failure`、`closure incomplete / unknown`、orphan edge、dangling node、missing trace-context，并保持 `unsupported` 仅作为 gap-kind。
- **新增/调整的测试**：[`../../tests/unit/test_telemetry_provenance_store.py`](../../tests/unit/test_telemetry_provenance_store.py)
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：writer ordering、resolver failure class、closure/integrity 边界与 inspection 排序语义由自动化回归锁定。
- **是否符合任务目标**：符合。

##### T31 / T32 | ingress normalization + injected/inferred matrix baseline

- **改动范围**：[`../../src/ai_sdlc/telemetry/provenance_ingress.py`](../../src/ai_sdlc/telemetry/provenance_ingress.py)、[`../../src/ai_sdlc/telemetry/provenance_adapters.py`](../../src/ai_sdlc/telemetry/provenance_adapters.py)、[`../../src/ai_sdlc/telemetry/__init__.py`](../../src/ai_sdlc/telemetry/__init__.py)、[`../../tests/unit/test_telemetry_provenance_ingress.py`](../../tests/unit/test_telemetry_provenance_ingress.py)、[`../../tests/unit/test_telemetry_provenance_store.py`](../../tests/unit/test_telemetry_provenance_store.py)
- **改动内容**：
  - 为 `conversation/message`、`skill invocation`、`exec_command bridge`、`rule provenance` 建立 injected adapter 与 normalized ingress 路径。
  - 锁定 `unknown / unobserved / unsupported / parse failure` 的 negative sample 行为，禁止 `unknown` 落成 fake facts，禁止 bridge inference 只凭 command 文本硬推。
  - 要求 inferred sample 带显式 basis refs，duplicate injected replay 不能静默抬升 confidence。
- **新增/调整的测试**：[`../../tests/unit/test_telemetry_provenance_ingress.py`](../../tests/unit/test_telemetry_provenance_ingress.py)、[`../../tests/unit/test_telemetry_provenance_store.py`](../../tests/unit/test_telemetry_provenance_store.py)
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：四条 provenance 链的正反样本矩阵与 gap semantics 已被 focused suite 固定。
- **是否符合任务目标**：符合。

##### T41 / T42 | read-only inspection + provenance CLI

- **改动范围**：[`../../src/ai_sdlc/telemetry/provenance_inspection.py`](../../src/ai_sdlc/telemetry/provenance_inspection.py)、[`../../src/ai_sdlc/cli/provenance_cmd.py`](../../src/ai_sdlc/cli/provenance_cmd.py)、[`../../src/ai_sdlc/cli/main.py`](../../src/ai_sdlc/cli/main.py)、[`../../src/ai_sdlc/cli/command_names.py`](../../src/ai_sdlc/cli/command_names.py)、[`../../tests/unit/test_telemetry_provenance_inspection.py`](../../tests/unit/test_telemetry_provenance_inspection.py)、[`../../tests/integration/test_cli_provenance.py`](../../tests/integration/test_cli_provenance.py)、[`../../tests/unit/test_command_names.py`](../../tests/unit/test_command_names.py)
- **改动内容**：
  - 实现 `chain / assessment / gap` inspection 视图，固定 `overall chain status / highest confidence source / key gaps` 输出结构与顺序。
  - 注册只读 `ai-sdlc provenance summary / explain / gaps / --json`，并让 flat command discovery 显式包含 provenance surface。
  - 保证 CLI 与 inspection 都不做 graph rewrite / repair / rebuild / implicit init。
- **新增/调整的测试**：[`../../tests/unit/test_telemetry_provenance_inspection.py`](../../tests/unit/test_telemetry_provenance_inspection.py)、[`../../tests/integration/test_cli_provenance.py`](../../tests/integration/test_cli_provenance.py)、[`../../tests/unit/test_command_names.py`](../../tests/unit/test_command_names.py)
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：inspection 和 CLI 的 human view / JSON shape 一致性与只读边界通过自动化验证。
- **是否符合任务目标**：符合。

##### T51 / T52 | non-blocking observer / governance integration

- **改动范围**：[`../../src/ai_sdlc/telemetry/provenance_observer.py`](../../src/ai_sdlc/telemetry/provenance_observer.py)、[`../../src/ai_sdlc/telemetry/provenance_governance.py`](../../src/ai_sdlc/telemetry/provenance_governance.py)、[`../../src/ai_sdlc/telemetry/observer.py`](../../src/ai_sdlc/telemetry/observer.py)、[`../../src/ai_sdlc/core/provenance_gate.py`](../../src/ai_sdlc/core/provenance_gate.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)、[`../../src/ai_sdlc/core/close_check.py`](../../src/ai_sdlc/core/close_check.py)、[`../../tests/unit/test_telemetry_provenance_observer.py`](../../tests/unit/test_telemetry_provenance_observer.py)、[`../../tests/unit/test_telemetry_provenance_governance.py`](../../tests/unit/test_telemetry_provenance_governance.py)、[`../../tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/unit/test_gates.py`](../../tests/unit/test_gates.py)
- **改动内容**：
  - provenance assessment / gap enrichments 接入 observer 结果，但不 override 既有 evaluation 主结果。
  - governance hook / candidate 与 Phase 1 placeholder gate payload 可生成、可见、可被 verify/close 消费，但默认只保留 advisory 语义。
  - hidden flag / env toggle / experimental path 都不允许把 provenance 升格成默认 blocker。
- **新增/调整的测试**：[`../../tests/unit/test_telemetry_provenance_observer.py`](../../tests/unit/test_telemetry_provenance_observer.py)、[`../../tests/unit/test_telemetry_provenance_governance.py`](../../tests/unit/test_telemetry_provenance_governance.py)、[`../../tests/unit/test_verify_constraints.py`](../../tests/unit/test_verify_constraints.py)、[`../../tests/unit/test_close_check.py`](../../tests/unit/test_close_check.py)、[`../../tests/unit/test_gates.py`](../../tests/unit/test_gates.py)
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：Phase 1 provenance governance surface 保持 gate-capable but non-blocking，且 verify/close 默认 blocker 路径不变。
- **是否符合任务目标**：符合。

##### T61 / T62 | docs close-out + targeted provenance suite + final verification

- **改动范围**：[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)、[`../../tests/integration/test_cli_provenance.py`](../../tests/integration/test_cli_provenance.py)、[`task-execution-log.md`](task-execution-log.md)
- **改动内容**：
  - 用户文档明确 `summary / explain / gaps` 是 Phase 1 的日常 read-only surface，`manual injection` 保持测试/诊断/回放定位。
  - provenance CLI discoverability、integration smoke 与用户文档命令口径统一。
  - 本批把 targeted provenance suite、repo-level regression、ruff、`verify constraints` 的 fresh evidence 与 formal disposition 一并归档，形成 `006` 的 close-out truth。
- **新增/调整的测试**：无新增运行时代码测试；本任务以 targeted provenance suite、全量回归、lint 与治理只读校验作为收口证据。
- **执行的命令**：见 V1 / V2 / Lint / 治理只读校验。
- **测试结果**：通过。CLI 文档口径、automation-facing JSON surface 与 Phase 1 默认 non-blocking 边界保持一致。
- **是否符合任务目标**：符合。

#### 2.4 代码审查（Mandatory）

- **宪章/规格对齐**：全链路保持 provenance inside telemetry、read-only first、gate-capable but non-blocking，没有创建第二事实系统，也没有把 provenance 偷渡成默认 execute/verify/close blocker。
- **代码质量**：contracts、store/resolver、ingress、inspection、observer/governance、CLI 与 close-surface 之间边界清晰；`unknown / unobserved / unsupported` 的语义被稳定隔离到 gap/assessment 层。
- **测试质量**：当前 turn 已完成 targeted provenance suite、仓库级 `pytest -q`、`ruff check` 与 `verify constraints`；覆盖 contracts、ordering、resolver failure classes、matrix negative samples、CLI shape、observer/governance non-regression。
- **结论**：`无 Critical 阻塞项`

#### 2.5 任务/计划同步状态（Mandatory）

- `tasks.md` 同步状态：`已同步`
- `related_plan`（如存在）同步状态：`已对账`
- 关联 branch/worktree disposition 计划：`archived / retained（对照保留）`
- 说明：当前 `codex/006-provenance-trace-phase-1` 及其 worktree 被有意保留为 provenance Phase 1 的可追溯实现容器；这解决 close truth 的 disposition 问题，但不宣称已 merged 到 `main`。

#### 2.6 自动决策记录（如有）

- AD-001：formal close-out 不伪造 `merged` 状态，而是将当前 `codex/006-provenance-trace-phase-1` scratch branch 固定为 `archived`、worktree 固定为 `retained（对照保留）`。理由：当前用户只要求继续 formal close-out，并未要求合流 `main`；把 scratch branch 误记为 merged 会污染 branch lifecycle 真值。

#### 2.7 批次结论

- `006` 的 Batch `1~6` 已全部具备 formal execution evidence，且 fresh verification 证明 provenance Phase 1 的 contracts、CLI、observer/governance advisory surface 与默认 blocker 边界均稳定通过。
- 当前 work item 已达到 formal close-out 条件；后续若要合流 `main`，应在新批次把 disposition 从 `archived / retained（对照保留）` 更新为 `merged / removed` 或其他真实处置。

#### 2.8 归档后动作

- **已完成 git 提交**：是
- **提交哈希**：`9815358`、`dde6fa7`、`0179859`、`5eddce2`、`12e1950`
- 当前批次 branch disposition 状态：`archived`
- 当前批次 worktree disposition 状态：`retained（对照保留）`
- 是否继续下一批：`阻断`（等待后续集成处置）
