# 功能规格：Frontend Mainline Browser Gate Real Probe Runtime Baseline

**功能编号**：`143-frontend-mainline-browser-gate-real-probe-runtime-baseline`
**创建日期**：2026-04-14
**状态**：formal baseline 已冻结；runtime implementation 待执行
**输入**：[`../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`](../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md)、[`../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md`](../125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md)、[`../126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md`](../126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md)、[`../../src/ai_sdlc/core/frontend_browser_gate_runtime.py`](../../src/ai_sdlc/core/frontend_browser_gate_runtime.py)、[`../../src/ai_sdlc/core/frontend_gate_verification.py`](../../src/ai_sdlc/core/frontend_gate_verification.py)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../program-manifest.yaml`](../../program-manifest.yaml)

> 口径：`143` 是 `frontend-mainline-delivery` 剩余 release blocker 的下一条 implementation carrier。它只把 `125` 里仍是 placeholder 的 `playwright_smoke / interaction_anti_pattern_checks` 真正推进成一次真实 browser probe runtime：共享 Playwright 运行基底、真实 Playwright trace archive / screenshot / interaction artifacts、结构化 `pass / evidence_missing / transient_run_failure` 分类，以及可被 `126` 下游 handoff 稳定消费的 execute truth。`143` 不补 `workspace_integration / root takeover`，也不扩张成多浏览器矩阵、auto-fix 或完整 visual regression 平台。

## 问题定义

`125` 已经建立了 browser gate 的 execution context、gate-run scoped artifact namespace 与 `latest.yaml` 写面，但当前实现仍保留一个 release-critical 空洞：

- `playwright_smoke` 与 `interaction_anti_pattern_checks` 目前无论 execute 与否，都会先 materialize 成 `missing` artifact 与 `evidence_missing`
- `126` 虽然已经把 browser gate artifact 接到 execute gate truth，却只能消费一个“尚未真正探测”的 artifact
- 结果是 `frontend-mainline-delivery` 的 browser gate 仍没有真正的质量验证主链，只能停留在“结构和 handoff 都有了，但真实探测还没发生”

如果继续停在这里，整个 release capability 会持续卡在 `partial`：

- apply 已完成，却无法用 machine-verifiable probe 证明 browser gate 真正跑过
- execute gate 只能反复输出 “需要补证据/重跑”，无法区分“浏览器没跑起来”“artifact 丢了”“页面真实通过了”
- 小白用户会看到一个永远不落地的 browser gate，而不是可解释、可重跑、可审计的发布门禁

`143` 的目标就是把这条主链补成真实 runtime：保持 `103/125/126` 已冻结的 truth order，不动 `workspace integration`，只把真实 Playwright-backed probe runtime 与 gate binding 接起来。

## 范围

- **覆盖**：
  - 为 browser gate 引入 bounded real probe runner contract，承接 shared runtime capture 与 interaction probe capture
  - 将 `playwright_smoke` 从 placeholder `missing` 产物推进为真实 trace / navigation screenshot capture 或真实 `capture_failed`
  - 将 `interaction_anti_pattern_checks` 从 placeholder `missing` 产物推进为一次真实 bounded interaction probe
  - 将 real probe 结果写回当前 `gate_run_id` artifact namespace 与 `latest.yaml`
  - 将 `pass / evidence_missing / transient_run_failure / actual_quality_blocker` 分类稳定投影到 execute gate truth
  - 补 focused unit/integration tests，锁定 real runner success / incomplete / transient failure / downstream execute binding
- **不覆盖**：
  - `workspace_integration`、root takeover、旧 frontend 根接管
  - 多浏览器/多设备矩阵、后台循环 replay、auto-fix engine
  - 重新设计 visual / a11y evidence provider 或完整 visual regression 平台
  - 重新定义 `126` 的 remediation vocabulary 或扩大到 program-level orchestrator 重构

## 已锁定决策

- `143` 继续以 `gate_run_id + apply artifact + solution snapshot` 作为唯一 scope；不得引入 project-global browser gate context
- real probe 默认走 bounded Node/Playwright subprocess runner；tests 必须通过 injected runner/stub 保持可复核与离线稳定
- `143` 明确假设 host 已满足 `096` 的 `node_runtime / package_manager / playwright_browsers` 最低可执行前提；本切片不会自动安装或下载 Playwright。若 default runner 发现 Playwright module、browser binary 或必要宿主依赖不可用，必须 fail-closed 为 `transient_run_failure`，并给出明确下一步命令与 plain-language 解释
- local path 型 `managed_frontend_target` 若未显式给出文件入口，默认派生到 `<managed_frontend_target>/index.html`；若仍不可导航，必须 fail-closed 为 `transient_run_failure`，不得伪装成空白通过
- default runner 必须设置硬超时；browser bootstrap / navigation / script execution 超时不得无限挂起 CLI
- `playwright_smoke` 至少必须产出 shared trace 与 shared navigation screenshot；若 runner 已执行但产物缺失，必须记为 `evidence_missing`，不得伪装成 `pass`
- browser launch / navigation / script execution failure 必须记为 `transient_run_failure`，并保持 `recheck_required`
- `interaction_anti_pattern_checks` 在本切片只要求一次 bounded real interaction path；没有 evidence-backed issue 时可以是 `pass`，不得为了“看起来更完整”伪造 blocker
- execute gate precedence 固定为：
  1. scope/linkage drift、required probe receipts 不完整、bundle/result inconsistency -> `blocked`
  2. 任一 check 为 `evidence_missing` 或 `transient_run_failure` -> `recheck_required`
  3. 否则任一 check 为 `actual_quality_blocker` -> `needs_remediation`
  4. 否则 `pass / advisory_only` -> `ready`
- `143` 只把 real probe 结果接成 execute truth，不扩张到 workspace integration 或 root-level mutate protocol

## 用户故事与验收

### US-143-1 — Operator 需要看到 browser gate 真的跑过

作为 **operator**，我希望 `program browser-gate-probe --execute` 产出真实 trace、截图与 interaction probe 证据，这样我不会再看到一个永远停留在 placeholder 的 browser gate。

**优先级说明**：P0；这是 `frontend-mainline-delivery` 当前唯一剩余 release blocker 的直接承接面。

**独立测试**：用 injected runner/stub 驱动真实 capture success / artifact missing / launch failure 三类结果，验证 `latest.yaml`、artifact root 与 execute gate decision 一致。

**验收场景**：

1. **Given** shared runner 成功生成 trace 与 navigation screenshot，**When** browser gate execute 完成，**Then** `playwright_smoke` receipt 必须是 `pass` 或 evidence-backed verdict，而不是默认 `evidence_missing`
2. **Given** runner 启动失败或导航超时，**When** browser gate execute 完成，**Then** 结果必须是 `transient_run_failure`，并下游映射为 `recheck_required`

### US-143-2 — Reviewer 需要 interaction probe 与 gate-run artifacts 保持单一真值

作为 **reviewer**，我希望 interaction probe 的真实 artifacts 继续绑定到当前 `gate_run_id`，这样 `126` 的 execute gate 不会消费到历史 run 或 placeholder 证据。

**优先级说明**：P0；这是 browser gate artifact 能否成为可信 execute truth 的核心约束。

**独立测试**：校验 artifact refs 全部位于当前 `artifact_root_ref`，bundle 不接受跨 run refs，scope/linkage 漂移保持 fail-closed。

**验收场景**：

1. **Given** 当前 gate run 成功执行了 bounded interaction probe，**When** bundle materialize，**Then** interaction receipts 与 artifact refs 必须全部位于当前 `gate_run_id` 的 artifact namespace
2. **Given** artifact namespace、apply linkage 或 required probe receipts 漂移，**When** `ProgramService` 读取 latest browser gate artifact，**Then** execute gate 必须 fail-closed 为 `blocked`

### US-143-3 — Maintainer 需要真实 probe 结果能直接驱动 execute gate

作为 **maintainer**，我希望 real probe runtime 的结果不只停在 artifact 目录里，而是能稳定投影到 `ready / recheck_required / needs_remediation / blocked`，这样 CLI、status 与 remediation runbook 继续只消费一套 truth。

**优先级说明**：P1；它决定 `143` 是否真的关闭 release blocker，而不是只新增一批更真实的文件。

**独立测试**：验证 `execute_frontend_browser_gate_probe`、`build_status`、`program browser-gate-probe` CLI 在 real probe success / incomplete / blocker 三类场景下给出一致 execute gate state。

**验收场景**：

1. **Given** real probe 与 visual/a11y evidence 都通过，**When** `program browser-gate-probe --execute` 完成，**Then** execute gate state 必须为 `ready`
2. **Given** real probe 只留下 `transient_run_failure` 或 `evidence_missing`，**When** 下游读取 artifact，**Then** execute gate state 必须为 `recheck_required`

## 功能需求

| ID | 需求 |
|----|------|
| FR-143-001 | 系统必须为 browser gate execute path 引入 bounded real probe runner contract，承接 shared runtime capture 与 interaction probe capture |
| FR-143-002 | `playwright_smoke` execute 成功时，系统必须真实写出当前 gate run 的 shared trace 与 navigation screenshot；不得继续无条件产出 placeholder `missing` artifacts |
| FR-143-003 | `interaction_anti_pattern_checks` 必须执行至少一次 bounded real interaction probe，并写出当前 gate run 的真实 artifact record / receipt |
| FR-143-004 | runner 已执行但缺少必需 artifacts 时，系统必须分类为 `evidence_missing`；runner 启动/导航/脚本失败时，系统必须分类为 `transient_run_failure` |
| FR-143-005 | real probe 成功且没有 evidence-backed blocker 时，系统必须将 `playwright_smoke` 与 `interaction_anti_pattern_checks` 记为 `pass`，并允许 downstream gate 根据 bundle 进入 `ready` |
| FR-143-006 | real probe 产出的 artifact refs、runtime session 与 bundle input 必须全部绑定到当前 `gate_run_id`，不得混入历史 latest refs |
| FR-143-007 | default runner 必须以 stdout JSON 返回结构化 `BrowserGateProbeRunnerResult`，Python 侧继续独占 canonical artifact / receipt / bundle materialization |
| FR-143-008 | `ProgramService` 与 CLI 必须继续基于 browser gate artifact 输出一致的 execute gate state / decision reason / next command |
| FR-143-009 | 当 Playwright module/browsers 不可用、browser launch failed、artifact missing 等场景出现时，CLI 必须输出 plain-language 原因与单一下一步命令，避免把新手卡在抽象 reason code 上 |
| FR-143-010 | `143` 不得实现 `workspace_integration`、root takeover、多浏览器矩阵、auto-fix 或 browser dependency auto-provision |
| FR-143-011 | `tests/unit/test_frontend_browser_gate_runtime.py`、`tests/unit/test_program_service.py`、`tests/integration/test_cli_program.py` 必须覆盖 real probe success / evidence missing / transient failure / runner-success-but-artifact-missing / downstream execute binding |

## 关键实体

### 1. BrowserGateRealProbeRunner

`BrowserGateRealProbeRunner` 是 `143` 新增的受控 runtime boundary，用于在当前 `gate_run_id` 下执行 shared browser bootstrap 与 interaction probe。

其最小职责至少包括：

- 接收 `BrowserQualityGateExecutionContext`
- 接收当前 artifact root 与 generated_at
- 返回 shared runtime capture、interaction probe capture、runtime diagnostics

规则：

- default runner 必须是 bounded Playwright-backed implementation
- tests 必须能以 injected runner/stub 复用同一 contract
- runner 不得直接改写 `ProgramService` 或跨 run 读取历史 artifacts
- runner 输出必须走 stdout JSON；Python 侧负责校验并将其投影为 `artifact_records / check_receipts / bundle_input / latest.yaml`

### 2. BrowserGateProbeRunnerResult

`BrowserGateProbeRunnerResult` 是 default runner 与 Python runtime 之间唯一允许的结构化交换面。

其最小字段至少包括：

- `runtime_status`
  - `completed`
  - `incomplete`
  - `failed_transient`
- `shared_capture`
- `interaction_capture`
- `diagnostic_codes`
- `warnings`

其中：

- `shared_capture` 必须至少包含 `trace_artifact_ref`、`navigation_screenshot_ref`、`capture_status`、`final_url`
- `interaction_capture` 必须至少包含 `interaction_probe_id`、`artifact_refs`、`capture_status`、`classification_candidate`

规则：

- stdout JSON 中的所有 artifact refs 都必须是当前 gate run artifact root 下的 repo-relative path
- runner 报告 `completed` 不等于 Python 侧必须接受为 `pass`；若 artifact 文件缺失、字段不全或 refs 越界，Python 侧必须转成 `evidence_missing` 或 `blocked`

### 3. BrowserGateSharedRuntimeCapture

`BrowserGateSharedRuntimeCapture` 是当前 gate run 的 shared browser substrate capture。

其最小字段至少包括：

- `gate_run_id`
- `trace_artifact_ref`
- `navigation_screenshot_ref`
- `capture_status`
  - `captured`
  - `missing`
  - `capture_failed`
- `final_url`
- `anchor_refs`
- `diagnostic_codes`

规则：

- trace 与 navigation screenshot 任一缺失时不得伪装成完整 smoke pass
- 所有 artifact refs 都必须落在当前 `artifact_root_ref` 内

### 4. BrowserGateInteractionProbeCapture

`BrowserGateInteractionProbeCapture` 是当前 gate run 的 bounded real interaction probe 结果。

其最小字段至少包括：

- `gate_run_id`
- `interaction_probe_id`
- `artifact_refs`
- `capture_status`
- `classification_candidate`
  - `pass`
  - `evidence_missing`
  - `transient_run_failure`
  - `actual_quality_blocker`
- `blocking_reason_codes`
- `anchor_refs`

规则：

- 本切片只要求一条 bounded interaction path，不要求多路径覆盖
- 没有 evidence-backed issue 时允许是 `pass`
- artifact 缺失与 runtime failure 必须区分开

## Runner Artifact Layout

default runner 在当前 `artifact_root_ref` 下的最小文件布局固定为：

- `shared-runtime/playwright-trace.zip`
- `shared-runtime/navigation-screenshot.png`
- `interaction/interaction-snapshot.json`

规则：

- Python 侧可以在 canonical artifact 层继续使用 YAML 写出 `latest.yaml`、artifact records 与 receipts，但 runner 直出的 raw artifacts 以当前 layout 为准
- runner 不得在 `artifact_root_ref` 之外写文件
- runner 若宣称某个 artifact 已 capture，Python 侧必须实际校验该文件存在；否则不得视为 `pass`

## 成功标准

### 可度量结果

- **SC-143-001**：`program browser-gate-probe --execute` 能在 shared runner success 场景下写出真实 `playwright_trace` 与 `navigation_screenshot` artifact refs
- **SC-143-002**：`interaction_anti_pattern_checks` 在 real probe success 场景下不再固定为 placeholder `evidence_missing`
- **SC-143-003**：real probe 的 `pass / evidence_missing / transient_run_failure / actual_quality_blocker` 能被 `ProgramService` 稳定映射到 `ready / recheck_required / needs_remediation / blocked`
- **SC-143-004**：focused unit/integration tests 通过，且 `uv run ai-sdlc program validate`、`uv run ai-sdlc verify constraints` 与 `uv run ai-sdlc workitem truth-check --wi specs/143-frontend-mainline-browser-gate-real-probe-runtime-baseline` 通过

---
related_doc:
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
  - "specs/125-frontend-mainline-browser-gate-probe-runtime-implementation-baseline/spec.md"
  - "specs/126-frontend-mainline-browser-gate-recheck-remediation-runtime-closure-baseline/spec.md"
  - "src/ai_sdlc/core/frontend_browser_gate_runtime.py"
  - "src/ai_sdlc/core/frontend_gate_verification.py"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
frontend_evidence_class: "framework_capability"
---
