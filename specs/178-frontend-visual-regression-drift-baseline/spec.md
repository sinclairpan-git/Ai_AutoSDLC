# 功能规格：Frontend Visual Regression Drift Baseline

**功能编号**：`178-frontend-visual-regression-drift-baseline`  
**状态**：草案（待评审）  
**创建日期**：2026-04-23  
**输入**：[`../../docs/superpowers/specs/2026-04-23-frontend-visual-regression-drift-design.md`](../../docs/superpowers/specs/2026-04-23-frontend-visual-regression-drift-design.md)、[`../149-frontend-p2-quality-platform-baseline/spec.md`](../149-frontend-p2-quality-platform-baseline/spec.md)、[`../171-frontend-browser-gate-delivery-context-binding-baseline/spec.md`](../171-frontend-browser-gate-delivery-context-binding-baseline/spec.md)、[`../172-frontend-browser-gate-runner-delivery-context-propagation-baseline/spec.md`](../172-frontend-browser-gate-runner-delivery-context-propagation-baseline/spec.md)、[`../../governance/frontend/quality-platform/evidence-platform.yaml`](../../governance/frontend/quality-platform/evidence-platform.yaml)、[`../../src/ai_sdlc/core/frontend_browser_gate_runtime.py`](../../src/ai_sdlc/core/frontend_browser_gate_runtime.py)、[`../../src/ai_sdlc/models/frontend_browser_gate.py`](../../src/ai_sdlc/models/frontend_browser_gate.py)

> 口径：`178` 不是在重写 browser gate 的启发式 a11y/visual foundation，也不是在另起一套视觉平台。它只把当前 browser gate 已经采集到的 screenshot 变成 contract-backed 的 visual regression drift 证据，并把这条证据接回现有 quality-platform contract plane 与 `visual_verdict` 交接面。

## 问题定义

当前仓库已经有三类相关事实：

1. browser gate 已经稳定生成 `navigation-screenshot.png`
2. `governance/frontend/quality-platform/evidence-platform.yaml` 已经定义了 `visual-regression-evidence` contract，要求 payload 至少包含 `screenshot_ref` 和 `diff_ratio`
3. `BrowserQualityBundleMaterializationInput` 已经预留 `visual_verdict` 槽位，但当前它仍主要由启发式 visual expectation 结果驱动

但现在还缺少一条真正可执行的视觉回归闭环：

- 当前截图和 repo-pinned baseline 没有做 contract-backed 比较
- baseline 资产与运行时 evidence 还没有分层
- 缺少依赖时，框架还没有自动补齐 managed frontend 的 diff 依赖
- `diff_ratio` 还没有被提升为可审计、可阻断、可回溯的质量信号

因此 `178` 的目标是把“有截图”升级成“有基线、有比较、有证据、有 verdict”。

## 范围

- **覆盖**：
  - 将 visual regression drift materialize 为 quality-platform contract-backed evidence
  - 将 baseline 资产与运行时 evidence 分层管理
  - 让 browser gate 在缺少 diff 依赖时自动 bootstrap managed frontend，再继续 probe
  - 让 `visual_verdict` 由 visual regression drift 结果驱动
  - 保留现有 a11y heuristics 作为独立 lane，不和 visual regression 混成一个 blob
- **不覆盖**：
  - keyboard traversal / tab-order 完整验证
  - 主观审美打分系统
  - 多浏览器矩阵扩张
  - 完整 WCAG 平台
  - 自动刷新 baseline 或无审查 blessing

## 已锁定决策

- 质量平台 contract plane 是 canonical output plane，不能被 spec-scoped debug 文件替代
- baseline 是 reference asset，不是运行时 evidence
- baseline 以 `matrix_id` 为主键，不以 `delivery_entry_id` 为主键
- `diff_ratio` 只是一项全局指标，必须配合 critical region / ignore region 语义使用，不能单独代表 human-perceived quality
- 缺少 diff 依赖时必须自动补齐 `managed/frontend` workspace 的依赖；如果 bootstrap 失败，结果必须诚实落入 `transient_run_failure`
- `visual_expectation` 作为既有 heuristic lane 继续存在，但不能在 `visual_regression` 生效后继续充当最终视觉回归真值

## 关键实体

### 1. Visual Regression Baseline Profile

视觉回归基线按 `quality-platform.coverage-matrix.yaml` 中的 `matrix_id` 组织。

每个 profile 至少应包含：

- `matrix_id`
- `browser_id`
- `viewport_id`
- `style_pack_id`
- `baseline_image_ref`
- `baseline_metadata_ref`
- `threshold`
- `critical_regions`
- `ignore_regions`
- `blessed_at`
- `source_screenshot_ref`
- `source_digest`

规则：

