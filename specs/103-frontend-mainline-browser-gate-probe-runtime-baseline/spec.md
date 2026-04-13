# 功能规格：Frontend Mainline Browser Gate Probe Runtime Baseline

**功能编号**：`103-frontend-mainline-browser-gate-probe-runtime-baseline`  
**创建日期**：2026-04-13  
**状态**：已冻结（formal baseline）  
**输入**：[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)、[`../102-frontend-mainline-browser-quality-gate-baseline/spec.md`](../102-frontend-mainline-browser-quality-gate-baseline/spec.md)

> 口径：`103` 冻结的不是 browser gate eligibility、不是 `020` handoff、不是 recheck/remediation binding，也不是完整视觉回归平台，而是 `102` 下游的 probe runtime 本身。它只回答五个问题：唯一 `BrowserQualityGateExecutionContext` 如何落成唯一浏览器运行会话；`playwright_smoke / visual_expectation / basic_a11y / interaction_anti_pattern_checks` 四类检查如何共享同一套真实浏览器 runtime substrate；trace、截图与其他 runtime evidence 如何被结构化产出；何时应归入 `evidence_missing`、何时应归入 `transient_run_failure`、何时才允许写出 evidence-backed blocker/advisory；以及 `browser_quality_bundle` 如何只从当前 gate run 的 artifacts materialize，而不在本层偷做 `020` binding。

## 问题定义

`102` 已把 browser quality gate 的 contract、四类检查面、失败分级、`browser_quality_bundle` 与 `020` handoff 冻结成单一真值，但它刻意没有回答 probe runtime 的执行细节。

当前链路里仍缺少一份独立 formal baseline，回答以下问题：

- `BrowserQualityGateExecutionContext` 到底怎样变成唯一的 Playwright probe 会话，而不是每类检查各起一套临时脚本
- gate run 的 trace、截图、anchor 与 evidence refs 应如何 materialize，才能支撑四类检查共用同一份事实底座
- probe runtime 怎样区分“浏览器或运行环境瞬时失败”与“浏览器活着但本次缺少可判定证据”
- `BrowserQualityCheckResult` 的 runtime write path 应如何固定，避免自由文本失败吞掉 anchor、evidence 与 requirement linkage
- `browser_quality_bundle` 的 runtime materialization 如何只消费当前 `gate_run_id` artifacts，而不漂移成 latest snapshot 或顺手绑定 `020`

如果不先冻结 `103`，后续实现会很快滑向四种常见偏差：

- 把四类检查拆成互相独立的小脚本，导致 scope binding、截图命名与 evidence refs 失去单一真值
- 用“能打开页面”或一两张人工截图替代真正的 trace + structured evidence materialization
- 把截图缺失、anchor 丢失、浏览器崩溃、页面真实质量问题统一压成“browser gate failed”
- 在 probe runtime 里顺手发明 recheck/remediation binding 或 program-level ready 语义，重新把 `102` 切开的边界缝回去

因此，`103` 的目标是把 browser gate 的 probe runtime 固定成一个最小但严格的执行基线：先冻结 shared runtime session、artifact materialization、四类检查的运行写出与 bundle materialization input，再把 recheck/remediation binding 与更宽质量平台继续留在后续切片。

## 范围

- **覆盖**：
  - 将 browser gate probe runtime 正式定义为 `102` 下游独立 child work item
  - 锁定 `BrowserQualityGateExecutionContext -> BrowserGateProbeRuntimeSession` 的运行时转化
  - 锁定 shared real-browser bootstrap、artifact namespace、trace/screenshot materialization 与 source linkage 继承
  - 锁定四类检查的 runtime execution order、最小 evidence capture 与结构化结果写出
  - 锁定 `browser_quality_bundle` 的 runtime materialization input 与单次 gate run 绑定
- **不覆盖**：
  - 重写 `102` 已冻结的 gate eligibility、failure taxonomy、bundle schema 或 `020` handoff schema
  - 在本 work item 中绑定 recheck/remediation replay、program aggregation、auto-fix 或自动重跑
  - 扩张成多浏览器/多设备矩阵、完整 visual diff 平台、完整 WCAG 平台或主观审美系统
  - 修改 `src/`、`tests/` 或声称 Playwright runner 已在本批实现

## 已锁定决策