- `matrix_id` 是唯一 lookup key
- `baseline_image_ref` 是 blessed reference image，不得由 runtime 自动覆盖
- `critical_regions` 至少要覆盖页面主视觉区域、主要 CTA、首屏内容区或其他业务关键区域
- `ignore_regions` 只能用于时间戳、头像、轮播、自动刷新计数这类动态噪声区域

### 2. Visual Regression Contract Evidence

`visual-regression-evidence` 是 quality-platform 的 canonical contract evidence。

其运行时产物建议按下面的治理路径 materialize：

- `governance/frontend/quality-platform/evidence/visual-regression/runs/<matrix_id>/<gate_run_id>.yaml`

baseline 参考资产建议按下面的路径 materialize：

- `governance/frontend/quality-platform/evidence/visual-regression/baselines/<matrix_id>/baseline.png`
- `governance/frontend/quality-platform/evidence/visual-regression/baselines/<matrix_id>/baseline.yaml`

运行时 evidence 的最小 payload 应包含：

- `matrix_id`
- `gate_run_id`
- `screenshot_ref`
- `baseline_ref`
- `diff_image_ref`
- `diff_ratio`
- `threshold`
- `region_summaries`
- `change_summary`
- `capture_protocol_ref`
- `verdict`

规则：

- 运行时 evidence 必须有 `artifact:` 语义的可回读引用
- `.ai-sdlc/artifacts/...` 只能保留为临时调试输出，不得成为 canonical contract location
- `diff_ratio` 必须和 region-level summaries 一起消费，不能单独决定最终 verdict

### 3. Browser Gate Visual Verdict

`BrowserQualityBundleMaterializationInput.visual_verdict` 继续是唯一的 bundle 视觉 verdict 槽位。

规则：

- 当 `visual-regression` evidence 可用时，`visual_verdict` 以其结果为主
- 当 baseline 缺失、diff 依赖 bootstrap 失败或当前 screenshot 缺失时，`visual_verdict` 不得伪装成 pass
- `visual_expectation` 仍可作为 legacy heuristic receipt 存在，但不能在 visual regression lane 生效后继续代表最终视觉回归真值

### 4. Managed Frontend Bootstrap

缺少视觉回归 diff 依赖时，browser gate orchestration 必须自动触发 managed frontend bootstrap。

规则：

- bootstrap 目标是 `managed/frontend`
- bootstrap 需要使用该 workspace 的 lockfile 解析
- bootstrap 成功后继续 probe execution
- bootstrap 失败时，probe 必须诚实落为 `transient_run_failure`
- bootstrap 过程必须可审计，不得在 verdict-producing runtime 中隐式改写 workspace 状态而不留证据

## Runtime Truth Order

1. **Eligibility check**
   - browser gate 已满足现有启动条件
   - 当前 pipeline 需要 visual regression verdict
2. **Dependency bootstrap**
   - 检查 managed frontend diff comparator 依赖是否已可解析
   - 若不可解析，自动执行 workspace bootstrap
   - 失败则返回 `transient_run_failure`
3. **Profile resolution**
   - 通过 quality platform 的 `matrix_id` 解析 browser / viewport / style pack
   - 读取对应 baseline profile
4. **Capture protocol freeze**
   - 固定 viewport/device profile
   - 冻结动画与过渡
   - 等待字体和首屏内容稳定
   - 应用 dynamic-region masks / ignore regions
5. **Screenshot comparison**
   - 生成当前 gate run screenshot
   - 使用 diff comparator 计算 `diff_ratio`
   - 生成 `diff_image_ref`
6. **Verdict classification**
   - baseline 缺失或 profile mis-keyed -> `evidence_missing`
   - screenshot 缺失 -> `evidence_missing`
   - bootstrap / comparator 安装失败 -> `transient_run_failure`
   - diff 超阈值或 critical region 超阈值 -> `actual_quality_blocker`
   - diff 在阈值内 -> `pass`
7. **Evidence materialization**
   - 写出 governance contract evidence
   - 写出 runtime diff artifact
   - 更新 bundle 的 `visual_verdict`

## 失败语义

- `evidence_missing`
  - baseline 不存在
  - baseline profile mis-keyed
  - screenshot 缺失
  - current run 没有形成可比较 evidence
- `transient_run_failure`
  - managed frontend diff dependencies bootstrap 失败
  - comparator 无法安装或解析
  - 浏览器/runner 在 diff 前崩溃
- `actual_quality_blocker`
  - `diff_ratio` 超阈值
  - critical region 超阈值
  - 页面布局、文字换行、CTA 可见性或遮挡产生确定性回归

## 功能需求

| ID | 需求 |
|----|------|
| FR-178-001 | `178` 必须把视觉回归实现为 quality-platform contract-backed evidence lane，而不是仅仅新增一套本地 debug artifact |
| FR-178-002 | `178` 必须将 baseline 与 runtime evidence 分层，且 baseline 只能由显式 blessing 更新，不得由 runtime 自动覆盖 |
| FR-178-003 | `178` 必须以 `matrix_id` 为 baseline lookup 主键，并让 browser / viewport / style pack 通过 matrix identity 间接解析 |
| FR-178-004 | `178` 必须在 managed frontend workspace 缺少 diff 依赖时自动 bootstrap；bootstrap 成功后继续 probe，失败则诚实分类为 `transient_run_failure` |
| FR-178-005 | `178` 必须在 screenshot comparison 中同时消费 global `diff_ratio` 与 critical / ignore region 语义，不能只用单一全局阈值 |
| FR-178-006 | `178` 必须 materialize 可回读的 governance evidence，且 evidence 的 canonical location 必须位于 `governance/frontend/quality-platform/evidence/visual-regression/` 下 |
| FR-178-007 | `178` 必须把 `.ai-sdlc/artifacts/...` 限定为 runtime debug output，不得作为 canonical contract source |
| FR-178-008 | `178` 必须明确 `visual_expectation` 与 `visual-regression` 的迁移关系，避免双真值或 verdict 漂移 |
| FR-178-009 | `178` 必须让 `BrowserQualityBundleMaterializationInput.visual_verdict` 由 visual regression drift 结果驱动，并在缺 baseline / 缺依赖时诚实落到非 pass 状态 |
| FR-178-010 | `178` 不得把 keyboard traversal、完整 WCAG 平台、多浏览器矩阵或自动 baseline bless 混入本切片 |

## 验收场景

1. **Given** managed frontend 缺少 diff comparator 依赖，**When** browser gate 进入 visual regression probe，**Then** 系统必须先尝试自动 bootstrap，并在 bootstrap 成功后继续执行比较。
2. **Given** bootstrap 失败，**When** probe 结束，**Then** 结果必须显式为 `transient_run_failure`，并给出可审计的 remediation hint。
3. **Given** baseline profile 存在且 current screenshot 与 baseline 在阈值内，**When** 比较完成，**Then** 必须 materialize `visual-regression-evidence` contract evidence 且 `visual_verdict=pass`。
4. **Given** baseline 缺失或 mis-keyed，**When** 比较完成，**Then** 必须返回 `evidence_missing`，而不是伪装成 blocker 或 pass。
5. **Given** 当前 screenshot 在关键 region 上产生稳定回归，**When** 比较完成，**Then** 必须返回 `actual_quality_blocker`，并携带 `diff_image_ref`、`diff_ratio` 与 region summaries。
6. **Given** `visual_expectation` 仍然产生 legacy heuristic 结论，**When** `visual-regression` 已可用，**Then** bundle 的 `visual_verdict` 仍必须以 visual regression 结果为主，不能被 heuristic pass 误导。

## 影响文件

- `src/ai_sdlc/core/frontend_browser_gate_runtime.py`
- `src/ai_sdlc/core/program_service.py`
- `src/ai_sdlc/models/frontend_browser_gate.py`
- `src/ai_sdlc/generators/frontend_quality_platform_artifacts.py`
- `src/ai_sdlc/models/frontend_quality_platform.py`
- `src/ai_sdlc/cli/sub_apps.py`
- `scripts/frontend_browser_gate_probe_runner.mjs`
- `managed/frontend/package.json`
- `managed/frontend/package-lock.json`
- `governance/frontend/quality-platform/evidence-platform.yaml`
- `governance/frontend/quality-platform/coverage-matrix.yaml`
- `tests/unit/test_frontend_browser_gate_runtime.py`
- `tests/unit/test_frontend_quality_platform_models.py`
- `tests/unit/test_frontend_quality_platform_artifacts.py`
- `tests/unit/test_program_service.py`
- `tests/integration/test_cli_program.py`

## 后续实现拆分建议

`178` 之后的实现建议拆成两段，不要一次把全部逻辑塞进 browser gate runtime：

1. **Visual regression evidence contract plumbing**
   - 将 governance contract、baseline profile、runtime evidence 和 bundle verdict 接通
2. **Managed frontend bootstrap and comparison runtime**
   - 在 managed/frontend 里自动补齐 diff 依赖，并完成 deterministic screenshot comparison

---
related_doc:
  - "docs/superpowers/specs/2026-04-23-frontend-visual-regression-drift-design.md"
  - "specs/149-frontend-p2-quality-platform-baseline/spec.md"
  - "specs/171-frontend-browser-gate-delivery-context-binding-baseline/spec.md"
  - "specs/172-frontend-browser-gate-runner-delivery-context-propagation-baseline/spec.md"
frontend_evidence_class: "framework_capability"