- `103` 只能消费 `102.BrowserQualityGateExecutionContext` 与其所绑定的 `101` apply truth、`073` provider/style truth、`071` visual/a11y truth；不得另造新的 scope、target 或 readiness subject
- Phase 1 probe runtime 必须运行在真实浏览器中，并以 Playwright orchestration 为单一 runtime substrate；不得退化成静态 DOM 分析或页面可打开检查
- 一个 `gate_run_id` 在任一时刻只能对应一个 active `BrowserGateProbeRuntimeSession`、一个 artifact namespace 与一个待 materialize 的 bundle
- trace 与截图必须是 runtime-owned artifacts；任何 blocker/advisory 都必须能回溯到当前 gate run 的 anchor + evidence + requirement linkage
- `103` 只负责把四类检查结果与 artifacts 写成 `102` 可消费的结构化输入；`020` handoff、recheck binding 与 remediation replay 仍留在后续切片

## 用户故事与验收

### US-103-1 — Framework Maintainer 需要 probe runtime 有独立 formal truth

作为**框架维护者**，我希望 browser gate 的 probe runtime 在 formal docs 中有独立 child work item，以便 Playwright orchestration、artifact materialization 与 per-check result write path 不再混在 `102` 的 gate contract 或未来的 remediation binding 里。

**验收**：

1. Given 我查看 `103` formal docs，When 我追踪 browser gate 主线，Then 可以明确看到它位于 `102` 下游且只负责 probe runtime  
2. Given 我审阅 `103` non-goals，When 我确认边界，Then 可以明确读到 `020` handoff binding、recheck/remediation replay 与 program aggregation 不在本工单内

### US-103-2 — Operator 需要知道 runtime 何时是缺证据，何时是瞬时失败

作为**operator**，我希望 probe runtime 能把 artifact 缺失和浏览器瞬时失败清楚分开，以便我知道该补证据、重跑浏览器，还是去修真正的前端质量问题。

**验收**：

1. Given 浏览器进程仍正常但关键截图或 anchor 没有生成，When 我查看 runtime 结果，Then 可以明确读到 `evidence_missing`，而不是被误报成质量 blocker  
2. Given 浏览器启动、导航或执行过程中发生 crash/timeout，When 系统分类结果，Then 可以明确读到 `transient_run_failure`，并保留重跑语义

### US-103-3 — Reviewer 需要确认 bundle 只来自当前 gate run

作为**reviewer**，我希望 `browser_quality_bundle` 的 materialization input 在 formal docs 中只允许消费当前 `gate_run_id` 的 artifacts，以便后续不会把上一轮截图或 latest trace 混进本次 verdict。

**验收**：

1. Given 我检查 `103` formal docs，When 我查看 artifact namespace 规则，Then 可以明确读到 `one gate_run_id == one runtime session == one artifact namespace`  
2. Given 我检查 `103` formal docs，When 我查看 bundle materialization 规则，Then 可以明确读到 bundle 只能消费当前 gate run artifacts，而不是 latest snapshot

## 关键实体

### 1. BrowserGateProbeRuntimeSession

`BrowserGateProbeRuntimeSession` 是 `103` 唯一的 browser probe 运行时真值。

其最小字段至少包括：

- `probe_runtime_session_id`
- `gate_run_id`
- `apply_result_id`
- `solution_snapshot_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `readiness_subject_id`
- `browser_engine`
  - `chromium`
- `browser_entry_ref`
- `artifact_root_ref`
- `status`
  - `bootstrapping`
  - `running_checks`
  - `materializing_bundle`
  - `completed`
  - `incomplete`
  - `failed`
- `started_at`
- `updated_at`
- `finished_at`
- `source_linkage_refs`

规则：

- 一个 `gate_run_id` 在任一时刻只能有一个 active runtime session
- `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 必须直接继承自 `102.BrowserQualityGateExecutionContext`
- Phase 1 的 `browser_engine` 固定为 `chromium`，用于冻结单一 probe substrate；多浏览器矩阵留给后续切片

### 2. BrowserProbeArtifactRecord

`BrowserProbeArtifactRecord` 是 probe runtime 对当前 gate run 产出的最小 artifact 索引。

其最小字段至少包括：

- `artifact_id`
- `gate_run_id`
- `check_name`
  - `shared_runtime`
  - `playwright_smoke`
  - `visual_expectation`
  - `basic_a11y`
  - `interaction_anti_pattern_checks`
- `artifact_type`
  - `playwright_trace`
  - `navigation_screenshot`
  - `checkpoint_screenshot`
  - `a11y_scan`
  - `interaction_snapshot`
- `artifact_ref`
- `anchor_refs`
- `capture_status`
  - `captured`
  - `missing`
  - `capture_failed`
- `captured_at`
- `source_linkage_refs`

规则：

- 每次 gate run 至少必须产出 shared trace 与 shared navigation screenshot；否则不得伪装成完整 probe run
- blocker/advisory 对应的 `BrowserQualityCheckResult` 至少必须引用一个当前 gate run 的 artifact record
- `missing` 与 `capture_failed` 必须保留，供后续分类成 `evidence_missing` 或 `transient_run_failure`；不得提前丢弃

### 3. BrowserProbeExecutionReceipt

`BrowserProbeExecutionReceipt` 是每一类检查在 runtime 内部的最小执行回执。

其最小字段至少包括：

- `check_name`
- `started_at`
- `finished_at`
- `runtime_status`
  - `not_started`
  - `running`
  - `completed`
  - `incomplete`
  - `failed_transient`
- `artifact_ids`
- `anchor_refs`
- `requirement_linkage`
- `classification_candidate`
  - `pass`
  - `evidence_missing`
  - `transient_run_failure`
  - `actual_quality_blocker`
  - `advisory_only`
- `recheck_required`
- `remediation_hints`

规则：

- 四类检查都必须先写 execution receipt，再 materialize 为 `102.BrowserQualityCheckResult`
- `classification_candidate` 必须由 runtime artifacts、anchor 与 requirement linkage 支撑；不得只写自由文本失败
- `failed_transient` 只用于浏览器/运行环境的瞬时失败；页面真实质量问题不得落在该状态

### 4. BrowserQualityBundleMaterializationInput

`BrowserQualityBundleMaterializationInput` 是 probe runtime 向 `102.browser_quality_bundle` 输出的唯一 bundle 组装输入。

其最小字段至少包括：

- `gate_run_id`
- `apply_result_id`
- `solution_snapshot_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `readiness_subject_id`
- `shared_trace_refs`
- `shared_screenshot_refs`
- `check_receipts`
- `source_linkage_refs`
- `generated_at`

规则：

- bundle materialization input 只能消费当前 runtime session 生成的 artifacts 与 receipts
- 不得从其他 gate run 继承 screenshot/trace，也不得引入 latest snapshot 兜底
- 本实体不包含 `020` handoff fields；hand off binding 继续由后续切片承接

## Runtime Truth Order

probe runtime 的单向顺序固定如下：

1. **Context receipt**
   - 接收唯一 `BrowserQualityGateExecutionContext`
   - 继承 `apply_result_id / solution_snapshot_id / spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id`
2. **Runtime session bootstrap**
   - 创建唯一 `BrowserGateProbeRuntimeSession`
   - 创建当前 `gate_run_id` 的 artifact namespace
3. **Shared browser bootstrap**
   - 用 Playwright 启动真实浏览器
   - 导航到 `browser_entry_ref`
   - 产出 shared trace 与 shared navigation screenshot
4. **Probe execution**
   - 按 `playwright_smoke -> visual_expectation -> basic_a11y -> interaction_anti_pattern_checks` 固定顺序执行
   - 每类检查都必须写 `BrowserProbeExecutionReceipt`
5. **Evidence normalization**
   - 将 `captured / missing / capture_failed` 与 runtime receipt 对齐
   - 归并成 `pass / evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only`
6. **Bundle materialization**
   - 只用当前 gate run receipts + artifacts 组装 `BrowserQualityBundleMaterializationInput`
   - 交给 `102.browser_quality_bundle` 的 schema materialization

## 四类检查的 runtime 固定边界

### 1. `playwright_smoke`

- 必须通过真实浏览器导航与最小主路径操作验证“页面可操作”，而不是只检测页面打开成功
- 必须至少留下导航前后或关键节点截图与 trace 片段
- 若浏览器导航成功但关键主路径缺少可判定 evidence，应分类为 `evidence_missing`，而不是默认 pass

### 2. `visual_expectation`

- 必须基于 live page screenshots 与 `073` 已冻结的 provider/style truth 判定关键区域可见性、布局断裂、文字溢出、遮挡与空白主视图
- 必须引用当前 gate run 的 screenshot artifacts；不得引用历史截图或人工点评
- 若 screenshot capture 失败但浏览器上下文仍可继续，结果必须落为 `evidence_missing`

### 3. `basic_a11y`

- 必须围绕 `071` 已冻结的 perceivability / semantics / keyboard / focus 底线执行 machine-checkable 检查
- 必须留下可追溯的 a11y scan 或交互 evidence；不得只写“无障碍失败”
- 若浏览器执行键盘/焦点脚本时发生瞬时崩溃或 runtime timeout，可归入 `transient_run_failure`

### 4. `interaction_anti_pattern_checks`

- Phase 1 只允许覆盖 `102` 已冻结的六类 machine-checkable 反模式
- 每个 blocker/advisory 都必须绑定当前 gate run 的 anchor、artifact 与 requirement linkage
- 不得在本检查面引入主观审美、品牌偏好或 recheck/remediation binding

## Evidence Honesty Rules

- 浏览器无法启动、上下文创建失败、页面崩溃、执行超时或 Playwright 基础设施瞬时异常，应归入 `transient_run_failure`
- 浏览器仍可运行，但某类检查缺少必需 artifact、anchor 或 requirement linkage，应归入 `evidence_missing`
- 只有在 artifact、anchor 与 requirement linkage 完整时，才允许写出 `actual_quality_blocker` 或 `advisory_only`
- `pass` 必须意味着该检查所需 evidence 已完整 materialize；不得在 evidence 缺口下给出推测性通过

## 验证场景

1. Given runtime session 正常启动且四类检查都写出完整 evidence，When bundle materialization input 生成，Then 当前 gate run 必须能完整映射到单一 `browser_quality_bundle`
2. Given shared trace 已生成但某类检查截图缺失，When 结果分类，Then 该检查必须为 `evidence_missing`，而不是 `actual_quality_blocker`
3. Given 浏览器在 smoke 执行阶段 crash，When runtime 写回结果，Then 必须得到 `transient_run_failure`，并保留 shared artifacts 与 source linkage
4. Given visual 或 interaction 检查发现真实问题且 evidence 完整，When runtime 写回结果，Then 必须得到带 anchor/evidence 的 `actual_quality_blocker` 或 `advisory_only`
5. Given 上一轮 gate run 留有旧截图，When 本轮 bundle materialization 发生，Then 系统不得复用旧 artifacts 填补当前 evidence 缺口

## 功能需求

| ID | 需求 |
|----|------|
| FR-103-001 | `103` 必须作为 `102` 下游的 browser gate probe runtime child work item 被正式定义 |
| FR-103-002 | `103` 必须明确 probe runtime 只消费 `102.BrowserQualityGateExecutionContext` 及其绑定的 `101 / 073 / 071` truths |
| FR-103-003 | 一个 `gate_run_id` 必须只允许一个 active `BrowserGateProbeRuntimeSession`、一个 artifact namespace 与一个 bundle materialization input |
| FR-103-004 | Phase 1 probe runtime 必须由 Playwright 驱动的真实浏览器执行，且当前固定 `browser_engine=chromium` |
| FR-103-005 | probe runtime 必须在 shared bootstrap 阶段产出至少一个 trace ref 与一个 navigation screenshot ref |
| FR-103-006 | `playwright_smoke` 必须验证关键主路径可操作，并留下 trace/screenshot evidence |
| FR-103-007 | `visual_expectation` 必须基于当前 gate run 的 live screenshots 与 `073` provider/style truth 输出结构化结果 |
| FR-103-008 | `basic_a11y` 必须围绕 `071` foundation 执行 machine-checkable 检查，并保留可追溯 evidence |
| FR-103-009 | `interaction_anti_pattern_checks` 只允许覆盖 `102` 已冻结的 machine-checkable 反模式集合 |
| FR-103-010 | 四类检查都必须先写 `BrowserProbeExecutionReceipt`，再映射为 `102.BrowserQualityCheckResult` |
| FR-103-011 | `capture_status=missing` 与 `capture_status=capture_failed` 必须被保留并诚实映射为 `evidence_missing` 或 `transient_run_failure` |
| FR-103-012 | blocker/advisory 结果必须同时绑定当前 gate run 的 artifact、anchor 与 requirement linkage；不得只写自由文本 |
| FR-103-013 | `BrowserQualityBundleMaterializationInput` 只能消费当前 gate run 的 receipts 与 artifacts，不得复用历史 run 产物 |
| FR-103-014 | `103` 不得在 probe runtime 内绑定 `020` handoff、recheck/remediation replay 或 program-level ready 语义 |
| FR-103-015 | `103` 当前只 formalize probe runtime contract，不得声称 Playwright runner、artifact store 或 tests 已在本切片实现 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-103-001 | reviewer 能从 `103` 直接读出 probe runtime 的 shared session、artifact namespace 与 execution order，而无需回到 `102` 临时推断 |
| SC-103-002 | maintainer 能直接确认 `evidence_missing` 与 `transient_run_failure` 在 runtime 层已经有稳定区分 |
| SC-103-003 | operator 能从 `103` 直接理解 blocker/advisory 必须绑定当前 gate run 的 artifacts，而不是靠人工描述 |
| SC-103-004 | 当前规格不会让人误以为 `020` handoff binding、recheck/remediation replay 或多浏览器矩阵已在本批实现 |

## 后续实现拆分建议

`103` 之后如果继续深化，优先应落在 browser gate 的结果绑定层，而不是重写 probe runtime：

1. **Browser Gate Recheck And Remediation Binding**
   - 负责把 `102/103` 的 incomplete、blocked 与 advisory 结果绑定到 `020` recheck/remediation vocabulary

---
related_doc:
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
